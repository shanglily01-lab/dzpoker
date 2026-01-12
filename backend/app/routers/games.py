"""游戏相关API路由"""
from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from typing import Dict, List
import uuid

from ..schemas import (
    CreateGameRequest, GameResponse, CardResponse,
    PlayerActionRequest, GameStateResponse
)
from ..core.poker import PokerGame, GameState
from ..ai.smart_dealer import smart_dealer
from ..ai.decision_maker import ai_decision_maker

router = APIRouter(prefix="/api/games", tags=["games"])

# 游戏存储 (生产环境应使用Redis)
games: Dict[str, PokerGame] = {}

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

    games[game_id] = game

    return GameResponse(
        game_id=game_id,
        num_players=request.num_players,
        small_blind=request.small_blind,
        big_blind=request.big_blind,
        status=game.state.value,
        pot=game.pot
    )


@router.get("/{game_id}")
async def get_game(game_id: str):
    """获取游戏状态"""
    if game_id not in games:
        raise HTTPException(status_code=404, detail="游戏不存在")

    game = games[game_id]
    return game.get_state()


@router.post("/{game_id}/start")
async def start_game(game_id: str):
    """开始游戏"""
    if game_id not in games:
        raise HTTPException(status_code=404, detail="游戏不存在")

    game = games[game_id]

    try:
        game.start_hand()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

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
    if game_id not in games:
        raise HTTPException(status_code=404, detail="游戏不存在")

    game = games[game_id]

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

    # 广播发牌结果
    await ws_manager.broadcast(game_id, {
        "type": "cards_dealt",
        "data": response
    })

    return response


@router.post("/{game_id}/flop")
async def deal_flop(game_id: str):
    """发翻牌"""
    if game_id not in games:
        raise HTTPException(status_code=404, detail="游戏不存在")

    game = games[game_id]

    try:
        flop = game.deal_flop()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    response = {
        "cards": [card.to_dict() for card in flop],
        "street": "flop"
    }

    await ws_manager.broadcast(game_id, {
        "type": "community_cards",
        "data": response
    })

    return response


@router.post("/{game_id}/turn")
async def deal_turn(game_id: str):
    """发转牌"""
    if game_id not in games:
        raise HTTPException(status_code=404, detail="游戏不存在")

    game = games[game_id]

    try:
        turn = game.deal_turn()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    response = {
        "card": turn.to_dict(),
        "street": "turn"
    }

    await ws_manager.broadcast(game_id, {
        "type": "community_cards",
        "data": response
    })

    return response


@router.post("/{game_id}/river")
async def deal_river(game_id: str):
    """发河牌"""
    if game_id not in games:
        raise HTTPException(status_code=404, detail="游戏不存在")

    game = games[game_id]

    try:
        river = game.deal_river()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    response = {
        "card": river.to_dict(),
        "street": "river"
    }

    await ws_manager.broadcast(game_id, {
        "type": "community_cards",
        "data": response
    })

    return response


@router.post("/{game_id}/action")
async def player_action(game_id: str, action: PlayerActionRequest):
    """处理玩家动作"""
    if game_id not in games:
        raise HTTPException(status_code=404, detail="游戏不存在")

    game = games[game_id]

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

    await ws_manager.broadcast(game_id, {
        "type": "player_action",
        "data": response
    })

    return response


@router.post("/{game_id}/showdown")
async def showdown(game_id: str):
    """执行摊牌并确定获胜者"""
    if game_id not in games:
        raise HTTPException(status_code=404, detail="游戏不存在")

    game = games[game_id]

    try:
        result = game.showdown()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # 广播摊牌结果
    await ws_manager.broadcast(game_id, {
        "type": "showdown",
        "data": result
    })

    return result


@router.post("/{game_id}/ai-action")
async def ai_single_action(game_id: str):
    """
    让当前玩家执行一次AI决策

    用于前端自动游戏功能
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

        response = {
            "success": True,
            "player_id": current_player.player_id,
            "player_type": player_type,
            "action": action,
            "amount": amount or 0,
            "game_state": game.get_state()
        }

        # 广播AI动作
        await ws_manager.broadcast(game_id, {
            "type": "player_action",
            "data": response
        })

        return response
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/stats")
async def get_game_stats():
    """获取游戏统计数据"""
    total_games = len(games)
    active_games = sum(1 for g in games.values() if g.state not in [GameState.WAITING, GameState.FINISHED])
    finished_games = sum(1 for g in games.values() if g.state == GameState.FINISHED)

    # 统计总玩家数（去重）
    all_players = set()
    total_hands = 0
    total_pot = 0

    for game in games.values():
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

    for game_id, game in games.items():
        # 状态过滤
        if state and game.state.value != state:
            continue

        game_info = {
            "game_id": game_id,
            "num_players": len(game.players),
            "state": game.state.value,
            "pot": game.pot,
            "current_bet": game.current_bet,
            "blind": game.blind,
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
                if game_id in games:
                    await websocket.send_json({
                        "type": "game_state",
                        "data": games[game_id].get_state()
                    })

    except WebSocketDisconnect:
        ws_manager.disconnect(game_id, websocket)
    except Exception as e:
        ws_manager.disconnect(game_id, websocket)
