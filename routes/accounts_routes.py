import json
import logging
import os
import secrets
import string
import sys
import traceback
from datetime import datetime, timedelta
from functools import wraps
from typing import Counter

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
def management():
    """Manage all users (admin, client, psychologist, staff)."""
    print("\n[DEBUG] ====== manage_users route called ======")
    print(f"[DEBUG] Request URL: {request.url}")
    print(f"[DEBUG] Current user: {current_user}")
    print(f"[DEBUG] is_authenticated: {current_user.is_authenticated}")
    print(f"[DEBUG] is_admin: {getattr(current_user, 'is_admin', False)}")
    
    # try:
    
    users_result = db_service.get_all_accounts();
    users_data = users_result.data if hasattr(users_result, "data") else []
          
    # Count users per role
    role_counts = Counter(user.get('role', '').lower() for user in users_data)
    active_counts = sum(1 for user in users_data if not user.get('is_active', False))
    
    # Count users created in the current month
    # Get current year and month
    now = datetime.now()
    current_year = now.year
    current_month = now.month
    
    users_created_this_month = [
        user for user in users_data
        if user.get('created_at') and
          datetime.fromisoformat(user['created_at']).year == current_year and
          datetime.fromisoformat(user['created_at']).month == current_month
    ]
    new_users_count = len(users_created_this_month)
    
    pending_counts = sum(1 for user in users_data if not user.get('is_verified', False))
    
    # Count users object
    user_counts = {
      'total_users': len(users_data),
      'active_counts': active_counts,
      'new_users_count': new_users_count,
      'pending_counts': role_counts.get('admin', 0)
    }
  
    return render_template('accounts/user_management.html',
      users= users_data,
      user_counts=user_counts,
      current_user=current_user)
      
    # except Exception as e:
    #   error_msg = f"[CRITICAL] Unhandled exception in manage_users: {str(e)}"
    #   print(error_msg)
    #   import traceback
    #   traceback.print_exc()
    #   flash('An error occurred while loading user data. Please check the logs for details.', 'error')
    #   return redirect(url_for('admin.dashboard'))

@accounts_bp.route('/user/<id>',methods=['GET'])
@login_required
def get_user(id):
  data = request.get_json()
  print("\n[DEBUG] ====== get_user route called ======")
  print(f"[DEBUG] Request Data: {data}")
  return jsonify({'message': 'User data fetched successfully.'}), 200
      
@accounts_bp.route('/user/create',methods=['POST'])
@login_required
def create_user():
  print("\n[DEBUG] ====== create_user route called ======")
  data = request.get_json()
  print(f"[DEBUG] Request Data:",data)
  return jsonify({'message': 'User created successfully.'}), 201
  
@accounts_bp.route('/user/update/<id>',methods=['PUT'])  
@login_required
def update_user(id):
  data = request.get_json()
  print("\n[DEBUG] ====== update_user route called ======")
  print(f"[DEBUG] Request Data: {data}")
  return jsonify({'message': 'User updated successfully.'}), 200
     
@accounts_bp.route('/user/delete/<id>',methods=['PUT'])  
@login_required
def delete_user(id):
  data = request.get_json()
  print("\n[DEBUG] ====== delete_user route called ======")
  print(f"[DEBUG] Request Data: {data}")
  return jsonify({'message': 'User deleted successfully.'}), 200


