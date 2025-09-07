from datetime import datetime, timezone
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import URLSafeTimedSerializer as Serializer
from typing import Optional, Dict, Any
import os

class User(UserMixin):
    def __init__(self, **kwargs):
        # Required by Flask-Login
        self.id = str(kwargs.get('id', ''))  # Ensure ID is always a string
        
        # Set default values for required attributes
        self.is_active = kwargs.get('is_active', True)
        self.is_authenticated = True
        self.is_anonymous = False
        self.is_admin = kwargs.get('is_admin', False)
        
        # User properties with defaults
        self.email = kwargs.get('email', '')
        self.username = kwargs.get('username', self.email.split('@')[0] if '@' in self.email else '')
        self.password_hash = kwargs.get('password_hash') or kwargs.get('password')
        self.is_verified = kwargs.get('is_verified', False)
        self.last_login = kwargs.get('last_login', datetime.now(timezone.utc))
        self.failed_login_attempts = int(kwargs.get('failed_login_attempts', 0))
        self.account_locked_until = kwargs.get('account_locked_until')
        
        # Handle name and personal info fields
        self.full_name = kwargs.get('full_name', '')
        self.first_name = kwargs.get('first_name', '')
        self.last_name = kwargs.get('last_name', '')
        self.gender = kwargs.get('gender')
        self.birthdate = kwargs.get('birthdate')
        self.avatar_url = kwargs.get('avatar_url')
        
        # If no first/last name but have full_name, try to split it
        if not self.first_name and not self.last_name and self.full_name:
            name_parts = self.full_name.split(' ', 1)
            self.first_name = name_parts[0]
            if len(name_parts) > 1:
                self.last_name = name_parts[1]
        # If still no names, try to use username
        elif not self.first_name and not self.last_name and self.username:
            name_parts = self.username.split(' ', 1)
            self.first_name = name_parts[0]
            if len(name_parts) > 1:
                self.last_name = name_parts[1]
        
        self.profile_image = kwargs.get('profile_image') or self.avatar_url
        self.created_at = kwargs.get('created_at', datetime.now(timezone.utc))
        self.updated_at = kwargs.get('updated_at', datetime.now(timezone.utc))
        
        # Handle datetime strings
        def parse_datetime(dt):
            if isinstance(dt, str):
                try:
                    return datetime.fromisoformat(dt.replace('Z', '+00:00'))
                except (ValueError, AttributeError):
                    return datetime.now(timezone.utc)
            return dt or datetime.now(timezone.utc)
        
        self.last_login = parse_datetime(self.last_login)
        self.account_locked_until = parse_datetime(self.account_locked_until) if self.account_locked_until else None
        self.created_at = parse_datetime(self.created_at)
        self.updated_at = parse_datetime(self.updated_at)

    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)
        self.updated_at = datetime.now(timezone.utc)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    def get_reset_token(self, expires_sec=1800):
        """Generate a password reset token for the user."""
        s = Serializer(os.getenv('FLASK_SECRET_KEY', 'dev-secret-key'), expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        """Verify a password reset token and return the user ID if valid."""
        s = Serializer(os.getenv('FLASK_SECRET_KEY', 'dev-secret-key'))
        try:
            user_id = s.loads(token, max_age=1800)['user_id']  # 30 minutes expiration
            return user_id
        except:
            return None

    def get_id(self):
        return str(self.id)

    @classmethod
    def from_dict(cls, data: dict):
        """Create a User instance from a dictionary (e.g., from database)."""
        if not data:
            return None
            
        # Map database fields to User attributes
        user_data = {
            'id': data.get('id'),
            'email': data.get('email', ''),
            'username': data.get('username', data.get('email', '').split('@')[0]),
            'password_hash': data.get('password_hash') or data.get('password'),
            'is_active': data.get('is_active', True),
            'is_verified': data.get('is_verified', False),
            'last_login': data.get('last_login'),
            'failed_login_attempts': data.get('failed_login_attempts', 0),
            'account_locked_until': data.get('account_locked_until'),
            'first_name': data.get('first_name', ''),
            'last_name': data.get('last_name', ''),
            'full_name': data.get('full_name', ''),
            'is_admin': data.get('is_admin', False),
            'profile_image': data.get('profile_image') or data.get('avatar_url'),
            'avatar_url': data.get('avatar_url'),
            'created_at': data.get('created_at'),
            'updated_at': data.get('updated_at')
        }
        
        # Ensure required fields have default values
        if user_data['id'] is None:
            user_data['id'] = ''
            
        return cls(**user_data)
    
    def to_dict(self):
        """Convert the User instance to a dictionary for storage."""
        return {
            'id': self.id,
            'email': self.email,
            'username': self.username,
            'password_hash': self.password_hash,
            'is_active': self.is_active,
            'is_verified': self.is_verified,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'failed_login_attempts': self.failed_login_attempts,
            'account_locked_until': self.account_locked_until.isoformat() if self.account_locked_until else None,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'is_admin': self.is_admin,
            'profile_image': self.profile_image,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
