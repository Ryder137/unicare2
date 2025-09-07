import os
import sys
import psycopg2
from getpass import getpass
from dotenv import load_dotenv

def create_admin():
    print("=== Create Super Admin ===\n")
    
    # Load environment variables
    load_dotenv()
    
    # Get database URL
    db_url = os.getenv('DATABASE_URL')
    if not db_url:
        print("❌ Error: DATABASE_URL not found in .env file")
        return
    
    # Get admin details
    print("Enter admin details:")
    email = input("Email: ").strip()
    password = getpass("Password: ").strip()
    confirm_password = getpass("Confirm password: ").strip()
    full_name = input("Full name: ").strip()
    
    if password != confirm_password:
        print("❌ Error: Passwords do not match")
        return
    
    if len(password) < 8:
        print("❌ Error: Password must be at least 8 characters long")
        return
    
    try:
        # Connect to the database
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()
        
        # Check if user already exists
        cur.execute("SELECT id FROM auth.users WHERE email = %s", (email,))
        if cur.fetchone():
            print(f"❌ Error: User with email {email} already exists")
            return
        
        # Create auth user (this is a simplified version - in production, use Supabase Auth)
        from werkzeug.security import generate_password_hash
        hashed_password = generate_password_hash(password)
        
        # Insert into auth.users (this is a simplified example - use Supabase Auth in production)
        cur.execute("""
            INSERT INTO auth.users (
                instance_id, aud, email, encrypted_password, 
                email_confirmed_at, is_super_admin, 
                last_sign_in_at, created_at, updated_at, 
                raw_app_meta_data, raw_user_meta_data
            ) VALUES (
                '00000000-0000-0000-0000-000000000000', 'authenticated', %s, %s, 
                NOW(), true, 
                NOW(), NOW(), NOW(),
                '{"provider": "email", "providers": ["email"]}',
                '{"full_name": %s}'
            ) RETURNING id
        """, (email, hashed_password, full_name))
        
        user_id = cur.fetchone()[0]
        
        # Insert into admin_users
        cur.execute("""
            INSERT INTO admin_users (
                id, email, full_name, is_active, is_super_admin, created_at, updated_at
            ) VALUES (
                %s, %s, %s, true, true, NOW(), NOW()
            )
        """, (user_id, email, full_name))
        
        # Commit the transaction
        conn.commit()
        print("\n✅ Successfully created super admin user!")
        print(f"   Email: {email}")
        print(f"   User ID: {user_id}")
        
    except Exception as e:
        print(f"\n❌ Error creating admin user: {str(e)}")
        if 'conn' in locals():
            conn.rollback()
    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    create_admin()
