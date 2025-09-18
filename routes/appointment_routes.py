from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user, login_required
from datetime import datetime, timedelta
from ..models.appointment import Appointment
from ..models.client import Client
from ..models.guidance_counselor import GuidanceCounselor
from ..models.psychologist import Psychologist
from ..models.admin_user import AdminUser
from .. import db

# Create blueprint
appointment_bp = Blueprint('appointment', __name__, url_prefix='/staff/appointments')


@appointment_bp.route('/')
@login_required
def manage_appointments():
    # Get all appointments for the current staff member
    appointments = Appointment.query.filter_by(staff_id=current_user.id).all()
    return render_template('admin/staff/appointments.html', 
                         appointments=appointments,
                         active_page='appointments')

@appointment_bp.route('/new', methods=['GET', 'POST'])
@login_required
def new_appointment():
    if request.method == 'POST':
        try:
            # Get form data
            title = request.form.get('title')
            description = request.form.get('description', '')
            start_time = datetime.fromisoformat(request.form.get('start_time'))
            end_time = datetime.fromisoformat(request.form.get('end_time'))
            professional_type = request.form.get('professional_type')
            professional_id = int(request.form.get('professional_id'))
            student_id = int(request.form.get('student_id'))
            
            # Create new appointment
            appointment = Appointment(
                title=title,
                description=description,
                start_time=start_time,
                end_time=end_time,
                professional_type=professional_type,
                professional_id=professional_id,
                student_id=student_id,
                staff_id=current_user.id,
                appointment_type=professional_type,
                status='scheduled'
            )
            
            db.session.add(appointment)
            db.session.commit()
            
            flash('Appointment scheduled successfully!', 'success')
            return jsonify({
                'status': 'success',
                'message': 'Appointment scheduled successfully!',
                'appointment': appointment.to_dict()
            })
            
        except Exception as e:
            db.session.rollback()
            return jsonify({
                'status': 'error',
                'message': f'Error scheduling appointment: {str(e)}'
            }), 400
    
    # GET request - show form
    students = Client.query.order_by(Client.first_name, Client.last_name).all()
    guidance_counselors = GuidanceCounselor.query.all()
    psychologists = Psychologist.query.all()
    
    return render_template('admin/staff/new_appointment.html',
                         students=students,
                         guidance_counselors=guidance_counselors,
                         psychologists=psychologists,
                         active_page='appointments')

@appointment_bp.route('/api/appointments/availability', methods=['GET'])
@login_required
def check_availability():
    try:
        professional_type = request.args.get('professional_type')
        professional_id = request.args.get('professional_id', type=int)
        start_time = datetime.fromisoformat(request.args.get('start_time'))
        end_time = datetime.fromisoformat(request.args.get('end_time'))
        
        # Check for overlapping appointments
        overlapping = Appointment.query.filter(
            Appointment.professional_type == professional_type,
            Appointment.professional_id == professional_id,
            ((Appointment.start_time < end_time) & (Appointment.end_time > start_time)),
            Appointment.status != 'cancelled'
        ).first()
        
        return jsonify({
            'available': overlapping is None,
            'message': 'This time slot is already booked. Please choose another time.' if overlapping else 'Time slot is available.'
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error checking availability: {str(e)}'
        }), 400

@appointment_bp.route('/api/appointments/<int:appointment_id>', methods=['PUT', 'DELETE'])
@login_required
def manage_appointment(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)
    
    if request.method == 'PUT':
        try:
            data = request.get_json()
            
            # Update appointment fields
            if 'status' in data:
                appointment.status = data['status']
            if 'title' in data:
                appointment.title = data['title']
            if 'description' in data:
                appointment.description = data['description']
            if 'start_time' in data:
                appointment.start_time = datetime.fromisoformat(data['start_time'])
            if 'end_time' in data:
                appointment.end_time = datetime.fromisoformat(data['end_time'])
            
            db.session.commit()
            
            return jsonify({
                'status': 'success',
                'message': 'Appointment updated successfully!',
                'appointment': appointment.to_dict()
            })
            
        except Exception as e:
            db.session.rollback()
            return jsonify({
                'status': 'error',
                'message': f'Error updating appointment: {str(e)}'
            }), 400
            
    elif request.method == 'DELETE':
        try:
            db.session.delete(appointment)
            db.session.commit()
            
            return jsonify({
                'status': 'success',
                'message': 'Appointment cancelled successfully!'
            })
            
        except Exception as e:
            db.session.rollback()
            return jsonify({
                'status': 'error',
                'message': f'Error cancelling appointment: {str(e)}'
            }), 400
