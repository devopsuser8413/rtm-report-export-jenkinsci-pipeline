#!/usr/bin/env python3

import os
import sys
import json
import requests
from datetime import datetime

JIRA_BASE = os.getenv("JIRA_BASE")
JIRA_USER = os.getenv("JIRA_USER")
JIRA_TOKEN = os.getenv("JIRA_TOKEN")
EXECUTION_ID = os.getenv("JIRA_EXECUTION_ID")  # Example: RD-4

OUTPUT_FILE = "data/rtm_data.json"

if not all([JIRA_BASE, JIRA_USER, JIRA_TOKEN, EXECUTION_ID]):
    print("Missing required environment variables.")
    sys.exit(1)

headers = {
    "Accept": "application/json"
}

# ------------------------------------------------------------------
# STEP 1 — Fetch Test Execution
# ------------------------------------------------------------------
exec_url = f"{JIRA_BASE}/api/v2/test-execution/{EXECUTION_ID}"

print(f"[INFO] Fetching Test Execution: {exec_url}")

resp = requests.get(exec_url, auth=(JIRA_USER, JIRA_TOKEN), headers=headers)
if resp.status_code != 200:
    print(f"[ERROR] Could not fetch Test Execution. {resp.status_code}: {resp.text}")
    sys.exit(2)

execution = resp.json()

# ------------------------------------------------------------------
# STEP 2 — Fetch Test Case Executions inside this Test Execution
# ------------------------------------------------------------------
tces_url = f"{JIRA_BASE}/api/v2/test-execution/{EXECUTION_ID}/tces"

print(f"[INFO] Fetching Test Case Executions: {tces_url}")

resp_tces = requests.get(tces_url, auth=(JIRA_USER, JIRA_TOKEN), headers=headers)
if resp_tces.status_code != 200:
    print(f"[ERROR] Could not fetch Test Case Executions. {resp_tces.status_code}: {resp_tces.text}")
    sys.exit(3)

tces = resp_tces.json()

# ------------------------------------------------------------------
# STEP 3 — Normalize Dataset for the Report Generator
# ------------------------------------------------------------------
issues = []

for tce in tces.get("values", []):
    issues.append({
        "key": tce.get("key"),
        "summary": tce.get("testCase", {}).get("name"),
        "type": "Test Case Execution",
        "priority": tce.get("priority", ""),
        "assignee": tce.get("assignee", {}).get("displayName", "Unassigned"),
        "status": tce.get("status", "")
    })

output = {
    "execution": execution,
    "issues": issues,
    "fetched_at": datetime.now().isoformat()
}

os.makedirs("data", exist_ok=True)
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(output, f, indent=2)

print(f"[SUCCESS] Saved RTM data → {OUTPUT_FILE}")
sys.exit(0)
