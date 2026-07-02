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
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>

<body style="margin:0;padding:0;background-color:#0b1f16;font-family:'Segoe UI',Arial,sans-serif;">

<table width="100%" cellpadding="0" cellspacing="0"
style="background-color:#0b1f16;padding:40px 0;">

<tr>
<td align="center">

<table width="600"
cellpadding="0"
cellspacing="0"
style="max-width:600px;width:100%;">

<!-- Header -->

<tr>

<td
style="background:linear-gradient(135deg,#0b3d2e,#14532d,#1b5e20);
border-radius:16px 16px 0 0;
padding:40px 30px;
text-align:center;">

<div style="font-size:48px;margin-bottom:10px;">
🍱
</div>

<h1
style="
color:#ffffff;
margin:0;
font-size:28px;
font-weight:700;
letter-spacing:1px;">

Food Saver

</h1>

<p
style="
color:#b7f5c5;
margin:8px 0 0;
font-size:14px;">

Reducing Waste · Helping People

</p>

</td>

</tr>

<!-- Body -->

<tr>

<td
style="
background:#10281d;
padding:40px 40px 30px;">

<h2
style="
color:#d4af37;
font-size:22px;
margin:0 0 16px;">

Welcome aboard, {user_name}! 🎉

</h2>

<p
style="
color:#d7e8d2;
font-size:16px;
line-height:1.7;
margin:0 0 20px;">

Thank you for registering with
<strong>Food Saver</strong>.
We are truly delighted to have you as a member of our growing community.

</p>

<p
style="
color:#d7e8d2;
font-size:16px;
line-height:1.7;
margin:0 0 30px;">

Together, we can make a real difference —
reducing food waste and ensuring food reaches people who need it most.

</p>
              <!-- What you can do box -->
              <table width="100%" cellpadding="0" cellspacing="0" style="background:#163324;border-left:4px solid #4caf50;border-radius:0 8px 8px 0;margin-bottom:30px;">
                <tr>
                  <td style="padding:20px 24px;">
                    <p style="color:#7CFC98;font-weight:700;font-size:15px;margin:0 0 12px;">✨ What you can do with Food Saver:</p>
                    <p style="color:#d7e8d2;font-size:14px;margin:6px 0;">🥘 &nbsp;Donate surplus food to those in need</p>
                    <p style="color:#d7e8d2;font-size:14px;margin:6px 0;">📦 &nbsp;Track your donations in real time</p>
                    <p style="color:#d7e8d2;font-size:14px;margin:6px 0;">🤝 &nbsp;Be part of a caring community</p>
                  </td>
                </tr>
              </table>

              <!-- CTA Button -->
              <table width="100%" cellpadding="0" cellspacing="0">
                <tr>
                  <td align="center" style="padding-bottom:10px;">
                    <a href="https://food-saver-17.onrender.com"
                       style="display:inline-block;background:linear-gradient(135deg,#1b5e20,#2e7d32,#4caf50);box-shadow:0 0 18px rgba(76,175,80,.45);color:#ffffff;text-decoration:none;font-size:16px;font-weight:700;padding:14px 40px;border-radius:50px;letter-spacing:0.5px;">
                      🍱 Start Donating Now
                    </a>
                  </td>
                </tr>
              </table>
            </td>
          </tr>

          <!-- Footer -->
          <tr>
            <td style="background:#0f2418;border-radius:0 0 16px 16px;padding:24px 40px;text-align:center;border-top:1px solid #2e7d32;">
              <p style="color:#a5d6a7;font-size:13px;margin:0 0 6px;">With gratitude,</p>
              <p style="color:#7CFC98;font-weight:700;font-size:15px;margin:0;">Food Saver Team 🌱</p>
              <p style="color:#6fbf73;font-size:12px;margin:12px 0 0;">© 2026 Food Saver · Making the world a better place</p>
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
<body style="margin:0;padding:0;background-color:#0b1f16;font-family:'Segoe UI',Arial,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background-color:#0b1f16;padding:40px 0;">
    <tr>
      <td align="center">
        <table width="600" cellpadding="0" cellspacing="0" style="max-width:600px;width:100%;">

          <!-- Header -->
          <tr>
            <td style="background:linear-gradient(135deg,#0b3d2e,#14532d,#1b5e20);border-radius:16px 16px 0 0;padding:40px 30px;text-align:center;">
              <div style="font-size:48px;margin-bottom:10px;">🤝</div>
              <h1 style="color:#ffffff;margin:0;font-size:28px;font-weight:700;letter-spacing:1px;">Food Saver</h1>
              <p style="color:#b7f5c5;margin:8px 0 0;font-size:14px;">Your Kindness Made a Difference Today</p>
            </td>
          </tr>

          <!-- Success Banner -->
          <tr>
            <td style="background:#163324;padding:20px 40px;text-align:center;border-left:1px solid #2e7d32;border-right:1px solid #2e7d32;">
              <p style="margin:0;font-size:18px;color:#d4af37;font-weight:700;">✅ Donation Successfully Recorded!</p>
            </td>
          </tr>

          <!-- Body -->
          <tr>
            <td style="background:#10281d;padding:40px 40px 30px;">
              <h2 style="color:#d4af37;font-size:22px;margin:0 0 16px;">Thank you, {user_name}! 💚</h2>

              <p style="color:#d7e8d2;font-size:16px;line-height:1.7;margin:0 0 20px;">
                Your food donation has been <strong>successfully recorded</strong> in our system. Our delivery team will pick it up and ensure it reaches people in need as soon as possible.
              </p>

              <p style="color:#d7e8d2;font-size:16px;line-height:1.7;margin:0 0 30px;">
                Your generosity helps reduce food waste and brings smiles to those who need it most. Every donation counts! 🌟
              </p>

              <!-- Impact box -->
              <table width="100%" cellpadding="0" cellspacing="0" style="background:#193826;border-left:4px solid #4caf50;border-radius:0 8px 8px 0;margin-bottom:30px;">
                <tr>
                  <td style="padding:20px 24px;">
                    <p style="color:#7CFC98;font-weight:700;font-size:15px;margin:0 0 12px;">🌍 Your impact at a glance:</p>
                    <p style="color:#d7e8d2;font-size:14px;margin:6px 0;">♻️ &nbsp;Helped reduce food waste</p>
                    <p style="color:#d7e8d2;font-size:14px;margin:6px 0;">❤️ &nbsp;Supported people in need</p>
                    <p style="color:#d7e8d2;font-size:14px;margin:6px 0;">📍 &nbsp;Track your donation status anytime</p>
                  </td>
                </tr>
              </table>
              <!-- CTA Button -->
              <table width="100%" cellpadding="0" cellspacing="0">
                <tr>
                  <td align="center" style="padding-bottom:10px;">
                    <a href="https://food-saver-17.onrender.com/track_donation"
                       style="display:inline-block;background:linear-gradient(135deg,#1b5e20,#2e7d32,#4caf50);box-shadow:0 0 18px rgba(76,175,80,.45);color:#ffffff;text-decoration:none;font-size:16px;font-weight:700;padding:14px 40px;border-radius:50px;letter-spacing:0.5px;">
                      📦 Track Your Donation
                    </a>
                  </td>
                </tr>
              </table>
            </td>
          </tr>

          <!-- Footer -->
          <tr>
            <td style="background:#0f2418;border-radius:0 0 16px 16px;padding:24px 40px;text-align:center;border-top:1px solid #2e7d32;">
              <p style="color:#a5d6a7;font-size:13px;margin:0 0 6px;">With gratitude,</p>
              <p style="color:#7CFC98;font-weight:700;font-size:15px;margin:0;">Food Saver Team 🌱</p>
              <p style="color:#6fbf73;font-size:12px;margin:12px 0 0;">© 2026 Food Saver · Making the world a better place</p>
            </td>
          </tr>

        </table>
      </td>
    </tr>
  </table>
</body>
</html>"""
def _send_email(to_email, to_name, subject, html_body, text_body):
