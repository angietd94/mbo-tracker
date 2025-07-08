"""
Email utility functions for the MBO Tracker application.

This module provides functions for sending emails through Gmail SMTP.
All emails are sent from notificationsmbo@snaplogic.com and BCC'd to the same address
for troubleshooting purposes.

Note: Requires Gmail App Password for authentication.
"""
import os
import ssl
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from flask import current_app

# Global SMTP settings
SMTP_HOST = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
SMTP_PORT = int(os.environ.get('MAIL_PORT', 587))
EMAIL_ENABLED = os.environ.get('EMAIL_ENABLED', 'True').lower() in ['true', 'yes', '1']
SENDER = "notificationsmbo@snaplogic.com"
BCC_EMAIL = "notificationsmbo@snaplogic.com"  # Always BCC to notifications mailbox
SMTP_USERNAME = os.environ.get('SMTP_USERNAME', os.environ.get('MAIL_USERNAME', 'notificationsmbo@snaplogic.com'))
SMTP_PASSWORD = os.environ.get('SMTP_PASSWORD', os.environ.get('MAIL_PASSWORD', ''))

def send_mail(to, subject, text_body, html_body, cc=None):
    """
    Send an email using Gmail SMTP.
    
    Args:
        to (str or list): Recipient email address(es)
        subject (str): Email subject
        text_body (str): Plain text email body
        html_body (str): HTML email body
        cc (str or list, optional): CC email address(es)
        
    Returns:
        bool: True if email was sent successfully, False otherwise
        
    Note:
        All emails are BCC'd to notificationsmbo@snaplogic.com for troubleshooting.
        Requires Gmail App Password for authentication.
        Set EMAIL_ENABLED=False in environment variables to disable email sending in development.
    """
    if not EMAIL_ENABLED:
        current_app.logger.info(f"Email sending disabled. Would have sent email to {to} with subject: {subject}")
        return True
    
    # Convert to list if single email
    if isinstance(to, str):
        to = [to]
    
    # Convert CC to list if provided
    if cc:
        if isinstance(cc, str):
            cc = [cc]
    else:
        cc = []
    
    # Create message
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = SENDER
    msg["To"] = ", ".join(to)
    
    # Add CC header if CC recipients exist
    if cc:
        msg["Cc"] = ", ".join(cc)
    
    msg["Bcc"] = BCC_EMAIL  # Always BCC to notifications mailbox
    
    # Add all recipients (TO + CC + BCC) to recipients list for actual sending
    recipients = to.copy()
    recipients.extend(cc)
    if BCC_EMAIL not in recipients:
        recipients.append(BCC_EMAIL)
    
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
            
            # Authenticate with Gmail using App Password
            if SMTP_USERNAME and SMTP_PASSWORD:
                server.login(SMTP_USERNAME, SMTP_PASSWORD)
                current_app.logger.info("Gmail SMTP authentication successful")
            
            # Send email
            server.sendmail(SENDER, recipients, msg.as_string().encode('utf-8'))
            current_app.logger.info(f"Email sent successfully to {to} with subject: {subject}")
            return True
            
    except Exception as e:
        current_app.logger.error(f"Error sending email: {str(e)}")
        import traceback
        current_app.logger.error(traceback.format_exc())
        return False