# Slack Message Verification Matrix

This document provides a comprehensive mapping of MBO events to Slack message recipients and expected content.

## Event × Recipient Matrix

| Event | Manager | Employee | Angelica (BCC) | Message Type |
|-------|---------|----------|----------------|--------------|
| MBO Created | ✅ Interactive | ✅ Notification | ✅ Copy | Block Kit + Plain |
| MBO Approved | ❌ | ✅ Notification | ❌ | Plain Text |
| MBO Declined | ❌ | ✅ Notification | ❌ | Plain Text |
| MBO Completed | ✅ Interactive | ✅ Notification | ✅ Copy | Block Kit + Plain |
| MBO Edited | ✅ Interactive | ✅ Notification | ✅ Copy | Block Kit + Plain |

## Message Content Verification

### Manager Approval Messages (Interactive)

**Event: MBO Created/Completed/Edited**
- **Format**: Block Kit with interactive buttons
- **Buttons**: ✅ Approve, ❌ Decline
- **Content**: Employee name, MBO title, description, action required
- **Deduplication**: 60-second window to prevent spam

**Expected Block Structure**:
```json
{
  "blocks": [
    {
      "type": "section",
      "text": {
        "type": "mrkdwn",
        "text": "*MBO Approval Required*\n\n*Employee:* John Doe\n*Title:* Q4 Sales Target\n*Description:* Achieve 120% of quarterly sales target..."
      }
    },
    {
      "type": "actions",
      "elements": [
        {
          "type": "button",
          "text": {"type": "plain_text", "text": "✅ Approve"},
          "style": "primary",
          "action_id": "approve_mbo",
          "value": "mbo_123"
        },
        {
          "type": "button",
          "text": {"type": "plain_text", "text": "❌ Decline"},
          "style": "danger",
          "action_id": "decline_mbo",
          "value": "mbo_123"
        }
      ]
    }
  ]
}
```

### Employee Notifications (Plain Text)

**Event: MBO Approved**
- **Content**: "Your MBO '[Title]' has been approved by [Manager]."

**Event: MBO Declined**
- **Content**: "Your MBO '[Title]' has been declined by [Manager]. Please review and resubmit."

**Event: MBO Created/Completed/Edited**
- **Content**: "Your MBO '[Title]' has been submitted for approval."

### Angelica BCC Messages (Copy)

**Purpose**: Troubleshooting and monitoring
- **Recipients**: Only Angelica (SLACK_ANGELICA_ID)
- **Content**: Exact copy of manager's interactive message
- **Format**: Same Block Kit structure as manager message
- **Trigger**: Only for events requiring manager approval

## Environment Variables

| Variable | Purpose | Example |
|----------|---------|---------|
| `SLACK_BOT_TOKEN` | Bot authentication | `your_slack_bot_token_from_oauth_page` |
| `SLACK_SIGNING_SECRET` | Request verification | `your_signing_secret_from_basic_info_page` |
| `SLACK_ANGELICA_ID` | Angelica's Slack user ID | `U123ANGELICA` |
| `BASE_URL` | Application base URL | `https://your-domain.com` |

## Deduplication Logic

**Purpose**: Prevent spam from rapid successive events
**Implementation**: Time-based cache with 60-second window
**Key Format**: `{user_id}:{mbo_id}:{event_type}`

**Example**:
```python
cache_key = f"U123MANAGER:mbo_456:created"
if cache_key in recent_messages and time.time() - recent_messages[cache_key] < 60:
    return  # Skip duplicate message
```

## Interactive Button Handling

### Action IDs
- `approve_mbo`: Handles ✅ Approve button clicks
- `decline_mbo`: Handles ❌ Decline button clicks

### Button Values
- Format: `mbo_{id}` where `{id}` is the MBO database ID
- Example: `mbo_123` for MBO with ID 123

### Response Handling
1. **Signature Verification**: Validates request authenticity using HMAC-SHA256
2. **Action Processing**: Updates MBO status in database
3. **Message Update**: Replaces interactive buttons with status text
4. **User Feedback**: Shows success/error message to button clicker

## Testing Scenarios

### Scenario 1: New MBO Creation
1. **Trigger**: Employee creates new MBO
2. **Expected Messages**:
   - Manager: Interactive approval message with buttons
   - Employee: "MBO submitted for approval" notification
   - Angelica: Copy of manager's interactive message

### Scenario 2: Manager Approval
1. **Trigger**: Manager clicks ✅ Approve button
2. **Expected Behavior**:
   - Original message updated to show "Approved by [Manager]"
   - Employee receives "MBO approved" notification
   - Database updated with approval status

### Scenario 3: Manager Decline
1. **Trigger**: Manager clicks ❌ Decline button
2. **Expected Behavior**:
   - Original message updated to show "Declined by [Manager]"
   - Employee receives "MBO declined" notification
   - Database updated with declined status

### Scenario 4: Deduplication Test
1. **Setup**: Create MBO, wait < 60 seconds
2. **Trigger**: Edit same MBO
3. **Expected**: No duplicate message sent to manager
4. **Verification**: Check logs for "Duplicate message prevented"

## Error Handling

### Signature Verification Failure
- **Cause**: Invalid SLACK_SIGNING_SECRET or tampered request
- **Response**: HTTP 401 Unauthorized
- **Logging**: "Slack signature verification failed"

### Missing Environment Variables
- **Cause**: SLACK_BOT_TOKEN or SLACK_SIGNING_SECRET not set
- **Response**: Application startup failure
- **Logging**: "Missing required Slack configuration"

### API Rate Limiting
- **Cause**: Too many Slack API requests
- **Response**: Exponential backoff retry
- **Logging**: "Slack API rate limit exceeded, retrying..."

### Invalid User IDs
- **Cause**: User not found in Slack workspace
- **Response**: Skip message, log warning
- **Logging**: "User [ID] not found in Slack workspace"

## Monitoring and Debugging

### Log Patterns to Monitor
- `"Sending Slack message to user"` - Normal message sending
- `"Duplicate message prevented"` - Deduplication working
- `"Slack signature verification failed"` - Security issue
- `"Interactive button clicked"` - User engagement

### Health Check Endpoints
- `/slack/interactions` - Should return 200 for valid POST requests
- Application logs should show Slack SDK initialization

### Common Issues
1. **Buttons not working**: Check Interactivity configuration in Slack app
2. **Messages not sending**: Verify bot token and permissions
3. **Signature failures**: Ensure signing secret matches Slack app settings
4. **Duplicate messages**: Check deduplication cache implementation

This matrix serves as the definitive reference for verifying correct Slack integration behavior across all MBO workflow scenarios.