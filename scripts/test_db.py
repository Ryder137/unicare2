import os
import psycopg2
from dotenv import load_dotenv

def test_db():
    print("🔍 Testing Database Connection...\n")
    
    # Load environment variables
    load_dotenv()
    db_url = os.getenv('DATABASE_URL')
    
    if not db_url:
        print("❌ Error: DATABASE_URL not found in .env file")
        return
    
    try:
        # Try to connect
        print("🔄 Attempting to connect to the database...")
        conn = psycopg2.connect(db_url)
        print("✅ Successfully connected to the database!")
        
        # Test a simple query
        print("\n🔍 Testing basic query...")
        cur = conn.cursor()
        cur.execute("SELECT version()")
        db_version = cur.fetchone()[0]
        print(f"✅ Database version: {db_version}")
        
        # Check if admin_users table exists
        print("\n🔍 Checking for admin_users table...")
        cur.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'admin_users'
            )
        """)
        table_exists = cur.fetchone()[0]
        
        if table_exists:
            print("✅ admin_users table exists")
            # Count admin users
            cur.execute("SELECT COUNT(*) FROM admin_users")
            count = cur.fetchone()[0]
            print(f"ℹ️ Found {count} admin users")
            
            # List admin users if any
            if count > 0:
                cur.execute("SELECT id, email, full_name, is_super_admin FROM admin_users")
                print("\n👥 Admin Users:")
                print("-" * 50)
                for user in cur.fetchall():
                    print(f"ID: {user[0]}")
                    print(f"Email: {user[1]}")
                    print(f"Name: {user[2]}")
                    print(f"Super Admin: {'✅' if user[3] else '❌'}")
                    print("-" * 50)
        else:
            print("❌ admin_users table does not exist")
            print("\nRun the setup_admin_table_structure.sql script first to create the table.")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        print("\nTroubleshooting:")
        print("1. Check your DATABASE_URL in .env")
        print("2. Verify your internet connection")
        print("3. Make sure your IP is whitelisted in Supabase")
        print("4. Check if your Supabase project is running")
    
    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()
            print("\n🔌 Database connection closed.")

if __name__ == "__main__":
    test_db()
