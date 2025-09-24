"""
Flask extensions module for the application.

This module initializes and configures all Flask extensions used in the application.
"""
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from flask_pymongo import PyMongo
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_wtf.csrf import CSRFProtect
from flask_socketio import SocketIO

# Initialize extensions
db = SQLAlchemy()
mail = Mail()
mongo = PyMongo()
csrf = CSRFProtect()
login_manager = LoginManager()
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)
socketio = SocketIO(cors_allowed_origins="*")

def init_extensions(app):
    """
    Initialize all Flask extensions with the application.
    
    Args:
        app: The Flask application instance
    """
    try:
        # Initialize SQLAlchemy
        db.init_app(app)
        
        # Initialize Flask-Mail if configured
        if app.config.get('MAIL_SERVER'):
            mail.init_app(app)
        
        # Initialize PyMongo if configured
        if app.config.get('MONGODB_URI'):
            mongo.init_app(app, uri=app.config['MONGODB_URI'])
        
        # Initialize CSRF protection
        csrf.init_app(app)
        
        # Configure login manager
        login_manager.init_app(app)
        login_manager.login_view = 'auth.login'
        login_manager.login_message_category = 'info'
        
        # Initialize rate limiting
        limiter.init_app(app)
        
        # Initialize Socket.IO
        socketio.init_app(app)
        
        return app
        
    except Exception as e:
        import logging
        logging.error(f"Failed to initialize extensions: {e}")
        raise
        
        # Initialize rate limiter
        limiter.init_app(app)
        
        # Import and register socket.io events - disabled for debugging
        # try:
        #     from . import events  # This will register socket.io event handlers
        #     app.logger.info("Socket.IO events registered successfully")
        # except ImportError as e:
        #     if 'events' in str(e):
        #         app.logger.warning("Socket.IO events module not found. WebSocket features will be disabled.")
        #     else:
        #         app.logger.error(f"Error importing socket.io events: {e}")
        # except Exception as e:
        #     app.logger.error(f"Error initializing socket.io events: {e}")
        app.logger.info("Socket.IO events initialization skipped for debugging")
        
    except Exception as e:
        app.logger.error(f"Error initializing extensions: {str(e)}")
        raise
    
    # Configure login manager
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login_selector'
    login_manager.login_message_category = 'info'
    
    return app
