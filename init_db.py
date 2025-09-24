import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Initialize Flask app
app = Flask(__name__)

# Configure the database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///unicare.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# Define models
class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<User {self.email}>'

class Appointment(db.Model):
    __tablename__ = 'appointments'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(50), default='scheduled')
    appointment_type = db.Column(db.String(100))
    professional_type = db.Column(db.String(50))
    professional_id = db.Column(db.Integer)
    staff_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Appointment {self.title} ({self.start_time} - {self.end_time})>'

def init_db():
    """Initialize the database."""
    # Ensure the instance folder exists
    os.makedirs('instance', exist_ok=True)
    
    # Create database tables
    with app.app_context():
        try:
            # Drop all existing tables
            db.drop_all()
            print("Dropped all existing tables.")
            
            # Create all tables
            db.create_all()
            print("Created database tables.")
            
            # Create a default admin user
            admin = User(
                email='admin@example.com',
                password='admin123',  # In production, hash this password
                first_name='Admin',
                last_name='User',
                is_admin=True
            )
            db.session.add(admin)
            
            # Create a test appointment
            from datetime import datetime, timedelta
            start_time = datetime.utcnow() + timedelta(days=1)
            end_time = start_time + timedelta(hours=1)
            
            appointment = Appointment(
                title='Initial Consultation',
                description='First appointment with student',
                start_time=start_time,
                end_time=end_time,
                status='scheduled',
                appointment_type='consultation',
                professional_type='counselor',
                professional_id=1,
                staff_id=1,
                student_id=1
            )
            db.session.add(appointment)
            
            db.session.commit()
            print("Added default admin user and test appointment.")
            
            print("\nDatabase initialized successfully!")
            print(f"Database file: {os.path.abspath('instance/unicare.db')}")
            
        except Exception as e:
            db.session.rollback()
            print(f"Error initializing database: {str(e)}")
            raise

if __name__ == '__main__':
    print("Initializing database...")
    init_db()
