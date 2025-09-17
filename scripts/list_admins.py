import os
import json
from dotenv import load_dotenv
from supabase import create_client

def main():
    # Load environment variables
    load_dotenv()
    
    # Get Supabase URL and key from environment
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_SERVICE_KEY')
    
    if not supabase_url or not supabase_key:
        print("Error: Missing Supabase URL or Service Key in environment variables")
        return
    
    try:
        # Initialize the Supabase client
        print("Connecting to Supabase...")
        supabase = create_client(supabase_url, supabase_key)
        
        # Fetch admin users with all columns
        print("\nFetching admin users...")
        response = supabase.table('admin_users').select('*').execute()
        
        # Print the raw response for debugging
        print("\nRaw response:")
        print(json.dumps(response.__dict__, default=str, indent=2))
        
        # Check if we got data back
        if hasattr(response, 'data') and response.data:
            print(f"\nFound {len(response.data)} admin users:")
            for admin in response.data:
                print(f"\nAdmin ID: {admin.get('id')}")
                for key, value in admin.items():
                    print(f"  {key}: {value}")
        else:
            print("\nNo admin users found in the database.")
        
    except Exception as e:
        print(f"\nError: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
