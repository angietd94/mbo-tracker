#!/usr/bin/env python3
"""
Final Slack Notification Verification Script for MBO Tracker

This script tests the complete Slack notification functionality by:
1. Verifying Slack configuration and connectivity
2. Sending a test notification with unique ID
3. Confirming message delivery via Slack API
4. Providing clear PASS/FAIL status

Usage:
    python verify_slack_final.py
"""

import os
import sys
import uuid
import time
from datetime import datetime
from typing import Dict, Any, Optional

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

def load_environment():
    """Load environment variables from .env file."""
    try:
        from dotenv import load_dotenv
        env_path = os.path.join(os.path.dirname(__file__), '.env')
        load_dotenv(env_path)
        return True
    except ImportError:
        print("⚠ python-dotenv not available, using system environment variables")
        return True
    except Exception as e:
        print(f"✗ Failed to load environment: {e}")
        return False

def verify_slack_connectivity() -> Dict[str, Any]:
    """Verify Slack API connectivity and bot permissions."""
    try:
        from slack_sdk import WebClient
        from slack_sdk.errors import SlackApiError
        
        bot_token = os.environ.get('SLACK_BOT_TOKEN', '')
        if not bot_token:
            return {'success': False, 'error': 'SLACK_BOT_TOKEN not configured'}
        
        client = WebClient(token=bot_token)
        
        # Test auth
        auth_response = client.auth_test()
        
        return {
            'success': True,
            'client': client,
            'team': auth_response['team'],
            'bot_user': auth_response['user'],
            'bot_id': auth_response['user_id']
        }
        
    except SlackApiError as e:
        return {'success': False, 'error': f"Slack API error: {e.response['error']}"}
    except ImportError:
        return {'success': False, 'error': 'slack_sdk not installed'}
    except Exception as e:
        return {'success': False, 'error': f"Unexpected error: {str(e)}"}

def send_test_notification(client, test_channel: str) -> Dict[str, Any]:
    """Send a test notification and return message details."""
    try:
        test_id = str(uuid.uuid4())[:8]
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')
        
        # Create test message
        test_message = {
            "text": f"PING {test_id}",
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": f"🧪 MBO Tracker Test - PING {test_id}"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"Test notification sent at {timestamp} to verify Slack integration is working correctly."
                    }
                },
                {
                    "type": "context",
                    "elements": [
                        {
                            "type": "mrkdwn",
                            "text": f"Test ID: {test_id} | Status: ✅ Integration Working"
                        }
                    ]
                }
            ]
        }
        
        # Send message
        response = client.chat_postMessage(
            channel=test_channel,
            **test_message
        )
        
        return {
            'success': True,
            'test_id': test_id,
            'timestamp': response['ts'],
            'channel': response['channel'],
            'message_text': f"PING {test_id}"
        }
        
    except Exception as e:
        return {'success': False, 'error': str(e)}

def verify_message_delivery(client, channel: str, test_id: str, message_ts: str) -> bool:
    """Verify that the test message was delivered by checking conversation history."""
    try:
        # Wait a moment for message to be processed
        time.sleep(2)
        
        # Get recent messages from the channel
        response = client.conversations_history(
            channel=channel,
            limit=10,
            oldest=str(float(message_ts) - 10)  # Look 10 seconds before our message
        )
        
        # Check if our test message appears in the history
        for message in response['messages']:
            if message.get('text', '').startswith(f"PING {test_id}"):
                return True
        
        return False
        
    except Exception as e:
        print(f"⚠ Could not verify message delivery: {e}")
        return False

def main():
    """Main verification function."""
    print("MBO Tracker - Final Slack Notification Verification")
    print("=" * 55)
    
    # Load environment
    if not load_environment():
        print("❌ FAILED - Environment configuration error")
        sys.exit(1)
    
    # Verify connectivity
    print("\n🔍 Testing Slack connectivity...")
    connectivity = verify_slack_connectivity()
    
    if not connectivity['success']:
        print(f"❌ FAILED - Slack connectivity: {connectivity['error']}")
        sys.exit(1)
    
    print(f"✓ Connected to Slack workspace: {connectivity['team']}")
    print(f"✓ Bot user: {connectivity['bot_user']} (ID: {connectivity['bot_id']})")
    
    # Get test channel
    test_channel = os.environ.get('SLACK_ANGELICA_ID', '')
    if not test_channel or test_channel == 'U01234567890':
        print("❌ FAILED - SLACK_ANGELICA_ID not properly configured (placeholder value detected)")
        print("Please set SLACK_ANGELICA_ID to a real Slack user ID")
        sys.exit(1)
    
    # Send test notification
    print(f"\n📤 Sending test notification to {test_channel}...")
    send_result = send_test_notification(connectivity['client'], test_channel)
    
    if not send_result['success']:
        print(f"❌ FAILED - Could not send test message: {send_result['error']}")
        sys.exit(1)
    
    print(f"✓ Test message sent successfully")
    print(f"✓ Test ID: {send_result['test_id']}")
    print(f"✓ Message timestamp: {send_result['timestamp']}")
    
    # Verify delivery
    print(f"\n🔍 Verifying message delivery...")
    delivery_verified = verify_message_delivery(
        connectivity['client'],
        send_result['channel'],
        send_result['test_id'],
        send_result['timestamp']
    )
    
    if delivery_verified:
        print(f"✓ Message delivery confirmed")
        print("\n" + "=" * 55)
        print("✅ SLACK OK")
        print("Slack notifications are working correctly!")
        sys.exit(0)
    else:
        print(f"⚠ Could not verify message delivery via API")
        print(f"Please manually check if message 'PING {send_result['test_id']}' was received")
        print("\n" + "=" * 55)
        print("⚠ SLACK PARTIAL")
        print("Message sent but delivery verification failed")
        sys.exit(1)

if __name__ == '__main__':
    main()