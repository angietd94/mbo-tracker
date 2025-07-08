#!/usr/bin/env python3
"""
Test script to debug new MBO notification issues.
"""
import os
import sys
sys.path.insert(0, '/home/ubuntu/mbo-tracker')

from app import app, db
from app.models import User, MBO
from app.notifications import send_notification

def test_new_mbo_notification():
    """Test the new MBO notification functionality."""
    
    with app.app_context():
        print("Testing new MBO notification...")
        
        # Find a user with a manager
        user_with_manager = User.query.filter(User.manager_id.isnot(None)).first()
        if not user_with_manager:
            print("ERROR: No user with manager found in database")
            return
            
        print(f"Found user: {user_with_manager.get_full_name()} (ID: {user_with_manager.id})")
        print(f"Manager: {user_with_manager.manager.get_full_name() if user_with_manager.manager else 'None'}")
        print(f"Manager email: {user_with_manager.manager.email if user_with_manager.manager else 'None'}")
        
        # Create a test MBO
        test_mbo = MBO(
            title="Test MBO for Email Notification",
            description="This is a test MBO to verify email notifications work",
            mbo_type="Learning and Certification",
            user_id=user_with_manager.id,
            progress_status="In progress",
            approval_status="Pending Approval"
        )
        
        # Don't save to database, just test the notification
        print("\nTesting send_notification('new_mbo', test_mbo)...")
        
        try:
            send_notification('new_mbo', test_mbo)
            print("✅ send_notification completed without errors")
        except Exception as e:
            print(f"❌ send_notification failed with error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    test_new_mbo_notification()