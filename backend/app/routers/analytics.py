"""数据分析API路由"""
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from ..core.database import get_db
from ..services.analytics_service import AnalyticsService

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


@router.get("/games")
async def get_game_history(
    db: AsyncSession = Depends(get_db),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    status: Optional[str] = Query(None, regex="^(finished|playing|waiting)$")
):
    """
    获取游戏历史记录

    Args:
        limit: 返回数量 (1-200)
        offset: 偏移量
        status: 游戏状态筛选 (finished/playing/waiting)
    """
    return await AnalyticsService.get_game_history(db, limit, offset, status)


@router.get("/games/{game_id}")
async def get_game_detail(
    game_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    获取游戏详细信息（包括所有手牌和动作）

    Args:
        game_id: 游戏ID
    """
    result = await AnalyticsService.get_game_detail(db, game_id)
    if not result:
        raise HTTPException(status_code=404, detail="游戏不存在")
    return result


@router.get("/players/{player_id}/stats")
async def get_player_stats(
    player_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    获取玩家统计信息

    Args:
        player_id: 玩家ID
    """
    result = await AnalyticsService.get_player_stats(db, player_id)
    if not result:
        raise HTTPException(status_code=404, detail="玩家统计不存在")
    return result


@router.get("/overview")
async def get_overall_statistics(
    db: AsyncSession = Depends(get_db),
    days: int = Query(30, ge=1, le=365)
):
    """
    获取整体统计数据

    Args:
        days: 统计最近多少天的数据 (1-365)
    """
    return await AnalyticsService.get_overall_statistics(db, days)


@router.get("/hand-types")
async def get_hand_type_distribution(
    db: AsyncSession = Depends(get_db),
    limit: int = Query(100, ge=10, le=1000)
):
    """
    获取手牌类型分布统计

    Args:
        limit: 统计最近多少局游戏 (10-1000)
    """
    return await AnalyticsService.get_hand_type_distribution(db, limit)


@router.get("/positions")
async def get_position_analysis(
    db: AsyncSession = Depends(get_db),
    limit: int = Query(100, ge=10, le=1000)
):
    """
    获取位置分析（各位置的胜率）

    Args:
        limit: 统计最近多少局 (10-1000)
    """
    return await AnalyticsService.get_position_analysis(db, limit)
