"""
Content model for the application.
"""
from datetime import datetime
from app.extensions import db

class Content(db.Model):
    """Content model for storing content management data."""
    __tablename__ = 'content_management'
    
    id = db.Column(db.String(36), primary_key=True)  # UUID as string for Supabase
    author = db.Column(db.String(100), nullable=False)
    messages = db.Column(db.Text, nullable=False)
    content_type = db.Column(db.String(50), nullable=True, default='general')
    is_active = db.Column(db.Boolean, default=True)
    created_by = db.Column(db.String(100), nullable=True)
    updated_by = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Content {self.id}: {self.author}>'
    
    def to_dict(self):
        """Convert the content object to a dictionary."""
        return {
            'id': self.id,
            'author': self.author,
            'messages': self.messages,
            'content_type': self.content_type,
            'is_active': self.is_active,
            'created_by': self.created_by,
            'updated_by': self.updated_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create a Content object from a dictionary."""
        return cls(
            id=data.get('id'),
            author=data.get('author'),
            messages=data.get('messages'),
            content_type=data.get('content_type', 'general'),
            is_active=data.get('is_active', True),
            created_by=data.get('created_by'),
            updated_by=data.get('updated_by')
        )