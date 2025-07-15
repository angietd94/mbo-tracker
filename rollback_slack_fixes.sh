#!/bin/bash
# Rollback script for Slack notification fixes
# Run this script to revert all changes made to fix Slack notifications

echo "🔄 Rolling back Slack notification fixes..."
echo "================================================"

# Backup current files before rollback
echo "📦 Creating backup of current files..."
mkdir -p /tmp/slack_fix_backup_$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/tmp/slack_fix_backup_$(date +%Y%m%d_%H%M%S)"

cp mbo-tracker/app/notifications.py "$BACKUP_DIR/notifications.py.fixed" 2>/dev/null
cp mbo-tracker/app/notifications/slack_improved.py "$BACKUP_DIR/slack_improved.py.fixed" 2>/dev/null
cp mbo-tracker/app/models.py "$BACKUP_DIR/models.py.fixed" 2>/dev/null

echo "✅ Current files backed up to: $BACKUP_DIR"

# Rollback notifications.py - comment out Slack import and fix function calls
echo "🔄 Rolling back app/notifications.py..."
cat > mbo-tracker/app/notifications.py << 'EOF'
import logging
import smtplib
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
from flask import current_app, render_template
from sqlalchemy import event
from sqlalchemy.orm import Session
from app.models import MBO, User
from app.email import send_email

logger = logging.getLogger(__name__)

# Check if Slack is available
try:
    # from app.notifications.slack_improved import send_slack_notification  # COMMENTED OUT - ORIGINAL STATE
    SLACK_AVAILABLE = False  # ORIGINAL STATE
    logger.info("Slack notifications disabled")
except ImportError as e:
    SLACK_AVAILABLE = False
    logger.warning(f"Slack not available: {e}")

def send_mbo_notification(mbo, event_type):
    """Send notifications for MBO events via email and Slack"""
    try:
        logger.info(f"Sending {event_type} notification for MBO {mbo.id}")
        
        # Send email notification
        send_email_notification(mbo, event_type)
        
        # Send Slack notification (if available)
        if SLACK_AVAILABLE:
            try:
                # ORIGINAL BROKEN FUNCTION CALL - 3 parameters instead of 2
                send_slack_notification(event_type, mbo, current_app.config)
                logger.info(f"Slack notification sent: event={event_type}, mbo_id={mbo.id}")
            except Exception as slack_error:
                logger.error(f"Failed to send Slack notification: {str(slack_error)}")
        
    except Exception as e:
        logger.error(f"Error sending {event_type} notification for MBO {mbo.id}: {str(e)}")

def send_email_notification(mbo, event_type):
    """Send email notification for MBO events"""
    try:
        if event_type == 'created':
            # Send to manager for approval
            if mbo.creator.manager:
                subject = f"[MBO] New MBO from {mbo.creator.get_full_name()} requires approval"
                template = 'email/mbo_approval_request.html'
                recipients = [mbo.creator.manager.email]
                
                send_email(
                    recipients=recipients,
                    subject=subject,
                    template=template,
                    mbo=mbo,
                    employee=mbo.creator,
                    manager=mbo.creator.manager
                )
                logger.info(f"Approval email sent to manager: {mbo.creator.manager.email}")
            
            # Send confirmation to employee
            subject = f"[MBO] Your MBO '{mbo.title}' has been submitted"
            template = 'email/mbo_created.html'
            recipients = [mbo.creator.email]
            
            send_email(
                recipients=recipients,
                subject=subject,
                template=template,
                mbo=mbo,
                employee=mbo.creator
            )
            logger.info(f"Confirmation email sent to employee: {mbo.creator.email}")
            
        elif event_type == 'approved':
            # Send to employee
            subject = f"[MBO] Your MBO '{mbo.title}' has been approved"
            template = 'email/mbo_approved.html'
            recipients = [mbo.creator.email]
            
            send_email(
                recipients=recipients,
                subject=subject,
                template=template,
                mbo=mbo,
                employee=mbo.creator
            )
            logger.info(f"Approval notification sent to: {mbo.creator.email}")
            
        elif event_type == 'declined':
            # Send to employee
            subject = f"[MBO] Your MBO '{mbo.title}' has been declined"
            template = 'email/mbo_declined.html'
            recipients = [mbo.creator.email]
            
            send_email(
                recipients=recipients,
                subject=subject,
                template=template,
                mbo=mbo,
                employee=mbo.creator
            )
            logger.info(f"Decline notification sent to: {mbo.creator.email}")
            
    except Exception as e:
        logger.error(f"Error sending email notification: {str(e)}")

# Event listeners for automatic notifications
@event.listens_for(MBO, 'after_insert')
def mbo_created_listener(mapper, connection, target):
    """Triggered when a new MBO is created"""
    try:
        # Get a new session for this operation
        from app import db
        with db.session() as session:
            # Re-query the MBO to ensure we have all relationships loaded
            mbo = session.get(MBO, target.id)
            if mbo:
                # ORIGINAL BROKEN CODE - calling with wrong parameters
                send_mbo_notification(mbo, 'created', session)  # 3 params instead of 2
                logger.info(f"MBO created notification triggered for MBO {mbo.id}")
            else:
                logger.error(f"Could not find MBO {target.id} for notification")
    except Exception as e:
        logger.error(f"Error in MBO created listener: {str(e)}")

@event.listens_for(MBO, 'after_update')
def mbo_updated_listener(mapper, connection, target):
    """Triggered when an MBO is updated"""
    try:
        # Check if status changed to approved or declined
        if hasattr(target, '_sa_instance_state'):
            history = target._sa_instance_state.attrs.status.history
            if history.has_changes():
                old_status = history.deleted[0] if history.deleted else None
                new_status = target.status
                
                if old_status != new_status:
                    from app import db
                    with db.session() as session:
                        mbo = session.get(MBO, target.id)
                        if mbo:
                            if new_status == 'approved':
                                send_mbo_notification(mbo, 'approved')
                                logger.info(f"MBO approved notification triggered for MBO {mbo.id}")
                            elif new_status == 'declined':
                                send_mbo_notification(mbo, 'declined')
                                logger.info(f"MBO declined notification triggered for MBO {mbo.id}")
    except Exception as e:
        logger.error(f"Error in MBO updated listener: {str(e)}")

def init_notifications():
    """Initialize notification system"""
    logger.info("Notifications module initialized and event listeners registered")
EOF

echo "✅ Rolled back app/notifications.py"

# Rollback models.py - remove slack_id field
echo "🔄 Rolling back app/models.py..."
sed -i '/slack_id = db.Column(db.String(50), nullable=True)/d' mbo-tracker/app/models.py
echo "✅ Rolled back app/models.py (removed slack_id field)"

# Rollback slack_improved.py to original broken state
echo "🔄 Rolling back app/notifications/slack_improved.py..."
cat > mbo-tracker/app/notifications/slack_improved.py << 'EOF'
import os
import logging
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

logger = logging.getLogger(__name__)

def send_slack_notification(event_type, mbo_data):
    """
    Send Slack notification based on event type and MBO data
    
    Args:
        event_type (str): Type of event ('mbo_created', 'mbo_approved', etc.)
        mbo_data (dict): Dictionary containing MBO information including slack_id fields
    """
    try:
        # Get Slack token from environment
        slack_token = os.getenv('SLACK_BOT_TOKEN')
        if not slack_token:
            logger.error("SLACK_BOT_TOKEN not found in environment variables")
            return False
            
        client = WebClient(token=slack_token)
        
        # Determine recipients based on event type
        recipients = []
        
        if event_type == 'mbo_created':
            # Notify employee and manager
            if mbo_data.get('employee_slack_id'):
                recipients.append(mbo_data['employee_slack_id'])
            if mbo_data.get('manager_slack_id'):
                recipients.append(mbo_data['manager_slack_id'])
                
        elif event_type in ['mbo_approved', 'mbo_declined']:
            # Notify employee
            if mbo_data.get('employee_slack_id'):
                recipients.append(mbo_data['employee_slack_id'])
                
        elif event_type == 'mbo_manager_edited':
            # Notify employee
            if mbo_data.get('employee_slack_id'):
                recipients.append(mbo_data['employee_slack_id'])
        
        if not recipients:
            logger.warning(f"No Slack recipients found for event {event_type}")
            return False
            
        # Create message based on event type
        message = _create_message(event_type, mbo_data)
        
        # Send message to each recipient
        success_count = 0
        for recipient in recipients:
            try:
                response = client.chat_postMessage(
                    channel=recipient,
                    text=message,
                    username="MBO Tracker Bot"
                )
                if response["ok"]:
                    success_count += 1
                    logger.info(f"Slack message sent successfully to {recipient}")
                else:
                    logger.error(f"Failed to send Slack message to {recipient}: {response}")
                    
            except SlackApiError as e:
                logger.error(f"Slack API error sending to {recipient}: {e.response['error']}")
            except Exception as e:
                logger.error(f"Unexpected error sending to {recipient}: {str(e)}")
                
        return success_count > 0
        
    except Exception as e:
        logger.error(f"Error in send_slack_notification: {str(e)}")
        return False

def _create_message(event_type, mbo_data):
    """Create appropriate message based on event type"""
    
    if event_type == 'mbo_created':
        return f"📋 New MBO Created: '{mbo_data['title']}' by {mbo_data['employee_name']}"
        
    elif event_type == 'mbo_approved':
        return f"✅ MBO Approved: '{mbo_data['title']}' has been approved!"
        
    elif event_type == 'mbo_declined':
        return f"❌ MBO Declined: '{mbo_data['title']}' has been declined."
        
    elif event_type == 'mbo_manager_edited':
        return f"✏️ MBO Updated: '{mbo_data['title']}' has been edited by your manager."
        
    else:
        return f"📢 MBO Update: '{mbo_data['title']}'"
EOF

echo "✅ Rolled back app/notifications/slack_improved.py"

# Remove test files
echo "🧹 Cleaning up test files..."
rm -f mbo-tracker/verify_slack.py
rm -f mbo-tracker/verify_slack_final.py
rm -f mbo-tracker/test_email_slack.py
echo "✅ Removed test files"

# Restart the application
echo "🔄 Restarting MBO Tracker service..."
sudo systemctl restart mbo-tracker

echo ""
echo "✅ Rollback completed successfully!"
echo "================================================"
echo "📋 Summary of changes reverted:"
echo "  • Commented out Slack import in notifications.py"
echo "  • Restored original broken function signatures"
echo "  • Removed slack_id field from User model"
echo "  • Restored original slack_improved.py expecting Slack IDs"
echo "  • Removed all test and verification scripts"
echo "  • Restarted the application"
echo ""
echo "⚠️  Note: The application is now back to its original broken state"
echo "   where Slack notifications will not work due to missing slack_id fields."
echo ""
echo "📁 Fixed files backed up to: $BACKUP_DIR"
echo "   You can restore the fixes by copying these files back if needed."
EOF
chmod +x mbo-tracker/rollback_slack_fixes.sh