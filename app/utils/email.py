"""
Email utility functions for the MBO Tracker application.

This module provides functions for sending emails through the Google Workspace SMTP relay.
All emails are sent from notificationsmbo@snaplogic.com and CC'd to the same address
for troubleshooting purposes.
"""
import os
import ssl
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from flask import current_app

# Global SMTP settings
SMTP_HOST = "smtp-relay.gmail.com"
SMTP_PORT = 587
EMAIL_ENABLED = os.environ.get('EMAIL_ENABLED', 'True').lower() in ['true', 'yes', '1']
SENDER = "notificationsmbo@snaplogic.com"
CC_EMAIL = "notificationsmbo@snaplogic.com"

def send_mail(to, subject, text_body, html_body):
    """
    Send an email using the Google Workspace SMTP relay.
    
    Args:
        to (str or list): Recipient email address(es)
        subject (str): Email subject
        text_body (str): Plain text email body
        html_body (str): HTML email body
        
    Returns:
        bool: True if email was sent successfully, False otherwise
        
    Note:
        All emails are CC'd to notificationsmbo@snaplogic.com for troubleshooting.
        Set EMAIL_ENABLED=False in environment variables to disable email sending in development.
    """
    if not EMAIL_ENABLED:
        current_app.logger.info(f"Email sending disabled. Would have sent email to {to} with subject: {subject}")
        return True
    
    # Convert to list if single email
    if isinstance(to, str):
        to = [to]
    
    # Create message
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = SENDER
    msg["To"] = ", ".join(to)
    msg["Cc"] = CC_EMAIL
    
    # Add CC to recipients list for actual sending
    recipients = to.copy()
    if CC_EMAIL not in recipients:
        recipients.append(CC_EMAIL)
    
    # Attach text and HTML parts
    msg.attach(MIMEText(text_body, "plain", "utf-8"))
    msg.attach(MIMEText(html_body, "html", "utf-8"))
    
    try:
        # Create SSL context
        context = ssl.create_default_context()
        
        # Connect to SMTP server
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=10) as server:
            current_app.logger.info(f"Connected to {SMTP_HOST}:{SMTP_PORT}")
            
            # Start TLS
            server.starttls(context=context)
            current_app.logger.info("STARTTLS established")
            
            # Send email (no authentication needed for Google Workspace SMTP relay)
            server.sendmail(SENDER, recipients, msg.as_string())
            current_app.logger.info(f"Email sent successfully to {to} with subject: {subject}")
            return True
            
    except Exception as e:
        current_app.logger.error(f"Error sending email: {str(e)}")
        import traceback
        current_app.logger.error(traceback.format_exc())
        return False