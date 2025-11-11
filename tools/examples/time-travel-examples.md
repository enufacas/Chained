# 🕰️ Repository Time-Travel Debugger - Usage Examples

This guide provides practical examples of using the Repository Time-Travel Debugger.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Basic Commands](#basic-commands)
3. [Search Operations](#search-operations)
4. [Navigation](#navigation)
5. [File Operations](#file-operations)
6. [Advanced Usage](#advanced-usage)
7. [Common Workflows](#common-workflows)

---

## Quick Start

### Run Interactive Mode
```bash
python3 tools/repo-time-travel.py
```

### Quick Operations (Non-Interactive)
```bash
# List last 10 commits
python3 tools/repo-time-travel.py --list 10

# Show commit details
python3 tools/repo-time-travel.py --show abc1234

# Search commits
python3 tools/repo-time-travel.py --search "fix bug"

# Show file history
python3 tools/repo-time-travel.py --history path/to/file.py
```

---

## Basic Commands

### Listing Commits

```bash
# In interactive mode:
time-travel> list 5

# Output:
→ [0] ad2ef51 - 2025-11-11 21:18:49 - copilot: Add time-travel debugger
  [1] 4bb93b1 - 2025-11-11 21:14:45 - copilot: Initial plan
  [2] 4af6ed4 - 2025-11-11 21:12:25 - copilot: Add feature
```

### Showing Commit Details

```bash
time-travel> show ad2ef51

# Output:
Commit: ad2ef51...
Author: copilot-swe-agent[bot]
Date:   2025-11-11 21:18:49 UTC

    Add repository time-travel debugger tool with tests

Files changed:
  A (added) tools/repo-time-travel.py
  A (added) tools/test_repo_time_travel.py
  M (modified) tools/README.md
```

### Current Position

```bash
time-travel> current

# Shows details of your current position in history
```

---

## Search Operations

### Search by Commit Message

```bash
time-travel> search fix bug

# Finds all commits with "fix bug" in the message
Found 3 commits:
abc1234 - 2025-11-10 15:30:45 - john: Fix bug in parser
def5678 - 2025-11-09 10:20:30 - jane: Fix bug in validator
```

### Search by Author

```bash
time-travel> search-author john

# Finds all commits by author "john"
Found 15 commits:
abc1234 - 2025-11-10 15:30:45 - john: Fix bug in parser
ghi9012 - 2025-11-08 09:15:20 - john: Add new feature
```

### Search by File

```bash
time-travel> search-file tools/analyzer.py

# Finds all commits that modified tools/analyzer.py
Found 8 commits:
abc1234 - 2025-11-10 15:30:45 - john: Update analyzer
def5678 - 2025-11-05 14:20:10 - jane: Add new metrics
```

### Search in Code Content

```bash
time-travel> search-code "def calculate_score"

# Finds commits that added/removed/modified this function
Found 2 commits:
abc1234 - 2025-11-10 15:30:45 - john: Add scoring function
def5678 - 2025-11-08 10:15:30 - jane: Update scoring logic
```

---

## Navigation

### Navigate to Specific Commit

```bash
time-travel> go abc1234

# Navigates directly to commit abc1234
Navigated to: abc1234 - 2025-11-10 15:30:45 - john: Fix bug
```

### Go Back in History

```bash
# Go back 1 commit
time-travel> back

# Go back 5 commits
time-travel> back 5

Moved back to: ghi9012 - 2025-11-08 09:15:20 - john: Add feature
```

### Go Forward in History

```bash
# Go forward 1 commit
time-travel> forward

# Go forward 3 commits
time-travel> forward 3

Moved forward to: abc1234 - 2025-11-10 15:30:45 - john: Fix bug
```

---

## File Operations

### View File at Specific Commit

```bash
time-travel> file abc1234 tools/analyzer.py

# Shows the content of tools/analyzer.py at commit abc1234
```

### File History

```bash
time-travel> history tools/analyzer.py

# Shows all commits that modified this file
History for tools/analyzer.py:
abc1234 - 2025-11-10 15:30:45 - john: Update analyzer
def5678 - 2025-11-05 14:20:10 - jane: Add new metrics
ghi9012 - 2025-10-20 09:30:00 - bob: Initial analyzer
```

### Diff Between Commits

```bash
# Diff entire repository between two commits
time-travel> diff abc1234 def5678

# Diff specific file between two commits
time-travel> diff abc1234 def5678 tools/analyzer.py
```

### Blame File

```bash
time-travel> blame tools/analyzer.py

# Shows who modified each line and when
abc1234 (john, 2025-11-10):
  def calculate_score():
      return 42

def5678 (jane, 2025-11-05):
  def validate_input(data):
      return True
```

---

## Advanced Usage

### Branch Information

```bash
# Show branches that contain current commit
time-travel> branches

# Show branches at specific commit
time-travel> branches abc1234

Branches containing abc1234:
  main
  feature/new-analyzer
  develop
```

### Tag Information

```bash
# Show tags at current commit
time-travel> tags

# Show tags at specific commit
time-travel> tags abc1234

Tags at abc1234:
  v1.0.0
  release-2025-11
```

---

## Common Workflows

### 1. Debugging When a Bug Was Introduced

**Goal:** Find when a specific bug was introduced.

```bash
# Start time-travel debugger
python3 tools/repo-time-travel.py

# Search for commits related to the feature
time-travel> search-code "problematic_function"

# Navigate to suspicious commit
time-travel> go abc1234

# View the file at that commit
time-travel> file abc1234 src/module.py

# Compare with previous commit
time-travel> back
time-travel> file def5678 src/module.py

# Check the diff
time-travel> diff def5678 abc1234 src/module.py
```

### 2. Understanding Code Evolution

**Goal:** Understand how a file evolved over time.

```bash
# Get file history
time-travel> history src/important.py

# Navigate to first commit
time-travel> go oldest_commit_hash

# View file at that time
time-travel> show

# Step through history
time-travel> forward
time-travel> show
time-travel> forward
time-travel> show
```

### 3. Finding Who Introduced a Feature

**Goal:** Find the author and commit that introduced specific code.

```bash
# Search for the feature in code
time-travel> search-code "new_feature_function"

# View the commit
time-travel> show abc1234

# Get detailed blame
time-travel> blame src/feature.py
```

### 4. Investigating Merge Issues

**Goal:** Understand what changed in different branches.

```bash
# Find commits on feature branch
time-travel> search-author feature-developer

# Navigate to branch point
time-travel> go branch_point_hash

# Check branches at that point
time-travel> branches

# View differences
time-travel> diff main_branch feature_branch
```

### 5. Reviewing Author Contributions

**Goal:** Review all changes by a specific author.

```bash
# Search by author
time-travel> search-author john

# Review each commit
time-travel> go abc1234
time-travel> show

time-travel> forward
time-travel> show
```

---

## Tips and Tricks

### Quick Navigation

- Use commit indices from `list` command: The numbers shown in `[0]`, `[1]`, etc. correspond to steps backward
- Use short commit hashes: `go abc1234` works, you don't need the full hash
- Chain navigation: Go back multiple times, review, then forward back to where you were

### Effective Searching

- **Message search** is case-insensitive
- **Code search** finds when lines were added/removed containing the text
- **File search** shows the complete history of a file
- Combine searches: Search first, then navigate to results

### Working with Large Repositories

- Use `--list N` for quick overviews without entering interactive mode
- Search first to narrow down commits of interest
- Use file-specific operations to focus on relevant parts

### Keyboard Shortcuts

- Press `Ctrl+C` to cancel current command (not exit)
- Use `quit` or `q` to exit
- Press `Up Arrow` in many terminals to recall previous commands

---

## Integration with Development Workflow

### Pre-commit Investigation
```bash
# Before committing, check recent history
python3 tools/repo-time-travel.py --list 5

# Ensure your changes don't duplicate recent work
```

### Code Review
```bash
# Review changes in a PR
time-travel> diff main feature-branch tools/module.py
```

### Bug Investigation
```bash
# When a bug is reported, find when it appeared
time-travel> search "feature that broke"
time-travel> go suspected_commit
time-travel> file suspected_commit path/to/file.py
```

### Documentation
```bash
# Document why code exists
time-travel> history src/legacy.py
time-travel> show oldest_commit
# Use commit messages and diffs to understand original intent
```

---

## Troubleshooting

### "Commit not found"
- Verify the commit hash is correct
- Try using a longer hash (first 7+ characters)
- Ensure you're in the correct repository

### "Cannot go forward/back"
- You've reached the end of history (oldest/newest commit)
- Use `list` to see available commits

### "File not found at commit"
- The file may not exist at that commit
- Check commit details with `show` to see files changed
- Use `history` to see when the file was added

---

## Examples from Real Usage

### Example 1: Finding a Performance Regression

```bash
time-travel> search "optimize performance"
Found 3 commits

time-travel> go abc1234
time-travel> show
# Check what optimization was made

time-travel> forward
time-travel> show
# See if later changes reverted the optimization
```

### Example 2: Understanding Architecture Decisions

```bash
time-travel> history src/core/architecture.py
# See all architectural changes

time-travel> go first_commit
time-travel> show
# Read original commit message explaining design

time-travel> diff first_commit latest_commit
# See how architecture evolved
```

---

## Getting Help

```bash
time-travel> help
# Shows available commands

time-travel> help <command>
# Shows help for specific command (if available)
```

For more information, see the [tools/README.md](README.md) documentation.
