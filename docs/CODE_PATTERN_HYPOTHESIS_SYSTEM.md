# AI Code Pattern Hypothesis Testing System

**Created by:** @create-botter  
**Category:** AI Learning & Pattern Discovery  
**Status:** Production Ready

## 🎯 Overview

The AI Code Pattern Hypothesis Testing System is an autonomous system that generates and tests hypotheses about code patterns in the repository. It discovers insights about code quality, maintainability, and best practices using statistical analysis and machine learning concepts.

### What It Does

1. **🤖 Generates Hypotheses**: Automatically creates testable hypotheses about code patterns
2. **🔬 Tests Scientifically**: Validates hypotheses using statistical analysis on real codebase data
3. **📊 Learns Continuously**: Tracks results over time to improve understanding
4. **💡 Creates Issues**: Automatically creates GitHub issues for validated insights
5. **📈 Integrates Learning**: Feeds discoveries back into the autonomous learning system

## 🌟 Key Features

### Automated Discovery

The system runs automatically every Sunday at 6 AM UTC, analyzing your codebase to discover:

- **Correlation Patterns**: "Functions with X tend to have Y"
- **Threshold Patterns**: "Functions exceeding N in metric X tend to have issue Y"
- **Naming Patterns**: "Functions with pattern X have characteristic Y"

### Scientific Validation

Each hypothesis is rigorously tested:

- Statistical correlation analysis
- Threshold group comparisons
- Pattern impact assessment
- Confidence scores and p-values

### Actionable Insights

Results are automatically converted to:

- **GitHub Issues**: For validated hypotheses requiring action
- **Learning Entries**: Fed into the autonomous learning system
- **PR with Results**: Complete analysis saved to repository
- **Summary Reports**: Markdown summaries in GitHub Actions

## 📋 Architecture

### Components

```
┌─────────────────────────────────────────────────┐
│   GitHub Actions Workflow (Orchestrator)        │
│   .github/workflows/code-pattern-hypothesis-    │
│   testing.yml                                    │
└─────────────────┬───────────────────────────────┘
                  │
                  ├──> Hypothesis Testing Engine
                  │    tools/hypothesis_testing_engine.py
                  │    ├─ CodeAnalyzer
                  │    ├─ HypothesisGenerator
                  │    ├─ HypothesisTester
                  │    └─ Results Storage
                  │
                  ├──> Issue Creator
                  │    (Creates issues for validated hypotheses)
                  │
                  ├──> Learning System Integration
                  │    (Adds to learnings/hypothesis_testing/)
                  │
                  └──> PR Creator
                       (Commits results to repository)
```

### Data Flow

1. **Trigger**: Schedule (weekly) or manual dispatch
2. **Analyze**: Extract metrics from Python files in repository
3. **Generate**: Create hypotheses based on metric patterns
4. **Test**: Validate hypotheses against code metrics
5. **Report**: Create issues, PRs, and learning entries
6. **Store**: Save results to `learnings/hypothesis_testing/`

## 🚀 Usage

### Automatic Execution

The system runs automatically every Sunday at 6 AM UTC. No action required!

### Manual Execution

Trigger manually from GitHub Actions:

```bash
# Navigate to: Actions > AI Code Pattern Hypothesis Testing > Run workflow

# Parameters:
# - num_hypotheses: Number to generate (default: 15)
# - max_files: Maximum files to analyze (default: 150)
# - create_issues: Create issues for validated hypotheses (default: true)
```

Or via GitHub CLI:

```bash
gh workflow run code-pattern-hypothesis-testing.yml \
  -f num_hypotheses=20 \
  -f max_files=200 \
  -f create_issues=true
```

### Direct Tool Usage

Run the hypothesis testing engine directly:

```bash
python3 tools/hypothesis_testing_engine.py \
  --num-hypotheses 15 \
  --max-files 150 \
  --output learnings/hypothesis_testing/results.json
```

## 📊 Output Structure

### Results File

Saved to `learnings/hypothesis_testing/results_YYYYMMDD_HHMMSS.json`:

```json
{
  "generated_at": "2025-11-24T06:00:00+00:00",
  "repository": ".",
  "metrics_analyzed": 150,
  "hypotheses_generated": 15,
  "hypotheses_validated": 5,
  "validation_rate": 0.33,
  "hypotheses": [
    {
      "hypothesis_id": "hyp_complexity_quality_1",
      "description": "Functions with high cyclomatic_complexity tend to have lower test_coverage",
      "hypothesis_type": "correlation",
      "validated": true,
      "confidence": 0.85,
      "p_value": 0.02,
      "sample_size": 150,
      "supporting_examples": [...]
    }
  ],
  "summary": {
    "top_validated_hypotheses": [...],
    "insights": [...]
  }
}
```

### Summary File

Markdown summary at `learnings/hypothesis_testing/results_YYYYMMDD_HHMMSS_summary.md`:

```markdown
## 🔬 AI Code Pattern Hypothesis Testing Results

**Run Date:** 2025-11-24
**Repository:** .

### 📊 Statistics
- **Functions Analyzed:** 150
- **Hypotheses Generated:** 15
- **Hypotheses Validated:** 5
- **Validation Rate:** 33.3%

### 🏆 Top Validated Hypotheses
1. **Functions with high cyclomatic_complexity tend to have lower test_coverage**
   - Confidence: 85.0%
   - Sample Size: 150

### 💡 Actionable Insights
- Consider refactoring functions with complexity > 10
- Add tests for complex functions
```

### Learning Log

Append-only log at `learnings/hypothesis_testing/learning_log.jsonl`:

```jsonl
{"timestamp": "2025-11-24T06:00:00+00:00", "type": "hypothesis_testing", "metrics": {...}}
```

### GitHub Issues

For each top validated hypothesis, an issue is created:

```
Title: 💡 Code Pattern Insight: Functions with high cyclomatic_complexity tend to...

Labels: ai-insight, code-pattern, automated
```

## 🧪 Testing

Run the test suite:

```bash
python3 tests/test_code_pattern_hypothesis_workflow.py
```

Tests cover:

- Workflow component integration
- Hypothesis validation logic
- Results format verification
- Learning system integration
- Issue creation data format

## 🔍 Example Hypotheses

The system can generate and test hypotheses like:

### Correlation Hypotheses

- "Functions with high cyclomatic_complexity tend to have lower test_coverage"
- "Functions with many parameters tend to have higher error_rate"
- "Functions with type_hints have fewer runtime_errors"

### Threshold Hypotheses

- "Functions exceeding 50 lines tend to have multiple responsibilities"
- "Functions exceeding 5 parameters tend to have poor cohesion"
- "Functions exceeding 10 cyclomatic_complexity have testing difficulties"

### Pattern Hypotheses

- "Functions with short naming have lower docstring_quality"
- "Functions with clear naming have better maintainability"

## 💡 Actionable Insights

When a hypothesis is validated, the system generates actionable insights:

- **Refactoring Recommendations**: Specific functions to improve
- **Coding Guidelines**: Patterns to follow or avoid
- **Quality Metrics**: Thresholds to maintain
- **Test Coverage**: Areas needing more tests

## 📈 Integration with Learning System

Results are integrated into the autonomous learning system:

1. **Learning Log**: Each run adds an entry to `learning_log.jsonl`
2. **Pattern Discovery**: Hypotheses inform pattern recognition
3. **Code Quality**: Insights improve code review criteria
4. **Agent Training**: Validated patterns train other agents

## 🎯 Success Metrics

Track the effectiveness of the system:

- **Validation Rate**: Percentage of hypotheses validated
- **Insight Quality**: Number of actionable insights generated
- **Issue Resolution**: Percentage of created issues resolved
- **Code Improvement**: Measurable quality improvements over time

## 🔧 Configuration

### Workflow Parameters

Edit `.github/workflows/code-pattern-hypothesis-testing.yml`:

```yaml
# Schedule (cron)
schedule:
  - cron: '0 6 * * 0'  # Every Sunday at 6 AM UTC

# Default parameters
inputs:
  num_hypotheses:
    default: '15'  # Number of hypotheses to generate
  max_files:
    default: '150'  # Maximum files to analyze
  create_issues:
    default: 'true'  # Create issues for validated hypotheses
```

### Hypothesis Templates

Customize in `tools/hypothesis_testing_engine.py`:

```python
def _load_templates(self) -> List[Dict]:
    return [
        {
            'id': 'your_template',
            'template': 'Your hypothesis template',
            'type': 'correlation',
            'combinations': [...]
        }
    ]
```

## 🚦 Workflow Steps

1. **Checkout**: Clone repository
2. **Setup Python**: Install Python 3.11
3. **Run Hypothesis Testing**: Execute engine
4. **Generate Summary**: Create markdown summary
5. **Create Issues**: Generate issues for validated hypotheses
6. **Commit Results**: Create PR with results
7. **Update Learning**: Add to learning log
8. **Workflow Summary**: Display summary in GitHub Actions

## 📝 Best Practices

### For Developers

- **Review Issues**: Check AI-generated issues weekly
- **Validate Insights**: Confirm hypotheses match reality
- **Act on Recommendations**: Implement suggested improvements
- **Provide Feedback**: Comment on issues with your findings

### For Maintainers

- **Monitor Validation Rate**: Should be 20-40% typically
- **Review Top Hypotheses**: Focus on high-confidence findings
- **Track Improvements**: Measure code quality changes over time
- **Adjust Parameters**: Tune based on repository size and needs

## 🔄 Continuous Improvement

The system improves over time by:

1. **Learning from Validation**: Failed hypotheses inform future generation
2. **Tracking Patterns**: Successful patterns are prioritized
3. **Metric Refinement**: Code metrics evolve with discoveries
4. **Template Expansion**: New hypothesis types added based on findings

## 🛠️ Troubleshooting

### Low Validation Rate

If validation rate is < 10%:

- Increase `max_files` to analyze more code
- Review hypothesis templates for relevance
- Check if codebase has sufficient complexity for patterns

### No Issues Created

If no issues are created:

- Verify `create_issues` parameter is `true`
- Check that some hypotheses were validated
- Review GitHub token permissions

### Missing Results

If results files are not created:

- Check workflow logs for Python errors
- Verify `learnings/hypothesis_testing/` directory exists
- Ensure sufficient disk space

## 🌐 Related Systems

This system integrates with:

- **Code Archaeologist**: Pattern analysis across time
- **PR Failure Intelligence**: Learning from failed PRs
- **Agent Evolution System**: Training specialized agents
- **Universal Truth Evaluator**: Validating code principles

## 🎓 Learn More

- **Hypothesis Testing Engine**: `tools/HYPOTHESIS_TESTING_ENGINE_README.md`
- **Learning System**: `learnings/README.md`
- **Agent System**: `.github/agents/README.md`
- **Workflow Documentation**: `docs/WORKFLOWS.md`

## 📄 License

Part of the Chained autonomous AI ecosystem.

---

**Created by @create-botter** - Visionary infrastructure inspired by Nikola Tesla 🔬✨

*"The present is theirs; the future, for which I really worked, is mine." - Nikola Tesla*
