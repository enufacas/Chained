#!/usr/bin/env python3
"""
Integration Test for AI Agent Learning System

Tests the complete flow from data loading through guidance generation.

Built by @create-botter to validate the learning system integration.
"""

import json
import subprocess
import sys
from pathlib import Path


def run_command(cmd: list, description: str) -> dict:
    """Run a command and return JSON output"""
    print(f"\n🧪 Testing: {description}")
    print(f"   Command: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode != 0:
            print(f"   ❌ FAILED: {result.stderr}")
            return None
        
        # Parse JSON output
        try:
            data = json.loads(result.stdout)
            print(f"   ✅ SUCCESS")
            return data
        except json.JSONDecodeError:
            # If not JSON, return the raw output
            print(f"   ✅ SUCCESS (non-JSON output)")
            return {"output": result.stdout}
    
    except subprocess.TimeoutExpired:
        print(f"   ❌ TIMEOUT")
        return None
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
        return None


def test_learning_api():
    """Test the agent-learning-api.py"""
    print("\n" + "="*60)
    print("Testing Agent Learning API")
    print("="*60)
    
    tests = [
        {
            "name": "Query guidance for create-botter",
            "cmd": [
                "python3", "tools/agent-learning-api.py", "query",
                "--agent", "create-botter",
                "--task-type", "infrastructure",
                "--task-description", "Test learning system"
            ],
            "checks": [
                ("agent_id", "create-botter"),
                ("risk_level", lambda x: x in ["low", "medium", "high"]),
                ("recommendations", lambda x: len(x) > 0),
                ("warnings", lambda x: len(x) > 0)
            ]
        },
        {
            "name": "Query guidance for engineer-master",
            "cmd": [
                "python3", "tools/agent-learning-api.py", "query",
                "--agent", "engineer-master",
                "--task-type", "api-development",
                "--task-description", "Create API endpoint"
            ],
            "checks": [
                ("agent_id", "engineer-master"),
                ("confidence", lambda x: 0 <= x <= 1.0)
            ]
        },
        {
            "name": "Assess file risk",
            "cmd": [
                "python3", "tools/agent-learning-api.py", "assess-risk",
                "--agent", "secure-specialist",
                "--files", "auth.py,tests/test_auth.py"
            ],
            "checks": [
                ("overall_risk", lambda x: 0 <= x <= 1.0),
                ("file_risks", lambda x: len(x) == 2)
            ]
        },
        {
            "name": "Get best practices",
            "cmd": [
                "python3", "tools/agent-learning-api.py", "best-practices",
                "--agent", "organize-guru"
            ],
            "checks": [
                ("agent_id", "organize-guru"),
                ("best_practices", lambda x: len(x) > 0)
            ]
        },
        {
            "name": "Get warnings",
            "cmd": [
                "python3", "tools/agent-learning-api.py", "warnings",
                "--agent", "refactor-champion",
                "--task-type", "refactoring"
            ],
            "checks": [
                ("agent_id", "refactor-champion"),
                ("warnings", lambda x: len(x) > 0)
            ]
        }
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        result = run_command(test["cmd"], test["name"])
        
        if result is None:
            failed += 1
            continue
        
        # Validate checks
        test_passed = True
        for key, expected in test["checks"]:
            if key not in result:
                print(f"      ⚠️ Missing key: {key}")
                test_passed = False
                continue
            
            actual = result[key]
            if callable(expected):
                if not expected(actual):
                    print(f"      ⚠️ Check failed: {key}")
                    test_passed = False
            elif actual != expected:
                print(f"      ⚠️ Value mismatch: {key} = {actual} (expected {expected})")
                test_passed = False
        
        if test_passed:
            passed += 1
            print(f"      ✅ All checks passed")
        else:
            failed += 1
    
    return passed, failed


def test_pr_learning_integrator():
    """Test the pr-learning-integrator.py"""
    print("\n" + "="*60)
    print("Testing PR Learning Integrator")
    print("="*60)
    
    tests = [
        {
            "name": "Generate issue body for create-botter",
            "cmd": [
                "python3", "tools/pr-learning-integrator.py",
                "--agent", "create-botter",
                "--format", "issue-body"
            ],
            "checks": [
                ("output", lambda x: "Recommended Approach" in x or "Success Patterns" in x)
            ]
        },
        {
            "name": "Generate JSON for engineer-master",
            "cmd": [
                "python3", "tools/pr-learning-integrator.py",
                "--agent", "engineer-master",
                "--format", "json"
            ],
            "checks": [
                ("warnings", lambda x: isinstance(x, list)),
                ("success_patterns", lambda x: isinstance(x, list)),
                ("recommendations", lambda x: isinstance(x, list))
            ]
        }
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        result = run_command(test["cmd"], test["name"])
        
        if result is None:
            failed += 1
            continue
        
        # Validate checks
        test_passed = True
        for key, check_fn in test["checks"]:
            if key not in result:
                print(f"      ⚠️ Missing key: {key}")
                test_passed = False
                continue
            
            if not check_fn(result[key]):
                print(f"      ⚠️ Check failed: {key}")
                test_passed = False
        
        if test_passed:
            passed += 1
            print(f"      ✅ All checks passed")
        else:
            failed += 1
    
    return passed, failed


def test_data_files():
    """Test that required data files exist and are valid"""
    print("\n" + "="*60)
    print("Testing Data Files")
    print("="*60)
    
    files = [
        ("learnings/pr_failures.json", lambda p: p.exists() and p.stat().st_size > 0),
        ("learnings/pr_intelligence/code_patterns.json", lambda p: p.exists() and p.stat().st_size > 0),
        ("tools/agent-learning-api.py", lambda p: p.exists()),
        ("tools/pr-learning-integrator.py", lambda p: p.exists()),
        ("tools/assign-copilot-to-issue.sh", lambda p: p.exists())
    ]
    
    passed = 0
    failed = 0
    
    for filepath, check_fn in files:
        path = Path(filepath)
        print(f"\n🧪 Testing: {filepath}")
        
        if check_fn(path):
            print(f"   ✅ EXISTS")
            passed += 1
        else:
            print(f"   ❌ MISSING or INVALID")
            failed += 1
    
    return passed, failed


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("AI Agent Learning System - Integration Tests")
    print("Built by @create-botter")
    print("="*60)
    
    total_passed = 0
    total_failed = 0
    
    # Test data files
    passed, failed = test_data_files()
    total_passed += passed
    total_failed += failed
    
    # Test learning API
    passed, failed = test_learning_api()
    total_passed += passed
    total_failed += failed
    
    # Test integrator
    passed, failed = test_pr_learning_integrator()
    total_passed += passed
    total_failed += failed
    
    # Summary
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    print(f"✅ Passed: {total_passed}")
    print(f"❌ Failed: {total_failed}")
    print(f"📊 Total:  {total_passed + total_failed}")
    
    if total_failed > 0:
        print("\n⚠️ Some tests failed. Please review the output above.")
        return 1
    else:
        print("\n🎉 All tests passed!")
        return 0


if __name__ == '__main__':
    sys.exit(main())
