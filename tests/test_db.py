import unittest
import sqlite3
import os
import tempfile
from src.db import init_db, get_connection, DB_PATH

class TestDB(unittest.TestCase):
    def setUp(self):
        # Use a temporary database for testing
        self.test_db = os.path.join(tempfile.gettempdir(), f"test_events_{os.getpid()}.db")
        # Monkeypatch DB_PATH in src.db to use the test database
        import src.db
        src.db.DB_PATH = self.test_db
        init_db()

    def tearDown(self):
        if os.path.exists(self.test_db):
            os.remove(self.test_db)

    def test_init_db(self):
        conn = get_connection()
        cursor = conn.cursor()
        # Check if tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        self.assertIn("sources", tables)
        self.assertIn("events", tables)
        self.assertIn("notifications", tables)
        self.assertIn("raw_pages", tables)
        conn.close()

    def test_source_insertion(self):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO sources (url, description, category) VALUES (?, ?, ?)", 
                       ("https://example.com", "test source", "test"))
        conn.commit()
        
        cursor.execute("SELECT url FROM sources WHERE url='https://example.com'")
        self.assertIsNotNone(cursor.fetchone())
        conn.close()

if __name__ == "__main__":
    unittest.main()
