import os
from typing import List, Optional, Dict, Any
from datetime import datetime
from supabase import create_client, Client
from config import init_supabase
from models import User, GameScore, PersonalityTestResult

class DatabaseService:
    def __init__(self):
        try:
            self.supabase: Client = init_supabase()
            print("[Supabase] Connection initialized in DatabaseService")
        except Exception as e:
            print(f"[Supabase] ❌ Failed to initialize in DatabaseService: {str(e)}")
            self.supabase = None
    
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
            response = client.table('users').select('*').eq('username', username).execute()
            
            if not response.data:
                return None
                
            return User.from_dict(response.data[0])
            
        except Exception as e:
            print(f"Error fetching user by username: {str(e)}")
            return None
    
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
            response = client.table('users').select('*').eq('email', email).execute()
            
            if not response.data:
                return None
                
            return User.from_dict(response.data[0])
            
        except Exception as e:
            print(f"Error fetching user by email: {str(e)}")
            return None
    
    def get_user_by_id(self, user_id: str, use_service_role: bool = False) -> Optional[User]:
        """
        Fetch user by ID.
        
        Args:
            user_id: The user ID to search for
            use_service_role: If True, uses the service role client (for authentication)
        """
        if not self.supabase:
            print("[Supabase] Not connected. Cannot fetch user by ID.")
            return None
            
        try:
            client = self._get_client(use_service_role)
            response = client.table('users').select('*').eq('id', user_id).execute()
            
            if not response.data:
                return None
                
            return User.from_dict(response.data[0])
            
        except Exception as e:
            print(f"Error fetching user by ID: {str(e)}")
            return None
    
    def _get_client(self, use_service_role: bool = False):
        """Get the appropriate Supabase client based on permissions needed."""
        if not use_service_role:
            return self.supabase
            
        service_role_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
        if not service_role_key:
            raise ValueError("SUPABASE_SERVICE_ROLE_KEY not found in environment variables")
            
        return create_client(os.getenv('SUPABASE_URL'), service_role_key)
    
    def increment_failed_login_attempts(self, user_id: str) -> None:
        """Increment the failed login attempts counter for a user."""
        if not self.supabase:
            print("[Supabase] Not connected. Cannot update user.")
            return
            
        try:
            # Get current failed attempts
            user = self.get_user_by_id(user_id, use_service_role=True)
            if not user:
                return
                
            failed_attempts = user.failed_login_attempts + 1
            update_data = {
                'failed_login_attempts': failed_attempts,
                'updated_at': datetime.utcnow().isoformat()
            }
            
            # Lock account after 3 failed attempts for 15 minutes
            if failed_attempts >= 3:
                lockout_time = datetime.utcnow() + timedelta(minutes=15)
                update_data['account_locked_until'] = lockout_time.isoformat()
            
            self.update_user(user_id, update_data, use_service_role=True)
            
        except Exception as e:
            print(f"Error incrementing failed login attempts: {str(e)}")
    
    def reset_failed_login_attempts(self, user_id: str) -> None:
        """Reset the failed login attempts counter for a user."""
        if not self.supabase:
            print("[Supabase] Not connected. Cannot update user.")
            return
            
        try:
            update_data = {
                'failed_login_attempts': 0,
                'account_locked_until': None,
                'updated_at': datetime.utcnow().isoformat()
            }
            
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
            if 'updated_at' not in update_data:
                update_data['updated_at'] = datetime.utcnow().isoformat()
            
            # Convert datetime objects to ISO format strings
            for key, value in update_data.items():
                if hasattr(value, 'isoformat'):
                    update_data[key] = value.isoformat()
            
            response = client.table('users').update(update_data).eq('id', user_id).execute()
            
            if not response.data:
                return None
                
            return User.from_dict(response.data[0])
            
        except Exception as e:
            print(f"Error updating user: {str(e)}")
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
            client = self.supabase
            
            # Use service role client if requested
            if use_service_role:
                service_role_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
                if not service_role_key:
                    raise ValueError("SUPABASE_SERVICE_ROLE_KEY not found in environment variables")
                client = create_client(os.getenv('SUPABASE_URL'), service_role_key)
            
            # Perform the query
            response = client.table('users').select('*').eq('id', user_id).execute()
            
            if not response.data:
                return None
                
            return User.from_dict(response.data[0])
            
        except Exception as e:
            print(f"Error fetching user by id: {str(e)}")
            return None
            
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Fetch user by email address (for password reset, etc)."""
        if not self.supabase:
            print("[Supabase] Not connected. Cannot fetch user by email.")
            return None
        try:
            # Use service role client for password reset flow
            from config import init_supabase
            service_role_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
            if not service_role_key:
                raise ValueError("SUPABASE_SERVICE_ROLE_KEY not found in environment variables")
                
            # Create a client with service role for this operation
            service_client = create_client(os.getenv('SUPABASE_URL'), service_role_key)
            
            # Now query with service role
            response = service_client.table('users').select('*').eq('email', email).execute()
            
            if not response.data:
                return None
                
            # Return user data without sensitive information
            user_data = response.data[0]
            return User.from_dict(user_data)
            
        except Exception as e:
            print(f"Error fetching user by email: {str(e)}")
            return None
    
    def create_user(self, user_data: Dict[str, Any]) -> Optional[User]:
        if not self.supabase:
            print("[Supabase] Not connected. Cannot create user.")
            return None
        user_data['created_at'] = datetime.utcnow().isoformat()
        try:
            response = self.supabase.table('users').insert(user_data).execute()
            if not response.data:
                return None
            return User.from_dict(response.data[0])
        except Exception as e:
            print(f"Error creating user: {str(e)}")
            return None
    
    def update_user(self, user_id: str, update_data: Dict[str, Any], use_service_role: bool = False) -> Optional[User]:
        """
        Update a user's information.
        
        Args:
            user_id: The ID of the user to update
            update_data: Dictionary of fields to update
            use_service_role: If True, uses the service role client (for password resets)
        """
        if not self.supabase:
            print("[Supabase] Not connected. Cannot update user.")
            return None
            
        # Make a copy of update_data to avoid modifying the original
        data_to_update = update_data.copy()
        
        # Only add updated_at if the column exists in the table
        # We'll try to update without it first, and if it fails, we'll know the column doesn't exist
        
        try:
            client = self.supabase
            
            # Use service role client if requested
            if use_service_role:
                service_role_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
                if not service_role_key:
                    raise ValueError("SUPABASE_SERVICE_ROLE_KEY not found in environment variables")
                client = create_client(os.getenv('SUPABASE_URL'), service_role_key)
            
            # First, try without updated_at
            response = client.table('users').update(data_to_update).eq('id', user_id).execute()
            
            if not response.data:
                return None
                
            return User.from_dict(response.data[0])
            
        except Exception as e:
            # If the error is about the updated_at column, try again without it
            if 'updated_at' in str(e):
                try:
                    data_to_update.pop('updated_at', None)
                    response = client.table('users').update(data_to_update).eq('id', user_id).execute()
                    
                    if not response.data:
                        return None
                        
                    return User.from_dict(response.data[0])
                except Exception as retry_error:
                    print(f"Error updating user (retry failed): {str(retry_error)}")
                    return None
            else:
                print(f"Error updating user: {str(e)}")
                return None
    
    # Game Score Operations
    def save_game_score(self, score_data: Dict[str, Any]) -> Optional[GameScore]:
        if not self.supabase:
            print("[Supabase] Not connected. Cannot save game score.")
            return None
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
            query = self.supabase.table('game_scores').select('*').eq('user_id', user_id)
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
                .eq('user_id', user_id)\
                .order('test_date', desc=True)\
                .execute()
            return [PersonalityTestResult.from_dict(test) for test in response.data]
        except Exception as e:
            print(f"Error fetching user personality tests: {str(e)}")
            return []
        return [PersonalityTestResult.from_dict(test) for test in response.data]

# Singleton instance
db_service = DatabaseService()
