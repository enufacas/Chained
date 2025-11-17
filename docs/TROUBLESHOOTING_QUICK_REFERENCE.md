# 🎯 Troubleshooting Quick Reference Card

> **Like a cheat sheet for the final exam, but the universe is the classroom!** 🌟  
> *Created by **@clarify-champion** - Your friendly neighborhood problem solver*

## 🚨 Emergency Commands

```bash
# System completely down?
./scripts/check-status.sh
gh run list --status failure --limit 5
curl -s https://www.githubstatus.com/api/v2/status.json | jq '.status.description'

# Need quick health check?
./scripts/quick-health-check.sh

# Restart the system?
./scripts/kickoff-system.sh
```

---

## 🎯 Most Common Issues (95% of problems)

### 1. Copilot Not Creating PRs (30%)
```bash
# Check if COPILOT_PAT exists
gh secret list | grep COPILOT_PAT

# If missing:
gh secret set COPILOT_PAT

# Verify issue has context
gh issue view [issue-number] --json body -q '.body' | wc -l  # Should be > 50 lines
```

**Quick Fixes:**
- ✅ Add COPILOT_PAT secret
- ✅ Add detailed context to issue
- ✅ Check Copilot service status: https://www.githubstatus.com

### 2. Workflows Not Running (20%)
```bash
# Check if workflow is enabled
gh workflow list

# Enable workflow
gh workflow enable [workflow-name]

# Test manually
gh workflow run [workflow-name]

# Check syntax
yamllint .github/workflows/*.yml
```

**Quick Fixes:**
- ✅ Enable workflow in Actions tab
- ✅ Fix YAML syntax errors
- ✅ Check cron expression is valid
- ✅ Verify permissions in workflow file

### 3. Auto-Merge Not Working (15%)
```bash
# Check auto-merge status
gh pr view [pr-number] --json autoMergeRequest

# Enable auto-merge
gh pr merge [pr-number] --auto --squash

# Check labels
gh pr view [pr-number] --json labels
```

**Quick Fixes:**
- ✅ Enable auto-merge on PR
- ✅ Add required labels (`automated`, `copilot`)
- ✅ Reduce branch protection restrictions
- ✅ Resolve merge conflicts

### 4. Agent Performance Zero (10%)
```bash
# Check agent age
cat .github/agent-system/registry.json | jq '.agents[] | select(.performance.quality_score == 0)'

# Check evaluator workflow
gh run list --workflow=agent-evaluator --limit 5
```

**Quick Fixes:**
- ✅ Wait 3+ hours for first evaluation
- ✅ Verify evaluator workflow runs
- ✅ Check registry.json is valid JSON
- ✅ Ensure agent has completed work

### 5. Learning Files Not Created (8%)
```bash
# Check API rate limit
gh api rate_limit

# Check recent runs
gh run list --workflow=tldr-learning --limit 5

# Test API endpoint
curl -I https://tldr.tech/api/latest
```

**Quick Fixes:**
- ✅ Wait for rate limit reset
- ✅ Reduce workflow frequency
- ✅ Add `contents: write` permission
- ✅ Test API endpoints manually

---

## 🔍 Error Messages → Instant Fixes

| Error Message | Instant Fix | Time |
|--------------|-------------|------|
| `Resource not accessible by integration` | Add `contents: write` permission to workflow | 2 min |
| `Bad credentials` | Regenerate COPILOT_PAT and update secret | 3 min |
| `Auto merge is not supported` | Enable auto-merge in repo settings | 1 min |
| `File not found` | Check file path is absolute, not relative | 1 min |
| `Invalid JSON` | Validate with `jq .` and restore from git | 2 min |
| `Rate limit exceeded` | Wait 1 hour or reduce workflow frequency | 60 min |
| `Workflow is not enabled` | Enable in Actions tab | 1 min |
| `Required status checks` | Update branch protection rules | 3 min |
| `Merge conflict` | Resolve conflicts in PR | 5 min |
| `Service unavailable` | Check GitHub status page | Variable |

---

## 📊 Diagnostic Decision Tree

```
Problem?
├─ Nothing works → Emergency diagnostic → Check GitHub status
├─ Copilot silent → Check COPILOT_PAT → Verify issue quality
├─ Workflow fails → Check logs → Fix specific error
├─ Agent zero score → Wait 3h → Check evaluator
├─ Pages stale → Trigger update → Clear browser cache
└─ Learning fails → Check rate limit → Test APIs
```

---

## 🎯 5-Step Diagnostic Method

1. **OBSERVE** 👀 - What's broken? When did it start?
2. **HYPOTHESIZE** 🤔 - List 3 possible causes
3. **TEST** 🔬 - Check logs, run diagnostics
4. **FIX** 🔧 - Apply targeted solution
5. **VERIFY** ✅ - Confirm it works

---

## 🔧 Essential Commands

### Git & GitHub
```bash
# Check status
git status
gh repo view

# Check workflows
gh run list --limit 10
gh workflow list

# Check issues
gh issue list --state open --limit 10

# Check PRs
gh pr list --state open --limit 10
```

### Workflow Debugging
```bash
# View failed runs
gh run list --status failure --limit 5

# View specific run
gh run view [run-id]

# View logs
gh run view [run-id] --log

# Re-run failed jobs
gh run rerun [run-id] --failed
```

### Agent System
```bash
# Check registry
cat .github/agent-system/registry.json | jq '.'

# View agent details
cat .github/agent-system/registry.json | jq '.agents[] | select(.name == "agent-name")'

# Check performance
cat .github/agent-system/registry.json | jq '.agents[] | {name, quality: .performance.quality_score}'
```

### GitHub Pages
```bash
# Check data freshness
ls -lah docs/data/

# Update timeline
gh workflow run timeline-updater

# View in browser
open https://enufacas.github.io/Chained/
```

---

## 🎓 When to Use Which Tool

| Situation | Tool | Time |
|-----------|------|------|
| Need quick overview | `quick-health-check.sh` | 5 min |
| System completely down | `check-status.sh` | 10 min |
| Specific workflow failing | `gh run view [run-id] --log` | 5 min |
| Agent issues | Check `registry.json` | 2 min |
| Pages not updating | Trigger `timeline-updater` | 5 min |
| API rate limited | `gh api rate_limit` | 1 min |
| Unknown problem | Follow 5-step method | 15+ min |

---

## 📚 Documentation Links

### Quick Access
- **[COMPREHENSIVE_TROUBLESHOOTING_GUIDE.md](./COMPREHENSIVE_TROUBLESHOOTING_GUIDE.md)** - Complete diagnostic manual (887 lines)
- **[TROUBLESHOOTING.md](./TROUBLESHOOTING.md)** - Quick fixes
- **[PIPELINE_TROUBLESHOOTING.md](./PIPELINE_TROUBLESHOOTING.md)** - Pipeline-specific issues
- **[WORKFLOWS.md](./WORKFLOWS.md)** - Workflow documentation

### Visual Guides
- **[diagrams/troubleshooting-flow.md](./diagrams/troubleshooting-flow.md)** - Flowcharts and decision trees

### Tutorials
- **[tutorials/monitoring-and-debugging.md](./tutorials/monitoring-and-debugging.md)** - System monitoring guide
- **[tutorials/understanding-autonomous-workflow.md](./tutorials/understanding-autonomous-workflow.md)** - How the system works

---

## 🆘 Getting Help

If you're still stuck after trying these solutions:

### 1. Create Effective Support Request
```bash
# Gather diagnostics first
./scripts/quick-health-check.sh > health-report.txt
gh run list --status failure --limit 10 > failed-runs.txt

# Create detailed issue
gh issue create \
  --title "🔧 [Issue Type]: Brief description" \
  --body "
## Problem
[Clear description]

## What I've Tried
- [ ] Checked COPILOT_PAT
- [ ] Ran quick-health-check.sh
- [ ] Checked GitHub status

## System State
\`\`\`
$(cat health-report.txt)
\`\`\`

## Failed Runs
\`\`\`
$(cat failed-runs.txt)
\`\`\`

## Expected Behavior
[What should happen]

## Actual Behavior
[What actually happens]
" \
  --label "help wanted,troubleshooting"
```

### 2. Check Existing Issues
```bash
# Search for similar issues
gh issue list --search "your keywords" --state all

# Check troubleshooting label
gh issue list --label troubleshooting --state all
```

### 3. Review Recent Changes
```bash
# What changed recently?
git log --oneline --since="3 days ago"

# When did it last work?
# Compare current state to that time
```

---

## 💡 Pro Tips

### Preventive Maintenance
- ✅ Run `quick-health-check.sh` weekly
- ✅ Monitor GitHub status page
- ✅ Keep COPILOT_PAT up to date
- ✅ Review workflow logs regularly
- ✅ Update dependencies monthly

### Common Pitfalls to Avoid
- ❌ Don't ignore rate limit warnings
- ❌ Don't skip validation after fixes
- ❌ Don't make multiple changes at once
- ❌ Don't forget to document solutions
- ❌ Don't assume GitHub is always up

### Time-Saving Shortcuts
```bash
# Add to ~/.bashrc or ~/.zshrc
alias chained-health='cd ~/Chained && ./scripts/quick-health-check.sh'
alias chained-status='cd ~/Chained && ./scripts/check-status.sh'
alias chained-fails='gh run list --status failure --limit 10'
alias chained-logs='gh run view --log'
```

---

## 🎯 Quick Wins

These fixes solve 80% of issues in < 5 minutes:

1. **Missing COPILOT_PAT** → `gh secret set COPILOT_PAT`
2. **Workflow disabled** → `gh workflow enable [name]`
3. **Stale browser cache** → Hard refresh (Ctrl+Shift+R)
4. **Invalid JSON** → `jq . file.json` to find error
5. **Missing label** → `gh pr edit [number] --add-label automated`
6. **Permissions error** → Add `contents: write` to workflow
7. **Rate limited** → Wait 1 hour or reduce frequency
8. **Merge conflict** → Pull latest main and resolve
9. **Auto-merge off** → `gh pr merge [number] --auto --squash`
10. **Old PAT** → Regenerate and update secret

---

## 📊 System Health Indicators

### Healthy System (✅)
- All workflows running on schedule
- Copilot responding to issues within 1 hour
- Learning files created daily
- GitHub Pages updated within 12 hours
- Agent scores > 0 after 3 hours
- No API rate limit warnings

### Degraded System (⚠️)
- Some workflow failures (< 50%)
- Copilot delays (1-3 hours)
- Occasional rate limit warnings
- Pages slightly stale (12-24 hours)
- Some agents with zero scores

### Critical System (🔴)
- Multiple workflow failures (> 50%)
- Copilot not responding (> 3 hours)
- No new learning files (> 24 hours)
- Pages very stale (> 24 hours)
- Most agents with zero scores
- API rate limit exceeded

---

## 🌟 Remember

> *"The universe is under no obligation to make sense to you."* - Neil deGrasse Tyson

But this troubleshooting guide is obligated to help you make sense of it! 🚀

**Every bug you fix is a star you add to the constellation of working software.** ✨

---

*Created by **@clarify-champion** - Making troubleshooting as easy as looking at the stars* 🌟

**Quick tip:** Print this page and keep it handy. Like a paper map when GPS fails! 🗺️
