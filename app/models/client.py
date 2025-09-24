"""
Client model for the application.
"""
from datetime import datetime
from app.extensions import db

class Client(db.Model):
    """Client model for storing client-specific data."""
    __tablename__ = 'clients'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=True)
    address = db.Column(db.String(200), nullable=True)
    phone_number = db.Column(db.String(20), nullable=True)
    emergency_contact = db.Column(db.String(100), nullable=True)
    emergency_phone = db.Column(db.String(20), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('client', uselist=False))
    
    def __repr__(self):
        return f'<Client {self.id}>'
    
    def to_dict(self):
        """Convert the client object to a dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'date_of_birth': self.date_of_birth.isoformat() if self.date_of_birth else None,
            'address': self.address,
            'phone_number': self.phone_number,
            'emergency_contact': self.emergency_contact,
            'emergency_phone': self.emergency_phone,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
