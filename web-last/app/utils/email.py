"""
Email OTP Utility Module
-----------------------
Purpose:
    Provides functions for generating, sending, storing, verifying, and deleting OTPs (One-Time Passwords) for user email verification.
    Handles all email-related logic for user authentication flows.
Layer:
    Backend / Utilities / Email & OTP
"""

import smtplib
import secrets
import string
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.utils import formataddr
from datetime import datetime, timedelta
import os
from app.config import settings
from app.utils.logger import logger

# In-memory OTP storage (for production, use Redis/Database)
otp_storage = {}
# In-memory verified emails store (email -> expiry datetime)
verified_emails = {}

# SMTP Configuration (from config)
SMTP_HOST = settings.smtp_server
SMTP_PORT = settings.smtp_port
SMTP_USER = settings.smtp_username
SMTP_PASSWORD = settings.smtp_password

# Logo path - relative to project root
LOGO_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "images", "logo.png")

def generate_otp(length=6):
    """
    Generate a random numeric OTP (One-Time Password).

    Parameters:
        length (int): Number of digits in the OTP (default: 6)

    Returns:
        str: The generated OTP as a string
    """
    return ''.join(secrets.choice(string.digits) for _ in range(length))

def send_otp_email(to_email: str, otp: str) -> bool:
    """
    Send an OTP email to the user with an embedded company logo.

    Parameters:
        to_email (str): Recipient's email address
        otp (str): The OTP code to send

    Returns:
        bool: True if email sent successfully, False otherwise

    Raises:
        smtplib.SMTPAuthenticationError: If SMTP authentication fails
        Exception: For other email sending errors
    """
    try:
        # Ensure SMTP credentials are configured
        if not SMTP_HOST or not SMTP_PORT or not SMTP_USER or not SMTP_PASSWORD:
            logger.error("SMTP configuration incomplete: SMTP_HOST, SMTP_PORT, SMTP_USER, or SMTP_PASSWORD missing")
            return False

        # Type assertions after validation
        assert SMTP_HOST is not None
        assert SMTP_PORT is not None
        assert SMTP_USER is not None
        assert SMTP_PASSWORD is not None

        # Create email with 'related' for embedded images
        msg = MIMEMultipart('related')
        msg['Subject'] = f'{otp} - Verification Code | Premnathrail Engineering'
        msg['From'] = formataddr(('Premnathrail Engineering', SMTP_USER))
        msg['To'] = to_email

        # HTML Email Body with embedded logo
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: 'Helvetica', Arial, sans-serif; background-color: #f4f4f4; margin: 0; padding: 20px; }}
                .container {{ max-width: 500px; margin: 0 auto; background-color: #ffffff; padding: 40px; border-radius: 10px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); }}
                .logo-section {{ text-align: center; margin-bottom: 20px; padding-bottom: 20px; border-bottom: 3px solid #16a34a; }}
                .logo-img {{ max-width: 180px; height: auto; }}
                .otp-box {{ font-size: 42px; font-weight: bold; letter-spacing: 12px; color: #000000; background: #f0fdf4; padding: 25px; text-align: center; border-radius: 10px; margin: 30px 0; border: 3px solid #16a34a; }}
                .text {{ color: #4b5563; font-size: 16px; line-height: 1.8; text-align: center; }}
                .warning {{ background: #fef3c7; color: #92400e; font-size: 14px; padding: 15px; border-radius: 8px; margin-top: 25px; text-align: center; }}
                .footer {{ font-size: 12px; color: #9ca3af; text-align: center; margin-top: 30px; border-top: 1px solid #e5e7eb; padding-top: 20px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="logo-section">
                    <img src="cid:company_logo" alt="Premnath Engineering Works" class="logo-img">
                </div>
                <h2 style="text-align:center; color:#111827; margin-bottom: 10px;">Email Verification Code</h2>
                <p class="text">Hello,</p>
                <p class="text">Please use the verification code below to complete your registration:</p>
                <div class="otp-box">{otp}</div>
                <div class="warning">
                    ⚠️ This code expires in <strong>10 minutes</strong>.<br>
                    Do not share this code with anyone.
                </div>


                <div class="footer">
                    <p>If you didn't request this code, please ignore this email.</p>
                    <p><strong>Premnath Engineering Works</strong></p>
                    <p>© 2024 All Rights Reserved</p>
                </div>
            </div>
        </body>
        </html>
        """

        text = f"Your verification code is: {otp}. Valid for 10 minutes. Do not share with anyone."

        # Create alternative part for HTML/Plain text
        msg_alternative = MIMEMultipart('alternative')
        msg.attach(msg_alternative)
        msg_alternative.attach(MIMEText(text, 'plain'))
        msg_alternative.attach(MIMEText(html, 'html'))

        # Embed logo image if exists
        if os.path.exists(LOGO_PATH):
            with open(LOGO_PATH, 'rb') as f:
                img_data = f.read()
                image = MIMEImage(img_data)
                image.add_header('Content-ID', '<company_logo>')
                image.add_header('Content-Disposition', 'inline', filename='logo.png')
                msg.attach(image)
        else:
            logger.warning("Logo file not found at: %s", LOGO_PATH)

        # Send email via Gmail SMTP
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(SMTP_USER, to_email, msg.as_string())

        logger.info("OTP sent successfully to %s", to_email)
        return True

    except smtplib.SMTPAuthenticationError as e:
        # Authentication error with SMTP server
        logger.error("SMTP Authentication failed: %s", e)
        return False
    except Exception as e:
        # Any other error during email sending
        logger.exception("Email sending failed to %s: %s", to_email, e)
        return False

def store_otp(email: str, otp: str):
    """
    Store an OTP for a given email address with an expiry time.

    Parameters:
        email (str): The user's email address
        otp (str): The OTP code to store

    Returns:
        None
    """
    otp_storage[email.lower()] = {
        'otp': otp,
        'expires_at': datetime.now() + timedelta(minutes=10),
        'attempts': 0
    }


def mark_email_verified(email: str, expiry_minutes: int = 60):
    """
    Mark an email as verified for a limited time window.

    Parameters:
        email (str): Email address to mark verified
        expiry_minutes (int): How long the verification should remain valid
    """
    verified_emails[email.lower()] = datetime.now() + timedelta(minutes=expiry_minutes)


def is_email_verified(email: str) -> bool:
    """
    Check whether an email is currently marked as verified.
    Expired entries are removed.
    """
    email = email.lower()
    if email not in verified_emails:
        return False
    if datetime.now() > verified_emails[email]:
        del verified_emails[email]
        return False
    return True

def verify_otp(email: str, otp: str) -> dict:
    """
    Verify an OTP for a given email address.

    Parameters:
        email (str): The user's email address
        otp (str): The OTP code to verify

    Returns:
        dict: Result of verification with success status and message
    """
    email = email.lower()

    # Check if OTP exists for the email
    if email not in otp_storage:
        return {'success': False, 'message': 'OTP not found. Please request a new one.'}

    stored = otp_storage[email]

    # Check if OTP is expired
    if datetime.now() > stored['expires_at']:
        del otp_storage[email]
        return {'success': False, 'message': 'OTP expired. Please request a new one.'}

    # Check if maximum attempts exceeded (max 3)
    if stored['attempts'] >= 3:
        del otp_storage[email]
        return {'success': False, 'message': 'Too many attempts. Please request a new OTP.'}

    # Verify OTP value
    if stored['otp'] == otp:
        # mark email as verified for a limited window and delete the stored OTP
        mark_email_verified(email, expiry_minutes=60)
        del otp_storage[email]
        return {'success': True, 'message': 'Email verified successfully!'}
    else:
        stored['attempts'] += 1
        remaining = 3 - stored['attempts']
        return {'success': False, 'message': f'Invalid OTP. {remaining} attempts remaining.'}

def delete_otp(email: str):
    """
    Delete the OTP for a given email address after successful verification or expiry.

    Parameters:
        email (str): The user's email address

    Returns:
        None
    """
    email = email.lower()
    if email in otp_storage:
        del otp_storage[email]
