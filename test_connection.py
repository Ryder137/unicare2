import os
import sys
import importlib.util
from dotenv import load_dotenv

def print_header(title):
    print("\n" + "="*50)
    print(f" {title} ".center(50, '='))
    print("="*50)

def check_python_version():
    print("\nPython Version:", sys.version.split('\n')[0])

def check_environment():
    print_header("Environment Variables")
    load_dotenv()
    
    env_vars = [
        'SUPABASE_URL',
        'SUPABASE_KEY',
        'SUPABASE_SERVICE_ROLE_KEY',
        'DATABASE_URL',
        'FLASK_APP',
        'FLASK_ENV'
    ]
    
    for var in env_vars:
        value = os.getenv(var, 'Not Set')
        print(f"{var}: {value[:10]}..." if len(str(value)) > 10 and var != 'FLASK_ENV' else f"{var}: {value}")

def check_imports():
    print_header("Checking Imports")
    
    packages = [
        'flask',
        'flask_login',
        'flask_sqlalchemy',
        'flask_migrate',
        'supabase',
        'python-dotenv',
        'psycopg2-binary'
    ]
    
    for package in packages:
        name = package.replace('-', '_')
        spec = importlib.util.find_spec(name)
        status = "✅" if spec else "❌"
        print(f"{status} {package}")

def test_supabase_connection():
    print_header("Testing Supabase Connection")
    
    try:
        from supabase import create_client
        
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_KEY')
        
        if not supabase_url or not supabase_key:
            print("❌ Missing Supabase credentials in .env file")
            return
            
        print("Connecting to Supabase...")
        supabase = create_client(supabase_url, supabase_key)
        
        try:
            # Try a simple query
            print("Executing test query...")
            result = supabase.table('users').select('*').limit(1).execute()
            
            if hasattr(result, 'data'):
                print(f"✅ Connection successful! Found {len(result.data) if result.data else 0} users.")
            else:
                print("⚠️ Connected but unexpected response format:")
                print(result)
                
        except Exception as e:
            print(f"❌ Query failed: {str(e)}")
            
    except Exception as e:
        print(f"❌ Failed to initialize Supabase client: {str(e)}")

def main():
    print_header("UNICARE Application Test")
    check_python_version()
    check_environment()
    check_imports()
    test_supabase_connection()
    print("\n" + "="*50)
    print(" Test Complete ".center(50, '='))
    print("="*50)

if __name__ == "__main__":
    main()
