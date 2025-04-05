# 赛博群友白苏文 - NoneBot 插件

[![NoneBot](https://img.shields.io/badge/NoneBot-2.0+-blue.svg)](https://v2.nonebot.dev/)

> 基于 DeepSeek 的智能聊天插件，搭载狼族少女「白苏文」角色设定

---

## 📦 安装方式

### 前置要求
- Python 3.8+
- NoneBot 2.0 框架
- OneBot V11 协议适配器
- Redis 5.0.14

### 安装方式

使用 nb-cli 安装
在 nonebot2 项目的根目录下打开命令行, 输入以下指令即可安装
```bash
nb plugin install nonebot_plugin_ds_baisuwen
```

---

## 🚀 核心功能

### 🤖 智能回复
- 支持群聊@触发和私聊直接对话
- 角色化回复（支持人设个人定制）

### 🕒 交互管理
- Redis 历史会话记录（保留最近5条）
- 用户级/群组级速率限制
  - 用户：1分钟内5次
  - 群组：1分钟内20次

### 🎭 角色系统
- 通过 `qq.json` 配置文件自定义：
  - 角色名称/年龄/特征
  - 系统提示词模板
  - 表情符号概率与内容

---

## ⚙️ 配置项

### 必要配置
1. **环境变量**（在 `.env` 文件中添加）：
```ini
DEEPSEEK_API_KEY="your_api_key"  # DeepSeek API密钥
REDIS_URL="redis://localhost:6379/0"  # Redis连接地址
```

2. **角色配置文件模板**（`data/qq.json`）：
```json
{
    "name": "白苏文",
    "age": 14,
    "characteristics": [
        "狼族少女",
        "银色狼耳和尾巴",
        "编程高手",
        "喜欢恶作剧"
    ],
    "system_prompt": [
        "你叫{name}，{age}岁的{characteristics[0]}，有着{characteristics[1]}",
        "说话方式：使用'呐~'、'嗷呜'等语气词，每3句话可能插入小恶作剧",
        "技术解释时使用动物比喻"
    ],
    "response_rules": {
        "emoticon_probability": 0.3,
        "prank_probability": 0.1,
        "emoticons": [
            "(耳朵动了动)",
            "(尾巴卷住手腕)"
        ],
        "pranks": [
            "\n(突然凑近耳边) 哇！",
            "\n悄悄调换键盘按键"
        ]
    }
}
```


---

## 📌 注意事项

1. **服务依赖**：
   - 需要运行 Redis 服务
   - 确保能访问 DeepSeek API 端点

2. **权限要求**：
   - 群聊需要@机器人或输入角色名称触发
   - 私聊无需触发词直接对话

3. **性能提示**：
   - API请求默认超时60秒
   - HTTP客户端使用连接池优化

---

## 📆 Todo

- [ ] 超管web管理后台
- [ ] 优化bot管理指令
- [ ] 支持更多交互方式（语音/图片）
- [ ] 支持提供Deepseek API使用权（按月计费）
---


> 提示：部署前请确保已正确配置 `DEEPSEEK_API_KEY`、`DEEPSEEK_API_BASE` 和 `REDIS_URL`，角色配置文件建议通过 [在线JSON校验工具](https://jsonlint.com/) 验证格式。

