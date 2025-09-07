import os
import sys
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv()

# Get Supabase credentials
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

if not SUPABASE_URL or not SUPABASE_KEY:
    print("Error: SUPABASE_URL and SUPABASE_KEY must be set in .env file")
    sys.exit(1)

def run_migration():
    try:
        # Initialize Supabase client
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        print("Connecting to Supabase...")
        
        # Read the migration file
        with open('migrations/20240901_reset_auth_tables.sql', 'r') as f:
            sql_commands = f.read()
        
        print("Executing SQL migration...")
        
        # Execute the SQL commands
        result = supabase.rpc('exec', {'query': sql_commands}).execute()
        
        print("\nSuccessfully reset authentication tables!")
        print("\nDefault credentials:")
        print("Admin: admin@example.com / admin123")
        print("User: user@example.com / user123")
        
    except Exception as e:
        print(f"Error executing migration: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    # Confirm before proceeding
    print("WARNING: This will delete all data in the users and admin_users tables.")
    confirm = input("Are you sure you want to continue? (yes/no): ")
    
    if confirm.lower() == 'yes':
        run_migration()
    else:
        print("Operation cancelled.")
        sys.exit(0)
