# app/routes/slack_interactions.py

import json
import hmac
import hashlib
import time
import requests
from flask import request, jsonify, current_app
from app import app, db
from app.models import MBO, User
import logging

logger = logging.getLogger(__name__)

def verify_slack_signature(request_body, timestamp, signature):
    """Verify Slack request signature for security."""
    signing_secret = current_app.config.get('SLACK_SIGNING_SECRET')
    
    if not signing_secret:
        logger.error("SLACK_SIGNING_SECRET not found in environment variables")
        return False
    
    # Check timestamp to prevent replay attacks (within 5 minutes)
    current_time = int(time.time())
    if abs(current_time - int(timestamp)) > 300:
        logger.error(f"Request timestamp too old: {timestamp}")
        return False
    
    # Create signature base string
    sig_basestring = f"v0:{timestamp}:{request_body}"
    
    # Calculate expected signature
    expected_signature = 'v0=' + hmac.new(
        signing_secret.encode(),
        sig_basestring.encode(),
        hashlib.sha256
    ).hexdigest()
    
    # Compare signatures
    if not hmac.compare_digest(expected_signature, signature):
        logger.error("Invalid Slack signature")
        return False
    
    return True

def update_mbo_status(mbo_id, status, slack_user_id):
    """Update MBO approval status."""
    try:
        mbo = MBO.query.get(mbo_id)
        if not mbo:
            logger.error(f"MBO {mbo_id} not found")
            return False
        
        # Update status
        if status == 'approved':
            mbo.approval_status = 'Approved'
        elif status == 'declined':
            mbo.approval_status = 'Rejected'
        else:
            logger.error(f"Invalid status: {status}")
            return False
        
        db.session.commit()
        logger.info(f"MBO {mbo_id} {status} by Slack user {slack_user_id}")
        return True
        
    except Exception as e:
        logger.error(f"Error updating MBO {mbo_id}: {str(e)}")
        db.session.rollback()
        return False

@app.route('/slack/interactions', methods=['POST'])
def handle_slack_interaction():
    """Handle Slack interactive button clicks."""
    try:
        # Get request data
        timestamp = request.headers.get('X-Slack-Request-Timestamp')
        signature = request.headers.get('X-Slack-Signature')
        request_body = request.get_data(as_text=True)
        
        logger.info(f"Slack interaction received - Timestamp: {timestamp}, Signature: {signature[:20]}...")
        
        # Verify signature
        if not verify_slack_signature(request_body, timestamp, signature):
            logger.error("Signature verification failed")
            return jsonify({'error': 'Unauthorized'}), 401
        
        # Parse payload
        try:
            payload_data = request.form.get('payload')
            if not payload_data:
                logger.error("No payload found in request")
                return jsonify({'error': 'No payload'}), 400
                
            payload = json.loads(payload_data)
        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"Error parsing payload: {str(e)}")
            return jsonify({'error': 'Invalid payload'}), 400
        
        # Handle block actions (button clicks)
        if payload.get('type') == 'block_actions':
            actions = payload.get('actions', [])
            user = payload.get('user', {})
            response_url = payload.get('response_url')
            
            for action in actions:
                action_id = action.get('action_id')
                value = action.get('value')
                
                if action_id in ['approve_mbo', 'decline_mbo']:
                    # Extract MBO ID from value (format: "mbo_123")
                    try:
                        mbo_id = int(value.replace('mbo_', ''))
                    except (ValueError, AttributeError):
                        logger.error(f"Invalid MBO ID format: {value}")
                        continue
                    
                    # Determine status
                    status = 'approved' if action_id == 'approve_mbo' else 'declined'
                    
                    # Update MBO
                    if update_mbo_status(mbo_id, status, user.get('id')):
                        # Send response back to Slack
                        response_text = f"✅ MBO {mbo_id} has been {status}!"
                        
                        if response_url:
                            try:
                                requests.post(response_url, json={
                                    'text': response_text,
                                    'replace_original': True
                                }, timeout=5)
                            except requests.RequestException as e:
                                logger.error(f"Error sending response to Slack: {str(e)}")
                        
                        return jsonify({'text': response_text}), 200
                    else:
                        error_text = f"❌ Failed to {status.replace('ed', 'e')} MBO {mbo_id}"
                        return jsonify({'text': error_text}), 500
        
        # Default response
        return jsonify({'text': 'Action processed'}), 200
        
    except Exception as e:
        logger.error(f"Error handling Slack interaction: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500