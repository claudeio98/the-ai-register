import sqlite3
import os

# Get the project root directory (parent of src)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(PROJECT_ROOT, "data", "events.db")

def get_connection():
    return sqlite3.connect(DB_PATH)

def init_db():
    with get_connection() as conn:
        cursor = conn.cursor()
        
        # sources table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sources (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT UNIQUE NOT NULL,
                description TEXT,
                category TEXT,
                last_checked TIMESTAMP,
                failures INTEGER DEFAULT 0
            )
        ''')
        
        # raw_pages table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS raw_pages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_id INTEGER,
                url TEXT,
                content TEXT,
                processed INTEGER DEFAULT 0,
                fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (source_id) REFERENCES sources (id)
            )
        ''')
        
        # events table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                speaker TEXT,
                institution TEXT,
                date TEXT,
                url TEXT,
                score REAL,
                status TEXT DEFAULT 'discovered',
                raw_content TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # notifications table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_id INTEGER,
                sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (event_id) REFERENCES events (id)
            )
        ''')
        conn.commit()

if __name__ == "__main__":
    init_db()
    print("Database initialized.")
