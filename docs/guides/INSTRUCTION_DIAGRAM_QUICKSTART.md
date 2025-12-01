# Quick Reference: Instruction Source Diagram

## 🎯 Purpose
Show where Copilot sourced instructions from in every PR.

## ⚡ Quick Start

### Basic Usage
```bash
python3 tools/generate-instruction-diagram.py \
  --issue ISSUE_NUMBER \
  --agent AGENT_NAME \
  --files file1.py file2.py file3.py
```

### Example
```bash
python3 tools/generate-instruction-diagram.py \
  --issue 3502 \
  --agent engineer-master \
  --files .github/workflows/test.yml docs/index.html
```

### With Git Auto-Detection
```bash
# Auto-detect modified files
FILES=$(git diff --name-only origin/main)
python3 tools/generate-instruction-diagram.py \
  --issue 3502 \
  --files $FILES
```

## 📊 What Gets Shown

| Icon | Source Type | Example |
|------|-------------|---------|
| 📚 | Repository Instructions | `.copilot-instructions.md` |
| 🎯 | Issue/Prompt | Issue #3502 |
| 🤖 | Agent Profile | `@engineer-master` |
| 📍 | Path-Based Instructions | `branch-protection.instructions.md` |

## 🔧 Integration in Workflows

### Manual PR Creation
1. Make your changes
2. Generate diagram: `python3 tools/generate-instruction-diagram.py --issue NUM --files ...`
3. Copy output to PR description
4. Create PR

### Automated PR Creation
```bash
# See examples/create-pr-with-diagram.sh for complete script
DIAGRAM=$(python3 tools/generate-instruction-diagram.py --issue $ISSUE --files $FILES)
gh pr create --body "$DIAGRAM"
```

## 📖 Full Documentation

- [Complete Guide](./INSTRUCTION_SOURCE_DIAGRAM.md)
- [Repository Instructions](../../.github/copilot-instructions.md)
- [Path Instructions](../../.github/instructions/README.md)

## 💡 Tips

- **Agent Detection**: Extract from issue body: `gh issue view NUM --json body | grep -oP '@\K[a-z-]+'`
- **File Detection**: Use `git diff --name-only origin/main` for all changes
- **No Agent**: Omit `--agent` parameter if no agent assigned
- **Repo Root**: Add `--repo-root /path` if running outside repo

## ❓ Troubleshooting

**Missing path instructions?**
- Check `applyTo` patterns in `.github/instructions/*.instructions.md`
- Verify file paths match glob patterns

**Agent not shown?**
- Ensure agent name is correct (no @ prefix)
- Check agent file exists: `.github/agents/AGENT_NAME.md`

**No output?**
- Verify Python 3 is installed
- Check file paths are correct
- Run with absolute paths if needed

---

**Need help?** See [INSTRUCTION_SOURCE_DIAGRAM.md](./INSTRUCTION_SOURCE_DIAGRAM.md) for complete documentation.
