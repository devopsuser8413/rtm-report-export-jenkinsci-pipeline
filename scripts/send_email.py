#!/usr/bin/env python3
"""
====================================================================================
📧 Email Notification – RTM Report Automation (Production-Ready)
------------------------------------------------------------------------------------
Sends RTM HTML & PDF reports via SMTP to stakeholders.

✅ Secure SMTP authentication (App Passwords / Jenkins credentials)
✅ MIME multipart email (HTML + PDF attachment)
✅ Includes Confluence page link
✅ Works seamlessly on Jenkins Windows/Linux agents

Author  : DevOpsUser8413
Version : 1.0.0
====================================================================================
"""

import os
import sys
import smtplib
import traceback
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from pathlib import Path
from datetime import datetime

# ------------------------------------------------------------------------------
# 🌍 Environment Variables (from Jenkins)
# ------------------------------------------------------------------------------
SMTP_HOST       = os.getenv("SMTP_HOST")
SMTP_PORT       = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER       = os.getenv("SMTP_USER")
SMTP_PASS       = os.getenv("SMTP_PASS")
REPORT_FROM     = os.getenv("REPORT_FROM", SMTP_USER)
REPORT_TO       = os.getenv("REPORT_TO")   # Comma-separated list
CONFLUENCE_LINK = os.getenv("CONFLUENCE_LINK", "https://confluence.yourorg.com/display/RTM/RTM+Test+Execution+Report")

HTML_REPORT = Path("report/rtm_report.html")
PDF_REPORT  = Path("report/rtm_report.pdf")
LOG_FILE    = Path("report/email_notification_log.txt")

# ------------------------------------------------------------------------------
# 🧩 Logging Utility
# ------------------------------------------------------------------------------
def log(message, level="INFO"):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{level}] {ts} | {message}"
    print(line)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")

# ------------------------------------------------------------------------------
# 🧾 Validation
# ------------------------------------------------------------------------------
if not all([SMTP_HOST, SMTP_USER, SMTP_PASS, REPORT_TO]):
    log("Missing SMTP configuration or recipient list.", "ERROR")
    sys.exit(1)

if not HTML_REPORT.exists() or not PDF_REPORT.exists():
    log("Missing report files. Expected rtm_report.html and rtm_report.pdf.", "ERROR")
    sys.exit(2)

recipients = [r.strip() for r in REPORT_TO.split(",") if r.strip()]
if not recipients:
    log("Recipient list is empty.", "ERROR")
    sys.exit(3)

# ------------------------------------------------------------------------------
# 📨 Compose Email
# ------------------------------------------------------------------------------
def build_email():
    log("Composing RTM report email...")

    subject = f"RTM Test Execution Report – {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    msg = MIMEMultipart("mixed")
    msg["From"] = REPORT_FROM
    msg["To"] = ", ".join(recipients)
    msg["Subject"] = subject

    # HTML Body
    html_body = f"""
    <html>
    <body style="font-family:Arial; font-size:14px; color:#333;">
        <p>Dear Team,</p>
        <p>Please find attached the latest <b>RTM Test Execution Report</b>.</p>
        <p>You can also view it on Confluence:<br>
           🔗 <a href="{CONFLUENCE_LINK}" target="_blank">{CONFLUENCE_LINK}</a></p>
        <p>Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
        <p>Regards,<br><b>DevOps CI/CD Automation</b></p>
    </body>
    </html>
    """

    msg.attach(MIMEText(html_body, "html"))

    # Attach HTML Report
    with open(HTML_REPORT, "rb") as f:
        html_part = MIMEApplication(f.read(), _subtype="html")
        html_part.add_header("Content-Disposition", "attachment", filename=HTML_REPORT.name)
        msg.attach(html_part)

    # Attach PDF Report
    with open(PDF_REPORT, "rb") as f:
        pdf_part = MIMEApplication(f.read(), _subtype="pdf")
        pdf_part.add_header("Content-Disposition", "attachment", filename=PDF_REPORT.name)
        msg.attach(pdf_part)

    log(f"Email composed successfully → Subject: {subject}")
    return msg

# ------------------------------------------------------------------------------
# 📬 Send Email
# ------------------------------------------------------------------------------
def send_email(msg):
    log(f"Connecting to SMTP server {SMTP_HOST}:{SMTP_PORT} as {SMTP_USER}...")
    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.sendmail(REPORT_FROM, recipients, msg.as_string())
        log("✅ Email sent successfully to recipients.")
    except Exception as e:
        log(f"❌ Email sending failed: {e}", "ERROR")
        traceback.print_exc()
        sys.exit(4)

# ------------------------------------------------------------------------------
# 🏁 Main
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    print("══════════════════════════════════════════════════════════════")
    print("        📧 Starting RTM Email Notification Process")
    print("══════════════════════════════════════════════════════════════")

    try:
        msg = build_email()
        send_email(msg)
        log("Email notification process completed successfully.")
        sys.exit(0)
    except Exception as e:
        log(f"Unexpected error: {e}", "ERROR")
        traceback.print_exc()
        sys.exit(99)
