"""
Unit tests for the email functionality.
"""
import pytest
from unittest.mock import patch, MagicMock
from app.utils.email import send_mail
from app import db
from app.models import User, MBO
from app.notifications import send_notification, send_quarter_end_reminder

@pytest.fixture
def app():
    """Create and configure a Flask application for testing."""
    # Use the same template folder as the main app
    import os
    from flask import Flask
    template_folder = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'app', 'templates')
    app = Flask(__name__, template_folder=template_folder)
    
    app.config.update(
        TESTING=True,
        SQLALCHEMY_DATABASE_URI='sqlite:///:memory:',
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        SECRET_KEY='test-key',
        BASE_URL='http://localhost:5000',
        DEBUG=True  # Enable debug mode for better error messages
    )
    
    # Initialize extensions
    db.init_app(app)
    
    # Create tables
    with app.app_context():
        db.create_all()
    
    return app

@pytest.fixture
def test_db(app):
    """Create test database and tables."""
    with app.app_context():
        db.create_all()
        yield db
        db.session.remove()
        db.drop_all()

@pytest.fixture
def test_users(app, test_db):
    """Create test users."""
    with app.app_context():
        # Create manager
        manager = User(
            email='manager@example.com',
            username='manager',
            first_name='Test',
            last_name='Manager',
            role='Manager'
        )
        manager.set_password('password')
        
        db.session.add(manager)
        db.session.flush()  # Flush to get the ID without committing
        
        # Create employee
        employee = User(
            email='employee@example.com',
            username='employee',
            first_name='Test',
            last_name='Employee',
            role='Employee',
            manager_id=manager.id
        )
        employee.set_password('password')
        
        db.session.add(employee)
        db.session.commit()
        
        # Store IDs for later use
        manager_id = manager.id
        employee_id = employee.id
        
        # Return a function that will get fresh instances from the database
        def get_users():
            return {
                'manager': User.query.get(manager_id),
                'employee': User.query.get(employee_id)
            }
        
        return get_users

@pytest.fixture
def test_mbo(app, test_db, test_users):
    """Create a test MBO."""
    with app.app_context():
        users = test_users()
        mbo = MBO(
            title='Test MBO',
            description='Test description',
            mbo_type='Learning and Certification',
            user_id=users['employee'].id,
            progress_status='In progress',
            approval_status='Pending Approval'
        )
        db.session.add(mbo)
        db.session.commit()
        
        # Store ID for later use
        mbo_id = mbo.id
        
        # Return a function that will get a fresh instance from the database
        def get_mbo():
            return MBO.query.get(mbo_id)
        
        return get_mbo

@patch('app.utils.email.smtplib.SMTP')
def test_send_mail_includes_cc(mock_smtp, app):
    """Test that send_mail includes the CC header."""
    with app.app_context():
        # Create a mock SMTP instance
        mock_smtp_instance = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_smtp_instance
        
        # Call the function
        send_mail(
            to='test@example.com',
            subject='Test Subject',
            text_body='Test plain text body',
            html_body='<p>Test HTML body</p>'
        )
        
        # Check that sendmail was called with the right arguments
        mock_smtp_instance.sendmail.assert_called_once()
        
        # Get the message string from the call arguments
        args = mock_smtp_instance.sendmail.call_args[0]
        sender = args[0]
        recipients = args[1]
        message = args[2]
        
        # Check that the sender is correct
        assert sender == "notificationsmbo@snaplogic.com"
        
        # Check that the CC address is in the recipients list
        assert "notificationsmbo@snaplogic.com" in recipients
        
        # Check that the CC header is in the message
        assert "Cc: notificationsmbo@snaplogic.com" in message

@patch('app.utils.email.send_mail')
def test_manager_notification_on_mbo_create(mock_send_mail, app, test_mbo, test_users):
    """Test that a notification is sent to the manager when an MBO is created."""
    with app.app_context():
        # Get fresh instances
        mbo = test_mbo()
        users = test_users()
        
        # Call the function
        send_notification('new_mbo', mbo)
        
        # Check that send_mail was called with the right arguments
        mock_send_mail.assert_called_once()
        args = mock_send_mail.call_args[0]
        kwargs = mock_send_mail.call_args[1]
        
        # Check that the recipient is the manager
        assert args[0] == users['manager'].email
        
        # Check that the subject contains the employee's name
        assert users['employee'].first_name in args[1]
        assert "created" in args[1]

@patch('app.utils.email.send_mail')
def test_employee_notification_on_mbo_update(mock_send_mail, app, test_mbo, test_users):
    """Test that a notification is sent to the employee when an MBO is updated."""
    with app.app_context():
        # Get fresh instances
        mbo = test_mbo()
        users = test_users()
        
        # Update MBO status to Approved
        mbo.approval_status = 'Approved'
        db.session.commit()
        
        # Call the function
        send_notification('mbo_updated', mbo)
        
        # Check that send_mail was called with the right arguments
        mock_send_mail.assert_called_once()
        args = mock_send_mail.call_args[0]
        kwargs = mock_send_mail.call_args[1]
        
        # Check that the recipient is the employee
        assert args[0] == users['employee'].email
        
        # Check that the subject contains the status
        assert "approved" in args[1].lower()

@patch('app.utils.email.send_mail')
def test_quarter_end_reminder(mock_send_mail, app, test_users):
    """Test that quarter-end reminders are sent to all users."""
    with app.app_context():
        # Mock datetime to simulate being 14 days before quarter end
        with patch('app.notifications.datetime') as mock_datetime:
            # Set today to April 16 (14 days before April 30, which is Q1 end)
            mock_date = MagicMock()
            mock_date.today.return_value = mock_datetime.date(2025, 4, 16)
            mock_date.side_effect = lambda *args, **kw: mock_datetime.date(*args, **kw)
            mock_datetime.date = mock_date
            
            # Call the function
            send_quarter_end_reminder()
            
            # Check that send_mail was called for each user
            assert mock_send_mail.call_count == 2  # One for manager, one for employee
            
            # Check that the subject is correct
            for call in mock_send_mail.call_args_list:
                args = call[0]
                assert "Quarter ends soon" in args[1]