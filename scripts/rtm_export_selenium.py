#!/usr/bin/env python3
"""
RTM Test Execution Report Export Automation
-------------------------------------------
Logs into Jira Cloud (with RTM plugin), navigates to the Test Execution report,
exports it as PDF, and saves it under /report folder for Jenkins CI/CD pipelines.
"""

import os
import sys
import time
import pathlib
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ------------------------------------------------------------------------------
# Environment Variables (injected from Jenkins)
# ------------------------------------------------------------------------------
JIRA_USER = os.getenv("JIRA_USER")
JIRA_PASS = os.getenv("JIRA_PASS")
JIRA_BASE = os.getenv("JIRA_BASE", "https://yourdomain.atlassian.net")
PROJECT_KEY = os.getenv("RTM_PROJECT")
TEST_EXEC = os.getenv("TEST_EXECUTION")
DOWNLOAD_DIR = os.getenv("DOWNLOAD_DIR", "report")

# ------------------------------------------------------------------------------
# Directory Setup
# ------------------------------------------------------------------------------
outdir = pathlib.Path(DOWNLOAD_DIR)
outdir.mkdir(parents=True, exist_ok=True)

# ------------------------------------------------------------------------------
# Configure Headless Chrome for Jenkins Agent
# ------------------------------------------------------------------------------
options = Options()
options.add_argument("--headless=new")  # New headless mode for Chrome 109+
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--window-size=1920,1080")
prefs = {
    "download.default_directory": str(outdir.resolve()),
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "safebrowsing.enabled": True
}
options.add_experimental_option("prefs", prefs)

driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 30)

try:
    # --------------------------------------------------------------------------
    # Jira Login Flow
    # --------------------------------------------------------------------------
    print(f"[INFO] Logging into Jira: {JIRA_BASE}")
    driver.get(JIRA_BASE)
    wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))

    if "Atlassian" in driver.title or "Login" in driver.title:
        try:
            print("[INFO] Atlassian login page detected.")
            username_box = wait.until(EC.presence_of_element_located((By.ID, "username")))
            username_box.clear()
            username_box.send_keys(JIRA_USER)
            driver.find_element(By.ID, "login-submit").click()

            print("[INFO] Waiting for password field...")
            wait.until(EC.presence_of_element_located((By.ID, "password")))
            driver.find_element(By.ID, "password").send_keys(JIRA_PASS)
            driver.find_element(By.ID, "login-submit").click()
            print("[INFO] Login submitted. Waiting for redirect...")
            time.sleep(10)

        except Exception as e:
            print(f"[WARN] Could not locate Atlassian login elements: {e}")
            print("[WARN] Possible SSO redirect (Google, Microsoft, etc).")
            driver.save_screenshot(str(outdir / "login_error.png"))
            raise

    elif "Dashboard" in driver.title or "Projects" in driver.title:
        print("[INFO] Already logged into Jira session (cached cookies).")

    else:
        print(f"[WARN] Unexpected login page title: {driver.title}")
        driver.save_screenshot(str(outdir / "unexpected_login.png"))

    # --------------------------------------------------------------------------
    # Navigate to RTM Test Execution Report
    # --------------------------------------------------------------------------
    rtm_report_url = f"{JIRA_BASE}/jira/apps/rtm/reports/test-execution"
    print(f"[INFO] Opening RTM Test Execution Report: {rtm_report_url}")
    driver.get(rtm_report_url)

    # Wait for report form elements to appear
    time.sleep(8)
    driver.find_element(By.XPATH, "//input[@placeholder='Project key']").send_keys(PROJECT_KEY)
    driver.find_element(By.XPATH, "//input[@placeholder='Execution key']").send_keys(TEST_EXEC)
    time.sleep(1)

    # Click "Generate" button
    print("[INFO] Generating report...")
    driver.find_element(By.XPATH, "//button[contains(.,'Generate')]").click()
    time.sleep(10)

    # --------------------------------------------------------------------------
    # Export to PDF
    # --------------------------------------------------------------------------
    print("[INFO] Exporting report as PDF...")
    driver.find_element(By.XPATH, "//button[contains(.,'Export')]").click()
    time.sleep(2)
    driver.find_element(By.XPATH, "//span[text()='PDF']").click()
    time.sleep(15)

    # --------------------------------------------------------------------------
    # Verify Download
    # --------------------------------------------------------------------------
    print(f"[INFO] Checking downloaded files in {DOWNLOAD_DIR}")
    found = False
    for f in outdir.glob("*.pdf"):
        print(f"[OK] Found report: {f}")
        found = True
        break

    if not found:
        print("[ERROR] No PDF file downloaded.")
        driver.save_screenshot(str(outdir / "export_failed.png"))
        sys.exit(2)

    print(f"[SUCCESS] RTM Test Execution report exported successfully.")
    sys.exit(0)

except Exception as e:
    print(f"[ERROR] Unexpected error occurred: {e}")
    driver.save_screenshot(str(outdir / "fatal_error.png"))
    sys.exit(1)

finally:
    driver.quit()
