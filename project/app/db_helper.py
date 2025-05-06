import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'wellness.db')
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), '..', 'schema.sql')

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # allows dict-style access
    return conn

def init_db():
    """Initialize or update database structure"""
    conn = get_db_connection()
    
    # Check which tables already exist
    tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
    existing_tables = [table[0] for table in tables]
    
    print(f"Existing database tables: {', '.join(existing_tables)}")
    
    # Add missing tables
    needed_tables = ['user', 'health_data', 'shared_content']
    missing_tables = [table for table in needed_tables if table not in existing_tables]
    
    if missing_tables:
        print(f"Tables to be added: {', '.join(missing_tables)}")
        
        # Execute SQL statements to create tables
        conn.executescript('''
        CREATE TABLE IF NOT EXISTS health_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            steps INTEGER NOT NULL,
            calories_burnt INTEGER NOT NULL,
            sleep_hours REAL,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES user (user_id),
            UNIQUE(user_id, date)
        );

        CREATE TABLE IF NOT EXISTS shared_content (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            shared_with_id INTEGER NOT NULL,
            content_type TEXT NOT NULL,
            content_id TEXT NOT NULL,
            message TEXT,
            share_date TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES user (user_id),
            FOREIGN KEY (shared_with_id) REFERENCES user (user_id)
        );

        -- Create indexes
        CREATE INDEX IF NOT EXISTS idx_health_data_user_date ON health_data (user_id, date);
        CREATE INDEX IF NOT EXISTS idx_shared_content_shared_with ON shared_content (shared_with_id);
        ''')
        
        conn.commit()
        print("Database structure has been updated")
    else:
        print("Database structure is complete, no updates needed")
    
    conn.close()

# Initialize the database on import if it doesn't exist
init_db()