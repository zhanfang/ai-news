import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file if present
load_dotenv()

class DeepSeekClient:
    def __init__(self):
        self.api_key = os.getenv("DEEPSEEK_API_KEY")
        # We don't raise an error here to allow the app to run without API key,
        # but the summarize method will check for it.
        
        if self.api_key:
            self.client = OpenAI(
                api_key=self.api_key,
                base_url="https://api.deepseek.com"
            )
        else:
            self.client = None

    def summarize(self, news_items):
        if not self.client:
            return "DeepSeek API Key not found. Please set DEEPSEEK_API_KEY environment variable."

        if not news_items:
            return "No news items to summarize."

        # Prepare the input text
        # Increase input limit to include more context for detailed summary
        news_text = ""
        for i, item in enumerate(news_items[:60], 1): # Increased to 60 to cover all 6 sources
            news_text += f"{i}. {item.get('title', 'No Title')} ({item.get('source', 'Unknown')})\n"

        prompt = f"""
Please generate a comprehensive and detailed AI news digest in Chinese (中文). Do not be brief; provide depth and context where possible.

Requirements:
1. **Detailed Analysis**: For each key news item, explain WHAT it is and WHY it matters.
2. **Early-Stage Focus**: Pay special attention to new product launches (especially from Product Hunt) and emerging trends. Describe what these products actually do.
3. **Categorize**: Group news into clear sections:
    - **🚀 Trending Products & Tools** (Focus on Product Hunt, Hacker News & GitHub launches)
    - **🔬 Research & Papers** (Hugging Face & Arxiv highlights)
    - **📰 Industry & Community** (TechCrunch, Reddit discussions & Major news)
4. **Format**: Use bullet points with bold headers for readability.
5. **Coverage**: Ensure you cover the most interesting items from ALL sources provided.
6. **Length**: aim for 800-1200 characters or more as needed to be thorough.

News:
{news_text}
"""

        try:
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": "You are a helpful AI news assistant. Provide concise and insightful summaries in Chinese."},
                    {"role": "user", "content": prompt}
                ],
                stream=False
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error generating summary: {str(e)}"
