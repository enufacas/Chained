#!/usr/bin/env python3
"""
ADK Pipeline Status Validator
==============================

Validates the ADK A2A blog pipeline infrastructure and tracking issue setup.

@create-botter - Ensuring reliability through comprehensive validation
"""

import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Tuple


# =============================================================================
# Configuration
# =============================================================================

REPO_ROOT = Path(__file__).parent.parent
WORKFLOW_FILE = REPO_ROOT / ".github" / "workflows" / "adk-a2a-blog-pipeline.yml"
ORCHESTRATOR_FILE = REPO_ROOT / "infrastructure" / "docker" / "adk-agents" / "orchestrator.py"
TEST_FILE = REPO_ROOT / "tests" / "test_adk_blog_pipeline.py"


# =============================================================================
# Validation Functions
# =============================================================================


def validate_workflow_file() -> Tuple[bool, List[str]]:
    """Validate workflow file exists and has required content."""
    issues = []
    
    if not WORKFLOW_FILE.exists():
        issues.append(f"❌ Workflow file not found: {WORKFLOW_FILE}")
        return False, issues
    
    content = WORKFLOW_FILE.read_text()
    
    # Check required sections
    required_elements = [
        ("schedule", "Scheduled execution"),
        ("workflow_dispatch", "Manual trigger"),
        ("adk-pipeline", "Pipeline label"),
        ("gh issue create", "Issue creation"),
        ("gh issue comment", "Issue commenting"),
        ("ADK A2A Blog Pipeline Status", "Tracking issue title"),
        ("pipeline-simulation", "Simulation mode"),
        ("preflight", "Pre-flight checks"),
    ]
    
    for element, description in required_elements:
        if element not in content:
            issues.append(f"❌ Missing {description} ({element})")
    
    # Check cron schedule
    if "cron:" in content:
        cron_match = re.search(r"cron:\s*['\"](.+?)['\"]", content)
        if cron_match:
            cron_expr = cron_match.group(1)
            print(f"✅ Cron schedule: {cron_expr}")
        else:
            issues.append("⚠️  Cron schedule format unclear")
    
    if not issues:
        print("✅ Workflow file validation passed")
    
    return len(issues) == 0, issues


def validate_orchestrator() -> Tuple[bool, List[str]]:
    """Validate orchestrator file exists and has required content."""
    issues = []
    
    if not ORCHESTRATOR_FILE.exists():
        issues.append(f"❌ Orchestrator not found: {ORCHESTRATOR_FILE}")
        return False, issues
    
    content = ORCHESTRATOR_FILE.read_text()
    
    # Check required components
    required_elements = [
        ("class A2AClient", "A2A client class"),
        ("class BlogPipelineOrchestrator", "Orchestrator class"),
        ("async def main()", "Main entry point"),
        ("pipeline_result.json", "Output file"),
        ("/a2a/tasks", "A2A task endpoint"),
        ("/.well-known/agent.json", "Agent card endpoint"),
    ]
    
    for element, description in required_elements:
        if element not in content:
            issues.append(f"❌ Missing {description} ({element})")
    
    # Check for proper error handling
    if "try:" not in content or "except" not in content:
        issues.append("⚠️  Limited error handling in orchestrator")
    
    if not issues:
        print("✅ Orchestrator validation passed")
    
    return len(issues) == 0, issues


def validate_test_file() -> Tuple[bool, List[str]]:
    """Validate test file exists and has coverage."""
    issues = []
    
    if not TEST_FILE.exists():
        issues.append(f"❌ Test file not found: {TEST_FILE}")
        return False, issues
    
    content = TEST_FILE.read_text()
    
    # Check test coverage
    required_tests = [
        ("TestOrchestratorModule", "Orchestrator module tests"),
        ("TestA2AClient", "A2A client tests"),
        ("TestWorkflowIntegration", "Workflow integration tests"),
        ("test_workflow_file_exists", "Workflow file existence test"),
        ("test_workflow_has_tracking_issue_logic", "Tracking issue logic test"),
    ]
    
    for test_name, description in required_tests:
        if test_name not in content:
            issues.append(f"❌ Missing {description} ({test_name})")
    
    if not issues:
        print("✅ Test file validation passed")
    
    return len(issues) == 0, issues


def validate_documentation() -> Tuple[bool, List[str]]:
    """Validate documentation exists."""
    issues = []
    
    docs = [
        "docs/ADK_PIPELINE_STATUS_GUIDE.md",
        "docs/ADK_A2A_PIPELINE_IMPLEMENTATION.md",
        "docs/ADK_PIPELINE_QUICK_REF.md",
        "docs/ADK_PIPELINE_DASHBOARD.md",
    ]
    
    for doc_path in docs:
        doc_file = REPO_ROOT / doc_path
        if not doc_file.exists():
            issues.append(f"❌ Missing documentation: {doc_path}")
        else:
            # Check file is not empty
            if doc_file.stat().st_size < 100:
                issues.append(f"⚠️  Documentation seems incomplete: {doc_path}")
    
    if not issues:
        print("✅ Documentation validation passed")
    
    return len(issues) == 0, issues


def validate_tracking_issue() -> Tuple[bool, List[str]]:
    """Validate tracking issue exists and is properly configured."""
    issues = []
    
    try:
        # Try to find tracking issue
        result = subprocess.run(
            ["gh", "issue", "list", "--label", "adk-pipeline", 
             "--state", "open", "--limit", "1", "--json", "number,title,labels"],
            capture_output=True,
            text=True,
            check=False
        )
        
        if result.returncode != 0:
            issues.append("⚠️  Could not query GitHub issues (gh CLI not configured)")
            return False, issues
        
        data = json.loads(result.stdout)
        
        if not data:
            issues.append("⚠️  No tracking issue found with label 'adk-pipeline'")
            issues.append("    Issue will be created on first workflow run")
            return True, issues  # This is OK - issue will be created
        
        issue = data[0]
        issue_number = issue["number"]
        issue_title = issue["title"]
        
        print(f"✅ Tracking issue found: #{issue_number}")
        print(f"   Title: {issue_title}")
        
        # Validate title
        if "ADK A2A Blog Pipeline Status" not in issue_title:
            issues.append(f"⚠️  Issue title doesn't match expected format")
        
        # Check labels
        labels = [label["name"] for label in issue["labels"]]
        if "adk-pipeline" not in labels:
            issues.append("❌ Issue missing 'adk-pipeline' label")
        
        if not issues:
            print("✅ Tracking issue validation passed")
        
    except Exception as e:
        issues.append(f"⚠️  Could not validate tracking issue: {e}")
    
    return len(issues) == 0, issues


def validate_agents_directory() -> Tuple[bool, List[str]]:
    """Validate agent files exist."""
    issues = []
    
    agents_dir = REPO_ROOT / "infrastructure" / "docker" / "adk-agents"
    
    if not agents_dir.exists():
        issues.append(f"❌ Agents directory not found: {agents_dir}")
        return False, issues
    
    required_agents = [
        "academic-research",
        "google-trends",
        "blog-writer",
    ]
    
    for agent_name in required_agents:
        agent_dir = agents_dir / agent_name
        agent_file = agent_dir / "agent.py"
        
        if not agent_dir.exists():
            issues.append(f"❌ Agent directory missing: {agent_name}")
        elif not agent_file.exists():
            issues.append(f"❌ Agent file missing: {agent_name}/agent.py")
        else:
            # Validate agent has A2A endpoints
            content = agent_file.read_text()
            if "/.well-known/agent.json" not in content:
                issues.append(f"⚠️  Agent {agent_name} missing agent.json endpoint")
            if "/a2a/tasks" not in content:
                issues.append(f"⚠️  Agent {agent_name} missing A2A tasks endpoint")
    
    if not issues:
        print("✅ Agents directory validation passed")
    
    return len(issues) == 0, issues


# =============================================================================
# Main Validation
# =============================================================================


def run_all_validations() -> bool:
    """Run all validation checks."""
    print("=" * 80)
    print("  🔍 ADK Pipeline Infrastructure Validation")
    print("  @create-botter - Ensuring Quality & Reliability")
    print("=" * 80)
    print()
    
    all_passed = True
    all_issues = []
    
    validations = [
        ("Workflow File", validate_workflow_file),
        ("Orchestrator", validate_orchestrator),
        ("Test Coverage", validate_test_file),
        ("Documentation", validate_documentation),
        ("Agents Directory", validate_agents_directory),
        ("Tracking Issue", validate_tracking_issue),
    ]
    
    for name, validator in validations:
        print(f"📋 Validating {name}...")
        passed, issues = validator()
        
        if not passed:
            all_passed = False
        
        if issues:
            all_issues.extend(issues)
            for issue in issues:
                print(f"   {issue}")
        
        print()
    
    # Print summary
    print("=" * 80)
    print("  📊 Validation Summary")
    print("=" * 80)
    print()
    
    if all_passed and not all_issues:
        print("✅ All validations passed!")
        print()
        print("🎉 ADK Pipeline infrastructure is properly configured")
        print("   Ready for scheduled execution and manual triggers")
        return True
    else:
        print(f"⚠️  Found {len(all_issues)} issues")
        print()
        
        # Categorize issues
        errors = [i for i in all_issues if i.startswith("❌")]
        warnings = [i for i in all_issues if i.startswith("⚠️")]
        
        if errors:
            print(f"❌ Errors: {len(errors)}")
            for error in errors:
                print(f"   {error}")
            print()
        
        if warnings:
            print(f"⚠️  Warnings: {len(warnings)}")
            for warning in warnings:
                print(f"   {warning}")
            print()
        
        if errors:
            print("🚨 Fix errors before deploying pipeline")
            return False
        else:
            print("✅ No critical errors - warnings can be addressed later")
            return True


# =============================================================================
# CLI
# =============================================================================


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Validate ADK Pipeline Infrastructure",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show verbose output"
    )
    
    args = parser.parse_args()
    
    try:
        success = run_all_validations()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Validation interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Validation failed with error: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
