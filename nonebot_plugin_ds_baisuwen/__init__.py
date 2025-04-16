from nonebot.plugin import PluginMetadata
from nonebot import logger, on_command, on_message,get_driver
from nonebot.internal.matcher import Matcher
from .voice_service import voice_service
from .message_handler import CHARACTER, combined_trigger
from .deepseek_service import DeepSeekAPI,_client
from .rate_limiter import RateLimiter
from .redis_handler import redis_client
from nonebot.adapters.onebot.v11 import (
    MessageEvent, 
    MessageSegment, 
    Message, 
    GroupMessageEvent
)
from nonebot.rule import Rule
from nonebot.params import CommandArg
from nonebot.permission import SUPERUSER

__version__ = "1.2.0"
__plugin_meta__ = PluginMetadata(
    name="赛博群友白苏文",
    description="基于DeepSeek的智能聊天机器人，打造属于你的赛博群友",
    usage="Ciallo～(∠・ω< )⌒★",
    type="application",
    homepage="https://github.com/Longxuanyue/nonebot_plugin_ds_baisuwen/",
    extra={},
)

driver = get_driver()
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

voice_switch = on_command(
    "语音模式", 
    aliases={"voice"}, 
    priority=5,
    permission=SUPERUSER
)

@voice_switch.handle()
async def handle_voice_switch(event: MessageEvent, arg: Message = CommandArg()):
    cmd = arg.extract_plain_text().strip().lower()
    if cmd in ["on", "开启"]:
        CHARACTER["voice_enabled"] = True
        msg = "语音回复已启用~ (≧∇≦)ﾉ"
    elif cmd in ["off", "关闭"]:
        CHARACTER["voice_enabled"] = False
        msg = "语音回复已关闭... (＞﹏＜)"
    else :
        msg = "无效的命令，请使用 `/语音模式 on` 或 `/语音模式 off` 来切换语音回复."
    await voice_switch.finish(msg)

@chat.handle()
async def handle_chat(event: MessageEvent):
    try:
        # 速率检查
        if not await limiter.check_limit(event):
            return await chat.finish("请求太频繁啦~ (>ω<)")
        
        user_id = event.get_user_id()
        history = await redis_client.get_history(user_id)
        
        # 生成文本回复
        api = DeepSeekAPI()
        response = await api.generate_response(
            prompt=event.get_plaintext(),
            history=history
        )
        
        # 构建复合消息（文本+语音）
        message1 = Message()
        message2 = Message()
        message1.append(MessageSegment.text(response))  # 显式添加文本段
        
        if CHARACTER["voice_enabled"] and voice_service:
            try:
                silk_path = await voice_service.text_to_speech(response)
                if silk_path and silk_path.exists():
                    # 使用URL编码路径
                    file_url = f"file:///{silk_path.as_posix()}"
                    message2.append(MessageSegment.record(file=file_url))
            except Exception as e:
                logger.error(f"语音生成失败: {str(e)}")
        
        is_group = isinstance(event, GroupMessageEvent)
        at_sender = not is_group
        
        # 原子化发送
        if message1:
            await chat.send(message1, at_sender=at_sender)
        if message2:
            if isinstance(message2, MessageSegment):
                pass
            else:
                await chat.send(message2, at_sender=at_sender)  # 发送语音消息

    except Exception as e:
        logger.error(f"全局异常 | {type(e).__name__}: {str(e)}")
        await chat.finish("消息发送失败，请通知管理员查看消息日志喵……(＞﹏＜)")