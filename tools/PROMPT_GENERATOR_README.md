# Self-Improving Prompt Generator

A self-improving prompt generator for GitHub Copilot interactions that learns from outcomes and continuously optimizes prompt quality.

## Overview

The Self-Improving Prompt Generator is part of the Chained autonomous AI ecosystem. It generates optimized prompts for different types of tasks (bug fixes, features, refactoring, etc.) and tracks their performance to continuously improve effectiveness.

## Features

- **Template-Based Generation**: Uses proven templates for different task categories
- **Performance Tracking**: Monitors success rates, resolution times, and outcomes
- **Self-Improvement**: Learns from successes and failures to optimize templates
- **Agent Integration**: Customizes prompts for specific agents (engineer-master, create-guru, etc.)
- **Learning Context**: Incorporates recent learnings from TLDR and Hacker News
- **Effectiveness Scoring**: Evaluates templates based on multiple performance metrics

## Installation

No additional dependencies required beyond the base Chained requirements:

```bash
pip install -r requirements.txt
```

## Usage

### Command Line Interface

The tool provides a CLI with four main commands:

#### Generate a Prompt

```bash
python3 tools/prompt-generator.py generate \
  --issue-body "Fix authentication bug causing 500 errors" \
  --category bug_fix \
  --agent engineer-master
```

**Output:**
```
Template ID: bug_fix_systematic

Generated Prompt:
**@engineer-master** - Please fix this bug using a systematic approach:
...
```

#### Record an Outcome

After a task is completed, record its outcome to help the system learn:

```bash
python3 tools/prompt-generator.py record \
  --prompt-id bug_fix_systematic \
  --issue-number 123 \
  --success \
  --resolution-time 3.5 \
  --agent engineer-master
```

For failures:

```bash
python3 tools/prompt-generator.py record \
  --prompt-id bug_fix_systematic \
  --issue-number 124 \
  --resolution-time 1.0 \
  --error-type build_failure \
  --agent engineer-master
```

#### Get Performance Report

View performance statistics for all templates:

```bash
python3 tools/prompt-generator.py report
```

**Output:**
```json
{
  "generated_at": "2025-11-13T14:00:00+00:00",
  "templates": {
    "bug_fix_systematic": {
      "category": "bug_fix",
      "success_rate": 0.85,
      "effectiveness_score": 0.82,
      "total_uses": 20,
      "avg_resolution_time": 3.2
    },
    ...
  },
  "insights": {
    "overall": {
      "total_prompts_used": 50,
      "success_rate": 0.78,
      "avg_resolution_time": 4.5
    }
  }
}
```

#### Optimize Templates

Analyze performance and get optimization suggestions:

```bash
python3 tools/prompt-generator.py optimize
```

**Output:**
```json
[
  {
    "template_id": "refactor_basic",
    "issue": "high_failure_rate",
    "success_rate": 0.35,
    "common_errors": {
      "test_failures": 3,
      "build_errors": 2
    },
    "recommendation": "Address common error patterns: test_failures, build_errors"
  }
]
```

### Python API

Use the generator programmatically:

```python
from prompt_generator import PromptGenerator

# Initialize
generator = PromptGenerator()

# Generate a prompt
prompt, template_id = generator.generate_prompt(
    issue_body="Implement user profile feature",
    category="feature",
    agent="create-guru",
    learning_context=[
        "Use modular architecture for maintainability",
        "Consider mobile-first design"
    ]
)

print(f"Using template: {template_id}")
print(prompt)

# Record outcome after task completion
generator.record_outcome(
    prompt_id=template_id,
    issue_number=456,
    success=True,
    resolution_time_hours=6.5,
    agent_used="create-guru"
)

# Get performance report
report = generator.get_performance_report()
print(f"Overall success rate: {report['insights']['overall']['success_rate']:.2%}")
```

## Template Categories

The system includes default templates for:

1. **bug_fix** - Systematic bug fixing with root cause analysis
2. **feature** - Rigorous feature implementation with comprehensive testing
3. **refactor** - Systematic code refactoring preserving behavior
4. **documentation** - Precise documentation with examples
5. **investigation** - Thorough investigation with evidence-based analysis
6. **security** - Defensive security fixes with best practices

Custom categories can be added dynamically.

## Performance Metrics

Templates are evaluated using multiple metrics:

### Success Rate
```
success_rate = successful_uses / total_uses
```

### Effectiveness Score
A weighted score (0-1) combining:
- Success rate (70% weight)
- Usage confidence (30% weight)
- Resolution time penalty for slow outcomes (>48 hours)

```python
effectiveness_score = (
    success_rate * 0.7 + 
    confidence_factor * 0.3 - 
    time_penalty
)
```

### Resolution Time
Moving average of task completion times (in hours), giving more weight to recent outcomes.

## Data Storage

The generator stores data in `tools/data/prompts/`:

- **templates.json** - Template definitions and statistics
- **outcomes.json** - Historical outcomes for all tasks
- **insights.json** - Analyzed insights and optimization suggestions

Data persists across runs and enables continuous learning.

## Integration with Chained

### With Agent System

The prompt generator integrates with the Chained agent system:

```python
# Match agent to task
agent = match_agent(issue_labels, issue_body)

# Generate optimized prompt for that agent
prompt, template_id = generator.generate_prompt(
    issue_body=issue_body,
    category=detect_category(issue_labels),
    agent=agent
)
```

### With Learning System

Incorporate recent learnings from TLDR and Hacker News:

```python
# Load recent learnings
learnings = load_recent_learnings(days=7)

# Extract relevant insights
relevant_learnings = extract_relevant(learnings, issue_category)

# Generate enhanced prompt
prompt, template_id = generator.generate_prompt(
    issue_body=issue_body,
    category=category,
    learning_context=relevant_learnings
)
```

### With Workflow Automation

Example workflow integration:

```yaml
- name: Generate optimized prompt
  run: |
    prompt=$(python3 tools/prompt-generator.py generate \
      --issue-body "${{ github.event.issue.body }}" \
      --category "${{ env.DETECTED_CATEGORY }}" \
      --agent "${{ env.MATCHED_AGENT }}")
    
    # Use prompt in Copilot assignment
    gh issue comment ${{ github.event.issue.number }} \
      --body "$prompt"

- name: Record outcome after completion
  if: success()
  run: |
    python3 tools/prompt-generator.py record \
      --prompt-id "${{ env.TEMPLATE_ID }}" \
      --issue-number ${{ github.event.issue.number }} \
      --success \
      --resolution-time "${{ env.ELAPSED_HOURS }}"
```

## Self-Improvement Process

The generator improves through a continuous feedback loop:

1. **Generate** - Create prompt using best template for category
2. **Execute** - Task is performed using the prompt
3. **Record** - Outcome is recorded with success/failure and timing
4. **Analyze** - Statistics and insights are updated
5. **Optimize** - Templates are evaluated and suggestions generated
6. **Evolve** - Templates are refined based on patterns

### Optimization Triggers

Templates are flagged for optimization when:
- Effectiveness score < 0.4 (low effectiveness)
- Success rate < 0.5 with 5+ uses (high failure rate)
- Average resolution time > 48 hours (too slow)

## Best Practices

### For Prompt Generation

1. **Choose appropriate category** - Accurate categorization improves template selection
2. **Specify the right agent** - Different agents have different strengths
3. **Include learning context** - Recent insights can significantly improve outcomes
4. **Clear issue descriptions** - Better input leads to better prompts

### For Outcome Recording

1. **Record all outcomes** - Both successes and failures improve the system
2. **Accurate timing** - Resolution time helps identify efficiency issues
3. **Specific error types** - Detailed error information enables pattern detection
4. **Consistent recording** - Regular feedback enables continuous improvement

### For Template Optimization

1. **Regular optimization runs** - Run weekly or monthly to analyze patterns
2. **Review suggestions** - Human judgment combined with data is most effective
3. **Iterative refinement** - Make small improvements based on data
4. **A/B testing** - Try variations and compare performance

## Examples

### Example 1: Bug Fix with Learning Context

```python
generator = PromptGenerator()

# Recent learnings about authentication
learnings = [
    "Use secure session tokens with expiration",
    "Implement rate limiting to prevent brute force",
    "Log authentication failures for security monitoring"
]

prompt, template_id = generator.generate_prompt(
    issue_body="Users are getting logged out unexpectedly",
    category="bug_fix",
    agent="secure-specialist",
    learning_context=learnings
)

# Prompt includes systematic debugging approach + security learnings
```

### Example 2: Feature Development Tracking

```python
# Generate prompt for feature
prompt, template_id = generator.generate_prompt(
    issue_body="Add dark mode support",
    category="feature",
    agent="create-guru"
)

# ... task is completed after 8 hours ...

# Record successful outcome
generator.record_outcome(
    prompt_id=template_id,
    issue_number=789,
    success=True,
    resolution_time_hours=8.0,
    agent_used="create-guru"
)

# Check how well this template performs
report = generator.get_performance_report()
template_stats = report['templates'][template_id]
print(f"Template effectiveness: {template_stats['effectiveness_score']:.2f}")
```

### Example 3: Identifying Problematic Templates

```python
# Run optimization analysis
suggestions = generator.optimize_templates()

for suggestion in suggestions:
    print(f"Template: {suggestion['template_id']}")
    print(f"Issue: {suggestion['issue']}")
    print(f"Recommendation: {suggestion['recommendation']}")
    
    if suggestion['issue'] == 'high_failure_rate':
        # Review common errors and revise template
        errors = suggestion['common_errors']
        print(f"Common errors: {errors}")
```

## Future Enhancements

Potential improvements for the self-improving prompt generator:

1. **A/B Testing** - Automatically test template variations
2. **Agent-Specific Templates** - Customize templates per agent personality
3. **Dynamic Template Generation** - Use LLMs to generate new templates
4. **Cross-Repository Learning** - Share insights across multiple repos
5. **Reinforcement Learning** - Advanced optimization using RL techniques
6. **Natural Language Analysis** - Analyze prompt effectiveness from PR comments

## Troubleshooting

### No templates found
- Check that `tools/data/prompts/` directory exists
- Run generator once to initialize default templates

### Low effectiveness scores
- Need more outcome data (minimum 10 outcomes)
- Review template content for clarity and specificity
- Consider category-specific optimizations

### Templates not improving
- Ensure outcomes are being recorded consistently
- Check that error types are specific (not just "unknown")
- Run optimization analysis regularly

## Contributing

To add new template categories or improve existing ones:

1. Review performance data using `report` command
2. Identify patterns in successful vs. failed outcomes
3. Design improved template based on insights
4. Test new template with real tasks
5. Submit PR with performance comparison

---

**Created by @engineer-master** - Systematic engineering for continuous improvement

**Part of the Chained Autonomous AI Ecosystem** - Where AI evolves itself
