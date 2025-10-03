from datetime import datetime, timezone
from typing import Optional, Any, Dict
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from models.accounts import AccountsModelDto

class User(UserMixin):
    def __init__(self, **kwargs):
        # Required by Flask-Login
        self.id = str(kwargs.get('id', ''))  # Ensure ID is always a string
        
        # Initialize Flask-Login properties with defaults
        self._is_active = kwargs.get('is_active', True)
        self._is_authenticated = True
        self._is_anonymous = False
        
        # User properties with defaults
        self.email = kwargs.get('email', '')
        self.username = kwargs.get('username', self.email.split('@')[0] if '@' in self.email else '')
        self.password_hash = kwargs.get('password_hash') or kwargs.get('password')
        self.is_verified = kwargs.get('is_verified', False)
        
        # Admin and staff properties
        self._is_admin = kwargs.get('is_admin', False)
        self._is_super_admin = kwargs.get('is_super_admin', False)
        self._is_staff = kwargs.get('is_staff', self._is_admin or self._is_super_admin)
        
        # Handle datetime fields
        self.created_at = self._parse_datetime(kwargs.get('created_at'))
        self.last_login = self._parse_datetime(kwargs.get('last_login'))
        self.account_locked_until = self._parse_datetime(kwargs.get('account_locked_until'))
        
        # Handle name fields
        self.full_name = kwargs.get('full_name', '')
        self.first_name = kwargs.get('first_name', '')
        self.last_name = kwargs.get('last_name', '')
        self.avatar_url = kwargs.get('avatar_url')
        self.profile_image = kwargs.get('profile_image', '')
        
        # Handle name splitting if full_name is provided but first/last aren't
        if not self.first_name and not self.last_name and self.full_name:
            name_parts = self.full_name.split(' ', 1)
            self.first_name = name_parts[0]
            if len(name_parts) > 1:
                self.last_name = name_parts[1]
    
    @classmethod
    def get_all_users_count(cls):
        """Get the total count of all users (non-admin)."""
        from app import db_service
        return db_service.get_users_count()
        
    def _parse_datetime(self, dt_value):
        """Helper method to parse datetime from string or return as is."""
        if dt_value is None:
            return None
        if isinstance(dt_value, str):
            try:
                # Handle both 'Z' and timezone offset formats
                if dt_value.endswith('Z'):
                    dt_value = dt_value[:-1] + '+00:00'
                return datetime.fromisoformat(dt_value).replace(tzinfo=timezone.utc) 
            except (ValueError, AttributeError) as e:
                print(f"[WARNING] Could not parse datetime {dt_value}: {e}")
                return datetime.now(timezone.utc)
        elif isinstance(dt_value, datetime):
            return dt_value.replace(tzinfo=timezone.utc) if dt_value.tzinfo is None else dt_value
        return None
    
    def set_password(self, password: str) -> None:
        """Set the user's password."""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password: str) -> bool:
        """Check if the provided password matches the stored hash."""
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)
    
    def to_user_dto_obj(data: Dict[str, Any]):
        """ Convert database response to user data transfer object """
        if not data:
            return None
        # Map database fields to User attributes
        email = data.get('email', '')
        user_obj = AccountsModelDto(
            id = data.get('id'),
            first_name = data.get('first_name', ''),
            middle_name = data.get('middle_name', ''),
            last_name = data.get('last_name', ''),
            email = data.get('email', ''),
            role = data.get('role', 'client'),
            password = data.get('password'),
            is_deleted = data.get('is_deleted', False),
            is_active = data.get('is_active', True),
            is_verified = data.get('is_verified', False),
            image = data.get('image', ''),
            created_at = data.get('created_at'),
            failed_attempt = data.get('failed_attempt', 0),
            last_login_at = data.get('last_login'),
            is_authenticated = True,
            username= email.split('@')[0]
        )
        return user_obj
    
    # Flask-Login required properties with getters and setters
    @property
    def is_active(self) -> bool:
        """Required by Flask-Login."""
        return self._is_active
        
    @is_active.setter
    def is_active(self, value: bool) -> None:
        """Set the active status of the user."""
        self._is_active = bool(value)
        
    @property
    def is_authenticated(self) -> bool:
        """Required by Flask-Login."""
        return self._is_authenticated
        
    @is_authenticated.setter
    def is_authenticated(self, value: bool) -> None:
        """Set the authenticated status of the user."""
        self._is_authenticated = bool(value)
        
    @property
    def is_anonymous(self) -> bool:
        """Required by Flask-Login."""
        return self._is_anonymous
        
    @is_anonymous.setter
    def is_anonymous(self, value: bool) -> None:
        """Set the anonymous status of the user."""
        self._is_anonymous = bool(value)
    
    @property
    def is_admin(self) -> bool:
        """Check if the user is an admin."""
        return self._is_admin
        
    @is_admin.setter
    def is_admin(self, value: bool) -> None:
        """Set the admin status of the user."""
        self._is_admin = bool(value)
    
    @property
    def is_super_admin(self) -> bool:
        """Check if the user is a super admin."""
        return self._is_super_admin
        
    @is_super_admin.setter
    def is_super_admin(self, value: bool) -> None:
        """Set the super admin status of the user."""
        self._is_super_admin = bool(value)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the User instance to a dictionary for storage."""
        return {
            'id': self.id,
            'email': self.email,
            'username': self.username,
            'is_active': self._is_active,
            'is_verified': self.is_verified,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'account_locked_until': self.account_locked_until.isoformat() if self.account_locked_until else None,
            'full_name': self.full_name,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'avatar_url': self.avatar_url,
            'profile_image': self.profile_image,
            'is_admin': self.is_admin,
            'is_super_admin': self.is_super_admin
        }
    
    def get_id(self) -> str:
        """Required by Flask-Login."""
        return str(self.id)
