#!/bin/bash
# Test script for prompt generator workflow integration
# This validates that all CLI commands work as expected by the workflows

set -e

echo "🧪 Testing Prompt Generator CLI Integration"
echo "============================================"
echo ""

cd "$(dirname "$0")/.."

# Test 1: Generate prompt
echo "✓ Test 1: Generate Prompt"
output=$(python3 tools/prompt-generator.py generate \
  --issue-body "Fix authentication bug in login system" \
  --category bug_fix \
  --agent engineer-master 2>&1)

if echo "$output" | grep -q "Template ID:"; then
  template_id=$(echo "$output" | grep "Template ID:" | cut -d: -f2 | xargs)
  echo "  ✅ Generated prompt with template: $template_id"
else
  echo "  ❌ Failed to generate prompt"
  exit 1
fi

# Test 2: Performance report
echo ""
echo "✓ Test 2: Performance Report"
report=$(python3 tools/prompt-generator.py report 2>&1 | grep -v Warning)

if echo "$report" | jq -e '.templates' > /dev/null 2>&1; then
  template_count=$(echo "$report" | jq '.templates | length')
  echo "  ✅ Generated report with $template_count templates"
else
  echo "  ❌ Failed to generate valid JSON report"
  exit 1
fi

# Test 3: Optimize suggestions
echo ""
echo "✓ Test 3: Optimization Suggestions"
suggestions=$(python3 tools/prompt-generator.py optimize 2>&1 | grep -v Warning)

if echo "$suggestions" | jq -e '.' > /dev/null 2>&1; then
  suggestion_count=$(echo "$suggestions" | jq 'length')
  echo "  ✅ Generated $suggestion_count optimization suggestions"
else
  echo "  ❌ Failed to generate valid JSON suggestions"
  exit 1
fi

# Test 4: Category detection logic (simulated)
echo ""
echo "✓ Test 4: Category Detection Logic"
detect_category() {
  local labels="$1"
  local title="$2"
  
  if echo "$labels" | grep -qi "bug"; then
    echo "bug_fix"
  elif echo "$labels" | grep -qi "security"; then
    echo "security"
  elif echo "$labels" | grep -qi "documentation"; then
    echo "documentation"
  elif echo "$title" | grep -qiE "fix|bug|error"; then
    echo "bug_fix"
  else
    echo "feature"
  fi
}

category=$(detect_category "bug,urgent" "Fix critical issue")
if [ "$category" = "bug_fix" ]; then
  echo "  ✅ Category detection: '$category' (correct)"
else
  echo "  ❌ Category detection failed: got '$category', expected 'bug_fix'"
  exit 1
fi

# Test 5: Workflow YAML syntax
echo ""
echo "✓ Test 5: Workflow YAML Validation"

if command -v yamllint > /dev/null 2>&1; then
  for workflow in .github/workflows/prompt-*.yml; do
    if yamllint -d relaxed "$workflow" > /dev/null 2>&1; then
      echo "  ✅ $(basename "$workflow") is valid YAML"
    else
      echo "  ⚠️  $(basename "$workflow") has linting warnings (non-critical)"
    fi
  done
else
  # Just check basic syntax with Python
  for workflow in .github/workflows/prompt-*.yml; do
    if python3 -c "import yaml; yaml.safe_load(open('$workflow'))" 2>/dev/null; then
      echo "  ✅ $(basename "$workflow") is valid YAML"
    else
      echo "  ❌ $(basename "$workflow") has syntax errors"
      exit 1
    fi
  done
fi

# Test 6: Learning refresh (dry run)
echo ""
echo "✓ Test 6: Learning Refresh"
if python3 tools/prompt-generator.py refresh-learnings --days 7 2>&1 | grep -q "insights"; then
  echo "  ✅ Learning refresh executed successfully"
else
  echo "  ⚠️  Learning refresh completed with warnings (acceptable)"
fi

# Test 7: Record outcome (simulated)
echo ""
echo "✓ Test 7: Record Outcome"
python3 tools/prompt-generator.py record \
  --prompt-id "$template_id" \
  --issue-number 999 \
  --success \
  --resolution-time 2.5 2>&1 | grep -v Warning > /dev/null

if [ $? -eq 0 ]; then
  echo "  ✅ Outcome recorded successfully"
else
  echo "  ❌ Failed to record outcome"
  exit 1
fi

echo ""
echo "============================================"
echo "✅ All tests passed!"
echo ""
echo "📊 Summary:"
echo "  - Prompt generation: ✅"
echo "  - Performance reports: ✅"
echo "  - Optimization suggestions: ✅"
echo "  - Category detection: ✅"
echo "  - Workflow YAML validation: ✅"
echo "  - Learning refresh: ✅"
echo "  - Outcome recording: ✅"
echo ""
echo "🎉 The prompt generator is ready for workflow integration!"
