"""Pydantic模型 - 请求/响应数据验证"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# ==================== 玩家相关 ====================

class PlayerCreate(BaseModel):
    """创建玩家请求"""
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)
    nickname: Optional[str] = None


class PlayerResponse(BaseModel):
    """玩家响应"""
    id: int
    username: str
    nickname: Optional[str]
    chips: float
    level: int
    created_at: datetime

    class Config:
        from_attributes = True


class PlayerStatsResponse(BaseModel):
    """玩家统计响应"""
    total_games: int
    total_hands: int
    wins: int
    vpip: float
    pfr: float
    af: float
    win_rate: float
    total_profit: float

    class Config:
        from_attributes = True


# ==================== 认证相关 ====================

class Token(BaseModel):
    """Token响应"""
    access_token: str
    token_type: str = "bearer"


class LoginRequest(BaseModel):
    """登录请求"""
    username: str
    password: str


# ==================== 游戏相关 ====================

class CreateGameRequest(BaseModel):
    """创建游戏请求"""
    num_players: int = Field(..., ge=2, le=10)
    small_blind: float = Field(default=1.0, gt=0)
    big_blind: float = Field(default=2.0, gt=0)


class GameResponse(BaseModel):
    """游戏响应"""
    game_id: str
    num_players: int
    small_blind: float
    big_blind: float
    status: str
    pot: float = 0


class CardResponse(BaseModel):
    """扑克牌响应"""
    suit: int  # 0-3 (黑桃、红心、方块、梅花)
    rank: int  # 0-12 (2-A)
    display: str  # 显示文字 如 "A♠"


class DealResponse(BaseModel):
    """发牌响应"""
    hole_cards: List[List[CardResponse]]
    deck_remaining: int


class CommunityCardsResponse(BaseModel):
    """公共牌响应"""
    cards: List[CardResponse]
    street: str  # flop, turn, river


# ==================== 玩家动作 ====================

class PlayerActionRequest(BaseModel):
    """玩家动作请求"""
    player_id: int
    action: str = Field(..., pattern="^(fold|call|raise|check|all_in)$")
    amount: Optional[float] = None


class GameStateResponse(BaseModel):
    """游戏状态响应"""
    game_id: str
    status: str
    current_player: Optional[int]
    pot: float
    community_cards: List[CardResponse]
    players: List[dict]
