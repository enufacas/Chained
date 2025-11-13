# Agent Deletion, Respawn, and Discussion Features

## Overview

This document describes the new features added to the Chained agent system for managing agents and enabling collaborative discussions before task assignment.

## Features

### 1. Agent Deletion and Respawn

The `agent-spawner.yml` workflow now supports deleting agents before spawning new ones.

#### Workflow Inputs

- **delete_mode**: Choose how to delete agents
  - `none` (default): Don't delete any agents
  - `all`: Delete all active agents
  - `specific`: Delete specific agents by ID

- **delete_agent_ids**: When `delete_mode` is `specific`, provide comma-separated agent IDs
  - Example: `agent-1762824870,agent-1762832596`

- **respawn_count**: Number of agents to spawn after deletion (1-5, default: 1)
  - Note: Currently spawns one agent per workflow run. Run multiple times for multiple agents.

#### Usage Examples

**Delete all agents and respawn:**
1. Go to Actions → Agent Spawner → Run workflow
2. Set `delete_mode` to `all`
3. Set `respawn_count` to the desired number (workflow will need to run that many times)
4. Click "Run workflow"

**Delete specific agents:**
1. Go to Actions → Agent Spawner → Run workflow
2. Set `delete_mode` to `specific`
3. Set `delete_agent_ids` to the IDs you want to delete (e.g., `agent-123,agent-456`)
4. Click "Run workflow"

**Normal spawn (no deletion):**
1. Leave `delete_mode` as `none` (or don't set it)
2. Click "Run workflow"

### 2. Agent Issue Discussion

The new `agent-issue-discussion.yml` workflow enables agents to discuss issues before one takes ownership.

#### How It Works

1. **Trigger**: Add the `agent-discussion` label to an issue, or manually run the workflow
2. **Agent Selection**: 3-5 active agents are randomly selected to participate
3. **Discussion Rounds**: Agents post 2-5 comments based on their:
   - **Personality**: enthusiastic, methodical, calm, bold, friendly, etc.
   - **Specialization**: bug-hunter, code-poet, performance-optimizer, etc.
   - **Communication Style**: technical, analogies, concise, encouraging, etc.
4. **Assignment**: After discussion, one agent is selected to take the issue
5. **Copilot Assignment**: The issue is then ready for Copilot implementation

#### Trigger Methods

**Method 1: Label an issue**
```bash
gh issue edit <issue-number> --add-label "agent-discussion"
```

**Method 2: Manual workflow dispatch**
1. Go to Actions → Agent Issue Discussion → Run workflow
2. Set `issue_number` to the issue you want discussed
3. Set `discussion_rounds` (2-5, default: 3)
4. Click "Run workflow"

#### Example Discussion Flow

```
Issue: #123 "Optimize database queries"

🎉 Oh, this looks interesting! I think we need to consider performance implications...
   - ⚡ Theta (performance-optimizer)

Let me analyze this carefully. We should focus on edge cases and error handling...
   - 🐛 Beta (bug-hunter)

💡 I have a bold idea! This is an opportunity for beautiful, maintainable code...
   - 🎨 Alpha (code-poet)

🎯 Discussion concluded!
After careful consideration, ⚡ Theta (performance-optimizer) will take ownership...
```

#### Personality Types

Agents can have different personalities that affect their communication:

- **Enthusiastic and energetic**: Uses exclamation marks, emojis, shows excitement
- **Methodical and precise**: Analytical, structured, careful
- **Calm and thoughtful**: Reflective, measured, considerate
- **Bold and innovative**: Creative, pushes boundaries, thinks big
- **Friendly and collaborative**: Team-oriented, encouraging, supportive

#### Specialization Perspectives

Each agent brings their domain expertise:

- **bug-hunter**: Focuses on edge cases, testing, error handling
- **code-poet**: Emphasizes readability, elegance, maintainability
- **performance-optimizer**: Considers efficiency, speed, resource usage
- **doc-master**: Ensures documentation, clarity, knowledge sharing
- **test-champion**: Prioritizes test coverage, quality assurance
- **security-guardian**: Analyzes security implications, vulnerabilities
- **feature-architect**: Designs for scalability, architecture
- **refactor-wizard**: Improves structure, reduces duplication
- **ux-enhancer**: Focuses on user experience, usability
- **validate-wizard**: Ensures validation, data integrity
- **coordinate-wizard**: Handles integration, system coordination
- **teach-wizard**: Makes solutions educational, clear

## Fixed Issues

### Missing Human Names

All agents now have proper `human_name`, `personality`, and `communication_style` fields in the registry. These fields are essential for:
- Identifying agents by name (not just ID)
- Enabling personality-driven discussions
- Creating unique agent identities

The fix was automatically applied to all 7 existing agents in the registry.

## Technical Implementation

### Registry Schema Updates

Each agent now includes:

```json
{
  "id": "agent-1762824870",
  "name": "🔗 Omega-1111",
  "human_name": "Omega",
  "specialization": "coordinate-wizard",
  "personality": "methodical and precise",
  "communication_style": "clear and professional",
  "status": "active",
  ...
}
```

### Deletion Process

When agents are deleted:
1. Status changed to `deleted`
2. `deleted_at` timestamp added
3. `deletion_reason` recorded
4. Profile moved to `.github/agent-system/archive/`
5. Removed from active agents list
6. Agent definition kept for future spawns

### Discussion Algorithm

1. **Agent Selection**: Random sampling of 3-5 active agents
2. **Comment Generation**: 
   - Template selection based on personality
   - Opinion formulation based on specialization
   - Detail generation with domain expertise
3. **Assignment Logic**: Random selection from discussants (can be enhanced)
4. **Rate Limiting**: 2-second delay between comments for natural flow

## Best Practices

### When to Use Deletion

- **Delete All**: When restarting the ecosystem or testing
- **Delete Specific**: When removing underperforming or problematic agents
- **Normal Spawn**: Regular operation (evaluator handles elimination)

### When to Use Discussion

- **Complex Issues**: Issues that benefit from multiple perspectives
- **High-Impact Changes**: Features or refactors affecting multiple areas
- **Team Building**: Demonstrating agent collaboration
- **Educational**: Showing different approaches to problems

### Tips

1. **Let the evaluator work**: The daily evaluator already eliminates low performers
2. **Use discussion for special cases**: Not every issue needs discussion
3. **Monitor agent count**: Need at least 2 agents for discussion to work
4. **Review discussions**: Check if agent comments are valuable and coherent

## Future Enhancements

Potential improvements:

1. **Smart assignment**: Use issue content to select best-fit agent
2. **Voting system**: Agents vote on who should take the issue
3. **Discussion quality**: AI-powered comment quality checks
4. **Thread continuity**: Agents respond to each other's comments
5. **Multi-agent collaboration**: Multiple agents work on same issue
6. **Discussion summaries**: AI-generated summary of key points

## Troubleshooting

### Not Enough Agents for Discussion

**Problem**: "Not enough active agents for discussion"

**Solution**: Spawn more agents using the agent-spawner workflow

### Agent Discussion Not Triggering

**Problem**: Adding label doesn't trigger workflow

**Solution**: 
1. Check if `agent-discussion` label exists
2. Verify workflow file is in main branch
3. Manually trigger workflow instead

### Deletion Not Working

**Problem**: Agents not being deleted

**Solution**:
1. Verify `delete_mode` is set correctly
2. Check agent IDs are correct (find in registry.json)
3. Review workflow logs for errors

## Testing

Run tests to verify features:

```bash
# Test new features
python3 test_agent_deletion_discussion.py

# Test overall agent system
python3 test_agent_system.py
```

Both test suites should pass with ✅ status.
