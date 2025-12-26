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
