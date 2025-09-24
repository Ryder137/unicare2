"""
Guidance Counselor model for the application.
"""
from datetime import datetime
from app.extensions import db

class GuidanceCounselor(db.Model):
    """Guidance Counselor model for storing counselor-specific data."""
    __tablename__ = 'guidance_counselors'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    license_number = db.Column(db.String(50), nullable=False, unique=True)
    specialization = db.Column(db.String(100), nullable=True)
    bio = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('guidance_counselor', uselist=False))
    
    def __repr__(self):
        return f'<GuidanceCounselor {self.id}>'
    
    def to_dict(self):
        """Convert the guidance counselor object to a dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'license_number': self.license_number,
            'specialization': self.specialization,
            'bio': self.bio,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
