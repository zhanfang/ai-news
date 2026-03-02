import requests
from bs4 import BeautifulSoup
import re

class ContentExtractor:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

    def extract(self, url, max_length=2000):
        """
        Extracts the main text content from a URL.
        Returns a truncated string of the content.
        """
        try:
            # Skip non-html files
            if url.endswith('.pdf') or url.endswith('.zip'):
                return "Content not available (File)"

            response = requests.get(url, headers=self.headers, timeout=5)
            if response.status_code != 200:
                return f"Failed to fetch content (Status {response.status_code})"

            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style", "nav", "footer", "header"]):
                script.decompose()

            # Get text
            text = soup.get_text()
            
            # Break into lines and remove leading/trailing space on each
            lines = (line.strip() for line in text.splitlines())
            # Break multi-headlines into a line each
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            # Drop blank lines
            text = '\n'.join(chunk for chunk in chunks if chunk)
            
            # Simple heuristic: find the longest consecutive text block or just return the clean text
            # For now, just return the clean text truncated
            return text[:max_length] + "..." if len(text) > max_length else text

        except Exception as e:
            return f"Error extracting content: {str(e)}"
