#!/usr/bin/env python3
"""
Tests for the dynamic orchestration system.
"""

import os
import sys
import json
import tempfile
import shutil
from datetime import datetime, timezone

# Add tools to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'tools'))

# Import the modules using importlib to handle dash in filename
import importlib.util

def load_module_from_file(module_name, file_path):
    """Load a Python module from a file path"""
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

# Load modules
copilot_tracker = load_module_from_file("copilot_tracker", "tools/copilot-usage-tracker.py")
workflow_orch = load_module_from_file("workflow_orch", "tools/workflow-orchestrator.py")

CopilotUsageTracker = copilot_tracker.CopilotUsageTracker
WorkflowOrchestrator = workflow_orch.WorkflowOrchestrator


def test_usage_tracker_aggressive_mode():
    """Test that low usage recommends aggressive mode"""
    print("Test 1: Low usage should recommend aggressive mode...")
    
    # Set environment for low usage
    os.environ['COPILOT_MONTHLY_QUOTA'] = '1500'
    os.environ['COPILOT_REQUESTS_USED'] = '200'
    os.environ['COPILOT_RESET_DAY'] = '1'
    
    # Create tracker with temporary history file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        history_file = f.name
    
    try:
        tracker = CopilotUsageTracker(history_file=history_file)
        stats = tracker.estimate_copilot_usage()
        
        assert stats.used == 200, f"Expected used=200, got {stats.used}"
        assert stats.remaining == 1300, f"Expected remaining=1300, got {stats.remaining}"
        assert stats.recommended_mode == 'aggressive', f"Expected aggressive mode, got {stats.recommended_mode}"
        assert stats.is_safe == True, f"Expected safe status"
        
        print("✓ Test 1 passed: Low usage correctly recommends aggressive mode")
        return True
    finally:
        if os.path.exists(history_file):
            os.remove(history_file)


def test_usage_tracker_conservative_mode():
    """Test that high usage recommends conservative mode"""
    print("\nTest 2: High usage should recommend conservative mode...")
    
    # Set environment for high usage
    os.environ['COPILOT_MONTHLY_QUOTA'] = '1500'
    os.environ['COPILOT_REQUESTS_USED'] = '1300'
    os.environ['COPILOT_RESET_DAY'] = '1'
    
    # Create tracker with temporary history file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        history_file = f.name
    
    try:
        tracker = CopilotUsageTracker(history_file=history_file)
        stats = tracker.estimate_copilot_usage()
        
        assert stats.used == 1300, f"Expected used=1300, got {stats.used}"
        assert stats.remaining == 200, f"Expected remaining=200, got {stats.remaining}"
        assert stats.recommended_mode == 'conservative', f"Expected conservative mode, got {stats.recommended_mode}"
        
        print("✓ Test 2 passed: High usage correctly recommends conservative mode")
        return True
    finally:
        if os.path.exists(history_file):
            os.remove(history_file)


def test_usage_tracker_normal_mode():
    """Test that moderate usage recommends normal mode"""
    print("\nTest 3: Moderate usage should recommend normal mode...")
    
    # Set environment for moderate usage
    # 500 out of 1500 is about 33%, which should be normal around mid-cycle
    os.environ['COPILOT_MONTHLY_QUOTA'] = '1500'
    os.environ['COPILOT_REQUESTS_USED'] = '500'
    os.environ['COPILOT_RESET_DAY'] = '1'
    
    # Create tracker with temporary history file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        history_file = f.name
    
    try:
        tracker = CopilotUsageTracker(history_file=history_file)
        stats = tracker.estimate_copilot_usage()
        
        assert stats.used == 500, f"Expected used=500, got {stats.used}"
        assert stats.remaining == 1000, f"Expected remaining=1000, got {stats.remaining}"
        # Should be normal or aggressive depending on time of month
        # With 500 used and ~19 days left, burn rate is ~22/day, projected ~930 total, which is safe
        # This should be normal or aggressive mode
        assert stats.recommended_mode in ['normal', 'aggressive'], f"Expected normal or aggressive mode, got {stats.recommended_mode}"
        
        print(f"✓ Test 3 passed: Moderate usage correctly recommends {stats.recommended_mode} mode")
        return True
    finally:
        if os.path.exists(history_file):
            os.remove(history_file)


def test_workflow_frequencies():
    """Test that workflow frequencies are correctly defined"""
    print("\nTest 4: Workflow frequencies should be defined for all modes...")
    
    # Create tracker
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        history_file = f.name
    
    try:
        tracker = CopilotUsageTracker(history_file=history_file)
        
        # Test all modes
        for mode in ['aggressive', 'normal', 'conservative']:
            freqs = tracker.get_workflow_frequencies(mode)
            
            # Check that all required workflows are present
            required_workflows = ['learn-tldr', 'learn-hn', 'idea-generator', 
                                'ai-idea-spawner', 'ai-friend', 'agent-spawner']
            
            for workflow in required_workflows:
                assert workflow in freqs, f"Missing workflow {workflow} in {mode} mode"
                # Check cron format (basic validation)
                cron = freqs[workflow]
                parts = cron.split()
                assert len(parts) == 5, f"Invalid cron format for {workflow} in {mode}: {cron}"
            
            print(f"  ✓ {mode.capitalize()} mode has all required workflows")
        
        print("✓ Test 4 passed: All workflow frequencies correctly defined")
        return True
    finally:
        if os.path.exists(history_file):
            os.remove(history_file)


def test_orchestrator_status():
    """Test that orchestrator can read workflow schedules"""
    print("\nTest 5: Orchestrator should read current workflow schedules...")
    
    # Create orchestrator (dry-run mode)
    orchestrator = WorkflowOrchestrator(repo_root='.', dry_run=True)
    
    # Get current schedules
    schedules = orchestrator.get_current_schedules()
    
    # Check that all managed workflows are read
    for workflow_name in orchestrator.MANAGED_WORKFLOWS.keys():
        assert workflow_name in schedules, f"Missing schedule for {workflow_name}"
        schedule = schedules[workflow_name]
        # Should either be a valid cron or an error message
        assert schedule is not None, f"Null schedule for {workflow_name}"
        print(f"  ✓ {workflow_name}: {schedule}")
    
    print("✓ Test 5 passed: Orchestrator successfully reads workflow schedules")
    return True


def test_orchestrator_dry_run():
    """Test that orchestrator dry-run doesn't modify files"""
    print("\nTest 6: Orchestrator dry-run should not modify files...")
    
    # Set aggressive mode environment
    os.environ['COPILOT_MONTHLY_QUOTA'] = '1500'
    os.environ['COPILOT_REQUESTS_USED'] = '200'
    
    # Get original workflow content
    workflow_file = '.github/workflows/learn-from-tldr.yml'
    with open(workflow_file, 'r') as f:
        original_content = f.read()
    
    # Run orchestrator in dry-run mode
    orchestrator = WorkflowOrchestrator(repo_root='.', dry_run=True)
    results = orchestrator.update_all_workflows(mode='aggressive')
    
    # Check file wasn't modified
    with open(workflow_file, 'r') as f:
        new_content = f.read()
    
    assert original_content == new_content, "Dry-run mode modified files!"
    
    print("✓ Test 6 passed: Dry-run mode does not modify files")
    return True


def main():
    """Run all tests"""
    print("="*70)
    print("Dynamic Orchestration System Tests")
    print("="*70)
    
    tests = [
        test_usage_tracker_aggressive_mode,
        test_usage_tracker_conservative_mode,
        test_usage_tracker_normal_mode,
        test_workflow_frequencies,
        test_orchestrator_status,
        test_orchestrator_dry_run,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
        except AssertionError as e:
            print(f"✗ Test failed: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ Test error: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print("\n" + "="*70)
    print(f"Test Results: {passed} passed, {failed} failed")
    print("="*70)
    
    return 0 if failed == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
