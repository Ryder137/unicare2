"""
Admin Service
------------
This module provides admin-related services and utilities.
"""
from typing import Optional, List, Dict, Any
from werkzeug.security import generate_password_hash
from models import Admin
from services.database_service import db_service

def create_admin_user(email: str, password: str, full_name: str = None, is_super_admin: bool = False) -> Optional[Admin]:
    """
    Create a new admin user.
    
    Args:
        email: Admin's email address
        password: Plain text password (will be hashed)
        full_name: Admin's full name
        is_super_admin: Whether the admin has super admin privileges
        
    Returns:
        Admin: The created admin user or None if failed
    """
    try:
        # Check if admin with this email already exists
        existing_admin = db_service.get_admin_by_email(email)
        if existing_admin:
            print(f"[ERROR] Admin with email {email} already exists")
            return None
            
        # Create admin data
        admin_data = {
            'email': email.lower().strip(),
            'password_hash': generate_password_hash(password),
            'full_name': full_name.strip() if full_name else None,
            'is_super_admin': bool(is_super_admin),
            'is_active': True,
            'failed_login_attempts': 0
        }
        
        # Save to database
        admin_id = db_service.create_admin(admin_data)
        if not admin_id:
            print("[ERROR] Failed to create admin user in database")
            return None
            
        # Return the created admin
        return db_service.get_admin_by_id(admin_id)
        
    except Exception as e:
        print(f"[ERROR] Error in create_admin_user: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return None

def get_admin_user(admin_id: str) -> Optional[Admin]:
    """Get an admin user by ID."""
    return db_service.get_admin_by_id(admin_id)
    
def get_all_admins() -> List[Admin]:
    """Get all admin users."""
    return db_service.get_all_admins()
    
def update_admin_user(admin_id: str, update_data: Dict[str, Any]) -> bool:
    """
    Update an admin user's information.
    
    Args:
        admin_id: ID of the admin to update
        update_data: Dictionary of fields to update
        
    Returns:
        bool: True if update was successful, False otherwise
    """
    # Remove None values and password if it's empty
    update_data = {k: v for k, v in update_data.items() if v is not None}
    
    # Hash password if it's being updated
    if 'password' in update_data and update_data['password']:
        update_data['password_hash'] = generate_password_hash(update_data.pop('password'))
    
    return db_service.update_admin(admin_id, update_data)

def delete_admin_user(admin_id: str) -> bool:
    """
    Delete an admin user.
    
    Args:
        admin_id: ID of the admin to delete
        
    Returns:
        bool: True if deletion was successful, False otherwise
    """
    try:
        client = db_service.get_supabase_client(use_service_role=True)
        if not client:
            return False
            
        response = client.table('admin_users').delete().eq('id', admin_id).execute()
        return not (hasattr(response, 'error') and response.error)
        
    except Exception as e:
        print(f"[ERROR] Error deleting admin: {str(e)}")
        return False

def is_admin_user(user_id: str) -> bool:
    """Check if a user ID belongs to an admin."""
    return db_service.is_user_admin(user_id)
