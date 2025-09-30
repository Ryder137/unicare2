from datetime import datetime, time
from . import db
from sqlalchemy.ext.hybrid import hybrid_property

class Appointment(db.Model):
    __tablename__ = 'appointments'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default='scheduled')  # scheduled, completed, cancelled, no-show
    appointment_type = db.Column(db.String(50), nullable=True)  # initial, follow-up, emergency, etc.
    professional_type = db.Column(db.String(20), nullable=False)  # guidance or psychologist
    
    # Relationships
    staff_id = db.Column(db.Integer, db.ForeignKey('admin_users.id'), nullable=False)
    staff = db.relationship('AdminUser', backref=db.backref('staff_appointments', lazy=True))
    professional_id = db.Column(db.Integer, nullable=False)  # ID of either guidance or psychologist
    user_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)
    # Using back_populates instead of backref to avoid conflicts
    client = db.relationship('Client', back_populates='appointments')
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Appointment {self.title} - {self.start_time}>'
        
    def to_dict(self):
        """Convert the appointment to a dictionary for JSON serialization."""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat(),
            'status': self.status,
            'appointment_type': self.appointment_type,
            'professional_type': self.professional_type,
            'staff_id': self.staff_id,
            'professional_id': self.professional_id,
            'student_id': self.student_id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'duration': self.duration,
            'is_past': self.is_past,
            'is_upcoming': self.is_upcoming,
            'is_ongoing': self.is_ongoing
        }
    
    @hybrid_property
    def duration(self):
        """Return the duration of the appointment in minutes."""
        return int((self.end_time - self.start_time).total_seconds() / 60)
    
    @hybrid_property
    def is_past(self):
        """Check if the appointment is in the past."""
        return self.end_time < datetime.utcnow()
    
    @hybrid_property
    def is_upcoming(self):
        """Check if the appointment is in the future."""
        return self.start_time > datetime.utcnow()
    
    @hybrid_property
    def is_ongoing(self):
        """Check if the appointment is currently ongoing."""
        now = datetime.utcnow()
        return self.start_time <= now <= self.end_time
    
    def get_professional_name(self):
        """Get the name of the professional (guidance or psychologist)."""
        if self.professional_type == 'guidance':
            from .guidance_counselor import GuidanceCounselor
            professional = GuidanceCounselor.query.get(self.professional_id)
        else:
            from .psychologist import Psychologist
            professional = Psychologist.query.get(self.professional_id)
            
        if professional:
            if hasattr(professional, 'full_name'):
                return professional.full_name
            elif hasattr(professional, 'first_name'):
                return f"{professional.first_name} {professional.last_name}"
        return 'Unknown'
    
    def to_dict(self):
        """Convert the appointment to a dictionary for JSON serialization."""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat(),
            'status': self.status,
            'appointment_type': self.appointment_type,
            'professional_type': self.professional_type,
            'staff_id': self.staff_id,
            'professional_id': self.professional_id,
            'student_id': self.student_id,
            'professional_name': self.get_professional_name(),
            'student_name': f"{self.student.first_name} {self.student.last_name}",
            'duration': self.duration,
            'is_past': self.is_past,
            'is_upcoming': self.is_upcoming,
            'is_ongoing': self.is_ongoing,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
