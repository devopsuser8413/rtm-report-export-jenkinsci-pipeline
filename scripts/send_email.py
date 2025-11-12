#!/usr/bin/env python3
# ======================================================================
# 📧 Email Notification Utility
# ----------------------------------------------------------------------
# Sends email notifications with optional attachments using SMTP.
# Designed for Jenkins pipelines to send automated test or RTM reports.
#
# Supports:
#   ✅ Multiple recipients
#   ✅ HTML or plain text bodies
#   ✅ File attachments (PDF, HTML, ZIP)
#   ✅ Secure SMTP (TLS/STARTTLS)
#
# ----------------------------------------------------------------------
# Required Environment Variables (set via Jenkins credentials):
#   SMTP_HOST   = "smtp.office365.com"
#   SMTP_PORT   = "587"
#   SMTP_USER   = "jenkins@company.com"
#   SMTP_PASS   = "<app-password>"
#   REPORT_FROM = "jenkins@company.com"
# ======================================================================

import os
import sys
import smtplib
import mimetypes
from email.message import EmailMessage
from pathlib import Path
import argparse

# ----------------------------------------------------------------------
# 🔧 Helper Functions
# ----------------------------------------------------------------------
def log(msg: str):
    """Log message to stdout (Jenkins friendly)."""
    print(f"[INFO] {msg}", flush=True)

def error(msg: str, code: int = 1):
    """Print error and exit."""
    print(f"[ERROR] {msg}", file=sys.stderr, flush=True)
    sys.exit(code)

def get_env(name: str, required=True, default=None):
    """Fetch environment variable safely."""
    val = os.getenv(name, default)
    if required and not val:
        error(f"Missing required environment variable: {name}")
    return val

# ----------------------------------------------------------------------
# ✉️ Email Builder
# ----------------------------------------------------------------------
def build_email(subject, body_path, sender, recipients, attachment_path=None):
    """Construct email with optional attachment."""
    msg = EmailMessage()
    msg["From"] = sender
    msg["To"] = recipients
    msg["Subject"] = subject

    # Read body file
    body_file = Path(body_path)
    if not body_file.exists():
        error(f"Email body file not found: {body_path}")
    with open(body_file, "r", encoding="utf-8") as f:
        body_content = f.read()

    # Determine if HTML or plain text
    subtype = "html" if "<html" in body_content.lower() or "<p>" in body_content.lower() else "plain"
    msg.set_content(body_content, subtype=subtype)

    # Add attachment (optional)
    if attachment_path:
        attach_file = Path(attachment_path)
        if not attach_file.exists():
            error(f"Attachment file not found: {attachment_path}")

        mime_type, _ = mimetypes.guess_type(attach_file)
        maintype, subtype = (mime_type or "application/octet-stream").split("/", 1)
        with open(attach_file, "rb") as f:
            msg.add_attachment(f.read(), maintype=maintype, subtype=subtype, filename=attach_file.name)
        log(f"📎 Attached file: {attach_file.name}")

    return msg

# ----------------------------------------------------------------------
# 🚀 SMTP Send
# ----------------------------------------------------------------------
def send_email(message, smtp_host, smtp_port, smtp_user, smtp_pass):
    """Send the email via SMTP (STARTTLS)."""
    try:
        with smtplib.SMTP(smtp_host, int(smtp_port)) as server:
            server.ehlo()
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.send_message(message)
            log("✅ Email sent successfully.")
    except Exception as e:
        error(f"Failed to send email: {e}")

# ----------------------------------------------------------------------
# 🧠 Main
# ----------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="Send email with optional attachment.")
    parser.add_argument("--subject", required=True, help="Email subject line")
    parser.add_argument("--body", required=True, help="Path to email body text file (HTML or plain text)")
    parser.add_argument("--to", required=True, help="Comma or semicolon separated recipient list")
    parser.add_argument("--attach", help="Optional attachment file path")
    args = parser.parse_args()

    # Load SMTP configuration
    smtp_host = get_env("SMTP_HOST")
    smtp_port = get_env("SMTP_PORT", default="587")
    smtp_user = get_env("SMTP_USER")
    smtp_pass = get_env("SMTP_PASS")
    sender = get_env("REPORT_FROM")

    # Process recipients
    recipients = [addr.strip() for addr in args.to.replace(";", ",").split(",") if addr.strip()]
    if not recipients:
        error("No recipients specified in --to argument.")
    recipients_str = ", ".join(recipients)

    log(f"Preparing email: {args.subject}")
    log(f"From: {sender}")
    log(f"To: {recipients_str}")

    # Build and send email
    msg = build_email(args.subject, args.body, sender, recipients_str, args.attach)
    send_email(msg, smtp_host, smtp_port, smtp_user, smtp_pass)

# ----------------------------------------------------------------------
if __name__ == "__main__":
    main()
