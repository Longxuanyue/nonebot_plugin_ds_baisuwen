import random
from typing import Optional
import httpx
import time
from typing import Optional
from nonebot import get_driver, logger
from tenacity import retry, stop_after_attempt, wait_exponential
from .config_loader import load_character_config
from .redis_handler import redis_client

config = load_character_config()
driver = get_driver()

_client = httpx.AsyncClient(
    http2=True,
    timeout=30.0,
    limits=httpx.Limits(
        max_keepalive_connections=50,
        max_connections=200
    )
)

class DeepSeekAPI:
    def __init__(self):
        self.api_key = driver.config.deepseek_api_key
        self.base_url = driver.config.deepseek_api_base.rstrip('/')
        self.cached_system_prompt = None  # 预加载后填充

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        reraise=True
    )
    async def generate_response(self, prompt: str, history: list) -> Optional[str]:
        """带重试机制的API请求方法"""
        logger.debug(f"请求DeepSeek API，提示词长度：{len(prompt)}")
        headers = {"Authorization": f"Bearer {self.api_key}"}
        system_prompt = self._build_system_prompt()
        start_time = time.time()

        # 配置超时参数（总超时60秒，单独读取超时60秒）
        timeout = httpx.Timeout(60.0, read=60.0)
        async with httpx.AsyncClient(timeout=timeout) as client:
            try:
                response = await client.post(
                    f"{self.base_url}/v1/chat/completions",
                    headers=headers,
                    json={
                        "model": "deepseek-chat",
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            *[{"role": msg["role"], "content": msg["content"]} for msg in history],
                            {"role": "user", "content": prompt}
                        ],
                        "temperature": 1.5,
                        "max_tokens": 256
                    }
                )

                cost = time.time() - start_time
                logger.debug(f"API请求耗时: {cost:.2f}s | 状态码: {response.status_code}")

                if response.status_code != 200:
                    logger.error(f"API请求失败：{response.status_code} {response.text}")
                    return "好像哪里不对劲...(・－・。)"

                return self._process_response(response.json())

            except httpx.TimeoutException as e:
                logger.warning(f"API请求超时：{str(e)}")
                return "思考需要更长时间呢~（>ω<）"
            except Exception as e:
                logger.error(f"未知错误：{str(e)}")
                return "呜...处理器冒烟了啦！(＞﹏＜)"

    def _build_system_prompt(self) -> str:
        """构建系统提示词"""
        params = {
            "name": config["name"],
            "age": config["age"],
            "characteristics": config["characteristics"]
        }
        prompt_lines = [line.format(**params) for line in config["system_prompt"]]
        return "\n".join(prompt_lines) + "\n当前会话规则：" + str(config["response_rules"])

    def _process_response(self, data: dict) -> str:
        """处理API响应"""
        content = data["choices"][0]["message"]["content"]
        return self._apply_response_rules(content)

    def _apply_response_rules(self, text: str) -> str:
        # """应用响应规则"""
        # # 添加表情符号
        # if random.random() < config["response_rules"]["emoticon_probability"]:
        #     text += random.choice(config["response_rules"]["emoticons"])
        
        # # 添加恶作剧
        # if random.random() < config["response_rules"]["prank_probability"]:
        #     text += random.choice(config["response_rules"]["pranks"])
        
        return text