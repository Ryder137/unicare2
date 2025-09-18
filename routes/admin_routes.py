import json
import logging
import os
import secrets
import string
import sys
import traceback
from datetime import datetime, timedelta
from functools import wraps

from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, current_app, abort, session
from flask_login import current_user, login_required, login_url, login_user, logout_user
from werkzeug.security import check_password_hash, generate_password_hash
from services import database_service as db_service

# Add the project root to the Python path first
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Now import the models and other project modules
from models import Admin, User, Psychologist, GuidanceCounselor
from services.database_service import db_service

# Import forms from the forms package
from forms.base_forms import (
    AdminRegisterForm, 
    AdminLoginForm,
    CreateAdminForm
)
from forms.psychologist_form import PsychologistForm
from forms.guidance_counselor_form import CreateGuidanceCounselorForm

# Import Supabase client
from supabase import create_client, Client
from config import SUPABASE_URL, SUPABASE_KEY, SUPABASE_SERVICE_ROLE_KEY

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create admin Blueprint with both template folder and URL prefix
admin_bp = Blueprint(
    'admin',
    __name__,
    template_folder='templates/admin',
    url_prefix='/admin'
)

# Initialize Supabase client
try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception as e:
    print(f"[ERROR] Failed to initialize Supabase client: {str(e)}")
    supabase = None

def process_login(form, is_admin=False):
    """Process login for admin users.
    
    Args:
        form: The login form containing email and password
        is_admin: Whether this is an admin login (for future use)
        
    Returns:
        Redirect response to dashboard or login page with error
    """
    logger.info("Processing admin login")
    
    if not form.validate_on_submit():
        logger.warning("Form validation failed: %s", form.errors)
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"{getattr(form, field).label.text}: {error}", 'error')
        return render_template('admin/login.html', form=form)
        
    try:
        email = form.email.data.lower().strip()
        password = form.password.data
        remember = form.remember_me.data
        
        logger.debug("Attempting login for email: %s", email)
        
        # Get admin user from database
        admin_data = db_service.get_admin_by_email(email)
        
        if not admin_data:
            logger.warning("Login failed - admin not found: %s", email)
            flash('Invalid email or password', 'error')
            return render_template('admin/login.html', form=form)
            
        # Verify password
        if not check_password_hash(admin_data.get('password_hash', ''), password):
            logger.warning("Login failed - invalid password for: %s", email)
            flash('Invalid email or password', 'error')
            return render_template('admin/login.html', form=form)
            
        # Check if account is active
        if not admin_data.get('is_active', True):
            logger.warning("Login failed - account inactive: %s", email)
            flash('This account has been deactivated', 'error')
            return render_template('admin/login.html', form=form)
            
        # Create user object
        admin_user = Admin(**admin_data)
        
        # Log the user in
        login_user(admin_user, remember=remember)
        
        # Update last login time
        db_service.update_admin_last_login(admin_user.id)
        
        # Set session variables
        session['user_id'] = admin_user.id
        session['is_admin'] = True
        session.permanent = True
        
        # Get the next URL from the form or query parameters
        next_url = request.form.get('next') or request.args.get('next')
        
        # Validate the next URL to prevent open redirects
        if next_url and not next_url.startswith('/'):
            next_url = None
            
        logger.info("Admin login successful: %s", email)
        
        # Redirect to dashboard or next URL
        return redirect(next_url or url_for('admin.dashboard'))
        
    except Exception as e:
        logger.error("Error during login: %s\n%s", str(e), traceback.format_exc())
        flash('An error occurred during login. Please try again.', 'error')
        return render_template('admin/login.html', form=form)

def admin_required(f):
    """Decorator to ensure the user is an admin."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        print("\n[DEBUG] ====== admin_required decorator called ======")
        print(f"[DEBUG] Request endpoint: {request.endpoint}")
        print(f"[DEBUG] Current user: {current_user}")
        print(f"[DEBUG] is_authenticated: {current_user.is_authenticated}")
        
        # Check if user is authenticated
        if not current_user.is_authenticated:
            print("[DEBUG] User not authenticated, redirecting to login")
            session['next'] = request.url if request.method == 'GET' else None
            return redirect(url_for('admin.admin_login', next=request.url))
            
        # Check if user is admin
        is_admin = getattr(current_user, 'is_admin', False)
        print(f"[DEBUG] User is_admin: {is_admin}")
        print(f"[DEBUG] User attributes: {dir(current_user)}")
        
        if not is_admin:
            print("[DEBUG] User is not an admin, redirecting to index")
            flash('You do not have permission to access this page.', 'error')
            return redirect(url_for('index'))
            
        print("[DEBUG] User is authenticated and is an admin, proceeding to route handler")
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/login', methods=['GET', 'POST'])
def admin_login():
    """Admin login page."""
    print("\n[DEBUG] ====== admin_login route called ======")
    print(f"[DEBUG] Method: {request.method}")
    print(f"[DEBUG] Current user: {current_user}")
    print(f"[DEBUG] Is authenticated: {current_user.is_authenticated if hasattr(current_user, 'is_authenticated') else 'N/A'}")
    
    # Clear any existing flash messages at the start
    clear_flash_messages()
    
    # If user is already logged in and is an admin, redirect to dashboard
    if current_user.is_authenticated and hasattr(current_user, 'is_admin') and current_user.is_admin:
        print("[DEBUG] User is already logged in as admin, redirecting to dashboard")
        return redirect(url_for('admin.dashboard'))
    
    form = AdminLoginForm()
    
    if form.validate_on_submit():
        print("\n[DEBUG] Form submitted, starting login process")
        print(f"[DEBUG] Email: {form.email.data}")
        
        # Process the login
        return process_login(form, is_admin=True)
        try:
            # Get user from database
            user = db_service.get_user_by_email(email)
            print(f"[DEBUG] User from DB: {user}")
            
            # Check if user exists and password is correct
            if not user or not user.check_password(password):
                print("[DEBUG] Invalid email or password")
                flash('Invalid email or password', 'danger')
                return redirect(url_for('admin.admin_login'))
            
            # Verify admin status
            if not getattr(user, 'is_admin', False):
                print("[DEBUG] User is not an admin")
                flash('You do not have admin privileges', 'danger')
                return redirect(url_for('admin.admin_login'))
            
            # Clear any existing session data
            session.clear()
            
            # Log the user in
            login_user(user, remember=remember_me)
            print(f"[DEBUG] User {user.email} logged in successfully")
            
            # Set session variables
            session.update({
                'user_id': str(user.id),
                'is_admin': True,
                'full_name': user.full_name or '',
                'email': user.email,
                '_fresh': True  # Mark session as fresh
            })
            
            # Set remember me cookie
            if remember_me:
                session.permanent = True
                current_app.permanent_session_lifetime = timedelta(days=30)
            
            # Ensure session is saved
            session.modified = True
            
            flash('Login successful!', 'success')
            
            # Get next URL safely
            next_url = request.args.get('next')
            if not next_url or not next_url.startswith('/'):
                next_url = url_for('admin.dashboard')
            
            print(f"[DEBUG] Redirecting to: {next_url}")
            return redirect(next_url)
            
        except Exception as e:
            print(f"[ERROR] Login error: {str(e)}")
            current_app.logger.error(f"Login error: {str(e)}", exc_info=True)
            session.clear()
            flash('An error occurred during login. Please try again.', 'danger')
    
    # For GET requests or failed form validation
    next_url = request.args.get('next')
    if next_url and not next_url.startswith('/'):
        next_url = None
    return render_template('admin/login.html', 
                         form=form, 
                         next=next_url)

@admin_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Handle admin registration with comprehensive error handling."""
    # Redirect to dashboard if already logged in
    if current_user.is_authenticated and getattr(current_user, 'is_admin', False):
        return redirect(url_for('admin.dashboard'))
    
    form = AdminRegisterForm()
    
    if form.validate_on_submit():
        try:
            # Check if email already exists
            existing_admin = db_service.get_admin_by_email(form.email.data)
            if existing_admin:
                flash('An admin with this email already exists. Please use a different email or log in instead.', 'error')
                return render_template('admin/register.html', form=form)
            
            # Prepare admin data with validation
            admin_data = {
                'full_name': form.full_name.data.strip() if form.full_name.data else None,
                'email': form.email.data.lower().strip(),
                'password': form.password.data,  # Will be hashed in the service
                'is_active': True,
                'is_super_admin': False  # Default to False for security
            }
            
            # Debug
            print("Attempting to create admin with data:", {k: v for k, v in admin_data.items() if k != 'password'})
            
            # Create admin user
            admin_id = db_service.create_admin(admin_data)
            
            if not admin_id:
                flash('Failed to create admin account. Please try again.', 'error')
                return render_template('admin/register.html', form=form)
            
            # Log the admin in
            admin_user = db_service.get_admin_by_id(admin_id)
            if not admin_user:
                flash('Admin account was created but we encountered an issue logging you in. Please try logging in manually.', 'warning')
                return redirect(url_for('admin.login'))
            
            login_user(admin_user, remember=form.remember_me.data)
            
            # Set session variables
            session.update({
                'user_id': str(admin_user.id),
                'is_admin': True,
                'full_name': admin_user.full_name or '',
                'email': admin_user.email
            })
            
            # Set remember me cookie
            if form.remember_me.data:
                session.permanent = True
                current_app.permanent_session_lifetime = timedelta(days=30)
            
            flash('Admin registration successful! Welcome to the dashboard.', 'success')
            return redirect(url_for('admin.dashboard'))
            
        except ValueError as ve:
            flash(f'Validation error: {str(ve)}', 'error')
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"Unexpected error in admin registration: {error_details}")
            current_app.logger.error(f"Admin registration error: {str(e)}\n{error_details}")
            flash('An unexpected error occurred during registration. Our team has been notified.', 'error')
    
    # If we get here, there was an error or it's a GET request
    return render_template('admin/register.html', form=form)

def clear_flash_messages():
    """Helper function to clear flash messages from session."""
    if '_flashes' in session:
        session.pop('_flashes', None)
        session.modified = True

@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    """Admin dashboard with statistics and overview."""
    # Clear any existing flash messages to prevent accumulation
    clear_flash_messages()
    
    print("\n[DEBUG] ====== Dashboard route called ======")
    print(f"[DEBUG] Current user: {current_user.email if current_user.is_authenticated else 'Not authenticated'}")
    print(f"[DEBUG] User ID: {current_user.id if current_user.is_authenticated else 'N/A'}")
    print(f"[DEBUG] Is admin: {getattr(current_user, 'is_admin', False)}")
    
    # Double-check admin status
    if not getattr(current_user, 'is_admin', False):
        print("[WARNING] User does not have admin privileges, logging out")
        session.clear()
        logout_user()
    total_users = 0
    new_users = 0
    total_active_users = 0
    recent_activity = []
    
    try:
        # Initialize Supabase client
        supabase = db_service.get_supabase_client()
        
        # Fetch client statistics
        print("[DEBUG] Fetching client statistics...")
        clients_response = supabase.table('clients').select('*').execute()
        
        if hasattr(clients_response, 'data'):
            clients = clients_response.data if clients_response.data else []
            total_users = len(clients)
            print(f"[DEBUG] Found {total_users} total users")
        else:
            clients = []
            total_users = 0
            print("[WARNING] No client data found")
            
        # Calculate new users (last 7 days)
        one_week_ago = (datetime.utcnow() - timedelta(days=7)).strftime('%Y-%m-%d')
        new_users = len([u for u in clients 
                        if u.get('created_at') 
                        and (isinstance(u['created_at'], str) and datetime.strptime(u['created_at'].split('T')[0], '%Y-%m-%d') >= datetime.strptime(one_week_ago, '%Y-%m-%d')
                             or not isinstance(u['created_at'], str) and u['created_at'].date() >= datetime.strptime(one_week_ago, '%Y-%m-%d').date())])
        
        # Get recent activity (last 10 logins)
        try:
            login_activity = supabase.table('clients')\
                .select('*')\
                .order('last_login', desc=True)\
                .limit(10)\
                .execute()
            
            if hasattr(login_activity, 'data'):
                recent_activity = login_activity.data
                print(f"[DEBUG] Found {len(recent_activity)} recent logins")
        except Exception as e:
            print(f"[WARNING] Could not fetch recent activity: {str(e)}")
            recent_activity = []
            
        # Get active users (last 24 hours)
        try:
            one_day_ago = (datetime.utcnow() - timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S')
            active_users = supabase.table('clients')\
                .select('id', count='exact')\
                .not_.is_('last_login', 'null')\
                .gte('last_login', one_day_ago)\
                .execute()
                
            if hasattr(active_users, 'count') and active_users.count is not None:
                total_active_users = active_users.count
            else:
                total_active_users = 0
        except Exception as e:
            print(f"[WARNING] Could not fetch active users: {str(e)}")
            total_active_users = 0
            
    except Exception as e:
        print(f"[ERROR] Error in dashboard data fetching: {str(e)}")
        # Use default values set at the beginning of the function
    
    # Prepare recent activity data with serializable timestamps
    serialized_activity = []
    for activity in recent_activity:
        try:
            # Create a copy of the activity dict
            serialized = dict(activity)
            
            # Convert datetime objects to ISO format strings
            for key, value in serialized.items():
                if hasattr(value, 'isoformat'):  # Check if it's a datetime object
                    serialized[key] = value.isoformat()
                    
            serialized_activity.append(serialized)
        except Exception as e:
            print(f"[WARNING] Error serializing activity: {str(e)}")
            continue
    
    # Prepare template context with serialized data
    return render_template('admin/dashboard.html',
                         total_users=total_users,
                         new_users=new_users,
                         total_active_users=total_active_users,
                         recent_activity=serialized_activity)

def generate_random_password(length=12):
    """Generate a random password."""
    alphabet = string.ascii_letters + string.digits + '!@#$%^&*'
    return ''.join(secrets.choice(alphabet) for _ in range(length))

@admin_bp.route('/debug/db')
@login_required
@admin_required
def debug_db():
    """Debug endpoint to check database connection and tables."""
    try:
        supabase = db_service.get_supabase_client()
        
        # Check if we can connect to the database
        try:
            result = supabase.table('clients').select('count', count='exact').execute()
            client_count = result.count or 0
        except Exception as e:
            return f"Error querying clients table: {str(e)}"
            
        # Get table structure
        tables = ['clients', 'admin_users', 'psychologists', 'guidance_counselors']
        table_info = {}
        
        for table in tables:
            try:
                # Get sample data (first row) to check structure
                result = supabase.table(table).select('*').limit(1).execute()
                table_info[table] = {
                    'exists': True,
                    'columns': list(result.data[0].keys()) if result.data else [],
                    'count': len(supabase.table(table).select('*').execute().data or [])
                }
            except Exception as e:
                table_info[table] = {
                    'exists': False,
                    'error': str(e)
                }
        
        return f"""
        <h1>Database Debug Info</h1>
        <h2>Connection Status</h2>
        <p>Connected to Supabase: {'Yes' if supabase else 'No'}</p>
        
        <h2>Table Information</h2>
        <pre>{json.dumps(table_info, indent=2)}</pre>
        """
        
    except Exception as e:
        return f"Error in debug endpoint: {str(e)}"

@admin_bp.route('/manage_users')
@login_required
@admin_required
def manage_users():
    """Manage all users (admin, client, psychologist, staff)."""
    print("\n[DEBUG] ====== manage_users route called ======")
    print(f"[DEBUG] Request URL: {request.url}")
    print(f"[DEBUG] Current user: {current_user}")
    print(f"[DEBUG] is_authenticated: {current_user.is_authenticated}")
    print(f"[DEBUG] is_admin: {getattr(current_user, 'is_admin', False)}")
    
    def process_user_list(users, user_type):
        """Helper function to process and validate user lists."""
        processed = []
        if not isinstance(users, list):
            print(f"[WARNING] Expected list for {user_type}, got {type(users).__name__}")
            return processed
            
        for user in users:
            try:
                if not isinstance(user, dict):
                    user = dict(user) if hasattr(user, '__dict__') else {}
                    if not user:
                        continue
                
                # Ensure required fields exist with defaults
                user.setdefault('first_name', 'Unknown')
                user.setdefault('last_name', 'User')
                user.setdefault('email', 'No email')
                user.setdefault('user_type', user_type)
                user.setdefault('is_active', True)
                user.setdefault('created_at', datetime.utcnow())
                
                # Ensure all string fields are properly encoded
                for key, value in user.items():
                    if isinstance(value, str):
                        user[key] = value.strip()
                    elif value is None:
                        user[key] = ''
                
                processed.append(user)
                
            except Exception as e:
                print(f"[ERROR] Error processing {user_type} user: {str(e)}")
                import traceback
                traceback.print_exc()
                continue
                
        return processed
    
    try:
        # Initialize empty lists for all user types
        clients = []
        psychologists = []
        admins = []
        guidance_counselors = []
        
        # Get all user types with error handling
        try:
            clients_data = db_service.get_all_users() or []
            clients = process_user_list(clients_data, 'client')
            print(f"[DEBUG] Processed {len(clients)} clients")
        except Exception as e:
            print(f"[ERROR] Error processing clients: {str(e)}")
            import traceback
            traceback.print_exc()
        
        try:
            psychs_data = db_service.get_all_psychologists() or []
            psychologists = process_user_list(psychs_data, 'psychologist')
            for psych in psychologists:
                psych.update({
                    'is_admin': False,
                    'is_psychologist': True,
                    'is_super_admin': False
                })
            print(f"[DEBUG] Processed {len(psychologists)} psychologists")
        except Exception as e:
            print(f"[ERROR] Error processing psychologists: {str(e)}")
            traceback.print_exc()
            
        try:
            admins_data = db_service.get_all_admins() or []
            admins = process_user_list(admins_data, 'admin')
            for admin in admins:
                admin.update({
                    'is_admin': True,
                    'is_psychologist': False,
                    'is_super_admin': admin.get('is_super_admin', False)
                })
            print(f"[DEBUG] Processed {len(admins)} admins")
        except Exception as e:
            print(f"[ERROR] Error processing admins: {str(e)}")
            traceback.print_exc()
            
        try:
            gcs_data = db_service.get_all_guidance_counselors() or []
            guidance_counselors = process_user_list(gcs_data, 'guidance_counselor')
            for gc in guidance_counselors:
                gc.update({
                    'is_admin': False,
                    'is_psychologist': False,
                    'is_super_admin': False,
                    'is_active': gc.get('is_active', gc.get('is_available', True))
                })
            print(f"[DEBUG] Processed {len(guidance_counselors)} guidance counselors")
        except Exception as e:
            print(f"[ERROR] Error processing guidance counselors: {str(e)}")
            traceback.print_exc()
        
        # Combine all users
        all_users = clients + psychologists + admins + guidance_counselors
        
        # Sort users by creation date (newest first)
        try:
            all_users.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        except Exception as e:
            print(f"[WARNING] Error sorting users by creation date: {str(e)}")
            # Keep unsorted if there's an error
        
        # Count users by type
        user_counts = {
            'total': len(all_users),
            'clients': len(clients),
            'psychologists': len(psychologists),
            'admins': len(admins),
            'guidance_counselors': len(guidance_counselors)
        }
        
        print(f"[INFO] Loaded {len(all_users)} total users ({user_counts['clients']} clients, "
              f"{user_counts['psychologists']} psychologists, {user_counts['admins']} admins, "
              f"{user_counts['guidance_counselors']} guidance counselors)")
        
        # Debug: Print first user of each type if available
        for user_type, user_list in [('clients', clients), ('psychologists', psychologists),
                                   ('admins', admins), ('guidance_counselors', guidance_counselors)]:
            if user_list:
                print(f"[DEBUG] First {user_type} user: {user_list[0].get('email', 'No email')}")
        
        return render_template('admin/user_management.html',
                            users=all_users,
                            user_counts=user_counts,
                            current_user=current_user)
    
    except Exception as e:
        error_msg = f"[CRITICAL] Unhandled exception in manage_users: {str(e)}"
        print(error_msg)
        import traceback
        traceback.print_exc()
        flash('An error occurred while loading user data. Please check the logs for details.', 'error')
        return redirect(url_for('admin.dashboard'))
    

@admin_bp.route('/create-admin', methods=['GET', 'POST'])
@login_required
@admin_required
def create_admin():
    """Create a new admin account."""
    # Only super admins can create other admins
    if not current_user.is_super_admin:
        flash('You do not have permission to create admin accounts.', 'error')
        return redirect(url_for('admin.manage_users'))
    
    form = CreateAdminForm()
    
    if form.validate_on_submit():
        try:
            # Hash the password
            hashed_password = generate_password_hash(form.password.data)
            
            # Prepare admin data
            admin_data = {
                'email': form.email.data.lower().strip(),
                'password_hash': hashed_password,
                'full_name': f"{form.first_name.data.strip()} {form.last_name.data.strip()}",
                'is_super_admin': form.is_super_admin.data,
                'is_active': True
            }
            
            # Save to database
            admin = db_service.create_admin(admin_data)
            
            if admin:
                flash('Admin account created successfully!', 'success')
                return redirect(url_for('admin.manage_users'))
            else:
                flash('Failed to create admin account. The email may already be in use.', 'error')
                
        except Exception as e:
            current_app.logger.error(f"Error creating admin: {str(e)}", exc_info=True)
            flash('An error occurred while creating the admin account. Please try again.', 'error')
    
    # For GET requests or form validation errors, render the create admin form
    return render_template('admin/create_admin.html', form=form)

@admin_bp.route('/create-psychologist', methods=['GET', 'POST'])
@login_required
@admin_required
def create_psychologist():
    """Create a new psychologist account."""
    form = PsychologistForm(prefix='psychologist')
    
    if form.validate_on_submit():
        try:
            # Generate a random password
            password = generate_random_password()
            hashed_password = generate_password_hash(password)
            
            # Create psychologist
            psychologist_data = {
                'email': form.email.data.lower().strip(),
                'password': hashed_password,
                'first_name': form.first_name.data.strip(),
                'last_name': form.last_name.data.strip(),
                'license_number': form.license_number.data.strip(),
                'specialization': form.specialization.data.strip(),
                'is_active': True
            }
            
            # Save to database
            psychologist = db_service.create_psychologist(psychologist_data)
            
            # TODO: Send email with credentials
            
            flash(f'Psychologist account created successfully. Temporary password: {password}', 'success')
            return redirect(url_for('admin.manage_users'))
            
        except Exception as e:
            current_app.logger.error(f"Error creating psychologist: {str(e)}")
            flash('An error occurred while creating the psychologist account.', 'error')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"{getattr(form, field).label.text}: {error}", 'error')
    
    return redirect(url_for('admin.manage_users'))

@admin_bp.route('/users/<user_type>/<user_id>')
@login_required
@admin_required
def view_user(user_type, user_id):
    """View detailed information about a user."""
    try:
        user = None
        
        if user_type == 'admin':
            user = db_service.get_admin_by_id(user_id)
        elif user_type == 'psychologist':
            user = db_service.get_psychologist_by_id(user_id)
        elif user_type == 'client':
            user = db_service.get_user_by_id(user_id)
        elif user_type == 'guidance_counselor':
            user = db_service.get_guidance_counselor_by_id(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
            
        # Format the user data for display
        user_data = {
            'id': str(user.get('id')),
            'name': f"{user.get('first_name', '')} {user.get('last_name', '')}",
            'email': user.get('email', ''),
            'user_type': user_type.capitalize(),
            'status': 'Active' if user.get('is_active', False) else 'Inactive',
            'created_at': user.get('created_at', '').strftime('%B %d, %Y') if user.get('created_at') else 'N/A',
            'last_login': user.get('last_login', '').strftime('%B %d, %Y %H:%M') if user.get('last_login') else 'Never',
        }
        
        # Add role-specific fields
        if user_type == 'psychologist':
            user_data.update({
                'license_number': user.get('license_number', 'N/A'),
                'specialization': user.get('specialization', 'N/A'),
                'bio': user.get('bio', 'No bio provided'),
            })
        
        return jsonify(user_data)
        
    except Exception as e:
        current_app.logger.error(f"Error fetching user {user_type} {user_id}: {str(e)}")
        return jsonify({'error': 'An error occurred while fetching user data'}), 500





@admin_bp.route('/update-role', methods=['POST'])
@login_required
@admin_required
def update_admin_role():
    """Update admin role (admin/super_admin)."""
    if not request.is_json:
        return jsonify({'message': 'Invalid request'}), 400

    data = request.get_json()
    user_id = data.get('user_id')
    is_super_admin = data.get('is_super_admin', False)

    if not user_id:
        return jsonify({'message': 'User ID is required'}), 400

    try:
        # Only super admins can change roles
        if not current_user.is_super_admin:
            return jsonify({'message': 'Insufficient permissions'}), 403

        # Prevent modifying your own role
        if str(current_user.id) == str(user_id):
            return jsonify({'message': 'Cannot modify your own role'}), 400

        # Get the user to update
        user = db_service.get_admin_by_id(user_id)
        if not user:
            return jsonify({'message': 'Admin user not found'}), 404

        # Update the role
        success = db_service.update_admin(user_id, {'is_super_admin': is_super_admin})
        
        if success:
            return jsonify({'message': 'Role updated successfully'}), 200
        else:
            return jsonify({'message': 'Failed to update role'}), 500

    except Exception as e:
        current_app.logger.error(f"Error updating admin role: {str(e)}")
        return jsonify({'message': 'An error occurred while updating the role'}), 500

@admin_bp.route('/delete-admin/<user_id>', methods=['DELETE'])
@login_required
@admin_required
def delete_admin_user(user_id):
    """Delete an admin user."""
    try:
        # Only super admins can delete admins
        if not current_user.is_super_admin:
            return jsonify({'message': 'Insufficient permissions'}), 403

        # Prevent deleting yourself
        if str(current_user.id) == str(user_id):
            return jsonify({'message': 'Cannot delete your own account'}), 400

        # Delete the admin
        success = db_service.delete_admin(user_id)
        
        if success:
            return jsonify({'message': 'Admin deleted successfully'}), 200
        else:
            return jsonify({'message': 'Failed to delete admin'}), 500

    except Exception as e:
        current_app.logger.error(f"Error deleting admin: {str(e)}")
        return jsonify({'message': 'An error occurred while deleting the admin'}), 500

@admin_bp.route('/users/<user_type>/<user_id>/delete', methods=['POST', 'DELETE'])
@login_required
@admin_required
def delete_user(user_type, user_id):
    """Delete a user, admin, or psychologist.
    
    This endpoint handles both form submissions (POST) and API calls (DELETE).
    """
    try:
        # Only super admins can delete users
        if not current_user.is_super_admin:
            if request.is_json:
                return jsonify({'message': 'Insufficient permissions'}), 403
            flash('You do not have permission to perform this action.', 'error')
            return redirect(url_for('admin.manage_users'))

        # Prevent deleting yourself
        if str(current_user.id) == str(user_id):
            if request.is_json:
                return jsonify({'message': 'Cannot delete your own account'}), 400
            flash('You cannot delete your own account.', 'error')
            return redirect(url_for('admin.manage_users'))

        # Delete the user based on type
        success = False
        if user_type == 'admin':
            success = db_service.delete_admin(user_id)
            flash_message = 'Admin account deleted successfully.'
        elif user_type == 'psychologist':
            success = db_service.delete_psychologist(user_id)
            flash_message = 'Psychologist account deleted successfully.'
        elif user_type == 'client':
            success = db_service.delete_user(user_id)
            flash_message = 'User account deleted successfully.'
        else:
            if request.is_json:
                return jsonify({'message': 'Invalid user type'}), 400
            flash('Invalid user type.', 'error')
            return redirect(url_for('admin.manage_users'))

        # Handle JSON response for API calls
        if request.is_json:
            if success:
                return jsonify({'message': flash_message}), 200
            else:
                return jsonify({'message': f'Failed to delete {user_type}'}), 500
        
        # Handle form submission response
        if success:
            flash(flash_message, 'success')
        else:
            flash(f'Failed to delete {user_type}.', 'error')

        return redirect(url_for('admin.manage_users'))

    except Exception as e:
        current_app.logger.error(f"Error deleting {user_type} {user_id}: {str(e)}")
        if request.is_json:
            return jsonify({'message': 'An error occurred while deleting the user'}), 500
        flash('An error occurred while deleting the user.', 'error')
        return redirect(url_for('admin.manage_users'))

@admin_bp.route('/api/users', methods=['POST'])
@admin_bp.route('/api/users/<string:user_id>', methods=['PUT'])
@login_required
@admin_required
def manage_user_api(user_id=None):
    """API endpoint for creating or updating users."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': 'No data provided'}), 400

        # Common user data
        user_data = {
            'first_name': data.get('first_name', '').strip(),
            'last_name': data.get('last_name', '').strip(),
            'email': data.get('email', '').lower().strip(),
            'is_active': bool(data.get('is_active', True))
        }

        # Validate required fields
        required_fields = ['first_name', 'last_name', 'email']
        for field in required_fields:
            if not user_data[field]:
                return jsonify({'success': False, 'message': f'{field.replace("_", " ").title()} is required'}), 400

        # Email validation
        import re
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, user_data['email']):
            return jsonify({'success': False, 'message': 'Invalid email format'}), 400

        # Handle password if provided or for new user
        password = data.get('password')
        if not user_id and not password:
            return jsonify({'success': False, 'message': 'Password is required for new users'}), 400
            
        if password:
            if len(password) < 8:
                return jsonify({'success': False, 'message': 'Password must be at least 8 characters long'}), 400
            user_data['password'] = password  # Will be hashed in the service layer

        role = data.get('role')
        if not role:
            return jsonify({'success': False, 'message': 'Role is required'}), 400

        # Create or update user based on role
        if role == 'admin':
            try:
                if user_id:
                    # Update existing admin
                    admin = db_service.get_admin_by_id(user_id)
                    if not admin:
                        return jsonify({'success': False, 'message': 'Admin not found'}), 404
                    
                    # Update admin data
                    updated_admin = db_service.update_admin(user_id, user_data)
                    return jsonify({
                        'success': True,
                        'message': 'Admin updated successfully',
                        'user': updated_admin
                    })
                else:
                    # Create new admin
                    admin_id = db_service.create_admin(user_data)
                    if not admin_id:
                        return jsonify({'success': False, 'message': 'Failed to create admin user'}), 400
                    
                    # Get the created admin to return
                    new_admin = db_service.get_admin_by_id(admin_id)
                    return jsonify({
                        'success': True,
                        'message': 'Admin created successfully',
                        'user': new_admin
                    }), 201
                    
            except ValueError as e:
                return jsonify({'success': False, 'message': str(e)}), 400
            except Exception as e:
                current_app.logger.error(f"Error in manage_user_api (admin): {str(e)}")
                return jsonify({'success': False, 'message': 'An error occurred while processing your request'}), 500
                
                new_admin = db_service.create_admin(user_data)
        elif role in ['psychologist', 'guidance_counselor']:
            try:
                # Additional fields for mental health professionals
                professional_data = {
                    'license_number': data.get('license_number', '').strip(),
                    'specialization': data.get('specialization', '').strip(),
                    'phone': data.get('phone', '').strip(),
                    'address': data.get('address', '').strip(),
                    'bio': data.get('bio', '').strip()
                }
                
                # Merge with user data
                user_data.update(professional_data)
                
                if role == 'psychologist':
                    if user_id:
                        # Update existing psychologist
                        psychologist = db_service.get_psychologist_by_id(user_id)
                        if not psychologist:
                            return jsonify({'success': False, 'message': 'Psychologist not found'}), 404
                        
                        updated_psychologist = db_service.update_psychologist(user_id, user_data)
                        return jsonify({
                            'success': True,
                            'message': 'Psychologist updated successfully',
                            'user': updated_psychologist
                        })
                    else:
                        # Create new psychologist
                        psychologist_id = db_service.create_psychologist(user_data)
                        if not psychologist_id:
                            return jsonify({'success': False, 'message': 'Failed to create psychologist'}), 400
                        
                        new_psychologist = db_service.get_psychologist_by_id(psychologist_id)
                        return jsonify({
                            'success': True,
                            'message': 'Psychologist created successfully',
                            'user': new_psychologist
                        }), 201
                else:  # guidance_counselor
                    if user_id:
                        # Update existing guidance counselor
                        counselor = db_service.get_guidance_counselor_by_id(user_id)
                        if not counselor:
                            return jsonify({'success': False, 'message': 'Guidance counselor not found'}), 404
                        
                        updated_counselor = db_service.update_guidance_counselor(user_id, user_data)
                        return jsonify({
                            'success': True,
                            'message': 'Guidance counselor updated successfully',
                            'user': updated_counselor
                        })
                    else:
                        # Create new guidance counselor
                        counselor_id = db_service.create_guidance_counselor(user_data)
                        if not counselor_id:
                            return jsonify({'success': False, 'message': 'Failed to create guidance counselor'}), 400
                        
                        new_counselor = db_service.get_guidance_counselor_by_id(counselor_id)
                        return jsonify({
                            'success': True,
                            'message': 'Guidance counselor created successfully',
                            'user': new_counselor
                        }), 201
                        
            except ValueError as e:
                return jsonify({'success': False, 'message': str(e)}), 400
            except Exception as e:
                current_app.logger.error(f"Error in manage_user_api ({role}): {str(e)}")
                return jsonify({'success': False, 'message': 'An error occurred while processing your request'}), 500
                
        elif role == 'client':
            try:
                # Additional fields for clients
                client_data = {
                    'username': data.get('username', '').strip(),
                    'date_of_birth': data.get('date_of_birth'),
                    'gender': data.get('gender', '').strip(),
                    'phone': data.get('phone', '').strip()
                }
                
                # Merge with user data
                user_data.update(client_data)
                
                if user_id:
                    # Update existing client
                    client = db_service.get_user_by_id(user_id)
                    if not client:
                        return jsonify({'success': False, 'message': 'Client not found'}), 404
                    
                    updated_client = db_service.update_user(user_id, user_data)
                    return jsonify({
                        'success': True,
                        'message': 'Client updated successfully',
                        'user': updated_client
                    })
                else:
                    # Create new client
                    client_id = db_service.create_user(user_data)
                    if not client_id:
                        return jsonify({'success': False, 'message': 'Failed to create client'}), 400
                    
                    new_client = db_service.get_user_by_id(client_id)
                    return jsonify({
                        'success': True,
                        'message': 'Client created successfully',
                        'user': new_client
                    }), 201
                    
            except ValueError as e:
                return jsonify({'success': False, 'message': str(e)}), 400
            except Exception as e:
                current_app.logger.error(f"Error in manage_user_api (client): {str(e)}")
                return jsonify({'success': False, 'message': 'An error occurred while processing your request'}), 500
                
        else:
            return jsonify({'success': False, 'message': 'Invalid role specified'}), 400
            
    except Exception as e:
        current_app.logger.error(f"Unexpected error in manage_user_api: {str(e)}")
        return jsonify({'success': False, 'message': 'An unexpected error occurred'}), 500

@admin_bp.route('/logout')
@login_required
@login_required
def logout():
    """Handle admin logout."""
    try:
        # Log the logout
        logger.info("Admin %s logging out", current_user.email)
        
        # Clear user session
        user_email = current_user.email
        
        # Logout the user (this will clear the session)
        logout_user()
        
        # Clear any remaining session data
        session.clear()
        
        # Clear any flash messages
        clear_flash_messages()
        
        # Add a success message
        flash('You have been successfully logged out.', 'success')
        logger.info("Admin %s logged out successfully", user_email)
        
    except Exception as e:
        logger.error("Error during logout: %s\n%s", str(e), traceback.format_exc())
        flash('An error occurred during logout.', 'error')
    
    # Redirect to login page
    return redirect(url_for('admin.admin_login'))
