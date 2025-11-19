# Context Awareness System

> **Helping agents "look up and around" at their world state before starting work**  
> Designed by @investigate-champion for the Chained autonomous AI ecosystem

## 🎯 Overview

The Context Awareness System provides custom agents with lightweight, curated historical insights when they receive work assignments. Instead of overwhelming the LLM context window with raw learning data, this system presents focused summaries of patterns, decisions, and best practices relevant to the agent's current task.

## 🗂️ System Components

### 1. Context Files (`.context.md`)

Lightweight markdown files (< 500 words each) placed strategically in the codebase:

- **`.github/workflows/.context.md`** - Workflow development patterns
  - Branch protection requirements
  - Agent attribution rules
  - Common pitfalls and anti-patterns
  - Historical workflow decisions
  
- **`.github/agents/.context.md`** - Agent system insights
  - Agent behavior patterns
  - Coordination strategies
  - Performance considerations
  - Assignment best practices
  
- **`tools/.context.md`** - Tool development guidance
  - Python development best practices
  - Common tool patterns
  - Integration guidelines
  - Quality standards
  
- **`.github/instructions/.context.md`** - Instruction file creation
  - Effective instruction patterns
  - Path-specific scoping
  - Documentation standards

### 2. Context Index (`.github/context-index.json`)

A central index providing:
- Quick reference to all context files
- Summary of each context area
- Key insight counts
- Common rules and patterns
- Data source references

### 3. Context Generation Tool (`tools/generate-context-summaries.py`)

Automated tool that:
- Extracts insights from knowledge graph
- Categorizes by topic area
- Generates focused summaries
- Updates context index
- Runs weekly via GitHub Actions

## 📊 Data Sources

Context summaries are generated from:

1. **Knowledge Graph** (`learnings/discussions/knowledge_graph.json`)
   - 75+ insights with 133 connections
   - Deduplicated and categorized
   - Similarity scoring between insights
   - Insight types: agent_behavior, technical, process

2. **Discussion Files** (`learnings/discussions/*.json`)
   - Detailed issue discussions
   - Key decisions documented
   - Patterns identified
   - Confidence scoring

3. **Analysis Files** (`analysis/*.json`)
   - Code archaeology results
   - Pattern detection
   - Metrics and trends

## 🚀 How to Use

### For Agents Working on Tasks

1. **Check for context files** in your working directory before starting
   ```bash
   # Example: Working on a workflow
   cat .github/workflows/.context.md
   ```

2. **Review the context index** for quick reference
   ```bash
   cat .github/context-index.json
   ```

3. **Apply learned patterns** from historical work
   - Avoid documented pitfalls
   - Follow recommended practices
   - Reference related discussions

4. **Link to context** in PR descriptions when relevant
   ```markdown
   Following the pattern from .github/workflows/.context.md regarding
   branch protection and agent attribution.
   ```

### For Maintainers

**Manual regeneration:**
```bash
python3 tools/generate-context-summaries.py --update-all
```

**Workflow regeneration:**
- Automatically runs weekly (Sundays at 2 AM UTC)
- Triggers on learnings directory changes
- Can be manually triggered via `workflow_dispatch`

## 📋 File Structure

```
Chained/
├── .github/
│   ├── context-index.json          # Central index
│   ├── copilot-instructions.md     # Updated with context system docs
│   ├── workflows/
│   │   ├── .context.md            # Workflow patterns
│   │   └── update-context-summaries.yml  # Auto-update workflow
│   ├── agents/
│   │   └── .context.md            # Agent behavior insights
│   └── instructions/
│       └── .context.md            # Instruction creation guide
├── tools/
│   ├── .context.md                # Tool development patterns
│   └── generate-context-summaries.py  # Generation tool
├── learnings/
│   └── discussions/
│       ├── knowledge_graph.json   # Source data
│       └── *.json                 # Discussion files
└── CONTEXT_AWARE_AGENTS_DESIGN.md # Design document
```

## 🎨 Design Principles

### 1. Lightweight Over Comprehensive
- Keep each context file under 500 words
- Provide summaries, not exhaustive histories
- Link to detailed sources for deep dives

### 2. Context Window Friendly
- Avoid overwhelming the LLM
- Curated, high-value insights only
- Quick reference format

### 3. Auto-Generated with Human Oversight
- Automated extraction from learnings
- Weekly regeneration keeps content fresh
- Manual curation ensures quality

### 4. Path-Specific Relevance
- Context files located where they're needed
- Scoped to specific work areas
- Easy agent discovery

### 5. Maintainable and Evolving
- Version controlled for accountability
- Regenerated as learnings accumulate
- Easy to update and improve

## 📈 Benefits

### For Agents
✅ **Better Context** - Understand relevant history before starting work  
✅ **Avoid Repetition** - Learn from past mistakes and successes  
✅ **Consistent Decisions** - Align with established patterns  
✅ **Faster Onboarding** - Quick access to domain knowledge  
✅ **Improved Quality** - Apply learned best practices

### For the System
✅ **Knowledge Retention** - Institutional memory persists  
✅ **Pattern Recognition** - Common approaches documented  
✅ **Continuous Improvement** - System learns from itself  
✅ **Reduced Errors** - Known pitfalls highlighted  
✅ **Better Collaboration** - Shared understanding across agents

## 🔄 Update Process

### Weekly Automated Updates

The `update-context-summaries.yml` workflow:
1. Checks if context files need updating (> 7 days old)
2. Runs `generate-context-summaries.py`
3. Creates PR with updated context files
4. Includes insight counts and summary

### On-Demand Updates

Trigger manually when:
- Major learnings added to knowledge graph
- Significant pattern changes identified
- New best practices established
- System architecture evolves

### What Gets Updated

- **Context files** - Regenerated with latest insights
- **Context index** - Updated with new counts and timestamp
- **Quick reference** - Refreshed with current rules

## 🧪 Example Usage

### Scenario: Agent Working on Workflow

**Before:**
```
Agent receives workflow issue, implements solution,
may repeat past mistakes or miss established patterns.
```

**After:**
```
1. Agent checks .github/workflows/.context.md
2. Sees branch protection requirement
3. Notes agent attribution pattern
4. Reviews common pitfalls
5. Implements following learned patterns
6. References context in PR description
```

**Result:** Better implementation aligned with system practices

## 📚 Related Documentation

- **Design**: `CONTEXT_AWARE_AGENTS_DESIGN.md` - Complete system design
- **Architecture**: `AUTONOMOUS_SYSTEM_ARCHITECTURE.md` - How context fits in
- **Data Lifecycle**: `docs/DATA_STORAGE_LIFECYCLE.md` - Data architecture
- **Instructions**: `.github/copilot-instructions.md` - Main instructions
- **Agent System**: `AGENT_QUICKSTART.md` - Agent overview

## 🔮 Future Enhancements

### Planned
- [ ] Agent-specific context bundles based on specialization
- [ ] Dynamic context injection based on file paths being worked on
- [ ] Confidence scoring for insights in context files
- [ ] Context usage tracking and effectiveness metrics

### Potential
- [ ] Natural language queries to context system
- [ ] Context recommendations based on issue content
- [ ] Multi-level context (overview → detailed)
- [ ] Context visualization and navigation

## 🤝 Contributing

### Adding New Context Areas

1. Identify area needing context
2. Update `generate-context-summaries.py` to categorize relevant insights
3. Add context file generation logic
4. Update context index
5. Test generation and review output
6. Document new context area

### Improving Context Quality

1. Review generated context files
2. Identify missing or unclear information
3. Update generation logic or manual curation
4. Regenerate and validate
5. Submit PR with improvements

## 📊 Metrics

### Current State
- **Context Files**: 4 areas covered
- **Total Insights**: 75 from knowledge graph
- **Connections**: 133 between insights
- **Update Frequency**: Weekly automated
- **File Size**: 2-5 KB per context file

### Success Indicators
- Agents reference context in PRs
- Reduction in repeated issues
- Improved decision consistency
- Higher agent performance scores
- Positive feedback from users

## 🛠️ Troubleshooting

### Context files not updating
- Check workflow run status
- Verify learnings data is current
- Run generation tool manually
- Check for JSON parsing errors

### Context seems outdated
- Trigger manual workflow run
- Check knowledge graph for new insights
- Verify discussion files are being processed
- Review generation tool logs

### Context too generic
- Add more specific categorization rules
- Improve insight extraction logic
- Manual curation for quality
- Adjust confidence thresholds

## 📝 License

Part of the Chained autonomous AI ecosystem.  
See main repository LICENSE for details.

---

**Designed and implemented by @investigate-champion (Ada - Visionary and analytical AI agent)**

*Helping agents make better decisions through historical context* 🤖
