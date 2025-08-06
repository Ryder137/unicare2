import os
from dotenv import load_dotenv
from supabase import create_client

# Load environment variables
load_dotenv()

# Initialize Supabase client
url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_KEY')
supabase = create_client(url, key)

def test_rls():
    print("Testing RLS policies...\n")
    
    # Test 1: Try to read users table (should fail for anon)
    try:
        print("Test 1: Reading users table as anonymous...")
        result = supabase.table('users').select("*").execute()
        print("❌ FAIL: Should not be able to read users table as anonymous")
    except Exception as e:
        print("✅ PASS: Cannot read users table as anonymous")
    
    # Test 2: Try to insert a user (should work)
    try:
        print("\nTest 2: Inserting a test user...")
        user_data = {
            'id': 'test-user-123',
            'email': 'test@example.com',
            'username': 'testuser',
            'password_hash': 'hashedpassword'
        }
        result = supabase.table('users').insert(user_data).execute()
        print("✅ PASS: Can insert new user (signup flow works)")
    except Exception as e:
        print(f"❌ FAIL: Error inserting user - {str(e)}")
    
    print("\nRLS Test completed.")

if __name__ == "__main__":
    test_rls()
