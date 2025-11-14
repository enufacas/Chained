# Path-Specific Custom Instructions for GitHub Copilot

This directory contains **path-specific custom instruction files** that provide targeted guidance for GitHub Copilot when working with specific areas of the codebase.

## What Are Path-Specific Instructions?

Path-specific instructions allow you to define rules, conventions, and guidelines that apply only to certain files or directories, using the `.instructions.md` file format with an `applyTo:` YAML header.

### Official Documentation
- [GitHub Docs: Adding repository custom instructions](https://docs.github.com/en/copilot/how-tos/configure-custom-instructions/add-repository-instructions)
- [GitHub Blog: Path-scoped custom instruction file support](https://github.blog/changelog/2025-09-03-copilot-code-review-path-scoped-custom-instruction-file-support/)
- [VS Code: Custom instructions](https://code.visualstudio.com/docs/copilot/customization/custom-instructions)

## How They Work

1. **Scoping**: Each `.instructions.md` file starts with a YAML `applyTo:` section that defines glob patterns
2. **Application**: When Copilot works on a matched file, both repository-wide AND path-specific instructions apply
3. **Precedence**: More specific instructions complement (not override) general instructions
4. **Tools**: Work with Copilot coding agent, Copilot Chat, and Copilot code review

## Instruction Files in This Directory

### 1. `agent-mentions.instructions.md`
**Applies to:** Workflows, scripts, and agent-related tooling
- Enforces @agent-name mention syntax everywhere
- Provides correct and incorrect usage examples
- Lists all available custom agents
- Explains why proper mentions are critical

**Scope:**
```yaml
applyTo:
  - "**/*.yml"
  - "**/*.yaml"
  - "**/assign-copilot-to-issue.sh"
  - "**/match-issue-to-agent.py"
  - ".github/workflows/**"
  - "tools/**"
```

### 2. `workflow-agent-assignment.instructions.md`
**Applies to:** Copilot and agent-related workflows
- Mandates @agent-name in issue body updates
- Requires @mentions in automated comments
- Specifies format for assignment messages
- Defines shell and Python script requirements

**Scope:**
```yaml
applyTo:
  - ".github/workflows/copilot-*.yml"
  - ".github/workflows/*-agent-*.yml"
  - ".github/workflows/agent-*.yml"
```

### 3. `issue-pr-agent-mentions.instructions.md`
**Applies to:** Issue and PR templates and related files
- Template formatting requirements for agent mentions
- Issue description agent reference format
- PR description agent attribution format
- Commit message agent reference patterns
- Multi-agent collaboration format

**Scope:**
```yaml
applyTo:
  - "**/*issue*.md"
  - "**/*pull_request*.md"
  - ".github/ISSUE_TEMPLATE/**"
  - ".github/PULL_REQUEST_TEMPLATE/**"
```

### 4. `branch-protection.instructions.md` 🆕
**Applies to:** All workflow files
- **CRITICAL**: Enforces PR-based workflow for all changes
- Prohibits direct pushes to main branch
- Provides patterns for creating PRs from workflows
- Migration guide for existing workflows
- Explains branch protection rationale

**Scope:**
```yaml
applyTo:
  - ".github/workflows/**/*.yml"
  - ".github/workflows/*.yml"
  - "**/*.yml"
  - "**/*.yaml"
```

### 5. `agent-issue-updates.instructions.md` 🆕
**Applies to:** All workflow files and agent-related code
- **CRITICAL**: Requires issue updates before removing WIP status
- Mandates progress comments on issues
- Provides templates for issue update comments
- Ensures transparency in agent work
- Defines timing and content requirements

**Scope:**
```yaml
applyTo:
  - ".github/workflows/**/*.yml"
  - ".github/workflows/*.yml"
  - ".github/workflows/copilot-*.yml"
  - ".github/workflows/*-agent-*.yml"
  - ".github/workflows/agent-*.yml"
  - "tools/**/*.py"
  - "tools/**/*.sh"
```

## File Format

Each instruction file follows this structure:

```markdown
---
applyTo:
  - "path/pattern/**"
  - "another/pattern/*.yml"
---

# Instructions Title

Your custom instructions here...
```

### Key Sections
1. **YAML Frontmatter**: `applyTo:` glob patterns
2. **Markdown Body**: Detailed instructions, rules, examples

## How to Add New Instructions

1. **Create file**: `NAME.instructions.md` in this directory
2. **Add scope**: Define `applyTo:` patterns in YAML frontmatter
3. **Write instructions**: Clear, specific guidance with examples
4. **Commit**: Changes take effect immediately for Copilot
5. **Test**: Verify Copilot follows instructions when working on matched files

## Benefits of Path-Specific Instructions

### ✅ Targeted Guidance
- Different rules for frontend vs backend
- Specific standards for testing vs production code
- Security requirements only where needed

### ✅ Better Copilot Suggestions
- More relevant code suggestions
- Context-aware recommendations
- Fewer off-topic suggestions

### ✅ Improved Code Review
- Copilot code review uses scoped instructions
- More focused feedback on PRs
- Better alignment with area-specific standards

### ✅ Modular Maintenance
- Edit one area's instructions without affecting others
- Team members can own their area's guidelines
- Easier to keep instructions current

## Current Focus: Agent Mention Enforcement

The instruction files in this directory primarily focus on **enforcing consistent @agent-name mentions** throughout the autonomous agent system. This is critical because:

1. **Performance Tracking**: Agent metrics depend on proper attribution
2. **Transparency**: Users must know which agent did what
3. **Accountability**: Work must be traceable to specific agents
4. **System Integrity**: The autonomous ecosystem relies on clear agent identification

### The Rule
**ALWAYS mention custom agents by name using @agent-name syntax in EVERY context where agents are discussed, assigned, or referenced.**

## Integration with Repository-Wide Instructions

These path-specific instructions work alongside:
- `.github/copilot-instructions.md` - Repository-wide rules
- `.github/agents/*.md` - Custom agent definitions
- Documentation in `docs/` directory

Together they create a **comprehensive instruction system** that guides Copilot to produce code that aligns with our autonomous agent ecosystem.

## Validation

To verify instructions are working:
1. Edit a file matching an `applyTo:` pattern
2. Ask Copilot Chat about the relevant rules
3. Request code suggestions and observe compliance
4. Review Copilot code review comments for rule awareness

## Troubleshooting

**Instructions not being followed?**
- Verify `applyTo:` patterns match your file paths
- Check YAML syntax is valid
- Ensure file is committed to default branch
- Test in different Copilot contexts (Chat, code review, coding agent)

**Conflicting instructions?**
- Path-specific instructions complement (not override) repository-wide instructions
- More specific patterns take precedence when conflicts exist
- Consider refining `applyTo:` patterns for better targeting

## Future Expansion

Consider adding instruction files for:
- **Security patterns**: `.github/instructions/security.instructions.md`
- **Testing standards**: `.github/instructions/testing.instructions.md`
- **Documentation style**: `.github/instructions/docs.instructions.md`
- **API design**: `.github/instructions/api-design.instructions.md`
- **Performance**: `.github/instructions/performance.instructions.md`

## References

- [Custom agents configuration](https://docs.github.com/en/copilot/reference/custom-agents-configuration)
- [Repository custom instructions](https://docs.github.com/en/copilot/how-tos/configure-custom-instructions/add-repository-instructions)
- [VS Code custom instructions](https://code.visualstudio.com/docs/copilot/customization/custom-instructions)
- [Copilot coding agent](https://docs.github.com/en/copilot/how-tos/use-copilot-agents/coding-agent)

---

*Part of the Chained autonomous AI ecosystem - ensuring consistent, transparent agent attribution.* 🤖
