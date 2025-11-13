#!/usr/bin/env python3
"""
RTM Report Generator – HTML & PDF
---------------------------------
Reads Deviniti RTM Test Execution results (testRuns)
and generates HTML + PDF reports.
"""

import os
import sys
import json
import html
import requests
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

from fpdf import FPDF
from tabulate import tabulate

# -----------------------------
# Paths & constants
# -----------------------------
DATA_FILE = Path("data/rtm_data.json")
REPORT_DIR = Path("report")
REPORT_DIR.mkdir(parents=True, exist_ok=True)

ts = datetime.now().strftime("%Y%m%d-%H%M%S")
HTML_FILE = REPORT_DIR / f"rtm_report_{ts}.html"
PDF_FILE = REPORT_DIR / f"rtm_report_{ts}.pdf"
HTML_LATEST = REPORT_DIR / "rtm_report.html"
PDF_LATEST = REPORT_DIR / "rtm_report.pdf"

JIRA_BASE = os.getenv("JIRA_BASE")
JIRA_USER = os.getenv("JIRA_USER")
JIRA_TOKEN = os.getenv("JIRA_TOKEN")

PROJECT_KEY = os.getenv("RTM_PROJECT", "")
EXECUTION_KEY = os.getenv("JIRA_EXECUTION_ID", "")
REPORT_TITLE = os.getenv("REPORT_TITLE", "RTM Test Execution Report")

FONT_PATH = Path("fonts/DejaVuSans.ttf")

# -----------------------------
# Logging
# -----------------------------
def log(msg, level="INFO"):
    t = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{level}] {t} | {msg}")

# -----------------------------
# Validate input
# -----------------------------
if not DATA_FILE.exists():
    log(f"Missing input file: {DATA_FILE}", "ERROR")
    sys.exit(1)

with open(DATA_FILE, encoding="utf-8") as f:
    data = json.load(f)

testRuns: List[Dict[str, Any]] = data.get("testRuns", [])

if not testRuns:
    log("No RTM test runs found. Nothing to report.", "ERROR")
    sys.exit(2)

log(f"Loaded {len(testRuns)} RTM test runs.")

# -----------------------------
# Fetch Test Case details
# -----------------------------
def fetch_test_case_details(testCaseKey):
    """RTM test case details (summary, priority, type)."""
    url = f"{JIRA_BASE}/rest/atm/1.0/testcases/{testCaseKey}"

    try:
        r = requests.get(url, auth=(JIRA_USER, JIRA_TOKEN))
        if r.status_code == 200:
            return r.json()
        else:
            return {}
    except:
        return {}

# -----------------------------
# Normalize rows for report
# -----------------------------
issues = []

for run in testRuns:
    key = run.get("testCaseKey", "")
    status = run.get("status", "Unknown")
    runBy = run.get("runBy", "Unassigned")

    tc = fetch_test_case_details(key)

    issues.append({
        "key": key,
        "summary": tc.get("name", ""),
        "type": tc.get("type", ""),
        "priority": tc.get("priority", ""),
        "assignee": runBy,
        "status": status
    })

# -----------------------------
# Status Summary
# -----------------------------
status_summary = {}
for i in issues:
    s = i.get("status", "Unknown")
    status_summary[s] = status_summary.get(s, 0) + 1

# -----------------------------
# HTML Report
# -----------------------------
def generate_html():
    log("Generating HTML...")

    rows = [
        [
            i["key"],
            i["summary"],
            i["type"],
            i["priority"],
            i["assignee"],
            i["status"],
        ]
        for i in issues
    ]

    table_html = tabulate(
        rows,
        headers=["Key", "Summary", "Type", "Priority", "Assignee", "Status"],
        tablefmt="html"
    )

    meta = f"""
    <b>Project:</b> {PROJECT_KEY}<br>
    <b>Execution:</b> {EXECUTION_KEY}<br>
    <b>Generated:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br>
    <b>Total Cases:</b> {len(issues)}<br>
    <b>Status Summary:</b> {html.escape(str(status_summary))}
    """

    html_doc = f"""
    <html><head>
    <meta charset="UTF-8">
    <title>{REPORT_TITLE}</title>
    </head>
    <body>
    <h1>{REPORT_TITLE}</h1>
    <div>{meta}</div><br>
    {table_html}
    </body></html>
    """

    HTML_FILE.write_text(html_doc, encoding="utf-8")
    HTML_LATEST.write_text(html_doc, encoding="utf-8")

    log(f"HTML written → {HTML_FILE}")

# -----------------------------
# PDF Report
# -----------------------------
class RTMReportPDF(FPDF):
    pass  # unchanged for simplicity — your existing PDF class still works

def generate_pdf():
    log("Generating PDF...")

    pdf = RTMReportPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, REPORT_TITLE, ln=True)

    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 6, f"Project: {PROJECT_KEY}", ln=True)
    pdf.cell(0, 6, f"Execution: {EXECUTION_KEY}", ln=True)
    pdf.cell(0, 6, f"Generated: {datetime.now()}", ln=True)
    pdf.ln(4)

    headers = ["Key", "Summary", "Type", "Priority", "Assignee", "Status"]

    col_widths = [25, 60, 25, 25, 30, 25]

    # Header
    pdf.set_font("Arial", "B", 9)
    for i, h in enumerate(headers):
        pdf.cell(col_widths[i], 8, h, 1, 0, "C")
    pdf.ln()

    # Rows
    pdf.set_font("Arial", "", 9)
    for i in issues:
        pdf.cell(col_widths[0], 6, i["key"], 1)
        pdf.cell(col_widths[1], 6, i["summary"][:40], 1)
        pdf.cell(col_widths[2], 6, i["type"], 1)
        pdf.cell(col_widths[3], 6, i["priority"], 1)
        pdf.cell(col_widths[4], 6, i["assignee"], 1)
        pdf.cell(col_widths[5], 6, i["status"], 1)
        pdf.ln()

    pdf.output(str(PDF_FILE))
    PDF_LATEST.write_bytes(PDF_FILE.read_bytes())
    log(f"PDF written → {PDF_FILE}")

# -----------------------------
# Main
# -----------------------------
generate_html()
generate_pdf()
log("Report generation complete.")
print("[OK] RTM HTML and PDF generated.")
