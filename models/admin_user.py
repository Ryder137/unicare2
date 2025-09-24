from . import db
from flask_login import UserMixin
from datetime import datetime

class AdminUser(db.Model, UserMixin):
    __tablename__ = 'admin_users'
    
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    appointments_made = db.relationship('Appointment', backref='staff_member', lazy=True)
    
    def __repr__(self):
        return f'<AdminUser {self.email}>'
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"
