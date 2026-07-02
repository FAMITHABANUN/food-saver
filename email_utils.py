"""
email_utils.py
----------------
Standalone email-sending helper for Food Saver.
Uses Brevo (formerly Sendinblue) API over HTTPS.
Works perfectly on Render's free plan - no SMTP blocking issues.

Required environment variable (set on Render → Environment tab):
    BREVO_API_KEY   your Brevo API key (starts with xkeysib-)
    MAIL_FROM       sender email (must match your Brevo account email)

If sending fails for any reason, this module logs the error and
returns False - it NEVER raises, so it can never break registration
or donation flows.
"""

import os
import json
import logging
import urllib.request
import urllib.error

logger = logging.getLogger("email_utils")

BREVO_API_URL = "https://api.brevo.com/v3/smtp/email"


def _send_email(to_email, to_name, subject, body):
    """
    Internal helper: sends email via Brevo HTTPS API.
    Returns True on success, False on any failure (never raises).
    """
    api_key  = os.environ.get("BREVO_API_KEY")
    mail_from = os.environ.get("MAIL_FROM", "famibanu786@gmail.com")

    if not api_key or not to_email:
        logger.warning("Email not sent: missing BREVO_API_KEY or recipient.")
        return False

    try:
        payload = json.dumps({
            "sender": {
                "name": "Food Saver",
                "email": mail_from
            },
            "to": [{"email": to_email, "name": to_name}],
            "subject": subject,
            "textContent": body
        }).encode("utf-8")

        req = urllib.request.Request(
            BREVO_API_URL,
            data=payload,
            headers={
                "api-key": api_key,
                "Content-Type": "application/json",
                "Accept": "application/json"
            },
            method="POST"
        )

        with urllib.request.urlopen(req, timeout=10) as resp:
            if resp.status in (200, 201):
                logger.info("Email sent successfully to %s", to_email)
                return True
            else:
                logger.error("Brevo API returned status %s", resp.status)
                return False

    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8", errors="ignore")
        logger.error("Brevo API error %s for %s: %s", e.code, to_email, error_body)
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
    return _send_email(user_email, user_name, subject, body)


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
    return _send_email(user_email, user_name, subject, body)
    
