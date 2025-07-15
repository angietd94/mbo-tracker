"""
Slack notifications module for MBO Tracker.

This module handles Slack notifications for MBO-related events with interactive buttons.
"""

import json
import time
import logging
from typing import Dict, Any, Optional
from flask import current_app
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

logger = logging.getLogger(__name__)

# Global cache for deduplication
_message_cache = {}

def _is_duplicate_message(channel: str, mbo_id: int, event_type: str) -> bool:
    """Check if this message was sent recently to prevent spam."""
    cache_key = f"{channel}:{mbo_id}:{event_type}"
    current_time = time.time()
    
    if cache_key in _message_cache:
        last_sent = _message_cache[cache_key]
        if current_time - last_sent < 60:  # 60 seconds cooldown
            return True
    
    _message_cache[cache_key] = current_time
    return False

def _get_slack_client() -> Optional[WebClient]:
    """Get configured Slack client."""
    try:
        bot_token = current_app.config.get('SLACK_BOT_TOKEN')
        if not bot_token:
            logger.error("SLACK_BOT_TOKEN not configured")
            return None
        
        return WebClient(token=bot_token)
    except Exception as e:
        logger.error(f"Failed to create Slack client: {str(e)}")
        return None

def _get_user_id_by_email(client: WebClient, email: str) -> Optional[str]:
    """
    Look up Slack user ID by email address.
    
    Args:
        client: Slack WebClient instance
        email: Email address to look up
        
    Returns:
        str: Slack user ID if found, None otherwise
    """
    try:
        response = client.users_lookupByEmail(email=email)
        if response["ok"]:
            user_id = response["user"]["id"]
            logger.info(f"Found Slack user ID {user_id} for email {email}")
            return user_id
        else:
            logger.warning(f"Could not find Slack user for email {email}: {response}")
            return None
    except SlackApiError as e:
        logger.warning(f"Email lookup failed for {email}: {e.response['error']}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error looking up email {email}: {str(e)}")
        return None

def _create_mbo_approval_blocks(mbo_data: Dict[str, Any]) -> list:
    """Create Slack Block Kit blocks for MBO approval message."""
    base_url = current_app.config.get('BASE_URL', 'http://localhost:5000')
    mbo_url = f"{base_url}/mbo_details/{mbo_data['id']}"
    
    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "🎯 New MBO Requires Approval"
            }
        },
        {
            "type": "section",
            "fields": [
                {
                    "type": "mrkdwn",
                    "text": f"*Employee:*\n{mbo_data.get('employee_name', 'Unknown')}"
                },
                {
                    "type": "mrkdwn",
                    "text": f"*Title:*\n{mbo_data.get('title', 'No title')}"
                }
            ]
        }
    ]
    
    if mbo_data.get('description'):
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*Description:*\n{mbo_data['description'][:200]}{'...' if len(mbo_data['description']) > 200 else ''}"
            }
        })
    
    # Action buttons
    blocks.extend([
        {
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "✅ Approve"
                    },
                    "style": "primary",
                    "action_id": "approve_mbo",
                    "value": f"mbo_{mbo_data['id']}"
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "❌ Decline"
                    },
                    "style": "danger",
                    "action_id": "decline_mbo",
                    "value": f"mbo_{mbo_data['id']}"
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "👀 View Details"
                    },
                    "url": mbo_url
                }
            ]
        },
        {
            "type": "divider"
        },
        {
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": f"MBO ID: {mbo_data['id']} | <{mbo_url}|View in MBO Tracker>"
                }
            ]
        }
    ])
    
    return blocks

def _create_simple_notification_blocks(mbo_data: Dict[str, Any], event_type: str) -> list:
    """Create simple notification blocks for non-interactive messages."""
    base_url = current_app.config.get('BASE_URL', 'http://localhost:5000')
    mbo_url = f"{base_url}/mbo_details/{mbo_data['id']}"
    
    if event_type == 'mbo_approved':
        emoji = "✅"
        title = "MBO Approved!"
        message = f"Your MBO '{mbo_data.get('title', 'Unknown')}' has been approved by your manager."
    elif event_type == 'mbo_rejected':
        emoji = "❌"
        title = "MBO Declined"
        message = f"Your MBO '{mbo_data.get('title', 'Unknown')}' was declined by your manager."
    else:
        emoji = "📋"
        title = "MBO Update"
        message = f"Your MBO '{mbo_data.get('title', 'Unknown')}' has been updated."
    
    return [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": f"{emoji} {title}"
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": message
            },
            "accessory": {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "View Details"
                },
                "url": mbo_url
            }
        },
        {
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": f"MBO ID: {mbo_data['id']} | <{mbo_url}|View in MBO Tracker>"
                }
            ]
        }
    ]

def send_slack_notification(event_type: str, mbo_data) -> bool:
    """
    Send Slack notification based on event type.
    
    Args:
        event_type: Type of event ('mbo_created', 'mbo_approved', 'mbo_rejected', 'new_mbo')
        mbo_data: Dictionary containing MBO information OR MBO object
        
    Returns:
        bool: True if notification was sent successfully
    """
    try:
        client = _get_slack_client()
        if not client:
            logger.error("Slack client not available")
            return False
        
        # Convert MBO object to dictionary if needed
        if hasattr(mbo_data, 'id'):  # It's an MBO object
            mbo_obj = mbo_data
            mbo_data = {
                'id': mbo_obj.id,
                'title': mbo_obj.title,
                'description': mbo_obj.description,
                'employee_name': mbo_obj.creator.get_full_name() if mbo_obj.creator else 'Unknown',
                'employee_slack_id': mbo_obj.creator.email if mbo_obj.creator else None,
                'manager_slack_id': mbo_obj.creator.manager.email if mbo_obj.creator and mbo_obj.creator.manager else None
            }
        
        recipients = []
        
        # Determine recipients based on event type (using email addresses)
        if event_type in ['mbo_created', 'new_mbo']:
            # Send to manager (interactive), employee (notification), and Angelica (BCC)
            manager_email = mbo_data.get('manager_slack_id')  # This contains email
            if manager_email:
                manager_user_id = _get_user_id_by_email(client, manager_email)
                if manager_user_id:
                    recipients.append(('manager', manager_user_id, True))  # Interactive
                else:
                    logger.warning(f"Could not find Slack user for manager email: {manager_email}")
            
            employee_email = mbo_data.get('employee_slack_id')  # This contains email
            if employee_email:
                employee_user_id = _get_user_id_by_email(client, employee_email)
                if employee_user_id:
                    recipients.append(('employee', employee_user_id, False))  # Simple notification
                else:
                    logger.warning(f"Could not find Slack user for employee email: {employee_email}")
            
            # Add Angelica as BCC (using direct ID from config)
            angelica_id = current_app.config.get('SLACK_ANGELICA_ID')
            if angelica_id and angelica_id != 'U01234567890':  # Skip if placeholder
                recipients.append(('angelica', angelica_id, True))  # Interactive (BCC copy)
            else:
                # Fallback: try to find Angelica by email
                angelica_user_id = _get_user_id_by_email(client, 'atdughetti@snaplogic.com')
                if angelica_user_id:
                    recipients.append(('angelica', angelica_user_id, True))
                
        elif event_type == 'mbo_approved':
            # Send only to employee
            employee_email = mbo_data.get('employee_slack_id')  # This contains email
            if employee_email:
                employee_user_id = _get_user_id_by_email(client, employee_email)
                if employee_user_id:
                    recipients.append(('employee', employee_user_id, False))
                else:
                    logger.warning(f"Could not find Slack user for employee email: {employee_email}")
                
        elif event_type == 'mbo_rejected':
            # Send only to employee
            employee_email = mbo_data.get('employee_slack_id')  # This contains email
            if employee_email:
                employee_user_id = _get_user_id_by_email(client, employee_email)
                if employee_user_id:
                    recipients.append(('employee', employee_user_id, False))
                else:
                    logger.warning(f"Could not find Slack user for employee email: {employee_email}")
        
        if not recipients:
            logger.warning(f"No Slack recipients found for event {event_type}")
            return False
        
        success_count = 0
        
        for recipient_type, channel, is_interactive in recipients:
            try:
                # Check for duplicates
                if _is_duplicate_message(channel, mbo_data['id'], event_type):
                    logger.info(f"Skipping duplicate message to {channel} for MBO {mbo_data['id']}")
                    continue
                
                # Create appropriate blocks
                if is_interactive and event_type == 'mbo_created':
                    blocks = _create_mbo_approval_blocks(mbo_data)
                    text = f"New MBO from {mbo_data.get('employee_name', 'Unknown')} requires approval"
                else:
                    blocks = _create_simple_notification_blocks(mbo_data, event_type)
                    text = f"MBO notification for {mbo_data.get('title', 'Unknown')}"
                
                # Send message
                response = client.chat_postMessage(
                    channel=channel,
                    text=text,
                    blocks=blocks
                )
                
                if response["ok"]:
                    logger.info(f"Slack message sent to {channel} ({recipient_type}) for MBO {mbo_data['id']}")
                    success_count += 1
                else:
                    logger.error(f"Failed to send Slack message to {channel}: {response}")
                    
            except SlackApiError as e:
                logger.error(f"Slack API error sending to {channel}: {e.response['error']}")
            except Exception as e:
                logger.error(f"Error sending Slack message to {channel}: {str(e)}")
        
        if success_count > 0:
            logger.info(f"Slack notifications sent: event={event_type}, mbo_id={mbo_data['id']}, recipients={success_count}/{len(recipients)}")
            return True
        else:
            logger.error(f"Failed to send any Slack notifications for event {event_type}")
            return False
            
    except Exception as e:
        logger.error(f"Error in send_slack_notification: {str(e)}")
        return False