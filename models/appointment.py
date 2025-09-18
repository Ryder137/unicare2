from datetime import datetime
from .. import db

class Appointment(db.Model):
    __tablename__ = 'appointments'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default='scheduled')  # scheduled, completed, cancelled, no-show
    appointment_type = db.Column(db.String(50))  # guidance, psychologist, etc.
    
    # Relationships
    staff_id = db.Column(db.Integer, db.ForeignKey('admin_users.id'), nullable=False)
    staff = db.relationship('AdminUser', backref=db.backref('appointments_made', lazy=True))
    
    # Can be either guidance counselor or psychologist
    professional_id = db.Column(db.Integer, nullable=False)  # ID of guidance/psychologist
    professional_type = db.Column(db.String(20))  # 'guidance' or 'psychologist'
    
    # Student information
    student_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)
    student = db.relationship('Client', backref=db.backref('appointments', lazy=True))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'start': self.start_time.isoformat(),
            'end': self.end_time.isoformat(),
            'status': self.status,
            'appointment_type': self.appointment_type,
            'staff_id': self.staff_id,
            'professional_id': self.professional_id,
            'professional_type': self.professional_type,
            'student_id': self.student_id,
            'student_name': f"{self.student.first_name} {self.student.last_name}",
            'professional_name': self.get_professional_name(),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    def get_professional_name(self):
        if self.professional_type == 'guidance':
            from .guidance_counselor import GuidanceCounselor
            professional = GuidanceCounselor.query.get(self.professional_id)
        else:  # psychologist
            from .psychologist import Psychologist
            professional = Psychologist.query.get(self.professional_id)
            
        if professional:
            return f"{professional.first_name} {professional.last_name}"
        return "Unknown"
    
    def __repr__(self):
        return f'<Appointment {self.id}: {self.title} - {self.start_time}>'
