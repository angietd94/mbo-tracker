#!/usr/bin/env python3

import os
import sys
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Add the app directory to Python path
sys.path.insert(0, '/home/ubuntu/mbo-tracker')

# Load environment variables
from dotenv import load_dotenv
load_dotenv('/home/ubuntu/mbo-tracker/.env')

def test_smtp_config():
    """Test SMTP configuration with current environment variables"""
    
    # Get SMTP settings from environment
    smtp_server = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    smtp_port = int(os.environ.get('MAIL_PORT', '587'))
    smtp_username = os.environ.get('MAIL_USERNAME', '')
    smtp_password = os.environ.get('MAIL_PASSWORD', '')
    
    print(f"Testing SMTP Configuration:")
    print(f"Server: {smtp_server}")
    print(f"Port: {smtp_port}")
    print(f"Username: {smtp_username}")
    print(f"Password: {'*' * len(smtp_password) if smtp_password else 'NOT SET'}")
    print()
    
    if smtp_password == '<SMTP_PASSWORD>':
        print("❌ MAIL_PASSWORD is still set to placeholder value")
        print("   You need to set a real Gmail App Password in the .env file")
        return False
    
    if not smtp_password:
        print("❌ MAIL_PASSWORD is empty")
        print("   You need to set a Gmail App Password in the .env file")
        return False
    
    try:
        print("Attempting SMTP connection...")
        
        # Create SMTP connection
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        
        print("✅ SMTP connection established")
        print("✅ TLS encryption started")
        
        # Test authentication
        server.login(smtp_username, smtp_password)
        print("✅ SMTP authentication successful")
        
        server.quit()
        print("✅ SMTP connection closed cleanly")
        
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        print(f"❌ SMTP Authentication failed: {e}")
        print("   Check your Gmail App Password")
        return False
    except smtplib.SMTPException as e:
        print(f"❌ SMTP Error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = test_smtp_config()
    sys.exit(0 if success else 1)