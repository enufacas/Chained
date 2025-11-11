#!/usr/bin/env python3
"""
Security Monitoring Script - Created by Katie Moussouris (monitor-champion)

This script performs comprehensive security monitoring checks on the Chained repository.
It checks for common security issues, validates configurations, and generates a security report.

Usage:
    python3 tools/security-monitor.py [--verbose] [--json]
"""

import os
import sys
import json
import yaml
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple

class SecurityMonitor:
    """
    Comprehensive security monitoring for the Chained repository.
    Focuses on proactive detection and alerting.
    """
    
    def __init__(self, verbose=False):
        self.verbose = verbose
        self.findings = []
        self.repo_root = Path.cwd()
        
    def log(self, message, level="INFO"):
        """Log a message if verbose mode is enabled."""
        if self.verbose:
            print(f"[{level}] {message}")
    
    def add_finding(self, category, severity, title, description, location=None):
        """Add a security finding to the report."""
        finding = {
            "category": category,
            "severity": severity,
            "title": title,
            "description": description,
            "location": location,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        self.findings.append(finding)
        self.log(f"[{severity}] {title}: {description}", severity)
    
    def check_hardcoded_secrets(self):
        """Check for potential hardcoded secrets in code files."""
        self.log("Checking for hardcoded secrets...")
        
        # Patterns that might indicate hardcoded secrets
        secret_patterns = [
            (r'(?i)(password|passwd|pwd)\s*=\s*["\'](?!.*\$\{)(.{3,})["\']', 'Hardcoded Password'),
            (r'(?i)(api[_-]?key|apikey)\s*=\s*["\'](?!.*\$\{)(.{10,})["\']', 'Hardcoded API Key'),
            (r'(?i)(secret[_-]?key|secretkey)\s*=\s*["\'](?!.*\$\{)(.{10,})["\']', 'Hardcoded Secret Key'),
            (r'(?i)(token|auth[_-]?token)\s*=\s*["\'](?!.*\$\{)(.{10,})["\']', 'Hardcoded Token'),
            (r'(?i)(aws[_-]?access[_-]?key|aws[_-]?secret)\s*=\s*["\'](.{10,})["\']', 'AWS Credential'),
        ]
        
        # Check Python files
        for py_file in self.repo_root.rglob("*.py"):
            if '.git' in str(py_file) or 'venv' in str(py_file):
                continue
                
            try:
                with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    for pattern, secret_type in secret_patterns:
                        matches = re.finditer(pattern, content)
                        for match in matches:
                            # Skip if it's in a comment or test file
                            line_start = content.rfind('\n', 0, match.start()) + 1
                            line = content[line_start:content.find('\n', match.start())]
                            if line.strip().startswith('#') or 'test' in str(py_file).lower():
                                continue
                            
                            self.add_finding(
                                "Secrets Management",
                                "HIGH",
                                f"Potential {secret_type} Found",
                                f"Found what appears to be a hardcoded {secret_type.lower()}. Consider using environment variables or a secrets management system.",
                                str(py_file.relative_to(self.repo_root))
                            )
            except Exception as e:
                self.log(f"Error checking {py_file}: {e}", "WARNING")
    
    def check_file_permissions(self):
        """Check for overly permissive file permissions."""
        self.log("Checking file permissions...")
        
        sensitive_files = [
            '.github/workflows/*.yml',
            'tools/*.py',
            '*.sh'
        ]
        
        for pattern in sensitive_files:
            for file_path in self.repo_root.glob(pattern):
                if file_path.is_file():
                    mode = file_path.stat().st_mode
                    # Check if file is world-writable (uncommon in repos but good to check)
                    if mode & 0o002:
                        self.add_finding(
                            "Access Control",
                            "MEDIUM",
                            "World-Writable File",
                            f"File has world-writable permissions, which could be a security risk.",
                            str(file_path.relative_to(self.repo_root))
                        )
    
    def check_workflow_security(self):
        """Check GitHub Actions workflows for security issues."""
        self.log("Checking GitHub Actions workflows...")
        
        workflow_dir = self.repo_root / '.github' / 'workflows'
        if not workflow_dir.exists():
            return
        
        for workflow_file in workflow_dir.glob('*.yml'):
            try:
                with open(workflow_file, 'r') as f:
                    workflow = yaml.safe_load(f)
                
                # Check for pull_request_target with checkout
                if 'on' in workflow:
                    triggers = workflow['on']
                    if isinstance(triggers, dict) and 'pull_request_target' in triggers:
                        jobs = workflow.get('jobs', {})
                        for job_name, job_config in jobs.items():
                            steps = job_config.get('steps', [])
                            has_checkout = any('checkout' in str(step).lower() for step in steps)
                            if has_checkout:
                                self.add_finding(
                                    "Workflow Security",
                                    "HIGH",
                                    "Potential pull_request_target Risk",
                                    f"Workflow uses pull_request_target with checkout, which can be dangerous. Review carefully to ensure untrusted code isn't executed.",
                                    str(workflow_file.relative_to(self.repo_root))
                                )
                
                # Check for actions without version pinning
                jobs = workflow.get('jobs', {})
                for job_name, job_config in jobs.items():
                    steps = job_config.get('steps', [])
                    for step in steps:
                        if isinstance(step, dict) and 'uses' in step:
                            action = step['uses']
                            # Check if action uses @main or @master instead of pinned version
                            if '@main' in action or '@master' in action:
                                self.add_finding(
                                    "Workflow Security",
                                    "LOW",
                                    "Unpinned Action Version",
                                    f"Action uses @main or @master instead of a pinned version: {action}. Consider pinning to a specific commit SHA for better security.",
                                    str(workflow_file.relative_to(self.repo_root))
                                )
                        
            except Exception as e:
                self.log(f"Error checking workflow {workflow_file}: {e}", "WARNING")
    
    def check_dependency_security(self):
        """Check for known vulnerable dependencies."""
        self.log("Checking dependencies...")
        
        # Check requirements.txt
        req_file = self.repo_root / 'requirements.txt'
        if req_file.exists():
            with open(req_file, 'r') as f:
                requirements = f.read()
                
            # Check for unpinned dependencies
            for line in requirements.split('\n'):
                line = line.strip()
                if line and not line.startswith('#'):
                    if '>=' in line or '>' in line or '~=' in line:
                        self.add_finding(
                            "Dependency Management",
                            "MEDIUM",
                            "Unpinned Dependency",
                            f"Dependency uses flexible version constraint: {line}. Consider pinning to specific versions for better security and reproducibility.",
                            "requirements.txt"
                        )
    
    def check_input_validation(self):
        """Check for potential input validation issues in Python files."""
        self.log("Checking input validation...")
        
        dangerous_functions = [
            ('eval(', 'eval() function'),
            ('exec(', 'exec() function'),
            ('__import__(', '__import__() function'),
            ('compile(', 'compile() function'),
        ]
        
        for py_file in self.repo_root.rglob("*.py"):
            if '.git' in str(py_file) or 'venv' in str(py_file):
                continue
                
            try:
                with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    for func, func_name in dangerous_functions:
                        if func in content:
                            # Check if it's not in a comment
                            for line_num, line in enumerate(content.split('\n'), 1):
                                if func in line and not line.strip().startswith('#'):
                                    self.add_finding(
                                        "Input Validation",
                                        "HIGH",
                                        f"Dangerous Function: {func_name}",
                                        f"Use of {func_name} can lead to code injection vulnerabilities. Ensure input is properly validated and sanitized.",
                                        f"{py_file.relative_to(self.repo_root)}:{line_num}"
                                    )
            except Exception as e:
                self.log(f"Error checking {py_file}: {e}", "WARNING")
    
    def check_data_integrity(self):
        """Check for potential data integrity issues."""
        self.log("Checking data integrity...")
        
        # Check JSON files for validity
        for json_file in self.repo_root.rglob("*.json"):
            if '.git' in str(json_file):
                continue
                
            try:
                with open(json_file, 'r') as f:
                    json.load(f)
            except json.JSONDecodeError as e:
                self.add_finding(
                    "Data Integrity",
                    "MEDIUM",
                    "Invalid JSON File",
                    f"JSON file has syntax errors: {e}",
                    str(json_file.relative_to(self.repo_root))
                )
            except Exception as e:
                self.log(f"Error checking {json_file}: {e}", "WARNING")
    
    def generate_report(self, output_format='text'):
        """Generate a security monitoring report."""
        if output_format == 'json':
            return json.dumps({
                'timestamp': datetime.utcnow().isoformat() + "Z",
                'total_findings': len(self.findings),
                'findings': self.findings
            }, indent=2)
        
        # Text format
        report = []
        report.append("=" * 80)
        report.append("🔐 SECURITY MONITORING REPORT - Katie Moussouris (monitor-champion)")
        report.append("=" * 80)
        report.append(f"Generated: {datetime.utcnow().isoformat()}Z")
        report.append(f"Total Findings: {len(self.findings)}")
        report.append("")
        
        # Group by severity
        by_severity = {'HIGH': [], 'MEDIUM': [], 'LOW': []}
        for finding in self.findings:
            severity = finding['severity']
            if severity in by_severity:
                by_severity[severity].append(finding)
        
        for severity in ['HIGH', 'MEDIUM', 'LOW']:
            findings_list = by_severity[severity]
            if findings_list:
                report.append(f"\n{severity} SEVERITY ({len(findings_list)} findings)")
                report.append("-" * 80)
                for finding in findings_list:
                    report.append(f"\n📍 {finding['title']}")
                    report.append(f"   Category: {finding['category']}")
                    if finding['location']:
                        report.append(f"   Location: {finding['location']}")
                    report.append(f"   {finding['description']}")
        
        if not self.findings:
            report.append("\n✅ No security issues detected! Great job keeping the codebase secure.")
        
        report.append("\n" + "=" * 80)
        report.append("End of Security Report")
        report.append("=" * 80)
        
        return "\n".join(report)
    
    def run_all_checks(self):
        """Run all security monitoring checks."""
        print("🔐 Starting Security Monitoring...")
        print("Performing comprehensive security checks...\n")
        
        self.check_hardcoded_secrets()
        self.check_file_permissions()
        self.check_workflow_security()
        self.check_dependency_security()
        self.check_input_validation()
        self.check_data_integrity()
        
        print("\n✅ Security monitoring complete!")
        return self.generate_report()

def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Security Monitoring Script by Katie Moussouris (monitor-champion)"
    )
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Enable verbose output')
    parser.add_argument('--json', action='store_true',
                        help='Output in JSON format')
    
    args = parser.parse_args()
    
    monitor = SecurityMonitor(verbose=args.verbose)
    report = monitor.run_all_checks()
    
    print("\n" + report)
    
    # Return exit code based on findings
    if monitor.findings:
        critical_findings = [f for f in monitor.findings if f['severity'] == 'HIGH']
        if critical_findings:
            return 2  # Critical issues found
        return 1  # Non-critical issues found
    return 0  # No issues

if __name__ == '__main__':
    sys.exit(main())
