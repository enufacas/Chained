# Self-Improving Prompt Generator for Copilot

A comprehensive, autonomous system that generates, tracks, and continuously optimizes prompts for GitHub Copilot interactions. Built by **@create-botter** with Tesla-inspired innovation and systematic engineering.

## 🎯 Overview

The Self-Improving Prompt Generator orchestrates multiple components into a unified feedback loop that continuously learns and improves:

```
Generate → Track → Learn → Adapt → Improve → Generate (loop)
```

### Key Features

- **🎨 Template-Based Generation**: Category-specific prompt templates (feature, bug_fix, refactor, etc.)
- **📊 Performance Tracking**: Monitors success rates, resolution times, and quality metrics
- **🧠 Learning Integration**: Extracts insights from TLDR, Hacker News, and past outcomes
- **🎯 Contextual Adaptation**: Customizes prompts for specific agents and issue contexts
- **🔬 A/B Testing**: Tests prompt variations to identify best performers
- **♻️ Feedback Loops**: Automatically improves templates based on outcomes

## 🏗️ Architecture

### Components

The system integrates five existing components plus a new orchestrator:

1. **`self-improving-prompt-generator.py`** (NEW) - Main orchestrator
2. **`prompt-generator.py`** - Base template management and tracking
3. **`prompt_learning_integration.py`** - Learning from TLDR/HN data
4. **`prompt-quality-scorer.py`** - Multi-dimensional quality scoring
5. **`contextual-prompt-adapter.py`** - Agent/issue-specific adaptation
6. **`.github/workflows/prompt-performance-tracker.yml`** - Automated tracking

### Data Flow

```
Issue Created
    ↓
Generate Prompt (orchestrator)
    ├→ Select Template (based on category & performance)
    ├→ Add Learning Insights (recent TLDR/HN trends)
    ├→ Apply Context (agent profile + issue details)
    ├→ A/B Test Variant (if enabled)
    └→ Return Optimized Prompt
    ↓
Copilot Works on Issue
    ↓
Record Feedback (success, time, quality)
    ↓
Auto-Improve Templates (if threshold not met)
    ↓
Performance Report (daily tracking)
```

## 📦 Installation

No installation required - the system is ready to use in the Chained repository.

## 🚀 Usage

### Basic Usage

```python
from self_improving_prompt_generator import (
    SelfImprovingPromptGenerator,
    PromptGenerationRequest,
    PromptFeedback
)

# Initialize generator
generator = SelfImprovingPromptGenerator()

# Generate prompt for an issue
request = PromptGenerationRequest(
    issue_number=123,
    issue_title="Add search feature",
    issue_body="Implement full-text search across the application",
    issue_labels=["feature", "enhancement"],
    agent_name="create-botter",
    category="feature"  # Optional - auto-detected from labels/title
)

prompt = generator.generate_prompt(request)

print(f"Prompt ID: {prompt.prompt_id}")
print(f"Quality Score: {prompt.quality_score:.2f}")
print(f"Learning Insights Used: {prompt.learning_insights_used}")
print("\nPrompt:")
print(prompt.prompt_text)
```

### Recording Feedback

```python
# After issue is resolved, record feedback
feedback = PromptFeedback(
    prompt_id=prompt.prompt_id,
    success=True,
    resolution_time_hours=18.5,
    quality_rating=0.85,  # Optional 0-1 rating
    notes="Great prompt - clear instructions"  # Optional
)

generator.record_feedback(feedback)
```

### Performance Reporting

```python
# Generate comprehensive performance report
report = generator.get_performance_report()

print(f"Total Prompts: {report['total_prompts_generated']}")
print(f"Overall Success Rate: {report['overall_metrics']['success_rate']:.1%}")
print(f"Avg Resolution Time: {report['overall_metrics']['avg_resolution_time_hours']:.1f}h")

# Template-specific metrics
for template_id, stats in report['templates'].items():
    print(f"\n{template_id}:")
    print(f"  Success Rate: {stats['success_rate']:.1%}")
    print(f"  Quality Score: {stats['quality_score']:.2f}")
    print(f"  Uses: {stats['total_uses']}")
```

### CLI Usage

```bash
# Generate a prompt
python3 tools/self-improving-prompt-generator.py generate \
  --issue 123 \
  --title "Add search feature" \
  --body "Implement full-text search" \
  --labels "feature,enhancement" \
  --agent "create-botter"

# Record feedback
python3 tools/self-improving-prompt-generator.py feedback \
  --prompt-id "prompt_123_20251213_101500" \
  --success true \
  --resolution-time 18.5

# View performance report
python3 tools/self-improving-prompt-generator.py report

# Refresh learning insights
python3 tools/self-improving-prompt-generator.py refresh
```

## 📊 Performance Metrics

The system tracks multiple quality dimensions:

### Quality Scoring (0-1 scale)

- **Resolution Score (40%)**: Success rate of issue resolution
- **Efficiency Score (25%)**: Average resolution time
- **Consistency Score (15%)**: Variance in outcomes
- **Learning Score (10%)**: Effectiveness of learning integration
- **Structure Score (10%)**: Template structure quality

### Performance Thresholds

- **Excellent**: ≥ 0.85 (A grade)
- **Good**: 0.70-0.84 (B grade)
- **Acceptable**: 0.60-0.69 (C grade)
- **Needs Improvement**: < 0.60 (D grade)

Templates below the quality threshold (default 0.60) trigger automatic improvement mechanisms.

## 🔬 A/B Testing

Enable A/B testing to experiment with prompt variations:

```python
# Enable A/B testing (enabled by default)
generator.config["ab_testing_enabled"] = True
generator.config["ab_test_traffic_split"] = 0.2  # 20% to test variants

# Create variant for testing
generator.ab_tests["feature_ab_test"] = {
    "variants": [
        {
            "variant_name": "detailed_steps",
            "template_id": "feature_v2",
            "template": "... variant template ..."
        }
    ]
}
```

The system automatically:
1. Routes traffic to variants based on split ratio
2. Tracks performance separately for each variant
3. Promotes high-performing variants to defaults

## 🧠 Learning Integration

The system learns from multiple sources:

### External Learning Sources

- **TLDR**: Daily tech news and trends
- **Hacker News**: Technology discussions and insights
- **GitHub Trending**: Popular repositories and patterns

### Learning Refresh

```python
# Manual refresh
generator._maybe_refresh_learnings()

# Automatic refresh (default: every 24 hours)
generator.config["learning_refresh_interval_hours"] = 24
```

### Learning Insights in Prompts

Relevant insights are automatically added to prompts:

```markdown
## 💡 Recent Insights

Consider these recent learnings when implementing:

- **AI Agent Patterns**: Multi-agent coordination showing strong results
- **Performance Optimization**: New caching strategies reducing latency by 40%
- **Security Best Practices**: Zero-trust architecture gaining adoption
```

## 🎯 Contextual Adaptation

Prompts are automatically adapted based on:

### Agent Profiles

Each agent has a unique personality and approach:

```python
# Prompt for @create-botter (Nikola Tesla-inspired)
# Includes: Visionary thinking, bold solutions, elegant architecture

# Prompt for @secure-specialist (Bruce Schneier-inspired)
# Includes: Security focus, threat modeling, defensive programming
```

### Issue Context

- **Labels**: Complexity warnings, dependency notes, performance flags
- **Keywords**: Technical terms trigger specialization tips
- **Urgency**: Priority issues get speed-focused guidance

## 🔄 Continuous Improvement

### Auto-Improvement Triggers

The system automatically improves when:

1. **Template falls below quality threshold** (< 0.60)
2. **Success rate drops significantly** (> 20% decline)
3. **New learning insights become available**
4. **A/B test variant outperforms default**

### Improvement Mechanisms

- **Template Evolution**: Successful elements propagate to other templates
- **Learning Integration**: High-relevance insights incorporated
- **Variant Promotion**: Winning A/B test variants become defaults
- **Pattern Detection**: Common failure modes trigger template adjustments

## 📁 Data Storage

All data is persisted in `tools/data/prompts/`:

```
tools/data/prompts/
├── templates.json              # Prompt templates and stats
├── generated_prompts.json      # History of generated prompts
├── prompt_feedback.json        # Feedback on prompt performance
├── ab_tests.json               # A/B test configurations
├── generator_config.json       # System configuration
├── learning_insights.json      # Cached learning insights
└── history/                    # Historical reports
    ├── report_20251213_020000.json
    └── summary_20251213_020000.md
```

## 🧪 Testing

Comprehensive test suite with 20+ tests:

```bash
# Run all tests
python3 -m unittest tests.test_self_improving_prompt_generator -v

# Run specific test class
python3 -m unittest tests.test_self_improving_prompt_generator.TestSelfImprovingPromptGenerator -v

# Run integration tests
python3 -m unittest tests.test_self_improving_prompt_generator.TestIntegration -v
```

### Test Coverage

- ✅ Initialization and configuration
- ✅ Prompt generation (basic and advanced)
- ✅ Category detection (labels and title)
- ✅ Feedback recording and persistence
- ✅ Template usage tracking
- ✅ Performance report generation
- ✅ A/B testing functionality
- ✅ Multi-category support
- ✅ Complete workflow integration
- ✅ Persistence across instances

## 🤖 Workflow Integration

The system integrates with GitHub Actions:

### Automated Performance Tracking

`.github/workflows/prompt-performance-tracker.yml` runs daily to:

1. Refresh learning insights from TLDR/HN
2. Generate performance reports
3. Identify optimization opportunities
4. Create PRs with performance updates

### Manual Triggering

```bash
# Trigger performance tracking workflow
gh workflow run "AI: Prompt Performance Tracker" \
  --field days_to_analyze=7 \
  --field refresh_learnings=true
```

## 📈 Success Metrics

Track these metrics to measure system effectiveness:

### Primary Metrics

- **Overall Success Rate**: Target > 75%
- **Average Resolution Time**: Target < 24 hours
- **Quality Score**: Target > 0.75
- **Learning Integration Rate**: Target > 60% of prompts

### Secondary Metrics

- **Template Coverage**: Multiple categories supported
- **Feedback Collection Rate**: Target > 80% of prompts
- **A/B Test Win Rate**: Variants improving defaults
- **Auto-Improvement Rate**: Templates evolving monthly

## 🔧 Configuration

### System Configuration

```python
{
    "ab_testing_enabled": true,
    "ab_test_traffic_split": 0.2,
    "learning_refresh_interval_hours": 24,
    "quality_threshold": 0.6,
    "auto_improve_enabled": true,
    "last_learning_refresh": "2025-12-13T10:00:00+00:00"
}
```

### Template Categories

Current categories:
- `feature`: New functionality
- `bug_fix`: Bug fixes and corrections
- `refactor`: Code improvements
- `documentation`: Documentation updates
- `security`: Security enhancements
- `performance`: Performance optimizations

## 🚀 Future Enhancements

Planned improvements:

1. **🔮 Predictive Quality**: ML model to predict prompt quality before use
2. **🎓 Transfer Learning**: Apply learnings across similar issue types
3. **🌐 Multi-Language Support**: Templates for different programming languages
4. **📱 Real-Time Adaptation**: Adjust prompts based on in-progress feedback
5. **🧩 Template Composition**: Combine best elements from multiple templates

## 🤝 Contributing

When adding new templates or features:

1. Follow existing template structure
2. Include comprehensive tests
3. Update documentation
4. Ensure backward compatibility
5. Test with real issues before deploying

## 📚 Related Documentation

- [Prompt Learning Integration](PROMPT_LEARNING_INTEGRATION_README.md)
- [Prompt Quality Scoring](PROMPT_QUALITY_SCORER_README.md)
- [Contextual Prompt Adapter](CONTEXTUAL_PROMPT_ADAPTER_README.md)
- [Agent System](../.github/agents/README.md)
- [Learning Pipeline](../docs/AUTONOMOUS_SYSTEM_ARCHITECTURE.md)

## 🙏 Acknowledgments

Built by **@create-botter** with inspiration from:
- Nikola Tesla - Visionary innovation
- Margaret Hamilton - Rigorous engineering
- The Chained autonomous AI ecosystem

---

**Part of the Chained autonomous AI learning system** - Continuously evolving through feedback and learning.
