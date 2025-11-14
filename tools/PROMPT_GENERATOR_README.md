# Self-Improving Prompt Generator

A self-improving prompt generator for GitHub Copilot interactions that learns from outcomes and continuously optimizes prompt quality.

**Enhanced by @engineer-master** with advanced learning integration, template evolution, and A/B testing capabilities.

## Overview

The Self-Improving Prompt Generator is part of the Chained autonomous AI ecosystem. It generates optimized prompts for different types of tasks (bug fixes, features, refactoring, etc.) and tracks their performance to continuously improve effectiveness.

### New in v2.0 (Enhanced by @engineer-master)

- 🧠 **Learning Integration**: Automatically extracts insights from TLDR and Hacker News
- 🧬 **Template Evolution**: Generates improved template variations based on performance data
- 🔬 **A/B Testing**: Systematically tests template variations to identify best performers
- 📊 **Advanced Analytics**: Tracks trending topics and their relevance to prompting
- 🎯 **Context-Aware Enhancement**: Incorporates recent tech trends into prompts
- 🔄 **Continuous Improvement**: Self-optimizes based on success/failure patterns

## Features

### Core Features
- **Template-Based Generation**: Uses proven templates for different task categories
- **Performance Tracking**: Monitors success rates, resolution times, and outcomes
- **Self-Improvement**: Learns from successes and failures to optimize templates
- **Agent Integration**: Customizes prompts for specific agents (engineer-master, create-guru, etc.)
- **Effectiveness Scoring**: Evaluates templates based on multiple performance metrics

### Enhanced Features (v2.0)
- **Learning Integration**: Extracts insights from TLDR Tech and Hacker News automatically
- **Trend Analysis**: Identifies trending technologies and incorporates them into prompts
- **Template Evolution**: Creates enhanced/simplified/focused variations of templates
- **A/B Testing Framework**: Compare template variants to determine best performers
- **Context-Aware Prompting**: Adds relevant recent learnings to prompts automatically
- **Predictive Scoring**: Calculates relevance scores for learning insights

## Installation

No additional dependencies required beyond the base Chained requirements:

```bash
pip install -r requirements.txt
```

The enhanced features require access to the `learnings/` directory for extracting TLDR insights.

## Usage

### Command Line Interface

The tool provides a CLI with enhanced commands:

#### Generate a Prompt (with Learning Integration)

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

**Recent Relevant Learnings:**
1. GPT-5.1 🤖, Waymo hits highways 🚗, Homebrew 5 👨‍💻
2. Elon $1T comp approved 💰, Google TPUs threaten Nvidia ⚡, agents from scratch 👨‍💻

Consider these recent insights from the tech community when approaching this task.
```

#### Refresh Learning Insights

Extract and analyze recent learnings from TLDR files:

```bash
python3 tools/prompt-generator.py refresh-learnings --days 7
```

**Output:**
```
Refreshing learnings from last 7 days...
Total insights: 206
Categories: {'ai_ml': 140, 'feature': 30, 'security': 15, ...}
```

#### Evolve a Template

Create an enhanced version of an existing template:

```bash
python3 tools/prompt-generator.py evolve \
  --template-id bug_fix_systematic \
  --mutation enhance
```

**Output:**
```
Created evolved template: bug_fix_systematic_enhance_v2
Category: bug_fix

Template text preview:
**@engineer-master** - Please fix this bug using a systematic approach:
...
**Additional Debugging Steps:**
- Check logs for stack traces
- Verify input validation
- Review recent code changes
```

#### Enable A/B Testing

Compare two templates to determine which performs better:

```bash
# Start a new A/B test
python3 tools/prompt-generator.py ab-test \
  --template-a bug_fix_systematic \
  --template-b bug_fix_systematic_enhance_v2
```

**Output:**
```json
{
  "test_id": "ab_bug_fix_systematic_vs_bug_fix_systematic_enhance_v2",
  "template_a": "bug_fix_systematic",
  "template_b": "bug_fix_systematic_enhance_v2",
  "start_date": "2025-11-14T16:30:00+00:00",
  "status": "active"
}
```

Get A/B test results:

```bash
python3 tools/prompt-generator.py ab-test \
  --test-id ab_bug_fix_systematic_vs_bug_fix_systematic_enhance_v2
```

**Output:**
```json
{
  "test_id": "ab_bug_fix_systematic_vs_bug_fix_systematic_enhance_v2",
  "results": {
    "a_effectiveness": 0.82,
    "b_effectiveness": 0.87,
    "winner": "b"
  }
}
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

Use the generator programmatically with enhanced features:

```python
from prompt_generator import PromptGenerator
from prompt_learning_integration import PromptLearningIntegrator

# Initialize with learning integration enabled
generator = PromptGenerator(enable_learning=True)

# Generate a prompt with automatic learning enhancement
prompt, template_id = generator.generate_prompt(
    issue_body="Implement user profile feature with OAuth2",
    category="feature",
    agent="create-guru",
    enable_learning_enhancement=True  # Automatically adds relevant learnings
)

print(f"Using template: {template_id}")
print(prompt)

# Manually refresh learnings from TLDR
generator._refresh_learnings(days=7)

# Evolve a template based on performance data
new_template = generator.evolve_template(
    template_id="feature_rigorous",
    mutation_type="enhance"
)

if new_template:
    print(f"Evolved template: {new_template.template_id}")

# Enable A/B testing between templates
ab_config = generator.enable_ab_testing(
    "feature_rigorous",
    "feature_rigorous_enhance_v2"
)
print(f"A/B test started: {ab_config['test_id']}")

# Record outcome after task completion
generator.record_outcome(
    prompt_id=template_id,
    issue_number=456,
    success=True,
    resolution_time_hours=6.5,
    agent_used="create-guru"
)

# Get performance report with learning insights
report = generator.get_performance_report()
print(f"Overall success rate: {report['insights']['overall']['success_rate']:.2%}")
print(f"Learning insights collected: {report['insights']['learning_integration']['total_insights']}")
```

### Learning Integration API

Use the learning integrator independently:

```python
from prompt_learning_integration import PromptLearningIntegrator

# Initialize integrator
integrator = PromptLearningIntegrator()

# Extract recent learnings from TLDR
insights = integrator.extract_learnings_from_tldr(days=7)
print(f"Extracted {len(insights)} insights")

# Get relevant insights for a specific category
relevant = integrator.get_relevant_insights(
    prompt_category="bug_fix",
    limit=5,
    min_relevance=0.6
)

for insight in relevant:
    print(f"- {insight.title} (relevance: {insight.relevance_score:.2f})")

# Analyze trending topics
trends = integrator.analyze_trending_topics(days=7)
print(f"Top keywords: {[k['keyword'] for k in trends['top_keywords'][:5]]}")

# Generate prompt enhancements
enhancements = integrator.generate_prompt_enhancements(
    prompt_category="feature",
    base_prompt="Implement new feature",
    max_enhancements=3
)

for enhancement in enhancements:
    print(f"Enhancement: {enhancement}")

# Get learning statistics
stats = integrator.get_learning_statistics()
print(f"Total insights: {stats['total_insights']}")
print(f"Average relevance: {stats['avg_relevance_score']:.2f}")
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

1. **Agent-Specific Templates** - Customize templates per agent personality *(partially implemented)*
2. **Dynamic Template Generation** - Use LLMs to generate new templates from scratch
3. **Cross-Repository Learning** - Share insights across multiple repos
4. **Reinforcement Learning** - Advanced optimization using RL techniques
5. **Natural Language Analysis** - Analyze prompt effectiveness from PR comments
6. **Multi-Model Support** - Optimize prompts for different LLMs (GPT-4, Claude, etc.)

## New Features in v2.0

### Learning Integration System

**@engineer-master** implemented a comprehensive learning integration system that:

- **Extracts Insights**: Automatically parses TLDR Tech and Hacker News data
- **Categorizes Content**: Classifies learnings into relevant categories (ai_ml, bug_fix, feature, etc.)
- **Scores Relevance**: Calculates 0-1 relevance scores for each insight
- **Tracks Trends**: Identifies trending keywords and technologies
- **Enhances Prompts**: Adds relevant recent learnings to generated prompts

**Key Classes:**
- `LearningInsight`: Dataclass representing a single learning insight
- `PromptLearningIntegrator`: Main class for learning integration

**Usage Example:**
```python
integrator = PromptLearningIntegrator()

# Extract learnings from last 7 days
insights = integrator.extract_learnings_from_tldr(days=7)

# Get insights relevant to bug fixing
bug_insights = integrator.get_relevant_insights("bug_fix", limit=5)

# Analyze trending topics
trends = integrator.analyze_trending_topics(days=7)
```

### Template Evolution Engine

The evolution engine creates improved template variations based on performance data:

**Mutation Types:**
1. **Enhance**: Adds more specific guidance and best practices
2. **Simplify**: Removes verbose explanations for faster execution
3. **Focus**: Emphasizes critical aspects based on learnings

**Requirements:**
- Template must have 10+ uses for safe evolution
- Maintains category and core structure
- Creates versioned templates (e.g., `bug_fix_systematic_enhance_v2`)

**Usage Example:**
```python
generator = PromptGenerator()

# Evolve a template
evolved = generator.evolve_template(
    template_id="bug_fix_systematic",
    mutation_type="enhance"
)

if evolved:
    print(f"Created: {evolved.template_id}")
```

### A/B Testing Framework

Systematically test template variations to identify best performers:

**Features:**
- Compare any two templates head-to-head
- Track usage counts and success rates
- Calculate effectiveness scores automatically
- Determine winning template based on data

**Usage Example:**
```python
generator = PromptGenerator()

# Start A/B test
config = generator.enable_ab_testing(
    template_id_a="bug_fix_systematic",
    template_id_b="bug_fix_systematic_enhance_v2"
)

# ... use templates and record outcomes ...

# Get results
results = generator.get_ab_test_results(config["test_id"])
print(f"Winner: Template {results['results']['winner']}")
```

### Context-Aware Prompting

Prompts are automatically enhanced with relevant recent learnings:

**How It Works:**
1. Extract recent insights from TLDR/HN data
2. Calculate relevance score for each insight
3. Select top 3 most relevant insights
4. Append to prompt with proper formatting

**Example Output:**
```
**@engineer-master** - Please implement this feature...

**Recent Relevant Learnings:**
1. GPT-5.1 🤖, Waymo hits highways 🚗, Homebrew 5 👨‍💻
2. MSFT OpenAI docs leak 📄, GPT-5.1 🤖, Anthropic's $50B Bet 💰
3. ChatGPT Group Chats 💬, growing an RL environment 🌍, ElevenLabs Scribe v2 🗣

Consider these recent insights from the tech community when approaching this task.
```

### Advanced Analytics

**Learning Statistics:**
- Total insights collected
- Category distribution
- Average relevance scores
- Trending topics and keywords

**Template Performance:**
- Success rate per template
- Effectiveness scores
- Resolution time averages
- Common failure patterns

**Optimization Suggestions:**
- Identifies underperforming templates
- Detects high failure rates
- Recommends improvements
- Tracks error patterns

## Architecture

### Component Overview

```
┌─────────────────────────────────────────────────────────┐
│          Self-Improving Prompt Generator                 │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  ┌──────────────────┐      ┌─────────────────────┐     │
│  │ PromptGenerator  │◄─────┤ Learning Integrator │     │
│  │                  │      │                     │     │
│  │ - Templates      │      │ - TLDR Parser       │     │
│  │ - Outcomes       │      │ - Trend Analyzer    │     │
│  │ - Insights       │      │ - Relevance Scorer  │     │
│  └────────┬─────────┘      └─────────────────────┘     │
│           │                                              │
│           ├── Template Evolution Engine                  │
│           │   ├── Enhance Mutation                      │
│           │   ├── Simplify Mutation                     │
│           │   └── Focus Mutation                        │
│           │                                              │
│           ├── A/B Testing Framework                      │
│           │   ├── Test Configuration                    │
│           │   ├── Performance Tracking                  │
│           │   └── Winner Determination                  │
│           │                                              │
│           └── Performance Analytics                      │
│               ├── Success Rate Calculation              │
│               ├── Effectiveness Scoring                 │
│               └── Optimization Suggestions              │
│                                                           │
└─────────────────────────────────────────────────────────┘
```

### Data Flow

1. **Learning Extraction**: TLDR/HN → Insights → Categorization → Relevance Scoring
2. **Prompt Generation**: Issue → Template Selection → Learning Enhancement → Output
3. **Outcome Recording**: Result → Metrics Update → Insights Analysis → Optimization
4. **Template Evolution**: Performance Data → Mutation → New Template → A/B Test

## Troubleshooting

### Learning Integration Issues

**Timestamps mismatch warning:**
```
Warning: Could not process tldr_*.json: can't compare offset-naive and offset-aware datetimes
```
- **Cause**: Old TLDR files with inconsistent timestamp formats
- **Impact**: Files are skipped, no data loss
- **Fix**: Not needed, system handles gracefully

**No learning integration available:**
```
Warning: Could not initialize learning integration
```
- **Cause**: Import error or missing learnings directory
- **Impact**: Generator works but without learning enhancements
- **Fix**: Check that `learnings/` directory exists and is accessible

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
5. Use A/B testing to compare with existing templates
6. Submit PR with performance comparison

**For Learning Integration:**
1. Add new learning sources to `PromptLearningIntegrator`
2. Implement parser for the new source
3. Update categorization keywords
4. Test relevance scoring
5. Submit PR with examples

---

**Created by @engineer-master** - Systematic engineering for continuous improvement

**Enhanced in v2.0 by @engineer-master** - Learning integration, template evolution, and A/B testing

**Part of the Chained Autonomous AI Ecosystem** - Where AI evolves itself
