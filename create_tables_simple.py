from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

# Initialize Flask app
app = Flask(__name__)

# Configure the database
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///unicare.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

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

# Create database tables
def create_tables():
    with app.app_context():
        try:
            print("Creating database tables...")
            db.create_all()
            print("Database tables created successfully!")
            
            # Create a default admin user
            admin = User.query.filter_by(email='admin@example.com').first()
            if not admin:
                admin = User(
                    email='admin@example.com',
                    password='admin123',  # In a real app, hash the password
                    first_name='Admin',
                    last_name='User',
                    is_admin=True
                )
                db.session.add(admin)
                db.session.commit()
                print("Created default admin user")
                
            return True
            
        except Exception as e:
            print(f"Error creating database tables: {str(e)}")
            return False

if __name__ == "__main__":
    if create_tables():
        print("Database setup completed successfully!")
    else:
        print("Database setup failed. Please check the error messages above.")
