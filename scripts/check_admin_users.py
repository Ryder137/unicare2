import sys
import os
from dotenv import load_dotenv
from supabase import create_client

def main():
    # Load environment variables
    load_dotenv()
    
    # Get Supabase URL and key from environment
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_SERVICE_KEY')
    
    if not supabase_url or not supabase_key:
        print("❌ Error: Missing Supabase URL or Service Key in environment variables")
        print(f"SUPABASE_URL: {'Set' if supabase_url else 'Not set'}")
        print(f"SUPABASE_SERVICE_KEY: {'Set' if supabase_key else 'Not set'}")
        return
    
    try:
        # Initialize the Supabase client
        print("🔌 Connecting to Supabase...")
        supabase = create_client(supabase_url, supabase_key)
        
        # Test connection by fetching admin users
        print("\n🔍 Fetching admin users...")
        result = supabase.table('admin_users').select('*').execute()
        
        if hasattr(result, 'data') and result.data:
            print(f"\n✅ Found {len(result.data)} admin users:")
            for i, admin in enumerate(result.data, 1):
                print(f"\nAdmin #{i}:")
                for key, value in admin.items():
                    print(f"  {key}: {value}")
        else:
            print("\nℹ️ No admin users found in the database.")
            
        # Check if the table exists
        print("\n🔍 Checking if table exists...")
        try:
            tables = supabase.table('pg_tables').select('tablename').execute()
            table_names = [t['tablename'] for t in tables.data if 'tablename' in t]
            print("\n📋 Available tables:")
            for table in sorted(table_names):
                print(f"- {table}")
        except Exception as e:
            print(f"\n❌ Error listing tables: {str(e)}")
            
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
