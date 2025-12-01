#!/usr/bin/env python3
"""
GCP Error Analyzer - Creates GitHub issues for GCP errors
Created by: @gcp-error-monitor agent
Part of the Chained autonomous AI ecosystem

This tool analyzes GCP Cloud Logging output and creates well-structured
GitHub issues for detected errors.

Usage:
    python3 gcp-error-analyzer.py --errors-file /tmp/gcp_errors.json
"""

import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from collections import defaultdict
from typing import Dict, List, Optional


class GCPErrorAnalyzer:
    """Analyzes GCP errors and creates GitHub issues."""
    
    # Configuration constants
    GROUPING_KEY_MAX_LENGTH = 100  # Max characters for error message grouping key
    MESSAGE_MAX_LENGTH = 500       # Max characters for error message in issue body
    ISSUE_TITLE_MAX_LENGTH = 100   # Max characters for GitHub issue title
    
    # GCP error message field locations (checked in order)
    ERROR_MESSAGE_FIELDS = [
        ('jsonPayload', 'message'),
        ('jsonPayload', 'error'),
        ('jsonPayload', 'errorMessage'),
        ('jsonPayload', 'msg'),
        ('protoPayload', 'status', 'message'),
        ('httpRequest', 'status'),
        ('textPayload', None),  # Special case: direct string
    ]
    
    def __init__(self, errors_file: str, project_id: str, dry_run: bool = False):
        self.errors_file = errors_file
        self.project_id = project_id
        self.dry_run = dry_run
        self.errors: List[Dict] = []
        self.issues_created = 0
        self.issues_skipped = 0
        
    def load_errors(self) -> bool:
        """Load errors from JSON file."""
        try:
            with open(self.errors_file, 'r') as f:
                self.errors = json.load(f)
            return True
        except (IOError, json.JSONDecodeError) as e:
            print(f"Error loading errors file: {e}")
            return False
    
    def extract_error_message(self, error: Dict) -> str:
        """Extract error message from GCP log entry, checking multiple possible fields."""
        for field_path in self.ERROR_MESSAGE_FIELDS:
            if field_path[1] is None:
                # Direct field (textPayload)
                message = error.get(field_path[0], '')
                if message:
                    return str(message)
            else:
                # Nested field - traverse path and break early if key not found
                value = error
                found = True
                try:
                    for key in field_path:
                        if key is not None and isinstance(value, dict):
                            if key not in value:
                                found = False
                                break
                            value = value[key]
                        else:
                            found = False
                            break
                    if found and value and isinstance(value, str):
                        return value
                except (TypeError, AttributeError, KeyError):
                    continue
        return ''
    
    def group_errors(self) -> Dict[str, List[Dict]]:
        """Group errors by unique signature (resource type + error message pattern)."""
        error_groups = defaultdict(list)
        
        for error in self.errors:
            # Create a signature for grouping
            resource_type = error.get('resource', {}).get('type', 'unknown')
            severity = error.get('severity', 'UNKNOWN')
            
            # Extract error message using comprehensive field search
            message = self.extract_error_message(error)
            
            # Truncate message for grouping key
            message_key = message[:self.GROUPING_KEY_MAX_LENGTH] if message else 'no-message'
            
            signature = f"{resource_type}:{severity}:{message_key}"
            error_groups[signature].append(error)
        
        return error_groups
    
    def classify_severity(self, severity: str) -> tuple:
        """Classify severity and return (label, emoji)."""
        if severity in ['CRITICAL', 'ALERT', 'EMERGENCY']:
            return 'CRITICAL', '🔴'
        elif severity == 'ERROR':
            return 'HIGH', '🟠'
        elif severity == 'WARNING':
            return 'MEDIUM', '🟡'
        else:
            return 'LOW', '🔵'
    
    def create_issue_body(self, resource_type: str, severity: str, severity_label: str,
                          severity_emoji: str, timestamp: str, count: int, message: str,
                          service_name: str, region: str, labels: Dict, repo: str, run_id: str) -> str:
        """Create the issue body markdown."""
        labels_json = json.dumps(labels, indent=2)
        
        body = f"""## {severity_emoji} GCP Error Detected: {resource_type}

| Field | Value |
|-------|-------|
| Severity | {severity_label} ({severity}) |
| Service | {resource_type} |
| First Detected | {timestamp} |
| Frequency | {count} occurrence(s) |

### Error Details

```
{message}
```

### Affected Resources

| Resource | Value |
|----------|-------|
| Project | {self.project_id} |
| Service | {service_name} |
| Region | {region} |
| Resource Type | {resource_type} |

### Resource Labels

```json
{labels_json}
```

### Recommended Actions

1. [ ] Review the error logs in GCP Console
2. [ ] Check service health and recent deployments
3. [ ] Investigate root cause
4. [ ] Apply fix or mitigation
5. [ ] Monitor for recurrence

### Links

- [GCP Logging Console](https://console.cloud.google.com/logs/query?project={self.project_id})
- [Error Reporting](https://console.cloud.google.com/errors?project={self.project_id})

---

Detected by @gcp-error-monitor via automated monitoring

Created by workflow: [GCP Error Monitor](https://github.com/{repo}/actions/runs/{run_id})
"""
        return body
    
    def check_existing_issue(self, resource_type: str, service_name: str) -> Optional[int]:
        """Check if a similar issue already exists."""
        try:
            result = subprocess.run(
                ['gh', 'issue', 'list', '--state', 'open', 
                 '--search', f'"{resource_type}" "{service_name}" in:title',
                 '--json', 'number,title', '--limit', '5'],
                capture_output=True,
                text=True
            )
            
            # Handle JSON parsing errors gracefully
            if result.returncode != 0:
                return None
            
            try:
                existing = json.loads(result.stdout)
            except json.JSONDecodeError:
                print(f"  Warning: Invalid JSON in gh issue list output")
                return None
            
            if not isinstance(existing, list):
                return None
            
            for issue in existing:
                if not isinstance(issue, dict):
                    continue
                title = issue.get('title', '')
                if resource_type.lower() in title.lower() and service_name.lower() in title.lower():
                    return issue.get('number')
            
            return None
        except Exception as e:
            print(f"  Warning: Could not check existing issues: {e}")
            return None
    
    def create_issue(self, title: str, body: str) -> Optional[str]:
        """Create a GitHub issue and return the URL."""
        try:
            result = subprocess.run(
                ['gh', 'issue', 'create',
                 '--title', title,
                 '--body', body,
                 '--label', 'gcp-error,gcp-monitoring,automated,infrastructure'],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                return result.stdout.strip()
            else:
                print(f"  Error: {result.stderr}")
                return None
        except Exception as e:
            print(f"  Error creating issue: {e}")
            return None
    
    def analyze_and_create_issues(self) -> tuple:
        """Analyze errors and create issues. Returns (created, skipped)."""
        if not self.errors:
            print("No errors to process")
            return 0, 0
        
        error_groups = self.group_errors()
        print(f"📊 Grouped {len(self.errors)} errors into {len(error_groups)} unique patterns")
        print("")
        
        repo = os.environ.get('GITHUB_REPOSITORY', 'unknown/unknown')
        run_id = os.environ.get('GITHUB_RUN_ID', '0')
        
        for signature, group in error_groups.items():
            resource_type, severity, _ = signature.split(':', 2)
            count = len(group)
            
            # Get the most recent error for details
            latest = group[0]
            timestamp = latest.get('timestamp', datetime.now(timezone.utc).isoformat())
            
            # Extract error details using comprehensive search
            message = self.extract_error_message(latest) or 'No error message available'
            
            # Truncate message if too long
            if len(message) > self.MESSAGE_MAX_LENGTH:
                message = message[:self.MESSAGE_MAX_LENGTH] + '...'
            
            # Get resource labels
            labels = latest.get('resource', {}).get('labels', {})
            service_name = labels.get('service_name', labels.get('function_name', 'Unknown'))
            region = labels.get('location', labels.get('region', 'Unknown'))
            
            # Classify severity
            severity_label, severity_emoji = self.classify_severity(severity)
            
            # Create issue title
            issue_title = f"🚨 GCP {severity}: {resource_type} - {service_name}"
            if len(issue_title) > self.ISSUE_TITLE_MAX_LENGTH:
                issue_title = issue_title[:self.ISSUE_TITLE_MAX_LENGTH - 3] + "..."
            
            print(f"{'[DRY RUN] ' if self.dry_run else ''}Processing: {issue_title}")
            print(f"  Severity: {severity_label}")
            print(f"  Occurrences: {count}")
            
            if self.dry_run:
                self.issues_skipped += 1
                print("  Skipped (dry run)")
                print("")
                continue
            
            # Check for existing issue
            existing_issue = self.check_existing_issue(resource_type, service_name)
            if existing_issue:
                print(f"  Skipping - similar issue exists: #{existing_issue}")
                self.issues_skipped += 1
                print("")
                continue
            
            # Create issue body
            issue_body = self.create_issue_body(
                resource_type, severity, severity_label, severity_emoji,
                timestamp, count, message, service_name, region, labels,
                repo, run_id
            )
            
            # Create the issue
            issue_url = self.create_issue(issue_title, issue_body)
            if issue_url:
                print(f"  Created: {issue_url}")
                self.issues_created += 1
            else:
                print("  Failed to create issue")
            
            print("")
        
        return self.issues_created, self.issues_skipped


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Analyze GCP errors and create GitHub issues')
    parser.add_argument('--errors-file', required=True, help='Path to JSON file with GCP errors')
    parser.add_argument('--project-id', default=os.environ.get('GCP_PROJECT_ID', 'unknown'),
                        help='GCP project ID')
    parser.add_argument('--dry-run', action='store_true', 
                        help='Analyze but do not create issues')
    
    args = parser.parse_args()
    
    # Override dry_run from environment if set
    dry_run = args.dry_run or os.environ.get('DRY_RUN', 'false').lower() == 'true'
    
    analyzer = GCPErrorAnalyzer(
        errors_file=args.errors_file,
        project_id=args.project_id,
        dry_run=dry_run
    )
    
    if not analyzer.load_errors():
        sys.exit(1)
    
    created, skipped = analyzer.analyze_and_create_issues()
    
    print("=" * 50)
    print(f"📊 Summary:")
    print(f"  Issues created: {created}")
    print(f"  Issues skipped: {skipped}")
    
    # Output for GitHub Actions
    if 'GITHUB_OUTPUT' in os.environ:
        with open(os.environ['GITHUB_OUTPUT'], 'a') as f:
            f.write(f"issues_created={created}\n")
            f.write(f"issues_skipped={skipped}\n")


if __name__ == '__main__':
    main()
