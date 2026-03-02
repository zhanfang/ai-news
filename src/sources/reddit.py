import requests

class RedditFetcher:
    def __init__(self):
        self.subreddits = ["MachineLearning", "ArtificialIntelligence", "LocalLLaMA"]
        self.headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}

    def fetch(self, limit=10):
        all_posts = []
        for sub in self.subreddits:
            try:
                # Try RSS first as it's more reliable without API key
                import feedparser
                rss_url = f"https://www.reddit.com/r/{sub}/top/.rss?t=day&limit={limit}"
                
                # Custom User-Agent is still needed for RSS
                headers = {
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
                }
                
                # feedparser can handle URL directly but sometimes fails with 429 if no UA
                # So we fetch content first
                response = requests.get(rss_url, headers=headers, timeout=10)
                
                if response.status_code == 200:
                    feed = feedparser.parse(response.content)
                    if feed.entries:
                        for entry in feed.entries[:limit]:
                            all_posts.append({
                                "source": f"Reddit r/{sub}",
                                "title": entry.title,
                                "url": entry.link,
                                "score": 0,
                                "comments": 0
                            })
                        continue
                
                # If RSS fails, try JSON API as backup
                url = f"https://www.reddit.com/r/{sub}/top.json?t=day&limit={limit}"
                response = requests.get(url, headers=headers, timeout=10)
                if response.status_code != 200:
                    print(f"Failed to fetch r/{sub}: {response.status_code}")
                    continue
                    
                data = response.json()
                children = data.get("data", {}).get("children", [])
                
                for post in children:
                    p = post.get("data", {})
                    all_posts.append({
                        "source": f"Reddit r/{sub}",
                        "title": p.get("title"),
                        "url": p.get("url"),
                        "score": p.get("score"),
                        "comments": p.get("num_comments")
                    })
            except Exception as e:
                print(f"Error fetching r/{sub}: {e}")
                
        return all_posts
