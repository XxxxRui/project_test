import sqlite3
import os
import random
from datetime import datetime, timedelta

def add_exercise_records_for_user(username, password_hash, num_records=200):
    # Connect to database
    conn = sqlite3.connect('wellness.db')
    conn.row_factory = sqlite3.Row
    
    # Check if user exists
    user = conn.execute('SELECT * FROM user WHERE username = ?', (username,)).fetchone()
    
    # Add user if they don't exist
    if not user:
        conn.execute('INSERT INTO user (username, password_hash) VALUES (?, ?)', 
                     (username, password_hash))
        conn.commit()
        user = conn.execute('SELECT * FROM user WHERE username = ?', (username,)).fetchone()
        print(f"Created new user {username} with ID {user['id']}")
    else:
        print(f"Found existing user {username} with ID {user['id']}")
    
    user_id = user['id']
    
    # Get all exercise types
    exercise_types = conn.execute('SELECT * FROM exercise_types').fetchall()
    
    # Generate random dates from the past year
    today = datetime.now()
    
    # Add records
    records_added = 0
    
    for _ in range(num_records):
        # Random date (within past year)
        random_days = random.randint(0, 365)
        record_date = (today - timedelta(days=random_days)).strftime('%Y-%m-%d')
        
        # Random exercise type
        exercise_type = random.choice(exercise_types)
        exercise_type_id = exercise_type['id']
        
        # Random duration (15-120 minutes)
        duration = random.randint(15, 120)
        
        # Calculate calories burned (based on exercise type and duration)
        calories = round(exercise_type['calories_per_minute'] * duration)
        
        # Check if a record already exists for this date and exercise type
        existing = conn.execute(
            'SELECT * FROM activity_data WHERE user_id = ? AND date = ? AND exercise_type_id = ?', 
            (user_id, record_date, exercise_type_id)
        ).fetchone()
        
        # Add record if none exists for this date and exercise type
        if not existing:
            conn.execute(
                '''INSERT INTO activity_data 
                   (user_id, exercise_type_id, date, duration_minutes, calories_burnt)
                   VALUES (?, ?, ?, ?, ?)''',
                (user_id, exercise_type_id, record_date, duration, calories)
            )
            records_added += 1
    
    # Commit changes
    conn.commit()
    conn.close()
    
    return records_added

# Add records for david user
if __name__ == '__main__':
    # Replace with david's actual password hash from the database
    password_hash = 'pbkdf2:sha256:600000$GDGzdtMogbHWtkit$51e52cd97992e8144acf4bc3a4e09deef9b7eb729867380a6e9a7da0e8f7d93f'
    records_added = add_exercise_records_for_user('david', password_hash, num_records=300)
    print(f"Added {records_added} exercise records for david")