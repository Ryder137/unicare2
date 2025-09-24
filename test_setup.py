"""
Clean test script to verify the application setup.
"""
import os
import sys
from flask import Flask

# Add the current directory to the Python path
sys.path.insert(0, os.path.abspath('.'))

def test_imports():
    """Test all necessary imports."""
    print("\n=== Testing Imports ===")
    
    # Test Flask and extensions
    try:
        from flask import Flask
        from flask_sqlalchemy import SQLAlchemy
        from flask_login import LoginManager
        from flask_mail import Mail
        from flask_pymongo import PyMongo
        print("✅ All Flask extensions imported successfully")
    except ImportError as e:
        print(f"❌ Error importing Flask extensions: {e}")
        return False
    
    # Test app imports
    try:
        from app.extensions import db, mail, mongo, login_manager
        print("✅ App extensions imported successfully")
    except ImportError as e:
        print(f"❌ Error importing app extensions: {e}")
        return False
    
    # Test models
    try:
        from app.models.user import User
        print("✅ User model imported successfully")
    except ImportError as e:
        print(f"❌ Error importing User model: {e}")
        return False
    
    # Test forms
    try:
        from app.forms.auth_forms import LoginForm, RegisterForm
        print("✅ Auth forms imported successfully")
    except ImportError as e:
        print(f"❌ Error importing auth forms: {e}")
        return False
    
    return True

def test_database():
    """Test database connection and models."""
    print("\n=== Testing Database ===")
    
    from app import create_app
    from app.extensions import db
    from app.models.user import User
    
    # Create test app
    app = create_app()
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test_unicare.db'
    app.config['TESTING'] = True
    
    with app.app_context():
        try:
            # Create tables
            db.create_all()
            print("✅ Database tables created successfully")
            
            # Test User model
            user = User(
                email='test@example.com',
                first_name='Test',
                last_name='User',
                is_admin=False
            )
            user.set_password('test123')
            
            db.session.add(user)
            db.session.commit()
            print("✅ User created successfully")
            
            # Clean up
            db.session.delete(user)
            db.session.commit()
            print("✅ Test user cleaned up")
            
            return True
            
        except Exception as e:
            print(f"❌ Database error: {e}")
            return False

if __name__ == '__main__':
    if test_imports():
        print("\nAll imports successful!")
    
    if test_database():
        print("\nDatabase tests passed!")
    
    print("\nTest complete!")
