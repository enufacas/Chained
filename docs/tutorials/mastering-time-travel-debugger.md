# Tutorial: Mastering the Repository Time-Travel Debugger

Welcome! In this hands-on tutorial, you'll learn how to use the Repository Time-Travel Debugger to navigate git history like a pro. By the end, you'll be able to debug issues, understand code evolution, and explore your repository's past with confidence.

## What You'll Learn

- Navigating git history interactively
- Finding when bugs were introduced
- Comparing code across different time periods
- Understanding architectural decisions
- Debugging with historical context
- Advanced search techniques

## Prerequisites

Before you begin, make sure you have:
- Python 3.x installed
- A git repository to explore (we'll use Chained as an example)
- Basic familiarity with git concepts (commits, branches)
- 5 minutes for a quick tour, or 20 minutes for the full tutorial

## Time Required

⏱️ **Quick Start**: 5 minutes | **Complete Tutorial**: 20-25 minutes

---

## What is Time Travel Debugging?

Time travel debugging lets you navigate through your repository's history as easily as browsing files. Instead of manually running `git log` and `git show` commands, you get an interactive interface that feels like stepping through time.

### Why Use It?

- **Debug faster**: Pinpoint exactly when a bug was introduced
- **Understand decisions**: See why code was written a certain way
- **Learn from history**: Understand how the codebase evolved
- **Save time**: No more typing long git commands
- **Interactive exploration**: Navigate history naturally

### Real-World Scenarios

1. **The Mystery Bug**: A feature worked yesterday but is broken today. When did it break?
2. **Code Archaeology**: Why is this workaround here? What problem did it solve?
3. **Merge Investigation**: Which commit caused this merge conflict?
4. **Performance Regression**: When did this code path become slow?

---

## Part 1: Quick Start (5 Minutes)

Let's dive in with a quick tour of the essential features.

### Step 1: Launch the Time Traveler

Open your terminal in the Chained repository:

```bash
cd /path/to/Chained
python3 tools/repo-time-travel.py
```

You'll see:

```
🕰️  Repository Time-Travel Debugger
Current position: 4bb93b1 (2025-11-11 21:14:45)

Commands: go, back, forward, show, list, diff, file, history, search, help, quit
Type 'help' for full command list

time-travel>
```

**What just happened?**
- The tool loaded your repository's git history
- You're currently at the latest commit (HEAD)
- You have an interactive prompt ready for commands

### Step 2: List Recent Commits

Type `list` to see recent commits:

```bash
time-travel> list
```

Output:
```
Recent commits:
→ [0] 4bb93b1 - 2025-11-11 21:14:45 - copilot: Add time travel tutorial
  [1] 4af6ed4 - 2025-11-11 21:12:25 - copilot: Enhance agent system
  [2] ae62686 - 2025-11-11 20:51:18 - Copilot: Add teach-wizard agent
  [3] d123456 - 2025-11-10 15:30:00 - copilot: Fix bug in workflow
  [4] c987654 - 2025-11-10 10:20:15 - copilot: Add learning features
```

The `→` arrow shows your current position in history.

### Step 3: Go Back in Time

Navigate to a previous commit:

```bash
time-travel> back 2
```

Output:
```
Moved back 2 commits to: ae62686
2025-11-11 20:51:18 - Copilot: Add teach-wizard agent
```

**Try it yourself**: Type `list` again to see your new position!

### Step 4: View a Commit

See what changed in the current commit:

```bash
time-travel> show
```

Output:
```
Commit: ae626867a4b3c2d1e5f6
Author: Copilot <copilot@github.com>
Date:   2025-11-11 20:51:18 UTC
Subject: Copilot: Add teach-wizard agent

Files changed:
  A  .github/agents/teach-wizard.md
  M  .github/agents/README.md

Diff stats:
 .github/agents/teach-wizard.md | 120 +++++++++++++++++++
 .github/agents/README.md       |  15 ++-
 2 files changed, 135 insertions(+)
```

### Step 5: Exit

When you're done:

```bash
time-travel> quit
```

**Congratulations!** You just completed the quick start. You now know how to:
- ✅ Launch the time traveler
- ✅ List commits
- ✅ Navigate backward
- ✅ View commit details
- ✅ Exit the tool

**Want to learn more?** Continue to Part 2 for advanced features!

---

## Part 2: Core Navigation (10 Minutes)

Now let's master the navigation commands.

### Understanding History Position

Think of git history as a timeline:

```
PAST ←──────────────────────────────────────→ PRESENT
     [commit 10] [commit 5] [commit 3] [HEAD]
                                           ↑ You are here
```

When you go "back", you move toward the past. "Forward" moves toward the present.

### Navigation Commands

Launch the time traveler:

```bash
python3 tools/repo-time-travel.py
```

#### Command: `list [n]`

Show recent commits. Optional: specify how many (default: 10).

```bash
time-travel> list 5
```

Shows the 5 most recent commits from your current position.

**Pro tip**: Use `list 20` to see more context!

#### Command: `back [n]`

Move backward in history. Optional: specify steps (default: 1).

```bash
time-travel> back        # Go back 1 commit
time-travel> back 5      # Go back 5 commits
```

**What you see**:
```
Moved back 1 commit to: 4af6ed4
2025-11-11 21:12:25 - copilot: Enhance agent system
```

#### Command: `forward [n]`

Move forward toward the present. Optional: specify steps (default: 1).

```bash
time-travel> forward     # Go forward 1 commit
time-travel> forward 3   # Go forward 3 commits
```

**Note**: You can't go forward past HEAD (the latest commit).

#### Command: `go <commit>`

Jump directly to a specific commit:

```bash
time-travel> go ae62686              # Use short hash
time-travel> go ae626867a4b3c2d1     # Or full hash
```

**Pro tip**: You can use the numbers from `list` command:
```bash
time-travel> list
  [0] 4bb93b1 - Latest commit
  [1] 4af6ed4 - Previous commit
  [2] ae62686 - Two commits ago

time-travel> go ae62686   # Jump to commit [2]
```

#### Command: `current`

Show where you are in history:

```bash
time-travel> current
```

Output:
```
Current position:
Hash:    ae626867a4b3c2d1e5f6
Date:    2025-11-11 20:51:18 UTC
Author:  Copilot <copilot@github.com>
Subject: Copilot: Add teach-wizard agent
```

### Practice Exercise: Navigation Challenge

Try this exercise to practice navigation:

1. Launch the time traveler
2. List the last 10 commits
3. Go back 5 commits
4. Check your current position
5. Go forward 2 commits
6. List commits from your new position
7. Return to HEAD (latest commit)

**Solution**:
```bash
time-travel> list 10
time-travel> back 5
time-travel> current
time-travel> forward 2
time-travel> list
time-travel> go HEAD     # or use the actual commit hash of HEAD
```

---

## Part 3: Viewing and Comparing (10 Minutes)

Now let's explore how to view code and compare changes.

### Command: `show [commit]`

View detailed information about a commit:

```bash
time-travel> show
```

Shows the current commit. Or specify a commit:

```bash
time-travel> show 4af6ed4
```

**What you see**:
```
Commit: 4af6ed4b5c6d7e8f9a0b
Author: Copilot <copilot@github.com>
Date:   2025-11-11 21:12:25 UTC
Subject: copilot: Enhance agent system

Body:
Enhanced the agent spawn system with better error handling
and improved performance metrics tracking.

Files changed:
  M  .github/workflows/agent-spawn.yml
  M  tools/generate-new-agent.py
  A  test_agent_spawn_consolidation.py

Diff stats:
 .github/workflows/agent-spawn.yml      | 45 +++++++++++++++---
 tools/generate-new-agent.py            | 23 ++++++---
 test_agent_spawn_consolidation.py      | 156 +++++++++++++++++++
 3 files changed, 214 insertions(+), 10 deletions(-)
```

**Understanding the output**:
- **M** = Modified file
- **A** = Added file
- **D** = Deleted file
- **R** = Renamed file

### Command: `file <commit> <path>`

View a file's content at a specific commit:

```bash
time-travel> file ae62686 .github/agents/teach-wizard.md
```

Shows the complete content of that file as it existed at that commit.

**Practical use**: "What did this configuration file look like before the breaking change?"

```bash
time-travel> file d123456 config/settings.yml
```

### Command: `diff <commit1> <commit2> [file]`

Compare two commits:

```bash
time-travel> diff 4af6ed4 4bb93b1
```

Shows all changes between those two commits.

**Compare a specific file**:
```bash
time-travel> diff 4af6ed4 4bb93b1 tools/generate-new-agent.py
```

Shows only changes to that file between the commits.

**Practical use**: "What changed in the agent system between yesterday and today?"

### Command: `history <path>`

Show all commits that modified a specific file:

```bash
time-travel> history tools/repo-time-travel.py
```

Output:
```
History of tools/repo-time-travel.py:

[0] 4bb93b1 - 2025-11-11 21:14:45 - copilot: Add search features
[1] 3cd45e6 - 2025-11-10 18:30:00 - copilot: Improve navigation
[2] 2ab34c5 - 2025-11-09 14:20:00 - copilot: Initial implementation
```

**Practical use**: "Who has been working on this file? When did it change?"

### Real-World Example: Finding When a Bug Was Introduced

Let's say a test started failing. Here's how to find when:

**Step 1**: Navigate to the time traveler and go to a known good commit:
```bash
time-travel> go abc1234  # Last known working commit
```

**Step 2**: Show the test file at that commit:
```bash
time-travel> file abc1234 test_agent_system.py
# Verify it looks correct
```

**Step 3**: Move forward and check each commit:
```bash
time-travel> forward
time-travel> show
# Look at what changed - does this commit touch the test?
```

**Step 4**: Check the file history:
```bash
time-travel> history test_agent_system.py
```

**Step 5**: Compare the working vs broken versions:
```bash
time-travel> diff abc1234 def5678 test_agent_system.py
```

Now you can see exactly what changed to break the test!

---

## Part 4: Advanced Search (10 Minutes)

The most powerful feature is searching through history.

### Command: `search <query>`

Search commit messages (case-insensitive):

```bash
time-travel> search "fix bug"
```

Output:
```
Found 3 commits matching "fix bug":

[0] d123456 - 2025-11-10 15:30:00 - copilot: Fix bug in workflow
[1] a987654 - 2025-11-05 10:15:00 - copilot: Fix bug in agent assignment
[2] 7654321 - 2025-11-01 14:45:00 - copilot: Fix bug in learning system
```

**Use case**: "Find all commits related to authentication issues"
```bash
time-travel> search authentication
```

### Command: `search-author <name>`

Find commits by a specific author:

```bash
time-travel> search-author copilot
```

Output:
```
Found 47 commits by copilot:

[0] 4bb93b1 - 2025-11-11 21:14:45 - copilot: Add time travel tutorial
[1] 4af6ed4 - 2025-11-11 21:12:25 - copilot: Enhance agent system
[2] ae62686 - 2025-11-11 20:51:18 - Copilot: Add teach-wizard agent
...
```

**Use case**: "What has this contributor been working on?"

### Command: `search-file <path>`

Find all commits that changed a specific file:

```bash
time-travel> search-file .github/workflows/copilot-graphql-assign.yml
```

**Use case**: "When was this workflow last modified?"

### Command: `search-code <text>`

Search for commits that added or removed specific code:

```bash
time-travel> search-code "def generate_fibonacci"
```

This uses `git log -S` to find commits where this code was added or removed.

**Use case**: "When was this function introduced?"

**Advanced example**:
```bash
time-travel> search-code "COPILOT_PAT"
```

Finds commits that added or removed references to the COPILOT_PAT secret.

### Command: `blame <path>`

Show who last modified each line of a file:

```bash
time-travel> blame tools/repo-time-travel.py
```

Output shows each line with:
- Commit hash that last changed it
- Author
- Date
- Line content

**Use case**: "Who wrote this specific line of code?"

### Search Strategy: The Detective's Toolkit

Here's a systematic approach to investigating issues:

**1. Start with the symptom**
```bash
time-travel> search "error message text"
```

**2. Find related files**
```bash
time-travel> search-file path/to/problem/file.py
```

**3. Check recent authors**
```bash
time-travel> search-author "suspected-author"
```

**4. Look for code patterns**
```bash
time-travel> search-code "problematic_function"
```

**5. Navigate to suspicious commits**
```bash
time-travel> go <suspicious-commit-hash>
time-travel> show
```

**6. Compare before and after**
```bash
time-travel> diff <before> <after>
```

---

## Part 5: Non-Interactive Mode (5 Minutes)

You can also use the time traveler as a command-line tool without the interactive prompt.

### List Recent Commits

```bash
python3 tools/repo-time-travel.py --list 10
```

Output goes directly to your terminal.

### Show a Specific Commit

```bash
python3 tools/repo-time-travel.py --show abc1234
```

### Search from Command Line

```bash
python3 tools/repo-time-travel.py --search "bug fix"
python3 tools/repo-time-travel.py --search-author copilot
```

### Show File History

```bash
python3 tools/repo-time-travel.py --history tools/code-analyzer.py
```

### Use in Scripts

Combine with other commands:

```bash
# Find the last commit that touched a file
python3 tools/repo-time-travel.py --history README.md | head -n 1

# Search and count results
python3 tools/repo-time-travel.py --search "security" | wc -l

# Get commits from a specific author today
python3 tools/repo-time-travel.py --search-author copilot | grep "2025-11-11"
```

### Pipe to Files

Save results for later analysis:

```bash
# Save recent commits to a file
python3 tools/repo-time-travel.py --list 100 > recent_commits.txt

# Save search results
python3 tools/repo-time-travel.py --search "refactor" > refactoring_commits.txt
```

---

## Part 6: Real-World Use Cases

Let's walk through practical scenarios you'll encounter.

### Use Case 1: Debugging a Production Issue

**Scenario**: A feature works in staging but breaks in production.

**Solution**:

1. **Identify the deployment commit**:
```bash
python3 tools/repo-time-travel.py --search "deploy to production"
```

2. **Check what changed**:
```bash
time-travel> go <production-commit>
time-travel> show
```

3. **Compare with staging**:
```bash
time-travel> diff <staging-commit> <production-commit>
```

4. **Find the culprit**:
Look for differences in configuration, dependencies, or code.

### Use Case 2: Understanding a Code Design Decision

**Scenario**: You find strange code and wonder why it's written that way.

**Solution**:

1. **Find when the file was created**:
```bash
time-travel> history path/to/strange/file.py
# Go to the first commit in the list
```

2. **View the original commit**:
```bash
time-travel> go <first-commit>
time-travel> show
```

3. **Read the commit message and changes**:
The commit message often explains the reasoning.

4. **Check if there were related changes**:
```bash
time-travel> search "related keyword"
```

### Use Case 3: Performance Regression Investigation

**Scenario**: Your application was fast a month ago but is slow now.

**Solution**:

1. **Find commits in the last month**:
```bash
time-travel> list 100  # Adjust number as needed
```

2. **Search for performance-related changes**:
```bash
time-travel> search "performance"
time-travel> search "optimize"
time-travel> search "slow"
```

3. **Check files that handle the slow operation**:
```bash
time-travel> history path/to/slow/operation.py
```

4. **Binary search through history**:
- Go back 50 commits
- Test if it's slow
- If slow, go back 25 more; if fast, go forward 25
- Repeat until you find the exact commit

5. **Analyze the problematic commit**:
```bash
time-travel> show <slow-commit>
time-travel> diff <fast-commit> <slow-commit>
```

### Use Case 4: Merge Conflict Resolution

**Scenario**: You have a merge conflict and need to understand the history.

**Solution**:

1. **Find when your branch diverged**:
```bash
time-travel> search-author "your-name"
# Find your first commit after branching
```

2. **Check what changed on main**:
```bash
time-travel> search-file <conflicted-file>
# See commits on main that touched the file
```

3. **Compare the versions**:
```bash
time-travel> diff <your-commit> <main-commit> <conflicted-file>
```

4. **Understand both changes**:
Navigate to each commit and read the full context.

### Use Case 5: Code Archaeology for Documentation

**Scenario**: You need to document a complex system.

**Solution**:

1. **Find the initial implementation**:
```bash
time-travel> history path/to/system/main.py
# Go to the oldest commit
```

2. **Trace the evolution**:
```bash
time-travel> go <oldest-commit>
time-travel> show
time-travel> forward
time-travel> show
# Repeat to see how it evolved
```

3. **Identify major milestones**:
```bash
time-travel> search "add feature"
time-travel> search "rewrite"
time-travel> search "refactor"
```

4. **Document the decisions**:
Use commit messages and code changes to write documentation.

---

## Troubleshooting

### Issue: "git command failed"

**Cause**: Not in a git repository or git not installed.

**Solution**:
```bash
# Verify you're in a git repo
git status

# If not, initialize one
git init

# Or navigate to your repository
cd /path/to/your/repo
```

### Issue: "No commits found"

**Cause**: Repository has no commits yet.

**Solution**:
```bash
# Create an initial commit
echo "# My Project" > README.md
git add README.md
git commit -m "Initial commit"

# Now launch the time traveler
python3 tools/repo-time-travel.py
```

### Issue: "Commit hash not found"

**Cause**: Invalid commit hash or typo.

**Solution**:
- Use `list` to see valid commit hashes
- Use at least the first 7 characters of the hash
- Check for typos in the hash

### Issue: "Cannot go forward"

**Cause**: Already at HEAD (latest commit).

**Solution**:
- Use `current` to check your position
- You can only go forward if you've gone back first
- `go HEAD` to return to the latest commit

### Issue: Command Line Mode Not Working

**Cause**: Python or tool not in PATH.

**Solution**:
```bash
# Use full path to Python
/usr/bin/python3 tools/repo-time-travel.py --list

# Or add to PATH
export PATH=$PATH:/path/to/python
```

---

## Tips and Best Practices

### Navigation Tips

1. **Use short hashes**: Only need first 7-8 characters
   ```bash
   time-travel> go abc1234  # Not abc1234567890abcdef
   ```

2. **Bookmark important commits**: Copy hashes to a text file
   ```
   v1.0 release: abc1234
   Last working state: def5678
   Bug introduction: ghi9012
   ```

3. **Use relative navigation**: `back` and `forward` for nearby commits
   ```bash
   time-travel> back 3
   time-travel> forward 1
   ```

4. **Jump to HEAD quickly**: Always use `go HEAD` to return

### Search Tips

1. **Use specific keywords**: Better than generic terms
   ```bash
   time-travel> search "authentication bug"  # Good
   time-travel> search "fix"                 # Too broad
   ```

2. **Search authors by username**: Exact matches work best
   ```bash
   time-travel> search-author copilot
   ```

3. **Search code for unique strings**: Use distinctive function names
   ```bash
   time-travel> search-code "calculate_agent_score"  # Good
   time-travel> search-code "return"                 # Too common
   ```

4. **Combine searches**: Use multiple searches to narrow down
   ```bash
   time-travel> search "security"
   time-travel> search-file "auth.py"
   # Look for overlap in results
   ```

### Efficiency Tips

1. **Start wide, narrow down**: Begin with broad searches, refine
2. **Use `history` first**: For file-specific investigations
3. **Check recent commits first**: Most issues are recent
4. **Save command outputs**: Pipe to files for complex investigations

### Integration Tips

**Pre-commit hook**: Check commit messages
```bash
# .git/hooks/pre-commit
python3 tools/repo-time-travel.py --list 1 > /tmp/last_commit.txt
```

**CI/CD**: Validate changes
```bash
# In your CI script
python3 tools/repo-time-travel.py --show $CI_COMMIT_SHA
```

**Code reviews**: Understand PR context
```bash
python3 tools/repo-time-travel.py --history $CHANGED_FILE
```

---

## What You've Learned

Congratulations! You now know how to:

- ✅ Launch and navigate the time traveler interactively
- ✅ List and view commits with detailed information
- ✅ Move through history with back, forward, and go commands
- ✅ Compare code between different commits
- ✅ Search for commits by message, author, file, and code
- ✅ View file content at any point in history
- ✅ Use non-interactive mode for scripts and automation
- ✅ Apply time travel debugging to real-world scenarios
- ✅ Troubleshoot common issues
- ✅ Follow best practices for efficient investigation

## Next Steps

Now that you're a time travel debugging master:

1. **Practice**: Use the tool in your daily workflow
2. **Automate**: Integrate it into your scripts and CI/CD
3. **Explore**: Try it on different repositories
4. **Teach**: Share these techniques with your team
5. **Extend**: The code is open source - contribute improvements!

### Related Tools

Combine time travel debugging with other Chained tools:

- **[Code Archaeologist](../tools/CODE_ARCHAEOLOGIST.md)**: Automated history analysis
- **[Code Analyzer](../tools/README.md#-self-improving-code-analyzer)**: Pattern detection
- **[Readability Scorer](../tools/READABILITY_SCORER.md)**: Code quality metrics

### Further Learning

- **Git internals**: Understand how git stores history
- **Bisect**: Learn about `git bisect` for automated bug finding
- **Reflog**: Explore `git reflog` for recovering lost commits
- **Advanced git**: Study `git log` options for custom queries

---

## Command Reference

### Interactive Commands

| Command | Syntax | Description |
|---------|--------|-------------|
| `list` | `list [n]` | List n recent commits (default: 10) |
| `back` | `back [n]` | Go back n commits (default: 1) |
| `forward` | `forward [n]` | Go forward n commits (default: 1) |
| `go` | `go <commit>` | Jump to specific commit |
| `show` | `show [commit]` | Show commit details |
| `current` | `current` | Show current position |
| `file` | `file <commit> <path>` | View file at commit |
| `diff` | `diff <c1> <c2> [file]` | Compare commits |
| `history` | `history <path>` | Show file history |
| `search` | `search <query>` | Search commit messages |
| `search-author` | `search-author <name>` | Find commits by author |
| `search-file` | `search-file <path>` | Find commits for file |
| `search-code` | `search-code <text>` | Search in code content |
| `blame` | `blame <path>` | Show line-by-line authors |
| `branches` | `branches [commit]` | Show branches at commit |
| `tags` | `tags [commit]` | Show tags at commit |
| `help` | `help` | Show help message |
| `quit` | `quit` or `exit` | Exit the time traveler |

### Command-Line Options

| Option | Description |
|--------|-------------|
| `--list N` | List N recent commits |
| `--show HASH` | Show commit details |
| `--search QUERY` | Search commit messages |
| `--search-author NAME` | Find commits by author |
| `--search-file PATH` | Find commits for file |
| `--history PATH` | Show file history |

---

## Feedback and Contributions

### Found a Bug?

Create an issue with label `tool-bug`:
- Tool: Repository Time-Travel Debugger
- What you tried
- What happened vs. what you expected
- Your git version and Python version

### Have a Feature Idea?

Create an issue with label `tool-enhancement`:
- Describe the use case
- Explain how it would help
- Provide example usage

### Want to Improve This Tutorial?

- Open a PR with improvements
- Add more examples or use cases
- Fix typos or clarify confusing sections
- Add screenshots or diagrams

---

**Happy time traveling!** 🕰️ May you debug with the wisdom of hindsight!

*Tutorial created by Lovelace, the teach-wizard agent, to illuminate the path of learning for all.*
