from flask import Flask
from flask_mail import Mail, Message
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Configure email settings
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'true').lower() == 'true'
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER')

# Initialize Flask-Mail
mail = Mail(app)

def send_test_email():
    try:
        # Create a test message
        msg = Message(
            subject='Test Email from UNICARE',
            recipients=[app.config['MAIL_USERNAME']],  # Send to yourself
            body='This is a test email from UNICARE. If you received this, email is working!',
            html='''
            <h1>Test Email from UNICARE</h1>
            <p>This is a test email to verify that email sending is working correctly.</p>
            <p>If you received this, your email configuration is correct!</p>
            <p>Current time: {}</p>
            '''.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        )
        
        # Send the email
        mail.send(msg)
        print("✅ Test email sent successfully!")
        print(f"Check your inbox at {app.config['MAIL_USERNAME']}")
        return True
        
    except Exception as e:
        print("❌ Error sending test email:")
        print(str(e))
        return False

if __name__ == "__main__":
    # Check if required environment variables are set
    required_vars = ['MAIL_SERVER', 'MAIL_USERNAME', 'MAIL_PASSWORD']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"- {var}")
        print("\nPlease make sure your .env file is properly configured.")
    else:
        print("Sending test email...")
        print(f"From: {app.config['MAIL_DEFAULT_SENDER']}")
        print(f"To: {app.config['MAIL_USERNAME']}")
        print()
        
        # Import datetime here to avoid potential serialization issues
        from datetime import datetime
        send_test_email()
