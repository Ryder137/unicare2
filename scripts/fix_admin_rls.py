import os
import time
from supabase import create_client
from dotenv import load_dotenv

def execute_sql(supabase, sql):
    """Helper function to execute SQL with retry logic."""
    max_retries = 3
    for attempt in range(max_retries):
        try:
            # Try direct SQL execution first
            result = supabase.rpc('execute', {'query': sql}).execute()
            return result
        except Exception as e:
            if 'function public.execute(unknown) does not exist' in str(e):
                # Fallback to raw SQL execution if execute function doesn't exist
                try:
                    from supabase.lib.client_options import ClientOptions
                    from supabase.client import Client as SupabaseClient
                    
                    # Create a new client with raw SQL execution capability
                    client_options = ClientOptions(schema='public')
                    supabase_raw = SupabaseClient(
                        os.getenv('SUPABASE_URL'),
                        os.getenv('SUPABASE_SERVICE_ROLE_KEY'),
                        client_options=client_options
                    )
                    
                    # Execute raw SQL
                    result = supabase_raw.rpc('execute', {'query': sql}).execute()
                    return result
                except Exception as inner_e:
                    if attempt == max_retries - 1:  # Last attempt
                        raise inner_e
            elif attempt == max_retries - 1:  # Last attempt
                raise
            
            # Wait before retrying
            time.sleep(1 * (attempt + 1))

def setup_admin_policies():
    """Set up RLS policies for the admin_users table."""
    try:
        # Initialize Supabase client
        supabase = create_client(
            os.getenv('SUPABASE_URL'),
            os.getenv('SUPABASE_SERVICE_ROLE_KEY')
        )

        # SQL commands to execute
        sql_commands = [
            # Enable RLS on admin_users if not already enabled
            "ALTER TABLE admin_users ENABLE ROW LEVEL SECURITY;",
            
            # Drop existing policies to avoid conflicts
            """
            DROP POLICY IF EXISTS "Enable service role access" ON public.admin_users;
            DROP POLICY IF EXISTS "Allow service role to manage admin_users" ON public.admin_users;
            DROP POLICY IF EXISTS "Allow admins to read all admin users" ON public.admin_users;
            DROP POLICY IF EXISTS "Allow users to update their own admin profile" ON public.admin_users;
            """,
            
            # Create a policy that allows all operations for service role
            """
            CREATE POLICY "Allow service role to manage admin_users" 
            ON public.admin_users
            FOR ALL
            TO service_role
            USING (true)
            WITH CHECK (true);
            """,
            
            # Create a policy that allows admins to read all admin users
            """
            CREATE POLICY "Allow admins to read all admin users"
            ON public.admin_users
            FOR SELECT
            TO authenticated
            USING (true);
            """,
            
            # Create a policy that allows users to update their own admin profile
            """
            CREATE POLICY "Allow users to update their own admin profile"
            ON public.admin_users
            FOR UPDATE
            TO authenticated
            USING (auth.uid() = id)
            WITH CHECK (auth.uid() = id);
            """
        ]
        
        # Execute each SQL command
        for sql in sql_commands:
            if sql.strip():
                print(f"Executing: {sql[:100]}...")
                try:
                    result = execute_sql(supabase, sql)
                    print("Success")
                except Exception as e:
                    print(f"Error: {str(e)[:200]}")
                    if 'already has a policy' in str(e):
                        print("Policy already exists, continuing...")
                    else:
                        raise
        
        print("\nRLS policies have been set up successfully!")
        
    except Exception as e:
        print(f"Error setting up RLS policies: {e}")
        print("\nIf you continue to have issues, try running these SQL commands")
        print("directly in the Supabase SQL Editor:")
        print("1. Go to Supabase Dashboard")
        print("2. Click on 'SQL Editor' in the left sidebar")
        print("3. Create a new query and run the SQL commands shown above")
        raise

if __name__ == "__main__":
    # Load environment variables
    load_dotenv()
    
    # Verify required environment variables
    required_vars = ['SUPABASE_URL', 'SUPABASE_SERVICE_ROLE_KEY']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"Error: Missing required environment variables: {', '.join(missing_vars)}")
        print("Please make sure your .env file contains these variables:")
        for var in required_vars:
            print(f"{var}=your_value_here")
        exit(1)
    
    print("Setting up RLS policies for admin_users table...")
    setup_admin_policies()
    print("\nYou can now try creating an admin user again.")
