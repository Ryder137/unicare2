import os
import sys
from dotenv import load_dotenv
from supabase import create_client, Client
from pathlib import Path

def verify_supabase_config():
    print("\n[INFO] ====== Verifying Supabase Configuration ======")
    
    # Load environment variables
    env_path = Path(__file__).parent.parent / '.env'
    load_dotenv(env_path)
    
    # Get Supabase credentials
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_KEY')
    service_role_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
    
    print(f"[DEBUG] Environment file: {env_path}")
    print(f"[DEBUG] SUPABASE_URL: {'Set' if supabase_url else 'Not set'}")
    print(f"[DEBUG] SUPABASE_KEY: {'Set' if supabase_key else 'Not set'}")
    print(f"[DEBUG] SUPABASE_SERVICE_ROLE_KEY: {'Set' if service_role_key else 'Not set'}")
    
    if not all([supabase_url, supabase_key, service_role_key]):
        print("\n[ERROR] Missing required Supabase credentials in .env file")
        print("Please ensure these environment variables are set:")
        print("- SUPABASE_URL: Your Supabase project URL")
        print("- SUPABASE_KEY: Your Supabase anon/public key")
        print("- SUPABASE_SERVICE_ROLE_KEY: Your Supabase service role key (bypasses RLS)")
        return
    
    print("\n[SUCCESS] All required Supabase environment variables are set")
    
    # Test Supabase client initialization
    print("\n[INFO] Testing Supabase client initialization...")
    try:
        # Initialize regular client
        supabase = create_client(supabase_url, supabase_key)
        print("[SUCCESS] Regular Supabase client initialized successfully")
        
        # Initialize service role client
        supabase_admin = create_client(supabase_url, service_role_key)
        print("[SUCCESS] Service role Supabase client initialized successfully")
        
        # Test a simple query
        print("\n[INFO] Testing database query...")
        try:
            # Try to get the first 5 users from the auth.users table
            print("[TEST] Attempting to query auth.users table...")
            result = supabase_admin.auth.admin.list_users()
            
            if hasattr(result, 'users'):
                user_count = len(result.users)
                print(f"[SUCCESS] Successfully queried auth.users table")
                print(f"          Found {user_count} users in the database")
                
                if user_count > 0:
                    print("\nFirst user details:")
                    user = result.users[0]
                    print(f"  ID: {user.id}")
                    print(f"  Email: {user.email}")
                    print(f"  Created At: {user.created_at}")
                    print(f"  Last Sign In: {user.last_sign_in_at}")
            else:
                print("[WARNING] Unexpected response format from auth.users")
                print(f"          Response: {result}")
                
        except Exception as query_error:
            print(f"[ERROR] Failed to query auth.users: {str(query_error)}")
            print("\nTrying alternative query to public tables...")
            
            try:
                # Try to query a public table
                print("[TEST] Attempting to query public.clients table...")
                result = supabase.table('clients').select('*').limit(1).execute()
                
                if hasattr(result, 'data'):
                    count = len(result.data) if result.data else 0
                    print(f"[SUCCESS] Successfully queried public.clients table")
                    print(f"          Found {count} records")
                    
                    if count > 0:
                        print("\nFirst client record:")
                        for key, value in result.data[0].items():
                            print(f"  {key}: {value}")
                else:
                    print("[WARNING] Unexpected response format from public.clients")
                    print(f"          Response: {result}")
                    
            except Exception as table_error:
                print(f"[ERROR] Failed to query public.clients: {str(table_error)}")
                print("\nPlease check:")
                print("1. Your Supabase project is running")
                print("2. The tables exist in your database")
                print("3. Your RLS policies allow access")
                print("4. Your service role key has the correct permissions")
    
    except Exception as e:
        print(f"\n[ERROR] Failed to initialize Supabase client: {str(e)}")
        print("\nTroubleshooting steps:")
        print("1. Verify your Supabase URL is correct")
        print("2. Check that your API keys are valid")
        print("3. Ensure your Supabase project is running")
        print("4. Check your internet connection")
        print("5. Verify there are no typos in your .env file")

if __name__ == "__main__":
    verify_supabase_config()
