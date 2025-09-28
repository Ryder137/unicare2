"""
Minimal Flask application to test authentication routes.
"""
import os
import sys
from flask import Flask, render_template_string

# Add the current directory to the Python path
sys.path.insert(0, os.path.abspath('.'))

app = Flask(__name__)
app.config['SECRET_KEY'] = 'test-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test_unicare.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy
try:
    from flask_sqlalchemy import SQLAlchemy
    db = SQLAlchemy()
    db.init_app(app)
    print("✅ Successfully initialized SQLAlchemy")
except Exception as e:
    print(f"❌ Error initializing SQLAlchemy: {e}")
    db = None

# Initialize LoginManager
try:
    from flask_login import LoginManager
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login_selector'
    print("✅ Successfully initialized LoginManager")
except Exception as e:
    print(f"❌ Error initializing LoginManager: {e}")
    login_manager = None

# Import and register auth blueprint
try:
    from app.routes.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')
    print("✅ Successfully registered auth blueprint")
except Exception as e:
    print(f"❌ Error registering auth blueprint: {e}")

# Simple route for testing
@app.route('/')
def index():
    return "Minimal Flask app is running!"

if __name__ == '__main__':
    with app.app_context():
        if db:
            db.create_all()
    app.run(debug=True, port=5001)
