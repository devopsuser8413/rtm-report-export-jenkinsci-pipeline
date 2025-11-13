#!/usr/bin/env python3
# ==========================================================
# 📘 fetch_rtm_data.py
# Purpose: Fetch RTM Test Execution data from Jira (Deviniti RTM API)
# Author: devopsuser8413
# Updated: 2025-11-13
# ==========================================================

import os
import sys
import json
import requests
from datetime import datetime

# ----------------------------------------------------------
# 🔧 Load Environment Variables
# ----------------------------------------------------------
JIRA_BASE        = os.getenv("JIRA_BASE")
JIRA_USER        = os.getenv("JIRA_USER")
JIRA_TOKEN       = os.getenv("JIRA_TOKEN")
PROJECT_KEY      = os.getenv("JIRA_PROJECT_KEY")
EXECUTION_KEY    = os.getenv("JIRA_EXECUTION_ID")
OUTPUT_FILE      = "data/rtm_data.json"

# ----------------------------------------------------------
# Validate
# ----------------------------------------------------------
missing = [v for v in ["JIRA_BASE", "JIRA_USER", "JIRA_TOKEN"] if not os.getenv(v)]
if missing:
    print(f"[ERROR] Missing environment variables: {missing}")
    sys.exit(1)

# ----------------------------------------------------------
# 🌐 RTM for Jira API endpoint (Deviniti)
# ----------------------------------------------------------
RTM_ENDPOINT = f"{JIRA_BASE}/rest/atm/1.0/testexecutions/{EXECUTION_KEY}/testRuns"

HEADERS = {
    "Accept": "application/json"
}

# ----------------------------------------------------------
# 🚀 Fetch RTM Test Execution Test Runs
# ----------------------------------------------------------
print("="*80)
print("🗂️  Fetching RTM Test Execution results (Deviniti RTM API)")
print("="*80)
print(f"[INFO] Test Execution: {EXECUTION_KEY}")
print(f"[INFO] Endpoint: {RTM_ENDPOINT}")

try:
    response = requests.get(
        RTM_ENDPOINT,
        headers=HEADERS,
        auth=(JIRA_USER, JIRA_TOKEN)
    )

    if response.status_code != 200:
        print(f"[ERROR] API Error {response.status_code}: {response.text}")
        sys.exit(2)

    testRuns = response.json()

    print(f"[SUCCESS] Retrieved {len(testRuns)} test run(s).")

    # Save JSON
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump({"testRuns": testRuns}, f, indent=4)

    print(f"[INFO] Data saved → {OUTPUT_FILE}")
    sys.exit(0)

except Exception as e:
    print(f"[EXCEPTION] {e}")
    sys.exit(3)
