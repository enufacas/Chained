# Tech Lead Agent System - Quick Reference

## 🚀 Quick Start

### What is a Tech Lead Agent?
A specialized review agent responsible for specific code areas, providing domain expertise and quality gates before PR merge.

### When Do You Need Tech Lead Review?
- Changes to protected paths (workflows, agents, CODEOWNERS)
- Large PRs (>5 files or >100 lines)
- Security-related changes
- Multiple subsystems affected

### Current Tech Lead Agents

| Tech Lead | Responsible For | Focus Areas |
|-----------|----------------|-------------|
| **workflows-tech-lead** 🔧 | `.github/workflows/`<br>`.github/actions/` | Security pinning<br>Permissions<br>Concurrency<br>Error handling |
| **agents-tech-lead** 🤖 | `.github/agents/`<br>`.github/agent-system/`<br>`tools/*agent*.py` | Agent definitions<br>Pattern matching<br>Registry consistency<br>System integrity |

## 📊 Label Reference

| Label | Meaning | Action |
|-------|---------|--------|
| `needs-tech-lead-review` | Tech Lead approval required | Blocks auto-merge |
| `tech-lead:workflows-tech-lead` | Specific Tech Lead assigned | Identifies reviewer |
| `tech-lead-approved` | Tech Lead approved changes | Enables auto-merge |
| `tech-lead-changes-requested` | Issues found, fixes needed | Blocks auto-merge |

## 🔍 Testing Commands

### Test Issue Matching
```bash
# Test if issue triggers Tech Lead agent
python3 tools/match-issue-to-agent.py \
  "Update workflow" \
  "Modify deploy.yml to add security scanning"

# Expected: workflows-tech-lead with high score
```

### Test PR Analysis
```bash
# Analyze PR for Tech Lead requirements
python3 tools/match-pr-to-tech-lead.py 123

# With complexity check
python3 tools/match-pr-to-tech-lead.py 123 --check-complexity
```

### Trigger Workflow Manually
```bash
# Trigger review workflow for PR
gh workflow run tech-lead-review-poc.yml -f pr_number=123

# Check workflow runs
gh run list --workflow=tech-lead-review-poc.yml

# View run details
gh run view <run_id>
```

## 💬 Common Scenarios

### Scenario 1: Workflow Change PR
```
PR: "feat: add security scanning to deploy workflow"
Files: .github/workflows/deploy.yml

Result:
✅ workflows-tech-lead assigned
✅ needs-tech-lead-review label added
✅ Analysis comment posted
⏸️ Auto-merge blocked until approved
```

### Scenario 2: Agent Definition Update
```
PR: "feat: add new cloud-architect agent"
Files: .github/agents/cloud-architect.md
       tools/match-issue-to-agent.py

Result:
✅ agents-tech-lead assigned
✅ needs-tech-lead-review label added
✅ Validates YAML frontmatter
✅ Checks pattern coverage
⏸️ Awaiting Tech Lead review
```

### Scenario 3: Documentation Only
```
PR: "docs: update README"
Files: README.md

Result:
ℹ️ No Tech Lead required
✅ Normal auto-review proceeds
✅ Can auto-merge without Tech Lead
```

## 🛠️ For Agent Developers

### What to Expect
1. Create PR as usual
2. If Tech Lead review needed, you'll get a comment
3. Wait for Tech Lead feedback
4. Address any requested changes
5. Tech Lead approves → PR can merge

### How to Prepare
- Review relevant Tech Lead checklists before submitting
- Ensure your changes follow domain best practices
- Test your changes thoroughly
- Document rationale for complex changes
- Be ready to explain design decisions

## 👔 For Tech Lead Agents

### Review Workflow
```bash
# View PR details
gh pr view 123

# Check files changed
gh pr diff 123

# Review with domain expertise
# Add comments or make direct fixes

# Approve
gh pr review 123 --approve --body "LGTM! ..."

# Or request changes
gh pr review 123 --request-changes --body "..."
```

### Fix Options

**Option A: Comment Suggestions**
```bash
gh pr comment 123 --body "Please update line X to Y because..."
```

**Option B: Direct Fixes**
```bash
# Checkout PR branch
gh pr checkout 123

# Make fixes
# ... edit files ...

# Commit and push
git add .
git commit -m "fix: address Tech Lead feedback"
git push

# Notify
gh pr comment 123 --body "Fixed issues and pushed updates"
```

### Review Checklist

Use your domain-specific checklist from your agent definition:
- workflows-tech-lead: Security, permissions, concurrency
- agents-tech-lead: YAML validation, pattern coverage, registry

## 📈 Complexity Thresholds

### Mandatory Review
```python
# Protected paths
.github/workflows/**
.github/agents/**
.github/agent-system/**
CODEOWNERS

# Large PRs
files_changed > 5
lines_changed > 100

# Security keywords
secret, password, auth, token, key
```

### Optional Review
```python
# Documentation only
**/*.md (no code changes)

# Small fixes
files_changed <= 5
lines_changed <= 100
```

## 🔧 Configuration

### Add New Tech Lead

1. **Create Agent Definition**
```bash
# Create .github/agents/my-tech-lead.md
cat > .github/agents/my-tech-lead.md << 'EOF'
---
name: my-tech-lead
description: Tech Lead for specific area
specialization: my-area
tech_lead_for_paths:
  - path/to/area/**
---
# Content here
EOF
```

2. **Add Matching Patterns**
```python
# In tools/match-issue-to-agent.py
'my-tech-lead': {
    'keywords': ['domain', 'keywords'],
    'patterns': [r'\bdomain\b', r'\bkeywords\b']
}
```

3. **Configure Paths**
```python
# In tools/match-pr-to-tech-lead.py
TECH_LEAD_PATHS = {
    'my-tech-lead': {
        'patterns': [
            'path/to/area/**',
            'another/path/**'
        ],
        'priority': 'high'
    }
}
```

4. **Test**
```bash
# Test issue matching
python3 tools/match-issue-to-agent.py "test title" "test body"

# Test PR matching  
# (create test PR first)
python3 tools/match-pr-to-tech-lead.py <pr_number>
```

### Adjust Thresholds

Edit `tools/match-pr-to-tech-lead.py`:

```python
TECH_LEAD_THRESHOLDS = {
    "protected_paths": [
        ".github/workflows/**",
        # Add more paths
    ],
    "max_files_for_optional": 5,  # Adjust size threshold
    "max_lines_for_optional": 100,
    "always_require_for_patterns": [
        r"secret",  # Add keywords
    ]
}
```

## 🎯 Integration Points

### With Auto-Review-Merge
```yaml
# Check Tech Lead status before merge
- name: Check Tech Lead Review
  run: |
    LABELS=$(gh pr view $PR_NUM --json labels --jq '.labels[].name')
    
    if echo "$LABELS" | grep -q "needs-tech-lead-review"; then
      if ! echo "$LABELS" | grep -q "tech-lead-approved"; then
        echo "Waiting for Tech Lead approval"
        exit 1
      fi
    fi
    
    if echo "$LABELS" | grep -q "tech-lead-changes-requested"; then
      echo "Tech Lead requested changes"
      exit 1
    fi
```

### With Copilot Assignment
```bash
# Future: Assign Tech Lead via GraphQL
python3 tools/assign-copilot-to-issue.sh <issue_number> <tech_lead_agent>
```

## 📚 Documentation References

- **Full Guide**: [`docs/TECH_LEAD_REVIEW_SYSTEM.md`](../docs/TECH_LEAD_REVIEW_SYSTEM.md)
- **workflows-tech-lead**: [`.github/agents/workflows-tech-lead.md`](../.github/agents/workflows-tech-lead.md)
- **agents-tech-lead**: [`.github/agents/agents-tech-lead.md`](../.github/agents/agents-tech-lead.md)
- **Matching Script**: [`tools/match-pr-to-tech-lead.py`](../tools/match-pr-to-tech-lead.py)
- **Review Workflow**: [`.github/workflows/tech-lead-review-poc.yml`](../.github/workflows/tech-lead-review-poc.yml)

## 🐛 Troubleshooting

### Issue: Tech Lead not being assigned
```bash
# Check if patterns exist
grep -A10 "workflows-tech-lead" tools/match-issue-to-agent.py

# Test matching manually
python3 tools/match-issue-to-agent.py "workflow" "test workflow issue"
```

### Issue: PR analysis failing
```bash
# Check gh CLI is installed
gh --version

# Check gh CLI authentication
gh auth status

# Test PR query manually
gh pr view 123 --json files
```

### Issue: Labels not being applied
```bash
# Check workflow run logs
gh run view <run_id> --log

# Check PR labels manually
gh pr view 123 --json labels

# Add label manually for testing
gh pr edit 123 --add-label "needs-tech-lead-review"
```

## ⚡ Quick Commands

```bash
# Check if PR needs Tech Lead
python3 tools/match-pr-to-tech-lead.py $PR_NUM

# View Tech Lead agent details
cat .github/agents/workflows-tech-lead.md

# Test workflow
gh workflow run tech-lead-review-poc.yml -f pr_number=$PR_NUM

# Check review status
gh pr view $PR_NUM --json labels | jq '.labels[].name' | grep tech-lead

# Approve as Tech Lead
gh pr review $PR_NUM --approve --body "Tech Lead approved"
```

## 🎓 Learning Resources

### For Understanding Tech Lead Patterns
- Read existing Tech Lead agent definitions
- Study their review checklists
- Look at matching patterns in `match-issue-to-agent.py`
- Review complexity thresholds in `match-pr-to-tech-lead.py`

### For Creating New Tech Leads
- Start with a clear domain definition
- Define specific path responsibilities
- Create comprehensive matching patterns
- Write detailed review criteria
- Test thoroughly with sample PRs

---

*📖 Quick Reference for Tech Lead Agent Review System*
*Version: 1.0 - Proof of Concept*
*Updated: 2025-11-18*
