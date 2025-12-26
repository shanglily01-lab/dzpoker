"""Redis连接配置"""
import redis.asyncio as redis
import json
from typing import Optional, Any
from .config import settings


class RedisClient:
    """Redis客户端封装"""

    def __init__(self):
        self.client: Optional[redis.Redis] = None

    async def connect(self):
        """连接Redis"""
        self.client = redis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True
        )

    async def disconnect(self):
        """断开连接"""
        if self.client:
            await self.client.close()

    async def set(self, key: str, value: Any, expire: int = 3600):
        """设置缓存"""
        if isinstance(value, (dict, list)):
            value = json.dumps(value, ensure_ascii=False)
        await self.client.setex(key, expire, value)

    async def get(self, key: str) -> Optional[Any]:
        """获取缓存"""
        value = await self.client.get(key)
        if value:
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
        return None

    async def delete(self, key: str):
        """删除缓存"""
        await self.client.delete(key)

    async def exists(self, key: str) -> bool:
        """检查键是否存在"""
        return await self.client.exists(key)


# 全局Redis客户端
redis_client = RedisClient()
