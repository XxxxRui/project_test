from flask import Blueprint, request, redirect, url_for, render_template, flash, jsonify, session
from app.db_helper import get_db_connection
from werkzeug.security import generate_password_hash, check_password_hash
import json
from datetime import datetime, timedelta

main = Blueprint('main', __name__)


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
        session['user_id'] = user['user_id']
        session['username'] = username
        flash("Login successful!", "success")
        return redirect(url_for('main.account'))
    else:
        flash("Invalid username or password", "error")
        return redirect(url_for('main.home'))

@main.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for('main.home'))

@main.route('/account')
def account():
    if 'user_id' not in session:
        flash("Please login first", "error")
        return redirect(url_for('main.home'))
    return render_template('account.html')

@main.route('/upload')
def upload():
    if 'user_id' not in session:
        flash("Please login first", "error")
        return redirect(url_for('main.home'))
    return render_template('upload.html')

@main.route('/upload_data', methods=['POST'])
def upload_data():
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    user_id = session['user_id']
    steps = request.form.get('steps', type=int)
    calories = request.form.get('calories', type=int)
    sleep = request.form.get('sleep', type=float)
    date = request.form.get('date', datetime.now().strftime('%Y-%m-%d'))
    
    # Validate inputs
    if not steps or not calories:
        flash("Steps and calories are required", "error")
        return redirect(url_for('main.upload'))
    
    conn = get_db_connection()
    
    # Check if an entry already exists for this date
    existing = conn.execute(
        'SELECT * FROM health_data WHERE user_id = ? AND date = ?', 
        (user_id, date)
    ).fetchone()
    
    if existing:
        # Update existing record
        conn.execute(
            '''UPDATE health_data 
               SET steps = ?, calories_burnt = ?, sleep_hours = ?
               WHERE user_id = ? AND date = ?''',
            (steps, calories, sleep, user_id, date)
        )
        flash("Health data updated successfully!", "success")
    else:
        # Insert new record
        conn.execute(
            '''INSERT INTO health_data (user_id, date, steps, calories_burnt, sleep_hours)
               VALUES (?, ?, ?, ?, ?)''',
            (user_id, date, steps, calories, sleep)
        )
        flash("Health data added successfully!", "success")
    
    conn.commit()
    conn.close()
    
    return redirect(url_for('main.visualize'))

@main.route('/visualize')
def visualize():
    if 'user_id' not in session:
        flash("Please login first", "error")
        return redirect(url_for('main.home'))
    
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
    health_data = conn.execute(
        '''SELECT date, steps, calories_burnt, sleep_hours
           FROM health_data 
           WHERE user_id = ? AND date >= ? 
           ORDER BY date ASC''',
        (user_id, start_date)
    ).fetchall()
    conn.close()
    
    # Format data for template
    formatted_data = []
    for row in health_data:
        date_obj = datetime.strptime(row['date'], '%Y-%m-%d')
        formatted_date = date_obj.strftime(date_format)
        formatted_data.append({
            'date': formatted_date,
            'full_date': row['date'],
            'steps': row['steps'],
            'calories': row['calories_burnt'],
            'sleep': row['sleep_hours'] if row['sleep_hours'] else 0
        })
    
    # Pass data to template
    return render_template('visualize.html', 
                           health_data=json.dumps(formatted_data),
                           time_period=time_period,
                           user_id=user_id)

@main.route('/api/health_data')
def get_health_data():
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
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
        '''SELECT date, steps, calories_burnt, sleep_hours
           FROM health_data
           WHERE user_id = ? AND date >= ?
           ORDER BY date ASC''',
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
            'steps': row['steps'],
            'calories': row['calories_burnt'],
            'sleep': row['sleep_hours'] if row['sleep_hours'] else 0
        })
    
    return jsonify(formatted_data)

@main.route('/api/edit_health_data', methods=['POST'])
def edit_health_data():
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    user_id = session['user_id']
    date = request.form.get('date')
    steps = request.form.get('steps', type=int)
    calories = request.form.get('calories', type=int)
    sleep = request.form.get('sleep', type=float)
    
    # Validate inputs
    if not date or not steps or not calories:
        return jsonify({'error': 'Missing required fields'}), 400
    
    conn = get_db_connection()
    
    # Check if the record exists and belongs to the user
    existing = conn.execute(
        'SELECT * FROM health_data WHERE user_id = ? AND date = ?', 
        (user_id, date)
    ).fetchone()
    
    if not existing:
        conn.close()
        return jsonify({'error': 'Record not found or access denied'}), 404
    
    # Update the record
    conn.execute(
        '''UPDATE health_data 
           SET steps = ?, calories_burnt = ?, sleep_hours = ?
           WHERE user_id = ? AND date = ?''',
        (steps, calories, sleep, user_id, date)
    )
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'message': 'Health data updated successfully'})

@main.route('/share_page')
def share_page():
    if 'user_id' not in session:
        flash("Please login first", "error")
        return redirect(url_for('main.home'))
    return render_template('share_page.html')

@main.route('/health_data', methods=['POST', 'GET'])
def health_data():
    if 'user_id' not in session:
        flash("Please login first", "error")
        return redirect(url_for('main.home'))
    return render_template('health_data.html')

@main.route('/faqs')
def faqs():
    return render_template('faqs.html')

@main.route('/history')
def history():
    return render_template('history.html')

@main.route('/api/share_data', methods=['POST'])
def share_data():
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
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
def shared_with_me():
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
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