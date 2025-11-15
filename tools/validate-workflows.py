#!/usr/bin/env python3
"""
Workflow Validation Tool

Validates GitHub Actions workflows to prevent common issues that lead to workflow failures.
This tool checks for:
- YAML syntax errors
- Prohibited patterns (direct push to main)
- Required workflow structure
- Common misconfigurations

Used by PR checks to ensure workflow changes are valid before merging.
"""

import sys
import yaml
import re
from pathlib import Path
from typing import List, Dict, Tuple, Any


class WorkflowValidationError(Exception):
    """Custom exception for workflow validation errors."""
    pass


class WorkflowValidator:
    """Validates GitHub Actions workflow files."""
    
    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []
        
        # Prohibited patterns
        self.prohibited_patterns = [
            {
                'pattern': r'^\s*git\s+push\s*$',
                'message': 'Direct "git push" without branch specification is prohibited. Use PR-based workflow pattern.',
                'severity': 'error'
            },
            {
                'pattern': r'^\s*git\s+push\s+origin\s+main\s*$',
                'message': 'Direct push to main branch is prohibited. Use PR-based workflow pattern.',
                'severity': 'error'
            },
            {
                'pattern': r'^\s*git\s+push\s+origin\s+\$\{\{\s*github\.ref\s*\}\}\s*$',
                'message': 'Push to current ref (which may be main) is risky. Use PR-based workflow pattern.',
                'severity': 'warning'
            }
        ]
    
    def validate_file(self, filepath: Path) -> bool:
        """
        Validate a single workflow file.
        
        Args:
            filepath: Path to the workflow YAML file
            
        Returns:
            True if validation passes, False otherwise
        """
        try:
            # Read file content
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Validate YAML syntax
            try:
                workflow = yaml.safe_load(content)
            except yaml.YAMLError as e:
                self.errors.append(f"YAML syntax error in {filepath.name}: {e}")
                return False
            
            # Validate workflow structure
            if not isinstance(workflow, dict):
                self.errors.append(f"Workflow {filepath.name} must be a YAML object")
                return False
            
            # Check for required fields
            self._validate_structure(workflow, filepath.name)
            
            # Check for prohibited patterns in the raw content
            self._check_prohibited_patterns(content, filepath.name)
            
            # Check for PR-based workflow best practices
            self._check_pr_workflow_pattern(content, filepath.name)
            
            return len(self.errors) == 0
            
        except Exception as e:
            self.errors.append(f"Unexpected error validating {filepath.name}: {e}")
            return False
    
    def _validate_structure(self, workflow: Dict, filename: str) -> None:
        """Validate basic workflow structure."""
        # Check for name
        if 'name' not in workflow:
            self.warnings.append(f"{filename}: Missing 'name' field")
        
        # Check for trigger (on key - may be parsed as True by YAML)
        has_trigger = 'on' in workflow or True in workflow
        if not has_trigger:
            self.errors.append(f"{filename}: Missing 'on' trigger field")
        
        # Check for jobs
        if 'jobs' not in workflow:
            self.errors.append(f"{filename}: Missing 'jobs' field")
        elif not isinstance(workflow['jobs'], dict):
            self.errors.append(f"{filename}: 'jobs' must be an object")
        elif len(workflow['jobs']) == 0:
            self.errors.append(f"{filename}: No jobs defined")
    
    def _check_prohibited_patterns(self, content: str, filename: str) -> None:
        """Check for prohibited patterns in workflow content."""
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, start=1):
            for pattern_check in self.prohibited_patterns:
                if re.search(pattern_check['pattern'], line, re.IGNORECASE):
                    message = f"{filename}:{line_num}: {pattern_check['message']}"
                    message += f"\n  Found: {line.strip()}"
                    
                    if pattern_check['severity'] == 'error':
                        self.errors.append(message)
                    else:
                        self.warnings.append(message)
    
    def _check_pr_workflow_pattern(self, content: str, filename: str) -> None:
        """Check if workflow uses PR-based pattern when committing changes."""
        # Check if workflow commits changes
        has_git_commit = 'git commit' in content
        has_git_push = 'git push' in content
        
        if has_git_commit and has_git_push:
            # Check if it uses PR-based pattern
            has_gh_pr_create = 'gh pr create' in content
            has_branch_checkout = 'git checkout -b' in content
            
            if not (has_gh_pr_create and has_branch_checkout):
                self.warnings.append(
                    f"{filename}: Workflow commits and pushes changes but doesn't use "
                    "PR-based workflow pattern (gh pr create + branch checkout)"
                )
    
    def validate_directory(self, dirpath: Path) -> Tuple[int, int]:
        """
        Validate all workflow files in a directory.
        
        Args:
            dirpath: Path to directory containing workflow files
            
        Returns:
            Tuple of (passed_count, failed_count)
        """
        workflow_files = list(dirpath.glob('*.yml')) + list(dirpath.glob('*.yaml'))
        
        if not workflow_files:
            print(f"No workflow files found in {dirpath}")
            return 0, 0
        
        passed = 0
        failed = 0
        
        for filepath in sorted(workflow_files):
            if self.validate_file(filepath):
                passed += 1
            else:
                failed += 1
        
        return passed, failed
    
    def get_report(self) -> str:
        """Get a formatted validation report."""
        report = []
        
        if self.errors:
            report.append("❌ Validation Errors:")
            for error in self.errors:
                report.append(f"  {error}")
        
        if self.warnings:
            report.append("\n⚠️  Warnings:")
            for warning in self.warnings:
                report.append(f"  {warning}")
        
        if not self.errors and not self.warnings:
            report.append("✅ All validations passed!")
        
        return "\n".join(report)


def validate_changed_workflows(changed_files: List[str]) -> bool:
    """
    Validate only the changed workflow files.
    
    Args:
        changed_files: List of changed file paths
        
    Returns:
        True if all validations pass, False otherwise
    """
    validator = WorkflowValidator()
    
    workflow_files = [
        Path(f) for f in changed_files 
        if f.startswith('.github/workflows/') and (f.endswith('.yml') or f.endswith('.yaml'))
    ]
    
    if not workflow_files:
        print("No workflow files changed")
        return True
    
    print(f"Validating {len(workflow_files)} changed workflow file(s)...")
    
    passed = 0
    failed = 0
    
    for filepath in workflow_files:
        print(f"\n📄 Checking {filepath}...")
        if filepath.exists() and validator.validate_file(filepath):
            print(f"  ✅ Passed")
            passed += 1
        else:
            print(f"  ❌ Failed")
            failed += 1
    
    print(f"\n{'='*60}")
    print(validator.get_report())
    print(f"\n{'='*60}")
    print(f"Summary: {passed} passed, {failed} failed")
    
    return failed == 0


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Validate GitHub Actions workflow files"
    )
    parser.add_argument(
        'paths',
        nargs='*',
        help='Workflow file or directory paths to validate'
    )
    parser.add_argument(
        '--changed-files',
        help='File containing list of changed files (one per line)'
    )
    parser.add_argument(
        '--all',
        action='store_true',
        help='Validate all workflows in .github/workflows/'
    )
    
    args = parser.parse_args()
    
    # Handle --changed-files option
    if args.changed_files:
        with open(args.changed_files, 'r') as f:
            changed_files = [line.strip() for line in f if line.strip()]
        return 0 if validate_changed_workflows(changed_files) else 1
    
    # Handle --all option
    if args.all:
        workflows_dir = Path('.github/workflows')
        if not workflows_dir.exists():
            print(f"Error: Directory not found: {workflows_dir}", file=sys.stderr)
            return 1
        
        validator = WorkflowValidator()
        passed, failed = validator.validate_directory(workflows_dir)
        
        print(f"\n{'='*60}")
        print(validator.get_report())
        print(f"\n{'='*60}")
        print(f"Summary: {passed} passed, {failed} failed out of {passed + failed} workflows")
        
        return 0 if failed == 0 else 1
    
    # Handle individual paths
    if not args.paths:
        parser.print_help()
        return 1
    
    validator = WorkflowValidator()
    passed = 0
    failed = 0
    
    for path_str in args.paths:
        path = Path(path_str)
        
        if not path.exists():
            print(f"Error: Path not found: {path}", file=sys.stderr)
            failed += 1
            continue
        
        if path.is_dir():
            p, f = validator.validate_directory(path)
            passed += p
            failed += f
        else:
            if validator.validate_file(path):
                passed += 1
            else:
                failed += 1
    
    print(f"\n{'='*60}")
    print(validator.get_report())
    print(f"\n{'='*60}")
    print(f"Summary: {passed} passed, {failed} failed")
    
    return 0 if failed == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
