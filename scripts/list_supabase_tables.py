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
    
    if not supabase_url or not supabase_key:
        print("[ERROR] Missing Supabase credentials in .env file")
        print("Please ensure these environment variables are set:")
        print("- SUPABASE_URL")
        print("- SUPABASE_KEY")
        print("- SUPABASE_SERVICE_ROLE_KEY (for admin operations)")
        return
    
    try:
        # Initialize Supabase client
        print("[INFO] Initializing Supabase client...")
        supabase = create_client(supabase_url, supabase_key)
        
        # Test connection by fetching tables
        print("\n[INFO] Fetching tables from Supabase...")
        
        # Method 1: Try using the tables() method if available
        try:
            tables = supabase.table('pg_tables').select('tablename').execute()
            if hasattr(tables, 'data') and tables.data:
                print("\n[SUCCESS] Tables found (method 1):")
                for table in tables.data:
                    print(f"- {table.get('tablename', 'Unknown')}")
                return
        except Exception as e:
            print("[INFO] Method 1 failed, trying alternative method...")
        
        # Method 2: Try using raw SQL query
        try:
            query = """
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public';
            """
            result = supabase.rpc('pg_query', {'query': query}).execute()
            
            if hasattr(result, 'data') and result.data:
                print("\n[SUCCESS] Tables found (method 2):")
                for row in result.data:
                    print(f"- {row.get('table_name', 'Unknown')}")
            else:
                print("[WARNING] No tables found or error fetching tables")
                
        except Exception as e:
            print(f"[ERROR] Error executing query: {str(e)}")
            
    except Exception as e:
        print(f"[ERROR] Failed to connect to Supabase: {str(e)}")
        print("Please check your Supabase URL and API key")

if __name__ == "__main__":
    list_supabase_tables()
