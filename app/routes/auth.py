"""
Authentication routes for the application.
"""
from functools import wraps
from flask import Blueprint, render_template, redirect, url_for, flash, request, session, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from bson import ObjectId
from datetime import datetime, timedelta
import jwt

# Initialize blueprint
bp = Blueprint('auth', __name__)

# Lazy imports
def get_limiter():
    from app.extensions import limiter
    return limiter

def get_mail():
    from app.extensions import mail
    return mail

def get_db():
    from app.extensions import db
    return db

def login_limiter(f):
    """Decorator to limit login attempts."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        limiter = get_limiter()
        if limiter is None:
            return f(*args, **kwargs)
        return limiter.limit("5 per hour")(f)(*args, **kwargs)
    return decorated_function

@bp.route('/login', methods=['GET', 'POST'])
@login_limiter
def login_selector():
    """Render the login selector page."""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    # Lazy import forms
    from app.forms.auth_forms import LoginForm
    
    form = LoginForm()
    return render_template('auth/login_selector.html', form=form)

@bp.route('/login/user', methods=['GET', 'POST'])
@login_limiter
def user_login():
    """Handle user login."""
    # Lazy imports
    from app.forms.auth_forms import LoginForm
    from app.models.user import User
    from flask_login import login_user
    
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        
        if user is None or not user.check_password(form.password.data):
            flash('Invalid email or password', 'danger')
            return redirect(url_for('auth.user_login'))
        
        if not user.is_active:
            flash('Your account is not active. Please contact support.', 'danger')
            return redirect(url_for('auth.user_login'))
        
        login_user(user, remember=form.remember_me.data)
        
        # Update last login
        from app.extensions import db
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        next_page = request.args.get('next')
        if not next_page or not next_page.startswith('/'):
            next_page = url_for('main.dashboard')
        
        return redirect(next_page)
    
    return render_template('auth/login.html', form=form, user_type='user')

@bp.route('/login/admin', methods=['GET', 'POST'])
@login_limiter
def admin_login():
    """Handle admin login."""
    # Lazy imports
    from app.forms.auth_forms import LoginForm
    from app.models.user import User
    from flask_login import login_user
    
    if current_user.is_authenticated and current_user.is_admin:
        return redirect(url_for('admin.dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.get_by_email(form.email.data)
        if user and user.check_password(form.password.data) and user.is_admin:
            if not user.is_active:
                flash('Your admin account has been deactivated.', 'danger')
                return redirect(url_for('auth.admin_login'))
            
            login_user(user, remember=form.remember_me.data)
            user.update_last_login()
            
            next_page = request.args.get('next')
            flash('Admin login successful!', 'success')
            return redirect(next_page or url_for('admin.dashboard'))
        
        flash('Invalid admin credentials', 'danger')
    
    return render_template('auth/login.html', form=form, user_type='admin')

@bp.route('/register', methods=['GET', 'POST'])
def register():
    """Handle user registration."""
    # Lazy imports
    from app.forms.auth_forms import RegisterForm
    from app.models.user import User
    from app.extensions import db
    
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = RegisterForm()
    if form.validate_on_submit():
        # Check if user already exists
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash('Email already registered. Please use a different email.', 'danger')
            return redirect(url_for('auth.register'))
        
        # Create new user
        user = User(
            email=form.email.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            is_admin=False,
            is_active=True
        )
        user.set_password(form.password.data)
        
        # Add to database
        try:
            db.session.add(user)
            db.session.commit()
            flash('Registration successful! You can now log in.', 'success')
            return redirect(url_for('auth.user_login'))
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error creating user: {e}")
            flash('An error occurred during registration. Please try again.', 'danger')
    
    return render_template('auth/register.html', form=form)

@bp.route('/logout')
@login_required
def logout():
    """Handle user logout."""
    logout_user()
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index'))

def get_reset_token(user_id, expires_sec=1800):
    """Generate a password reset token."""
    return jwt.encode(
        {'user_id': str(user_id), 'exp': datetime.utcnow() + timedelta(seconds=expires_sec)},
        current_app.config['SECRET_KEY'],
        algorithm='HS256'
    )

def verify_reset_token(token):
    """Verify a password reset token."""
    try:
        user_id = jwt.decode(
            token,
            current_app.config['SECRET_KEY'],
            algorithms=['HS256']
        )['user_id']
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None
    
    return User.get_by_id(user_id)

def send_reset_email(user):
    """Send a password reset email to the user."""
    token = get_reset_token(user.id)
    reset_url = url_for('auth.reset_password', token=token, _external=True)
    
    msg = Message(
        'Password Reset Request',
        sender=current_app.config['MAIL_DEFAULT_SENDER'],
        recipients=[user.email]
    )
    
    msg.body = f'''To reset your password, visit the following link:
{reset_url}

If you did not make this request, simply ignore this email and no changes will be made.
'''
    
    mail.send(msg)

@bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """Handle forgot password request."""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        user = User.get_by_email(form.email.data)
        if user:
            send_reset_email(user)
        
        flash('If an account exists with that email, a password reset link has been sent.', 'info')
        return redirect(url_for('auth.user_login'))
    
    return render_template('auth/forgot_password.html', form=form)

@bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """Handle password reset."""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    user = verify_reset_token(token)
    if not user:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('auth.forgot_password'))
    
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        user.update_last_login()
        
        # Update password in database
        from ..extensions import mongo
        mongo.db.users.update_one(
            {'_id': ObjectId(user.id)},
            {'$set': {'password': user.password_hash}}
        )
        
        flash('Your password has been updated! You are now logged in.', 'success')
        login_user(user)
        return redirect(url_for('main.dashboard'))
    
    return render_template('auth/reset_password.html', form=form, token=token)

# Export the blueprint
bp = bp
