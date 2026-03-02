import requests
from concurrent.futures import ThreadPoolExecutor

class HackerNewsFetcher:
    def __init__(self):
        self.base_url = "https://hacker-news.firebaseio.com/v0"
        self.keywords = ["AI", "LLM", "GPT", "Machine Learning", "Neural Network", "OpenAI", "Anthropic", "Gemini", "Llama", "Mistral", "DeepLearning", "Computer Vision", "NLP"]

    def fetch(self, limit=50):
        try:
            # Get top stories IDs
            response = requests.get(f"{self.base_url}/topstories.json")
            story_ids = response.json()[:limit]

            # Fetch details in parallel
            with ThreadPoolExecutor(max_workers=10) as executor:
                results = list(executor.map(self._fetch_story, story_ids))

            # Filter None and return
            return [r for r in results if r]
        except Exception as e:
            print(f"Error fetching HN: {e}")
            return []

    def _fetch_story(self, story_id):
        try:
            response = requests.get(f"{self.base_url}/item/{story_id}.json", timeout=5)
            story = response.json()
            if not story or "title" not in story or "url" not in story:
                return None
            
            # Check keywords
            title = story["title"]
            if any(k.lower() in title.lower() for k in self.keywords):
                return {
                    "source": "Hacker News",
                    "title": title,
                    "url": story["url"],
                    "score": story.get("score", 0),
                    "comments": story.get("descendants", 0)
                }
            return None
        except:
            return None
