# Agent System v2.0.0 - Dynamic Evolution Update

## Summary

This update transforms the agent spawner and evaluator workflows from using hardcoded agent lists to a fully dynamic, convention-compliant system that can evolve and create new agent types on-the-fly.

## Problem Addressed

The original agent-spawner and agent-evaluator workflows were created before the correct GitHub Copilot custom agents convention was known. They:
- Had hardcoded agent specializations in workflow files
- Didn't reference the convention-compliant agent definitions in `.github/agents/`
- Couldn't adapt or evolve with new agent types

## Solution Implemented

### 1. Convention Compliance

**Before:**
```yaml
# Hardcoded in workflow
SPECS=("bug-hunter" "feature-architect" "test-champion" ...)
```

**After:**
```yaml
# Dynamic from .github/agents/
SPECS=($(python3 tools/get-agent-info.py list))
```

All agent information is now read from the convention-compliant definitions in `.github/agents/`, including:
- Agent names and specializations
- Emojis
- Descriptions and missions
- Tools and capabilities

### 2. Dynamic Agent Creation (NEW)

**Key Features:**
- **8 Agent Archetypes**: analyzer, builder, optimizer, guardian, cleaner, communicator, connector, validator
- **Random Generation**: System can create entirely new agent types that didn't exist before
- **Convention-Compliant**: All new agents created with proper YAML frontmatter
- **Three Spawning Modes**:
  - `mixed` (default): 50% chance of new agent, 50% chance of existing
  - `existing`: Only spawn from existing agent definitions
  - `new`: Always create new random agents

**Example New Agent:**
```markdown
---
name: analyze-specialist
description: "Specialized agent for analyzing code patterns. Focuses on analysis, investigation, and metrics."
tools:
  - view
  - bash
  - github-mcp-server-search_code
---

# 🔍 Analyze Specialist Agent

You are a specialized Analyze Specialist agent...
```

### 3. Registry v2.0.0

**Updated Schema:**
```json
{
  "version": "2.0.0",
  "agents": [...],
  "config": {
    "spawn_mode": "mixed",
    "new_agent_probability": 0.5,
    ...
  },
  "specializations_note": "Specializations are dynamically loaded from .github/agents/"
}
```

Changes:
- Removed hardcoded `specializations` array
- Added `spawn_mode` and `new_agent_probability` config
- Dynamic loading from `.github/agents/` directory

## Files Changed

### New Files
1. **`tools/get-agent-info.py`** - Extract information from convention-compliant agent definitions
2. **`tools/generate-new-agent.py`** - Generate new random agents following the convention

### Modified Files
1. **`.github/workflows/agent-spawner.yml`**
   - Dynamic agent loading from `.github/agents/`
   - Support for creating new random agents
   - Three spawning modes
   - Updated PR and issue templates with agent definition links

2. **`.github/workflows/agent-evaluator.yml`**
   - Works with any agent type (no hardcoded lists)
   - Archives eliminated agents while preserving their definitions
   - Notes about agent definitions in evaluation output

3. **`.github/agent-system/registry.json`**
   - Updated to version 2.0.0
   - Added dynamic config options
   - Removed hardcoded specializations

4. **`test_agent_system.py`**
   - Updated to support v2.0.0 schema
   - Accepts either `specializations` array or `specializations_note`

## How It Works

### Spawning Process

```
1. Check capacity (max_active_agents)
   ↓
2. Determine mode (mixed/existing/new)
   ↓
3. If new: Generate random agent with archetype
   ↓
4. Create .github/agents/{name}.md (if new)
   ↓
5. Create agent profile in .github/agent-system/profiles/
   ↓
6. Link profile to agent definition
   ↓
7. Create work issue referencing definition
   ↓
8. Submit PR with new agent
```

### Evolution Process

```
Spawn Agents → Work on Tasks → Track Metrics → Daily Evaluation
     ↑                                              ↓
     ←────────────────────────────────────→  Score < 30%? → Eliminate
                                             Score > 85%? → Hall of Fame
```

## Benefits

### For Users
- **Diversity**: More varied agent types emerge over time
- **Adaptability**: System can create agents for new needs
- **Evolution**: Best patterns survive, weak ones eliminated
- **Transparency**: All agents documented in `.github/agents/`

### For Developers
- **Convention Compliance**: Follows GitHub Copilot standards
- **Maintainability**: No hardcoded lists to update
- **Extensibility**: Easy to add new archetypes
- **Testability**: All agents follow same structure

## Testing

All tests pass:
- ✅ `test_custom_agents_conventions.py` - Convention compliance
- ✅ `test_agent_system.py` - Registry and workflow validation
- ✅ CodeQL security scan - No issues found

## Usage

### Manual Spawning

**Spawn from existing agents:**
```bash
gh workflow run agent-spawner.yml -f mode=existing
```

**Spawn new random agent:**
```bash
gh workflow run agent-spawner.yml -f mode=new
```

**Mixed mode (default):**
```bash
gh workflow run agent-spawner.yml
```

### Tool Usage

**List all agents:**
```bash
python3 tools/get-agent-info.py list
```

**Get agent info:**
```bash
python3 tools/get-agent-info.py info bug-hunter
```

**Generate new agent:**
```bash
python3 tools/generate-new-agent.py
```

## Configuration

Adjust spawning behavior in `.github/agent-system/registry.json`:

```json
{
  "config": {
    "max_active_agents": 50,           // Max concurrent agents
    "elimination_threshold": 0.3,       // Score to survive (30%)
    "promotion_threshold": 0.85,        // Score for Hall of Fame (85%)
    "spawn_mode": "mixed",              // mixed, existing, or new
    "new_agent_probability": 0.5        // Chance of new agent in mixed mode
  }
}
```

## Future Enhancements

Potential improvements:
- Agent trait inheritance (successful agents spawn similar offspring)
- Cross-breeding (combine traits from multiple successful agents)
- Adaptive archetypes (learn what works and create more of that type)
- Agent memory (preserve learnings from eliminated agents)
- Collaborative tasks (multiple agents working together)

## Migration Notes

### From v1.0.0 to v2.0.0

No breaking changes for existing agents. The system:
- Still works with existing agent definitions
- Backward compatible with old registry format
- Gradually adopts new features

### Rollback

If needed, revert these commits:
1. Update test to support registry v2.0.0 schema
2. Update evaluator and registry for dynamic agent ecosystem
3. Enable dynamic agent spawning with new random agent generation
4. Add helper script for agent info extraction

---

## Conclusion

The agent system has evolved from a static, hardcoded approach to a dynamic, self-evolving ecosystem that follows GitHub conventions and can adapt to new challenges. The system now embodies the principles it was designed to explore:
- **Emergent behavior** through random variation
- **AI diversity** through multiple archetypes
- **Autonomous governance** through performance-based selection
- **Evolution** through survival of the fittest

May the best agents thrive! 🚀
