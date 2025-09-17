import os
import sys
from dotenv import load_dotenv
from supabase import create_client, Client
from pathlib import Path

def test_supabase_client():
    print("\n[INFO] ====== Testing Supabase Client ======")
    
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
        print("Please ensure these environment variables are set:")
        print("- SUPABASE_URL")
        print("- SUPABASE_KEY")
        return
    
    try:
        # Initialize Supabase client
        print("\n[INFO] Initializing Supabase client...")
        supabase: Client = create_client(supabase_url, supabase_key)
        
        # Test authentication
        print("\n[INFO] Testing authentication...")
        try:
            # This is a simple test to check if the client can make authenticated requests
            response = supabase.auth.get_user()
            if hasattr(response, 'user'):
                print(f"[SUCCESS] Authenticated as user: {response.user.email}")
            else:
                print("[WARNING] Not authenticated (this might be expected)")
        except Exception as auth_error:
            print(f"[WARNING] Authentication test failed (might be expected): {str(auth_error)}")
        
        # Test table access
        print("\n[INFO] Testing table access...")
        
        # List of tables to test
        tables_to_test = [
            'clients',
            'admin_users',
            'psychologists',
            'guidance_counselors',
            'users'  # This is the auth.users table in Supabase
        ]
        
        for table in tables_to_test:
            try:
                print(f"\n[TEST] Testing access to table: {table}")
                
                # Try to get a single record
                result = supabase.table(table).select("*").limit(1).execute()
                
                if hasattr(result, 'data') and result.data is not None:
                    count = len(result.data)
                    print(f"[SUCCESS] Successfully accessed table '{table}'")
                    print(f"         Found {count} records")
                    if count > 0:
                        print(f"         Sample data: {result.data[0]}")
                else:
                    print(f"[WARNING] Table '{table}' exists but returned no data")
                    print(f"          Response: {result}")
                    
            except Exception as e:
                print(f"[ERROR] Failed to access table '{table}': {str(e)}")
        
        # Test RPC functions if needed
        print("\n[INFO] Testing RPC functions...")
        try:
            # This is a simple RPC test - adjust based on your actual RPC functions
            result = supabase.rpc('version').execute()
            print(f"[SUCCESS] RPC test successful: {result}")
        except Exception as e:
            print(f"[WARNING] RPC test failed (might be expected): {str(e)}")
        
        print("\n[INFO] Testing complete!")
        
    except Exception as e:
        print(f"\n[ERROR] An error occurred: {str(e)}")
        print("\nTroubleshooting tips:")
        print("1. Verify your Supabase URL and key are correct")
        print("2. Check your internet connection")
        print("3. Ensure your Supabase project is running")
        print("4. Check if there are any CORS or network restrictions")
        print("5. Verify that the Supabase client is properly initialized")
        
        # Print the full error for debugging
        import traceback
        print("\nFull error traceback:")
        traceback.print_exc()

if __name__ == "__main__":
    test_supabase_client()
