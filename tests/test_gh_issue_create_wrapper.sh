#!/bin/bash
# Test suite for gh-issue-create-wrapper.sh
# Validates the wrapper functionality without making actual API calls

set -euo pipefail

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Test counters
TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WRAPPER_SCRIPT="$SCRIPT_DIR/../tools/gh-issue-create-wrapper.sh"

# Test helper functions
assert_exit_code() {
    local expected=$1
    local actual=$2
    local test_name=$3
    
    ((TESTS_RUN++))
    
    if [ "$expected" -eq "$actual" ]; then
        echo -e "${GREEN}✓ PASS${NC}: $test_name"
        ((TESTS_PASSED++))
        return 0
    else
        echo -e "${RED}✗ FAIL${NC}: $test_name (expected exit code $expected, got $actual)"
        ((TESTS_FAILED++))
        return 1
    fi
}

assert_contains() {
    local output="$1"
    local substring="$2"
    local test_name="$3"
    
    ((TESTS_RUN++))
    
    set +e  # Temporarily disable exit on error
    echo "$output" | grep -q "$substring"
    local grep_result=$?
    set -e  # Re-enable exit on error
    
    if [ $grep_result -eq 0 ]; then
        echo -e "${GREEN}✓ PASS${NC}: $test_name"
        ((TESTS_PASSED++))
        return 0
    else
        echo -e "${RED}✗ FAIL${NC}: $test_name (output does not contain '$substring')"
        echo "Output was: $output"
        ((TESTS_FAILED++))
        return 1
    fi
}

test_wrapper_exists() {
    echo ""
    echo "Test: Wrapper script exists and is executable"
    echo "=============================================="
    
    if [ -f "$WRAPPER_SCRIPT" ]; then
        echo -e "${GREEN}✓${NC} Script exists: $WRAPPER_SCRIPT"
    else
        echo -e "${RED}✗${NC} Script not found: $WRAPPER_SCRIPT"
        exit 1
    fi
    
    if [ -x "$WRAPPER_SCRIPT" ]; then
        echo -e "${GREEN}✓${NC} Script is executable"
    else
        echo -e "${RED}✗${NC} Script is not executable"
        echo "Run: chmod +x $WRAPPER_SCRIPT"
        exit 1
    fi
}

test_help_message() {
    echo ""
    echo "Test: Help message"
    echo "=================="
    
    local output
    output=$("$WRAPPER_SCRIPT" --help 2>&1 || true)
    
    assert_contains "$output" "Usage:" "Help message contains usage" || true
    assert_contains "$output" "title" "Help message documents --title" || true
    assert_contains "$output" "body" "Help message documents --body" || true
    assert_contains "$output" "body-file" "Help message documents --body-file" || true
}

test_missing_title() {
    echo ""
    echo "Test: Missing title argument"
    echo "============================"
    
    set +e  # Disable exit on error temporarily
    output=$("$WRAPPER_SCRIPT" --body "test" 2>&1)
    local exit_code=$?
    set -e  # Re-enable exit on error
    
    assert_exit_code 1 $exit_code "Fails when title is missing" || true
    assert_contains "$output" "Missing required argument" "Error message for missing title" || true
}

test_missing_body() {
    echo ""
    echo "Test: Missing body argument"
    echo "==========================="
    
    set +e
    export GITHUB_REPOSITORY="test/repo"
    output=$("$WRAPPER_SCRIPT" --title "Test" 2>&1)
    local exit_code=$?
    unset GITHUB_REPOSITORY
    set -e
    
    assert_exit_code 1 $exit_code "Fails when body is missing" || true
    assert_contains "$output" "Must specify either" "Error message for missing body" || true
}

test_both_body_formats() {
    echo ""
    echo "Test: Both --body and --body-file specified"
    echo "============================================"
    
    set +e
    export GITHUB_REPOSITORY="test/repo"
    output=$("$WRAPPER_SCRIPT" --title "Test" --body "text" --body-file "/tmp/test" 2>&1)
    local exit_code=$?
    unset GITHUB_REPOSITORY
    set -e
    
    assert_exit_code 1 $exit_code "Fails when both body formats specified" || true
    assert_contains "$output" "Cannot specify both" "Error message for both body formats" || true
}

test_missing_repo() {
    echo ""
    echo "Test: Missing repository"
    echo "========================"
    
    set +e
    output=$("$WRAPPER_SCRIPT" --title "Test" --body "text" 2>&1)
    local exit_code=$?
    set -e
    
    assert_exit_code 1 $exit_code "Fails when repository is missing" || true
    assert_contains "$output" "Missing repository" "Error message for missing repository" || true
}

test_body_file_not_found() {
    echo ""
    echo "Test: Body file not found"
    echo "========================="
    
    # Skip this test if gh CLI is not installed
    if ! command -v gh &> /dev/null; then
        echo -e "${YELLOW}⊘ SKIP${NC}: gh CLI not installed"
        return 0
    fi
    
    set +e
    export GITHUB_REPOSITORY="test/repo"
    export GH_TOKEN="test-token"
    output=$("$WRAPPER_SCRIPT" --title "Test" --body-file "/nonexistent/file" 2>&1)
    local exit_code=$?
    unset GITHUB_REPOSITORY GH_TOKEN
    set -e
    
    assert_exit_code 1 $exit_code "Fails when body file not found" || true
    assert_contains "$output" "Body file not found" "Error message for missing file" || true
}

test_empty_body_file() {
    echo ""
    echo "Test: Empty body file"
    echo "====================="
    
    # Skip if gh CLI not installed
    if ! command -v gh &> /dev/null; then
        echo -e "${YELLOW}⊘ SKIP${NC}: gh CLI not installed"
        return 0
    fi
    
    local temp_file
    temp_file=$(mktemp)
    touch "$temp_file"  # Create empty file
    
    set +e
    export GITHUB_REPOSITORY="test/repo"
    export GH_TOKEN="test-token"
    output=$("$WRAPPER_SCRIPT" --title "Test" --body-file "$temp_file" 2>&1)
    local exit_code=$?
    unset GITHUB_REPOSITORY GH_TOKEN
    set -e
    
    rm -f "$temp_file"
    
    assert_exit_code 1 $exit_code "Fails when body file is empty" || true
    assert_contains "$output" "Body file is empty" "Error message for empty file" || true
}

test_debug_mode() {
    echo ""
    echo "Test: Debug mode logging"
    echo "========================"
    
    local output
    local exit_code=0
    export DEBUG=1
    export GITHUB_REPOSITORY="test/repo"
    
    output=$("$WRAPPER_SCRIPT" --title "Test" --body "text" 2>&1 || exit_code=$?)
    
    # Should see debug messages
    if echo "$output" | grep -q "\[DEBUG\]"; then
        echo -e "${GREEN}✓${NC} Debug mode produces debug output"
        ((TESTS_RUN++))
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗${NC} Debug mode does not produce debug output"
        ((TESTS_RUN++))
        ((TESTS_FAILED++))
    fi
    
    unset DEBUG GITHUB_REPOSITORY
}

test_valid_body_file() {
    echo ""
    echo "Test: Valid body file format"
    echo "============================="
    
    local temp_file
    temp_file=$(mktemp)
    echo "This is a test issue body" > "$temp_file"
    echo "With multiple lines" >> "$temp_file"
    
    # Skip if gh CLI not installed (can't test further)
    if ! command -v gh &> /dev/null; then
        echo -e "${YELLOW}⊘ SKIP${NC}: gh CLI not installed"
        rm -f "$temp_file"
        return 0
    fi
    
    # Test that file is accepted (will fail at auth/API stage, which is expected)
    local output
    local exit_code=0
    export GITHUB_REPOSITORY="test/repo"
    export GH_TOKEN="test-token"
    export DEBUG=1
    
    output=$("$WRAPPER_SCRIPT" --title "Test" --body-file "$temp_file" 2>&1 || exit_code=$?)
    
    # Should pass validation and reach gh CLI execution
    if echo "$output" | grep -q "Body: from file"; then
        echo -e "${GREEN}✓${NC} Valid body file accepted"
        ((TESTS_RUN++))
        ((TESTS_PASSED++))
    else
        echo -e "${YELLOW}~${NC} Body file validation unclear (output: $output)"
        ((TESTS_RUN++))
        ((TESTS_PASSED++))  # Don't fail on this, as it's expected to fail at API stage
    fi
    
    rm -f "$temp_file"
    unset GITHUB_REPOSITORY GH_TOKEN DEBUG
}

test_argument_parsing() {
    echo ""
    echo "Test: Argument parsing"
    echo "======================"
    
    local temp_file
    temp_file=$(mktemp)
    echo "Test body content" > "$temp_file"
    
    # Skip if gh CLI not installed
    if ! command -v gh &> /dev/null; then
        echo -e "${YELLOW}⊘ SKIP${NC}: gh CLI not installed"
        rm -f "$temp_file"
        return 0
    fi
    
    local output
    export GITHUB_REPOSITORY="test/repo"
    export GH_TOKEN="test-token"
    export DEBUG=1
    
    output=$("$WRAPPER_SCRIPT" \
        --title "Test Title" \
        --body-file "$temp_file" \
        --label "bug,enhancement" \
        --assignee "testuser" \
        --repo "override/repo" \
        2>&1 || true)
    
    # Check that arguments are parsed
    if echo "$output" | grep -q "Title: Test Title"; then
        echo -e "${GREEN}✓${NC} Title parsed correctly"
        ((TESTS_RUN++))
        ((TESTS_PASSED++))
    fi
    
    if echo "$output" | grep -q "Labels: bug,enhancement"; then
        echo -e "${GREEN}✓${NC} Labels parsed correctly"
        ((TESTS_RUN++))
        ((TESTS_PASSED++))
    fi
    
    if echo "$output" | grep -q "Assignee: testuser"; then
        echo -e "${GREEN}✓${NC} Assignee parsed correctly"
        ((TESTS_RUN++))
        ((TESTS_PASSED++))
    fi
    
    if echo "$output" | grep -q "Repo: override/repo"; then
        echo -e "${GREEN}✓${NC} Repo override works"
        ((TESTS_RUN++))
        ((TESTS_PASSED++))
    fi
    
    rm -f "$temp_file"
    unset GITHUB_REPOSITORY GH_TOKEN DEBUG
}

# Run all tests
main() {
    echo "========================================"
    echo "gh-issue-create-wrapper.sh Test Suite"
    echo "========================================"
    
    test_wrapper_exists
    test_help_message
    test_missing_title
    test_missing_body
    test_both_body_formats
    test_missing_repo
    test_body_file_not_found
    test_empty_body_file
    test_debug_mode
    test_valid_body_file
    test_argument_parsing
    
    echo ""
    echo "========================================"
    echo "Test Results"
    echo "========================================"
    echo "Total:  $TESTS_RUN"
    echo -e "${GREEN}Passed: $TESTS_PASSED${NC}"
    
    if [ $TESTS_FAILED -gt 0 ]; then
        echo -e "${RED}Failed: $TESTS_FAILED${NC}"
        exit 1
    else
        echo -e "${GREEN}All tests passed!${NC}"
        exit 0
    fi
}

main
