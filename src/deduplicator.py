from difflib import SequenceMatcher

class Deduplicator:
    def __init__(self, threshold=0.85):
        self.threshold = threshold

    def _similarity(self, a, b):
        return SequenceMatcher(None, a, b).ratio()

    def deduplicate(self, news_items):
        """
        Removes duplicates from a list of news items based on title similarity.
        Prioritizes items that appear earlier in the list (so order matters).
        """
        unique_items = []
        
        for item in news_items:
            is_duplicate = False
            title = item.get('title', '').lower()
            
            for unique in unique_items:
                unique_title = unique.get('title', '').lower()
                
                # Check for near-exact title match
                if self._similarity(title, unique_title) > self.threshold:
                    is_duplicate = True
                    break
                
                # Check if one is a substring of another (common for reposts)
                if len(title) > 10 and len(unique_title) > 10:
                    if title in unique_title or unique_title in title:
                        is_duplicate = True
                        break
            
            if not is_duplicate:
                unique_items.append(item)
                
        return unique_items
