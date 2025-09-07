import os
import psycopg2
from dotenv import load_dotenv

def main():
    print("🔍 Running minimal database test...")
    
    # Load environment variables
    load_dotenv()
    db_url = os.getenv('DATABASE_URL')
    
    if not db_url:
        print("❌ Error: DATABASE_URL not found in .env file")
        return
    
    # Mask password in the URL for security
    safe_url = db_url.split('@')[0] + '@' + db_url.split('@')[1] if '@' in db_url else db_url
    print(f"ℹ️ Using database URL: {safe_url}")
    
    try:
        print("\n🔄 Attempting to connect...")
        conn = psycopg2.connect(db_url)
        print("✅ Successfully connected to the database!")
        
        # Test a simple query
        cur = conn.cursor()
        cur.execute("SELECT 1")
        print("✅ Successfully executed a test query")
        
    except Exception as e:
        print(f"\n❌ Connection failed!")
        print(f"Error type: {type(e).__name__}")
        print(f"Error details: {str(e)}")
        
        # Provide specific troubleshooting based on error type
        if "connection to server" in str(e).lower():
            print("\nThis is a network-level connection issue. Please check:")
            print("1. Your internet connection")
            print("2. If the database server is running and accessible")
            print("3. If your IP is whitelisted in Supabase")
        elif "authentication failed" in str(e).lower():
            print("\nAuthentication failed. Please check:")
            print("1. Your database username and password in DATABASE_URL")
            print("2. If the database user has the correct permissions")
        else:
            print("\nPlease check your DATABASE_URL format and credentials.")
            
    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()
            print("\n🔌 Connection closed.")

if __name__ == "__main__":
    main()
