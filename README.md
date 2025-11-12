# 📘 RTM Test Execution Report Automation (Jenkins – Jira – Confluence – Email)

Automates **Test Execution Report Export** from **Jira RTM**, publishes it to **Confluence**, and sends it as an **email notification** — all orchestrated via **Jenkins CI/CD**.

---

## 🧩 Table of Contents
1. Software Installation
2. Software Tools Setup
3. Jenkins Setup (Step-by-Step)
4. Jira & RTM Configuration
5. GitHub Repository Setup
6. Confluence Space & API Token
7. Email App Password Setup
8. Pipeline Stage Breakdown
9. Common Issues & Fixes
10. Folder Structure

---

## 🧱 1. Software Installation

Install the following software on the Jenkins agent:

| Software | Purpose | Version |
|-----------|----------|---------|
| Python 3.11+ | Run automation scripts | python --version |
| Google Chrome | Browser for Selenium | Latest |
| ChromeDriver | Controls Chrome (match version) | Same as Chrome |
| Git | Source code checkout | Latest |
| Jenkins | CI/CD automation | 2.462+ |
| pip | Python dependency manager | pip install --upgrade pip |

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

---

## ⚙️ 2. Software Tools Setup

| Tool | Description |
|------|--------------|
| Jira Cloud | Manage Scrum project & test executions |
| RTM for Jira (Cloud) | Plugin for test management |
| Confluence Cloud | Publish generated test execution reports |
| Jenkins | CI/CD automation tool |
| GitHub | SCM for storing pipeline and Python scripts |
| SMTP (Office365/Gmail) | For automated email delivery |

---

## 🧰 3. Jenkins Setup (Step-by-Step)

### Step 1: Install Jenkins Plugins
Install:
- Pipeline
- Credentials Binding
- AnsiColor
- Git
- ShiningPanda
- Email Extension

### Step 2: Add Jenkins Credentials

| ID | Type | Description |
|----|------|-------------|
| jira-base | Secret text | Jira URL |
| jira-user | Secret text | Jira email |
| jira-pass | Secret text | Jira API token |
| confluence-base | Secret text | Confluence URL |
| confluence-user | Secret text | Confluence email |
| confluence-token | Secret text | Confluence API token |
| smtp-host | Secret text | SMTP server |
| smtp-user | Secret text | Email sender |
| smtp-pass | Secret text | Email app password |
| sender-email | Secret text | Sender email |
| multi-receivers | Secret text | Recipients list |

### Step 3: Create Jenkins Pipeline Job

1. Jenkins → New Item → Pipeline  
2. Name: `rtm-report-export-pipeline`  
3. SCM: Git → Repo URL  
4. Branch: main  
5. Script Path: Jenkinsfile  
6. Save & Build  

---

## 📋 4. Jira & RTM Configuration

### Step 1: Create Scrum Project
- Jira → Projects → Create Project → Scrum → Team-managed  
- Key: RTM-DEMO

### Step 2: Install RTM Plugin
- Jira Settings → Apps → Find “RTM for Jira Cloud” → Install

### Step 3: Enable RTM
- Project Settings → Apps → RTM → Enable

### Step 4: Create Test Artifacts

| Artifact | Description |
|-----------|--------------|
| Requirements | Define test requirements |
| Test Cases | Write test cases |
| Test Plans | Group test cases |
| Test Executions | Execute and track tests |

### Step 5: Export Report Automation
- Manual: RTM → Reports → Test Execution → Generate → Export → PDF  
- Automated: Jenkins pipeline runs Selenium script `rtm_export_selenium.py`

---

## 💻 5. GitHub Repository Setup

```bash
git clone https://github.com/<user>/rtm-report-export-jenkinsci-pipeline.git
cd rtm-report-export-jenkinsci-pipeline
git add .
git commit -m "Initial commit - RTM automation"
git push origin main
```

Generate GitHub Token → Developer Settings → Tokens → Scopes: repo, workflow.

---

## 📘 6. Confluence Space & API Token

1. Confluence → Spaces → Create Space → Blank → Space Key: DEV  
2. Create API Token → https://id.atlassian.com/manage/api-tokens  
3. Label: confluence-api-jenkins  
4. Add in Jenkins credentials as `confluence-token`

---

## 📧 7. Email App Password Setup

### Office365
1. Account → Security → App Passwords → Generate  
2. Use as smtp-pass in Jenkins  

### Gmail
1. Enable 2-Step Verification → App Passwords → Select Mail → Windows Computer  
2. Add as Jenkins credential `smtp-pass`

---

## 🔄 8. Pipeline Stage Breakdown

| Stage | Description |
|--------|--------------|
| Checkout Source Code | Pulls scripts and Jenkinsfile from GitHub |
| Setup Python Environment | Creates .venv and installs requirements.txt |
| Export RTM Report | Uses Selenium to generate PDF report |
| Publish to Confluence | Uploads PDF to Confluence space |
| Email Notification | Sends email with report attachment |
| Post Actions | Archives report artifact |

---

## 🧠 9. Common Issues & Fixes

| Issue | Cause | Fix |
|--------|--------|----|
| ChromeDriver mismatch | Different versions | Match Chrome and ChromeDriver |
| 401 Unauthorized | Invalid API token | Regenerate API token |
| No PDF found | RTM report slow to load | Increase sleep time in Selenium script |
| Email not sent | SMTP blocked | Use correct port & app password |
| Permission denied | Jenkins access issue | Run Jenkins as admin |
| Jira login failed | SSO enabled | Use API token |
| Workspace error | Path issue | Use absolute paths |

---

## 📁 10. Folder Structure

```
rtm-report-export-jenkinsci-pipeline/
├── Jenkinsfile
├── README.md
├── requirements.txt
├── report/
│   └── (generated PDFs)
└── scripts/
    ├── rtm_export_selenium.py
    ├── confluence_publish.py
    └── send_email.py
```

---

## ✅ Contributors

- **DevOps Engineer:** Project Owner  
- **Tools:** Jenkins, Jira RTM, Confluence, GitHub, Python  
- **Version:** v1.0.0 (Production Release)
