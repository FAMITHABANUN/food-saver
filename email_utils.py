"""
email_utils.py
----------------
Standalone email-sending helper for Food Saver.

Uses Gmail API over HTTPS (OAuth2) instead of SMTP.
This works on Render's free plan because HTTPS is not blocked.
No third-party packages needed — uses Python's built-in urllib only.

Required environment variables (set on Render → Environment tab):
    GMAIL_CLIENT_ID      your Google OAuth client ID
    GMAIL_CLIENT_SECRET  your Google OAuth client secret
    GMAIL_REFRESH_TOKEN  your OAuth refresh token
    GMAIL_SENDER         sender email e.g. famibanu786@gmail.com

If sending fails for any reason, this module logs the error and
returns False - it NEVER raises, so it can never break registration
or donation flows.
"""

import os
import json
import base64
import logging
import urllib.request
import urllib.parse
import urllib.error
from email.mime.text import MIMEText

logger = logging.getLogger("email_utils")


def _get_access_token(client_id, client_secret, refresh_token):
    """Exchange refresh token for a short-lived access token."""
    data = urllib.parse.urlencode({
        "client_id": client_id,
        "client_secret": client_secret,
        "refresh_token": refresh_token,
        "grant_type": "refresh_token"
    }).encode("utf-8")

    req = urllib.request.Request(
        "https://oauth2.googleapis.com/token",
        data=data,
        method="POST"
    )

    with urllib.request.urlopen(req, timeout=10) as resp:
        result = json.loads(resp.read().decode("utf-8"))
        return result["access_token"]


def _send_email(to_email, subject, body):
    """
    Internal helper: sends email via Gmail API over HTTPS.
    Returns True on success, False on any failure (never raises).
    """
    client_id     = os.environ.get("GMAIL_CLIENT_ID")
    client_secret = os.environ.get("GMAIL_CLIENT_SECRET")
    refresh_token = os.environ.get("GMAIL_REFRESH_TOKEN")
    sender        = os.environ.get("GMAIL_SENDER")

    if not all([client_id, client_secret, refresh_token, sender, to_email]):
        logger.warning("Email not sent: missing credentials or recipient.")
        return False

    try:
        # Step 1: get a fresh access token
        access_token = _get_access_token(client_id, client_secret, refresh_token)

        # Step 2: build the email message
        msg = MIMEText(body, "plain")
        msg["To"]      = to_email
        msg["From"]    = sender
        msg["Subject"] = subject

        # Step 3: base64url-encode the raw message
        raw = base64.urlsafe_b64encode(msg.as_bytes()).decode("utf-8")

        # Step 4: send via Gmail API
        payload = json.dumps({"raw": raw}).encode("utf-8")

        req = urllib.request.Request(
            "https://gmail.googleapis.com/gmail/v1/users/me/messages/send",
            data=payload,
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            },
            method="POST"
        )

        with urllib.request.urlopen(req, timeout=10) as resp:
            if resp.status in (200, 201):
                logger.info("Email sent successfully to %s", to_email)
                return True
            else:
                logger.error("Gmail API returned status %s", resp.status)
                return False

    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8", errors="ignore")
        logger.error("Gmail API HTTP error %s for %s: %s", e.code, to_email, error_body)
        return False

    except Exception as e:
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
    
