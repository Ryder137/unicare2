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

from flask import Blueprint, app, render_template, redirect, url_for, flash, request, jsonify, current_app, abort, session
from flask_login import current_user, login_required, login_url, login_user, logout_user
from werkzeug.security import check_password_hash, generate_password_hash
from forms import RegisterForm
from models.accounts import AccountsModel,PsychologistDetailModel

# Add the project root to the Python path first
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Now import the accounts repository service
from services.accounts_reposervice import account_repo_service

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
    
    try:
      users_result = account_repo_service.get_all_accounts();
      users_data = users_result.data if hasattr(users_result, "data") else []
      
      # Count users created in the current month
      # Get current year and month
      now = datetime.now()
      current_year = now.year
      current_month = now.month
      
      from dateutil import parser
      
      new_users_count = len([
          user for user in users_data
          if user.get('created_at') and
            parser.parse(user['created_at']).year == current_year and
            parser.parse(user['created_at']).month == current_month
      ])
      
      user_counts = len(users_data)
      active_counts = sum(1 for user in users_data if user.get('is_active', True))
      pending_counts = sum(1 for user in users_data if not user.get('is_verified', True))
      
      # Count users object
      user_counts = {
        'total_users': user_counts,
        'active_counts': active_counts,
        'new_users_count': new_users_count,
        'pending_counts': pending_counts
      }
    
      return render_template('accounts/user_management.html',
        users= users_data,
        user_counts=user_counts,
        current_user=current_user)
      
    except Exception as e:
      error_msg = f"[CRITICAL] Unhandled exception in manage_users: {str(e)}"
      print(error_msg)
      import traceback
      traceback.print_exc()
      flash('An error occurred while loading user data. Please check the logs for details.', 'error')
      return redirect(url_for('admin.dashboard'))

@accounts_bp.route('/register', methods=['GET', 'POST'])
def register():
  print("\n[DEBUG] Accounts/Register route called") 
  form = RegisterForm()
  
  
  return render_template('accounts/register_client.html',form=form)

# API AJAX URL CALLS

@accounts_bp.route('/user/<string:id>',methods=['GET'])
@login_required
def get_user(id):
  print("\n[DEBUG] ====== get_user route called ======")
  print("\n[DEBUG] GET USER DETAILS : ",id  )

  user_result = db_service.get_account_by_id(id);

  if not user_result:
      return jsonify({'error': 'User not found.'}), 404
    
  return jsonify({'user': user_result}), 200
  
# CREATE USER ACCOUNT
@accounts_bp.route('/user/create',methods=['POST'])
@login_required
def create_user():
  print("\n[DEBUG] ====== create_user route called ======")
  # Accept multipart/form-data for file upload
  print(f"[DEBUG] Request Form: {request.form}")
  print(f"[DEBUG] Request Files: {request.files}")
  data = request.form.to_dict()
  avatar_file = request.files.get('avatar')
  
  # Ensure data is a dictionary
  if isinstance(data, str):
    try:
        data = json.loads(data)
    except Exception as e:
        print(f"[ERROR] Failed to parse JSON string: {e}")
        return jsonify({'error': 'Invalid JSON format.'}), 400
  elif not isinstance(data, dict):
      return jsonify({'error': 'Invalid data format.'}), 400
  
  # Validate password and confirm_password match
  password = data.get("password")
  confirm_password = data.get("confirm_password")
  if password != confirm_password:
    return jsonify({'error': 'Password and confirm password do not match.'}), 400

  # Hash the password
  hashed_password = generate_password_hash(password)

  # Handle avatar upload to Supabase Storage
  avatar_url = None
  if avatar_file and avatar_file.filename:
    try:
      # Generate unique filename
      ext = os.path.splitext(avatar_file.filename)[1]
      filename = f"avatars/{secrets.token_hex(8)}{ext}"
      # Upload to Supabase Storage bucket (e.g., 'avatars')
      file_bytes = avatar_file.read()
      res = supabase.storage.from_('avatars').upload(filename, file_bytes)
      if hasattr(res, 'error') and res.error:
        print(f"[ERROR] Supabase upload error: {res.error}")
      else:
        # Get public URL
        avatar_url = supabase.storage.from_('avatars').get_public_url(filename)
        print(f"[DEBUG] Avatar uploaded: {avatar_url}")
    except Exception as e:
      print(f"[ERROR] Avatar upload failed: {str(e)}")

  try:
    reqAccounts = AccountsModel(
      id=None,
      first_name = data.get("first_name"),
      middle_name = data.get("middle_name"),
      last_name = data.get("last_name"),
      email = data.get("email"),
      role = data.get("role"),
      password = hashed_password,
      is_deleted = False,
      is_active = True,
      is_verified = False,
      image = avatar_url
    )
    
    print(f"[DEBUG] Prepared Account Data Image: {reqAccounts.image}")
      
    new_user = account_repo_service.create_account(reqAccounts)
    print(f"[DEBUG] New User Created: {new_user}")
    
    # If the new user is a psychologist, create a corresponding psychologist detail record
    if reqAccounts.role == 'psychologist' and new_user is not None:
      reqPsychologistDetail = PsychologistDetailModel(
        id=None,
        user_id=new_user,  # Use the ID of the newly created user account
        license_number = data.get("license_number"),
        specialization = data.get("specialization"),
        bio = data.get("bio"),
        years_of_experience = data.get("years_of_experience"),
        education = data.get("education"),
        languages_spoken = data.get("languages_spoken", []),
        consultation_fee = data.get("consultation_fee"),
        is_available = data.get("is_available", True),
        created_at = datetime.now().isoformat(),
        updated_at = datetime.now().isoformat()
      )
      
      print(f"[DEBUG] Prepared Psychologist Detail Data: {reqPsychologistDetail}")
      
      psychologist_detail_result = account_repo_service.create_psychologist_detail(reqPsychologistDetail)
      print(f"[DEBUG] Psychologist Detail Created: {psychologist_detail_result}")
    
    return jsonify({'message': 'User created successfully.'}), 201
  
  except Exception as e:
    print(f"[ERROR] Failed to create user: {str(e)}")
    return jsonify({'error': 'Failed to create user.'}), 500
#######################################################################
  
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

@accounts_bp.route('/modal/user/register')
def modal_user():
    print("\n[DEBUG] ====== modal_user route called ======")
    try:
      return render_template('accounts/user_modal_form.html')
    except Exception as e:
        print(f"[ERROR] Failed to load user modal form: {str(e)}")
        return jsonify({'error': 'Failed to load user modal form.'}), 500

@accounts_bp.route('/modal/user/<user_id>', methods=['GET'])
def modal_view_user(user_id):
    print("\n[DEBUG] ====== modal_view_user route called ======")
    print("\n[DEBUG] Selected user id : ",user_id)
    try:
      result = account_repo_service.get_account_by_id(user_id)
      user = result.data[0] if hasattr(result, "data") and result.data else None
      
      if not user:
        return jsonify({'error': 'User not found.'}), 404
      
      psych_user = None
      if user.get('role') == 'psychologist':
        psych_result = account_repo_service.get_psychologist_details(user_id)
        psych_user = psych_result.data[0] if hasattr(psych_result, "data") and psych_result.data else None
      
      return render_template('accounts/user_modal_profile.html', 
                             user=user, 
                             psych_user=psych_user,
                             now=datetime.now())
    except Exception as e:
      print(f"[ERROR] Failed to load user modal form: {str(e)}")
      return jsonify({'error': 'Failed to load user modal form.'}), 500

@accounts_bp.route('/users/data')
def users_data():
  # Query your users and return as JSON
  result = account_repo_service.get_all_accounts();
  users = result.data if hasattr(result, "data") else []
  
  # Render table rows as HTML using Jinja2
  table_rows = render_template('accounts/user_table_list.html', users=users)
  
  return jsonify({'html': table_rows})