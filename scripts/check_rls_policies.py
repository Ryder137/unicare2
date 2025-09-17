import os
import sys
from dotenv import load_dotenv
from supabase import create_client
from pathlib import Path

def check_rls_policies():
    print("\n[INFO] ====== Checking Supabase RLS Policies ======")
    
    # Load environment variables
    env_path = Path(__file__).parent.parent / '.env'
    load_dotenv(env_path)
    
    # Get Supabase credentials - use service role key to bypass RLS
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_SERVICE_KEY')
    
    if not supabase_url or not supabase_key:
        print("[ERROR] Missing Supabase credentials in .env file")
        print("Please ensure these environment variables are set:")
        print("- SUPABASE_URL")
        print("- SUPABASE_SERVICE_KEY")
        return
    
    try:
        # Initialize Supabase client with service role key
        print("[INFO] Initializing Supabase client with service role key...")
        supabase = create_client(supabase_url, supabase_key)
        
        # Get list of all tables in the public schema
        print("\n[INFO] Fetching list of tables...")
        tables_query = """
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
        ORDER BY table_name;
        """
        
        try:
            result = supabase.rpc('pg_query', {'query': tables_query}).execute()
            
            if not hasattr(result, 'data') or not result.data:
                print("[ERROR] Could not fetch tables list")
                return
                
            tables = [row['table_name'] for row in result.data]
            print(f"[INFO] Found {len(tables)} tables in the database")
            
            # Check RLS policies for each table
            for table in tables:
                print(f"\n--- {table.upper()} ---")
                
                # Check if RLS is enabled
                rls_query = f"""
                SELECT relname, relrowsecurity, relforcerowsecurity
                FROM pg_class
                WHERE oid = '{table}'::regclass;
                """
                
                try:
                    rls_result = supabase.rpc('pg_query', {'query': rls_query}).execute()
                    if hasattr(rls_result, 'data') and rls_result.data:
                        rls_info = rls_result.data[0]
                        print(f"RLS Enabled: {'Yes' if rls_info.get('relrowsecurity') else 'No'}")
                        print(f"RLS Forced: {'Yes' if rls_info.get('relforcerowsecurity') else 'No'}")
                    
                    # Get RLS policies
                    policies_query = f"""
                    SELECT * FROM pg_policies 
                    WHERE tablename = '{table}'
                    ORDER BY policyname;
                    """
                    
                    policies_result = supabase.rpc('pg_query', {'query': policies_query}).execute()
                    if hasattr(policies_result, 'data') and policies_result.data:
                        print(f"RLS Policies ({len(policies_result.data)}):")
                        for policy in policies_result.data:
                            print(f"  - {policy.get('policyname')}")
                            print(f"    Command: {policy.get('cmd')}")
                            print(f"    Roles: {policy.get('roles')}")
                            print(f"    Using: {policy.get('qual') or 'None'}")
                            print(f"    With Check: {policy.get('with_check') or 'None'}")
                    else:
                        print("No RLS policies defined")
                        
                except Exception as e:
                    print(f"[ERROR] Error checking RLS for {table}: {str(e)}")
                
                # Try to fetch a row from the table
                try:
                    data = supabase.table(table).select("*").limit(1).execute()
                    if hasattr(data, 'data') and data.data:
                        print(f"Sample data: {data.data[0]}")
                    else:
                        print("No data returned (table may be empty or access denied)")
                except Exception as e:
                    print(f"[ERROR] Error fetching data from {table}: {str(e)}")
            
            print("\n[INFO] RLS policy check complete!")
            
        except Exception as e:
            print(f"[ERROR] Error executing query: {str(e)}")
            
    except Exception as e:
        print(f"[ERROR] Failed to connect to Supabase: {str(e)}")
        print("\nTroubleshooting tips:")
        print("1. Check your internet connection")
        print("2. Verify the SUPABASE_URL and SUPABASE_SERVICE_KEY in your .env file")
        print("3. Make sure your Supabase project is running and accessible")
        print("4. Check if your Supabase project has RLS enabled")

if __name__ == "__main__":
    check_rls_policies()
