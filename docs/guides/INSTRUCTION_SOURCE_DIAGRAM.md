# Instruction Source Diagram for Pull Requests

## Overview

All Pull Requests created by GitHub Copilot in this repository must include an **Instruction Source Diagram** that shows where Copilot sourced its instructions from. This provides transparency and helps reviewers understand the context and constraints that guided the code generation.

## Purpose

The instruction source diagram serves multiple purposes:

1. **Transparency**: Shows exactly which instructions influenced the PR
2. **Accountability**: Makes it clear which agents and rules were involved
3. **Debugging**: Helps identify if wrong instructions were applied
4. **Learning**: Helps understand how the instruction system works
5. **Audit Trail**: Provides a record of what context was available

## What's Included in the Diagram

The diagram shows four main sources of instructions:

### 1. Repository-Level Instructions
- `.copilot-instructions.md` (root)
- `.github/copilot-instructions.md`

These are always active and provide base-level guidance for all work in the repository.

### 2. Issue/Prompt
- The original issue that triggered the work
- Includes a link to the issue for reference

### 3. Agent Profile (if applicable)
- The specialized agent assigned to the issue
- Links to the agent's profile in `.github/agents/`
- Shows the agent's specialization and approach

### 4. Path-Based Instructions
- Instructions that apply to specific files or directories
- Located in `.github/instructions/*.instructions.md`
- Use YAML frontmatter with `applyTo` patterns to specify which files they affect

## How to Generate the Diagram

The diagram is generated using the `tools/generate-instruction-diagram.py` utility.

### Basic Usage

```bash
python3 tools/generate-instruction-diagram.py \
  --issue ISSUE_NUMBER \
  --agent AGENT_NAME \
  --files FILE1 FILE2 FILE3 ...
```

### Parameters

- `--issue`: Issue number that triggered this work (e.g., `123`)
- `--agent`: Name of the assigned agent without @ (e.g., `engineer-master`)
- `--files`: List of files that were modified (used to detect applicable path instructions)
- `--repo-root`: Repository root directory (optional, defaults to current directory)

### Example

```bash
python3 tools/generate-instruction-diagram.py \
  --issue 456 \
  --agent organize-guru \
  --files \
    .github/workflows/test.yml \
    .github/workflows/deploy.yml \
    docs/README.md
```

## Output Format

The tool generates markdown output with two main sections:

### 1. ASCII Diagram

A visual representation showing the instruction flow:

```
                    ╔══════════════════════════════════╗
                    ║   GitHub Copilot Instructions   ║
                    ╚══════════════════════════════════╝
                                  │
                                  │
        ┌─────────────────────────┼─────────────────────────┐
        │                         │                         │
        ▼                         ▼                         ▼
  ┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
  │   Repository    │       │  Issue/Prompt   │       │  Agent Profile  │
  │  Instructions   │       │    #  123        │       │  @engineer-master│
  └─────────────────┘       └─────────────────┘       └─────────────────┘
        │
        ▼
  ┌─────────────────────────────────────────────┐
  │       Path-Specific Instructions           │
  │           (4 files apply)                   │
  └─────────────────────────────────────────────┘
```

### 2. Detailed Table

A table listing all instruction sources with links:

| Source Type | Location | Description |
|-------------|----------|-------------|
| 📚 Repository | `.copilot-instructions.md` | Base repository instructions |
| 🎯 Prompt | Issue #456 | Original issue description |
| 🤖 Agent | @organize-guru | Organizing code structure... |
| 📍 Path Rules | `branch-protection.instructions.md` | Branch Protection: PR-Based... |

## Integration with PR Workflow

### When Creating a PR

1. Collect the list of modified files
2. Identify the assigned agent (from issue body or labels)
3. Get the issue number
4. Run the diagram generator
5. Include the output in your PR description

### Automated Integration

For automated workflows, the diagram generation can be integrated into the PR creation script:

```bash
# Get modified files
MODIFIED_FILES=$(git diff --name-only origin/main)

# Extract agent name from issue body
AGENT_NAME=$(gh issue view $ISSUE_NUMBER --json body | jq -r '.body' | grep -oP '@\K[\w-]+' | head -1)

# Generate diagram
DIAGRAM=$(python3 tools/generate-instruction-diagram.py \
  --issue $ISSUE_NUMBER \
  --agent $AGENT_NAME \
  --files $MODIFIED_FILES)

# Include in PR description
gh pr create \
  --title "..." \
  --body "## Changes

...

$DIAGRAM"
```

## Path-Based Instruction Matching

The tool uses glob pattern matching to determine which path-based instructions apply:

### Pattern Examples

- `**/*.yml` - All YAML files anywhere
- `.github/workflows/*.yml` - YAML files in workflows directory
- `docs/**/*.html` - HTML files in docs and subdirectories
- `tools/*.py` - Python files directly in tools directory

### How It Works

1. Each `.instructions.md` file has a YAML frontmatter section
2. The `applyTo` field contains a list of glob patterns
3. The tool checks each modified file against all patterns
4. Matching instructions are included in the diagram

### Example Instruction File

```markdown
---
applyTo:
  - ".github/workflows/**/*.yml"
  - ".github/workflows/*.yml"
---

# Workflow Instructions

These instructions apply to all workflow files...
```

## Benefits

### For Developers
- Understand what influenced the code generation
- Verify correct instructions were used
- Learn about the instruction system

### For Reviewers
- Quickly see the context
- Verify appropriate instructions were applied
- Check if agent specialization matches task

### For the System
- Provides audit trail
- Enables debugging of instruction issues
- Helps improve instruction organization

## Troubleshooting

### Missing Path Instructions

If expected path instructions don't appear:
1. Check the `applyTo` patterns in the instruction file
2. Verify the file path matches the pattern
3. Make sure the instruction file is not in the `archive/` directory

### Agent Not Detected

If the agent isn't shown:
1. Verify the agent file exists in `.github/agents/`
2. Check the agent name is correct (without @)
3. Ensure the agent file has proper frontmatter

### No Repository Instructions

If repository instructions don't appear:
1. Check that `.copilot-instructions.md` exists in the root
2. Check that `.github/copilot-instructions.md` exists
3. Verify file permissions allow reading

## Related Documentation

- [Path-Specific Instructions README](.github/instructions/README.md)
- [Agent System Documentation](.github/agents/README.md)
- [Repository Instructions](.github/copilot-instructions.md)

## Future Enhancements

Potential improvements to consider:

1. **Auto-detection**: Automatically detect agent and files from git context
2. **Validation**: Check that all required sources are present
3. **Metrics**: Track which instructions are most frequently used
4. **Visualization**: Web-based interactive visualization of instruction hierarchy
5. **Recommendation**: Suggest relevant instructions based on file changes

---

**Created**: 2025-12-01  
**Author**: @organize-guru (via Copilot)  
**Status**: Active
