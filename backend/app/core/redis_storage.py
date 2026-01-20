"""Redis 游戏状态存储"""
import pickle
import redis
from typing import Optional
from fastapi import HTTPException

from .poker import PokerGame


class RedisGameStorage:
    """Redis 游戏状态存储"""

    def __init__(self, redis_url: str = "redis://redis:6379/0"):
        """
        初始化 Redis 存储

        Args:
            redis_url: Redis 连接 URL
        """
        try:
            self.redis_client = redis.from_url(redis_url, decode_responses=False)
            # 测试连接
            self.redis_client.ping()
            print(f"✅ Redis 游戏存储初始化成功: {redis_url}")
        except Exception as e:
            print(f"⚠️  Redis 连接失败，使用内存存储: {e}")
            self.redis_client = None

        # 内存备份（Redis 不可用时使用）
        self._memory_storage = {}

    def save_game(self, game_id: str, game: PokerGame, ttl: int = 3600):
        """
        保存游戏状态

        Args:
            game_id: 游戏 ID
            game: 游戏对象
            ttl: 过期时间（秒），默认 1 小时
        """
        key = f"game:{game_id}"

        try:
            if self.redis_client:
                # 使用 Redis 存储
                serialized = pickle.dumps(game)
                self.redis_client.setex(key, ttl, serialized)
            else:
                # 使用内存存储
                self._memory_storage[game_id] = game
        except Exception as e:
            print(f"⚠️  Redis 保存失败，使用内存备份: {e}")
            self._memory_storage[game_id] = game

    def load_game(self, game_id: str) -> Optional[PokerGame]:
        """
        加载游戏状态

        Args:
            game_id: 游戏 ID

        Returns:
            游戏对象，如果不存在返回 None
        """
        key = f"game:{game_id}"

        try:
            if self.redis_client:
                # 从 Redis 加载
                data = self.redis_client.get(key)
                if data:
                    return pickle.loads(data)

            # 从内存加载
            return self._memory_storage.get(game_id)
        except Exception as e:
            print(f"⚠️  Redis 加载失败，尝试内存: {e}")
            return self._memory_storage.get(game_id)

    def delete_game(self, game_id: str):
        """
        删除游戏状态

        Args:
            game_id: 游戏 ID
        """
        key = f"game:{game_id}"

        try:
            if self.redis_client:
                self.redis_client.delete(key)

            if game_id in self._memory_storage:
                del self._memory_storage[game_id]
        except Exception as e:
            print(f"⚠️  Redis 删除失败: {e}")

    def exists(self, game_id: str) -> bool:
        """
        检查游戏是否存在

        Args:
            game_id: 游戏 ID

        Returns:
            是否存在
        """
        key = f"game:{game_id}"

        try:
            if self.redis_client:
                return self.redis_client.exists(key) > 0

            return game_id in self._memory_storage
        except Exception as e:
            print(f"⚠️  Redis 检查失败: {e}")
            return game_id in self._memory_storage

    def get_all_game_ids(self) -> list:
        """
        获取所有游戏 ID

        Returns:
            游戏 ID 列表
        """
        try:
            if self.redis_client:
                keys = self.redis_client.keys("game:*")
                return [k.decode().replace("game:", "") for k in keys]

            return list(self._memory_storage.keys())
        except Exception as e:
            print(f"⚠️  Redis 获取失败: {e}")
            return list(self._memory_storage.keys())


# 全局实例
game_storage = RedisGameStorage()
