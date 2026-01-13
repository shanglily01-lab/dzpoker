"""游戏数据分析服务"""
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, desc
from sqlalchemy.orm import selectinload

from ..models import Game, Hand, Action, Player, PlayerStats


class AnalyticsService:
    """游戏数据分析服务"""

    @staticmethod
    async def get_game_history(
        db: AsyncSession,
        limit: int = 50,
        offset: int = 0,
        status: Optional[str] = None
    ) -> Dict:
        """
        获取游戏历史记录

        Args:
            db: 数据库会话
            limit: 返回数量
            offset: 偏移量
            status: 游戏状态筛选 (finished/playing/waiting)

        Returns:
            游戏历史列表和统计信息
        """
        # 构建查询
        query = select(Game).options(
            selectinload(Game.hands)
        ).order_by(desc(Game.started_at))

        if status:
            query = query.where(Game.status == status)

        # 分页
        query = query.limit(limit).offset(offset)

        result = await db.execute(query)
        games = result.scalars().all()

        # 统计信息
        total_query = select(func.count(Game.id))
        if status:
            total_query = total_query.where(Game.status == status)
        total_result = await db.execute(total_query)
        total = total_result.scalar()

        return {
            "games": [
                {
                    "id": g.id,
                    "game_uuid": g.game_uuid,
                    "num_players": g.num_players,
                    "small_blind": g.small_blind,
                    "big_blind": g.big_blind,
                    "total_pot": g.total_pot,
                    "winner_id": g.winner_id,
                    "status": g.status,
                    "started_at": g.started_at.isoformat() if g.started_at else None,
                    "ended_at": g.ended_at.isoformat() if g.ended_at else None,
                    "duration": (g.ended_at - g.started_at).total_seconds() if g.ended_at and g.started_at else None,
                    "hands_count": len(g.hands)
                }
                for g in games
            ],
            "total": total,
            "limit": limit,
            "offset": offset
        }

    @staticmethod
    async def get_game_detail(
        db: AsyncSession,
        game_id: int
    ) -> Optional[Dict]:
        """
        获取游戏详细信息（包括所有手牌和动作）

        Args:
            db: 数据库会话
            game_id: 游戏ID

        Returns:
            游戏详细信息
        """
        result = await db.execute(
            select(Game)
            .options(
                selectinload(Game.hands).selectinload(Hand.actions)
            )
            .where(Game.id == game_id)
        )
        game = result.scalar_one_or_none()

        if not game:
            return None

        return {
            "id": game.id,
            "game_uuid": game.game_uuid,
            "num_players": game.num_players,
            "small_blind": game.small_blind,
            "big_blind": game.big_blind,
            "total_pot": game.total_pot,
            "winner_id": game.winner_id,
            "status": game.status,
            "started_at": game.started_at.isoformat() if game.started_at else None,
            "ended_at": game.ended_at.isoformat() if game.ended_at else None,
            "hands": [
                {
                    "id": h.id,
                    "player_id": h.player_id,
                    "position": h.position,
                    "hole_cards": h.hole_cards,
                    "final_hand": h.final_hand,
                    "profit_loss": h.profit_loss,
                    "is_winner": h.is_winner,
                    "actions": [
                        {
                            "street": a.street,
                            "action_type": a.action_type,
                            "amount": a.amount,
                            "pot_size": a.pot_size,
                            "created_at": a.created_at.isoformat() if a.created_at else None
                        }
                        for a in h.actions
                    ]
                }
                for h in game.hands
            ]
        }

    @staticmethod
    async def get_player_stats(
        db: AsyncSession,
        player_id: int
    ) -> Optional[Dict]:
        """
        获取玩家统计信息

        Args:
            db: 数据库会话
            player_id: 玩家ID

        Returns:
            玩家统计信息
        """
        result = await db.execute(
            select(PlayerStats)
            .options(selectinload(PlayerStats.player))
            .where(PlayerStats.player_id == player_id)
        )
        stats = result.scalar_one_or_none()

        if not stats:
            return None

        # 获取最近手牌记录
        hands_result = await db.execute(
            select(Hand)
            .where(Hand.player_id == player_id)
            .order_by(desc(Hand.created_at))
            .limit(20)
        )
        recent_hands = hands_result.scalars().all()

        return {
            "player_id": player_id,
            "total_games": stats.total_games,
            "total_hands": stats.total_hands,
            "wins": stats.wins,
            "win_rate": stats.win_rate,
            "total_profit": stats.total_profit,
            "vpip": stats.vpip,
            "pfr": stats.pfr,
            "af": stats.af,
            "updated_at": stats.updated_at.isoformat() if stats.updated_at else None,
            "recent_hands": [
                {
                    "game_id": h.game_id,
                    "position": h.position,
                    "hole_cards": h.hole_cards,
                    "final_hand": h.final_hand,
                    "profit_loss": h.profit_loss,
                    "is_winner": h.is_winner,
                    "created_at": h.created_at.isoformat() if h.created_at else None
                }
                for h in recent_hands
            ]
        }

    @staticmethod
    async def get_overall_statistics(
        db: AsyncSession,
        days: int = 30
    ) -> Dict:
        """
        获取整体统计数据

        Args:
            db: 数据库会话
            days: 统计最近多少天的数据

        Returns:
            整体统计信息
        """
        start_date = datetime.utcnow() - timedelta(days=days)

        # 总游戏数
        total_games_result = await db.execute(
            select(func.count(Game.id))
            .where(Game.started_at >= start_date)
        )
        total_games = total_games_result.scalar()

        # 已完成游戏数
        finished_games_result = await db.execute(
            select(func.count(Game.id))
            .where(and_(
                Game.status == "finished",
                Game.started_at >= start_date
            ))
        )
        finished_games = finished_games_result.scalar()

        # 总底池
        total_pot_result = await db.execute(
            select(func.sum(Game.total_pot))
            .where(and_(
                Game.status == "finished",
                Game.started_at >= start_date
            ))
        )
        total_pot = total_pot_result.scalar() or 0

        # 平均游戏时长
        avg_duration_result = await db.execute(
            select(func.avg(
                func.extract('epoch', Game.ended_at - Game.started_at)
            ))
            .where(and_(
                Game.status == "finished",
                Game.started_at >= start_date,
                Game.ended_at.isnot(None)
            ))
        )
        avg_duration = avg_duration_result.scalar()

        # 总手牌数
        total_hands_result = await db.execute(
            select(func.count(Hand.id))
            .join(Game)
            .where(Game.started_at >= start_date)
        )
        total_hands = total_hands_result.scalar()

        # 最大底池游戏
        max_pot_game_result = await db.execute(
            select(Game)
            .where(and_(
                Game.status == "finished",
                Game.started_at >= start_date
            ))
            .order_by(desc(Game.total_pot))
            .limit(1)
        )
        max_pot_game = max_pot_game_result.scalar_one_or_none()

        return {
            "period_days": days,
            "total_games": total_games,
            "finished_games": finished_games,
            "total_pot": float(total_pot),
            "avg_duration_seconds": float(avg_duration) if avg_duration else None,
            "total_hands": total_hands,
            "max_pot_game": {
                "game_uuid": max_pot_game.game_uuid,
                "total_pot": max_pot_game.total_pot,
                "started_at": max_pot_game.started_at.isoformat() if max_pot_game.started_at else None
            } if max_pot_game else None
        }

    @staticmethod
    async def get_hand_type_distribution(
        db: AsyncSession,
        limit: int = 100
    ) -> Dict:
        """
        获取手牌类型分布统计

        Args:
            db: 数据库会话
            limit: 统计最近多少局游戏

        Returns:
            手牌类型分布
        """
        # 获取最近的手牌记录
        result = await db.execute(
            select(Hand)
            .where(Hand.final_hand.isnot(None))
            .order_by(desc(Hand.created_at))
            .limit(limit)
        )
        hands = result.scalars().all()

        # 统计牌型分布
        hand_type_counts = {}
        for hand in hands:
            if hand.final_hand:
                # 提取牌型名称（去掉具体点数）
                hand_type = hand.final_hand.split('(')[0].strip() if '(' in hand.final_hand else hand.final_hand
                hand_type_counts[hand_type] = hand_type_counts.get(hand_type, 0) + 1

        return {
            "total_hands": len(hands),
            "distribution": [
                {"hand_type": k, "count": v, "percentage": (v / len(hands) * 100) if hands else 0}
                for k, v in sorted(hand_type_counts.items(), key=lambda x: x[1], reverse=True)
            ]
        }

    @staticmethod
    async def get_position_analysis(
        db: AsyncSession,
        limit: int = 100
    ) -> Dict:
        """
        获取位置分析（各位置的胜率）

        Args:
            db: 数据库会话
            limit: 统计最近多少局

        Returns:
            位置胜率分析
        """
        result = await db.execute(
            select(Hand)
            .order_by(desc(Hand.created_at))
            .limit(limit)
        )
        hands = result.scalars().all()

        position_stats = {}
        for hand in hands:
            pos = hand.position
            if pos not in position_stats:
                position_stats[pos] = {"total": 0, "wins": 0, "profit": 0.0}

            position_stats[pos]["total"] += 1
            if hand.is_winner:
                position_stats[pos]["wins"] += 1
            position_stats[pos]["profit"] += hand.profit_loss

        position_names = {0: "BTN", 1: "SB", 2: "BB", 3: "UTG", 4: "MP", 5: "CO"}

        return {
            "total_hands": len(hands),
            "positions": [
                {
                    "position": pos,
                    "position_name": position_names.get(pos, f"P{pos+1}"),
                    "total": stats["total"],
                    "wins": stats["wins"],
                    "win_rate": (stats["wins"] / stats["total"] * 100) if stats["total"] > 0 else 0,
                    "avg_profit": stats["profit"] / stats["total"] if stats["total"] > 0 else 0
                }
                for pos, stats in sorted(position_stats.items())
            ]
        }
