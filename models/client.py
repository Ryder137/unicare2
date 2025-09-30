from datetime import datetime
from .base import BaseModel, UserMixinExtended
from . import db

class Client(BaseModel, UserMixinExtended):
    """Client model representing students in the system"""
    __tablename__ = 'clients'
    
    # Extended user fields
    student_id = db.Column(db.String(50), unique=True, nullable=True)
    date_of_birth = db.Column(db.Date, nullable=True)
    address = db.Column(db.Text, nullable=True)
    
    # Relationships
    appointments = db.relationship('Appointment', 
                                 back_populates='client', 
                                 lazy='dynamic',
                                 cascade='all, delete-orphan')
    
    # Additional methods specific to Client
    @property
    def age(self):
        """Calculate age from date of birth"""
        if not self.date_of_birth:
            return None
        today = datetime.utcnow().date()
        return today.year - self.date_of_birth.year - (
            (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
        )
    
    def to_dict(self):
        """Convert client to dictionary"""
        return {
            'id': self.id,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'full_name': self.full_name,
            'student_id': self.student_id,
            'date_of_birth': self.date_of_birth.isoformat() if self.date_of_birth else None,
            'phone_number': self.phone_number,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
