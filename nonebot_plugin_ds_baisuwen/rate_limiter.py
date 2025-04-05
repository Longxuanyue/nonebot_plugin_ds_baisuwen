from datetime import timedelta
from nonebot import get_driver
from .redis_handler import redis_client
from nonebot.adapters.onebot.v11 import MessageEvent, GroupMessageEvent

class RateLimiter:
    def __init__(self):
        self.limit_config = {
            "user": (5, timedelta(minutes=1)),  # 用户级限制
            "group": (20, timedelta(minutes=1)) # 群组级限制
        }
    
    async def check_limit(self, event: MessageEvent) -> bool:
        identifier = self._get_identifier(event)
        limit, delta = self.limit_config.get(
            "group" if isinstance(event, GroupMessageEvent) else "user",
            (5, timedelta(minutes=1))
        )
        
        key = f"rate:{identifier}"
        count = await redis_client.redis.get(key) or 0
        if int(count) >= limit:
            return False
        
        await redis_client.redis.incr(key)
        await redis_client.redis.expire(key, delta.seconds)
        return True
    
    def _get_identifier(self, event):
        if isinstance(event, GroupMessageEvent):
            return f"group:{event.group_id}"
        return f"user:{event.user_id}"