import webbrowser
import os
import sys

def print_instructions():
    print("""
    ===============================================
    GMAIL APP PASSWORD SETUP INSTRUCTIONS
    ===============================================
    
    To enable email sending from your Gmail account, follow these steps:
    
    1. Go to your Google Account Security page:
       https://myaccount.google.com/security
    
    2. Under "Signing in to Google", make sure 2-Step Verification is ON.
       If not, click on it and follow the setup process.
    
    3. Once 2-Step Verification is enabled, go to App Passwords:
       https://myaccount.google.com/apppasswords
    
    4. At the bottom, under "Select app", choose "Other (Custom name)"
    
    5. Enter a name like "UNICARE App" and click "Generate"
    
    6. Copy the 16-character password that appears
    
    7. Open the .env file in your project directory and update these values:
       - MAIL_USERNAME=your-email@gmail.com
       - MAIL_PASSWORD=the-16-character-app-password
       - MAIL_DEFAULT_SENDER=your-email@gmail.com
    
    8. Save the .env file and restart your Flask application
    
    ===============================================
    """)

def main():
    print_instructions()
    
    # Ask if user wants to open the links
    open_links = input("Would you like me to open the required Google pages for you? (y/n): ").lower()
    
    if open_links == 'y':
        print("Opening Google Account Security page...")
        webbrowser.open("https://myaccount.google.com/security")
        
        print("Opening App Passwords page...")
        webbrowser.open("https://myaccount.google.com/apppasswords")
    
    # Show where the .env file is located
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    print(f"\nYour .env file is located at: {env_path}")
    
    # Try to open the .env file
    try:
        if sys.platform == 'win32':
            os.startfile(env_path)
        else:
            os.system(f'open "{env_path}"')
    except Exception as e:
        print(f"Could not open .env file automatically. Please open it manually at: {env_path}")

if __name__ == "__main__":
    main()
