# Context Size Optimization Guide

## Problem Statement

GitHub Copilot has context size limits (estimated ~40,000-50,000 tokens including code context). When custom instructions exceed these limits, API requests fail with HTTP 413 "Request Entity Too Large" errors.

**Previous state:**
- Total instruction size: 122KB
- Estimated token count: ~30,000 tokens
- Result: HTTP 413 errors, Copilot failures

**Current state:**
- Total instruction size: 50KB
- Estimated token count: ~12,500 tokens
- Result: ✅ Within limits, Copilot works

## Optimization Strategies

### 1. Move Detailed Content to Documentation

Instead of including comprehensive guides in `.instructions.md` files:
- Move detailed examples to `docs/guides/`
- Keep only essential quick references in `.github/instructions/`
- Link to full documentation from instruction files

**Example:**
```markdown
# Quick Reference (in .github/instructions/)
## MANDATORY: Test 3D rendering
- Test FPS (target: 60fps)
- Check draw calls (< 50)
- Take screenshots

**For detailed guidance**, see: [docs/guides/copilot-instructions/threejs-rendering-guide.md](...)
```

### 2. Remove Redundant Examples

Avoid repeating the same pattern multiple times:

❌ **Verbose:**
```markdown
### Example 1
```yaml
code example 1
```

### Example 2
```yaml
code example 2
```

### Example 3
```yaml
code example 3
```
```

✅ **Concise:**
```markdown
### Pattern
```yaml
one complete example
```
```

### 3. Consolidate Related Instructions

Instead of:
- `agent-mentions-workflows.instructions.md`
- `agent-mentions-scripts.instructions.md`
- `agent-mentions-templates.instructions.md`

Use:
- `agent-mentions.instructions.md` (covers all cases)

### 4. Focus on MUST/MUST NOT Rules

Instruction files should be prescriptive, not educational:

❌ **Verbose:**
```markdown
### Why This Matters
Agents are part of our autonomous system that tracks performance based on mentions. When we don't use mentions, the system can't attribute work correctly. This leads to problems with metrics collection and makes it hard to understand which agent did what work. Therefore, it's important to always use @mentions...
```

✅ **Concise:**
```markdown
### Why This Matters
- **Attribution**: Performance tracking requires @mentions
- **Metrics**: System depends on proper identification
```

### 5. Use Bullet Points Over Paragraphs

Transform narrative explanations into scannable lists:

❌ **Verbose:**
```markdown
When you create a PR, you should make sure to include the agent name in the title or body. This is important because it helps us track which agent did the work. You should also add a label to the PR so we can filter by agent later.
```

✅ **Concise:**
```markdown
**PR Requirements:**
- Include `@agent-name` in title or body
- Add `agent:agent-name` label
```

## Size Limits and Guidelines

### Target Sizes
- **Total instructions**: < 60KB (< 15,000 tokens)
- **Individual files**: < 3KB when possible
- **Critical files**: < 5KB maximum

### Checking Size
```bash
# Check total size
cd /home/runner/work/Chained/Chained
python3 << 'EOF'
import os
path = '.github/instructions'
total = sum(os.path.getsize(os.path.join(path, f)) 
            for f in os.listdir(path) if f.endswith('.md'))
print(f"Total: {total:,} bytes ({total/1024:.1f} KB)")
print(f"Estimated tokens: ~{total/4:.0f}")
if total > 60000:
    print("⚠️  WARNING: Over 60KB limit!")
else:
    print("✅ Within limits")
EOF
```

### Validation Checklist
Before adding new instructions:
- [ ] File is under 3KB
- [ ] Contains only essential MUST/MUST NOT rules
- [ ] Links to detailed docs for examples
- [ ] No repetitive or redundant content
- [ ] Total instructions stay under 60KB

## Migration Pattern

When condensing existing instructions:

1. **Extract detailed content**
   - Move to `docs/guides/copilot-instructions/`
   - Keep as comprehensive reference

2. **Create quick reference**
   - MANDATORY rules only
   - One complete example (not 5)
   - Link to detailed guide

3. **Test size**
   ```bash
   wc -c .github/instructions/*.instructions.md | tail -1
   ```

4. **Verify content**
   - All critical rules retained
   - No information loss (moved to docs)
   - Links are correct

## Monitoring

Add a CI check to prevent future bloat:

```yaml
# .github/workflows/validate-instructions-size.yml
name: Validate Instructions Size
on: [pull_request]
jobs:
  check-size:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Check instruction size
        run: |
          TOTAL=$(find .github/instructions -name "*.md" -exec cat {} \; | wc -c)
          echo "Total size: $TOTAL bytes"
          if [ $TOTAL -gt 60000 ]; then
            echo "❌ Instructions exceed 60KB limit!"
            exit 1
          fi
          echo "✅ Instructions within limits"
```

## Future Best Practices

### When Adding New Instructions
1. Start concise - can always expand in docs
2. Focus on what Copilot MUST do/avoid
3. Link to comprehensive docs
4. Check total size after adding

### When Updating Instructions
1. Look for consolidation opportunities
2. Remove outdated content
3. Move examples to docs if file growing
4. Verify total size hasn't grown

### Red Flags
- ⚠️ Same pattern shown 3+ times
- ⚠️ Long narrative paragraphs
- ⚠️ Detailed "why" explanations (link to docs instead)
- ⚠️ File over 5KB
- ⚠️ Total over 55KB

## Success Metrics

**Before optimization:**
- 122KB instructions
- HTTP 413 errors
- Copilot failures

**After optimization:**
- 50KB instructions
- No HTTP 413 errors
- Copilot works reliably

**Ongoing:**
- Monitor total size stays < 60KB
- Add validation to CI
- Keep instructions focused and concise
