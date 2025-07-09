#!/usr/bin/env python3
"""
Comprehensive test suite for Slack interactive messages implementation.
Tests signature verification, button actions, deduplication, and Angelica BCC.
"""

import json
import time
import hmac
import hashlib
from unittest.mock import Mock, patch
import pytest
from app import create_app
from app.routes.slack_interactions import handle_slack_interaction


class TestSlackInteractions:
    """Test suite for Slack interactive message handling."""
    
    def setup_method(self):
        """Set up test environment before each test."""
        self.app = create_app()
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        # Mock Slack signing secret
        self.signing_secret = "test_signing_secret_123"
        
    def teardown_method(self):
        """Clean up after each test."""
        self.app_context.pop()
    
    def generate_slack_signature(self, timestamp, body):
        """Generate valid Slack signature for testing."""
        sig_basestring = f"v0:{timestamp}:{body}"
        signature = hmac.new(
            self.signing_secret.encode(),
            sig_basestring.encode(),
            hashlib.sha256
        ).hexdigest()
        return f"v0={signature}"
    
    def test_signature_verification_success(self):
        """Test successful signature verification."""
        timestamp = str(int(time.time()))
        body = "payload=test_payload"
        signature = self.generate_slack_signature(timestamp, body)
        
        headers = {
            'X-Slack-Request-Timestamp': timestamp,
            'X-Slack-Signature': signature,
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        with patch('app.routes.slack_interactions.current_app') as mock_app:
            mock_app.config = {'SLACK_SIGNING_SECRET': self.signing_secret}
            
            response = self.client.post('/slack/interactions', 
                                      data=body, 
                                      headers=headers)
            
            # Should not fail on signature verification
            assert response.status_code != 401
    
    def test_signature_verification_failure(self):
        """Test signature verification failure with invalid signature."""
        timestamp = str(int(time.time()))
        body = "payload=test_payload"
        invalid_signature = "v0=invalid_signature_hash"
        
        headers = {
            'X-Slack-Request-Timestamp': timestamp,
            'X-Slack-Signature': invalid_signature,
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        with patch('app.routes.slack_interactions.current_app') as mock_app:
            mock_app.config = {'SLACK_SIGNING_SECRET': self.signing_secret}
            
            response = self.client.post('/slack/interactions', 
                                      data=body, 
                                      headers=headers)
            
            assert response.status_code == 401
    
    def test_approve_mbo_action(self):
        """Test MBO approval button click handling."""
        payload = {
            "type": "block_actions",
            "user": {"id": "U123MANAGER", "name": "manager"},
            "actions": [{
                "action_id": "approve_mbo",
                "value": "mbo_123"
            }],
            "response_url": "https://hooks.slack.com/actions/test"
        }
        
        timestamp = str(int(time.time()))
        body = f"payload={json.dumps(payload)}"
        signature = self.generate_slack_signature(timestamp, body)
        
        headers = {
            'X-Slack-Request-Timestamp': timestamp,
            'X-Slack-Signature': signature,
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        with patch('app.routes.slack_interactions.current_app') as mock_app, \
             patch('app.routes.slack_interactions.update_mbo_status') as mock_update, \
             patch('app.routes.slack_interactions.requests.post') as mock_post:
            
            mock_app.config = {'SLACK_SIGNING_SECRET': self.signing_secret}
            mock_update.return_value = True
            mock_post.return_value.status_code = 200
            
            response = self.client.post('/slack/interactions', 
                                      data=body, 
                                      headers=headers)
            
            assert response.status_code == 200
            mock_update.assert_called_once_with(123, 'approved', 'U123MANAGER')
    
    def test_decline_mbo_action(self):
        """Test MBO decline button click handling."""
        payload = {
            "type": "block_actions",
            "user": {"id": "U123MANAGER", "name": "manager"},
            "actions": [{
                "action_id": "decline_mbo",
                "value": "mbo_456"
            }],
            "response_url": "https://hooks.slack.com/actions/test"
        }
        
        timestamp = str(int(time.time()))
        body = f"payload={json.dumps(payload)}"
        signature = self.generate_slack_signature(timestamp, body)
        
        headers = {
            'X-Slack-Request-Timestamp': timestamp,
            'X-Slack-Signature': signature,
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        with patch('app.routes.slack_interactions.current_app') as mock_app, \
             patch('app.routes.slack_interactions.update_mbo_status') as mock_update, \
             patch('app.routes.slack_interactions.requests.post') as mock_post:
            
            mock_app.config = {'SLACK_SIGNING_SECRET': self.signing_secret}
            mock_update.return_value = True
            mock_post.return_value.status_code = 200
            
            response = self.client.post('/slack/interactions', 
                                      data=body, 
                                      headers=headers)
            
            assert response.status_code == 200
            mock_update.assert_called_once_with(456, 'declined', 'U123MANAGER')


class TestSlackNotifications:
    """Test suite for Slack notification sending and deduplication."""
    
    def setup_method(self):
        """Set up test environment."""
        self.app = create_app()
        self.app_context = self.app.app_context()
        self.app_context.push()
    
    def teardown_method(self):
        """Clean up after each test."""
        self.app_context.pop()
    
    @patch('app.notifications.slack_improved.WebClient')
    def test_manager_approval_message(self, mock_webclient):
        """Test sending interactive approval message to manager."""
        from app.notifications.slack_improved import send_slack_notification
        
        mock_client = Mock()
        mock_webclient.return_value = mock_client
        mock_client.chat_postMessage.return_value = {"ok": True}
        
        # Test data
        mbo_data = {
            'id': 123,
            'title': 'Q4 Sales Target',
            'description': 'Achieve 120% of quarterly sales target',
            'employee_name': 'John Doe',
            'manager_slack_id': 'U123MANAGER'
        }
        
        send_slack_notification('mbo_created', mbo_data)
        
        # Verify interactive message was sent
        mock_client.chat_postMessage.assert_called()
        call_args = mock_client.chat_postMessage.call_args
        
        assert call_args[1]['channel'] == 'U123MANAGER'
        assert 'blocks' in call_args[1]  # Should use Block Kit
        
        # Verify buttons are present
        blocks = call_args[1]['blocks']
        action_block = next((b for b in blocks if b['type'] == 'actions'), None)
        assert action_block is not None
        
        buttons = action_block['elements']
        assert len(buttons) == 2
        assert buttons[0]['action_id'] == 'approve_mbo'
        assert buttons[1]['action_id'] == 'decline_mbo'
    
    @patch('app.notifications.slack_improved.WebClient')
    def test_deduplication_logic(self, mock_webclient):
        """Test message deduplication prevents spam."""
        from app.notifications.slack_improved import send_slack_notification, _is_duplicate_message
        
        mock_client = Mock()
        mock_webclient.return_value = mock_client
        mock_client.chat_postMessage.return_value = {"ok": True}
        
        mbo_data = {
            'id': 123,
            'manager_slack_id': 'U123MANAGER'
        }
        
        # First message should be sent
        send_slack_notification('mbo_created', mbo_data)
        assert mock_client.chat_postMessage.call_count == 1
        
        # Second message within 60 seconds should be blocked
        send_slack_notification('mbo_created', mbo_data)
        assert mock_client.chat_postMessage.call_count == 1  # Still 1, not 2
        
        # Test deduplication function directly
        assert _is_duplicate_message('U123MANAGER', 123, 'mbo_created') == True
    
    @patch('app.notifications.slack_improved.WebClient')
    def test_angelica_bcc_functionality(self, mock_webclient):
        """Test Angelica receives BCC copy of manager messages."""
        from app.notifications.slack_improved import send_slack_notification
        
        mock_client = Mock()
        mock_webclient.return_value = mock_client
        mock_client.chat_postMessage.return_value = {"ok": True}
        
        with patch('app.notifications.slack_improved.current_app') as mock_app:
            mock_app.config = {'SLACK_ANGELICA_ID': 'U123ANGELICA'}
            
            mbo_data = {
                'id': 123,
                'title': 'Test MBO',
                'manager_slack_id': 'U123MANAGER'
            }
            
            send_slack_notification('mbo_created', mbo_data)
            
            # Should send to both manager and Angelica
            assert mock_client.chat_postMessage.call_count == 2
            
            # Verify both calls
            calls = mock_client.chat_postMessage.call_args_list
            channels = [call[1]['channel'] for call in calls]
            
            assert 'U123MANAGER' in channels
            assert 'U123ANGELICA' in channels


class TestEventRecipientMatrix:
    """Test the complete event × recipient matrix from SLACK_VERIFICATION_MATRIX.md"""
    
    @patch('app.notifications.slack_improved.WebClient')
    def test_mbo_created_recipients(self, mock_webclient):
        """Test MBO created event sends to correct recipients."""
        from app.notifications.slack_improved import send_slack_notification
        
        mock_client = Mock()
        mock_webclient.return_value = mock_client
        mock_client.chat_postMessage.return_value = {"ok": True}
        
        with patch('app.notifications.slack_improved.current_app') as mock_app:
            mock_app.config = {'SLACK_ANGELICA_ID': 'U123ANGELICA'}
            
            mbo_data = {
                'id': 123,
                'manager_slack_id': 'U123MANAGER',
                'employee_slack_id': 'U123EMPLOYEE'
            }
            
            send_slack_notification('mbo_created', mbo_data)
            
            # Should send to manager (interactive), employee (notification), Angelica (BCC)
            assert mock_client.chat_postMessage.call_count == 3
    
    @patch('app.notifications.slack_improved.WebClient')
    def test_mbo_approved_recipients(self, mock_webclient):
        """Test MBO approved event sends only to employee."""
        from app.notifications.slack_improved import send_slack_notification
        
        mock_client = Mock()
        mock_webclient.return_value = mock_client
        mock_client.chat_postMessage.return_value = {"ok": True}
        
        mbo_data = {
            'id': 123,
            'employee_slack_id': 'U123EMPLOYEE'
        }
        
        send_slack_notification('mbo_approved', mbo_data)
        
        # Should send only to employee
        assert mock_client.chat_postMessage.call_count == 1
        call_args = mock_client.chat_postMessage.call_args
        assert call_args[1]['channel'] == 'U123EMPLOYEE'


def run_comprehensive_tests():
    """Run all tests and generate report."""
    print("🧪 Running Slack Interactive Messages Test Suite")
    print("=" * 60)
    
    # Test classes to run
    test_classes = [
        TestSlackInteractions,
        TestSlackNotifications,
        TestEventRecipientMatrix
    ]
    
    total_tests = 0
    passed_tests = 0
    
    for test_class in test_classes:
        print(f"\n📋 {test_class.__name__}")
        print("-" * 40)
        
        # Get all test methods
        test_methods = [method for method in dir(test_class) 
                       if method.startswith('test_')]
        
        for test_method in test_methods:
            total_tests += 1
            try:
                # Create instance and run test
                instance = test_class()
                instance.setup_method()
                getattr(instance, test_method)()
                instance.teardown_method()
                
                print(f"✅ {test_method}")
                passed_tests += 1
                
            except Exception as e:
                print(f"❌ {test_method}: {str(e)}")
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed_tests}/{total_tests} passed")
    
    if passed_tests == total_tests:
        print("🎉 All tests passed! Slack integration is working correctly.")
    else:
        print("⚠️  Some tests failed. Check implementation and configuration.")
    
    return passed_tests == total_tests


if __name__ == "__main__":
    run_comprehensive_tests()