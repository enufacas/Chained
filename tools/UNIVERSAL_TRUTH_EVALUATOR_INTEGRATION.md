# 🌌 Universal Truth Evaluator - Integration Guide

## Quick Integration

### 1. Add to Existing Workflows

The Universal Truth Evaluator can be integrated into any workflow that analyzes system behavior:

```yaml
# In your workflow
- name: Discover Universal Truths
  run: |
    python3 tools/universal_truth_evaluator.py
    
    # Access results
    if [ -f world/universal_truths.json ]; then
      echo "Truths discovered:"
      jq '.total_truths' world/universal_truths.json
    fi
```

### 2. Use in Python Scripts

```python
from tools.universal_truth_evaluator import UniversalTruthEvaluator

# Initialize
evaluator = UniversalTruthEvaluator()

# Run discovery
insights = evaluator.run_full_discovery()

# Access specific truths
for truth_id, truth in evaluator.truths.items():
    if truth.confidence > 0.8:
        print(f"High confidence: {truth.statement}")

# Get recommendations
for rec in insights['recommendations']:
    print(f"Action: {rec}")
```

### 3. Scheduled Discovery

The included workflow (`discover-universal-truths.yml`) runs daily at 6 AM UTC:

- Discovers new truths
- Creates PR with findings
- Optionally creates issue with summary
- Generates insights report

### 4. Custom Truth Discovery

Create domain-specific truth discovery:

```python
from tools.universal_truth_evaluator import UniversalTruthEvaluator

evaluator = UniversalTruthEvaluator()

# Add custom truth
custom_truth = evaluator._create_or_update_truth(
    truth_id='my_custom_truth',
    category='agent_behavior',
    statement='Custom observation about agents',
    confidence=0.75,
    evidence={'my_data': [1, 2, 3]}
)

# Save
evaluator._save_truths()
```

## Use Cases

### System Health Monitoring

```python
evaluator = UniversalTruthEvaluator()
insights = evaluator.run_full_discovery()

# Check system health
stability_ratio = insights['stable_truths'] / insights['total_truths']
if stability_ratio < 0.5:
    print("WARNING: System showing unstable behavior")
```

### Agent Performance Optimization

```python
# Find performance-related truths
perf_truths = [
    t for t in evaluator.truths.values()
    if 'performance' in t.truth_id and t.confidence > 0.8
]

# Apply insights
for truth in perf_truths:
    print(f"Optimization opportunity: {truth.statement}")
```

### Predictive Analysis

```python
# Find stable patterns for prediction
stable_patterns = [
    t for t in evaluator.truths.values()
    if t.is_stable() and t.category == 'system_dynamics'
]

# Use for forecasting
for pattern in stable_patterns:
    print(f"Predictable pattern: {pattern.statement}")
```

### Research & Documentation

```python
insights = evaluator.generate_insights()

# Generate research report
print("## System Principles")
for discovery in insights['key_discoveries']:
    print(f"- {discovery['statement']}")
```

## Data Flow

```
External Data Sources
        │
        ▼
[Universal Truth Evaluator]
        │
        ├─► world/universal_truths.json
        ├─► analysis/universal_truths_insights.json
        └─► GitHub Issue (optional)
```

## Output Schema

### Truths Database (`world/universal_truths.json`)

```json
{
  "version": "1.0.0",
  "last_updated": "2025-11-22T04:00:00Z",
  "total_truths": 7,
  "truths": {
    "truth_id": {
      "truth_id": "string",
      "category": "agent_behavior | system_dynamics | collaboration | evolution",
      "statement": "string",
      "confidence": 0.0-1.0,
      "evidence_count": 0,
      "first_observed": "ISO timestamp",
      "last_validated": "ISO timestamp",
      "supporting_data": [...],
      "counter_examples": [...],
      "evolution_history": [...],
      "related_truths": [...]
    }
  }
}
```

### Insights Report (`analysis/universal_truths_insights.json`)

```json
{
  "timestamp": "ISO timestamp",
  "total_truths": 0,
  "stable_truths": 0,
  "high_confidence_truths": 0,
  "category_distribution": {
    "agent_behavior": 0,
    "system_dynamics": 0,
    "collaboration": 0,
    "evolution": 0
  },
  "key_discoveries": [...],
  "recommendations": [...],
  "meta_observations": [...]
}
```

## Extending the System

### Add New Truth Categories

```python
# In universal_truth_evaluator.py
def discover_truths_from_custom_source(self) -> List[UniversalTruth]:
    """Discover truths from custom data source."""
    truths = []
    
    # Your discovery logic here
    truth = self._create_or_update_truth(
        'custom_truth_id',
        'custom_category',  # Add new category
        'Your truth statement',
        confidence=0.8,
        evidence={'your': 'data'}
    )
    truths.append(truth)
    
    return truths
```

### Add Custom Validation

```python
def validate_custom_truth(self, truth_id: str) -> bool:
    """Custom validation logic."""
    truth = self.truths.get(truth_id)
    if not truth:
        return False
    
    # Your validation logic
    is_valid = your_validation_function(truth)
    
    if is_valid:
        self.validate_truth(truth_id, {'validated': True})
    else:
        self.challenge_truth(truth_id, {'invalid': True})
    
    return is_valid
```

## Best Practices

1. **Run regularly**: Use scheduled workflow for continuous discovery
2. **Monitor stability**: Track stable_truths ratio (target: >70%)
3. **Act on recommendations**: Use insights for system optimization
4. **Validate manually**: Periodically review high-confidence truths
5. **Track evolution**: Monitor how truths change over time

## Troubleshooting

### No truths discovered
- Check that world state, learnings, and analysis data exist
- Verify JSON files are valid
- Run with verbose output: `python3 -v tools/universal_truth_evaluator.py`

### Low confidence truths
- Increase evidence accumulation
- Validate truths with new data
- Challenge questionable truths

### Truth conflicts
- Review related truths
- Check counter-examples
- May indicate system evolution

## Performance

- **Discovery time**: ~1-2 seconds per cycle
- **Memory usage**: <50MB
- **Storage**: ~10-20KB per 10 truths
- **Scalability**: Linear with agent count

## Future Enhancements

See [README](./UNIVERSAL_TRUTH_EVALUATOR_README.md#-future-enhancements) for planned features:
- Predictive truth engine
- Auto-learning integration
- Truth contradiction detection
- Causal analysis
- Truth visualization
- Historical playback

---

**Created by**: @create-guru  
**Version**: 1.0.0  
**Last Updated**: 2025-11-22
