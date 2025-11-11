#!/usr/bin/env python3
"""
Comprehensive test suite for GitHub Actions workflow integrity.

This test validates that all workflow files:
1. Are valid YAML syntax
2. Have required fields for GitHub Actions
3. Use proper scheduling syntax
4. Have valid job and step structures
5. Use secure practices (no hardcoded secrets)
6. Follow naming conventions
7. Have proper permissions defined
8. Use appropriate triggers

This complements existing tests by ensuring workflow files are well-formed
and follow GitHub Actions best practices.
"""

import sys
import yaml
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional


# Workflow validation constants
REQUIRED_WORKFLOW_KEYS = ['name', 'on']
VALID_EVENTS = [
    'push', 'pull_request', 'schedule', 'workflow_dispatch', 'issues',
    'issue_comment', 'pull_request_review', 'workflow_call', 'repository_dispatch',
    'create', 'delete', 'deployment', 'fork', 'page_build', 'release', 'status',
    'watch', 'check_run', 'check_suite', 'discussion', 'gollum', 'label',
    'milestone', 'project', 'public', 'registry_package', 'workflow_run'
]
REQUIRED_JOB_KEYS = ['runs-on']
VALID_RUNNERS = ['ubuntu-latest', 'ubuntu-22.04', 'ubuntu-20.04', 'windows-latest', 
                 'macos-latest', 'macos-13', 'macos-12']

# Security patterns to check
SECRET_PATTERNS = [
    (r'password\s*[:=]\s*[\'"][^\'"]+[\'"]', 'Hardcoded password'),
    (r'api[_-]?key\s*[:=]\s*[\'"][^\'"]+[\'"]', 'Hardcoded API key'),
    (r'token\s*[:=]\s*[\'"](?!secrets\.)[^\'"]+[\'"]', 'Hardcoded token'),
    (r'secret\s*[:=]\s*[\'"](?!secrets\.)[^\'"]+[\'"]', 'Hardcoded secret'),
]


class WorkflowValidationError(Exception):
    """Exception raised for workflow validation failures."""
    pass


def load_workflow_file(filepath: Path) -> Dict:
    """Load and parse a workflow YAML file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            # Use safe_load with custom resolver to handle 'on' as string not boolean
            content = f.read()
            # Replace standalone 'on:' to prevent YAML boolean interpretation
            workflow = yaml.safe_load(content)
            
            # YAML might interpret 'on:' as True (boolean)
            # Check if we have True as key (from 'on:') and fix it
            if workflow and True in workflow and 'on' not in workflow:
                workflow['on'] = workflow.pop(True)
            
            return workflow
    except yaml.YAMLError as e:
        raise WorkflowValidationError(f"YAML syntax error: {e}")
    except Exception as e:
        raise WorkflowValidationError(f"Failed to load file: {e}")


def validate_workflow_structure(workflow: Dict, filename: str) -> List[str]:
    """Validate basic workflow structure."""
    issues = []
    
    # Check required top-level keys
    for key in REQUIRED_WORKFLOW_KEYS:
        if key not in workflow:
            issues.append(f"Missing required key: '{key}'")
    
    # Validate workflow name
    if 'name' in workflow:
        name = workflow['name']
        if not isinstance(name, str) or not name.strip():
            issues.append("Workflow 'name' must be a non-empty string")
        elif len(name) > 100:
            issues.append(f"Workflow name is too long ({len(name)} chars)")
    
    # Validate 'on' trigger
    if 'on' in workflow:
        triggers = workflow['on']
        if isinstance(triggers, str):
            if triggers not in VALID_EVENTS:
                issues.append(f"Unknown event trigger: '{triggers}'")
        elif isinstance(triggers, list):
            for trigger in triggers:
                if trigger not in VALID_EVENTS:
                    issues.append(f"Unknown event trigger: '{trigger}'")
        elif isinstance(triggers, dict):
            for event in triggers.keys():
                if event not in VALID_EVENTS:
                    issues.append(f"Unknown event trigger: '{event}'")
        else:
            issues.append("Workflow 'on' must be string, list, or dict")
    
    # Validate jobs
    if 'jobs' not in workflow:
        issues.append("Workflow has no 'jobs' defined")
    elif not isinstance(workflow['jobs'], dict):
        issues.append("Workflow 'jobs' must be a mapping")
    elif len(workflow['jobs']) == 0:
        issues.append("Workflow has no jobs defined")
    
    return issues


def validate_schedule_syntax(workflow: Dict, filename: str) -> List[str]:
    """Validate cron schedule syntax."""
    issues = []
    
    if 'on' not in workflow:
        return issues
    
    triggers = workflow['on']
    if isinstance(triggers, dict) and 'schedule' in triggers:
        schedule = triggers['schedule']
        
        if not isinstance(schedule, list):
            issues.append("Schedule must be a list")
            return issues
        
        for idx, item in enumerate(schedule):
            if not isinstance(item, dict) or 'cron' not in item:
                issues.append(f"Schedule item {idx} must have 'cron' key")
                continue
            
            cron = item['cron']
            
            # Validate cron format: 5 fields (minute hour day month weekday)
            parts = cron.split()
            if len(parts) != 5:
                issues.append(f"Invalid cron syntax (needs 5 fields): '{cron}'")
                continue
            
            # Basic validation of each field
            minute, hour, day, month, weekday = parts
            
            # Validate minute (0-59, can have comma-separated values, ranges, steps)
            if not re.match(r'^(\*|[0-5]?[0-9](-[0-5]?[0-9])?(,[0-5]?[0-9](-[0-5]?[0-9])?)*|(\*|[0-5]?[0-9])/[0-9]+)$', minute):
                issues.append(f"Invalid minute in cron: '{minute}'")
            
            # Validate hour (0-23, can have comma-separated values, ranges, steps)
            if not re.match(r'^(\*|([01]?[0-9]|2[0-3])(-([01]?[0-9]|2[0-3]))?(,([01]?[0-9]|2[0-3])(-([01]?[0-9]|2[0-3]))?)*|(\*|([01]?[0-9]|2[0-3]))/[0-9]+)$', hour):
                issues.append(f"Invalid hour in cron: '{hour}'")
    
    return issues


def validate_jobs(workflow: Dict, filename: str) -> List[str]:
    """Validate job structure and configuration."""
    issues = []
    
    if 'jobs' not in workflow or not isinstance(workflow['jobs'], dict):
        return issues
    
    for job_name, job_config in workflow['jobs'].items():
        if not isinstance(job_config, dict):
            issues.append(f"Job '{job_name}' must be a mapping")
            continue
        
        # Check required job keys
        for key in REQUIRED_JOB_KEYS:
            if key not in job_config:
                issues.append(f"Job '{job_name}' missing required key: '{key}'")
        
        # Validate runs-on
        if 'runs-on' in job_config:
            runner = job_config['runs-on']
            if isinstance(runner, str):
                if runner not in VALID_RUNNERS and not runner.startswith('${{'):
                    issues.append(f"Job '{job_name}' uses unknown runner: '{runner}'")
            elif not isinstance(runner, list):
                issues.append(f"Job '{job_name}' runs-on must be string or list")
        
        # Validate steps
        if 'steps' in job_config:
            if not isinstance(job_config['steps'], list):
                issues.append(f"Job '{job_name}' steps must be a list")
            else:
                for idx, step in enumerate(job_config['steps']):
                    if not isinstance(step, dict):
                        issues.append(f"Job '{job_name}' step {idx} must be a mapping")
                        continue
                    
                    # Each step should have either 'uses' or 'run'
                    if 'uses' not in step and 'run' not in step:
                        # Allow steps with just 'name' for organization
                        if 'name' not in step:
                            issues.append(f"Job '{job_name}' step {idx} needs 'uses' or 'run'")
    
    return issues


def validate_permissions(workflow: Dict, filename: str) -> List[str]:
    """Validate permissions configuration."""
    issues = []
    
    valid_permissions = [
        'actions', 'checks', 'contents', 'deployments', 'id-token',
        'issues', 'discussions', 'packages', 'pages', 'pull-requests',
        'repository-projects', 'security-events', 'statuses'
    ]
    
    # Check top-level permissions
    if 'permissions' in workflow:
        perms = workflow['permissions']
        if isinstance(perms, str):
            if perms not in ['read-all', 'write-all']:
                issues.append(f"Invalid permissions value: '{perms}'")
        elif isinstance(perms, dict):
            for perm, value in perms.items():
                if perm not in valid_permissions:
                    issues.append(f"Unknown permission scope: '{perm}'")
                if value not in ['read', 'write', 'none']:
                    issues.append(f"Invalid permission value for '{perm}': '{value}'")
    
    # Check job-level permissions
    if 'jobs' in workflow:
        for job_name, job_config in workflow['jobs'].items():
            if isinstance(job_config, dict) and 'permissions' in job_config:
                perms = job_config['permissions']
                if isinstance(perms, str) and perms not in ['read-all', 'write-all']:
                    issues.append(f"Job '{job_name}' has invalid permissions: '{perms}'")
                elif isinstance(perms, dict):
                    for perm, value in perms.items():
                        if perm not in valid_permissions:
                            issues.append(f"Job '{job_name}' unknown permission: '{perm}'")
    
    return issues


def check_security_issues(filepath: Path, workflow: Dict) -> List[str]:
    """Check for potential security issues."""
    issues = []
    
    # Read file as text for pattern matching
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for hardcoded secrets
        for pattern, description in SECRET_PATTERNS:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                # Skip if it's a secrets reference
                if 'secrets.' not in match.group(0).lower():
                    line_num = content[:match.start()].count('\n') + 1
                    issues.append(f"Potential security issue on line {line_num}: {description}")
        
        # Check for script injection vulnerabilities in run commands
        if 'jobs' in workflow:
            for job_name, job_config in workflow['jobs'].items():
                if isinstance(job_config, dict) and 'steps' in job_config:
                    for idx, step in enumerate(job_config['steps']):
                        if isinstance(step, dict) and 'run' in step:
                            run_cmd = step['run']
                            # Check for unsafe use of github context
                            if '${{' in run_cmd and 'github.event' in run_cmd:
                                if 'github.event.issue.title' in run_cmd or \
                                   'github.event.issue.body' in run_cmd or \
                                   'github.event.comment.body' in run_cmd:
                                    issues.append(
                                        f"Job '{job_name}' step {idx} may have script injection vulnerability "
                                        "(using github.event data directly in run command)"
                                    )
    
    except Exception as e:
        issues.append(f"Failed to check security: {e}")
    
    return issues


def validate_naming_conventions(filename: str, workflow: Dict) -> List[str]:
    """Validate naming conventions."""
    issues = []
    
    # Filename should be kebab-case with .yml or .yaml extension
    name = filename.replace('.yml', '').replace('.yaml', '')
    if not re.match(r'^[a-z0-9-]+$', name):
        issues.append(
            f"Filename should be kebab-case (lowercase with hyphens): '{filename}'"
        )
    
    # Job names should be descriptive
    if 'jobs' in workflow and isinstance(workflow['jobs'], dict):
        for job_name in workflow['jobs'].keys():
            if len(job_name) < 3:
                issues.append(f"Job name too short: '{job_name}'")
            # Job names should use kebab-case or snake_case
            if not re.match(r'^[a-zA-Z0-9_-]+$', job_name):
                issues.append(f"Job name has invalid characters: '{job_name}'")
    
    return issues


def validate_single_workflow(filepath: Path) -> Tuple[bool, List[str], List[str]]:
    """Validate a single workflow file."""
    warnings = []
    errors = []
    
    try:
        workflow = load_workflow_file(filepath)
        
        # Run all validation checks
        errors.extend(validate_workflow_structure(workflow, filepath.name))
        errors.extend(validate_schedule_syntax(workflow, filepath.name))
        errors.extend(validate_jobs(workflow, filepath.name))
        errors.extend(validate_permissions(workflow, filepath.name))
        
        # Security checks generate errors
        security_issues = check_security_issues(filepath, workflow)
        if security_issues:
            errors.extend(security_issues)
        
        # Naming convention issues are warnings
        warnings.extend(validate_naming_conventions(filepath.name, workflow))
        
        return len(errors) == 0, warnings, errors
        
    except WorkflowValidationError as e:
        errors.append(str(e))
        return False, warnings, errors
    except Exception as e:
        errors.append(f"Unexpected error: {e}")
        return False, warnings, errors


def test_workflow_files_exist():
    """Test that workflow directory exists and contains files."""
    print("\n📋 Testing: Workflow Files Existence")
    print("-" * 70)
    
    workflow_dir = Path('.github/workflows')
    
    if not workflow_dir.exists():
        raise WorkflowValidationError("Directory '.github/workflows' does not exist")
    
    if not workflow_dir.is_dir():
        raise WorkflowValidationError("'.github/workflows' exists but is not a directory")
    
    workflow_files = list(workflow_dir.glob('*.yml')) + list(workflow_dir.glob('*.yaml'))
    
    if not workflow_files:
        raise WorkflowValidationError("No workflow files found (*.yml or *.yaml)")
    
    print(f"✅ Found {len(workflow_files)} workflow file(s)")
    for f in sorted(workflow_files):
        print(f"   • {f.name}")
    
    return workflow_files


def test_workflow_integrity():
    """Test integrity of all workflow files."""
    print("\n📋 Testing: Workflow File Integrity")
    print("-" * 70)
    
    workflow_files = test_workflow_files_exist()
    
    all_passed = True
    total_warnings = 0
    total_errors = 0
    results = []
    
    for filepath in sorted(workflow_files):
        passed, warnings, errors = validate_single_workflow(filepath)
        
        result = {
            'file': filepath.name,
            'passed': passed,
            'warnings': warnings,
            'errors': errors
        }
        results.append(result)
        
        if passed and not warnings:
            print(f"✅ {filepath.name}")
        elif passed and warnings:
            print(f"⚠️  {filepath.name} ({len(warnings)} warning(s))")
            for warning in warnings:
                print(f"     Warning: {warning}")
            total_warnings += len(warnings)
        else:
            print(f"❌ {filepath.name}")
            for error in errors:
                print(f"     Error: {error}")
            all_passed = False
            total_errors += len(errors)
            if warnings:
                for warning in warnings:
                    print(f"     Warning: {warning}")
                total_warnings += len(warnings)
    
    print(f"\n📊 Summary: {len([r for r in results if r['passed']])} passed, "
          f"{len([r for r in results if not r['passed']])} failed")
    print(f"    Total errors: {total_errors}, Total warnings: {total_warnings}")
    
    if not all_passed:
        raise WorkflowValidationError(f"{total_errors} validation error(s) found")
    
    return results


def test_critical_workflows():
    """Test that critical workflows exist."""
    print("\n📋 Testing: Critical Workflows Existence")
    print("-" * 70)
    
    workflow_dir = Path('.github/workflows')
    
    # Define critical workflows for this repository
    critical_workflows = [
        'agent-spawner.yml',
        'agent-evaluator.yml',
        'agent-data-sync.yml',
        'system-kickoff.yml',
    ]
    
    missing = []
    for workflow in critical_workflows:
        workflow_path = workflow_dir / workflow
        if workflow_path.exists():
            print(f"✅ {workflow}")
        else:
            print(f"❌ {workflow} (missing)")
            missing.append(workflow)
    
    if missing:
        raise WorkflowValidationError(
            f"Missing {len(missing)} critical workflow(s): {', '.join(missing)}"
        )
    
    print(f"\n✅ All {len(critical_workflows)} critical workflows exist")
    return True


def test_workflow_schedule_diversity():
    """Test that scheduled workflows don't all run at the same time."""
    print("\n📋 Testing: Schedule Diversity")
    print("-" * 70)
    
    workflow_dir = Path('.github/workflows')
    workflow_files = list(workflow_dir.glob('*.yml')) + list(workflow_dir.glob('*.yaml'))
    
    schedules = []
    
    for filepath in workflow_files:
        try:
            workflow = load_workflow_file(filepath)
            if 'on' in workflow and isinstance(workflow['on'], dict):
                if 'schedule' in workflow['on']:
                    schedule_list = workflow['on']['schedule']
                    if isinstance(schedule_list, list):
                        for item in schedule_list:
                            if 'cron' in item:
                                schedules.append({
                                    'file': filepath.name,
                                    'cron': item['cron']
                                })
        except Exception as e:
            print(f"⚠️  Could not parse {filepath.name}: {e}")
    
    print(f"Found {len(schedules)} scheduled workflow(s)")
    
    # Group by cron expression
    cron_groups = {}
    for sched in schedules:
        cron = sched['cron']
        if cron not in cron_groups:
            cron_groups[cron] = []
        cron_groups[cron].append(sched['file'])
    
    # Check for duplicate schedules
    duplicates = {k: v for k, v in cron_groups.items() if len(v) > 1}
    
    if duplicates:
        print("\n⚠️  Warning: Multiple workflows share the same schedule:")
        for cron, files in duplicates.items():
            print(f"   '{cron}':")
            for f in files:
                print(f"      - {f}")
        print("\n   Consider staggering schedules to avoid resource contention.")
    else:
        print("✅ All scheduled workflows have unique schedules")
    
    if schedules:
        print(f"\n📅 Schedule summary:")
        for sched in schedules:
            print(f"   {sched['file']}: {sched['cron']}")
    
    return True


def main():
    """Run all workflow integrity tests."""
    print("=" * 70)
    print("🧪 GitHub Actions Workflow Integrity Tests")
    print("=" * 70)
    print("\nValidating workflow files for:")
    print("  • Valid YAML syntax")
    print("  • Required fields and structure")
    print("  • Correct schedule syntax")
    print("  • Job and step configuration")
    print("  • Permissions settings")
    print("  • Security best practices")
    print("  • Naming conventions")
    
    tests = [
        ("Workflow Integrity", test_workflow_integrity),
        ("Critical Workflows", test_critical_workflows),
        ("Schedule Diversity", test_workflow_schedule_diversity),
    ]
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        try:
            test_func()
            passed += 1
        except WorkflowValidationError as e:
            print(f"\n❌ Test Failed: {name}")
            print(f"   Error: {e}")
            failed += 1
        except Exception as e:
            print(f"\n❌ Test Failed: {name}")
            print(f"   Unexpected error: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    # Print final summary
    print("\n" + "=" * 70)
    print("📊 Test Summary")
    print("=" * 70)
    print(f"\nPassed: {passed}/{passed + failed}")
    
    if failed == 0:
        print("\n✅ All workflow integrity tests passed!")
        print("\n🎉 Workflow files are well-formed and follow best practices:")
        print("   • Valid YAML syntax")
        print("   • Proper GitHub Actions structure")
        print("   • Secure configuration")
        print("   • Good naming conventions")
        return 0
    else:
        print(f"\n❌ {failed} test(s) failed")
        print("\n⚠️  Please fix validation errors before deploying workflows")
        return 1


if __name__ == '__main__':
    sys.exit(main())
