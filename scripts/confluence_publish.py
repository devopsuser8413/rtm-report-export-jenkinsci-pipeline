#!/usr/bin/env python3
# ======================================================================
# 📘 Confluence Publisher Utility
# ----------------------------------------------------------------------
# Automates publishing RTM Test Execution reports (PDF/HTML) to a
# Confluence page via REST API.
#
# Supports:
#   • Create page if missing
#   • Update existing page body
#   • Upload/replace attachments (PDF/HTML reports)
#
# Usage Example (in Jenkins):
#   python scripts/confluence_publish.py \
#       --space DEV \
#       --title "RTM Test Execution Report – RTM-DEMO/RD-4" \
#       --body "<p>Automated RTM report body</p>" \
#       --attach "report/rtm_report_RTM-DEMO_RD-4.pdf"
#
# ----------------------------------------------------------------------
# Required Environment Variables (set via Jenkins credentials):
#   CONFLUENCE_BASE   = "https://yourcompany.atlassian.net/wiki"
#   CONFLUENCE_USER   = "<user@domain.com>"
#   CONFLUENCE_TOKEN  = "<api-token>"
# ======================================================================

import os
import sys
import json
import time
import argparse
import requests
from pathlib import Path

# ----------------------------------------------------------------------
# 🔧 Helper Functions
# ----------------------------------------------------------------------
def log(msg: str):
    """Print formatted info message"""
    print(f"[INFO] {msg}", flush=True)

def error(msg: str, code: int = 1):
    """Print error and exit"""
    print(f"[ERROR] {msg}", file=sys.stderr, flush=True)
    sys.exit(code)

def get_env(name: str, required=True, default=None):
    """Read environment variable safely"""
    val = os.getenv(name, default)
    if required and not val:
        error(f"Missing required environment variable: {name}")
    return val

# ----------------------------------------------------------------------
# 🔐 Authentication
# ----------------------------------------------------------------------
def get_auth_session():
    """Return an authenticated session for Confluence REST API"""
    base = get_env("CONFLUENCE_BASE")
    user = get_env("CONFLUENCE_USER")
    token = get_env("CONFLUENCE_TOKEN")

    sess = requests.Session()
    sess.auth = (user, token)
    sess.headers.update({
        "Accept": "application/json",
        "Content-Type": "application/json"
    })
    return base.rstrip("/"), sess

# ----------------------------------------------------------------------
# 📄 Page Operations
# ----------------------------------------------------------------------
def find_page(base, sess, space, title):
    """Search for an existing Confluence page"""
    url = f"{base}/rest/api/content"
    params = {"spaceKey": space, "title": title, "expand": "version"}
    r = sess.get(url, params=params)
    if not r.ok:
        error(f"Failed to search page: {r.status_code} {r.text[:200]}")
    data = r.json()
    results = data.get("results", [])
    return results[0] if results else None

def create_page(base, sess, space, title, body):
    """Create a new Confluence page"""
    url = f"{base}/rest/api/content/"
    payload = {
        "type": "page",
        "title": title,
        "space": {"key": space},
        "body": {
            "storage": {"value": body, "representation": "storage"}
        }
    }
    r = sess.post(url, data=json.dumps(payload))
    if not r.ok:
        error(f"Failed to create page: {r.status_code} {r.text[:200]}")
    return r.json()

def update_page(base, sess, page, body):
    """Update an existing Confluence page"""
    page_id = page["id"]
    version = page["version"]["number"] + 1
    url = f"{base}/rest/api/content/{page_id}"

    payload = {
        "id": page_id,
        "type": "page",
        "title": page["title"],
        "version": {"number": version},
        "body": {
            "storage": {"value": body, "representation": "storage"}
        }
    }

    r = sess.put(url, data=json.dumps(payload))
    if not r.ok:
        error(f"Failed to update page: {r.status_code} {r.text[:200]}")
    return r.json()

# ----------------------------------------------------------------------
# 📎 Attachment Handling
# ----------------------------------------------------------------------
def upload_attachment(base, sess, page_id, filepath):
    """Upload or update attachment to Confluence page"""
    path = Path(filepath)
    if not path.exists():
        error(f"Attachment not found: {filepath}")

    # Delete any existing attachment with the same name
    del_url = f"{base}/rest/api/content/{page_id}/child/attachment"
    r = sess.get(del_url, params={"filename": path.name})
    if r.ok and r.json().get("results"):
        attach_id = r.json()["results"][0]["id"]
        del_resp = sess.delete(f"{base}/rest/api/content/{attach_id}")
        if not del_resp.ok:
            log(f"Warning: could not delete old attachment {path.name}")

    # Upload new attachment
    upload_url = f"{base}/rest/api/content/{page_id}/child/attachment"
    files = {"file": (path.name, open(path, "rb"), "application/octet-stream")}
    headers = {"X-Atlassian-Token": "no-check"}
    r = sess.post(upload_url, headers=headers, files=files)
    if not r.ok:
        error(f"Failed to upload attachment: {r.status_code} {r.text[:200]}")
    log(f"📎 Uploaded attachment: {path.name}")
    return r.json()

# ----------------------------------------------------------------------
# 🚀 Main
# ----------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="Publish report to Confluence")
    parser.add_argument("--space", required=True, help="Confluence space key")
    parser.add_argument("--title", required=True, help="Page title")
    parser.add_argument("--body", required=True, help="HTML body content")
    parser.add_argument("--attach", help="Path to attachment file (PDF/HTML)")
    args = parser.parse_args()

    base, sess = get_auth_session()

    log(f"Connecting to Confluence: {base}")
    page = find_page(base, sess, args.space, args.title)

    if page:
        log(f"Updating existing page: {args.title}")
        page = update_page(base, sess, page, args.body)
    else:
        log(f"Creating new page: {args.title}")
        page = create_page(base, sess, args.space, args.title, args.body)

    page_id = page["id"]
    page_url = f"{base}/pages/{page_id}"
    log(f"✅ Page ready: {page_url}")

    # Upload attachment if specified
    if args.attach:
        upload_attachment(base, sess, page_id, args.attach)

    log("🎉 Confluence publish completed successfully.")
    print(f"PAGE_URL={page_url}")

if __name__ == "__main__":
    main()
