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
from services.accounts_reposervice import db_service

# Import forms from the forms package
from forms.base_forms import (
    CreateAdminForm
)

# Import Supabase client
from supabase import create_client, Client
from config import SUPABASE_URL, SUPABASE_KEY, SUPABASE_SERVICE_ROLE_KEY

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create admin Blueprint with both template folder and URL prefix
accounts_bp = Blueprint(
    'accounts',
    __name__,
    template_folder='templates/accounts',
    url_prefix='/accounts'
)

# Initialize Supabase client
try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception as e:
    print(f"[ERROR] Failed to initialize Supabase client: {str(e)}")
    supabase = None

@accounts_bp.route('/management')
@login_required
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
    

