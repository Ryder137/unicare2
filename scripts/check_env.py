import os
from dotenv import load_dotenv

def check_env_vars():
    """Check if required environment variables are set."""
    print("\n[INFO] ====== Checking Environment Variables ======")
    
    # Load environment variables from .env file
    load_dotenv()
    
    # List of required environment variables
    required_vars = [
        'SUPABASE_URL',
        'SUPABASE_KEY',
        'SUPABASE_SERVICE_ROLE_KEY',
        'FLASK_APP',
        'FLASK_ENV',
        'SECRET_KEY',
        'MONGODB_URI',
        'MAIL_SERVER',
        'MAIL_PORT',
        'MAIL_USE_TLS',
        'MAIL_USERNAME',
        'MAIL_PASSWORD',
        'MAIL_DEFAULT_SENDER',
        'OPENAI_API_KEY'
    ]
    
    # Check each required variable
    missing_vars = []
    for var in required_vars:
        value = os.getenv(var)
        if value is None or value == '':
            missing_vars.append(var)
    
    # Print results
    if missing_vars:
        print("\n[WARNING] The following required environment variables are missing or empty:")
        for var in missing_vars:
            print(f"- {var}")
        
        print("\nPlease add these variables to your .env file with appropriate values.")
        print("Refer to .env.example for the required format.")
    else:
        print("\n[SUCCESS] All required environment variables are set!")
    
    # Print current values (masking sensitive info)
    print("\n[INFO] Current Environment Variables:")
    for var in required_vars:
        value = os.getenv(var, 'Not Set')
        if var in ['SUPABASE_KEY', 'SUPABASE_SERVICE_ROLE_KEY', 'SECRET_KEY', 'MAIL_PASSWORD', 'OPENAI_API_KEY'] and value != 'Not Set':
            value = f"{'*' * 8}{value[-4:] if len(value) > 4 else ''}"
        print(f"{var}: {value}")

if __name__ == "__main__":
    check_env_vars()
