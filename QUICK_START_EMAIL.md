# Quick Start: Send Reports via Email

## 5-Minute Setup

### 1. Get EmailJS Credentials (2 minutes)
- Visit: https://www.emailjs.com/
- Sign up for free account
- Get these IDs from dashboard:
  - **User ID**
  - **Service ID** (create Email Service in dashboard)
  - **Template ID** (create Email Template in dashboard)
  - **Private Key** (from Account settings)

### 2. Set Environment Variables (1 minute)

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
$env:EMAILJS_SERVICE_ID = "service_xxxxx"
$env:EMAILJS_TEMPLATE_ID = "template_xxxxx"
$env:EMAILJS_USER_ID = "user_xxxxx"
$env:EMAILJS_PRIVATE_KEY = "your_private_key"
$env:EMAILJS_RECIPIENT = "your-email@example.com"
```

### 3. Run Report Generation (1-2 minutes)
```bash
python3 scripts/test.py
```

### 4. Send Report via Email

**Option A: Python Script** (recommended)
```bash
python3 scripts/send_email_report_py.py
```

**Option B: Bash Script**
```bash
bash scripts/send_report.sh
```

**Option C: Node.js Script**
```bash
node scripts/send_email_report.js
```

## GitHub Actions (Automated)

### 1. Add Secrets to Repository

Go to: **Settings** > **Secrets and variables** > **Actions** > **New repository secret**

Add:
- `EMAILJS_SERVICE_ID`
- `EMAILJS_TEMPLATE_ID`
- `EMAILJS_USER_ID`
- `EMAILJS_PRIVATE_KEY`
- `EMAILJS_RECIPIENT`

### 2. Trigger Workflow

**Option A: Push to main branch**
```bash
git push origin main
```

**Option B: Manual trigger**
- Go to **Actions** tab
- Select **MISRA Compliance CI**
- Click **Run workflow**

**Option C: Pull request** (analysis only, no email)
```bash
git push origin feature-branch
# Create PR to main
```

## Email Template Example

Create a template with these variables in EmailJS dashboard:

```
Subject: MISRA Analysis Report - {{status}}

Project: {{project_name}}
Status: {{status}}

Summary:
- Total Issues: {{total_issues}}
- MISRA Violations: {{misra_violations}}
- Errors: {{errors}}
- Warnings: {{warnings}}
- Portability Issues: {{portability_issues}}
- Style Issues: {{style_issues}}

Report:
{{report_content}}
```

## Troubleshooting

### Email not sending?

1. **Check credentials:**
   ```bash
   echo $EMAILJS_SERVICE_ID
   echo $EMAILJS_RECIPIENT
   ```

2. **Check report exists:**
   ```bash
   ls -la reports/cppcheck_analysis_report.txt
   cat reports/cppcheck_analysis_report.txt | head -20
   ```

3. **Test with debug mode:**
   ```bash
   bash -x scripts/send_report.sh
   ```

4. **Check EmailJS API:**
   - Visit: https://status.emailjs.com/
   - Verify API is operational

5. **Review GitHub Actions logs:**
   - Go to **Actions** > **MISRA Compliance CI**
   - Select most recent run
   - Click "Send email via EmailJS" step
   - Check output for errors

## Files Created

| File | Purpose | Usage |
|------|---------|-------|
| `.github/workflows/misra_ci.yml` | GitHub Actions workflow | Automatically sends email on push/PR |
| `scripts/send_email_report_py.py` | Python email sender | Local: `python3 scripts/send_email_report_py.py` |
| `scripts/send_email_report.js` | Node.js email sender | Local: `node scripts/send_email_report.js` |
| `scripts/send_report.sh` | Bash email sender | Local: `bash scripts/send_report.sh` |
| `EMAIL_SETUP.md` | Full setup guide | Reference: comprehensive instructions |

## Next Steps

1. ✅ Set up EmailJS account
2. ✅ Add GitHub Secrets
3. ✅ Push to main branch (triggers email)
4. ✅ Check email inbox
5. 📧 **Done!** Automated reports working

## Support

- **EmailJS Issues**: https://www.emailjs.com/docs/
- **GitHub Actions Issues**: https://docs.github.com/en/actions
- **This Project**: See EMAIL_SETUP.md for detailed guide

---

**All YAML updated! All scripts created! Ready to send reports! 📧**
