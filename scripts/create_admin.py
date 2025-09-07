#!/usr/bin/env python3
"""
Script to create the first admin user for the UniCare2 admin panel.
Run this script after setting up the database tables.
"""
import os
import sys
import bcrypt
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv()

def get_supabase_client() -> Client:
    """Initialize and return a Supabase client."""
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
    
    if not supabase_url or not supabase_key:
        print("Error: SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set in .env file")
        sys.exit(1)
        
    return create_client(supabase_url, supabase_key)

def hash_password(password: str) -> str:
    """Hash a password for storing in the database."""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def create_admin_user(email: str, password: str, full_name: str) -> None:
    """Create a new admin user in the database."""
    supabase = get_supabase_client()
    
    # Check if admin_users table exists
    try:
        result = supabase.table('admin_users').select('count', count='exact').execute()
    except Exception as e:
        print(f"Error: Could not access admin_users table. Make sure the tables are created. {e}")
        sys.exit(1)
    
    # Hash the password
    hashed_password = hash_password(password)
    
    # Create the admin user
    try:
        result = supabase.table('admin_users').insert({
            'email': email,
            'password_hash': hashed_password,
            'full_name': full_name,
            'is_active': True,
            'is_super_admin': True
        }).execute()
        
        if hasattr(result, 'error') and result.error:
            print(f"Error creating admin user: {result.error}")
            sys.exit(1)
            
        print(f"✅ Successfully created admin user: {email}")
        
    except Exception as e:
        print(f"Error creating admin user: {e}")
        sys.exit(1)

if __name__ == "__main__":
    print("=== Create Admin User ===\n")
    
    # Get user input
    email = input("Admin email: ").strip()
    password = input("Password: ").strip()
    confirm_password = input("Confirm password: ").strip()
    full_name = input("Full name: ").strip()
    
    # Validate input
    if not email or '@' not in email:
        print("Error: Please enter a valid email address")
        sys.exit(1)
        
    if not password or len(password) < 8:
        print("Error: Password must be at least 8 characters long")
        sys.exit(1)
        
    if password != confirm_password:
        print("Error: Passwords do not match")
        sys.exit(1)
    
    # Create the admin user
    create_admin_user(email, password, full_name)
