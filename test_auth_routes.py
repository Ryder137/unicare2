"""
Test authentication routes.
"""
import sys
import os
from flask import Flask, request, jsonify

# Add the current directory to the Python path
sys.path.insert(0, os.path.abspath('.'))

app = Flask(__name__)
app.config['SECRET_KEY'] = 'test-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test_unicare.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
from app.extensions import db, login_manager
db.init_app(app)
login_manager.init_app(app)

# Import and register auth blueprint
from app.routes.auth import bp as auth_bp
app.register_blueprint(auth_bp, url_prefix='/auth')

@app.route('/')
def index():
    return "Test app is running!"

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5001)
