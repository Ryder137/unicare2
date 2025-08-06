import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
from datetime import datetime

print("Testing email configuration...\n")

# Load environment variables
load_dotenv()

# Get email settings from environment variables
mail_server = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
mail_port = int(os.getenv('MAIL_PORT', 587))
mail_username = os.getenv('MAIL_USERNAME')
mail_password = os.getenv('MAIL_PASSWORD')
mail_use_tls = os.getenv('MAIL_USE_TLS', 'true').lower() == 'true'

# Check if required variables are set
if not all([mail_username, mail_password]):
    print("❌ Error: Missing required email configuration")
    print("Please make sure these variables are set in your .env file:")
    if not mail_username:
        print("- MAIL_USERNAME (your email address)")
    if not mail_password:
        print("- MAIL_PASSWORD (your app password)")
    exit(1)

print("Configuration found:")
print(f"SMTP Server: {mail_server}:{mail_port}")
print(f"Username: {mail_username}")
print(f"Using TLS: {mail_use_tls}")
print("\nAttempting to connect to the SMTP server...")

try:
    # Create message
    msg = MIMEMultipart()
    msg['From'] = mail_username
    msg['To'] = mail_username
    msg['Subject'] = 'UNICARE - Test Email Configuration'
    
    # Email body
    body = f"""
    <h1>Test Email from UNICARE</h1>
    <p>This is a test email to verify your email configuration.</p>
    <p>If you received this, your email settings are working correctly!</p>
    <p>Time sent: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    """
    
    msg.attach(MIMEText(body, 'html'))
    
    # Connect to the SMTP server
    with smtplib.SMTP(mail_server, mail_port) as server:
        server.ehlo()
        
        if mail_use_tls:
            server.starttls()
            server.ehlo()
        
        # Login to the server
        print("Logging in to the SMTP server...")
        server.login(mail_username, mail_password)
        
        # Send the email
        print("Sending test email...")
        server.send_message(msg)
        
        print("\n✅ Test email sent successfully!")
        print(f"Check your inbox at {mail_username}")
        
except Exception as e:
    print("\n❌ Error sending test email:")
    print(str(e))
    print("\nTroubleshooting tips:")
    print("1. Make sure your app password is correct")
    print("2. Verify that 'Less secure app access' is enabled in your Google account")
    print("3. Check if your firewall or antivirus is blocking the connection")
    print("4. Try using a different network connection")
    print("5. If using Gmail, you might need to allow access from less secure apps:")
    print("   https://myaccount.google.com/lesssecureapps")
    print("   (Note: This link might not work if you have 2-Step Verification enabled)")
