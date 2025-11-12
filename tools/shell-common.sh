#!/bin/bash

# Chained Shell Script Common Library
# Shared functions and variables for consistency across shell scripts
#
# Usage: source "$(dirname "$0")/tools/shell-common.sh"
#    or: source "$(dirname "$0")/../tools/shell-common.sh" (from subdirectories)

# Color codes for consistent output formatting
export GREEN='\033[0;32m'
export YELLOW='\033[1;33m'
export BLUE='\033[0;34m'
export RED='\033[0;31m'
export NC='\033[0m'  # No Color

# Check if GitHub CLI is available and authenticated
# Returns 0 if ready, 1 if not
check_gh_cli() {
    local require_auth="${1:-true}"
    
    # Check if gh CLI is available
    if ! command -v gh &> /dev/null; then
        echo -e "${RED}Error: GitHub CLI (gh) is required but not installed.${NC}" >&2
        echo "Please install it from: https://cli.github.com/" >&2
        return 1
    fi
    
    # Check if gh is authenticated (if required)
    if [ "$require_auth" = "true" ]; then
        if ! gh auth status &> /dev/null; then
            echo -e "${RED}Error: GitHub CLI is not authenticated.${NC}" >&2
            echo "Please run: gh auth login" >&2
            return 1
        fi
    fi
    
    return 0
}

# Print a status message with color
# Usage: print_status "OK|WARN|ERROR" "message"
print_status() {
    local status="$1"
    local message="$2"
    
    case "$status" in
        "OK")
            echo -e "${GREEN}✓${NC} $message"
            ;;
        "WARN")
            echo -e "${YELLOW}⚠${NC} $message"
            ;;
        "ERROR"|*)
            echo -e "${RED}✗${NC} $message"
            ;;
    esac
}

# Print a section header
# Usage: print_header "Section Title"
print_header() {
    local title="$1"
    echo ""
    echo -e "${BLUE}$title${NC}"
    # Print underline matching title length
    local len=${#title}
    printf '%*s\n' "$len" '' | tr ' ' '-'
    echo ""
}
