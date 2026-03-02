import feedparser

class TechCrunchFetcher:
    def __init__(self):
        self.feed_url = "https://techcrunch.com/category/artificial-intelligence/feed/"

    def fetch(self, limit=10):
        try:
            feed = feedparser.parse(self.feed_url)
            if not feed.entries:
                return []
            
            results = []
            for entry in feed.entries[:limit]:
                results.append({
                    "source": "TechCrunch AI",
                    "title": entry.title,
                    "url": entry.link,
                    "published": entry.published if 'published' in entry else ""
                })
            
            return results
        except Exception as e:
            print(f"Error fetching TechCrunch: {e}")
            return []
