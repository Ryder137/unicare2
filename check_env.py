import os
from dotenv import load_dotenv

def mask_sensitive(value):
    if not value:
        return "[Not Set]"
    if len(value) > 10:
        return value[:5] + '*' * (len(value) - 10) + value[-5:]
    return "**********"

print("=== Environment Variables ===\n")

# Load .env file
load_dotenv()

# Check if .env file exists
if not os.path.exists('.env'):
    print("❌ .env file not found in the current directory")
    print("Please create a .env file in the project root with your Supabase credentials")
    print("\nRequired variables:")
    print("SUPABASE_URL=your_supabase_project_url")
    print("SUPABASE_KEY=your_supabase_anon_key")
    print("SUPABASE_SERVICE_ROLE_KEY=your_service_role_key")
    print("DATABASE_URL=postgresql://...")
    exit(1)

# Get and display environment variables
env_vars = [
    'SUPABASE_URL',
    'SUPABASE_KEY',
    'SUPABASE_SERVICE_ROLE_KEY',
    'DATABASE_URL',
    'FLASK_APP',
    'FLASK_ENV',
    'SECRET_KEY'
]

print("Current .env configuration (sensitive data masked):\n")

for var in env_vars:
    value = os.getenv(var)
    if value:
        print(f"{var}: {mask_sensitive(value)}")
    else:
        print(f"{var}: [Not Set]")
