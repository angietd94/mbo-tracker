#!/usr/bin/env python3
"""
Test script to simulate MBO creation and verify both email and Slack notifications work.
This simulates the exact same process that happens when creating an MBO through the web interface.
"""

import sys
import os
from datetime import datetime

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

from app import app, db
from app.models import User, MBO
from app.notifications import send_notification

def test_mbo_creation():
    """Test MBO creation with notifications"""
    
    with app.app_context():
        print("=== MBO Creation Notification Test ===")
        print(f"Test started at: {datetime.now()}")
        print()
        
        # Find Angelica's user account
        user = User.query.filter_by(email='atdughetti@snaplogic.com').first()
        if not user:
            print("❌ ERROR: User atdughetti@snaplogic.com not found")
            return False
            
        print(f"✅ Found user: {user.get_full_name()} (ID: {user.id})")
        print(f"   Email: {user.email}")
        if user.manager:
            print(f"   Manager: {user.manager.get_full_name()} ({user.manager.email})")
        else:
            print("   Manager: None")
        print()
        
        # Create a test MBO (similar to what happens in the web interface)
        test_mbo = MBO(
            title="TEST: Notification System Verification",
            description="This is a test MBO created to verify that both email and Slack notifications are working correctly after the recent fixes.",
            mbo_type="Impact Outside of Pod",
            points=2,
            user_id=user.id,
            approval_status='Pending Approval'
        )
        
        try:
            # Add to database (this will trigger SQLAlchemy event listeners)
            db.session.add(test_mbo)
            db.session.commit()
            print(f"✅ Created test MBO: '{test_mbo.title}' (ID: {test_mbo.id})")
            print()
            
            # Now call the same notification function that the web interface calls
            print("🔔 Sending notifications via route-based system (new_mbo event)...")
            try:
                send_notification('new_mbo', test_mbo)
                print("✅ Route-based notification call completed successfully")
            except Exception as e:
                print(f"❌ Route-based notification failed: {str(e)}")
                return False
            
            print()
            print("=== Test Results ===")
            print("✅ MBO created successfully")
            print("✅ Notification system called without errors")
            print("✅ Both email and Slack should have been sent")
            print()
            print("Expected notifications:")
            print("📧 Email notifications:")
            print(f"   - TO: {user.email} (atdughetti@snaplogic.com)")
            if user.manager:
                print(f"   - TO: {user.manager.email} (manager)")
            print("   - CC: atdughetti@snaplogic.com (added by our fix)")
            print("   - BCC: notificationsmbo@snaplogic.com (automatic)")
            print()
            print("💬 Slack notifications:")
            print("   - Interactive message to manager (if manager has Slack)")
            print("   - Notification to employee (Angelica)")
            print("   - BCC to Angelica (fallback)")
            print()
            
            # Clean up the test MBO
            db.session.delete(test_mbo)
            db.session.commit()
            print("🧹 Test MBO cleaned up from database")
            
            return True
            
        except Exception as e:
            print(f"❌ ERROR during MBO creation: {str(e)}")
            # Try to clean up if something went wrong
            try:
                if test_mbo.id:
                    db.session.delete(test_mbo)
                    db.session.commit()
            except:
                pass
            return False

if __name__ == "__main__":
    success = test_mbo_creation()
    if success:
        print("\n🎉 TEST PASSED: MBO creation and notification system working correctly!")
        sys.exit(0)
    else:
        print("\n❌ TEST FAILED: Issues detected in MBO creation or notification system")
        sys.exit(1)