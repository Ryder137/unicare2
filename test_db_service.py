import os
import sys
from dotenv import load_dotenv

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Load environment variables
load_dotenv()

def test_db_connection():
    try:
        from services.database_service import db_service
        
        print("Testing database connection...")
        
        # Get the Supabase client
        supabase = db_service.supabase
        
        if not supabase:
            print("❌ Failed to initialize Supabase client")
            return
            
        print("✅ Supabase client initialized successfully")
        
        # Test a simple query
        print("\nTesting database query...")
        try:
            result = supabase.table('users').select('*').limit(1).execute()
            print(f"✅ Query successful! Found {len(result.data) if hasattr(result, 'data') else 0} users")
        except Exception as e:
            print(f"❌ Query failed: {str(e)}")
            
    except ImportError as e:
        print(f"❌ Import error: {str(e)}")
        print("Make sure you're running this from the project root directory")
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")

if __name__ == "__main__":
    test_db_connection()
