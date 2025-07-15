"""
Notifications module for MBO Tracker.

This module handles email and Slack notifications for MBO-related events.
"""
import threading
import logging
import datetime
import os
from flask import render_template, current_app
from flask_sqlalchemy import SQLAlchemy
from app.models import MBO, User
from app.utils.email import send_mail

# Set up logger first
logger = logging.getLogger(__name__)

# Try to import Slack functionality
try:
    from app.notifications.slack_improved import send_slack_notification
    SLACK_AVAILABLE = True
except ImportError:
    SLACK_AVAILABLE = False
    logger.warning("Slack notifications not available - slack_improved module not found")

# Import APScheduler only if enabled
ENABLE_SCHEDULER = os.environ.get('ENABLE_SCHEDULER', 'False').lower() in ['true', 'yes', '1']
if ENABLE_SCHEDULER:
    try:
        from apscheduler.schedulers.background import BackgroundScheduler
        from apscheduler.triggers.cron import CronTrigger
    except ImportError:
        logger.warning("APScheduler not installed. Quarter-end reminders will be disabled.")
        ENABLE_SCHEDULER = False

# Global scheduler
scheduler = None

def notify_mbo(event: str, mbo: MBO, actor: User) -> None:
    """
    Send MBO notification emails based on the event type.
    
    Args:
        event: Event type ('created', 'approved', 'rejected', 'updated')
        mbo: MBO object
        actor: User who triggered the event
    """
    app = current_app._get_current_object()
    base_url = app.config.get('BASE_URL', 'http://localhost:5000')
    
    try:
        if event == 'created':
            # Business rule 1: When a new MBO is created
            # Send email to employee (creator)
            if mbo.creator and mbo.creator.email:
                subject = f"Your MBO '{mbo.title}' is pending manager approval"
                
                html_body = f"""
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #e9ecef; border-radius: 5px;">
                    <h2 style="color: #0046ad; margin-bottom: 20px;">MBO Created Successfully</h2>
                    <p>Hello {mbo.creator.first_name},</p>
                    <p>Your MBO has been created and is now pending manager approval:</p>
                    
                    <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0;">
                        <h3 style="margin-top: 0; color: #0046ad;">{mbo.title}</h3>
                        <p><strong>Type:</strong> {mbo.mbo_type}</p>
                        <p><strong>Points:</strong> {mbo.points}</p>
                        <p><strong>Status:</strong> {mbo.approval_status}</p>
                    </div>
                    
                    <div style="text-align: center; margin-top: 30px;">
                        <a href="{base_url}/mbo_details/{mbo.id}"
                           style="background-color: #0046ad; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">
                            View MBO
                        </a>
                    </div>
                    
                    <p style="margin-top: 30px; color: #6c757d; font-size: 0.9em;">
                        This is an automated message from the SnapLogic MBO Tracker.
                    </p>
                </div>
                """
                
                text_body = f"""
                MBO Created Successfully
                
                Hello {mbo.creator.first_name},
                
                Your MBO has been created and is now pending manager approval:
                
                Title: {mbo.title}
                Type: {mbo.mbo_type}
                Points: {mbo.points}
                Status: {mbo.approval_status}
                
                View MBO: {base_url}/mbo_details/{mbo.id}
                
                This is an automated message from the SnapLogic MBO Tracker.
                """
                
                # Send email with CC to notifications and atdughetti@snaplogic.com
                send_mail([mbo.creator.email], subject, text_body, html_body, cc=['notificationsmbo@snaplogic.com', 'atdughetti@snaplogic.com'])
                logger.info(f"Email notification sent: event={event}, mbo_id={mbo.id}, to={mbo.creator.email}, cc=notificationsmbo@snaplogic.com,atdughetti@snaplogic.com, subject={subject}")
                
                # Send Slack notification to employee
                if SLACK_AVAILABLE:
                    try:
                        mbo_data = {
                            'id': mbo.id,
                            'title': mbo.title,
                            'description': mbo.description,
                            'employee_name': mbo.creator.get_full_name(),
                            'employee_slack_id': mbo.creator.email,
                            'manager_slack_id': mbo.creator.manager.email if mbo.creator.manager else None
                        }
                        send_slack_notification('mbo_created', mbo_data)
                        logger.info(f"Slack notification sent: event=mbo_created, mbo_id={mbo.id}, to={mbo.creator.get_full_name()}")
                    except Exception as slack_error:
                        logger.error(f"Failed to send Slack notification to employee: {str(slack_error)}")
            
            # Send email to manager
            if mbo.creator and mbo.creator.manager and mbo.creator.manager.email:
                manager = mbo.creator.manager
                subject = f"Approval needed: '{mbo.creator.get_full_name()}' has created new MBO"
                
                html_body = f"""
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #e9ecef; border-radius: 5px;">
                    <h2 style="color: #0046ad; margin-bottom: 20px;">New MBO Requires Approval</h2>
                    <p>Hello {manager.first_name},</p>
                    <p>{mbo.creator.get_full_name()} has created a new MBO that requires your approval:</p>
                    
                    <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0;">
                        <h3 style="margin-top: 0; color: #0046ad;">{mbo.title}</h3>
                        <p><strong>Employee:</strong> {mbo.creator.get_full_name()}</p>
                        <p><strong>Type:</strong> {mbo.mbo_type}</p>
                        <p><strong>Points:</strong> {mbo.points}</p>
                        <p><strong>Description:</strong> {mbo.description}</p>
                    </div>
                    
                    <div style="text-align: center; margin-top: 30px;">
                        <a href="{base_url}/mbo_details/{mbo.id}"
                           style="background-color: #0046ad; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">
                            Review & Approve MBO
                        </a>
                    </div>
                    
                    <p style="margin-top: 30px; color: #6c757d; font-size: 0.9em;">
                        This is an automated message from the SnapLogic MBO Tracker.
                    </p>
                </div>
                """
                
                text_body = f"""
                New MBO Requires Approval
                
                Hello {manager.first_name},
                
                {mbo.creator.get_full_name()} has created a new MBO that requires your approval:
                
                Title: {mbo.title}
                Employee: {mbo.creator.get_full_name()}
                Type: {mbo.mbo_type}
                Points: {mbo.points}
                Description: {mbo.description}
                
                Review & Approve MBO: {base_url}/mbo_details/{mbo.id}
                
                This is an automated message from the SnapLogic MBO Tracker.
                """
                
                # Send email with CC to notifications and atdughetti@snaplogic.com
                send_mail([manager.email], subject, text_body, html_body, cc=['notificationsmbo@snaplogic.com', 'atdughetti@snaplogic.com'])
                logger.info(f"Email notification sent: event={event}, mbo_id={mbo.id}, to={manager.email}, cc=notificationsmbo@snaplogic.com,atdughetti@snaplogic.com, subject={subject}")
                
                # Send Slack notification to manager
                try:
                    mbo_data = {
                        'id': mbo.id,
                        'title': mbo.title,
                        'description': mbo.description,
                        'employee_name': mbo.creator.get_full_name(),
                        'employee_slack_id': getattr(mbo.creator, 'slack_id', None),
                        'manager_slack_id': getattr(manager, 'slack_id', None)
                    }
                    send_slack_notification('mbo_created', mbo_data)
                    logger.info(f"Slack notification sent: event=mbo_created, mbo_id={mbo.id}, to={manager.get_full_name()}")
                except Exception as slack_error:
                    logger.error(f"Failed to send Slack notification to manager: {str(slack_error)}")
                
        elif event in ['approved', 'rejected']:
            # Business rule 2: When an MBO is approved or rejected
            # Send email only to the employee
            if mbo.creator and mbo.creator.email:
                status_text = event.upper()
                subject = f"Your MBO '{mbo.title}' was {status_text}"
                
                html_body = f"""
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #e9ecef; border-radius: 5px;">
                    <h2 style="color: #0046ad; margin-bottom: 20px;">MBO {status_text}</h2>
                    <p>Hello {mbo.creator.first_name},</p>
                    <p>Your MBO has been <strong>{status_text.lower()}</strong> by your manager:</p>
                    
                    <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0;">
                        <h3 style="margin-top: 0; color: #0046ad;">{mbo.title}</h3>
                        <p><strong>Type:</strong> {mbo.mbo_type}</p>
                        <p><strong>Points:</strong> {mbo.points}</p>
                        <p><strong>Status:</strong> {mbo.approval_status}</p>
                    </div>
                    
                    <div style="text-align: center; margin-top: 30px;">
                        <a href="{base_url}/mbo_details/{mbo.id}"
                           style="background-color: #0046ad; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">
                            View MBO
                        </a>
                    </div>
                    
                    <p style="margin-top: 30px; color: #6c757d; font-size: 0.9em;">
                        This is an automated message from the SnapLogic MBO Tracker.
                    </p>
                </div>
                """
                
                text_body = f"""
                MBO {status_text}
                
                Hello {mbo.creator.first_name},
                
                Your MBO has been {status_text.lower()} by your manager:
                
                Title: {mbo.title}
                Type: {mbo.mbo_type}
                Points: {mbo.points}
                Status: {mbo.approval_status}
                
                View MBO: {base_url}/mbo_details/{mbo.id}
                
                This is an automated message from the SnapLogic MBO Tracker.
                """
                
                # Send email with CC to notifications and atdughetti@snaplogic.com
                send_mail([mbo.creator.email], subject, text_body, html_body, cc=['notificationsmbo@snaplogic.com', 'atdughetti@snaplogic.com'])
                logger.info(f"Email notification sent: event={event}, mbo_id={mbo.id}, to={mbo.creator.email}, cc=notificationsmbo@snaplogic.com,atdughetti@snaplogic.com, subject={subject}")
                
                # Send Slack notification to employee
                try:
                    slack_event = 'mbo_approved' if event == 'approved' else 'mbo_rejected'
                    mbo_data = {
                        'id': mbo.id,
                        'title': mbo.title,
                        'description': mbo.description,
                        'employee_name': mbo.creator.get_full_name(),
                        'employee_slack_id': getattr(mbo.creator, 'slack_id', None),
                        'manager_slack_id': getattr(mbo.creator.manager, 'slack_id', None) if mbo.creator.manager else None
                    }
                    send_slack_notification(slack_event, mbo_data)
                    logger.info(f"Slack notification sent: event={slack_event}, mbo_id={mbo.id}, to={mbo.creator.get_full_name()}")
                except Exception as slack_error:
                    logger.error(f"Failed to send Slack notification for {event}: {str(slack_error)}")
                
        elif event == 'updated':
            # Business rule 3: When an MBO is updated in any way after creation
            # Send email only to the employee
            if mbo.creator and mbo.creator.email:
                subject = f"Your MBO '{mbo.title}' was updated"
                
                html_body = f"""
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #e9ecef; border-radius: 5px;">
                    <h2 style="color: #0046ad; margin-bottom: 20px;">MBO Updated</h2>
                    <p>Hello {mbo.creator.first_name},</p>
                    <p>Your MBO has been updated:</p>
                    
                    <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0;">
                        <h3 style="margin-top: 0; color: #0046ad;">{mbo.title}</h3>
                        <p><strong>Type:</strong> {mbo.mbo_type}</p>
                        <p><strong>Points:</strong> {mbo.points}</p>
                        <p><strong>Status:</strong> {mbo.approval_status}</p>
                        <p><strong>Progress:</strong> {mbo.progress_status}</p>
                    </div>
                    
                    <div style="text-align: center; margin-top: 30px;">
                        <a href="{base_url}/mbo_details/{mbo.id}"
                           style="background-color: #0046ad; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">
                            View MBO
                        </a>
                    </div>
                    
                    <p style="margin-top: 30px; color: #6c757d; font-size: 0.9em;">
                        This is an automated message from the SnapLogic MBO Tracker.
                    </p>
                </div>
                """
                
                text_body = f"""
                MBO Updated
                
                Hello {mbo.creator.first_name},
                
                Your MBO has been updated:
                
                Title: {mbo.title}
                Type: {mbo.mbo_type}
                Points: {mbo.points}
                Status: {mbo.approval_status}
                Progress: {mbo.progress_status}
                
                View MBO: {base_url}/mbo_details/{mbo.id}
                
                This is an automated message from the SnapLogic MBO Tracker.
                """
                
                # Send email with CC to notifications and atdughetti@snaplogic.com
                send_mail([mbo.creator.email], subject, text_body, html_body, cc=['notificationsmbo@snaplogic.com', 'atdughetti@snaplogic.com'])
                logger.info(f"Email notification sent: event={event}, mbo_id={mbo.id}, to={mbo.creator.email}, cc=notificationsmbo@snaplogic.com,atdughetti@snaplogic.com, subject={subject}")
                
                # Send Slack notification to employee
                try:
                    # Note: slack_improved.py doesn't have a specific 'updated' event, so we'll use a generic approach
                    # or we could extend it to support mbo_updated
                    logger.info(f"Skipping Slack notification for updated event - not implemented in slack_improved.py")
                except Exception as slack_error:
                    logger.error(f"Failed to send Slack notification for updated: {str(slack_error)}")
        
        else:
            logger.warning(f"Unknown notification event type: {event}")
            return
            
    except Exception as e:
        logger.error(f"Error sending notification email: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        # Re-raise in non-test environments to return 5xx
        if not current_app.config.get('TESTING', False):
            raise


def send_notification(event: str, mbo: MBO) -> None:
    """
    Legacy function for backward compatibility.
    Maps old event names to new notify_mbo function.
    """
    # Map old events to new events
    event_mapping = {
        'new_mbo': 'created',
        'mbo_updated': 'approved',  # This was used for approval notifications
        'mbo_finished': 'updated',  # This was used for progress updates
        'mbo_manager_edited': 'updated',
        'mbo_deleted': 'deleted'  # Keep this for deletion notifications
    }
    
    if event in event_mapping:
        if event == 'mbo_deleted':
            # Handle deletion separately as it doesn't fit the new pattern
            _handle_mbo_deletion(mbo)
        else:
            # Use the current user as actor (this is a limitation of the legacy interface)
            from flask_login import current_user
            actor = current_user if current_user.is_authenticated else mbo.creator
            notify_mbo(event_mapping[event], mbo, actor)
    else:
        logger.warning(f"Unknown legacy notification event type: {event}")


def _handle_mbo_deletion(mbo: MBO) -> None:
    """Handle MBO deletion notifications (legacy behavior)."""
    app = current_app._get_current_object()
    base_url = app.config.get('BASE_URL', 'http://localhost:5000')
    
    try:
        if not mbo.creator:
            logger.debug(f"Cannot send mbo_deleted notification: creator not found for MBO {mbo.id}")
            return
            
        # Get manager info
        manager = mbo.creator.manager if mbo.creator.manager else None
        if not manager or not manager.email:
            logger.debug(f"Cannot send mbo_deleted notification: manager not found for MBO {mbo.id}")
            return
            
        subject = f"[MBO] {mbo.creator.get_full_name()} deleted an MBO"
        
        # Create simple email content
        html_body = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #e9ecef; border-radius: 5px;">
            <h2 style="color: #0046ad; margin-bottom: 20px;">MBO Deleted</h2>
            <p>Hello {manager.first_name},</p>
            <p>{mbo.creator.get_full_name()} has deleted the following MBO:</p>
            
            <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0;">
                <h3 style="margin-top: 0; color: #0046ad;">{mbo.title}</h3>
                <p><strong>Type:</strong> {mbo.mbo_type}</p>
                <p><strong>Points:</strong> {mbo.points}</p>
                <p><strong>Status:</strong> {mbo.approval_status}</p>
            </div>
            
            <p style="margin-top: 30px; color: #6c757d; font-size: 0.9em;">
                This is an automated message from the SnapLogic MBO Tracker.
            </p>
        </div>
        """
        
        text_body = f"""
        MBO Deleted
        
        Hello {manager.first_name},
        
        {mbo.creator.get_full_name()} has deleted the following MBO:
        
        Title: {mbo.title}
        Type: {mbo.mbo_type}
        Points: {mbo.points}
        Status: {mbo.approval_status}
        
        This is an automated message from the SnapLogic MBO Tracker.
        """
        
        # Send email
        send_mail([manager.email], subject, text_body, html_body)
        logger.info(f"Email notification sent: event=mbo_deleted, mbo_id={mbo.id}, to={manager.email}, subject={subject}")
        
    except Exception as e:
        logger.error(f"Error sending mbo_deleted notification: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())


def send_quarter_end_reminder():
    """
    Send a reminder email to all users two weeks before the quarter ends.
    """
    app = current_app._get_current_object()
    
    try:
        with app.app_context():
            # Get current date
            today = datetime.date.today()
            
            # Determine current quarter end date
            # Q1 = Feb-Apr, Q2 = May-Jul, Q3 = Aug-Oct, Q4 = Nov-Jan
            month = today.month
            year = today.year
            
            if 2 <= month <= 4:  # Q1
                quarter_end = datetime.date(year, 4, 30)
                quarter = "Q1"
            elif 5 <= month <= 7:  # Q2
                quarter_end = datetime.date(year, 7, 31)
                quarter = "Q2"
            elif 8 <= month <= 10:  # Q3
                quarter_end = datetime.date(year, 10, 31)
                quarter = "Q3"
            else:  # Q4 (Nov-Jan)
                if month >= 11:  # Nov-Dec
                    quarter_end = datetime.date(year + 1, 1, 31)
                else:  # Jan
                    quarter_end = datetime.date(year, 1, 31)
                quarter = "Q4"
            
            # Check if today is 14 days before quarter end
            days_until_end = (quarter_end - today).days
            if days_until_end == 14:
                logger.info(f"Sending quarter-end reminder emails (14 days before {quarter} ends)")
                
                # Get all users
                from flask import current_app
                db = current_app.extensions['sqlalchemy']
                users = db.session.execute(db.select(User)).scalars().all()
                base_url = app.config.get('BASE_URL', 'http://localhost:5000')
                
                # Email content
                subject = f"[MBO] Quarter ends soon – review your objectives"
                
                for user in users:
                    if not user.email:
                        continue
                        
                    html_body = f"""
                    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #e9ecef; border-radius: 5px;">
                        <h2 style="color: #0046ad; margin-bottom: 20px;">Quarter End Reminder</h2>
                        <p>Hello {user.first_name},</p>
                        <p>This is a reminder that {quarter} is ending in two weeks. Please take some time to:</p>
                        
                        <ul>
                            <li>Mark completed objectives as "Finished"</li>
                            <li>Update the progress status of your ongoing objectives</li>
                            <li>Confirm that all your completed work has been properly documented</li>
                        </ul>
                        
                        <div style="text-align: center; margin-top: 30px;">
                            <a href="{base_url}/my_mbos"
                               style="background-color: #0046ad; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">
                                Review My MBOs
                            </a>
                        </div>
                        
                        <p style="margin-top: 30px; color: #6c757d; font-size: 0.9em;">
                            This is an automated message from the SnapLogic MBO Tracker.
                        </p>
                    </div>
                    """
                    
                    text_body = f"""
                    Quarter End Reminder
                    
                    Hello {user.first_name},
                    
                    This is a reminder that {quarter} is ending in two weeks. Please take some time to:
                    
                    - Mark completed objectives as "Finished"
                    - Update the progress status of your ongoing objectives
                    - Confirm that all your completed work has been properly documented
                    
                    Review your MBOs: {base_url}/my_mbos
                    
                    This is an automated message from the SnapLogic MBO Tracker.
                    """
                    
                    # Send email
                    send_mail([user.email], subject, text_body, html_body)
                
                logger.info(f"Sent quarter-end reminder emails to {len(users)} users")
            else:
                logger.debug(f"Not sending quarter-end reminder: {days_until_end} days until quarter end")
                
    except Exception as e:
        logger.error(f"Error sending quarter-end reminder emails: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())

# SQLAlchemy event listeners
def _after_insert_listener(mapper, connection, target):
    """
    Listener for after_insert event on MBO model.
    Sends notification when a new MBO is created.
    """
    try:
        logger.info(f"After insert event triggered for MBO {target.id}: {target.title}")
        # Load the creator relationship manually since refresh doesn't work in event listeners
        from app.models import User
        from flask import current_app
        db = current_app.extensions['sqlalchemy']
        creator = db.session.get(User, target.user_id) if target.user_id else None
        # Use the creator as the actor for MBO creation
        notify_mbo('created', target, creator)
    except Exception as e:
        logger.error(f"Error in after_insert listener: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())

def _after_update_listener(mapper, connection, target):
    """
    Listener for after_update event on MBO model.
    Sends notifications based on MBO status changes.
    """
    try:
        logger.info(f"After update event triggered for MBO {target.id}: {target.title}")
        
        # Load the creator relationship manually
        from app.models import User
        from flask import current_app
        db = current_app.extensions['sqlalchemy']
        creator = db.session.get(User, target.user_id) if target.user_id else None
        
        # Get the previous state to detect changes
        history = db.inspect(target).attrs
        
        # Debug logging for approval status history
        logger.info(f"Checking approval status history for MBO {target.id}")
        logger.info(f"Current approval_status: {target.approval_status}")
        if hasattr(history.approval_status, 'history'):
            logger.info(f"Has approval_status history: {history.approval_status.history}")
            if history.approval_status.history and history.approval_status.history.deleted:
                old_status = history.approval_status.history.deleted[0]
                logger.info(f"Old approval_status: {old_status}")
            else:
                logger.info("No deleted values in approval_status history")
        else:
            logger.info("No approval_status history attribute")
        
        # Check if approval status changed to approved or rejected
        approval_status_changed = False
        if hasattr(history.approval_status, 'history') and history.approval_status.history:
            old_status = history.approval_status.history.deleted[0] if history.approval_status.history.deleted else None
            logger.info(f"Comparing old_status '{old_status}' with current '{target.approval_status}'")
            if old_status != target.approval_status and old_status is not None:  # Only if there was a real change from an existing value
                approval_status_changed = True
                logger.info(f"Approval status changed from '{old_status}' to '{target.approval_status}'")
                if target.approval_status == "Approved":
                    logger.info(f"MBO {target.id} was approved, sending notification to employee")
                    # Use manager as actor for approval
                    manager = db.session.get(User, creator.manager_id) if creator and creator.manager_id else None
                    actor = manager if manager else creator
                    notify_mbo('approved', target, actor)
                    return  # Don't send update notification for approval changes
                elif target.approval_status == "Rejected":
                    logger.info(f"MBO {target.id} was rejected, sending notification to employee")
                    # Use manager as actor for rejection
                    manager = db.session.get(User, creator.manager_id) if creator and creator.manager_id else None
                    actor = manager if manager else creator
                    notify_mbo('rejected', target, actor)
                    return  # Don't send update notification for rejection changes
            else:
                logger.info(f"No significant approval status change detected")
        
        # Check if any other field was modified (general update notification)
        modified_fields = []
        for attr_name in ['title', 'description', 'mbo_type', 'points', 'optional_link', 'progress_status']:
            attr = getattr(history, attr_name, None)
            if attr and hasattr(attr, 'history') and attr.history and attr.history.deleted:
                old_value = attr.history.deleted[0]
                new_value = getattr(target, attr_name)
                if old_value != new_value:
                    modified_fields.append(attr_name)
        
        logger.info(f"Modified fields: {modified_fields}, approval_status_changed: {approval_status_changed}")
        
        # Send update notification if fields were modified and it wasn't an approval status change
        if modified_fields and not approval_status_changed:
            logger.info(f"MBO {target.id} was updated (fields: {', '.join(modified_fields)}), sending notification to employee")
            # Use current user as actor, fallback to creator
            from flask_login import current_user
            actor = current_user if current_user.is_authenticated else creator
            notify_mbo('updated', target, actor)
                
    except Exception as e:
        logger.error(f"Error in after_update listener: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())

def _after_delete_listener(mapper, connection, target):
    """
    Listener for after_delete event on MBO model.
    Sends notification when an MBO is deleted.
    """
    try:
        logger.info(f"After delete event triggered for MBO {target.id}: {target.title}")
        # Use legacy deletion handler for now
        send_notification('mbo_deleted', target)
    except Exception as e:
        logger.error(f"Error in after_delete listener: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())

# Register SQLAlchemy event listeners
def init_app(app):
    """
    Initialize the notifications module.
    Register SQLAlchemy event listeners and set up the scheduler.
    """
    global scheduler
    
    with app.app_context():
        # Import db from current app context to avoid circular imports
        from flask import current_app
        db = current_app.extensions['sqlalchemy']
        
        # Add debug logging
        logger.info("Initializing notifications module")
        
        # Register event listeners
        db.event.listen(MBO, 'after_insert', _after_insert_listener)
        db.event.listen(MBO, 'after_update', _after_update_listener)
        db.event.listen(MBO, 'after_delete', _after_delete_listener)
        
        logger.info("Registered MBO notification event listeners")
        
        # Set up scheduler for quarter-end reminders if enabled
        if ENABLE_SCHEDULER and not app.config.get('TESTING', False):
            try:
                scheduler = BackgroundScheduler()
                
                # Run the job every day at midnight to check if it's 14 days before quarter end
                scheduler.add_job(
                    send_quarter_end_reminder,
                    trigger=CronTrigger(hour=0, minute=0),
                    id='quarter_end_reminder',
                    replace_existing=True
                )
                
                # Start the scheduler
                scheduler.start()
                logger.info("Started scheduler for quarter-end reminders")
            except Exception as e:
                logger.error(f"Failed to start scheduler: {str(e)}")
                logger.error("Quarter-end reminders will be disabled")
        
        # Print a message to the console as well
        print("Notifications module initialized and event listeners registered")