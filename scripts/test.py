#!/usr/bin/env python3
"""
Build and Analysis Script for Tiny Webserver
This script removes build folders, builds the project with CMake,
runs cppcheck MISRA analysis, and generates reports in TXT and HTML formats.
"""

import os
import sys
import shutil
import subprocess
import json
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional

class BuildAnalyzer:
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root).resolve()
        self.build_dir = self.project_root / "build"
        self.report_dir = self.project_root / "reports"
        self.misra_report_txt = self.build_dir / "misra_report.txt"
        self.final_report_txt = self.report_dir / "cppcheck_analysis_report.txt"
        self.final_report_html = self.report_dir / "cppcheck_analysis_report.html"
        
    def remove_build_folders(self) -> None:
        """Remove build directories and reports"""
        print("=" * 60)
        print("Step 1: Removing build folders and old reports...")
        print("=" * 60)
        
        # Remove build directory
        if self.build_dir.exists():
            shutil.rmtree(self.build_dir)
            print(f"[OK] Removed build directory: {self.build_dir}")
        else:
            print(f"! Build directory not found: {self.build_dir}")
        
        # Remove reports directory
        if self.report_dir.exists():
            shutil.rmtree(self.report_dir)
            print(f"[OK] Removed reports directory: {self.report_dir}")
        else:
            print(f"! Reports directory not found: {self.report_dir}")
        
        # Remove any CMake cache files in root
        cache_files = [
            self.project_root / "CMakeCache.txt",
            self.project_root / "CMakeFiles"
        ]
        for cache in cache_files:
            if cache.exists():
                if cache.is_file():
                    cache.unlink()
                else:
                    shutil.rmtree(cache)
                print(f"[OK] Removed: {cache}")
        
        print("\n")
    
    def configure_cmake(self) -> bool:
        """Configure the CMake project"""
        print("=" * 60)
        print("Step 2: Configuring CMake project...")
        print("=" * 60)
        
        try:
            # Create build directory
            self.build_dir.mkdir(exist_ok=True)
            
            # Run CMake configuration
            cmake_cmd = [
                "cmake",
                "-S", str(self.project_root),
                "-B", str(self.build_dir),
                "-DCMAKE_EXPORT_COMPILE_COMMANDS=ON"
            ]
            
            print(f"Running: {' '.join(cmake_cmd)}")
            result = subprocess.run(
                cmake_cmd,
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                print("[ERROR] CMake configuration failed!")
                print("Error output:")
                print(result.stderr)
                return False
            
            print("[OK] CMake configuration successful")
            print("\n")
            return True
            
        except Exception as e:
            print(f"[ERROR] Exception during CMake configuration: {e}")
            return False
    
    def build_project(self) -> bool:
        """Build the project"""
        print("=" * 60)
        print("Step 3: Building the project...")
        print("=" * 60)
        
        try:
            # Run CMake build
            build_cmd = ["cmake", "--build", str(self.build_dir)]
            
            print(f"Running: {' '.join(build_cmd)}")
            result = subprocess.run(
                build_cmd,
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                print("[ERROR] Build failed!")
                print("Error output:")
                print(result.stderr)
                return False
            
            print("[OK] Build successful")
            print("\n")
            return True
            
        except Exception as e:
            print(f"[ERROR] Exception during build: {e}")
            return False
    
    def run_cppcheck_misra(self) -> bool:
        """Run cppcheck with MISRA checks"""
        print("=" * 60)
        print("Step 4: Running cppcheck with MISRA analysis...")
        print("=" * 60)
        
        # Check if cppcheck is available
        if not shutil.which("cppcheck"):
            print("[ERROR] cppcheck not found! Please install cppcheck:")
            print("  - Ubuntu/Debian: sudo apt-get install cppcheck")
            print("  - macOS: brew install cppcheck")
            print("  - Windows: choco install cppcheck")
            return False
        
        # Source and include directories
        src_dir = self.project_root / "src"
        include_dir = self.project_root / "include"
        
        if not src_dir.exists():
            print(f"[ERROR] Source directory not found: {src_dir}")
            return False
        
        # Prepare cppcheck command
        cppcheck_cmd = [
            "cppcheck",
            "--enable=all",
            "--addon=misra",
            "--std=c99",
            "--suppress=missingIncludeSystem",
            "--suppress=unmatchedSuppression",
            "--xml",  # Also generate XML for better parsing
            f"--output-file={self.misra_report_txt}",
            f"-I{include_dir}",
            str(src_dir)
        ]
        
        # XML output for better parsing
        xml_output = self.build_dir / "misra_report.xml"
        cppcheck_cmd_xml = cppcheck_cmd.copy()
        cppcheck_cmd_xml.extend(["--xml", f"--xml-version=2"])
        cppcheck_cmd_xml[cppcheck_cmd_xml.index(f"--output-file={self.misra_report_txt}")] = f"--output-file={xml_output}"
        
        print(f"Running cppcheck with MISRA rules...")
        print(f"This may take a few moments...")
        
        try:
            # Run cppcheck
            result = subprocess.run(
                cppcheck_cmd,
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            
            # Also generate XML
            subprocess.run(
                cppcheck_cmd_xml,
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            
            if self.misra_report_txt.exists():
                print(f"[OK] MISRA analysis completed")
                print(f"  Report saved to: {self.misra_report_txt}")
                print(f"  XML report saved to: {xml_output}")
                print("\n")
                return True
            else:
                print("[ERROR] MISRA analysis failed to generate report")
                return False
                
        except Exception as e:
            print(f"[ERROR] Exception during cppcheck: {e}")
            return False
    
    def parse_cppcheck_report(self) -> Dict:
        """Parse the cppcheck report and categorize issues"""
        print("=" * 60)
        print("Step 5: Parsing and analyzing cppcheck report...")
        print("=" * 60)
        
        issues = {
            "misra_violations": [],
            "errors": [],
            "warnings": [],
            "performance": [],
            "portability": [],
            "style": [],
            "information": [],
            "summary": {
                "total_issues": 0,
                "misra_count": 0,
                "error_count": 0,
                "warning_count": 0,
                "performance_count": 0,
                "portability_count": 0,
                "style_count": 0
            }
        }
        
        if not self.misra_report_txt.exists():
            print(f"[ERROR] Report file not found: {self.misra_report_txt}")
            return issues
        
        try:
            import xml.etree.ElementTree as ET
            
            # Parse XML report
            tree = ET.parse(self.misra_report_txt)
            root = tree.getroot()
            
            # Categorize each error in the XML
            for error in root.findall('.//error'):
                error_id = error.get('id', '')
                severity = error.get('severity', '')
                msg = error.get('msg', '')
                
                error_entry = f"[{error_id}] {severity.upper()}: {msg}"
                
                # Categorize based on error ID and severity
                if 'misra' in error_id.lower():
                    issues["misra_violations"].append(error_entry)
                    issues["summary"]["misra_count"] += 1
                elif severity == 'error':
                    # Detect portability issues
                    if 'uninit' in error_id.lower() or 'uninitialized' in msg.lower():
                        issues["portability"].append(error_entry)
                        issues["summary"]["portability_count"] += 1
                    else:
                        issues["errors"].append(error_entry)
                        issues["summary"]["error_count"] += 1
                elif severity == 'warning':
                    issues["warnings"].append(error_entry)
                    issues["summary"]["warning_count"] += 1
                elif severity == 'performance':
                    issues["performance"].append(error_entry)
                    issues["summary"]["performance_count"] += 1
                elif severity == 'portability':
                    issues["portability"].append(error_entry)
                    issues["summary"]["portability_count"] += 1
                elif severity == 'style':
                    issues["style"].append(error_entry)
                    issues["summary"]["style_count"] += 1
                else:
                    issues["information"].append(error_entry)
            
            # Calculate total
            issues["summary"]["total_issues"] = (
                issues["summary"]["misra_count"] +
                issues["summary"]["error_count"] +
                issues["summary"]["warning_count"] +
                issues["summary"]["performance_count"] +
                issues["summary"]["portability_count"] +
                issues["summary"]["style_count"]
            )
            
            print(f"[OK] Parsed {issues['summary']['total_issues']} total issues")
            print(f"  - MISRA Violations: {issues['summary']['misra_count']}")
            print(f"  - Errors: {issues['summary']['error_count']}")
            print(f"  - Warnings: {issues['summary']['warning_count']}")
            print(f"  - Performance: {issues['summary']['performance_count']}")
            print(f"  - Portability: {issues['summary']['portability_count']}")
            print(f"  - Style: {issues['summary']['style_count']}")
            print("\n")
            
        except Exception as e:
            print(f"[ERROR] Error parsing report: {e}")
        
        return issues
    
    def generate_txt_report(self, issues: Dict) -> None:
        """Generate a formatted text report"""
        print("=" * 60)
        print("Step 6: Generating TXT report...")
        print("=" * 60)
        
        # Create reports directory
        self.report_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        with open(self.final_report_txt, 'w', encoding='utf-8') as f:
            # Header
            f.write("=" * 80 + "\n")
            f.write("CPPCHECK MISRA ANALYSIS REPORT\n")
            f.write("=" * 80 + "\n")
            f.write(f"Generated: {timestamp}\n")
            f.write(f"Project: Tiny Webserver\n")
            f.write(f"Build Directory: {self.build_dir}\n\n")
            
            # Summary
            f.write("SUMMARY\n")
            f.write("-" * 80 + "\n")
            summary = issues["summary"]
            f.write(f"Total Issues Found: {summary['total_issues']}\n")
            f.write(f"  • MISRA Violations: {summary['misra_count']}\n")
            f.write(f"  • Errors: {summary['error_count']}\n")
            f.write(f"  • Warnings: {summary['warning_count']}\n")
            f.write(f"  • Performance Issues: {summary['performance_count']}\n")
            f.write(f"  • Portability Issues: {summary['portability_count']}\n")
            f.write(f"  • Style Issues: {summary['style_count']}\n\n")
            
            # Severity Levels
            f.write("SEVERITY LEVELS\n")
            f.write("-" * 80 + "\n")
            f.write("• CRITICAL: MISRA violations (coding standard violations)\n")
            f.write("• HIGH: Errors (definite bugs)\n")
            f.write("• MEDIUM: Warnings (potential bugs)\n")
            f.write("• LOW: Performance, Portability, Style issues\n\n")
            
            # MISRA Violations (Critical)
            if issues["misra_violations"]:
                f.write("MISRA VIOLATIONS (CRITICAL)\n")
                f.write("-" * 80 + "\n")
                for i, violation in enumerate(issues["misra_violations"], 1):
                    f.write(f"{i:3d}. {violation}\n")
                f.write("\n")
            
            # Errors (High)
            if issues["errors"]:
                f.write("ERRORS (HIGH SEVERITY)\n")
                f.write("-" * 80 + "\n")
                for i, error in enumerate(issues["errors"], 1):
                    f.write(f"{i:3d}. {error}\n")
                f.write("\n")
            
            # Warnings (Medium)
            if issues["warnings"]:
                f.write("WARNINGS (MEDIUM SEVERITY)\n")
                f.write("-" * 80 + "\n")
                for i, warning in enumerate(issues["warnings"], 1):
                    f.write(f"{i:3d}. {warning}\n")
                f.write("\n")
            
            # Performance Issues (Low)
            if issues["performance"]:
                f.write("PERFORMANCE ISSUES (LOW SEVERITY)\n")
                f.write("-" * 80 + "\n")
                for i, perf in enumerate(issues["performance"], 1):
                    f.write(f"{i:3d}. {perf}\n")
                f.write("\n")
            
            # Portability Issues (Low)
            if issues["portability"]:
                f.write("PORTABILITY ISSUES (LOW SEVERITY)\n")
                f.write("-" * 80 + "\n")
                for i, port in enumerate(issues["portability"], 1):
                    f.write(f"{i:3d}. {port}\n")
                f.write("\n")
            
            # Style Issues (Low)
            if issues["style"]:
                f.write("STYLE ISSUES (LOW SEVERITY)\n")
                f.write("-" * 80 + "\n")
                for i, style in enumerate(issues["style"], 1):
                    f.write(f"{i:3d}. {style}\n")
                f.write("\n")
            
            # Recommendations
            f.write("RECOMMENDATIONS\n")
            f.write("-" * 80 + "\n")
            if summary['misra_count'] > 0:
                f.write("• Fix all MISRA violations to ensure coding standard compliance\n")
            if summary['error_count'] > 0:
                f.write("• Address all errors as they represent definite bugs\n")
            if summary['warning_count'] > 0:
                f.write("• Review warnings to prevent potential runtime issues\n")
            if summary['performance_count'] > 0:
                f.write("• Optimize performance-critical sections\n")
            
            f.write("\n" + "=" * 80 + "\n")
            f.write("END OF REPORT\n")
            f.write("=" * 80 + "\n")
        
        print(f"[OK] TXT report generated: {self.final_report_txt}\n")
    
    def generate_html_report(self, issues: Dict) -> None:
        """Generate an HTML report with better formatting"""
        print("=" * 60)
        print("Step 7: Generating HTML report...")
        print("=" * 60)
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        summary = issues["summary"]
        
        # Calculate severity percentages
        total = summary['total_issues'] if summary['total_issues'] > 0 else 1
        critical_pct = (summary['misra_count'] / total) * 100
        high_pct = (summary['error_count'] / total) * 100
        medium_pct = (summary['warning_count'] / total) * 100
        low_pct = ((summary['performance_count'] + summary['portability_count'] + 
                   summary['style_count']) / total) * 100
        
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CPPcheck MISRA Analysis Report - Tiny Webserver</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            color: #333;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        
        .header .timestamp {{
            font-size: 0.9em;
            opacity: 0.9;
        }}
        
        .summary {{
            padding: 30px;
            background: #f8f9fa;
            border-bottom: 1px solid #e0e0e0;
        }}
        
        .summary h2 {{
            color: #667eea;
            margin-bottom: 20px;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .stat-card {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            text-align: center;
            transition: transform 0.3s;
        }}
        
        .stat-card:hover {{
            transform: translateY(-5px);
        }}
        
        .stat-number {{
            font-size: 2.5em;
            font-weight: bold;
            color: #667eea;
        }}
        
        .stat-label {{
            color: #666;
            margin-top: 10px;
            font-size: 0.9em;
        }}
        
        .severity-bars {{
            margin-top: 20px;
        }}
        
        .severity-bar {{
            margin: 10px 0;
        }}
        
        .bar-label {{
            display: inline-block;
            width: 120px;
            font-weight: bold;
        }}
        
        .bar {{
            display: inline-block;
            height: 30px;
            background: linear-gradient(90deg, #667eea, #764ba2);
            border-radius: 5px;
            color: white;
            line-height: 30px;
            padding: 0 10px;
            font-size: 0.9em;
        }}
        
        .issues-section {{
            padding: 30px;
        }}
        
        .issue-category {{
            margin-bottom: 40px;
            border: 1px solid #e0e0e0;
            border-radius: 10px;
            overflow: hidden;
        }}
        
        .category-header {{
            padding: 15px 20px;
            cursor: pointer;
            user-select: none;
            font-weight: bold;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        
        .category-header.critical {{
            background: #fee;
            color: #c00;
            border-left: 5px solid #c00;
        }}
        
        .category-header.high {{
            background: #ffe6e6;
            color: #d00;
            border-left: 5px solid #d00;
        }}
        
        .category-header.medium {{
            background: #fff3e0;
            color: #e67e22;
            border-left: 5px solid #e67e22;
        }}
        
        .category-header.low {{
            background: #e8f5e9;
            color: #27ae60;
            border-left: 5px solid #27ae60;
        }}
        
        .category-count {{
            background: rgba(0,0,0,0.1);
            padding: 2px 10px;
            border-radius: 20px;
            font-size: 0.9em;
        }}
        
        .category-content {{
            max-height: 0;
            overflow: hidden;
            transition: max-height 0.3s ease-out;
        }}
        
        .category-content.open {{
            max-height: 2000px;
            transition: max-height 0.5s ease-in;
        }}
        
        .issue-item {{
            padding: 10px 20px;
            border-bottom: 1px solid #f0f0f0;
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
            background: #fafafa;
        }}
        
        .issue-item:hover {{
            background: #f0f0f0;
        }}
        
        .recommendations {{
            background: #e8f5e9;
            padding: 20px 30px;
            border-top: 1px solid #e0e0e0;
        }}
        
        .recommendations h3 {{
            color: #27ae60;
            margin-bottom: 15px;
        }}
        
        .recommendations ul {{
            margin-left: 20px;
        }}
        
        .recommendations li {{
            margin: 10px 0;
        }}
        
        .footer {{
            background: #f8f9fa;
            padding: 20px;
            text-align: center;
            color: #666;
            font-size: 0.8em;
        }}
        
        .toggle-icon {{
            font-size: 1.2em;
        }}
        
        @media (max-width: 768px) {{
            .stats-grid {{
                grid-template-columns: 1fr;
            }}
            
            .bar-label {{
                width: 100%;
                margin-bottom: 5px;
            }}
            
            .bar {{
                width: 100%;
            }}
        }}
    </style>
    <script>
        function toggleCategory(categoryId) {{
            const content = document.getElementById(categoryId);
            const icon = document.getElementById(categoryId + '-icon');
            content.classList.toggle('open');
            icon.textContent = content.classList.contains('open') ? '▼' : '▶';
        }}
    </script>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔍 CPPcheck MISRA Analysis Report</h1>
            <div class="timestamp">Generated: {timestamp}</div>
            <div class="timestamp">Project: Tiny Webserver</div>
        </div>
        
        <div class="summary">
            <h2>Executive Summary</h2>
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-number">{summary['total_issues']}</div>
                    <div class="stat-label">Total Issues</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number" style="color: #c00;">{summary['misra_count']}</div>
                    <div class="stat-label">MISRA Violations</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number" style="color: #d00;">{summary['error_count']}</div>
                    <div class="stat-label">Errors</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number" style="color: #e67e22;">{summary['warning_count']}</div>
                    <div class="stat-label">Warnings</div>
                </div>
            </div>
            
            <div class="severity-bars">
                <h3>Severity Distribution</h3>
                <div class="severity-bar">
                    <span class="bar-label">Critical (MISRA):</span>
                    <div class="bar" style="width: {critical_pct}%; background: #c00;">{summary['misra_count']} issues ({critical_pct:.1f}%)</div>
                </div>
                <div class="severity-bar">
                    <span class="bar-label">High (Errors):</span>
                    <div class="bar" style="width: {high_pct}%; background: #d00;">{summary['error_count']} issues ({high_pct:.1f}%)</div>
                </div>
                <div class="severity-bar">
                    <span class="bar-label">Medium (Warnings):</span>
                    <div class="bar" style="width: {medium_pct}%; background: #e67e22;">{summary['warning_count']} issues ({medium_pct:.1f}%)</div>
                </div>
                <div class="severity-bar">
                    <span class="bar-label">Low (Other):</span>
                    <div class="bar" style="width: {low_pct}%; background: #27ae60;">{summary['performance_count'] + summary['portability_count'] + summary['style_count']} issues ({low_pct:.1f}%)</div>
                </div>
            </div>
        </div>
        
        <div class="issues-section">
            <h2>Detailed Analysis</h2>
"""
        
        # MISRA Violations
        if issues["misra_violations"]:
            html_content += f"""
            <div class="issue-category">
                <div class="category-header critical" onclick="toggleCategory('misra-content')">
                    <span>MISRA Violations (Critical)</span>
                    <span class="category-count">{len(issues['misra_violations'])} issues</span>
                    <span class="toggle-icon" id="misra-content-icon">▶</span>
                </div>
                <div class="category-content" id="misra-content">
                    {self._format_issues_html(issues['misra_violations'])}
                </div>
            </div>
"""
        
        # Errors
        if issues["errors"]:
            html_content += f"""
            <div class="issue-category">
                <div class="category-header high" onclick="toggleCategory('errors-content')">
                    <span>Errors (High Severity)</span>
                    <span class="category-count">{len(issues['errors'])} issues</span>
                    <span class="toggle-icon" id="errors-content-icon">▶</span>
                </div>
                <div class="category-content" id="errors-content">
                    {self._format_issues_html(issues['errors'])}
                </div>
            </div>
"""
        
        # Warnings
        if issues["warnings"]:
            html_content += f"""
            <div class="issue-category">
                <div class="category-header medium" onclick="toggleCategory('warnings-content')">
                    <span>⚠️ Warnings (Medium Severity)</span>
                    <span class="category-count">{len(issues['warnings'])} issues</span>
                    <span class="toggle-icon" id="warnings-content-icon">▶</span>
                </div>
                <div class="category-content" id="warnings-content">
                    {self._format_issues_html(issues['warnings'])}
                </div>
            </div>
"""
        
        # Performance Issues
        if issues["performance"]:
            html_content += f"""
            <div class="issue-category">
                <div class="category-header low" onclick="toggleCategory('performance-content')">
                    <span>⚡ Performance Issues (Low Severity)</span>
                    <span class="category-count">{len(issues['performance'])} issues</span>
                    <span class="toggle-icon" id="performance-content-icon">▶</span>
                </div>
                <div class="category-content" id="performance-content">
                    {self._format_issues_html(issues['performance'])}
                </div>
            </div>
"""
        
        # Portability Issues
        if issues["portability"]:
            html_content += f"""
            <div class="issue-category">
                <div class="category-header low" onclick="toggleCategory('portability-content')">
                    <span>🔄 Portability Issues (Low Severity)</span>
                    <span class="category-count">{len(issues['portability'])} issues</span>
                    <span class="toggle-icon" id="portability-content-icon">▶</span>
                </div>
                <div class="category-content" id="portability-content">
                    {self._format_issues_html(issues['portability'])}
                </div>
            </div>
"""
        
        # Style Issues
        if issues["style"]:
            html_content += f"""
            <div class="issue-category">
                <div class="category-header low" onclick="toggleCategory('style-content')">
                    <span>🎨 Style Issues (Low Severity)</span>
                    <span class="category-count">{len(issues['style'])} issues</span>
                    <span class="toggle-icon" id="style-content-icon">▶</span>
                </div>
                <div class="category-content" id="style-content">
                    {self._format_issues_html(issues['style'])}
                </div>
            </div>
"""
        
        # Recommendations
        html_content += """
        </div>
        
        <div class="recommendations">
            <h3>💡 Recommendations</h3>
            <ul>
"""
        
        if summary['misra_count'] > 0:
            html_content += "                <li>🔴 <strong>Fix all MISRA violations</strong> to ensure coding standard compliance</li>\n"
        if summary['error_count'] > 0:
            html_content += "                <li>🟠 <strong>Address all errors</strong> as they represent definite bugs that could cause crashes</li>\n"
        if summary['warning_count'] > 0:
            html_content += "                <li>🟡 <strong>Review warnings</strong> to prevent potential runtime issues and undefined behavior</li>\n"
        if summary['performance_count'] > 0:
            html_content += "                <li>🟢 <strong>Optimize performance-critical sections</strong> for better throughput</li>\n"
        if summary['portability_count'] > 0:
            html_content += "                <li>🟢 <strong>Improve portability</strong> to ensure compatibility across different platforms</li>\n"
        if summary['style_count'] > 0:
            html_content += "                <li>🟢 <strong>Address style issues</strong> for better code maintainability</li>\n"
        
        html_content += f"""
            </ul>
        </div>
        
        <div class="footer">
            <p>Generated by CPPcheck MISRA Analyzer | Build Directory: {self.build_dir}</p>
            <p>MISRA C:2012 Guidelines | C99 Standard</p>
        </div>
    </div>
</body>
</html>
"""
        
        with open(self.final_report_html, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"[OK] HTML report generated: {self.final_report_html}\n")
    
    def _format_issues_html(self, issues_list: List[str]) -> str:
        """Format issues list for HTML display"""
        html = ""
        for issue in issues_list:
            # Escape HTML special characters
            escaped_issue = issue.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            html += f'                    <div class="issue-item">{escaped_issue}</div>\n'
        return html
    
    def run_complete_analysis(self) -> bool:
        """Run the complete analysis pipeline"""
        print("\n" + "=" * 60)
        print("STARTING COMPLETE BUILD AND ANALYSIS PIPELINE")
        print("=" * 60 + "\n")
        
        start_time = datetime.now()
        
        # Step 1: Remove build folders
        self.remove_build_folders()
        
        # Step 2: Configure CMake
        if not self.configure_cmake():
            print("[ERROR] Pipeline failed at CMake configuration step")
            return False
        
        # Step 3: Build project
        if not self.build_project():
            print("[ERROR] Pipeline failed at build step")
            return False
        
        # Step 4: Run cppcheck MISRA
        if not self.run_cppcheck_misra():
            print("[ERROR] Pipeline failed at cppcheck analysis step")
            return False
        
        # Step 5: Parse report
        issues = self.parse_cppcheck_report()
        
        # Step 6: Generate TXT report
        self.generate_txt_report(issues)
        
        # Step 7: Generate HTML report
        self.generate_html_report(issues)
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        print("=" * 60)
        print("[SUCCESS] PIPELINE COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print(f"Total execution time: {duration:.2f} seconds")
        print(f"\nReports generated:")
        print(f"   - TXT Report: {self.final_report_txt}")
        print(f"   - HTML Report: {self.final_report_html}")
        print(f"\nAnalysis Summary:")
        print(f"   - Total issues found: {issues['summary']['total_issues']}")
        print(f"   - Critical issues (MISRA): {issues['summary']['misra_count']}")
        print(f"   - High severity issues: {issues['summary']['error_count']}")
        print(f"   - Medium severity issues: {issues['summary']['warning_count']}")
        
        return True

def main():
    """Main entry point"""
    # Check Python version
    if sys.version_info < (3, 6):
        print("[ERROR] Python 3.6 or higher is required")
        sys.exit(1)
    
    # Get project root (parent of scripts directory)
    script_dir = Path(__file__).parent if "__file__" in globals() else Path.cwd()
    project_root = script_dir.parent  # Go up one level to the actual project root
    
    # Create analyzer instance
    analyzer = BuildAnalyzer(project_root)
    
    # Run complete analysis
    success = analyzer.run_complete_analysis()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()