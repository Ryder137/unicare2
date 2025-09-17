import os
import sys
from dotenv import load_dotenv
from supabase import create_client
from pathlib import Path

def check_database_structure():
    print("\n[INFO] ====== Checking Database Structure ======")
    
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
        # Initialize Supabase client with service role key for admin access
        print("[INFO] Initializing Supabase client...")
        supabase = create_client(supabase_url, supabase_key)
        
        # List all tables in the public schema
        print("\n[INFO] Fetching list of tables...")
        
        # Get all tables using SQL query through RPC
        query = """
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
        ORDER BY table_name;
        """
        
        try:
            result = supabase.rpc('pg_query', {'query': query}).execute()
            
            if hasattr(result, 'data') and result.data:
                tables = [row['table_name'] for row in result.data]
                print(f"\n[SUCCESS] Found {len(tables)} tables in the database:")
                
                # Get row count and structure for each table
                for table in tables:
                    print(f"\n--- {table} ---")
                    
                    # Get row count
                    try:
                        count_result = supabase.table(table).select("*", count='exact').limit(1).execute()
                        row_count = count_result.count if hasattr(count_result, 'count') else 'N/A'
                        print(f"Rows: {row_count}")
                    except Exception as e:
                        print(f"Error getting row count: {str(e)}")
                    
                    # Get table structure
                    try:
                        columns_query = f"""
                        SELECT column_name, data_type, is_nullable, column_default
                        FROM information_schema.columns
                        WHERE table_name = '{table}'
                        ORDER BY ordinal_position;
                        """
                        
                        columns_result = supabase.rpc('pg_query', {'query': columns_query}).execute()
                        if hasattr(columns_result, 'data') and columns_result.data:
                            print("Columns:")
                            for col in columns_result.data:
                                default = f" DEFAULT {col['column_default']}" if col['column_default'] else ''
                                nullable = 'NULL' if col['is_nullable'] == 'YES' else 'NOT NULL'
                                print(f"  - {col['column_name']} ({col['data_type']}) {nullable}{default}")
                        
                        # Check RLS policies
                        policies_query = f"""
                        SELECT * FROM pg_policies 
                        WHERE tablename = '{table}';
                        """
                        policies_result = supabase.rpc('pg_query', {'query': policies_query}).execute()
                        if hasattr(policies_result, 'data') and policies_result.data:
                            print("\n  RLS Policies:")
                            for policy in policies_result.data:
                                print(f"  - {policy['policyname']}: {policy['cmd']} - {policy['qual'] or 'No conditions'}")
                        
                    except Exception as e:
                        print(f"  Error getting table structure: {str(e)}")
                        
            else:
                print("[ERROR] No tables found or error fetching tables")
                print(f"Response: {result}")
                
        except Exception as e:
            print(f"[ERROR] Error executing query: {str(e)}")
            
    except Exception as e:
        print(f"[ERROR] Failed to connect to Supabase: {str(e)}")
        print("Please check your Supabase URL and service role key")

if __name__ == "__main__":
    check_database_structure()
