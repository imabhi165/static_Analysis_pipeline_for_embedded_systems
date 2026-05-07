#!/usr/bin/env node

/**
 * @file    send_email_report.js
 * @brief   Send cppcheck analysis report via EmailJS
 * @note    Run with: node scripts/send_email_report.js
 */

const fs = require('fs');
const path = require('path');
const https = require('https');

// Configuration
const CONFIG = {
    REPORT_PATH: './reports/cppcheck_analysis_report.txt',
    SERVICE_ID: process.env.EMAILJS_SERVICE_ID || '',
    TEMPLATE_ID: process.env.EMAILJS_TEMPLATE_ID || '',
    USER_ID: process.env.EMAILJS_USER_ID || '',
    PRIVATE_KEY: process.env.EMAILJS_PRIVATE_KEY || '',
    TO_EMAIL: process.env.EMAILJS_RECIPIENT || 'your-email@example.com',
};

/**
 * Read the cppcheck analysis report
 */
function readReport() {
    try {
        if (!fs.existsSync(CONFIG.REPORT_PATH)) {
            console.error(`[ERROR] Report file not found: ${CONFIG.REPORT_PATH}`);
            process.exit(1);
        }
        return fs.readFileSync(CONFIG.REPORT_PATH, 'utf-8');
    } catch (error) {
        console.error(`[ERROR] Failed to read report: ${error.message}`);
        process.exit(1);
    }
}

/**
 * Parse the report to extract summary information
 */
function parseReportSummary(reportContent) {
    const summary = {
        total_issues: '0',
        misra_violations: '0',
        errors: '0',
        warnings: '0',
        portability_issues: '0',
        style_issues: '0'
    };

    // Extract total issues
    const totalMatch = reportContent.match(/Total Issues Found:\s*(\d+)/);
    if (totalMatch) summary.total_issues = totalMatch[1];

    // Extract issue categories
    const misraMatch = reportContent.match(/MISRA Violations:\s*(\d+)/);
    if (misraMatch) summary.misra_violations = misraMatch[1];

    const errorMatch = reportContent.match(/Errors:\s*(\d+)/);
    if (errorMatch) summary.errors = errorMatch[1];

    const warningMatch = reportContent.match(/Warnings:\s*(\d+)/);
    if (warningMatch) summary.warnings = warningMatch[1];

    const portabilityMatch = reportContent.match(/Portability Issues:\s*(\d+)/);
    if (portabilityMatch) summary.portability_issues = portabilityMatch[1];

    const styleMatch = reportContent.match(/Style Issues:\s*(\d+)/);
    if (styleMatch) summary.style_issues = styleMatch[1];

    return summary;
}

/**
 * Validate configuration
 */
function validateConfig() {
    const required = ['SERVICE_ID', 'TEMPLATE_ID', 'USER_ID', 'PRIVATE_KEY'];
    const missing = required.filter(key => !CONFIG[key]);

    if (missing.length > 0) {
        console.error('[ERROR] Missing required environment variables:');
        missing.forEach(key => console.error(`  - EMAILJS_${key}`));
        console.error('\nSet them using:');
        console.error('  export EMAILJS_SERVICE_ID="your_service_id"');
        console.error('  export EMAILJS_TEMPLATE_ID="your_template_id"');
        console.error('  export EMAILJS_USER_ID="your_user_id"');
        console.error('  export EMAILJS_PRIVATE_KEY="your_private_key"');
        process.exit(1);
    }
}

/**
 * Send email via EmailJS API
 */
function sendEmail(reportPath, summary) {
    validateConfig();

    const timestamp = new Date().toISOString();
    const status = parseInt(summary.total_issues) === 0 ? 'PASS' : 'FAIL';

    // Prepare base64 encoded attachment
    console.log('[INFO] Preparing report attachment...');
    try {
        const fileBuffer = fs.readFileSync(reportPath);
        const base64Data = fileBuffer.toString('base64');
        const attachment = `data:text/plain;base64,${base64Data}`;
    } catch (error) {
        console.error(`[ERROR] Failed to encode report file: ${error.message}`);
        process.exit(1);
    }

    const emailPayload = {
        service_id: CONFIG.SERVICE_ID,
        template_id: CONFIG.TEMPLATE_ID,
        user_id: CONFIG.USER_ID,
        accessToken: CONFIG.PRIVATE_KEY,
        template_params: {
            to_email: CONFIG.TO_EMAIL,
            project_name: 'Simple Webserver',
            status: status,
            total_issues: summary.total_issues,
            misra_violations: summary.misra_violations,
            errors: summary.errors,
            warnings: summary.warnings,
            portability_issues: summary.portability_issues,
            style_issues: summary.style_issues,
            timestamp: timestamp,
            attachment: attachment
        }
    };

    const options = {
        hostname: 'api.emailjs.com',
        port: 443,
        path: '/api/v1.0/email/send',
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    };

    return new Promise((resolve, reject) => {
        const req = https.request(options, (res) => {
            let data = '';

            res.on('data', (chunk) => {
                data += chunk;
            });

            res.on('end', () => {
                if (res.statusCode === 200) {
                    resolve(data);
                } else {
                    reject(new Error(`HTTP ${res.statusCode}: ${data}`));
                }
            });
        });

        req.on('error', (error) => {
            reject(error);
        });

        req.write(JSON.stringify(emailPayload));
        req.end();
    });
}

/**
 * Main function
 */
async function main() {
    console.log('============================================================');
    console.log('CPPCHECK ANALYSIS REPORT EMAIL SENDER');
    console.log('============================================================\n');

    // Read report
    console.log('[INFO] Reading cppcheck analysis report...');
    const reportContent = readReport();
    console.log(`[OK] Report loaded (${reportContent.length} bytes)\n`);

    // Parse summary
    console.log('[INFO] Parsing report summary...');
    const summary = parseReportSummary(reportContent);
    console.log('[OK] Summary parsed:');
    console.log(`     - Total Issues: ${summary.total_issues}`);
    console.log(`     - MISRA Violations: ${summary.misra_violations}`);
    console.log(`     - Errors: ${summary.errors}`);
    console.log(`     - Warnings: ${summary.warnings}`);
    console.log(`     - Portability Issues: ${summary.portability_issues}`);
    console.log(`     - Style Issues: ${summary.style_issues}\n`);

    // Send email
    console.log('[INFO] Sending email via EmailJS...');
    try {
        await sendEmail(CONFIG.REPORT_PATH, summary);
        console.log('[SUCCESS] Email sent successfully!');
        console.log(`[INFO] Recipient: ${CONFIG.TO_EMAIL}`);
        console.log('============================================================');
        process.exit(0);
    } catch (error) {
        console.error(`[ERROR] Failed to send email: ${error.message}`);
        console.error('============================================================');
        process.exit(1);
    }
}

// Run main function
main();
