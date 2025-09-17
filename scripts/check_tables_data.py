import os
import sys
from dotenv import load_dotenv
from supabase import create_client
from pathlib import Path

def check_table_data(supabase, table_name, sample_count=3):
    """Check data in a specific table with detailed error reporting."""
    print(f"\n=== Checking table: {table_name} ===")
    
    # 1. Check if table exists and get row count
    try:
        count_result = supabase.table(table_name).select("*", count='exact').limit(1).execute()
        row_count = count_result.count if hasattr(count_result, 'count') else 'Unknown'
        print(f"Row count: {row_count}")
        
        if row_count == 0:
            print(f"[WARNING] Table '{table_name}' exists but is empty")
            return
            
    except Exception as e:
        print(f"[ERROR] Error accessing table '{table_name}': {str(e)}")
        return
    
    # 2. Try to fetch sample data
    try:
        print(f"\nSample data (first {min(sample_count, row_count)} rows):")
        result = supabase.table(table_name).select("*").limit(sample_count).execute()
        
        if hasattr(result, 'data') and result.data:
            for i, row in enumerate(result.data, 1):
                print(f"\nRow {i}:")
                for key, value in row.items():
                    print(f"  {key}: {value}")
        else:
            print("  No data returned (empty result)")
            
    except Exception as e:
        print(f"[ERROR] Error fetching data from '{table_name}': {str(e)}")

def main():
    print("\n[INFO] ====== Checking Database Tables Data ======")
    
    # Load environment variables
    env_path = Path(__file__).parent.parent / '.env'
    load_dotenv(env_path)
    
    # Get Supabase credentials
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_SERVICE_KEY')
    
    if not supabase_url or not supabase_key:
        print("[ERROR] Missing Supabase credentials in .env file")
        print("Please set SUPABASE_URL and SUPABASE_SERVICE_KEY")
        return
    
    try:
        # Initialize Supabase client with service role key
        print("[INFO] Initializing Supabase client...")
        supabase = create_client(supabase_url, supabase_key)
        
        # List of tables to check (add/remove as needed)
        tables_to_check = [
            'admin_users',
            'clients',
            'psychologists',
            'guidance_counselors',
            'users'  # If you have a users table
        ]
        
        # Check each table
        for table in tables_to_check:
            check_table_data(supabase, table)
        
        print("\n[INFO] Data check complete!")
        
    except Exception as e:
        print(f"[ERROR] Fatal error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
