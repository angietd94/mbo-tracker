#!/usr/bin/env python3
"""
Test script to actually send a test email and see what happens.
"""
import os
import sys
sys.path.insert(0, '/home/ubuntu/mbo-tracker')

from app import app, db
from app.models import User, MBO
from app.utils.email import send_mail

def test_actual_email_send():
    """Test sending an actual email."""
    
    with app.app_context():
        print("Testing actual email sending...")
        
        # Test basic email sending
        try:
            print("Attempting to send test email...")
            send_mail(
                to="notificationsmbo@snaplogic.com",  # Send to self for testing
                subject="Test Email from MBO Tracker",
                text_body="This is a test email to verify SMTP configuration.",
                html_body="<p>This is a test email to verify SMTP configuration.</p>"
            )
            print("✅ Email sent successfully!")
        except Exception as e:
            print(f"❌ Email sending failed: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    test_actual_email_send()