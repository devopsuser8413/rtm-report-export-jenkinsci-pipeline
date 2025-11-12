#!/usr/bin/env python3
# ==========================================================
# 📘 fetch_rtm_data.py
# Purpose: Fetch RTM Test Execution data from Jira using REST API (new /search/jql endpoint)
# Author: devopsuser8413
# Updated: 2025-11-12
# ==========================================================

import os
import sys
import json
import requests
from datetime import datetime

# ----------------------------------------------------------
# 🔧 Load Environment Variables from Jenkins Pipeline
# ----------------------------------------------------------
JIRA_BASE   = os.getenv("JIRA_BASE")
JIRA_USER   = os.getenv("JIRA_USER")
JIRA_TOKEN  = os.getenv("JIRA_TOKEN")
PROJECT_KEY = os.getenv("JIRA_PROJECT_KEY", "RTM-DEMO")
EXECUTION_ID = os.getenv("JIRA_EXECUTION_ID", "RD-4")
OUTPUT_FILE = "data/rtm_data.json"

# ----------------------------------------------------------
# 🧭 Validate Environment
# ----------------------------------------------------------
missing = [var for var in ["JIRA_BASE", "JIRA_USER", "JIRA_TOKEN"] if not os.getenv(var)]
if missing:
    print(f"[ERROR] Missing required environment variable(s): {', '.join(missing)}")
    sys.exit(3)

# ----------------------------------------------------------
# 🌐 Jira API Configuration (New Endpoint)
# ----------------------------------------------------------
API_ENDPOINT = f"{JIRA_BASE}/rest/api/3/search/jql"
HEADERS = {
    "Accept": "application/json",
    "Content-Type": "application/json"
}

# ----------------------------------------------------------
# 🔍 Build JQL Query
# ----------------------------------------------------------
# Example: Fetch all Test Cases or Executions linked to a given execution ID
JQL_QUERY = f'project = "{PROJECT_KEY}" AND issuekey = "{EXECUTION_ID}"'

payload = {"jql": JQL_QUERY}

# ----------------------------------------------------------
# 🚀 Fetch Data from Jira API
# ----------------------------------------------------------
print("=" * 80)
print("🗂️  Starting Jira RTM Data Fetch Process")
print("=" * 80)
print(f"[INFO] Fetching RTM data for Project '{PROJECT_KEY}' | Execution '{EXECUTION_ID}'")
print(f"[INFO] Using Jira Endpoint: {API_ENDPOINT}")

try:
    response = requests.post(
        API_ENDPOINT,
        headers=HEADERS,
        auth=(JIRA_USER, JIRA_TOKEN),
        json=payload
    )

    if response.status_code == 200:
        data = response.json()
        issue_count = len(data.get("issues", []))
        print(f"[SUCCESS] Retrieved {issue_count} issue(s) from Jira.")
        print(f"[INFO] Writing RTM data to {OUTPUT_FILE}")

        os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

        print(f"[INFO] Data saved successfully at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        sys.exit(0)

    else:
        print(f"[ERROR] Jira API returned {response.status_code}: {response.text}")
        print("[ACTION] Please verify your Jira Cloud API URL and credentials, "
              "or check Atlassian’s migration guide for the /search/jql API.")
        sys.exit(3)

except requests.exceptions.RequestException as e:
    print(f"[EXCEPTION] Network or connection error: {e}")
    sys.exit(3)
