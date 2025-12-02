---
applyTo:
  - "CHANGELOG.md"
  - "**/*.md"
---

# Changelog Maintenance Requirements

## MANDATORY: Update CHANGELOG.md on Every PR

When making changes that will be merged to main, **you MUST update CHANGELOG.md** to document the change.

### What Gets Documented

**DO document:**
- ✅ New features (feat:)
- ✅ Bug fixes (fix:)
- ✅ Breaking changes
- ✅ Significant refactors
- ✅ Performance improvements
- ✅ Security fixes
- ✅ User-facing changes

**DO NOT document:**
- ❌ Auto-churn commits (🔄 AgentOps data sync, 🧠 Daily Learning, etc.)
- ❌ "Initial plan" commits
- ❌ Automated data updates
- ❌ Routine maintenance by bots
- ❌ Architecture evolution tracking commits
- ❌ Reviewer dashboard updates

### Format Guidelines

#### Entry Structure
```markdown
## YYYY-MM-DD

### ✨ Features

- 👤 ⚙️ Workflows User-initiated feature description [#PR_NUMBER](PR_LINK)
- 🤖 🔧 Agents Bot-generated feature description [#PR_NUMBER](PR_LINK)

### 🐛 Bug Fixes

- 👤 Fix description [#PR_NUMBER](PR_LINK)
- 🤖 📋 Instructions Fix description [#PR_NUMBER](PR_LINK)

### 🧹 Chores & Maintenance

- 🤖 📚 Docs **Documentation**: Description [#PR_NUMBER](PR_LINK)

---
```

#### Actor Indicators
- **👤** = User-initiated (from issues you logged or direct commits)
- **🤖** = Bot-generated (autonomous system or agent task)

#### Codebase Area Indicators
- ⚙️ **Workflows** - GitHub Actions (`.github/workflows/`)
- 🔧 **Agents** - Custom agents (`.github/agents/`)
- 📋 **Instructions** - Copilot instructions (`.github/instructions/`)
- 🏗️ **Infrastructure** - GCP, Terraform, Docker
- 📚 **Docs** - Documentation (`docs/`)
- 🧠 **Learning** - Analytics and learning systems
- 📊 **GitHub Pages** - Timeline and public site

#### Categories

**Features** (all features):
- All feat: commits, both user and bot
- Includes all new capabilities and enhancements
- Group by actor type

**Bug Fixes**:
- All fix: commits
- Critical fixes get priority

**Chores & Maintenance**:
- docs:, chore:, refactor:, test:, perf:, ci:, build:, style:
- Grouped together with type labels

### Update Process

#### Option 1: Automatic Generation (Recommended)
Use the script to regenerate from git history:
```bash
python3 tools/generate-changelog.py --since YYYY-MM-DD --output CHANGELOG.md
```

The script:
- Fetches all merged PRs from `origin/main` only
- Achieves 100% PR link coverage
- Auto-excludes AgentOps data syncs and routine maintenance
- Adds actor indicators (👤 user vs 🤖 bot)
- Adds codebase area indicators
- Collapses repeated tasks (e.g., "Update timeline data (x10)")

#### Option 2: Manual Update
Add entry at the top of CHANGELOG.md:
1. Determine today's date section (or create it)
2. Choose appropriate category
3. Add actor indicator (👤 or 🤖)
4. Add codebase area if applicable
5. Write clear, concise description
6. Link to PR if available

### Examples

**Good entries:**
```markdown
- 👤 Add real-time pipeline execution with A2A agent coordination [#3438](https://github.com/enufacas/Chained/pull/3438)
- 🤖 Fix memory leak in AG-UI frontend by increasing limit to 1Gi
- 👤 Implement feature changelog system with automatic generation [#XXXX](https://github.com/enufacas/Chained/pull/XXXX)
```

**Bad entries:**
```markdown
- Fixed stuff (too vague)
- The agent updated something (not specific)
- 🔄 AgentOps data sync (auto-churn, should be excluded)
```

### Commit Message Convention

To ensure proper changelog generation, follow conventional commit format:

```
type: subject

Body (optional)

Refs: #issue_number
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `chore`: Routine task
- `refactor`: Code restructuring
- `test`: Adding tests
- `perf`: Performance improvement
- `ci`: CI/CD changes
- `build`: Build system changes
- `style`: Code style changes
- `revert`: Revert a commit

### Automation

A GitHub workflow updates CHANGELOG.md automatically on PR merge for commits with conventional prefixes. **The workflow auto-merges changelog updates**, so manual review is not required. The changelog stays current automatically.

**Auto-Merge Process:**
1. PR merges to main
2. Workflow detects conventional commits
3. Generates updated CHANGELOG.md
4. Creates PR with changes
5. Enables auto-merge
6. PR merges automatically when checks pass

### Backfill

The changelog has been backfilled from repository inception (2025-11-13) using `tools/generate-changelog.py --backfill`.

### Detection Logic

The script uses these patterns to identify auto-churn:
- Commits starting with 🔄, 🧠, 🏗️
- "AgentOps data sync", "Daily Learning Reflection"
- "Update architecture evolution tracking"
- "Update AI ideas history"
- "[auto]" prefix
- "chore: update reviewer dashboard"

### Actor Detection

**User-initiated** if:
- Author email contains known user names
- PR merged by main Copilot account (not copilot-swe-agent)
- Indicates pair programming or issue-prompted work

**Bot-generated** otherwise:
- copilot-swe-agent[bot]
- github-actions[bot]
- Autonomous agent work

### When to Regenerate

Regenerate the full changelog when:
- Major release preparation
- Significant backlog of undocumented changes
- After merging multiple PRs without updates

Command:
```bash
python3 tools/generate-changelog.py --since 2025-11-25 --output CHANGELOG.md
```

### Checklist for PR

Before marking PR ready for review:
- [ ] CHANGELOG.md has entry for this change (if user-facing)
- [ ] Entry is in correct date section
- [ ] Actor indicator is accurate (👤 or 🤖)
- [ ] Description is clear and concise
- [ ] PR number is linked
- [ ] Auto-churn commits are not documented

### Why This Matters

- **User Transparency**: Clear record of what changed and when
- **Release Notes**: Easy to generate from changelog
- **Actor Attribution**: Distinguishes user-driven vs autonomous work
- **Historical Context**: Future reference for debugging and planning
- **Documentation**: Living record of project evolution

---

**Remember**: The changelog is a communication tool for users and future maintainers. Focus on **what changed and why it matters**, not implementation details.
