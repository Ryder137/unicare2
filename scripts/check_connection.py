import os
import psycopg2
from dotenv import load_dotenv

def check_connection():
    print("🔍 Checking database connection...\n")
    
    # Load environment variables
    load_dotenv()
    db_url = os.getenv('DATABASE_URL')
    
    if not db_url:
        print("❌ Error: DATABASE_URL not found in .env file")
        return False
    
    try:
        # Try to connect to the database
        print(f"Connecting to database...")
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()
        
        # Test connection with a simple query
        print("✅ Successfully connected to the database")
        
        # Check if admin_users table exists and count records
        try:
            cur.execute("SELECT COUNT(*) FROM admin_users")
            count = cur.fetchone()[0]
            print(f"ℹ️ Found {count} admin users in the database")
            
            # List all admin users
            if count > 0:
                print("\nAdmin Users:")
                print("------------")
                cur.execute("SELECT id, email, full_name, is_super_admin FROM admin_users")
                for user in cur.fetchall():
                    print(f"ID: {user[0]}")
                    print(f"Email: {user[1]}")
                    print(f"Name: {user[2]}")
                    print(f"Is Super Admin: {user[3]}")
                    print("------------")
        except Exception as e:
            print(f"⚠️ Could not query admin_users table: {str(e)}")
            print("   This might be normal if the table doesn't exist yet")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to connect to the database: {str(e)}")
        print("\nTroubleshooting steps:")
        print("1. Check if your DATABASE_URL in .env is correct")
        print("2. Verify your internet connection")
        print("3. Make sure your IP is whitelisted in Supabase")
        print("4. Check if your Supabase project is running")
        return False
    
    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    check_connection()
