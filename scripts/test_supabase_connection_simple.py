import os
import sys
from dotenv import load_dotenv
from supabase import create_client
from pathlib import Path

def test_supabase_connection():
    print("\n[INFO] ====== Testing Supabase Connection ======")
    
    # Load environment variables
    env_path = Path(__file__).parent.parent / '.env'
    load_dotenv(env_path)
    
    # Get Supabase credentials
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_KEY')
    
    print(f"[DEBUG] Supabase URL: {supabase_url}")
    print(f"[DEBUG] Supabase Key: {'*' * 8}{supabase_key[-4:] if supabase_key else ''}")
    
    if not supabase_url or not supabase_key:
        print("[ERROR] Missing Supabase credentials in .env file")
        return
    
    try:
        # Initialize Supabase client
        print("\n[INFO] Initializing Supabase client...")
        supabase = create_client(supabase_url, supabase_key)
        
        # Test connection by fetching version
        print("\n[INFO] Testing connection by fetching version...")
        try:
            # This is a simple query that should work on any PostgreSQL database
            result = supabase.rpc('version').execute()
            print(f"[SUCCESS] Successfully connected to Supabase")
            print(f"          Version: {result}")
            
            # Try to list tables using a direct query
            print("\n[INFO] Attempting to list tables...")
            try:
                # This query lists all tables in the public schema
                query = """
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public';
                """
                
                tables_result = supabase.rpc('pg_query', {'query': query}).execute()
                if hasattr(tables_result, 'data') and tables_result.data:
                    print("\n[SUCCESS] Tables found in the database:")
                    for row in tables_result.data:
                        print(f"- {row.get('table_name', 'Unknown')}")
                else:
                    print("\n[WARNING] No tables found or error fetching tables")
                    print(f"Response: {tables_result}")
                    
            except Exception as table_error:
                print(f"\n[ERROR] Error listing tables: {str(table_error)}")
            
        except Exception as version_error:
            print(f"\n[ERROR] Failed to get database version: {str(version_error)}")
            
        # Test authentication
        print("\n[INFO] Testing authentication...")
        try:
            # Try to get the current user
            user = supabase.auth.get_user()
            if hasattr(user, 'user') and user.user:
                print(f"[SUCCESS] Authenticated as user: {user.user.email}")
            else:
                print("[WARNING] Not authenticated (this might be expected)")
        except Exception as auth_error:
            print(f"[WARNING] Authentication test failed (might be expected): {str(auth_error)}")
        
        print("\n[INFO] Testing complete!")
        
    except Exception as e:
        print(f"\n[ERROR] Failed to connect to Supabase: {str(e)}")
        print("\nTroubleshooting tips:")
        print("1. Check your internet connection")
        print("2. Verify the SUPABASE_URL and SUPABASE_KEY in your .env file")
        print("3. Make sure your Supabase project is running and accessible")
        print("4. Check if there are any firewall restrictions")
        print("5. Verify that the Supabase client is properly initialized")

if __name__ == "__main__":
    test_supabase_connection()
