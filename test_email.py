"""
Test script to directly test email sending functionality.
"""
import os
import sys
from flask import Flask
from flask_mail import Mail, Message

# Create a simple Flask app
app = Flask(__name__)

# Configure mail settings directly
app.config['MAIL_SERVER'] = 'smtp.mailtrap.io'
app.config['MAIL_PORT'] = 2525
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = 'd4e9f8a8b1c7d0'
app.config['MAIL_PASSWORD'] = 'a1b2c3d4e5f6g7'

# Initialize mail
mail = Mail(app)

def send_test_email():
    """Send a test email to verify email functionality."""
    with app.app_context():
        try:
            # Create a test message
            msg = Message(
                subject="Test Email from MBO Tracker",
                sender="notificationsmbo@snaplogic.com",
                recipients=["atdughetti@snaplogic.com"],
                body="This is a test email to verify email functionality.",
                html="<p>This is a <b>test email</b> to verify email functionality.</p>"
            )
            
            # Print mail configuration
            print(f"Mail Server: {app.config['MAIL_SERVER']}")
            print(f"Mail Port: {app.config['MAIL_PORT']}")
            print(f"Mail Use TLS: {app.config['MAIL_USE_TLS']}")
            print(f"Mail Use SSL: {app.config['MAIL_USE_SSL']}")
            print(f"Mail Username: {app.config['MAIL_USERNAME']}")
            print(f"Mail Password: {'*' * len(app.config['MAIL_PASSWORD'])}")
            
            # Send the email
            print("Sending test email...")
            mail.send(msg)
            print("Test email sent successfully!")
            return True
        except Exception as e:
            print(f"Error sending test email: {str(e)}")
            import traceback
            print(traceback.format_exc())
            return False

if __name__ == "__main__":
    # Load environment variables from .env file if python-dotenv is available
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print("Loaded environment variables from .env file")
    except ImportError:
        print("python-dotenv not installed. Using environment variables from system.")
    
    # Send the test email
    success = send_test_email()
    sys.exit(0 if success else 1)