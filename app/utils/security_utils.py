# app/utils/security_utils.py

import re
import secrets
import hashlib
from datetime import datetime, timedelta
from flask import request, current_app
import logging
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from app import app

def validate_password(password):
    """
    Validate password complexity.
    
    Requirements:
    - At least 8 characters
    - Contains at least one uppercase letter
    - Contains at least one lowercase letter
    - Contains at least one digit
    - Contains at least one special character
    
    Returns:
    - (bool, str): (is_valid, error_message)
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long."
    
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter."
    
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter."
    
    if not re.search(r'[0-9]', password):
        return False, "Password must contain at least one digit."
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "Password must contain at least one special character."
    
    return True, "Password meets complexity requirements."

def sanitize_data(data):
    """
    Remove sensitive information from data before logging.
    
    Args:
        data (dict): Data to sanitize
        
    Returns:
        dict: Sanitized data
    """
    if not isinstance(data, dict):
        return data
    
    sanitized = data.copy()
    sensitive_fields = ['password', 'password_hash', 'secret', 'token', 'key']
    
    for field in sensitive_fields:
        if field in sanitized:
            sanitized[field] = '[REDACTED]'
    
    return sanitized

def setup_security_logging():
    """Configure security logging."""
    logger = logging.getLogger('security')
    
    if not logger.handlers:
        handler = logging.FileHandler('security.log')
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    
    return logger

def log_auth_event(event_type, user_id=None, success=True, details=None):
    """
    Log authentication events.
    
    Args:
        event_type (str): Type of event (login, logout, password_reset, etc.)
        user_id (int, optional): User ID
        success (bool, optional): Whether the event was successful
        details (dict, optional): Additional details
    """
    logger = logging.getLogger('security')
    
    # Sanitize details to remove sensitive information
    safe_details = sanitize_data(details) if details else {}
    
    ip_address = request.remote_addr if request else 'N/A'
    user_agent = request.user_agent.string if request and request.user_agent else 'N/A'
    
    logger.info(
        f"AUTH EVENT: {event_type} | User ID: {user_id} | Success: {success} | "
        f"IP: {ip_address} | User-Agent: {user_agent} | Details: {safe_details}"
    )

def log_admin_action(action_type, admin_id, target_id=None, details=None):
    """
    Log administrative actions.
    
    Args:
        action_type (str): Type of action
        admin_id (int): Admin user ID
        target_id (int, optional): Target user ID
        details (dict, optional): Additional details
    """
    logger = logging.getLogger('security')
    
    # Sanitize details to remove sensitive information
    safe_details = sanitize_data(details) if details else {}
    
    ip_address = request.remote_addr if request else 'N/A'
    user_agent = request.user_agent.string if request and request.user_agent else 'N/A'
    
    logger.info(
        f"ADMIN ACTION: {action_type} | Admin ID: {admin_id} | Target ID: {target_id} | "
        f"IP: {ip_address} | User-Agent: {user_agent} | Details: {safe_details}"
    )

def generate_reset_token(user_id):
    """
    Generate a secure token for password reset.
    
    Args:
        user_id: The user ID
        
    Returns:
        str: A secure token
    """
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    return serializer.dumps(user_id, salt=app.config.get('SECURITY_PASSWORD_SALT', 'password-reset-salt'))

def verify_reset_token(token, expiration=86400):
    """
    Verify a password reset token.
    
    Args:
        token: The token to verify
        expiration: Token expiration time in seconds (default: 24 hours)
        
    Returns:
        int or None: The user ID if the token is valid, None otherwise
    """
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    try:
        user_id = serializer.loads(
            token,
            salt=app.config.get('SECURITY_PASSWORD_SALT', 'password-reset-salt'),
            max_age=expiration
        )
        return user_id
    except (BadSignature, SignatureExpired):
        return None