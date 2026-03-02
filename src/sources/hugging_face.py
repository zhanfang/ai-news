import requests
from bs4 import BeautifulSoup

class HuggingFaceFetcher:
    def __init__(self):
        self.url = "https://huggingface.co/papers"

    def fetch(self):
        try:
            response = requests.get(self.url, timeout=10)
            soup = BeautifulSoup(response.text, "html.parser")
            
            papers = []
            # Find paper cards - this selector might need adjustment based on current site layout
            # Usually papers are in articles or divs with specific classes
            # Let's try finding h3 tags inside main content area
            
            articles = soup.find_all("article")
            for article in articles:
                title_elem = article.find("h3")
                if not title_elem:
                    continue
                    
                title = title_elem.get_text(strip=True)
                link = "https://huggingface.co" + title_elem.find("a")["href"] if title_elem.find("a") else ""
                
                # Try to find abstract or summary
                summary_elem = article.find("p", class_="text-gray-500")
                summary = summary_elem.get_text(strip=True) if summary_elem else "No summary available"
                
                papers.append({
                    "source": "Hugging Face Papers",
                    "title": title,
                    "url": link,
                    "summary": summary
                })
                
            return papers
        except Exception as e:
            print(f"Error fetching Hugging Face: {e}")
            return []
