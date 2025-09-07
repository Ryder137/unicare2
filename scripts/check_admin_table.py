import os
from supabase import create_client
from dotenv import load_dotenv

def check_or_create_admin_table():
    """Check if admin_users table exists, create it if it doesn't."""
    try:
        # Initialize Supabase client
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_KEY')
        
        if not supabase_url or not supabase_key:
            print("ERROR: SUPABASE_URL and SUPABASE_KEY must be set in .env file")
            return False
            
        supabase = create_client(supabase_url, supabase_key)
        
        # Check if table exists
        try:
            result = supabase.table('admin_users').select('*').limit(1).execute()
            print("✅ admin_users table exists")
            return True
            
        except Exception as e:
            if 'relation "_users" does not exist' in str(e):
                print("ℹ️ admin_users table does not exist, creating...")
                # Create the admin_users table
                create_table_sql = """
                CREATE TABLE IF NOT EXISTS public.admin_users (
                    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    first_name TEXT,
                    last_name TEXT,
                    is_active BOOLEAN DEFAULT true,
                    is_superadmin BOOLEAN DEFAULT false,
                    last_login_at TIMESTAMPTZ,
                    created_at TIMESTAMPTZ DEFAULT now(),
                    updated_at TIMESTAMPTZ DEFAULT now()
                );
                
                -- Create index for faster lookups
                CREATE INDEX IF NOT EXISTS idx_admin_users_email ON public.admin_users(email);
                
                -- Enable RLS (Row Level Security) for better security
                ALTER TABLE public.admin_users ENABLE ROW LEVEL SECURITY;
                """
                
                # Execute the SQL to create the table
                result = supabase.rpc('pg_temp.execute_sql', {'sql': create_table_sql}).execute()
                print("✅ admin_users table created successfully")
                return True
                
            else:
                print(f"❌ Error checking admin_users table: {str(e)}")
                return False
                
    except Exception as e:
        print(f"❌ An error occurred: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    load_dotenv()  # Load environment variables from .env file
    success = check_or_create_admin_table()
    if not success:
        print("\nPlease ensure you have the following environment variables set in your .env file:")
        print("SUPABASE_URL=your_supabase_project_url")
        print("SUPABASE_KEY=your_supabase_anon_key")
    sys.exit(0 if success else 1)
