import os
import pytest
from unittest.mock import patch, MagicMock
from flask import Flask
import logging

from app import db
from app.models import User, MBO
from app.notifications import notify_mbo
from app.utils.email import send_mail


@pytest.fixture
def app():
    """Create and configure a Flask application for testing."""
    # Use the same template folder as the main app
    template_folder = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'app', 'templates')
    app = Flask(__name__, template_folder=template_folder)
    
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
        yield app
        db.drop_all()


class TestMBONotificationWorkflow:
    """Test the MBO notification workflow according to business rules."""
    
    @patch('app.notifications.send_mail')
    def test_mbo_creation_sends_two_emails(self, mock_send_mail, app):
        """
        Business rule 1: When a new MBO is created:
        - Send email to employee (creator)
        - Send email to manager
        - CC notificationsmbo@snaplogic.com on both messages
        """
        with app.app_context():
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
            
            # Reset mock to clear any previous calls
            mock_send_mail.reset_mock()
            
            # Trigger the notification
            notify_mbo('created', mbo, employee)
            
            # Should have been called twice (employee + manager)
            assert mock_send_mail.call_count == 2
            
            # Check first call (employee notification)
            first_call = mock_send_mail.call_args_list[0]
            employee_to = first_call[0][0]  # First positional argument (to)
            employee_subject = first_call[0][1]  # Second positional argument (subject)
            employee_cc = first_call[1].get('cc', [])  # CC from kwargs
            
            assert employee_to == [employee.email]
            assert "pending manager approval" in employee_subject
            assert mbo.title in employee_subject
            assert 'notificationsmbo@snaplogic.com' in employee_cc
            
            # Check second call (manager notification)
            second_call = mock_send_mail.call_args_list[1]
            manager_to = second_call[0][0]
            manager_subject = second_call[0][1]
            manager_cc = second_call[1].get('cc', [])
            
            assert manager_to == [manager.email]
            assert "Approval needed" in manager_subject
            assert employee.get_full_name() in manager_subject
            assert 'notificationsmbo@snaplogic.com' in manager_cc
    
    @patch('app.notifications.send_mail')
    def test_mbo_approval_sends_one_email(self, mock_send_mail, app):
        """
        Business rule 2: When an MBO is approved:
        - Send email only to employee
        - CC notificationsmbo@snaplogic.com
        """
        with app.app_context():
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
                approval_status='Approved',
                progress_status='In progress'
            )
            db.session.add(mbo)
            db.session.commit()
            
            # Refresh to ensure relationships are loaded
            db.session.refresh(mbo)
            db.session.refresh(employee)
            db.session.refresh(manager)
            
            mock_send_mail.reset_mock()
            
            # Trigger the notification
            notify_mbo('approved', mbo, manager)
            
            # Should have been called once (employee only)
            assert mock_send_mail.call_count == 1
            
            # Check the call
            call_args = mock_send_mail.call_args
            to_emails = call_args[0][0]
            subject = call_args[0][1]
            cc_emails = call_args[1].get('cc', [])
            
            assert to_emails == [employee.email]
            assert "approved" in subject.lower()
            assert mbo.title in subject
            assert 'notificationsmbo@snaplogic.com' in cc_emails
    
    @patch('app.notifications.send_mail')
    def test_mbo_rejection_sends_one_email(self, mock_send_mail, app):
        """
        Business rule 3: When an MBO is rejected:
        - Send email only to employee
        - CC notificationsmbo@snaplogic.com
        """
        with app.app_context():
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
                approval_status='Rejected',
                progress_status='In progress'
            )
            db.session.add(mbo)
            db.session.commit()
            
            # Refresh to ensure relationships are loaded
            db.session.refresh(mbo)
            db.session.refresh(employee)
            if 'manager' in locals():
                db.session.refresh(manager)
            
            mock_send_mail.reset_mock()
            
            # Trigger the notification
            notify_mbo('rejected', mbo, manager)
            
            # Should have been called once (employee only)
            assert mock_send_mail.call_count == 1
            
            # Check the call
            call_args = mock_send_mail.call_args
            to_emails = call_args[0][0]
            subject = call_args[0][1]
            cc_emails = call_args[1].get('cc', [])
            
            assert to_emails == [employee.email]
            assert "rejected" in subject.lower()
            assert mbo.title in subject
            assert 'notificationsmbo@snaplogic.com' in cc_emails
    
    @patch('app.notifications.send_mail')
    def test_mbo_update_sends_one_email(self, mock_send_mail, app):
        """
        Business rule 4: When an MBO is updated (non-approval change):
        - Send email only to employee
        - CC notificationsmbo@snaplogic.com
        """
        with app.app_context():
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
                approval_status='Approved',
                progress_status='Completed'
            )
            db.session.add(mbo)
            db.session.commit()
            
            # Refresh to ensure relationships are loaded
            db.session.refresh(mbo)
            db.session.refresh(employee)
            if 'manager' in locals():
                db.session.refresh(manager)
            
            mock_send_mail.reset_mock()
            
            # Trigger the notification
            notify_mbo('updated', mbo, employee)
            
            # Should have been called once (employee only)
            assert mock_send_mail.call_count == 1
            
            # Check the call
            call_args = mock_send_mail.call_args
            to_emails = call_args[0][0]
            subject = call_args[0][1]
            cc_emails = call_args[1].get('cc', [])
            
            assert to_emails == [employee.email]
            assert "updated" in subject.lower()
            assert mbo.title in subject
            assert 'notificationsmbo@snaplogic.com' in cc_emails
    
    @patch('app.notifications.send_mail')
    def test_email_contains_deep_link(self, mock_send_mail, app):
        """Test that notification emails contain deep links to the MBO."""
        with app.app_context():
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
            if 'manager' in locals():
                db.session.refresh(manager)
            
            mock_send_mail.reset_mock()
            
            # Trigger the notification
            notify_mbo('created', mbo, employee)
            
            # Check that HTML body contains deep link
            call_args = mock_send_mail.call_args_list[0]  # First call (employee)
            html_body = call_args[0][3]  # Fourth positional argument (html_body)
            
            expected_link = f"/mbo/{mbo.id}"
            assert expected_link in html_body
    
    @patch('app.notifications.send_mail')
    def test_notification_logging(self, mock_send_mail, app, caplog):
        """Test that notifications are properly logged."""
        with app.app_context():
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
            
            with caplog.at_level(logging.INFO):
                notify_mbo('created', mbo, employee)
            
            # Check that required fields are logged
            log_messages = [record.message for record in caplog.records]
            assert any('event=created' in msg for msg in log_messages)
            assert any(f'mbo_id={mbo.id}' in msg for msg in log_messages)
            assert any('to=' in msg for msg in log_messages)
            assert any('cc=' in msg for msg in log_messages)
            assert any('subject=' in msg for msg in log_messages)
    
    @patch('app.notifications.send_mail')
    def test_missing_manager_handling(self, mock_send_mail, app):
        """Test that notifications handle missing manager gracefully."""
        with app.app_context():
            # Create employee without manager
            employee = User(
                email='orphan@snaplogic.com',
                first_name='Orphan',
                last_name='Employee',
                role='Employee'
            )
            db.session.add(employee)
            db.session.flush()
            
            # Create MBO for employee without manager
            mbo = MBO(
                title='Orphan MBO',
                description='MBO for employee without manager',
                mbo_type='Learning and Certification',
                points=2,
                user_id=employee.id
            )
            db.session.add(mbo)
            db.session.commit()
            
            # Refresh to ensure relationships are loaded
            db.session.refresh(mbo)
            db.session.refresh(employee)
            if 'manager' in locals():
                db.session.refresh(manager)
            
            mock_send_mail.reset_mock()
            
            # Should only send one email (to employee) since no manager exists
            notify_mbo('created', mbo, employee)
            
            # Should have been called once (employee only, no manager email)
            assert mock_send_mail.call_count == 1
            
            # Check the call
            call_args = mock_send_mail.call_args
            to_emails = call_args[0][0]
            assert to_emails == [employee.email]
    
    @patch('app.notifications.send_mail')
    def test_error_handling_in_non_test_env(self, mock_send_mail, app):
        """Test that email errors are handled properly in non-test environments."""
        with app.app_context():
            # Temporarily disable testing mode
            app.config['TESTING'] = False
            
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
            
            # Make send_mail raise an exception
            mock_send_mail.side_effect = Exception("SMTP server error")
            
            # This should raise an exception in non-test environment
            with pytest.raises(Exception):
                notify_mbo('created', mbo, employee)
            
            # Restore testing mode
            app.config['TESTING'] = True


class TestSQLAlchemyEventListeners:
    """Test that SQLAlchemy event listeners properly trigger notifications."""
    
    @patch('app.notifications.notify_mbo')
    def test_mbo_insert_triggers_created_notification(self, mock_notify, app):
        """Test that creating an MBO triggers the 'created' notification."""
        with app.app_context():
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
            
            mock_notify.reset_mock()
            
            # Create a new MBO (this should trigger the after_insert listener)
            mbo = MBO(
                title='New Test MBO',
                description='Testing insert trigger',
                mbo_type='Demo and Assets',
                points=3,
                user_id=employee.id
            )
            db.session.add(mbo)
            db.session.commit()
            
            # Refresh to ensure relationships are loaded
            db.session.refresh(mbo)
            db.session.refresh(employee)
            if 'manager' in locals():
                db.session.refresh(manager)
            
            # Verify notify_mbo was called with 'created' event
            mock_notify.assert_called_once()
            call_args = mock_notify.call_args
            assert call_args[0][0] == 'created'  # event
            assert call_args[0][1].title == 'New Test MBO'  # mbo
            assert call_args[0][2].email == employee.email  # actor
    
    @patch('app.notifications.notify_mbo')
    def test_mbo_approval_triggers_approved_notification(self, mock_notify, app):
        """Test that approving an MBO triggers the 'approved' notification."""
        with app.app_context():
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
            
            # Create MBO with pending status
            mbo = MBO(
                title='Test MBO',
                description='Testing approval trigger',
                mbo_type='Demo and Assets',
                points=3,
                user_id=employee.id,
                approval_status='Pending Approval'
            )
            db.session.add(mbo)
            db.session.commit()
            
            mock_notify.reset_mock()
            
            # Change approval status to approved (this should trigger after_update listener)
            mbo.approval_status = 'Approved'
            db.session.commit()
            
            # Verify notify_mbo was called with 'approved' event
            mock_notify.assert_called_once()
            call_args = mock_notify.call_args
            assert call_args[0][0] == 'approved'  # event
            assert call_args[0][1].approval_status == 'Approved'  # mbo
    
    @patch('app.notifications.notify_mbo')
    def test_mbo_rejection_triggers_rejected_notification(self, mock_notify, app):
        """Test that rejecting an MBO triggers the 'rejected' notification."""
        with app.app_context():
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
            
            # Create MBO with pending status
            mbo = MBO(
                title='Test MBO',
                description='Testing rejection trigger',
                mbo_type='Demo and Assets',
                points=3,
                user_id=employee.id,
                approval_status='Pending Approval'
            )
            db.session.add(mbo)
            db.session.commit()
            
            mock_notify.reset_mock()
            
            # Change approval status to rejected (this should trigger after_update listener)
            mbo.approval_status = 'Rejected'
            db.session.commit()
            
            # Verify notify_mbo was called with 'rejected' event
            mock_notify.assert_called_once()
            call_args = mock_notify.call_args
            assert call_args[0][0] == 'rejected'  # event
            assert call_args[0][1].approval_status == 'Rejected'  # mbo
    
    @patch('app.notifications.notify_mbo')
    def test_mbo_field_update_triggers_updated_notification(self, mock_notify, app):
        """Test that updating MBO fields (non-approval) triggers 'updated' notification."""
        with app.app_context():
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
            
            # Create MBO without approval status initially
            mbo = MBO(
                title='Test MBO',
                description='Testing field update trigger',
                mbo_type='Demo and Assets',
                points=3,
                user_id=employee.id,
                progress_status='In progress'
            )
            db.session.add(mbo)
            db.session.commit()

            # Set approval status after creation to avoid triggering approval notification
            mbo.approval_status = 'Approved'
            db.session.commit()

            mock_notify.reset_mock()

            # Update a non-approval field (this should trigger after_update listener)
            mbo.progress_status = 'Completed'
            db.session.commit()
            
            # Verify notify_mbo was called with 'updated' event
            mock_notify.assert_called_once()
            call_args = mock_notify.call_args
            assert call_args[0][0] == 'updated'  # event
            assert call_args[0][1].progress_status == 'Completed'  # mbo