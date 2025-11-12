#!/usr/bin/env python3
"""
RTM Test Execution Report Export Automation (Jenkins-Stable Edition)
--------------------------------------------------------------------
Automates Jira RTM Test Execution report export to PDF.

✅ Designed for:
  - Jenkins running on Windows (java -jar jenkins.war)
  - Chrome installed system-wide
  - Headless execution using software rendering

Author: DevOps Automation (RTM Report Export)
"""

import os
import sys
import time
import pathlib
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ------------------------------------------------------------------------------
# Environment Variables (from Jenkins)
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
# Detect Chrome installation path
# ------------------------------------------------------------------------------
CHROME_PATHS = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    rf"C:\Users\{os.getenv('USERNAME')}\AppData\Local\Google\Chrome\Application\chrome.exe",
]

chrome_binary = next((p for p in CHROME_PATHS if os.path.exists(p)), None)
if not chrome_binary:
    print("[ERROR] Google Chrome not found. Please install Chrome or update path.")
    sys.exit(1)

print(f"[INFO] Chrome detected at: {chrome_binary}")

# ------------------------------------------------------------------------------
# Configure Chrome Options (Safe Headless Jenkins Mode)
# ------------------------------------------------------------------------------
options = Options()

# 🧩 Core stability flags for Jenkins Windows background mode
options.add_argument("--headless=new")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-software-rasterizer")
options.add_argument("--single-process")
options.add_argument("--disable-extensions")
options.add_argument("--disable-background-networking")
options.add_argument("--disable-client-side-phishing-detection")
options.add_argument("--disable-component-update")
options.add_argument("--disable-default-apps")
options.add_argument("--disable-popup-blocking")
options.add_argument("--disable-sync")
options.add_argument("--no-first-run")
options.add_argument("--no-service-autorun")
options.add_argument("--password-store=basic")
options.add_argument("--use-mock-keychain")
options.add_argument("--window-size=1920,1080")
options.add_argument("--remote-debugging-port=9222")
options.add_argument("--enable-logging")
options.add_argument("--v=1")
options.add_argument("--force-device-scale-factor=1")

# ✅ Force software rendering mode
options.add_argument("--disable-features=VizDisplayCompositor,UseOzonePlatform,PlatformHEVCDecoderSupport")
options.add_argument("--use-gl=swiftshader")
options.add_argument("--use-angle=swiftshader")

# Optional — Chrome profile (for SSO)
options.add_argument(r"user-data-dir=C:\Users\I17270834\AppData\Local\Google\Chrome\User Data")

# Explicit binary
options.binary_location = chrome_binary

# Preferences for auto-download
prefs = {
    "download.default_directory": str(outdir.resolve()),
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "safebrowsing.enabled": True,
    "plugins.always_open_pdf_externally": True
}
options.add_experimental_option("prefs", prefs)

print(f"[INFO] Chrome binary set to: {options.binary_location}")

# ------------------------------------------------------------------------------
# Start ChromeDriver
# ------------------------------------------------------------------------------
service = Service(r"C:\tools\chromedriver\chromedriver-win64\chromedriver.exe")

try:
    driver = webdriver.Chrome(service=service, options=options)
    wait = WebDriverWait(driver, 30)
    print("[INFO] ✅ Chrome started successfully.")
except Exception as e:
    print(f"[ERROR] ❌ Chrome startup failed: {e}")
    print("[HINT] Try disabling headless mode or running Jenkins interactively.")
    sys.exit(1)

# ------------------------------------------------------------------------------
# Jira Login and RTM Export
# ------------------------------------------------------------------------------
try:
    print(f"[INFO] Logging into Jira: {JIRA_BASE}")
    driver.get(JIRA_BASE)
    wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))

    # Detect login page
    if "Atlassian" in driver.title or "Login" in driver.title:
        print("[INFO] Atlassian login page detected.")
        try:
            username_box = wait.until(
                EC.presence_of_element_located((By.XPATH, "//input[@id='username' or @name='username']"))
            )
            username_box.clear()
            username_box.send_keys(JIRA_USER)
            print("[INFO] Username entered.")

            # Continue
            try:
                driver.find_element(By.ID, "login-submit").click()
            except:
                driver.find_element(By.XPATH, "//button[contains(.,'Continue')]").click()

            # Password
            print("[INFO] Waiting for password field...")
            password_box = wait.until(
                EC.presence_of_element_located((By.XPATH, "//input[@id='password' or @name='password']"))
            )
            password_box.clear()
            password_box.send_keys(JIRA_PASS)
            print("[INFO] Password entered.")

            # Login
            try:
                driver.find_element(By.ID, "login-submit").click()
            except:
                driver.find_element(By.XPATH, "//button[contains(.,'Log in')]").click()

            print("[INFO] Login submitted. Waiting for redirect...")
            time.sleep(10)

        except Exception as e:
            print(f"[WARN] Login elements not found or redirected to SSO: {e}")
            driver.save_screenshot(str(outdir / "sso_redirect.png"))
            print("[WARN] If using SSO, configure Chrome profile reuse via user-data-dir.")
            sys.exit(2)
    else:
        print(f"[INFO] Jira page title: {driver.title}")

    # --------------------------------------------------------------------------
    # Navigate to RTM Test Execution Report
    # --------------------------------------------------------------------------
    rtm_url = f"{JIRA_BASE}/jira/apps/rtm/reports/test-execution"
    print(f"[INFO] Navigating to RTM Test Execution Report: {rtm_url}")
    driver.get(rtm_url)
    time.sleep(8)

    # Fill report fields
    driver.find_element(By.XPATH, "//input[@placeholder='Project key']").send_keys(PROJECT_KEY)
    driver.find_element(By.XPATH, "//input[@placeholder='Execution key']").send_keys(TEST_EXEC)
    time.sleep(1)

    print("[INFO] Generating RTM report...")
    driver.find_element(By.XPATH, "//button[contains(.,'Generate')]").click()
    time.sleep(10)

    # --------------------------------------------------------------------------
    # Export Report as PDF
    # --------------------------------------------------------------------------
    print("[INFO] Exporting report as PDF...")
    driver.find_element(By.XPATH, "//button[contains(.,'Export')]").click()
    time.sleep(2)
    driver.find_element(By.XPATH, "//span[text()='PDF']").click()
    time.sleep(20)

    # --------------------------------------------------------------------------
    # Verify Download
    # --------------------------------------------------------------------------
    print(f"[INFO] Checking for downloaded PDF in '{DOWNLOAD_DIR}' ...")
    for f in outdir.glob("*.pdf"):
        print(f"[SUCCESS] ✅ Report downloaded: {f}")
        sys.exit(0)

    print("[ERROR] ❌ PDF not found after export.")
    driver.save_screenshot(str(outdir / "export_failed.png"))
    sys.exit(3)

except Exception as e:
    print(f"[ERROR] Unexpected failure: {e}")
    driver.save_screenshot(str(outdir / "fatal_error.png"))
    sys.exit(4)

finally:
    driver.quit()
