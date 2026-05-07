#!/bin/bash
# Email Sending - Command Reference
# Copy and paste these commands to send cppcheck reports via email

# ============================================================
# SETUP (Do once)
# ============================================================

# 1. Get EmailJS credentials from https://www.emailjs.com/
# 2. Set environment variables:

export EMAILJS_SERVICE_ID="your_service_id_here"
export EMAILJS_TEMPLATE_ID="your_template_id_here"
export EMAILJS_USER_ID="your_user_id_here"
export EMAILJS_PRIVATE_KEY="your_private_key_here"
export EMAILJS_RECIPIENT="your-email@example.com"

# ============================================================
# GENERATE REPORT
# ============================================================

# Run the complete analysis pipeline
python3 scripts/test.py

# ============================================================
# SEND REPORT VIA EMAIL (Choose one)
# ============================================================

# Option 1: Python Script (Recommended)
python3 scripts/send_email_report_py.py

# Option 2: Bash Script
bash scripts/send_report.sh

# Option 3: Node.js Script
node scripts/send_email_report.js

# ============================================================
# ADVANCED USAGE
# ============================================================

# Python: Custom report path
python3 scripts/send_email_report_py.py --report ./custom_report.txt

# Python: Custom recipient
python3 scripts/send_email_report_py.py --to custom@example.com

# Python: Both custom
python3 scripts/send_email_report_py.py \
  --report ./custom_report.txt \
  --to custom@example.com

# Bash: Custom recipient
bash scripts/send_report.sh --to custom@example.com

# ============================================================
# GITHUB ACTIONS (Automated)
# ============================================================

# Add secrets to repository (Settings > Secrets > New Secret):
# EMAILJS_SERVICE_ID
# EMAILJS_TEMPLATE_ID
# EMAILJS_USER_ID
# EMAILJS_PRIVATE_KEY
# EMAILJS_RECIPIENT

# Trigger manually:
# 1. Go to Actions tab
# 2. Select "MISRA Compliance CI"
# 3. Click "Run workflow"

# Or push to main branch:
git push origin main

# ============================================================
# VERIFY SETUP
# ============================================================

# Check if report exists
ls -lah reports/cppcheck_analysis_report.txt

# View report
cat reports/cppcheck_analysis_report.txt

# Check environment variables are set
echo "Service ID: $EMAILJS_SERVICE_ID"
echo "Template ID: $EMAILJS_TEMPLATE_ID"
echo "User ID: $EMAILJS_USER_ID"
echo "Recipient: $EMAILJS_RECIPIENT"

# ============================================================
# TROUBLESHOOTING
# ============================================================

# Test with debug output
bash -x scripts/send_report.sh

# Check if jq is installed
which jq

# Install jq if missing
sudo apt-get install -y jq

# Check curl accessibility
which curl

# ============================================================
# ONE-LINER COMMANDS
# ============================================================

# Generate and send report (all steps in one)
python3 scripts/test.py && python3 scripts/send_email_report_py.py

# Generate, send to custom recipient
python3 scripts/test.py && python3 scripts/send_email_report_py.py --to custom@example.com

# ============================================================
# CRON / SCHEDULED EXECUTION
# ============================================================

# Edit crontab
crontab -e

# Add this line to run daily at 9 AM:
0 9 * * * cd /home/abhishek/Desktop/project-2026/Simple_webserver_in_C && python3 scripts/test.py && python3 scripts/send_email_report_py.py

# ============================================================
# DOCKER / CONTAINER EXECUTION
# ============================================================

# If using Docker, set environment:
docker run -e EMAILJS_SERVICE_ID="..." \
           -e EMAILJS_TEMPLATE_ID="..." \
           -e EMAILJS_USER_ID="..." \
           -e EMAILJS_PRIVATE_KEY="..." \
           -e EMAILJS_RECIPIENT="..." \
           your-image \
           bash -c "python3 scripts/test.py && python3 scripts/send_email_report_py.py"

# ============================================================
# SEND MULTIPLE RECIPIENTS
# ============================================================

# For multiple recipients, create separate environment variables:
RECIPIENTS="user1@example.com user2@example.com user3@example.com"

for recipient in $RECIPIENTS; do
  python3 scripts/send_email_report_py.py --to "$recipient"
done

# ============================================================
# BACKUP & ARCHIVE REPORTS
# ============================================================

# Create timestamped backup
cp reports/cppcheck_analysis_report.txt "reports/backup_$(date +%Y%m%d_%H%M%S).txt"

# Archive all reports
tar -czf reports_archive_$(date +%Y%m%d).tar.gz reports/

# ============================================================
# CI/CD INTEGRATION EXAMPLES
# ============================================================

# Jenkins Pipeline (Groovy)
stage('Send Report') {
    steps {
        sh 'python3 scripts/send_email_report_py.py'
    }
}

# GitLab CI
send_report:
  stage: notify
  script:
    - python3 scripts/send_email_report_py.py
  only:
    - main

# ============================================================
# HELP & DOCUMENTATION
# ============================================================

# View quick start guide
cat QUICK_START_EMAIL.md

# View full setup guide
cat EMAIL_SETUP.md

# View implementation summary
cat IMPLEMENTATION_SUMMARY.md

# View Python script help
python3 scripts/send_email_report_py.py --help

# ============================================================
