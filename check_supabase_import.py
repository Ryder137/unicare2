import sys
import os
from dotenv import load_dotenv

def check_supabase():
    print("=== Supabase Import Test ===\n")
    
    # Load environment variables
    load_dotenv()
    
    # Check if Supabase is installed
    try:
        import supabase
        print("✅ supabase package is installed")
    except ImportError:
        print("❌ supabase package is not installed. Please install it with:")
        print("pip install supabase")
        return
    
    # Check environment variables
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_KEY')
    
    print("\n=== Environment Variables ===")
    print(f"SUPABASE_URL: {'set' if supabase_url else 'not set'}")
    print(f"SUPABASE_KEY: {'set' if supabase_key else 'not set'}")
    
    if not supabase_url or not supabase_key:
        print("\n❌ Missing Supabase credentials in .env file")
        print("Please make sure you have the following in your .env file:")
        print("SUPABASE_URL=your_supabase_project_url")
        print("SUPABASE_KEY=your_supabase_anon_key")
        return
    
    # Try to create a Supabase client
    try:
        from supabase import create_client
        print("\nAttempting to create Supabase client...")
        client = create_client(supabase_url, supabase_key)
        print("✅ Successfully created Supabase client")
        
        # Test a simple query
        print("\nTesting database query...")
        try:
            result = client.table('users').select('*').limit(1).execute()
            print("✅ Query executed successfully")
            if hasattr(result, 'data'):
                print(f"Found {len(result.data) if result.data else 0} users")
            else:
                print("Unexpected response format:", result)
        except Exception as e:
            print(f"❌ Query failed: {str(e)}")
            
    except Exception as e:
        print(f"❌ Failed to create Supabase client: {str(e)}")

if __name__ == "__main__":
    check_supabase()
