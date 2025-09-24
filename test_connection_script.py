import os
import sys
from dotenv import load_dotenv

print("🔍 Testing environment and database connection...")

# 1. Check Python version
print(f"\n🐍 Python version: {sys.version}")

# 2. Load environment variables
print("\n🔧 Loading environment variables...")
load_dotenv()

# 3. Check if required environment variables exist
required_vars = ['DATABASE_URL', 'SUPABASE_URL', 'SUPABASE_KEY']
missing_vars = [var for var in required_vars if not os.getenv(var)]

if missing_vars:
    print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
    print("Please check your .env file and make sure these variables are set.")
else:
    print("✅ All required environment variables are present")
    print(f"   DATABASE_URL: {'*' * 20}")
    print(f"   SUPABASE_URL: {os.getenv('SUPABASE_URL')}")
    print(f"   SUPABASE_KEY: {'*' * 20}")

# 4. Test database connection if DATABASE_URL is available
db_url = os.getenv('DATABASE_URL')
if db_url:
    print("\n🔌 Testing database connection...")
    try:
        from urllib.parse import urlparse
        parsed = urlparse(db_url)
        print(f"   Database type: {parsed.scheme}")
        print(f"   Host: {parsed.hostname}")
        print(f"   Port: {parsed.port}")
        print(f"   Database: {parsed.path[1:]}")
        
        # Test connection
        if 'postgresql' in db_url:
            try:
                import psycopg2
                conn = psycopg2.connect(db_url)
                cursor = conn.cursor()
                cursor.execute("SELECT version();")
                version = cursor.fetchone()
                print(f"✅ Successfully connected to PostgreSQL: {version[0]}")
                cursor.close()
                conn.close()
            except Exception as e:
                print(f"❌ Error connecting to PostgreSQL: {e}")
        else:
            print("⚠️  Only PostgreSQL connections are currently tested")
            
    except Exception as e:
        print(f"❌ Error parsing DATABASE_URL: {e}")
else:
    print("\n⚠️  No DATABASE_URL found, skipping database connection test")

print("\n🏁 Test completed")
