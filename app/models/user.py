"""
User model for the application.
"""
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from bson import ObjectId
from datetime import datetime

class User(UserMixin):
    """User class that implements Flask-Login's UserMixin."""
    
    def __init__(self, user_data):
        """Initialize user with data from database."""
        self.id = str(user_data.get('_id'))
        self.email = user_data.get('email')
        self.password_hash = user_data.get('password')
        self.first_name = user_data.get('first_name', '')
        self.last_name = user_data.get('last_name', '')
        self.is_admin = user_data.get('is_admin', False)
        self.is_active = user_data.get('is_active', True)
        self.created_at = user_data.get('created_at', datetime.utcnow())
        self.last_login = user_data.get('last_login')
        self.avatar = user_data.get('avatar')
    
    def get_id(self):
        """Return the user ID as a string."""
        return str(self.id)
    
    def set_password(self, password):
        """Set the user's password."""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if the provided password matches the user's password."""
        return check_password_hash(self.password_hash, password)
    
    def update_last_login(self):
        """Update the user's last login timestamp."""
        from ..extensions import mongo
        self.last_login = datetime.utcnow()
        mongo.db.users.update_one(
            {'_id': ObjectId(self.id)},
            {'$set': {'last_login': self.last_login}}
        )
    
    @classmethod
    def get_by_id(cls, user_id):
        """Get a user by ID."""
        from ..extensions import mongo
        user_data = mongo.db.users.find_one({'_id': ObjectId(user_id)})
        if user_data:
            return cls(user_data)
        return None
    
    @classmethod
    def get_by_email(cls, email):
        """Get a user by email."""
        from ..extensions import mongo
        user_data = mongo.db.users.find_one({'email': email.lower()})
        if user_data:
            return cls(user_data)
        return None
    
    def to_dict(self):
        """Convert user object to dictionary."""
        return {
            'id': self.id,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'is_admin': self.is_admin,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'avatar': self.avatar
        }
    
    @classmethod
    def create(cls, email, password, first_name='', last_name='', is_admin=False):
        """Create a new user."""
        from ..extensions import mongo
        
        if cls.get_by_email(email):
            return None  # User already exists
        
        user_data = {
            'email': email.lower(),
            'password': generate_password_hash(password),
            'first_name': first_name,
            'last_name': last_name,
            'is_admin': is_admin,
            'is_active': True,
            'created_at': datetime.utcnow(),
            'last_login': None,
            'avatar': None
        }
        
        result = mongo.db.users.insert_one(user_data)
        user_data['_id'] = result.inserted_id
        return cls(user_data)
