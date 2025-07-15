#!/usr/bin/env python3
"""
Test script to verify email-based Slack notifications
"""

import os
import sys
import logging
from flask import Flask
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_env():
    """Load environment variables from .env file"""
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value
        print("✅ Environment variables loaded from .env")
    else:
        print("❌ .env file not found")

def test_slack_email_lookup():
    """Test Slack email lookup functionality"""
    print("\n🔍 Testing Slack Email Lookup...")
    
    # Load environment
    load_env()
    
    # Get Slack token
    slack_token = os.getenv('SLACK_BOT_TOKEN')
    if not slack_token:
        print("❌ SLACK_BOT_TOKEN not found in environment")
        return False
    
    print(f"✅ Slack token found: {slack_token[:10]}...")
    
    # Create Slack client
    try:
        client = WebClient(token=slack_token)
        print("✅ Slack client created")
    except Exception as e:
        print(f"❌ Failed to create Slack client: {e}")
        return False
    
    # Test email addresses from the application
    test_emails = [
        'atdughetti@snaplogic.com',  # Angelica (employee)
        'jarcega@snaplogic.com'     # Manager
    ]
    
    for email in test_emails:
        print(f"\n📧 Testing email lookup for: {email}")
        try:
            response = client.users_lookupByEmail(email=email)
            if response["ok"]:
                user_id = response["user"]["id"]
                user_name = response["user"]["real_name"]
                print(f"✅ Found user: {user_name} (ID: {user_id})")
            else:
                print(f"❌ User not found: {response}")
        except SlackApiError as e:
            print(f"❌ Slack API error: {e.response['error']}")
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
    
    return True

def test_notification_function():
    """Test the notification function with email addresses"""
    print("\n🧪 Testing Notification Function...")
    
    # Create Flask app context
    app = Flask(__name__)
    app.config['SLACK_BOT_TOKEN'] = os.getenv('SLACK_BOT_TOKEN')
    app.config['SLACK_ANGELICA_ID'] = os.getenv('SLACK_ANGELICA_ID', 'U01234567890')
    app.config['BASE_URL'] = 'http://13.37.227.99:5000'
    
    with app.app_context():
        try:
            # Import the notification function
            from notifications.slack_improved import send_slack_notification
            
            # Test data with email addresses
            mbo_data = {
                'id': 999,
                'title': 'Test MBO - Email Lookup',
                'description': 'Testing email-based Slack notifications',
                'employee_name': 'Angelica Tacca Dughetti',
                'employee_slack_id': 'atdughetti@snaplogic.com',  # Email instead of Slack ID
                'manager_slack_id': 'jarcega@snaplogic.com'       # Email instead of Slack ID
            }
            
            print("📤 Sending test notification...")
            result = send_slack_notification('mbo_created', mbo_data)
            
            if result:
                print("✅ Notification sent successfully!")
            else:
                print("❌ Notification failed")
                
            return result
            
        except Exception as e:
            print(f"❌ Error testing notification function: {e}")
            return False

if __name__ == "__main__":
    print("🚀 Starting Email-based Slack Notification Test")
    print("=" * 50)
    
    # Test 1: Email lookup
    lookup_success = test_slack_email_lookup()
    
    # Test 2: Notification function
    if lookup_success:
        notification_success = test_notification_function()
        
        if notification_success:
            print("\n🎉 All tests passed! Email-based Slack notifications are working.")
        else:
            print("\n❌ Notification test failed.")
    else:
        print("\n❌ Email lookup test failed. Skipping notification test.")
    
    print("\n" + "=" * 50)
    print("Test completed.")