#!/usr/bin/env python3
"""
Send cppcheck analysis report via EmailJS

Usage:
    python3 scripts/send_email_report_py.py [--report <path>] [--to <email>]

Environment variables required:
    EMAILJS_SERVICE_ID
    EMAILJS_TEMPLATE_ID
    EMAILJS_USER_ID
    EMAILJS_PRIVATE_KEY
    EMAILJS_RECIPIENT (optional, can be overridden with --to)
"""

import os
import sys
import json
import re
import argparse
import requests
import base64
from pathlib import Path
from datetime import datetime


class EmailReportSender:
    """Send cppcheck analysis report via EmailJS"""
    
    def __init__(self, report_path=None, to_email=None):
        self.report_path = Path(report_path or "reports/cppcheck_analysis_report.txt")
        self.to_email = to_email or os.getenv("EMAILJS_RECIPIENT", "")
        
        # Load credentials from environment
        self.service_id = os.getenv("EMAILJS_SERVICE_ID", "")
        self.template_id = os.getenv("EMAILJS_TEMPLATE_ID", "")
        self.user_id = os.getenv("EMAILJS_USER_ID", "")
        self.private_key = os.getenv("EMAILJS_PRIVATE_KEY", "")
        
        self.api_url = "https://api.emailjs.com/api/v1.0/email/send"
    
    def validate_config(self) -> bool:
        """Validate EmailJS configuration"""
        print("=" * 60)
        print("Validating EmailJS Configuration...")
        print("=" * 60)
        
        required = {
            "SERVICE_ID": self.service_id,
            "TEMPLATE_ID": self.template_id,
            "USER_ID": self.user_id,
            "PRIVATE_KEY": self.private_key,
            "TO_EMAIL": self.to_email
        }
        
        missing = [key for key, value in required.items() if not value]
        
        if missing:
            print("[ERROR] Missing required configuration:")
            for key in missing:
                print(f"  - Set EMAILJS_{key} environment variable")
            return False
        
        print("[OK] All required credentials configured")
        print()
        return True
    
    def read_report(self) -> bool:
        """Read the cppcheck analysis report"""
        print("=" * 60)
        print("Reading cppcheck Analysis Report...")
        print("=" * 60)
        
        if not self.report_path.exists():
            print(f"[ERROR] Report file not found: {self.report_path}")
            return False
        
        try:
            with open(self.report_path, 'r', encoding='utf-8') as f:
                self.report_content = f.read()
            
            file_size = self.report_path.stat().st_size
            print(f"[OK] Report loaded ({file_size} bytes)")
            print(f"[OK] Lines: {len(self.report_content.splitlines())}")
            print()
            return True
        except Exception as e:
            print(f"[ERROR] Failed to read report: {e}")
            return False
    
    def parse_summary(self) -> dict:
        """Parse the report to extract summary information"""
        print("=" * 60)
        print("Parsing Report Summary...")
        print("=" * 60)
        
        summary = {
            "total_issues": "0",
            "misra_violations": "0",
            "errors": "0",
            "warnings": "0",
            "portability_issues": "0",
            "style_issues": "0"
        }
        
        patterns = {
            "total_issues": r"Total Issues Found:\s*(\d+)",
            "misra_violations": r"MISRA Violations:\s*(\d+)",
            "errors": r"Errors:\s*(\d+)",
            "warnings": r"Warnings:\s*(\d+)",
            "portability_issues": r"Portability Issues:\s*(\d+)",
            "style_issues": r"Style Issues:\s*(\d+)"
        }
        
        for key, pattern in patterns.items():
            match = re.search(pattern, self.report_content)
            if match:
                summary[key] = match.group(1)
        
        print("[OK] Summary extracted:")
        for key, value in summary.items():
            print(f"     - {key.replace('_', ' ').title()}: {value}")
        print()
        
        return summary
    
    def send_email(self, summary: dict) -> bool:
        """Send email via EmailJS API"""
        print("=" * 60)
        print("Sending Email via EmailJS...")
        print("=" * 60)
        
        # Determine status
        total = int(summary.get("total_issues", 0))
        status = "PASS - No Issues Found" if total == 0 else f"FAIL - {total} Issues Found"
        
        # Prepare base64 encoded attachment
        print("[INFO] Preparing report attachment...")
        try:
            with open(self.report_path, 'rb') as f:
                file_data = f.read()
            encoded_file = base64.b64encode(file_data).decode('utf-8')
            attachment = f"data:text/plain;base64,{encoded_file}"
        except Exception as e:
            print(f"[ERROR] Failed to encode report file: {e}")
            return False
        
        # Prepare email payload
        payload = {
            "service_id": self.service_id,
            "template_id": self.template_id,
            "user_id": self.user_id,
            "accessToken": self.private_key,
            "template_params": {
                "to_email": self.to_email,
                "project_name": "Simple Webserver",
                "status": status,
                "total_issues": summary.get("total_issues", "0"),
                "misra_violations": summary.get("misra_violations", "0"),
                "errors": summary.get("errors", "0"),
                "warnings": summary.get("warnings", "0"),
                "portability_issues": summary.get("portability_issues", "0"),
                "style_issues": summary.get("style_issues", "0"),
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC"),
                "attachment": attachment
            }
        }
        
        try:
            print("[INFO] Connecting to EmailJS API...")
            response = requests.post(
                self.api_url,
                json=payload,
                timeout=30,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                print("[OK] Email sent successfully!")
                print(f"[INFO] Recipient: {self.to_email}")
                print(f"[INFO] Status: {status}")
                print()
                return True
            else:
                print(f"[ERROR] Failed to send email (HTTP {response.status_code})")
                print(f"[ERROR] Response: {response.text}")
                print()
                return False
        
        except requests.exceptions.Timeout:
            print("[ERROR] Request timeout - EmailJS API not responding")
            print()
            return False
        except requests.exceptions.ConnectionError as e:
            print(f"[ERROR] Connection error: {e}")
            print()
            return False
        except Exception as e:
            print(f"[ERROR] Failed to send email: {e}")
            print()
            return False
    
    def run(self) -> bool:
        """Run the complete email sending process"""
        print("\n")
        print("🚀" * 15)
        print("CPPCHECK ANALYSIS REPORT EMAIL SENDER")
        print("🚀" * 15)
        print("\n")
        
        # Validate configuration
        if not self.validate_config():
            return False
        
        # Read report
        if not self.read_report():
            return False
        
        # Parse summary
        summary = self.parse_summary()
        
        # Send email
        if not self.send_email(summary):
            return False
        
        print("=" * 60)
        print("[SUCCESS] REPORT SENT VIA EMAIL")
        print("=" * 60)
        print("\n")
        
        return True


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Send cppcheck analysis report via EmailJS"
    )
    parser.add_argument(
        "--report",
        default="reports/cppcheck_analysis_report.txt",
        help="Path to cppcheck analysis report (default: reports/cppcheck_analysis_report.txt)"
    )
    parser.add_argument(
        "--to",
        dest="email",
        help="Recipient email address (overrides EMAILJS_RECIPIENT)"
    )
    
    args = parser.parse_args()
    
    # Create sender and run
    sender = EmailReportSender(report_path=args.report, to_email=args.email)
    success = sender.run()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
