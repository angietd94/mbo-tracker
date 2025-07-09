# Slack App Configuration Guide

This guide walks through setting up a Slack app to enable interactive messages for the MBO tracker.

## Prerequisites

- Slack workspace admin access
- MBO tracker application deployed and accessible via HTTPS
- Basic understanding of Slack app configuration

## Step 1: Create Slack App

1. Go to [https://api.slack.com/apps](https://api.slack.com/apps)
2. Click "Create New App"
3. Choose "From scratch"
4. Enter app name: "MBO Tracker"
5. Select your workspace
6. Click "Create App"

## Step 2: Configure Basic Information

1. In the app dashboard, go to "Basic Information"
2. Scroll down to "App Credentials"
3. Copy the "Signing Secret" - you'll need this later
4. Optionally add app icon and description

## Step 3: Configure OAuth & Permissions

1. Go to "OAuth & Permissions" in the sidebar
2. Scroll down to "Scopes"
3. Add the following Bot Token Scopes:
   - `chat:write` - Send messages as the bot
   - `chat:write.public` - Send messages to channels the bot isn't in
   - `users:read` - Read user information
   - `users:read.email` - Read user email addresses

4. Scroll up to "OAuth Tokens for Your Workspace"
5. Click "Install to Workspace"
6. Review permissions and click "Allow"
7. Copy the "Bot User OAuth Token" - you'll need this later

## Step 4: Enable Interactivity

1. Go to "Interactivity & Shortcuts" in the sidebar
2. Turn on "Interactivity"
3. Set the Request URL to: `https://your-domain.com/slack/interactions`
   - Replace `your-domain.com` with your actual domain
   - This endpoint handles button clicks and other interactive elements

4. Click "Save Changes"

## Step 5: Configure Event Subscriptions (Optional)

If you want to handle additional Slack events:

1. Go to "Event Subscriptions" in the sidebar
2. Turn on "Enable Events"
3. Set the Request URL to: `https://your-domain.com/slack/events`
4. Subscribe to bot events as needed
5. Click "Save Changes"

## Step 6: Configure Environment Variables

Add these to your application's environment:
```bash
SLACK_BOT_TOKEN=your_slack_bot_token_from_oauth_page
SLACK_SIGNING_SECRET=your_signing_secret_from_basic_info_page
SLACK_ANGELICA_ID=U123ANGELICA
BASE_URL=https://your-domain.com
```

### Finding User IDs

To find Slack user IDs (like Angelica's):
1. In Slack, right-click on the user's profile
2. Select "Copy member ID"
3. The ID will be in format `U123ABC456`

## Step 7: Test the Integration

1. Restart your application to load the new environment variables
2. Trigger an MBO approval workflow
3. Check that:
   - Manager receives interactive message with ✅ Approve / ❌ Decline buttons
   - Clicking buttons updates the message
   - No "This app is not configured to handle interactive responses" tooltip appears

## Troubleshooting

### Common Issues

**"This app is not configured to handle interactive responses"**
- Verify Interactivity is enabled in Slack app settings
- Check that Request URL is correct and accessible
- Ensure SLACK_SIGNING_SECRET is set correctly

**Messages not sending**
- Verify SLACK_BOT_TOKEN is correct
- Check that bot has necessary permissions
- Ensure bot is added to relevant channels

**Signature verification failures**
- Verify SLACK_SIGNING_SECRET matches the one in Slack app settings
- Check that your server time is synchronized
- Ensure the signing secret hasn't been regenerated

### Testing Locally

For local development with ngrok:

1. Install ngrok: `npm install -g ngrok`
2. Start your local server: `python app.py`
3. In another terminal: `ngrok http 5000`
4. Copy the HTTPS URL from ngrok
5. Update Slack app Request URL to: `https://abc123.ngrok.io/slack/interactions`
6. Test the integration

### Logs and Debugging

The application includes comprehensive logging for Slack interactions:
- Check application logs for signature verification issues
- Monitor `/slack/interactions` endpoint for incoming requests
- Angelica receives BCC copies of manager messages for troubleshooting

## Security Notes

- Never commit Slack tokens to version control
- Use environment variables for all sensitive configuration
- Regularly rotate tokens if compromised
- Monitor Slack app usage in your workspace settings

## Next Steps

Once configured, the MBO tracker will automatically:
- Send interactive approval messages to managers
- Handle button clicks and update message status
- Provide deduplication to prevent spam
- Copy messages to Angelica for troubleshooting

The implementation is already complete in the codebase - only this Slack app configuration is required.