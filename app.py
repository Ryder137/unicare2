from flask import Flask, render_template, request, jsonify, session, g, flash, redirect, url_for, current_app
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_pymongo import PyMongo
from datetime import datetime, timedelta
import os
import json
from dotenv import load_dotenv
import bcrypt
from flask_wtf.csrf import CSRFProtect, generate_csrf
import socketio
from bson.objectid import ObjectId
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from flask_mail import Mail, Message
from forms import ForgotPasswordForm, ResetPasswordForm
from functools import wraps
import logging

def create_default_env():
    """Create a default .env file if it doesn't exist"""
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    if not os.path.exists(env_path):
        with open(env_path, 'w') as f:
            f.write("""# Flask Configuration
FLASK_SECRET_KEY=your-very-secret-key-here-make-it-strong

# Email Configuration (GMAIL)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password-here
MAIL_DEFAULT_SENDER=your-email@gmail.com
MAIL_DEBUG=false

# Database Configuration
MONGODB_URI=your-mongodb-connection-string
""")
        print("Created default .env file. Please update it with your configuration.")

# Create default .env if it doesn't exist
create_default_env()

# Now load the environment variables
load_dotenv()

app = Flask(__name__)
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

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize CSRF Protection
csrf = CSRFProtect(app)

# Make CSRF token available in all templates
@app.context_processor
def inject_csrf_token():
    return dict(csrf_token=generate_csrf)

# Initialize Socket.IO
sio = socketio.Server(cors_allowed_origins="*")
app.wsgi_app = socketio.WSGIApp(sio, app.wsgi_app)

# MongoDB configuration
app.config['MONGO_URI'] = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/unicare')
mongo = PyMongo(app)

# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

from models import User

@login_manager.user_loader
def load_user(user_id):
    # Fetch user from Supabase using UUID with service role for authentication
    from services.database_service import db_service
    try:
        print(f"[DEBUG] load_user called with user_id: {user_id}")
        user = db_service.get_user_by_id(user_id, use_service_role=True)
        
        if user:
            print(f"[DEBUG] Found user in database: {user.__dict__}")
            # Create a proper User object with all required fields
            user_obj = User(
                id=str(user.id),
                username=getattr(user, 'username', user.email.split('@')[0]),
                email=user.email,
                first_name=getattr(user, 'first_name', ''),
                last_name=getattr(user, 'last_name', ''),
                profile_image=getattr(user, 'profile_image', None),
                password=getattr(user, 'password', '')  # Hashed password
            )
            print(f"[DEBUG] Created user object: {user_obj.__dict__}")
            return user_obj
        else:
            print(f"[DEBUG] No user found with id: {user_id}")
            return None
            
    except Exception as e:
        print(f"[ERROR] Error in load_user: {str(e)}")
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
def chatbot_message():
    data = request.get_json()
    user_message = data.get('message', '')
    last_topic = data.get('last_topic')
    user_facts = data.get('user_facts', {})
    bot_reply, new_topic, updated_facts = get_bot_response(user_message, last_topic, user_facts)
    return jsonify({'reply': bot_reply, 'topic': new_topic, 'user_facts': updated_facts})

# Mood Tracker route
from flask import flash

@app.route('/mood_tracker', methods=['GET', 'POST'])
def mood_tracker():
    if request.method == 'POST':
        mood = request.form.get('mood')
        note = request.form.get('note')
        # TODO: Store mood/note in DB, for now just flash
        if mood:
            flash(f"Mood tracked: {mood.capitalize()}" + (f" | Note: {note}" if note else ""), 'success')
        else:
            flash("Please select a mood.", 'danger')
    return render_template('mood_tracker.html')

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
def forgot_password():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
        
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        email = form.email.data.lower()
        user = db_service.get_user_by_email(email)
        
        if user:
            # Generate token and send email
            token = get_reset_token(email)
            reset_url = url_for('reset_password', token=token, _external=True)
            
            if send_reset_email(email, reset_url):
                flash('If an account with that email exists, you will receive a password reset link shortly.', 'info')
            else:
                flash('Could not send reset email. Please try again later.', 'danger')
        else:
            # Don't reveal if the email exists for security reasons
            flash('If an account with that email exists, you will receive a password reset link shortly.', 'info')
            
        return redirect(url_for('login'))
        
    return render_template('forgot_password.html', form=form)

@app.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    # Verify token
    email = verify_reset_token(token)
    if not email:
        flash('The password reset link is invalid or has expired.', 'danger')
        return redirect(url_for('forgot_password'))
    
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user = db_service.get_user_by_email(email)
        if user:
            # Update password with service role client to bypass RLS
            try:
                hashed_password = bcrypt.hashpw(form.password.data.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                update_data = {'password': hashed_password}
                
                # Use service role client to bypass RLS
                if db_service.update_user(user.id, update_data, use_service_role=True):
                    flash('Your password has been updated! You can now log in with your new password.', 'success')
                    return redirect(url_for('login'))
                else:
                    flash('An error occurred while updating your password. Please try again.', 'danger')
            except Exception as e:
                logger.error(f'Error updating password: {str(e)}')
                flash('An unexpected error occurred. Please try again later.', 'danger')
        else:
            flash('User not found. Please try again.', 'danger')
    
    return render_template('reset_password.html', form=form, token=token)

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

@app.route('/gratitude-journal')
@login_required
def gratitude_journal():
    # Pass current date to the template
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
from forms import LoginForm
from services.database_service import db_service

def login_limiter(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        current_time = datetime.now(pytz.utc)
        
        if 'login_attempts' not in session:
            session['login_attempts'] = 0
            session['first_attempt'] = current_time.timestamp()
        
        # Reset attempts if more than 5 minutes have passed since first attempt
        if 'first_attempt' in session:
            time_since_first_attempt = current_time.timestamp() - session['first_attempt']
            if time_since_first_attempt > 300:  # 5 minutes in seconds
                session['login_attempts'] = 0
                session['first_attempt'] = current_time.timestamp()
        
        # Check if too many attempts
        if session.get('login_attempts', 0) >= 5:  # Max 5 attempts
            flash('Too many login attempts. Please try again later.', 'danger')
            return redirect(url_for('login'))
        
        return f(*args, **kwargs)
    return decorated_function

@app.route('/login', methods=['GET', 'POST'])
@login_limiter
def login():
    """Handle user login with rate limiting and account lockout."""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = LoginForm()
    
    if form.validate_on_submit():
        email = form.email.data.lower().strip()  # Normalize email
        password = form.password.data
        remember_me = form.remember_me.data
        
        try:
            # Get user from database using service role to bypass RLS
            user = db_service.get_user_by_email(email, use_service_role=True)
            
            # Check if user exists and is active
            if not user or not user.is_active:
                # Don't reveal if user exists or not for security
                session['login_attempts'] = session.get('login_attempts', 0) + 1
                flash('Invalid email or password', 'danger')
                return render_template('login.html', form=form)
            
            # Check if account is locked
            current_time = datetime.now(pytz.utc)
            if user.account_locked_until and user.account_locked_until > current_time:
                remaining = (user.account_locked_until - current_time).seconds // 60
                flash(f'Account is temporarily locked. Please try again in {remaining} minutes.', 'danger')
                return render_template('login.html', form=form)
            
            # Verify password
            if not user.check_password(password):
                # Increment failed login attempts
                db_service.increment_failed_login_attempts(user.id)
                
                # Get updated user data to check if account was just locked
                updated_user = db_service.get_user_by_id(user.id, use_service_role=True)
                if updated_user and updated_user.account_locked_until:
                    flash('Too many failed attempts. Account locked for 15 minutes.', 'danger')
                else:
                    flash('Invalid email or password', 'danger')
                
                session['login_attempts'] = session.get('login_attempts', 0) + 1
                return render_template('login.html', form=form)
            
            # If we get here, login is successful
            # Reset failed login attempts
            db_service.reset_failed_login_attempts(user.id)
            
            # Update last login time
            user.last_login = datetime.now(pytz.utc)
            db_service.update_user(user.id, {
                'last_login': user.last_login.isoformat()
            }, use_service_role=True)
            
            # Log the user in
            login_user(user, remember=remember_me)
            
            # Clear login attempts from session
            session.pop('login_attempts', None)
            session.pop('first_attempt', None)
            
            # Log successful login
            print(f"[AUTH] User {user.email} logged in successfully")
            
            # Redirect to next page or dashboard
            next_page = request.args.get('next')
            if not next_page or not next_page.startswith('/'):
                next_page = url_for('dashboard')
                
            return redirect(next_page)
            
        except Exception as e:
            print(f"[ERROR] Login error: {str(e)}")
            import traceback
            traceback.print_exc()
            flash('An unexpected error occurred. Please try again later.', 'danger')
    
    return render_template('login.html', form=form)

from forms import RegisterForm

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        password = form.password.data
        # Check if user exists
        existing_user = db_service.get_user(username)
        if existing_user:
            flash('Username already exists', 'danger')
            return render_template('register.html', form=form), 400
        # Hash password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        user_data = {
            'username': username,
            'email': email,
            'first_name': form.first_name.data or username,
            'last_name': form.last_name.data,
            'profile_image': form.profile_image.data,
            'password': hashed_password,
            'created_at': datetime.utcnow().isoformat(),
            'last_login': datetime.utcnow().isoformat(),
            'streak': 0,
            'badges': [],
            'points': 0
        }
        new_user = db_service.create_user(user_data)
        if not new_user:
            flash('Failed to register user. Please try again.', 'danger')
            return render_template('register.html', form=form), 500
        user_obj = User(user_id=str(new_user.id), username=username, email=email)
        login_user(user_obj)
        flash('Registration successful! Welcome to UNICARE.', 'success')
        return redirect(url_for('dashboard'))
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
        result = supabase_db.supabase.table('users')\
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
    # Fetch user from Supabase using UUID
    user = supabase_db.fetch_user_by_id(current_user.id)
    return render_template('dashboard.html', user=user)

@app.route('/api/assessment', methods=['POST'])
@login_required
def submit_assessment():
    data = request.json
    user_id = ObjectId(current_user.id)
    
    # Insert assessment
    assessment_id = mongo.db.assessments.insert_one({
        'user_id': str(user_id),
        'mood': data.get('mood'),
        'stress_level': data.get('stress_level'),
        'timestamp': datetime.utcnow()
    }).inserted_id
    
    # Update streak
    user = mongo.db.users.find_one({'_id': user_id})
    if user:
        last_assessment = mongo.db.assessments.find_one({
            'user_id': str(user_id),
            '_id': {'$ne': assessment_id}
        }).sort('timestamp', -1).limit(1)
        
        if last_assessment:
            last_date = last_assessment['timestamp'].date()
            current_date = datetime.utcnow().date()
            if (current_date - last_date).days <= 1:
                mongo.db.users.update_one(
                    {'_id': user_id},
                    {'$inc': {'streak': 1}}
                )
        else:
            mongo.db.users.update_one(
                {'_id': user_id},
                {'$set': {'streak': 1}}
            )
    
    # Award points and badges
    points = 10  # Base points for assessment
    if data.get('stress_level') <= 3:
        points += 5
    
    mongo.db.users.update_one(
        {'_id': user_id},
        {'$inc': {'points': points}}
    )
    
    # Check for new badges
    user = mongo.db.users.find_one({'_id': user_id})
    if user['points'] >= 100 and 'bronze' not in user['badges']:
        mongo.db.users.update_one(
            {'_id': user_id},
            {'$push': {'badges': 'bronze'}}
        )
    elif user['points'] >= 500 and 'silver' not in user['badges']:
        mongo.db.users.update_one(
            {'_id': user_id},
            {'$push': {'badges': 'silver'}}
        )
    elif user['points'] >= 1000 and 'gold' not in user['badges']:
        mongo.db.users.update_one(
            {'_id': user_id},
            {'$push': {'badges': 'gold'}}
        )
    
    return jsonify({'success': True})

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

if __name__ == '__main__':
    app.run(debug=True)
