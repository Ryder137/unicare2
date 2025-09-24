"""
UNICARE - Main application entry point
"""
import os
import sys
import logging
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.absolute()
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_default_env():
    """Create a default .env file if it doesn't exist"""
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    if not os.path.exists(env_path):
        try:
            with open(env_path, 'w') as f:
                f.write("""# Flask Configuration
FLASK_APP=app.py
FLASK_ENV=development
FLASK_DEBUG=true
SECRET_KEY=your-very-secret-key-here-make-it-strong

# Database Configuration
DATABASE_URL=sqlite:///unicare.db
SQLALCHEMY_DATABASE_URI=sqlite:///unicare.db
SQLALCHEMY_TRACK_MODIFICATIONS=false

# MongoDB Configuration
MONGODB_URI=mongodb://localhost:27017/unicare

# Email Configuration (GMAIL)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password-here
MAIL_DEFAULT_SENDER=your-email@gmail.com
MAIL_DEBUG=false
""")
            logger.info(f"Created default .env file at {env_path}")
        except Exception as e:
            logger.error(f"Failed to create .env file: {e}")
            raise

def create_app():
    """Create and configure the Flask application"""
    # Create default .env if it doesn't exist
    create_default_env()
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Import app factory
    from app import create_app as app_factory
    
    # Create the application
    app = app_factory()
    
    # Configure login manager
    from flask_login import LoginManager
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    
    # Import models after app creation to avoid circular imports
    from app.models.user import User
    
    # Configure user loader
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Register blueprints
    from app.routes import auth, admin, main, games, assessments
    app.register_blueprint(auth.bp)
    app.register_blueprint(admin.bp, url_prefix='/admin')
    app.register_blueprint(main.bp)
    app.register_blueprint(games.bp, url_prefix='/games')
    app.register_blueprint(assessments.bp, url_prefix='/assessments')
    
    logger.info("Application initialized successfully")
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=app.config.get('FLASK_DEBUG', True))
