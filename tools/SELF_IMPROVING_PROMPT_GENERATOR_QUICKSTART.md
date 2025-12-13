# Self-Improving Prompt Generator - Quick Start

Get started with the self-improving prompt generator in 5 minutes!

## 🚀 Quick Example

```python
from tools.self_improving_prompt_generator import (
    SelfImprovingPromptGenerator,
    PromptGenerationRequest,
    PromptFeedback
)

# 1. Initialize
generator = SelfImprovingPromptGenerator()

# 2. Generate a prompt
request = PromptGenerationRequest(
    issue_number=123,
    issue_title="Add user authentication",
    issue_body="Implement JWT-based authentication system",
    issue_labels=["feature", "security"],
    agent_name="create-botter"
)

prompt = generator.generate_prompt(request)
print(f"✓ Generated prompt with quality score: {prompt.quality_score:.2f}")
print(prompt.prompt_text)

# 3. After issue is resolved, record feedback
feedback = PromptFeedback(
    prompt_id=prompt.prompt_id,
    success=True,
    resolution_time_hours=16.5
)

generator.record_feedback(feedback)
print("✓ Feedback recorded - system will learn and improve!")

# 4. View performance
report = generator.get_performance_report()
print(f"✓ Success rate: {report['overall_metrics']['success_rate']:.1%}")
```

## 📋 Command Line Usage

```bash
# Generate a prompt
python3 tools/self-improving-prompt-generator.py generate \
  --issue 123 \
  --title "Add authentication" \
  --body "Implement JWT auth" \
  --labels "feature,security" \
  --agent "create-botter"

# Record feedback
python3 tools/self-improving-prompt-generator.py feedback \
  --prompt-id "prompt_123_20251213_101500" \
  --success true \
  --resolution-time 16.5

# View report
python3 tools/self-improving-prompt-generator.py report | jq .

# Refresh learnings
python3 tools/self-improving-prompt-generator.py refresh
```

## 🎯 Key Features

1. **Auto-Categorization**: Detects issue type from labels/title
2. **Learning Integration**: Adds relevant insights from TLDR/HN
3. **Context Adaptation**: Customizes for agent personality
4. **Quality Tracking**: Monitors success rates and improvements
5. **A/B Testing**: Tests variations automatically

## 📊 Performance Metrics

Check prompt effectiveness:

```python
report = generator.get_performance_report()

# Overall metrics
print(f"Success rate: {report['overall_metrics']['success_rate']:.1%}")
print(f"Avg time: {report['overall_metrics']['avg_resolution_time_hours']:.1f}h")

# Template-specific
for template_id, stats in report['templates'].items():
    print(f"{template_id}: {stats['success_rate']:.1%} success")
```

## 🔄 Feedback Loop

The system improves automatically:

1. **Generate** → Creates optimized prompts
2. **Track** → Records outcomes
3. **Learn** → Extracts patterns
4. **Adapt** → Adjusts templates
5. **Repeat** → Gets better over time

## 📁 Data Location

All data stored in `tools/data/prompts/`:
- `templates.json` - Template definitions
- `generated_prompts.json` - Prompt history
- `prompt_feedback.json` - Performance data
- `generator_config.json` - Settings

## 🧪 Testing

```bash
# Run all tests
python3 -m unittest tests.test_self_improving_prompt_generator -v

# Specific test
python3 -m unittest tests.test_self_improving_prompt_generator.TestSelfImprovingPromptGenerator.test_generate_prompt_basic
```

## 📚 Next Steps

1. Read the [full README](SELF_IMPROVING_PROMPT_GENERATOR_README.md)
2. Check [quality scoring details](PROMPT_QUALITY_SCORER_README.md)
3. Explore [learning integration](PROMPT_LEARNING_INTEGRATION_README.md)
4. Review [contextual adaptation](CONTEXTUAL_PROMPT_ADAPTER_README.md)

## 💡 Tips

- Let the system auto-detect categories when possible
- Record feedback consistently for best learning
- Check performance reports weekly
- Enable A/B testing to experiment with variations
- Refresh learnings daily for latest insights

---

Built by **@create-botter** with Tesla-inspired innovation! 🚀
