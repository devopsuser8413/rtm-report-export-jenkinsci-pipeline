#!/usr/bin/env python3
"""
====================================================================================
📘 RTM Data Fetcher – Jira Cloud Integration (Production-Ready)
------------------------------------------------------------------------------------
This script connects to Jira Cloud via REST API and fetches Requirement Traceability
Matrix (RTM) test execution data for a specific project and execution key.

✅ Designed for CI/CD pipelines (Jenkins, GitLab, etc.)
✅ Pulls test case summaries, execution results, and metadata
✅ Outputs normalized JSON for downstream reporting

Author  : DevOpsUser8413
Version : 1.0.0
====================================================================================
"""

import os
import sys
import json
import requests
from pathlib import Path
from datetime import datetime

# ------------------------------------------------------------------------------
# 🧭 Environment Configuration (Injected by Jenkins)
# ------------------------------------------------------------------------------
JIRA_BASE   = os.getenv("JIRA_BASE")
JIRA_USER   = os.getenv("JIRA_USER")
JIRA_TOKEN  = os.getenv("JIRA_TOKEN")
PROJECT_KEY = os.getenv("RTM_PROJECT", "RTM-DEMO")
TEST_EXEC   = os.getenv("TEST_EXECUTION", "RD-4")

# ------------------------------------------------------------------------------
# 📂 Directory and File Setup
# ------------------------------------------------------------------------------
DATA_DIR = Path("data")
DATA_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_FILE = DATA_DIR / "rtm_data.json"
LOG_FILE = DATA_DIR / "fetch_rtm_log.txt"

# ------------------------------------------------------------------------------
# 🧱 Validation
# ------------------------------------------------------------------------------
if not all([JIRA_BASE, JIRA_USER, JIRA_TOKEN]):
    print("[ERROR] Missing Jira API credentials or base URL.")
    sys.exit(1)

# ------------------------------------------------------------------------------
# 📡 Jira REST API Endpoint
# ------------------------------------------------------------------------------
SEARCH_URL = f"{JIRA_BASE}/rest/api/3/search"
JQL_QUERY = f'project = "{PROJECT_KEY}" AND "Test Execution[RTM]" = "{TEST_EXEC}"'

HEADERS = {
    "Accept": "application/json",
    "Content-Type": "application/json"
}

PAYLOAD = {
    "jql": JQL_QUERY,
    "maxResults": 500,
    "fields": [
        "summary",
        "status",
        "issuetype",
        "priority",
        "assignee",
        "reporter",
        "customfield_10047",  # RTM Requirement Links
        "customfield_10048",  # RTM Test Execution Reference
    ]
}

# ------------------------------------------------------------------------------
# 🚀 Fetch Data from Jira
# ------------------------------------------------------------------------------
def fetch_rtm_data():
    print(f"[INFO] Fetching RTM data for Project '{PROJECT_KEY}' | Execution '{TEST_EXEC}'")
    print(f"[INFO] Using Jira Endpoint: {SEARCH_URL}")

    try:
        response = requests.post(
            SEARCH_URL,
            auth=(JIRA_USER, JIRA_TOKEN),
            headers=HEADERS,
            json=PAYLOAD,
            timeout=60
        )
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Network error while connecting to Jira: {e}")
        sys.exit(2)

    if response.status_code != 200:
        print(f"[ERROR] Jira API returned {response.status_code}: {response.text}")
        sys.exit(3)

    try:
        data = response.json()
    except json.JSONDecodeError as e:
        print(f"[ERROR] Invalid JSON response: {e}")
        sys.exit(4)

    return data

# ------------------------------------------------------------------------------
# 🧮 Normalize Data (optional cleanup)
# ------------------------------------------------------------------------------
def normalize_issues(data):
    issues = []
    for issue in data.get("issues", []):
        fields = issue.get("fields", {})
        issues.append({
            "key": issue.get("key"),
            "summary": fields.get("summary", ""),
            "status": fields.get("status", {}).get("name", ""),
            "type": fields.get("issuetype", {}).get("name", ""),
            "priority": fields.get("priority", {}).get("name", ""),
            "assignee": fields.get("assignee", {}).get("displayName", "Unassigned"),
            "requirement_links": fields.get("customfield_10047"),
            "execution_ref": fields.get("customfield_10048")
        })
    return {"issues": issues, "fetched_at": datetime.utcnow().isoformat()}

# ------------------------------------------------------------------------------
# 💾 Save Data to JSON File
# ------------------------------------------------------------------------------
def save_json(data):
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print(f"[SUCCESS] RTM data exported → {OUTPUT_FILE}")

# ------------------------------------------------------------------------------
# 🧾 Logging Utility
# ------------------------------------------------------------------------------
def log_summary(data):
    total = len(data.get("issues", []))
    statuses = {}
    for issue in data.get("issues", []):
        status = issue.get("status", "Unknown")
        statuses[status] = statuses.get(status, 0) + 1

    with open(LOG_FILE, "w", encoding="utf-8") as log:
        log.write(f"Jira Project: {PROJECT_KEY}\n")
        log.write(f"Execution Key: {TEST_EXEC}\n")
        log.write(f"Total Issues: {total}\n")
        log.write("Status Breakdown:\n")
        for k, v in statuses.items():
            log.write(f"  - {k}: {v}\n")

    print(f"[INFO] Log summary written → {LOG_FILE}")

# ------------------------------------------------------------------------------
# 🏁 Main Execution
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    print("══════════════════════════════════════════════════════════════")
    print("        📡 Starting Jira RTM Data Fetch Process")
    print("══════════════════════════════════════════════════════════════")

    data = fetch_rtm_data()
    normalized = normalize_issues(data)
    save_json(normalized)
    log_summary(normalized)

    print("[✅] RTM Data Fetch Completed Successfully.")
    sys.exit(0)
