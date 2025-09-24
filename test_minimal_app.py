"""
Minimal test application to verify basic functionality.
"""
import os
import sys

# Add the project root to the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def test_imports():
    """Test if we can import the main application components."""
    print("Testing imports...")
    
    # Test Flask and extensions
    try:
        from flask import Flask
        from flask_sqlalchemy import SQLAlchemy
        from flask_login import LoginManager
        print("✅ Core Flask imports successful")
    except ImportError as e:
        print(f"❌ Failed to import Flask components: {e}")
        return False
    
    # Test local imports
    try:
        from app.forms import BaseLoginForm, LoginForm
        print("✅ Form imports successful")
    except ImportError as e:
        print(f"❌ Failed to import forms: {e}")
        return False
    
    # Test database service
    try:
        from services.database_service import db_service
        print("✅ Database service import successful")
    except ImportError as e:
        print(f"❌ Failed to import database service: {e}")
        return False
    
    return True

def create_test_app():
    """Create a minimal test application."""
    from flask import Flask
    
    app = Flask(__name__)
    app.config.update(
        SECRET_KEY='test-secret-key',
        SQLALCHEMY_DATABASE_URI='sqlite:///:memory:',
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        WTF_CSRF_ENABLED=False
    )
    
    # Initialize extensions
    from flask_sqlalchemy import SQLAlchemy
    from flask_login import LoginManager
    
    db = SQLAlchemy(app)
    login_manager = LoginManager(app)
    
    # Import and register blueprints
    try:
        from routes.auth_routes import auth_bp
        app.register_blueprint(auth_bp, url_prefix='/auth')
        print("✅ Registered auth blueprint")
    except Exception as e:
        print(f"❌ Failed to register auth blueprint: {e}")
        return None
    
    return app

if __name__ == '__main__':
    print("=== Starting minimal test ===")
    
    # Test imports first
    if not test_imports():
        print("\n❌ Some imports failed. Please check the errors above.")
        sys.exit(1)
    
    # Create test app
    print("\nCreating test application...")
    app = create_test_app()
    
    if app:
        print("\n✅ Test application created successfully!")
        print("You can now run the main application with: python app.py")
    else:
        print("\n❌ Failed to create test application")
