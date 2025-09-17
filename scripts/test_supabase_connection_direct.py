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
        
        # Test connection by fetching tables
        print("\n[INFO] Fetching tables from Supabase...")
        
        # List all tables using SQL query
        query = """
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public';
        """
        
        try:
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
            
    except Exception as e:
        print(f"\n[ERROR] Failed to connect to Supabase: {str(e)}")

if __name__ == "__main__":
    test_supabase_connection()
