import os
import sys
from dotenv import load_dotenv
from supabase import create_client, Client

def check_supabase_tables():
    """Check Supabase connection and list all tables with row counts."""
    print("\n[INFO] ====== Checking Supabase Connection and Tables ======")
    
    # Load environment variables
    load_dotenv()
    
    # Get Supabase credentials
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
    
    if not supabase_url or not supabase_key:
        print("[ERROR] Missing Supabase credentials in .env file")
        print("Make sure SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY are set")
        return
    
    try:
        # Initialize Supabase client
        print("[INFO] Initializing Supabase client...")
        supabase: Client = create_client(supabase_url, supabase_key)
        
        # Test connection by fetching tables
        print("\n[INFO] Fetching tables from Supabase...")
        
        # Get all tables using the information_schema
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
                print(f"\n[SUCCESS] Found {len(tables)} tables in Supabase:")
                
                # Get row count for each table
                for table in tables:
                    try:
                        count = supabase.table(table).select("*", count='exact').execute()
                        row_count = count.count if hasattr(count, 'count') else 'N/A'
                        print(f"- {table}: {row_count} rows")
                    except Exception as e:
                        print(f"- {table}: Error counting rows - {str(e)}")
                
                # Check if clients table exists
                if 'clients' not in tables:
                    print("\n[WARNING] 'clients' table not found in the database!")
                else:
                    # Check clients table structure
                    print("\n[INFO] Checking 'clients' table structure...")
                    try:
                        columns_query = """
                        SELECT column_name, data_type, is_nullable
                        FROM information_schema.columns
                        WHERE table_name = 'clients';
                        """
                        
                        columns_result = supabase.rpc('pg_query', {'query': columns_query}).execute()
                        if hasattr(columns_result, 'data') and columns_result.data:
                            print("\n[SUCCESS] 'clients' table columns:")
                            for col in columns_result.data:
                                print(f"- {col['column_name']} ({col['data_type']}) {'NULL' if col['is_nullable'] == 'YES' else 'NOT NULL'}")
                        
                        # Check RLS policies for clients table
                        policies_query = """
                        SELECT * FROM pg_policies 
                        WHERE tablename = 'clients';
                        """
                        policies_result = supabase.rpc('pg_query', {'query': policies_query}).execute()
                        if hasattr(policies_result, 'data') and policies_result.data:
                            print("\n[SUCCESS] RLS Policies for 'clients' table:")
                            for policy in policies_result.data:
                                print(f"- {policy['policyname']}: {policy['cmd']} - {policy['qual'] or 'No conditions'}")
                        else:
                            print("\n[WARNING] No RLS policies found for 'clients' table")
                        
                    except Exception as e:
                        print(f"[ERROR] Error checking 'clients' table structure: {str(e)}")
                        
            else:
                print("[ERROR] No tables found or error fetching tables")
                print(f"Response: {result}")
                
        except Exception as e:
            print(f"[ERROR] Error executing query: {str(e)}")
            
    except Exception as e:
        print(f"[ERROR] Failed to connect to Supabase: {str(e)}")
        print("Please check your Supabase URL and service role key")

if __name__ == "__main__":
    check_supabase_tables()
