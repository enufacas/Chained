# Path-Specific Custom Instructions for GitHub Copilot

This directory contains **condensed, focused instruction files** that provide targeted guidance for GitHub Copilot when working with specific areas of the codebase.

> **⚠️ Size Optimization**: These instructions have been optimized to stay under GitHub Copilot's context limits. Detailed guides are available in `docs/guides/copilot-instructions/`.

## Context Size Management

**Current Status:**
- Total instruction size: ~55KB (down from 120KB)
- Estimated token count: ~14,000 tokens
- Status: ✅ Within limits

**Why This Matters:**
GitHub Copilot has context size limits. Exceeding them causes HTTP 413 errors and workflow failures. These instructions are kept concise while linking to detailed guides for comprehensive information.

## Instruction Files Overview

### Core Agent System Instructions
1. **`agent-mentions.instructions.md`** - Agent @mention syntax rules
2. **`agent-definition-sync.instructions.md`** - Sync agent definitions with patterns
3. **`agent-issue-updates.instructions.md`** - Issue update requirements
4. **`issue-pr-agent-mentions.instructions.md`** - Template formatting

### Workflow Instructions
5. **`branch-protection.instructions.md`** - PR-based workflow requirements
6. **`workflow-reference.instructions.md`** - Workflow attribution
7. **`workflow-agent-assignment.instructions.md`** - Agent assignment patterns

### Tech Lead Instructions
8. **`workflows-tech-lead.instructions.md`** - Workflow reviews
9. **`agents-tech-lead.instructions.md`** - Agent system reviews
10. **`docs-tech-lead.instructions.md`** - Documentation reviews
11. **`github-pages-tech-lead.instructions.md`** - Web content reviews

### Domain-Specific Instructions
12. **`threejs-rendering.instructions.md`** - 3D rendering quick reference
13. **`github-pages-testing.instructions.md`** - Pages testing quick reference

## Detailed Guides

For comprehensive information, see:
- `docs/guides/copilot-instructions/threejs-rendering-guide.md`
- `docs/guides/copilot-instructions/github-pages-testing-guide.md`

## Adding New Instructions

### Size Guidelines
- Keep individual files under 3KB when possible
- Focus on MUST/MUST NOT rules
- Link to detailed docs for examples
- Avoid repetitive examples

### Testing Size
```bash
# Check total size
find .github/instructions -name "*.md" -exec du -ch {} + | tail -1

# Estimate token count (rough: bytes / 4)
python3 << 'EOF'
import os
total = sum(os.path.getsize(os.path.join('.github/instructions', f)) 
            for f in os.listdir('.github/instructions') if f.endswith('.md'))
print(f"Total: {total:,} bytes (~{total/4:.0f} tokens)")
EOF
```

### Validation
Before committing new instructions:
- [ ] Total size stays under 60KB
- [ ] Individual files are focused and concise
- [ ] Links provided for detailed information
- [ ] No repetitive examples or verbose explanations

## Official Documentation
- [GitHub Docs: Adding repository custom instructions](https://docs.github.com/en/copilot/how-tos/configure-custom-instructions/add-repository-instructions)
- [GitHub Blog: Path-scoped custom instruction file support](https://github.blog/changelog/2025-09-03-copilot-code-review-path-scoped-custom-instruction-file-support/)
