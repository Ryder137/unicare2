import os
from dotenv import load_dotenv
from supabase import create_client

def main():
    # Load environment variables
    load_dotenv()
    
    # Get Supabase credentials
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_SERVICE_KEY')
    
    if not all([supabase_url, supabase_key]):
        print("Error: Missing Supabase credentials in environment variables")
        return
    
    try:
        # Initialize Supabase client
        print("🔌 Connecting to Supabase...")
        supabase = create_client(supabase_url, supabase_key)
        
        # Fetch admin users
        print("\n📋 Fetching admin users...")
        response = supabase.table('admin_users').select('*').execute()
        
        # Get the data from the response
        admins = response.data if hasattr(response, 'data') else []
        
        if not admins:
            print("\n❌ No admin users found in the database.")
            return
        
        # Print admin users in a clean format
        print(f"\n✅ Found {len(admins)} admin users:")
        print("-" * 80)
        
        for i, admin in enumerate(admins, 1):
            print(f"\n👤 Admin #{i}")
            print("-" * 40)
            for key, value in admin.items():
                print(f"  {key}: {value}")
            
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
