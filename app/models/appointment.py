"""
Appointment model for the application.
"""
from datetime import datetime
from enum import Enum
from app.extensions import db

class AppointmentStatus(Enum):
    SCHEDULED = 'scheduled'
    COMPLETED = 'completed'
    CANCELLED = 'cancelled'
    NO_SHOW = 'no_show'

class Appointment(db.Model):
    """Appointment model for scheduling sessions."""
    __tablename__ = 'appointments'
    
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)
    professional_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    appointment_datetime = db.Column(db.DateTime, nullable=False)
    duration_minutes = db.Column(db.Integer, default=60)
    status = db.Column(db.Enum(AppointmentStatus), default=AppointmentStatus.SCHEDULED)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    client = db.relationship('Client', backref='appointments')
    professional = db.relationship('User', backref='appointments')
    
    def __repr__(self):
        return f'<Appointment {self.id} - {self.appointment_datetime}>'
    
    def to_dict(self):
        """Convert the appointment object to a dictionary."""
        return {
            'id': self.id,
            'client_id': self.client_id,
            'professional_id': self.professional_id,
            'appointment_datetime': self.appointment_datetime.isoformat(),
            'duration_minutes': self.duration_minutes,
            'status': self.status.value,
            'notes': self.notes,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
