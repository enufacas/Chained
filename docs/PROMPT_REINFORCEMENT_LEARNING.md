# Self-Improving Prompt Generator - Reinforcement Learning

## Overview

The self-improving prompt generator now includes **reinforcement learning** capabilities that enable it to learn from outcomes and continuously optimize prompt effectiveness. This autonomous system analyzes feedback, identifies successful patterns, and evolves templates to maximize success rates.

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│         Self-Improving Prompt Generator                 │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │   Template   │  │   Learning   │  │Reinforcement │ │
│  │   System     │  │ Integration  │  │   Learning   │ │
│  │              │  │              │  │              │ │
│  │ • Templates  │  │ • TLDR/HN    │  │ • Feedback   │ │
│  │ • Tracking   │  │ • Trends     │  │ • Patterns   │ │
│  │ • A/B Test   │  │ • Insights   │  │ • Optimize   │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
│         │                  │                  │         │
│         └──────────────────┴──────────────────┘         │
│                            │                            │
│                     ┌──────▼──────┐                     │
│                     │   Enhanced  │                     │
│                     │   Prompts   │                     │
│                     └─────────────┘                     │
└─────────────────────────────────────────────────────────┘
```

## Key Components

### 1. PromptReinforcementLearner

The core reinforcement learning module that:

- **Collects Feedback**: Records outcomes from PR reviews and issue resolutions
- **Extracts Patterns**: Identifies successful and unsuccessful patterns in prompts
- **Calculates Effectiveness**: Tracks success rates for each pattern (0-1 scale)
- **Generates Recommendations**: Suggests specific improvements for templates
- **Prunes Ineffectives**: Removes patterns that consistently fail
- **Maintains Diversity**: Prevents convergence to a single strategy

### 2. Pattern Types

The system recognizes four pattern types:

- **Structure Patterns**: `structure_step_by_step`, `structure_hierarchical`
- **Keyword Patterns**: `emphasis_clear`, `emphasis_thorough`
- **Instruction Patterns**: `include_examples`, `include_tests`
- **Constraint Patterns**: `avoid_vague`, `avoid_unclear`

### 3. Feedback Sources

Reinforcement learning uses multiple feedback sources:

1. **PR Reviews**: Comments from code reviews
2. **Issue Resolution**: Success/failure of issue completion
3. **Build Results**: CI/CD outcome data
4. **Test Failures**: Test execution results

## Usage

### Basic Usage

```python
from prompt_generator import PromptGenerator

# Initialize with reinforcement learning enabled
generator = PromptGenerator(enable_reinforcement=True)

# Generate enhanced prompt
prompt, template_id = generator.generate_prompt(
    issue_body="Fix authentication bug in login flow",
    category="bug_fix",
    agent="engineer-master"
)

# Prompt automatically includes proven success patterns
print(prompt)
```

### Recording Outcomes with Feedback

```python
# After issue is resolved, record outcome with feedback
generator.record_outcome(
    prompt_id=template_id,
    issue_number=123,
    success=True,
    resolution_time_hours=2.5,
    agent_used="engineer-master",
    feedback_text="Clear systematic approach with step-by-step guidance led to quick resolution"
)

# System extracts patterns and updates effectiveness scores
```

### Getting Optimization Recommendations

```python
# Get recommendations for improving a specific template
recommendations = generator.reinforcement_learner.generate_optimization_recommendations(
    prompt_id="bug_fix_systematic"
)

for rec in recommendations:
    print(f"{rec['priority']}: {rec['action']}")
```

### Viewing Top Patterns

```python
# Get most effective patterns for a category
top_patterns = generator.reinforcement_learner.get_top_patterns(
    category="bug_fix",
    min_effectiveness=0.7,
    limit=5
)

for pattern in top_patterns:
    print(f"{pattern.pattern}: {pattern.effectiveness:.0%} effective ({pattern.success_count} successes)")
```

### Pruning Ineffective Patterns

```python
# Automatically remove patterns that consistently fail
pruned = generator.reinforcement_learner.prune_ineffective_patterns(
    min_samples=10,
    effectiveness_threshold=0.3
)

print(f"Pruned {len(pruned)} ineffective patterns")
```

## CLI Interface

### Record Feedback

```bash
python3 tools/prompt_reinforcement.py record \
  --prompt-id "bug_fix_systematic" \
  --issue-number 123 \
  --feedback-type "pr_review" \
  --sentiment "positive" \
  --feedback-text "Clear and thorough approach"
```

### View Top Patterns

```bash
python3 tools/prompt_reinforcement.py patterns \
  --category "bug_fix" \
  --limit 10
```

### Get Optimization Recommendations

```bash
python3 tools/prompt_reinforcement.py optimize \
  --prompt-id "feature_rigorous"
```

### View Metrics

```bash
python3 tools/prompt_reinforcement.py metrics
```

### Prune Ineffective Patterns

```bash
python3 tools/prompt_reinforcement.py prune
```

## Performance Metrics

The system tracks multiple metrics:

### Pattern Effectiveness

- **Success Rate**: Percentage of successful outcomes
- **Usage Count**: Number of times pattern was used
- **Confidence**: Based on sample size
- **Effectiveness Score**: Combined metric (0-1)

### System Health

- **Total Patterns**: Number of learned patterns
- **Effective Patterns**: Patterns above effectiveness threshold
- **Diversity Score**: Measure of pattern variety (0-1)
- **Pattern Types**: Distribution across types

### Performance Reports

```python
report = generator.get_performance_report()

print(f"Overall Success Rate: {report['insights']['overall']['success_rate']:.0%}")
print(f"Effective Patterns: {report['reinforcement']['effective_patterns']}")
print(f"Diversity Score: {report['reinforcement']['diversity_score']:.2f}")
```

## Integration with Existing System

### Template Enhancement

Prompts are automatically enhanced with proven patterns:

```
Original Template:
**@engineer-master** - Fix this bug systematically.

Enhanced Prompt (after learning):
**@engineer-master** - Fix this bug systematically.

**Key Success Patterns (learned from outcomes):**
1. Structure Step By Step (effectiveness: 85%)
2. Emphasis Clear (effectiveness: 82%)
3. Include Examples (effectiveness: 78%)

Apply these proven patterns to maximize success.
```

### Optimization Integration

```python
# Optimization now includes both statistical and RL recommendations
suggestions = generator.optimize_templates()

for suggestion in suggestions:
    if suggestion.get("source") == "reinforcement_learning":
        print(f"RL Recommendation: {suggestion['action']}")
    else:
        print(f"Statistical: {suggestion['recommendation']}")
```

## Best Practices

### 1. Provide Rich Feedback

More detailed feedback leads to better pattern extraction:

```python
# ✅ Good - specific feedback
feedback = "Clear step-by-step approach with examples led to comprehensive implementation"

# ❌ Poor - vague feedback
feedback = "Good work"
```

### 2. Wait for Sufficient Data

Patterns require minimum samples before being considered effective:

- **Minimum 3 samples**: Before including in top patterns
- **Minimum 10 samples**: Before considering for pruning
- **Higher confidence**: More samples = more reliable effectiveness scores

### 3. Monitor Diversity

Prevent convergence to single pattern:

```python
diversity = generator.reinforcement_learner.calculate_diversity_score()

if diversity < 0.3:
    print("Warning: Low diversity - system may be converging")
```

### 4. Regular Pruning

Remove ineffective patterns periodically:

```python
# Run weekly or monthly
pruned = generator.reinforcement_learner.prune_ineffective_patterns()
```

## Data Storage

Reinforcement learning data is stored in:

```
tools/data/prompts/
├── feedback.json          # Feedback history
├── patterns.json          # Pattern database with stats
└── reinforcement_metrics.json  # System metrics
```

## Testing

Comprehensive test suite ensures reliability:

```bash
# Test reinforcement learning module
python3 tests/test_prompt_reinforcement.py

# Test integration with prompt generator
python3 tests/test_prompt_generator_integration.py

# Test original functionality still works
python3 tests/test_prompt_generator.py
```

## Future Enhancements

Potential improvements for the system:

1. **Multi-Agent Learning**: Learn patterns specific to each agent type
2. **Context-Aware Patterns**: Patterns that adapt to issue complexity
3. **Temporal Analysis**: Track how patterns evolve over time
4. **Cross-Repository Learning**: Share patterns across multiple repos
5. **Automated Template Generation**: Create new templates from successful patterns

## Contributing

When contributing to the reinforcement learning system:

1. **Maintain Backward Compatibility**: System should work with `enable_reinforcement=False`
2. **Add Tests**: All new features must include comprehensive tests
3. **Document Patterns**: Explain pattern types and extraction logic
4. **Preserve Diversity**: Ensure changes don't reduce pattern variety
5. **Follow @APIs-architect Principles**: Rigorous testing and systematic approach

## References

- [Main Prompt Generator](./prompt-generator.py)
- [Learning Integration](./prompt_learning_integration.py)
- [Reinforcement Module](./prompt_reinforcement.py)
- [Integration Tests](../tests/test_prompt_generator_integration.py)
- [Prompt Generator Workflows](../.github/workflows/prompt-generator-integration.yml)

---

**Created by @APIs-architect** - Rigorous and innovative engineering approach inspired by Margaret Hamilton.
