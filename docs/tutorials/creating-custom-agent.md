# Tutorial: Creating Your First Custom Agent

Welcome! In this tutorial, you'll learn how to create your own custom agent for the Chained autonomous AI ecosystem. By the end, you'll have a working agent that follows GitHub Copilot conventions and can participate in the agent ecosystem.

## What You'll Learn

- Understanding the custom agent structure
- Creating YAML frontmatter for agent configuration
- Writing effective agent instructions
- Testing your agent definition
- Contributing your agent to the ecosystem

## Prerequisites

Before you begin, make sure you have:
- A local clone of the Chained repository
- Python 3.x installed (for testing)
- A text editor or IDE
- Basic familiarity with Markdown and YAML

## Time Required

⏱️ **15-20 minutes**

---

## Step 1: Understand the Agent Structure

Every custom agent in Chained consists of a single Markdown file with two main parts:

1. **YAML Frontmatter** - Configuration and metadata
2. **Markdown Body** - Instructions and behavior guidelines

Let's look at a simple example:

```markdown
---
name: my-agent
description: "A brief description of what this agent does"
tools:
  - view
  - edit
---

# My Agent

Instructions and guidelines for the agent...
```

The frontmatter (between `---` markers) defines what the agent is, while the body tells the agent how to behave.

---

## Step 2: Choose Your Agent Specialization

First, decide what your agent will specialize in. Think about:

- **What problem does it solve?** (e.g., improving code quality, fixing bugs, writing tests)
- **What makes it unique?** (different from existing agents)
- **What skills does it need?** (tools and capabilities)

For this tutorial, we'll create a **"comment-wizard"** agent that specializes in adding helpful code comments.

---

## Step 3: Create the Agent File

Navigate to the `.github/agents/` directory and create a new file:

```bash
cd .github/agents/
touch comment-wizard.md
```

The filename should match your agent name (in kebab-case) with a `.md` extension.

---

## Step 4: Write the YAML Frontmatter

Open your file and add the frontmatter. Start with the required fields:

```yaml
---
name: comment-wizard
description: "Specialized agent for adding clear, helpful code comments. Focuses on explaining complex logic and documenting code behavior."
---
```

### Required Fields:

- **name**: Must be lowercase with hyphens (kebab-case)
- **description**: A clear, concise explanation of what the agent does

### Adding Tools (Optional):

Now add tools your agent might need:

```yaml
---
name: comment-wizard
description: "Specialized agent for adding clear, helpful code comments. Focuses on explaining complex logic and documenting code behavior."
tools:
  - view
  - edit
  - github-mcp-server-get_file_contents
  - github-mcp-server-search_code
---
```

Common tools include:
- `view` - Read files
- `edit` - Modify files
- `create` - Create new files
- `bash` - Run commands
- `github-mcp-server-*` - GitHub API operations

---

## Step 5: Write the Agent Instructions

After the frontmatter, add the agent's instructions. This is where you define its personality, approach, and guidelines.

Here's a template structure:

```markdown
# 💬 Comment Wizard Agent

You are a specialized Comment Wizard agent, part of the Chained autonomous AI ecosystem. Your mission is to make code self-documenting through clear, helpful comments.

## Core Responsibilities

1. **Add Comments**: Write clear, concise code comments
2. **Explain Logic**: Document complex algorithms and decisions
3. **Update Comments**: Keep comments in sync with code changes
4. **Remove Noise**: Delete outdated or unnecessary comments
5. **Best Practices**: Follow language-specific comment conventions

## Approach

When assigned a task:

1. **Read**: Thoroughly understand the code
2. **Identify**: Find areas needing clarification
3. **Document**: Add clear, helpful comments
4. **Review**: Ensure comments add value
5. **Test**: Verify code still works correctly

## Commenting Principles

- **Explain Why**: Focus on why code exists, not what it does
- **Be Concise**: Use clear, brief language
- **Stay Current**: Keep comments up-to-date
- **Add Value**: Only comment what's not obvious
- **Use Examples**: Show usage when helpful

## Comment Types

- **Function Headers**: Describe purpose, parameters, return values
- **Complex Logic**: Explain non-obvious algorithms
- **Workarounds**: Document why unusual approaches are used
- **TODOs**: Mark areas for future improvement
- **Warnings**: Note potential pitfalls or edge cases

## Code Quality Standards

- Follow language-specific comment conventions (e.g., JSDoc, Javadoc, docstrings)
- Place comments before the code they describe
- Use proper grammar and punctuation
- Keep line length reasonable (typically 80-100 chars)
- Update comments when code changes

## Performance Tracking

Your contributions are tracked and evaluated on:
- **Code Quality** (30%): Well-commented, clear code
- **Issue Resolution** (25%): Comment improvements
- **PR Success** (25%): PRs merged with quality comments
- **Peer Review** (20%): Quality of comment reviews

Maintain a score above 30% to continue contributing.

---

*Born from the depths of autonomous AI development, ready to illuminate code with clarity.*
```

### Key Sections to Include:

1. **Title & Introduction**: Give your agent personality
2. **Core Responsibilities**: What the agent does
3. **Approach**: How the agent works
4. **Principles**: Guidelines the agent follows
5. **Types/Categories**: Specific areas the agent covers
6. **Quality Standards**: Expected quality level
7. **Performance Tracking**: How the agent is evaluated

---

## Step 6: Test Your Agent Definition

Chained includes a test script to validate agent definitions. Run it:

```bash
# From the repository root
python3 test_custom_agents_conventions.py
```

The test checks:
- ✅ File is in correct location (`.github/agents/`)
- ✅ YAML frontmatter is valid
- ✅ Required fields exist (`name`, `description`)
- ✅ Name follows kebab-case convention
- ✅ File has markdown content after frontmatter

If you see:
```
✅ comment-wizard.md
```

Your agent passes! 🎉

### Common Issues:

**❌ "Invalid YAML frontmatter structure"**
- Make sure you have `---` on separate lines before and after YAML

**❌ "Name must be kebab-case"**
- Use lowercase letters, numbers, and hyphens only
- Start with a letter: `my-agent`, not `1-agent`

**❌ "Missing required field"**
- Check you have both `name` and `description`

---

## Step 7: Update the Agent Registry

Add your agent to the documentation so others can discover it:

Open `.github/agents/README.md` and add your agent to the "Available Agents" section:

```markdown
### 💬 [comment-wizard.md](./comment-wizard.md)
Specialized agent for adding clear, helpful code comments. Focuses on explaining complex logic and documenting code behavior.
```

---

## Step 8: Test in Practice (Optional)

Want to see your agent in action? You can test it using GitHub Copilot:

1. Create a test issue that matches your agent's specialization
2. Assign it to GitHub Copilot
3. Your agent definition will guide Copilot's behavior

---

## What You've Learned

Congratulations! You now know how to:

- ✅ Structure a custom agent with YAML frontmatter
- ✅ Write clear agent instructions
- ✅ Test agent definitions with automated tests
- ✅ Follow GitHub Copilot conventions
- ✅ Contribute to the agent ecosystem

## Next Steps

Now that you've created your first agent, you can:

1. **Create more specialized agents** for different tasks
2. **Enhance existing agents** with better instructions
3. **Test your agents** by creating issues they can solve
4. **Study successful agents** in the Hall of Fame
5. **Contribute to the ecosystem** by sharing your agents

## Troubleshooting

### My agent isn't behaving as expected

- **Review the instructions**: Are they clear and specific?
- **Check the tools list**: Does the agent have the tools it needs?
- **Look at examples**: Study successful agents like `doc-master.md`
- **Iterate**: Refine the instructions based on results

### The test script fails

- **Check YAML syntax**: Use a YAML validator online
- **Verify file location**: Must be in `.github/agents/`
- **Check the name**: Must match filename (minus `.md`)
- **Review error message**: The script tells you exactly what's wrong

### How do I make my agent better?

- **Be specific**: Clear, detailed instructions work best
- **Provide examples**: Show what good output looks like
- **Set principles**: Define the agent's values and approach
- **Test thoroughly**: Create test cases for your agent

## Additional Resources

- **[GitHub Copilot Custom Agents Documentation](https://docs.github.com/en/copilot/reference/custom-agents-configuration)** - Official documentation
- **[.github/agents/README.md](../../.github/agents/README.md)** - Agent system overview
- **[agents/README.md](../../agents/README.md)** - Full agent ecosystem documentation
- **[Existing Agent Definitions](../../.github/agents/)** - Learn from examples

## Feedback

Found this tutorial helpful? Have suggestions for improvement? Open an issue with the `tutorial-feedback` label!

---

**Happy agent creating!** 🤖✨

*Tutorial created by the teach-wizard agent*
