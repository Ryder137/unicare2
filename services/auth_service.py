from werkzeug.security import check_password_hash
from models import Psychologist, GuidanceCounselor, Client, Admin
from config import init_supabase

from flask import (
    Flask, render_template, request, jsonify, session, g, flash, 
    redirect, url_for, current_app, abort, send_from_directory
)

from flask_login import (
    LoginManager, UserMixin, login_user, login_required, 
    logout_user, current_user
)

from services.accounts_reposervice import account_repo_service
from models.user import User

class AuthService:
  def __init__(self):
    try:
      self.supabase: Client = init_supabase()
    except Exception as e:
      print(f"[Supabase] ❌ Failed to initialize in DatabaseService: {str(e)}")
      self.supabase = None

  def authenticate_user(self, credentials: dict):
      try:
          print(f"[AUTH] Authenticating user with email: {credentials.get('email')}")
          response = self.supabase.auth.sign_in_with_password(credentials)
          print(f"[AUTH] Supabase response: {response.user}")
          if response.user:
            print(f"[AUTH] User authenticated: {response}")
            return response.user  # Authenticated user object
          return None
      except Exception as e:
          print(f"[AUTH] Error authenticating user: {str(e)}")
          import traceback
          print(traceback.format_exc())
          return None


  """Process login for both users and admins."""
  def process_login(self, form, is_admin=False):
      print(f"[DEBUG] ***app.py_process_login ***")

      login_url = 'admin/login.html' if is_admin else 'auth/login.html'
      email = form.email.data.lower().strip()
      password = form.password.data
      remember_me = form.remember_me.data
      
      print(f"\n[LOGIN] {'Admin' if is_admin else 'User'} login attempt - Email: {email}")
      print(f"[DEBUG] Remember me: {remember_me}")
      
      # Validation : Check if Email is registered or not
      response_email = account_repo_service.get_account_by_email(email)
      user = response_email.data[0] if response_email and response_email.data else None
      if not response_email or not response_email.data or len(response_email.data) == 0:
          flash('Email not registered. Please sign up.', 'danger')
          print("[DEBUG] Login failed - email not found or not registered:", email)
          return render_template(login_url, form=form)

      user_role = user.get('role')
      # Validation : Check if Credentials are correct
      credentials = { "email": email, "password": password }
      response = auth_service.authenticate_user(credentials)
      
      if response is None:
          # Check for too many failed login attempts
          failed_attempts = user.get('failed_attempt', 0)
          if failed_attempts >= 5:  # Lock account after 5 failed attempts
              print(f"[LOGIN] Account locked due to too many failed {failed_attempts} attempts: {email}")
              flash('This account is temporarily locked. Please try again later or contact support.', 'error')
              return render_template(login_url, form=form)
          
          # Update failed login attempts
          account_repo_service.update_attempts(email, user_role, failed_attempts + 1)
          remaining_attempts = 5 - (failed_attempts + 1)
          if remaining_attempts > 0:
              flash(f'Invalid password. {remaining_attempts} attempts remaining.', 'error')
          else:
              flash('Account locked due to too many failed attempts. Please contact support.', 'error')
          
          print("[DEBUG] Login failed - authentication service error or invalid credentials")
          return render_template(login_url, form=form)
      
      print("[DEBUG] Login Success - DATA : ", user)
     
      user_id = response.id
      # Validate: User login is active or not
      is_active = user.get('is_active', True)
      if not is_active:
        print(f"[LOGIN] User account is not active: {email}")
        flash('This user account is disabled. Please contact support.', 'error')
        return render_template(login_url, form=form)
        
      print(f"[LOGIN] User account found and authenticated {user_role} user: {email}")
      
      fname = user.get('first_name') or ''
      lname = user.get('last_name') or ''
      full_name = f'{fname} {lname}'
      username = email.split('@')[0]
      
      session['user_role'] = user_role
      session['user_id'] = user_id
      
      # Create a user object for flask login.
      user_obj = User(
              id=user_id,
              email=email,
              username=username,
              is_admin=(user_role != 'client'),
              is_active=True
          )
      
      # Assign user object to flask login user for authenthication purposes in admin route
      login_user(user_obj, remember=remember_me)
      
      print(f"[DEBUG] user_role: {user_role}, is_admin: {current_user.is_admin}")
      print(f"[DEBUG] Redirecting to: {url_for('admin.dashboard') if user_role != 'client' else url_for('dashboard')}")
      print(f"[DEBUG] current_user: {current_user}, id: {current_user.id}, is_admin: {current_user.is_admin}")
      
      
      flash(f'Welcome back, {full_name}!', 'success')
      
      # Reset failed attempts and Update
      account_repo_service.reset_attempts(email, user_role)    
      
      if user_role != 'client':
        # For Admin dashboard users
        print("[DEBUG] Redirecting to admin dashboard", url_for('admin.dashboard'))
        return redirect(url_for('admin.dashboard'))
      else:
        # For regular users, check for next parameter or go to dashboard
        next_page = request.args.get('next')
        if next_page:
          print(f"[DEBUG] Redirecting to next page: {next_page}")
          return redirect(next_page)

      print(f"[DEBUG] Redirecting to user dashboard: {url_for('dashboard')}")
      return redirect(url_for('dashboard'))
        
# Singleton instance
auth_service = AuthService()
