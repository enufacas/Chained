#!/bin/bash
# Manual Data Refresh Script for GitHub Pages Health
# Use this to update data files when timeline-update job is disabled
# Requires: gh CLI, jq

set -e

echo "📊 Manual GitHub Pages Data Refresh"
echo "===================================="
echo ""

# Check prerequisites
if ! command -v gh &> /dev/null; then
    echo "❌ Error: GitHub CLI (gh) is required but not installed"
    echo "   Install from: https://cli.github.com/"
    exit 1
fi

if ! command -v jq &> /dev/null; then
    echo "❌ Error: jq is required but not installed"
    echo "   Install jq to process JSON data"
    exit 1
fi

# Check if we're in the repository root
if [ ! -d "docs/data" ]; then
    echo "❌ Error: docs/data directory not found"
    echo "   Please run this script from the repository root"
    exit 1
fi

echo "✅ Prerequisites checked"
echo ""

# Create backup
echo "📦 Creating backup..."
mkdir -p docs/data/backups
timestamp=$(date +%Y%m%d-%H%M%S)
cp docs/data/stats.json "docs/data/backups/stats.json.${timestamp}"
cp docs/data/automation-log.json "docs/data/backups/automation-log.json.${timestamp}"
echo "✅ Backups created in docs/data/backups/"
echo ""

# Fetch current data
echo "🔄 Fetching latest repository data..."
echo "  - Issues..."
gh issue list --limit 100 --json number,title,body,state,createdAt,closedAt,labels,url > docs/data/issues.json

echo "  - Pull requests..."
gh pr list --limit 100 --state all --json number,title,body,state,createdAt,closedAt,mergedAt,url,author > docs/data/pulls.json

echo "  - Workflow runs..."
gh run list --limit 100 --json databaseId,name,status,conclusion,createdAt,displayTitle > docs/data/workflows.json

echo "✅ Data files updated"
echo ""

# Calculate statistics
echo "📊 Calculating statistics..."
total_issues=$(gh issue list --state all --limit 1000 --json number | jq '. | length')
open_issues=$(gh issue list --state open --limit 1000 --json number | jq '. | length')
closed_issues=$(gh issue list --state closed --limit 1000 --json number | jq '. | length')
total_prs=$(gh pr list --state all --limit 1000 --json number | jq '. | length')
merged_prs=$(gh pr list --state merged --limit 1000 --json number | jq '. | length')
ai_generated=$(gh issue list --state all --label "ai-generated" --limit 1000 --json number | jq '. | length')
copilot_assigned=$(gh issue list --state all --label "copilot-assigned" --limit 1000 --json number | jq '. | length')
completed=$(gh issue list --state all --label "completed" --limit 1000 --json number | jq '. | length')
in_progress=$(gh issue list --state open --label "in-progress" --limit 1000 --json number | jq '. | length')

# Calculate rates (handle division by zero)
if [ ${ai_generated} -gt 0 ]; then
    completion_rate=$(awk "BEGIN {printf \"%.1f\", (${completed}/${ai_generated})*100}")
else
    completion_rate="0.0"
fi

if [ ${total_prs} -gt 0 ]; then
    merge_rate=$(awk "BEGIN {printf \"%.1f\", (${merged_prs}/${total_prs})*100}")
else
    merge_rate="0.0"
fi

echo "  Total Issues: ${total_issues}"
echo "  Open Issues: ${open_issues}"
echo "  Total PRs: ${total_prs}"
echo "  Merged PRs: ${merged_prs}"
echo "✅ Statistics calculated"
echo ""

# Update stats.json
echo "💾 Updating stats.json..."
cat > docs/data/stats.json << EOF
{
  "total_issues": ${total_issues},
  "open_issues": ${open_issues},
  "closed_issues": ${closed_issues},
  "total_prs": ${total_prs},
  "merged_prs": ${merged_prs},
  "ai_generated": ${ai_generated},
  "copilot_assigned": ${copilot_assigned},
  "completed": ${completed},
  "in_progress": ${in_progress},
  "completion_rate": ${completion_rate},
  "merge_rate": ${merge_rate},
  "last_updated": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
}
EOF
echo "✅ stats.json updated"
echo ""

# Update automation log
echo "💾 Updating automation-log.json..."
cat > docs/data/automation-log.json << EOF
{
  "last_idea_generated": "$(gh issue list --label "ai-generated" --limit 1 --json createdAt --jq '.[0].createdAt // "N/A"')",
  "last_pr_merged": "$(gh pr list --state merged --limit 1 --json mergedAt --jq '.[0].mergedAt // "N/A"')",
  "last_issue_closed": "$(gh issue list --state closed --limit 1 --json closedAt --jq '.[0].closedAt // "N/A"')",
  "autonomous_actions_today": "$(date +%s | awk '{print int($1/86400)}')",
  "system_status": "active",
  "last_manual_refresh": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "refresh_note": "Manual data refresh - timeline-update job intentionally disabled"
}
EOF
echo "✅ automation-log.json updated"
echo ""

# Summary
echo "===================================="
echo "✅ Manual data refresh complete!"
echo "===================================="
echo ""
echo "Updated files:"
echo "  - docs/data/stats.json"
echo "  - docs/data/automation-log.json"
echo "  - docs/data/issues.json"
echo "  - docs/data/pulls.json"
echo "  - docs/data/workflows.json"
echo ""
echo "📅 Last Updated: $(date -u +'%Y-%m-%d %H:%M:%S UTC')"
echo ""
echo "Next steps:"
echo "  1. Review changes: git diff docs/data/"
echo "  2. Commit: git add docs/data/*.json"
echo "  3. Commit message: git commit -m '📊 Manual data refresh - $(date -u +%Y-%m-%d)'"
echo "  4. Push: git push"
echo ""
echo "Note: This data will become stale again in 12 hours"
echo "Consider re-enabling timeline-update job in .github/workflows/system-monitor.yml"
echo ""
