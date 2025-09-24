import os
import sys
from dotenv import load_dotenv

print("=== Supabase Configuration Check ===\n")

# Load environment variables
load_dotenv()

# Get environment variables
env_vars = {
    'SUPABASE_URL': os.getenv('SUPABASE_URL'),
    'SUPABASE_KEY': os.getenv('SUPABASE_KEY'),
    'SUPABASE_SERVICE_ROLE_KEY': os.getenv('SUPABASE_SERVICE_ROLE_KEY'),
    'DATABASE_URL': os.getenv('DATABASE_URL')
}

# Print environment variables (masking sensitive data)
print("Current Configuration:")
for key, value in env_vars.items():
    if value:
        masked = value[:5] + '*' * (len(value) - 10) + value[-5:] if len(value) > 10 else '**********'
        print(f"{key}: {masked}")
    else:
        print(f"{key}: Not set")

# Test Supabase connection
if env_vars['SUPABASE_URL'] and env_vars['SUPABASE_KEY']:
    try:
        from supabase import create_client
        
        print("\nTesting Supabase connection...")
        supabase = create_client(env_vars['SUPABASE_URL'], env_vars['SUPABASE_KEY'])
        
        # Test with a simple query
        print("Executing test query...")
        result = supabase.table('users').select('*').limit(1).execute()
        
        if hasattr(result, 'data'):
            print("\n✅ Successful connection to Supabase!")
            print(f"Data sample: {result.data[:1] if result.data else 'No data returned'}")
        else:
            print("\n⚠️ Connection successful but unexpected response format:")
            print(result)
            
    except Exception as e:
        print(f"\n❌ Error connecting to Supabase: {str(e)}")
        print("\nTroubleshooting steps:")
        print("1. Verify your Supabase project URL and API key are correct")
        print("2. Check your internet connection")
        print("3. Ensure your Supabase project is running")
        print("4. Verify the database tables exist in your Supabase project")
else:
    print("\n❌ Missing Supabase configuration. Please check your .env file.")
    print("Required variables: SUPABASE_URL, SUPABASE_KEY")
