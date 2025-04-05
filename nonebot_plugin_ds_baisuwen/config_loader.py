import json
from pathlib import Path
from typing import Dict, Any
import importlib.resources

def load_character_config() -> Dict[str, Any]:
    # 使用 importlib.resources 安全访问包内文件
    with importlib.resources.path("nonebot_plugin_ds_baisuwen.data", "qq.json") as config_path:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)