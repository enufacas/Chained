# Self-Improving Prompt Generator

**Created by @construct-specialist** - Direct and practical autonomous prompt evolution.

## Overview

The self-improving prompt generator uses **genetic algorithms** and **multi-dimensional quality scoring** to continuously evolve and optimize prompts for GitHub Copilot based on real-world performance data.

## Key Features

### 1. Multi-Dimensional Quality Scoring

Every prompt is assessed across 5 dimensions:

- **Clarity** (0-1): How clear and understandable the instructions are
- **Completeness** (0-1): Whether all necessary information is included
- **Actionability** (0-1): How actionable the instructions are
- **Specificity** (0-1): Level of detail and specificity vs generic guidance
- **Success Rate** (0-1): Historical success rate from actual usage

**Overall Score** = Weighted average prioritizing actionability and success rate

### 2. Genetic Algorithm Evolution

Uses natural selection principles to evolve prompts:

```
┌─────────────┐
│ Population  │  Templates with fitness scores
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Selection  │  Top performers become parents
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Crossover  │  Combine successful elements
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Mutation   │  Introduce variations
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Elitism   │  Preserve best performers
└──────┬──────┘
       │
       ▼
┌─────────────┐
│New Generation│ Evolved prompts
└─────────────┘
```

### 3. Automated Feedback Extraction

Learns from PR reviews automatically:

- Extracts sentiment (positive/negative/neutral)
- Identifies patterns (clarity, completeness, testing)
- Detects issues (missing tests, unclear instructions)
- Updates gene fitness scores based on feedback

### 4. Prompt Genes

Reusable genetic components tracked for effectiveness:

- **Structure genes**: Numbered lists, principle sections
- **Instruction genes**: "Test thoroughly", "Make minimal changes"
- **Constraint genes**: "Follow conventions", "Handle errors"

Each gene has a fitness score that adapts based on outcomes.

## How It Works

### Phase 1: Data Collection

The system collects data from:
- Issue resolutions (success/failure)
- Resolution times
- PR reviews and feedback
- Code review comments

Minimum **20 outcomes** needed for auto-improvement.

### Phase 2: Quality Assessment

```bash
python3 tools/prompt-generator.py assess-quality
```

Assesses all templates across 5 dimensions:

```json
{
  "total_templates": 6,
  "avg_overall_score": 0.641,
  "top_performers": [
    ["bug_fix_systematic", {
      "clarity": 0.80,
      "completeness": 1.00,
      "actionability": 0.90,
      "specificity": 0.90,
      "overall_score": 0.75
    }]
  ],
  "needs_improvement": [...]
}
```

### Phase 3: Genetic Evolution

```bash
python3 tools/prompt-generator.py auto-improve
```

1. **Build population** from existing templates with performance data
2. **Select parents** based on effectiveness scores
3. **Crossover** combines best elements from multiple parents
4. **Mutate** introduces random variations (30% chance)
5. **Elitism** preserves top 20% of performers
6. **Create offspring** to reach target population size

### Phase 4: New Generation

System creates new templates with IDs like:
- `evolved_bug_fix_gen3_v1`
- `evolved_feature_gen3_v2`

Each new template has:
- Quality score ≥ 0.6 (threshold for acceptance)
- Category inherited from parents
- Timestamp and generation tracking

### Phase 5: Continuous Learning

```bash
python3 tools/prompt-generator.py extract-feedback --issue-number 123
```

PR reviews update gene fitness:
- Positive feedback → increase fitness
- Negative feedback → decrease fitness
- Patterns identified → inform future evolution

## CLI Commands

### Generate Prompt

```bash
python3 tools/prompt-generator.py generate \
  --issue-body "Fix authentication bug" \
  --category "bug_fix" \
  --agent "engineer-master"
```

### Record Outcome

```bash
python3 tools/prompt-generator.py record \
  --prompt-id "bug_fix_systematic" \
  --issue-number 123 \
  --success \
  --resolution-time 3.5
```

### Assess Quality

```bash
python3 tools/prompt-generator.py assess-quality
```

### Auto-Improve

```bash
python3 tools/prompt-generator.py auto-improve
```

### Extract Feedback

```bash
python3 tools/prompt-generator.py extract-feedback \
  --issue-number 123 \
  --review-body "Great work! Tests are comprehensive."
```

### Get Report

```bash
python3 tools/prompt-generator.py report
```

## Workflow Integration

### Auto-Improvement Workflow

`.github/workflows/prompt-auto-improve.yml` runs weekly:

1. **Check readiness**: Verify sufficient outcomes collected
2. **Assess quality**: Baseline measurement
3. **Run evolution**: Genetic algorithm generates new templates
4. **Re-assess**: Measure improvement
5. **Create PR**: Automated PR with evolution report

**Trigger**: Every Sunday at 3 AM UTC (or manual via `workflow_dispatch`)

### Manual Trigger

```bash
gh workflow run prompt-auto-improve.yml \
  --field min_outcomes=20
```

## Data Storage

### Files

```
tools/data/prompts/
├── templates.json          # All prompt templates
├── outcomes.json           # Historical outcomes
├── insights.json           # Performance insights
├── prompt_genes.json       # Genetic components
├── quality_scores.json     # Quality assessments
├── evolution_history.json  # Evolution events
└── history/               # Historical snapshots
    ├── report_*.json
    └── summary_*.md
```

### Structure

**prompt_genes.json**:
```json
{
  "structure_numbered_steps": {
    "gene_id": "structure_numbered_steps",
    "gene_type": "structure",
    "content": "1. **Step**: Description",
    "fitness_score": 0.8
  }
}
```

**evolution_history.json**:
```json
[
  {
    "timestamp": "2025-01-15T10:30:00Z",
    "generation_size": 5,
    "new_templates": 2,
    "avg_quality": 0.72
  }
]
```

## Performance Metrics

### Effectiveness Score

```
effectiveness = (
  success_rate * 0.7 +
  confidence_factor * 0.3
) * time_penalty
```

Where:
- `confidence_factor = min(1.0, total_uses / 10.0)`
- `time_penalty = 1.0 - min(0.2, (resolution_time - 48) / 240)`

### Quality Score

```
overall_score = (
  clarity * 0.20 +
  completeness * 0.20 +
  actionability * 0.25 +
  specificity * 0.15 +
  success_rate * 0.20
)
```

### Fitness Update

Gene fitness adapts using exponential moving average:

```python
if success:
    fitness = fitness * 0.9 + 0.1  # Move towards 1.0
else:
    fitness = fitness * 0.9         # Move towards 0.0
```

## Examples

### Example 1: Evolution Cycle

```bash
# Start with baseline
$ python3 tools/prompt-generator.py assess-quality
{
  "avg_overall_score": 0.641,
  "total_templates": 6
}

# Run auto-improvement
$ python3 tools/prompt-generator.py auto-improve
{
  "improvements_made": 3,
  "evolution_generation": 2,
  "new_templates": [
    {
      "template_id": "evolved_bug_fix_gen2_v1",
      "quality_score": 0.78
    }
  ]
}

# Check improvement
$ python3 tools/prompt-generator.py assess-quality
{
  "avg_overall_score": 0.703,  # +9.7% improvement
  "total_templates": 9
}
```

### Example 2: Feedback Learning

```bash
# Extract feedback from PR
$ python3 tools/prompt-generator.py extract-feedback \
  --issue-number 456 \
  --review-body "Implementation is clear and thorough. Tests cover edge cases well."

{
  "sentiment": "positive",
  "positive_patterns": ["clarity", "completeness", "testing"],
  "suggestions": [],
  "pr_number": 456
}
```

## Best Practices

### 1. Regular Evolution

Run auto-improvement weekly to continuously optimize prompts.

### 2. Record Outcomes

Always record outcomes for learning:

```bash
python3 tools/prompt-generator.py record \
  --prompt-id "feature_rigorous" \
  --issue-number 789 \
  --success \
  --resolution-time 4.2
```

### 3. Extract Feedback

Pull PR reviews into the system:

```bash
# In workflow
gh pr view $PR_NUMBER --json reviews --jq '.reviews[0].body' | \
  python3 tools/prompt-generator.py extract-feedback \
    --issue-number $PR_NUMBER \
    --review-body "$(cat -)"
```

### 4. Monitor Quality

Track template quality over time:

```bash
python3 tools/prompt-generator.py assess-quality > quality_$(date +%Y%m%d).json
```

### 5. A/B Testing

Test template variations:

```bash
# Start A/B test
python3 tools/prompt-generator.py ab-test \
  --template-a "bug_fix_systematic" \
  --template-b "evolved_bug_fix_gen2_v1"

# Check results
python3 tools/prompt-generator.py ab-test \
  --test-id "ab_bug_fix_systematic_vs_evolved_bug_fix_gen2_v1"
```

## Architecture

### Component Diagram

```
┌─────────────────────────────────────────────┐
│         PromptGenerator (Main)              │
│  - Generate prompts                         │
│  - Record outcomes                          │
│  - Track performance                        │
└────────────┬────────────────────────────────┘
             │
             ├─────────────────────┐
             │                     │
             ▼                     ▼
┌────────────────────┐  ┌──────────────────────┐
│PromptReinforcementLearner│  │PromptSelfImprover│
│ - Extract patterns  │  │ - Quality scoring   │
│ - Learn from feedback│  │ - Genetic algorithm │
│ - Track effectiveness│  │ - Mutation engine   │
└────────────────────┘  └──────────────────────┘
```

### Data Flow

```
Issue → Generate → Record → Learn → Evolve → New Templates
  ↑                                              │
  └──────────────────────────────────────────────┘
```

## Testing

Run comprehensive test suite:

```bash
python3 tests/test_prompt_self_improver.py
```

Tests cover:
1. ✅ Quality assessment (multi-dimensional scoring)
2. ✅ Genetic crossover (parent combination)
3. ✅ Mutation (variation generation)
4. ✅ Feedback extraction (sentiment analysis)
5. ✅ Evolution generation (full GA cycle)
6. ✅ Gene fitness updates (learning)
7. ✅ Evolution reporting (metrics)

All tests pass with 100% success rate.

## Troubleshooting

### Not Enough Outcomes

```
Error: Need at least 20 outcomes for auto-improvement
```

**Solution**: Record more outcomes or lower threshold:
```bash
# In workflow, adjust min_outcomes input
min_outcomes: '10'  # Lower threshold for testing
```

### Low Quality Scores

If templates consistently score below 0.6:

1. Check template structure (needs numbered steps)
2. Add Key Principles section
3. Include actionable verbs (implement, test, validate)
4. Reference issue context with `{issue_body}`

### No Improvements Generated

If auto-improve returns 0 improvements:

1. Templates may already be optimal
2. Population too homogeneous (need diversity)
3. Quality threshold too high (templates < 0.6 rejected)

**Solution**: Introduce manual variations or adjust threshold.

## Future Enhancements

Potential improvements:

1. **Neural Network Scoring** - Replace heuristics with learned model
2. **Multi-Objective Optimization** - Balance multiple goals (speed vs quality)
3. **Adaptive Mutation Rates** - Adjust mutation strength based on performance
4. **Cross-Category Evolution** - Allow genes to transfer between categories
5. **Ensemble Prompts** - Combine multiple templates for complex tasks

## References

- Main implementation: `tools/prompt_self_improver.py`
- Integration: `tools/prompt-generator.py`
- Tests: `tests/test_prompt_self_improver.py`
- Workflow: `.github/workflows/prompt-auto-improve.yml`

---

**@construct-specialist** - Direct. Practical. Works.

*Self-improving AI that learns from real-world performance.*
