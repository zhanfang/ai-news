# AI News Aggregator (AI 新闻聚合助手)

这是一个自动化的 AI 新闻聚合工具，旨在帮助你每天早晨快速掌握全球 AI 领域的最新动态。它会从多个高质量科技源抓取信息，使用 DeepSeek 大模型生成深度中文摘要，并推送到你的飞书（Feishu）群组和邮箱。

## 🌟 功能亮点

*   **多源聚合**：一站式获取 Hacker News, Hugging Face Papers, Reddit, Product Hunt, GitHub Trending, TechCrunch AI 等 6 大源的最新 AI 资讯。
*   **深度研报**：利用 DeepSeek LLM 生成高密度的中文研报，对每条重要新闻进行“What/Why”深度解析。
*   **多渠道推送**：支持飞书（Feishu）卡片消息和精美的 HTML 邮件推送。
*   **可靠运行**：
    *   **采集与分析分离**：原始数据优先入库，支持离线重试和历史回溯。
    *   **智能唤醒**：使用 macOS LaunchAgent，确保电脑唤醒后自动补发错过的早报。
    *   **配置分离**：敏感密钥存储在系统环境变量，业务配置在 `config.yaml`，安全又灵活。

---

## 🚀 快速开始

### 1. 环境准备

确保你的电脑已安装 [Python 3.8+](https://www.python.org/downloads/)。

```bash
# 克隆仓库
git clone git@github.com:zhanfang/ai-news.git
cd ai-news

# 创建并激活虚拟环境 (推荐)
python3 -m venv .venv
source .venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置密钥 (安全模式)

为了防止密钥泄露，请将敏感 API Key 配置在你的 Shell 配置文件中 (`~/.zshrc` 或 `~/.bashrc`)。

```bash
# 打开配置文件
nano ~/.zshrc

# 在末尾添加以下内容：
# ------------------------------------------------
# AI News Aggregator Config
export DEEPSEEK_API_KEY="sk-xxxxxxxxxxxxxxxxxxxxxxxx"

# 飞书配置 (可选)
export FEISHU_APP_ID="cli_xxxxxxxx"
export FEISHU_APP_SECRET="xxxxxxxxxxxxxxxxxxxxxxxx"
export FEISHU_RECEIVER_ID="oc_xxxxxxxxxxxxxxxxxxxxxxxx"
export FEISHU_RECEIVER_ID_TYPE="chat_id"

# 邮件配置 (可选)
export SMTP_SERVER="smtp.gmail.com"
export SMTP_PORT="587"
export SMTP_USER="your_email@gmail.com"
export SMTP_PASS="your_app_password" # 注意：使用应用专用密码，非登录密码
export SMTP_FROM="your_email@gmail.com"
export SMTP_TO="your_email@gmail.com"
# ------------------------------------------------

# 保存生效
source ~/.zshrc
```

### 3. 业务配置 (config.yaml)

项目根目录下的 `config.yaml` 用于管理非敏感配置（如收件人列表、抓取数量等）。

```yaml
notification:
  email:
    recipients:
      - your_email@gmail.com
      - team_member@example.com

source_limits:
  hacker_news: 50
  product_hunt: 50
  # ...
```

### 4. 运行测试

在终端直接运行：

```bash
# 默认模式：仅抓取新消息（适合定时任务）
python3 src/main.py

# 强制模式：抓取所有消息（忽略历史记录，适合测试）
python3 src/main.py --all

# 分析模式：仅分析数据库中已抓取但未发送的新闻（适合离线重试）
python3 src/main.py --analyze-only
```

---

## 🛠️ 自动化部署 (macOS)

推荐使用 macOS 原生的 LaunchAgent 替代 Crontab，它能在电脑从睡眠中唤醒后自动补发任务。

### 1. 安装定时任务

```bash
# 赋予脚本执行权限
chmod +x run_ai_news.sh

# 复制配置文件到系统目录
mkdir -p ~/Library/LaunchAgents
cp com.bytedance.ai-news-aggregator.plist ~/Library/LaunchAgents/

# 修改 plist 中的路径 (如果你的代码不在 /Users/bytedance/Documents/...)
# vim ~/Library/LaunchAgents/com.bytedance.ai-news-aggregator.plist

# 加载任务
launchctl load ~/Library/LaunchAgents/com.bytedance.ai-news-aggregator.plist
```

### 2. 验证状态

```bash
launchctl list | grep ai-news
```

如果显示状态码 `0`，说明任务已就绪。每天早上 09:00 系统会自动运行。

---

## 📂 项目结构

*   `src/main.py`: 主程序入口
*   `src/database.py`: SQLite 数据库管理 (RawNews, SentNews)
*   `src/llm_client.py`: DeepSeek API 客户端
*   `src/email_client.py`: SMTP 邮件客户端
*   `src/feishu_client.py`: 飞书机器人客户端
*   `config.yaml`: 业务配置文件
*   `news.db`: 本地数据库 (存储抓取历史)
