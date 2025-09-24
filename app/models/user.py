"""
User model for the application.
"""
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from ..extensions import db

class User(UserMixin, db.Model):
    """User model that implements Flask-Login's UserMixin and SQLAlchemy Model."""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    first_name = db.Column(db.String(50), nullable=False, default='')
    last_name = db.Column(db.String(50), nullable=False, default='')
    is_admin = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    avatar = db.Column(db.String(256))
    
    # Relationships
    appointments = db.relationship('Appointment', backref='user', lazy='dynamic')
    
    def __repr__(self):
        return f'<User {self.email}>'
    
    # Flask-Login required properties and methods
    @property
    def is_authenticated(self):
        """Return True if the user is authenticated."""
        return True
    
    @property
    def is_active(self):
        """Return True if the user is active."""
        return self.is_active
    
    @property
    def is_anonymous(self):
        """Return False as anonymous users are not supported."""
        return False
    
    def get_id(self):
        """Return the user ID as a string."""
        return str(self.id)
    
    def set_password(self, password):
        """Set the user's password."""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if the provided password matches the user's password."""
        return check_password_hash(self.password_hash, password)
    
    def update_last_login(self):
        """Update the user's last login timestamp."""
        self.last_login = datetime.utcnow()
        db.session.commit()
    
    @classmethod
    def get_by_id(cls, user_id):
        """Get a user by ID."""
        return cls.query.get(int(user_id))
    
    @classmethod
    def get_by_email(cls, email):
        """Get a user by email (case-insensitive)."""
        return cls.query.filter(db.func.lower(cls.email) == email.lower()).first()
    
    @classmethod
    def create(cls, email, password, first_name='', last_name='', is_admin=False, **kwargs):
        """Create a new user."""
        user = cls(
            email=email.lower(),
            first_name=first_name,
            last_name=last_name,
            is_admin=is_admin,
            **kwargs
        )
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return user
    
    def update(self, **kwargs):
        """Update user attributes."""
        for key, value in kwargs.items():
            if hasattr(self, key) and key != 'id':
                setattr(self, key, value)
        db.session.commit()
        return self
    
    def delete(self):
        """Delete the user."""
        db.session.delete(self)
        db.session.commit()
    
    def to_dict(self):
        """Return user data as a dictionary."""
        return {
            'id': self.id,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'is_admin': self.is_admin,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'avatar': self.avatar
        }
