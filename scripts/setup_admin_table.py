import os
import sys
from supabase import create_client, Client
from dotenv import load_dotenv

def setup_rls_policies() -> bool:
    """Set up RLS policies for the admin_users table."""
    try:
        load_dotenv()
        supabase: Client = create_client(
            os.getenv('SUPABASE_URL'),
            os.getenv('SUPABASE_SERVICE_ROLE_KEY')
        )
        
        # Create the RLS enable function if it doesn't exist
        create_rls_function = """
        CREATE OR REPLACE FUNCTION public.rls_enable_table(schema_name text, table_name text)
        RETURNS void
        LANGUAGE plpgsql
        SECURITY DEFINER
        AS $$
        BEGIN
            EXECUTE format('ALTER TABLE %I.%I ENABLE ROW LEVEL SECURITY', schema_name, table_name);
        END;
        $$;
        """
        
        # Create the function
        supabase.rpc('execute_sql', {'query': create_rls_function}).execute()
        print("✓ Created RLS enable function")
        
        # Enable RLS on admin_users
        print("Enabling RLS on admin_users table...")
        supabase.rpc('rls_enable_table', {
            'schema_name': 'public',
            'table_name': 'admin_users'
        }).execute()
        print("✓ RLS enabled successfully")
        
        # Drop existing policies
        print("\nDropping existing policies...")
        policies_to_drop = [
            "Enable service role access",
            "Allow service role to manage admin_users",
            "Allow admins to read all admin users",
            "Allow users to update their own admin profile"
        ]
        
        for policy_name in policies_to_drop:
            try:
                supabase.rpc('policy_drop', {
                    'table_name': 'admin_users',
                    'policy_name': policy_name
                }).execute()
                print(f"✓ Dropped policy: {policy_name}")
            except Exception as e:
                if "policy" in str(e).lower() and "does not exist" in str(e).lower():
                    print(f"ℹ️ Policy '{policy_name}' not found, skipping...")
                else:
                    print(f"⚠️ Error dropping policy {policy_name}: {str(e)}")
        
        # Create service role policy
        print("\nCreating service role policy...")
        supabase.rpc('policy_create', {
            'table_name': 'admin_users',
            'policy_name': 'Allow service role to manage admin_users',
            'action': 'ALL',
            'role': 'service_role',
            'using': 'true',
            'check': 'true'
        }).execute()
        print("✓ Service role policy created")
        
        print("\n✅ RLS policies have been set up successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Error setting up RLS policies: {str(e)}")
        return False

def create_admin_user(email: str, password: str, full_name: str) -> bool:
    """Create an admin user using Supabase client."""
    try:
        load_dotenv()
        supabase: Client = create_client(
            os.getenv('SUPABASE_URL'),
            os.getenv('SUPABASE_SERVICE_ROLE_KEY')  # Using service role for admin operations
        )
        
        # Check if user already exists
        existing_user = supabase.table('admin_users') \
            .select('*') \
            .eq('email', email) \
            .execute()
            
        if existing_user.data:
            print(f"❌ Admin user with email {email} already exists")
            return False
        
        # Create auth user
        auth_response = supabase.auth.sign_up({
            'email': email,
            'password': password,
            'options': {
                'data': {
                    'full_name': full_name,
                    'is_admin': True
                }
            }
        })
        
        if hasattr(auth_response, 'error') and auth_response.error:
            print(f"❌ Error creating auth user: {auth_response.error.message}")
            return False
            
        # Create admin user in admin_users table
        admin_data = {
            'id': auth_response.user.id,
            'email': email,
            'full_name': full_name,
            'is_active': True,
            'is_super_admin': True,
            'failed_login_attempts': 0
        }
        
        result = supabase.table('admin_users').insert(admin_data).execute()
        
        if hasattr(result, 'error') and result.error:
            print(f"❌ Error creating admin user: {result.error.message}")
            return False
            
        print(f"✅ Admin user {email} created successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error creating admin user: {str(e)}")
        return False

if __name__ == "__main__":
    # Set up RLS policies first
    if not setup_rls_policies():
        print("\nFailed to set up RLS policies. Please check the error above.")
        sys.exit(1)
    
    # Create admin user
    email = "enjhaym1@gmail.com"  # Change this to your desired admin email
    password = "admin123"       # Change this to a strong password
    full_name = "Nathalie Jane M. Manjares"    # Change this to the admin's full name
    
    print(f"\nCreating admin user: {email}")
    if create_admin_user(email, password, full_name):
        print("\n✅ Setup completed successfully!")
        print("You can now log in to the admin dashboard with the credentials above.")
    else:
        print("\n❌ Failed to create admin user. Please check the error messages above.")
        sys.exit(1)