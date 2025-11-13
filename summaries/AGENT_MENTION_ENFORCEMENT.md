# Agent Mention Enforcement System

## Overview

This document describes the comprehensive enforcement system implemented to ensure custom agents are **always mentioned by name** using `@agent-name` syntax throughout the Chained autonomous AI ecosystem.

## Problem Statement

The repository needed to ensure that when a custom agent is mentioned in an issue, that agent is always referenced by name in the conversation that the Copilot workflow creates. This is critical for:
- Proper attribution of work to specific agents
- Performance tracking and metrics
- Transparency in the autonomous agent system
- Clear accountability for agent contributions

## Solution: Multi-Layer Enforcement

We implemented a **four-layer enforcement system** based on GitHub's official documentation for custom instructions:

### Layer 1: Repository-Wide Instructions

**File**: `.github/copilot-instructions.md`

**Changes**:
- Added "Agent Mention Rule ⚠️ CRITICAL REQUIREMENT" section
- Upgraded enforcement language from "REQUIRED" to "CRITICAL"
- Provided comprehensive examples (correct vs incorrect)
- Explained multiple enforcement mechanisms
- Added references to path-specific instruction files

**Key Requirements**:
```markdown
MANDATORY: When a custom agent is assigned to an issue, you MUST mention 
that agent by name using @agent-name syntax in EVERY conversation, comment, 
PR, and interaction related to that issue.
```

### Layer 2: Path-Specific Instructions

**Directory**: `.github/instructions/`

Created three specialized instruction files that apply to specific file patterns:

#### 2.1 Agent Mentions Instructions
**File**: `agent-mentions.instructions.md`

**Applies to**:
- `**/*.yml`, `**/*.yaml` - All YAML files
- `**/assign-copilot-to-issue.sh` - Assignment script
- `**/match-issue-to-agent.py` - Matching script
- `.github/workflows/**` - All workflows
- `tools/**` - All tooling

**Enforces**:
- Always use `@agent-name` syntax
- Lists all 13 custom agents with correct format
- Provides correct/incorrect examples
- Explains non-compliance consequences

#### 2.2 Workflow Agent Assignment Instructions
**File**: `workflow-agent-assignment.instructions.md`

**Applies to**:
- `.github/workflows/copilot-*.yml`
- `.github/workflows/*-agent-*.yml`
- `.github/workflows/agent-*.yml`

**Enforces**:
- Issue body updates must include @agent-name
- Comments must use @agent-name
- Assignment messages must specify @agent-name
- Step-by-step instructions must prefix with @agent-name
- Shell/Python script requirements for @mentions

#### 2.3 Issue/PR Agent Mentions Instructions
**File**: `issue-pr-agent-mentions.instructions.md`

**Applies to**:
- `**/*issue*.md`
- `**/*pull_request*.md`
- `.github/ISSUE_TEMPLATE/**`
- `.github/PULL_REQUEST_TEMPLATE/**`

**Enforces**:
- Issue description agent reference format
- PR description agent attribution format
- Comment formatting with @mentions
- Commit message patterns
- Multi-agent collaboration format
- Template variable patterns

### Layer 3: Workflow Automation

**File**: `tools/assign-copilot-to-issue.sh`

**Enhancements**:
1. Issue body directive now includes:
   - `@$matched_agent` in the main directive
   - "IMPORTANT: Always mention **@$matched_agent** by name" reminder

2. Assignment comments now include:
   - `**@$matched_agent**` in bullet lists
   - Direct address to `**@$matched_agent**`
   - "IMPORTANT" reminder about @mentions

3. "What happens next" section:
   - Each step prefixed with `**@$matched_agent**`
   - Added "Assigned agent: @$matched_agent" field

4. Both assignment methods (direct and fallback):
   - Show agent name as `**@agent-name**`
   - Include reminder about @mentions

### Layer 4: Documentation

**File**: `.github/instructions/README.md`

Complete documentation of the instruction file system:
- Explains path-specific instructions
- Documents each instruction file
- Provides usage guidelines
- Links to official GitHub documentation
- Troubleshooting guide
- Future expansion suggestions

## How It Works Together

```
┌─────────────────────────────────────────────┐
│  1. Repository-Wide Instructions            │
│     (.github/copilot-instructions.md)       │
│     → Sets global agent mention rules       │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│  2. Path-Specific Instructions              │
│     (.github/instructions/*.instructions.md)│
│     → Applies targeted rules to file types  │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│  3. Workflow Automation                     │
│     (tools/assign-copilot-to-issue.sh)      │
│     → Generates proper @mentions            │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│  4. GitHub Copilot                          │
│     → Reads all instructions                │
│     → Suggests proper @mentions             │
│     → Flags missing @mentions in review     │
└─────────────────────────────────────────────┘
```

## Example: Complete Flow

### 1. Issue Created
User creates issue: "Fix the authentication bug"

### 2. Agent Matching
Workflow runs `match-issue-to-agent.py` → matches to `@secure-specialist`

### 3. Issue Body Updated
```markdown
> **🤖 Agent Assignment**
> 
> This issue has been assigned to GitHub Copilot with the 🛡️ secure-specialist custom agent profile.
> 
> **@secure-specialist** - Please use the specialized approach and tools defined in `.github/agents/secure-specialist.md`.
> 
> **IMPORTANT**: Always mention **@secure-specialist** by name in all conversations, comments, and PRs related to this issue.
```

### 4. Assignment Comment Posted
```markdown
🤖 **Copilot Assigned Successfully**

GitHub Copilot has been automatically assigned to this issue via the official GitHub GraphQL API.

## 🧠 Intelligent Agent Matching

This issue has been analyzed and matched to the **🛡️ @secure-specialist** specialization:

- **Agent**: @secure-specialist
- **Match Confidence**: high
- **IMPORTANT**: Always mention **@secure-specialist** by name in all conversations related to this issue.

**What happens next:**
1. ✅ **@secure-specialist** will analyze the issue requirements
2. 💻 **@secure-specialist** will create a branch and implement the solution
3. 📝 **@secure-specialist** will open a PR with the implementation

**Assigned agent:** @secure-specialist (security implementation)
```

### 5. Copilot Reads Instructions
When Copilot starts work:
- Reads `.github/copilot-instructions.md` → knows to use @agent-name
- Reads `.github/instructions/workflow-agent-assignment.instructions.md` → workflow-specific rules
- Reads `.github/instructions/issue-pr-agent-mentions.instructions.md` → issue/PR rules
- Sees @secure-specialist mentioned multiple times in issue
- **Identifies @secure-specialist as the required working identity**

### 6. Copilot Executes in Runner with Agent Identity
**This is the critical step where Copilot must use the agent mentioned in the issue:**

When Copilot executes as the coding agent in the GitHub Actions runner:

1. **Reads Issue Body**: Parses for `<!-- COPILOT_AGENT:secure-specialist -->` and `**@secure-specialist**` mentions
2. **Adopts Agent Identity**: Works as @secure-specialist, not as generic Copilot
3. **Follows Agent Specialization**: Reads `.github/agents/secure-specialist.md` for approach
4. **Uses Agent Name Throughout**: All outputs reference @secure-specialist

### 7. Copilot Works on Issue with Proper Attribution
Every comment, PR, commit references `@secure-specialist`:
- PR title: "Fix authentication bug (@secure-specialist)"
- PR body: "**@secure-specialist** has fixed the vulnerability..."
- Commits: "feat: add auth validation as specified by @secure-specialist"
- Comments: "@secure-specialist implemented additional security checks"

## Benefits

### ✅ Automatic Enforcement
GitHub Copilot automatically:
- Suggests proper @mentions when editing
- Flags missing @mentions in code review
- Uses @mentions in generated content
- Maintains consistency across all files
- **Reads issue body to identify assigned agent when executing in runner**
- **Adopts agent identity and uses it throughout all work**

### ✅ Context-Aware
Different rules apply to different contexts:
- Workflows get workflow-specific instructions
- Issues/PRs get template-specific instructions
- Scripts get code-specific instructions
- Everything gets repository-wide instructions
- **Runner execution gets special agent identity instructions**

### ✅ Attribution System
The agent mention system enables:
- **Performance tracking**: Agent metrics based on @mention attribution
- **Transparent accountability**: Clear identification of who did what
- **Evolution tracking**: Agent performance over time
- **Quality scoring**: Work evaluated per agent specialization
- **Runner identity**: Copilot knows which agent persona to adopt when executing

### ✅ Modular & Maintainable
- Easy to update individual instruction files
- Clear separation of concerns
- Well-documented system
- Extensible for future needs

### ✅ Standards-Based
Uses GitHub's official instruction file format:
- `.github/copilot-instructions.md` for repository-wide rules
- `.github/instructions/*.instructions.md` for path-specific rules
- YAML `applyTo:` frontmatter for targeting
- Markdown body for detailed instructions

## Verification

To verify the system is working:

### 1. Check Instruction Files
```bash
ls -la .github/instructions/
# Should show:
# - README.md
# - agent-mentions.instructions.md
# - workflow-agent-assignment.instructions.md
# - issue-pr-agent-mentions.instructions.md
```

### 2. Edit a Workflow File
Open `.github/workflows/copilot-graphql-assign.yml` and add a comment mentioning an agent. Copilot should suggest using `@agent-name` format.

### 3. Test Issue Assignment
Create a test issue and observe:
- Issue body contains `@agent-name`
- Assignment comment uses `@agent-name`
- All action items reference `@agent-name`
- Reminder about @mentions is present

### 4. Check Code Review
Submit a PR that mentions an agent without @. Copilot code review should flag it.

### 5. Verify Runner Execution (Critical)
When Copilot executes in the GitHub Actions runner:
- Check that PR title includes `(@agent-name)`
- Verify PR description starts with `**@agent-name** has...`
- Confirm commits reference `@agent-name` where relevant
- Validate all comments use proper `@agent-name` attribution

## Critical: Runner Execution Context

### Why This Matters Most

The most important enforcement point is **when Copilot executes as the coding agent in the GitHub Actions runner**. This is where the agent identity must be properly applied.

### How It Works

1. **Issue contains agent assignment**: `**@engineer-master** - Please use...`
2. **Copilot runner starts**: Reads issue body and extracts agent name
3. **Copilot adopts identity**: Works as @engineer-master, not generic Copilot
4. **All outputs use agent name**: PRs, commits, comments all reference @engineer-master

### What Copilot Must Do in Runner

**MANDATORY BEHAVIOR:**
- Read issue body FIRST to identify assigned agent
- Extract agent name from `@agent-name` mentions
- Use agent name in PR title: `feat: description (@agent-name)`
- Use agent name in PR body: `**@agent-name** has implemented...`
- Use agent name in commits: `fix: change per @agent-name`
- Use agent name in comments: `@agent-name completed milestone`

**FORBIDDEN BEHAVIOR:**
- ❌ Ignore the agent assignment
- ❌ Use "I" or "Copilot" without the agent name
- ❌ Create PRs without agent attribution
- ❌ Work generically when agent is assigned

### Example: Correct Runner Execution

```
Issue Body:
> **@secure-specialist** - Please fix the authentication vulnerability.
> IMPORTANT: Always mention **@secure-specialist** by name.

Copilot in Runner:
1. Reads issue, extracts: @secure-specialist
2. Reads .github/agents/secure-specialist.md
3. Adopts secure-specialist identity and approach

PR Created:
Title: fix: add authentication validation (@secure-specialist)

Description:
**@secure-specialist** has fixed the authentication vulnerability.

Following the @secure-specialist security-focused approach:
- Analyzed vulnerability thoroughly
- Implemented input validation  
- Added security tests
- Reviewed for additional attack vectors

@secure-specialist has ensured the fix follows security best practices.

Commits:
- fix: add input validation per @secure-specialist
- test: add security tests per @secure-specialist approach
- docs: document security fix by @secure-specialist
```

### Example: Incorrect Runner Execution (DON'T DO THIS)

```
Issue Body:
> **@secure-specialist** - Please fix the authentication vulnerability.

❌ WRONG - Copilot creates:
Title: fix: add authentication validation

Description:
I have fixed the authentication vulnerability by adding input validation.

Commits:
- fix: add input validation
- test: add tests
```

**This is wrong because:**
- No @secure-specialist mention in title
- No @secure-specialist in description
- No attribution to the assigned agent
- Breaks performance tracking
- Loses agent identity

## Verification

The system tracks 13 custom agents:

1. @accelerate-master - Performance optimization
2. @assert-specialist - Testing & quality assurance
3. @coach-master - Code reviews & best practices
4. @create-guru - Infrastructure & feature creation
5. @engineer-master - API engineering (systematic)
6. @engineer-wizard - API engineering (creative)
7. @investigate-champion - Code analysis & metrics
8. @meta-coordinator - Multi-agent coordination
9. @monitor-champion - Security monitoring
10. @organize-guru - Code structure & duplication
11. @secure-specialist - Security implementation
12. @support-master - Documentation & skill building
13. @troubleshoot-expert - CI/CD & GitHub Actions (protected)

## References

### GitHub Official Documentation
- [Custom agents configuration](https://docs.github.com/en/copilot/reference/custom-agents-configuration)
- [Repository custom instructions](https://docs.github.com/en/copilot/how-tos/configure-custom-instructions/add-repository-instructions)
- [Path-scoped instruction support](https://github.blog/changelog/2025-09-03-copilot-code-review-path-scoped-custom-instruction-file-support/)
- [VS Code custom instructions](https://code.visualstudio.com/docs/copilot/customization/custom-instructions)

### Repository Documentation
- [Custom Agents README](.github/agents/README.md)
- [Copilot Instructions](.github/copilot-instructions.md)
- [Instructions Directory](.github/instructions/README.md)
- [Custom Agent Assignment Limitations](docs/CUSTOM_AGENT_ASSIGNMENT_LIMITATIONS.md)

## Future Enhancements

Potential additions to the instruction system:

1. **Security-specific instructions**: `.github/instructions/security.instructions.md`
2. **Testing standards**: `.github/instructions/testing.instructions.md`
3. **Documentation style**: `.github/instructions/docs.instructions.md`
4. **API design rules**: `.github/instructions/api-design.instructions.md`
5. **Performance guidelines**: `.github/instructions/performance.instructions.md`

## Maintenance

### Updating Instructions
1. Edit the relevant `.instructions.md` file
2. Test changes with Copilot
3. Commit to default branch
4. Changes take effect immediately

### Adding New Agents
1. Create agent file in `.github/agents/`
2. Add agent to list in `agent-mentions.instructions.md`
3. Update `copilot-instructions.md` agent selection guidelines
4. Document in `AGENT_QUICKSTART.md`

### Monitoring Compliance
- Review issue assignment comments for proper @mentions
- Check PRs for agent attribution
- Monitor agent performance metrics
- Analyze commit messages for @agent-name usage

## Conclusion

This multi-layer enforcement system ensures that custom agents are **always mentioned by name** using proper `@agent-name` syntax. This maintains the integrity of the autonomous agent ecosystem, enables proper performance tracking, and provides transparent attribution for all agent contributions.

The system leverages GitHub's official custom instruction mechanisms to provide automatic, context-aware enforcement that guides Copilot to generate properly formatted agent mentions across all interactions.

---

**Implementation Date**: 2025-11-13
**Status**: ✅ Active
**Maintained By**: Autonomous Agent System

*Part of the Chained autonomous AI ecosystem - ensuring transparent, traceable agent contributions.* 🤖
