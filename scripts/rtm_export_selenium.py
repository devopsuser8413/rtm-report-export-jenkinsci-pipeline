#!/usr/bin/env python3
import os, time, sys, pathlib
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

JIRA_USER = os.getenv("JIRA_USER")
JIRA_PASS = os.getenv("JIRA_PASS")
JIRA_BASE = os.getenv("JIRA_BASE", "https://yourdomain.atlassian.net")
PROJECT_KEY = os.getenv("RTM_PROJECT")
TEST_EXEC = os.getenv("TEST_EXECUTION")
DOWNLOAD_DIR = os.getenv("DOWNLOAD_DIR", "report")

outdir = pathlib.Path(DOWNLOAD_DIR)
outdir.mkdir(parents=True, exist_ok=True)

options = Options()
options.add_argument("--headless=new")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
prefs = {"download.default_directory": str(outdir.resolve()), "download.prompt_for_download": False}
options.add_experimental_option("prefs", prefs)

driver = webdriver.Chrome(options=options)

try:
    print(f"[INFO] Logging into Jira: {JIRA_BASE}")
    driver.get(JIRA_BASE)
    time.sleep(5)

    # login if needed
    if "Atlassian" in driver.title:
        driver.find_element(By.ID, "username").send_keys(JIRA_USER)
        driver.find_element(By.ID, "login-submit").click()
        time.sleep(2)
        driver.find_element(By.ID, "password").send_keys(JIRA_PASS)
        driver.find_element(By.ID, "login-submit").click()
        time.sleep(10)

    # Navigate to RTM Test Execution report
    rtm_report_url = f"{JIRA_BASE}/jira/apps/rtm/reports/test-execution"
    driver.get(rtm_report_url)
    time.sleep(8)

    # Select project and test execution (adjust if RTM uses dropdown)
    driver.find_element(By.XPATH, "//input[@placeholder='Project key']").send_keys(PROJECT_KEY)
    driver.find_element(By.XPATH, "//input[@placeholder='Execution key']").send_keys(TEST_EXEC)
    time.sleep(1)

    # Click "Generate" button
    driver.find_element(By.XPATH, "//button[contains(.,'Generate')]").click()
    time.sleep(10)

    # Click "Export → PDF"
    driver.find_element(By.XPATH, "//button[contains(.,'Export')]").click()
    time.sleep(2)
    driver.find_element(By.XPATH, "//span[text()='PDF']").click()
    time.sleep(15)

    print(f"[INFO] File downloaded to {DOWNLOAD_DIR}")
    for f in outdir.glob("*.pdf"):
        print(f"[OK] Found report: {f}")
        sys.exit(0)

    print("[ERROR] No PDF file downloaded.")
    sys.exit(2)

finally:
    driver.quit()
