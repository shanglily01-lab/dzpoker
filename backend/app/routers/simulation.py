"""
游戏模拟路由 - 自动运行完整游戏流程

提供自动模拟游戏的API端点
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, List
import asyncio

from ..core.poker import PokerGame, Card
from ..ai.decision_maker import ai_decision_maker
from .games import games

router = APIRouter(prefix="/simulation", tags=["simulation"])


@router.post("/{game_id}/auto-play")
async def auto_play_game(game_id: str, speed: float = 1.0):
    """
    自动运行整局游戏

    Args:
        game_id: 游戏ID
        speed: 速度倍数 (1.0 = 正常速度, 2.0 = 2倍速)

    Returns:
        完整的游戏记录
    """
    if game_id not in games:
        raise HTTPException(status_code=404, detail="游戏不存在")

    game = games[game_id]

    # 游戏记录
    game_log = {
        "game_id": game_id,
        "actions": [],
        "winners": []
    }

    try:
        # 为每个玩家分配AI类型
        player_types = {}
        for player in game.players:
            player_types[player.player_id] = ai_decision_maker.assign_player_type(
                player.player_id
            )
            game_log["actions"].append({
                "type": "player_type_assigned",
                "player_id": player.player_id,
                "player_type": player_types[player.player_id]
            })

        # 开始游戏
        game.start_game()
        game_log["actions"].append({
            "type": "game_started",
            "state": game.state.value
        })

        await asyncio.sleep(0.5 / speed)

        # 发底牌
        game.deal_hole_cards()
        game_log["actions"].append({
            "type": "hole_cards_dealt",
            "state": game.state.value
        })

        await asyncio.sleep(0.5 / speed)

        # 翻牌前下注轮
        await _run_betting_round(game, game_log, player_types, speed)

        # 发翻牌
        if game.state.value == "preflop":
            flop = game.deal_flop()
            game_log["actions"].append({
                "type": "flop_dealt",
                "cards": [c.to_dict() for c in flop],
                "state": game.state.value
            })
            await asyncio.sleep(0.5 / speed)

            # 翻牌圈下注
            await _run_betting_round(game, game_log, player_types, speed)

        # 发转牌
        if game.state.value == "flop":
            turn = game.deal_turn()
            game_log["actions"].append({
                "type": "turn_dealt",
                "card": turn.to_dict(),
                "state": game.state.value
            })
            await asyncio.sleep(0.5 / speed)

            # 转牌圈下注
            await _run_betting_round(game, game_log, player_types, speed)

        # 发河牌
        if game.state.value == "turn":
            river = game.deal_river()
            game_log["actions"].append({
                "type": "river_dealt",
                "card": river.to_dict(),
                "state": game.state.value
            })
            await asyncio.sleep(0.5 / speed)

            # 河牌圈下注
            await _run_betting_round(game, game_log, player_types, speed)

        # 摊牌
        if game.state.value == "river" or game.state.value == "showdown":
            result = game.showdown()
            game_log["actions"].append({
                "type": "showdown",
                "result": result
            })
            game_log["winners"] = result["winners"]

        return {
            "success": True,
            "game_log": game_log,
            "final_state": game.get_state()
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"游戏模拟失败: {str(e)}")


async def _run_betting_round(
    game: PokerGame,
    game_log: Dict,
    player_types: Dict[int, str],
    speed: float
):
    """运行一轮下注"""
    max_iterations = 50  # 防止无限循环
    iteration = 0

    while game.state.value in ["preflop", "flop", "turn", "river"] and iteration < max_iterations:
        iteration += 1

        current_player = game.get_current_player()
        if not current_player:
            break

        # 检查是否需要继续下注
        active_players = [p for p in game.players if p.is_active and not p.is_all_in]
        if len(active_players) <= 1:
            break

        # 检查当前下注轮是否结束
        if game._is_betting_round_complete():
            break

        # AI决策
        player_type = player_types.get(current_player.player_id, "REGULAR")
        action, amount = ai_decision_maker.make_decision(
            player_id=current_player.player_id,
            player_type=player_type,
            hole_cards=current_player.hole_cards,
            community_cards=game.community_cards,
            current_bet=game.current_bet,
            player_bet=current_player.current_bet,
            player_chips=current_player.chips,
            pot=game.pot,
            game_state=game.state.value,
            position=current_player.position
        )

        # 执行动作
        try:
            result = game.player_action(
                current_player.player_id,
                action,
                amount or 0
            )

            game_log["actions"].append({
                "type": "player_action",
                "player_id": current_player.player_id,
                "player_type": player_type,
                "action": action,
                "amount": amount or 0,
                "chips_remaining": current_player.chips,
                "pot": game.pot
            })

            await asyncio.sleep(0.3 / speed)

        except ValueError as e:
            # 如果动作无效，尝试弃牌
            game_log["actions"].append({
                "type": "invalid_action",
                "player_id": current_player.player_id,
                "attempted_action": action,
                "error": str(e)
            })

            try:
                game.player_action(current_player.player_id, "fold", 0)
                game_log["actions"].append({
                    "type": "player_action",
                    "player_id": current_player.player_id,
                    "action": "fold",
                    "amount": 0
                })
            except:
                pass

    # 如果只剩一个活跃玩家，直接结束
    active_players = [p for p in game.players if p.is_active]
    if len(active_players) == 1:
        # 赢家获得底池
        winner = active_players[0]
        winner.chips += game.pot
        game_log["actions"].append({
            "type": "early_win",
            "winner_id": winner.player_id,
            "pot": game.pot
        })


@router.post("/{game_id}/single-action")
async def single_ai_action(game_id: str):
    """
    让当前玩家执行一次AI决策

    用于逐步控制游戏进程
    """
    if game_id not in games:
        raise HTTPException(status_code=404, detail="游戏不存在")

    game = games[game_id]
    current_player = game.get_current_player()

    if not current_player:
        raise HTTPException(status_code=400, detail="没有当前玩家")

    # 分配玩家类型（如果还没有）
    if not hasattr(game, '_player_types'):
        game._player_types = {}

    if current_player.player_id not in game._player_types:
        game._player_types[current_player.player_id] = ai_decision_maker.assign_player_type(
            current_player.player_id
        )

    player_type = game._player_types[current_player.player_id]

    # AI决策
    action, amount = ai_decision_maker.make_decision(
        player_id=current_player.player_id,
        player_type=player_type,
        hole_cards=current_player.hole_cards,
        community_cards=game.community_cards,
        current_bet=game.current_bet,
        player_bet=current_player.current_bet,
        player_chips=current_player.chips,
        pot=game.pot,
        game_state=game.state.value,
        position=current_player.position
    )

    # 执行动作
    try:
        result = game.player_action(
            current_player.player_id,
            action,
            amount or 0
        )

        return {
            "success": True,
            "player_id": current_player.player_id,
            "player_type": player_type,
            "action": action,
            "amount": amount or 0,
            "game_state": game.get_state()
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
