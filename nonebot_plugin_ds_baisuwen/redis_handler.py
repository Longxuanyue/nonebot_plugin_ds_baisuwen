import json
from redis import asyncio as aioredis
from nonebot import get_driver, logger
from typing import Optional

driver = get_driver()

class RedisClient:
    def __init__(self):
        self.redis = aioredis.from_url(
            driver.config.redis_url,
            decode_responses=False  # 二进制数据需要关闭解码
        )
        self.history_size = 5
        self.voice_cache_ttl = 3600  # 语音缓存1小时

    async def test_connection(self):
        try:
            await self.redis.ping()
            logger.success("Redis连接成功")
            return True
        except Exception as e:
            logger.error(f"Redis连接失败：{str(e)}")
            return False
    
    # 对话历史功能
    async def add_message(self, user_id: str, role: str, content: str):
        key = f"chat:{user_id}"
        message = json.dumps({"role": role, "content": content})
        await self.redis.lpush(key, message)
        await self.redis.ltrim(key, 0, self.history_size-1)
        await self.redis.expire(key, 3600*24)

    async def get_history(self, user_id: str) -> list:
        key = f"chat:{user_id}"
        history = await self.redis.lrange(key, 0, -1)
        return [json.loads(msg) for msg in reversed(history)]
    
    # 语音缓存功能
    async def cache_voice(self, text: str, audio_data: bytes):
        """缓存语音数据"""
        key = f"voice:{text}"
        await self.redis.setex(key, self.voice_cache_ttl, audio_data)

    async def get_cached_voice(self, text: str) -> Optional[bytes]:
        """获取缓存的语音"""
        key = f"voice:{text}"
        return await self.redis.get(key)

@driver.on_startup
async def init_redis():
    if not await redis_client.test_connection():
        raise RuntimeError("Redis连接异常")

redis_client = RedisClient()