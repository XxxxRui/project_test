from flask import Flask
import os
from flask_wtf.csrf import CSRFProtect

def create_app():
    app = Flask(__name__,
                template_folder=os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates'),
                static_folder=os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static'))

    # Configure app
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'secretkey104')
    app.config['PERMANENT_SESSION_LIFETIME'] = 86400  # Session lifetime in seconds (24 hours)
    
    # Set up CSRF protection
    csrf = CSRFProtect(app)
    
    # Ensure instance folder exists
    os.makedirs(app.instance_path, exist_ok=True)
    
    # Import and initialize database
    from app.db_helper import init_db
    init_db()
    
    # Register blueprints
    from app.routes import main
    app.register_blueprint(main)

    return app