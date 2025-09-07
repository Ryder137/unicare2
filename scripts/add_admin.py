import os
import sys
import uuid
from werkzeug.security import generate_password_hash
from supabase import create_client, Client
from dotenv import load_dotenv

def get_supabase_client(use_service_role=False):
    """Initialize and return a Supabase client.
    
    Args:
        use_service_role (bool): If True, use the service role key with bypass RLS
    """
    supabase_url = os.getenv('SUPABASE_URL')
    # Use service role key if specified, otherwise use anon key
    if use_service_role:
        supabase_key = os.getenv('SUPABASE_SERVICE_ROLE') or os.getenv('SUPABASE_KEY')
    else:
        supabase_key = os.getenv('SUPABASE_KEY')
    
    if not supabase_url or not supabase_key:
        raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in .env file")
    
    return create_client(supabase_url, supabase_key)

def add_admin_user(email: str, password: str, full_name: str, _=None):
    """
    Add an admin user to the admin_users table.
    
    Args:
        email (str): Admin's email address
        password (str): Plain text password (will be hashed)
        full_name (str): Admin's full name
        _: Kept for backward compatibility (unused)
    """
    try:
        # Initialize Supabase client with service role to bypass RLS
        supabase = get_supabase_client(use_service_role=True)
        
        # Check if user already exists
        existing_user = supabase.table('admin_users') \
            .select('*') \
            .eq('email', email) \
            .execute()
        
        if existing_user.data:
            print(f"[ERROR] Admin user with email {email} already exists")
            return False
        
        # Hash the password
        password_hash = generate_password_hash(password)
        
        # Create admin user with the correct schema
        admin_data = {
            'email': email,
            'password_hash': password_hash,
            'full_name': full_name.strip(),
            'is_active': True,
            'is_super_admin': False,  # Note: field name is is_super_admin (with underscore)
            'failed_login_attempts': 0
            # created_at and updated_at will be set automatically by the database
        }
        
        # Insert into admin_users table
        result = supabase.table('admin_users').insert(admin_data).execute()
        
        if hasattr(result, 'error') and result.error:
            print(f"[ERROR] Failed to add admin user: {result.error}")
            return False
        
        print(f"[SUCCESS] Admin user {email} created successfully!")
        return True
        
    except Exception as e:
        print(f"[ERROR] An error occurred: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python add_admin.py <email> <password> <full_name>")
        print("Example: python add_admin.py admin@example.com securepassword123 \"John Doe\"")
        sys.exit(1)
    
    load_dotenv()  # Load environment variables from .env file
    
    email = sys.argv[1]
    password = sys.argv[2]
    full_name = ' '.join(sys.argv[3:])  # Join remaining args as full name
    
    success = add_admin_user(email, password, full_name, "")  # Pass empty string as last_name
    sys.exit(0 if success else 1)
