# Changelog System Documentation

## Overview

The Chained project maintains a comprehensive changelog system that automatically tracks and documents all notable changes to the repository. This system is designed to:

1. **Capture user-initiated improvements** separate from autonomous bot changes
2. **Exclude auto-churn commits** (data syncs, routine maintenance)
3. **Distinguish actors** (user-prompted vs bot-only work)
4. **Follow conventional commit standards** (feat, fix, chore, etc.)
5. **Generate automatically** from git history

## Files and Components

### Core Files

- **`CHANGELOG.md`** - The main changelog file in the repository root
- **`tools/generate-changelog.py`** - Python script to generate/update changelog from git history
- **`.github/workflows/update-changelog.yml`** - Automated workflow to update changelog on PR merge
- **`.github/instructions/changelog-maintenance.instructions.md`** - Path-specific instructions for Copilot

### Generated Content

The CHANGELOG.md file contains:
- Chronologically organized entries by date (newest first)
- Categorized changes (Features, Bug Fixes, Major Improvements, Chores)
- Actor indicators (👤 user-initiated, 🤖 bot-generated)
- PR links for traceability
- Exclusion of auto-churn commits

## Usage

### For Users

**Viewing the Changelog:**
Simply open [CHANGELOG.md](../CHANGELOG.md) to see all notable changes organized by date and category.

**Understanding Actor Indicators:**
- 👤 = User-initiated (features you requested via issues or direct commits)
- 🤖 = Bot-generated (autonomous agent work)

### For Contributors

**When Creating a PR:**

1. **Use conventional commit messages:**
   ```
   feat: Add new feature
   fix: Fix bug in component
   docs: Update documentation
   chore: Update dependencies
   ```

2. **Verify changelog update** (one of):
   - Let the automated workflow handle it after merge
   - Manually add entry to CHANGELOG.md following the format
   - Use the script to regenerate: `python3 tools/generate-changelog.py --since YYYY-MM-DD`

3. **Review the entry** before finalizing PR to ensure it's accurate

### For Maintainers

**Regenerating the Changelog:**

Generate changelog for recent changes:
```bash
python3 tools/generate-changelog.py --since 2025-11-25 --output CHANGELOG.md
```

Backfill complete history:
```bash
python3 tools/generate-changelog.py --backfill --output CHANGELOG.md
```

Append new entries:
```bash
python3 tools/generate-changelog.py --since 2025-12-01 --append --output CHANGELOG.md
```

**Script Options:**
- `--since DATE` - Only include commits since this date (YYYY-MM-DD)
- `--output FILE` - Output file path (default: CHANGELOG.md)
- `--append` - Append to existing changelog instead of overwriting
- `--backfill` - Generate complete history from inception

## Automated Workflow

### Trigger

The `update-changelog.yml` workflow runs automatically when:
- A PR is merged to the `main` branch
- The PR contains commits with conventional commit prefixes

### Process

1. **Check for conventional commits** in the merged PR
2. **Generate updated changelog** for the last 7 days
3. **Create a new PR** if changes are detected
4. **Link to the original PR** that triggered the update

### Auto-Merge

Changelog update PRs are automatically created but require manual review and approval before merging.

## Conventional Commit Types

The system recognizes these commit types:

| Type | Icon | Description | Category |
|------|------|-------------|----------|
| `feat` | ✨ | New feature | Features / Major Improvements |
| `fix` | 🐛 | Bug fix | Bug Fixes |
| `docs` | 📚 | Documentation | Chores & Maintenance |
| `chore` | 🧹 | Routine task | Chores & Maintenance |
| `refactor` | ♻️ | Code restructuring | Chores & Maintenance |
| `test` | ✅ | Testing | Chores & Maintenance |
| `perf` | ⚡ | Performance | Chores & Maintenance |
| `ci` | 👷 | CI/CD | Chores & Maintenance |
| `build` | 🔨 | Build system | Chores & Maintenance |
| `style` | 💎 | Code style | Chores & Maintenance |
| `revert` | ⏪ | Revert commit | Chores & Maintenance |

## Auto-Churn Exclusions

The following commits are automatically excluded from the changelog:

### Patterns Excluded
- `🔄 AgentOps data sync`
- `🧠 Daily Learning Reflection`
- `🏗️ Update architecture evolution tracking`
- `Update AI ideas history`
- `[auto]` prefix
- `chore: update reviewer dashboard`
- `Initial plan` commits

### Reasoning
These commits represent:
- Automated data synchronization
- Routine maintenance by bots
- Non-user-facing changes
- Planning commits without actual changes

## Actor Detection

### User-Initiated Changes

Marked with 👤 when:
- Author email contains known user names (e.g., 'enufacas')
- PR merged by main Copilot account (indicates user-prompted work)
- Represents pair programming or issue-prompted work

### Bot-Generated Changes

Marked with 🤖 when:
- Author is `copilot-swe-agent[bot]`
- Author is `github-actions[bot]`
- Represents autonomous agent work

## Major Improvements Category

**Major Improvements** is a special category that captures:
- User-initiated features (feat: commits with 👤 indicator)
- Significant changes explicitly requested through issues
- Features from pair programming sessions

This separates "what the user wanted" from "what the bots did autonomously."

## Examples

### Good Changelog Entries

```markdown
## 2025-12-02

### ✨ Major Improvements

- 👤 Implement feature changelog system with automatic generation [#3520](https://github.com/enufacas/Chained/pull/3520)

### ✨ Features

- 🤖 Add MCP mode for full repository access in Copilot sessions
- 👤 Add "ask gemini" escalation standard for Copilot sessions [#3510](https://github.com/enufacas/Chained/pull/3510)

### 🐛 Bug Fixes

- 🤖 Increase AG-UI Frontend memory limit to 1Gi to prevent OOM crashes
- 👤 Fix authentication flow for third-party OAuth providers [#3505](https://github.com/enufacas/Chained/pull/3505)

### 🧹 Chores & Maintenance

- 🤖 **Documentation**: Add comprehensive implementation summary
- 🤖 **Refactor**: Improve error handling in auto-merge step
```

### Bad Changelog Entries

```markdown
## 2025-12-02

- Fixed stuff (too vague, no type prefix, no actor)
- 🔄 AgentOps data sync (auto-churn, should be excluded)
- The agent updated something (not specific enough)
- chore: update reviewer dashboard (auto-churn)
```

## Maintenance

### Regular Tasks

1. **Weekly**: Review recent changelog entries for accuracy
2. **Monthly**: Verify auto-churn patterns are still effective
3. **Release**: Generate clean changelog for release notes
4. **Quarterly**: Backfill any missing entries from git history

### Troubleshooting

**Changelog not updating after PR merge:**
- Check if commits use conventional commit prefixes
- Verify workflow has necessary permissions
- Check workflow logs for errors

**Too many auto-churn commits appearing:**
- Update `AUTO_CHURN_PATTERNS` in `tools/generate-changelog.py`
- Add new patterns to `.github/instructions/changelog-maintenance.instructions.md`

**Actor indicators incorrect:**
- Update `USER_ACTORS` list in `tools/generate-changelog.py`
- Review actor detection logic in `Commit._determine_user_initiated()`

## Benefits

### For Users
- **Clear history** of what changed and when
- **Distinction** between user-driven and autonomous changes
- **Traceability** via PR links
- **Release notes** generation

### For Contributors
- **Guided documentation** through conventional commits
- **Automatic generation** reduces manual work
- **Consistent format** across all entries

### For Maintainers
- **Historical context** for debugging
- **Planning reference** for future work
- **Audit trail** of project evolution
- **Communication tool** for stakeholders

## Related Documentation

- [CHANGELOG.md](../CHANGELOG.md) - The actual changelog
- [Changelog Maintenance Instructions](./.github/instructions/changelog-maintenance.instructions.md) - Copilot instructions
- [Conventional Commits](https://www.conventionalcommits.org/) - Commit message standard
- [Keep a Changelog](https://keepachangelog.com/) - Changelog format inspiration

## Future Enhancements

Potential improvements to the changelog system:

- [ ] GitHub release notes generation from changelog
- [ ] Changelog viewer web interface on GitHub Pages
- [ ] Breaking changes detection and highlighting
- [ ] Version tagging integration
- [ ] Changelog search functionality
- [ ] Statistics dashboard (features vs fixes ratio, actor distribution)
- [ ] Integration with issue tracking for impact analysis

---

**Maintained by**: Chained Project
**Last Updated**: 2025-12-02
**Version**: 1.0.0
