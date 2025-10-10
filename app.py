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

# Now import the accounts repository service
from services.accounts_reposervice import account_repo_service
from services.auth_service import auth_service

# Import models
from models.accounts import AccountsModel, AccountsModelDto
from services.auth_service import auth_service
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

def parse_iso_datetime(value):
    print(f"entry point parse_iso_datetime value: {value}")
    if isinstance(value, str):
        try:
            # Try parsing ISO format string to datetime
            # Handles formats like '2025-10-02T13:00:44.41363+00:00' and '2025-10-02T13:00:44.41363+0000'
            if value.endswith('+00:00'):
                value = value[:-6] + '+00:00'
            elif value.endswith('+0000'):
                value = value[:-5] + '+00:00'
            return datetime.fromisoformat(value)
        except Exception as e:
            print(f"parse_iso_datetime error: {e}, value: {value}")
            return None
    return value

app.jinja_env.filters['parse_iso_datetime'] = parse_iso_datetime

def datetimeformat(value, format='%m/%d/%Y %I:%M %p'):
    if value is None:
        return ''
    # If value is a string, try to parse to datetime
    if isinstance(value, str):
        try:
            value = datetime.fromisoformat(value.replace('+00:00', '+0000'))
        except Exception as e:
            print(f"datetimeformat parse error: {e}, value: {value}")
            return value
    return value.strftime(format)

app.jinja_env.filters['datetimeformat'] = datetimeformat

# Register blueprints
def register_blueprints(app):
    # Import blueprints here to avoid circular imports
    from routes.admin_routes import admin_bp
    from routes.guidance_routes import guidance_bp
    from routes.accounts_routes import accounts_bp
    from routes.content_routes import content_bp
    
    # Register blueprints with URL prefixes
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(guidance_bp, url_prefix='/guidance')
    app.register_blueprint(accounts_bp, url_prefix='/accounts')
    app.register_blueprint(content_bp, url_prefix='/content')
    
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
        print("[DEBUG] ... create_default_admin ...")
        
        # Always run this in development, or if explicitly enabled in production
        if app.config.get('FLASK_ENV') != 'development' and not app.config.get('CREATE_DEFAULT_ADMIN', False):
            print("[INFO] Skipping default admin creation - not in development mode")
            return
            
        from werkzeug.security import generate_password_hash
        from services.database_service import db_service
        from models import Admin
        from models.accounts import AccountsModel
        
        admin_email = 'admin123@gmail.com'  # Change this to your desired admin email
        admin_password = 'admin123'  # Change this to a secure password in production
        
        # Get Supabase client with service role to bypass RLS if needed
        supabase = db_service.get_supabase_client(use_service_role=True)
        
        if not supabase:
            print("[ERROR] Failed to initialize Supabase client")
            return False
        
        # Check if admin already exists
        try:
            print("[DEBUG] Checking if admin user exists...")
            response = supabase.table('user_accounts') \
                .select('*') \
                .eq('email', admin_email) \
                .eq('role', 'admin') \
                .execute()
            
            existing_admins = response.data if hasattr(response, 'data') else []
            
            if not existing_admins:
                print(f"[DEBUG] Attempting to create default admin: {admin_email}")
                print("[INFO] Creating default admin user...")
                
                admin_data = AccountsModel(
                    first_name='System',
                    last_name='Admin',
                    middle_name='',
                    role='admin',
                    email=admin_email,
                    password=admin_password,
                    is_verified=True
                )
                
                # Insert into admin_users table
                print("[DEBUG] Inserting admin user into database...")
                result = account_repo_service.create_account(admin_data)
                
                if(result is None):
                    print(f"[ERROR] Failed to create default admin user: {admin_email}")
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
    print(f"\n[DEBUG] ====== load_user called ======")
    print(f"[DEBUG] Provided User Id:{user_id} ")
    print(f"[DEBUG] Current session: {dict(session)}")
    
    try:    
        if not user_id:
            print("[DEBUG] Empty user_id provided")
            return None
        
        result = account_repo_service.get_account_by_user_id(user_id)
        result_data = result.data[0] if result and result.data else None
        if result_data and len(result_data) > 0:
          user_obj = User.to_user_dto_obj(result_data)
          return user_obj
        
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
        if current_user.role != 'client':
            return redirect(url_for('admin.dashboard'))
        return redirect(url_for('dashboard'))
    return render_template('auth/login_selector.html')

@app.route('/user/login', methods=['GET'])
def user_login():
    """Render the user login page."""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    form = LoginForm()
    return render_template('auth/login.html', form=form)

@app.route('/user/login', methods=['POST'])
@login_limiter
def handle_user_login():
    """Handle user login form submission."""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        return auth_service.process_login(form, is_admin=False)
    return render_template('auth/login.html', form=form)

   
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
    
    print("[DEBUG] Rendering registration form method:", request.method)

    if request.method == 'POST':
        print("[DEBUG] Form submitted with data before validate:", form.data)
        if form.validate_on_submit():
            print(f"[DEBUG] Form submitted with data after validate: {form.data}")
            
            try:
                validate_email = form.validate_email(form.email)
                if validate_email:
                    flash('This email is already registered. Please log in instead.', 'info')
                    return render_template('register.html', form=form)           
                
                # Validate password and confirm_password match
                password = form.password.data
                confirm_password = form.confirm_password.data
                if password != confirm_password:
                    flash('Password and confirm password do not match.', 'danger')
                    return render_template('register.html', form=form)
  
                # Prepare user data with all form fields
                print(f"[DEBUG] Prepare user data with all form fields")
                user_data = AccountsModel(
                    id = None,  # ID will be set by the database
                    first_name = form.first_name.data.strip() if form.first_name.data else None,
                    middle_name = None,
                    last_name = form.last_name.data.strip() if form.last_name.data else None,
                    role = 'client',
                    email = form.email.data.lower().strip(),
                    password = password,  # This will be hashed in create_user
                    is_active = True,
                    image = None
                )

                print(f"[DEBUG] Creating new user for {user_data}")

                # Create user in database
                try:
                    user_id = account_repo_service.create_account(user_data)
                    print(f"[DEBUG] Creating new user response {user_id}")
                    if not user_id:
                        flash('Failed to create user. Please try again.', 'danger')
                        return render_template('register.html', form=form)

                    print(f"[DEBUG] User created successfully with ID: {user_id}")

                    # Don't log the user in automatically
                    print(f"[DEBUG] Registration successful for user {user_id}, redirecting to login")

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
        else:
          # Form validation failed
          print(f"[DEBUG] Form validation failed with errors: {form.errors}")
         
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
        result = (supabase_db.supabase.table('clients')
                  .update({'profile_image': avatar_url})
                  .eq('id', current_user.id)
                  .execute())
        
        if not result.data:
          return jsonify({'error': 'Failed to update avatar'}), 500
            
        return jsonify({'success': True})
    except Exception as e:
        print(f"Error updating avatar: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/dashboard')
@login_required
def dashboard():
    print(f"[DEBUG] Rendering dashboard for user: {current_user}")
    # Get user data to pass to the template
    user_data = {
        'username': current_user.username,
        'email': current_user.email,
        'first_name': current_user.first_name,
        'last_name': current_user.last_name,
        'avatar_url': current_user.image or url_for('static', filename='img/avatars/user.png')
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
                url = url_for('index', _external=True)
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
