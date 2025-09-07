import os
import sys
import psycopg2
from werkzeug.security import generate_password_hash
from dotenv import load_dotenv

def create_admin_user(email, password, full_name):
    """Create an admin user directly in the database."""
    load_dotenv()
    
    # Get database connection details from environment
    db_url = os.getenv('DATABASE_URL') or os.getenv('SUPABASE_DB_URL')
    if not db_url:
        print("Error: DATABASE_URL or SUPABASE_DB_URL must be set in .env")
        return False
        
    # Connect to the database
    conn = psycopg2.connect(db_url)
    cur = conn.cursor()
    
    # Check if user already exists
    cur.execute("SELECT id FROM admin_users WHERE email = %s", (email,))
    if cur.fetchone():
        print(f"[ERROR] Admin user with email {email} already exists")
        return False
    
    # Hash the password
    password_hash = generate_password_hash(password)
    
    # Insert the admin user
    cur.execute("""
        INSERT INTO admin_users (email, password_hash, full_name, is_active, is_super_admin)
        VALUES (%s, %s, %s, true, true)
        RETURNING id
    """, (email, password_hash, full_name))
