"""
Psychologist model for the application.
"""
from datetime import datetime
from app.extensions import db

class Psychologist(db.Model):
    """Psychologist model for storing psychologist-specific data."""
    __tablename__ = 'psychologists'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    license_number = db.Column(db.String(50), nullable=False, unique=True)
    specialization = db.Column(db.String(100), nullable=True)
    years_of_experience = db.Column(db.Integer, nullable=True)
    bio = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('psychologist', uselist=False))
    
    def __repr__(self):
        return f'<Psychologist {self.id}>'
    
    def to_dict(self):
        """Convert the psychologist object to a dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'license_number': self.license_number,
            'specialization': self.specialization,
            'years_of_experience': self.years_of_experience,
            'bio': self.bio,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
