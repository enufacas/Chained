# Tech Lead Agent Review System

## Overview

The Tech Lead Agent Review System extends the autonomous agent ecosystem with specialized "Tech Lead" agents who are responsible for specific areas of the codebase. These agents provide an additional layer of quality assurance and domain expertise before PRs are merged.

## Architecture

### What are Tech Lead Agents?

Tech Lead agents are specialized review agents with:
- **Domain Expertise**: Deep knowledge of specific code areas
- **Path Responsibilities**: Ownership of specific directories/files
- **Enhanced Review Focus**: Security, reliability, and best practices
- **Mentorship Role**: Guide other agents and provide learning feedback
- **Higher Standards**: More thorough review with focus on regression prevention

### Tech Lead vs Regular Agents

| Aspect | Regular Agent | Tech Lead Agent |
|--------|--------------|-----------------|
| **Primary Role** | Implement features/fixes | Review and approve changes |
| **Scope** | Task-specific | Area-specific (paths) |
| **Review Depth** | Basic (automated) | Deep (domain expertise) |
| **Tools** | Standard MCP servers | Enhanced analysis tools |
| **Authority** | Creates PRs | Approves/blocks PRs |
| **Behavior** | Task-focused | Quality & mentorship focused |

## System Components

### 1. Tech Lead Agent Definitions

Tech Lead agents are defined in `.github/agents/` with special properties:

```yaml
---
name: workflows-tech-lead
description: Tech Lead for GitHub Actions workflows
specialization: workflows
tech_lead_for_paths:
  - .github/workflows/**
  - .github/actions/**
responsibilities:
  - Review workflow changes
  - Ensure security best practices
  - Prevent CI/CD regressions
---
```

**Key Properties:**
- `tech_lead_for_paths`: List of glob patterns for owned paths
- `responsibilities`: What they're accountable for
- `review_focus`: Specific areas of concern
- Enhanced personality emphasizing thoroughness

### 2. PR-to-Tech-Lead Matching

**Tool:** `tools/match-pr-to-tech-lead.py`

Analyzes PR file changes and identifies which Tech Lead agents should review:

```bash
# Basic usage
python3 tools/match-pr-to-tech-lead.py 123

# With complexity analysis
python3 tools/match-pr-to-tech-lead.py 123 --check-complexity
```

**Output:**
```json
{
  "pr_number": "123",
  "total_files": 5,
  "tech_leads": [
    {
      "name": "workflows-tech-lead",
      "specialization": "workflows",
      "file_count": 3,
      "files": [".github/workflows/deploy.yml", ...]
    }
  ],
  "complexity": {
    "requires_review": true,
    "recommendation": "required"
  }
}
```

### 3. Tech Lead Review Workflow

**Workflow:** `.github/workflows/tech-lead-review-poc.yml`

**Triggers:**
- PR opened
- PR ready for review
- PR synchronized (new commits)
- Manual dispatch

**Process:**
1. Analyzes PR file changes
2. Matches to Tech Lead agents
3. Evaluates complexity/risk
4. Adds appropriate labels
5. Posts analysis comment
6. Assigns Tech Lead (future)

### 4. Label System

Labels control the review process:

| Label | Purpose | Effect |
|-------|---------|--------|
| `needs-tech-lead-review` | PR requires Tech Lead approval | Blocks auto-merge |
| `tech-lead:agent-name` | Specific Tech Lead assigned | Identifies reviewer |
| `tech-lead-approved` | Tech Lead approved changes | Allows auto-merge |
| `tech-lead-changes-requested` | Issues found in review | Blocks auto-merge |

### 5. Complexity Analysis

The system determines if Tech Lead review is required based on:

**Mandatory Review Triggers:**
- Changes to protected paths (workflows, agents, etc.)
- PRs with security-related keywords
- Large PRs (>5 files or >100 lines changed)
- Multiple subsystems affected

**Optional Review:**
- Documentation-only changes
- Small bug fixes in isolated areas
- Routine maintenance

**Configuration in `match-pr-to-tech-lead.py`:**
```python
TECH_LEAD_THRESHOLDS = {
    "protected_paths": [
        ".github/workflows/**",
        ".github/agents/**",
        ".github/agent-system/**",
    ],
    "max_files_for_optional": 5,
    "max_lines_for_optional": 100,
    "always_require_for_patterns": [
        r"secret", r"password", r"auth", r"security"
    ]
}
```

## Review Process Flow

```
┌─────────────────────────────────────────┐
│ PR Created by Agent X                   │
│ (e.g., @create-guru implements feature) │
└─────────────┬───────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────┐
│ Automated Review (existing system)      │
│ - Linting                               │
│ - Tests                                 │
│ - Security scan                         │
└─────────────┬───────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────┐
│ Tech Lead Review Workflow Triggered     │
│ (.github/workflows/tech-lead-review-    │
│  poc.yml)                               │
└─────────────┬───────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────┐
│ Analyze PR Changes                      │
│ - Get changed files                     │
│ - Match to Tech Lead agents             │
│ - Evaluate complexity                   │
└─────────────┬───────────────────────────┘
              │
              ▼
        ┌─────┴──────┐
        │ Complex?   │
        └─────┬──────┘
              │
         ┌────┴────┐
         │         │
    YES  │         │  NO
         │         │
         ▼         ▼
   ┌─────────┐  ┌──────────────┐
   │ Add     │  │ Optional     │
   │ Labels  │  │ Review       │
   └────┬────┘  └──────┬───────┘
        │              │
        │              │
        ▼              ▼
   ┌─────────────────────────────────┐
   │ Post Analysis Comment           │
   │ - Tech Leads identified         │
   │ - Complexity factors            │
   │ - Review recommendation         │
   └────────────┬────────────────────┘
                │
                ▼
   ┌─────────────────────────────────┐
   │ Assign Tech Lead Agent          │
   │ (Future: via GraphQL API)       │
   └────────────┬────────────────────┘
                │
                ▼
   ┌─────────────────────────────────┐
   │ Tech Lead Reviews PR            │
   │ - Analyzes changes              │
   │ - Runs domain-specific checks   │
   │ - Evaluates against criteria    │
   └────────────┬────────────────────┘
                │
          ┌─────┴─────┐
          │           │
     APPROVE     REQUEST CHANGES
          │           │
          ▼           ▼
   ┌──────────┐  ┌───────────────┐
   │ Add      │  │ Add           │
   │ tech-    │  │ tech-lead-    │
   │ lead-    │  │ changes-      │
   │ approved │  │ requested     │
   └────┬─────┘  └───────┬───────┘
        │                │
        │                ▼
        │         ┌─────────────────┐
        │         │ Provide         │
        │         │ Feedback        │
        │         │ - Comments      │
        │         │ - Suggestions   │
        │         │ - Or direct fix │
        │         └────────┬────────┘
        │                  │
        │                  ▼
        │         ┌─────────────────┐
        │         │ Agent or Tech   │
        │         │ Lead Makes      │
        │         │ Corrections     │
        │         └────────┬────────┘
        │                  │
        │                  ▼
        │         ┌─────────────────┐
        │         │ Re-review       │
        │         │ (loop back)     │
        │         └─────────────────┘
        │
        ▼
   ┌──────────────────────────────────┐
   │ Auto-Merge Proceeds              │
   │ (if tech-lead-approved present)  │
   └──────────────────────────────────┘
```

## Tech Lead Fix Strategies

When a Tech Lead finds issues, they have several options:

### Option A: Comment Suggestions

Tech Lead leaves detailed review comments with:
- Specific issues identified
- Code examples of corrections
- References to best practices
- Rationale for requested changes

**Original agent makes corrections and pushes updates**

### Option B: Direct Fixes (Commit to PR Branch)

Tech Lead can make minor fixes directly:

```bash
# Checkout PR branch
gh pr checkout 123

# Make targeted fixes
# ... edit files ...

# Commit and push
git add .
git commit -m "fix: address Tech Lead feedback"
git push

# Comment on PR
gh pr comment 123 --body "Made minor corrections per review"
```

**Advantages:**
- Fast turnaround for simple issues
- Shows example of correct approach
- Reduces iteration cycles

**When to use:**
- Syntax/formatting issues
- Clear-cut best practice violations
- Security fixes that are straightforward

### Option C: Separate Fix PR (Future)

For complex fixes:
1. Tech Lead creates new PR targeting the original PR branch
2. Fix PR is reviewed and merged to original PR
3. Tech Lead then approves original PR

**Advantages:**
- Clean separation of concerns
- Allows review of Tech Lead's changes
- Better git history

## Integration with Auto-Merge

The `auto-review-merge.yml` workflow needs modification to:

1. **Check for Tech Lead labels before merging:**
   ```yaml
   # Add to existing checks
   - name: Check Tech Lead review status
     run: |
       LABELS=$(gh pr view $PR_NUM --json labels --jq '.labels[].name')
       
       # Block if needs Tech Lead review
       if echo "$LABELS" | grep -q "needs-tech-lead-review"; then
         if ! echo "$LABELS" | grep -q "tech-lead-approved"; then
           echo "❌ Waiting for Tech Lead approval"
           exit 1
         fi
       fi
       
       # Block if changes requested
       if echo "$LABELS" | grep -q "tech-lead-changes-requested"; then
         echo "❌ Tech Lead requested changes"
         exit 1
       fi
   ```

2. **Skip auto-merge for PRs under Tech Lead review**

3. **Allow auto-merge once `tech-lead-approved` is present**

## Current Tech Lead Agents

### workflows-tech-lead

**Specialization:** GitHub Actions and CI/CD pipelines

**Responsibilities:**
- `.github/workflows/**` - All workflow files
- `.github/actions/**` - Custom actions

**Review Focus:**
- Action version pinning (security)
- Proper permission scoping
- Secret handling
- Concurrency controls
- Error handling and retries

**Inspired by:** Martha Graham - choreographic precision

### agents-tech-lead

**Specialization:** Agent system integrity

**Responsibilities:**
- `.github/agents/**` - Agent definitions
- `.github/agent-system/**` - Agent infrastructure
- `tools/match-issue-to-agent.py` - Matching logic
- `tools/*agent*.py` - Agent-related tools

**Review Focus:**
- Agent YAML frontmatter validation
- Pattern matching coverage
- Registry consistency
- Specialization uniqueness
- Performance metrics integrity

**Inspired by:** Alan Turing - systematic agent orchestration

## Usage Examples

### For Agent Developers

When your PR touches protected areas, expect Tech Lead review:

```bash
# Create PR as usual
gh pr create --title "feat: add new workflow" --body "..."

# Tech Lead review workflow automatically triggers
# You'll receive a comment with analysis
# Wait for Tech Lead approval before merge
```

### For Tech Lead Agents

When assigned to review a PR:

```bash
# View PR details
gh pr view 123

# Check files changed
gh pr diff 123

# Review with your domain expertise
# Add comments or make direct fixes

# Approve or request changes
gh pr review 123 --approve
# or
gh pr review 123 --request-changes --body "..."

# System adds appropriate labels
```

### For Repository Maintainers

Configure Tech Lead requirements:

```python
# Edit tools/match-pr-to-tech-lead.py
TECH_LEAD_THRESHOLDS = {
    "protected_paths": [
        # Add paths requiring Tech Lead review
        ".github/workflows/**",
        "src/core/**",
    ],
    "max_files_for_optional": 5,
    "max_lines_for_optional": 100,
}
```

## Enhanced Tools for Tech Leads

Tech Lead agents can be enhanced with specialized MCP servers:

### Workflow-Specific Tools (Future)
- YAML validation and schema checking
- Workflow security scanner
- Action version checker
- Workflow performance analyzer
- Historical failure pattern analysis

### Agent-System Tools (Future)
- Agent definition validator
- Pattern coverage analyzer
- Registry consistency checker
- Performance impact predictor
- Agent conflict detector

### General Review Tools
- Code complexity metrics
- Regression risk analyzer
- Security vulnerability scanner
- Best practices checker
- Historical change impact analysis

## Performance Tracking

Tech Lead agents are tracked with enhanced metrics:

**Standard Metrics:**
- Reviews completed
- Response time
- Approval rate
- Issues caught

**Tech Lead-Specific Metrics:**
- Regressions prevented
- Security issues found
- Quality improvements
- Mentorship impact

**Hall of Fame Category:**
Tech Leads can be inducted for:
- Exceptional review quality
- High impact on code quality
- Effective mentorship
- Domain expertise demonstration

## Configuration

### Creating New Tech Lead Agents

1. **Create agent definition:**
   ```bash
   # Create .github/agents/my-tech-lead.md
   ```

2. **Define path responsibilities:**
   ```yaml
   tech_lead_for_paths:
     - path/to/area/**
     - another/critical/path/**
   ```

3. **Add matching patterns:**
   ```python
   # In tools/match-issue-to-agent.py
   'my-tech-lead': {
       'keywords': ['my', 'domain', 'keywords'],
       'patterns': [r'\bmy\b', r'\bdomain\b']
   }
   ```

4. **Test matching:**
   ```bash
   python3 tools/match-pr-to-tech-lead.py <test_pr_number>
   ```

### Adjusting Review Thresholds

Edit `tools/match-pr-to-tech-lead.py`:

```python
TECH_LEAD_THRESHOLDS = {
    # Paths always requiring review
    "protected_paths": [...],
    
    # Size thresholds
    "max_files_for_optional": 5,
    "max_lines_for_optional": 100,
    
    # Keyword patterns requiring review
    "always_require_for_patterns": [
        r"secret", r"password", ...
    ]
}
```

## Benefits

✅ **Quality Gate:** Additional review layer catches issues
✅ **Domain Expertise:** Specialized knowledge applied to reviews
✅ **Regression Prevention:** Experienced agents prevent breaking changes
✅ **Mentorship:** Learning opportunity for regular agents
✅ **Clear Ownership:** Defined responsibility for code areas
✅ **Better Security:** Enhanced focus on security best practices
✅ **Gradual Rollout:** Can be enabled for critical paths first

## Trade-offs

⚠️ **Slower PRs:** Additional review step adds time
⚠️ **Complexity:** More workflow orchestration needed
⚠️ **Bottleneck Risk:** Tech Lead availability can gate merges
⚠️ **Conflict Resolution:** Need clear process for disagreements
⚠️ **Maintenance:** Tech Lead agents require upkeep

## Future Enhancements

### Phase 1 - Foundation (✅ Complete)
- [x] Tech Lead agent definitions
- [x] PR-to-Tech-Lead matching logic
- [x] Proof-of-concept workflow
- [x] Label system design
- [x] Documentation

### Phase 2 - Review Workflow
- [ ] Assign Tech Lead via GraphQL API
- [ ] Integrate with auto-review-merge.yml
- [ ] Implement approval/rejection flow
- [ ] Add re-review on PR updates
- [ ] Create notification system

### Phase 3 - Fix Mechanisms
- [ ] Comment suggestion templates
- [ ] Direct fix capability (git operations)
- [ ] Fix PR creation automation
- [ ] Conflict resolution process

### Phase 4 - Enhanced Tools
- [ ] MCP server for workflow validation
- [ ] Agent system integrity checker
- [ ] Historical pattern analyzer
- [ ] Security scanning integration
- [ ] Performance impact prediction

### Phase 5 - Advanced Features
- [ ] Multi-Tech-Lead coordination
- [ ] Tech Lead hierarchy (lead of leads)
- [ ] Automated learning from reviews
- [ ] Review pattern recognition
- [ ] Predictive risk assessment

## Open Questions

1. **Protected Status:** Should Tech Leads be immune to elimination?
2. **Count:** How many Tech Lead agents are optimal?
3. **Veto Power:** Can Tech Leads block auto-merge permanently?
4. **Disagreements:** What's the escalation path?
5. **Cross-Review:** Should Tech Leads review each other?
6. **Availability:** What if Tech Lead is unavailable?
7. **Override:** Can repository owner override Tech Lead decisions?

## Related Documentation

- [Agent System Overview](../.github/agent-system/README.md)
- [Custom Agents](../.github/agents/README.md)
- [Auto-Review-Merge Workflow](../.github/workflows/auto-review-merge.yml)
- [Copilot Assignment](../.github/workflows/copilot-graphql-assign.yml)

## Testing

### Test PR Matching
```bash
# Create test PR
gh pr create --title "test: workflow change" --body "Testing Tech Lead"

# Run matching
python3 tools/match-pr-to-tech-lead.py <pr_number> --check-complexity

# Verify correct Tech Lead identified
```

### Test Workflow
```bash
# Trigger workflow manually
gh workflow run tech-lead-review-poc.yml -f pr_number=123

# Check workflow run
gh run list --workflow=tech-lead-review-poc.yml

# View results
gh run view <run_id>
```

### Test Labels
```bash
# Check PR labels
gh pr view 123 --json labels

# Verify correct labels applied
# - needs-tech-lead-review
# - tech-lead:workflows-tech-lead
```

## Conclusion

The Tech Lead Agent Review System adds a crucial quality layer to the autonomous ecosystem. By combining domain expertise with automated workflows, we can maintain high code quality while still leveraging the speed and efficiency of AI agents.

The system is designed for gradual adoption - start with critical paths (workflows, agent definitions) and expand as the system proves its value.

---

*🏗️ Tech Lead Review System - Ensuring Quality Through Domain Expertise*
*Created: 2025-11-18*
*Status: Proof of Concept - Design Complete, Implementation Partial*
