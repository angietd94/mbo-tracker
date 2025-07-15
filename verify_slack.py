#!/usr/bin/env python3
"""
Slack verification script for MBO Tracker.
Sends a test message via Slack and verifies delivery.
"""

import os
import sys
import uuid
import time
import logging
from datetime import datetime

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

from app import app
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

def main():
    """Send test Slack message and verify delivery."""
    with app.app_context():
        try:
            # Generate unique test message
            test_uuid = str(uuid.uuid4())[:8]
            test_message = f"PING {test_uuid}"
            
            print(f"Sending test Slack message: {test_message}")
            
            # Get Slack client
            bot_token = app.config.get('SLACK_BOT_TOKEN')
            if not bot_token:
                print("ERROR: SLACK_BOT_TOKEN not configured")
                return 1
            
            client = WebClient(token=bot_token)
            
            # Test channel - try to send to atdughetti@snaplogic.com
            try:
                # Look up user by email
                response = client.users_lookupByEmail(email='atdughetti@snaplogic.com')
                if not response["ok"]:
                    print(f"ERROR: Could not find Slack user for atdughetti@snaplogic.com")
                    return 1
                
                user_id = response["user"]["id"]
                print(f"Found Slack user ID: {user_id}")
                
            except SlackApiError as e:
                print(f"ERROR: Slack API error looking up user: {e.response['error']}")
                return 1
            
            # Send test message
            try:
                response = client.chat_postMessage(
                    channel=user_id,
                    text=test_message,
                    blocks=[
                        {
                            "type": "section",
                            "text": {
                                "type": "mrkdwn",
                                "text": f"🧪 *Test Message*\n{test_message}\n\nThis is a test of the MBO Tracker Slack integration."
                            }
                        }
                    ]
                )
                
                if not response["ok"]:
                    print(f"ERROR: Failed to send Slack message: {response}")
                    return 1
                
                message_ts = response["ts"]
                print(f"Test message sent successfully (ts: {message_ts})")
                
            except SlackApiError as e:
                print(f"ERROR: Slack API error sending message: {e.response['error']}")
                return 1
            
            # Wait for message to be delivered
            print("Waiting 3 seconds for message delivery...")
            time.sleep(3)
            
            # Verify message was delivered by checking conversation history
            try:
                # Get recent messages from the DM
                history_response = client.conversations_history(
                    channel=user_id,
                    limit=10
                )
                
                if not history_response["ok"]:
                    print(f"ERROR: Could not retrieve conversation history")
                    return 1
                
                # Look for our test message
                messages = history_response["messages"]
                found_message = False
                
                for message in messages:
                    if message.get("text") == test_message and message.get("ts") == message_ts:
                        found_message = True
                        break
                
                if found_message:
                    print("SLACK OK")
                    return 0
                else:
                    print(f"ERROR: Test message not found in conversation history")
                    print(f"Recent messages: {[msg.get('text', 'No text')[:50] for msg in messages[:3]]}")
                    return 1
                    
            except SlackApiError as e:
                print(f"ERROR: Could not verify message delivery: {e.response['error']}")
                return 1
                
        except Exception as e:
            print(f"ERROR: {str(e)}")
            import traceback
            traceback.print_exc()
            return 1

if __name__ == "__main__":
    exit(main())