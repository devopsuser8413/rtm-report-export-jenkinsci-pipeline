#!/usr/bin/env python3
"""
====================================================================================
📘 RTM Report Generator – HTML & PDF (Production-Ready)
------------------------------------------------------------------------------------
Generates Requirement Traceability Matrix (RTM) reports from JSON data fetched
from Jira. Produces:
  ✅ HTML Report (for Confluence upload)
  ✅ PDF Report  (for email distribution)

Author  : DevOpsUser8413
Version : 1.0.0
====================================================================================
"""

import os
import sys
import json
from pathlib import Path
from fpdf import FPDF
from tabulate import tabulate
from datetime import datetime

# ------------------------------------------------------------------------------
# 📂 Directory Setup
# ------------------------------------------------------------------------------
DATA_FILE = Path("data/rtm_data.json")
REPORT_DIR = Path("report")
REPORT_DIR.mkdir(parents=True, exist_ok=True)

HTML_FILE = REPORT_DIR / "rtm_report.html"
PDF_FILE  = REPORT_DIR / "rtm_report.pdf"
LOG_FILE  = REPORT_DIR / "report_generation_log.txt"

# ------------------------------------------------------------------------------
# 🧾 Validation
# ------------------------------------------------------------------------------
if not DATA_FILE.exists():
    print(f"[ERROR] Missing input file: {DATA_FILE}")
    sys.exit(1)

# ------------------------------------------------------------------------------
# 🧩 Helper: Log messages to both console and file
# ------------------------------------------------------------------------------
def log(message, level="INFO"):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted = f"[{level}] {ts} | {message}"
    print(formatted)
    with open(LOG_FILE, "a", encoding="utf-8") as logf:
        logf.write(formatted + "\n")

# ------------------------------------------------------------------------------
# 🧮 Load & Validate Data
# ------------------------------------------------------------------------------
try:
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
except json.JSONDecodeError as e:
    log(f"Invalid JSON structure in {DATA_FILE}: {e}", "ERROR")
    sys.exit(2)

issues = data.get("issues", [])
if not issues:
    log("No issues found in RTM dataset. Aborting report generation.", "ERROR")
    sys.exit(3)

log(f"Loaded {len(issues)} RTM issues for reporting.")

# ------------------------------------------------------------------------------
# 🧱 Generate Summary Stats
# ------------------------------------------------------------------------------
status_summary = {}
for issue in issues:
    status = issue.get("status", "Unknown")
    status_summary[status] = status_summary.get(status, 0) + 1

log(f"Status Breakdown: {status_summary}")

# ------------------------------------------------------------------------------
# 🧩 Generate HTML Report
# ------------------------------------------------------------------------------
def generate_html_report():
    log("Generating HTML report...")

    rows = []
    for i in issues:
        rows.append([
            i.get("key", ""),
            i.get("summary", ""),
            i.get("type", ""),
            i.get("priority", ""),
            i.get("assignee", ""),
            i.get("status", "")
        ])

    html_table = tabulate(
        rows,
        headers=["Key", "Summary", "Type", "Priority", "Assignee", "Status"],
        tablefmt="html"
    )

    html_content = f"""
    <html>
    <head>
        <meta charset="UTF-8">
        <title>RTM Test Execution Report</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 20px;
                color: #333;
            }}
            h1 {{
                color: #0073AA;
                border-bottom: 2px solid #0073AA;
                padding-bottom: 10px;
            }}
            .summary {{
                background: #f2f2f2;
                padding: 10px;
                margin-bottom: 20px;
                border-radius: 8px;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 10px;
            }}
            th, td {{
                border: 1px solid #ddd;
                padding: 8px;
                text-align: left;
            }}
            th {{
                background-color: #0073AA;
                color: white;
            }}
            tr:nth-child(even) {{
                background-color: #f9f9f9;
            }}
        </style>
    </head>
    <body>
        <h1>RTM Test Execution Report</h1>
        <div class="summary">
            <b>Generated On:</b> {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}<br>
            <b>Total Issues:</b> {len(issues)}<br>
            <b>Status Breakdown:</b> {status_summary}
        </div>
        {html_table}
    </body>
    </html>
    """

    HTML_FILE.write_text(html_content, encoding="utf-8")
    log(f"HTML report generated successfully → {HTML_FILE}")

# ------------------------------------------------------------------------------
# 🧾 Generate PDF Report
# ------------------------------------------------------------------------------
def generate_pdf_report():
    log("Generating PDF report...")

    class RTMReportPDF(FPDF):
        def header(self):
            self.set_font("Arial", "B", 14)
            self.cell(0, 10, "RTM Test Execution Report", ln=True, align="C")
            self.ln(5)
            self.set_font("Arial", "", 10)
            self.cell(0, 8, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True, align="C")
            self.ln(8)

        def footer(self):
            self.set_y(-15)
            self.set_font("Arial", "I", 8)
            self.cell(0, 10, f"Page {self.page_no()}", align="C")

    pdf = RTMReportPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=10)

    pdf.cell(0, 8, f"Total Issues: {len(issues)}", ln=True)
    pdf.cell(0, 8, f"Status Breakdown: {status_summary}", ln=True)
    pdf.ln(10)

    # Table header
    pdf.set_font("Arial", "B", 10)
    headers = ["Key", "Summary", "Type", "Priority", "Assignee", "Status"]
    col_widths = [25, 65, 25, 25, 35, 25]
    for idx, h in enumerate(headers):
        pdf.cell(col_widths[idx], 8, h, 1, 0, "C")
    pdf.ln()

    # Table data
    pdf.set_font("Arial", "", 9)
    for issue in issues:
        pdf.cell(col_widths[0], 8, issue.get("key", ""), 1)
        pdf.cell(col_widths[1], 8, issue.get("summary", "")[:45], 1)
        pdf.cell(col_widths[2], 8, issue.get("type", ""), 1)
        pdf.cell(col_widths[3], 8, issue.get("priority", ""), 1)
        pdf.cell(col_widths[4], 8, issue.get("assignee", "")[:20], 1)
        pdf.cell(col_widths[5], 8, issue.get("status", ""), 1)
        pdf.ln()

    pdf.output(str(PDF_FILE))
    log(f"PDF report generated successfully → {PDF_FILE}")

# ------------------------------------------------------------------------------
# 🏁 Main
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    print("══════════════════════════════════════════════════════════════")
    print("        🧾 Starting RTM Report Generation Process")
    print("══════════════════════════════════════════════════════════════")

    generate_html_report()
    generate_pdf_report()

    log("RTM report generation completed successfully.")
    print("[✅] RTM HTML and PDF reports generated successfully.")
    sys.exit(0)
