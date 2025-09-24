"""
Minimal test script to verify Flask and database connection.
"""
import os
import sys
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Add the current directory to the Python path
sys.path.insert(0, os.path.abspath('.'))

# Create a minimal Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'test-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test_unicare.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy
db = SQLAlchemy()
db.init_app(app)

# Define a simple model
class TestUser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    def __repr__(self):
        return f'<TestUser {self.username}>'

# Create routes
@app.route('/')
def index():
    return 'Test app is running!'

@app.route('/create')
def create_user():
    try:
        user = TestUser(username='testuser', email='test@example.com')
        db.session.add(user)
        db.session.commit()
        return 'User created successfully!'
    except Exception as e:
        return f'Error creating user: {str(e)}'

@app.route('/users')
def list_users():
    users = TestUser.query.all()
    return {'users': [{'id': u.id, 'username': u.username, 'email': u.email} for u in users]}

if __name__ == '__main__':
    with app.app_context():
        # Create all database tables
        db.create_all()
    
    # Run the app
    app.run(debug=True, port=5001)
