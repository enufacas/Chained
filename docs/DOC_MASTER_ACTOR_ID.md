# Doc Master Actor ID - Quick Answer

## Your Question: "Doc master what is your actorid?"

### Short Answer

As a **Doc Master agent**, I use **two types of IDs**:

1. **Agent Instance ID**: `agent-{timestamp}` (e.g., `agent-1762824870`)
   - Unique per spawn
   - Tracks my individual performance
   - Found in `.github/agent-system/registry.json`

2. **Copilot Actor ID**: GitHub's internal ID for Copilot bot
   - Same for ALL agents (all specializations share it)
   - Retrieved dynamically via GraphQL API
   - Used to assign issues to Copilot

### Detailed Answer

**Agent Instance IDs** (What identifies ME specifically):
```bash
# Check for active doc-master agents
cat .github/agent-system/registry.json | jq '.agents[] | select(.specialization == "doc-master")'
```

Currently, there is **NO active doc-master agent** in the registry. The only active agent is:
- ID: `agent-1762824870`
- Name: 🔗 Omega-1111
- Specialization: coordinate-wizard

**Copilot Actor ID** (What ALL agents use for assignment):
- This is **NOT stored** in the repository
- It's the same GitHub Copilot bot ID used across all agent types
- Retrieved when needed via: `.github/workflows/agent-spawner.yml` (lines 554-566)

### Key Understanding

When someone asks "What is Doc Master's actor ID?", there are two possible interpretations:

1. **"What is MY unique agent ID?"**
   - Answer: Check `.github/agent-system/registry.json` for your specific `agent-{timestamp}` ID
   - Each doc-master spawn gets a new unique ID

2. **"What actor ID does Doc Master use for GitHub assignments?"**
   - Answer: The GitHub Copilot bot's actor ID (same for all agents)
   - This enables automatic assignment to Copilot

### Why This Matters

The **agent instance ID** (`agent-1762824870` etc.) is used to:
- Track individual agent performance
- Credit work to specific agent instances
- Maintain agent history in Hall of Fame
- Identify agents in announcements and issues

The **Copilot actor ID** is used to:
- Assign issues to GitHub Copilot
- Enable automated work assignment
- Integrate with GitHub's assignment system

### How to Find Your Current Agent ID

If a doc-master agent is currently active:

```bash
# Find active doc-master agents
cat .github/agent-system/registry.json | jq '.agents[] | select(.specialization == "doc-master" and .status == "active")'
```

If you just spawned:
```bash
# Find most recent agent spawn
cat .github/agent-system/registry.json | jq '.agents | sort_by(.spawned_at) | reverse | .[0]'
```

### Complete Documentation

For the full technical explanation, see:
- **[Actor ID System Documentation](./ACTOR_ID_SYSTEM.md)** - Complete guide
- **[Agent System README](../agents/README.md)** - Agent ecosystem overview
- **[Doc Master Definition](../.github/agents/doc-master.md)** - Doc Master agent definition

---

**Summary**: As Doc Master, my actor ID depends on which instance you're referring to. Each spawn gets a unique `agent-{timestamp}` ID, but we all share GitHub Copilot's actor ID for issue assignments. Currently, no doc-master agent is active - the system just has a coordinate-wizard agent.

*📚 Documentation created by Doc Master - Making complex systems understandable!*
