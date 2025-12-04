# Self-Improving Prompt Generator Enhancements

**Created by @create-botter** - Infrastructure enhancements for the autonomous prompt generation system

## Overview

This document describes the enhancements made to the self-improving prompt generator system to create a truly autonomous, continuously improving prompt optimization infrastructure.

## 🆕 New Components

### 1. Prompt Auto-Tuner Workflow

**File:** `.github/workflows/prompt-auto-tuner.yml`

An automated workflow that runs weekly (every Sunday at 3 AM UTC) to:

- **Analyze Performance**: Evaluates all prompt templates based on historical data
- **Identify Issues**: Finds underperforming templates that need optimization
- **Evolve Templates**: Creates improved variants using different mutation strategies
- **Enable A/B Testing**: Sets up experiments to test evolved templates vs originals
- **Auto-Merge Winners**: Automatically promotes better-performing templates

**Key Features:**
- Requires minimum 10 prompts of data before optimizing
- Creates 3 types of mutations: enhance, focus, simplify
- Generates comprehensive tuning reports
- Creates PRs with optimization results
- Fully automated - no human intervention needed

**Manual Triggering:**
```bash
gh workflow run prompt-auto-tuner.yml -f force_evolution=true -f min_effectiveness=0.3
```

### 2. Prompt Quality Scorer

**File:** `tools/prompt-quality-scorer.py`

A sophisticated quality evaluation system that scores prompts on 5 dimensions:

#### Quality Dimensions

1. **Resolution Score (40% weight)**: How often prompts lead to successful outcomes
   - Based on success rate with confidence adjustment
   - New templates regress toward neutral score
   
2. **Efficiency Score (25% weight)**: How quickly issues get resolved
   - <6 hours: Excellent (1.0)
   - 6-24 hours: Good (0.8-1.0)
   - 24-72 hours: Acceptable (0.5-0.8)
   - >72 hours: Poor (0.0-0.5)

3. **Consistency Score (15% weight)**: How stable results are
   - Measures variance in outcomes
   - Considers both success rate and time consistency

4. **Learning Score (10% weight)**: How well learning insights are applied
   - Checks for learning integration in template
   - Compares early vs recent outcomes

5. **Structure Score (10% weight)**: Quality of template structure
   - Clear sections and formatting
   - Agent mentions
   - Lists and organization
   - Actionable instructions
   - Appropriate length

#### Usage

```bash
# Score all templates
python3 tools/prompt-quality-scorer.py score

# Generate quality report
python3 tools/prompt-quality-scorer.py report

# Score specific template
python3 tools/prompt-quality-scorer.py template --template-id bug_fix_systematic
```

#### Output Format

```json
{
  "generated_at": "2025-11-24T12:00:00Z",
  "total_templates": 6,
  "templates": [
    {
      "template_id": "bug_fix_systematic",
      "overall_quality": 0.847,
      "scores": {
        "resolution": 0.920,
        "efficiency": 0.850,
        "consistency": 0.780,
        "learning": 0.700,
        "structure": 0.800
      },
      "sample_size": 42,
      "grade": "A-"
    }
  ],
  "summary": {
    "avg_quality": 0.675,
    "highest_quality": 0.847,
    "lowest_quality": 0.450,
    "grades": {
      "A-": 1,
      "B+": 2,
      "C": 3
    }
  }
}
```

### 3. Contextual Prompt Adapter

**File:** `tools/contextual-prompt-adapter.py`

Enhances prompts based on agent specialization, issue context, and repository state.

#### Adaptation Factors

1. **Agent Personality**: Adds personality-appropriate guidance
   - Nikola Tesla: Visionary, innovative approach
   - Grace Hopper: Pragmatic pioneer
   - Margaret Hamilton: Mission-critical rigor
   - Edsger Dijkstra: Elegant efficiency
   - Rich Hickey: Thoughtful design
   - Alan Turing: Systematic collaboration

2. **Specialization Tips**: Context-specific best practices
   - Infrastructure: Scalability, reusability, developer experience
   - Performance: Profiling, measurement, maintainability
   - Testing: Edge cases, documentation, coverage
   - Security: Input validation, least privilege, assumptions
   - Refactoring: Behavior preservation, incremental changes
   - Documentation: Examples, structure, audience

3. **Contextual Notes**: Issue-specific warnings
   - Complexity warnings
   - Dependency checks
   - Performance considerations
   - Breaking change alerts
   - First-time contributor guidance

#### Usage

```bash
# Adapt prompt for specific agent
python3 tools/contextual-prompt-adapter.py create-botter \
  --prompt "Implement this feature: {issue_body}" \
  --labels "feature,infrastructure" \
  --title "Add new infrastructure component" \
  --body "We need async task handling"
```

#### Integration with Prompt Generator

The contextual adapter can be integrated into the existing `prompt-generator.py`:

```python
from contextual_prompt_adapter import ContextualPromptAdapter

adapter = ContextualPromptAdapter()
enhanced_prompt = adapter.enhance_prompt_with_context(
    base_prompt,
    agent_name="create-botter",
    issue_title=title,
    issue_labels=labels,
    issue_body=body
)
```

## 🔄 How It All Works Together

### The Self-Improvement Loop

```
1. GENERATE
   ↓
   Prompt generator creates optimized prompts
   Using best templates + learning insights + contextual adaptation
   
2. EXECUTE
   ↓
   Agents use prompts to resolve issues
   Outcomes are recorded (success/failure, time, errors)
   
3. MEASURE
   ↓
   Quality scorer evaluates template performance
   Calculates multi-dimensional quality metrics
   
4. OPTIMIZE
   ↓
   Auto-tuner identifies improvement opportunities
   Evolves underperforming templates
   
5. TEST
   ↓
   A/B testing compares variants
   Best performers automatically selected
   
6. LEARN
   ↓
   Insights feed back to prompt generator
   System gets smarter with each iteration
```

### Data Flow

```
Issue Created
    ↓
[Prompt Generator]
    ↓
Base Template Selected (by category)
    ↓
[Contextual Adapter]
    ↓
Enhanced with Agent/Issue Context
    ↓
[Learning Integration]
    ↓
Enriched with Recent Insights
    ↓
Final Optimized Prompt
    ↓
Agent Resolves Issue
    ↓
Outcome Recorded
    ↓
[Quality Scorer]
    ↓
Template Performance Evaluated
    ↓
[Auto-Tuner] (weekly)
    ↓
Templates Evolved & A/B Tests Created
    ↓
[Selection] (automatic)
    ↓
Best Templates Used Going Forward
```

## 📊 Performance Tracking

### Metrics Collected

- **Success Rate**: Percentage of successful outcomes per template
- **Resolution Time**: Average time to resolve issues
- **Consistency**: Variance in outcomes
- **Learning Effectiveness**: Impact of learning integration
- **Structure Quality**: Template organization and clarity

### Quality Grades

| Grade | Score Range | Description |
|-------|-------------|-------------|
| A+    | 0.90-1.00  | Exceptional performance |
| A     | 0.85-0.90  | Excellent |
| A-    | 0.80-0.85  | Very Good |
| B+    | 0.75-0.80  | Good |
| B     | 0.70-0.75  | Above Average |
| B-    | 0.65-0.70  | Average |
| C+    | 0.60-0.65  | Below Average |
| C     | 0.55-0.60  | Needs Improvement |
| C-    | 0.50-0.55  | Poor |
| D     | <0.50      | Failing |

## 🧪 Testing

Comprehensive test suite in `tests/test_prompt_generator_enhancements.py`:

```bash
# Run all tests
python3 tests/test_prompt_generator_enhancements.py

# Tests cover:
# - Quality scorer initialization
# - Quality scoring with sample data
# - Quality report generation
# - Contextual adapter initialization
# - Prompt adaptation for agents
# - Full contextual enhancement
```

All tests pass with 100% success rate.

## 🚀 Getting Started

### 1. Ensure Data Directory Exists

```bash
mkdir -p tools/data/prompts
```

### 2. Generate Initial Prompts

```bash
python3 tools/prompt-generator.py generate \
  --issue-body "Fix authentication bug" \
  --category bug_fix \
  --agent engineer-master
```

### 3. Record Outcomes

```bash
python3 tools/prompt-generator.py record \
  --prompt-id bug_fix_systematic \
  --issue-number 123 \
  --success \
  --resolution-time 8.5
```

### 4. Check Quality Scores

```bash
python3 tools/prompt-quality-scorer.py report
```

### 5. Let Auto-Tuner Optimize

The workflow runs automatically every Sunday, or trigger manually:

```bash
gh workflow run prompt-auto-tuner.yml
```

## 🎯 Benefits

### For the System

1. **Continuous Improvement**: Templates get better over time automatically
2. **Data-Driven**: Decisions based on real performance metrics
3. **Autonomous**: No manual intervention required
4. **Adaptive**: Learns from both successes and failures
5. **Scalable**: Handles growing template library efficiently

### For Agents

1. **Better Instructions**: Higher quality prompts lead to better outcomes
2. **Personalized**: Adapted to agent personality and specialization
3. **Contextual**: Takes issue specifics into account
4. **Current**: Integrates latest tech insights

### For the Repository

1. **Higher Success Rate**: Better prompts = more successful resolutions
2. **Faster Resolution**: Optimized prompts reduce time-to-fix
3. **Consistent Quality**: Reduced variance in outcomes
4. **Documented Evolution**: Full history of improvements

## 🔮 Future Enhancements

Potential areas for further improvement:

1. **Multi-Agent Prompts**: Optimize prompts for agent collaboration
2. **Reinforcement Learning**: More sophisticated learning algorithms
3. **Predictive Optimization**: Anticipate what prompts will be needed
4. **Cross-Repository Learning**: Learn from multiple repositories
5. **Real-time Adaptation**: Adjust prompts during issue resolution

## 📚 Related Documentation

- [Prompt Generator Original](../tools/prompt-generator.py)
- [Learning Integration](../tools/prompt_learning_integration.py)
- [Reinforcement Learning](../tools/prompt_reinforcement.py)
- [Workflow Integration](../.github/workflows/prompt-generator-integration.yml)
- [Performance Tracker](../.github/workflows/prompt-performance-tracker.yml)

## 🤝 Contributing

To add new features to the self-improving prompt system:

1. Follow the existing patterns for data storage
2. Add comprehensive tests
3. Update this documentation
4. Ensure integration with auto-tuner workflow
5. Test with real issue data before deploying

---

**@create-botter** - Building infrastructure that evolves itself, inspired by the vision of Nikola Tesla
