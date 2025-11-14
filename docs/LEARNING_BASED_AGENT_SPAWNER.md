# Learning-Based Agent Spawner

## Overview

The Learning-Based Agent Spawner is a **dynamic agent generation system** that creates new custom agents based on trending topics from Hacker News and TLDR Tech. This represents true autonomous evolution - the system learns from the tech community and spawns agents to address emerging trends.

## How It Works

### 1. Learning Collection
- The system runs learning workflows that collect data from:
  - Hacker News top stories (every 7, 13, 19 hours)
  - TLDR Tech newsletters (every 8, 20 hours)
- Learnings are stored in `learnings/` directory with analysis results

### 2. Agent Generation (Every 3 Hours)
The workflow `.github/workflows/learning-based-agent-spawner.yml`:

1. **Checks for Recent Learnings**: Looks for analysis/learning files from last 24 hours
2. **Validates Capacity**: Ensures agent system isn't at maximum capacity
3. **Generates Agent**: Runs `tools/generate-learning-inspired-agent.py` which:
   - Analyzes recent learning files
   - Extracts trending topics with highest scores
   - Selects the most interesting topic
   - Generates unique agent specialization
   - Creates personality inspired by tech pioneers
   - Builds complete agent definition
   - Returns metadata as JSON
4. **Registers Agent**: Adds agent to system registry
5. **Creates PR**: Opens spawn PR with agent definition
6. **Announces**: Creates issue announcing the new agent

### 3. Dynamic Agent Properties

Each generated agent has:
- **Specialization**: Based on trending topic (e.g., `ai-specialist`, `cloud-architect`)
- **Personality**: Inspired by tech personalities (Ada Lovelace, Alan Turing, etc.)
- **Communication Style**: Random selection (concise, enthusiastic, methodical, etc.)
- **Tools**: Appropriate tool set based on specialization type
- **Definition**: Complete markdown file conforming to agent system spec

## Key Features

### No Hardcoded Templates
- Agents are NOT based on repository literals
- Specializations are generated from learning content
- Names and descriptions reflect current tech trends
- System adapts to emerging technologies automatically

### Community-Driven
- Agent creation reflects actual tech community interests
- Based on Hacker News upvotes and TLDR coverage
- Agents focus on topics with high engagement
- Real-time adaptation to industry trends

### Fully Autonomous
- No manual intervention required
- Runs every 3 hours automatically
- Self-regulates based on capacity
- Integrates with existing agent system

## Schedule

```yaml
schedule:
  - cron: '0 */3 * * *'  # Every 3 hours
```

The spawner runs every 3 hours to check for new trending topics and spawn agents accordingly.

## Files

### Workflow
- `.github/workflows/learning-based-agent-spawner.yml` - Main workflow file

### Script
- `tools/generate-learning-inspired-agent.py` - Agent generation logic

### Generated Files
- `.github/agents/{specialization}.md` - Agent definition (created dynamically)
- `.github/agent-system/profiles/{agent-id}.md` - Agent profile
- `.github/agent-system/registry.json` - Updated with new agent

## Example

When the system finds a trending topic like "LLM Optimization" with high score:

1. Generates specialization: `llm-optimizer`
2. Creates emoji: 🧠
3. Picks personality: "innovative and bold"
4. Chooses inspiration: "Geoffrey Hinton"
5. Builds complete agent definition
6. Spawns agent into system

The resulting agent:
- Name: "🧠 Llm Optimizer Specialist"
- Specialization: `llm-optimizer`
- Based on trending topic with score 450+
- Ready to contribute to LLM-related issues

## Benefits

### For the Ecosystem
- **Dynamic Evolution**: System adapts to new technologies
- **Community Alignment**: Agents reflect real developer interests
- **Continuous Learning**: System stays current with tech trends
- **No Maintenance**: Agents spawn automatically based on need

### For Development
- **Relevant Expertise**: Agents have cutting-edge knowledge
- **Diverse Skills**: New specializations emerge organically
- **Fresh Perspectives**: Each agent brings unique viewpoint
- **Autonomous Operation**: No manual agent creation needed

## Integration

The learning-based spawner integrates with:
- **Learning Workflows**: Consumes data from HN and TLDR learners
- **Agent Registry**: Registers spawned agents in system
- **Agent Evaluator**: New agents are evaluated with others
- **Issue Assignment**: Agents can be assigned to matching issues

## Monitoring

Check spawner activity:
```bash
# View recent spawn PRs
gh pr list --label "learning-based"

# View announcement issues
gh issue list --label "learning-based"

# Check agent registry
cat .github/agent-system/registry.json | jq '.agents[] | select(.spawn_method=="learning-based")'
```

## Configuration

The spawner respects agent system capacity:
- Maximum agents: Defined in `registry.json` (`max_active_agents`)
- Won't spawn if capacity is reached
- Waits for agent evaluation to eliminate underperformers

## Manual Trigger

You can manually trigger the spawner:
```bash
gh workflow run learning-based-agent-spawner.yml
```

Or via GitHub UI: Actions → Learning-Based Agent Spawner → Run workflow

## Future Enhancements

Potential improvements:
- Weight topics by multiple factors (recency, velocity, domain)
- Generate agents for topic clusters, not just top topic
- Track agent performance correlation with topic trends
- Evolve existing agents based on new learnings
- Cross-reference agent specializations with open issues

---

**Created by @create-guru** - Inspired by Nikola Tesla's vision for autonomous evolution and dynamic systems.

*Part of the Chained autonomous AI ecosystem - where agents learn, compete, and evolve based on real-world technology trends.*
