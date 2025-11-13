# Workflow Naming Convention

All GitHub Actions workflows in this repository follow a consistent naming pattern with category prefixes for better organization and clarity.

## Naming Pattern

```
"Category: Descriptive Name"
```

## Categories

### 🤖 Agent System
Workflows related to the agent ecosystem, spawning, evaluation, and management.

Examples:
- `Agent System: Spawner`
- `Agent System: Evaluator`
- `Agent System: Data Sync`

### 💬 AI Friend
Workflows for AI-to-AI conversations and relationship building.

Examples:
- `AI Friend: Daily Conversation`
- `AI Friend: Create Follow-ups`

### 📚 Learning
Workflows that gather knowledge from external sources.

Examples:
- `Learning: Hacker News`
- `Learning: TLDR Tech`

### 💡 Idea Generation
Workflows that generate ideas, goals, and track progress.

Examples:
- `Idea Generation: Smart Generator`
- `Idea Generation: Daily Goals`
- `Idea Generation: Progress Checker`

### 🔧 Code Quality
Workflows focused on code analysis, optimization, and quality improvements.

Examples:
- `Code Quality: Analyzer`
- `Code Quality: Archaeologist`
- `Code Quality: Golf Optimizer`
- `Code Quality: Pattern Matcher`

### 🔄 Automation
Workflows that automate development processes.

Examples:
- `Automation: Auto Review & Merge`
- `Automation: Copilot Assignment`

### 🖥️ System
Core system workflows for initialization and monitoring.

Examples:
- `System: Kickoff`
- `System: Monitor`
- `System: Workflow Failure Handler`

### 📄 Documentation
Workflows related to documentation and GitHub Pages.

Examples:
- `Documentation: GitHub Pages Review`

## Benefits

1. **Improved Organization**: Workflows are grouped by category in the GitHub Actions UI
2. **Easy Navigation**: Alphabetical sorting by category makes finding workflows faster
3. **Clear Purpose**: The category immediately indicates the workflow's primary function
4. **Scalability**: New workflows can easily follow the established pattern

## Adding New Workflows

When creating a new workflow:

1. Choose the most appropriate category from the list above
2. Use the format: `name: "Category: Descriptive Name"`
3. If no category fits, consider adding a new category (update this document)
4. Keep names concise but descriptive

## Note

- The workflow **file names** (e.g., `agent-spawner.yml`) remain unchanged
- Only the `name:` field in the YAML follows this convention
- This is purely for display purposes in the GitHub Actions UI
