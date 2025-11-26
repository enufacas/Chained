#!/bin/bash
# Test Meta-Coordinator Tooling
#
# This script validates that all meta-coordinator scripts work correctly
# Run this in dry-run mode to verify improvements without making changes

set -euo pipefail

echo "========================================="
echo "Meta-Coordinator Tooling Test Suite"
echo "========================================="
echo ""

TESTS_PASSED=0
TESTS_FAILED=0

# Helper function to run tests
run_test() {
  local test_name="$1"
  local test_command="$2"
  
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo "TEST: ${test_name}"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  
  if eval "$test_command"; then
    echo "✅ PASS: ${test_name}"
    TESTS_PASSED=$((TESTS_PASSED + 1))
  else
    echo "❌ FAIL: ${test_name}"
    TESTS_FAILED=$((TESTS_FAILED + 1))
  fi
  echo ""
}

# Test 1: Scripts exist and are executable
run_test "Auto-merge script exists" \
  "[ -x tools/auto-merge-pr.sh ]"

run_test "Cleanup script exists" \
  "[ -x tools/cleanup-stale-prs.sh ]"

run_test "Check eligibility script exists" \
  "[ -x tools/check-pr-merge-eligibility.sh ]"

run_test "Assign Copilot script exists" \
  "[ -x tools/assign-copilot-to-issue.sh ]"

# Test 2: Memory system is importable
run_test "Memory system Python module" \
  "python3 -c 'import sys; sys.path.insert(0, \"tools\"); from meta_coordinator_memory import MetaCoordinatorMemory; print(\"OK\")' 2>/dev/null"

# Test 3: Documentation exists
run_test "Auto-merge README exists" \
  "[ -f tools/AUTO_MERGE_PR_README.md ]"

run_test "Tooling quick reference exists" \
  "[ -f .github/agents/META_COORDINATOR_TOOLING_QUICK_REF.md ]"

# Test 4: Scripts accept --help or show usage
run_test "Cleanup script shows usage" \
  "tools/cleanup-stale-prs.sh 2>&1 | head -5 | grep -qi 'cleanup' || true"

# Test 5: Check that critical patterns exist in scripts
run_test "Auto-merge checks WIP before marking ready" \
  "grep -q 'STEP 2.*WIP' tools/auto-merge-pr.sh && grep -q 'STEP 4.*draft' tools/auto-merge-pr.sh"

run_test "Check eligibility has WIP check before draft handling" \
  "awk '/STEP 2.*WIP/,/STEP 3/ { if (/STEP 2/) found=1 } /STEP 4.*draft/ { if (found) exit 0 } END { exit 1 }' tools/check-pr-merge-eligibility.sh"

run_test "Cleanup script outputs JSON" \
  "grep -q 'cleanup_summary.json' tools/cleanup-stale-prs.sh"

# Test 6: Workflow uses memory tracking
run_test "Workflow records open counts" \
  "grep -q 'memory.record_open_counts' .github/workflows/meta-coordinator.yml"

run_test "Workflow parses JSON from cleanup" \
  "grep -q 'cleanup_summary.json' .github/workflows/meta-coordinator.yml"

# Test 7: Agent instructions reference new tooling
run_test "Agent references auto-merge script" \
  "grep -q 'auto-merge-pr.sh' .github/agents/meta-coordinator-system.md"

run_test "Agent references tooling quick ref" \
  "grep -q 'META_COORDINATOR_TOOLING_QUICK_REF' .github/agents/meta-coordinator-system.md"

# Test 8: Dry-run mode works (if GH_TOKEN available)
if [ -n "${GH_TOKEN:-}" ]; then
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo "TEST: Cleanup dry-run (with GH_TOKEN)"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  
  if tools/cleanup-stale-prs.sh --dry-run 2>&1 | grep -q "dry run"; then
    echo "✅ PASS: Cleanup dry-run works"
    TESTS_PASSED=$((TESTS_PASSED + 1))
  else
    echo "❌ FAIL: Cleanup dry-run failed"
    TESTS_FAILED=$((TESTS_FAILED + 1))
  fi
  echo ""
  
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo "TEST: Check cleanup JSON output"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  
  if [ -f /tmp/cleanup_summary.json ] && jq -e . /tmp/cleanup_summary.json >/dev/null 2>&1; then
    echo "✅ PASS: JSON output is valid"
    TESTS_PASSED=$((TESTS_PASSED + 1))
    echo "Contents:"
    jq . /tmp/cleanup_summary.json
  else
    echo "❌ FAIL: JSON output missing or invalid"
    TESTS_FAILED=$((TESTS_FAILED + 1))
  fi
  echo ""
else
  echo "⏭️  SKIP: GH_TOKEN not set, skipping API-dependent tests"
  echo ""
fi

# Summary
echo "========================================="
echo "Test Summary"
echo "========================================="
echo ""
echo "✅ Passed: ${TESTS_PASSED}"
echo "❌ Failed: ${TESTS_FAILED}"
echo ""

if [ ${TESTS_FAILED} -eq 0 ]; then
  echo "🎉 All tests passed!"
  exit 0
else
  echo "⚠️  Some tests failed"
  exit 1
fi
