# Consolidated Workflows Documentation

**@workflows-tech-lead** has organized 16 workflows into 5 consolidated mega-workflows to improve maintainability and reduce complexity.

## Overview

Instead of having many small workflows that are difficult to manage, we now have larger workflows with named stages that can be triggered independently.

## Benefits

1. **Easier Maintenance**: Related functionality is grouped together
2. **Better Organization**: Clear categorization by function
3. **Flexible Execution**: Each stage can be triggered independently
4. **Reduced Clutter**: Fewer workflow files to manage
5. **Preserved Functionality**: All original triggers and features maintained

## Consolidated Workflows

### 1. demos-and-experiments.yml

**Purpose**: Development experiments and proof-of-concepts

**Original Workflows Consolidated**:
- `nl-to-code-demo.yml` → Stage: `nl-to-code-translation`
- `tech-lead-review-poc.yml` → Stage: `tech-lead-review`

**Triggers**:
- Manual dispatch with stage selection
- Issue labeled `nl-to-code-demo`
- Pull request with `tech-lead-review` label

**How to Use**:
```bash
# Trigger specific stage manually
gh workflow run demos-and-experiments.yml \
  -f stage=nl-to-code-translation

# Or use the GitHub UI:
# Actions → demos-and-experiments → Run workflow → Select stage
```

---

### 2. ab-testing-system.yml

**Purpose**: A/B testing and experimentation system

**Original Workflows Consolidated**:
- `ab-testing-demo.yml` → Stage: `ab-testing-demo`
- `ab-testing-manager.yml` → Stage: `experiment-manager`
- `autonomous-ab-testing.yml` → Stage: `autonomous-orchestrator`

**Triggers**:
- Demo: Every 6 hours
- Manager: Daily at 8 AM UTC
- Autonomous: Twice daily (6 AM, 6 PM UTC)
- Manual dispatch with stage selection

**How to Use**:
```bash
# Run demo stage with specific action
gh workflow run ab-testing-system.yml \
  -f stage=ab-testing-demo \
  -f action=create_experiment

# Run autonomous orchestrator
gh workflow run ab-testing-system.yml \
  -f stage=autonomous-orchestrator \
  -f action=evaluate_experiments
```

**Available Actions**:
- Demo: `create_experiment`, `run_experiment`, `analyze_results`
- Manager: `list_experiments`, `promote_winner`, `archive_experiment`
- Autonomous: `create_hypothesis`, `run_experiments`, `evaluate_experiments`, `auto_promote`

---

### 3. agent-spawning.yml

**Purpose**: Agent creation and management

**Original Workflows Consolidated**:
- `agent-spawner.yml` → Stage: `standard-spawner`
- `learning-based-agent-spawner.yml` → Stage: `learning-based-spawner`
- `multi-agent-spawner.yml` → Stage: `multi-spawner`
- `workload-subagent-spawner.yml` → Stage: `workload-spawner`

**Triggers**:
- Standard spawner: Every 3 hours
- Manual dispatch with stage selection

**How to Use**:
```bash
# Spawn agents based on learning data
gh workflow run agent-spawning.yml \
  -f stage=learning-based-spawner \
  -f spawn_count=3

# Spawn workload-based subagents
gh workflow run agent-spawning.yml \
  -f stage=workload-spawner \
  -f mode=intelligent \
  -f max_spawns=5
```

**Stage Parameters**:
- Standard: `spawn_count` (default: 1)
- Learning-based: `spawn_count` (default: 2)
- Multi: `spawn_count` (default: 3)
- Workload: `mode` (random/intelligent), `max_spawns`

---

### 4. code-quality.yml

**Purpose**: Code analysis and quality checks

**Original Workflows Consolidated**:
- `code-analyzer.yml` → Stage: `analyzer`
- `code-archaeologist.yml` → Stage: `archaeologist`
- `code-golf-optimizer.yml` → Stage: `golf-optimizer`

**Triggers**:
- Analyzer: Push to main, PR merge, manual
- Archaeologist: Weekly Monday 9 AM UTC, manual
- Golf Optimizer: Weekly Monday 10 AM UTC, manual
- Manual dispatch with stage selection

**How to Use**:
```bash
# Run code analyzer on specific directory
gh workflow run code-quality.yml \
  -f stage=analyzer \
  -f directory=tools \
  -f mark_as_failure=false

# Run code archaeologist
gh workflow run code-quality.yml \
  -f stage=archaeologist \
  -f max_commits=200 \
  -f since="2 weeks ago"

# Run code golf optimizer
gh workflow run code-quality.yml \
  -f stage=golf-optimizer \
  -f language=python
```

**Stage Parameters**:
- Analyzer: `directory`, `mark_as_failure`
- Archaeologist: `max_commits`, `since`
- Golf: `file_path`, `language` (python/javascript/bash)

---

### 5. goal-and-idea-system.yml

**Purpose**: Goal tracking and idea generation

**Original Workflows Consolidated**:
- `ai-idea-spawner.yml` → Stage: `ai-idea-spawner`
- `daily-goal-generator.yml` → Stage: `daily-goals`
- `goal-progress-checker.yml` → Stage: `progress-checker`
- `idea-generator.yml` → Stage: `general-ideas`

**Triggers**:
- AI Ideas: Every 4 hours
- Daily Goals: Daily 6 AM UTC
- Progress Check: Daily 8 PM UTC
- Manual dispatch with stage selection

**How to Use**:
```bash
# Generate AI-focused idea
gh workflow run goal-and-idea-system.yml \
  -f stage=ai-idea-spawner \
  -f focus=ai-autonomy

# Generate daily goal (force new)
gh workflow run goal-and-idea-system.yml \
  -f stage=daily-goals \
  -f force_new_goal=true

# Check goal progress
gh workflow run goal-and-idea-system.yml \
  -f stage=progress-checker

# Generate general ideas
gh workflow run goal-and-idea-system.yml \
  -f stage=general-ideas \
  -f idea_count=5
```

**Stage Parameters**:
- AI Ideas: `focus` (auto/ai-autonomy/ml-learning/code-generation/agent-systems/performance)
- Daily Goals: `force_new_goal` (true/false)
- General Ideas: `idea_count` (number)

---

## Migration Guide

### For Workflow Developers

If you previously referenced one of the consolidated workflows, update your references:

**Old**:
```yaml
uses: ./.github/workflows/code-analyzer.yml
```

**New**:
```yaml
uses: ./.github/workflows/code-quality.yml
# Note: May need to specify which stage via inputs
```

### For Issue/PR Labels

Label triggers remain the same - they're preserved in the consolidated workflows.

### For Scheduled Jobs

All schedules are preserved. The consolidated workflows will run the appropriate stage based on the schedule trigger.

---

## Testing Strategy

Each consolidated workflow has been designed to:

1. **Preserve all original functionality** - No features removed
2. **Maintain all triggers** - Schedules, labels, manual dispatch
3. **Support independent execution** - Each stage can run alone
4. **Provide proper attribution** - PRs/issues credit @workflows-tech-lead

### Testing Checklist

- [ ] Test each stage via manual dispatch
- [ ] Verify scheduled triggers work correctly
- [ ] Check label-based triggers
- [ ] Validate PR/issue creation
- [ ] Confirm proper attribution

---

## Deprecation Plan

### Phase 1: Validation (2 weeks)
- Run consolidated workflows alongside original workflows
- Monitor for any issues or regressions
- Gather feedback from users

### Phase 2: Migration (1 week)
- Update documentation to reference new workflows
- Add deprecation notices to old workflows
- Ensure all integrations use new workflows

### Phase 3: Cleanup (After validation)
- Archive original workflow files
- Update any remaining references
- Document migration in changelog

---

## Troubleshooting

### Issue: Stage not running as expected

**Check**:
1. Verify the `if` condition for the job
2. Check the schedule cron expression
3. Ensure stage name matches input exactly

### Issue: Stage parameters not working

**Check**:
1. Parameter names match workflow inputs
2. Parameter types are correct (string, boolean, choice)
3. Default values are reasonable

### Issue: Original functionality missing

**Check**:
1. Compare with original workflow file
2. Verify all steps are present
3. Check environment variables and secrets

---

## Contributing

When adding new stages to consolidated workflows:

1. **Add to appropriate workflow** - Choose the right category
2. **Follow naming conventions** - Use descriptive stage names
3. **Update documentation** - Add to this file
4. **Test thoroughly** - Verify independent execution
5. **Maintain attribution** - Credit @workflows-tech-lead

---

## Summary

**@workflows-tech-lead** has consolidated 16 workflows into 5 organized mega-workflows:

| Consolidated Workflow | Original Count | Categories |
|----------------------|----------------|------------|
| demos-and-experiments.yml | 2 | Development, POC |
| ab-testing-system.yml | 3 | A/B Testing |
| agent-spawning.yml | 4 | Agent Management |
| code-quality.yml | 3 | Code Analysis |
| goal-and-idea-system.yml | 4 | Goals, Ideas |
| **Total** | **16** | - |

This consolidation improves maintainability while preserving all functionality and adding the flexibility to trigger individual stages as needed.

---

*Created by **@workflows-tech-lead** - 2025-11-19*
