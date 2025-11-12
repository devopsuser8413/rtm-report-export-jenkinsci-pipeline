#!/usr/bin/env python3
"""
====================================================================================
📘 Confluence Publisher – RTM Report Automation (Production-Ready)
------------------------------------------------------------------------------------
Uploads the generated RTM HTML & PDF reports to a Confluence Cloud page.

✅ Creates page if missing
✅ Updates page content on version bump
✅ Attaches latest HTML/PDF report files
✅ Compatible with Jenkins or standalone runs

Author  : DevOpsUser8413
Version : 1.0.0
====================================================================================
"""

import os
import sys
import json
import time
import base64
import requests
from pathlib import Path
from datetime import datetime

# ------------------------------------------------------------------------------
# 🌍 Environment Variables (Injected by Jenkins)
# ------------------------------------------------------------------------------
CONFLUENCE_BASE   = os.getenv("CONFLUENCE_BASE")
CONFLUENCE_USER   = os.getenv("CONFLUENCE_USER")
CONFLUENCE_TOKEN  = os.getenv("CONFLUENCE_TOKEN")
CONFLUENCE_SPACE  = os.getenv("CONFLUENCE_SPACE", "DEMO")
CONFLUENCE_TITLE  = os.getenv("CONFLUENCE_TITLE", "RTM Test Execution Report")

HTML_FILE = Path("report/rtm_report.html")
PDF_FILE  = Path("report/rtm_report.pdf")
LOG_FILE  = Path("report/confluence_publish_log.txt")

# ------------------------------------------------------------------------------
# 🧩 Logging Utility
# ------------------------------------------------------------------------------
def log(message, level="INFO"):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted = f"[{level}] {timestamp} | {message}"
    print(formatted)
    with open(LOG_FILE, "a", encoding="utf-8") as logf:
        logf.write(formatted + "\n")

# ------------------------------------------------------------------------------
# 🧱 Validation
# ------------------------------------------------------------------------------
if not all([CONFLUENCE_BASE, CONFLUENCE_USER, CONFLUENCE_TOKEN]):
    log("Missing Confluence credentials or base URL.", "ERROR")
    sys.exit(1)

if not HTML_FILE.exists() or not PDF_FILE.exists():
    log("Missing report files. Expected rtm_report.html and rtm_report.pdf.", "ERROR")
    sys.exit(2)

# ------------------------------------------------------------------------------
# 🔐 Authentication Setup
# ------------------------------------------------------------------------------
auth = (CONFLUENCE_USER, CONFLUENCE_TOKEN)
headers = {"Content-Type": "application/json"}

# ------------------------------------------------------------------------------
# 🔍 Find Existing Page
# ------------------------------------------------------------------------------
def find_page():
    search_url = f"{CONFLUENCE_BASE}/rest/api/content"
    params = {"title": CONFLUENCE_TITLE, "spaceKey": CONFLUENCE_SPACE, "expand": "version"}
    response = requests.get(search_url, auth=auth, params=params)

    if response.status_code != 200:
        log(f"Failed to query Confluence page: {response.status_code} {response.text}", "ERROR")
        sys.exit(3)

    results = response.json().get("results", [])
    if results:
        return results[0]
    return None

# ------------------------------------------------------------------------------
# 📝 Create or Update Page
# ------------------------------------------------------------------------------
def create_or_update_page(page):
    with open(HTML_FILE, "r", encoding="utf-8") as f:
        html_content = f.read()

    payload = {
        "type": "page",
        "title": CONFLUENCE_TITLE,
        "space": {"key": CONFLUENCE_SPACE},
        "body": {"storage": {"value": html_content, "representation": "storage"}},
    }

    if not page:
        # Create new page
        log(f"Creating new Confluence page '{CONFLUENCE_TITLE}' in space '{CONFLUENCE_SPACE}'...")
        response = requests.post(f"{CONFLUENCE_BASE}/rest/api/content", auth=auth, headers=headers, json=payload)
        if response.status_code != 200 and response.status_code != 201:
            log(f"Failed to create Confluence page: {response.status_code} {response.text}", "ERROR")
            sys.exit(4)
        return response.json()
    else:
        # Update existing page version
        page_id = page["id"]
        current_ver = page["version"]["number"]
        payload["version"] = {"number": current_ver + 1}
        log(f"Updating existing Confluence page '{CONFLUENCE_TITLE}' (version {current_ver + 1})...")
        response = requests.put(f"{CONFLUENCE_BASE}/rest/api/content/{page_id}", auth=auth, headers=headers, json=payload)
        if response.status_code not in [200, 201]:
            log(f"Failed to update Confluence page: {response.status_code} {response.text}", "ERROR")
            sys.exit(5)
        return response.json()

# ------------------------------------------------------------------------------
# 📎 Upload Attachments
# ------------------------------------------------------------------------------
def upload_attachment(page_id, file_path):
    upload_url = f"{CONFLUENCE_BASE}/rest/api/content/{page_id}/child/attachment"
    file_name = file_path.name
    log(f"Attaching file: {file_name}")

    files = {
        "file": (file_name, open(file_path, "rb"), "application/octet-stream"),
    }
    headers = {"X-Atlassian-Token": "no-check"}

    # Check if file exists already → update instead of duplicate
    existing_files = requests.get(upload_url, auth=auth).json()
    existing_names = [a["title"] for a in existing_files.get("results", [])]
    if file_name in existing_names:
        log(f"File '{file_name}' already exists → updating attachment...")
        attach_id = next((a["id"] for a in existing_files["results"] if a["title"] == file_name), None)
        if attach_id:
            update_url = f"{upload_url}/{attach_id}/data"
            response = requests.post(update_url, auth=auth, headers=headers, files=files)
        else:
            response = requests.post(upload_url, auth=auth, headers=headers, files=files)
    else:
        response = requests.post(upload_url, auth=auth, headers=headers, files=files)

    if response.status_code not in [200, 201]:
        log(f"Attachment upload failed ({file_name}): {response.status_code} {response.text}", "ERROR")
        sys.exit(6)
    log(f"Attachment uploaded successfully → {file_name}")

# ------------------------------------------------------------------------------
# 🏁 Main
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    print("══════════════════════════════════════════════════════════════")
    print("        🌐 Starting Confluence Publishing Process")
    print("══════════════════════════════════════════════════════════════")

    try:
        page = find_page()
        page_data = create_or_update_page(page)
        page_id = page_data["id"]

        upload_attachment(page_id, HTML_FILE)
        upload_attachment(page_id, PDF_FILE)

        log("✅ Confluence publishing completed successfully.")
        print(f"[SUCCESS] RTM Report published to Confluence page ID: {page_id}")
        sys.exit(0)

    except Exception as e:
        log(f"Unexpected failure: {e}", "ERROR")
        sys.exit(99)
