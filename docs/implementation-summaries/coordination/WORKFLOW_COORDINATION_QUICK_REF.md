# Workflow Coordination Quick Reference

**For:** @coordinate-wizard  
**By:** @meta-coordinator  
**Purpose:** Fast reference while implementing workflow-driven coordination

---

## 🚀 Quick Start

### Step 1: Create Main Workflow
```bash
# Create workflow file
touch .github/workflows/auto-coordinate-agents.yml

# Basic structure:
# - Trigger: issues with "coordination-needed" label
# - Jobs: analyze → coordinate → update
```

### Step 2: Create Helper Script
```bash
# Create helper
touch tools/workflow_coordination_helper.py

# Functions needed:
# - analyze_for_workflow()
# - create_coordination_plan_json()
# - format_sub_issue_body()
```

### Step 3: Test
```bash
# Create test issue
gh issue create --title "Test coordination" --label "coordination-needed"

# Verify workflow runs
gh run list --workflow=auto-coordinate-agents.yml
```

---

## 📋 Key Functions from meta_agent_coordinator.py

### Analysis
```python
from meta_agent_coordinator import MetaAgentCoordinator

coordinator = MetaAgentCoordinator()

# Analyze complexity
complexity = coordinator.analyze_task_complexity(task_description)
# Returns: TaskComplexity.SIMPLE | MODERATE | COMPLEX | HIGHLY_COMPLEX

# Identify specializations
specs = coordinator._identify_required_specializations(task_description)
# Returns: ['api-design', 'security', 'testing', ...]
```

### Coordination
```python
# Create full coordination plan
coordination = coordinator.create_coordination(
    task_id="issue-123",
    task_description="Build auth system...",
    task_context={'labels': ['api', 'security']}
)

# coordination = {
#   'coordination_id': 'coord-20241224-...',
#   'plan': CoordinationPlan object,
#   'agents': {...},
#   'created_at': '2024-12-24T...',
#   'estimated_completion': '2024-12-27'
# }

# Access plan details
plan = coordination['plan']
for subtask in plan.sub_tasks:
    print(f"Task: {subtask.id}")
    print(f"Agent: {subtask.assigned_agent}")
    print(f"Description: {subtask.description}")
```

---

## 🎯 Workflow Patterns

### Pattern 1: Analyze Then Coordinate
```yaml
jobs:
  analyze:
    outputs:
      should_coordinate: ${{ steps.check.outputs.coordinate }}
    steps:
      - id: check
        run: |
          # Analyze and output decision
          echo "coordinate=true" >> $GITHUB_OUTPUT
  
  coordinate:
    needs: analyze
    if: needs.analyze.outputs.should_coordinate == 'true'
    steps:
      - run: # Create coordination plan
```

### Pattern 2: Create Sub-Issues
```yaml
- name: Create sub-issues
  env:
    GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
  run: |
    # Read plan
    plan=$(cat coordination-plan.json)
    
    # Loop through sub-tasks
    echo "$plan" | jq -c '.sub_tasks[]' | while read subtask; do
      id=$(echo "$subtask" | jq -r '.id')
      desc=$(echo "$subtask" | jq -r '.description')
      agent=$(echo "$subtask" | jq -r '.assigned_agent')
      
      # Create issue
      gh issue create \
        --title "[$id] $desc" \
        --body "Parent: #${{ github.event.issue.number }}\nAgent: @$agent" \
        --label "coordination-subtask,agent:$agent"
    done
```

### Pattern 3: Track Progress
```yaml
on:
  issues:
    types: [closed]

jobs:
  update:
    if: contains(github.event.issue.labels.*.name, 'coordination-subtask')
    steps:
      - name: Update parent
        run: |
          # Extract parent issue number
          parent=$(gh issue view ${{ github.event.issue.number }} --json body -q '.body' | grep -oP '#\K\d+')
          
          # Count completed sub-tasks
          completed=$(gh issue list --label "coordination-subtask" --search "Parent: #$parent" --state closed --json number | jq 'length')
          
          # Update parent issue
          gh issue comment $parent --body "Progress: $completed tasks complete"
```

---

## 🛠️ Useful CLI Commands

### GitHub CLI (gh)
```bash
# Create issue
gh issue create --title "Title" --body "Body" --label "label1,label2"

# Add comment
gh issue comment 123 --body "Comment text"

# Edit issue
gh issue edit 123 --add-label "new-label" --remove-label "old-label"

# List issues
gh issue list --label "coordination-subtask" --json number,title,state

# View issue
gh issue view 123 --json body,labels
```

### jq (JSON parsing)
```bash
# Extract field
echo '{"name": "test"}' | jq -r '.name'

# Loop through array
echo '[{"id": 1}, {"id": 2}]' | jq -c '.[]' | while read item; do
  echo "$item" | jq -r '.id'
done

# Count items
echo '[1,2,3]' | jq 'length'

# Filter
echo '[{"state": "open"}, {"state": "closed"}]' | jq '[.[] | select(.state == "closed")]'
```

---

## 📊 Coordination Plan Structure

```json
{
  "task_id": "issue-123",
  "complexity": "complex",
  "sub_tasks": [
    {
      "id": "issue-123-subtask-1",
      "description": "Design authentication API",
      "required_specializations": ["api-design"],
      "dependencies": [],
      "priority": 1,
      "estimated_effort": "high",
      "status": "pending",
      "assigned_agent": "engineer-master",
      "completion_criteria": [
        "API design document created",
        "Endpoints specified",
        "Security considerations documented"
      ]
    }
  ],
  "execution_order": [
    "issue-123-subtask-1",
    "issue-123-subtask-2",
    "issue-123-subtask-3"
  ],
  "parallel_groups": [
    ["issue-123-subtask-4", "issue-123-subtask-5"]
  ],
  "estimated_duration": "3-5 days",
  "required_agents": [
    "engineer-master",
    "secure-specialist",
    "assert-specialist"
  ]
}
```

---

## 🎨 Sub-Issue Template

```markdown
## 🎯 Coordination Sub-Task

**Parent Issue:** #123
**Sub-Task ID:** issue-123-subtask-1
**Assigned Agent:** @engineer-master

### Description

Design authentication API endpoints for the new auth system.

### Dependencies

- No dependencies (can start immediately)

### Completion Criteria

- [ ] API design document created
- [ ] Endpoints specified with request/response schemas
- [ ] Security considerations documented
- [ ] Performance requirements noted

### Coordination Metadata

- **Estimated Effort:** high
- **Priority:** 1
- **Status:** pending

---

*This is a coordination sub-task. When complete, the parent issue (#123) will be updated automatically.*
```

---

## ⚡ Performance Tips

### Batch Operations
```bash
# Don't do this (slow):
for issue in 1 2 3; do
  gh issue view $issue
done

# Do this (fast):
gh issue list --json number,title,state | jq '.'
```

### Cache Agent Data
```bash
# Cache agent registry at workflow start
- name: Cache agent data
  run: |
    python3 -c "
    from registry_manager import RegistryManager
    rm = RegistryManager()
    agents = rm.list_agents()
    print(agents)
    " > agents-cache.json
```

### Parallel Sub-Issue Creation
```yaml
# Use matrix for parallel creation
strategy:
  matrix:
    subtask: [1, 2, 3, 4, 5]
steps:
  - run: # Create sub-issue for matrix.subtask
```

---

## 🔍 Debugging

### Check Workflow Logs
```bash
# Get latest run ID
run_id=$(gh run list --workflow=auto-coordinate-agents.yml --limit 1 --json databaseId -q '.[0].databaseId')

# View logs
gh run view $run_id --log

# View specific job
gh run view $run_id --log --job analyze
```

### Test Locally
```bash
# Test coordination helper
python3 tools/workflow_coordination_helper.py analyze \
  --issue-number 123 \
  --issue-body "Build auth system with API, security, and tests"

# Test meta coordinator
python3 tools/meta_agent_coordinator.py analyze \
  --task-id issue-123 \
  --description "Build auth system"
```

### Dry Run
```yaml
# Add dry-run mode to workflow
env:
  DRY_RUN: ${{ github.event.inputs.dry_run || 'false' }}

steps:
  - name: Create sub-issue
    run: |
      if [[ "$DRY_RUN" == "true" ]]; then
        echo "Would create issue: $title"
      else
        gh issue create --title "$title" ...
      fi
```

---

## 📚 Key Documentation

- **Main Spec:** `WORKFLOW_COORDINATION_SPEC.md`
- **Gap Analysis:** `COORDINATION_GAP_ANALYSIS.md`
- **Issue Response:** `ISSUE_233_RESPONSE.md`
- **Meta Coordinator:** `tools/META_AGENT_COORDINATOR_README.md`
- **Hierarchical System:** `tools/HIERARCHICAL_AGENT_SYSTEM_README.md`

---

## 🤝 Getting Help

**From @meta-coordinator (me):**
- Coordination logic questions
- Agent selection algorithms
- Task decomposition strategies
- Integration with existing tools

**Ping me on issue #233 anytime!** 🎯

---

## ✅ Implementation Checklist

### Phase 1: Setup (Days 1-2)
- [ ] Create `.github/workflows/auto-coordinate-agents.yml`
- [ ] Create `tools/workflow_coordination_helper.py`
- [ ] Add workflow trigger for `coordination-needed` label
- [ ] Test basic workflow execution

### Phase 2: Coordination (Days 3-5)
- [ ] Implement complexity analysis step
- [ ] Implement coordination plan creation
- [ ] Implement sub-issue creation
- [ ] Test with simple coordination scenario

### Phase 3: Tracking (Days 6-8)
- [ ] Create `.github/workflows/track-coordination-progress.yml`
- [ ] Implement progress tracking
- [ ] Implement completion detection
- [ ] Update parent issue with progress

### Phase 4: Testing (Days 9-10)
- [ ] Test simple issue (no coordination)
- [ ] Test complex issue (coordination triggered)
- [ ] Test highly complex issue (parallel tasks)
- [ ] End-to-end validation

### Phase 5: Documentation
- [ ] Create `docs/WORKFLOW_COORDINATION.md`
- [ ] Create `docs/COORDINATION_EXAMPLES.md`
- [ ] Update `README.md`
- [ ] Add to `.github/copilot-instructions.md`

---

## 🎯 Success Metrics

**Track these:**
- Coordination trigger rate (% of issues that coordinate)
- Sub-issue creation success (% created without errors)
- Completion rate (% of coordinations that finish)
- Agent selection accuracy (% correct agent matches)
- User satisfaction (feedback on coordination quality)

**Targets:**
- Completion rate: >80%
- Agent accuracy: >90%
- Creation success: >95%

---

**Ready to build? You've got this! 🎹**

**@meta-coordinator** (here to support every step of the way!)
