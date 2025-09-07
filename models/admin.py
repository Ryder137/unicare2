from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash
from typing import Optional, Dict, Any
from datetime import datetime

class Admin(UserMixin):
    def __init__(self, id: str, email: str, password_hash: str, 
                 full_name: Optional[str] = None, 
                 is_active: bool = True, 
                 is_super_admin: bool = False,
                 failed_login_attempts: int = 0,
                 last_login_at: Optional[datetime] = None,
                 created_at: Optional[datetime] = None,
                 updated_at: Optional[datetime] = None):
        self.id = id
        self.email = email
        self.password_hash = password_hash
        self.full_name = full_name
        self.is_active = is_active
        self.is_super_admin = is_super_admin
        self.failed_login_attempts = failed_login_attempts
        self.last_login_at = last_login_at
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
        self.is_admin = True  # For Flask-Login compatibility

    def check_password(self, password: str) -> bool:
        """Check if the provided password matches the stored hash."""
        return check_password_hash(self.password_hash, password)
        
    def get_all_users_count(self) -> int:
        """Get the total count of all users in the system."""
        from services.database_service import db_service
        try:
            # Get counts for different user types
            users_count = db_service.get_users_count()
            admins_count = db_service.get_admins_count()
            psychologists_count = db_service.get_psychologists_count()
            
            # Return the sum of all user types
            return users_count + admins_count + psychologists_count
        except Exception as e:
            print(f"Error getting users count: {str(e)}")
            return 0

    def get_id(self) -> str:
        """Return the admin ID as a string."""
        return str(self.id)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Admin':
        """Create an Admin instance from a dictionary."""
        return cls(
            id=data.get('id'),
            email=data['email'],
            password_hash=data['password_hash'],
            full_name=data.get('full_name'),
            is_active=data.get('is_active', True),
            is_super_admin=data.get('is_super_admin', False),
            failed_login_attempts=data.get('failed_login_attempts', 0),
            last_login_at=cls._parse_datetime(data.get('last_login_at')),
            created_at=cls._parse_datetime(data.get('created_at')),
            updated_at=cls._parse_datetime(data.get('updated_at'))
        )

    @staticmethod
    def _parse_datetime(dt_str: Optional[str]) -> Optional[datetime]:
        """Parse a datetime string into a datetime object."""
        if not dt_str:
            return None
        try:
            # Handle both with and without timezone
            if 'T' in dt_str:
                if 'Z' in dt_str or '+' in dt_str or dt_str.endswith('+00:00'):
                    return datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
                return datetime.fromisoformat(dt_str)
            return datetime.strptime(dt_str, '%Y-%m-%d %H:%M:%S')
        except (ValueError, TypeError):
            return None