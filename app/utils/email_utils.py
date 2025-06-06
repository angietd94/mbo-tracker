"""
Utility functions for sending emails.
"""
from flask import render_template
from flask_mail import Message
from app import app, mail

def send_email(subject, recipients, html_body, text_body=None):
    """
    Send an email with the given subject and body to the specified recipients.
    
    Args:
        subject: Email subject
        recipients: List of recipient email addresses
        html_body: HTML content of the email
        text_body: Plain text content of the email (optional)
    """
    msg = Message(subject, recipients=recipients)
    msg.html = html_body
    if text_body:
        msg.body = text_body
    
    try:
        mail.send(msg)
        return True
    except Exception as e:
        app.logger.error(f"Error sending email: {e}")
        return False

def send_new_mbo_notification(mbo, manager):
    """
    Send a notification email to a manager when a new MBO is created.
    
    Args:
        mbo: The MBO object
        manager: The manager User object
    """
    # Check if manager has email notifications enabled
    try:
        if not manager.get_email_notifications():
            return False
    except:
        # If there's an error checking email notifications, assume they're enabled
        pass
        
    subject = f"New MBO Submitted: {mbo.title}"
    recipients = [manager.email]
    
    html_body = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #e9ecef; border-radius: 5px;">
        <div style="text-align: center; margin-bottom: 20px;">
            <img src="https://www.snaplogic.com/wp-content/themes/snaplogic-2022/assets/images/snaplogic-logo.svg" alt="SnapLogic Logo" style="height: 50px;">
        </div>
        <h2 style="color: #0046ad; margin-bottom: 20px;">New MBO Submitted</h2>
        <p>Hello {manager.first_name},</p>
        <p>{mbo.creator.first_name} {mbo.creator.last_name} has submitted a new MBO for your approval:</p>
        
        <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0;">
            <h3 style="margin-top: 0; color: #0046ad;">{mbo.title}</h3>
            <p><strong>Type:</strong> {mbo.mbo_type}</p>
            <p><strong>Description:</strong> {mbo.description}</p>
            <p><strong>Status:</strong> {mbo.progress_status}</p>
        </div>
        
        <p>Please review this MBO at your earliest convenience.</p>
        
        <div style="text-align: center; margin-top: 30px;">
            <a href="{app.config.get('BASE_URL', 'http://localhost:5000')}/mbo/{mbo.id}" 
               style="background-color: #0046ad; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">
                Review MBO
            </a>
        </div>
        
        <p style="margin-top: 30px; color: #6c757d; font-size: 0.9em;">
            This is an automated message from the SnapLogic MBO Tracker.
        </p>
    </div>
    """
    
    text_body = f"""
    New MBO Submitted
    
    Hello {manager.first_name},
    
    {mbo.creator.first_name} {mbo.creator.last_name} has submitted a new MBO for your approval:
    
    Title: {mbo.title}
    Type: {mbo.mbo_type}
    Description: {mbo.description}
    Status: {mbo.progress_status}
    
    Please review this MBO at your earliest convenience.
    
    Review MBO: {app.config.get('BASE_URL', 'http://localhost:5000')}/mbo/{mbo.id}
    
    This is an automated message from the SnapLogic MBO Tracker.
    """
    
    return send_email(subject, recipients, html_body, text_body)

def send_password_reset_email(user, token):
    """
    Send a password reset email to a user.
    
    Args:
        user: The User object
        token: The password reset token
    """
    subject = "Password Reset Request"
    recipients = [user.email]
    
    reset_url = f"{app.config.get('BASE_URL', 'http://localhost:5000')}/reset_password/{token}"
    
    html_body = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #e9ecef; border-radius: 5px;">
        <div style="text-align: center; margin-bottom: 20px;">
            <img src="https://www.snaplogic.com/wp-content/themes/snaplogic-2022/assets/images/snaplogic-logo.svg" alt="SnapLogic Logo" style="height: 50px;">
        </div>
        <h2 style="color: #0046ad; margin-bottom: 20px;">Password Reset Request</h2>
        <p>Hello {user.first_name},</p>
        <p>We received a request to reset your password for the SnapLogic MBO Tracker. If you didn't make this request, you can ignore this email.</p>
        
        <p>To reset your password, click the button below:</p>
        
        <div style="text-align: center; margin: 30px 0;">
            <a href="{reset_url}"
               style="background-color: #0046ad; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">
                Reset Password
            </a>
        </div>
        
        <p>Or copy and paste this link into your browser:</p>
        <p style="word-break: break-all; background-color: #f8f9fa; padding: 10px; border-radius: 5px;">{reset_url}</p>
        
        <p>This link will expire in 24 hours.</p>
        
        <p style="margin-top: 30px; color: #6c757d; font-size: 0.9em;">
            This is an automated message from the SnapLogic MBO Tracker.
        </p>
    </div>
    """
    
    text_body = f"""
    Password Reset Request
    
    Hello {user.first_name},
    
    We received a request to reset your password for the SnapLogic MBO Tracker. If you didn't make this request, you can ignore this email.
    
    To reset your password, click the link below:
    
    {reset_url}
    
    This link will expire in 24 hours.
    
    This is an automated message from the SnapLogic MBO Tracker.
    """
    
    return send_email(subject, recipients, html_body, text_body)
def send_mbo_status_notification(mbo, action, actor):
    """
    Send a notification email to the MBO creator when the MBO status changes.
    
    Args:
        mbo: The MBO object
        action: The action performed (e.g., "approved", "rejected", "edited")
        actor: The User object who performed the action
    """
    # Check if creator has email notifications enabled
    try:
        if not mbo.creator.get_email_notifications():
            return False
    except:
        # If there's an error checking email notifications, assume they're enabled
        pass
        
    subject = f"MBO {action.capitalize()}: {mbo.title}"
    recipients = [mbo.creator.email]
    
    html_body = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #e9ecef; border-radius: 5px;">
        <div style="text-align: center; margin-bottom: 20px;">
            <img src="https://www.snaplogic.com/wp-content/themes/snaplogic-2022/assets/images/snaplogic-logo.svg" alt="SnapLogic Logo" style="height: 50px;">
        </div>
        <h2 style="color: #0046ad; margin-bottom: 20px;">MBO {action.capitalize()}</h2>
        <p>Hello {mbo.creator.first_name},</p>
        <p>Your MBO "{mbo.title}" has been {action} by {actor.first_name} {actor.last_name}.</p>
        
        <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0;">
            <h3 style="margin-top: 0; color: #0046ad;">{mbo.title}</h3>
            <p><strong>Type:</strong> {mbo.mbo_type}</p>
            <p><strong>Description:</strong> {mbo.description}</p>
            <p><strong>Status:</strong> {mbo.progress_status}</p>
            <p><strong>Approval Status:</strong> {mbo.approval_status}</p>
            <p><strong>Points:</strong> {mbo.points}</p>
        </div>
        
        <div style="text-align: center; margin-top: 30px;">
            <a href="{app.config.get('BASE_URL', 'http://localhost:5000')}/mbo/{mbo.id}" 
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
    MBO {action.capitalize()}
    
    Hello {mbo.creator.first_name},
    
    Your MBO "{mbo.title}" has been {action} by {actor.first_name} {actor.last_name}.
    
    Title: {mbo.title}
    Type: {mbo.mbo_type}
    Description: {mbo.description}
    Status: {mbo.progress_status}
    Approval Status: {mbo.approval_status}
    Points: {mbo.points}
    
    View MBO: {app.config.get('BASE_URL', 'http://localhost:5000')}/mbo/{mbo.id}
    
    This is an automated message from the SnapLogic MBO Tracker.
    """
    
    return send_email(subject, recipients, html_body, text_body)