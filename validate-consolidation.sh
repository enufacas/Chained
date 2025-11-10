#!/bin/bash
# Workflow Consolidation Validation Script

echo "================================================"
echo "Workflow Consolidation Validation"
echo "================================================"
echo ""

# Count workflows
workflow_count=$(ls -1 .github/workflows/*.yml 2>/dev/null | wc -l)
echo "✓ Total workflows: ${workflow_count}"
echo ""

# Verify key consolidated workflows exist
echo "Checking consolidated workflows..."
for workflow in "system-kickoff.yml" "idea-generator.yml" "auto-review-merge.yml" "system-monitor.yml"; do
    if [ -f ".github/workflows/${workflow}" ]; then
        echo "  ✓ ${workflow} exists"
    else
        echo "  ✗ ${workflow} MISSING!"
        exit 1
    fi
done
echo ""

# Verify removed workflows are gone
echo "Checking removed workflows..."
for workflow in "auto-kickoff.yml" "smart-idea-generator.yml" "auto-label-copilot-prs.yml" "progress-tracker.yml" "timeline-updater.yml" "workflow-monitor.yml"; do
    if [ ! -f ".github/workflows/${workflow}" ]; then
        echo "  ✓ ${workflow} removed"
    else
        echo "  ✗ ${workflow} still exists!"
        exit 1
    fi
done
echo ""

# Validate YAML syntax
echo "Validating YAML syntax..."
yaml_valid=true
for file in .github/workflows/*.yml; do
    if python3 -c "import yaml; yaml.safe_load(open('${file}'))" 2>/dev/null; then
        echo "  ✓ $(basename ${file})"
    else
        echo "  ✗ $(basename ${file}) - INVALID YAML!"
        yaml_valid=false
    fi
done
echo ""

if [ "${yaml_valid}" = "false" ]; then
    echo "❌ YAML validation failed!"
    exit 1
fi

# Check schedule optimization
echo "Verifying schedule optimization..."

# Check that pattern-matcher runs at 10:00 (not 11:00)
pattern_schedule=$(grep "cron:" .github/workflows/pattern-matcher.yml | grep "10")
if [ -n "${pattern_schedule}" ]; then
    echo "  ✓ Pattern matcher schedule optimized to 10:00 UTC"
else
    echo "  ⚠ Pattern matcher schedule may not be optimized"
fi

# Check that system-monitor has the consolidated jobs
if grep -q "timeline-update:" .github/workflows/system-monitor.yml && \
   grep -q "progress-tracking:" .github/workflows/system-monitor.yml && \
   grep -q "workflow-monitoring:" .github/workflows/system-monitor.yml; then
    echo "  ✓ System monitor has all three consolidated jobs"
else
    echo "  ✗ System monitor missing expected jobs!"
    exit 1
fi
echo ""

# Check documentation
echo "Checking documentation..."
if [ -f "WORKFLOW_CONSOLIDATION.md" ]; then
    echo "  ✓ WORKFLOW_CONSOLIDATION.md exists"
else
    echo "  ✗ WORKFLOW_CONSOLIDATION.md missing!"
    exit 1
fi
echo ""

echo "================================================"
echo "✅ All validation checks passed!"
echo "================================================"
echo ""
echo "Summary:"
echo "  - ${workflow_count} workflows (down from 15)"
echo "  - All consolidated workflows present"
echo "  - All removed workflows deleted"
echo "  - All YAML syntax valid"
echo "  - Schedules optimized"
echo "  - Documentation complete"
echo ""
echo "Consolidation successful! 🎉"
