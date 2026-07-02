"""
email_utils.py
----------------
Standalone email-sending helper for Food Saver.

Uses Python's built-in smtplib so no new dependency needs to be added
to requirements.txt. Works with Gmail SMTP, Outlook, SendGrid SMTP,
Mailgun SMTP, Amazon SES SMTP, or any standard SMTP provider - just
set the environment variables below.

Required environment variables (set these on Render / your host):
    MAIL_SERVER    e.g. "smtp.gmail.com"
    MAIL_PORT      e.g. "587"
    MAIL_USERNAME  the SMTP login / sender email address
    MAIL_PASSWORD  the SMTP password or app password
    MAIL_FROM      (optional) "From" address shown to recipients,
                   defaults to MAIL_USERNAME if not set

If MAIL_USERNAME / MAIL_PASSWORD are not configured, or if sending
fails for any reason (bad credentials, network issue, etc.), this
module logs the error and returns False - it NEVER raises, so it
can never break registration or donation flows.
"""

import os
import smtplib
import logging
from email.mime.text import MIMEText

logger = logging.getLogger("email_utils")


def _send_email(to_email, subject, body):
    """
    Internal helper: sends a plain-text email.
    Returns True on success, False on any failure (never raises).
    """
    mail_server = os.environ.get("MAIL_SERVER", "smtp.gmail.com")
    mail_port = int(os.environ.get("MAIL_PORT", "587"))
    mail_username = os.environ.get("MAIL_USERNAME")
    mail_password = os.environ.get("MAIL_PASSWORD")
    mail_from = os.environ.get("MAIL_FROM", mail_username)

    if not to_email or not mail_username or not mail_password:
        logger.warning("Email not sent: missing recipient or SMTP credentials.")
        return False

    try:
        msg = MIMEText(body, "plain")
        msg["Subject"] = subject
        msg["From"] = mail_from
        msg["To"] = to_email

        with smtplib.SMTP(mail_server, mail_port, timeout=10) as server:
            server.starttls()
            server.login(mail_username, mail_password)
            server.sendmail(mail_from, [to_email], msg.as_string())

        return True

    except Exception as e:
        # Any SMTP/network error is caught here so the caller's
        # registration/donation flow is never interrupted.
        logger.error("Failed to send email to %s: %s", to_email, e)
        return False


def send_registration_email(user_email, user_name):
    """Sends the 'Welcome to Food Saver!' email after successful registration."""
    subject = "Welcome to Food Saver!"
    body = f"""Hello {user_name},

Thank you for registering with Food Saver.

We are delighted to have you as a member of our community.

Together, we can reduce food waste and help people in need.

Thank you for joining us!

Regards,
Food Saver Team
"""
    return _send_email(user_email, subject, body)


def send_donation_email(user_email, user_name):
    """Sends the 'Food Donation Successful' email after a successful donation."""
    subject = "Food Donation Successful"
    body = f"""Hello {user_name},

Thank you for donating food through Food Saver.

Your donation has been successfully recorded.

Your kindness helps reduce food waste and supports people in need.

Thank you for making a difference.

Regards,
Food Saver Team
"""
    return _send_email(user_email, subject, body)
  
