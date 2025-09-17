import os
import sys
from dotenv import load_dotenv
from supabase import create_client
from pathlib import Path

def check_supabase_settings():
    print("\n[INFO] ====== Checking Supabase Settings ======")
    
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
        
        # Check if we can access the auth.users table
        print("\n[INFO] Testing auth.users table access...")
        try:
            # This is a protected table, so we need to use the admin API
            users = supabase.auth.admin.list_users()
            if hasattr(users, 'users'):
                print(f"[SUCCESS] Successfully accessed auth.users table")
                print(f"          Found {len(users.users)} users")
                
                if users.users:
                    print("\nFirst user:")
                    user = users.users[0]
                    print(f"  ID: {user.id}")
                    print(f"  Email: {user.email}")
                    print(f"  Created At: {user.created_at}")
            else:
                print("[WARNING] Unexpected response format from auth.users")
                print(f"          Response: {users}")
                
        except Exception as e:
            print(f"[ERROR] Failed to access auth.users: {str(e)}")
        
        # Check if we can access the public schema
        print("\n[INFO] Testing public schema access...")
        try:
            # Try to list all tables in the public schema
            query = """
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public';
            """
            
            print("\n[INFO] Executing SQL query to list tables...")
            result = supabase.rpc('pg_query', {'query': query}).execute()
            
            if hasattr(result, 'data') and result.data:
                print("\n[SUCCESS] Tables found in the public schema:")
                for row in result.data:
                    print(f"- {row.get('table_name', 'Unknown')}")
            else:
                print("\n[WARNING] No tables found or error fetching tables")
                print(f"Response: {result}")
                
        except Exception as e:
            print(f"\n[ERROR] Error executing query: {str(e)}")
        
        # Check RLS policies
        print("\n[INFO] Checking RLS policies...")
        try:
            # Get all RLS policies
            query = """
            SELECT tablename, policyname, roles, cmd, qual, with_check
            FROM pg_policies 
            WHERE schemaname = 'public';
            """
            
            print("\n[INFO] Executing SQL query to get RLS policies...")
            result = supabase.rpc('pg_query', {'query': query}).execute()
            
            if hasattr(result, 'data') and result.data:
                print("\n[SUCCESS] RLS policies found:")
                for policy in result.data:
                    print(f"\nTable: {policy.get('tablename')}")
                    print(f"  Policy: {policy.get('policyname')}")
                    print(f"  Roles: {policy.get('roles')}")
                    print(f"  Command: {policy.get('cmd')}")
                    print(f"  Using: {policy.get('qual') or 'No conditions'}")
                    print(f"  With Check: {policy.get('with_check') or 'No conditions'}")
            else:
                print("\n[WARNING] No RLS policies found or error fetching policies")
                print(f"Response: {result}")
                
        except Exception as e:
            print(f"\n[ERROR] Error getting RLS policies: {str(e)}")
        
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
    check_supabase_settings()
