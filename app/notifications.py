"""
Notifications module for MBO Tracker.

This module handles email notifications for MBO-related events.
"""
import threading
import logging
import datetime
import os
from flask import render_template, current_app
from app import db
from app.models import MBO, User
from app.utils.email import send_mail
# Import APScheduler only if enabled
ENABLE_SCHEDULER = os.environ.get('ENABLE_SCHEDULER', 'False').lower() in ['true', 'yes', '1']
if ENABLE_SCHEDULER:
    try:
        from apscheduler.schedulers.background import BackgroundScheduler
        from apscheduler.triggers.cron import CronTrigger
    except ImportError:
        logger.warning("APScheduler not installed. Quarter-end reminders will be disabled.")
        ENABLE_SCHEDULER = False

# Set up logger
logger = logging.getLogger(__name__)

# Global scheduler
scheduler = None

def send_notification(event: str, mbo: MBO) -> None:
    """
    Send a notification email based on the event type.
    
    Args:
        event: Event type (new_mbo, mbo_updated, mbo_deleted)
        mbo: MBO object
    """
    app = current_app._get_current_object()
    base_url = app.config.get('BASE_URL', 'http://localhost:5000')
    
    try:
        if event == 'new_mbo':
            # Notification for new MBO submission (to manager)
            if not mbo.creator:
                logger.debug(f"Cannot send new_mbo notification: creator not found for MBO {mbo.id}")
                return
                
            # Get manager info
            manager = mbo.creator.manager if mbo.creator.manager else None
            if not manager or not manager.email:
                logger.debug(f"Cannot send new_mbo notification: manager not found for MBO {mbo.id}")
                return
                
            subject = f"[MBO] {mbo.creator.get_full_name()} created an MBO"
            
            # Render email templates
            html_body = render_template(
                'email/new_mbo_submitted.html',
                mbo=mbo,
                manager=manager,
                base_url=base_url
            )
            text_body = render_template(
                'email/new_mbo_submitted.txt',
                mbo=mbo,
                manager=manager,
                base_url=base_url
            )
            
            # Send email
            send_mail(manager.email, subject, text_body, html_body)
            
        elif event == 'mbo_updated':
            # Notification for MBO updated (to employee)
            if not mbo.creator or not mbo.creator.email:
                logger.debug(f"Cannot send mbo_updated notification: creator not found for MBO {mbo.id}")
                return
                
            subject = f"[MBO] Your objective has been {mbo.approval_status.lower()}"
            
            # Render email templates
            html_body = render_template(
                'email/mbo_updated.html',
                mbo=mbo,
                base_url=base_url
            )
            text_body = render_template(
                'email/mbo_updated.txt',
                mbo=mbo,
                base_url=base_url
            )
            
            # Send email
            send_mail(mbo.creator.email, subject, text_body, html_body)
            
        elif event == 'mbo_deleted':
            # Notification for MBO deleted (to manager)
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
            send_mail(manager.email, subject, text_body, html_body)
            
        else:
            logger.warning(f"Unknown notification event type: {event}")
            return
            
        # Log that email was sent
        logger.info(f"Email notification sent: {event} for MBO {mbo.id}")
        
    except Exception as e:
        logger.error(f"Error sending notification email: {str(e)}")
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
                users = User.query.all()
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
                    send_mail(user.email, subject, text_body, html_body)
                
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
        send_notification('new_mbo', target)
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
        
        # Check if MBO is accepted or manager edited any field
        if target.approval_status in ["Approved", "Accepted"]:
            logger.info(f"MBO {target.id} is {target.approval_status}, sending notification")
            send_notification('mbo_updated', target)
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