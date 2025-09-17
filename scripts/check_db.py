import os
import sys
from dotenv import load_dotenv
from supabase import create_client, Client

def main():
    # Load environment variables
    load_dotenv()
    
    # Get Supabase URL and key from environment
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_SERVICE_KEY')
    
    print("Supabase URL:", supabase_url)
    print("Supabase Key:", "*" * 20 + supabase_key[-4:] if supabase_key else "Not set")
    
    if not supabase_url or not supabase_key:
        print("Error: Missing Supabase URL or Service Key in environment variables")
        return
    
    try:
        # Initialize the Supabase client
        print("\nConnecting to Supabase...")
        supabase: Client = create_client(supabase_url, supabase_key)
        
        # Test connection by fetching admin users
        print("\nFetching admin users...")
        result = supabase.table('admin_users').select('*').execute()
        
        print("\nRaw result:", result)
        
        if hasattr(result, 'data') and result.data:
            print(f"\nFound {len(result.data)} admin users:")
            for admin in result.data:
                print(f"- ID: {admin.get('id')}, Email: {admin.get('email')}, Name: {admin.get('first_name')} {admin.get('last_name')}")
        else:
            print("\nNo admin users found in the database.")
        
    except Exception as e:
        print(f"\nError: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
