import sqlite3
from db import get_connection

def migrate():
    print("Migrating database: Adding parent_id and index to sources...")
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            # Add column if not exists
            cursor.execute("PRAGMA table_info(sources)")
            columns = [column[1] for column in cursor.fetchall()]
            
            if 'parent_id' not in columns:
                cursor.execute("ALTER TABLE sources ADD COLUMN parent_id INTEGER REFERENCES sources(id)")
                print("Successfully added parent_id column.")
            
            # Create index on parent_id for efficient lineage lookups
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_sources_parent_id ON sources(parent_id)")
            print("Successfully ensured index on parent_id exists.")
            
            conn.commit()
    except Exception as e:
        print(f"Migration failed: {e}")

if __name__ == "__main__":
    migrate()
