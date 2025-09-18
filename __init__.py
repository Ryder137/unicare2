from flask import Flask
from flask_login import LoginManager
from flask_mail import Mail
from flask_pymongo import PyMongo
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import os
from dotenv import load_dotenv
import logging

# Initialize extensions
mail = Mail()
mongo = PyMongo()
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)
login_manager = LoginManager()

def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)
    
    # Load environment variables
    load_dotenv()
    
    # Configure the app
    app.config.update(
        SECRET_KEY=os.getenv('FLASK_SECRET_KEY', 'dev-secret-key'),
        MONGO_URI=os.getenv('MONGODB_URI', 'mongodb://localhost:27017/unicare'),
        MAIL_SERVER=os.getenv('MAIL_SERVER', 'smtp.gmail.com'),
        MAIL_PORT=int(os.getenv('MAIL_PORT', 587)),
        MAIL_USE_TLS=os.getenv('MAIL_USE_TLS', 'true').lower() == 'true',
        MAIL_USERNAME=os.getenv('MAIL_USERNAME'),
        MAIL_PASSWORD=os.getenv('MAIL_PASSWORD'),
        MAIL_DEFAULT_SENDER=os.getenv('MAIL_DEFAULT_SENDER', os.getenv('MAIL_USERNAME')),
        FLASK_ENV=os.getenv('FLASK_ENV', 'development'),
        FLASK_DEBUG=os.getenv('FLASK_DEBUG', 'true').lower() == 'true'
    )
    
    # Initialize extensions with app
    mail.init_app(app)
    mongo.init_app(app)
    limiter.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login_selector'
    
    # Register blueprints
    from routes import admin_bp, auth_bp, appointment_bp
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(appointment_bp, url_prefix='')
    
    # Register filters
    from utils.filters import time_ago
    app.jinja_env.filters['time_ago'] = time_ago
    
    # Configure logging
    if app.config['FLASK_ENV'] == 'development':
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)
    
    return app
