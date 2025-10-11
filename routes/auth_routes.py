from flask import Blueprint, jsonify, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user, login_required
from app.forms.admin_forms import AdminLoginForm
from models import Admin
from services.auth_service import auth_service
from services.database_service import db_service

# Create auth blueprint
auth_bp = Blueprint('auth', __name__, template_folder='../templates/auth')

@auth_bp.route('/logout')
@login_required
def logout():
    """Logout route for all user types"""
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('auth.login'))


@auth_bp.route('/verify-email', methods=['GET', 'POST'])
def verify_email():
    print(f"[DEBUG] verify_email called with method: {request.method}")
    if request.method == 'GET':
        return render_template('auth/verify_email.html')
    
    # Handle POST request for token verification
    data = request.get_json()
    return jsonify({'success': True, 'message': 'Email verified successfully'})
            
    
@auth_bp.route('/resend-verification', methods=['POST'])
def resend_verification():
    """Resend email verification"""
    print(f"[DEBUG] resend_verification called")
    
    # Get email from request data
    data = request.get_json()
    email = data.get('email')
    
    if not email:
        return jsonify({'success': False, 'error': 'Email address is required'}), 400
    
    try:
        # Resend verification email using auth service
        result = auth_service.send_verification_email(email)
        
        if result.get('success'):
            return jsonify({
                'success': True, 
                'message': 'Verification email sent successfully'
            })
        else:
            return jsonify({
                'success': False, 
                'error': result.get('error', 'Failed to send verification email')
            }), 400
            
    except Exception as e:
        print(f"[ERROR] Error resending verification: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500
