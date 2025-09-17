"""
Flask extensions module for the application.
"""
from flask_login import LoginManager
from flask_mail import Mail
from flask_pymongo import PyMongo
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_wtf.csrf import CSRFProtect
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

def init_extensions(app):
    """Initialize all extensions with the Flask application."""
    mail.init_app(app)
    mongo.init_app(app, uri=app.config['MONGO_URI'])
    csrf.init_app(app)
    
    # Configure login manager
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login_selector'
    login_manager.login_message_category = 'info'
    
    # Configure rate limiting
    limiter.init_app(app)
    
    # Configure CSRF protection
    csrf.init_app(app)
    
    return app
