import os
from typing import List, Optional, Dict, Any, Union
from datetime import datetime, timedelta, timezone
from supabase import create_client, Client
from config import init_supabase
from models.user import User
from models.game_score import GameScore
from models.personality_test import PersonalityTestResult
from models.admin import Admin

class DatabaseService:
    def __init__(self):
        try:
            self.supabase: Client = init_supabase()
            print("[Supabase] Connection initialized in DatabaseService")
        except Exception as e:
            print(f"[Supabase] ❌ Failed to initialize in DatabaseService: {str(e)}")
            self.supabase = None
            
    def get_supabase_client(self, use_service_role: bool = False) -> Client:
        """
        Get the Supabase client instance.
        
        Args:
            use_service_role: If True, uses the service role client (bypasses RLS)
            
        Returns:
            The Supabase client instance
            
        Raises:
            Exception: If Supabase client is not initialized
        """
        if not self.supabase:
            try:
                if use_service_role:
                    # Import here to avoid circular imports
                    from config import SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY
                    self.supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
                else:
                    self.supabase = init_supabase()
                    
                if not self.supabase:
                    raise Exception("Failed to initialize Supabase client")
            except Exception as e:
                print(f"[Supabase] ❌ Error getting Supabase client: {str(e)}")
                raise Exception("Database connection error. Please try again later.")
        return self.supabase
    
    # User Management Methods
    def get_users_count(self) -> int:
        """Get the total count of all clients (non-admin)."""
        try:
            supabase = self.get_supabase_client()
            result = supabase.table('clients').select('*', count='exact').execute()
            return result.count or 0
        except Exception as e:
            print(f"[Database] Error getting clients count: {str(e)}")
            return 0
            
    def get_all_users(self, exclude_id: str = None) -> List[dict]:
        """Get all regular users (non-admin)."""
        try:
            supabase = self.get_supabase_client()
            query = supabase.table('clients').select('*').order('created_at', desc=True)
            
            if exclude_id:
                query.neq('id', exclude_id)
                
            result = query.execute()
            return result.data if result.data else []
        except Exception as e:
            print(f"[Database] Error getting all users: {str(e)}")
            return []
            
    def get_all_admins(self, exclude_id: str = None) -> List[dict]:
        """Get all admin users."""
        try:
            supabase = self.get_supabase_client(use_service_role=True)
            query = supabase.table('admin_users').select('*').order('created_at', desc=True)
            
            if exclude_id:
                query.neq('id', exclude_id)
                
            result = query.execute()
            return result.data if result.data else []
        except Exception as e:
            print(f"[Database] Error getting all admins: {str(e)}")
            return []
            
    def get_all_psychologists(self) -> List[dict]:
        """Get all psychologist users."""
        try:
            supabase = self.get_supabase_client(use_service_role=True)
            result = supabase.table('psychologists').select('*').order('created_at', desc=True).execute()
            return result.data if result.data else []
        except Exception as e:
            print(f"[Database] Error getting all psychologists: {str(e)}")
            return []
            
    def create_admin(self, admin_data: dict) -> Optional[dict]:
        """Create a new admin user."""
        try:
            supabase = self.get_supabase_client(use_service_role=True)
            result = supabase.table('admin_users').insert(admin_data).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"[Database] Error creating admin: {str(e)}")
            return None
            
    def create_psychologist(self, psychologist_data: dict) -> Optional[dict]:
        """Create a new psychologist user."""
        try:
            supabase = self.get_supabase_client(use_service_role=True)
            result = supabase.table('psychologists').insert(psychologist_data).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"[Database] Error creating psychologist: {str(e)}")
            return None
            
    def delete_admin(self, admin_id: str) -> bool:
        """Delete an admin user."""
        try:
            supabase = self.get_supabase_client(use_service_role=True)
            result = supabase.table('admin_users').delete().eq('id', admin_id).execute()
            return True if result.data else False
        except Exception as e:
            print(f"[Database] Error deleting admin: {str(e)}")
            return False
            
    def delete_psychologist(self, psychologist_id: str) -> bool:
        """Delete a psychologist user."""
        try:
            supabase = self.get_supabase_client(use_service_role=True)
            result = supabase.table('psychologists').delete().eq('id', psychologist_id).execute()
            return True if result.data else False
        except Exception as e:
            print(f"[Database] Error deleting psychologist: {str(e)}")
            return False
            
    def delete_user(self, user_id: str) -> bool:
        """Delete a client."""
        try:
            supabase = self.get_supabase_client(use_service_role=True)
            result = supabase.table('clients').delete().eq('id', user_id).execute()
            return True if result.data else False
        except Exception as e:
            print(f"[Database] Error deleting client: {str(e)}")
            return False
            
    def get_psychologist_by_license(self, license_number: str) -> Optional[dict]:
        """Get a psychologist by license number."""
        try:
            supabase = self.get_supabase_client()
            result = supabase.table('psychologists').select('*').eq('license_number', license_number).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"[Database] Error getting psychologist by license: {str(e)}")
            return None
            
    # User Operations
    def get_user(self, username: str, use_service_role: bool = False) -> Optional[User]:
        """
        Fetch user by username.
        
        Args:
            username: The username to search for
            use_service_role: If True, uses the service role client (for authentication)
        """
        if not self.supabase:
            print("[Supabase] Not connected. Cannot fetch user.")
            return None
            
        try:
            client = self._get_client(use_service_role)
            response = client.table('clients').select('*').eq('username', username).execute()
            
            if not response.data:
                return None
                
            return User.from_dict(response.data[0])
            
        except Exception as e:
            print(f"Error fetching user by username: {str(e)}")
            return None
    
    def _create_user_object(self, user_data: Dict[str, Any]) -> User:
        """
        Create a User object from dictionary data.
        
        Args:
            user_data: Dictionary containing user data
            
        Returns:
            User object
        """
        from models.user import User  # Import here to avoid circular imports
        return User(**user_data)
        
    def get_user_by_email(self, email: str, use_service_role: bool = False) -> Optional[User]:
        """
        Fetch user by email address.
        
        Args:
            email: The email address to search for
            use_service_role: If True, uses the service role client (for authentication)
        """
        if not self.supabase:
            print("[Supabase] Not connected. Cannot fetch user by email.")
            return None
            
        try:
            client = self._get_client(use_service_role)
            response = client.table('clients').select('*').eq('email', email).execute()
            if not response.data:
                print(f"[DEBUG] No user found with email: {email}")
                return None
            user_data = dict(response.data[0])
            print(f"[DEBUG] Found user in public.clients table: {user_data.get('email')}")
            # Ensure required fields are present
            user_data.setdefault('is_active', True)
            user_data.setdefault('is_verified', False)
            user_obj = User.from_dict(user_data)
            if user_obj:
                print(f"[DEBUG] Created user object from table: {user_obj.id}")
            return user_obj
        except Exception as e:
            return None
        except Exception as e:
            print(f"[ERROR] Error getting user by email: {str(e)}")
            return None
    
    def get_user_by_id(self, user_id: str, use_service_role: bool = False) -> Optional[User]:
        try:
            client = self._get_client(use_service_role)
            response = client.table('clients').select('*').eq('id', user_id).execute()
            if response.data:
                return User.from_dict(response.data[0])
            return None
        except Exception as e:
            print(f"[ERROR] Error getting user by ID: {str(e)}")
            return None
    
    def _get_client(self, use_service_role: bool = False):
        """Get the appropriate Supabase client based on permissions needed."""
        if not use_service_role:
            return self.supabase
            
        service_role_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
        if not service_role_key:
            raise ValueError("SUPABASE_SERVICE_ROLE_KEY not found in environment variables")
            
        return create_client(os.getenv('SUPABASE_URL'), service_role_key)
    
    def increment_failed_login_attempts(self, user_id: str, max_attempts: int = 5, lockout_minutes: int = 15) -> Optional[User]:
        """
        Increment the failed login attempts counter and lock the account if needed.
        
        Args:
            user_id: The ID of the user
            max_attempts: Maximum number of allowed failed attempts before lockout
            lockout_minutes: Number of minutes to lock the account for
            
        Returns:
            Updated User object or None if update failed
        """
        if not self.supabase:
            print("[Supabase] Not connected. Cannot update login attempts.")
            return None
            
        # Use service role client for updates that may bypass RLS
        client = self._get_client(use_service_role=True)
        try:
            # Get current user data
            user = self.get_user_by_id(user_id, use_service_role=True)
            if not user:
                print(f"[ERROR] User {user_id} not found when updating login attempts")
                return None
            
            # Increment failed attempts (if column exists)
            current_attempts = getattr(user, 'failed_login_attempts', 0) + 1
            update_data = {
                'updated_at': datetime.utcnow().isoformat()
            }
            
            # Only add failed_login_attempts if the column exists
            try:
                # Test if the column exists by doing a small update
                test_update = client.table('clients').update({'updated_at': datetime.utcnow().isoformat()}).eq('id', user_id).execute()
                if test_update:
                    update_data['failed_login_attempts'] = current_attempts
            except Exception:
                # Column doesn't exist, skip it
                pass
            
            # Lock account if max attempts reached
            if current_attempts >= max_attempts:
                lockout_until = datetime.utcnow() + timedelta(minutes=lockout_minutes)
                update_data['account_locked_until'] = lockout_until.isoformat()
                print(f"[SECURITY] Account {user_id} locked until {lockout_until} after {current_attempts} failed attempts")
            
            # Update the user record
            updated_user = self.update_user(user_id, update_data, use_service_role=True)
            if not updated_user:
                print(f"[ERROR] Failed to update login attempts for user {user_id}")
                return None
                
            return updated_user
            
        except Exception as e:
            print(f"[ERROR] Error updating login attempts: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
    
    def reset_failed_login_attempts(self, user_id: str) -> None:
        """Reset the failed login attempts counter for a user."""
        if not self.supabase:
            print("[Supabase] Not connected. Cannot update user.")
            return
            
        try:
            update_data = {
                'updated_at': datetime.utcnow().isoformat()
            }
            
            # Only add columns if they exist
            try:
                # Test if failed_login_attempts column exists
                test_update = self.supabase.table('clients').update({'updated_at': datetime.utcnow().isoformat()}).eq('id', user_id).execute()
                if test_update:
                    update_data['failed_login_attempts'] = 0
                    update_data['account_locked_until'] = None
            except Exception:
                # Columns don't exist, skip them
                pass
            
            self.update_user(user_id, update_data, use_service_role=True)
            
        except Exception as e:
            print(f"Error resetting failed login attempts: {str(e)}")
    
    def update_user(self, user_id: str, update_data: Dict[str, Any], use_service_role: bool = False) -> Optional[User]:
        """
        Update user data.
        
        Args:
            user_id: The ID of the user to update
            update_data: Dictionary of fields to update
            use_service_role: If True, uses the service role client (for authentication)
        """
        if not self.supabase:
            print("[Supabase] Not connected. Cannot update user.")
            return None
            
        try:
            client = self._get_client(use_service_role)
            
            # Always update the updated_at timestamp
            update_data['updated_at'] = datetime.utcnow().isoformat()
            
            # Convert datetime objects to ISO format strings
            for key, value in update_data.items():
                if hasattr(value, 'isoformat'):
                    update_data[key] = value.isoformat()
                
                # Convert boolean values to proper booleans
                if isinstance(value, str) and value.lower() in ('true', 'false'):
                    update_data[key] = value.lower() == 'true'
            
            print(f"[DEBUG] Updating user {user_id} with data: {update_data}")
            response = client.table('clients').update(update_data).eq('id', user_id).execute()
            
            if not response.data:
                print(f"[ERROR] No data returned when updating user {user_id}")
                return None
                
            updated_user = User.from_dict(response.data[0])
            print(f"[DEBUG] Updated user: {updated_user.__dict__}")
            return updated_user
            
        except Exception as e:
            print(f"Error updating user: {str(e)}")
            import traceback
            traceback.print_exc()
            return None

    def get_user_by_id(self, user_id: str, use_service_role: bool = False) -> Optional[User]:
        """
        Fetch user by UUID id (for Flask-Login user_loader, etc).
        
        Args:
            user_id: The user ID to search for
            use_service_role: If True, uses the service role client (for authentication)
        """
        if not self.supabase:
            print("[Supabase] Not connected. Cannot fetch user by id.")
            return None
            
        try:
            client = self._get_client(use_service_role)

            # Try to get user from Supabase Auth (by ID)
            try:
                auth_response = client.auth.admin.get_user_by_id(user_id)
                if getattr(auth_response, 'user', None):
                    user = auth_response.user
                    print(f"[DEBUG] Found user in Auth system by ID: {user.email}")
                    user_data = {
                        'id': user.id,
                        'email': user.email,
                        'username': (user.user_metadata or {}).get('username', (user.email or '').split('@')[0]),
                        'first_name': (user.user_metadata or {}).get('first_name'),
                        'last_name': (user.user_metadata or {}).get('last_name'),
                        'gender': (user.user_metadata or {}).get('gender'),
                        'birthdate': (user.user_metadata or {}).get('birthdate'),
                        'is_active': True,
                        'is_verified': getattr(user, 'email_confirmed_at', None) is not None,
                        'created_at': getattr(user, 'created_at', None)
                    }
                    user_obj = User.from_dict(user_data)
                    print(f"[DEBUG] Created user object from Auth by ID: {user_obj.id}")
                    return user_obj
            except Exception as auth_error:
                print(f"[DEBUG] Auth lookup by ID failed: {str(auth_error)}")

            # Fallback: public.users table by ID
            try:
                response = client.table('clients').select('*').eq('id', user_id).execute()
                if response.data and len(response.data) > 0:
                    user_data = response.data[0]
                    print(f"[DEBUG] Found user in public.users table by ID: {user_data.get('email')}")
                    user_obj = User.from_dict(user_data)
                    if user_obj:
                        print(f"[DEBUG] Created user object from table by ID: {user_obj.id}")
                        return user_obj
            except Exception as e_table:
                print(f"[DEBUG] Table lookup by ID failed: {str(e_table)}")

            print(f"[DEBUG] No user found with ID: {user_id}")
            return None
            
        except Exception as e:
            print(f"Error fetching user by id: {str(e)}")
            return None
            

    
    def create_user(self, user_data: Dict[str, Any]) -> Optional[User]:
        """
        Create a new user in the database using Supabase Auth.
        
        Args:
            user_data: Dictionary containing user data with at least 'email' and 'password' keys
            
        Returns:
            User object if successful, None otherwise
            
        Raises:
            ValueError: If required fields are missing or user already exists
            Exception: If there's an error during user creation
        """
        if not user_data or 'email' not in user_data or 'password' not in user_data:
            error_msg = "Missing required user data (email or password)"
            print(f"[ERROR] {error_msg}")
            raise ValueError(error_msg)
            
        try:
            email = user_data['email'].lower().strip()
            password = user_data['password']
            
            print(f"[DEBUG] Creating new user with email: {email}")
            
            # 1. First, check if user already exists
            existing_user = self.get_user_by_email(email)
            if existing_user:
                error_msg = "A user with this email already exists"
                print(f"[ERROR] {error_msg}")
                raise ValueError(error_msg)
            
            # 2. Hash the password before storing it
            from werkzeug.security import generate_password_hash
            hashed_password = generate_password_hash(password)
            
            # 3. Prepare user profile data
            username = user_data.get('username', '').strip() or email.split('@')[0]
            
            # Start with only the essential columns that should exist
            profile_data = {
                'email': email,
                'username': username,
                'password_hash': hashed_password
            }
            
            # Try to add optional columns one by one, testing if they exist
            optional_columns = {
                'first_name': user_data.get('first_name', '').strip() or None,
                'last_name': user_data.get('last_name', '').strip() or None,
                'gender': user_data.get('gender'),
                'birthdate': user_data.get('birthdate'),
                'created_at': user_data.get('created_at', datetime.now(timezone.utc).isoformat())
            }
            
            # Only add columns that have values
            for col, value in optional_columns.items():
                if value is not None:
                    profile_data[col] = value
            
            # 4. Use Supabase Auth to create the user (this bypasses RLS)
            client = self._get_client(use_service_role=True)
            
            # 5. Create user through Supabase Auth
            auth_response = client.auth.admin.create_user({
                'email': email,
                'password': password,
                'email_confirm': True,
                'user_metadata': {
                    'username': username,
                    'first_name': user_data.get('first_name'),
                    'last_name': user_data.get('last_name'),
                    'gender': user_data.get('gender'),
                    'birthdate': user_data.get('birthdate')
                }
            })
            
            if not auth_response.user:
                error_msg = "Failed to create user through Supabase Auth"
                print(f"[ERROR] {error_msg}")
                raise Exception(error_msg)
                
            # 6. Get the created user
            user_id = auth_response.user.id
            print(f"[DEBUG] User created successfully through Auth with ID: {user_id}")
            
            # 7. Create a User object with the auth user data
            user_data = {
                'id': user_id,
                'email': email,
                'username': username,
                'first_name': user_data.get('first_name'),
                'last_name': user_data.get('last_name'),
                'gender': user_data.get('gender'),
                'birthdate': user_data.get('birthdate'),
                'is_active': True,
                'is_verified': True,
                'created_at': user_data.get('created_at', datetime.now(timezone.utc).isoformat())
            }
            
            # 8. Also persist a profile row in public.clients (for app queries and joins)
            try:
                minimal_row = {
                    'id': user_id,
                    'email': email,
                    'username': username,
                    'password': hashed_password,  # Using password column as per the schema
                    'first_name': user_data.get('first_name'),
                    'last_name': user_data.get('last_name'),
                    'gender': user_data.get('gender'),
                    'birthdate': user_data.get('birthdate'),
                    'is_admin': False,
                    'created_at': user_data.get('created_at', datetime.now(timezone.utc).isoformat())
                }
                # Remove Nones to avoid column issues
                minimal_row = {k: v for k, v in minimal_row.items() if v is not None}
                # Use upsert to avoid duplicates if row already exists
                client.table('clients').upsert(minimal_row, on_conflict='id').execute()
                print(f"[DEBUG] Synced user to public.clients table: {email}")
            except Exception as sync_error:
                print(f"[WARNING] Could not sync to public.users: {str(sync_error)}")
            
            return self._create_user_object(user_data)
                
        except Exception as e:
            error_msg = str(e)
            print(f"[ERROR] Error in create_user: {error_msg}")
            
            # Provide more user-friendly error messages
            if 'unique' in error_msg.lower() or 'duplicate' in error_msg.lower():
                if 'email' in error_msg.lower():
                    error_msg = "A user with this email already exists. Please use a different email or log in."
                elif 'username' in error_msg.lower():
                    error_msg = "This username is already taken. Please choose a different one."
                else:
                    error_msg = "A user with these details already exists."
            elif 'rate limit' in error_msg.lower() or '429' in error_msg:
                error_msg = "Too many signup attempts. Please wait a moment and try again."
                
            # Clean up any partially created resources
            try:
                if 'user_id' in locals():
                    # Try to clean up any partially created user
                    self.supabase.auth.admin.delete_user(user_id)
                    print(f"[DEBUG] Cleaned up partially created user: {user_id}")
            except Exception as cleanup_error:
                print(f"[WARNING] Failed to clean up partially created user: {str(cleanup_error)}")
                
            raise Exception(error_msg)


    
    # Game Score Operations
    def save_game_score(self, score_data: Dict[str, Any]) -> Optional[GameScore]:
        if not self.supabase:
            print("[Supabase] Not connected. Cannot save game score.")
            return None
        # Handle both user_id and client_id for backward compatibility
        if 'user_id' in score_data and 'client_id' not in score_data:
            score_data['client_id'] = score_data.pop('user_id')
        score_data['created_at'] = datetime.utcnow().isoformat()
        try:
            response = self.supabase.table('game_scores').insert(score_data).execute()
            if not response.data:
                return None
            return GameScore.from_dict(response.data[0])
        except Exception as e:
            print(f"Error saving game score: {str(e)}")
            return None
    
    def get_user_scores(self, user_id: str, game_name: str = None) -> List[GameScore]:
        if not self.supabase:
            print("[Supabase] Not connected. Cannot fetch user scores.")
            return []
        try:
            query = self.supabase.table('game_scores').select('*').eq('client_id', user_id)
            if game_name:
                query = query.eq('game_name', game_name)
            response = query.order('created_at', desc=True).execute()
            return [GameScore.from_dict(score) for score in response.data]
        except Exception as e:
            print(f"Error fetching user scores: {str(e)}")
            return []
    
    def get_high_scores(self, game_name: str, limit: int = 10) -> List[GameScore]:
        if not self.supabase:
            print("[Supabase] Not connected. Cannot fetch high scores.")
            return []
        try:
            response = self.supabase.table('game_scores')\
                .select('*')\
                .eq('game_name', game_name)\
                .order('score', desc=True)\
                .limit(limit)\
                .execute()
            return [GameScore.from_dict(score) for score in response.data]
        except Exception as e:
            print(f"Error fetching high scores: {str(e)}")
            return []
    
    # Personality Test Operations
    def save_personality_test_result(self, test_data: Dict[str, Any]) -> Optional[PersonalityTestResult]:
        if not self.supabase:
            print("[Supabase] Not connected. Cannot save personality test result.")
            return None
        # Handle both user_id and client_id for backward compatibility
        if 'user_id' in test_data and 'client_id' not in test_data:
            test_data['client_id'] = test_data.pop('user_id')
        test_data['test_date'] = datetime.utcnow().isoformat()
        try:
            response = self.supabase.table('personality_tests').insert(test_data).execute()
            if not response.data:
                return None
            return PersonalityTestResult.from_dict(response.data[0])
        except Exception as e:
            print(f"Error saving personality test result: {str(e)}")
            return None
    
    def get_user_personality_tests(self, user_id: str) -> List[PersonalityTestResult]:
        if not self.supabase:
            print("[Supabase] Not connected. Cannot fetch user personality tests.")
            return []
        try:
            response = self.supabase.table('personality_tests')\
                .select('*')\
                .eq('client_id', user_id)\
                .order('test_date', desc=True)\
                .execute()
            return [PersonalityTestResult.from_dict(test) for test in response.data]
        except Exception as e:
            print(f"Error fetching user personality tests: {str(e)}")
            return []
        return [PersonalityTestResult.from_dict(test) for test in response.data]

    # Admin Operations
    def create_admin(self, admin_data: dict) -> Optional[str]:
        """Create a new admin user in the database with validation and error handling."""
        try:
            # Input validation
            if not admin_data or not isinstance(admin_data, dict):
                raise ValueError("Invalid admin data provided")
            
            required_fields = ['email', 'password']
            for field in required_fields:
                if not admin_data.get(field):
                    raise ValueError(f"Missing required field: {field}")
            
            # Email format validation
            import re
            email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_regex, admin_data['email']):
                raise ValueError("Invalid email format")
            
            # Password strength validation
            if len(admin_data['password']) < 8:
                raise ValueError("Password must be at least 8 characters long")
            
            client = self.get_supabase_client(use_service_role=True)
            if not client:
                raise ConnectionError("Failed to connect to the database")
            
            # Hash the password before storing
            from werkzeug.security import generate_password_hash
            hashed_password = generate_password_hash(admin_data['password'])
            
            # Prepare admin data
            admin_record = {
                'email': admin_data['email'].lower().strip(),
                'password_hash': hashed_password,
                'full_name': admin_data.get('full_name', '').strip() or None,
                'is_active': bool(admin_data.get('is_active', True)),
                'is_super_admin': bool(admin_data.get('is_super_admin', False))
            }
            
            # Insert new admin
            response = client.table('admin_users').insert(admin_record).execute()
            
            # Check response
            if not response.data:
                raise ValueError("No data returned from database")
                
            if isinstance(response.data, list):
                if not response.data:
                    raise ValueError("Empty response from database")
                created_admin = response.data[0]
            else:
                created_admin = response.data
            
            admin_id = created_admin.get('id')
            if not admin_id:
                raise ValueError("Failed to retrieve admin ID after creation")
                
            return str(admin_id)
                
        except Exception as e:
            error_msg = f"Failed to create admin: {str(e)}"
            print(error_msg)
            import traceback
            print(traceback.format_exc())
            if isinstance(e, ValueError):
                raise  # Re-raise validation errors
            raise Exception("An error occurred while creating the admin account")
    
    def get_admin_by_email(self, email: str) -> Optional[Admin]:
        """Fetch admin by email address."""
        if not self.supabase:
            print("[Supabase] Not connected. Cannot fetch admin by email.")
            return None
            
        try:
            response = self.supabase.table('admin_users')\
                .select('*')\
                .eq('email', email.lower().strip())\
                .execute()
                
            if not response.data or len(response.data) == 0:
                return None
                
            admin_data = response.data[0]
            return Admin(
                id=str(admin_data['id']),
                email=admin_data['email'],
                password_hash=admin_data['password_hash'],
                full_name=admin_data.get('full_name'),
                is_active=bool(admin_data.get('is_active', True)),
                is_super_admin=bool(admin_data.get('is_super_admin', False)),
                created_at=admin_data.get('created_at'),
                updated_at=admin_data.get('updated_at')
            )
            
        except Exception as e:
            print(f"Error fetching admin by email: {str(e)}")
            import traceback
            print(traceback.format_exc())
            return None
    
    def get_admin_by_id(self, admin_id: str) -> Optional[Admin]:
        """Fetch admin by ID."""
        if not self.supabase:
            print("[Supabase] Not connected. Cannot fetch admin by ID.")
            return None
            
        try:
            response = self.supabase.table('admin_users')\
                .select('*')\
                .eq('id', admin_id)\
                .execute()
                
            if not response.data or len(response.data) == 0:
                return None
                
            admin_data = response.data[0]
            return Admin(
                id=str(admin_data['id']),
                email=admin_data['email'],
                password_hash=admin_data['password_hash'],
                full_name=admin_data.get('full_name'),
                is_active=bool(admin_data.get('is_active', True)),
                is_super_admin=bool(admin_data.get('is_super_admin', False)),
                created_at=admin_data.get('created_at'),
                updated_at=admin_data.get('updated_at')
            )
            
        except Exception as e:
            print(f"Error fetching admin by ID: {str(e)}")
            import traceback
            print(traceback.format_exc())
            return None
            
    # Guidance Counselor Management Methods
    def get_guidance_counselor_by_id(self, counselor_id: str) -> Optional[dict]:
        """Get a guidance counselor by ID."""
        try:
            supabase = self.get_supabase_client()
            result = supabase.table('guidance_counselors').select('*').eq('id', counselor_id).execute()
            return result.data[0] if result.data and len(result.data) > 0 else None
        except Exception as e:
            print(f"[Database] Error getting guidance counselor: {str(e)}")
            return None
            
    def get_guidance_counselor_by_user_id(self, user_id: str) -> Optional[dict]:
        """Get a guidance counselor by user ID."""
        try:
            supabase = self.get_supabase_client()
            result = supabase.table('guidance_counselors').select('*').eq('user_id', user_id).execute()
            return result.data[0] if result.data and len(result.data) > 0 else None
        except Exception as e:
            print(f"[Database] Error getting guidance counselor by user ID: {str(e)}")
            return None
            
    def get_all_guidance_counselors(self) -> List[dict]:
        """Get all guidance counselors."""
        try:
            supabase = self.get_supabase_client()
            result = supabase.table('guidance_counselors').select('*').order('created_at', desc=True).execute()
            return result.data if result.data else []
        except Exception as e:
            print(f"[Database] Error getting all guidance counselors: {str(e)}")
            return []
            
    def create_guidance_counselor(self, counselor_data: dict) -> Optional[dict]:
        """Create a new guidance counselor."""
        try:
            supabase = self.get_supabase_client(use_service_role=True)
            
            # Add timestamps
            now = datetime.now(timezone.utc).isoformat()
            counselor_data.update({
                'created_at': now,
                'updated_at': now
            })
            
            result = supabase.table('guidance_counselors').insert(counselor_data).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"[Database] Error creating guidance counselor: {str(e)}")
            return None
            
    def update_guidance_counselor(self, counselor_id: str, update_data: dict) -> bool:
        """Update a guidance counselor."""
        try:
            supabase = self.get_supabase_client(use_service_role=True)
            
            # Update the updated_at timestamp
            update_data['updated_at'] = datetime.now(timezone.utc).isoformat()
            
            result = supabase.table('guidance_counselors').update(update_data).eq('id', counselor_id).execute()
            return True if result.data else False
        except Exception as e:
            print(f"[Database] Error updating guidance counselor: {str(e)}")
            return False
            
    def delete_guidance_counselor(self, counselor_id: str) -> bool:
        """Delete a guidance counselor."""
        try:
            supabase = self.get_supabase_client(use_service_role=True)
            result = supabase.table('guidance_counselors').delete().eq('id', counselor_id).execute()
            return True if result.data else False
        except Exception as e:
            print(f"[Database] Error deleting guidance counselor: {str(e)}")
            return False
# Singleton instance
db_service = DatabaseService()
