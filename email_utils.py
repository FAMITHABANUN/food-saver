"""
email_utils.py
----------------
Standalone email-sending helper for Food Saver.
Uses Brevo API over HTTPS with beautiful HTML email templates.
"""

import os
import json
import logging
import urllib.request
import urllib.error

logger = logging.getLogger("email_utils")

BREVO_API_URL = "https://api.brevo.com/v3/smtp/email"


def _get_registration_html(user_name):
    return f"""<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"></head>
<body style="margin:0;padding:0;background-color:#f4f6f9;font-family:'Segoe UI',Arial,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background-color:#f4f6f9;padding:40px 0;">
    <tr>
      <td align="center">
        <table width="600" cellpadding="0" cellspacing="0" style="max-width:600px;width:100%;">

          <!-- Header -->
          <tr>
            <td style="background:linear-gradient(135deg,#2e7d32,#66bb6a);border-radius:16px 16px 0 0;padding:40px 30px;text-align:center;">
              <div style="font-size:48px;margin-bottom:10px;">🍱</div>
              <h1 style="color:#ffffff;margin:0;font-size:28px;font-weight:700;letter-spacing:1px;">Food Saver</h1>
              <p style="color:#c8e6c9;margin:8px 0 0;font-size:14px;">Reducing Waste · Helping People</p>
            </td>
          </tr>

          <!-- Body -->
          <tr>
            <td style="background:#ffffff;padding:40px 40px 30px;">
              <h2 style="color:#2e7d32;font-size:22px;margin:0 0 16px;">Welcome aboard, {user_name}! 🎉</h2>
              <p style="color:#555;font-size:16px;line-height:1.7;margin:0 0 20px;">
                Thank you for registering with <strong>Food Saver</strong>. We are truly delighted to have you as a member of our growing community.
              </p>
              <p style="color:#555;font-size:16px;line-height:1.7;margin:0 0 30px;">
                Together, we can make a real difference — reducing food waste and ensuring food reaches people who need it most.
              </p>

              <!-- What you can do box -->
              <table width="100%" cellpadding="0" cellspacing="0" style="background:#f1f8e9;border-left:4px solid #66bb6a;border-radius:0 8px 8px 0;margin-bottom:30px;">
                <tr>
                  <td style="padding:20px 24px;">
                    <p style="color:#2e7d32;font-weight:700;font-size:15px;margin:0 0 12px;">✨ What you can do with Food Saver:</p>
                    <p style="color:#555;font-size:14px;margin:6px 0;">🥘 &nbsp;Donate surplus food to those in need</p>
                    <p style="color:#555;font-size:14px;margin:6px 0;">📦 &nbsp;Track your donations in real time</p>
                    <p style="color:#555;font-size:14px;margin:6px 0;">🤝 &nbsp;Be part of a caring community</p>
                  </td>
                </tr>
              </table>

              <!-- CTA Button -->
              <table width="100%" cellpadding="0" cellspacing="0">
                <tr>
                  <td align="center" style="padding-bottom:10px;">
                    <a href="https://food-saver-17.onrender.com" 
                       style="display:inline-block;background:linear-gradient(135deg,#2e7d32,#66bb6a);color:#ffffff;text-decoration:none;font-size:16px;font-weight:700;padding:14px 40px;border-radius:50px;letter-spacing:0.5px;">
                      🍱 Start Donating Now
                    </a>
                  </td>
                </tr>
              </table>
            </td>
          </tr>

          <!-- Footer -->
          <tr>
            <td style="background:#f9fbe7;border-radius:0 0 16px 16px;padding:24px 40px;text-align:center;border-top:1px solid #e8f5e9;">
              <p style="color:#888;font-size:13px;margin:0 0 6px;">With gratitude,</p>
              <p style="color:#2e7d32;font-weight:700;font-size:15px;margin:0;">Food Saver Team 🌱</p>
              <p style="color:#bbb;font-size:12px;margin:12px 0 0;">© 2026 Food Saver · Making the world a better place</p>
            </td>
          </tr>

        </table>
      </td>
    </tr>
  </table>
</body>
</html>"""


def _get_donation_html(user_name):
    return f"""<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"></head>
<body style="margin:0;padding:0;background-color:#f4f6f9;font-family:'Segoe UI',Arial,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background-color:#f4f6f9;padding:40px 0;">
    <tr>
      <td align="center">
        <table width="600" cellpadding="0" cellspacing="0" style="max-width:600px;width:100%;">

          <!-- Header -->
          <tr>
            <td style="background:linear-gradient(135deg,#1565c0,#42a5f5);border-radius:16px 16px 0 0;padding:40px 30px;text-align:center;">
              <div style="font-size:48px;margin-bottom:10px;">🤝</div>
              <h1 style="color:#ffffff;margin:0;font-size:28px;font-weight:700;letter-spacing:1px;">Food Saver</h1>
              <p style="color:#bbdefb;margin:8px 0 0;font-size:14px;">Your Kindness Made a Difference Today</p>
            </td>
          </tr>

          <!-- Success Banner -->
          <tr>
            <td style="background:#e3f2fd;padding:20px 40px;text-align:center;border-left:1px solid #90caf9;border-right:1px solid #90caf9;">
              <p style="margin:0;font-size:18px;color:#1565c0;font-weight:700;">✅ Donation Successfully Recorded!</p>
            </td>
          </tr>

          <!-- Body -->
          <tr>
            <td style="background:#ffffff;padding:40px 40px 30px;">
              <h2 style="color:#1565c0;font-size:22px;margin:0 0 16px;">Thank you, {user_name}! 💙</h2>
              <p style="color:#555;font-size:16px;line-height:1.7;margin:0 0 20px;">
                Your food donation has been <strong>successfully recorded</strong> in our system. Our delivery team will pick it up and ensure it reaches people in need as soon as possible.
              </p>
              <p style="color:#555;font-size:16px;line-height:1.7;margin:0 0 30px;">
                Your generosity helps reduce food waste and brings smiles to those who need it most. Every donation counts! 🌟
              </p>

              <!-- Impact box -->
              <table width="100%" cellpadding="0" cellspacing="0" style="background:#e8f4fd;border-left:4px solid #42a5f5;border-radius:0 8px 8px 0;margin-bottom:30px;">
                <tr>
                  <td style="padding:20px 24px;">
                    <p style="color:#1565c0;font-weight:700;font-size:15px;margin:0 0 12px;">🌍 Your impact at a glance:</p>
                    <p style="color:#555;font-size:14px;margin:6px 0;">♻️ &nbsp;Helped reduce food waste</p>
                    <p style="color:#555;font-size:14px;margin:6px 0;">❤️ &nbsp;Supported people in need</p>
                    <p style="color:#555;font-size:14px;margin:6px 0;">📍 &nbsp;Track your donation status anytime</p>
                  </td>
                </tr>
              </table>

              <!-- CTA Button -->
              <table width="100%" cellpadding="0" cellspacing="0">
                <tr>
                  <td align="center" style="padding-bottom:10px;">
                    <a href="https://food-saver-17.onrender.com/track_donation" 
                       style="display:inline-block;background:linear-gradient(135deg,#1565c0,#42a5f5);color:#ffffff;text-decoration:none;font-size:16px;font-weight:700;padding:14px 40px;border-radius:50px;letter-spacing:0.5px;">
                      📦 Track Your Donation
                    </a>
                  </td>
                </tr>
              </table>
            </td>
          </tr>

          <!-- Footer -->
          <tr>
            <td style="background:#e3f2fd;border-radius:0 0 16px 16px;padding:24px 40px;text-align:center;border-top:1px solid #90caf9;">
              <p style="color:#888;font-size:13px;margin:0 0 6px;">With gratitude,</p>
              <p style="color:#1565c0;font-weight:700;font-size:15px;margin:0;">Food Saver Team 🌱</p>
              <p style="color:#bbb;font-size:12px;margin:12px 0 0;">© 2026 Food Saver · Making the world a better place</p>
            </td>
          </tr>

        </table>
      </td>
    </tr>
  </table>
</body>
</html>"""


def _send_email(to_email, to_name, subject, html_body, text_body):
    """
    Internal helper: sends HTML email via Brevo HTTPS API.
    Returns True on success, False on any failure (never raises).
    """
    api_key   = os.environ.get("BREVO_API_KEY")
    mail_from = os.environ.get("MAIL_FROM", "famibanu786@gmail.com")

    if not api_key or not to_email:
        logger.warning("Email not sent: missing BREVO_API_KEY or recipient.")
        return False

    try:
        payload = json.dumps({
            "sender": {"name": "Food Saver", "email": mail_from},
            "to": [{"email": to_email, "name": to_name}],
            "subject": subject,
            "htmlContent": html_body,
            "textContent": text_body
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
    subject   = "Welcome to Food Saver! 🍱"
    html_body = _get_registration_html(user_name)
    text_body = f"""Hello {user_name},

Thank you for registering with Food Saver.

We are delighted to have you as a member of our community.

Together, we can reduce food waste and help people in need.

Thank you for joining us!

Regards,
Food Saver Team
"""
    return _send_email(user_email, user_name, subject, html_body, text_body)


def send_donation_email(user_email, user_name):
    """Sends the 'Food Donation Successful' email after a successful donation."""
    subject   = "Food Donation Successful ✅"
    html_body = _get_donation_html(user_name)
    text_body = f"""Hello {user_name},

Thank you for donating food through Food Saver.

Your donation has been successfully recorded.

Your kindness helps reduce food waste and supports people in need.

Thank you for making a difference.

Regards,
Food Saver Team
"""
    return _send_email(user_email, user_name, subject, html_body, text_body)
