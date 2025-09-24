import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Print environment variables (without sensitive values)
print("Checking environment variables...")
print(f"SUPABASE_URL: {'set' if os.getenv('SUPABASE_URL') else 'not set'}")
print(f"SUPABASE_KEY: {'set' if os.getenv('SUPABASE_KEY') else 'not set'}")
print(f"DATABASE_URL: {'set' if os.getenv('DATABASE_URL') else 'not set'}")

# Test database connection
try:
    from supabase import create_client
    
    supabase = create_client(
        os.getenv('SUPABASE_URL'),
        os.getenv('SUPABASE_KEY')
    )
    
    # Simple query to test connection
    print("\nTesting Supabase connection...")
    result = supabase.table('users').select('*').limit(1).execute()
    print("✅ Connection successful!")
    print(f"Response: {result}")
    
except Exception as e:
    print("\n❌ Error connecting to Supabase:")
    print(str(e))
