from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user, login_required
from app.forms.admin_forms import AdminLoginForm
from models import Admin
from services.database_service import db_service

# Create auth blueprint
auth_bp = Blueprint('auth', __name__, template_folder='../templates/auth')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Unified login route for admin users"""
    if current_user.is_authenticated:
        return redirect(url_for('admin.dashboard'))
        
    form = AdminLoginForm()
    
    if form.validate_on_submit():
        user = db_service.authenticate_user(
            email=form.email.data,
            password=form.password.data,
            role='admin'
        )
        
        if user:
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('admin.dashboard'))
            
        flash('Invalid email or password', 'danger')
    
    return render_template('login.html', form=form, role='Admin')

@auth_bp.route('/logout')
@login_required
def logout():
    """Logout route for all user types"""
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('auth.login'))

def init_auth_routes(app):
    """Initialize authentication routes with the Flask app"""
    app.register_blueprint(auth_bp, url_prefix='/auth')
