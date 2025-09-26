import sys
import os
import sys
import logging
import json
import jwt
import secrets
import bcrypt
from datetime import datetime, timedelta, timezone
from functools import wraps
from threading import Timer

# Add the project root to the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Third-party imports
from flask import (
    Flask, render_template, request, jsonify, session, g, flash, 
    redirect, url_for, current_app, abort, send_from_directory
)
from flask_login import (
    LoginManager, UserMixin, login_user, login_required, 
    logout_user, current_user
)
from flask_pymongo import PyMongo
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from dotenv import load_dotenv
from flask_wtf.csrf import CSRFProtect, generate_csrf
import socketio
from bson.objectid import ObjectId
from flask_mail import Mail, Message

# Initialize Flask app
app = Flask(__name__)

# Load environment variables
load_dotenv()

# Configure app
app.config.update(
    # Flask settings
    SECRET_KEY=os.getenv('FLASK_SECRET_KEY', 'dev-secret-key'),
    FLASK_ENV=os.getenv('FLASK_ENV', 'development'),
    FLASK_DEBUG=os.getenv('FLASK_DEBUG', 'true').lower() == 'true',
    
    # Database settings
    SQLALCHEMY_DATABASE_URI=os.getenv('DATABASE_URL', 'sqlite:///unicare.db'),
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
    
    # MongoDB settings
    MONGODB_URI=os.getenv('MONGODB_URI', 'mongodb://localhost:27017/unicare'),
    
    # Email settings
    MAIL_SERVER=os.getenv('MAIL_SERVER', 'smtp.gmail.com'),
    MAIL_PORT=int(os.getenv('MAIL_PORT', 587)),
    MAIL_USE_TLS=os.getenv('MAIL_USE_TLS', 'true').lower() == 'true',
    MAIL_USERNAME=os.getenv('MAIL_USERNAME'),
    MAIL_PASSWORD=os.getenv('MAIL_PASSWORD'),
    MAIL_DEFAULT_SENDER=os.getenv('MAIL_DEFAULT_SENDER', os.getenv('MAIL_USERNAME')),
    
    # Session settings
    SESSION_COOKIE_SECURE=False,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
    PERMANENT_SESSION_LIFETIME=3600  # 1 hour
)

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if app.config['FLASK_DEBUG'] else logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize extensions
db = SQLAlchemy()
mail = Mail()
csrf = CSRFProtect()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager = LoginManager(app)
login_manager.login_view = 'auth.login'  # Update this to your login route

# Initialize Socket.IO
sio = socketio.Server(cors_allowed_origins="*")
app.wsgi_app = socketio.WSGIApp(sio, app.wsgi_app)

# Import database service
try:
    from services.database_service import db_service
except ImportError as e:
    logging.error(f"Failed to import database service: {e}")
    raise

# Import forms after app creation to avoid circular imports
from app.forms import (
    ForgotPasswordForm, 
    ResetPasswordForm, 
    AdminLoginForm, 
    LoginForm, 
    AdminRegisterForm,
    CreateAdminForm,
    RegisterForm,
    BaseLoginForm
)

# Configure server settings for URL generation
app.config['SERVER_NAME'] = 'localhost:5000'  # Update with your domain in production
app.config['APPLICATION_ROOT'] = '/'
app.config['PREFERRED_URL_SCHEME'] = 'http'

# Initialize rate limiter
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'your-secret-key')

# Email configuration
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'true').lower() == 'true'
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER', os.getenv('MAIL_USERNAME'))

# Initialize Flask-Mail
mail = Mail(app)

class SensitiveDataFilter(logging.Filter):
    def filter(self, record):
        if hasattr(record, 'msg'):
            # Redact password hashes and sensitive data
            if isinstance(record.msg, str):
                record.msg = record.msg.replace('password_hash', '***REDACTED***')
                record.msg = record.msg.replace('password', '***REDACTED***')
                record.msg = record.msg.replace('Vminkook09', '***REDACTED***')
        return True

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
logger.addFilter(SensitiveDataFilter())

# Disable logging for sensitive routes
logging.getLogger('werkzeug').setLevel(logging.WARNING)

# Initialize CSRF Protection
csrf = CSRFProtect(app)

# Make CSRF token available in all templates
@app.context_processor
def inject_csrf_token():
    return dict(csrf_token=generate_csrf)

# Initialize Socket.IO
sio = socketio.Server(cors_allowed_origins="*")
app.wsgi_app = socketio.WSGIApp(sio, app.wsgi_app)

# Add headers to prevent caching of authenticated pages
@app.after_request
def add_header(response):
    if current_user.is_authenticated:
        # For authenticated pages, prevent caching
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '-1'
    return response

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost/unicare')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# MongoDB configuration (for existing functionality)
app.config['MONGO_URI'] = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/unicare')
mongo = PyMongo(app)

# Initialize token serializer
token_serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])

def generate_token(user_id, expires_in=3600):
    """Generate a JWT token for password reset.
    
    Args:
        user_id: The user ID to include in the token
        expires_in: Token expiration time in seconds (default: 1 hour)
        
    Returns:
        str: A signed token
    """
    try:
        payload = {
            'user_id': str(user_id),
            'exp': datetime.utcnow() + timedelta(seconds=expires_in)
        }
        return jwt.encode(
            payload,
            app.config['SECRET_KEY'],
            algorithm='HS256'
        )
    except Exception as e:
        print(f"Error generating token: {str(e)}")
        return None

def verify_token(token, max_age=3600):
    """Verify a JWT token and return the user ID if valid.
    
    Args:
        token: The token to verify
        max_age: Maximum token age in seconds (default: 1 hour)
        
    Returns:
        str: The user ID if token is valid, None otherwise
    """
    try:
        payload = jwt.decode(
            token,
            app.config['SECRET_KEY'],
            algorithms=['HS256'],
            options={'verify_exp': True}
        )
        return payload.get('user_id')
    except jwt.ExpiredSignatureError:
        return None
    except (jwt.InvalidTokenError, Exception) as e:
        print(f"Error verifying token: {str(e)}")
        return None

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login_selector'

from utils.filters import time_ago

# Import blueprints from their respective modules
from routes.admin_routes import admin_bp
# Import other blueprints as needed

# Register blueprints
def register_blueprints(app):
    # Import blueprints here to avoid circular imports
    from routes.admin_routes import admin_bp
    from routes.guidance_routes import guidance_bp
    
    # Register blueprints with URL prefixes
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(guidance_bp, url_prefix='/guidance')
    
    # Import and register other blueprints when they're available
    # from routes.auth import auth_bp
    # app.register_blueprint(auth_bp, url_prefix='/auth')
    
    # from routes.assessments import assessment_bp
    # app.register_blueprint(assessment_bp, url_prefix='/assessments')
    
    # Register custom filters
    app.jinja_env.filters['time_ago'] = time_ago

# Import admin service
from services.admin_service import create_admin_user, get_admin_user, update_admin_user, delete_admin_user, is_admin_user

def create_default_admin():
    """Create a default admin user if it doesn't exist."""
    try:
        # Always run this in development, or if explicitly enabled in production
        if app.config.get('FLASK_ENV') != 'development' and not app.config.get('CREATE_DEFAULT_ADMIN', False):
            print("[INFO] Skipping default admin creation - not in development mode")
            return
            
        from werkzeug.security import generate_password_hash
        from services.database_service import db_service
        from models import Admin
        
        admin_email = 'enjhaym1@gmail.com'  # Change this to your desired admin email
        admin_password = 'admin123'  # Change this to a secure password in production
        
        print(f"[DEBUG] Attempting to create default admin: {admin_email}")
        
        # Get Supabase client with service role to bypass RLS if needed
        supabase = db_service.get_supabase_client(use_service_role=True)
        
        if not supabase:
            print("[ERROR] Failed to initialize Supabase client")
            return False
        
        # Check if admin already exists
        try:
            print("[DEBUG] Checking if admin user exists...")
            response = supabase.table('admin_users') \
                .select('*') \
                .eq('email', admin_email) \
                .execute()
            
            existing_admins = response.data if hasattr(response, 'data') else []
            
            if not existing_admins:
                print("[INFO] Creating default admin user...")
                # Create admin user
                password_hash = generate_password_hash(admin_password)
                admin_data = {
                    'email': admin_email,
                    'password_hash': password_hash,
                    'full_name': 'Admin User',
                    'is_active': True,
                    'is_super_admin': True,
                    'failed_login_attempts': 0,
                    'created_at': datetime.utcnow().isoformat(),
                    'updated_at': datetime.utcnow().isoformat()
                }
                
                # Insert into admin_users table
                print("[DEBUG] Inserting admin user into database...")
                result = supabase.table('admin_users').insert(admin_data).execute()
                
                if hasattr(result, 'error') and result.error:
                    print(f"[ERROR] Failed to create default admin: {result.error}")
                    return False
                else:
                    print(f"[SUCCESS] Created default admin user: {admin_email}")
                    print("\n" + "="*50)
                    print(f"ADMIN CREDENTIALS (CHANGE THESE IN PRODUCTION!)")
                    print(f"Email: {admin_email}")
                    print(f"Password: {admin_password}")
                    print("="*50 + "\n")
                    return True
            else:
                print(f"[INFO] Admin user already exists: {admin_email}")
                return True
                
        except Exception as e:
            print(f"[ERROR] Database operation failed: {str(e)}")
            import traceback
            print(traceback.format_exc())
            return False
        
    except Exception as e:
        print(f"[ERROR] Error in create_default_admin: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return False

from models import User

@login_manager.user_loader
def load_user(user_id):
    """Load user by ID from the database.
    
    Args:
        user_id: The user ID to load, which could be a UUID, email, or prefixed ID (admin_/user_)
        
    Returns:
        User: The user object if found, None otherwise
    """
    from services.database_service import db_service
    
    try:
        print(f"\n[DEBUG] ====== load_user called ======")
        print(f"[DEBUG] Input user_id: {user_id} (type: {type(user_id)})")
        print(f"[DEBUG] Current session: {dict(session)}")
        
        if not user_id:
            print("[DEBUG] Empty user_id provided")
            return None
            
        supabase = db_service.get_supabase_client()
        
        # Check if the user_id has a prefix (admin_ or user_)
        has_prefix = isinstance(user_id, str) and ('admin_' in user_id or 'user_' in user_id)
        prefix = None
        clean_user_id = user_id
        
        if has_prefix:
            if 'admin_' in user_id:
                prefix = 'admin_'
                clean_user_id = user_id.replace('admin_', '', 1)
                print(f"[DEBUG] Detected admin prefix, clean ID: {clean_user_id}")
                
                # Try to get admin user
                try:
                    admin_result = supabase.table('admin_users').select('*').eq('id', clean_user_id).execute()
                    if admin_result.data and len(admin_result.data) > 0:
                        admin_data = admin_result.data[0]
                        print(f"[DEBUG] Found admin in admin_users table: {admin_data.get('email')}")
                        user_obj = User.from_dict(admin_data)
                        user_obj.is_admin = True
                        # Ensure the session reflects admin status
                        session['is_admin'] = True
                        return user_obj
                except Exception as e:
                    print(f"[DEBUG] Error querying admin_users table: {str(e)}")
                    
            elif 'user_' in user_id:
                prefix = 'user_'
                clean_user_id = user_id.replace('user_', '', 1)
                print(f"[DEBUG] Detected user prefix, clean ID: {clean_user_id}")
        
        # Check if we have an admin flag in the session
        if session.get('is_admin'):
            print("[DEBUG] Found is_admin flag in session, checking admin_users table")
            try:
                admin_result = supabase.table('admin_users').select('*').eq('id', clean_user_id).execute()
                if admin_result.data and len(admin_result.data) > 0:
                    admin_data = admin_result.data[0]
                    print(f"[DEBUG] Found admin in admin_users table (from session flag): {admin_data.get('email')}")
                    user_obj = User.from_dict(admin_data)
                    user_obj.is_admin = True
                    return user_obj
            except Exception as e:
                print(f"[DEBUG] Error querying admin_users table (from session flag): {str(e)}")
        
        # Try to get the user by ID from the clients table
        try:
            result = supabase.table('clients').select('*').eq('id', clean_user_id).execute()
            if result.data and len(result.data) > 0:
                user_data = result.data[0]
                print(f"[DEBUG] Found user in clients table by ID: {user_data.get('email')}")
                user_obj = User.from_dict(user_data)
                user_obj.is_admin = False
                return user_obj
        except Exception as e:
            print(f"[DEBUG] Error querying clients table by ID: {str(e)}")
            
        # If we still don't have a user, try by email
        try:
            result = supabase.table('clients').select('*').ilike('email', clean_user_id).execute()
            if result.data and len(result.data) > 0:
                user_data = result.data[0]
                print(f"[DEBUG] Found user in clients table by email: {user_data.get('email')}")
                user_obj = User.from_dict(user_data)
                user_obj.is_admin = False
                return user_obj
        except Exception as e:
            print(f"[DEBUG] Error querying clients table by email: {str(e)}")
            
        # If not found and we have a prefix, try the admin_users table
        if has_prefix and prefix == 'admin_':
            try:
                print(f"[DEBUG] Checking admin_users table for ID: {clean_user_id}")
                result = supabase.table('admin_users').select('*').eq('id', clean_user_id).execute()
                print(f"[DEBUG] Admin users table query result: {result.data}")
                if result.data and len(result.data) > 0:
                    user_data = result.data[0]
                    print(f"[DEBUG] Found admin user in admin_users table: {user_data.get('email')}")
                    user_obj = User.from_dict(user_data)
                    user_obj.is_admin = True
                    return user_obj
            except Exception as e:
                print(f"[ERROR] Error querying admin_users table: {str(e)}")
        
        # If still not found, try to get the user from Supabase Auth
        try:
            auth_client = db_service.get_supabase_client(use_service_role=True)
            auth_resp = auth_client.auth.admin.get_user_by_id(clean_user_id)
            
            if getattr(auth_resp, 'user', None):
                u = auth_resp.user
                print(f"[DEBUG] Found user in Supabase Auth: {u.email}")
                
                # Create user data from Auth response
                user_data = {
                    'id': u.id,
                    'email': u.email,
                    'username': (u.user_metadata or {}).get('username') or (u.email or '').split('@')[0],
                    'first_name': (u.user_metadata or {}).get('first_name'),
                    'last_name': (u.user_metadata or {}).get('last_name'),
                    'is_active': True,
                    'is_verified': getattr(u, 'email_confirmed_at', None) is not None,
                }
                
                # Create the user object
                user_obj = User.from_dict(user_data)
                user_obj.is_admin = False
                
                # Try to save this user to the public.users table for future lookups
                try:
                    profile_data = {
                        'id': u.id,
                        'email': u.email,
                        'username': user_data['username'],
                        'first_name': user_data.get('first_name'),
                        'last_name': user_data.get('last_name'),
                        'is_active': True,
                        'created_at': datetime.now(timezone.utc).isoformat()
                    }
                    # Remove None values
                    profile_data = {k: v for k, v in profile_data.items() if v is not None}
                    
                    # Upsert the user profile
                    supabase.table('clients').upsert(profile_data, on_conflict='id').execute()
                    print(f"[DEBUG] Synced Auth user to public.users table: {u.email}")
                except Exception as sync_error:
                    print(f"[WARNING] Could not sync Auth user to public.users: {str(sync_error)}")
                
                return user_obj
                
        except Exception as e:
            print(f"[ERROR] Error querying Supabase Auth: {str(e)}")
        
        # If we get here, no user was found
        print(f"[DEBUG] No user found with id: {user_id}")
        return None
            
    except Exception as e:
        print(f"[ERROR] Error in load_user: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

# Chatbot route (accessible to all)
@app.route('/chatbot')
def chatbot():
    return render_template('chatbot.html')

# Chatbot message handler (no API, rule-based)
from flask import jsonify
from chatbot_rules import get_bot_response

@app.route('/chatbot/message', methods=['POST'])
@csrf.exempt
@limiter.limit("10 per minute")
def chatbot_message():
    data = request.get_json()
    user_message = data.get('message', '')
    last_topic = data.get('last_topic')
    user_facts = data.get('user_facts', {})
    bot_reply, new_topic, updated_facts = get_bot_response(user_message, last_topic, user_facts)
    return jsonify({'reply': bot_reply, 'topic': new_topic, 'user_facts': updated_facts})


# Static page routes
@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/faq')
def faq():
    return render_template('faq.html')

@app.route('/privacy')
def privacy():
    return render_template('privacy.html')

@app.route('/terms')
def terms():
    return render_template('terms.html')

@app.route('/resources')
def resources():
    return render_template('resources.html')

@app.route('/cookies')
def cookies():
    return render_template('cookies.html')

def get_reset_token(email, expires_sec=3600):
    """Generate a password reset token"""
    serializer = URLSafeTimedSerializer(app.secret_key)
    return serializer.dumps(email, salt='password-reset-salt')

def verify_reset_token(token, max_age=3600):
    """Verify the password reset token"""
    serializer = URLSafeTimedSerializer(app.secret_key)
    try:
        email = serializer.loads(
            token,
            salt='password-reset-salt',
            max_age=max_age
        )
        return email
    except (SignatureExpired, BadSignature) as e:
        logger.error(f'Token verification failed: {str(e)}')
        return None

def send_reset_email(user_email, reset_url):
    """Send password reset email"""
    try:
        msg = Message(
            'Password Reset Request - UNICARE',
            recipients=[user_email]
        )
        
        msg.html = render_template(
            'email/reset_password_email.html',
            reset_url=reset_url,
            current_year=datetime.utcnow().year
        )
        
        mail.send(msg)
        logger.info(f'Password reset email sent to {user_email}')
        return True
    except Exception as e:
        logger.error(f'Error sending password reset email: {str(e)}')
        return False

@app.route('/forgot-password', methods=['GET', 'POST'])
@limiter.limit('10 per hour')
def forgot_password():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
        
    form = ForgotPasswordForm()
    
    if form.validate_on_submit():
        email = form.email.data.lower().strip()
        
        try:
            # Check if user exists using service role to bypass RLS
            user = db_service.get_user_by_email(email, use_service_role=True)
            
            if user:
                # Generate a password reset token (valid for 1 hour)
                reset_token = generate_token(user.id, expires_in=3600)
                
                # Save the token to the database
                db_service.update_user(user.id, {
                    'reset_password_token': reset_token,
                    'reset_password_sent_at': datetime.utcnow()
                }, use_service_role=True)
                
                # Send password reset email
                reset_url = url_for('reset_password', token=reset_token, _external=True)
                
                # Render email content
                html_content = render_template('email/reset_password_email.html', 
                                            user=user, 
                                            reset_url=reset_url)
                text_content = f"""
                Hello {user.first_name or 'there'},

                You requested to reset your password for your UNICARE account.
                Please click the link below to set a new password:

                {reset_url}

                If you didn't request this, please ignore this email and your password will remain unchanged.

                Best regards,
                The UNICARE Team
                """
                
                # Send the email
                send_email(
                    subject="Reset Your UNICARE Password",
                    recipients=[user.email],
                    text_body=text_content,
                    html_body=html_content
                )
            
            # Always show success message to prevent email enumeration
            flash('If an account exists with that email, you will receive a password reset link shortly.', 'info')
            return redirect(url_for('login'))
            
        except Exception as e:
            print(f"Error sending password reset email: {str(e)}")
            flash('An error occurred while processing your request. Please try again later.', 'danger')
    
    return render_template('forgot_password.html', title='Forgot Password', form=form)
        
    return render_template('forgot_password.html', form=form)

@app.route('/reset-password/<token>', methods=['GET', 'POST'])
@limiter.limit('10 per hour')
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = ResetPasswordForm()
    
    # Verify token
    try:
        user_id = verify_token(token)
        if not user_id:
            flash('The password reset link is invalid or has expired.', 'danger')
            return redirect(url_for('forgot_password'))
        
        # Get user with service role to bypass RLS
        user = db_service.get_user_by_id(user_id, use_service_role=True)
        if not user or not user.reset_password_token or user.reset_password_token != token:
            flash('The password reset link is invalid or has expired.', 'danger')
            return redirect(url_for('forgot_password'))
        
        # Check if token is expired (24 hours)
        if user.reset_password_sent_at and \
           (datetime.utcnow() - user.reset_password_sent_at).total_seconds() > 86400:
            flash('The password reset link has expired. Please request a new one.', 'danger')
            return redirect(url_for('forgot_password'))
        
        if form.validate_on_submit():
            # Update user's password
            user.set_password(form.password.data)
            
            # Clear reset token and update password
            db_service.update_user(user.id, {
                'password_hash': user.password_hash,
                'reset_password_token': None,
                'reset_password_sent_at': None,
                'last_password_change': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat()
            }, use_service_role=True)
            
            flash('Your password has been reset successfully. You can now log in with your new password.', 'success')
            return redirect(url_for('login'))
        
    except Exception as e:
        print(f"Error in reset_password: {str(e)}")
        flash('An error occurred while processing your request. Please try again.', 'danger')
        return redirect(url_for('forgot_password'))
    
    return render_template('reset_password.html', title='Reset Password', form=form, token=token)

@app.route('/')
def index():
    return render_template('index.html', is_guest=not current_user.is_authenticated)

# Games and Assessments Routes
@app.route('/games')
def games():
    return render_template('games.html', is_guest=not current_user.is_authenticated)

@app.route('/personality-test')
def personality_test():
    return render_template('personality_test.html', is_guest=not current_user.is_authenticated)

@app.route('/submit-personality-test', methods=['POST'])
@login_required
def submit_personality_test():
    try:
        # Check if the request is JSON or form data
        if request.is_json:
            data = request.get_json()
            answers = data.get('answers', [])
            results = data.get('results', {})
        else:
            # Handle form data
            answers = request.form.get('answers')
            results = request.form.get('results')
            if answers:
                answers = json.loads(answers)
            if results:
                results = json.loads(results)
        
        # If we have pre-calculated results, use them
        if results:
            scores = results
        else:
            # Otherwise, calculate scores from answers
            scores = {
                'openness': 0,
                'conscientiousness': 0,
                'extraversion': 0,
                'agreeableness': 0,
                'neuroticism': 0
            }
            
            # Process answers
            for answer in answers:
                if isinstance(answer, dict):
                    trait = answer.get('trait')
                    score = answer.get('answer', 3)  # Default to neutral if not provided
                    reversed = answer.get('reversed', False)
                    
                    # Adjust score if reversed (e.g., 1 becomes 5, 2 becomes 4, etc.)
                    if reversed:
                        score = 6 - score
                    
                    # Add to the corresponding trait score
                    if trait in scores:
                        scores[trait] += score
            
            # Calculate average scores (assuming 10 questions per trait)
            for trait in scores:
                scores[trait] = (scores[trait] / 10) * 20  # Convert to percentage (assuming 10 questions per trait)
        
        # Save results to database
        result = {
            'user_id': ObjectId(current_user.id),
            'test_type': 'big_five',
            'scores': scores,
            'date_taken': datetime.utcnow()
        }
        
        mongo.db.assessment_results.insert_one(result)
        
        # Return appropriate response based on request type
        if request.is_json:
            return jsonify({
                'success': True,
                'scores': scores
            })
        else:
            # For form submission, redirect to dashboard with success message
            flash('Your personality test results have been saved!', 'success')
            return redirect(url_for('dashboard'))
            
    except Exception as e:
        if request.is_json:
            return jsonify({
                'success': False,
                'message': str(e)
            }), 500
        else:
            flash('An error occurred while saving your results. Please try again.', 'error')
            return redirect(url_for('personality_test'))

@app.route('/breathing-exercise')
def breathing_exercise():
    return render_template('breathing_exercise.html')

@app.route('/api/mood-data')
@login_required
def mood_data():
    # In a real app, you would fetch this from your database
    # For now, we'll use localStorage data from the client side
    return jsonify({
        'message': 'Mood data should be fetched from the client side localStorage',
        'data': []
    })

@app.route('/gratitude-journal')
@login_required
def gratitude_journal():
    return render_template('gratitude_journal.html', now=datetime.utcnow())

@app.route('/mindfulness-bell')
def mindfulness_bell():
    return render_template('mindfulness_bell.html')

@app.route('/memory-match')
def memory_match():
    return render_template('memory_match.html', is_guest=not current_user.is_authenticated)

@app.route('/eq-test')
def eq_test():
    return render_template('eq_test.html', is_guest=not current_user.is_authenticated)

@app.route('/fidget-spinner')
def fidget_spinner():
    return render_template('fidget_spinner.html', is_guest=not current_user.is_authenticated)

@app.route('/bubble-wrap')
def bubble_wrap():
    return render_template('bubble_wrap.html', is_guest=not current_user.is_authenticated)

@app.route('/clicker')
def clicker():
    return render_template('clicker_game.html', is_guest=not current_user.is_authenticated)

# Import necessary modules after route definition to avoid circular imports
from datetime import datetime, timedelta, timezone
from functools import wraps
from flask import session, flash, redirect, url_for, render_template, request
from flask_login import login_user, current_user, login_required, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
import pytz
# Forms are already imported at the top of the file
from services.database_service import db_service

def login_limiter(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Skip rate limiting in development
        if app.config.get('ENV') == 'development':
            return f(*args, **kwargs)
            
        current_time = datetime.now(pytz.utc)
        
        # Initialize session variables if they don't exist
        if 'login_attempts' not in session:
            session['login_attempts'] = 0
            session['first_attempt'] = current_time.timestamp()
        
        # Reset attempts if more than 5 minutes have passed since first attempt
        time_since_first_attempt = current_time.timestamp() - session['first_attempt']
        if time_since_first_attempt > 300:  # 5 minutes in seconds
            session['login_attempts'] = 0
            session['first_attempt'] = current_time.timestamp()
        
        # Check if too many attempts (increased to 10 for development)
        max_attempts = 10  # Increased from 5 to 10
        if session.get('login_attempts', 0) >= max_attempts:
            time_left = int(300 - time_since_first_attempt)  # Time left in seconds
            minutes, seconds = divmod(time_left, 60)
            flash(f'Too many login attempts. Please try again in {minutes}m {seconds}s.', 'danger')
            return redirect(url_for('login_selector')), 429  # 429: Too Many Requests
        
        # Increment login attempts
        session['login_attempts'] = session.get('login_attempts', 0) + 1
        session.modified = True
        
        # Log the attempt
        print(f"[LOGIN] Login attempt {session['login_attempts']}/{max_attempts} from {request.remote_addr}")
        
        return f(*args, **kwargs)
    return decorated_function

@app.route('/clear-rate-limit', methods=['GET'])
def clear_rate_limit():
    """Clear rate limiting for the current session (development only)."""
    if 'login_attempts' in session:
        session.pop('login_attempts')
    if 'first_attempt' in session:
        session.pop('first_attempt')
    flash('Rate limit has been reset.', 'success')
    return redirect(url_for('login_selector'))

@app.route('/login', methods=['GET'])
def login_selector():
    """Render the login selector page."""
    if current_user.is_authenticated:
        if current_user.is_admin:
            return redirect(url_for('admin.dashboard'))
        return redirect(url_for('dashboard'))
    return render_template('auth/login_selector.html')

@app.route('/user/login', methods=['GET'])
def user_login():
    """Render the user login page."""
    if current_user.is_authenticated and not current_user.is_admin:
        return redirect(url_for('dashboard'))
    form = LoginForm()
    return render_template('auth/login.html', form=form)

@app.route('/user/login', methods=['POST'])
@login_limiter
def handle_user_login():
    """Handle user login form submission."""
    if current_user.is_authenticated and not current_user.is_admin:
        return redirect(url_for('dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        return process_login(form, is_admin=False)
    return render_template('auth/login.html', form=form)

@app.route('/admin/login', methods=['POST'])
@login_limiter
def handle_admin_login():
    """Handle admin login form submission."""
    print("\n[DEBUG] Admin login attempt started")
    if current_user.is_authenticated and current_user.is_admin:
        print("[DEBUG] Already logged in as admin, redirecting to admin dashboard")
        return redirect(url_for('admin.dashboard'))
    
    form = AdminLoginForm()
    print(f"[DEBUG] Form data: {form.data}")
    
    if form.validate_on_submit():
        print("[DEBUG] Form validation passed, processing login")
        return process_login(form, is_admin=True)
    else:
        print(f"[DEBUG] Form validation failed with errors: {form.errors}")
    
    return render_template('admin/login.html', form=form)

def process_login(form, is_admin=False):
    """Process login for both users and admins."""
    email = form.email.data.lower().strip()
    password = form.password.data
    remember_me = form.remember_me.data
    
    print(f"\n[LOGIN] {'Admin' if is_admin else 'User'} login attempt - Email: {email}")
    print(f"[DEBUG] is_admin flag: {is_admin}")
    print(f"[DEBUG] Remember me: {remember_me}")
    
    user = None
    user_type = None
    
    try:
        supabase = db_service.get_supabase_client()
        
        if is_admin:
            print(f"[DEBUG] Checking admin_users table for email: {email}")
            try:
                # First try to find admin by email (case-insensitive)
                result = supabase.table('admin_users') \
                    .select('*') \
                    .ilike('email', email) \
                    .execute()
                
                print(f"[DEBUG] Admin query result: {result}")
                print(f"[DEBUG] Raw data: {result.data}")
                print(f"[DEBUG] Data length: {len(result.data) if result.data else 0}")
                
                # If no results, try direct match in case ilike isn't supported
                if not result.data or len(result.data) == 0:
                    print("[DEBUG] No results with ilike, trying direct match")
                    result = supabase.table('admin_users') \
                        .select('*') \
                        .eq('email', email) \
                        .execute()
                    print(f"[DEBUG] Direct match result: {result}")
                    print(f"[DEBUG] Raw direct match data: {result.data}")
                
                if not result.data or len(result.data) == 0:
                    print(f"[DEBUG] No admin user found with email: {email}")
                    flash('Invalid email or password.', 'error')
                    return render_template('admin/login.html', form=form)
                    
                user = result.data[0]
                print(f"[DEBUG] Found admin user: {user}")
                
                # Check if admin is active
                is_active = user.get('is_active', True)
                if isinstance(is_active, str):
                    is_active = is_active.lower() == 'true' or is_active == '1'
                
                if not is_active:
                    print(f"[LOGIN] Admin account is not active: {email}")
                    flash('This admin account is not active. Please contact support.', 'error')
                    return render_template('admin/login.html', form=form)
                
                # Check for too many failed login attempts
                failed_attempts = user.get('failed_login_attempts', 0)
                if failed_attempts >= 5:  # Lock account after 5 failed attempts
                    print(f"[LOGIN] Account locked due to too many failed attempts: {email}")
                    flash('This account is temporarily locked. Please try again later or contact support.', 'error')
                    return render_template('admin/login.html', form=form)
                
                # Verify the password - handle multiple hashing formats
                from werkzeug.security import check_password_hash
                from passlib.hash import pbkdf2_sha256, scrypt
                
                password_hash = user.get('password_hash', '')
                is_password_valid = False
                
                print(f"[DEBUG] Verifying password for email: {email}")
                print(f"[DEBUG] Stored hash: {password_hash}")
                
                # Check password hash format and verify accordingly
                if password_hash.startswith('$scrypt$'):
                    # scrypt format (e.g., from Supabase Auth)
                    try:
                        print("[DEBUG] Using scrypt verification")
                        is_password_valid = scrypt.verify(password, password_hash)
                    except Exception as e:
                        print(f"[ERROR] scrypt verification failed: {str(e)}")
                        is_password_valid = False
                elif password_hash.startswith('$pbkdf2-sha256$'):
                    # passlib pbkdf2_sha256 format
                    print("[DEBUG] Using pbkdf2_sha256 verification")
                    is_password_valid = pbkdf2_sha256.verify(password, password_hash)
                else:
                    # werkzeug format
                    print("[DEBUG] Using werkzeug check_password_hash")
                    is_password_valid = check_password_hash(password_hash, password)
                
                print(f"[DEBUG] Password verification result: {is_password_valid}")
                
                if not is_password_valid:
                    # Update failed login attempts
                    supabase.table('admin_users') \
                        .update({'failed_login_attempts': failed_attempts + 1}) \
                        .eq('email', email) \
                        .execute()
                    
                    remaining_attempts = 5 - (failed_attempts + 1)
                    if remaining_attempts > 0:
                        flash(f'Invalid email or password. {remaining_attempts} attempts remaining.', 'error')
                    else:
                        flash('Account locked due to too many failed attempts. Please contact support.', 'error')
                    
                    print(f"[LOGIN] Invalid password for admin: {email}")
                    return render_template('admin/login.html', form=form)
                
                # Reset failed login attempts on successful login
                supabase.table('admin_users') \
                    .update({
                        'failed_login_attempts': 0,
                        'last_login_at': 'now()'
                    }) \
                    .eq('email', email) \
                    .execute()
                
                user_type = 'admin'
                print(f"[LOGIN] Successfully authenticated admin user: {user.get('email')}")
                
                # If we reach here, login was successful
                # The rest of the code is now properly handled in the main try block
                user_type = 'admin'
                print(f"[LOGIN] Found and authenticated admin user: {user.get('email')}")
                print(f"[DEBUG] Admin user data: {user}")
                
            except Exception as e:
                print(f"[ERROR] Error during admin login: {str(e)}")
                import traceback
                traceback.print_exc()
                flash('An error occurred while trying to log in. Please try again.', 'error')
                return render_template('admin/login.html', form=form)
        else:
            # Authenticate regular users via Supabase Auth
            try:
                auth_client = db_service.get_supabase_client(use_service_role=True)
                auth_resp = auth_client.auth.sign_in_with_password({
                    'email': email,
                    'password': password
                })

                # Successful auth returns a session and user
                if getattr(auth_resp, 'user', None):
                    auth_user = auth_resp.user
                    user = {
                        'id': auth_user.id,
                        'email': auth_user.email,
                        'username': (auth_user.user_metadata or {}).get('username', (auth_user.email or '').split('@')[0]),
                        'first_name': (auth_user.user_metadata or {}).get('first_name'),
                        'last_name': (auth_user.user_metadata or {}).get('last_name'),
                        'is_active': True,
                        'is_verified': getattr(auth_user, 'email_confirmed_at', None) is not None,
                    }
                    user_type = 'user'
                    print(f"[LOGIN] Authenticated regular user via Supabase Auth: {user.get('email')}")
                else:
                    print(f"[LOGIN] No user returned from Supabase Auth for: {email}")
            except Exception as e:
                print(f"[ERROR] Supabase Auth sign-in failed: {str(e)}")
        
        # Check if user exists and is active
        if not user:
            print(f"[LOGIN] No user found for email: {email}")
            flash('Invalid email or password', 'danger')
            return redirect(url_for('admin.admin_login' if is_admin else 'user_login'))
            
        # For admin users, check if account is active
        if user_type == 'admin' and not user.get('is_active', True):
            print(f"[LOGIN] Admin account is not active: {email}")
            flash('This admin account is not active. Please contact support.', 'error')
            return redirect(url_for('admin.admin_login'))
        
        # Check if account is locked (for regular users)
        if user_type == 'user' and user.get('is_locked', False):
            lockout_time = user.get('lockout_until')
            if lockout_time and datetime.fromisoformat(lockout_time) > datetime.utcnow():
                print(f"[LOGIN] Account locked for email: {email}")
                flash('This account is temporarily locked. Please try again later or reset your password.', 'danger')
                return redirect(url_for('user_login'))
            else:
                # Reset lockout if time has passed
                supabase.table('clients') \
                    .update({
                        'is_locked': False,
                        'failed_login_attempts': 0,
                        'lockout_until': None
                    }) \
                    .eq('id', user['id']) \
                    .execute()
        
        # Password verification:
        # - Admins: verify locally against stored hash in admin_users
        # - Regular users: already verified by Supabase Auth above, so skip
        if user_type == 'admin':
            stored_password = user.get('password_hash') or user.get('password')
            if not stored_password:
                flash('Invalid email or password', 'danger')
                return redirect(url_for('admin.admin_login'))
            from werkzeug.security import check_password_hash as _check_hash
            if not _check_hash(stored_password, password):
                flash('Invalid email or password', 'danger')
                return redirect(url_for('admin.admin_login'))
        
        # Determine user type and admin status
        is_admin = (user_type == 'admin')
        
        # Get the user's email and username
        user_email = user.get('email', '')
        username = user.get('username', user_email.split('@')[0] if user_email else 'user')
        
        # Create the user object with admin status
        
        # Get the user ID and ensure it's a string
        user_id = str(user.get('id') or user.get('_id', ''))
        
        # For admin users, ensure we use the prefixed ID
        if user_type == 'admin' and not user_id.startswith('admin_'):
            user_id = f"admin_{user_id}"
        # For regular users, ensure we use a consistent ID format
        elif user_type == 'user' and not user_id.startswith('user_') and user_id:
            user_id = f"user_{user_id}"
        
        # Create a user object with the appropriate attributes
        print(f"[DEBUG] Creating User object with ID: {user_id}")
        user_obj = User(
            id=user_id,  # Use the possibly prefixed ID
            email=user['email'],
            username=user.get('username', user['email'].split('@')[0]),
            is_admin=(user_type == 'admin'),
            is_active=True
        )
        print(f"[DEBUG] User object created - ID: {user_obj.id}, get_id(): {user_obj.get_id()}")
        
        # Set additional attributes
        for attr in ['first_name', 'last_name', 'profile_image', 'is_super_admin']:
            if attr in user:
                setattr(user_obj, attr, user[attr])
        
        # Log the user in
        print(f"[DEBUG] About to call login_user with user_obj.id: {user_obj.id}")
        print(f"[DEBUG] User object get_id() returns: {user_obj.get_id()}")
        login_user(user_obj, remember=remember_me)
        
        # Update last login time
        try:
            if user_type == 'admin':
                supabase.table('admin_users') \
                    .update({'last_login': datetime.utcnow().isoformat()}) \
                    .eq('id', user['id']) \
                    .execute()
            else:
                # For regular users, update last login and reset failed attempts
                update_data = {'last_login': datetime.utcnow().isoformat()}
                if user.get('failed_login_attempts', 0) > 0:
                    update_data.update({
                        'failed_login_attempts': 0,
                        'is_locked': False,
                        'lockout_until': None
                    })
                supabase.table('clients') \
                    .update(update_data) \
                    .eq('id', user['id']) \
                    .execute()
                    
                # Also update the local user object with the latest data
                result = supabase.table('clients') \
                    .select('*') \
                    .eq('id', user['id']) \
                    .single() \
                    .execute()
                    
                if result and hasattr(result, 'data') and result.data:
                    user = result.data
        except Exception as e:
            print(f"[WARNING] Could not update user data: {str(e)}")
        
        print(f"[LOGIN] {'Admin' if is_admin else 'User'} logged in successfully: {user['email']}")
        
        # Set session variables
        session['user_id'] = user_id  # Use the prefixed ID for admin users
        session['is_admin'] = (user_type == 'admin')
        session.permanent = remember_me
        
        # Debug logging
        print(f"[DEBUG] User logged in - ID: {user_id}, Admin: {is_admin}, Email: {user['email']}")
        print(f"[DEBUG] Current user authenticated: {current_user.is_authenticated}")
        print(f"[DEBUG] Current user is admin: {current_user.is_admin if current_user.is_authenticated else 'Not authenticated'}")
        
        # Prepare success message
        flash(f'Welcome back, {user_obj.username}!', 'success')
        
        # For admin, always redirect to admin dashboard
        if is_admin:
            print("[DEBUG] Redirecting to admin dashboard")
            return redirect(url_for('admin.dashboard'))
            
        # For regular users, check for next parameter or go to dashboard
        next_page = request.args.get('next')
        if next_page and is_safe_url(next_page, request.host_url):
            print(f"[DEBUG] Redirecting to next page: {next_page}")
            return redirect(next_page)
            
        print("[DEBUG] Redirecting to user dashboard")
        return redirect(url_for('dashboard'))
        
    except Exception as e:
        print(f"[ERROR] Login error: {str(e)}")
        import traceback
        traceback.print_exc()
        flash('An error occurred during login. Please try again.', 'danger')
    
    return render_template('admin/login.html' if is_admin else 'auth/login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    """Handle user logout with security best practices."""
    # Log the user out
    user_email = current_user.email if current_user.is_authenticated else 'unknown user'
    logger.info(f'User {user_email} is logging out')
    
    logout_user()
    
    # Clear the session to prevent session fixation attacks
    session.clear()
    
    # Create response before clearing cookies
    response = redirect(url_for('index'))
    
    # Clear all cookies that might contain sensitive information
    for key in request.cookies:
        if key in ['session', 'remember_token', 'session_id']:
            response.delete_cookie(key)
    
    # Add security headers
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    
    # Flash a message to the user
    flash('You have been successfully logged out.', 'success')
    
    return response

# Forms are already imported at the top of the file

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    print("\n[DEBUG] Register route called")
    form = RegisterForm()
    
    if form.validate_on_submit():
        print(f"[DEBUG] Form submitted with data: {form.data}")
        
        try:
            print("[DEBUG] Checking if email already exists...")
            existing_user = db_service.get_user_by_email(form.email.data)
            if existing_user:
                flash('Email is already registered. Please use a different email or log in.', 'danger')
                print("[DEBUG] Registration failed - email already exists")
                return render_template('register.html', form=form)
            
            # Check if username is already taken
            existing_username = db_service.get_user(form.username.data)
            if existing_username:
                flash('Username is already taken. Please choose a different one.', 'danger')
                return render_template('register.html', form=form)
            
            print("[DEBUG] Creating new user...")
            # Prepare user data with all form fields
            user_data = {
                'username': form.username.data.strip(),
                'email': form.email.data.lower().strip(),
                'password': form.password.data,  # This will be hashed in create_user
                'first_name': form.first_name.data.strip() if form.first_name.data else None,
                'last_name': form.last_name.data.strip() if form.last_name.data else None,
                'gender': form.gender.data if hasattr(form, 'gender') and form.gender.data else None,
                'birthdate': form.birthdate.data.isoformat() if hasattr(form, 'birthdate') and form.birthdate.data else None,
                'created_at': datetime.now(timezone.utc).isoformat(),
                'is_active': True,
                'is_admin': False
            }
            
            print(f"[DEBUG] User data prepared: {user_data}")
            
            # Create user in database
            try:
                user = db_service.create_user(user_data)
                if not user:
                    flash('Failed to create user. Please try again.', 'danger')
                    return render_template('register.html', form=form)
                    
                print(f"[DEBUG] User created successfully with ID: {user.id}")
                
                # Don't log the user in automatically
                print(f"[DEBUG] Registration successful for user {user.id}, redirecting to login")
                
                flash('🎉 Registration successful! Please log in to continue.', 'success')
                return redirect(url_for('user_login'))
                
            except Exception as e:
                error_msg = str(e)
                print(f"[ERROR] Error creating user: {error_msg}")
                if '429' in error_msg or 'rate limit' in error_msg.lower():
                    flash('Too many signup attempts. Please wait a moment and try again.', 'warning')
                elif 'already registered' in error_msg.lower() or 'duplicate key' in error_msg.lower():
                    flash('This email or username is already registered. Please log in instead.', 'info')
                else:
                    flash('An error occurred during registration. Please try again.', 'danger')
                return render_template('register.html', form=form)
                
        except Exception as e:
            print(f"[ERROR] Registration error: {str(e)}")
            import traceback
            traceback.print_exc()
            flash('An unexpected error occurred during registration. Please try again.', 'danger')
    elif request.method == 'POST':
        # Form validation failed
        print(f"[DEBUG] Form validation failed with errors: {form.errors}")
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"{getattr(form, field).label.text}: {error}", 'danger')
    
    # For GET requests or if form validation fails
    return render_template('register.html', form=form)

@app.route('/update_avatar', methods=['POST'])
@login_required
def update_avatar():
    data = request.get_json()
    avatar_url = data.get('avatar_url')
    
    if not avatar_url:
        return jsonify({'error': 'No avatar URL provided'}), 400
    
    try:
        # Update user's profile image in Supabase
        result = supabase_db.supabase.table('clients')\
            .update({'profile_image': avatar_url})\
            .eq('id', current_user.id)\
            .execute()
        
        if not result.data:
            return jsonify({'error': 'Failed to update avatar'}), 500
            
        return jsonify({'success': True})
    except Exception as e:
        print(f"Error updating avatar: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/dashboard')
@login_required
def dashboard():
    # Get user data to pass to the template
    user_data = {
        'username': current_user.username,
        'email': current_user.email,
        'first_name': current_user.first_name,
        'last_name': current_user.last_name,
        'avatar_url': current_user.avatar_url or url_for('static', filename='img/avatars/default.png')
    }
    return render_template('dashboard.html', user=user_data)

@app.route('/api/assessment', methods=['POST'])
@login_required
def submit_assessment():
    data = request.json
    user_id = current_user.id

    # Get the current timestamp with timezone
    from datetime import timezone
    timestamp = datetime.now(timezone.utc).isoformat()
    
    # Prepare the assessment data
    assessment_data = {
        'user_id': user_id,
        'depression_score': data.get('depression_score'),
        'anxiety_score': data.get('anxiety_score'),
        'stress_score': data.get('stress_score'),
        'depression_level': data.get('depression_level'),
        'anxiety_level': data.get('anxiety_level'),
        'stress_level': data.get('stress_level'),
        'responses': data.get('responses', []),
        'created_at': timestamp,
        'updated_at': timestamp
    }
    
    try:
        # Get the database service instance
        from services.database_service import db_service
        
        # Get the Supabase client with service role
        supabase = db_service.get_supabase_client(use_service_role=True)
        
        # Insert assessment
        result = supabase.table('assessments').insert(assessment_data).execute()
        
        if hasattr(result, 'error') and result.error:
            raise Exception(f"Supabase error: {result.error.message}")
            
        # Update user's last assessment date and streak
        user_data = supabase.table('clients').select('last_assessment, streak').eq('id', user_id).single().execute()
        
        if hasattr(user_data, 'error') and user_data.error:
            raise Exception(f"Error fetching user data: {user_data.error.message}")
            
        user_data = user_data.data if hasattr(user_data, 'data') else {}
        current_streak = user_data.get('streak', 0)
        last_assessment_date = user_data.get('last_assessment')
        
        # Check if we should increment the streak
        if last_assessment_date:
            last_date = datetime.fromisoformat(last_assessment_date.replace('Z', '+00:00')).date()
            current_date = datetime.now(timezone.utc).date()
            
            if (current_date - last_date).days == 1:
                # Consecutive day
                current_streak += 1
            elif (current_date - last_date).days > 1:
                # Streak broken
                current_streak = 1
            # If same day, don't update the streak
        else:
            # First assessment
            current_streak = 1
        
        # Update user record
        update_result = supabase.table('clients').update({
            'last_assessment': timestamp,
            'streak': current_streak,
            'updated_at': timestamp
        }).eq('id', user_id).execute()
        
        if hasattr(update_result, 'error') and update_result.error:
            raise Exception(f"Error updating user: {update_result.error.message}")
        
        return jsonify({
            'success': True,
            'message': 'Assessment saved successfully',
            'streak': current_streak
        }), 200
        
    except Exception as e:
        print(f"Error saving assessment: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Failed to save assessment: {str(e)}'
        }), 500

@app.route('/api/user/stats')
@login_required
def get_user_stats():
    user = mongo.db.users.find_one({'_id': ObjectId(current_user.id)})
    if user:
        return jsonify({
            'streak': user.get('streak', 0),
            'points': user.get('points', 0),
            'badges': user.get('badges', [])
        })
    return jsonify({'error': 'User not found'}), 404

@sio.event
def connect(sid, environ):
    print('Client connected:', sid)

@sio.event
def disconnect(sid):
    print('Client disconnected:', sid)

@sio.event
def chat_message(sid, data):
    # Simple rule-based chatbot responses
    message = data.get('message', '').lower()
    
    if 'hi' in message or 'hello' in message:
        response = "Hi there! How can I help you today?"
    elif 'stress' in message or 'anxious' in message:
        response = "I understand things can be tough sometimes. Would you like to try some breathing exercises?"
    elif 'well' in message or 'good' in message:
        response = "That's great to hear! What's making you feel good today?"
    else:
        response = "I'm here to listen. What would you like to talk about?"
    
    sio.emit('chat_response', {'message': response})


# Admin routes are now handled by the admin Blueprint

@app.route('/clear-session')
def clear_session():
    """Clear the current session to fix login state issues."""
    from flask import session
    session.clear()
    return redirect(url_for('index'))

# Register blueprints before running the app
register_blueprints(app)

def print_startup_info():
    """Print startup information after the app is running."""
    with app.app_context():
        try:
            print("\n" + "="*50)
            print("Application is running!")
            print("="*50)
            print("\nAdmin Interface:")
            print(f"- Login URL: {url_for('admin.admin_login', _external=True)}")
            print("\n" + "="*50 + "\n")
        except Exception as e:
            print("\n[WARNING] Could not print startup URLs:", str(e))

# Import models to ensure they are registered with SQLAlchemy
from models.appointment import Appointment
from models.client import Client
from models.admin_user import AdminUser

if __name__ == '__main__':
    try:
        # Print initialization header
        print("\n" + "="*50)
        print("Starting application initialization...")
        print("="*50 + "\n")
        
        # Force create default admin in development
        if app.config.get('FLASK_ENV') == 'development':
            app.config['CREATE_DEFAULT_ADMIN'] = True
            
        # Create default admin user
        if create_default_admin():
            print("\n[SUCCESS] Application initialization completed successfully!")
        else:
            print("\n[WARNING] Application initialization completed with warnings")
        
        # Run the application
        from threading import Timer
        import webbrowser
        
        def open_browser():
            with app.app_context():
                url = url_for('admin.admin_login', _external=True)
                webbrowser.open(url)
        
        # Print startup info after a short delay to ensure app is running
        Timer(1, print_startup_info).start()
        
        # Only open browser in development mode
        if app.config.get('FLASK_ENV') == 'development' and not os.environ.get('WERKZEUG_RUN_MAIN'):
            Timer(2, open_browser).start()
            
    except Exception as e:
        print(f"\n[CRITICAL] Application initialization failed: {str(e)}")
        import traceback
        print(traceback.format_exc())
    
    # Run the application
    app.run(debug=app.config.get('FLASK_DEBUG', True))
