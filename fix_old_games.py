"""
批量修复历史游戏数据
将所有"进行中"状态的旧游戏标记为已完成
"""
import asyncio
import sys
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta

# 添加backend路径
sys.path.insert(0, '/app')

from app.models import Game, Hand
from app.core.database import get_db_url

async def fix_old_games():
    """修复旧游戏数据"""
    # 创建数据库连接
    engine = create_async_engine(get_db_url(), echo=True)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as db:
        # 查找所有"进行中"但已经超过1小时的游戏
        one_hour_ago = datetime.utcnow() - timedelta(hours=1)

        result = await db.execute(
            select(Game).where(
                Game.status == 'playing',
                Game.started_at < one_hour_ago
            )
        )
        old_games = result.scalars().all()

        print(f"\n找到 {len(old_games)} 个需要修复的旧游戏")

        for game in old_games:
            print(f"\n修复游戏 {game.game_uuid}:")
            print(f"  - 开始时间: {game.started_at}")
            print(f"  - 当前状态: {game.status}")

            # 检查是否已有手牌数据
            hands_result = await db.execute(
                select(Hand).where(Hand.game_id == game.id)
            )
            hands = hands_result.scalars().all()

            print(f"  - 已有手牌数: {len(hands)}")

            # 更新游戏状态为已完成
            game.status = 'finished'
            game.ended_at = game.started_at + timedelta(minutes=5)  # 假设每局5分钟

            print(f"  ✓ 已标记为finished")

        # 提交所有更改
        await db.commit()
        print(f"\n✅ 成功修复 {len(old_games)} 个游戏！")

if __name__ == "__main__":
    asyncio.run(fix_old_games())
