# MBO Tracker Notification Fix - Rollback Instructions

## Overview
This document provides instructions to rollback all changes made to fix email and Slack notification issues in the MBO Tracker application.

## Changes Made
The following files were modified to fix notification issues:

1. **app/notifications.py** - Added `atdughetti@snaplogic.com` to CC lists
2. **app/notifications/slack_improved.py** - Enhanced error handling and fallback mechanisms
3. **verify_email.py** - Created email verification script
4. **verify_slack.py** - Created Slack verification script
5. **verify_email_simple.py** - Created simple email test script

## Rollback Commands

### 1. Revert notifications.py changes
```bash
cd mbo-tracker
git checkout HEAD -- app/notifications.py
```

### 2. Revert slack_improved.py changes
```bash
git checkout HEAD -- app/notifications/slack_improved.py
```

### 3. Remove verification scripts
```bash
rm -f verify_email.py verify_slack.py verify_email_simple.py ROLLBACK_INSTRUCTIONS.md
```

### 4. Restart the MBO Tracker service
```bash
sudo systemctl restart mbo-tracker
```

### 5. Verify rollback
```bash
sudo systemctl status mbo-tracker
```

## One-Liner Rollback Command
Execute this single command to rollback all changes:

```bash
cd mbo-tracker && git checkout HEAD -- app/notifications.py app/notifications/slack_improved.py && rm -f verify_email.py verify_slack.py verify_email_simple.py ROLLBACK_INSTRUCTIONS.md && sudo systemctl restart mbo-tracker && sudo systemctl status mbo-tracker
```

## What Gets Reverted

### Email Notifications
- Removes `atdughetti@snaplogic.com` from CC lists in all notification functions
- Reverts to original email recipient configuration

### Slack Notifications  
- Removes enhanced error handling and logging
- Removes fallback mechanism for Angelica notifications
- Reverts to original Slack recipient resolution logic

### Verification Scripts
- Removes all test scripts created for verification

## Post-Rollback State
After rollback:
- Email notifications will revert to original behavior (may not include troubleshooting recipient)
- Slack notifications will revert to original error-prone behavior
- No verification scripts will be available
- System will be in the exact state before fixes were applied

## Re-applying Fixes
If you need to re-apply the fixes after rollback, you can:
1. Re-run the original fix commands
2. Or restore from backup if available
3. Or manually re-implement the changes documented in the fix summary

## Support
If you encounter issues during rollback:
1. Check system logs: `sudo journalctl -u mbo-tracker -f`
2. Verify file permissions and ownership
3. Ensure the MBO Tracker service is running properly