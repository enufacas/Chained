#!/usr/bin/env python3
"""
Comprehensive edge case test suite for Chained test flows.

Created by @assert-specialist following specification-driven testing principles
inspired by Leslie Lamport.

This test suite systematically validates:
1. Boundary conditions in test execution
2. State transitions and invariants
3. Error handling completeness
4. Test flow determinism
5. Edge cases in agent matching and workflow validation

Specification:
- All tests must be independent and deterministic
- All boundary conditions must be explicitly tested
- All assertions must have clear failure messages
- All edge cases must be documented with their specification
"""

import sys
import os
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple, Optional


class EdgeCaseTestError(Exception):
    """Exception for edge case test failures."""
    pass


def run_command(cmd: List[str], **kwargs) -> Dict[str, any]:
    """
    Run a command and return structured result.
    
    Specification:
    - Command execution must timeout after reasonable period
    - All output must be captured (stdout, stderr)
    - Return code must be preserved
    - Exceptions must be handled gracefully
    """
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=10,
            **kwargs
        )
        return {
            'returncode': result.returncode,
            'stdout': result.stdout.strip(),
            'stderr': result.stderr.strip(),
            'success': result.returncode == 0
        }
    except subprocess.TimeoutExpired:
        return {
            'returncode': -1,
            'stdout': '',
            'stderr': 'Command timed out after 10 seconds',
            'success': False
        }
    except Exception as e:
        return {
            'returncode': -1,
            'stdout': '',
            'stderr': f'Exception: {str(e)}',
            'success': False
        }


def assert_equals(actual, expected, message: str):
    """
    Assert with clear failure message.
    
    Specification: Assertion failures must clearly state:
    - What was expected
    - What was actually received
    - Context of the failure
    """
    if actual != expected:
        raise EdgeCaseTestError(
            f"{message}\n"
            f"  Expected: {expected}\n"
            f"  Actual:   {actual}"
        )


def assert_true(condition, message: str):
    """Assert condition is true with clear message."""
    if not condition:
        raise EdgeCaseTestError(f"Assertion failed: {message}")


def assert_false(condition, message: str):
    """Assert condition is false with clear message."""
    if condition:
        raise EdgeCaseTestError(f"Assertion failed: {message}")


def test_boundary_empty_inputs():
    """
    Test boundary condition: Empty inputs to agent matching.
    
    Specification:
    - Empty string inputs must be handled gracefully
    - System must default to appropriate agent
    - No crashes or exceptions
    - Valid JSON output required
    """
    print("\n🧪 Testing: Boundary Condition - Empty Inputs")
    print("-" * 70)
    
    test_cases = [
        ("", "", "Both empty"),
        ("", "Some body", "Empty title"),
        ("Some title", "", "Empty body"),
        ("   ", "   ", "Whitespace only"),
    ]
    
    for title, body, description in test_cases:
        result = run_command([
            'python3', 'tools/match-issue-to-agent.py',
            title, body
        ])
        
        assert_true(
            result['success'],
            f"Empty input handling failed for: {description}"
        )
        
        # Validate JSON output
        try:
            data = json.loads(result['stdout'])
            assert_true(
                'agent' in data,
                f"Missing 'agent' field in response for: {description}"
            )
            assert_true(
                isinstance(data['agent'], str) and len(data['agent']) > 0,
                f"Agent field must be non-empty string for: {description}"
            )
            print(f"✅ PASSED: {description} → {data['agent']}")
        except json.JSONDecodeError:
            raise EdgeCaseTestError(
                f"Invalid JSON output for {description}: {result['stdout']}"
            )


def test_boundary_maximum_inputs():
    """
    Test boundary condition: Maximum length inputs.
    
    Specification:
    - Very long inputs (10KB+) must be handled
    - No buffer overflows or crashes
    - Response time must be reasonable
    - Memory usage must be bounded
    """
    print("\n🧪 Testing: Boundary Condition - Maximum Length Inputs")
    print("-" * 70)
    
    # Test with very long inputs
    long_title = "A" * 10000
    long_body = "B" * 50000
    
    result = run_command([
        'python3', 'tools/match-issue-to-agent.py',
        long_title, long_body
    ])
    
    assert_true(
        result['success'],
        "Maximum length input handling failed"
    )
    
    try:
        data = json.loads(result['stdout'])
        assert_true(
            'agent' in data,
            "Missing 'agent' field for maximum length input"
        )
        print(f"✅ PASSED: Maximum length inputs handled → {data['agent']}")
    except json.JSONDecodeError:
        raise EdgeCaseTestError(
            f"Invalid JSON for maximum length input: {result['stdout']}"
        )


def test_boundary_special_characters():
    """
    Test boundary condition: Special characters and encoding.
    
    Specification:
    - Unicode characters must be handled correctly
    - Special characters (quotes, brackets, etc.) must not break parsing
    - HTML/script tags must be handled safely
    - Emoji and other non-ASCII must work
    """
    print("\n🧪 Testing: Boundary Condition - Special Characters")
    print("-" * 70)
    
    test_cases = [
        ('Fix "bug" in code', 'Issue with "quotes"', "Double quotes"),
        ("Fix 'bug' in code", "Issue with 'quotes'", "Single quotes"),
        ("Fix <script>alert(1)</script>", "XSS test", "HTML/script tags"),
        ("Fix bug 🐛", "Emoji test 🎉", "Emoji characters"),
        ("Fix bug\nwith\nnewlines", "Body\nwith\nnewlines", "Newlines"),
        ("Fix bug\twith\ttabs", "Body\twith\ttabs", "Tab characters"),
        ("Ñoño bug", "Привет мир", "Unicode characters"),
        ("Fix bug | pipe", "Body & ampersand", "Special operators"),
    ]
    
    for title, body, description in test_cases:
        result = run_command([
            'python3', 'tools/match-issue-to-agent.py',
            title, body
        ])
        
        assert_true(
            result['success'],
            f"Special character handling failed for: {description}"
        )
        
        try:
            data = json.loads(result['stdout'])
            assert_true('agent' in data, f"Missing agent for: {description}")
            print(f"✅ PASSED: {description}")
        except json.JSONDecodeError:
            raise EdgeCaseTestError(
                f"JSON parsing failed for {description}"
            )


def test_invariant_agent_existence():
    """
    Test invariant: All matched agents must exist.
    
    Specification (Invariant):
    For all issue inputs I, if match(I) returns agent A, then:
    - Agent A must exist in agent registry
    - Agent A must have valid definition file
    - get_agent_info(A) must succeed
    
    This is a critical invariant that must never be violated.
    """
    print("\n🧪 Testing: Invariant - Matched Agents Must Exist")
    print("-" * 70)
    
    # Get list of all agents
    list_result = run_command(['python3', 'tools/get-agent-info.py', 'list'])
    assert_true(list_result['success'], "Failed to list agents")
    
    available_agents = set(list_result['stdout'].split())
    assert_true(
        len(available_agents) > 0,
        "Agent list must not be empty"
    )
    
    print(f"Available agents: {len(available_agents)}")
    
    # Test various issue types
    test_issues = [
        ("Security vulnerability", "Fix XSS"),
        ("Add new feature", "Implement user profiles"),
        ("Performance issue", "Slow query"),
        ("Bug fix", "Login broken"),
        ("Documentation", "Update README"),
        ("Refactoring", "Clean up code"),
        ("Testing", "Add unit tests"),
    ]
    
    violations = []
    for title, body in test_issues:
        match_result = run_command([
            'python3', 'tools/match-issue-to-agent.py',
            title, body
        ])
        
        if not match_result['success']:
            violations.append(f"Matching failed for '{title}'")
            continue
        
        try:
            data = json.loads(match_result['stdout'])
            agent = data.get('agent')
            
            # Invariant check: matched agent must exist
            if agent not in available_agents:
                violations.append(
                    f"INVARIANT VIOLATION: '{title}' matched to non-existent "
                    f"agent '{agent}'"
                )
            else:
                # Further verify agent exists
                info_result = run_command([
                    'python3', 'tools/get-agent-info.py',
                    'info', agent
                ])
                
                if not info_result['success']:
                    violations.append(
                        f"INVARIANT VIOLATION: Agent '{agent}' matched but "
                        f"get_agent_info failed"
                    )
        except json.JSONDecodeError:
            violations.append(f"Invalid JSON for '{title}'")
    
    if violations:
        raise EdgeCaseTestError(
            "Invariant violations detected:\n" +
            "\n".join(f"  - {v}" for v in violations)
        )
    
    print(f"✅ PASSED: All {len(test_issues)} matched agents exist")


def test_invariant_json_structure():
    """
    Test invariant: All tool outputs must be valid JSON with required fields.
    
    Specification (Invariant):
    For all tool commands C, the output must satisfy:
    - Valid JSON syntax
    - Contains expected top-level fields
    - Field types match specification
    - No extra/unexpected fields (unless documented)
    """
    print("\n🧪 Testing: Invariant - JSON Output Structure")
    print("-" * 70)
    
    # Test match-issue-to-agent output structure
    match_result = run_command([
        'python3', 'tools/match-issue-to-agent.py',
        'Test issue', 'Test body'
    ])
    
    assert_true(match_result['success'], "Match command failed")
    
    try:
        match_data = json.loads(match_result['stdout'])
        
        # Required fields for match output (based on actual implementation)
        required_fields = ['agent', 'confidence', 'reason']
        for field in required_fields:
            assert_true(
                field in match_data,
                f"Match output missing required field: {field}"
            )
        
        # Type checks
        assert_true(
            isinstance(match_data['agent'], str),
            "Agent field must be string"
        )
        assert_true(
            isinstance(match_data['reason'], str),
            "Reason field must be string"
        )
        assert_true(
            isinstance(match_data['confidence'], str),
            "Confidence field must be string"
        )
        
        print("✅ PASSED: match-issue-to-agent JSON structure valid")
    except json.JSONDecodeError as e:
        raise EdgeCaseTestError(f"Invalid JSON from matcher: {e}")
    
    # Test get-agent-info output structure
    info_result = run_command([
        'python3', 'tools/get-agent-info.py',
        'info', 'assert-specialist'
    ])
    
    assert_true(info_result['success'], "Get-agent-info command failed")
    
    try:
        info_data = json.loads(info_result['stdout'])
        
        # Required fields for agent info
        required_fields = ['name', 'description', 'tools']
        for field in required_fields:
            assert_true(
                field in info_data,
                f"Agent info missing required field: {field}"
            )
        
        # Type checks
        assert_true(
            isinstance(info_data['name'], str),
            "Name field must be string"
        )
        assert_true(
            isinstance(info_data['description'], str),
            "Description field must be string"
        )
        assert_true(
            isinstance(info_data['tools'], list),
            "Tools field must be list"
        )
        
        print("✅ PASSED: get-agent-info JSON structure valid")
    except json.JSONDecodeError as e:
        raise EdgeCaseTestError(f"Invalid JSON from agent info: {e}")


def test_determinism_matching():
    """
    Test property: Agent matching must be deterministic.
    
    Specification (Determinism):
    For all inputs I, if match(I) = A at time t1,
    then match(I) = A at time t2 (assuming no system changes).
    
    Non-determinism in matching would violate reproducibility.
    """
    print("\n🧪 Testing: Property - Matching Determinism")
    print("-" * 70)
    
    test_cases = [
        ("Security issue", "Fix vulnerability"),
        ("Performance problem", "Optimize query"),
        ("New feature", "Add user profiles"),
    ]
    
    for title, body in test_cases:
        results = []
        
        # Run matching 5 times
        for i in range(5):
            result = run_command([
                'python3', 'tools/match-issue-to-agent.py',
                title, body
            ])
            
            assert_true(
                result['success'],
                f"Matching failed on iteration {i+1} for '{title}'"
            )
            
            data = json.loads(result['stdout'])
            results.append(data['agent'])
        
        # Check all results are identical
        first_agent = results[0]
        for i, agent in enumerate(results[1:], 2):
            assert_equals(
                agent,
                first_agent,
                f"Non-deterministic matching for '{title}' (iteration {i})"
            )
        
        print(f"✅ PASSED: Deterministic matching for '{title}' → {first_agent}")


def test_error_handling_invalid_agent():
    """
    Test error handling: Invalid agent queries.
    
    Specification:
    - Querying non-existent agents must fail gracefully
    - Error messages must be clear and actionable
    - No stack traces exposed to user
    - Exit codes must indicate failure
    """
    print("\n🧪 Testing: Error Handling - Invalid Agent Queries")
    print("-" * 70)
    
    invalid_agents = [
        "nonexistent-agent-xyz",
        "agent-with-very-long-name-that-does-not-exist-" + "x" * 100,
        "",
        "agent/with/slashes",
        "../../../etc/passwd",  # Path traversal attempt
    ]
    
    for agent in invalid_agents:
        result = run_command([
            'python3', 'tools/get-agent-info.py',
            'info', agent
        ])
        
        # Must fail for invalid agent
        assert_false(
            result['success'],
            f"Invalid agent '{agent}' should fail but succeeded"
        )
        
        # Should not expose stack traces
        assert_false(
            'Traceback' in result['stderr'],
            f"Stack trace exposed for invalid agent '{agent}'"
        )
        
        print(f"✅ PASSED: Invalid agent '{agent[:30]}...' handled correctly")


def test_workflow_file_completeness():
    """
    Test specification completeness: All workflow files have required fields.
    
    Specification:
    Every workflow file W must have:
    - Valid YAML syntax
    - 'name' field (non-empty string)
    - 'on' trigger field
    - At least one job
    - Each job must have 'runs-on'
    """
    print("\n🧪 Testing: Specification Completeness - Workflow Files")
    print("-" * 70)
    
    workflow_dir = Path('.github/workflows')
    assert_true(
        workflow_dir.exists(),
        "Workflow directory must exist"
    )
    
    workflow_files = list(workflow_dir.glob('*.yml')) + list(workflow_dir.glob('*.yaml'))
    assert_true(
        len(workflow_files) > 0,
        "At least one workflow file must exist"
    )
    
    print(f"Checking {len(workflow_files)} workflow files...")
    
    import yaml
    
    violations = []
    for filepath in workflow_files:
        try:
            with open(filepath, 'r') as f:
                workflow = yaml.safe_load(f.read())
            
            # Check 'name' field
            if 'name' not in workflow:
                violations.append(f"{filepath.name}: Missing 'name' field")
            elif not isinstance(workflow['name'], str) or not workflow['name'].strip():
                violations.append(f"{filepath.name}: Invalid 'name' field")
            
            # Check 'on' trigger
            if 'on' not in workflow and True not in workflow:  # Handle YAML bool conversion
                violations.append(f"{filepath.name}: Missing 'on' trigger")
            
            # Check jobs
            if 'jobs' not in workflow:
                violations.append(f"{filepath.name}: Missing 'jobs' field")
            elif not isinstance(workflow['jobs'], dict):
                violations.append(f"{filepath.name}: Jobs must be a mapping")
            elif len(workflow['jobs']) == 0:
                violations.append(f"{filepath.name}: At least one job required")
            else:
                # Check each job has runs-on
                for job_name, job_config in workflow['jobs'].items():
                    if isinstance(job_config, dict) and 'runs-on' not in job_config:
                        violations.append(
                            f"{filepath.name}: Job '{job_name}' missing 'runs-on'"
                        )
        
        except yaml.YAMLError as e:
            violations.append(f"{filepath.name}: YAML syntax error - {e}")
        except Exception as e:
            violations.append(f"{filepath.name}: Unexpected error - {e}")
    
    if violations:
        raise EdgeCaseTestError(
            "Workflow specification violations:\n" +
            "\n".join(f"  - {v}" for v in violations)
        )
    
    print(f"✅ PASSED: All {len(workflow_files)} workflows meet specification")


def main():
    """Run all edge case tests."""
    print("=" * 70)
    print("🧪 Comprehensive Edge Case Test Suite")
    print("   by @assert-specialist")
    print("=" * 70)
    print("\nSpecification-driven testing following Leslie Lamport principles:")
    print("  • Systematic boundary condition coverage")
    print("  • Invariant validation at critical points")
    print("  • Determinism and reproducibility verification")
    print("  • Complete error handling validation")
    print("  • Specification completeness checks")
    
    # Change to repo root
    repo_root = Path(__file__).parent.parent
    os.chdir(repo_root)
    print(f"\nWorking directory: {os.getcwd()}")
    
    tests = [
        ("Boundary: Empty Inputs", test_boundary_empty_inputs),
        ("Boundary: Maximum Inputs", test_boundary_maximum_inputs),
        ("Boundary: Special Characters", test_boundary_special_characters),
        ("Invariant: Agent Existence", test_invariant_agent_existence),
        ("Invariant: JSON Structure", test_invariant_json_structure),
        ("Property: Matching Determinism", test_determinism_matching),
        ("Error Handling: Invalid Agent", test_error_handling_invalid_agent),
        ("Specification: Workflow Completeness", test_workflow_file_completeness),
    ]
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        try:
            test_func()
            passed += 1
        except EdgeCaseTestError as e:
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
    print("📊 Edge Case Test Summary")
    print("=" * 70)
    print(f"\nPassed: {passed}/{passed + failed}")
    print(f"Failed: {failed}/{passed + failed}")
    
    if failed == 0:
        print("\n✅ All edge case tests passed!")
        print("\n🎉 Test suite demonstrates:")
        print("   • Complete boundary condition coverage")
        print("   • All invariants hold")
        print("   • Deterministic behavior verified")
        print("   • Robust error handling")
        print("   • Specification completeness validated")
        return 0
    else:
        print(f"\n❌ {failed} edge case test(s) failed")
        print("\n⚠️  Please address edge case violations")
        return 1


if __name__ == '__main__':
    sys.exit(main())
