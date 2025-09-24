"""
Minimal test to identify the import error.
"""
import sys
import os

# Add the current directory to the Python path
sys.path.insert(0, os.path.abspath('.'))

try:
    print("1. Importing Flask...")
    from flask import Flask
    
    print("2. Creating app...")
    app = Flask(__name__)
    
    print("3. Configuring app...")
    app.config.update(
        SECRET_KEY='test-secret-key',
        SQLALCHEMY_DATABASE_URI='sqlite:///test.db',
        SQLALCHEMY_TRACK_MODIFICATIONS=False
    )
    
    print("4. Initializing extensions...")
    from app.extensions import db
    db.init_app(app)
    
    print("5. Testing model imports...")
    from app.models.user import User
    print(f"✅ User model: {User}")
    
    print("6. Testing form imports...")
    from app.forms.auth_forms import LoginForm, RegisterForm
    print(f"✅ LoginForm: {LoginForm}")
    print(f"✅ RegisterForm: {RegisterForm}")
    
    print("7. Testing route imports...")
    from app.routes.auth import bp as auth_bp
    print(f"✅ Auth blueprint: {auth_bp}")
    
    print("\n✅ All imports successful!")
    
except Exception as e:
    print(f"\n❌ Error: {e}", file=sys.stderr)
    import traceback
    traceback.print_exc()
