import sqlite3
from db import get_connection, DB_PATH

def migrate():
    print("Running database migrations...")
    with get_connection() as conn:
        cursor = conn.cursor()

        # Check if 'failures' column exists in 'sources' table
        cursor.execute("PRAGMA table_info(sources)")
        columns = [column[1] for column in cursor.fetchall()]

        if "failures" not in columns:
            print("Adding 'failures' column to 'sources' table...")
            try:
                cursor.execute("ALTER TABLE sources ADD COLUMN failures INTEGER DEFAULT 0")
                print("Successfully added 'failures' column.")
            except sqlite3.OperationalError as e:
                print(f"Migration failed: {e}")
        else:
            print("'failures' column already exists.")

        # Create subscribers table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS subscribers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                subscribed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                active INTEGER DEFAULT 1
            )
        """)
        print("Ensured 'subscribers' table exists.")

        # Add conference_id column to events table
        cursor.execute("PRAGMA table_info(events)")
        event_columns = [column[1] for column in cursor.fetchall()]

        if "conference_id" not in event_columns:
            print("Adding 'conference_id' column to 'events' table...")
            try:
                cursor.execute("ALTER TABLE events ADD COLUMN conference_id INTEGER REFERENCES events(id)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_events_conference_id ON events(conference_id)")
                print("Successfully added 'conference_id' column and index.")
            except sqlite3.OperationalError as e:
                print(f"Migration failed: {e}")
        else:
            print("'conference_id' column already exists.")

        # Add crawl_depth column to sources table
        cursor.execute("PRAGMA table_info(sources)")
        source_columns = [column[1] for column in cursor.fetchall()]

        if "crawl_depth" not in source_columns:
            print("Adding 'crawl_depth' column to 'sources' table...")
            try:
                cursor.execute("ALTER TABLE sources ADD COLUMN crawl_depth INTEGER DEFAULT 0")
                print("Successfully added 'crawl_depth' column.")
            except sqlite3.OperationalError as e:
                print(f"Migration failed: {e}")
        else:
            print("'crawl_depth' column already exists.")

        # Add discovery_source_id column to events table
        cursor.execute("PRAGMA table_info(events)")
        event_columns_2 = [column[1] for column in cursor.fetchall()]

        if "discovery_source_id" not in event_columns_2:
            print("Adding 'discovery_source_id' column to 'events' table...")
            try:
                cursor.execute("ALTER TABLE events ADD COLUMN discovery_source_id INTEGER REFERENCES sources(id)")
                print("Successfully added 'discovery_source_id' column.")
            except sqlite3.OperationalError as e:
                print(f"Migration failed: {e}")
        else:
            print("'discovery_source_id' column already exists.")

        conn.commit()

if __name__ == "__main__":
    migrate()