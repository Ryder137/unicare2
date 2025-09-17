import os
from supabase import create_client
from dotenv import load_dotenv
from pathlib import Path

def test_supabase_connection():
    try:
        # Load environment variables
        env_path = Path(__file__).parent.parent / '.env'
        load_dotenv(env_path)
        
        # Get Supabase credentials
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_SERVICE_KEY')
        
        if not supabase_url or not supabase_key:
            print("❌ Missing Supabase credentials in .env file")
            return False
            
        print("🔌 Testing Supabase connection...")
        
        # Initialize the client
        supabase = create_client(supabase_url, supabase_key)
        
        # Test connection by making a simple request
        response = supabase.table('admin_users').select("*").limit(1).execute()
        
        if hasattr(response, 'error') and response.error:
            print(f"⚠️ Could not query admin_users table: {response.error.message}")
            print("   This might be normal if the table doesn't exist yet")
        else:
            count = len(response.data) if hasattr(response, 'data') else 0
            print(f"✅ Successfully connected to Supabase!")
            print(f"ℹ️ Found {count} admin users")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to connect to Supabase: {str(e)}")
        return False

if __name__ == "__main__":
    test_supabase_connection()
