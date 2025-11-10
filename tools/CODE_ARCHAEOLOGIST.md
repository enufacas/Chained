# 🏛️ AI Code Archaeologist

An intelligent tool that analyzes git history to document legacy decisions, understand architectural evolution, and track technical debt.

## Overview

The AI Code Archaeologist is designed to help developers understand the "why" behind code by analyzing git commit history. It extracts architectural decisions, tracks technical debt, and documents how the codebase has evolved over time.

## Key Concepts

### What is Code Archaeology?

Code archaeology is the practice of understanding legacy code by examining its history. Instead of just seeing what the code does now, archaeology reveals:

- **Why** decisions were made
- **When** architectural changes happened
- **Who** contributed key features
- **What** technical debt exists

This helps new developers understand the codebase faster and helps teams avoid repeating past mistakes.

## Features

### 🏗️ Architectural Decision Tracking

Automatically extracts architectural decisions from commit messages by looking for patterns like:
- "Decided to..."
- "Chose to..."
- "Migrated to..."
- "Changed to... because..."

### ⚠️ Technical Debt Detection

Identifies technical debt items by scanning for:
- TODO comments in commits
- FIXME annotations
- HACK warnings
- Workaround mentions
- Temporary solutions

### 📊 Code Evolution Timeline

Categorizes commits into:
- **Architectural Refactors**: Design changes and restructuring
- **Feature Additions**: New capabilities
- **Bug Fixes**: Problem resolutions
- **Maintenance**: Regular updates and cleanup

### 📈 Statistics & Insights

Provides comprehensive statistics:
- Commits by category
- Top contributors
- Most frequently changed files
- Decision timeline
- Technical debt accumulation

## Installation

The archaeologist is a standalone Python script with no external dependencies:

```bash
# Make the script executable
chmod +x tools/code-archaeologist.py

# Run directly
./tools/code-archaeologist.py --help
```

## Usage

### Basic Usage

```bash
# Analyze last 100 commits in current repository
python3 tools/code-archaeologist.py

# Analyze specific number of commits
python3 tools/code-archaeologist.py -n 50

# Analyze different repository
python3 tools/code-archaeologist.py -d /path/to/repo
```

### Time-Based Analysis

```bash
# Analyze last month
python3 tools/code-archaeologist.py --since "1 month ago"

# Analyze last year
python3 tools/code-archaeologist.py --since "1 year ago"

# Analyze since specific date
python3 tools/code-archaeologist.py --since "2023-01-01"
```

### Output Options

```bash
# Save report to file
python3 tools/code-archaeologist.py -o report.md

# Generate JSON output
python3 tools/code-archaeologist.py --format json -o report.json

# Analyze and save (default saves to analysis/ directory)
python3 tools/code-archaeologist.py -n 200
```

### Command-Line Options

```
-d, --directory DIR      Repository directory to analyze (default: current)
-n, --max-commits NUM    Maximum number of commits to analyze (default: 100)
--since DATE            Only analyze commits since this date
-o, --output FILE       Output file for report (default: stdout)
--format FORMAT         Output format: text or json (default: text)
```

## Understanding the Output

### Report Structure

The report includes:

1. **Summary**: High-level statistics
2. **Statistics**: Detailed breakdowns
3. **Architectural Decisions**: Extracted decisions with context
4. **Technical Debt**: Identified debt items
5. **Code Evolution**: Timeline of changes
6. **Insights**: Automated observations
7. **Recommendations**: Actionable next steps

### Example Report

```markdown
# 🏛️ Code Archaeology Report

**Generated:** 2024-01-15T10:30:00+00:00
**Repository:** MyProject

## 📊 Summary
- Total commits analyzed: 150
- Architectural decisions found: 18
- Technical debt items found: 12

## 📈 Statistics

### Commits by Category
- **feature**: 65 commits
- **bug_fix**: 45 commits
- **architectural**: 25 commits
- **technical_debt**: 15 commits

### Top Contributors
- **Alice**: 80 commits
- **Bob**: 45 commits
- **Charlie**: 25 commits

### Most Changed Files
- `src/main.py`: 42 changes
- `config/settings.py`: 28 changes
- `utils/helpers.py`: 21 changes

## 🏗️ Architectural Decisions

Found 18 documented decisions:

1. **Migrated from REST to GraphQL because it reduces over-fetching**
   - Commit: `abc123d`
   - Date: 2023-12-01

2. **Decided to use PostgreSQL instead of MySQL due to better JSON support**
   - Commit: `def456e`
   - Date: 2023-11-15

## ⚠️ Technical Debt

Found 12 technical debt items:

1. **TODO: Refactor authentication module to use OAuth2**
   - Commit: `ghi789f`
   - Date: 2023-10-20
   - Files: auth/login.py, auth/session.py

2. **FIXME: Temporary workaround for database connection pooling**
   - Commit: `jkl012g`
   - Date: 2023-09-15
   - Files: db/connection.py

## 💡 Insights

- 📝 This repository has documented architectural decisions in commit messages
- ⚠️ 12 technical debt items identified - consider addressing them
- 🏗️ High refactoring activity (16.7%) suggests active code improvement

## 🎯 Recommendations

- 🔧 Address 12 documented technical debt items
- 📋 Create issues for TODO/FIXME items to track them properly
- 📖 Continue documenting legacy decisions for future maintainers
- 🔍 Run this tool regularly to track decision evolution
```

## Database Structure

The archaeologist maintains a JSON database at `analysis/archaeology.json`:

```json
{
  "version": "1.0.0",
  "last_updated": "2024-01-15T10:30:00+00:00",
  "repository": "MyProject",
  "total_commits_analyzed": 150,
  "architectural_decisions": [
    {
      "type": "explicit_decision",
      "content": "migrated from REST to GraphQL",
      "commit": "abc123d",
      "timestamp": "2023-12-01T00:00:00+00:00"
    }
  ],
  "technical_debt": [
    {
      "type": "technical_debt",
      "description": "TODO: Refactor authentication module",
      "commit": "ghi789f",
      "timestamp": "2023-10-20T00:00:00+00:00",
      "files": ["auth/login.py"]
    }
  ],
  "code_evolution": {
    "major_refactors": [],
    "feature_additions": [],
    "bug_fixes": []
  },
  "decision_timeline": []
}
```

## GitHub Actions Integration

The archaeologist runs automatically via GitHub Actions:

### Weekly Analysis

Runs every Monday at 9 AM UTC, analyzing the last 100 commits and generating a report.

### Manual Trigger

You can trigger the workflow manually from the Actions tab:

1. Go to **Actions** → **Code Archaeologist**
2. Click **Run workflow**
3. Optionally specify:
   - Number of commits to analyze
   - Date to analyze from
4. View the generated report and issue

### Workflow Features

- Analyzes repository history
- Generates markdown report
- Commits archaeology database
- Creates GitHub issue with findings
- Uploads artifacts for download

## Best Practices

### Writing Archaeology-Friendly Commits

To help the archaeologist extract better information:

**✅ Do:**
- Explain WHY you made changes, not just what
- Use clear language: "Decided to...", "Changed to... because..."
- Document workarounds explicitly: "Temporary workaround for..."
- Tag technical debt: "TODO:", "FIXME:", "HACK:"

**Example good commit:**
```
Refactor: Migrate authentication to JWT tokens

Decided to use JWT instead of session cookies because:
- Better support for microservices architecture
- Easier to scale horizontally
- Simplifies mobile app integration
```

**❌ Don't:**
- Write vague messages: "fix stuff", "update code"
- Omit reasoning: "Use JWT tokens" (no explanation)
- Leave hidden technical debt
- Mix multiple unrelated changes

### Regular Analysis

Run archaeology regularly to:
- Onboard new developers faster
- Review technical debt accumulation
- Document architectural evolution
- Learn from past decisions

### Integrating with Development

Use archaeology findings to:
- Create issues from technical debt
- Document architectural decision records (ADRs)
- Plan refactoring sprints
- Improve commit message quality

## Limitations

- **Commit Message Quality**: Depends on quality of commit messages
- **Language Understanding**: Uses pattern matching, not true NLP
- **Context**: Cannot understand complex business logic
- **History Depth**: Large repositories may need limited analysis
- **Decision Coverage**: Only finds explicitly documented decisions

## Tips for Better Results

1. **Analyze Recent History**: Focus on last 100-200 commits for relevant insights
2. **Time-Based Analysis**: Use `--since` to analyze specific periods
3. **Regular Runs**: Run weekly to track evolution over time
4. **Team Education**: Teach team to write archaeology-friendly commits
5. **Review Findings**: Use reports to create proper documentation

## Use Cases

### Onboarding New Developers

```bash
# Generate comprehensive history report
python3 tools/code-archaeologist.py -n 500 -o onboarding_history.md
```

Help new developers understand:
- Why the architecture is designed this way
- What technical debt exists
- What major refactors happened

### Technical Debt Review

```bash
# Focus on recent technical debt
python3 tools/code-archaeologist.py --since "3 months ago"
```

Review and address accumulated technical debt.

### Architecture Documentation

```bash
# Extract architectural decisions
python3 tools/code-archaeologist.py -n 1000 --format json
```

Generate ADR-style documentation from commit history.

### Code Review

```bash
# Analyze changes in a feature branch
git log feature-branch --format=%H | head -20 | \
  xargs -I {} python3 tools/code-archaeologist.py ...
```

Understand the reasoning behind feature implementation.

## Contributing

To enhance the archaeologist:

1. Add new decision patterns in `_extract_decisions()`
2. Improve categorization in `_categorize_commit()`
3. Add language-specific analysis
4. Enhance report formatting
5. Add new statistics

## Testing

Run the comprehensive test suite:

```bash
python3 tools/test_code_archaeologist.py
```

Tests cover:
- Git history parsing
- Decision extraction
- Technical debt detection
- Report generation
- Database persistence

## Related Tools

- **Code Analyzer**: Analyzes code patterns and quality
- **Pattern Matcher**: Detects anti-patterns and security issues
- **Code Golf Optimizer**: Minimizes code size

## License

Part of the Chained autonomous AI development system.

---

*Uncover the stories hidden in your git history* 🏛️
