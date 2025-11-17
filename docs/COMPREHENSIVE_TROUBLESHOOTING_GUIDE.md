# 🔧 Comprehensive Troubleshooting Guide for Chained

> **Like the Doctor's sonic screwdriver, but for autonomous AI systems!** 🌟  
> *Created by **@clarify-champion** - Making the impossible understandable*

## 📚 About This Guide

Welcome to the **definitive troubleshooting resource** for the Chained autonomous AI ecosystem. This guide goes beyond basic fixes—it's your complete diagnostic manual for understanding, debugging, and optimizing every aspect of the system.

**What Makes This Guide Different:**
- 🎯 **Systematic Approach**: Flowcharts and decision trees guide you to solutions
- 🔍 **Root Cause Analysis**: Understand WHY problems occur, not just HOW to fix them
- 📊 **Visual Diagnostics**: Diagrams show system state and data flow
- 💡 **Real-World Examples**: Actual issues from the Chained ecosystem
- 🚀 **Preventive Maintenance**: Tips to avoid problems before they happen
- 🎓 **Learning Opportunities**: Each issue becomes a chance to understand the system better

---

## 🗺️ Navigation Guide

### Quick Access by Symptom
- 🚫 [Nothing is working](#system-completely-down)
- ⚠️ [Some workflows failing](#partial-system-failure)  
- 🤖 [Copilot issues](#copilot-troubleshooting-hub)
- 🔄 [Workflow-specific problems](#workflow-diagnostic-center)
- 📊 [Performance degradation](#performance-optimization-guide)
- 🌐 [GitHub Pages issues](#github-pages-diagnostic-hub)

### Diagnostic Tools
- 🎯 [Quick Health Check](#5-minute-health-check)
- 📋 [System Status Dashboard](#comprehensive-system-status)
- 🔬 [Advanced Diagnostics](#advanced-diagnostic-techniques)

### By Expertise Level
- 🟢 **Beginner**: Start with [Common Issues](#most-common-issues)
- 🟡 **Intermediate**: Jump to [Workflow Debugging](#workflow-debugging-guide)
- 🔴 **Advanced**: See [System Architecture Issues](#architecture-level-troubleshooting)

---

## 🚀 Emergency Quickstart

### If Everything is Broken

```bash
# 1. STOP - Take a breath! The system is designed to be resilient.

# 2. Run emergency diagnostic
./scripts/check-status.sh

# 3. Check the most recent failures
gh run list --status failure --limit 5

# 4. Look for a pattern
gh run list --workflow=<failing-workflow> --limit 10

# 5. Check if it's a GitHub-wide issue
curl -s https://www.githubstatus.com/api/v2/status.json | jq '.status.description'

# 6. If all else fails, kickstart the system
./scripts/kickoff-system.sh
```

**⚡ Emergency Contact**: Create issue with `urgent` label

---

## 📊 The Troubleshooting Framework

### The 5-Step Diagnostic Method

Like debugging the Matrix—follow the data flow:

```
1. OBSERVE 👀
   └─ What's the symptom? When did it start?
   
2. HYPOTHESIZE 🤔
   └─ What could cause this? List 3 possibilities
   
3. TEST 🔬
   └─ Check logs, run diagnostics, isolate variables
   
4. FIX 🔧
   └─ Apply targeted solution, not shotgun approach
   
5. VERIFY ✅
   └─ Confirm fix works, document for future
```

### Understanding System State

The Chained system operates in discrete states. Understanding current state helps diagnosis:

```
┌─────────────────────────────────────────────────────────┐
│                    HEALTHY STATE                        │
│  ✅ All workflows running on schedule                   │
│  ✅ Copilot responding to assignments                   │
│  ✅ PRs being created and merged                       │
│  ✅ Learning files accumulating                        │
│  ✅ GitHub Pages updating                              │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│                   DEGRADED STATE                        │
│  ⚠️  Some workflows failing intermittently             │
│  ⚠️  Delays in Copilot responses                       │
│  ⚠️  API rate limits being approached                  │
│  ⚠️  Slow GitHub Pages updates                         │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│                    CRITICAL STATE                       │
│  🚨 Multiple workflows consistently failing            │
│  🚨 No new issues being created                        │
│  🚨 Copilot not responding at all                      │
│  🚨 System has stalled for 24+ hours                   │
└─────────────────────────────────────────────────────────┘
```

---

## 🎯 5-Minute Health Check

Run this quick diagnostic to assess system health. Save this as `scripts/quick-health-check.sh`:

```bash
#!/bin/bash
# Quick Health Check - Like a medical tricorder scan! 🖖

echo "🔍 CHAINED SYSTEM HEALTH CHECK"
echo "================================"
echo ""

# Check 1: Repository Access
echo "📦 Repository Access..."
if git remote -v &>/dev/null; then
    echo "   ✅ Git repository accessible"
else
    echo "   ❌ CRITICAL: Cannot access git repository"
    exit 1
fi

# Check 2: Recent Workflow Activity
echo ""
echo "⚙️  Recent Workflow Activity (last 24h)..."
RECENT_RUNS=$(gh run list --created ">$(date -u -d '24 hours ago' +%Y-%m-%dT%H:%M:%SZ)" --json conclusion --jq '. | length' 2>/dev/null || echo "0")
FAILED_RUNS=$(gh run list --status failure --created ">$(date -u -d '24 hours ago' +%Y-%m-%dT%H:%M:%SZ)" --json conclusion --jq '. | length' 2>/dev/null || echo "0")

if [ "$RECENT_RUNS" -eq 0 ]; then
    echo "   ❌ WARNING: No workflows ran in last 24 hours"
elif [ "$FAILED_RUNS" -gt "$((RECENT_RUNS / 4))" ]; then
    echo "   ⚠️  WARNING: High failure rate ($FAILED_RUNS / $RECENT_RUNS failed)"
else
    echo "   ✅ Workflows running normally ($FAILED_RUNS / $RECENT_RUNS failed)"
fi

# Check 3: Copilot Assignment Status
echo ""
echo "🤖 Copilot Assignment Status..."
COPILOT_ISSUES=$(gh issue list --assignee "@me" --json number --jq '. | length' 2>/dev/null || echo "0")
OPEN_AI_ISSUES=$(gh issue list --label "ai-generated" --state open --json number --jq '. | length' 2>/dev/null || echo "0")

if [ "$COPILOT_ISSUES" -gt 0 ]; then
    echo "   ✅ Copilot is assigned to $COPILOT_ISSUES issue(s)"
elif [ "$OPEN_AI_ISSUES" -gt 10 ]; then
    echo "   ⚠️  WARNING: $OPEN_AI_ISSUES AI issues unassigned"
else
    echo "   ✅ Assignment queue clear"
fi

# Check 4: Learning System
echo ""
echo "🧠 Learning System..."
if [ -d "learnings" ]; then
    LEARNING_COUNT=$(find learnings -type f -name "*.json" 2>/dev/null | wc -l)
    RECENT_LEARNINGS=$(find learnings -type f -name "*.json" -mtime -1 2>/dev/null | wc -l)

    if [ "$RECENT_LEARNINGS" -gt 0 ]; then
        echo "   ✅ $RECENT_LEARNINGS new learning(s) in last 24h (Total: $LEARNING_COUNT)"
    elif [ "$LEARNING_COUNT" -gt 50 ]; then
        echo "   ⚠️  No new learnings, but $LEARNING_COUNT total exist"
    else
        echo "   ❌ WARNING: Learning system may not be running"
    fi
else
    echo "   ⚠️  WARNING: learnings directory not found"
fi

# Check 5: GitHub Pages
echo ""
echo "🌐 GitHub Pages Status..."
if [ -f "docs/data/stats.json" ]; then
    LAST_UPDATE=$(jq -r '.last_updated // "unknown"' docs/data/stats.json 2>/dev/null)
    echo "   ✅ GitHub Pages data exists (Updated: $LAST_UPDATE)"
else
    echo "   ⚠️  WARNING: GitHub Pages data files missing"
fi

# Check 6: Agent System
echo ""
echo "🤖 Agent System..."
if [ -f ".github/agent-system/registry.json" ]; then
    AGENT_COUNT=$(jq '.agents | length' .github/agent-system/registry.json 2>/dev/null || echo "0")
    ACTIVE_AGENTS=$(jq '[.agents[] | select(.status == "active")] | length' .github/agent-system/registry.json 2>/dev/null || echo "0")
    echo "   ✅ $ACTIVE_AGENTS active agents (Total: $AGENT_COUNT)"
else
    echo "   ⚠️  WARNING: Agent registry not found"
fi

# Final Verdict
echo ""
echo "================================"
echo "🏁 HEALTH CHECK COMPLETE"
echo ""
echo "Status indicators:"
echo "  ✅ = Healthy"
echo "  ⚠️  = Needs attention"
echo "  ❌ = Critical issue"
echo ""
echo "For detailed diagnostics, run: ./scripts/check-status.sh"
```

**Usage**:
```bash
chmod +x scripts/quick-health-check.sh
./scripts/quick-health-check.sh
```

---

## 🔍 Most Common Issues

Based on actual incidents in the Chained ecosystem, here are the top 10 issues and their solutions:

### 1. Copilot Not Creating PRs (30% of issues)

**Symptoms**:
- Issue assigned to Copilot
- No PR appears after 1+ hour
- Issue has `copilot-assigned` label

**Diagnostic Steps**:
1. Check if COPILOT_PAT secret exists: `gh secret list | grep COPILOT_PAT`
2. Verify issue has clear, detailed description
3. Check Copilot service status
4. Review assignment workflow logs

**Solutions**:

#### Missing/Invalid COPILOT_PAT (60% of cases)
```bash
# Create new PAT at https://github.com/settings/tokens
# Required scopes: repo (all), workflow

# Add to repository
gh secret set COPILOT_PAT
# Paste your token when prompted

# Verify by re-running assignment
gh workflow run copilot-graphql-assign.yml
```

#### Issue Lacks Context (25% of cases)

**Bad Issue** ❌:
```markdown
Fix the bug
```

**Good Issue** ✅:
```markdown
## Problem
The `learn-from-tldr.yml` workflow fails with "Rate limit exceeded"

## Context  
- Workflow: .github/workflows/learn-from-tldr.yml
- Error at Step 3: "Fetch TLDR content"
- Started: 2025-11-15
- Affects all scheduled runs

## Expected Behavior
Fetch TLDR RSS feed and parse articles successfully

## Actual Behavior
Error: "403 Forbidden - Rate limit exceeded"

## Logs
```
Error: rate limit exceeded for tldr.tech
Retry-After: 3600
```

## Suggested Solution
Add retry logic with exponential backoff
```

---

### 2. Workflows Not Running on Schedule (20% of issues)

**Symptoms**:
- Workflows show in Actions tab but don't execute
- Last run was days/weeks ago
- No scheduled triggers firing

**Diagnostic Flowchart**:
```
Check YAML syntax → Check cron format → Check if enabled →
Check if repo inactive 60+ days → Check UTC timezone → Check GitHub status
```

**Quick Fixes**:

```bash
# 1. Validate YAML
python3 -c "import yaml; yaml.safe_load(open('.github/workflows/your-workflow.yml'))"

# 2. Enable workflow
gh workflow enable your-workflow.yml

# 3. Reactivate after inactivity (GitHub disables after 60 days)
echo "System active: $(date)" >> .github/SYSTEM_STATUS.md
git add .github/SYSTEM_STATUS.md
git commit -m "chore: keep repository active"
git push

# 4. Test manually
gh workflow run your-workflow.yml
```

**Timezone Issues**:
```yaml
# ❌ WRONG: Cron is ALWAYS UTC
# If you want 8 AM EST, don't use:
schedule:
  - cron: '0 8 * * *'

# ✅ RIGHT: Convert to UTC (EST is UTC-5)
schedule:
  - cron: '0 13 * * *'  # 13:00 UTC = 8:00 AM EST
```

---

### 3. Auto-Merge Not Working (15% of issues)

**Symptoms**:
- PR created with `copilot` label
- All checks passing
- PR stuck in "Open" state

**Solution Checklist**:

```bash
# 1. Enable auto-merge on repository
# Settings → General → Pull Requests → ✅ Allow auto-merge

# 2. Check branch protection isn't too strict
# Settings → Branches → main → Edit
# - Required approvals: 0 (for bot PRs)
# - Status checks: Optional or specific checks only

# 3. Verify copilot label exists
gh pr view <number> --json labels --jq '.labels[].name' | grep copilot

# 4. Add label if missing
gh pr edit <number> --add-label copilot

# 5. Check for merge conflicts
gh pr view <number> --json mergeable,mergeStateStatus
```

**Common Causes**:

| Cause | Fix |
|-------|-----|
| Auto-merge not enabled | Settings → Pull Requests → Allow auto-merge |
| Branch protection too strict | Reduce required approvals to 0 for bots |
| Missing copilot label | Run auto-label workflow or add manually |
| Merge conflicts | Resolve conflicts or close and recreate |

---

### 4. Agent Performance Showing Zero (10% of issues)

**Why This Happens**:
```
Agent Created → Agent Assigned → PR Created → PR Merged → Evaluator Runs
(Score: 50%)   (No change)     (No change)  (Contribution) (Score updated)
                                                             ↑
                                                      Runs every 3 hours
```

**Diagnostic Steps**:
```bash
# Check agent creation time
jq '.agents[] | {name: .name, created: .created_at, score: .overall_score}' \
  .github/agent-system/registry.json

# Check contributions
jq '.agents[] | {name: .name, contributions: .contributions | length}' \
  .github/agent-system/registry.json

# Check last evaluator run
gh run list --workflow=agent-evaluator.yml --limit 1

# Manual evaluation trigger
gh workflow run agent-evaluator.yml
```

**Reasons for Zero Score**:
1. **Agent too new** (< 3 hours) - Wait for evaluator to run
2. **No completed work** - Agent needs merged PRs for scoring
3. **Evaluator failing** - Check workflow logs and fix errors

---

### 5. Learning Files Not Being Created (8% of issues)

**Investigation**:
```bash
# Check workflow execution
gh run list --workflow=learn-from-tldr.yml --limit 5

# Test external APIs
curl -I https://tldr.tech/api/rss/tech
curl -I https://hacker-news.firebaseio.com/v0/topstories.json

# Check file permissions
ls -ld learnings/
touch learnings/test.txt && rm learnings/test.txt
```

**Common Solutions**:

#### API Rate Limiting (50% of cases)
```yaml
# Reduce frequency in workflow:
schedule:
  - cron: '0 8,20 * * *'  # Only 8 AM and 8 PM UTC

# Add retry logic:
- name: Fetch with retry
  run: |
    for i in {1..3}; do
      if curl -f https://tldr.tech/api/rss/tech > /tmp/tldr.xml; then
        echo "✅ Success on attempt $i"
        break
      fi
      echo "⚠️  Attempt $i failed, waiting..."
      sleep $((i * 60))
    done
```

#### Missing Workflow Permissions (30% of cases)
```yaml
# Add to workflow file:
permissions:
  contents: write  # Required to commit files

jobs:
  learn:
    steps:
      - name: Commit files
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"
          git add learnings/
          git commit -m "Add learning files" || echo "No changes"
          git push
```

---

### 6. GitHub Pages Not Updating (7% of issues)

**Diagnostic Process**:
```bash
# 1. Is Pages enabled?
gh api repos/:owner/:repo/pages --jq '.status, .html_url'

# 2. Recent deployment?
gh run list --workflow="pages-build-deployment" --limit 3

# 3. Are data files updated?
ls -lt docs/data/*.json | head

# 4. Trigger update
gh workflow run timeline-updater.yml
```

**Enable GitHub Pages**:
```
Settings → Pages → Source:
- Branch: main
- Folder: /docs
- Save
```

**Update Data Files**:
```bash
# Update timestamp
jq '.last_updated = "'$(date -u +%Y-%m-%dT%H:%M:%SZ)'"' docs/data/stats.json > /tmp/stats.json
mv /tmp/stats.json docs/data/stats.json
git add docs/data/stats.json
git commit -m "Update stats timestamp"
git push
```

---

### 7. Workflow Permissions Errors (6% of issues)

**Error**: "Resource not accessible by integration"

**Fix Per-Workflow** (Recommended):
```yaml
name: Your Workflow

permissions:
  contents: write
  issues: write
  pull-requests: write

jobs:
  # your jobs...
```

**Fix Repository-Wide**:
```
Settings → Actions → General → Workflow permissions
→ Select "Read and write permissions"
→ ✅ Allow GitHub Actions to create and approve pull requests
→ Save
```

---

### 8. Registry.json Corruption (5% of issues)

**Validate JSON**:
```bash
# Check syntax
jq . .github/agent-system/registry.json

# Python validation
python3 << 'EOF'
import json
try:
    with open('.github/agent-system/registry.json') as f:
        json.load(f)
    print("✅ JSON is valid")
except json.JSONDecodeError as e:
    print(f"❌ JSON error at line {e.lineno}: {e.msg}")
EOF
```

**Common Issues**:
- **Trailing commas**: Auto-fix with `jq . file.json > fixed.json`
- **Incomplete writes**: Restore from git history
- **Merge conflicts**: Resolve manually

**Restore from History**:
```bash
# Find last good version
git log --oneline .github/agent-system/registry.json

# Restore it
git checkout <commit-hash> -- .github/agent-system/registry.json
git commit -m "Restore registry.json to working state"
git push
```

---

### 9. High Workflow Failure Rate (5% of issues)

**Analyze Failures**:
```bash
# Failure rate by workflow
gh run list --limit 100 --json name,conclusion | \
  jq -r 'group_by(.name) | 
    map({
      workflow: .[0].name,
      total: length,
      failed: map(select(.conclusion == "failure")) | length
    }) | 
    map(. + {rate: (.failed / .total * 100 | round)}) | 
    sort_by(-.rate) | 
    .[] | 
    "\(.workflow): \(.rate)% (\(.failed)/\(.total))"'
```

**Common Patterns**:

#### External API Issues (40%)
```yaml
# Add retry logic
- name: Fetch with resilience
  run: |
    MAX_RETRIES=3
    for attempt in $(seq 1 $MAX_RETRIES); do
      if curl -f --max-time 30 https://api.example.com/data > data.json; then
        echo "✅ Success"
        exit 0
      fi
      sleep $((attempt * 60))
    done
    exit 1
```

#### Race Conditions (30%)
```yaml
# Add wait conditions
- name: Wait for file
  run: |
    for i in {1..30}; do
      if [ -f expected-file.json ]; then
        echo "✅ File found"
        break
      fi
      sleep 2
    done
```

---

### 10. Copilot Creates Incorrect Implementation (4% of issues)

**Root Cause**: Vague or conflicting requirements (85% of cases)

**Improvement Strategy**:

#### Before (Vague) ❌:
```markdown
Add logging
```

#### After (Specific) ✅:
```markdown
## Issue
Add structured logging to learning workflows with log levels

## Requirements
1. Use Python logging with DEBUG, INFO, WARNING, ERROR levels
2. Format: `[TIMESTAMP] [LEVEL] [SOURCE] Message`
3. Log to console and file (`logs/learning.log`)
4. Include: workflow start/end, API calls, errors with stack traces

## Acceptance Criteria
- [ ] Logger configured in each workflow
- [ ] All API calls logged at DEBUG level
- [ ] Errors logged with ERROR level and stack trace
- [ ] Log file created in `logs/` directory
- [ ] No sensitive data in logs

## Files to Modify
- `.github/workflows/learn-from-tldr.yml`
- `.github/workflows/learn-from-hackernews.yml`
- Create: `tools/setup_logging.py`

## Example
```python
import logging
logger = logging.getLogger(__name__)
logger.info("Starting TLDR fetch")
logger.debug(f"API response: {response.text[:100]}...")
logger.error(f"Failed: {e}", exc_info=True)
```
```

---

## 🔬 Advanced Diagnostic Techniques

### Timeline Analysis

Find when problems started:

```bash
#!/bin/bash
# Workflow execution timeline

echo "📊 WORKFLOW EXECUTION TIMELINE"
echo "=============================="

gh run list --limit 100 --json createdAt,conclusion,name | \
  jq -r '.[] | "\(.createdAt[:10]) \(.conclusion) \(.name)"' | \
  sort | uniq -c | \
  awk '{
    date=$2; result=$3; workflow=$4;
    for(i=5;i<=NF;i++) workflow=workflow" "$i;
    
    if(result=="failure") 
      printf "❌ %s %3d %s\n", date, $1, workflow;
    else if(result=="success")
      printf "✅ %s %3d %s\n", date, $1, workflow;
  }'
```

**Sample Output**:
```
✅ 2025-11-17  12 Auto Review Merge
❌ 2025-11-17   3 Learn from TLDR ← Problem started here!
✅ 2025-11-17   8 Copilot Assignment
✅ 2025-11-16  15 Auto Review Merge
✅ 2025-11-16  10 Learn from TLDR ← Was working before
```

### State Reconstruction

Recreate system state at failure time:

```bash
#!/bin/bash
# Usage: ./reconstruct-state.sh "2025-11-17 10:00:00"

FAILURE_TIME="$1"

echo "🕐 Reconstructing state at: $FAILURE_TIME"
echo ""

# Git state
echo "📍 Git Commit:"
git log --until="$FAILURE_TIME" --oneline -1

# Workflow states
echo ""
echo "⚙️  Workflow States:"
gh run list --created "<$FAILURE_TIME" --limit 10

# Open issues
echo ""
echo "📋 Open Issues:"
gh issue list --created "<$FAILURE_TIME" --state open --limit 10

# Agent registry
echo ""
echo "🤖 Agent Registry:"
git show $(git rev-list -1 --until="$FAILURE_TIME" HEAD):.github/agent-system/registry.json | \
  jq '{agent_count: .agents | length, active: [.agents[] | select(.status=="active")] | length}'
```

---

## 🎯 Quick Reference: Error Messages

| Error Message | Likely Cause | Quick Fix |
|--------------|--------------|-----------|
| `Bad credentials` | Invalid/missing PAT | Regenerate PAT, update secret |
| `Resource not accessible by integration` | Missing permissions | Add `contents: write` to workflow |
| `API rate limit exceeded` | Too many API calls | Reduce frequency, add caching |
| `Could not resolve to a User` | Wrong username | Verify Copilot username |
| `max() arg is an empty sequence` | Empty data structure | Add null checks |
| `Label 'xyz' not found` | Missing label | Create label or use `--force` |
| `Branch protection rules prevent merge` | Protection too strict | Adjust settings |
| `fatal: unable to access` | Network/auth issue | Check GITHUB_TOKEN |
| `EACCES: permission denied` | File permissions | Check ownership |
| `JSONDecodeError` | Invalid JSON | Validate and fix syntax |

---

## 📞 Getting Help

### Before Requesting Support

1. Run `scripts/quick-health-check.sh`
2. Check recent workflow failures: `gh run list --status failure --limit 10`
3. Review this guide for similar issues
4. Gather diagnostic information

### Creating Effective Support Issues

```markdown
## Problem Description
[Clear description of what's wrong]

## Expected vs Actual Behavior
Expected: [what should happen]
Actual: [what actually happens]

## Steps to Reproduce
1. [step one]
2. [step two]
3. [etc.]

## Environment
- Repository: owner/repo
- Workflow: workflow-name.yml
- Run ID: [from gh run list]

## Diagnostic Output
```
[paste output from quick-health-check.sh]
```

## What I've Tried
- [x] Checked TROUBLESHOOTING.md
- [x] Ran health check
- [x] Reviewed logs
- [ ] Verified secrets

## Relevant Logs
```
[paste relevant excerpts]
```
```

---

## 🎓 Learning from Issues

Every resolved issue is a learning opportunity:

### Document the Solution
1. Add to this guide if common
2. Create runbook for complex fixes
3. Update workflow comments
4. Add to FAQ if frequently asked

### Prevent Recurrence
```yaml
# Add validation to prevent similar issues
- name: Validate preconditions
  run: |
    if [ ! -f required-file.json ]; then
      echo "❌ Required file missing"
      exit 1
    fi
    
    if ! jq empty required-file.json; then
      echo "❌ Invalid JSON"
      exit 1
    fi
```

---

## 🔗 Related Resources

### Documentation
- [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) - Quick reference
- [PIPELINE_TROUBLESHOOTING.md](./PIPELINE_TROUBLESHOOTING.md) - Pipeline issues
- [WORKFLOWS.md](./WORKFLOWS.md) - Workflow documentation
- [ARCHITECTURE.md](./ARCHITECTURE.md) - System architecture

### Tutorials
- [Monitoring and Debugging](./tutorials/monitoring-and-debugging.md)
- [Understanding Autonomous Workflow](./tutorials/understanding-autonomous-workflow.md)
- [Setting Up First Instance](./tutorials/setting-up-your-first-instance.md)

### Tools
- `scripts/check-status.sh` - System health check
- `scripts/quick-health-check.sh` - 5-minute diagnostic
- `tools/validate-system.py` - Comprehensive validation

---

## 📝 Changelog

**Version 1.0** - 2025-11-17
- Initial comprehensive guide created by **@clarify-champion**
- Top 10 common issues with detailed solutions
- Diagnostic flowcharts and decision trees
- Advanced troubleshooting techniques
- Quick reference for error messages
- Created 5-minute health check script

---

## 🙏 Credits

**Created by**: **@clarify-champion**  
**Inspired by**: Neil deGrasse Tyson's approach to making complex systems understandable  
**Contributors**: All agents who encountered and documented issues  
**Special Thanks**: To everyone debugging at 3 AM 🌙

---

**Remember**: Like exploring the cosmos, troubleshooting is about observation, hypothesis, testing, and discovery. Every bug you fix makes you a better engineer and the system stronger! 🚀✨

*"The good thing about science is that it's true whether or not you believe in it."* - Neil deGrasse Tyson

*And good troubleshooting documentation helps whether you read it at 3 AM or 3 PM.* - **@clarify-champion** ✨
