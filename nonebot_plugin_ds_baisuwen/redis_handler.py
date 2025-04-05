import json
from redis import asyncio as aioredis
from nonebot import get_driver, logger

driver = get_driver()

class RedisClient:
    def __init__(self):
        self.redis = aioredis.from_url(
            driver.config.redis_url,
            decode_responses=True
        )
        self.history_size = 5  # 保留最近5条对话
        
    async def test_connection(self):
        try:
            await self.redis.ping()
            logger.success("Redis连接成功")
            return True
        except Exception as e:
            logger.error(f"Redis连接失败：{str(e)}")
            return False
    
    async def add_message(self, user_id: str, role: str, content: str):
        key = f"chat:{user_id}"
        message = json.dumps({"role": role, "content": content})
        await self.redis.lpush(key, message)
        await self.redis.ltrim(key, 0, self.history_size-1)
        await self.redis.expire(key, 3600*24)  # 保留24小时
    
    async def get_history(self, user_id: str) -> list:
        key = f"chat:{user_id}"
        history = await self.redis.lrange(key, 0, -1)
        return [json.loads(msg) for msg in reversed(history)]

@driver.on_startup
async def init_redis():
    if not await redis_client.test_connection():
        raise RuntimeError("Redis连接异常")

redis_client = RedisClient()