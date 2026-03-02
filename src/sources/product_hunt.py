import feedparser

class ProductHuntFetcher:
    def __init__(self):
        self.rss_url = "https://www.producthunt.com/feed"
        self.keywords = ["AI", "Artificial Intelligence", "GPT", "LLM", "Machine Learning", "Neural", "Bot", "Assistant"]

    def fetch(self):
        try:
            feed = feedparser.parse(self.rss_url)
            posts = []
            
            for entry in feed.entries:
                title = entry.title
                summary = entry.summary
                
                # Check if it's AI related
                content = (title + " " + summary).lower()
                if any(k.lower() in content for k in self.keywords):
                    posts.append({
                        "source": "Product Hunt",
                        "title": title,
                        "url": entry.link,
                        "summary": summary[:200] + "..." if len(summary) > 200 else summary
                    })
            return posts
        except Exception as e:
            print(f"Error fetching Product Hunt: {e}")
            return []
