from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from services.database_service import db_service
from functools import wraps

guidance_bp = Blueprint('guidance', __name__, url_prefix='/guidance')

def guidance_required(f):
    """Decorator to ensure the user is a guidance counselor."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('auth.user_login'))
        if not hasattr(current_user, 'is_guidance_counselor') or not current_user.is_guidance_counselor:
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

@guidance_bp.route('/dashboard')
@login_required
@guidance_required
def dashboard():
    """Guidance counselor dashboard."""
    # Get dashboard statistics (example - replace with actual data)
    stats = {
        'upcoming_appointments': 7,
        'active_students': 45,
        'pending_requests': 6,
        'total_sessions': 128
    }
    
    # Get today's schedule (example - replace with actual data)
    today_schedule = [
        {
            'title': 'Meeting with Student',
            'time': '9:00 AM - 9:45 AM',
            'details': 'John Smith - Academic Advising',
            'location': 'Room 205'
        },
        {
            'title': 'Group Session',
            'time': '11:00 AM - 12:00 PM',
            'details': 'Stress Management Workshop',
            'location': 'Guidance Office'
        },
        {
            'title': 'Parent Meeting',
            'time': '2:30 PM - 3:15 PM',
            'details': 'Sarah Johnson (Parent of Emily Johnson)',
            'location': 'Conference Room B'
        }
    ]
    
    # Get alerts (example - replace with actual data)
    alerts = [
        {
            'title': 'New Assessment Submitted',
            'time': '1 hour ago',
            'details': 'Michael Brown has completed the anxiety assessment.',
            'is_urgent': True
        },
        {
            'title': 'Meeting Request',
            'time': '3 hours ago',
            'details': 'Emily Chen has requested an appointment.',
            'is_urgent': False
        },
        {
            'title': 'Follow-up Required',
            'time': 'Yesterday',
            'details': 'Follow up with David Wilson regarding last session.',
            'is_urgent': False
        }
    ]
    
    return render_template('guidance/dashboard.html', 
                         stats=stats, 
                         today_schedule=today_schedule,
                         alerts=alerts)

# Add more routes for guidance counselor functionality
@guidance_bp.route('/students')
@login_required
@guidance_required
def students():
    """View all students."""
    # TODO: Implement student listing
    return render_template('guidance/students.html')

@guidance_bp.route('/appointments')
@login_required
@guidance_required
def appointments():
    """View all appointments."""
    # TODO: Implement appointment listing
    return render_template('guidance/appointments.html')

@guidance_bp.route('/assessments')
@login_required
@guidance_required
def assessments():
    """View all assessments."""
    # TODO: Implement assessment listing
    return render_template('guidance/assessments.html')

@guidance_bp.route('/resources')
@login_required
@guidance_required
def resources():
    """View resources."""
    # TODO: Implement resources listing
    return render_template('guidance/resources.html')

@guidance_bp.route('/profile')
@login_required
@guidance_required
def profile():
    """View and edit profile."""
    # TODO: Implement profile view/edit
    return render_template('guidance/profile.html')

# Add more routes as needed
