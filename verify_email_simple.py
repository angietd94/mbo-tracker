#!/usr/bin/env python3
"""
Simple email verification script for MBO Tracker.
Tests SMTP connectivity and email sending.
"""

import os
import sys

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

from app import app
from app.utils.email import send_mail

def main():
    """Test email functionality."""
    with app.app_context():
        try:
            print("=== EMAIL VERIFICATION TEST ===")
            print("Testing SMTP connectivity and email sending...")
            
            # Send test email
            test_body = "This is a test email to verify SMTP connectivity and email functionality."
            send_mail(
                to=['atdughetti@snaplogic.com'],
                cc=['notificationsmbo@snaplogic.com'],
                subject="MBO Tracker Email Verification Test",
                text_body=test_body,
                html_body=f"<p>{test_body}</p>"
            )
            
            print("EMAIL OK - Test email sent successfully")
            return 0
            
        except Exception as e:
            print(f"EMAIL FAILED - Error: {str(e)}")
            return 1

if __name__ == "__main__":
    exit(main())