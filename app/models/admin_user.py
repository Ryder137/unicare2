"""
Admin User model for the application.
"""
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db

class AdminUser(UserMixin, db.Model):
    """Admin user model for the application."""
    __tablename__ = 'admin_users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))
    is_active = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), 
                         onupdate=db.func.current_timestamp())

    def __repr__(self):
        return f'<AdminUser {self.username}>'

    def set_password(self, password):
        """Create hashed password."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Check hashed password."""
        return check_password_hash(self.password_hash, password)

    @classmethod
    def get_by_username(cls, username):
        """Get admin user by username."""
        return cls.query.filter_by(username=username).first()

    @classmethod
    def get_by_email(cls, email):
        """Get admin user by email."""
        return cls.query.filter_by(email=email).first()

    def to_dict(self):
        """Return admin user data as a dictionary."""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'is_active': self.is_active,
            'is_admin': self.is_admin,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
