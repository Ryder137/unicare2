"""
Minimal Flask application to test imports.
"""
import os
import sys

# Add the current directory to the Python path
sys.path.insert(0, os.path.abspath('.'))

# Basic Flask app
from flask import Flask
app = Flask(__name__)

# Test importing forms
print("\nTesting form imports...")
try:
    from app.forms.auth_forms import LoginForm
    print("✅ Successfully imported LoginForm")
except ImportError as e:
    print(f"❌ Error importing LoginForm: {e}")

try:
    from app.forms.admin_forms import CreateAdminForm
    print("✅ Successfully imported CreateAdminForm")
except ImportError as e:
    print(f"❌ Error importing CreateAdminForm: {e}")

# Test importing models
print("\nTesting model imports...")
try:
    from app.models.user import User
    print("✅ Successfully imported User model")
except ImportError as e:
    print(f"❌ Error importing User model: {e}")

# Test importing routes
print("\nTesting route imports...")
try:
    from app.routes.auth import bp as auth_bp
    print("✅ Successfully imported auth blueprint")
    app.register_blueprint(auth_bp, url_prefix='/auth')
except ImportError as e:
    print(f"❌ Error importing auth blueprint: {e}")

try:
    from app.routes.main import bp as main_bp
    print("✅ Successfully imported main blueprint")
    app.register_blueprint(main_bp)
except ImportError as e:
    print(f"❌ Error importing main blueprint: {e}")

if __name__ == '__main__':
    print("\nStarting minimal test app...")
    app.run(debug=True, port=5001)
