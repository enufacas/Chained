#!/bin/bash
# Test script for shell-common.sh library

set -e

echo "Testing shell-common.sh library..."
echo ""

# Source the library
source "$(dirname "$0")/shell-common.sh"

echo "1. Testing color variables..."
echo -e "  ${GREEN}GREEN${NC} - Should be green"
echo -e "  ${YELLOW}YELLOW${NC} - Should be yellow"
echo -e "  ${BLUE}BLUE${NC} - Should be blue"
echo -e "  ${RED}RED${NC} - Should be red"
echo ""

echo "2. Testing print_status function..."
print_status "OK" "This is an OK status"
print_status "WARN" "This is a WARNING status"
print_status "ERROR" "This is an ERROR status"
echo ""

echo "3. Testing print_header function..."
print_header "Sample Section Header"
echo ""

echo "4. Testing check_gh_cli function..."
# Test without requiring auth (since gh may not be authenticated in test environment)
if check_gh_cli "false"; then
    echo "  ✓ check_gh_cli works (gh is available)"
else
    echo "  ⚠ check_gh_cli returned false (gh not available - this is OK in test)"
fi
echo ""

echo "✅ All tests passed!"
