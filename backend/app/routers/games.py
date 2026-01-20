"""游戏相关API路由"""
from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect, Depends
from typing import Dict, List
import uuid
from sqlalchemy.ext.asyncio import AsyncSession

from ..schemas import (
    CreateGameRequest, GameResponse, CardResponse,
    PlayerActionRequest, GameStateResponse
)
from ..core.poker import PokerGame, GameState
from ..core.database import get_db
from ..core.redis_storage import game_storage
from ..services.game_service import GameService
from ..ai.smart_dealer import smart_dealer
from ..ai.decision_maker import ai_decision_maker

router = APIRouter(prefix="/api/games", tags=["games"])

# WebSocket连接管理
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, game_id: str, websocket: WebSocket):
        await websocket.accept()
        if game_id not in self.active_connections:
            self.active_connections[game_id] = []
        self.active_connections[game_id].append(websocket)

    def disconnect(self, game_id: str, websocket: WebSocket):
        if game_id in self.active_connections:
            self.active_connections[game_id].remove(websocket)

    async def broadcast(self, game_id: str, message: dict):
        if game_id in self.active_connections:
            for connection in self.active_connections[game_id]:
                try:
                    await connection.send_json(message)
                except Exception:
                    pass


ws_manager = ConnectionManager()


def save_game_state(game_id: str, game: PokerGame):
    """保存游戏状态到 Redis"""
    game_storage.save_game(game_id, game)


@router.post("", response_model=GameResponse)
async def create_game(request: CreateGameRequest):
    """创建新游戏"""
    game_id = str(uuid.uuid4())[:8]

    game = PokerGame(
        game_id=game_id,
        small_blind=request.small_blind,
        big_blind=request.big_blind
    )

    # 添加虚拟玩家 (实际应从请求中获取)
    for i in range(request.num_players):
        game.add_player(player_id=i + 1, chips=1000)

    # 保存到 Redis
    game_storage.save_game(game_id, game)

    return GameResponse(
        game_id=game_id,
        num_players=request.num_players,
        small_blind=request.small_blind,
        big_blind=request.big_blind,
        status=game.state.value,
        pot=game.pot
    )


@router.get("/stats")
async def get_game_stats():
    """获取游戏统计数据"""
    game_ids = game_storage.get_all_game_ids()
    total_games = len(game_ids)

    active_games = 0
    finished_games = 0
    all_players = set()
    total_hands = 0
    total_pot = 0

    for game_id in game_ids:
        game = game_storage.load_game(game_id)
        if not game:
            continue

        if game.state not in [GameState.WAITING, GameState.FINISHED]:
            active_games += 1
        if game.state == GameState.FINISHED:
            finished_games += 1

        for player in game.players:
            all_players.add(player.player_id)
        if game.state != GameState.WAITING:
            total_hands += 1
        total_pot += game.pot

    return {
        "total_games": total_games,
        "active_games": active_games,
        "finished_games": finished_games,
        "total_players": len(all_players),
        "total_hands": total_hands,
        "total_pot": total_pot
    }


@router.get("/list")
async def list_games(limit: int = 10, state: str = None):
    """获取游戏列表"""
    game_list = []
    game_ids = game_storage.get_all_game_ids()

    for game_id in game_ids:
        game = game_storage.load_game(game_id)
        if not game:
            continue

        # 状态过滤
        if state and game.state.value != state:
            continue

        game_info = {
            "game_id": game_id,
            "num_players": len(game.players),
            "state": game.state.value,
            "pot": game.pot,
            "current_bet": game.current_bet,
            "small_blind": game.small_blind,
            "big_blind": game.big_blind,
            "players": [
                {
                    "player_id": p.player_id,
                    "chips": p.chips,
                    "is_active": p.is_active
                }
                for p in game.players
            ]
        }
        game_list.append(game_info)

    # 按创建时间排序（最新的在前）
    game_list.reverse()

    return game_list[:limit]


@router.get("/{game_id}")
async def get_game(game_id: str, include_hole_cards: bool = False):
    """获取游戏状态

    Args:
        game_id: 游戏ID
        include_hole_cards: 是否包含所有玩家底牌（调试用）
    """
    game = game_storage.load_game(game_id)
    if not game:
        raise HTTPException(status_code=404, detail="游戏不存在")
    return game.get_state(include_hole_cards=include_hole_cards)


@router.post("/{game_id}/start")
async def start_game(game_id: str, db: AsyncSession = Depends(get_db)):
    """开始游戏"""
    game = game_storage.load_game(game_id)
    if not game:
        raise HTTPException(status_code=404, detail="游戏不存在")

    try:
        game.start_hand()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # 创建游戏记录
    try:
        await GameService.create_game_record(db, game)
        print(f"[Database] Game {game_id} record created")
    except Exception as e:
        # 数据库保存失败不影响游戏
        import traceback
        print(f"[Database] Failed to create game record: {str(e)}")
        print(traceback.format_exc())

    # 保存游戏状态
    save_game_state(game_id, game)

    # 广播游戏开始
    await ws_manager.broadcast(game_id, {
        "type": "game_started",
        "state": game.get_state()
    })

    return {
        "message": "游戏开始",
        "state": game.state.value,
        "pot": game.pot
    }


@router.post("/{game_id}/deal")
async def deal_hole_cards(game_id: str, smart: bool = False):
    """
    发底牌

    Args:
        game_id: 游戏ID
        smart: 是否使用智能发牌
    """
    game = game_storage.load_game(game_id)
    if not game:
        raise HTTPException(status_code=404, detail="游戏不存在")

    if game.state != GameState.WAITING:
        raise HTTPException(status_code=400, detail="游戏已经开始")

    # 使用智能发牌或标准发牌
    if smart:
        # 构建玩家状态
        player_states = [
            {
                "player_id": p.player_id,
                "activity_score": 1.0,  # 实际应从数据库获取
                "loss_streak": 0,
                "skill_level": 50
            }
            for p in game.players
        ]

        hole_cards, _ = smart_dealer.deal_with_strategy(
            len(game.players),
            player_states
        )

        # 分配手牌
        for i, player in enumerate(game.players):
            player.hole_cards = hole_cards[i]

        game.state = GameState.PREFLOP
    else:
        game.start_hand()

    # 构建响应
    response = {
        "hole_cards": [
            [card.to_dict() for card in player.hole_cards]
            for player in game.players
        ],
        "deck_remaining": len(game.deck.cards)
    }

    # 保存游戏状态
    save_game_state(game_id, game)

    # 广播发牌结果
    await ws_manager.broadcast(game_id, {
        "type": "cards_dealt",
        "data": response
    })

    return response


@router.post("/{game_id}/flop")
async def deal_flop(game_id: str):
    """发翻牌"""
    game = game_storage.load_game(game_id)
    if not game:
        raise HTTPException(status_code=404, detail="游戏不存在")

    try:
        flop = game.deal_flop()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    response = {
        "cards": [card.to_dict() for card in flop],
        "street": "flop"
    }

    # 保存游戏状态
    save_game_state(game_id, game)

    await ws_manager.broadcast(game_id, {
        "type": "community_cards",
        "data": response
    })

    return response


@router.post("/{game_id}/turn")
async def deal_turn(game_id: str):
    """发转牌"""
    game = game_storage.load_game(game_id)
    if not game:
        raise HTTPException(status_code=404, detail="游戏不存在")

    try:
        turn = game.deal_turn()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    response = {
        "card": turn.to_dict(),
        "street": "turn"
    }

    # 保存游戏状态
    save_game_state(game_id, game)

    await ws_manager.broadcast(game_id, {
        "type": "community_cards",
        "data": response
    })

    return response


@router.post("/{game_id}/river")
async def deal_river(game_id: str):
    """发河牌"""
    game = game_storage.load_game(game_id)
    if not game:
        raise HTTPException(status_code=404, detail="游戏不存在")

    try:
        river = game.deal_river()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    response = {
        "card": river.to_dict(),
        "street": "river"
    }

    # 保存游戏状态
    save_game_state(game_id, game)

    await ws_manager.broadcast(game_id, {
        "type": "community_cards",
        "data": response
    })

    return response


@router.post("/{game_id}/action")
async def player_action(game_id: str, action: PlayerActionRequest):
    """处理玩家动作"""
    game = game_storage.load_game(game_id)
    if not game:
        raise HTTPException(status_code=404, detail="游戏不存在")

    try:
        result = game.player_action(
            player_id=action.player_id,
            action=action.action,
            amount=action.amount or 0
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    response = {
        "player_id": action.player_id,
        "action": action.action,
        "amount": result.get("amount", 0),
        "game_state": game.get_state()
    }

    # 保存游戏状态
    save_game_state(game_id, game)

    await ws_manager.broadcast(game_id, {
        "type": "player_action",
        "data": response
    })

    return response


@router.post("/{game_id}/showdown")
async def showdown(game_id: str, db: AsyncSession = Depends(get_db)):
    """执行摊牌并确定获胜者"""
    game = game_storage.load_game(game_id)
    if not game:
        raise HTTPException(status_code=404, detail="游戏不存在")

    try:
        result = game.showdown()
    except ValueError as e:
        # 记录错误详情
        print(f"Showdown ValueError: {str(e)}")
        print(f"Game state: {game.state.value}")
        print(f"Community cards: {len(game.community_cards)}")
        print(f"Players: {[(p.player_id, p.is_active, p.is_all_in, len(p.hole_cards)) for p in game.players]}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # 记录未预期的错误
        import traceback
        print(f"Showdown unexpected error: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"摊牌时发生错误: {str(e)}")

    # 保存游戏数据到数据库
    try:
        await GameService.finish_game(db, game, result["winners"])
        print(f"[Database] Game {game_id} data saved successfully")
    except Exception as e:
        # 数据库保存失败不影响游戏结果
        import traceback
        print(f"[Database] Failed to save game data: {str(e)}")
        print(traceback.format_exc())

    # 广播摊牌结果
    await ws_manager.broadcast(game_id, {
        "type": "showdown",
        "data": result
    })

    return result


@router.post("/{game_id}/finish")
async def finish_game_route(game_id: str, db: AsyncSession = Depends(get_db)):
    """
    结束游戏并保存数据（用于非showdown路径，如所有人弃牌）
    """
    game = game_storage.load_game(game_id)
    if not game:
        raise HTTPException(status_code=404, detail="游戏不存在")

    # 检查游戏是否已结束
    if game.state.value != 'finished':
        raise HTTPException(status_code=400, detail="游戏尚未结束")

    # 检查数据库中是否已经保存（避免重复保存）
    from sqlalchemy import select
    from ..models import Game as GameModel
    result = await db.execute(
        select(GameModel).where(GameModel.game_uuid == game_id)
    )
    existing_game = result.scalar_one_or_none()

    if existing_game and existing_game.status == "finished":
        print(f"[Database] Game {game_id} already finished and saved, skipping")
        # 返回已保存的获胜者信息
        winners = game.last_winners if hasattr(game, 'last_winners') and game.last_winners else []
        return {"success": True, "winners": winners, "already_saved": True}

    # 获取获胜者信息（已在_advance_state中设置）
    winners = game.last_winners if hasattr(game, 'last_winners') and game.last_winners else []

    if not winners:
        # 如果没有winners信息，尝试从当前状态推断
        active_players = [p for p in game.players if p.is_active]
        if len(active_players) == 1:
            winner = active_players[0]
            winners = [{
                "player_id": winner.player_id,
                "hand_description": "其他玩家弃牌",
                "winnings": 0,  # 底池已经分配
                "hole_cards": [c.to_dict() for c in winner.hole_cards] if winner.hole_cards else []
            }]

    # 打印调试信息
    print(f"[Database Debug] Game {game_id} - Players hole cards:")
    for player in game.players:
        has_cards = player.hole_cards is not None and len(player.hole_cards) > 0
        cards_str = str([f"{c.rank}{c.suit}" for c in player.hole_cards]) if has_cards else "None"
        print(f"  Player {player.player_id}: has_hole_cards={has_cards}, cards={cards_str}")

    print(f"[Database Debug] Game {game_id} - action_history count: {len(game.action_history) if hasattr(game, 'action_history') else 0}")

    # 保存游戏数据到数据库
    try:
        await GameService.finish_game(db, game, winners)
        print(f"[Database] Game {game_id} finished and data saved successfully")
        return {"success": True, "winners": winners}
    except Exception as e:
        import traceback
        print(f"[Database] Failed to save finished game data: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"保存游戏数据失败: {str(e)}")


@router.post("/{game_id}/ai-action")
async def ai_single_action(game_id: str):
    """
    让当前玩家执行一次AI决策

    用于前端自动游戏功能
    """
    game = game_storage.load_game(game_id)
    if not game:
        raise HTTPException(status_code=404, detail="游戏不存在")
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

        response = {
            "success": True,
            "player_id": current_player.player_id,
            "player_type": player_type,
            "action": action,
            "amount": amount or 0,
            "game_state": game.get_state()
        }

        # 保存游戏状态
        save_game_state(game_id, game)

        # 广播AI动作
        await ws_manager.broadcast(game_id, {
            "type": "player_action",
            "data": response
        })

        return response
    except ValueError as e:
        # 记录详细错误信息
        print(f"[AI Action Error] Player {current_player.player_id}, Action: {action}, Amount: {amount}")
        print(f"[AI Action Error] Current bet: {game.current_bet}, Player bet: {current_player.current_bet}")
        print(f"[AI Action Error] Error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@router.websocket("/ws/{game_id}")
async def game_websocket(websocket: WebSocket, game_id: str):
    """游戏WebSocket连接"""
    await ws_manager.connect(game_id, websocket)

    try:
        while True:
            data = await websocket.receive_json()

            # 处理接收到的消息
            msg_type = data.get("type")

            if msg_type == "ping":
                await websocket.send_json({"type": "pong"})

            elif msg_type == "get_state":
                game = game_storage.load_game(game_id)
                if game:
                    await websocket.send_json({
                        "type": "game_state",
                        "data": game.get_state()
                    })

    except WebSocketDisconnect:
        ws_manager.disconnect(game_id, websocket)
    except Exception as e:
        ws_manager.disconnect(game_id, websocket)
