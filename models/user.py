from datetime import datetime
from dataclasses import dataclass
from typing import Optional

@dataclass
class User:
    id: str
    email: str
    created_at: datetime
    last_login: Optional[datetime] = None
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            id=data.get('id'),
            email=data.get('email'),
            created_at=datetime.fromisoformat(data.get('created_at')) if data.get('created_at') else None,
            last_login=datetime.fromisoformat(data.get('last_login')) if data.get('last_login') else None,
            full_name=data.get('full_name'),
            avatar_url=data.get('avatar_url')
        )
    
    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'full_name': self.full_name,
            'avatar_url': self.avatar_url
        }
