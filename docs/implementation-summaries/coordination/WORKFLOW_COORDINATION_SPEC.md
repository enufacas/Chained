# Workflow-Driven Coordination: Implementation Specification

**Project:** Automated Multi-Agent Coordination via GitHub Actions  
**Lead:** @coordinate-wizard  
**Support:** @meta-coordinator  
**Target:** Issue #233 - Meta-agent coordination enhancement

---

## Overview

This specification details how to implement workflow-driven coordination that automatically:
1. Detects complex issues requiring multiple agents
2. Analyzes complexity and creates coordination plans
3. Spawns sub-issues with agent assignments
4. Tracks progress and aggregates results

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    GitHub Issue Created                     │
│                                                             │
│   User adds label: "coordination-needed"                    │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│         Workflow: auto-coordinate-agents.yml                │
│                                                             │
│  Step 1: Analyze Complexity                                 │
│  ├─ Parse issue body                                        │
│  ├─ Detect required specializations                         │
│  └─ Determine: simple | moderate | complex | highly complex │
│                                                             │
│  Step 2: Create Coordination Plan                           │
│  ├─ Decompose into sub-tasks                                │
│  ├─ Identify dependencies                                   │
│  ├─ Select agents for each sub-task                         │
│  └─ Determine execution order                               │
│                                                             │
│  Step 3: Spawn Sub-Issues                                   │
│  ├─ Create issue for each sub-task                          │
│  ├─ Add agent assignment (@agent-name)                      │
│  ├─ Link to parent issue                                    │
│  └─ Add coordination metadata                               │
│                                                             │
│  Step 4: Update Parent Issue                                │
│  ├─ Comment with coordination plan                          │
│  ├─ Add tracking section                                    │
│  └─ Link to all sub-issues                                  │
└─────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              Sub-Issues Progress Tracking                   │
│                                                             │
│  Workflow: track-coordination-progress.yml                  │
│                                                             │
│  Triggers:                                                  │
│  - On sub-issue labeled "coordination-subtask"              │
│  - On sub-issue closed                                      │
│  - On PR merged that references sub-issue                   │
│                                                             │
│  Actions:                                                   │
│  ├─ Update parent issue progress section                    │
│  ├─ Check if all sub-tasks complete                         │
│  └─ If complete: mark coordination done                     │
└─────────────────────────────────────────────────────────────┘
```

---

## Workflow 1: Auto-Coordinate Agents

**File:** `.github/workflows/auto-coordinate-agents.yml`

### Trigger
```yaml
on:
  issues:
    types: [labeled, opened, edited]
  workflow_dispatch:
    inputs:
      issue_number:
        description: 'Issue number to coordinate'
        required: true
        type: number
```

### Jobs

#### Job 1: Analyze
```yaml
analyze:
  if: contains(github.event.issue.labels.*.name, 'coordination-needed')
  runs-on: ubuntu-latest
  outputs:
    complexity: ${{ steps.analyze.outputs.complexity }}
    should_coordinate: ${{ steps.analyze.outputs.should_coordinate }}
  
  steps:
    - name: Checkout
      uses: actions/checkout@v4
    
    - name: Analyze task complexity
      id: analyze
      run: |
        complexity=$(python3 tools/meta_agent_coordinator.py analyze \
          --task-id "${{ github.event.issue.number }}" \
          --description "${{ github.event.issue.body }}" | jq -r '.complexity')
        
        should_coordinate="false"
        if [[ "$complexity" == "complex" ]] || [[ "$complexity" == "highly_complex" ]]; then
          should_coordinate="true"
        fi
        
        echo "complexity=$complexity" >> $GITHUB_OUTPUT
        echo "should_coordinate=$should_coordinate" >> $GITHUB_OUTPUT
```

#### Job 2: Coordinate
```yaml
coordinate:
  needs: analyze
  if: needs.analyze.outputs.should_coordinate == 'true'
  runs-on: ubuntu-latest
  
  steps:
    - name: Checkout
      uses: actions/checkout@v4
    
    - name: Create coordination plan
      id: plan
      run: |
        python3 tools/meta_agent_coordinator.py coordinate \
          --task-id "${{ github.event.issue.number }}" \
          --description "${{ github.event.issue.body }}" \
          --output coordination-plan.json
        
        # Store plan for next step
        echo "plan_file=coordination-plan.json" >> $GITHUB_OUTPUT
    
    - name: Create sub-issues
      env:
        GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      run: |
        # Parse coordination plan
        plan=$(cat coordination-plan.json)
        
        # Extract sub-tasks
        subtasks=$(echo "$plan" | jq -r '.sub_tasks[]')
        
        # Create issue for each sub-task
        for subtask in $(echo "$subtasks" | jq -r '.id'); do
          description=$(echo "$plan" | jq -r ".sub_tasks[] | select(.id == \"$subtask\") | .description")
          agent=$(echo "$plan" | jq -r ".sub_tasks[] | select(.id == \"$subtask\") | .assigned_agent")
          
          # Create sub-issue
          sub_issue=$(gh issue create \
            --title "[$subtask] $description" \
            --body "**Coordination Sub-Task**\n\nParent Issue: #${{ github.event.issue.number }}\nAssigned Agent: @$agent\n\n$description" \
            --label "coordination-subtask,agent:$agent" \
            --assignee "$agent")
          
          echo "Created sub-issue: $sub_issue"
        done
    
    - name: Update parent issue
      env:
        GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      run: |
        # Create coordination summary
        plan=$(cat coordination-plan.json)
        complexity=$(echo "$plan" | jq -r '.complexity')
        subtask_count=$(echo "$plan" | jq -r '.sub_tasks | length')
        
        # Comment on parent issue
        gh issue comment ${{ github.event.issue.number }} --body "
        ## 🎯 Coordination Plan Created
        
        **Complexity:** $complexity
        **Sub-tasks:** $subtask_count
        **Coordination ID:** $(echo $plan | jq -r '.coordination_id')
        
        ### Sub-Tasks
        
        $(echo "$plan" | jq -r '.sub_tasks[] | "- [ ] **\(.id)**: \(.description) (@\(.assigned_agent))"')
        
        ### Execution Order
        
        $(echo "$plan" | jq -r '.execution_order[] | "1. \(.)"')
        
        ---
        
        **Coordination Progress:** 0 / $subtask_count complete
        
        *This issue is being coordinated by @meta-coordinator. Sub-issues will be created for each task.*
        "
```

---

## Workflow 2: Track Coordination Progress

**File:** `.github/workflows/track-coordination-progress.yml`

### Trigger
```yaml
on:
  issues:
    types: [closed, labeled]
  pull_request:
    types: [closed]
```

### Jobs

#### Job: Update Progress
```yaml
update-progress:
  if: contains(github.event.issue.labels.*.name, 'coordination-subtask')
  runs-on: ubuntu-latest
  
  steps:
    - name: Checkout
      uses: actions/checkout@v4
    
    - name: Find parent issue
      id: parent
      env:
        GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      run: |
        # Extract parent issue from body
        parent_num=$(gh issue view ${{ github.event.issue.number }} --json body --jq '.body' | grep -oP 'Parent Issue: #\K\d+')
        echo "parent_number=$parent_num" >> $GITHUB_OUTPUT
    
    - name: Check if coordination complete
      id: check
      env:
        GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      run: |
        parent_num=${{ steps.parent.outputs.parent_number }}
        
        # Get all sub-issues
        sub_issues=$(gh issue list --label "coordination-subtask" --search "Parent Issue: #$parent_num" --json number,state)
        
        total=$(echo "$sub_issues" | jq 'length')
        closed=$(echo "$sub_issues" | jq '[.[] | select(.state == "CLOSED")] | length')
        
        echo "total=$total" >> $GITHUB_OUTPUT
        echo "closed=$closed" >> $GITHUB_OUTPUT
        
        if [[ "$total" == "$closed" ]]; then
          echo "complete=true" >> $GITHUB_OUTPUT
        else
          echo "complete=false" >> $GITHUB_OUTPUT
        fi
    
    - name: Update parent issue progress
      env:
        GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      run: |
        parent_num=${{ steps.parent.outputs.parent_number }}
        closed=${{ steps.check.outputs.closed }}
        total=${{ steps.check.outputs.total }}
        
        # Find and update progress comment
        gh issue comment $parent_num --body "
        ## 📊 Coordination Progress Update
        
        **Progress:** $closed / $total sub-tasks complete
        **Last Update:** $(date -u +"%Y-%m-%d %H:%M:%S UTC")
        
        $( [[ ${{ steps.check.outputs.complete }} == "true" ]] && echo "✅ **All sub-tasks completed!**" || echo "⏳ Coordination in progress..." )
        "
    
    - name: Complete coordination
      if: steps.check.outputs.complete == 'true'
      env:
        GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      run: |
        parent_num=${{ steps.parent.outputs.parent_number }}
        
        # Add completion comment
        gh issue comment $parent_num --body "
        ## 🎉 Coordination Complete!
        
        All sub-tasks have been completed by the coordinated agents.
        
        **Next Steps:**
        1. Review the work from all sub-tasks
        2. Ensure integration is correct
        3. Close this coordination issue
        
        **Coordinated by:** @meta-coordinator
        **Completed:** $(date -u +"%Y-%m-%d %H:%M:%S UTC")
        "
        
        # Remove coordination-needed label
        gh issue edit $parent_num --remove-label "coordination-needed"
        gh issue edit $parent_num --add-label "coordination-complete"
```

---

## Helper Script: Workflow Coordination Utilities

**File:** `tools/workflow_coordination_helper.py`

```python
#!/usr/bin/env python3
"""
Workflow Coordination Helper

Utilities for workflow-driven multi-agent coordination.
Provides GitHub Actions-friendly wrappers around meta_agent_coordinator.py.
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Any

sys.path.insert(0, str(Path(__file__).parent))
from meta_agent_coordinator import MetaAgentCoordinator

class WorkflowCoordinationHelper:
    """Helper for workflow-based coordination"""
    
    def __init__(self):
        self.coordinator = MetaAgentCoordinator()
    
    def analyze_for_workflow(self, issue_number: int, issue_body: str) -> Dict[str, Any]:
        """
        Analyze issue and return workflow-friendly output.
        
        Returns:
            {
                'complexity': 'simple|moderate|complex|highly_complex',
                'should_coordinate': bool,
                'required_specializations': list,
                'estimated_agents': int
            }
        """
        complexity = self.coordinator.analyze_task_complexity(issue_body)
        
        return {
            'complexity': complexity.value,
            'should_coordinate': complexity.value in ['complex', 'highly_complex'],
            'required_specializations': self.coordinator._identify_required_specializations(issue_body),
            'estimated_agents': len(self.coordinator._identify_required_specializations(issue_body))
        }
    
    def create_coordination_plan_json(self, issue_number: int, issue_body: str, 
                                     output_file: str = 'coordination-plan.json') -> str:
        """
        Create coordination plan and save to JSON file for workflow consumption.
        
        Returns:
            Path to created JSON file
        """
        coordination = self.coordinator.create_coordination(
            task_id=f"issue-{issue_number}",
            task_description=issue_body
        )
        
        plan_dict = coordination['plan'].to_dict()
        plan_dict['issue_number'] = issue_number
        plan_dict['coordination_id'] = coordination['coordination_id']
        plan_dict['created_at'] = coordination['created_at']
        
        with open(output_file, 'w') as f:
            json.dump(plan_dict, f, indent=2)
        
        return output_file
    
    def format_sub_issue_body(self, parent_issue: int, subtask: Dict[str, Any]) -> str:
        """
        Format sub-issue body with coordination metadata.
        """
        body = f"""## 🎯 Coordination Sub-Task

**Parent Issue:** #{parent_issue}
**Sub-Task ID:** {subtask['id']}
**Assigned Agent:** @{subtask['assigned_agent']}

### Description

{subtask['description']}

### Dependencies

"""
        
        if subtask['dependencies']:
            for dep in subtask['dependencies']:
                body += f"- Depends on: {dep}\n"
        else:
            body += "- No dependencies\n"
        
        body += f"""
### Completion Criteria

"""
        
        for criteria in subtask['completion_criteria']:
            body += f"- [ ] {criteria}\n"
        
        body += f"""
### Coordination Metadata

- **Estimated Effort:** {subtask['estimated_effort']}
- **Priority:** {subtask['priority']}
- **Status:** {subtask['status']}

---

*This is a coordination sub-task. When complete, the parent issue will be updated automatically.*
"""
        
        return body

def main():
    """CLI for workflow coordination helper"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Workflow Coordination Helper')
    parser.add_argument('command', choices=['analyze', 'plan', 'format-subtask'])
    parser.add_argument('--issue-number', type=int, required=True)
    parser.add_argument('--issue-body', type=str, required=True)
    parser.add_argument('--output', type=str, default='coordination-plan.json')
    parser.add_argument('--subtask-json', type=str, help='Subtask JSON for formatting')
    
    args = parser.parse_args()
    
    helper = WorkflowCoordinationHelper()
    
    if args.command == 'analyze':
        result = helper.analyze_for_workflow(args.issue_number, args.issue_body)
        print(json.dumps(result, indent=2))
    
    elif args.command == 'plan':
        output_file = helper.create_coordination_plan_json(
            args.issue_number,
            args.issue_body,
            args.output
        )
        print(f"Created: {output_file}")
    
    elif args.command == 'format-subtask':
        with open(args.subtask_json) as f:
            subtask = json.load(f)
        body = helper.format_sub_issue_body(args.issue_number, subtask)
        print(body)

if __name__ == '__main__':
    main()
```

---

## Testing Strategy

### Test Case 1: Simple Issue (No Coordination)
```markdown
**Issue:** Fix typo in README

**Expected:** 
- Workflow analyzes: complexity = "simple"
- No coordination triggered
- Normal agent assignment continues
```

### Test Case 2: Complex Issue (Coordination Triggered)
```markdown
**Issue:** Build new authentication system

**Expected:**
- Workflow analyzes: complexity = "complex"
- Coordination triggered
- Sub-issues created for:
  - API design (@engineer-master)
  - Security review (@secure-specialist)
  - Implementation (@engineer-wizard)
  - Testing (@assert-specialist)
  - Documentation (@document-ninja)
- Parent issue updated with plan
- Progress tracked as sub-issues complete
```

### Test Case 3: Highly Complex Issue (Parallel Coordination)
```markdown
**Issue:** Comprehensive test coverage for entire system

**Expected:**
- Workflow analyzes: complexity = "highly_complex"
- Coordination triggered
- Sub-issues created (parallel execution):
  - Unit tests (@assert-specialist)
  - Integration tests (@validator-pro)
  - Edge cases (@edge-cases-pro)
  - Performance tests (@accelerate-master)
- All can run in parallel
- Results aggregated when all complete
```

---

## Success Criteria

### Functional Requirements
- ✅ Workflow triggers on `coordination-needed` label
- ✅ Complexity analysis completes in <10 seconds
- ✅ Sub-issues created with proper agent assignments
- ✅ Parent issue updated with plan and progress
- ✅ Progress tracked as sub-issues complete
- ✅ Coordination marked complete when all done

### Performance Requirements
- ✅ Coordination plan creation: <30 seconds
- ✅ Sub-issue creation: <5 seconds per issue
- ✅ Progress update: <10 seconds

### Quality Requirements
- ✅ Agent selection accuracy: >90%
- ✅ Sub-task decomposition quality: High (manual review)
- ✅ Coordination completion rate: >80%

---

## Documentation Requirements

### User Documentation
- `docs/WORKFLOW_COORDINATION.md` - How to use workflow coordination
- `docs/COORDINATION_EXAMPLES.md` - Real-world examples
- Update `README.md` with coordination capabilities

### Developer Documentation
- `tools/WORKFLOW_COORDINATION_HELPER_README.md` - Helper API docs
- Update `.github/copilot-instructions.md` with coordination info
- Add examples to `docs/guides/`

---

## Next Steps for @coordinate-wizard

1. **Review this specification** - Feedback welcome!
2. **Create workflow skeleton** - Start with basic structure
3. **Test with simple case** - Verify workflow triggers
4. **Build out coordination logic** - Add sub-issue creation
5. **Add progress tracking** - Second workflow
6. **Test end-to-end** - Full coordination scenario
7. **Document** - User and developer docs
8. **Launch** - Beta test with real issues

---

**Questions or suggestions?** Let's discuss on issue #233!

**@meta-coordinator** (ready to support your implementation! 🎯)
