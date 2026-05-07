# Email Report Sending Setup Guide

This guide explains how to send cppcheck analysis reports via email using EmailJS.

## Table of Contents
1. [EmailJS Setup](#emailjs-setup)
2. [GitHub Actions Integration](#github-actions-integration)
3. [Local Usage](#local-usage)
4. [Environment Variables](#environment-variables)

---

## EmailJS Setup

### Step 1: Create EmailJS Account
1. Visit [emailjs.com](https://www.emailjs.com/)
2. Sign up for a free account
3. Go to dashboard and note your **User ID**

### Step 2: Create Email Service
1. Click on "Email Services" in the left menu
2. Click "Add New Service"
3. Choose your email provider (Gmail, Outlook, etc.)
4. Follow the setup wizard to authenticate
5. Copy the **Service ID** (e.g., `service_xxxxx`)

### Step 3: Create Email Template
1. Click on "Email Templates"
2. Click "Create New Template"
3. Set the following template:

```
Template Name: Cppcheck Report Email
Subject: MISRA Analysis - {{status}}
Content:

Project: {{project_name}}
Status: {{status}}
Branch: {{branch}}
Commit: {{commit}}

ANALYSIS SUMMARY:
- Total Issues: {{total_issues}}
- MISRA Violations: {{misra_violations}}
- Errors: {{errors}}
- Warnings: {{warnings}}
- Portability Issues: {{portability_issues}}
- Style Issues: {{style_issues}}

Generated: {{timestamp}}
Workflow: {{workflow_link}}

DETAILED REPORT:
{{report_content}}
```

4. Copy the **Template ID** (e.g., `template_xxxxx`)

### Step 4: Get API Credentials
1. Go to "Account" settings
2. Click on "API" or "Security"
3. Find your **Private Key** (also called API Key)

---

## GitHub Actions Integration

### Step 1: Add Secrets to GitHub Repository

1. Go to your repository settings
2. Navigate to **Secrets and variables** > **Actions**
3. Click "New repository secret"
4. Add these secrets:

| Secret Name | Value |
|-----------|-------|
| `EMAILJS_SERVICE_ID` | Your Service ID from EmailJS |
| `EMAILJS_TEMPLATE_ID` | Your Template ID from EmailJS |
| `EMAILJS_USER_ID` | Your User ID from EmailJS |
| `EMAILJS_PRIVATE_KEY` | Your Private Key from EmailJS |
| `EMAILJS_RECIPIENT` | Your recipient email address |

### Step 2: Workflow Configuration

The workflow file `.github/workflows/misra_ci.yml` automatically:
- Runs cppcheck analysis on push to `main` branch
- Sends email notification with full report
- Includes detailed statistics and report content

**Trigger conditions:**
- Manual trigger: `workflow_dispatch`
- Push to `main` branch
- Pull requests (analysis only, no email)

### Step 3: Monitor Emails

After each workflow run:
1. Check your email inbox
2. Email will include full analysis report
3. Click workflow link to see full GitHub Actions logs

---

## Local Usage

### Python Script

#### Prerequisites
```bash
pip install requests
```

#### Setup Environment Variables

**Linux/macOS:**
```bash
export EMAILJS_SERVICE_ID="service_xxxxx"
export EMAILJS_TEMPLATE_ID="template_xxxxx"
export EMAILJS_USER_ID="user_xxxxx"
export EMAILJS_PRIVATE_KEY="your_private_key"
export EMAILJS_RECIPIENT="your-email@example.com"
```

**Windows (PowerShell):**
```powershell
$env:EMAILJS_SERVICE_ID="service_xxxxx"
$env:EMAILJS_TEMPLATE_ID="template_xxxxx"
$env:EMAILJS_USER_ID="user_xxxxx"
$env:EMAILJS_PRIVATE_KEY="your_private_key"
$env:EMAILJS_RECIPIENT="your-email@example.com"
```

#### Run the Script

```bash
# Using default report path (reports/cppcheck_analysis_report.txt)
python3 scripts/send_email_report_py.py

# Using custom report path
python3 scripts/send_email_report_py.py --report ./custom_report.txt

# Using custom recipient
python3 scripts/send_email_report_py.py --to custom@example.com
```

### Node.js Script

#### Prerequisites
```bash
npm install
```

#### Setup Environment Variables

Same as Python script (see above)

#### Run the Script

```bash
node scripts/send_email_report.js
```

---

## Environment Variables

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `EMAILJS_SERVICE_ID` | SMTP Service ID | `service_a1b2c3d4e5f6g7h8` |
| `EMAILJS_TEMPLATE_ID` | Email Template ID | `template_x1y2z3a4b5c6d7e8f` |
| `EMAILJS_USER_ID` | EmailJS Account User ID | `a1b2c3d4e5f6g7h8i9j0k1l2` |
| `EMAILJS_PRIVATE_KEY` | EmailJS API Private Key | `abc123def456ghi789jkl012` |
| `EMAILJS_RECIPIENT` | Recipient email address | `your-email@example.com` |

### Optional Variables

- `EMAILJS_PROJECT_NAME` - Project name in email (default: "Simple Webserver")

---

## Workflow Files

### Automatic Email on Main Branch Push

The workflow automatically sends email when:
1. You push to the `main` branch
2. You manually trigger with `workflow_dispatch`

### Manual Trigger

1. Go to GitHub repository
2. Click **Actions** tab
3. Select **MISRA Compliance CI**
4. Click **Run workflow**
5. Choose branch and click **Run workflow**

---

## Troubleshooting

### Email Not Sending

**Check 1: Verify credentials**
```bash
# Python
python3 -c "import os; print('Service:', os.getenv('EMAILJS_SERVICE_ID', 'NOT SET'))"

# Bash
echo "Service: $EMAILJS_SERVICE_ID"
```

**Check 2: Verify EmailJS API status**
- Visit [status.emailjs.com](https://status.emailjs.com/)
- Ensure API is operational

**Check 3: Check report file exists**
```bash
ls -la reports/cppcheck_analysis_report.txt
```

**Check 4: Review GitHub Actions logs**
1. Go to your repository
2. Click **Actions** tab
3. Select the failed workflow
4. Check "Send email via EmailJS" step logs

### Report Not Including Content

1. Verify report was generated: `ls reports/`
2. Check report size: `wc -c reports/cppcheck_analysis_report.txt`
3. If report > 8MB, consider sending summary only

### Template Issues

1. Verify template ID is correct
2. Check template variables match those in script
3. Visit EmailJS dashboard to test template

---

## Security Best Practices

1. **Never commit secrets** to repository
2. **Use GitHub Secrets** for all credentials
3. **Rotate private keys** periodically
4. **Restrict email recipients** to authorized users
5. **Monitor email activity** in EmailJS dashboard

---

## Support

For issues with:
- **EmailJS**: Visit [emailjs.com/docs](https://www.emailjs.com/docs/)
- **GitHub Actions**: Visit [github.com/actions/docs](https://docs.github.com/en/actions)
- **This project**: Check the project README

---

## Example Output

### Python Script Output
```
============================================================
CPPCHECK ANALYSIS REPORT EMAIL SENDER
============================================================

============================================================
Validating EmailJS Configuration...
============================================================
[OK] All required credentials configured

============================================================
Reading cppcheck Analysis Report...
============================================================
[OK] Report loaded (12543 bytes)
[OK] Lines: 127

============================================================
Parsing Report Summary...
============================================================
[OK] Summary extracted:
     - Total Issues: 80
     - Misra Violations: 74
     - Errors: 1
     - Warnings: 0
     - Portability Issues: 1
     - Style Issues: 4

============================================================
Sending Email via EmailJS...
============================================================
[INFO] Connecting to EmailJS API...
[OK] Email sent successfully!
[INFO] Recipient: your-email@example.com
[INFO] Status: FAIL - 80 Issues Found

============================================================
[SUCCESS] REPORT SENT VIA EMAIL
============================================================
```

### Received Email Example
```
From: noreply@emailjs.com
To: your-email@example.com
Subject: MISRA Analysis - FAIL - 80 Issues Found

Project: Simple Webserver
Status: FAIL - 80 Issues Found

ANALYSIS SUMMARY:
- Total Issues: 80
- MISRA Violations: 74
- Errors: 1
- Warnings: 0
- Portability Issues: 1
- Style Issues: 4

Generated: 2026-04-09 17:47:07 UTC
...
[Full report content follows]
```

---

## License

These scripts are part of the Simple Webserver project.
