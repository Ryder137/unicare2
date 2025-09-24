import os
import sys
from dotenv import load_dotenv
from supabase import create_client

def apply_migration():
    # Load environment variables
    load_dotenv()
    
    # Get Supabase credentials
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_KEY')
    
    if not supabase_url or not supabase_key:
        print("❌ Error: SUPABASE_URL and SUPABASE_KEY must be set in .env")
        return False
    
    try:
        # Initialize Supabase client
        print("🔌 Connecting to Supabase...")
        supabase = create_client(supabase_url, supabase_key)
        
        # Read the migration SQL file
        with open('migrations/fix_guidance_counselors_function.sql', 'r') as f:
            sql_script = f.read()
        
        # Split the script into individual statements
        # (Supabase SQL API doesn't support multiple statements in one call)
        statements = [s.strip() for s in sql_script.split(';') if s.strip()]
        
        # Execute each statement
        for i, statement in enumerate(statements, 1):
            print(f"🔄 Executing statement {i}/{len(statements)}...")
            try:
                result = supabase.rpc('execute_sql', {'query': statement + ';'}).execute()
                if hasattr(result, 'error') and result.error:
                    print(f"⚠️  Warning in statement {i}: {result.error}")
            except Exception as e:
                print(f"⚠️  Warning in statement {i}: {str(e)}")
        
        # Verify the function was created
        print("✅ Migration completed. Verifying function...")
        
        # Try to call the function to verify it works
        try:
            result = supabase.rpc('get_guidance_counselors_with_users').execute()
            if hasattr(result, 'data'):
                print("✅ Function verified successfully!")
                return True
            else:
                print("⚠️  Function exists but returned no data")
                return True
        except Exception as e:
            print(f"⚠️  Error verifying function: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Error applying migration: {e}")
        return False

if __name__ == "__main__":
    if apply_migration():
        print("\n🎉 Migration completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Migration failed")
        sys.exit(1)
