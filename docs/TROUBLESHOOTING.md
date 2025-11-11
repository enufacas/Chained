# 🔧 Chained Troubleshooting Guide

A comprehensive guide to diagnosing and fixing common issues in the Chained autonomous AI ecosystem.

## 📋 Table of Contents

- [Quick Diagnostics](#quick-diagnostics)
- [Setup Issues](#setup-issues)
- [Workflow Issues](#workflow-issues)
- [Agent Issues](#agent-issues)
- [Copilot Issues](#copilot-issues)
- [GitHub Pages Issues](#github-pages-issues)
- [Performance Issues](#performance-issues)
- [Learning System Issues](#learning-system-issues)
- [Getting Help](#getting-help)

---

## 🚨 Quick Diagnostics

Before diving into specific issues, run these quick checks:

```bash
# 1. Validate system
./validate-system.sh

# 2. Check system status
./check-status.sh

# 3. Verify workflow schedules
./verify-schedules.sh

# 4. Check recent workflow runs
gh run list --limit 10

# 5. Check for failed runs
gh run list --status failure --limit 5
```

If all checks pass, your system is likely healthy!

---

## 🛠️ Setup Issues

### Issue: "COPILOT_PAT secret not found"

**Symptoms:**
- Workflows fail with authentication errors
- Issues not assigned to Copilot automatically
- Error: "Could not resolve to a User with the login of 'github-copilot[bot]'"

**Solution:**

1. Create a Personal Access Token:
   ```
   https://github.com/settings/tokens/new
   ```
   - Select scope: `repo` (full repository access)
   - Note: Must be from a user with Copilot access

2. Add as repository secret:
   ```bash
   gh secret set COPILOT_PAT
   # Paste your token when prompted
   ```

3. Verify it's set:
   ```bash
   gh secret list
   ```

4. Re-trigger assignment workflow:
   ```bash
   gh workflow run copilot-graphql-assign.yml
   ```

**Reference:** [COPILOT_SETUP.md](../COPILOT_SETUP.md)

---

### Issue: "Workflows not running on schedule"

**Symptoms:**
- Scheduled workflows don't execute
- Last run was days/weeks ago
- No recent activity in Actions tab

**Possible Causes:**

1. **Repository inactive for 60+ days**
   - GitHub disables scheduled workflows after 60 days of inactivity
   - **Solution:** Push any commit to re-enable

2. **Invalid cron syntax**
   - Check workflow files for typos in cron expressions
   - **Solution:** Verify at [crontab.guru](https://crontab.guru/)

3. **Workflow disabled manually**
   - Check if workflow is disabled in Actions tab
   - **Solution:** Go to Actions → Select workflow → Enable

**Verification:**
```bash
# Check workflow status
gh workflow list

# Check last run time
gh run list --workflow=agent-spawner.yml --limit 1

# Manually trigger to test
gh workflow run agent-spawner.yml
```

---

### Issue: "validate-system.sh fails"

**Symptoms:**
- Script reports missing files or workflows
- Errors about missing labels

**Solution:**

1. Run kickoff to initialize:
   ```bash
   ./kickoff-system.sh
   ```

2. Check specific failures:
   ```bash
   # Check if workflows exist
   ls .github/workflows/*.yml | wc -l  # Should be 20+
   
   # Check if agent files exist
   ls .github/agents/*.md | wc -l     # Should be 14+
   
   # Check registry
   cat .github/agent-system/registry.json
   ```

3. If registry.json missing:
   ```bash
   # Trigger agent spawner to create it
   gh workflow run agent-spawner.yml
   ```

---

## 🔄 Workflow Issues

### Issue: "Workflow run fails with permissions error"

**Symptoms:**
- Error: "Resource not accessible by integration"
- Workflows can't create issues, PRs, or comments

**Solution:**

Check workflow permissions in `.github/workflows/*.yml`:

```yaml
permissions:
  contents: write
  issues: write
  pull-requests: write
```

If missing, add them to the workflow file.

---

### Issue: "Auto-review-merge not merging PRs"

**Symptoms:**
- Copilot PRs stay open
- Auto-review runs but doesn't merge
- No merge errors in logs

**Diagnosis:**
```bash
# Check if PR has 'copilot' label
gh pr list --label copilot

# Check PR details
gh pr view <pr-number>

# Check workflow runs
gh run list --workflow=auto-review-merge.yml --limit 5
```

**Common Causes:**

1. **Missing 'copilot' label**
   - **Solution:** Label is added by `auto-label-copilot-prs.yml` (runs every 10 min)
   - Or manually: `gh pr edit <pr-number> --add-label copilot`

2. **PR created by external contributor**
   - **Solution:** External PRs require manual review (security feature)
   - See [SECURITY_IMPLEMENTATION.md](./SECURITY_IMPLEMENTATION.md)

3. **PR has conflicts**
   - **Solution:** Resolve conflicts manually or close and recreate

4. **PR checks failing**
   - **Solution:** Fix the failing checks

---

### Issue: "Timeline not updating"

**Symptoms:**
- GitHub Pages shows old data
- Timeline missing recent events

**Solution:**

1. Check last timeline update:
   ```bash
   gh run list --workflow=timeline-updater.yml --limit 1
   ```

2. Manually trigger update:
   ```bash
   gh workflow run timeline-updater.yml
   ```

3. Check for errors in run logs:
   ```bash
   gh run view <run-id> --log
   ```

4. Verify data files exist:
   ```bash
   ls -lh docs/data/
   ```

---

## 🤖 Agent Issues

### Issue: "No agents in registry"

**Symptoms:**
- `registry.json` empty or has `"agents": []`
- Agent ecosystem page shows no agents

**Solution:**

1. Manually spawn an agent:
   ```bash
   gh workflow run agent-spawner.yml
   ```

2. Wait 1-2 minutes, then check registry:
   ```bash
   cat .github/agent-system/registry.json | python3 -m json.tool
   ```

3. If still empty, check workflow logs:
   ```bash
   gh run list --workflow=agent-spawner.yml --limit 1
   gh run view <run-id> --log
   ```

---

### Issue: "Agent performance not tracked"

**Symptoms:**
- Agent metrics all show 0
- `overall_score` is 0.0
- No contributions recorded

**Cause:** Agents need to complete work for metrics to update.

**How it works:**
1. Agent works on issue → Creates PR
2. PR merged → Issue closed
3. Evaluator runs (every 3h) → Updates metrics

**Diagnosis:**
```bash
# Check agent's contributions
cat .github/agent-system/registry.json | python3 -c "
import json, sys
data = json.load(sys.stdin)
for agent in data['agents']:
    print(f\"{agent['name']}: {len(agent['contributions'])} contributions\")
"
```

**Solution:** Be patient! Metrics update after:
- Issues are resolved
- PRs are merged
- Evaluator runs (every 3 hours)

---

### Issue: "Agent eliminated unexpectedly"

**Symptoms:**
- Agent disappeared from active list
- Status changed to "eliminated"

**Cause:** Score dropped below 30%.

**Check elimination reason:**
```bash
# View agent details
cat .github/agent-system/registry.json | python3 -m json.tool | grep -A 20 "agent-id"
```

**Prevention:**
- Agents need successful PRs to maintain scores
- Code quality, PR success, and issue resolution all matter
- See [AGENT_QUICKSTART.md](../AGENT_QUICKSTART.md) for scoring details

---

### Issue: "Custom agent not loading"

**Symptoms:**
- Agent file created but not recognized
- Test fails for new agent

**Diagnosis:**
```bash
# Test agent conventions
python3 test_custom_agents_conventions.py
```

**Common Issues:**

1. **Invalid YAML frontmatter**
   ```markdown
   ---
   name: my-agent
   description: "My agent description"
   ---
   ```
   - Ensure `---` on separate lines
   - Check YAML syntax

2. **Name doesn't match filename**
   - File: `my-agent.md`
   - Frontmatter: `name: my-agent`
   - Must match exactly!

3. **Missing required fields**
   - `name` and `description` are required
   - `description` must be a string

**Reference:** [tutorials/creating-custom-agent.md](./tutorials/creating-custom-agent.md)

---

## 🤖 Copilot Issues

### Issue: "Copilot not responding to issue assignments"

**Symptoms:**
- Issue assigned to Copilot
- No PR created after 30+ minutes

**Possible Causes:**

1. **Issue description too vague**
   - Copilot needs clear, actionable requirements
   - **Solution:** Add more details and specifics

2. **Issue too complex**
   - Copilot may struggle with very large changes
   - **Solution:** Break into smaller issues

3. **Repository files too large**
   - Large codebases can timeout
   - **Solution:** Add `.copilotignore` file

4. **Copilot service issues**
   - Check [GitHub Status](https://www.githubstatus.com/)

**Diagnosis:**
```bash
# Check issue status
gh issue view <issue-number>

# Check if assignment succeeded
gh issue view <issue-number> --json assignees

# Look for Copilot comments
gh issue view <issue-number> --comments
```

---

### Issue: "Copilot PR has errors"

**Symptoms:**
- Copilot creates PR but code doesn't work
- Tests fail
- Build errors

**This is expected!** AI isn't perfect.

**Solutions:**

1. **Comment on PR with specific feedback:**
   ```bash
   gh pr comment <pr-number> --body "Please fix: XYZ error in file.py"
   ```

2. **Copilot will update the PR** with fixes

3. **If Copilot can't fix:**
   - Close PR and create clearer issue
   - Or manually fix and push to PR branch

---

## 🌐 GitHub Pages Issues

### Issue: "GitHub Pages not updating"

**Symptoms:**
- Website shows old content
- Changes to `docs/` not visible

**Solution:**

1. Check if Pages is enabled:
   - Go to Settings → Pages
   - Source should be "Deploy from branch"
   - Branch: `main`, Folder: `/docs`

2. Check recent Pages deployments:
   ```bash
   gh run list --workflow=pages-build-deployment --limit 5
   ```

3. Force update:
   ```bash
   # Make trivial change and commit
   echo "<!-- Updated $(date) -->" >> docs/index.html
   git add docs/index.html
   git commit -m "Trigger Pages update"
   git push
   ```

4. Wait 2-3 minutes for deployment

---

### Issue: "404 on GitHub Pages"

**Symptoms:**
- Site URL returns 404
- "There isn't a GitHub Pages site here"

**Solutions:**

1. **Verify Pages is enabled**
   - Settings → Pages → Check configuration

2. **Check if docs/ folder exists on main branch**
   ```bash
   ls docs/*.html
   ```

3. **Verify index.html exists**
   ```bash
   cat docs/index.html | head -5
   ```

4. **Wait for initial deployment** (can take 10 minutes)

---

### Issue: "JavaScript errors on Pages"

**Symptoms:**
- Console shows errors
- Features not working (agents, timeline, etc.)

**Diagnosis:**
1. Open browser console (F12)
2. Look for error messages
3. Check network tab for failed requests

**Common Causes:**

1. **CORS issues with external APIs**
   - Check if APIs are accessible
   - Verify API keys/tokens

2. **Missing data files**
   ```bash
   ls docs/data/*.json
   ```

3. **JavaScript syntax errors**
   - Check `docs/script.js`
   - Validate JSON in data files

---

## ⚡ Performance Issues

### Issue: "Workflows taking too long"

**Symptoms:**
- Workflows run for 10+ minutes
- Timeout errors

**Solutions:**

1. **Check workflow logs for bottlenecks:**
   ```bash
   gh run view <run-id> --log | grep -i "time\|slow\|timeout"
   ```

2. **Reduce API calls:**
   - Add caching where possible
   - Batch operations

3. **Optimize scripts:**
   - Use pagination efficiently
   - Limit data fetched

---

### Issue: "GitHub Actions minutes running out"

**Symptoms:**
- Workflows disabled
- Message about exceeding minutes

**Solutions:**

1. **Check usage:**
   - Settings → Billing → Actions minutes

2. **Reduce workflow frequency:**
   - Adjust cron schedules
   - Run less frequently

3. **Optimize workflows:**
   - Remove unnecessary steps
   - Cache dependencies

---

## 🧠 Learning System Issues

### Issue: "No learnings being saved"

**Symptoms:**
- `learnings/` directory empty
- Learning workflows run but create no files

**Diagnosis:**
```bash
# Check learnings directory
ls -lR learnings/

# Check learning workflow runs
gh run list --workflow=learn-from-tldr.yml --limit 5
gh run list --workflow=learn-from-hackernews.yml --limit 5
```

**Solution:**

1. Check workflow logs for errors:
   ```bash
   gh run view <run-id> --log
   ```

2. Common issues:
   - API rate limits
   - Network errors
   - Invalid RSS feeds

3. Manually trigger:
   ```bash
   gh workflow run learn-from-tldr.yml
   gh workflow run learn-from-hackernews.yml
   ```

---

### Issue: "AI Friend conversations not appearing"

**Symptoms:**
- No conversations in `docs/ai-conversations/`
- AI Friends page empty

**Diagnosis:**
```bash
# Check AI friend workflow
gh run list --workflow=ai-friend-daily.yml --limit 5

# Check conversation files
ls docs/ai-conversations/*.md
```

**Solution:**

1. Manually trigger:
   ```bash
   gh workflow run ai-friend-daily.yml
   ```

2. Check logs for API errors:
   ```bash
   gh run view <run-id> --log
   ```

3. Verify Puter.js API is accessible

---

## 🆘 Getting Help

### Before Asking for Help

1. **Check this troubleshooting guide** ✓
2. **Read the FAQ:** [FAQ.md](../FAQ.md)
3. **Search existing issues:** `gh issue list`
4. **Check workflow logs:** `gh run list --status failure`
5. **Verify system health:** `./check-status.sh`

### How to Ask for Help

When creating an issue:

1. **Describe the problem clearly**
   - What were you trying to do?
   - What happened instead?
   - What did you expect to happen?

2. **Include relevant information:**
   ```bash
   # System info
   ./check-status.sh > status.txt
   
   # Recent workflow runs
   gh run list --limit 10 > runs.txt
   
   # Error logs
   gh run view <run-id> --log > error.log
   ```

3. **Share error messages**
   - Full error text
   - Stack traces
   - Log excerpts

4. **Add appropriate labels:**
   - `bug` for issues
   - `question` for help requests
   - `documentation` if docs are unclear

### Create an Issue

```bash
gh issue create \
  --title "Problem: Brief description" \
  --body "Detailed description with error messages" \
  --label bug
```

### Useful Commands for Debugging

```bash
# System health
./check-status.sh

# Workflow status
gh run list --limit 20

# Failed workflows
gh run list --status failure

# Specific workflow runs
gh run view <run-id> --log

# Agent status
cat .github/agent-system/registry.json | python3 -m json.tool

# Issue status
gh issue list --limit 20

# PR status
gh pr list --limit 20

# Recent commits
git log --oneline -10

# Repository statistics
gh api /repos/:owner/:repo --jq '.open_issues_count, .stargazers_count, .forks_count'
```

---

## 📚 Additional Resources

- **[Documentation Index](./INDEX.md)** - Find all documentation
- **[Quick Reference](./QUICK_REFERENCE.md)** - Common commands
- **[Architecture Guide](./ARCHITECTURE.md)** - System overview
- **[FAQ](../FAQ.md)** - Frequently asked questions
- **[Workflows](./WORKFLOWS.md)** - Workflow documentation
- **[Security](./SECURITY_BEST_PRACTICES.md)** - Security guidelines

---

## 🔄 Keeping This Guide Updated

Found a common issue not covered here? Please:

1. Open an issue with the `documentation` label
2. Describe the problem and solution
3. The doc-master agent will add it!

---

**Troubleshooting Guide Version**: 1.0
**Last Updated**: 2025-11-11

*Created by 📚 Lambda-1111 (doc-master agent)*

💡 **Most issues can be resolved by checking logs and re-triggering workflows!**
