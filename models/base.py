from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class BaseModel(db.Model):
    """Base model with common fields and methods"""
    __abstract__ = True
    
    id = db.Column(db.Integer, primary_key=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def save(self):
        """Save the current instance to the database"""
        db.session.add(self)
        db.session.commit()
        return self
    
    def delete(self):
        """Soft delete the current instance"""
        self.is_active = False
        db.session.commit()
    
    @classmethod
    def get_by_id(cls, id):
        """Get an instance by ID"""
        return cls.query.filter_by(id=id, is_active=True).first()


class UserMixinExtended(UserMixin):
    """Extended UserMixin with common user fields and methods"""
    __table_args__ = {'extend_existing': True}
    
    # Authentication fields
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=True)
    is_verified = db.Column(db.Boolean, default=False, nullable=False)
    last_login = db.Column(db.DateTime, nullable=True)
    
    # Profile fields
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    phone_number = db.Column(db.String(20), nullable=True)
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def set_password(self, password):
        """Set password hash from plain password"""
        from werkzeug.security import generate_password_hash
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if the password matches the hash"""
        from werkzeug.security import check_password_hash
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<{self.__class__.__name__} {self.email}>'
