"""
UNICARE - A Gamified Support System for Mental Health and Emotional Resilience

This package initializes the Flask application and its extensions.
"""
import os
import logging
from flask import Flask

# Load environment variables early
from dotenv import load_dotenv
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if os.getenv('FLASK_DEBUG', 'true').lower() == 'true' else logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import extensions (but don't initialize them yet)
from .extensions import db, mail, mongo, csrf, login_manager, limiter, socketio, init_extensions

def create_app(config=None):
    """
    Create and configure the Flask application.
    
    Args:
        config (dict, optional): Configuration overrides. Defaults to None.
        
    Returns:
        Flask: The configured Flask application
    """
    # Create the Flask application
    app = Flask(__name__, instance_relative_config=True)
    
    try:
        # Default configuration
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
            PERMANENT_SESSION_LIFETIME=3600  # 1 hour
        )
        
        # Override with any custom config
        if config:
            app.config.update(config)
        
        # Initialize all extensions
        init_extensions(app)
        
        # Import and register blueprints
        from .routes import auth, admin, main, games, assessments
        
        # Register blueprints
        app.register_blueprint(auth.bp)
        app.register_blueprint(admin.bp, url_prefix='/admin')
        app.register_blueprint(main.bp)
        app.register_blueprint(games.bp, url_prefix='/games')
        app.register_blueprint(assessments.bp, url_prefix='/assessments')
        
        # Import and register error handlers
        from . import errors
        errors.init_app(app)
        
        # Import and register context processors
        from . import context_processors
        context_processors.init_app(app)
        
        logger.info("Application initialized successfully")
        return app
        
    except Exception as e:
        logger.error(f"Failed to initialize application: {e}")
        raise
