"""
UNICARE - A Gamified Support System for Mental Health and Emotional Resilience
"""

import os
import sys
import logging
import json
import jwt
import secrets
import bcrypt
from datetime import datetime, timedelta, timezone
from functools import wraps
from threading import Timer

# Add the project root to the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Third-party imports
from flask import (
    Flask, render_template, request, jsonify, session, g, flash, 
    redirect, url_for, current_app, abort, send_from_directory
)
from flask_login import (
    LoginManager, UserMixin, login_user, login_required, 
    logout_user, current_user
)
from flask_pymongo import PyMongo
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from dotenv import load_dotenv
from flask_wtf.csrf import CSRFProtect, generate_csrf
import socketio
from bson.objectid import ObjectId
from flask_mail import Mail, Message

# Initialize Flask app
app = Flask(__name__)

# Load environment variables
load_dotenv()

# Configure app
app.config.update(
    # Flask settings
    SECRET_KEY=os.getenv('FLASK_SECRET_KEY', 'dev-secret-key'),
    FLASK_ENV=os.getenv('FLASK_ENV', 'development'),
    FLASK_DEBUG=os.getenv('FLASK_DEBUG', 'true').lower() == 'true',
    
    # Database settings
    SQLALCHEMY_DATABASE_URI=os.getenv('DATABASE_URL', 'sqlite:///unicare.db'),
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
    
    # MongoDB settings
    MONGODB_URI=os.getenv('MONGODB_URI', 'mongodb://localhost:27017/unicare'),
    
    # Email settings
    MAIL_SERVER=os.getenv('MAIL_SERVER', 'smtp.gmail.com'),
    MAIL_PORT=int(os.getenv('MAIL_PORT', 587)),
    MAIL_USE_TLS=os.getenv('MAIL_USE_TLS', 'true').lower() == 'true',
    MAIL_USERNAME=os.getenv('MAIL_USERNAME'),
    MAIL_PASSWORD=os.getenv('MAIL_PASSWORD'),
    MAIL_DEFAULT_SENDER=os.getenv('MAIL_DEFAULT_SENDER', os.getenv('MAIL_USERNAME')),
    
    # Session settings
    SESSION_COOKIE_SECURE=False,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
    PERMANENT_SESSION_LIFETIME=3600,  # 1 hour
    
    # Server settings
    SERVER_NAME=os.getenv('SERVER_NAME', 'localhost:5000'),
    PREFERRED_URL_SCHEME=os.getenv('PREFERRED_URL_SCHEME', 'http')
)

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if app.config['FLASK_DEBUG'] else logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize extensions
db = SQLAlchemy()
mail = Mail()
csrf = CSRFProtect()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)

# Initialize Socket.IO
sio = socketio.Server(cors_allowed_origins="*")
app.wsgi_app = socketio.WSGIApp(sio, app.wsgi_app)

# Import database service
try:
    from services.database_service import db_service
    logger.info("Successfully imported database service")
except ImportError as e:
    logger.error(f"Failed to import database service: {e}")
    raise

# Initialize extensions with app
db.init_app(app)
mail.init_app(app)
csrf.init_app(app)
login_manager.init_app(app)

# Import models after db initialization to avoid circular imports
from models.user import User
from models.admin_user import AdminUser
from models.appointment import Appointment
from models.client import Client

# Import blueprints
try:
    from routes.auth_routes import auth_bp
    from routes.admin_routes import admin_bp
    from routes.assessment_routes import assessment_bp
    
    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(assessment_bp, url_prefix='/assessments')
    
    logger.info("Successfully registered blueprints")
except ImportError as e:
    logger.error(f"Failed to import blueprints: {e}")
    raise

# Import and register error handlers
try:
    from utils.error_handlers import register_error_handlers
    register_error_handlers(app)
    logger.info("Successfully registered error handlers")
except ImportError as e:
    logger.error(f"Failed to import error handlers: {e}")

# Import and register context processors
try:
    from utils.context_processors import register_context_processors
    register_context_processors(app)
    logger.info("Successfully registered context processors")
except ImportError as e:
    logger.warning(f"Could not register context processors: {e}")

# Import and register template filters
try:
    from utils.filters import register_template_filters
    register_template_filters(app)
    logger.info("Successfully registered template filters")
except ImportError as e:
    logger.warning(f"Could not register template filters: {e}")

# Create database tables if they don't exist
with app.app_context():
    try:
        db.create_all()
        logger.info("Database tables created/verified")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")

# Create default admin user if in development mode
if app.config['FLASK_ENV'] == 'development':
    from scripts.create_admin import create_default_admin
    with app.app_context():
        create_default_admin()

# Main route
@app.route('/')
def index():
    """Render the home page."""
    return render_template('index.html')

# Health check endpoint
@app.route('/health')
def health_check():
    """Health check endpoint for monitoring."""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'environment': app.config['FLASK_ENV']
    }), 200

if __name__ == '__main__':
    # Print startup info
    logger.info(f"Starting UNICARE in {app.config['FLASK_ENV']} mode")
    logger.info(f"Debug mode: {'ON' if app.config['FLASK_DEBUG'] else 'OFF'}")
    logger.info(f"Database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
    
    # Run the app
    app.run(
        host=os.getenv('HOST', '0.0.0.0'),
        port=int(os.getenv('PORT', 5000)),
        debug=app.config['FLASK_DEBUG']
    )
