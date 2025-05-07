from flask import Blueprint, request, redirect, url_for, render_template, flash, jsonify, session
from app.db_helper import get_db_connection, get_exercise_types, calculate_calories
from werkzeug.security import generate_password_hash, check_password_hash
import json
from datetime import datetime, timedelta
from functools import wraps

main = Blueprint('main', __name__)

# Authentication decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("Please login first", "error")
            return redirect(url_for('main.home'))
        return f(*args, **kwargs)
    return decorated_function


@main.route('/')
def home():
    return render_template('login.html')



@main.route('/register', methods=['POST'])
def register():
    username = request.form.get('username')
    password = request.form.get('password')
    confirm_password = request.form.get('confirm_password')

    if not username or not password or not confirm_password:
        flash("All fields are required", "error")
        return redirect(url_for('main.home'))

    if password != confirm_password:
        flash("Passwords do not match", "error")
        return redirect(url_for('main.home'))

    conn = get_db_connection()
    user = conn.execute('SELECT * FROM user WHERE username = ?', (username,)).fetchone()

    if user:
        conn.close()
        flash("Username already exists", "error")
        return redirect(url_for('main.home'))

    hashed_pw = generate_password_hash(password)
    conn.execute('INSERT INTO user (username, password_hash) VALUES (?, ?)', (username, hashed_pw))
    conn.commit()
    conn.close()

    flash("Registration successful! Please log in.", "success")
    return redirect(url_for('main.home'))

@main.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')

    conn = get_db_connection()
    user = conn.execute('SELECT * FROM user WHERE username = ?', (username,)).fetchone()
    conn.close()

    if user and check_password_hash(user['password_hash'], password):
        session['user_id'] = user['id']
        session['username'] = username
        flash("Login successful!", "success")
        return redirect(url_for('main.health_data'))
    else:
        flash("Invalid username or password", "error")
        return redirect(url_for('main.home'))

@main.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for('main.home'))

@main.route('/account')
@login_required
def account():
    return render_template('account.html')

@main.route('/upload')
@login_required
def upload():
    # Get exercise types for the dropdown
    exercise_types = get_exercise_types()
    return render_template('upload.html', exercise_types=exercise_types, today=datetime.now().strftime('%Y-%m-%d'))

@main.route('/upload_data', methods=['POST'])
@login_required
def upload_data():
    user_id = session['user_id']
    exercise_type_id = request.form.get('exercise_type', type=int)
    duration = request.form.get('duration', type=int)
    date = request.form.get('date', datetime.now().strftime('%Y-%m-%d'))
    
    # Validate inputs
    if not exercise_type_id or not duration:
        flash("Exercise type and duration are required", "error")
        return redirect(url_for('main.upload'))
    
    # Calculate calories based on exercise type and duration
    calories = calculate_calories(exercise_type_id, duration)
    
    conn = get_db_connection()
    
    # Insert the activity data
    conn.execute(
        '''INSERT INTO activity_data (user_id, exercise_type_id, date, duration_minutes, calories_burnt)
           VALUES (?, ?, ?, ?, ?)''',
        (user_id, exercise_type_id, date, duration, calories)
    )
    
    conn.commit()
    conn.close()
    
    flash("Activity data added successfully!", "success")
    return redirect(url_for('main.visualize'))

@main.route('/visualize')
@login_required
def visualize():
    user_id = session['user_id']
    time_period = request.args.get('period', 'week')
    
    # Get current date
    today = datetime.now().date()
    
    # Calculate date range based on time period
    if time_period == 'week':
        start_date = (today - timedelta(days=6)).strftime('%Y-%m-%d')
        date_format = '%a'  # Abbreviated weekday name
    elif time_period == 'month':
        start_date = (today - timedelta(days=29)).strftime('%Y-%m-%d')
        date_format = '%d %b'  # Day and abbreviated month
    elif time_period == 'year':
        start_date = (today - timedelta(days=364)).strftime('%Y-%m-%d')
        date_format = '%b'  # Abbreviated month name
    else:
        start_date = (today - timedelta(days=6)).strftime('%Y-%m-%d')
        date_format = '%a'
    
    # Query data from database
    conn = get_db_connection()
    activity_data = conn.execute(
        '''SELECT a.date, a.duration_minutes, a.calories_burnt, e.name as exercise_type 
           FROM activity_data a
           JOIN exercise_types e ON a.exercise_type_id = e.id
           WHERE a.user_id = ? AND a.date >= ? 
           ORDER BY a.date ASC''',
        (user_id, start_date)
    ).fetchall()
    conn.close()
    
    # Format data for template
    formatted_data = []
    for row in activity_data:
        date_obj = datetime.strptime(row['date'], '%Y-%m-%d')
        formatted_date = date_obj.strftime(date_format)
        formatted_data.append({
            'date': formatted_date,
            'full_date': row['date'],
            'duration': row['duration_minutes'],
            'calories': row['calories_burnt'],
            'exercise_type': row['exercise_type']
        })
    
    # Pass data to template
    return render_template('visualize.html', 
                           health_data=json.dumps(formatted_data),
                           time_period=time_period,
                           user_id=user_id)

@main.route('/api/health_data')
@login_required
def get_health_data():
    user_id = session['user_id']
    period = request.args.get('period', 'week')
    
    # Calculate date range based on period
    today = datetime.now().date()
    if period == 'week':
        start_date = (today - timedelta(days=6)).strftime('%Y-%m-%d')
        date_format = '%a'
    elif period == 'month':
        start_date = (today - timedelta(days=29)).strftime('%Y-%m-%d')
        date_format = '%d %b'
    elif period == 'year':
        start_date = (today - timedelta(days=364)).strftime('%Y-%m-%d')
        date_format = '%b'
    else:
        start_date = (today - timedelta(days=6)).strftime('%Y-%m-%d')
        date_format = '%a'
    
    # Get data from database
    conn = get_db_connection()
    data = conn.execute(
        '''SELECT a.date, a.duration_minutes, a.calories_burnt, e.name as exercise_type 
           FROM activity_data a
           JOIN exercise_types e ON a.exercise_type_id = e.id
           WHERE a.user_id = ? AND a.date >= ?
           ORDER BY a.date ASC''',
        (user_id, start_date)
    ).fetchall()
    conn.close()
    
    # Format data for JSON response
    formatted_data = []
    for row in data:
        date_obj = datetime.strptime(row['date'], '%Y-%m-%d')
        formatted_date = date_obj.strftime(date_format)
        formatted_data.append({
            'date': formatted_date,
            'full_date': row['date'],
            'duration': row['duration_minutes'],
            'calories': row['calories_burnt'],
            'exercise_type': row['exercise_type']
        })
    
    return jsonify(formatted_data)

@main.route('/api/exercise_types')
def get_api_exercise_types():
    exercise_types = get_exercise_types()
    return jsonify([dict(t) for t in exercise_types])

@main.route('/api/calculate_calories')
def api_calculate_calories():
    exercise_type_id = request.args.get('exercise_type_id', type=int)
    duration = request.args.get('duration', type=int)
    
    if not exercise_type_id or not duration:
        return jsonify({'error': 'Missing required parameters'}), 400
    
    calories = calculate_calories(exercise_type_id, duration)
    return jsonify({'calories': calories})

@main.route('/share_page')
@login_required
def share_page():
    return render_template('share_page.html')

@main.route('/health_data', methods=['POST', 'GET'])
@login_required
def health_data():
    return render_template('health_data.html')

@main.route('/faqs')
def faqs():
    return render_template('faqs.html')

@main.route('/history')
def history():
    return render_template('history.html')

@main.route('/api/share_data', methods=['POST'])
@login_required
def share_data():
    user_id = session['user_id']
    shared_with = request.form.get('shared_with_id')
    content_type = request.form.get('content_type')  # 'activity', 'achievement', 'stats'
    content_id = request.form.get('content_id')
    message = request.form.get('message', '')
    
    # Validate inputs
    if not shared_with or not content_type or not content_id:
        return jsonify({'error': 'Missing required fields'}), 400
    
    conn = get_db_connection()
    
    # Check if the shared_with user exists
    user_exists = conn.execute(
        'SELECT id FROM user WHERE id = ?', 
        (shared_with,)
    ).fetchone()
    
    if not user_exists:
        conn.close()
        return jsonify({'error': 'User not found'}), 404
    
    # Store the share in the database
    conn.execute(
        '''INSERT INTO shared_content (user_id, shared_with_id, content_type, content_id, message, share_date)
           VALUES (?, ?, ?, ?, ?, ?)''',
        (user_id, shared_with, content_type, content_id, message, datetime.now().strftime('%Y-%m-%d'))
    )
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'message': 'Content shared successfully'})

@main.route('/api/shared_with_me')
@login_required
def shared_with_me():
    user_id = session['user_id']
    
    conn = get_db_connection()
    
    # Get data shared with the current user
    shared = conn.execute(
        '''SELECT s.*, u.username as shared_by_username
           FROM shared_content s
           JOIN user u ON s.user_id = u.id
           WHERE s.shared_with_id = ?
           ORDER BY s.share_date DESC''',
        (user_id,)
    ).fetchall()
    
    conn.close()
    
    # Format data for JSON response
    formatted_shared = []
    for row in shared:
        formatted_shared.append({
            'id': row['id'],
            'shared_by': row['shared_by_username'],
            'content_type': row['content_type'],
            'content_id': row['content_id'],
            'message': row['message'],
            'share_date': row['share_date']
        })
    
    return jsonify(formatted_shared)