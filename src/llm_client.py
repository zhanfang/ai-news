import json
import re
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
            return "DeepSeek API Key not found. Please set DEEPSEEK_API_KEY environment variable.", []

        if not news_items:
            return "No news items to summarize.", []
        
        # Batch processing if news items > 40
        chunk_size = 40
        chunks = [news_items[i:i + chunk_size] for i in range(0, len(news_items), chunk_size)]
        
        summaries_text = [None] * len(chunks)
        analyzed_items = [] # To store structured data for DB

        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            future_to_index = {
                executor.submit(self._generate_chunk_analysis, chunk, i + 1, len(chunks)): i 
                for i, chunk in enumerate(chunks)
            }
            for future in concurrent.futures.as_completed(future_to_index):
                index = future_to_index[future]
                try:
                    # Result is now a tuple: (markdown_text, list_of_dicts)
                    chunk_text, chunk_data = future.result()
                    summaries_text[index] = chunk_text
                    if chunk_data:
                        analyzed_items.extend(chunk_data)
                except Exception as e:
                    summaries_text[index] = f"Error generating summary for chunk {index + 1}: {str(e)}"
        
        full_detailed_report = "\n\n".join(filter(None, summaries_text))
        
        return full_detailed_report, analyzed_items

    def _generate_chunk_analysis(self, news_items, chunk_index=1, total_chunks=1):
        # Prepare the input text
        news_text = ""
        # Map input index to item for later merging
        item_map = {}
        for i, item in enumerate(news_items, 1):
            title = item.get('title', 'No Title')
            source = item.get('source', 'Unknown')
            content = item.get('full_content', '')
            url = item.get('url', '')
            item_map[i] = item
            
            # If full content is available, include a snippet
            if content:
                # Limit content to ~800 chars to fit more items in context
                # Escape potential JSON breaking characters in input
                content_snippet = content[:800].replace('\n', ' ').replace('"', "'").replace('\\', '')
                news_text += f"Item {i}:\nTitle: {title}\nSource: {source}\nURL: {url}\nContent: {content_snippet}...\n\n"
            else:
                news_text += f"Item {i}:\nTitle: {title}\nSource: {source}\nURL: {url}\n\n"

        prompt = f"""
You are a strategic AI analyst. Analyze the following news items.
This is Part {chunk_index} of {total_chunks}.

**Goal**: Return a comprehensive, detailed, and high-density AI news report in Chinese.

**Output Format**:
Return pure Markdown content. Do not use JSON.
Organize the items into these categories:
*   **🏗️ Infrastructure & Models**
*   **🚀 Applications & Tools**
*   **🔬 Research & Papers**
*   **💰 Funding & M&A**
*   **⚖️ Policy & Regulation**
*   **📰 Industry & Community**

**Item Format**:
For EVERY item, use this exact structure:
*   **Title**: [Refined Title in Chinese]
    *   **Source**: [Source Name]
    *   **What**: [1-2 sentences explaining exactly what it is (technical specs, core function)]
    *   **Why**: [1-2 sentences explaining why it matters, its potential impact, or what problem it solves]

**Strict Rules**:
1. **LANGUAGE**: All content MUST be in Simplified Chinese (简体中文).
2. **DEPTH**: Analyze EVERY item provided in the input. Do not skip any.
3. **NO JSON**: Do not output JSON. Just output the Markdown text.

News Input:
{news_text}
"""

        try:
            response = self._retry_api_call(
                lambda: self.client.chat.completions.create(
                    model="deepseek-chat",
                    messages=[
                        {"role": "system", "content": "You are a senior AI research analyst. Output detailed Markdown report in Chinese."},
                        {"role": "user", "content": prompt}
                    ],
                    stream=False
                )
            )
            content = response.choices[0].message.content
            
            # Since we are back to text-only, we can't easily parse enriched items for DB.
            # We will return empty list for enriched_items, and main.py will fallback to basic items.
            return content, []

        except Exception as e:
            return f"Error generating analysis for chunk {chunk_index}: {str(e)}", []
            
    # Deprecated: _generate_chunk_summary (Replaced by _generate_chunk_analysis)
    
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
