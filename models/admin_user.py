from .base import BaseModel, UserMixinExtended
from . import db
from datetime import datetime

class AdminUser(BaseModel, UserMixinExtended):
    """Admin/Staff user model with extended permissions"""
    __tablename__ = 'admin_users'
    
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Extended user fields
    role = db.Column(db.String(20), nullable=False, default='staff')  # 'admin' or 'staff'
    department = db.Column(db.String(100), nullable=True)
    
    # Relationships
    appointments_made = db.relationship(
        'Appointment', 
        backref='staff_member', 
        lazy='dynamic',
        cascade='all, delete-orphan'
    )
    
    # Role-based properties
    @property
    def is_admin(self):
        return self.role == 'admin'
    
    @property
    def is_staff(self):
        return self.role in ['admin', 'staff']
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def to_dict(self):
        """Convert admin user to dictionary"""
        return {
            'id': self.id,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'full_name': self.get_full_name(),
            'role': self.role,
            'department': self.department,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'is_admin': self.is_admin,
            'is_staff': self.is_staff
        }
    
    def __repr__(self):
        return f'<AdminUser {self.email}>'
