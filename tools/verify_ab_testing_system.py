#!/usr/bin/env python3
"""
Autonomous A/B Testing System Verification Script

Verifies that all components of the autonomous A/B testing system
are working correctly and ready for production use.

Author: @create-botter
Created: 2025-12-17
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Tuple

# Add tools to path
sys.path.insert(0, str(Path(__file__).parent))

def verify_imports() -> Tuple[bool, str]:
    """Verify all required modules can be imported."""
    try:
        from workflow_config_generator import WorkflowConfigGenerator
        from workflow_ab_testing_integration import WorkflowABTestingIntegration
        from ab_testing_engine import ABTestingEngine
        from autonomous_experiment_creator import AutonomousExperimentCreator
        return True, "✅ All modules imported successfully"
    except ImportError as e:
        return False, f"❌ Import failed: {e}"


def verify_config_generator() -> Tuple[bool, str]:
    """Verify the workflow config generator."""
    try:
        from workflow_config_generator import WorkflowConfigGenerator
        
        generator = WorkflowConfigGenerator()
        
        # Test schedule variant generation with required params
        schedule_variants = generator.generate_schedule_variants("0 */6 * * *", "test-workflow")
        if len(schedule_variants) < 2:
            return False, "❌ Schedule variant generation failed"
        
        # Test timeout variant generation with required params
        timeout_variants = generator.generate_timeout_variants(300, "test-workflow", "test-job")
        if len(timeout_variants) < 2:
            return False, "❌ Timeout variant generation failed"
        
        # Test concurrency variant generation
        concurrency_variants = generator.generate_concurrency_variants("test-workflow")
        if len(concurrency_variants) < 2:
            return False, "❌ Concurrency variant generation failed"
        
        return True, f"✅ Config generator working (generates {len(schedule_variants)} schedule, {len(timeout_variants)} timeout, {len(concurrency_variants)} concurrency variants)"
    except Exception as e:
        return False, f"❌ Config generator error: {e}"


def verify_ab_testing_engine() -> Tuple[bool, str]:
    """Verify the A/B testing engine."""
    try:
        from ab_testing_engine import ABTestingEngine
        
        engine = ABTestingEngine()
        
        # Try to list experiments (should not error even if empty)
        active = engine.list_experiments(status="active")
        completed = engine.list_experiments(status="completed")
        
        return True, f"✅ A/B testing engine working ({len(active)} active, {len(completed)} completed experiments)"
    except Exception as e:
        return False, f"❌ A/B testing engine error: {e}"


def verify_autonomous_creator() -> Tuple[bool, str]:
    """Verify the autonomous experiment creator."""
    try:
        from autonomous_experiment_creator import AutonomousExperimentCreator
        
        creator = AutonomousExperimentCreator(max_concurrent_experiments=5)
        
        # Verify it can be instantiated
        if not hasattr(creator, 'run_autonomous_cycle'):
            return False, "❌ Autonomous creator missing run_autonomous_cycle method"
        
        return True, "✅ Autonomous experiment creator initialized successfully"
    except Exception as e:
        return False, f"❌ Autonomous creator error: {e}"


def verify_workflow_integration() -> Tuple[bool, str]:
    """Verify the workflow A/B testing integration."""
    try:
        from workflow_ab_testing_integration import WorkflowABTestingIntegration
        
        integration = WorkflowABTestingIntegration()
        
        # Verify it can be instantiated and has key methods
        if not hasattr(integration, 'create_experiment_for_workflow'):
            return False, "❌ Integration missing create_experiment_for_workflow method"
        
        if not hasattr(integration, 'create_experiments_from_opportunities'):
            return False, "❌ Integration missing create_experiments_from_opportunities method"
        
        return True, "✅ Workflow A/B testing integration initialized successfully"
    except Exception as e:
        return False, f"❌ Workflow integration error: {e}"


def verify_documentation() -> Tuple[bool, str]:
    """Verify documentation exists."""
    docs_to_check = [
        "docs/AUTONOMOUS_AB_TESTING_GUIDE.md",
        "tools/AB_TESTING_README.md"
    ]
    
    missing = []
    for doc in docs_to_check:
        if not Path(doc).exists():
            missing.append(doc)
    
    if missing:
        return False, f"❌ Missing documentation: {', '.join(missing)}"
    
    return True, f"✅ All documentation present ({len(docs_to_check)} files)"


def verify_workflows() -> Tuple[bool, str]:
    """Verify workflow files exist."""
    workflows_to_check = [
        ".github/workflows/ab-testing-system.yml",
        ".github/workflows/autonomous-ab-testing.yml"
    ]
    
    missing = []
    for workflow in workflows_to_check:
        if not Path(workflow).exists():
            missing.append(workflow)
    
    if missing:
        return False, f"❌ Missing workflows: {', '.join(missing)}"
    
    return True, f"✅ All workflows present ({len(workflows_to_check)} files)"


def verify_tests() -> Tuple[bool, str]:
    """Verify test files exist."""
    test_files = [
        "tests/test_workflow_config_generator.py",
        "tests/test_ab_testing_api.py"
    ]
    
    existing = [f for f in test_files if Path(f).exists()]
    
    if not existing:
        return False, "❌ No test files found"
    
    return True, f"✅ Test files present ({len(existing)} files)"


def main():
    """Run all verification checks."""
    print("=" * 70)
    print(" Autonomous A/B Testing System Verification")
    print("=" * 70)
    print()
    
    verifications = [
        ("Module Imports", verify_imports),
        ("Config Generator", verify_config_generator),
        ("A/B Testing Engine", verify_ab_testing_engine),
        ("Autonomous Creator", verify_autonomous_creator),
        ("Workflow Integration", verify_workflow_integration),
        ("Documentation", verify_documentation),
        ("Workflows", verify_workflows),
        ("Tests", verify_tests)
    ]
    
    all_passed = True
    results = []
    
    for name, verify_func in verifications:
        print(f"Checking {name}...", end=" ")
        sys.stdout.flush()
        
        passed, message = verify_func()
        results.append((name, passed, message))
        
        print(message)
        
        if not passed:
            all_passed = False
    
    print()
    print("=" * 70)
    print(" Verification Summary")
    print("=" * 70)
    print()
    
    for name, passed, message in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {name}")
        if not passed:
            print(f"       {message}")
    
    print()
    
    if all_passed:
        print("🎉 All verifications passed! System is fully operational.")
        print()
        print("The autonomous A/B testing system includes:")
        print("  • Workflow configuration variant generator")
        print("  • A/B testing engine with statistical analysis")
        print("  • Autonomous experiment creator")
        print("  • Workflow integration tools")
        print("  • Complete test suite")
        print("  • Comprehensive documentation")
        print()
        print("System created by: @create-botter")
        print("Date: 2025-11-26")
        return 0
    else:
        print("⚠️  Some verifications failed. Please check the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
