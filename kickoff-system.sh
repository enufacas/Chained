#!/bin/bash

################################################################################
# Chained System Kickoff Script
#
# An elegant initialization script that brings the Chained autonomous AI
# ecosystem to life. This script orchestrates system validation, configuration
# verification, and workflow activation with grace and clarity.
#
# Features:
#   • Pre-flight validation checks
#   • GitHub configuration verification
#   • Automated label creation
#   • Workflow initialization
#   • Comprehensive status reporting
#
# Usage:
#   ./kickoff-system.sh
#
# Requirements:
#   • GitHub CLI (gh) installed and authenticated
#   • Repository write access
#   • Proper GitHub Actions permissions configured
################################################################################

set -e  # Exit on any error

# Terminal color codes for beautiful output
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly RED='\033[0;31m'
readonly NC='\033[0m'  # No Color

################################################################################
# Display Functions
################################################################################

print_header() {
    echo "🚀 Chained System Kickoff"
    echo "========================="
    echo ""
}

print_step() {
    local step_number="$1"
    local step_name="$2"
    echo ""
    echo -e "${BLUE}Step ${step_number}: ${step_name}${NC}"
    echo "$(printf '%.0s-' {1..50})"
    echo ""
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

################################################################################
# Validation Functions
################################################################################

check_github_cli() {
    if ! command -v gh &> /dev/null; then
        print_error "GitHub CLI (gh) is required but not installed."
        echo ""
        echo "Please install it from: https://cli.github.com/"
        echo ""
        return 1
    fi
    return 0
}

check_authentication() {
    if ! gh auth status &> /dev/null; then
        print_error "GitHub CLI is not authenticated."
        echo ""
        echo "Please run: gh auth login"
        echo ""
        return 1
    fi
    return 0
}

################################################################################
# Main Script Logic
################################################################################

main() {
    print_header
    
    # Validate prerequisites
    check_github_cli || exit 1
    check_authentication || exit 1
    
    print_step 1 "Pre-flight Validation"

# Run validation script
if [ -f "./validate-system.sh" ]; then
    if ./validate-system.sh; then
        print_success "Validation passed!"
    else
        print_error "Validation failed. Please fix errors before proceeding."
        exit 1
    fi
else
    print_warning "Validation script not found, skipping validation."
fi

print_step 2 "Verify GitHub Configuration"

# Get repository info
REPO_INFO=$(gh repo view --json owner,name -q '.owner.login + "/" + .name')
echo "Repository: $REPO_INFO"

# Check workflow permissions
echo ""
echo "Checking required permissions..."
print_warning "Note: This script cannot verify all GitHub settings."
echo "Please ensure these are configured in your repository settings:"
echo "  1. Settings → Actions → General → Workflow permissions"
echo "     ✓ Read and write permissions"
echo "     ✓ Allow GitHub Actions to create and approve pull requests"
echo ""
echo "  2. Settings → Branches → Branch protection rules for 'main'"
echo "     ✓ Require a pull request before merging"
echo "     ✓ Required approvals: 0 (important!)"
echo "     ✓ Allow auto-merge"
echo "     ✓ Automatically delete head branches"
echo ""
echo "  3. Settings → Pages"
echo "     ✓ Source: Deploy from a branch"
echo "     ✓ Branch: main"
echo "     ✓ Folder: /docs"
echo ""

read -p "Have you configured these settings? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "Please configure the settings above and run this script again."
    echo "See QUICKSTART.md for detailed instructions."
    exit 1
fi

print_step 3 "Create Required Labels"

# Define labels as associative array
declare -A labels=(
    ["ai-generated"]="7057ff:Created by AI Idea Generator"
    ["copilot-assigned"]="0366d6:Assigned to Copilot"
    ["copilot"]="0366d6:Created by Copilot"
    ["automated"]="fbca04:Automated process"
    ["in-progress"]="fbca04:Work in progress"
    ["completed"]="0e8a16:Completed task"
    ["learning"]="d93f0b:Learning or insight"
    ["progress-report"]="c5def5:Progress tracking"
    ["enhancement"]="a2eeef:New feature or request"
)

echo "Creating labels..."
for label in "${!labels[@]}"; do
    IFS=':' read -r color description <<< "${labels[$label]}"
    
    # Check if label exists
    if gh label list --search "$label" 2>/dev/null | grep -q "$label"; then
        print_success "Label '$label' already exists"
    else
        if gh label create "$label" --color "$color" --description "$description" 2>/dev/null; then
            print_success "Created label '$label'"
        else
            print_warning "Could not create label '$label' (may already exist)"
        fi
    fi
done

print_step 4 "Initialize Learnings Directory"

# Ensure learnings directory exists
if [ ! -d "learnings" ]; then
    mkdir -p learnings
    print_success "Created learnings directory"
else
    print_success "Learnings directory already exists"
fi

# Check if learnings/README.md exists
if [ ! -f "learnings/README.md" ]; then
    print_warning "learnings/README.md not found (will be created by workflows)"
fi

print_step 5 "Trigger Initial Workflows"

echo "Would you like to trigger the initial workflows now?"
echo "This will:"
echo "  1. Generate the first AI idea"
echo "  2. Create an issue from that idea"
echo "  3. Start the autonomous cycle"
echo ""

read -p "Trigger workflows? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "Triggering workflows..."
    
    # Trigger idea generator
    if gh workflow run "idea-generator.yml" 2>/dev/null; then
        print_success "Triggered AI Idea Generator"
    else
        print_warning "Could not trigger AI Idea Generator (may need to wait or trigger manually)"
    fi
    
    # Wait a moment
    sleep 2
    
    # Trigger learning workflows
    if gh workflow run "learn-from-tldr.yml" 2>/dev/null; then
        print_success "Triggered Learn from TLDR"
    else
        print_warning "Could not trigger Learn from TLDR"
    fi
    
    if gh workflow run "learn-from-hackernews.yml" 2>/dev/null; then
        print_success "Triggered Learn from Hacker News"
    else
        print_warning "Could not trigger Learn from Hacker News"
    fi
    
    echo ""
    echo "Workflows triggered! Check the Actions tab to see progress:"
    echo "  https://github.com/$REPO_INFO/actions"
else
    echo ""
    echo "Skipping workflow triggers. You can trigger them manually later."
fi

echo ""
echo "================================================================"
echo -e "${GREEN}🎉 Kickoff Complete!${NC}"
echo "================================================================"
echo ""
echo "Your Chained perpetual AI motion machine is now initialized!"
echo ""
echo "What happens next:"
echo "  • Workflows will run on their scheduled times"
echo "  • Ideas will be generated automatically"
echo "  • Issues will be created and converted to PRs"
echo "  • AI will review and merge its own work"
echo "  • Timeline will be updated on GitHub Pages"
echo ""
echo "Monitor progress:"
echo "  📊 GitHub Pages: https://$(gh repo view --json owner,name -q '.owner.login').github.io/$(gh repo view --json name -q '.name')/"
echo "  🔄 Actions: https://github.com/$REPO_INFO/actions"
echo "  📋 Issues: https://github.com/$REPO_INFO/issues"
echo "  🔀 Pull Requests: https://github.com/$REPO_INFO/pulls"
echo ""
echo "Check system status:"
echo "  ./check-status.sh"
echo ""
print_warning "Tip: Come back in 24 hours to see what the AI has built!"
echo ""
}

# Execute main function
main
