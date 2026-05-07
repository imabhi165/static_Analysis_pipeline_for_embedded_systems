#!/bin/bash

# ========================================================================
# Email Report Sender Script
# 
# Send cppcheck analysis report via EmailJS
# Usage: ./scripts/send_report.sh [--report <path>] [--to <email>]
# 
# Environment variables required:
#   EMAILJS_SERVICE_ID
#   EMAILJS_TEMPLATE_ID
#   EMAILJS_USER_ID
#   EMAILJS_PRIVATE_KEY
#   EMAILJS_RECIPIENT (optional, can be overridden with --to)
# ========================================================================

set -e

# Load .env file if present
DOTENV_PATH="${PWD}/.env"
if [ -f "$DOTENV_PATH" ]; then
    echo "[INFO] Loading environment variables from .env"
    # shellcheck disable=SC1091
    set -o allexport
    source "$DOTENV_PATH"
    set +o allexport
fi

# Configuration
REPORT_PATH="./reports/cppcheck_analysis_report.txt"
TO_EMAIL="${EMAILJS_RECIPIENT:-}"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --report)
            REPORT_PATH="$2"
            shift 2
            ;;
        --to)
            TO_EMAIL="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Helper functions
print_header() {
    echo ""
    echo -e "${BLUE}============================================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}============================================================${NC}"
    echo ""
}

print_ok() {
    echo -e "${GREEN}[OK]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

check_jq() {
    if ! command -v jq >/dev/null 2>&1; then
        print_info "jq is not installed. Attempting to install jq..."
        if command -v apt-get >/dev/null 2>&1; then
            sudo apt-get update -qq
            sudo apt-get install -y jq
        elif command -v yum >/dev/null 2>&1; then
            sudo yum install -y jq
        else
            print_error "jq is required but not installed. Please install jq and try again."
            exit 1
        fi

        if ! command -v jq >/dev/null 2>&1; then
            print_error "jq installation failed. Please install jq manually."
            exit 1
        fi
        print_ok "jq installed successfully"
    fi
}

# Main execution
print_header "CPPCHECK ANALYSIS REPORT EMAIL SENDER"

# Validate configuration
print_info "Validating EmailJS credentials..."

MISSING_CREDS=0
for VAR in SERVICE_ID TEMPLATE_ID USER_ID PRIVATE_KEY; do
    ENV_VAR="EMAILJS_${VAR}"
    if [ -z "${!ENV_VAR}" ]; then
        print_error "Missing: ${ENV_VAR}"
        MISSING_CREDS=1
    fi
done

if [ "$MISSING_CREDS" -eq 1 ]; then
    echo ""
    print_error "Please set the following environment variables:"
    echo "  export EMAILJS_SERVICE_ID='your_service_id'"
    echo "  export EMAILJS_TEMPLATE_ID='your_template_id'"
    echo "  export EMAILJS_USER_ID='your_user_id'"
    echo "  export EMAILJS_PRIVATE_KEY='your_private_key'"
    echo "  export EMAILJS_RECIPIENT='your-email@example.com'"
    exit 1
fi

if [ -z "$TO_EMAIL" ]; then
    print_error "Recipient email not specified. Use --to or set EMAILJS_RECIPIENT"
    exit 1
fi

print_ok "All credentials configured"
echo ""

# Check report file
print_info "Reading cppcheck analysis report..."
if [ ! -f "$REPORT_PATH" ]; then
    print_error "Report file not found: $REPORT_PATH"
    exit 1
fi

REPORT_CONTENT=$(cat "$REPORT_PATH")
REPORT_SIZE=$(wc -c < "$REPORT_PATH")

print_ok "Report loaded ($REPORT_SIZE bytes)"
lines=$(wc -l < "$REPORT_PATH")
echo -e "${BLUE}[INFO]${NC} Lines: $lines"
echo ""

# Parse summary
print_info "Parsing report summary..."

TOTAL_ISSUES=$(grep "^Total Issues Found:" "$REPORT_PATH" 2>/dev/null | awk '{print $NF}' || echo "0")
MISRA_COUNT=$(grep "^  • MISRA Violations:" "$REPORT_PATH" 2>/dev/null | grep -oE '[0-9]+$' || echo "0")
ERROR_COUNT=$(grep "^  • Errors:" "$REPORT_PATH" 2>/dev/null | grep -oE '[0-9]+$' || echo "0")
WARNING_COUNT=$(grep "^  • Warnings:" "$REPORT_PATH" 2>/dev/null | grep -oE '[0-9]+$' || echo "0")
PORTABILITY_COUNT=$(grep "^  • Portability Issues:" "$REPORT_PATH" 2>/dev/null | grep -oE '[0-9]+$' || echo "0")
STYLE_COUNT=$(grep "^  • Style Issues:" "$REPORT_PATH" 2>/dev/null | grep -oE '[0-9]+$' || echo "0")

print_ok "Summary parsed:"
echo -e "     - Total Issues: $TOTAL_ISSUES"
echo -e "     - MISRA Violations: $MISRA_COUNT"
echo -e "     - Errors: $ERROR_COUNT"
echo -e "     - Warnings: $WARNING_COUNT"
echo -e "     - Portability Issues: $PORTABILITY_COUNT"
echo -e "     - Style Issues: $STYLE_COUNT"
echo ""

# Determine status
if [ "$TOTAL_ISSUES" == "0" ] || [ -z "$TOTAL_ISSUES" ]; then
    STATUS="PASS - No Issues Found"
else
    STATUS="FAIL - ${TOTAL_ISSUES} Issues Found"
fi

# Ensure jq is available
check_jq

# Prepare base64 encoded attachment
print_info "Preparing report attachment..."
if ! command -v base64 >/dev/null 2>&1; then
    print_error "base64 command not found. This is required for file attachments."
    exit 1
fi

REPORT_B64=$(base64 -w 0 "$REPORT_PATH")
ATTACHMENT="data:text/plain;base64,${REPORT_B64}"

# Send email
print_info "Sending email via EmailJS..."

RESPONSE=$(curl -s -X POST https://api.emailjs.com/api/v1.0/email/send \
  -H 'Content-Type: application/json' \
  -d "{
    \"service_id\": \"${EMAILJS_SERVICE_ID}\",
    \"template_id\": \"${EMAILJS_TEMPLATE_ID}\",
    \"user_id\": \"${EMAILJS_USER_ID}\",
    \"accessToken\": \"${EMAILJS_PRIVATE_KEY}\",
    \"template_params\": {
      \"to_email\": \"${TO_EMAIL}\",
      \"project_name\": \"Simple Webserver\",
      \"status\": \"${STATUS}\",
      \"total_issues\": \"${TOTAL_ISSUES}\",
      \"misra_violations\": \"${MISRA_COUNT}\",
      \"errors\": \"${ERROR_COUNT}\",
      \"warnings\": \"${WARNING_COUNT}\",
      \"portability_issues\": \"${PORTABILITY_COUNT}\",
      \"style_issues\": \"${STYLE_COUNT}\",
      \"timestamp\": \"$(date '+%Y-%m-%d %H:%M:%S UTC')\",
      \"attachment\": \"${ATTACHMENT}\"
    }
  }" 2>&1)

# Check response
if echo "$RESPONSE" | jq . > /dev/null 2>&1; then
    if echo "$RESPONSE" | jq -e '.ok' > /dev/null 2>&1; then
        print_ok "Email sent successfully!"
    else
        ERROR_MSG=$(echo "$RESPONSE" | jq -r '.message // "Unknown error"' 2>/dev/null || echo "Failed to send email")
        print_error "$ERROR_MSG"
        echo ""
        print_error "Response: $RESPONSE"
        exit 1
    fi
else
    # Response might still be successful even if not JSON
if echo "$RESPONSE" | grep -qi "success\|ok\|sent\|email sent"; then
        print_ok "Email likely sent successfully"
    else
        print_error "Failed to send email"
        echo ""
        print_error "Response: $RESPONSE"
        exit 1
    fi
fi

print_ok "Recipient: $TO_EMAIL"
echo -e "${BLUE}[INFO]${NC} Status: $STATUS"
echo ""

print_header "SUCCESS - REPORT SENT VIA EMAIL"
