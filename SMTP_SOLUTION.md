# SMTP Email Solution for MBO Tracker

## Problem Diagnosis

The MBO Tracker application was failing to send emails because:

1. **Wrong Authentication Method**: The app was trying to use an Okta app password (`")cXzn2'z"`) with Gmail SMTP
2. **Gmail Account**: `notificationsmbo@snaplogic.com` is a **Gmail account**, not Office 365
3. **Missing App Password**: Gmail requires an App Password for SMTP authentication, not the regular account password

## Error Analysis

The SMTP test showed:
- ✅ Connection to `smtp.gmail.com:587` works
- ✅ STARTTLS encryption works  
- ❌ Authentication fails with error 535: "Username and Password not accepted"

This confirms the credentials are wrong for Gmail SMTP.

## Solution

### Step 1: Generate Gmail App Password

You need to generate a Gmail App Password for `notificationsmbo@snaplogic.com`:

1. Go to [Google Account Settings](https://myaccount.google.com/)
2. Navigate to **Security** → **2-Step Verification** → **App passwords**
3. Generate a new app password for "Mail"
4. Copy the 16-character password (format: `xxxx xxxx xxxx xxxx`)

### Step 2: Update Environment Variables

Replace `<GMAIL_APP_PASSWORD>` in `.env` with the actual Gmail App Password:

```bash
# Mail configuration - Gmail SMTP
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=notificationsmbo@snaplogic.com
MAIL_PASSWORD=your-16-char-app-password-here

# SMTP configuration (for email.py utility)
SMTP_USERNAME=notificationsmbo@snaplogic.com
SMTP_PASSWORD=your-16-char-app-password-here
```

### Step 3: Test Configuration

Run the verification script:
```bash
cd mbo-tracker
python3 verify_smtp.py
```

### Step 4: Update Application Code

The existing email utilities in `app/utils/email.py` are already correctly configured for Gmail SMTP. No code changes needed once the App Password is set.

## Technical Details

- **SMTP Host**: `smtp.gmail.com`
- **Port**: `587` (STARTTLS)
- **Authentication**: Gmail App Password
- **From Address**: `notificationsmbo@snaplogic.com`
- **BCC**: All emails automatically BCC to `notificationsmbo@snaplogic.com`

## Security Notes

- Gmail App Passwords are more secure than regular passwords for SMTP
- The app password only works for SMTP, not web login
- Keep the app password secure in environment variables
- Never commit passwords to version control

## Testing

After setting the Gmail App Password, the verification script should show:
```
✅ SUCCESS - Test email sent successfully!
```

And you should receive a test email at `notificationsmbo@snaplogic.com`.