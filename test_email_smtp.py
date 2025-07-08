#!/usr/bin/env python3
"""
Test script to verify SMTP email functionality with Office365.
"""
import os
import sys
import ssl
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✓ Loaded environment variables from .env file")
except ImportError:
    print("⚠ python-dotenv not installed. Using system environment variables.")

# SMTP Configuration
SMTP_HOST = "smtp.office365.com"
SMTP_PORT = 587
SMTP_USERNAME = os.environ.get('MAIL_USERNAME', 'notificationsmbo@snaplogic.com')
SMTP_PASSWORD = os.environ.get('MAIL_PASSWORD', '')
SENDER = "notificationsmbo@snaplogic.com"

def send_test_email():
    """Send a test email to verify SMTP configuration."""
    
    print(f"🔧 SMTP Configuration:")
    print(f"   Host: {SMTP_HOST}")
    print(f"   Port: {SMTP_PORT}")
    print(f"   Username: {SMTP_USERNAME}")
    print(f"   Password: {'*' * len(SMTP_PASSWORD) if SMTP_PASSWORD else 'NOT SET'}")
    print()
    
    if not SMTP_PASSWORD:
        print("❌ ERROR: SMTP_PASSWORD not set in environment variables")
        return False
    
    # Test email details
    to_email = "notificationsmbo@snaplogic.com"  # Send to ourselves for testing
    subject = "[TEST] MBO Tracker SMTP Configuration Test"
    
    # Create message
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = SENDER
    msg["To"] = to_email
    msg["Cc"] = SENDER  # CC to ourselves
    
    # Email content
    html_body = """
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #e9ecef; border-radius: 5px;">
        <div style="text-align: center; margin-bottom: 20px;">
            <img src="https://www.snaplogic.com/wp-content/themes/snaplogic-2022/assets/images/snaplogic-logo.svg" alt="SnapLogic Logo" style="height: 50px;">
        </div>
        <h2 style="color: #0046ad; margin-bottom: 20px;">🧪 SMTP Test Email</h2>
        <p>Hello,</p>
        <p>This is a test email to verify that the MBO Tracker SMTP configuration is working correctly with Office365.</p>
        
        <div style="background-color: #d4edda; padding: 15px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #28a745;">
            <h3 style="margin-top: 0; color: #155724;">✅ Configuration Details</h3>
            <p><strong>SMTP Server:</strong> smtp.office365.com:587</p>
            <p><strong>Authentication:</strong> Enabled</p>
            <p><strong>TLS:</strong> Enabled</p>
            <p><strong>From:</strong> notificationsmbo@snaplogic.com</p>
        </div>
        
        <p>If you received this email, the SMTP configuration is working correctly!</p>
        
        <p style="margin-top: 30px; color: #6c757d; font-size: 0.9em;">
            This is a test message from the SnapLogic MBO Tracker.<br>
            Sent from: notificationsmbo@snaplogic.com
        </p>
    </div>
    """
    
    text_body = """
    SMTP Test Email
    
    Hello,
    
    This is a test email to verify that the MBO Tracker SMTP configuration is working correctly with Office365.
    
    Configuration Details:
    - SMTP Server: smtp.office365.com:587
    - Authentication: Enabled
    - TLS: Enabled
    - From: notificationsmbo@snaplogic.com
    
    If you received this email, the SMTP configuration is working correctly!
    
    This is a test message from the SnapLogic MBO Tracker.
    Sent from: notificationsmbo@snaplogic.com
    """
    
    # Attach text and HTML parts
    msg.attach(MIMEText(text_body, "plain", "utf-8"))
    msg.attach(MIMEText(html_body, "html", "utf-8"))
    
    try:
        print("🔌 Connecting to SMTP server...")
        
        # Create SSL context
        context = ssl.create_default_context()
        
        # Connect to SMTP server
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=10) as server:
            print(f"✓ Connected to {SMTP_HOST}:{SMTP_PORT}")
            
            # Start TLS
            server.starttls(context=context)
            print("✓ STARTTLS established")
            
            # Authenticate
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            print("✓ SMTP authentication successful")
            
            # Send email
            recipients = [to_email, SENDER]  # Include CC
            server.sendmail(SENDER, recipients, msg.as_string())
            print(f"✅ Test email sent successfully to {to_email}")
            print(f"📧 Subject: {subject}")
            return True
            
    except Exception as e:
        print(f"❌ Error sending test email: {str(e)}")
        import traceback
        print(f"📋 Full error details:")
        print(traceback.format_exc())
        return False

if __name__ == "__main__":
    print("🚀 Starting MBO Tracker SMTP Test")
    print("=" * 50)
    
    success = send_test_email()
    
    print("=" * 50)
    if success:
        print("🎉 SMTP test completed successfully!")
        print("📬 Check your email inbox for the test message.")
    else:
        print("💥 SMTP test failed!")
        print("🔍 Please check your SMTP configuration and credentials.")
    
    sys.exit(0 if success else 1)