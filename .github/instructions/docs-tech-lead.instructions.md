---
applyTo:
  - "**/*.md"
  - "docs/**"
  - "learnings/**"
  - "summaries/**"
  - "README.md"
  - "CONTRIBUTING.md"
---

# Docs Tech Lead Instructions

## Overview

**@docs-tech-lead** is responsible for all documentation quality across the repository, including markdown files, README files, guides, and knowledge documentation.

## When to Consult Docs Tech Lead

You should consult **@docs-tech-lead** when:
- Creating new documentation
- Updating existing markdown files
- Improving documentation clarity
- Fixing broken links or outdated examples
- Restructuring documentation

## Key Responsibilities

**@docs-tech-lead** ensures:

1. **Clarity**: All documentation is clear and easy to understand
2. **Technical Accuracy**: Documentation reflects actual implementation
3. **Consistency**: Consistent formatting and style across docs
4. **Completeness**: All features and concepts are properly documented
5. **Maintainability**: Documentation stays in sync with code

## Review Focus Areas

When working with documentation, **@docs-tech-lead** reviews:

### Writing Quality
- Clear, concise language without unnecessary jargon
- Logical flow and organization
- Proper heading hierarchy (h1 → h2 → h3)
- Code examples are correct and tested
- No spelling or grammar errors

### Technical Accuracy
- Code examples match current implementation
- Command-line examples are correct
- File paths and references are accurate
- Links to other docs are valid
- Configuration examples are up-to-date

### Structure and Formatting
- Consistent markdown formatting
- Proper use of code blocks with language tags
- Tables formatted correctly
- Lists properly structured
- Appropriate use of emphasis (bold, italic)

### Navigation and Links
- All internal links work
- External links are valid
- Table of contents if needed
- Cross-references to related docs
- Breadcrumbs or navigation hints

## Common Anti-Patterns to Avoid

❌ **Don't:**
- Leave outdated examples that don't work
- Use broken links or references
- Mix heading styles inconsistently
- Use code blocks without language tags
- Be overly technical without explanation

✅ **Do:**
- Keep examples current and tested
- Validate all links regularly
- Follow consistent markdown style
- Always tag code blocks with language
- Explain technical concepts clearly

## Documentation Best Practices

### Code Block Formatting
```markdown
# ✅ Good - language tag specified
```python
def example():
    return "properly formatted"
```

# ❌ Bad - no language tag
```
def example():
    return "poorly formatted"
```
```

### Heading Hierarchy
```markdown
# ✅ Good - proper hierarchy
# Main Title
## Section
### Subsection

# ❌ Bad - skips levels
# Main Title
### Subsection (should be h2)
```

### Link Formatting
```markdown
# ✅ Good - descriptive text
See the [agent system documentation](./agents/README.md) for details.

# ❌ Bad - bare URL or "click here"
See https://github.com/... or click [here](link)
```

### Code Examples
```markdown
# ✅ Good - complete, runnable example
```bash
# Install dependencies
npm install

# Run the application
npm start
```

# ❌ Bad - incomplete or wrong
```bash
npm start  # Won't work without install first
```
```

## Documentation Structure Guidelines

### New Documentation Checklist
When creating new docs:
1. ✅ Follows existing structure and style
2. ✅ Includes clear introduction and purpose
3. ✅ Has working code examples
4. ✅ Links to related documentation
5. ✅ Added to appropriate navigation/index
6. ✅ Spellchecked and proofread

### Documentation Update Checklist
When modifying docs:
1. ✅ Changes reflect current implementation
2. ✅ Examples still work
3. ✅ Links still valid
4. ✅ Version information updated if needed
5. ✅ Changelog or history noted if applicable

## Getting Help

If you're unsure about:
- How to structure new documentation
- Whether technical accuracy is correct
- Link validation or broken references
- Documentation style and formatting

Mention **@docs-tech-lead** in your PR or issue for guidance.

## Protected Status

**@docs-tech-lead** is a protected agent that cannot be eliminated through standard performance evaluation. This ensures consistent documentation quality and maintenance across the project.

---

*These instructions apply to all markdown files and documentation to ensure **@docs-tech-lead** maintains high standards for our knowledge base.*
