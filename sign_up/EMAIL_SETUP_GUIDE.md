# Email Verification Setup Guide

## Overview
Your Flask application now includes email verification functionality. When users register, they will receive an email with a verification link that they must click to activate their account.

## Required Dependencies
Install the required packages:
```bash
pip install -r "Requirement .txt"
```

## Email Configuration

### 1. Gmail Setup (Recommended)
To use Gmail for sending emails:

1. **Enable 2-Factor Authentication** on your Gmail account
2. **Generate an App Password**:
   - Go to Google Account settings
   - Security → 2-Step Verification → App passwords
   - Generate a password for "Mail"
   - Copy the 16-character password

3. **Update .env file** with your credentials:
```env
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USE_SSL=False
MAIL_USERNAME=your_email@gmail.com
MAIL_PASSWORD=your_16_character_app_password
MAIL_DEFAULT_SENDER=your_email@gmail.com
SECRET_KEY=your_secret_key_here_change_this_in_production
APP_NAME=Africa House Pakistan
BASE_URL=http://localhost:5000
TOKEN_EXPIRY_HOURS=24
```

### 2. Other Email Providers
For other email providers, update the MAIL_SERVER and MAIL_PORT:

**Outlook/Hotmail:**
```env
MAIL_SERVER=smtp-mail.outlook.com
MAIL_PORT=587
```

**Yahoo:**
```env
MAIL_SERVER=smtp.mail.yahoo.com
MAIL_PORT=587
```

## Database Changes
The application automatically updates your database with new columns:
- `email_verified` (Boolean)
- `verification_token` (Text)
- `verification_token_expires` (DateTime)
- `created_at` (DateTime)

A new table `email_verification_logs` is also created to track verification attempts.

## How It Works

### 1. User Registration
- User fills out registration form
- System validates input (password match, length, unique email)
- User account is created with `email_verified = False`
- Verification email is sent automatically
- User is redirected to "verification sent" page

### 2. Email Verification
- User receives professional email with verification link
- Link expires in 24 hours for security
- Clicking link verifies the email and activates account
- User can then proceed to login

### 3. Resend Functionality
- Users can request a new verification email if needed
- New token is generated with fresh 24-hour expiry

## New Routes Added

- `/verification-sent` - Shows after registration
- `/verify-email/<token>` - Handles email verification
- `/resend-verification` - Resends verification email

## Security Features

- **Secure tokens** using URLSafeTimedSerializer
- **24-hour expiry** on verification links
- **Unique email constraint** prevents duplicates
- **Password validation** (minimum 6 characters)
- **SQL injection protection** with parameterized queries

## Testing

### 1. Local Testing
1. Update `.env` with your email credentials
2. Run the application: `python app.py`
3. Register a new account
4. Check your email for verification link
5. Click link to verify

### 2. Production Deployment
- Use environment variables instead of `.env` file
- Use a strong SECRET_KEY
- Consider using a dedicated email service (SendGrid, Mailgun)
- Update BASE_URL to your domain

## Troubleshooting

### Email Not Sending
1. Check your email credentials in `.env`
2. Verify Gmail app password is correct
3. Check spam folder
4. Look at console output for error messages

### Verification Link Not Working
1. Check if link has expired (24 hours)
2. Verify BASE_URL is correct
3. Check database for user record

### Database Issues
1. Delete `database.db` to reset
2. Run `python model.py` to recreate tables
3. Check console for SQL errors

## Email Template Customization
The verification email includes:
- Professional Africa House Pakistan branding
- Clear call-to-action button
- Security warnings about link expiry
- Plain text fallback
- Contact information

You can customize the email template in `email_utils.py` in the `send_verification_email` function.

## Support
For issues with email verification:
1. Check the console output for error messages
2. Verify your email provider settings
3. Test with a different email address
4. Contact support if problems persist
