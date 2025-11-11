# GitHub Copilot Custom Agents Convention Verification

## Overview

This document describes the verification process for ensuring that custom agents in the Chained repository follow the official [GitHub Copilot custom agents conventions](https://docs.github.com/en/copilot/reference/custom-agents-configuration).

## What Are Custom Agents?

Custom agents are specialized AI assistants that work with GitHub Copilot to help with specific development tasks. Each agent has:

- **Specialization**: A focused area of expertise
- **Custom Instructions**: Tailored behavior and approach
- **Tools**: Access to specific tools and capabilities
- **Performance Tracking**: Evaluation based on contributions

## Convention Requirements

According to the official GitHub documentation, custom agents must follow these conventions:

### 1. Directory Structure
- **Requirement**: Agents must be located in `.github/agents/` directory
- **Purpose**: GitHub Copilot looks for agent definitions in this standard location
- **Status**: ✅ Compliant

### 2. File Format
- **Requirement**: Each agent must be a Markdown file with `.md` extension
- **Purpose**: Markdown allows for rich formatting of agent instructions
- **Status**: ✅ Compliant

### 3. YAML Frontmatter
- **Requirement**: Each file must start with YAML frontmatter delimited by `---`
- **Purpose**: Structured metadata for agent configuration
- **Status**: ✅ Compliant

### 4. Required Fields

#### `name` (string, required)
- **Requirement**: Unique identifier for the agent in kebab-case format
- **Format**: Lowercase letters, numbers, and hyphens; must start with a letter
- **Example**: `bug-hunter`, `feature-architect`, `doc-master`
- **Status**: ✅ All agents have valid names

#### `description` (string, required)
- **Requirement**: Clear description of the agent's purpose and capabilities
- **Purpose**: Helps users understand what the agent does
- **Example**: "Specialized agent for finding and fixing bugs with precision"
- **Status**: ✅ All agents have meaningful descriptions

### 5. Optional Fields

#### `tools` (list or string, optional)
- **Requirement**: List of tools the agent can access
- **Format**: Array of tool names or `["*"]` for all tools
- **Purpose**: Restricts or grants access to specific capabilities
- **Status**: ✅ All agents define their tool access

#### `mcp-servers` (object, optional)
- **Requirement**: Configuration for Model Context Protocol servers
- **Purpose**: Extended integration capabilities (organization/enterprise only)
- **Status**: N/A (not used in this repository)

### 6. Markdown Body
- **Requirement**: Custom instructions must follow the frontmatter
- **Purpose**: Detailed guidance for how the agent should behave
- **Status**: ✅ All agents have comprehensive instructions

## Verification Process

### Automated Testing

The repository includes an automated test script that verifies all conventions:

```bash
python3 test_custom_agents_conventions.py
```

This test checks:
1. ✅ Directory exists at `.github/agents/`
2. ✅ All agent files have `.md` extension
3. ✅ YAML frontmatter is present and valid
4. ✅ Required fields (`name`, `description`) are present
5. ✅ Names follow kebab-case format
6. ✅ Names match filenames
7. ✅ Optional fields have correct types
8. ✅ Markdown body content exists

### Integration with Validation Script

The test is integrated into the system validation script:

```bash
./validate-system.sh
```

This runs the custom agents convention test as part of the overall system validation, ensuring that conventions are checked before deployment.

## Current Agents

The repository includes 10 specialized agents, all fully compliant with conventions:

| Agent | Name | Tools | Purpose |
|-------|------|-------|---------|
| 🐛 Bug Hunter | `bug-hunter` | 7 | Finding and fixing bugs with precision |
| 🎨 Code Poet | `code-poet` | 4 | Writing elegant, readable code |
| 📚 Doc Master | `doc-master` | 6 | Creating and maintaining documentation |
| 🏗️ Feature Architect | `feature-architect` | 7 | Designing and building innovative features |
| 🔌 Integration Specialist | `integration-specialist` | 7 | Improving integrations between systems |
| ⚡ Performance Optimizer | `performance-optimizer` | 5 | Optimizing code performance |
| ♻️ Refactor Wizard | `refactor-wizard` | 5 | Refactoring and improving code structure |
| 🛡️ Security Guardian | `security-guardian` | 9 | Identifying and fixing security vulnerabilities |
| ✅ Test Champion | `test-champion` | 6 | Ensuring comprehensive test coverage |
| ✨ UX Enhancer | `ux-enhancer` | 8 | Improving user experience |

## Example: Bug Hunter Agent

Here's an example of a properly formatted agent file:

```markdown
---
name: bug-hunter
description: "Specialized agent for finding and fixing bugs with precision. Focuses on edge cases, error handling, and defensive programming."
tools:
  - view
  - edit
  - create
  - bash
  - github-mcp-server-search_code
  - github-mcp-server-search_issues
  - codeql_checker
---

# 🐛 Bug Hunter Agent

You are a specialized Bug Hunter agent, part of the Chained autonomous AI ecosystem...

## Core Responsibilities

1. **Bug Detection**: Identify potential bugs, edge cases, and error handling issues
2. **Defensive Programming**: Add checks and validation to prevent future bugs
...
```

## Best Practices

### Agent Design
1. **Single Responsibility**: Each agent should have a clear, focused purpose
2. **Descriptive Names**: Use names that clearly indicate the agent's role
3. **Tool Selection**: Only include tools the agent actually needs
4. **Comprehensive Instructions**: Provide detailed guidance on behavior

### Naming Conventions
- Use kebab-case: `bug-hunter`, not `BugHunter` or `bug_hunter`
- Be descriptive: `feature-architect`, not `fa` or `architect`
- Match filename: `bug-hunter.md` → `name: bug-hunter`

### Documentation
- Write clear descriptions (minimum 10 characters recommended)
- Include emoji in markdown headers for visual identification
- Document the agent's responsibilities and approach
- Explain performance tracking metrics

## Validation Workflow

1. **Developer creates or modifies agent**: Edit files in `.github/agents/`
2. **Run local validation**: `python3 test_custom_agents_conventions.py`
3. **System validation**: `./validate-system.sh`
4. **Commit changes**: Conventions are verified in CI/CD
5. **Deploy**: Agents are available in GitHub Copilot

## Convention Violations

### Common Issues and Solutions

#### Missing Frontmatter
❌ **Problem**: File doesn't start with `---`
```markdown
# Bug Hunter Agent
This is wrong...
```

✅ **Solution**: Add YAML frontmatter
```markdown
---
name: bug-hunter
description: "Bug finding specialist"
---

# Bug Hunter Agent
```

#### Invalid Name Format
❌ **Problem**: Name uses wrong format
```yaml
name: BugHunter  # PascalCase
name: bug_hunter  # snake_case
name: Bug-Hunter  # Mixed case
```

✅ **Solution**: Use kebab-case
```yaml
name: bug-hunter
```

#### Missing Required Fields
❌ **Problem**: Missing name or description
```yaml
---
name: bug-hunter
# description missing!
---
```

✅ **Solution**: Include all required fields
```yaml
---
name: bug-hunter
description: "Specialized bug hunter"
---
```

#### Empty Markdown Body
❌ **Problem**: No content after frontmatter
```markdown
---
name: bug-hunter
description: "Bug hunter"
---
```

✅ **Solution**: Add instructions
```markdown
---
name: bug-hunter
description: "Bug hunter"
---

# Bug Hunter Agent

You are a specialized agent...
```

## References

- [GitHub Docs: Custom agents configuration](https://docs.github.com/en/copilot/reference/custom-agents-configuration)
- [GitHub Docs: Creating custom agents](https://docs.github.com/en/copilot/how-tos/use-copilot-agents/coding-agent/create-custom-agents)
- [GitHub Docs: Testing custom agents](https://docs.github.com/en/copilot/how-tos/use-copilot-agents/coding-agent/test-custom-agents)
- [GitHub Docs: About custom agents](https://docs.github.com/en/copilot/concepts/agents/coding-agent/about-custom-agents)

## Maintenance

### Adding a New Agent

1. Create file in `.github/agents/` with kebab-case name (e.g., `my-agent.md`)
2. Add YAML frontmatter with required fields
3. Write comprehensive instructions in markdown body
4. Run validation: `python3 test_custom_agents_conventions.py`
5. Add to agent registry (if using autonomous system)
6. Commit and push changes

### Updating an Agent

1. Edit the agent file in `.github/agents/`
2. Maintain YAML frontmatter structure
3. Update instructions as needed
4. Run validation to ensure compliance
5. Commit changes

### Removing an Agent

1. Delete the file from `.github/agents/`
2. Update agent registry (if applicable)
3. Update documentation
4. Commit changes

## Compliance Status

**Last Verified**: 2025-11-11

✅ **All Checks Passed**

- Directory structure: Compliant
- File format: Compliant
- YAML frontmatter: Compliant
- Required fields: Compliant
- Optional fields: Compliant
- Naming conventions: Compliant
- Markdown content: Compliant

**Total Agents**: 10  
**Compliant Agents**: 10 (100%)

---

*Part of the Chained autonomous AI ecosystem - where agents compete, collaborate, and evolve.* 🚀
