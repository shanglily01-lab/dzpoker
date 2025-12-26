"""玩家相关API路由"""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt
from typing import Optional

from ..core.database import get_db
from ..core.config import settings
from ..models import Player, PlayerStats
from ..schemas import (
    PlayerCreate, PlayerResponse, PlayerStatsResponse,
    Token, LoginRequest
)
from ..ai.analyzer import player_analyzer, PlayerProfile

router = APIRouter(prefix="/api/players", tags=["players"])

# 密码加密
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """加密密码"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """创建JWT Token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


@router.post("/register", response_model=PlayerResponse)
async def register(player: PlayerCreate, db: AsyncSession = Depends(get_db)):
    """注册新玩家"""
    # 检查用户名是否已存在
    result = await db.execute(
        select(Player).where(Player.username == player.username)
    )
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="用户名已存在")

    # 创建玩家
    new_player = Player(
        username=player.username,
        nickname=player.nickname or player.username,
        password_hash=hash_password(player.password),
        chips=10000.0
    )

    db.add(new_player)
    await db.commit()
    await db.refresh(new_player)

    # 创建统计记录
    stats = PlayerStats(player_id=new_player.id)
    db.add(stats)
    await db.commit()

    return new_player


@router.post("/login", response_model=Token)
async def login(request: LoginRequest, db: AsyncSession = Depends(get_db)):
    """玩家登录"""
    result = await db.execute(
        select(Player).where(Player.username == request.username)
    )
    player = result.scalar_one_or_none()

    if not player or not verify_password(request.password, player.password_hash):
        raise HTTPException(status_code=401, detail="用户名或密码错误")

    access_token = create_access_token(
        data={"sub": player.username, "player_id": player.id},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    return Token(access_token=access_token)


@router.get("/{player_id}", response_model=PlayerResponse)
async def get_player(player_id: int, db: AsyncSession = Depends(get_db)):
    """获取玩家信息"""
    result = await db.execute(
        select(Player).where(Player.id == player_id)
    )
    player = result.scalar_one_or_none()

    if not player:
        raise HTTPException(status_code=404, detail="玩家不存在")

    return player


@router.get("/{player_id}/stats", response_model=PlayerStatsResponse)
async def get_player_stats(player_id: int, db: AsyncSession = Depends(get_db)):
    """获取玩家统计数据"""
    result = await db.execute(
        select(PlayerStats).where(PlayerStats.player_id == player_id)
    )
    stats = result.scalar_one_or_none()

    if not stats:
        raise HTTPException(status_code=404, detail="玩家统计不存在")

    return stats


@router.get("/{player_id}/profile")
async def get_player_profile(player_id: int, db: AsyncSession = Depends(get_db)):
    """获取玩家AI画像分析"""
    # 获取玩家统计
    result = await db.execute(
        select(PlayerStats).where(PlayerStats.player_id == player_id)
    )
    stats = result.scalar_one_or_none()

    if not stats:
        raise HTTPException(status_code=404, detail="玩家不存在")

    # 构建统计数据
    stats_dict = {
        "vpip": stats.vpip,
        "pfr": stats.pfr,
        "af": stats.af,
        "three_bet": 0,
        "wtsd": 25,
        "total_hands": stats.total_hands
    }

    # AI分析
    player_type = player_analyzer.classify_player(stats_dict)
    skill_level = player_analyzer.evaluate_skill(stats_dict)

    profile = PlayerProfile(
        player_id=player_id,
        player_type=player_type,
        skill_level=skill_level,
        vpip=stats.vpip,
        pfr=stats.pfr,
        af=stats.af,
        three_bet=0,
        wtsd=25,
        total_hands=stats.total_hands
    )

    recommendations = player_analyzer.get_recommendations(profile)

    return {
        "player_id": player_id,
        "player_type": player_type.value,
        "skill_level": skill_level,
        "stats": stats_dict,
        "recommendations": recommendations
    }


@router.get("")
async def list_players(
    skip: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_db)
):
    """获取玩家列表"""
    result = await db.execute(
        select(Player)
        .order_by(Player.chips.desc())
        .offset(skip)
        .limit(limit)
    )
    players = result.scalars().all()

    return {
        "players": [
            {
                "id": p.id,
                "username": p.username,
                "nickname": p.nickname,
                "chips": p.chips,
                "level": p.level
            }
            for p in players
        ],
        "total": len(players)
    }
