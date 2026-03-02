import requests
from bs4 import BeautifulSoup

class GitHubTrendingFetcher:
    def __init__(self):
        self.base_url = "https://github.com/trending/python?since=daily"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        self.keywords = ["AI", "LLM", "GPT", "Machine Learning", "Neural", "OpenAI", "DeepSeek", "Llama", "RAG", "Agent", "Vision", "Diffusion", "Chat", "Model"]

    def fetch(self, limit=10):
        try:
            response = requests.get(self.base_url, headers=self.headers, timeout=10)
            if response.status_code != 200:
                print(f"Failed to fetch GitHub Trending: {response.status_code}")
                return []
            
            soup = BeautifulSoup(response.text, 'html.parser')
            repos = soup.select('article.Box-row')
            
            results = []
            for repo in repos:
                if len(results) >= limit:
                    break
                    
                # Title & Link
                title_tag = repo.select_one('h2 a')
                if not title_tag:
                    continue
                
                relative_link = title_tag['href'].strip() # e.g. /user/repo
                full_link = f"https://github.com{relative_link}"
                repo_name = relative_link.lstrip('/')
                
                # Description
                desc_tag = repo.select_one('p')
                description = desc_tag.text.strip() if desc_tag else ""
                
                # Check for AI relevance in name or description
                combined_text = (repo_name + " " + description).lower()
                is_ai_related = any(k.lower() in combined_text for k in self.keywords)
                
                if is_ai_related:
                    results.append({
                        "source": "GitHub Trending",
                        "title": f"{repo_name}: {description}"[:100], # Truncate for display
                        "url": full_link,
                        "description": description
                    })
            
            return results
            
        except Exception as e:
            print(f"Error fetching GitHub Trending: {e}")
            return []
