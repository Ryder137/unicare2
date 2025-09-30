from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for, abort, current_app
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from models import db, User, Appointment
from functools import wraps

# Create blueprint
appointment_bp = Blueprint('appointment', __name__)

def staff_required(f):
    """Decorator to ensure user is a staff member."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not hasattr(current_user, 'is_staff') or not current_user.is_staff:
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


@appointment_bp.route('/staff/appointments')
@login_required
@staff_required
def manage_appointments():
    """
    View all appointments for the current staff member with pagination and filtering.
    
    Query Parameters:
        page: Page number for pagination (default: 1)
        status: Filter by appointment status (scheduled, completed, cancelled)
        date_from: Filter appointments from this date (YYYY-MM-DD)
        date_to: Filter appointments up to this date (YYYY-MM-DD)
        
    Returns:
        Renders the staff appointments template with paginated and filtered
        list of appointments and available students.
    """
    try:
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        status_filter = request.args.get('status', '')
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        
        # Base query
        query = Appointment.query.filter_by(staff_id=current_user.id)
        
        # Apply filters
        if status_filter:
            query = query.filter(Appointment.status == status_filter)
            
        if date_from:
            try:
                from_date = datetime.strptime(date_from, '%Y-%m-%d')
                query = query.filter(Appointment.start_time >= from_date)
            except ValueError:
                pass  # Ignore invalid date format
                
        if date_to:
            try:
                to_date = datetime.strptime(date_to + ' 23:59:59', '%Y-%m-%d %H:%M:%S')
                query = query.filter(Appointment.start_time <= to_date)
            except ValueError:
                pass  # Ignore invalid date format
        
        # Pagination
        per_page = 10  # Items per page
        pagination = query.order_by(
            Appointment.start_time.desc()
        ).paginate(page=page, per_page=per_page, error_out=False)
        appointments = pagination.items
        
        
        # Get list of active students for the appointment form
        students = User.query.filter_by(
            is_student=True,
            is_active=True
        ).order_by(User.last_name, User.first_name).all()
        
        # Get available statuses for filter
        statuses = ['scheduled', 'completed', 'cancelled']
        
        # Get current filter values
        current_filters = {
            'status': status_filter,
            'date_from': date_from,
            'date_to': date_to
        }
        
        # Convert appointments to a format suitable for the template
        appointments_data = []
        for appt in appointments:
            appt_data = {
                'id': appt.id,
                'title': appt.title or 'Appointment',
                'start_time': appt.start_time.isoformat() if appt.start_time else None,
                'end_time': appt.end_time.isoformat() if appt.end_time else None,
                'status': appt.status or 'scheduled',
                'appointment_type': appt.appointment_type or '',
                'client': {
                    'id': appt.client.id,
                    'full_name': f"{appt.client.first_name} {appt.client.last_name}"
                } if appt.client else None
            }
            appointments_data.append(appt_data)
        
        return render_template('admin/staff/appointments.html',
                            appointments=appointments_data,
                            students=students,
                            active_page='appointments',
                            pagination=pagination,
                            statuses=statuses,
                            filters=current_filters)
                            
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        current_app.logger.error(f"Error in manage_appointments: {str(e)}\n{error_details}")
        flash('An error occurred while loading appointments. Please try again.', 'danger')
        return redirect(url_for('appointment.dashboard'))

@appointment_bp.route('/api/appointments', methods=['POST'])
@login_required
@staff_required
def create_appointment():
    """Create a new appointment (API endpoint)."""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['title', 'start_time', 'end_time', 'user_id', 'appointment_type', 'professional_type']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({
                    'success': False,
                    'message': f'Missing required field: {field}'
                }), 400
        
        # Parse datetime strings
        start_time = datetime.fromisoformat(data['start_time'].replace('Z', '+00:00'))
        end_time = datetime.fromisoformat(data['end_time'].replace('Z', '+00:00'))
        
        # Check if end time is after start time
        if end_time <= start_time:
            return jsonify({
                'success': False,
                'message': 'End time must be after start time.'
            }), 400
            
        # Check if student exists
        student = User.query.get(data['student_id'])
        if not student or not student.is_student:
            return jsonify({
                'success': False,
                'message': 'Invalid student selected.'
            }), 400
            
        # Check for scheduling conflicts
        conflict = Appointment.query.filter(
            Appointment.staff_id == current_user.id,
            Appointment.start_time < end_time,
            Appointment.end_time > start_time,
            Appointment.status != 'cancelled'
        ).first()
        
        if conflict:
            return jsonify({
                'success': False,
                'message': 'There is a scheduling conflict with an existing appointment.'
            }), 409
            
        # Create new appointment
        appointment = Appointment(
            title=data['title'],
            description=data.get('description', ''),
            start_time=start_time,
            end_time=end_time,
            #student_id=data['student_id'],
            staff_id=current_user.id,
            appointment_type=data['appointment_type'],
            professional_type=data['professional_type'],
            status='scheduled'
        )
        
        db.session.add(appointment)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Appointment created successfully!',
            'appointment_id': appointment.id
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error creating appointment: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'An error occurred: {str(e)}'
        }), 500

@appointment_bp.route('/api/appointments/<int:appointment_id>', methods=['GET', 'PUT', 'DELETE'])
@login_required
@staff_required
def manage_appointment(appointment_id):
    """Get, update, or delete a specific appointment."""
    appointment = Appointment.query.get_or_404(appointment_id)
    
    # Ensure the current user owns this appointment or is an admin
    if appointment.staff_id != current_user.id and not current_user.is_admin:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    if request.method == 'GET':
        # Return appointment details
        return jsonify({
            'success': True,
            'appointment': {
                'id': appointment.id,
                'title': appointment.title,
                'description': appointment.description,
                'start_time': appointment.start_time.isoformat(),
                'end_time': appointment.end_time.isoformat(),
                'status': appointment.status,
                'appointment_type': appointment.appointment_type,
                'professional_type': appointment.professional_type,
                'user_id': appointment.user_id,
                'created_at': appointment.created_at.isoformat(),
                'updated_at': appointment.updated_at.isoformat()
            }
        })
        
    elif request.method == 'PUT':
        # Update appointment
        try:
            data = request.get_json()
            
            # Update fields if provided
            if 'title' in data:
                appointment.title = data['title']
            if 'description' in data:
                appointment.description = data['description']
            if 'status' in data and data['status'] in ['scheduled', 'completed', 'cancelled']:
                appointment.status = data['status']
            
            # Handle rescheduling
            if 'start_time' in data and 'end_time' in data:
                new_start = datetime.fromisoformat(data['start_time'].replace('Z', '+00:00'))
                new_end = datetime.fromisoformat(data['end_time'].replace('Z', '+00:00'))
                
                # Check for conflicts (excluding the current appointment)
                conflict = Appointment.query.filter(
                    Appointment.id != appointment.id,
                    Appointment.staff_id == current_user.id,
                    Appointment.start_time < new_end,
                    Appointment.end_time > new_start,
                    Appointment.status != 'cancelled'
                ).first()
                
                if conflict:
                    return jsonify({
                        'success': False,
                        'message': 'There is a scheduling conflict with another appointment.'
                    }), 409
                
                appointment.start_time = new_start
                appointment.end_time = new_end
            
            appointment.updated_at = datetime.utcnow()
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Appointment updated successfully!'
            })
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error updating appointment: {str(e)}")
            return jsonify({
                'success': False,
                'message': f'An error occurred: {str(e)}'
            }), 500
            
    elif request.method == 'DELETE':
        # Delete appointment
        try:
            db.session.delete(appointment)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Appointment deleted successfully!'
            })
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error deleting appointment: {str(e)}")
            return jsonify({
                'success': False,
                'message': f'An error occurred: {str(e)}'
            }), 500

@appointment_bp.route('/api/appointments/check-availability', methods=['POST'])
@login_required
@staff_required
def check_availability():
    """Check if a time slot is available for scheduling."""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['start_time', 'end_time']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({
                    'success': False,
                    'message': f'Missing required field: {field}'
                }), 400
        
        # Parse datetime strings
        start_time = datetime.fromisoformat(data['start_time'].replace('Z', '+00:00'))
        end_time = datetime.fromisoformat(data['end_time'].replace('Z', '+00:00'))
        
        # Check for conflicts
        conflict_query = Appointment.query.filter(
            Appointment.staff_id == current_user.id,
            Appointment.start_time < end_time,
            Appointment.end_time > start_time,
            Appointment.status != 'cancelled'
        )
        
        # If checking a specific appointment (for updates), exclude it from the conflict check
        if 'appointment_id' in data and data['appointment_id']:
            conflict_query = conflict_query.filter(Appointment.id != data['appointment_id'])
        
        conflict = conflict_query.first()
        
        return jsonify({
            'success': True,
            'available': conflict is None,
            'conflict': {
                'id': conflict.id if conflict else None,
                'title': conflict.title if conflict else None,
                'start_time': conflict.start_time.isoformat() if conflict else None,
                'end_time': conflict.end_time.isoformat() if conflict else None
            } if conflict else None
        })
        
    except Exception as e:
        current_app.logger.error(f"Error checking availability: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'An error occurred while checking availability: {str(e)}'
        }), 500
    # Check if current user is the staff who created the appointment
    if appointment.staff_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    if request.method == 'GET':
        # Return appointment details
        return jsonify({
            'status': 'success',
            'appointment': appointment.to_dict()
        })
    
    elif request.method == 'PUT':
        data = request.get_json()
        
        # Update appointment fields
        for field in ['title', 'description', 'status', 'appointment_type']:
            if field in data:
                setattr(appointment, field, data[field])
                
        # Update times if provided
        if 'start_time' in data:
            appointment.start_time = datetime.fromisoformat(data['start_time'].replace('Z', '+00:00'))
        if 'end_time' in data:
            appointment.end_time = datetime.fromisoformat(data['end_time'].replace('Z', '+00:00'))
            
        db.session.commit()
        return jsonify({
            'status': 'success', 
            'message': 'Appointment updated successfully',
            'appointment': appointment.to_dict()
        })
        
    elif request.method == 'DELETE':
        try:
            # Soft delete by changing status
            appointment.status = 'cancelled'
            db.session.commit()
            return jsonify({
                'status': 'success', 
                'message': 'Appointment cancelled successfully',
                'appointment_id': appointment_id
            })
        except Exception as e:
            db.session.rollback()
            return jsonify({
                'status': 'error',
                'message': f'Error cancelling appointment: {str(e)}'
            }), 400
