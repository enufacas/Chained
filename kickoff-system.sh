#!/bin/bash

# Chained System Kickoff Script
# This script initializes and starts the perpetual AI motion machine

set -e

# Load shared library
source "$(dirname "$0")/tools/shell-common.sh"

echo "🚀 Chained System Kickoff"
echo "========================="
echo ""

# Check GitHub CLI prerequisites
if ! check_gh_cli; then
    echo ""
    exit 1
fi

echo -e "${BLUE}Step 1: Pre-flight Validation${NC}"
echo "------------------------------"
echo ""

# Run validation script
if [ -f "./validate-system.sh" ]; then
    if ./validate-system.sh; then
        echo -e "${GREEN}✓ Validation passed!${NC}"
    else
        echo -e "${RED}✗ Validation failed. Please fix errors before proceeding.${NC}"
        exit 1
    fi
else
    echo -e "${YELLOW}⚠ Validation script not found, skipping validation.${NC}"
fi

echo ""
echo -e "${BLUE}Step 2: Verify GitHub Configuration${NC}"
echo "------------------------------------"
echo ""

# Get repository info
REPO_INFO=$(gh repo view --json owner,name -q '.owner.login + "/" + .name')
echo "Repository: $REPO_INFO"

# Check workflow permissions
echo ""
echo "Checking required permissions..."
echo -e "${YELLOW}Note: This script cannot verify all GitHub settings.${NC}"
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

echo ""
echo -e "${BLUE}Step 3: Create Required Labels${NC}"
echo "-------------------------------"
echo ""

# Define labels
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
        echo -e "${GREEN}✓${NC} Label '$label' already exists"
    else
        if gh label create "$label" --color "$color" --description "$description" 2>/dev/null; then
            echo -e "${GREEN}✓${NC} Created label '$label'"
        else
            echo -e "${YELLOW}⚠${NC} Could not create label '$label' (may already exist)"
        fi
    fi
done

echo ""
echo -e "${BLUE}Step 4: Initialize Learnings Directory${NC}"
echo "---------------------------------------"
echo ""

# Ensure learnings directory exists
if [ ! -d "learnings" ]; then
    mkdir -p learnings
    echo -e "${GREEN}✓${NC} Created learnings directory"
else
    echo -e "${GREEN}✓${NC} Learnings directory already exists"
fi

# Check if learnings/README.md exists
if [ ! -f "learnings/README.md" ]; then
    echo -e "${YELLOW}⚠${NC} learnings/README.md not found (will be created by workflows)"
fi

echo ""
echo -e "${BLUE}Step 5: Trigger Initial Workflows${NC}"
echo "----------------------------------"
echo ""

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
        echo -e "${GREEN}✓${NC} Triggered AI Idea Generator"
    else
        echo -e "${YELLOW}⚠${NC} Could not trigger AI Idea Generator (may need to wait or trigger manually)"
    fi
    
    # Wait a moment
    sleep 2
    
    # Trigger learning workflows
    if gh workflow run "learn-from-tldr.yml" 2>/dev/null; then
        echo -e "${GREEN}✓${NC} Triggered Learn from TLDR"
    else
        echo -e "${YELLOW}⚠${NC} Could not trigger Learn from TLDR"
    fi
    
    if gh workflow run "learn-from-hackernews.yml" 2>/dev/null; then
        echo -e "${GREEN}✓${NC} Triggered Learn from Hacker News"
    else
        echo -e "${YELLOW}⚠${NC} Could not trigger Learn from Hacker News"
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
echo -e "${YELLOW}Tip: Come back in 24 hours to see what the AI has built!${NC}"
echo ""
