import os
from dotenv import load_dotenv
from pathlib import Path

def test_env():
    # Get the root directory of your project (where .env should be)
    env_path = Path(__file__).parent.parent / '.env'
    print(f"Looking for .env at: {env_path}")
    
    # Load the .env file
    load_dotenv(env_path)
    
    # List of expected environment variables
    expected_vars = [
        'SUPABASE_URL',
        'SUPABASE_ANON_KEY',
        'SUPABASE_SERVICE_ROLE_KEY',
        'DATABASE_URL'
    ]
    
    print("\nEnvironment Variables:")
    print("===================")
    
    # Check each expected variable
    all_vars_found = True
    for var in expected_vars:
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: {'*' * 8 + value[-4:] if 'KEY' in var else value}")
        else:
            print(f"❌ {var}: Not found")
            all_vars_found = False
    
    if all_vars_found:
        print("\n✅ All environment variables are loaded successfully!")
    else:
        print("\n❌ Some environment variables are missing. Please check your .env file.")

if __name__ == "__main__":
    test_env()
