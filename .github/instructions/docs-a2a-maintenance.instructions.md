---
applyTo:
  - "docs/a2a/**"
  - "infrastructure/docker/adk-agents/error-observer/**"
  - "infrastructure/docker/adk-agents/log-consumer/**"
  - "infrastructure/docker/adk-agents/shared/error_event.py"
  - "docs/error_observer_*.md"
  - "docs/cloudrun_log_consumer.md"
---

# A2A Documentation Maintenance

## MANDATORY: Keep docs/a2a/README.md Up to Date

When making changes to A2A-related systems, **you MUST update the A2A README** to reflect the changes.

### What Requires README Updates

#### 1. New A2A Agents or Systems
When adding any new agent or system that uses the A2A protocol:
- [ ] Add to "Project Structure" section with path and description
- [ ] Add to appropriate phase in "Implementation Status"
- [ ] Add to "Reading Order" if documentation exists
- [ ] Include icon/emoji for visual organization

#### 2. Error Observer System Changes
The error observer is a **production A2A system** and key example. Update when:
- [ ] Changing error event schema
- [ ] Adding new error sources
- [ ] Modifying error flow
- [ ] Changing GitHub integration
- [ ] Adding/removing components

#### 3. New A2A Documentation
When creating new docs in `docs/a2a/`:
- [ ] Add to "Documentation Index" with 🆕 emoji for new items
- [ ] Add to "Reading Order" with context
- [ ] Update "Implementation Status" if it affects roadmap

#### 4. Architecture Changes
When modifying A2A architecture:
- [ ] Update "Architecture Overview" section
- [ ] Update diagrams if visual changes
- [ ] Update "Project Structure" paths
- [ ] Document breaking changes

#### 5. Workflow Changes
When adding/modifying workflows that use A2A:
- [ ] Add to "Project Structure" under `.github/workflows/`
- [ ] Update testing section if test workflows
- [ ] Document in README-A2A-TESTING.md

### Update Pattern

```markdown
# docs/a2a/README.md structure:

## Top Section
- Success announcement
- Quick start links

## Documentation Index
- Quick Start subsection
- Architecture & Design subsection
- Transport Layers subsection
- Implementation Status subsection

## Architecture Overview
- Three-tier architecture
- Use cases and characteristics

## Project Structure
- Complete file tree
- All A2A components
- **Always include error observer components**

## Implementation Status
- Phase completion tracking
- Current phase details
- Future phases

## A2A Error Observer System (NEW)
- Architecture diagram
- Components list
- Key features
- Documentation links
- Example flow
- **Keep this section current**

## Reading Order
- Numbered reading sequence
- Context for each document

## Use Cases (if applicable)
- Real-world examples

## External Resources
- Links to specifications
- Related projects

## Contributing
- Development guidelines
```

### Error Observer Documentation

The error observer system demonstrates A2A in production. Always keep these docs synchronized:

| Document | Content | Update When |
|----------|---------|-------------|
| `docs/a2a/README.md` | High-level overview, architecture | Any error observer change |
| `docs/error_observer_overview.md` | Complete system design | Architecture/component changes |
| `docs/error_observer_schema.md` | Error event schema | Schema changes |
| `docs/cloudrun_log_consumer.md` | Log processing | Log consumer changes |

### Cross-References

When documenting A2A features, always cross-reference:
- Link to related A2A docs in other documents
- Link back to main A2A README from specific docs
- Keep links up to date when moving files

### Icons and Visual Organization

Use consistent emoji/icons:
- 🎉 Success/milestones
- 🆕 New features
- 🚀 Primary implementations
- 🔍 Error observer
- 📝 Log consumer
- ✅ Completed phases
- 🔄 In progress
- 📋 Planned

### Validation Checklist

Before committing A2A-related changes:
- [ ] docs/a2a/README.md reflects changes
- [ ] Project structure section is accurate
- [ ] Implementation status is current
- [ ] Error observer section (if applicable) is updated
- [ ] Reading order includes new docs
- [ ] All links work
- [ ] Dates are current

### Why This Matters

The A2A README is the **entry point** for understanding the A2A system. It must accurately reflect:
- What's implemented
- What's in progress
- How components fit together
- Where to find detailed information

Outdated documentation leads to:
- ❌ Confusion about system capabilities
- ❌ Duplicate work
- ❌ Incorrect assumptions
- ❌ Wasted time searching for information

### Original Intent (PR #3520)

The error observer was implemented in PR #3520 as a demonstration of A2A's power:
- **First production A2A system** beyond examples
- **Treats errors as A2A tasks** - errors are first-class messages
- **End-to-end flow** - from agent error to GitHub issue
- **Observable** - UI shows real-time status
- **Autonomous triage** - Copilot can fix errors

This system proves A2A works for real-world use cases, not just demos.

---

**Remember**: The A2A README is a living document. Update it as you iterate!
