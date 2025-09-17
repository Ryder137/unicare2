import os
from dotenv import load_dotenv
from supabase import create_client
from pathlib import Path

def test_connection():
    print("\n[INFO] ====== Testing Supabase Connection ======")
    
    # Load environment variables
    env_path = Path(__file__).parent.parent / '.env'
    load_dotenv(env_path)
    
    # Get Supabase credentials
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_KEY')
    
    if not supabase_url or not supabase_key:
        print("[ERROR] Missing Supabase credentials in .env file")
        print("Please ensure these environment variables are set:")
        print("- SUPABASE_URL")
        print("- SUPABASE_KEY")
        return
    
    try:
        # Initialize Supabase client
        print(f"[INFO] Connecting to Supabase at: {supabase_url}")
        supabase = create_client(supabase_url, supabase_key)
        
        # Test connection with a simple query
        print("\n[INFO] Testing connection with a simple query...")
        
        # Try to get server version
        try:
            result = supabase.rpc('version').execute()
            print(f"[SUCCESS] Connected to Supabase!")
            print(f"Server response: {result}")
            return True
        except Exception as e:
            print(f"[ERROR] Error executing version query: {str(e)}")
            
        # If version query failed, try a different approach
        print("\n[INFO] Trying alternative connection method...")
        
        try:
            # Try to list tables using information_schema
            query = "SELECT current_database() as db_name, current_user as user, version() as version;"
            result = supabase.rpc('pg_query', {'query': query}).execute()
            
            if hasattr(result, 'data') and result.data:
                db_info = result.data[0]
                print("\n[SUCCESS] Database connection details:")
                print(f"- Database: {db_info.get('db_name')}")
                print(f"- User: {db_info.get('user')}")
                print(f"- Version: {db_info.get('version')}")
                return True
            else:
                print("[ERROR] Could not get database information")
                
        except Exception as e:
            print(f"[ERROR] Error connecting to database: {str(e)}")
            
    except Exception as e:
        print(f"[ERROR] Failed to connect to Supabase: {str(e)}")
        
    print("\n[INFO] Connection test complete")
    return False

if __name__ == "__main__":
    test_connection()
