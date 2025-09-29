from flask import Flask
from flask_login import LoginManager
from flask_mail import Mail
from flask_pymongo import PyMongo
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os
from dotenv import load_dotenv
import logging

# Initialize extensions
db = SQLAlchemy()
mail = Mail()
mongo = PyMongo()
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)
login_manager = LoginManager()
# Initialize migrate without app first, will be initialized with app later
migrate = Migrate()

def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)
    
    # Load environment variables
    load_dotenv()
    
    # Configure the app
    app.config.update(
        SECRET_KEY=os.getenv('FLASK_SECRET_KEY', 'dev-secret-key'),
        MONGO_URI=os.getenv('MONGODB_URI', 'mongodb://localhost:27017/unicare'),
        SQLALCHEMY_DATABASE_URI=os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost/unicare'),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
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
    db.init_app(app)
    mail.init_app(app)
    mongo.init_app(app)
    limiter.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login_selector'
    
    # Initialize migrate with app and db
    migrate.init_app(app, db)
    
    # Import models to ensure they are registered with SQLAlchemy
    from models import (
        user, 
        game_score, 
        personality_test, 
        admin, 
        psychologist, 
        guidance_counselor,
        admin_user,
        client,
        appointment
    )
    
    # Import models to register them with SQLAlchemy
    from models import (
        user, 
        game_score, 
        personality_test, 
        admin, 
        psychologist, 
        guidance_counselor,
        admin_user,
        client,
        appointment
    )
    
    # Import and register blueprints
    from routes import admin_bp, auth_bp, appointment_bp, guidance_bp, psychologist_bp, assessments_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(appointment_bp, url_prefix='/appointments')
    app.register_blueprint(guidance_bp, url_prefix='/guidance')
    app.register_blueprint(psychologist_bp, url_prefix='/psychologist')
    app.register_blueprint(assessments_bp, url_prefix='/assessments')
    
    # Register filters
    from utils.filters import time_ago
    app.jinja_env.filters['time_ago'] = time_ago
    
    # Configure logging
    if app.config['FLASK_ENV'] == 'development':
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)
    
    return app
