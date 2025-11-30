# Disabled Workflows Report

*Generated: 2025-11-30*

This report documents all disabled workflows in the repository, including their purpose, original triggers/schedules, and the artifacts/outcomes they produce.

---

## Table of Contents

1. [Summary](#summary)
2. [Disabled Workflows (Active Directory)](#disabled-workflows-active-directory)
3. [Archived Workflows](#archived-workflows)
4. [Reasons for Disabling](#reasons-for-disabling)
5. [Re-enabling Workflows](#re-enabling-workflows)

---

## Summary

| Category | Count |
|----------|-------|
| Disabled (if:false) | 4 |
| Disabled (commented triggers) | 1 |
| Archived | 18 |
| **Total** | **23** |

---

## Disabled Workflows (Active Directory)

These workflows exist in `.github/workflows/` but have been disabled through `if: false` conditions or commented-out triggers.

### 1. Auto Review & Merge (Improved)

**File:** `auto-review-merge.yml`

**Status:** ⛔ Fully Disabled (replaced by meta-coordinator)

**Purpose:**
- Combined auto-review, tech lead review, and auto-merge into a single workflow
- Analyzed PRs for tech lead review requirements
- Processed PR labels and review states
- Auto-merged approved PRs from trusted sources

**Original Triggers:**
| Trigger | Configuration |
|---------|---------------|
| `pull_request` | `opened`, `synchronize`, `ready_for_review`, `reopened` |
| `pull_request_review` | `submitted` |
| `schedule` | `*/15 * * * *` (every 15 minutes) |
| `workflow_dispatch` | Manual with optional PR number input |

**Artifacts/Outcomes:**
- Tech lead labels added to PRs (`needs-tech-lead-review`, `tech-lead-approved`)
- PR comments with tech lead analysis
- Auto-merge of eligible PRs
- PR approval reviews

**Disabled Jobs:**
- `analyze-prs` - Build PR matrix with tech lead analysis
- `process-pr` - Process each PR with tech lead review and labels
- `auto-merge` - Auto-merge eligible PRs

**Replacement:** `meta-coordinator.yml` via `@meta-coordinator-system` agent

---

### 2. Copilot Assignment (GraphQL)

**File:** `copilot-graphql-assign.yml`

**Status:** ⛔ Fully Disabled (replaced by meta-coordinator)

**Purpose:**
- Assigned GitHub Copilot to issues using GraphQL API
- Processed newly opened issues
- Ran scheduled sweeps for unassigned issues
- Triggered after idea/mission generation workflows

**Original Triggers:**
| Trigger | Configuration |
|---------|---------------|
| `issues` | `opened` |
| `schedule` | `*/15 * * * *` (every 15 minutes) |
| `workflow_dispatch` | Manual with optional issue number input |
| `workflow_run` | After "Idea Generation: Progress Checker" and "World Model Update" |

**Artifacts/Outcomes:**
- Copilot assigned to issues
- Agent labels added (`agent:X`)
- Issue comments with agent assignment directive

**Replacement:** `meta-coordinator.yml` via `@meta-coordinator-system` agent

---

### 3. Copilot PR Assignment

**File:** `copilot-pr-assignment.yml`

**Status:** ⛔ Fully Disabled (replaced by meta-coordinator)

**Purpose:**
- Assigned agents to PRs needing tech lead attention
- Created feedback issues when tech leads requested changes
- Proactively assigned tech lead agents to review PRs

**Original Triggers:**
| Trigger | Configuration |
|---------|---------------|
| `schedule` | `*/7 * * * *` (every 7 minutes) |
| `workflow_dispatch` | Manual with optional PR number input |

**Artifacts/Outcomes:**
- Feedback issues created for PRs with change requests
- Tech lead review issues created proactively
- Agent labels added to PRs
- PR comments linking to feedback issues

**Replacement:** `meta-coordinator.yml` via `@meta-coordinator-system` agent

---

### 4. Autonomous Refactoring Learning

**File:** `autonomous-refactoring-learning.yml`

**Status:** ⚠️ Temporarily Disabled (branch protection violation)

**Purpose:**
- Learned optimal coding patterns from merged PRs
- Performed periodic style learning from repository
- Created refactoring suggestions based on patterns

**Original Triggers:**
| Trigger | Configuration |
|---------|---------------|
| `pull_request` | `closed` (on merge to main) |
| `schedule` | `0 */6 * * *` (every 6 hours) |
| `workflow_dispatch` | Manual with `force_report` option |

**Artifacts/Outcomes:**
- Style patterns learned from merged code
- Refactoring recommendations generated
- PRs with suggested improvements

**Disabled Jobs:**
- `learn-from-merged-pr` - Learn style from merged PRs
- `periodic-learning` - Periodic style analysis
- `create-refactoring-pr` - Create refactoring PR

**Issue:** Jobs performed direct `git push` to main branch, violating branch protection rules

**Fix Required:** Refactor to use PR-based workflow pattern (assigned to @troubleshoot-expert)

---

### 5. Workflow Failure Handler

**File:** `workflow-failure-handler.yml`

**Status:** ⚠️ Partially Disabled (workflow_run trigger commented out)

**Purpose:**
- Automatically detected workflow failures
- Created or updated failure tracking issues
- Provided failure details and quick links for debugging

**Original Triggers:**
| Trigger | Configuration |
|---------|---------------|
| `workflow_run` | Monitored 12+ workflows for failures (commented out) |
| `workflow_dispatch` | Manual (still available) |

**Monitored Workflows (disabled):**
- AI Friend Daily
- Auto Review and Merge
- Code Analyzer
- Code Golf Optimizer
- Copilot Assignment Workflow
- Daily AI Goal Generator
- Goal Progress Checker
- Smart Idea Generator
- Learning from Hacker News
- Learning from TLDR Tech
- Pattern Matcher
- System Kickoff
- System Monitor

**Artifacts/Outcomes:**
- Failure tracking issues created with `workflow-failure` label
- Comments on existing issues for repeated failures
- Failure details including run URL, commit, branch

---

## Archived Workflows

These workflows have been moved to `.github/workflows/archive/` and are no longer active.

### 1. Actions Generator Agent (Demo)

**File:** `archive/actions-generator-agent-DEMO.yml`

**Purpose:** Demonstrated how to generate custom GitHub Actions using pattern analysis

**Original Trigger:** `workflow_dispatch` only

**Artifacts/Outcomes:**
- Pattern analysis reports
- Generated custom actions in `.github/actions/`
- PRs with generated actions or recommendation issues

---

### 2. Autonomous Code Reviewer

**File:** `archive/autonomous-code-reviewer.yml`

**Purpose:** Automated code review on pull requests using AI-based criteria

**Original Trigger:** `pull_request` (`opened`, `synchronize`, `reopened`)

**Artifacts/Outcomes:**
- Review comments posted on PRs
- Quality labels added to PRs
- Review results stored in `.github/review-system/reviews/`
- Criteria evolution PRs

---

### 3. Cleanup Old Learning Files

**File:** `archive/cleanup-old-learning-files.yml`

**Purpose:** Automated cleanup of old learning files to prevent repository bloat

**Original Triggers:**
| Trigger | Configuration |
|---------|---------------|
| `schedule` | `0 2 * * *` (daily at 2 AM UTC) |
| `workflow_dispatch` | Manual with `days_old` and `dry_run` options |

**Artifacts/Outcomes:**
- Old learning files deleted from `learnings/`, `summaries/`, `investigation-reports/`
- PRs with cleanup changes
- Space freed reports

**Protected Files:** README.md, docs/QUICKSTART.md, learnings/book/, learnings/agent_memory/, learnings/discussions/

---

### 4. Code Pattern Hypothesis Testing

**File:** `archive/code-pattern-hypothesis-testing.yml`

**Purpose:** AI-generated and validated hypotheses about code patterns

**Original Triggers:**
| Trigger | Configuration |
|---------|---------------|
| `schedule` | Weekly |
| `workflow_dispatch` | Manual with options for min confidence, create issues |

**Artifacts/Outcomes:**
- Hypothesis test results in `learnings/hypothesis_testing/`
- Issues created for validated hypotheses
- PRs with hypothesis testing results
- Learning log entries

---

### 5. Dynamic Orchestrator

**File:** `archive/dynamic-orchestrator.yml`

**Purpose:** Dynamically adjusted workflow schedules based on Copilot API usage

**Original Triggers:**
| Trigger | Configuration |
|---------|---------------|
| `schedule` | `0 0 * * *` (daily at midnight UTC) |
| `workflow_dispatch` | Manual with mode and usage override options |

**Artifacts/Outcomes:**
- Updated workflow schedules (aggressive/normal/conservative modes)
- Repository variables updated (`COPILOT_REQUESTS_USED`, `COPILOT_MONTHLY_QUOTA`)
- PRs for schedule updates
- Usage history in `tools/analysis/copilot_usage_history.json`

---

### 6. Example A/B Testing Workflow

**File:** `archive/example-ab-testing-workflow.yml`

**Purpose:** Demonstrated A/B testing integration for workflows

**Original Trigger:** `workflow_dispatch` with config override option

**Artifacts/Outcomes:**
- A/B test participation records
- Execution metrics recorded for experiments
- Summary reports in job output

---

### 7. Example Copilot with MCP

**File:** `archive/example-copilot-mcp.yml`

**Purpose:** Demonstrated MCP (Model Context Protocol) server integration with Copilot

**Original Trigger:** `workflow_dispatch` with test issue inputs

**Artifacts/Outcomes:**
- MCP server configuration demonstration
- Agent matching examples
- Learning search examples

---

### 8. Example Enhanced Actions

**File:** `archive/example-enhanced-actions.yml`

**Purpose:** Test suite for custom reusable GitHub Actions

**Original Trigger:** `workflow_dispatch` with test category options

**Artifacts/Outcomes:**
- Test results for JSON, regex, HTTP, Python, and Git operations
- Integration test results
- Test summary reports

---

### 9. Learn Commit Strategies

**File:** `archive/learn-commit-strategies.yml`

**Purpose:** Analyzed git commit history to learn optimal commit patterns

**Original Triggers:**
| Trigger | Configuration |
|---------|---------------|
| `schedule` | `0 2 * * *` (daily at 2 AM UTC) |
| `workflow_dispatch` | Manual with days and branch options |

**Artifacts/Outcomes:**
- Commit pattern analysis in `analysis/commit_patterns.json`
- PRs with learned patterns
- Strategy recommendations

---

### 10. Mentorship Monitoring

**File:** `archive/mentorship-monitoring.yml`

**Purpose:** Monitored and evaluated agent mentorship relationships

**Original Triggers:**
| Trigger | Configuration |
|---------|---------------|
| `schedule` | `0 0 * * *` (daily at midnight UTC) |
| `workflow_dispatch` | Manual with force evaluation option |

**Artifacts/Outcomes:**
- Mentorship health reports
- Capacity dashboard visualizations
- Active mentorship trees
- Statistical summaries

---

### 11. Meta-Learning Optimizer

**File:** `archive/meta-learning-optimizer.yml`

**Purpose:** Optimized workflow schedules using meta-learning from execution patterns

**Original Triggers:**
| Trigger | Configuration |
|---------|---------------|
| `schedule` | `0 */6 * * *` (every 6 hours) |
| `workflow_dispatch` | Manual with force evolution and report options |

**Artifacts/Outcomes:**
- Evolved scheduling strategies
- Learning reports
- PRs with strategy changes

---

### 12. Neural Workflow Adaptation

**File:** `archive/neural-workflow-adaptation.yml`

**Purpose:** Self-evolving neural architecture for workflow adaptation

**Original Triggers:**
| Trigger | Configuration |
|---------|---------------|
| `workflow_run` | After "Performance Metrics Collection" |
| `schedule` | `0 */6 * * *` (every 6 hours) |
| `workflow_dispatch` | Manual with force adapt option |

**Artifacts/Outcomes:**
- Workflow execution statistics
- Adaptation recommendations
- PRs with workflow optimizations

---

### 13. Prompt Auto-Tuner

**File:** `archive/prompt-auto-tuner.yml`

**Purpose:** Automatically tuned prompt templates based on performance data

**Original Triggers:**
| Trigger | Configuration |
|---------|---------------|
| `schedule` | `0 3 * * 0` (weekly, Sunday 3 AM UTC) |
| `workflow_dispatch` | Manual with force evolution and min effectiveness options |

**Artifacts/Outcomes:**
- Template performance analysis
- Evolved prompt templates
- PRs with template updates
- Optimization reports

---

### 14. Prompt Generator Integration

**File:** `archive/prompt-generator-integration.yml`

**Purpose:** Generated optimized prompts for Copilot based on issue content

**Original Trigger:** `workflow_dispatch` with issue number, agent, and learning options

**Artifacts/Outcomes:**
- Generated prompts tailored to issues
- Issue comments with generated prompts
- Category detection results

---

### 15. Review Criteria Learning

**File:** `archive/review-criteria-learning.yml`

**Purpose:** Evolved code review criteria based on PR outcomes

**Original Triggers:**
| Trigger | Configuration |
|---------|---------------|
| `schedule` | `0 2 * * *` (daily at 2 AM UTC) |
| `workflow_dispatch` | Manual |

**Artifacts/Outcomes:**
- Updated criteria in `.github/review-system/criteria.json`
- Learning reports
- PRs with evolved criteria

---

### 16. Self-Reinforcement Learning

**File:** `archive/self-reinforcement.yml`

**Purpose:** Collected insights from closed issues and merged PRs for self-improvement

**Original Trigger:** `workflow_dispatch` only (now part of `autonomous-pipeline.yml`)

**Artifacts/Outcomes:**
- Insights extracted from closed issues and PRs
- Pattern analysis from labels
- Self-reinforcement data collection

**Note:** This workflow is now an optional stage in `autonomous-pipeline.yml`

---

### 17. Setup Tech Lead Labels

**File:** `archive/setup-tech-lead-labels.yml`

**Purpose:** Created required labels for the Tech Lead Review System

**Original Triggers:**
| Trigger | Configuration |
|---------|---------------|
| `workflow_dispatch` | Manual |
| `push` | To main, when tech-lead-review.yml changes |

**Artifacts/Outcomes:**
- Labels created: `needs-tech-lead-review`, `tech-lead-approved`, `tech-lead-changes-requested`, `tech-lead-review-cycle`

---

### 18. Validate Instructions Size

**File:** `archive/validate-instructions-size.yml`

**Purpose:** Validated Copilot instructions don't exceed size/token limits

**Original Triggers:**
| Trigger | Configuration |
|---------|---------------|
| `pull_request` | Changes to `.github/instructions/**` or `.copilot-instructions.md` |
| `workflow_dispatch` | Manual |

**Artifacts/Outcomes:**
- Size check results (bytes, KB, estimated tokens)
- PR comments with validation status
- Warnings for approaching limits

**Limits Enforced:**
- Maximum: 60,000 bytes (60 KB)
- Token estimate: < 15,000 tokens

---

## Reasons for Disabling

| Reason | Workflows Affected |
|--------|-------------------|
| Replaced by meta-coordinator | `auto-review-merge.yml`, `copilot-graphql-assign.yml`, `copilot-pr-assignment.yml` |
| Branch protection violation | `autonomous-refactoring-learning.yml` |
| Functionality integrated elsewhere | `self-reinforcement.yml` (into autonomous-pipeline) |
| No longer needed | Various archived workflows |
| Example/Demo workflows | `example-*.yml`, `actions-generator-agent-DEMO.yml` |

---

## Re-enabling Workflows

### Workflows with `if: false` Conditions

To re-enable, remove the `if: false` condition from the job definition and ensure the workflow is still compatible with current system architecture.

```yaml
# Before (disabled)
jobs:
  my-job:
    if: false  # DISABLED
    runs-on: ubuntu-latest

# After (enabled)
jobs:
  my-job:
    runs-on: ubuntu-latest
```

### Workflows with Commented Triggers

To re-enable, uncomment the trigger section:

```yaml
# Before (disabled)
on:
  # workflow_run:
  #   workflows: ["Workflow Name"]
  #   types: [completed]

# After (enabled)
on:
  workflow_run:
    workflows: ["Workflow Name"]
    types: [completed]
```

### Archived Workflows

To re-enable an archived workflow:
1. Move the file from `.github/workflows/archive/` back to `.github/workflows/`
2. Review and update any outdated references or dependencies
3. Test the workflow manually via `workflow_dispatch` before enabling scheduled runs

---

## See Also

- [META_COORDINATOR_IMPLEMENTATION.md](../.github/workflows/META_COORDINATOR_IMPLEMENTATION.md) - Meta-coordinator system documentation
- [WORKFLOWS.md](./WORKFLOWS.md) - Active workflows documentation
- [AUTONOMOUS_SYSTEM_ARCHITECTURE.md](./AUTONOMOUS_SYSTEM_ARCHITECTURE.md) - System architecture overview

---

*Report generated by **@investigate-champion** - Understanding disabled workflows for transparency and documentation.*
