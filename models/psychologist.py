from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash
from typing import Optional, Dict, Any
from datetime import datetime

class Psychologist(UserMixin):
    def __init__(self, id: str, email: str, password_hash: str, 
                 full_name: Optional[str] = None, 
                 specialization: Optional[str] = None,
                 license_number: Optional[str] = None,
                 is_active: bool = True, 
                 failed_login_attempts: int = 0,
                 last_login_at: Optional[datetime] = None,
                 created_at: Optional[datetime] = None,
                 updated_at: Optional[datetime] = None):
        self.id = id
        self.email = email
        self.password_hash = password_hash
        self.full_name = full_name
        self.specialization = specialization
        self.license_number = license_number
        self.is_active = is_active
        self.failed_login_attempts = failed_login_attempts
        self.last_login_at = last_login_at
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
        self.is_psychologist = True  # For role checking

    def check_password(self, password: str) -> bool:
        """Check if the provided password matches the stored hash."""
        return check_password_hash(self.password_hash, password)

    def set_password(self, password: str) -> None:
        """Set a new password for the psychologist."""
        self.password_hash = generate_password_hash(password)
        self.updated_at = datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        """Convert the psychologist object to a dictionary."""
        return {
            'id': self.id,
            'email': self.email,
            'full_name': self.full_name,
            'specialization': self.specialization,
            'license_number': self.license_number,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'last_login_at': self.last_login_at.isoformat() if self.last_login_at else None
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Psychologist':
        """Create a Psychologist instance from a dictionary."""
        return cls(
            id=data['id'],
            email=data['email'],
            password_hash=data['password_hash'],
            full_name=data.get('full_name'),
            specialization=data.get('specialization'),
            license_number=data.get('license_number'),
            is_active=data.get('is_active', True),
            failed_login_attempts=data.get('failed_login_attempts', 0),
            last_login_at=datetime.fromisoformat(data['last_login_at']) if data.get('last_login_at') else None,
            created_at=datetime.fromisoformat(data['created_at']) if data.get('created_at') else None,
            updated_at=datetime.fromisoformat(data['updated_at']) if data.get('updated_at') else None
        )
