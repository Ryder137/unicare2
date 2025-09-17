from werkzeug.security import check_password_hash
from models import Psychologist, GuidanceCounselor, Client, Admin
from services.database_service import db_service

class AuthService:
    @staticmethod
    def authenticate_user(email: str, password: str, role: str):
        """
        Authenticate a user based on email, password, and role.
        
        Args:
            email (str): User's email
            password (str): User's password
            role (str): User's role (admin, psychologist, counselor, client)
            
        Returns:
            User: Authenticated user object if successful, None otherwise
        """
        try:
            user = None
            
            # Get user based on role
            if role == 'admin':
                user = db_service.get_admin_by_email(email)
            elif role == 'psychologist':
                user = db_service.get_psychologist_by_email(email)
            elif role == 'counselor':
                user = db_service.get_guidance_counselor_by_email(email)
            elif role == 'client':
                user = db_service.get_client_by_email(email)
            
            # Verify user exists and password is correct
            if user and check_password_hash(user.password_hash, password):
                # Update last login time
                user.last_login = datetime.utcnow()
                db_service.update_user(user.id, {'last_login': user.last_login})
                return user
                
            return None
            
        except Exception as e:
            print(f"[AUTH] Error authenticating user: {str(e)}")
            return None
    
    @staticmethod
    def get_user_by_id(user_id: str, role: str):
        """
        Get a user by ID and role.
        
        Args:
            user_id (str): User's ID
            role (str): User's role
            
        Returns:
            User: User object if found, None otherwise
        """
        try:
            if role == 'admin':
                return db_service.get_admin_by_id(user_id)
            elif role == 'psychologist':
                return db_service.get_psychologist_by_id(user_id)
            elif role == 'counselor':
                return db_service.get_guidance_counselor_by_id(user_id)
            elif role == 'client':
                return db_service.get_client_by_id(user_id)
            return None
        except Exception as e:
            print(f"[AUTH] Error getting user by ID: {str(e)}")
            return None

# Singleton instance
auth_service = AuthService()
