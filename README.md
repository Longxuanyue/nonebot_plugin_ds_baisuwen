# 赛博群友白苏文 - NoneBot 插件

> 基于 DeepSeek 的智能聊天插件，搭载狼族少女「白苏文」角色设定

> 当前版本：V1.2.0

---

## ⚠️ 重要通知
<font color="red" size=5>**1）本项目现已停止在Nonebot商店上架，如有需要请直接下载本仓库内容并按照本地加载插件的方式进行修改。若出现加载异常问题，请附带运行日志、运行截图与具体问题描述进行咨询。**</font>

<font color="#4169E1" size=4>**2）本项目代码需要本地化调整，请勿下载后直接运行（后续会进行优化更新）**</font>

---

## 🚀 核心功能

### 🤖 智能回复
- 支持群聊@触发和私聊直接对话
- 角色化回复（支持人设个人定制）
- **VITS语音回复功能**（需自行部署模型）

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

## 🎤 VITS语音模型部署
**使用前请注意：**
1. 需自行修改代码中所有路径定义部分
2. 项目自带预训练中日双语模型「rosmontic（迷迭香）」
3. **必须本地部署VITS模型**，推荐以下方式：

**部署方式一**  
根据 [VITS官方文档](https://github.com/Plachtaa/VITS-fast-fine-tuning/blob/main/LOCAL.md) 进行部署

**部署方式二**  
联系开发者获取优化整合包：  
📮 **2461292801@qq.com**

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
        "你叫{name}，回复要简短自然，像日常对话",
        "绝对禁止使用换行符，所有文字必须保持一行",
        "每句话控制在30字以内，用空格代替标点分割",
        "示例格式：'好呀 要不要一起写代码 我可以教你哦'"
    ],
    "response_rules": {
        "max_tokens": 1024
    },
    "vits_model_path": "按照实际的模型位置进行更改",
    "vits_config_path": "按照实际的config位置进行更改",
    "voice_enabled": true
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

4. **启动顺序**：
   - 启动本项目之前<font color="red" size=5>请确认</font>已启动本地VITS模型中的VC_inference.py，否则将会产生语音API异常（不会影响运行，但语音输出结果会差很多）
   - 需下载silk解码器
---

## 📆 Todo

- <font color="#FFDAB9">[✓] 实现语音回复功能(V1.2)</font> 
- <font color="#E6E6FA">[✗] 好感度养成系统(V1.3) 
- [✗] 超管web管理后台(V1.4)  
- [✗] 优化bot管理指令  
- [✗] 支持提供Deepseek API使用权（按月计费）</font> 

---

> **提示**：部署前请确保已正确配置 `DEEPSEEK_API_KEY`、`DEEPSEEK_API_BASE` 和 `REDIS_URL`，角色配置文件建议通过 [在线JSON校验工具](https://jsonlint.com/) 验证格式。