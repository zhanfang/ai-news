import feedparser
import requests

class OfficialBlogsFetcher:
    def __init__(self):
        self.sources = {
            "OpenAI Blog": "https://openai.com/index/rss",
            "Anthropic Research": "https://www.anthropic.com/index.xml",
            "Google DeepMind": "https://deepmind.google/blog/rss.xml",
            "Meta AI": "https://ai.meta.com/blog/rss.xml",
            "Microsoft AI": "https://blogs.microsoft.com/ai/feed/"
        }
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

    def fetch(self, limit=3):
        all_results = []
        
        for name, url in self.sources.items():
            try:
                # Some feeds might block default feedparser UA, so we fetch content first
                response = requests.get(url, headers=self.headers, timeout=10)
                if response.status_code != 200:
                    print(f"Failed to fetch {name}: {response.status_code}")
                    continue
                
                feed = feedparser.parse(response.content)
                if not feed.entries:
                    continue
                
                # Take top N from each source
                for entry in feed.entries[:limit]:
                    all_results.append({
                        "source": name,
                        "title": entry.title,
                        "url": entry.link,
                        "published": entry.published if 'published' in entry else ""
                    })
                    
            except Exception as e:
                print(f"Error fetching {name}: {e}")
                
        return all_results
