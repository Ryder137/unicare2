from datetime import datetime, timezone
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import URLSafeTimedSerializer as Serializer
from typing import Optional, Dict, Any
import os

class User(UserMixin):
    def __init__(self, id: str, email: str, username: str = None, 
                 password_hash: str = None, is_active: bool = True, 
                 is_verified: bool = False, last_login: datetime = None,
                 failed_login_attempts: int = 0, account_locked_until: datetime = None):
        self.id = str(id)  # Ensure ID is always a string
        self.email = email
        self.username = username or email.split('@')[0]
        self.password_hash = password_hash
        self.is_active = is_active
        self.is_verified = is_verified
        self.last_login = last_login or datetime.now(timezone.utc)
        self.failed_login_attempts = failed_login_attempts
        self.account_locked_until = account_locked_until
        self.created_at = datetime.now(timezone.utc)
        self.updated_at = datetime.now(timezone.utc)

    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)
        self.updated_at = datetime.now(timezone.utc)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    def get_reset_token(self, expires_sec=1800):
        s = Serializer(os.getenv('SECRET_KEY'), expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(os.getenv('SECRET_KEY'))
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return user_id
        self.first_name = first_name or username  # fallback for nav
        self.last_name = last_name
        self.profile_image = profile_image
        self.password = password  # only for login check, not exposed elsewhere
        
        # Required by Flask-Login
        self.is_active = True
        self.is_authenticated = True
        self.is_anonymous = False

    def get_id(self):
        return str(self.id)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        return cls(
            id=str(data.get('id', '')),
            username=data.get('username', data.get('email', '').split('@')[0]),  # Fallback to email prefix
            email=data.get('email', ''),
            first_name=data.get('first_name'),
            last_name=data.get('last_name'),
            profile_image=data.get('profile_image'),
            password=data.get('password')
        )
