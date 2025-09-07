import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Supabase client
SUPABASE_URL = os.getenv('SUPABASE_URL', 'https://rzktipnfmqrhpqtlfixp.supabase.co')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_KEY') or os.getenv('SUPABASE_KEY')

if not SUPABASE_KEY:
    print("Error: SUPABASE_SERVICE_KEY or SUPABASE_KEY environment variable is required")
    exit(1)

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def check_rls_policies():
    """Check the current RLS policies on the admin_users table."""
    try:
        # This requires the pg_catalog schema access
        result = supabase.rpc('get_rls_policies', {'table_name': 'admin_users'}).execute()
        print("Current RLS policies:")
        print(result)
    except Exception as e:
        print(f"Error checking RLS policies: {e}")

def create_admin_policy():
    """Create an RLS policy to allow admin user creation with service role key."""
    try:
        # This uses the service role key to bypass RLS for admin operations
        policy_sql = """
        DO $$
        BEGIN
            -- Check if policy already exists
            IF NOT EXISTS (
                SELECT 1 FROM pg_policies 
                WHERE tablename = 'admin_users' 
                AND policyname = 'Allow service role to manage admin_users'
            ) THEN
                -- Create policy to allow all operations with service role
                EXECUTE 'CREATE POLICY "Allow service role to manage admin_users" 
                        ON public.admin_users 
                        FOR ALL 
                        TO service_role 
                        USING (true) 
                        WITH CHECK (true);';
                
                RAISE NOTICE 'Created service role policy for admin_users';
            ELSE
                RAISE NOTICE 'Service role policy for admin_users already exists';
            END IF;
        END $$;
        """
        
        # Execute the SQL using the Supabase RPC
        result = supabase.rpc('execute_sql', {'query': policy_sql}).execute()
        print("RLS policy creation result:")
        print(result)
        
        print("\nRLS policy created successfully. You should now be able to create admin users.")
        
    except Exception as e:
        print(f"Error creating RLS policy: {e}")

if __name__ == "__main__":
    print("Checking RLS policies...")
    check_rls_policies()
    
    print("\nCreating RLS policy if needed...")
    create_admin_policy()
    
    print("\nDone. You can now try creating an admin user again.")
