import os
import sys
from dotenv import load_dotenv

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Load environment variables
load_dotenv()

def test_supabase_connection():
    try:
        from supabase import create_client
        
        # Get Supabase credentials
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_KEY')
        
        if not supabase_url or not supabase_key:
            print("❌ Missing Supabase credentials in .env file")
            print("Please make sure you have the following in your .env file:")
            print("SUPABASE_URL=your_supabase_project_url")
            print("SUPABASE_KEY=your_supabase_anon_key")
            return
            
        print(f"Connecting to Supabase at: {supabase_url}")
        
        # Initialize Supabase client
        supabase = create_client(supabase_url, supabase_key)
        
        # Test connection with a simple query
        print("\nTesting database connection...")
        try:
            # Try to list tables in the public schema
            result = supabase.table('users').select('*').limit(1).execute()
            
            if hasattr(result, 'data'):
                print("✅ Successfully connected to Supabase!")
                print(f"Found {len(result.data) if result.data else 0} users in the database.")
            else:
                print("⚠️ Connected to Supabase but couldn't fetch data.")
                print("Response:", result)
                
        except Exception as e:
            print(f"❌ Error executing query: {str(e)}")
            print("\nTroubleshooting steps:")
            print("1. Verify your Supabase project URL and API key are correct")
            print("2. Check if the 'users' table exists in your Supabase database")
            print("3. Make sure your IP is whitelisted in Supabase if using IP restrictions")
            
    except ImportError:
        print("❌ supabase-py package not found. Install it with:")
        print("pip install supabase")
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")

if __name__ == "__main__":
    test_supabase_connection()
