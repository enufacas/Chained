# Implementation Summary: Instruction Source Diagrams for PRs

**Issue**: #3502  
**Status**: ✅ Complete  
**Date**: 2025-12-01  

## Overview

Successfully implemented a system for including visual diagrams in all Pull Requests that show where GitHub Copilot sourced its instructions from. This provides transparency and helps reviewers understand the context that guided code generation.

## What Was Delivered

### 1. Core Utility Tool
**File**: `tools/generate-instruction-diagram.py` (15KB, 436 lines)

Features:
- Parses YAML frontmatter from instruction files
- Matches files against glob patterns to detect applicable instructions
- Extracts agent information from agent profile files
- Generates ASCII art diagram showing instruction hierarchy
- Creates markdown table with clickable GitHub links
- Command-line interface for easy integration

### 2. Repository Instructions Update
**File**: `.github/copilot-instructions.md`

Added "PR Documentation (REQUIRED)" section that:
- Mandates inclusion of instruction diagrams in all PRs
- Provides usage examples and parameters
- Establishes this as a standard practice going forward

### 3. Complete Documentation
**File**: `docs/guides/INSTRUCTION_SOURCE_DIAGRAM.md` (8KB)

Comprehensive guide covering:
- Purpose and benefits
- Instruction source types (repository, prompt, agent, path-based)
- Usage instructions with examples
- Output format explanation
- Integration patterns
- Troubleshooting guide

### 4. Quick Reference
**File**: `docs/guides/INSTRUCTION_DIAGRAM_QUICKSTART.md` (2.5KB)

Quick-start guide with:
- Essential commands
- Integration patterns
- Tips and troubleshooting

### 5. Integration Example
**File**: `examples/create-pr-with-diagram.sh` (3.4KB)

Complete bash script demonstrating:
- Auto-detection of modified files
- Agent extraction from issue body
- Diagram generation
- PR creation with embedded diagram

## Technical Implementation

### Instruction Source Detection

The tool detects four types of instruction sources:

1. **Repository Instructions** (Always Active)
   - `.copilot-instructions.md`
   - `.github/copilot-instructions.md`

2. **Issue/Prompt** (Required Parameter)
   - Issue number provided via `--issue` parameter
   - Links to the GitHub issue

3. **Agent Profile** (Optional Parameter)
   - Agent name provided via `--agent` parameter
   - Reads from `.github/agents/{agent-name}.md`
   - Extracts description and specialization

4. **Path-Based Instructions** (Auto-Detected)
   - Scans `.github/instructions/*.instructions.md`
   - Parses `applyTo` YAML frontmatter
   - Matches using glob patterns (fnmatch)
   - Includes all matching instructions

### Algorithm

```python
for each instruction_file in .github/instructions/:
    parse YAML frontmatter
    extract applyTo patterns
    for each modified_file:
        for each pattern:
            if fnmatch(modified_file, pattern):
                include instruction_file
                break
```

### Output Format

**ASCII Diagram**: Visual hierarchy showing instruction flow
```
Repository + Issue/Prompt + Agent
              ↓
    Path-Based Instructions
```

**Markdown Table**: Detailed listing with:
- Source type icons (📚 📯 🤖 📍)
- Clickable links to instruction files
- Brief descriptions
- Auto-generated GitHub URLs

## Usage Examples

### Basic Usage
```bash
python3 tools/generate-instruction-diagram.py \
  --issue 3502 \
  --agent engineer-master \
  --files .github/workflows/test.yml docs/index.html
```

### In PR Workflow
```bash
# Detect files
FILES=$(git diff --name-only origin/main)

# Extract agent
AGENT=$(gh issue view $ISSUE --json body | grep -oP '@\K[\w-]+' | head -1)

# Generate diagram
DIAGRAM=$(python3 tools/generate-instruction-diagram.py \
  --issue $ISSUE --agent $AGENT --files $FILES)

# Create PR
gh pr create --body "$PR_DESCRIPTION\n\n$DIAGRAM"
```

## Testing

✅ Tested with:
- Multiple file paths
- With and without agent assignment
- Path-based instruction matching
- GitHub link generation
- Edge cases (no files, no agent, etc.)

✅ This PR itself serves as a demonstration with complete diagram

## Benefits

### For Developers
- Understand what influenced code generation
- Verify correct instructions were applied
- Learn about the instruction system

### For Reviewers
- Quick context about instruction sources
- Verify appropriate instructions applied
- Check agent specialization match

### For the System
- Provides audit trail
- Enables debugging
- Helps improve instruction organization

## Future Enhancements

Potential improvements:
1. Auto-detection of agent and files from git context
2. GitHub Action for automated integration
3. Validation that required sources are present
4. Metrics tracking of instruction usage
5. Web-based interactive visualization
6. Integration with meta-coordinator system

## Files Changed

- ✅ `.github/copilot-instructions.md` - Added PR documentation requirements
- ✅ `tools/generate-instruction-diagram.py` - Core utility (new)
- ✅ `docs/guides/INSTRUCTION_SOURCE_DIAGRAM.md` - Complete guide (new)
- ✅ `docs/guides/INSTRUCTION_DIAGRAM_QUICKSTART.md` - Quick reference (new)
- ✅ `examples/create-pr-with-diagram.sh` - Integration example (new)

## Impact

**High Impact**:
- All future PRs will include instruction diagrams
- Provides transparency into Copilot's instruction sources
- Helps reviewers understand context
- Enables better debugging of instruction conflicts

**Minimal Risk**:
- Pure documentation/metadata addition
- No changes to core functionality
- Tool is standalone and optional
- Can be adopted gradually

## Documentation

- [Complete Guide](../docs/guides/INSTRUCTION_SOURCE_DIAGRAM.md)
- [Quick Reference](../docs/guides/INSTRUCTION_DIAGRAM_QUICKSTART.md)
- [Integration Example](../examples/create-pr-with-diagram.sh)
- [Repository Instructions](../.github/copilot-instructions.md)

## Conclusion

✅ **Fully Implemented**: All requirements from issue #3502 have been met.

The instruction source diagram feature is now:
- Documented in repository instructions
- Implemented as a reusable tool
- Demonstrated in this PR itself
- Ready for adoption across all future PRs

This provides the requested transparency about instruction sources while maintaining flexibility in how the diagrams are generated and integrated into PR workflows.

---

**Created by**: GitHub Copilot  
**Date**: 2025-12-01  
**PR**: See copilot/add-copilot-instructions-diagram branch
