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
    
    db_exists = os.path.exists(DB_PATH)
    
    conn = get_db_connection()
    
    if not db_exists:
        
        with open(SCHEMA_PATH, 'r') as f:
            schema_sql = f.read()
        
        conn.executescript(schema_sql)
        conn.commit()
        print("New database created with initial structure")
    else:
        
        tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
        existing_tables = [table[0] for table in tables]
        
        # Check if tables exist and create them if not
        if 'user' not in existing_tables:
            conn.execute('''
            CREATE TABLE user (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                date_created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            ''')
        
        if 'exercise_types' not in existing_tables:
            conn.execute('''
            CREATE TABLE exercise_types (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                calories_per_minute REAL NOT NULL
            )
            ''')
            
            # 插入基本运动类型数据
            exercise_types = [
                ('Running', 11.5),
                ('Walking', 5.0),
                ('Cycling', 8.5),
                ('Swimming', 10.0),
                ('Hiking', 7.0),
                ('Weight Training', 6.0),
                ('Yoga', 3.5),
                ('Dancing', 7.5),
                ('Basketball', 9.0),
                ('Soccer', 10.0)
            ]
            
            for ex_type in exercise_types:
                conn.execute('INSERT INTO exercise_types (name, calories_per_minute) VALUES (?, ?)', ex_type)
        
        if 'activity_data' not in existing_tables:
            conn.execute('''
            CREATE TABLE activity_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                exercise_type_id INTEGER NOT NULL,
                date TEXT NOT NULL,
                duration_minutes INTEGER NOT NULL,
                calories_burnt INTEGER NOT NULL,
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES user (id),
                FOREIGN KEY (exercise_type_id) REFERENCES exercise_types (id)
            )
            ''')
            
            conn.execute('CREATE INDEX IF NOT EXISTS idx_activity_data_user_date ON activity_data (user_id, date)')
        
        if 'shared_content' not in existing_tables:
            conn.execute('''
            CREATE TABLE shared_content (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                shared_with_id INTEGER NOT NULL,
                content_type TEXT NOT NULL,
                content_id TEXT NOT NULL,
                message TEXT,
                share_date TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES user (id),
                FOREIGN KEY (shared_with_id) REFERENCES user (id)
            )
            ''')
            
            conn.execute('CREATE INDEX IF NOT EXISTS idx_shared_content_shared_with ON shared_content (shared_with_id)')
        
        conn.commit()
        print("Database structure updated as needed")
    
    conn.close()

def get_exercise_types():
    """Get list of exercise types and their calorie rates"""
    conn = get_db_connection()
    exercise_types = conn.execute('SELECT id, name, calories_per_minute FROM exercise_types ORDER BY name').fetchall()
    conn.close()
    return exercise_types

def calculate_calories(exercise_type_id, duration_minutes):
    """Calculate calories burnt based on exercise type and duration"""
    conn = get_db_connection()
    exercise = conn.execute(
        'SELECT calories_per_minute FROM exercise_types WHERE id = ?', 
        (exercise_type_id,)
    ).fetchone()
    conn.close()
    
    if exercise:
        return round(exercise['calories_per_minute'] * duration_minutes)
    return 0

# Initialize the database on import if it doesn't exist
init_db()