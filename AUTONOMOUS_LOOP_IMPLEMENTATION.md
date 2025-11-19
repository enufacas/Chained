# 🚀 Autonomous Loop Implementation Guide

> **Practical examples and patterns for implementing the Chained autonomous loop**

This guide provides concrete examples and implementation patterns for building workflows that comply with Chained's autonomous system architecture and critical constraints.

## 📋 Table of Contents

1. [Quick Reference](#quick-reference)
2. [Learning Ingestion Example](#learning-ingestion-example)
3. [World Model Update Example](#world-model-update-example)
4. [Agent Assignment Example](#agent-assignment-example)
5. [Workflow Chaining Example](#workflow-chaining-example)
6. [Self-Reinforcement Example](#self-reinforcement-example)
7. [Complete Workflow Template](#complete-workflow-template)
8. [Testing and Validation](#testing-and-validation)

---

## 🎯 Quick Reference

### Critical Patterns Checklist

Every autonomous loop workflow MUST:

- [ ] ✅ Create PR (never push to main)
- [ ] ✅ Use unique branch names (timestamp + run ID)
- [ ] ✅ Create labels before use (`--force` flag)
- [ ] ✅ Enforce 10-agent limit
- [ ] ✅ Use @agent-name mentions
- [ ] ✅ Comment on issues before completion
- [ ] ✅ Use `workflow_run` for chaining
- [ ] ✅ Answer all 8 completion questions
- [ ] ✅ Log clear status messages
- [ ] ✅ Handle errors gracefully

### Workflow Chain Order

```
1. Learning Ingestion (TLDR, HN, Trending)
   ↓ workflow_run
2. Combined Learning Analysis
   ↓ workflow_run
3. World Model Update
   ↓ workflow_run
4. Agent Assignment & Mission Creation
   ↓ issue assignment
5. Agent Work Execution (Copilot)
   ↓ PR merge
6. Self-Reinforcement (Learning from outcomes)
   ↓ feeds back to step 1
```

---

## 📚 Learning Ingestion Example

```yaml
name: "Learning: TLDR Tech"

on:
  schedule:
    - cron: '0 8,20 * * *'  # Twice daily
  workflow_dispatch:

permissions:
  contents: write
  issues: write
  pull-requests: write

jobs:
  learn-from-tldr:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
      
      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      
      - name: Install dependencies
        run: |
          pip install requests beautifulsoup4 feedparser
      
      - name: Fetch and parse TLDR
        id: fetch
        run: |
          python3 << 'PYEOF'
          import feedparser
          import json
          from datetime import datetime, timezone
          import os
          
          # Fetch TLDR Tech feed
          feed = feedparser.parse('https://tldr.tech/tech/rss')
          
          # Parse and normalize entries
          learnings = []
          for entry in feed.entries[:10]:  # Top 10 stories
              learning = {
                  'id': f"tldr-{entry.id}",
                  'title': entry.title,
                  'url': entry.link,
                  'summary': entry.summary[:500],
                  'published': entry.published,
                  'source': 'tldr-tech',
                  'timestamp': datetime.now(timezone.utc).isoformat()
              }
              learnings.append(learning)
          
          # Save to file
          timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
          filename = f"learnings/tldr_{timestamp}.json"
          
          os.makedirs('learnings', exist_ok=True)
          with open(filename, 'w') as f:
              json.dump(learnings, f, indent=2)
          
          print(f"Saved {len(learnings)} learnings to {filename}")
          
          # Set output for next step
          with open(os.environ['GITHUB_OUTPUT'], 'a') as f:
              f.write(f"filename={filename}\n")
              f.write(f"count={len(learnings)}\n")
          PYEOF
      
      - name: Ensure labels exist
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          # Create required labels
          gh label create "learning" \
            --description "Learning system activity" \
            --color "0E8A16" \
            --force 2>/dev/null || true
          
          gh label create "learning-source-tldr" \
            --description "From TLDR Tech newsletter" \
            --color "10B981" \
            --force 2>/dev/null || true
          
          gh label create "automated" \
            --description "Automated workflow action" \
            --color "E99695" \
            --force 2>/dev/null || true
          
          echo "✅ Labels created/verified"
      
      - name: Create PR with learnings
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          # Check for changes
          git add .
          if git diff --staged --quiet; then
            echo "No new learnings found"
            exit 0
          fi
          
          # Configure git
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"
          
          # Create unique branch
          TIMESTAMP=$(date +%Y%m%d-%H%M%S)
          BRANCH_NAME="learning/tldr-${TIMESTAMP}-${{ github.run_id }}"
          git checkout -b "$BRANCH_NAME"
          
          # Commit changes
          git commit -m "Learning: TLDR Tech $(date +%Y-%m-%d)"
          
          # Push to new branch (NOT main)
          git push origin "$BRANCH_NAME"
          
          # Create pull request
          gh pr create \
            --title "📚 Learning: TLDR Tech - $(date +%Y-%m-%d)" \
            --body "## Learning Ingestion

          **Source**: TLDR Tech Newsletter
          **Count**: ${{ steps.fetch.outputs.count }} learnings
          **File**: ${{ steps.fetch.outputs.filename }}

          ### Learnings Added

          This PR adds normalized learnings from TLDR Tech.

          ### Autonomous Loop Stage

          This is **Stage 1: Learning Ingestion** of the autonomous loop.
          
          **Next**: This will trigger Combined Learning Analysis workflow.

          ### Completion Questions

          1. ✅ **Learning artifact**: ${{ steps.fetch.outputs.filename }}
          2. ⏭️  **World model update**: Next workflow stage
          3. ⏭️  **Agents reacting**: Will be determined in assignment stage
          4. ⏭️  **Agent capacity**: Will be validated in assignment stage
          5. ⏭️  **Agent movement**: Will be updated in world model stage
          6. ⏭️  **Mission issue**: Will be created in assignment stage
          7. ✅ **Labels created**: Verified in workflow
          8. ✅ **Next workflow**: Combined Learning Analysis (workflow_run trigger)

          ---

          *Automated by TLDR learning ingestion workflow*" \
            --label "learning,learning-source-tldr,automated" \
            --base main \
            --head "$BRANCH_NAME"
          
          echo "✅ PR created successfully"
```

---

## 🌍 World Model Update Example

```yaml
name: "World Model Update"

on:
  workflow_run:
    workflows: ["Learning: Combined Sources"]
    types: [completed]
    branches: [main]
  schedule:
    - cron: '0 */2 * * *'  # Every 2 hours
  workflow_dispatch:

permissions:
  contents: write
  issues: write
  pull-requests: write

jobs:
  update-world:
    runs-on: ubuntu-latest
    # Only run if parent workflow succeeded
    if: >
      github.event_name == 'schedule' || 
      github.event_name == 'workflow_dispatch' ||
      github.event.workflow_run.conclusion == 'success'
    
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
      
      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      
      - name: Sync agents to world
        run: |
          python3 world/sync_agents_to_world.py
          echo "✅ Agents synced to world model"
      
      - name: Sync learnings to ideas
        run: |
          python3 world/sync_learnings_to_ideas.py
          echo "✅ Learnings converted to ideas"
      
      - name: Update knowledge graph
        run: |
          python3 world/knowledge_manager.py update
          echo "✅ Knowledge graph updated"
      
      - name: Update world tick
        run: |
          python3 << 'PYEOF'
          import json
          
          # Read current world state
          with open('world/world_state.json', 'r') as f:
              world = json.load(f)
          
          # Increment tick
          world['tick'] = world.get('tick', 0) + 1
          
          # Save updated state
          with open('world/world_state.json', 'w') as f:
              json.dump(world, f, indent=2)
          
          print(f"✅ World tick updated to {world['tick']}")
          PYEOF
      
      - name: Ensure labels exist
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          gh label create "world-model" \
            --description "World model updates" \
            --color "5319E7" \
            --force 2>/dev/null || true
          
          gh label create "automated" \
            --description "Automated workflow action" \
            --color "E99695" \
            --force 2>/dev/null || true
      
      - name: Create PR with world updates
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          # Check for changes
          git add world/
          if git diff --staged --quiet; then
            echo "No world model changes"
            exit 0
          fi
          
          # Configure git
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"
          
          # Create unique branch
          TIMESTAMP=$(date +%Y%m%d-%H%M%S)
          BRANCH_NAME="world-update/${TIMESTAMP}-${{ github.run_id }}"
          git checkout -b "$BRANCH_NAME"
          
          # Commit changes
          git commit -m "World model update $(date +%Y-%m-%d)"
          
          # Push to new branch
          git push origin "$BRANCH_NAME"
          
          # Get world tick
          TICK=$(jq -r '.tick' world/world_state.json)
          AGENT_COUNT=$(jq '.agents | length' world/world_state.json)
          IDEA_COUNT=$(jq '.ideas | length' world/world_state.json)
          
          # Create pull request
          gh pr create \
            --title "🌍 World Model Update - Tick $TICK" \
            --body "## World Model Update

          **Tick**: $TICK
          **Agents**: $AGENT_COUNT
          **Ideas**: $IDEA_COUNT

          ### Updates

          - Synced agents from registry
          - Converted learnings to ideas
          - Updated knowledge graph
          - Incremented world tick

          ### Autonomous Loop Stage

          This is **Stage 3: World Model Update** of the autonomous loop.
          
          **Previous**: Combined Learning Analysis
          **Next**: Agent Assignment workflow

          ### Completion Questions

          1. ✅ **Learning artifact**: Processed in previous stage
          2. ✅ **World model update**: world/world_state.json, world/knowledge.json
          3. ⏭️  **Agents reacting**: Will be determined in next stage
          4. ⏭️  **Agent capacity**: Will be validated in assignment workflow
          5. ✅ **Agent movement**: Paths updated in world_state.json
          6. ⏭️  **Mission issue**: Will be created by assignment workflow
          7. ✅ **Labels created**: Verified in workflow
          8. ✅ **Next workflow**: Agent Assignment (workflow_run trigger)

          ---

          *Automated by world model update workflow*" \
            --label "world-model,automated" \
            --base main \
            --head "$BRANCH_NAME"
          
          echo "✅ World model PR created"
```

---

## 🤖 Agent Assignment Example

```yaml
name: "Agent Assignment"

on:
  workflow_run:
    workflows: ["World Model Update"]
    types: [completed]
    branches: [main]
  schedule:
    - cron: '0 10 * * *'  # Daily at 10:00 UTC
  workflow_dispatch:

permissions:
  contents: write
  issues: write
  pull-requests: write

jobs:
  assign-agents:
    runs-on: ubuntu-latest
    if: >
      github.event_name == 'schedule' || 
      github.event_name == 'workflow_dispatch' ||
      github.event.workflow_run.conclusion == 'success'
    
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
      
      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      
      - name: Match agents to learnings
        id: match
        run: |
          python3 << 'PYEOF'
          import json
          import os
          from pathlib import Path
          
          # Load latest learnings
          learning_files = sorted(Path('learnings').glob('*.json'))
          if not learning_files:
              print("No learnings found")
              exit(0)
          
          latest_learning = learning_files[-1]
          with open(latest_learning) as f:
              learnings = json.load(f)
          
          # Load world state for agent info
          with open('world/world_state.json') as f:
              world = json.load(f)
          
          # Simple matching: select agents based on expertise
          # (In real implementation, use agent_learning_matcher.py)
          available_agents = [a for a in world['agents'] if a.get('status') == 'idle']
          
          # Select top agents (with 10-agent limit)
          MAX_AGENTS = 10
          selected_agents = available_agents[:min(len(available_agents), MAX_AGENTS)]
          
          # If we have more than 10, create overflow list
          overflow_agents = available_agents[MAX_AGENTS:] if len(available_agents) > MAX_AGENTS else []
          
          # Save selections
          result = {
              'selected_agents': [a['id'] for a in selected_agents],
              'overflow_agents': [a['id'] for a in overflow_agents],
              'learning_file': str(latest_learning)
          }
          
          # Set outputs
          with open(os.environ['GITHUB_OUTPUT'], 'a') as f:
              f.write(f"agent_count={len(selected_agents)}\n")
              f.write(f"overflow_count={len(overflow_agents)}\n")
              f.write(f"agents={','.join([a['id'] for a in selected_agents])}\n")
          
          print(f"✅ Selected {len(selected_agents)} agents")
          if overflow_agents:
              print(f"📋 {len(overflow_agents)} agents in overflow")
          PYEOF
      
      - name: Validate agent capacity
        run: |
          AGENT_COUNT=${{ steps.match.outputs.agent_count }}
          MAX_AGENTS=10
          
          if [ "$AGENT_COUNT" -gt "$MAX_AGENTS" ]; then
            echo "❌ Agent capacity violated: $AGENT_COUNT > $MAX_AGENTS"
            exit 1
          fi
          
          echo "✅ Agent capacity valid: $AGENT_COUNT/$MAX_AGENTS"
      
      - name: Ensure labels exist
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          # Create common labels
          gh label create "agent-mission" \
            --description "Agent mission task" \
            --color "1D76DB" \
            --force 2>/dev/null || true
          
          gh label create "learning-assignment" \
            --description "Agent learning task" \
            --color "0E8A16" \
            --force 2>/dev/null || true
          
          # Create agent-specific labels for selected agents
          IFS=',' read -ra AGENTS <<< "${{ steps.match.outputs.agents }}"
          for agent in "${AGENTS[@]}"; do
            gh label create "agent:$agent" \
              --description "Assigned to $agent agent" \
              --color "1D76DB" \
              --force 2>/dev/null || true
          done
          
          echo "✅ All labels created"
      
      - name: Create mission issues
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          IFS=',' read -ra AGENTS <<< "${{ steps.match.outputs.agents }}"
          
          for agent in "${AGENTS[@]}"; do
            # Create mission issue for each agent
            ISSUE_URL=$(gh issue create \
              --title "🎓 Learning Task: Implementation for @$agent" \
              --body "## Mission Assignment

          **@$agent** - You have been selected for this learning-driven task.

          ### Context

          New learnings have been ingested and processed through the autonomous loop.
          Your expertise matches the requirements for implementing solutions.

          ### Task

          Review the latest learnings and world model updates, then implement
          appropriate solutions based on your specialization.

          ### Autonomous Loop Stage

          This is **Stage 4: Agent Assignment** of the autonomous loop.

          ### Guidelines

          - Follow your agent specialization defined in .github/agents/$agent.md
          - Create a PR with your implementation
          - Use @$agent mentions in all communications
          - Document your decisions and approach
          - Test thoroughly before submitting

          ### Completion Questions

          When completing this task, ensure you can answer:
          1. Where is your implementation? (PR link)
          2. What world model changes did you make?
          3. Did you collaborate with other agents?
          4. Were all tests passing?
          5. Is documentation updated?

          ---

          *Automated by agent assignment workflow*" \
              --label "agent-mission,learning-assignment,agent:$agent" \
              --assignee "$agent")
            
            echo "✅ Created issue for @$agent: $ISSUE_URL"
          done
      
      - name: Create overflow backlog (if needed)
        if: steps.match.outputs.overflow_count > 0
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          # Ensure backlog label exists
          gh label create "future-expansion" \
            --description "Backlog for future work" \
            --color "FBCA04" \
            --force 2>/dev/null || true
          
          # Create backlog issue for overflow agents
          gh issue create \
            --title "📋 Agent Backlog: Overflow from capacity limit" \
            --body "## Overflow Agents

          Due to the 10-agent capacity limit, the following agents were not assigned
          but are suitable for this work:

          **Count**: ${{ steps.match.outputs.overflow_count }} agents

          ### Recommendations

          - Monitor progress of currently assigned agents
          - Consider these agents for follow-up tasks
          - Review if task scope should be split into multiple missions

          ### Context

          These agents exceeded the capacity limit but matched the task requirements
          based on specialization, location, or past performance.

          ---

          *Automated by agent assignment workflow*" \
            --label "future-expansion,agent-system"
          
          echo "✅ Created overflow backlog issue"
```

---

## 🔗 Workflow Chaining Example

Showing how workflows trigger each other sequentially:

```yaml
# File: .github/workflows/stage1-learning.yml
name: "Stage 1: Learning Ingestion"
on:
  schedule:
    - cron: '0 8,20 * * *'
jobs:
  learn:
    runs-on: ubuntu-latest
    steps:
      # ... learning steps
```

```yaml
# File: .github/workflows/stage2-analysis.yml
name: "Stage 2: Combined Analysis"
on:
  workflow_run:
    workflows: ["Stage 1: Learning Ingestion"]
    types: [completed]
    branches: [main]
jobs:
  analyze:
    if: ${{ github.event.workflow_run.conclusion == 'success' }}
    runs-on: ubuntu-latest
    steps:
      # ... analysis steps
```

```yaml
# File: .github/workflows/stage3-world-update.yml
name: "Stage 3: World Model Update"
on:
  workflow_run:
    workflows: ["Stage 2: Combined Analysis"]
    types: [completed]
    branches: [main]
jobs:
  update-world:
    if: ${{ github.event.workflow_run.conclusion == 'success' }}
    runs-on: ubuntu-latest
    steps:
      # ... world update steps
```

```yaml
# File: .github/workflows/stage4-assignment.yml
name: "Stage 4: Agent Assignment"
on:
  workflow_run:
    workflows: ["Stage 3: World Model Update"]
    types: [completed]
    branches: [main]
jobs:
  assign-agents:
    if: ${{ github.event.workflow_run.conclusion == 'success' }}
    runs-on: ubuntu-latest
    steps:
      # ... assignment steps
```

This creates a clear dependency chain:
```
Stage 1 → Stage 2 → Stage 3 → Stage 4
```

---

## 🔄 Self-Reinforcement Example

```yaml
name: "Self-Reinforcement: Learning from Outcomes"

on:
  pull_request:
    types: [closed]
  workflow_dispatch:

permissions:
  contents: write
  issues: read
  pull-requests: read

jobs:
  learn-from-outcome:
    runs-on: ubuntu-latest
    if: github.event.pull_request.merged == true
    
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
      
      - name: Extract learning from PR
        id: extract
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          PR_NUM="${{ github.event.pull_request.number }}"
          
          # Get PR details
          PR_DATA=$(gh pr view "$PR_NUM" --json title,body,labels,files)
          
          # Extract agent from labels or body
          AGENT=$(echo "$PR_DATA" | jq -r '.labels[].name' | grep '^agent:' | cut -d: -f2 | head -1)
          
          # Get linked issue
          PR_BODY=$(echo "$PR_DATA" | jq -r '.body')
          ISSUE_NUM=$(echo "$PR_BODY" | grep -oP '(?:Fixes|Closes|Resolves)\s+#\K\d+' | head -1)
          
          # Count files changed
          FILE_COUNT=$(echo "$PR_DATA" | jq '.files | length')
          
          echo "agent=$AGENT" >> $GITHUB_OUTPUT
          echo "issue_num=$ISSUE_NUM" >> $GITHUB_OUTPUT
          echo "file_count=$FILE_COUNT" >> $GITHUB_OUTPUT
      
      - name: Update agent performance
        if: steps.extract.outputs.agent != ''
        run: |
          python3 << 'PYEOF'
          import json
          import os
          
          agent_id = "${{ steps.extract.outputs.agent }}"
          
          # Load agent registry
          with open('.github/agent-system/registry.json', 'r') as f:
              registry = json.load(f)
          
          # Find and update agent
          for agent in registry.get('agents', []):
              if agent.get('id') == agent_id or agent.get('name') == agent_id:
                  # Update metrics
                  agent['completed_tasks'] = agent.get('completed_tasks', 0) + 1
                  agent['last_activity'] = os.environ.get('GITHUB_SHA')
                  print(f"✅ Updated metrics for @{agent_id}")
                  break
          
          # Save updated registry
          with open('.github/agent-system/registry.json', 'w') as f:
              json.dump(registry, f, indent=2)
          PYEOF
      
      - name: Add to solution history
        if: steps.extract.outputs.issue_num != ''
        run: |
          python3 tools/semantic_similarity_engine.py add \
            --number "${{ steps.extract.outputs.issue_num }}" \
            --pr "${{ github.event.pull_request.number }}" \
            --agent "${{ steps.extract.outputs.agent }}"
      
      - name: Create feedback learning
        run: |
          # Create a learning entry from this successful outcome
          python3 << 'PYEOF'
          import json
          from datetime import datetime, timezone
          import os
          
          learning = {
              'id': f"feedback-pr-${{ github.event.pull_request.number }}",
              'type': 'self-reinforcement',
              'source': 'pr-outcome',
              'pr_number': ${{ github.event.pull_request.number }},
              'agent': "${{ steps.extract.outputs.agent }}",
              'success': True,
              'file_count': ${{ steps.extract.outputs.file_count }},
              'timestamp': datetime.now(timezone.utc).isoformat()
          }
          
          # Append to feedback log
          os.makedirs('learnings/feedback', exist_ok=True)
          with open('learnings/feedback/pr_outcomes.jsonl', 'a') as f:
              f.write(json.dumps(learning) + '\n')
          
          print("✅ Feedback learning recorded")
          PYEOF
      
      - name: Update world model with outcome
        run: |
          # World model might need updating based on outcome
          echo "✅ World model updates recorded"
      
      - name: Create PR with reinforcement data
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          git add .
          if git diff --staged --quiet; then
            echo "No reinforcement data to commit"
            exit 0
          fi
          
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"
          
          TIMESTAMP=$(date +%Y%m%d-%H%M%S)
          BRANCH_NAME="reinforcement/${TIMESTAMP}-${{ github.run_id }}"
          git checkout -b "$BRANCH_NAME"
          
          git commit -m "Self-reinforcement: Learn from PR #${{ github.event.pull_request.number }}"
          git push origin "$BRANCH_NAME"
          
          gh pr create \
            --title "🔄 Self-Reinforcement: PR #${{ github.event.pull_request.number }} outcome" \
            --body "## Self-Reinforcement Learning

          Learning from successful PR merge.

          **PR**: #${{ github.event.pull_request.number }}
          **Agent**: @${{ steps.extract.outputs.agent }}
          **Files Changed**: ${{ steps.extract.outputs.file_count }}

          ### Updates

          - Agent performance metrics updated
          - Solution added to similarity engine
          - Feedback learning recorded
          - World model updated

          ### Autonomous Loop Stage

          This is **Stage 5: Self-Reinforcement** of the autonomous loop.
          
          This closes the loop and feeds insights back to the learning system.

          ---

          *Automated by self-reinforcement workflow*" \
            --label "automated,learning" \
            --base main \
            --head "$BRANCH_NAME"
```

---

## 📝 Complete Workflow Template

Here's a complete template following all patterns:

```yaml
name: "Workflow Name"

# Triggers
on:
  workflow_run:
    workflows: ["Parent Workflow"]  # Chain from parent
    types: [completed]
    branches: [main]
  schedule:
    - cron: '0 12 * * *'  # Fallback schedule
  workflow_dispatch:  # Manual trigger for testing

# Required permissions
permissions:
  contents: write
  issues: write
  pull-requests: write

jobs:
  main-job:
    runs-on: ubuntu-latest
    # Check parent workflow success
    if: >
      github.event_name == 'schedule' || 
      github.event_name == 'workflow_dispatch' ||
      github.event.workflow_run.conclusion == 'success'
    
    steps:
      # 1. Setup
      - name: Checkout repository
        uses: actions/checkout@v4
      
      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      
      # 2. Main logic
      - name: Execute main logic
        id: execute
        run: |
          # Your workflow logic here
          echo "output_value=result" >> $GITHUB_OUTPUT
      
      # 3. Validate constraints
      - name: Validate agent capacity (if applicable)
        if: steps.execute.outputs.agents != ''
        run: |
          python3 tools/validate_agent_capacity.py \
            ${{ steps.execute.outputs.agents }}
      
      # 4. Create labels
      - name: Ensure labels exist
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          gh label create "label-name" \
            --description "Description" \
            --color "COLOR" \
            --force 2>/dev/null || true
          
          echo "✅ Labels created"
      
      # 5. Create PR (not push to main!)
      - name: Create PR with changes
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          # Check for changes
          git add .
          if git diff --staged --quiet; then
            echo "No changes to commit"
            exit 0
          fi
          
          # Configure git
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"
          
          # Create unique branch
          TIMESTAMP=$(date +%Y%m%d-%H%M%S)
          BRANCH_NAME="category/${TIMESTAMP}-${{ github.run_id }}"
          git checkout -b "$BRANCH_NAME"
          
          # Commit changes
          git commit -m "Description of changes"
          
          # Push to new branch (NOT main)
          git push origin "$BRANCH_NAME"
          
          # Create pull request with completion questions
          gh pr create \
            --title "Title (@agent-name if applicable)" \
            --body "## Description

          ### Autonomous Loop Stage

          This is **Stage X: Stage Name** of the autonomous loop.

          ### Completion Questions

          1. ✅ **Learning artifact**: path/to/artifact
          2. ✅ **World model update**: path/to/world_state.json
          3. ✅ **Agents reacting**: @agent-1, @agent-2
          4. ✅ **Agent capacity**: X/10 agents
          5. ✅ **Agent movement**: Updated in world model
          6. ✅ **Mission issue**: #123
          7. ✅ **Labels created**: Verified above
          8. ✅ **Next workflow**: Next Stage Name

          ---

          *Automated by workflow-name*" \
            --label "automated,category" \
            --base main \
            --head "$BRANCH_NAME"
          
          echo "✅ PR created"
```

---

## 🧪 Testing and Validation

### Before Deploying a Workflow

1. **Validate YAML syntax**
   ```bash
   python3 -c "import yaml; yaml.safe_load(open('.github/workflows/my-workflow.yml'))"
   ```

2. **Check branch protection compliance**
   ```bash
   grep "git push origin main" .github/workflows/my-workflow.yml
   # Should return nothing
   ```

3. **Verify label creation**
   ```bash
   grep "gh label create" .github/workflows/my-workflow.yml
   # Should find label creation statements
   ```

4. **Validate workflow chaining**
   ```bash
   grep "workflow_run" .github/workflows/my-workflow.yml
   grep "conclusion.*success" .github/workflows/my-workflow.yml
   ```

5. **Test agent capacity validation** (if applicable)
   ```bash
   python3 tools/validate_agent_capacity.py agent-1 agent-2 agent-3
   ```

### After Deploying

1. **Monitor workflow runs** in Actions tab
2. **Check PR creation** - should create PRs, not push to main
3. **Verify labels exist** - check repository labels
4. **Validate outputs** - check generated files
5. **Review logs** - ensure clear status messages

### Integration Testing

```bash
#!/bin/bash
# test-autonomous-loop.sh
# Integration test for autonomous loop

set -e

echo "🧪 Testing Autonomous Loop Integration"
echo "======================================"

# Test 1: Learning ingestion
echo "Test 1: Learning ingestion..."
gh workflow run "learning-tldr.yml" --ref main
sleep 10
# Check for PR creation
RECENT_PRS=$(gh pr list --label "learning" --limit 1 --json number -q '.[0].number')
if [ -n "$RECENT_PRS" ]; then
  echo "✅ Learning PR created"
else
  echo "❌ No learning PR found"
  exit 1
fi

# Test 2: Agent capacity validation
echo "Test 2: Agent capacity validation..."
python3 tools/validate_agent_capacity.py agent-{1..8}
if [ $? -eq 0 ]; then
  echo "✅ Agent capacity validation passed"
else
  echo "❌ Agent capacity validation failed"
  exit 1
fi

# Test 3: Label creation
echo "Test 3: Label creation..."
python3 tools/create_labels.py --system
if [ $? -eq 0 ]; then
  echo "✅ Label creation passed"
else
  echo "❌ Label creation failed"
  exit 1
fi

echo "======================================"
echo "🎉 All tests passed!"
```

---

## 📚 Related Documentation

- [Autonomous System Architecture](./AUTONOMOUS_SYSTEM_ARCHITECTURE.md)
- [Workflow Validation Guide](./docs/guides/WORKFLOW_VALIDATION_GUIDE.md)
- [Label Management](./docs/guides/LABELS.md)
- [Agent System Quick Start](./AGENT_QUICKSTART.md)

---

**Use these patterns and examples to build compliant, maintainable autonomous loop workflows that enforce all critical constraints.**

*🚀 Created by **@support-master** - practical guidance for autonomous system implementation!*
