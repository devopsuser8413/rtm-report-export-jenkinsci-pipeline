/************************************************************************************
 * 📘 RTM Report Export & Publishing Pipeline
 * ----------------------------------------------------------------------------------
 * Fetches Jira RTM data via REST API, generates HTML/PDF report,
 * publishes to Confluence, and emails stakeholders.
 *
 * ✅ Fully headless (no Selenium or browser required)
 * ✅ Works in Windows or Linux Jenkins agents
 * ✅ Modular Python-based scripts with virtual environment
 *
 * Author: DevOpsUser8413
 * Version: 1.0.0
 ************************************************************************************/

pipeline {
    agent any

    /***************************************************************
     * 🧭 Global Options
     ***************************************************************/
    options {
        timestamps()          // Show build timestamps
        ansiColor('xterm')    // Colored console output
        disableConcurrentBuilds()
    }

    /***************************************************************
     * 🌍 Environment Variables
     ***************************************************************/
    environment {
        // 🔹 Jira API
        JIRA_BASE   = credentials('jira-base')
        JIRA_USER   = credentials('jira-user')
        JIRA_TOKEN  = credentials('jira-token')

        // 🔹 Confluence API
        CONFLUENCE_BASE   = credentials('confluence-base')
        CONFLUENCE_USER   = credentials('confluence-user')
        CONFLUENCE_TOKEN  = credentials('confluence-token')
        CONFLUENCE_SPACE  = 'DEMO'
        CONFLUENCE_TITLE  = 'RTM Test Execution Report'

        // 🔹 SMTP Email
        SMTP_HOST    = credentials('smtp-host')
        SMTP_PORT    = '587'
        SMTP_USER    = credentials('smtp-user')
        SMTP_PASS    = credentials('smtp-pass')
        REPORT_FROM  = credentials('sender-email')
        REPORT_TO    = credentials('multi-receivers')

        // 🔹 Project Runtime
        RTM_PROJECT     = 'RTM-DEMO'
        TEST_EXECUTION  = 'RD-4'
        VENV_PATH       = '.venv'
    }

    /***************************************************************
     * 🧱 Pipeline Stages
     ***************************************************************/
    stages {

        /***********************
         * Stage 1: Checkout
         ***********************/
        stage('Checkout Source Code') {
            steps {
                echo "🔍 Checking out repository from Git..."
                checkout scm
            }
        }

        /***********************
         * Stage 2: Setup Environment
         ***********************/
        stage('Setup Python Environment') {
            steps {
                echo "📦 Setting up Python virtual environment..."
                bat """
                    if not exist %VENV_PATH% python -m venv %VENV_PATH%
                    %VENV_PATH%\\Scripts\\python -m pip install --upgrade pip
                    %VENV_PATH%\\Scripts\\pip install -r requirements.txt
                """
            }
        }

        /***********************
         * Stage 3: Fetch Jira RTM Data
         ***********************/
        stage('Fetch RTM Data from Jira') {
            steps {
                echo "📡 Fetching RTM Test Execution data from Jira via REST API..."
                bat """
                    %VENV_PATH%\\Scripts\\python scripts\\fetch_rtm_data.py
                """
            }
        }

        /***********************
         * Stage 4: Generate Report
         ***********************/
        stage('Generate HTML/PDF Report') {
            steps {
                echo "🧾 Generating RTM HTML and PDF reports..."
                bat """
                    %VENV_PATH%\\Scripts\\python scripts\\generate_rtm_report.py
                """
            }
        }

        /***********************
         * Stage 5: Publish to Confluence
         ***********************/
        stage('Publish to Confluence') {
            steps {
                echo "🌐 Publishing RTM report to Confluence space..."
                bat """
                    %VENV_PATH%\\Scripts\\python scripts\\confluence_publish.py
                """
            }
        }

        /***********************
         * Stage 6: Email Notification
         ***********************/
        stage('Send Email Notification') {
            steps {
                echo "📧 Sending RTM report via email..."
                bat """
                    %VENV_PATH%\\Scripts\\python scripts\\send_email.py
                """
            }
        }
    }

    /***************************************************************
     * 📦 Post-Build Actions
     ***************************************************************/
    post {
        always {
            echo "📘 Jenkins workspace: ${env.WORKSPACE}"
            echo "🧹 Cleaning temporary files..."
            cleanWs()
        }
        success {
            echo "✅ Pipeline completed successfully!"
        }
        failure {
            echo "❌ Pipeline failed. Check Jenkins console logs for details."
        }
    }
}
