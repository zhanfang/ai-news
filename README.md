# AI News Aggregator

A command-line tool to aggregate the latest AI news, papers, and product launches from top tech sources.

## Features

- **Hacker News**: Fetches top stories matching AI-related keywords.
- **Hugging Face Papers**: Scrapes the latest trending papers.
- **Product Hunt**: Finds new AI product launches via RSS.
- **Reddit**: (Experimental) Fetches top posts from r/MachineLearning, r/ArtificialIntelligence, etc.
- **Rich UI**: Beautiful terminal output with tables and progress bars.
- **AI Summary**: Uses DeepSeek LLM to generate a concise summary of the latest news.
- **Feishu Notification**: Sends the AI summary to a Feishu (Lark) group via Webhook or Custom App.

## Installation

1.  Clone the repository.
2.  Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

Run the main script:

```bash
python3 src/main.py
```

## Configuration

To enable AI summaries and Feishu notifications, create a `.env` file:

1.  Create a `.env` file in the project root:
    ```bash
    cp .env.example .env
    ```
2.  Add your keys:
    ```
    DEEPSEEK_API_KEY=your_deepseek_api_key
    
    # Option 1: Feishu Webhook (Simpler)
    FEISHU_WEBHOOK_URL=your_feishu_webhook_url
    
    # Option 2: Feishu Custom App (More secure/flexible)
    FEISHU_APP_ID=your_app_id
    FEISHU_APP_SECRET=your_app_secret
    FEISHU_RECEIVER_ID=your_receiver_id (e.g. email or chat_id)
    FEISHU_RECEIVER_ID_TYPE=email (or open_id, user_id, chat_id)
    ```

Currently, keywords and sources are hardcoded in `src/sources/*.py`. You can modify them directly to customize your feed.

## Future Plans

-   [x] Add LLM integration (DeepSeek) to summarize the news automatically.
-   [x] Add Feishu/Lark notification support.
-   [ ] Add Reddit API authentication for reliable fetching.
-   [ ] Add "Save to Markdown" feature.
