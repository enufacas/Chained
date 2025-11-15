#!/usr/bin/env python3
"""
Comprehensive test suite for PR auto-labeling system.
Built by @assert-specialist with specification-driven testing approach.

Test Philosophy:
    - Specification first: Define expected behavior before testing
    - Systematic coverage: Test all states, transitions, and boundaries
    - Meaningful assertions: Every assert validates a specific invariant
    - Edge case focus: Test boundary conditions and error cases
"""

import sys
import json
import importlib.util
from pathlib import Path

# Load the pr-content-analyzer module (has dash in filename)
tools_dir = Path(__file__).parent.parent / "tools"
analyzer_path = tools_dir / "pr-content-analyzer.py"

if not analyzer_path.exists():
    print(f"Error: pr-content-analyzer.py not found at {analyzer_path}")
    sys.exit(1)

# Import module from file path
spec = importlib.util.spec_from_file_location("pr_content_analyzer", analyzer_path)
pr_content_analyzer = importlib.util.module_from_spec(spec)
sys.modules["pr_content_analyzer"] = pr_content_analyzer
spec.loader.exec_module(pr_content_analyzer)

# Import classes
PRContentAnalyzer = pr_content_analyzer.PRContentAnalyzer
PRAnalysis = pr_content_analyzer.PRAnalysis
LabelRule = pr_content_analyzer.LabelRule


def print_test(name: str):
    """Print test name with formatting."""
    print(f"\n🧪 Testing: {name}")
    print("-" * 70)


def assert_valid_analysis(result: PRAnalysis, test_name: str):
    """
    Validate common invariants for any PRAnalysis result.
    
    Invariants:
        - No duplicate labels
        - All confidence scores between 0 and 1
        - All labels have confidence scores
        - Analysis details exist
    """
    # Invariant: No duplicate labels
    assert len(result.labels) == len(set(result.labels)), \
        f"{test_name}: Duplicate labels found: {result.labels}"
    
    # Invariant: All confidence scores valid
    for label, score in result.confidence_scores.items():
        assert 0.0 <= score <= 1.0, \
            f"{test_name}: Invalid confidence score for {label}: {score}"
    
    # Invariant: All labels have confidence scores
    for label in result.labels:
        assert label in result.confidence_scores, \
            f"{test_name}: Missing confidence score for label: {label}"
    
    # Invariant: Analysis details exist
    assert result.analysis_details is not None, \
        f"{test_name}: Missing analysis details"
    
    print(f"✅ PASSED: All invariants validated for {test_name}")


def test_empty_pr():
    """
    Test edge case: Empty PR with no content.
    
    Specification:
        - Empty title, body, files should not crash
        - Should return valid PRAnalysis with empty labels
        - All invariants must hold
    """
    print_test("Empty PR (Edge Case)")
    
    analyzer = PRContentAnalyzer()
    result = analyzer.analyze_pr(
        title="",
        body="",
        files=[],
        diff=""
    )
    
    # Postcondition: Valid result
    assert isinstance(result, PRAnalysis), "Must return PRAnalysis"
    
    # Postcondition: Empty labels expected for empty PR
    assert result.labels == [], f"Empty PR should have no labels, got: {result.labels}"
    
    # Validate all invariants
    assert_valid_analysis(result, "empty_pr")
    
    print("✅ PASSED: Empty PR handled correctly")
    return True


def test_code_quality_pr():
    """
    Test code quality label detection.
    
    Specification:
        - PRs with refactoring keywords should get 'code-quality' label
        - Confidence should be > 0.6
        - Python files should increase confidence
    """
    print_test("Code Quality PR Detection")
    
    analyzer = PRContentAnalyzer()
    result = analyzer.analyze_pr(
        title="Refactor authentication module",
        body="Simplify the auth code and improve readability",
        files=["src/auth.py", "tests/test_auth.py"],
        diff=""
    )
    
    # Postcondition: code-quality label present
    assert "code-quality" in result.labels, \
        f"Expected 'code-quality' label, got: {result.labels}"
    
    # Postcondition: Sufficient confidence
    assert result.confidence_scores["code-quality"] >= 0.6, \
        f"Confidence too low: {result.confidence_scores['code-quality']}"
    
    # Validate invariants
    assert_valid_analysis(result, "code_quality_pr")
    
    print("✅ PASSED: Code quality PR detected correctly")
    return True


def test_documentation_pr():
    """
    Test documentation label detection.
    
    Specification:
        - PRs updating markdown files should get 'documentation' label
        - README changes should have high confidence
    """
    print_test("Documentation PR Detection")
    
    analyzer = PRContentAnalyzer()
    result = analyzer.analyze_pr(
        title="Update README with installation guide",
        body="Add detailed installation instructions and examples",
        files=["README.md", "docs/INSTALLATION.md"],
        diff=""
    )
    
    # Postcondition: documentation label present
    assert "documentation" in result.labels, \
        f"Expected 'documentation' label, got: {result.labels}"
    
    # Postcondition: High confidence for clear doc changes
    assert result.confidence_scores["documentation"] >= 0.7, \
        f"Documentation confidence should be high: {result.confidence_scores['documentation']}"
    
    # Validate invariants
    assert_valid_analysis(result, "documentation_pr")
    
    print("✅ PASSED: Documentation PR detected correctly")
    return True


def test_testing_pr():
    """
    Test testing label detection.
    
    Specification:
        - PRs with test files should get 'testing' label
        - Test keywords increase confidence
    """
    print_test("Testing PR Detection")
    
    analyzer = PRContentAnalyzer()
    result = analyzer.analyze_pr(
        title="Add unit tests for payment module",
        body="Increase test coverage with comprehensive test suite",
        files=["tests/test_payment.py", "test_utils.py"],
        diff=""
    )
    
    # Postcondition: testing label present
    assert "testing" in result.labels, \
        f"Expected 'testing' label, got: {result.labels}"
    
    # Validate invariants
    assert_valid_analysis(result, "testing_pr")
    
    print("✅ PASSED: Testing PR detected correctly")
    return True


def test_agent_system_pr():
    """
    Test agent-system label detection.
    
    Specification:
        - Changes to .github/agents/ should get 'agent-system' label
        - Agent-related keywords should boost confidence
    """
    print_test("Agent System PR Detection")
    
    analyzer = PRContentAnalyzer()
    result = analyzer.analyze_pr(
        title="Add new agent for code review",
        body="Implement a specialized agent for reviewing code quality",
        files=[".github/agents/review-agent.md", ".github/agent-system/registry.json"],
        diff=""
    )
    
    # Postcondition: agent-system label present
    assert "agent-system" in result.labels, \
        f"Expected 'agent-system' label, got: {result.labels}"
    
    # Validate invariants
    assert_valid_analysis(result, "agent_system_pr")
    
    print("✅ PASSED: Agent system PR detected correctly")
    return True


def test_workflow_pr():
    """
    Test workflow-optimization label detection.
    
    Specification:
        - Changes to .github/workflows/*.yml should get 'workflow-optimization'
        - Workflow keywords should be detected
    """
    print_test("Workflow PR Detection")
    
    analyzer = PRContentAnalyzer()
    result = analyzer.analyze_pr(
        title="Optimize CI/CD pipeline",
        body="Improve GitHub Actions workflow efficiency",
        files=[".github/workflows/test.yml", ".github/workflows/deploy.yml"],
        diff=""
    )
    
    # Postcondition: workflow-optimization label present
    assert "workflow-optimization" in result.labels, \
        f"Expected 'workflow-optimization' label, got: {result.labels}"
    
    # Validate invariants
    assert_valid_analysis(result, "workflow_pr")
    
    print("✅ PASSED: Workflow PR detected correctly")
    return True


def test_bug_fix_pr():
    """
    Test bug label detection.
    
    Specification:
        - PRs with fix/bug keywords should get 'bug' label
        - No specific file patterns required
    """
    print_test("Bug Fix PR Detection")
    
    analyzer = PRContentAnalyzer()
    result = analyzer.analyze_pr(
        title="Fix crash in login module",
        body="Resolve issue causing application to crash during login",
        files=["src/login.py"],
        diff=""
    )
    
    # Postcondition: bug label present
    assert "bug" in result.labels, \
        f"Expected 'bug' label, got: {result.labels}"
    
    # Validate invariants
    assert_valid_analysis(result, "bug_fix_pr")
    
    print("✅ PASSED: Bug fix PR detected correctly")
    return True


def test_enhancement_pr():
    """
    Test enhancement label detection.
    
    Specification:
        - PRs with add/new/feature keywords should get 'enhancement'
    """
    print_test("Enhancement PR Detection")
    
    analyzer = PRContentAnalyzer()
    result = analyzer.analyze_pr(
        title="Add user profile feature",
        body="Implement new user profile page with avatar upload",
        files=["src/profile.py", "templates/profile.html"],
        diff=""
    )
    
    # Postcondition: enhancement label present
    assert "enhancement" in result.labels, \
        f"Expected 'enhancement' label, got: {result.labels}"
    
    # Validate invariants
    assert_valid_analysis(result, "enhancement_pr")
    
    print("✅ PASSED: Enhancement PR detected correctly")
    return True


def test_security_pr():
    """
    Test security label detection.
    
    Specification:
        - Security-related keywords should trigger 'security' label
        - High importance for security issues
    """
    print_test("Security PR Detection")
    
    analyzer = PRContentAnalyzer()
    result = analyzer.analyze_pr(
        title="Fix SQL injection vulnerability",
        body="Sanitize user input to prevent SQL injection attacks",
        files=["src/database.py"],
        diff=""
    )
    
    # Postcondition: security label present
    assert "security" in result.labels, \
        f"Expected 'security' label, got: {result.labels}"
    
    # Validate invariants
    assert_valid_analysis(result, "security_pr")
    
    print("✅ PASSED: Security PR detected correctly")
    return True


def test_multiple_labels():
    """
    Test PR that should receive multiple labels.
    
    Specification:
        - A PR can have multiple labels
        - All labels should have valid confidence scores
        - No duplicates allowed
    """
    print_test("Multiple Labels Detection")
    
    analyzer = PRContentAnalyzer()
    result = analyzer.analyze_pr(
        title="Refactor auth and add tests",
        body="Improve code quality and add comprehensive test coverage for authentication",
        files=["src/auth.py", "tests/test_auth.py", "docs/AUTH.md"],
        diff=""
    )
    
    # Postcondition: Multiple labels present
    assert len(result.labels) >= 2, \
        f"Expected multiple labels, got: {result.labels}"
    
    # Postcondition: Likely labels for this PR
    expected_labels = {"code-quality", "testing", "documentation"}
    actual_labels = set(result.labels)
    
    # At least some expected labels should be present
    assert len(expected_labels & actual_labels) >= 2, \
        f"Expected at least 2 of {expected_labels}, got: {actual_labels}"
    
    # Validate invariants (especially no duplicates)
    assert_valid_analysis(result, "multiple_labels")
    
    print("✅ PASSED: Multiple labels detected correctly")
    return True


def test_large_pr():
    """
    Test edge case: PR with many files.
    
    Specification:
        - Should handle large number of files without error
        - Performance should be acceptable
    """
    print_test("Large PR (Edge Case)")
    
    # Generate large file list
    files = [f"src/module{i}.py" for i in range(100)]
    
    analyzer = PRContentAnalyzer()
    result = analyzer.analyze_pr(
        title="Large refactoring",
        body="Major code restructuring",
        files=files,
        diff=""
    )
    
    # Postcondition: Handles large PR
    assert isinstance(result, PRAnalysis), "Must return valid analysis"
    
    # Postcondition: Analysis details reflect file count
    assert result.analysis_details["files_changed"] == 100, \
        f"Should track all files: {result.analysis_details['files_changed']}"
    
    # Validate invariants
    assert_valid_analysis(result, "large_pr")
    
    print("✅ PASSED: Large PR handled correctly")
    return True


def test_json_input():
    """
    Test analyze_from_json method.
    
    Specification:
        - Should handle JSON input format
        - Should handle missing optional fields
        - Should handle None values
    """
    print_test("JSON Input Handling")
    
    analyzer = PRContentAnalyzer()
    
    # Test with complete data
    pr_data = {
        "title": "Fix bug",
        "body": "Fix critical issue",
        "files": ["src/main.py"],
        "diff": "- old\n+ new"
    }
    result = analyzer.analyze_from_json(pr_data)
    assert isinstance(result, PRAnalysis), "Must return valid analysis"
    assert_valid_analysis(result, "json_complete")
    
    # Test with minimal data (edge case)
    pr_data_minimal = {"title": "Test"}
    result_minimal = analyzer.analyze_from_json(pr_data_minimal)
    assert isinstance(result_minimal, PRAnalysis), "Must handle minimal data"
    assert_valid_analysis(result_minimal, "json_minimal")
    
    # Test with None values (edge case)
    pr_data_none = {
        "title": None,
        "body": None,
        "files": None,
        "diff": None
    }
    result_none = analyzer.analyze_from_json(pr_data_none)
    assert isinstance(result_none, PRAnalysis), "Must handle None values"
    assert_valid_analysis(result_none, "json_none")
    
    print("✅ PASSED: JSON input handled correctly")
    return True


def test_confidence_thresholds():
    """
    Test confidence score thresholds.
    
    Specification:
        - Labels below min_confidence should not be included
        - Only high-confidence labels should be returned
    """
    print_test("Confidence Threshold Validation")
    
    analyzer = PRContentAnalyzer()
    
    # Weak signal - should not trigger label
    result_weak = analyzer.analyze_pr(
        title="Minor update",
        body="Small change",
        files=["file.txt"],
        diff=""
    )
    
    # If any labels present, they must meet threshold
    for label in result_weak.labels:
        score = result_weak.confidence_scores[label]
        # Find the rule for this label
        rule = next(r for r in analyzer.LABEL_RULES if r.label == label)
        assert score >= rule.min_confidence, \
            f"Label {label} below threshold: {score} < {rule.min_confidence}"
    
    assert_valid_analysis(result_weak, "weak_signal")
    
    # Strong signal - should trigger label
    result_strong = analyzer.analyze_pr(
        title="Refactor improve optimize clean simplify",
        body="Major code quality improvements with refactoring",
        files=["src/main.py", "src/utils.py"],
        diff=""
    )
    
    assert "code-quality" in result_strong.labels, \
        "Strong signal should trigger label"
    
    assert_valid_analysis(result_strong, "strong_signal")
    
    print("✅ PASSED: Confidence thresholds working correctly")
    return True


def test_label_rules_validity():
    """
    Test that all label rules are valid.
    
    Specification:
        - All rules must have valid structure
        - Confidence thresholds must be valid
        - Keywords and patterns must be lists
    """
    print_test("Label Rules Validity")
    
    analyzer = PRContentAnalyzer()
    
    for rule in analyzer.LABEL_RULES:
        # Invariant: Valid confidence range
        assert 0.0 <= rule.min_confidence <= 1.0, \
            f"Invalid confidence for {rule.label}: {rule.min_confidence}"
        
        # Invariant: Non-empty label
        assert rule.label, f"Empty label in rule"
        
        # Invariant: Keywords is list
        assert isinstance(rule.keywords, list), \
            f"Keywords must be list for {rule.label}"
        
        # Invariant: File patterns is list
        assert isinstance(rule.file_patterns, list), \
            f"File patterns must be list for {rule.label}"
    
    print(f"✅ PASSED: All {len(analyzer.LABEL_RULES)} rules are valid")
    return True


def test_performance_pr():
    """
    Test performance label detection.
    
    Specification:
        - Performance keywords should trigger 'performance' label
        - May also trigger code-quality if optimization mentioned
    """
    print_test("Performance PR Detection")
    
    analyzer = PRContentAnalyzer()
    result = analyzer.analyze_pr(
        title="Improve query performance and reduce latency",
        body="Optimize database performance with caching to improve speed and throughput",
        files=["src/database.py", "benchmark/perf_test.py"],
        diff=""
    )
    
    # Postcondition: performance label present
    # (May also have code-quality, which is acceptable)
    assert "performance" in result.labels, \
        f"Expected 'performance' label, got: {result.labels}"
    
    # Validate invariants
    assert_valid_analysis(result, "performance_pr")
    
    print("✅ PASSED: Performance PR detected correctly")
    return True


def test_pages_health_pr():
    """
    Test pages-health label detection.
    
    Specification:
        - Changes to docs/*.html should trigger 'pages-health'
        - GitHub Pages related keywords should boost confidence
    """
    print_test("GitHub Pages PR Detection")
    
    analyzer = PRContentAnalyzer()
    result = analyzer.analyze_pr(
        title="Update GitHub Pages site",
        body="Fix styling issues on the documentation website",
        files=["docs/index.html", "docs/style.css", "docs/script.js"],
        diff=""
    )
    
    # Postcondition: pages-health label present
    assert "pages-health" in result.labels, \
        f"Expected 'pages-health' label, got: {result.labels}"
    
    # Validate invariants
    assert_valid_analysis(result, "pages_health_pr")
    
    print("✅ PASSED: GitHub Pages PR detected correctly")
    return True


def main():
    """Run all tests systematically."""
    print("=" * 70)
    print("🧪 PR Auto-Labeler Test Suite (@assert-specialist)")
    print("=" * 70)
    print("\nSpecification-driven testing with systematic coverage")
    print("Focus: Invariants, edge cases, and boundary conditions")
    print("=" * 70)
    
    # Define test suite in execution order
    tests = [
        # Basic functionality tests
        ("Label Rules Validity", test_label_rules_validity),
        
        # Edge cases first (assert-specialist approach)
        ("Empty PR", test_empty_pr),
        ("Large PR", test_large_pr),
        ("JSON Input", test_json_input),
        
        # Core label detection tests
        ("Code Quality", test_code_quality_pr),
        ("Documentation", test_documentation_pr),
        ("Testing", test_testing_pr),
        ("Bug Fix", test_bug_fix_pr),
        ("Enhancement", test_enhancement_pr),
        ("Security", test_security_pr),
        ("Performance", test_performance_pr),
        
        # System-specific labels
        ("Agent System", test_agent_system_pr),
        ("Workflow", test_workflow_pr),
        ("GitHub Pages", test_pages_health_pr),
        
        # Complex scenarios
        ("Multiple Labels", test_multiple_labels),
        ("Confidence Thresholds", test_confidence_thresholds),
    ]
    
    # Execute tests
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except AssertionError as e:
            print(f"\n❌ FAILED: {test_name}")
            print(f"   Assertion: {e}")
            results.append((test_name, False))
        except Exception as e:
            print(f"\n❌ ERROR: {test_name}")
            print(f"   Exception: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 Test Summary")
    print("=" * 70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print(f"\nPassed: {passed}/{total}")
    print(f"Failed: {total - passed}/{total}")
    
    if total - passed > 0:
        print("\n❌ Failed tests:")
        for test_name, result in results:
            if not result:
                print(f"   - {test_name}")
    
    print("\n" + "=" * 70)
    
    if passed == total:
        print("✅ All tests passed! System is specification-compliant.")
        print("=" * 70)
        return 0
    else:
        print(f"❌ {total - passed} test(s) failed - investigation required")
        print("=" * 70)
        return 1


if __name__ == '__main__':
    sys.exit(main())
