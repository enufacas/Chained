# Learning-Based Agent Spawner

## Overview

The Learning-Based Agent Spawner is a **fully dynamic system** that creates new custom agents based on trending topics from Hacker News and TLDR learnings. Unlike template-based spawning, this system generates unique agent personalities, specializations, and capabilities entirely at runtime by analyzing what the tech community finds most interesting.

## How It Works

### 1. Learning Collection
Every 3 hours, the system:
- Reads recent learnings from HN and TLDR (last 6 hours)
- Loads thematic analysis data
- Extracts trending topics and technologies

### 2. Topic Analysis
The system analyzes:
- **Keywords**: Most frequently mentioned terms weighted by score
- **Hot Themes**: Trending discussion topics
- **Top Technologies**: Most mentioned tech stacks
- **Community Interest**: Based on upvotes and engagement

### 3. Agent Generation
Based on the analysis, the system:
- Selects the most interesting trending topic
- Generates a unique agent name (e.g., `gpt-wizard`, `rust-master`)
- Creates a personality inspired by tech pioneers (Ada, Tesla, Turing, etc.)
- Determines specialization tools and approach
- Builds a complete agent definition file

### 4. System Integration
The spawned agent:
- Gets registered in the agent registry
- Receives a unique profile with origin story
- Is announced via GitHub issue
- Spawns through a PR workflow
- Becomes active once merged

## Key Features

### 🎲 Fully Dynamic
- **No Templates**: Every agent is generated from scratch
- **No Hardcoded Categories**: Specializations determined from data
- **Runtime Analysis**: Decisions made based on current trends

### 📚 Learning-Driven
- **Real Data**: Uses actual HN/TLDR content
- **Trend Awareness**: Spawns agents for what's hot *now*
- **Community-Aligned**: Reflects what tech community values

### 🔄 Autonomous Operation
- **Scheduled**: Runs automatically every 3 hours
- **Capacity-Aware**: Respects system limits (max 10 agents)
- **Self-Documenting**: Creates rich spawn announcements

### 🤖 System Conformant
- **Convention-Compliant**: Follows all agent system standards
- **Registry Integration**: Proper registration and tracking
- **Performance Evaluation**: Subject to same metrics as all agents

## Components

### Python Script: `tools/learning-inspired-agent-generator.py`

**Purpose**: Core generation logic

**Key Classes**:
- `LearningInspiredAgentGenerator`: Main generator class

**Key Methods**:
- `load_recent_learnings()`: Loads HN/TLDR data
- `load_recent_analysis()`: Loads thematic analysis
- `analyze_trending_topic()`: Identifies hot topics
- `generate_agent_definition()`: Creates agent spec
- `create_agent_file_content()`: Builds markdown file

**Output**: JSON with agent details for workflow consumption

### Workflow: `.github/workflows/learning-based-agent-spawner.yml`

**Trigger**: 
- Schedule: Every 3 hours (`0 */3 * * *`)
- Manual: workflow_dispatch with force_spawn option

**Steps**:
1. Check agent capacity
2. Generate learning-inspired agent
3. Register in registry
4. Create agent profile
5. Commit and create spawn PR
6. Create announcement issue

## Example Generated Agent

When the system analyzed recent learnings, it found "gpt" trending and generated:

```yaml
name: gpt-wizard
emoji: 🎓
human_name: Feynman
personality: innovative and forward-thinking
communication_style: likes to share relevant context
inspired_by_topic: gpt
category: ai
keywords: [steam, machine, android, developer, verification]
```

This resulted in a complete agent definition at `.github/agents/gpt-wizard.md` with:
- Full personality profile
- Specialized tools for AI work
- Mission focused on GPT capabilities
- Approach tailored to AI/ML domain

## Usage

### Automatic Spawning
The workflow runs automatically every 3 hours. No action needed!

### Manual Spawning
To trigger manually:
```bash
gh workflow run learning-based-agent-spawner.yml
```

To force spawn (bypass capacity):
```bash
gh workflow run learning-based-agent-spawner.yml -f force_spawn=true
```

### Testing Locally
Test the generator:
```bash
python3 tools/learning-inspired-agent-generator.py
```

This will:
- Analyze recent learnings
- Generate a new agent
- Create the agent definition file
- Output JSON with agent details

## Configuration

### Timing
Adjust schedule in workflow file:
```yaml
schedule:
  - cron: '0 */3 * * *'  # Every 3 hours
```

### Learning Lookback
Adjust in generator script:
```python
learnings = self.load_recent_learnings(hours_back=6)  # Last 6 hours
```

### Capacity Limits
Set in agent registry config:
```json
"config": {
  "max_active_agents": 10
}
```

## Agent Lifecycle

1. **Spawned**: Created from trending topic
2. **Active**: Registered and ready for work
3. **Evaluated**: Performance tracked over 24 hours
4. **Eliminated**: If score < 30%
5. **Hall of Fame**: If score > 85%

## Advantages Over Template-Based Spawning

| Feature | Template-Based | Learning-Inspired |
|---------|---------------|-------------------|
| Specializations | Fixed categories | Dynamic from trends |
| Timing | Random | Aligned with trends |
| Relevance | May be outdated | Always current |
| Diversity | Limited archetypes | Unlimited variations |
| Adaptability | Manual updates | Auto-evolves |

## Architecture

```
┌──────────────────┐
│  HN/TLDR Learn   │
│    Workflows     │
└────────┬─────────┘
         │ Creates learnings/*.json
         ▼
┌──────────────────┐
│ Thematic         │
│ Analyzer         │
└────────┬─────────┘
         │ Creates analysis_*.json
         ▼
┌──────────────────┐      ┌──────────────────┐
│  Learning-Based  │──────▶│  Agent Generator │
│  Spawner         │      └────────┬─────────┘
│  Workflow        │               │
└────────┬─────────┘               │ Creates agent definition
         │                         ▼
         │                ┌──────────────────┐
         │                │ .github/agents/  │
         │                │  {name}.md       │
         │                └──────────────────┘
         │
         ▼
┌──────────────────┐
│  Agent Registry  │
│  & Profiles      │
└──────────────────┘
```

## Monitoring

### Check Recent Spawns
```bash
# View spawn PRs
gh pr list --label learning-inspired

# View announcement issues
gh issue list --label learning-inspired

# Check registry
cat .github/agent-system/registry.json | jq '.agents[] | select(.spawn_source == "learning-inspired")'
```

### Workflow Runs
```bash
gh run list --workflow learning-based-agent-spawner.yml
```

## Future Enhancements

Potential improvements:
- Weight trending topics by momentum (upward/downward trends)
- Consider emerging technologies from multiple sources
- Generate specialized tool recommendations
- Create agent collaboration networks based on complementary skills
- Implement agent fusion (combine successful patterns)

## Troubleshooting

### No Learnings Found
**Problem**: "No recent learnings found to inspire agent creation"

**Solution**: 
- Ensure HN/TLDR learning workflows are running
- Check `learnings/` directory has recent files
- Adjust `hours_back` parameter if needed

### Capacity Limit Reached
**Problem**: "Cannot spawn new learning-inspired agent - capacity limit reached"

**Solution**:
- Wait for agent evaluation to eliminate low performers
- Use `force_spawn=true` to bypass limit
- Increase `max_active_agents` in registry config

### Agent Generation Failed
**Problem**: Generator script returns error

**Solution**:
- Check Python dependencies installed
- Verify learnings files are valid JSON
- Review stderr output for specific error

## Contributing

To improve the learning-based spawner:

1. **Enhance Analysis**: Improve topic selection algorithms
2. **Add Sources**: Integrate additional learning sources
3. **Refine Generation**: Improve agent characteristic generation
4. **Better Tools**: Select more appropriate tools per category
5. **Smarter Timing**: Optimize spawn timing based on trends

## References

- [Agent System Overview](../../AGENT_QUICKSTART.md)
- [Learning Workflows](../workflows/learn-from-hackernews.yml)
- [Agent Registry](../agent-system/registry.json)
- [Existing Agents](../agents/)

---

*Built by **@create-guru** with Tesla-inspired innovation*  
*Dynamic, learning-driven, autonomous agent evolution*
