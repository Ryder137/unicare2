import os
import sys
from dotenv import load_dotenv
from supabase import create_client
from pathlib import Path

def test_supabase_tables():
    print("\n[INFO] ====== Testing Supabase Tables ======")
    
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
        print("[INFO] Initializing Supabase client...")
        supabase = create_client(supabase_url, supabase_key)
        
        # Test connection by fetching tables
        print("\n[INFO] Testing connection by fetching tables...")
        
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
            print("\nTrying alternative method...")
            
            # Method 2: Try to fetch from a known table
            try:
                print("\n[INFO] Trying to fetch from 'clients' table...")
                result = supabase.table('clients').select("*").limit(1).execute()
                print(f"[SUCCESS] Successfully connected to 'clients' table")
                print(f"Data sample: {result.data[:1] if hasattr(result, 'data') else 'No data'}")
                
            except Exception as e2:
                print(f"[ERROR] Could not fetch from 'clients' table: {str(e2)}")
                
                # Method 3: List all tables using the Supabase REST API
                try:
                    print("\n[INFO] Trying to list tables using REST API...")
                    rest_url = f"{supabase_url}/rest/v1/"
                    import requests
                    response = requests.get(rest_url, headers={
                        'apikey': supabase_key,
                        'Authorization': f'Bearer {supabase_key}'
                    })
                    print(f"REST API Status Code: {response.status_code}")
                    print(f"Response: {response.text[:500]}...")
                    
                except Exception as e3:
                    print(f"[ERROR] REST API request failed: {str(e3)}")
        
        print("\n[INFO] Testing complete!")
        
    except Exception as e:
        print(f"\n[ERROR] Failed to connect to Supabase: {str(e)}")
        print("\nTroubleshooting tips:")
        print("1. Check your internet connection")
        print("2. Verify the SUPABASE_URL and SUPABASE_KEY in your .env file")
        print("3. Make sure your Supabase project is running and accessible")
        print("4. Check if there are any firewall restrictions")
        print("5. Verify that the Supabase project has the required tables")

if __name__ == "__main__":
    test_supabase_tables()
