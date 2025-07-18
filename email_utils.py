import os
import secrets
import sqlite3
from datetime import datetime, timedelta
from flask import url_for, current_app
from flask_mail import Message
from itsdangerous import URLSafeTimedSerializer

def generate_verification_token():
    """Generate a secure random token for email verification"""
    return secrets.token_urlsafe(32)

def create_verification_token(email):
    """Create a signed token for email verification"""
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return serializer.dumps(email, salt='email-verification')

def verify_token(token, expiration=86400):  # 24 hours default
    """Verify the email verification token"""
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        email = serializer.loads(token, salt='email-verification', max_age=expiration)
        return email
    except:
        return None

def send_verification_email(mail, user_email, user_name, verification_token):
    """Send email verification email to user"""
    try:
        # Create verification URL
        verification_url = url_for('verify_email', 
                                 token=verification_token, 
                                 _external=True)
        
        # Create email message
        msg = Message(
            subject=f'Verify Your Email - {current_app.config.get("APP_NAME", "Africa House Pakistan")}',
            sender=current_app.config['MAIL_DEFAULT_SENDER'],
            recipients=[user_email]
        )
        
        # Email body (HTML)
        msg.html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Email Verification</title>
            <style>
                body {{
                    font-family: 'Arial', sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                    background-color: #f8f9fa;
                }}
                .container {{
                    background-color: #ffffff;
                    border-radius: 10px;
                    padding: 30px;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                }}
                .header {{
                    text-align: center;
                    margin-bottom: 30px;
                }}
                .logo {{
                    color: #006A44;
                    font-size: 24px;
                    font-weight: bold;
                    margin-bottom: 10px;
                }}
                .title {{
                    color: #006A44;
                    font-size: 28px;
                    margin-bottom: 20px;
                }}
                .content {{
                    margin-bottom: 30px;
                }}
                .verify-button {{
                    display: inline-block;
                    background-color: #006A44;
                    color: white;
                    padding: 15px 30px;
                    text-decoration: none;
                    border-radius: 5px;
                    font-weight: bold;
                    margin: 20px 0;
                }}
                .verify-button:hover {{
                    background-color: #004d32;
                }}
                .footer {{
                    margin-top: 30px;
                    padding-top: 20px;
                    border-top: 1px solid #eee;
                    font-size: 14px;
                    color: #666;
                }}
                .warning {{
                    background-color: #fff3cd;
                    border: 1px solid #ffeaa7;
                    color: #856404;
                    padding: 15px;
                    border-radius: 5px;
                    margin: 20px 0;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <div class="logo">Africa House Pakistan</div>
                    <h1 class="title">Verify Your Email Address</h1>
                </div>
                
                <div class="content">
                    <p>Dear {user_name},</p>
                    
                    <p>Welcome to Africa House Pakistan! We're excited to have you join our platform that connects Pakistani businesses with opportunities across the African continent.</p>
                    
                    <p>To complete your registration and start exploring trade opportunities, please verify your email address by clicking the button below:</p>
                    
                    <div style="text-align: center;">
                        <a href="{verification_url}" class="verify-button">Verify Email Address</a>
                    </div>
                    
                    <p>If the button doesn't work, you can copy and paste this link into your browser:</p>
                    <p style="word-break: break-all; color: #006A44;">{verification_url}</p>
                    
                    <div class="warning">
                        <strong>Important:</strong> This verification link will expire in 24 hours for security reasons. If you don't verify your email within this time, you'll need to register again.
                    </div>
                    
                    <p>Once verified, you'll be able to:</p>
                    <ul>
                        <li>Access your vendor dashboard</li>
                        <li>Connect with trade partners across Africa</li>
                        <li>Explore business opportunities</li>
                        <li>Use our AI assistant for trade insights</li>
                    </ul>
                </div>
                
                <div class="footer">
                    <p>If you didn't create an account with Africa House Pakistan, please ignore this email.</p>
                    <p>For support, contact us at support@africahousepakistan.com</p>
                    <p>&copy; 2024 Africa House Pakistan. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Plain text version
        msg.body = f"""
        Dear {user_name},

        Welcome to Africa House Pakistan!

        Please verify your email address by clicking the following link:
        {verification_url}

        This link will expire in 24 hours.

        If you didn't create an account with us, please ignore this email.

        Best regards,
        Africa House Pakistan Team
        """
        
        # Send email
        mail.send(msg)
        return True
        
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        return False

def log_verification_attempt(user_id, email, verification_token):
    """Log email verification attempt to database"""
    try:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO email_verification_logs (user_id, email, verification_token)
            VALUES (?, ?, ?)
        ''', (user_id, email, verification_token))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error logging verification attempt: {str(e)}")
        return False

def mark_email_verified(email):
    """Mark user's email as verified in database"""
    try:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        
        # Update user's email verification status
        cursor.execute('''
            UPDATE users 
            SET email_verified = TRUE, verification_token = NULL, verification_token_expires = NULL
            WHERE email = ?
        ''', (email,))
        
        # Update verification log
        cursor.execute('''
            UPDATE email_verification_logs 
            SET verified_at = CURRENT_TIMESTAMP, status = 'verified'
            WHERE email = ? AND status = 'pending'
        ''', (email,))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error marking email as verified: {str(e)}")
        return False
