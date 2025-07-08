#!/usr/bin/env python3

import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from unittest.mock import patch, MagicMock
from flask import Flask
from app import db
from app.models import User, MBO
from app.notifications import notify_mbo

# Create Flask app
app = Flask(__name__)
app.config.update(
    TESTING=True,
    SQLALCHEMY_DATABASE_URI='sqlite:///:memory:',
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
    WTF_CSRF_ENABLED=False,
    EMAIL_ENABLED=True,
    SECRET_KEY='test-secret-key'
)

# Initialize database
db.init_app(app)

with app.app_context():
    db.create_all()
    
    # Create test users
    manager = User(
        email='manager@snaplogic.com',
        first_name='John',
        last_name='Manager',
        role='Manager'
    )
    db.session.add(manager)
    db.session.flush()
    
    employee = User(
        email='employee@snaplogic.com',
        first_name='Jane',
        last_name='Employee',
        role='Employee',
        manager_id=manager.id
    )
    db.session.add(employee)
    db.session.flush()
    
    # Create test MBO
    mbo = MBO(
        title='Test MBO for Notifications',
        description='This is a test MBO for notification testing',
        mbo_type='Learning and Certification',
        points=2,
        user_id=employee.id,
        approval_status='Pending Approval',
        progress_status='In progress'
    )
    db.session.add(mbo)
    db.session.commit()
    
    # Refresh to ensure relationships are loaded
    db.session.refresh(mbo)
    db.session.refresh(employee)
    db.session.refresh(manager)
    
    print(f"MBO ID: {mbo.id}")
    print(f"MBO user_id: {mbo.user_id}")
    print(f"MBO creator: {mbo.creator}")
    print(f"MBO creator email: {mbo.creator.email if mbo.creator else 'None'}")
    print(f"Employee ID: {employee.id}")
    print(f"Employee email: {employee.email}")
    print(f"Employee manager: {employee.manager}")
    print(f"Employee manager email: {employee.manager.email if employee.manager else 'None'}")
    
    # Check email configuration
    print(f"\nEmail configuration:")
    print(f"EMAIL_ENABLED env var: {os.environ.get('EMAIL_ENABLED', 'Not set')}")
    print(f"App config EMAIL_ENABLED: {app.config.get('EMAIL_ENABLED', 'Not set')}")
    
    # Import email module to check its EMAIL_ENABLED
    from app.utils.email import EMAIL_ENABLED as email_module_enabled
    print(f"Email module EMAIL_ENABLED: {email_module_enabled}")
    
    # Test the notification function with mocking and detailed debugging
    print("\nTesting with mock and debugging...")
    
    # Patch send_mail and add debugging to notify_mbo
    with patch('app.utils.email.send_mail') as mock_send_mail:
        with patch('app.notifications.logger') as mock_logger:
            mock_send_mail.reset_mock()
            mock_logger.reset_mock()
            
            try:
                print("Calling notify_mbo...")
                notify_mbo('created', mbo, employee)
                print("notify_mbo completed successfully")
                print(f"send_mail call count: {mock_send_mail.call_count}")
                print(f"logger call count: {mock_logger.info.call_count + mock_logger.error.call_count + mock_logger.warning.call_count}")
                
                if mock_send_mail.call_count > 0:
                    print("Mock send_mail calls:")
                    for i, call in enumerate(mock_send_mail.call_args_list):
                        print(f"  Call {i+1}: {call}")
                
                if mock_logger.info.call_count > 0:
                    print("Logger info calls:")
                    for i, call in enumerate(mock_logger.info.call_args_list):
                        print(f"  Info {i+1}: {call}")
                        
                if mock_logger.error.call_count > 0:
                    print("Logger error calls:")
                    for i, call in enumerate(mock_logger.error.call_args_list):
                        print(f"  Error {i+1}: {call}")
                        
                if mock_logger.warning.call_count > 0:
                    print("Logger warning calls:")
                    for i, call in enumerate(mock_logger.warning.call_args_list):
                        print(f"  Warning {i+1}: {call}")
                        
            except Exception as e:
                print(f"Error in notify_mbo: {e}")
                import traceback
                traceback.print_exc()