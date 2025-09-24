import os
import sys
from dotenv import load_dotenv
import psycopg2
from psycopg2 import sql

def apply_migration():
    # Load environment variables
    load_dotenv()
    
    # Get database URL from environment
    db_url = os.getenv('DATABASE_URL')
    if not db_url:
        print("❌ Error: DATABASE_URL not found in environment variables")
        return False
    
    try:
        # Read the migration SQL file
        with open('migrations/fix_guidance_counselors_function.sql', 'r') as f:
            sql_script = f.read()
        
        # Connect to the database
        print("🔌 Connecting to the database...")
        conn = psycopg2.connect(db_url)
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Execute the migration
        print("🔄 Applying migration...")
        cursor.execute(sql_script)
        
        # Verify the function was created
        cursor.execute("""
            SELECT proname 
            FROM pg_proc 
            WHERE proname = 'get_guidance_counselors_with_users'
        """)
        
        if cursor.fetchone():
            print("✅ Migration applied successfully!")
            return True
        else:
            print("❌ Failed to verify the function was created")
            return False
            
    except Exception as e:
        print(f"❌ Error applying migration: {e}")
        return False
    finally:
        if 'conn' in locals():
            cursor.close()
            conn.close()

if __name__ == "__main__":
    if apply_migration():
        sys.exit(0)
    else:
        sys.exit(1)
