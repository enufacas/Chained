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
        
        # Compile file exclusion patterns for better performance
        self._exclusion_patterns = [
            re.compile(r'test_'),
            re.compile(r'_test\.'),
            re.compile(r'/tests/'),
            re.compile(r'/examples/'),
            re.compile(r'anti[-_]pattern'),
            re.compile(r'\.min\.'),
            re.compile(r'pattern[-_]matcher'),
        ]
        
    def _load_patterns(self) -> Dict:
        """Load pattern definitions
        
        Patterns can be either:
        - line-level: checked against each line
        - file-level: checked against entire file content
        """
        return {
            'python': [
                {
                    'id': 'py-no-bare-except',
                    'name': 'Bare except clause',
                    'pattern': r'except\s*:',
                    'severity': 'warning',
                    'category': 'error-handling',
                    'suggestion': 'Use specific exception types instead of bare except:',
                    'description': 'Bare except clauses catch all exceptions including system exits',
                    'scope': 'line'
                },
                {
                    'id': 'py-print-debug',
                    'name': 'Debug print statements',
                    'pattern': r'print\s*\(["\']debug|DEBUG',
                    'severity': 'info',
                    'category': 'debugging',
                    'suggestion': 'Use logging module instead of print for debugging',
                    'description': 'Print statements for debugging should use logging',
                    'scope': 'line'
                },
                {
                    'id': 'py-todo-comment',
                    'name': 'TODO comments',
                    'pattern': r'#\s*TODO|#\s*FIXME|#\s*XXX',
                    'severity': 'info',
                    'category': 'maintenance',
                    'suggestion': 'Convert TODO comments to tracked issues',
                    'description': 'TODO comments can be forgotten',
                    'scope': 'line'
                },
                {
                    'id': 'py-hardcoded-secrets',
                    'name': 'Potential hardcoded secrets',
                    'pattern': r'(password|api_key|secret|token)\s*=\s*["\'][^"\']{10,}["\']',
                    'severity': 'error',
                    'category': 'security',
                    'suggestion': 'Use environment variables or secret management',
                    'description': 'Hardcoded secrets are a security risk',
                    'scope': 'line'
                },
                {
                    'id': 'py-sql-injection',
                    'name': 'Potential SQL injection',
                    'pattern': r'execute\s*\(\s*["\'].*%s.*["\']',
                    'severity': 'error',
                    'category': 'security',
                    'suggestion': 'Use parameterized queries instead of string formatting',
                    'description': 'String formatting in SQL queries can lead to injection',
                    'scope': 'line'
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
                    'description': 'Console.log should not be in production code',
                    'scope': 'line'
                },
                {
                    'id': 'js-var-keyword',
                    'name': 'Use of var keyword',
                    'pattern': r'\bvar\s+\w+',
                    'severity': 'warning',
                    'category': 'best-practices',
                    'suggestion': 'Use let or const instead of var',
                    'description': 'var has function scope, let/const have block scope',
                    'scope': 'line'
                },
                {
                    'id': 'js-eval-usage',
                    'name': 'Use of eval()',
                    'pattern': r'\beval\s*\(',
                    'severity': 'error',
                    'category': 'security',
                    'suggestion': 'Avoid eval() for security reasons',
                    'description': 'eval() can execute arbitrary code',
                    'scope': 'line'
                },
                {
                    'id': 'js-todo-comment',
                    'name': 'TODO comments',
                    'pattern': r'//\s*TODO|//\s*FIXME|//\s*XXX',
                    'severity': 'info',
                    'category': 'maintenance',
                    'suggestion': 'Convert TODO comments to tracked issues',
                    'description': 'TODO comments can be forgotten',
                    'scope': 'line'
                },
            ],
            'bash': [
                # Only flag truly dangerous unquoted variable patterns
                {
                    'id': 'bash-unquoted-in-single-bracket-test',
                    'name': 'Unquoted variable in single-bracket test condition',
                    'pattern': r'^\s*(?:if|while|until)?\s*\[\s+\$\w+\s+[!=<>]',
                    'severity': 'warning',
                    'category': 'best-practices',
                    'suggestion': 'Quote variables in single-bracket test conditions: [ "$var" = "value" ]',
                    'description': 'Unquoted variables in [ ] tests can cause syntax errors (double-bracket [[ ]] is OK)',
                    'scope': 'line'
                },
                {
                    'id': 'bash-unquoted-in-command',
                    'name': 'Potentially unquoted variable as command argument',
                    # Match dangerous commands with unquoted variables: rm $file, cp $src $dst, etc.
                    'pattern': r'^(rm|cp|mv|chmod|chown)\s+[^"\']*\$\w+',
                    'severity': 'info',
                    'category': 'best-practices',
                    'suggestion': 'Consider quoting variables in file operations: "$var"',
                    'description': 'Unquoted variables can cause word splitting with spaces in filenames',
                    'scope': 'line'
                },
            ],
            'bash_file': [
                # File-level checks for bash scripts
                {
                    'id': 'bash-missing-shebang',
                    'name': 'Missing shebang',
                    # Match lines that don't start with #! (after optional whitespace)
                    'pattern': r'^\s*(?!#!)',
                    'severity': 'info',
                    'category': 'portability',
                    'suggestion': 'Add shebang line (#!/bin/bash or #!/usr/bin/env bash)',
                    'description': 'Shebang ensures script runs with correct interpreter',
                    'check_first_line': True
                },
                {
                    'id': 'bash-no-set-e',
                    'name': 'Consider using set -e',
                    # Match 'set -e' command at start of line (checks if file contains this anywhere)
                    # With invert=True, flags files that DON'T have 'set -e' command
                    'pattern': r'^\s*set\s+-[a-zA-Z]*e',
                    'severity': 'info',
                    'category': 'error-handling',
                    'suggestion': 'Consider adding "set -e" near the top to exit on error',
                    'description': 'set -e makes scripts fail fast on errors (check entire file)',
                    'invert': True  # Flag if pattern NOT found
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
                    'description': 'Hardcoded secrets in YAML are a security risk',
                    'scope': 'line'
                },
                {
                    'id': 'yaml-todo-comment',
                    'name': 'TODO comments',
                    'pattern': r'#\s*TODO|#\s*FIXME|#\s*XXX',
                    'severity': 'info',
                    'category': 'maintenance',
                    'suggestion': 'Convert TODO comments to tracked issues',
                    'description': 'TODO comments can be forgotten',
                    'scope': 'line'
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
    
    def should_skip_file(self, file_path: str) -> bool:
        """Check if file should be skipped (test/example files)"""
        path_lower = file_path.lower()
        
        # Use pre-compiled patterns for performance
        for pattern in self._exclusion_patterns:
            if pattern.search(path_lower):
                return True
        
        # Check for 'example' in just the filename (optimization)
        if 'example' in path_lower.split('/')[-1]:
            return True
            
        return False
    
    def is_safe_placeholder(self, matched_text: str) -> bool:
        """Check if matched text is a safe placeholder/documentation"""
        safe_patterns = [
            r'your[-_]?(token|key|secret|password|api[-_]?key)',
            r'sk[-_]test[-_]',
            r'test[-_](token|key|secret|password)',
            r'example[-_](token|key)',
            r'export\s+(GEMINI_API_KEY|GOOGLE_API_KEY|GH_TOKEN|ANTHROPIC_API_KEY)',
            r'print\s*\(\s*["\'].*export',
        ]
        
        text_lower = matched_text.lower()
        for pattern in safe_patterns:
            if re.search(pattern, text_lower, re.IGNORECASE):
                return True
        return False
    
    def scan_file(self, file_path: str) -> List[PatternMatch]:
        """Scan a single file for pattern matches"""
        # Skip test and example files
        if self.should_skip_file(file_path):
            return []
        
        language = self.detect_language(file_path)
        if not language or language not in self.patterns:
            return []
        
        matches = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Get the content as a single string for file-level checks
            content = ''.join(lines)
            
            # Line-level pattern checks
            for line_num, line in enumerate(lines, 1):
                for pattern_def in self.patterns.get(language, []):
                    # Only check line-scoped patterns
                    if pattern_def.get('scope', 'line') != 'line':
                        continue
                        
                    if re.search(pattern_def['pattern'], line, re.IGNORECASE):
                        # Skip safe placeholders for security patterns
                        if pattern_def['category'] == 'security' and self.is_safe_placeholder(line):
                            continue
                        
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
            
            # File-level pattern checks
            file_patterns_key = f'{language}_file'
            for pattern_def in self.patterns.get(file_patterns_key, []):
                # Special handling for first-line checks
                if pattern_def.get('check_first_line'):
                    if lines and re.search(pattern_def['pattern'], lines[0].strip()):
                        match = PatternMatch(
                            pattern_id=pattern_def['id'],
                            pattern_name=pattern_def['name'],
                            severity=pattern_def['severity'],
                            file_path=file_path,
                            line_number=1,
                            matched_text=lines[0].strip() if lines else '',
                            suggestion=pattern_def['suggestion'],
                            category=pattern_def['category']
                        )
                        matches.append(match)
                # Inverted checks (flag if pattern NOT found)
                elif pattern_def.get('invert'):
                    if not re.search(pattern_def['pattern'], content, re.MULTILINE):
                        match = PatternMatch(
                            pattern_id=pattern_def['id'],
                            pattern_name=pattern_def['name'],
                            severity=pattern_def['severity'],
                            file_path=file_path,
                            line_number=1,
                            matched_text='(entire file)',
                            suggestion=pattern_def['suggestion'],
                            category=pattern_def['category']
                        )
                        matches.append(match)
                # Standard file-level check
                else:
                    for match_obj in re.finditer(pattern_def['pattern'], content, re.MULTILINE):
                        # Calculate line number from position
                        line_num = content[:match_obj.start()].count('\n') + 1
                        matched_line = lines[line_num - 1].strip() if line_num <= len(lines) else match_obj.group()
                        
                        match = PatternMatch(
                            pattern_id=pattern_def['id'],
                            pattern_name=pattern_def['name'],
                            severity=pattern_def['severity'],
                            file_path=file_path,
                            line_number=line_num,
                            matched_text=matched_line,
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
