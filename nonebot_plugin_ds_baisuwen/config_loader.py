import json
from pathlib import Path
from typing import Dict, Any

def load_character_config() -> Dict[str, Any]:
    config_path = Path(__file__).parent.parent.parent / "data" / "qq.json"
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)
