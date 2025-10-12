import os
from werkzeug.security import check_password_hash
from models import Psychologist, GuidanceCounselor, Client, Admin
from config import init_supabase

from flask import render_template, request, session, g, flash, redirect, url_for
from flask_login import login_user , current_user

from services.accounts_reposervice import account_repo_service
from models.user import User

class AuthService:
  def __init__(self):
    try:
      self.supabase: Client = init_supabase()
      self.supabase_role: Client = init_supabase(True)
    except Exception as e:
      print(f"[Supabase] ❌ Failed to initialize in DatabaseService: {str(e)}")
      self.supabase = None
      self.supabase_role = None

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
              user_id=user_id,
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
  
  def send_verification_email(self, email):
      """Send email verification for new user or resend for existing user"""
      try:
          # Resend verification for existing user
          response = self.supabase.auth.resend({
              "type": "signup",
              "email": email,
              "options": {
                  "email_redirect_to": f"{os.getenv('APP_URL')}/auth/verify-email"
              }
          })
          
          #Get Account By Email
          user_account = account_repo_service.get_account_by_email(email)
          user = user_account.data[0] if user_account and user_account.data else None
          if not user:
              print(f"[ERROR] No user account found for email: {email}")
              return {"success": False, "error": "User account not found"}
          
          #Update user_accounts verified email
          resp = account_repo_service.update_account(user.get('user_id'), {"is_verified": True})
          
          return {"success": True, "data": response}
      except Exception as e:
          return {"success": False, "error": str(e)}
  
  def get_auth_user_by_id(self, user_id: str):
    """Fetch user data from auth.users table by user ID"""
    try:
        if not self.supabase_role:
            print("[ERROR] Service role client not initialized")
            return None
            
        # Use admin client to get user from auth.users
        response = self.supabase_role.auth.admin.get_user_by_id(user_id)
        
        if response.user:
            print(f"[DEBUG] Auth user found: {response.user.email}")
            return response.user
        else:
            print(f"[DEBUG] No auth user found with ID: {user_id}")
            return None
            
    except Exception as e:
        print(f"[ERROR] Failed to fetch auth user: {str(e)}")
        return None
  
  def get_auth_user_by_email(self, email: str):
    """Fetch user data from auth.users table by email"""
    try:
        if not self.supabase_role:
            print("[ERROR] Service role client not initialized")
            return None
            
        # List users and filter by email (since there's no direct get by email)
        response = self.supabase_role.auth.admin.list_users()
        
        if response.users:
            for user in response.users:
                if user.email and user.email.lower() == email.lower():
                    print(f"[DEBUG] Auth user found by email: {user.email}")
                    return user
                    
        print(f"[DEBUG] No auth user found with email: {email}")
        return None
        
    except Exception as e:
        print(f"[ERROR] Failed to fetch auth user by email: {str(e)}")
        return None
    
  def get_all_auth_users(self):
    """Get all users from auth.users table"""
    try:
        if not self.supabase_role:
            print("[ERROR] Service role client not initialized")
            return None
            
        response = self.supabase_role.auth.admin.list_users()
        
        if response.users:
            print(f"[DEBUG] Found {len(response.users)} auth users")
            return response.users
        else:
            print("[DEBUG] No auth users found")
            return []
            
    except Exception as e:
        print(f"[ERROR] Failed to fetch all auth users: {str(e)}")
        return None  
        
  
# Singleton instance
auth_service = AuthService()
