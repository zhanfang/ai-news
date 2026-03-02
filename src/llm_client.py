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
        
        # Batch processing if news items > 40
        chunk_size = 40
        if len(news_items) > chunk_size:
            chunks = [news_items[i:i + chunk_size] for i in range(0, len(news_items), chunk_size)]
            summaries = [None] * len(chunks)
            
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                future_to_index = {
                    executor.submit(self._generate_chunk_summary, chunk, i + 1, len(chunks)): i 
                    for i, chunk in enumerate(chunks)
                }
                for future in concurrent.futures.as_completed(future_to_index):
                    index = future_to_index[future]
                    try:
                        summaries[index] = future.result()
                    except Exception as e:
                        summaries[index] = f"Error generating summary for chunk {index + 1}: {str(e)}"
            
            full_detailed_report = "\n\n".join(summaries)
            
            # Generate Executive Briefing based on the detailed report
            executive_brief = self._generate_executive_brief(full_detailed_report)
            
            return f"{executive_brief}\n\n---\n\n{full_detailed_report}"
        else:
            detailed = self._generate_chunk_summary(news_items)
            brief = self._generate_executive_brief(detailed)
            return f"{brief}\n\n---\n\n{detailed}"

    def _generate_executive_brief(self, detailed_report):
        prompt = f"""
You are a strategic advisor to a CEO of an AI company.
Based on the following detailed daily AI news report, write a "CEO Executive Briefing" in Chinese (中文).

**Requirements:**
1.  **Top 3 Strategic Insights**: Identify the 3 most critical developments that a CEO *must* know today. Focus on major model releases, significant regulatory shifts, or breakthrough research. Ignore minor tool updates.
2.  **Market Sentiment**: Briefly describe the overall mood of the industry today (e.g., "Excited about new open source models", "Concerned about regulation", "Quiet news day").
3.  **Actionable Intelligence**: One sentence on what this means for the AI strategy (e.g., "Open source models are closing the gap; consider evaluating Llama 3 for internal use.").

**Format**:
# 👑 CEO Executive Briefing (CEO 每日速递)
## 🚨 Top Strategic Shifts (战略风向)
*   [Insight 1]
*   [Insight 2]
*   [Insight 3]

## 🌡️ Market Sentiment (市场情绪)
[1-2 sentences]

## 💡 Strategic Takeaway (决策建议)
[1 sentence]

**Detailed Report Context**:
{detailed_report[:15000]}  # Truncate to avoid context limit if report is huge
"""
        try:
            return self._retry_api_call(
                lambda: self.client.chat.completions.create(
                    model="deepseek-chat",
                    messages=[
                        {"role": "system", "content": "You are a strategic AI advisor."},
                        {"role": "user", "content": prompt}
                    ],
                    stream=False
                )
            ).choices[0].message.content
        except Exception as e:
            return f"Error generating executive brief: {str(e)}"

    def _retry_api_call(self, func, max_retries=3):
        import time
        for attempt in range(max_retries):
            try:
                return func()
            except Exception as e:
                if attempt == max_retries - 1:
                    raise e
                time.sleep(2 * (attempt + 1))  # Exponential backoff

    def _generate_chunk_summary(self, news_items, chunk_index=1, total_chunks=1):
        # Prepare the input text
        news_text = ""
        for i, item in enumerate(news_items, 1):
            title = item.get('title', 'No Title')
            source = item.get('source', 'Unknown')
            content = item.get('full_content', '')
            
            # If full content is available, include a snippet
            if content:
                # Limit content to ~800 chars to fit more items in context
                content_snippet = content[:800].replace('\n', ' ')
                news_text += f"{i}. {title} ({source})\n   Context: {content_snippet}...\n\n"
            else:
                news_text += f"{i}. {title} ({source})\n"

        prompt = f"""
Please generate a highly detailed and comprehensive AI news research report in Chinese (中文) for the following items.
This is Part {chunk_index} of {total_chunks} of the daily news.

**Strict Output Requirements:**

1.  **Structure**:
    *   **📣 Official Announcements**: Summarize major updates from big tech.
    *   **🚀 Trending Products & Tools**: Focus on new tools (Product Hunt/GitHub). *Explicitly describe what they do.*
    *   **🔬 Research & Papers**: Explain the core contribution of new papers.
    *   **📰 Industry & Community**: Discussions from Reddit/HN.

    *Note: If this chunk does not contain items for a specific category, simply skip that header.*

2.  **Depth (Crucial)**:
    *   **ANALYZE EVERY SINGLE ITEM** provided in the input list. Do not skip any.
    *   For every item, you MUST follow this format:
        *   **Title**: [Name of the item]
        *   **What**: 1-2 sentences explaining exactly what it is (technical specs, core function).
        *   **Why**: 1-2 sentences explaining why it matters, its potential impact, or what problem it solves.
    *   *Do not* group items into a single vague bullet point. Treat each major item as a distinct entity worth analyzing.

3.  **Tone**: Professional, analytical, and dense with information. Avoid marketing fluff.

4.  **Format**: Return pure Markdown content. Do not include introductory or concluding remarks like "Here is the summary".

News Input:
{news_text}
"""

        try:
            response = self._retry_api_call(
                lambda: self.client.chat.completions.create(
                    model="deepseek-chat",
                    messages=[
                        {"role": "system", "content": "You are a senior AI research analyst. Your goal is to produce a high-density, comprehensive daily briefing covering EVERY item provided. Do not filter."},
                        {"role": "user", "content": prompt}
                    ],
                    stream=False
                )
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error generating summary for chunk {chunk_index}: {str(e)}"
