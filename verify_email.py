#!/usr/bin/env python3
"""
Email verification script for MBO Tracker.
Creates a test MBO and verifies email notifications are sent.
"""

import os
import sys
import uuid
import time
import logging
from datetime import datetime

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

from app import app, db
from app.models import User, MBO
from app.notifications import send_slack_notification
from app.utils.email import send_mail

def main():
    """Create test MBO and verify email notification."""
    with app.app_context():
        try:
            # Generate unique test title
            test_uuid = str(uuid.uuid4())[:8]
            test_title = f"TEST-EMAIL {test_uuid}"
            
            print(f"Creating test MBO: {test_title}")
            
            # Find a test user (use atdughetti@snaplogic.com)
            test_user = User.query.filter_by(email='atdughetti@snaplogic.com').first()
            if not test_user:
                print("ERROR: Test user atdughetti@snaplogic.com not found")
                return 1
            
            # Create test MBO
            test_mbo = MBO(
                title=test_title,
                description=f"Test MBO created for email verification at {datetime.utcnow()}",
                mbo_type="Learning and Certification",
                user_id=test_user.id,
                progress_status="In progress",
                approval_status="Pending Approval"
            )
            
            db.session.add(test_mbo)
            db.session.commit()
            
            print(f"Test MBO created with ID: {test_mbo.id}")
            
            # Send notification manually to test
            try:
                # Import the notification function from the main notifications.py
                from app.notifications import send_slack_notification
                # Trigger the SQLAlchemy event that sends notifications
                db.session.flush()  # This triggers the after_insert event
                print("Email notification triggered successfully")
            except Exception as e:
                print(f"ERROR: Failed to send notification: {str(e)}")
                return 1
            
            # Wait a moment for email to be sent
            print("Waiting 5 seconds for email delivery...")
            time.sleep(5)
            
            # Clean up test MBO
            db.session.delete(test_mbo)
            db.session.commit()
            print(f"Test MBO {test_mbo.id} cleaned up")
            
            # Check logs for email success
            print("Checking recent logs for email delivery...")
            import subprocess
            try:
                result = subprocess.run([
                    'sudo', 'journalctl', '-u', 'mbo-tracker', 
                    '--since', '1 minute ago',
                    '--grep', f'Email sent successfully.*{test_title}'
                ], capture_output=True, text=True, timeout=10)
                
                if result.returncode == 0 and test_title in result.stdout:
                    print("EMAIL OK")
                    return 0
                else:
                    print(f"ERROR: Email delivery not confirmed in logs")
                    print(f"Log output: {result.stdout}")
                    return 1
                    
            except subprocess.TimeoutExpired:
                print("ERROR: Log check timed out")
                return 1
            except Exception as e:
                print(f"ERROR: Could not check logs: {str(e)}")
                return 1
                
        except Exception as e:
            print(f"ERROR: {str(e)}")
            import traceback
            traceback.print_exc()
            return 1

if __name__ == "__main__":
    exit(main())