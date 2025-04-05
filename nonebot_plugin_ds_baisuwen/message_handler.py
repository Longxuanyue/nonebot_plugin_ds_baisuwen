from nonebot.adapters.onebot.v11 import MessageEvent, GroupMessageEvent, PrivateMessageEvent
from nonebot import get_driver, logger
from .config_loader import load_character_config

CHARACTER = load_character_config()
driver = get_driver()

async def combined_trigger(event: MessageEvent) -> bool:
    text = event.get_plaintext().lstrip()
    if isinstance(event, GroupMessageEvent):
        # 群聊触发条件
        return event.is_tome() or event.get_plaintext().startswith(CHARACTER["name"])
    elif isinstance(event, PrivateMessageEvent):
        # 私聊触发条件
        return True
    return False

# async def _is_friend(user_id: int) -> bool:
#     """异步检测好友状态"""
#     try:
#         friend_list = await driver.bot.get_friend_list()
#         return any(friend["user_id"] == user_id for friend in friend_list)
#     except Exception as e:
#         logger.error(f"好友检测失败: {str(e)}")
#         return False