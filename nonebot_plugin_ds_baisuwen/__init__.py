from nonebot.plugin import PluginMetadata
from nonebot import logger, on_message,get_driver
from nonebot.internal.matcher import Matcher
from .message_handler import combined_trigger
from .deepseek_service import DeepSeekAPI,_client
from .rate_limiter import RateLimiter
from .redis_handler import redis_client
from nonebot.adapters.onebot.v11 import MessageEvent, GroupMessageEvent, PrivateMessageEvent
from nonebot.rule import Rule

__version__ = "1.1.8"
__plugin_meta__ = PluginMetadata(
    name="赛博群友白苏文",
    description="基于DeepSeek的智能聊天机器人，打造属于你的赛博群友",
    usage="Ciallo～(∠・ω< )⌒★",
    type="application",
    homepage="https://github.com/KarisAya/nonebot_plugin_ds_baisuwen/",
    supported_adapters={"~onebot.v11"},  # 修正适配器标识符
    extra={
        "version": __version__
    }
)

driver = get_driver()
chat = on_message(rule=combined_trigger, priority=10, block=True)
limiter = RateLimiter()

@driver.on_shutdown
async def close_client():
    """关闭HTTP客户端"""
    await _client.aclose()
    logger.info("HTTP客户端已关闭")

chat = on_message(
    rule=Rule(combined_trigger),  # 直接应用组合规则
    priority=10,
    block=True
)

limiter = RateLimiter()

@chat.handle()
async def handle_chat(event: MessageEvent):
    # 检查速率限制
    if not await limiter.check_limit(event):
        return await chat.finish("请求太频繁啦~ (>ω<)")
    
    # 获取用户ID和历史记录
    user_id = event.get_user_id()
    history = await redis_client.get_history(user_id)
    
    # 调用DeepSeek API
    api = DeepSeekAPI()
    response = await api.generate_response(
        prompt=event.get_plaintext(),
        history=history
    )
    
    # 存储对话记录
    await redis_client.add_message(user_id, "user", event.get_plaintext())
    await redis_client.add_message(user_id, "assistant", response)
    
    await chat.finish(response)
