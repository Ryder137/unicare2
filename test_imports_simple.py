"""
Simple test script to check imports one by one.
"""
import sys
import os

# Add the current directory to the Python path
sys.path.insert(0, os.path.abspath('.'))

print("Testing imports...\n")

# Test 1: Basic Python imports
try:
    import flask
    print("✅ Success: Imported flask")
except ImportError as e:
    print(f"❌ Failed to import flask: {e}")

# Test 2: SQLAlchemy
try:
    from flask_sqlalchemy import SQLAlchemy
    print("✅ Success: Imported SQLAlchemy")
except ImportError as e:
    print(f"❌ Failed to import SQLAlchemy: {e}")

# Test 3: Flask-Login
try:
    from flask_login import LoginManager
    print("✅ Success: Imported LoginManager")
except ImportError as e:
    print(f"❌ Failed to import LoginManager: {e}")

# Test 4: App extensions
try:
    from app.extensions import db
    print("✅ Success: Imported db from app.extensions")
except ImportError as e:
    print(f"❌ Failed to import db from app.extensions: {e}")

# Test 5: User model
try:
    from app.models.user import User
    print("✅ Success: Imported User model")
except ImportError as e:
    print(f"❌ Failed to import User model: {e}")

# Test 6: Auth forms
try:
    from app.forms.auth_forms import LoginForm
    print("✅ Success: Imported LoginForm")
except ImportError as e:
    print(f"❌ Failed to import LoginForm: {e}")

# Test 7: Auth blueprint
try:
    from app.routes.auth import bp as auth_bp
    print("✅ Success: Imported auth blueprint")
except ImportError as e:
    print(f"❌ Failed to import auth blueprint: {e}")

print("\nImport testing complete.")
