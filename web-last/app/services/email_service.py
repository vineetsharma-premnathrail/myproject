# Email Service
# Email sending functionality for notifications and reports

from typing import List, Optional
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.config import settings
from app.utils.logger import logger


class EmailService:
    """Email service for sending notifications"""

    def __init__(self):
        self.smtp_server = settings.smtp_server
        """
        Email Service Module
        --------------------
        Purpose:
            Provides business logic for sending emails, such as notifications, password resets, and other transactional messages.
            Used by API endpoints and background tasks to communicate with users via email.
        Layer:
            Backend / Services / Email
        """

        self.smtp_port = settings.smtp_port
        self.username = settings.smtp_username
        self.password = settings.smtp_password

    def is_configured(self) -> bool:
        """Check if email service is properly configured"""
        return all([
            self.smtp_server,
            self.smtp_port,
            self.username,
            self.password
        ])

    def send_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        html_body: Optional[str] = None
    ) -> bool:
        """Send an email"""
        if not self.is_configured():
            return False

        # Type assertions after configuration check
        assert self.smtp_server is not None
        assert self.smtp_port is not None
        assert self.username is not None
        assert self.password is not None

        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.username
            msg['To'] = to_email

            # Add text body
            text_part = MIMEText(body, 'plain')
            msg.attach(text_part)

            # Add HTML body if provided
            if html_body:
                html_part = MIMEText(html_body, 'html')
                msg.attach(html_part)

            # Send email
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.username, self.password)
            server.sendmail(self.username, to_email, msg.as_string())
            server.quit()

            return True
        except smtplib.SMTPAuthenticationError as auth_err:
            logger.error("SMTP Authentication failed: %s", auth_err)
            return False
        except Exception as e:
            logger.exception("Failed to send email to %s: %s", to_email, e)
            return False

    def send_welcome_email(self, to_email: str, user_name: str) -> bool:
        """Send welcome email to new users"""
        subject = "Welcome to Engineering Tools SaaS"
        body = f"""
        Welcome {user_name}!

        Thank you for signing up for Engineering Tools SaaS.
        You can now access all our engineering calculation tools.

        Best regards,
        Engineering Tools Team
        """
        return self.send_email(to_email, subject, body)

    def send_license_activated_email(self, to_email: str) -> bool:
        """Send license activation confirmation"""
        subject = "License Activated - Engineering Tools SaaS"
        body = """
        Your license has been successfully activated!

        You now have access to all premium features and tools.

        Best regards,
        Engineering Tools Team
        """
        return self.send_email(to_email, subject, body)


# Global email service instance
email_service = EmailService()