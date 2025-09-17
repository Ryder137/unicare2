"""
UNICARE - A Gamified Support System for Mental Health and Emotional Resilience

This package initializes the Flask application and its extensions.
"""
from flask import Flask, render_template
from flask_login import LoginManager
from flask_mail import Mail
from flask_pymongo import PyMongo
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_wtf.csrf import CSRFProtect
import os
from dotenv import load_dotenv
import logging
import socketio

# Initialize extensions
mail = Mail()
mongo = PyMongo()
csrf = CSRFProtect()
login_manager = LoginManager()
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)

# Initialize Socket.IO
sio = socketio.Server(cors_allowed_origins="*", async_mode='threading')

def create_app(config=None):
    """Create and configure the Flask application."""
    # Create the Flask application
    app = Flask(__name__, instance_relative_config=True)
    
    # Load environment variables
    load_dotenv()
    
    # Default configuration
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
        FLASK_DEBUG=os.getenv('FLASK_DEBUG', 'true').lower() == 'true',
        SESSION_COOKIE_SECURE=False,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE='Lax',
        PERMANENT_SESSION_LIFETIME=3600  # 1 hour
    )
    
    # Override with any custom config
    if config:
        app.config.update(config)
    
    # Initialize extensions with app
    mail.init_app(app)
    mongo.init_app(app, uri=app.config['MONGO_URI'])
    csrf.init_app(app)
    limiter.init_app(app)
    
    # Configure login manager
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login_selector'
    login_manager.login_message_category = 'info'
    
    # Import and register blueprints
    from .routes import auth, admin, main, games, assessments
    
    # Register blueprints
    app.register_blueprint(auth.bp)
    app.register_blueprint(admin.bp, url_prefix='/admin')
    app.register_blueprint(games.bp, url_prefix='/games')
    app.register_blueprint(assessments.bp, url_prefix='/assessments')
    app.register_blueprint(main.bp)
    
    # Register error handlers
    register_error_handlers(app)
    
    # Register template filters
    register_template_filters(app)
    
    # Register context processors
    register_context_processors(app)
    
    # Register socket.io
    register_socketio(app)
    
    # Configure logging
    if app.config['FLASK_ENV'] == 'development':
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)
    
    return app

def register_error_handlers(app):
    """Register error handlers for the application."""
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(403)
    def forbidden(e):
        return render_template('errors/403.html'), 403
    
    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('errors/500.html'), 500

def register_template_filters(app):
    """Register custom template filters."""
    from .utils.filters import time_ago, format_datetime
    
    app.jinja_env.filters['time_ago'] = time_ago
    app.jinja_env.filters['format_datetime'] = format_datetime

def register_context_processors(app):
    """Register context processors."""
    from flask import session, g
    
    @app.context_processor
    def inject_user():
        """Inject current user into all templates."""
        from flask_login import current_user
        return dict(current_user=current_user)
    
    @app.context_processor
    def inject_now():
        """Inject current datetime into all templates."""
        from datetime import datetime
        return {'now': datetime.utcnow()}

def register_socketio(app):
    """Register Socket.IO event handlers."""
    from . import events  # Import socket.io event handlers
    
    # Wrap the Flask application with Socket.IO
    app.wsgi_app = socketio.WSGIApp(sio, app.wsgi_app)
    
    @sio.event
    def connect(sid, environ):
        """Handle socket connection."""
        app.logger.debug(f"Client connected: {sid}")
    
    @sio.event
    def disconnect(sid):
        """Handle socket disconnection."""
        app.logger.debug(f"Client disconnected: {sid}")

# Import models to ensure they are registered with Flask-Login
from .models.user import User  # noqa
