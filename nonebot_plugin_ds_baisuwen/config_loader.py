import json
from pathlib import Path
from typing import Dict, Any

def load_character_config() -> Dict[str, Any]:
    config_path = Path(__file__).parent.parent.parent / "data" / "qq.json"
    
    # 默认配置（用户配置会覆盖这些值）
    default_config = {
        "name": "白苏文",
        "age": 14,
        "characteristics": [
            "狼族少女",
            "银色狼耳和尾巴",
            "编程高手",
            "喜欢恶作剧"
        ],
        "system_prompt": [
            "你叫{name}，回复要简短自然，像日常对话",
            "每句话控制在15字以内，避免复杂句式",
            "多用口语化表达：'好呀'、'不知道呢'、'要不要试试？'"
        ],
        "response_rules": {
            "max_tokens": 128
        },
        "voice_enabled": True,
        "vits_model_path": "D:/VITS/.../G_latest.pth",
        "vits_config_path": "D:/VITS/.../config.json",
        "response_rules": {
            "max_tokens":256
        }
    }
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            user_config = json.load(f)
        return {**default_config, **user_config}
    except Exception as e:
        print(f"配置加载失败，使用默认配置: {str(e)}")
        return default_config