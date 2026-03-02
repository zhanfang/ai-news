import sqlite3
import os
from datetime import datetime

class Database:
    def __init__(self, db_path="news.db"):
        # Ensure we use absolute path relative to project root if not specified
        if not os.path.isabs(db_path):
            project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            self.db_path = os.path.join(project_dir, db_path)
        else:
            self.db_path = db_path
            
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create table to track sent news
        # We use URL as the unique identifier
        # V2: Added full_content, summary, category, score, entities
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS sent_news (
            url TEXT PRIMARY KEY,
            title TEXT,
            source TEXT,
            sent_at TIMESTAMP,
            full_content TEXT,
            summary TEXT,
            category TEXT,
            score INTEGER,
            entities TEXT
        )
        ''')
        
        # Check if new columns exist, if not add them (simple migration)
        cursor.execute("PRAGMA table_info(sent_news)")
        columns = [info[1] for info in cursor.fetchall()]
        
        if 'full_content' not in columns:
            cursor.execute("ALTER TABLE sent_news ADD COLUMN full_content TEXT")
        if 'summary' not in columns:
            cursor.execute("ALTER TABLE sent_news ADD COLUMN summary TEXT")
        if 'category' not in columns:
            cursor.execute("ALTER TABLE sent_news ADD COLUMN category TEXT")
        if 'score' not in columns:
            cursor.execute("ALTER TABLE sent_news ADD COLUMN score INTEGER")
        if 'entities' not in columns:
            cursor.execute("ALTER TABLE sent_news ADD COLUMN entities TEXT")
            
        # Create raw_news table for decoupled fetch/analyze
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS raw_news (
            url TEXT PRIMARY KEY,
            title TEXT,
            source TEXT,
            published_at TIMESTAMP,
            fetched_at TIMESTAMP,
            full_content TEXT,
            is_analyzed BOOLEAN DEFAULT 0
        )
        ''')
        
        conn.commit()
        conn.close()

    def save_raw_news(self, item):
        """Save fetched news to raw_news table."""
        url = item.get('url')
        if not url:
            return

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
            INSERT OR IGNORE INTO raw_news (url, title, source, published_at, fetched_at, full_content)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                url, 
                item.get('title', ''), 
                item.get('source', ''), 
                item.get('published_at', ''),
                datetime.now().isoformat(),
                item.get('full_content', '')
            ))
            # If full_content was updated (e.g. fetched later), update it
            if item.get('full_content'):
                 cursor.execute('''
                UPDATE raw_news SET full_content = ? WHERE url = ?
                ''', (item.get('full_content'), url))
                 
            conn.commit()
        except Exception as e:
            print(f"Error saving to raw_news: {e}")
        finally:
            conn.close()

    def get_unanalyzed_news(self, limit=100):
        """Get news items that haven't been analyzed yet."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        try:
            cursor.execute("SELECT * FROM raw_news WHERE is_analyzed = 0 LIMIT ?", (limit,))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        finally:
            conn.close()

    def mark_as_analyzed(self, url):
        """Mark a raw news item as analyzed."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE raw_news SET is_analyzed = 1 WHERE url = ?", (url,))
            conn.commit()
        finally:
            conn.close()

    def is_new(self, url):
        """Check if the URL has been sent before."""
        if not url:
            return True # If no URL, treat as new (or handle differently)
            
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT 1 FROM sent_news WHERE url = ?', (url,))
        result = cursor.fetchone()
        
        conn.close()
        return result is None

    def mark_as_sent(self, item):
        """Mark a news item as sent with optional full details."""
        url = item.get('url')
        if not url:
            return

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Use INSERT OR REPLACE to update existing records with new analysis
            cursor.execute('''
            INSERT OR REPLACE INTO sent_news (url, title, source, sent_at, full_content, summary, category, score, entities)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                url, 
                item.get('title', ''), 
                item.get('source', ''), 
                datetime.now().isoformat(),
                item.get('full_content', ''),
                item.get('summary', ''),
                item.get('category', ''),
                item.get('score', 0),
                item.get('entities', '')
            ))
            conn.commit()
        except Exception as e:
            print(f"Error saving to DB: {e}")
        finally:
            conn.close()
            
    def prune_old_records(self, days=30):
        """Optional: Clean up old records to keep DB small."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("DELETE FROM sent_news WHERE sent_at < date('now', '-' || ? || ' days')", (str(days),))
            conn.commit()
        except Exception as e:
            print(f"Error pruning DB: {e}")
        finally:
            conn.close()

    def get_weekly_news(self):
        """Retrieve news sent in the last 7 days."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        try:
            cursor.execute("SELECT * FROM sent_news WHERE sent_at > date('now', '-7 days') ORDER BY sent_at DESC")
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        finally:
            conn.close()

    def search_news(self, keyword, limit=20):
        """Search for news by keyword in title or URL."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        try:
            query = f"%{keyword}%"
            cursor.execute("""
                SELECT * FROM sent_news 
                WHERE title LIKE ? OR url LIKE ? 
                ORDER BY sent_at DESC 
                LIMIT ?
            """, (query, query, limit))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        finally:
            conn.close()
