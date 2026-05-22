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
            
        conn.commit()

if __name__ == "__main__":
    migrate()
