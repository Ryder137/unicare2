import os
import sys
from datetime import datetime, timedelta
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, current_user

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'test-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test_unicare.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Models
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    is_staff = db.Column(db.Boolean, default=False)
    is_student = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def get_id(self):
        return str(self.id)
    
    def __repr__(self):
        return f'<User {self.email}>'

class Appointment(db.Model):
    __tablename__ = 'appointments'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default='scheduled')
    appointment_type = db.Column(db.String(100), nullable=True)
    professional_type = db.Column(db.String(50), nullable=False)
    staff_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
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
            'student_id': self.student_id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    def __repr__(self):
        return f'<Appointment {self.title} - {self.start_time}>'

# Flask-Login user loader
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes for testing
@app.route('/test/setup', methods=['GET'])
def setup_test_data():
    """Set up test data in the database."""
    # Clear existing data
    db.drop_all()
    db.create_all()
    
    # Create test users
    staff = User(
        email='staff@example.com',
        password='staff123',
        first_name='Staff',
        last_name='Member',
        is_staff=True
    )
    
    student = User(
        email='student@example.com',
        password='student123',
        first_name='Student',
        last_name='User',
        is_student=True
    )
    
    db.session.add(staff)
    db.session.add(student)
    db.session.commit()
    
    # Create test appointment
    start_time = datetime.utcnow() + timedelta(days=1)
    end_time = start_time + timedelta(hours=1)
    
    appointment = Appointment(
        title='Initial Consultation',
        description='First meeting with student',
        start_time=start_time,
        end_time=end_time,
        status='scheduled',
        appointment_type='consultation',
        professional_type='counselor',
        staff_id=staff.id,
        student_id=student.id
    )
    
    db.session.add(appointment)
    db.session.commit()
    
    return jsonify({
        'message': 'Test data set up successfully',
        'staff_id': staff.id,
        'student_id': student.id,
        'appointment_id': appointment.id
    })

@app.route('/test/login/<user_type>', methods=['POST'])
def test_login(user_type):
    """Login as a test user."""
    if user_type == 'staff':
        user = User.query.filter_by(email='staff@example.com').first()
    elif user_type == 'student':
        user = User.query.filter_by(email='student@example.com').first()
    else:
        return jsonify({'error': 'Invalid user type'}), 400
    
    if not user:
        return jsonify({'error': 'Test user not found'}), 404
    
    login_user(user)
    return jsonify({'message': f'Logged in as {user.email}'})

@app.route('/test/appointments', methods=['GET'])
@login_required
def list_appointments():
    """List all appointments for the current user."""
    if current_user.is_staff:
        appointments = Appointment.query.filter_by(staff_id=current_user.id).all()
    else:
        appointments = Appointment.query.filter_by(student_id=current_user.id).all()
    
    return jsonify({
        'appointments': [appt.to_dict() for appt in appointments]
    })

if __name__ == '__main__':
    # Create test database
    with app.app_context():
        db.create_all()
    
    # Run the test server
    app.run(debug=True, port=5001)
