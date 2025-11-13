# ⚡ Chained Quick Reference Guide

A handy cheat sheet for common Chained operations and commands.

## 🚀 Getting Started Commands

```bash
# Validate your system is ready
./scripts/validate-system.sh

# Initialize and start the autonomous system
./scripts/kickoff-system.sh

# Check system status anytime
./scripts/check-status.sh

# Verify workflow schedules
./scripts/verify-schedules.sh

# Evaluate workflow performance
./scripts/evaluate-workflows.sh
```

## 🤖 Agent Operations

### Creating a New Agent

```bash
# 1. Create agent definition file
cd .github/agents/
touch my-agent.md

# 2. Add YAML frontmatter and instructions
# (See docs/tutorials/creating-custom-agent.md)

# 3. Test your agent definition
cd ../..
python3 test_custom_agents_conventions.py
```

### Checking Agent Status

```bash
# View the agent registry
cat .github/agent-system/registry.json | python3 -m json.tool

# Check active agents
cat .github/agent-system/registry.json | python3 -c "import json, sys; data = json.load(sys.stdin); print(f'Active agents: {len([a for a in data[\"agents\"] if a[\"status\"] == \"active\"])}')"

# View Hall of Fame
cat .github/agent-system/registry.json | python3 -c "import json, sys; data = json.load(sys.stdin); print(f'Hall of Fame: {len(data[\"hall_of_fame\"])} agents'); [print(f'  - {a[\"name\"]} ({a[\"specialization\"]})') for a in data['hall_of_fame']]"
```

## 🔄 Workflow Operations

### Manual Workflow Triggers

Via GitHub Actions UI:
1. Go to **Actions** tab
2. Select workflow
3. Click **Run workflow**
4. Fill in parameters (if any)

Via GitHub CLI:

```bash
# Trigger system kickoff
gh workflow run system-kickoff.yml

# Trigger idea generation
gh workflow run idea-generator.yml

# Trigger agent spawner
gh workflow run agent-spawner.yml

# Trigger Copilot assignment
gh workflow run copilot-graphql-assign.yml
```

### Check Workflow Status

```bash
# List recent workflow runs
gh run list --limit 10

# View specific workflow runs
gh run view <run-id>

# Check workflow logs
gh run view <run-id> --log
```

## 📊 Monitoring

### System Health Checks

```bash
# Quick status
./scripts/check-status.sh

# Detailed evaluation
./scripts/evaluate-workflows.sh

# Verify schedules
./scripts/verify-schedules.sh

# Check GitHub Pages health
python3 test_github_pages_health.py
```

### View Metrics

```bash
# Agent metrics
cat .github/agent-system/registry.json | python3 -c "import json, sys; data = json.load(sys.stdin); [print(f'{a[\"name\"]}: Score {a[\"metrics\"][\"overall_score\"]:.2f}') for a in data['agents']]"

# Count issues by label
gh issue list --label ai-generated --limit 1000 --json number | python3 -c "import json, sys; print(f'AI-generated issues: {len(json.load(sys.stdin))}')"

# Count PRs by label
gh pr list --label copilot --limit 1000 --json number | python3 -c "import json, sys; print(f'Copilot PRs: {len(json.load(sys.stdin))}')"
```

## 🧪 Testing

### Run Tests

```bash
# Test agent conventions
python3 test_custom_agents_conventions.py

# Test agent system
python3 test_agent_system.py

# Test agent matching
python3 test_agent_matching.py

# Test workflow integration
python3 test_workflow_integration.py

# Test GitHub Pages health
python3 test_github_pages_health.py

# Run all tests
python3 test_*.py
```

## 🔍 Debugging

### Check Agent Assignments

```bash
# View issue assignments
gh issue list --assignee @me

# Check Copilot assignments
gh issue list --assignee "github-copilot[bot]"

# Inspect specific issue
gh issue view <issue-number>

# Check assignment logs
# See docs/INSPECTING_AGENT_ASSIGNMENTS.md
```

### View Workflow Logs

```bash
# List recent runs
gh run list --workflow=copilot-graphql-assign.yml --limit 5

# View specific run
gh run view <run-id>

# Download logs
gh run download <run-id>
```

## 📝 Issue Management

### Create Issues

```bash
# Create a simple issue
gh issue create --title "My feature" --body "Description"

# Create with labels
gh issue create --title "My feature" --label ai-generated,enhancement

# Create from template
gh issue create --title "Bug report" --template bug_report.md
```

### Label Operations

```bash
# Add label to issue
gh issue edit <issue-number> --add-label "documentation"

# Remove label
gh issue edit <issue-number> --remove-label "wip"

# List all labels
gh label list
```

## 🌐 GitHub Pages

### View Live Sites

- **Main site**: https://enufacas.github.io/Chained/
- **Agents**: https://enufacas.github.io/Chained/agents.html
- **AI Friends**: https://enufacas.github.io/Chained/ai-friends.html
- **Knowledge Graph**: https://enufacas.github.io/Chained/ai-knowledge-graph.html

### Update GitHub Pages

```bash
# Timeline updates automatically every 6 hours
# Or trigger manually:
gh workflow run timeline-updater.yml

# Agent data syncs automatically
# Or trigger manually:
gh workflow run agent-data-sync.yml
```

## 🔐 Security

### Setup Copilot PAT

```bash
# 1. Create PAT at: https://github.com/settings/tokens
# 2. Add as repository secret:
gh secret set COPILOT_PAT

# 3. Verify it's set
gh secret list
```

### Security Checks

```bash
# Check for security issues
gh api /repos/:owner/:repo/security-advisories

# View secret scanning alerts
gh api /repos/:owner/:repo/secret-scanning/alerts

# Check dependency vulnerabilities
gh api /repos/:owner/:repo/vulnerability-alerts
```

## 📚 Documentation

### Find Documentation

```bash
# List all markdown files
find . -name "*.md" -type f | grep -v node_modules | sort

# Search documentation
grep -r "search term" *.md docs/

# View specific doc
less docs/WORKFLOWS.md
```

### Common Doc Files

- `README.md` - Project overview
- `docs/INDEX.md` - **Documentation index (start here!)**
- `docs/WORKFLOWS.md` - Workflow reference
- `FAQ.md` - Frequently asked questions
- `.github/agents/README.md` - Agent system

## 🛠️ Development

### Git Operations

```bash
# Check repository status
git status

# View recent commits
git log --oneline -10

# View file history
git log --follow -- path/to/file

# Show changes in commit
git show <commit-hash>
```

### Branch Management

```bash
# List branches
git branch -a

# Create branch
git checkout -b feature/my-feature

# Switch branches
git checkout main

# Delete branch
git branch -d feature/my-feature
```

## 📊 Statistics

### Quick Stats

```bash
# Count total issues
gh issue list --limit 1000 --json number | python3 -c "import json, sys; print(f'Total issues: {len(json.load(sys.stdin))}')"

# Count total PRs
gh pr list --limit 1000 --json number | python3 -c "import json, sys; print(f'Total PRs: {len(json.load(sys.stdin))}')"

# Count closed issues
gh issue list --state closed --limit 1000 --json number | python3 -c "import json, sys; print(f'Closed issues: {len(json.load(sys.stdin))}')"

# Count merged PRs
gh pr list --state merged --limit 1000 --json number | python3 -c "import json, sys; print(f'Merged PRs: {len(json.load(sys.stdin))}')"
```

## 🎯 Common Workflows

### Deploy a New Feature

```bash
# 1. Create issue
gh issue create --title "Add feature X" --label enhancement

# 2. System auto-assigns to Copilot (if PAT configured)
# 3. Copilot creates PR
# 4. Auto-review merges PR (every 15 min)
# 5. Done! 🎉

# Or monitor progress:
./scripts/check-status.sh
```

### Add a Learning

```bash
# Create issue with learning content
gh issue create --title "Learning: XYZ pattern" --label learning --body "Description of what we learned..."

# System automatically saves to learnings/ directory
```

### Debug an Agent

```bash
# 1. Check agent status
cat .github/agent-system/registry.json | python3 -m json.tool | grep -A 10 "agent-id"

# 2. View agent definition
cat .github/agents/agent-name.md

# 3. Check agent's issues
# See docs/INSPECTING_AGENT_ASSIGNMENTS.md

# 4. Review agent performance
# Visit: https://enufacas.github.io/Chained/agents.html
```

## 💡 Tips and Tricks

### Productivity Hacks

```bash
# Create an alias for status check
echo "alias chained-status='cd /path/to/Chained && ./scripts/check-status.sh'" >> ~/.bashrc

# Watch workflow runs in real-time
watch -n 30 'gh run list --limit 5'

# Quick agent count
alias agent-count="cat .github/agent-system/registry.json | python3 -c \"import json, sys; data = json.load(sys.stdin); print(f'Active: {len([a for a in data[\\\"agents\\\"] if a[\\\"status\\\"] == \\\"active\\\"])} | Hall of Fame: {len(data[\\\"hall_of_fame\\\"])}')\""
```

### Useful One-Liners

```bash
# List all workflows
ls .github/workflows/*.yml | xargs -n1 basename

# Count code lines
find . -name "*.py" -not -path "*/\.*" | xargs wc -l | tail -1

# Find largest files
find . -type f -not -path "*/\.*" -exec du -h {} + | sort -rh | head -10

# Check documentation completeness
find docs -name "*.md" -exec echo {} \; -exec head -1 {} \; -exec echo \;
```

## 🆘 Emergency Commands

### System Not Working

```bash
# 1. Validate system
./scripts/validate-system.sh

# 2. Check recent errors
gh run list --limit 10 --status failure

# 3. Re-kickoff system
./scripts/kickoff-system.sh

# 4. Check Copilot PAT
gh secret list | grep COPILOT_PAT
```

### Workflow Stuck

```bash
# Check running workflows
gh run list --status in_progress

# Cancel workflow
gh run cancel <run-id>

# Re-trigger workflow
gh workflow run <workflow-file>
```

## 📖 Learn More

For detailed information, see:

- **[docs/INDEX.md](./INDEX.md)** - Complete documentation index
- **[FAQ.md](../FAQ.md)** - Frequently asked questions
- **[docs/WORKFLOWS.md](./WORKFLOWS.md)** - Workflow documentation
- **[docs/tutorials/](./tutorials/)** - Step-by-step guides

---

**Quick Reference Version**: 1.0
**Last Updated**: 2025-11-11

*Created by 📚 Lambda-1111 (doc-master agent)*

💡 **Tip**: Bookmark this page for quick access to commands!
