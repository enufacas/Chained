#!/usr/bin/env python3
"""
Cross-Repository Pattern Matcher for Best Practices

Analyzes code repositories to detect best practice patterns and anti-patterns
across multiple programming languages.
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict


@dataclass
class PatternMatch:
    """Represents a matched pattern in code"""
    pattern_id: str
    pattern_name: str
    severity: str  # 'info', 'warning', 'error'
    file_path: str
    line_number: int
    matched_text: str
    suggestion: str
    category: str


class PatternMatcher:
    """Cross-repository pattern matcher for best practices"""
    
    def __init__(self):
        self.patterns = self._load_patterns()
        self.matches = []
        
    def _load_patterns(self) -> Dict:
        """Load pattern definitions"""
        return {
            'python': [
                {
                    'id': 'py-no-bare-except',
                    'name': 'Bare except clause',
                    'pattern': r'except\s*:',
                    'severity': 'warning',
                    'category': 'error-handling',
                    'suggestion': 'Use specific exception types instead of bare except:',
                    'description': 'Bare except clauses catch all exceptions including system exits'
                },
                {
                    'id': 'py-print-debug',
                    'name': 'Debug print statements',
                    'pattern': r'print\s*\(["\']debug|DEBUG',
                    'severity': 'info',
                    'category': 'debugging',
                    'suggestion': 'Use logging module instead of print for debugging',
                    'description': 'Print statements for debugging should use logging'
                },
                {
                    'id': 'py-todo-comment',
                    'name': 'TODO comments',
                    'pattern': r'#\s*TODO|#\s*FIXME|#\s*XXX',
                    'severity': 'info',
                    'category': 'maintenance',
                    'suggestion': 'Convert TODO comments to tracked issues',
                    'description': 'TODO comments can be forgotten'
                },
                {
                    'id': 'py-type-hints',
                    'name': 'Missing type hints',
                    'pattern': r'def\s+\w+\s*\([^)]*\)\s*:(?!\s*-\>)',
                    'severity': 'info',
                    'category': 'type-safety',
                    'suggestion': 'Add type hints for better code clarity',
                    'description': 'Type hints improve code documentation and IDE support'
                },
                {
                    'id': 'py-hardcoded-secrets',
                    'name': 'Potential hardcoded secrets',
                    'pattern': r'(password|api_key|secret|token)\s*=\s*["\'][^"\']{10,}["\']',
                    'severity': 'error',
                    'category': 'security',
                    'suggestion': 'Use environment variables or secret management',
                    'description': 'Hardcoded secrets are a security risk'
                },
                {
                    'id': 'py-sql-injection',
                    'name': 'Potential SQL injection',
                    'pattern': r'execute\s*\(\s*["\'].*%s.*["\']',
                    'severity': 'error',
                    'category': 'security',
                    'suggestion': 'Use parameterized queries instead of string formatting',
                    'description': 'String formatting in SQL queries can lead to injection'
                },
            ],
            'javascript': [
                {
                    'id': 'js-console-log',
                    'name': 'Console.log statements',
                    'pattern': r'console\.log\s*\(',
                    'severity': 'info',
                    'category': 'debugging',
                    'suggestion': 'Remove or use proper logging framework',
                    'description': 'Console.log should not be in production code'
                },
                {
                    'id': 'js-var-keyword',
                    'name': 'Use of var keyword',
                    'pattern': r'\bvar\s+\w+',
                    'severity': 'warning',
                    'category': 'best-practices',
                    'suggestion': 'Use let or const instead of var',
                    'description': 'var has function scope, let/const have block scope'
                },
                {
                    'id': 'js-eval-usage',
                    'name': 'Use of eval()',
                    'pattern': r'\beval\s*\(',
                    'severity': 'error',
                    'category': 'security',
                    'suggestion': 'Avoid eval() for security reasons',
                    'description': 'eval() can execute arbitrary code'
                },
                {
                    'id': 'js-todo-comment',
                    'name': 'TODO comments',
                    'pattern': r'//\s*TODO|//\s*FIXME|//\s*XXX',
                    'severity': 'info',
                    'category': 'maintenance',
                    'suggestion': 'Convert TODO comments to tracked issues',
                    'description': 'TODO comments can be forgotten'
                },
                {
                    'id': 'js-equality-operator',
                    'name': 'Loose equality operator',
                    'pattern': r'[^!=]=[^=]',
                    'severity': 'warning',
                    'category': 'best-practices',
                    'suggestion': 'Use === instead of == for type-safe comparison',
                    'description': 'Loose equality can cause unexpected type coercion'
                },
            ],
            'bash': [
                {
                    'id': 'bash-unquoted-vars',
                    'name': 'Unquoted variables',
                    'pattern': r'\$\w+(?!["\'])',
                    'severity': 'warning',
                    'category': 'best-practices',
                    'suggestion': 'Quote variables to prevent word splitting',
                    'description': 'Unquoted variables can cause unexpected behavior'
                },
                {
                    'id': 'bash-missing-shebang',
                    'name': 'Missing shebang',
                    'pattern': r'^(?!#!)',
                    'severity': 'info',
                    'category': 'portability',
                    'suggestion': 'Add shebang line (#!/bin/bash)',
                    'description': 'Shebang ensures script runs with correct interpreter'
                },
                {
                    'id': 'bash-set-e',
                    'name': 'Missing set -e',
                    'pattern': r'^(?!.*set\s+-e)',
                    'severity': 'info',
                    'category': 'error-handling',
                    'suggestion': 'Add "set -e" to exit on error',
                    'description': 'set -e makes scripts fail fast on errors'
                },
            ],
            'yaml': [
                {
                    'id': 'yaml-hardcoded-secrets',
                    'name': 'Potential hardcoded secrets',
                    'pattern': r'(password|api_key|secret|token):\s*["\'][^"\']{10,}["\']',
                    'severity': 'error',
                    'category': 'security',
                    'suggestion': 'Use GitHub secrets or environment variables',
                    'description': 'Hardcoded secrets in YAML are a security risk'
                },
                {
                    'id': 'yaml-todo-comment',
                    'name': 'TODO comments',
                    'pattern': r'#\s*TODO|#\s*FIXME|#\s*XXX',
                    'severity': 'info',
                    'category': 'maintenance',
                    'suggestion': 'Convert TODO comments to tracked issues',
                    'description': 'TODO comments can be forgotten'
                },
            ]
        }
    
    def detect_language(self, file_path: str) -> Optional[str]:
        """Detect programming language from file extension"""
        ext_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.sh': 'bash',
            '.bash': 'bash',
            '.yml': 'yaml',
            '.yaml': 'yaml',
        }
        ext = Path(file_path).suffix.lower()
        return ext_map.get(ext)
    
    def scan_file(self, file_path: str) -> List[PatternMatch]:
        """Scan a single file for pattern matches"""
        language = self.detect_language(file_path)
        if not language or language not in self.patterns:
            return []
        
        matches = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
            for line_num, line in enumerate(lines, 1):
                for pattern_def in self.patterns[language]:
                    if re.search(pattern_def['pattern'], line, re.IGNORECASE):
                        match = PatternMatch(
                            pattern_id=pattern_def['id'],
                            pattern_name=pattern_def['name'],
                            severity=pattern_def['severity'],
                            file_path=file_path,
                            line_number=line_num,
                            matched_text=line.strip(),
                            suggestion=pattern_def['suggestion'],
                            category=pattern_def['category']
                        )
                        matches.append(match)
        except Exception as e:
            print(f"Error scanning {file_path}: {e}", file=sys.stderr)
        
        return matches
    
    def scan_directory(self, directory: str, recursive: bool = True) -> List[PatternMatch]:
        """Scan a directory for pattern matches"""
        all_matches = []
        
        if recursive:
            for root, dirs, files in os.walk(directory):
                # Skip hidden directories and common ignore patterns
                dirs[:] = [d for d in dirs if not d.startswith('.') 
                          and d not in ['node_modules', '__pycache__', 'venv', 'dist', 'build']]
                
                for file in files:
                    if not file.startswith('.'):
                        file_path = os.path.join(root, file)
                        matches = self.scan_file(file_path)
                        all_matches.extend(matches)
        else:
            for file in os.listdir(directory):
                file_path = os.path.join(directory, file)
                if os.path.isfile(file_path) and not file.startswith('.'):
                    matches = self.scan_file(file_path)
                    all_matches.extend(matches)
        
        return all_matches
    
    def generate_report(self, matches: List[PatternMatch], output_format: str = 'text') -> str:
        """Generate a report from pattern matches"""
        if output_format == 'json':
            return json.dumps([asdict(m) for m in matches], indent=2)
        
        # Text format
        report = []
        report.append("=" * 80)
        report.append("Cross-Repository Pattern Matcher Report")
        report.append("=" * 80)
        report.append("")
        
        if not matches:
            report.append("✅ No pattern issues found!")
            return "\n".join(report)
        
        # Group by severity
        by_severity = {'error': [], 'warning': [], 'info': []}
        for match in matches:
            by_severity[match.severity].append(match)
        
        # Summary
        report.append(f"Total Issues Found: {len(matches)}")
        report.append(f"  - Errors: {len(by_severity['error'])}")
        report.append(f"  - Warnings: {len(by_severity['warning'])}")
        report.append(f"  - Info: {len(by_severity['info'])}")
        report.append("")
        
        # Detailed findings by severity
        for severity in ['error', 'warning', 'info']:
            severity_matches = by_severity[severity]
            if not severity_matches:
                continue
            
            icon = {'error': '❌', 'warning': '⚠️', 'info': 'ℹ️'}[severity]
            report.append("-" * 80)
            report.append(f"{icon} {severity.upper()} ({len(severity_matches)})")
            report.append("-" * 80)
            report.append("")
            
            # Group by category
            by_category = {}
            for match in severity_matches:
                if match.category not in by_category:
                    by_category[match.category] = []
                by_category[match.category].append(match)
            
            for category, cat_matches in sorted(by_category.items()):
                report.append(f"Category: {category.upper()}")
                report.append("")
                
                for match in cat_matches:
                    report.append(f"  [{match.pattern_id}] {match.pattern_name}")
                    report.append(f"  File: {match.file_path}:{match.line_number}")
                    report.append(f"  Code: {match.matched_text}")
                    report.append(f"  💡 {match.suggestion}")
                    report.append("")
        
        report.append("=" * 80)
        
        return "\n".join(report)
    
    def get_statistics(self, matches: List[PatternMatch]) -> Dict:
        """Get statistics about pattern matches"""
        stats = {
            'total_issues': len(matches),
            'by_severity': {'error': 0, 'warning': 0, 'info': 0},
            'by_category': {},
            'by_file': {},
            'by_pattern': {}
        }
        
        for match in matches:
            # Count by severity
            stats['by_severity'][match.severity] += 1
            
            # Count by category
            if match.category not in stats['by_category']:
                stats['by_category'][match.category] = 0
            stats['by_category'][match.category] += 1
            
            # Count by file
            if match.file_path not in stats['by_file']:
                stats['by_file'][match.file_path] = 0
            stats['by_file'][match.file_path] += 1
            
            # Count by pattern
            if match.pattern_id not in stats['by_pattern']:
                stats['by_pattern'][match.pattern_id] = 0
            stats['by_pattern'][match.pattern_id] += 1
        
        return stats


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Cross-Repository Pattern Matcher for Best Practices',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Scan a single file
  %(prog)s -f script.py
  
  # Scan a directory recursively
  %(prog)s -d /path/to/repo
  
  # Scan current directory, output as JSON
  %(prog)s -d . --format json
  
  # Save report to file
  %(prog)s -d . -o report.txt
  
  # Show statistics only
  %(prog)s -d . --stats
        """
    )
    
    parser.add_argument('-f', '--file', help='File to scan')
    parser.add_argument('-d', '--directory', help='Directory to scan')
    parser.add_argument('-r', '--recursive', action='store_true', default=True,
                       help='Scan directories recursively (default: True)')
    parser.add_argument('--format', choices=['text', 'json'], default='text',
                       help='Output format (default: text)')
    parser.add_argument('-o', '--output', help='Output file (default: stdout)')
    parser.add_argument('--stats', action='store_true',
                       help='Show statistics only')
    
    args = parser.parse_args()
    
    # Validate arguments
    if not args.file and not args.directory:
        args.directory = '.'  # Default to current directory
    
    # Create matcher
    matcher = PatternMatcher()
    
    # Scan files
    matches = []
    if args.file:
        matches = matcher.scan_file(args.file)
    elif args.directory:
        matches = matcher.scan_directory(args.directory, args.recursive)
    
    # Generate output
    if args.stats:
        stats = matcher.get_statistics(matches)
        output = json.dumps(stats, indent=2)
    else:
        output = matcher.generate_report(matches, args.format)
    
    # Write output
    if args.output:
        with open(args.output, 'w') as f:
            f.write(output)
        print(f"Report written to {args.output}")
    else:
        print(output)
    
    # Exit with appropriate code
    error_count = sum(1 for m in matches if m.severity == 'error')
    sys.exit(1 if error_count > 0 else 0)


if __name__ == '__main__':
    main()
