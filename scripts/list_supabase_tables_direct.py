import os
import sys
from dotenv import load_dotenv
from supabase import create_client
from pathlib import Path

def list_supabase_tables():
    print("\n[INFO] ====== Listing Supabase Tables ======")
    
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
        
        # List all tables using the Supabase client
        print("\n[INFO] Fetching tables from Supabase...")
        
        # Method 1: Try to list tables using the information_schema
        try:
            # This query should work in most PostgreSQL databases
            query = """
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public';
            """
            
            print("\n[INFO] Executing SQL query to list tables...")
            result = supabase.rpc('pg_query', {'query': query}).execute()
            
            if hasattr(result, 'data') and result.data:
                print("\n[SUCCESS] Tables found in the database:")
                for row in result.data:
                    print(f"- {row.get('table_name', 'Unknown')}")
            else:
                print("\n[WARNING] No tables found or error fetching tables")
                print(f"Response: {result}")
                
        except Exception as e:
            print(f"\n[ERROR] Error executing query: {str(e)}")
            
        # Method 2: Try to fetch from known tables
        print("\n[INFO] Testing access to known tables...")
        
        known_tables = [
            'clients',
            'admin_users',
            'psychologists',
            'guidance_counselors',
            'users',
            'game_scores',
            'personality_test_results'
        ]
        
        for table in known_tables:
            try:
                print(f"\n[TEST] Testing access to table: {table}")
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
    list_supabase_tables()
