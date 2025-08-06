import sys
import os
from config import init_supabase

def test_connection():
    try:
        print("🔄 Attempting to connect to Supabase...")
        
        # Initialize Supabase client
        supabase = init_supabase()
        
        # Test connection by fetching a small amount of data
        print("✅ Successfully connected to Supabase!")
        print("\nTesting database connection...")
        
        # Try to fetch some data (e.g., first 5 users)
        try:
            result = supabase.table('users').select('*').limit(1).execute()
            print(f"✅ Successfully queried users table. Found {len(result.data)} users.")
            if result.data:
                print("\nSample user data:")
                print(result.data[0])
        except Exception as e:
            print(f"⚠️ Could not query users table: {str(e)}")
            print("This might be normal if the table is empty or doesn't exist yet.")
        
    except Exception as e:
        print(f"❌ Failed to connect to Supabase: {str(e)}")
        print("\nTroubleshooting steps:")
        print("1. Make sure your .env file exists in the project root")
        print("2. Verify that SUPABASE_URL and SUPABASE_KEY are correctly set in .env")
        print("3. Check your internet connection")
        print("4. Ensure your Supabase project is running and the URL is correct")
        print("5. Verify that the anon/public key has the correct permissions in Supabase")
        return False
    
    return True

if __name__ == "__main__":
    print("=== Supabase Connection Test ===\n")
    test_connection()
