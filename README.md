# AI News Aggregator (AI 新闻聚合助手)

这是一个自动化的 AI 新闻聚合工具，旨在帮助你每天早晨快速掌握全球 AI 领域的最新动态。它会从多个高质量科技源抓取信息，使用 DeepSeek 大模型生成深度中文摘要，并推送到你的飞书（Feishu）群组。

![Terminal Preview](https://via.placeholder.com/800x400?text=Terminal+Preview)

## 🌟 功能亮点

*   **多源聚合**：一站式获取 Hacker News, Hugging Face Papers, Reddit, Product Hunt, GitHub Trending, TechCrunch AI 等 6 大源的最新 AI 资讯。
*   **深度摘要**：利用 DeepSeek LLM 生成详细的中文研报，包含“热门产品”、“前沿研究”和“行业动态”三大板块。
*   **飞书推送**：格式精美的飞书卡片消息，支持原链接直达。
*   **自动化运行**：支持注册为系统命令及每日定时任务。

---

## 🚀 快速开始 (小白教程)

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

### 2. 配置密钥

本项目需要 DeepSeek API 和 飞书应用凭证。为了安全，建议将密钥配置在你的个人配置文件 `~/.zshrc` (或 `~/.bashrc`) 中，而不是项目文件里。

1.  打开你的配置文件：
    ```bash
    nano ~/.zshrc
    ```
2.  在文件末尾添加以下内容（替换为你自己的 Key）：
    ```bash
    # AI News Aggregator Config
    export DEEPSEEK_API_KEY="sk-xxxxxxxxxxxxxxxxxxxxxxxx"
    
    # 飞书配置 (需要创建一个企业自建应用)
    export FEISHU_APP_ID="cli_xxxxxxxx"
    export FEISHU_APP_SECRET="xxxxxxxxxxxxxxxxxxxxxxxx"
    export FEISHU_RECEIVER_ID="oc_xxxxxxxxxxxxxxxxxxxxxxxx" # 群组的 chat_id
    export FEISHU_RECEIVER_ID_TYPE="chat_id"
    ```
3.  保存并退出 (Ctrl+O, Enter, Ctrl+X)，然后使配置生效：
    ```bash
    source ~/.zshrc
    ```

> **如何获取飞书 chat_id？**
> 1. 将你的飞书机器人拉入目标群组。
> 2. 运行本项目提供的工具脚本：`python3 src/get_chat_id.py`

### 3. 运行测试

在终端直接运行：

```bash
python3 src/main.py
```

如果配置正确，你将看到终端开始抓取新闻，生成摘要，并在几分钟后你的飞书群组会收到一条消息。

---

## 🛠️ 进阶玩法：自动化运行

想要每天早上自动收到新闻早报？

### 1. 注册为系统命令

运行以下命令，创建一个名为 `ai-news` 的快捷指令：

```bash
# 创建存放脚本的目录
mkdir -p ~/.local/bin

# 创建软链接
ln -sf $(pwd)/run_ai_news.sh ~/.local/bin/ai-news

# 确保 ~/.local/bin 在你的 PATH 中 (如果 ai-news 没反应，检查你的 .zshrc)
```

现在，你在任何地方输入 `ai-news` 即可运行。

### 2. 设置每日定时任务 (Mac/Linux)

使用 `crontab` 设置每天早上 8:00 自动运行。

1.  运行命令：
    ```bash
    (crontab -l 2>/dev/null; echo "0 8 * * * ~/.local/bin/ai-news >> $(pwd)/cron.log 2>&1") | crontab -
    ```
2.  **Mac 用户注意**：你需要给 `cron` 授予**完全磁盘访问权限**。
    *   打开 **系统设置** -> **隐私与安全性** -> **完全磁盘访问权限**。
    *   添加 `/usr/sbin/cron` 并启用。

---

## 📂 项目结构

*   `src/main.py`: 主程序入口。
*   `src/sources/`: 各个新闻源的抓取脚本。
*   `src/llm_client.py`: DeepSeek LLM 调用逻辑。
*   `src/feishu_client.py`: 飞书消息发送逻辑。
*   `run_ai_news.sh`: 用于自动化运行的 Shell 包装脚本。

## 🤝 贡献

欢迎提交 Issue 或 Pull Request 来增加新的数据源或功能！
