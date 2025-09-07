import os
import psycopg2
from dotenv import load_dotenv
from pathlib import Path

def test_db_connection():
    try:
        # Load environment variables
        env_path = Path(__file__).parent.parent / '.env'
        load_dotenv(env_path)
        
        # Get database URL from environment variables
        db_url = os.getenv('DATABASE_URL')
        if not db_url:
            print("❌ DATABASE_URL not found in environment variables")
            return False
            
        print("🔌 Testing database connection...")
        
        # Try to connect to the database
        conn = psycopg2.connect(db_url)
        cursor = conn.cursor()
        
        # Execute a simple query to test the connection
        cursor.execute("SELECT version();")
        db_version = cursor.fetchone()
        
        print(f"✅ Successfully connected to PostgreSQL {db_version[0]}")
        
        # Test if we can query the admin_users table
        try:
            cursor.execute("SELECT COUNT(*) FROM admin_users;")
            count = cursor.fetchone()[0]
            print(f"ℹ️ Found {count} admin users in the database")
        except Exception as e:
            print(f"⚠️ Could not query admin_users table: {str(e)}")
            print("   This might be normal if the table doesn't exist yet")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Failed to connect to the database: {str(e)}")
        return False

if __name__ == "__main__":
    test_db_connection()
