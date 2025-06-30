"""
Test script to trigger MBO notifications.
"""
import os
import sys
from flask import Flask
from app import db
from app.models import User, MBO
from app.notifications import send_notification

def test_notifications():
    """Test all notification types."""
    try:
        # Find a user with a manager
        user = User.query.filter(User.manager_id.isnot(None)).first()
        if not user:
            print("No user with a manager found. Cannot test notifications.")
            return False
            
        print(f"Found user: {user.first_name} {user.last_name} (ID: {user.id})")
        print(f"Manager: {user.get_manager_name()} (ID: {user.manager_id})")
        
        # Create a test MBO
        test_mbo = MBO(
            title="Test MBO for Notifications",
            description="This is a test MBO created to test the notification system.",
            mbo_type="Learning and Certification",
            user_id=user.id,
            progress_status="In progress",
            approval_status="Pending Approval"
        )
        
        # Add to database
        db.session.add(test_mbo)
        db.session.commit()
        print(f"Created test MBO with ID: {test_mbo.id}")
        
        # Test new MBO notification
        print("\nTesting new MBO notification...")
        send_notification('new_mbo', test_mbo)
        
        # Test MBO finished notification
        print("\nTesting MBO finished notification...")
        test_mbo.progress_status = "FINISHED"
        db.session.commit()
        send_notification('mbo_finished', test_mbo)
        
        # Test MBO updated notification
        print("\nTesting MBO updated notification...")
        test_mbo.approval_status = "Approved"
        db.session.commit()
        send_notification('mbo_updated', test_mbo)
        
        print("\nAll notification tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"Error testing notifications: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return False

if __name__ == "__main__":
    # Import Flask app
    from app import app
    
    # Run the test within the app context
    with app.app_context():
        success = test_notifications()
        sys.exit(0 if success else 1)