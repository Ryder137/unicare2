import os
import sys
import psycopg2
from getpass import getpass
from werkzeug.security import generate_password_hash
from dotenv import load_dotenv

def setup_admin():
    print("🔒 Secure Admin Setup 🔒\n")
    
    # Load environment variables
    load_dotenv()
    db_url = os.getenv('DATABASE_URL')
    
    if not db_url:
        print("❌ Error: DATABASE_URL not found in .env file")
        return
    
    try:
        # Get admin details
        print("Enter admin details:")
        email = input("📧 Email: ").strip()
        password = getpass("🔑 Password (hidden input): ").strip()
        confirm_password = getpass("🔑 Confirm password: ").strip()
        full_name = input("👤 Full name: ").strip()
        
        if password != confirm_password:
            print("❌ Error: Passwords do not match")
            return
            
        if len(password) < 8:
            print("❌ Error: Password must be at least 8 characters long")
            return
        
        # Hash the password
        hashed_password = generate_password_hash(password)
        
        # Connect to database
        print("\n🔌 Connecting to database...")
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()
        
        # Check if admin_users table exists
        cur.execute("""
            CREATE TABLE IF NOT EXISTS admin_users (
                id SERIAL PRIMARY KEY,
                email VARCHAR(255) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                full_name VARCHAR(255),
                is_active BOOLEAN DEFAULT true,
                is_super_admin BOOLEAN DEFAULT false,
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW()
            )
        """)
        
        # Check if user already exists
        cur.execute("SELECT id FROM admin_users WHERE email = %s", (email,))
        if cur.fetchone():
            print(f"\n❌ Error: Admin with email {email} already exists")
            return
        
        # Insert new admin user
        cur.execute("""
            INSERT INTO admin_users (email, password_hash, full_name, is_super_admin)
            VALUES (%s, %s, %s, %s)
            RETURNING id
        """, (email, hashed_password, full_name, True))
        
        user_id = cur.fetchone()[0]
        conn.commit()
        
        print("\n✅ Admin user created successfully!")
        print(f"   User ID: {user_id}")
        print(f"   Email: {email}")
        print("\n🔒 Please keep these credentials secure!")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        if 'conn' in locals():
            conn.rollback()
    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    setup_admin()
