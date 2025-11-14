# 🏛️ Enhanced Code Archaeology with Active Learning

Transform your git history into a **learning dataset** that predicts outcomes, assesses risks, and recommends actions!

## 🎯 What's New

The enhanced Code Archaeology system goes beyond documentation to provide **active learning** and **predictive insights**:

### Traditional Archaeology ✅
- Documents architectural decisions
- Tracks technical debt
- Shows code evolution over time
- Creates decision timelines

### Active Learning (NEW!) 🆕
- **Learns** from every success and failure
- **Predicts** outcomes before they happen
- **Assesses** risks with probability scoring
- **Recommends** proven approaches
- **Prevents** future problems proactively

## 🚀 Key Features

### 1. **Pattern Learning System**

Automatically learns from history:

```python
# Success patterns: What works
- "Refactoring with tests → 85% success rate"
- "Small incremental changes → Fewer bugs"
- "Documented decisions → Better maintainability"

# Failure patterns: What to avoid
- "Large changes without tests → 70% need fixes"
- "Missing documentation → Future confusion"
- "High file churn → Instability"
```

### 2. **Predictive Insights**

Make informed decisions:

```python
from archaeology_learner import ArchaeologyLearner

learner = ArchaeologyLearner()
learner.analyze_and_learn(max_commits=200)

# Predict outcome
prediction = learner.predict_outcome({
    'is_refactor': True,
    'has_tests': True,
    'large_change': False
})
# → {'prediction': 'success', 'confidence': 0.85}

# Assess risk
risk = learner.assess_risk({
    'is_feature': True,
    'has_tests': False,
    'large_change': True
})
# → {'risk_level': 'high', 'risk_score': 0.75}

# Estimate timeline
timeline = learner.estimate_timeline('feature', files_count=5)
# → {'estimated_days': 3.5, 'range': '2.5-4.5 days'}
```

### 3. **Living Knowledge Base**

Searchable archive of best practices:

```python
# Search for relevant knowledge
results = learner.search_knowledge_base("test")
# → [
#   {'type': 'best_practice', 'content': 'Include comprehensive test coverage'},
#   {'type': 'common_pitfall', 'content': 'Skipping tests leads to bugs'}
# ]

# Find similar historical changes
similar = learner.find_similar_changes({
    'is_refactor': True,
    'has_tests': True
}, max_results=5)
# → Returns 5 most similar past changes with lessons learned
```

### 4. **Workflow Integration**

Seamless GitHub integration:

```python
from archaeology_integration import ArchaeologyIntegration

integration = ArchaeologyIntegration()

# PR Analysis
pr_insights = integration.analyze_pr_changes(
    files_changed=['api.py', 'auth.py'],
    pr_description="Add authentication feature"
)
# → Risk assessment, predictions, similar changes

# Issue Planning
planning = integration.plan_issue_work(
    issue_title="Implement new API endpoint",
    issue_description="Need to add /users endpoint"
)
# → Timeline estimates, similar past work, best practices

# Preventive Maintenance
suggestions = integration.suggest_preventive_maintenance()
# → List of files needing attention based on patterns
```

## 📊 Usage

### Command Line

#### Run Learning Analysis

```bash
# Basic analysis
python3 tools/archaeology-learner.py -n 200

# With predictions
python3 tools/archaeology-learner.py -n 200 --predict

# With risk assessment
python3 tools/archaeology-learner.py -n 200 --assess-risk

# With timeline estimation
python3 tools/archaeology-learner.py -n 200 --estimate-timeline

# Search knowledge base
python3 tools/archaeology-learner.py -n 200 --search "test"

# Find similar changes
python3 tools/archaeology-learner.py -n 200 --find-similar
```

#### Integration Helpers

```bash
# Analyze PR changes
python3 tools/archaeology-integration.py analyze-pr \
  --files api.py auth.py \
  --description "Add authentication"

# Plan issue work
python3 tools/archaeology-integration.py plan-issue \
  --title "New feature: User dashboard" \
  --description "Create dashboard for users"

# Suggest preventive maintenance
python3 tools/archaeology-integration.py suggest-maintenance
```

### In Workflows

The system integrates with `.github/workflows/code-archaeologist.yml`:

```yaml
- name: Run Code Archaeologist with Active Learning
  run: |
    python3 tools/code-archaeologist.py \
      -n 100 \
      --learn  # ← Enables active learning
```

## 💡 Example Scenarios

### Scenario 1: PR Review

```
New PR touches authentication code
→ Archaeology shows 3 past auth bugs
→ Highlights common pitfalls: "Missing edge case tests"
→ Suggests: "Add security testing like PR #123"
→ Risk level: MEDIUM
→ Recommendation: "Add comprehensive security tests"
```

### Scenario 2: Issue Planning

```
New feature request for API endpoint
→ Archaeology finds 10 similar past features
→ Shows average completion time: 2.5 days
→ Lists common challenges:
  - "Edge case handling"
  - "Authentication integration"
→ Suggests proven implementation approach
→ References successful similar PRs
```

### Scenario 3: Preventive Maintenance

```
Archaeology detects pattern: "core.py changes often"
→ File has 15 changes in 3 months
→ Change frequency: VERY_FREQUENT
→ Risk: High churn indicates instability
→ Action: Create issue to refactor and stabilize
→ Prevents: Future bugs and maintenance burden
```

## 🔮 Predictive Capabilities

### Risk Assessment

Evaluates proposed changes against historical patterns:

- **Risk Score**: 0.0 (low) to 1.0 (high)
- **Risk Factors**: Specific concerns identified
- **Success Probability**: Likelihood of clean implementation
- **Recommendations**: Mitigation strategies

### Timeline Estimation

Predicts completion time based on similar past work:

- **Estimated Days**: Most likely duration
- **Range**: Min-max timeframe
- **Confidence**: High/Medium/Low based on data
- **Sample Size**: Number of similar historical tasks

### Similar Change Finder

Locates relevant historical examples:

- **Similarity Score**: How closely it matches
- **Outcome**: Success or failure
- **Lessons Learned**: Key takeaways
- **References**: Commit hashes for details

## 📈 Success Metrics

The system tracks its own effectiveness:

- **Pattern Count**: Total patterns learned
- **Prediction Accuracy**: % of correct predictions
- **Recommendations**: Actions suggested
- **Validation**: Actual vs predicted outcomes

## 🔧 Configuration

Patterns are stored in `analysis/archaeology-patterns.json`:

```json
{
  "version": "1.0",
  "patterns": {
    "success": [...],
    "failure": [...],
    "evolution": [...]
  },
  "knowledge_base": {
    "best_practices": [...],
    "common_pitfalls": [...],
    "success_examples": [...],
    "failure_examples": [...]
  },
  "timeline_data": {
    "feature_completion_times": [...],
    "refactor_completion_times": [...],
    "bugfix_completion_times": [...]
  }
}
```

## 🧪 Testing

Run tests to verify functionality:

```bash
# Original tests
python3 tools/test_archaeology_learner.py

# Enhanced feature tests
python3 tools/test_archaeology_learner_enhanced.py
```

## 📚 API Reference

### ArchaeologyLearner

Main learning class:

- `analyze_and_learn(max_commits=200)` - Learn from git history
- `predict_outcome(characteristics)` - Predict change outcome
- `assess_risk(characteristics, files)` - Assess risk level
- `estimate_timeline(change_type, files_count)` - Estimate duration
- `find_similar_changes(characteristics, max_results)` - Find examples
- `search_knowledge_base(query, category)` - Search insights
- `generate_report()` - Create human-readable report

### ArchaeologyIntegration

Workflow integration helpers:

- `analyze_pr_changes(files, description)` - PR analysis
- `plan_issue_work(title, description)` - Issue planning
- `suggest_preventive_maintenance()` - Maintenance suggestions
- `generate_pr_comment(files, description)` - Format PR comment
- `generate_issue_comment(title, description)` - Format issue comment

## 🎓 Learning Process

The system learns through these steps:

1. **Pattern Extraction**: Analyzes commits and outcomes
2. **Outcome Analysis**: Tracks follow-up fixes and improvements
3. **Timeline Tracking**: Records completion times by type
4. **Knowledge Building**: Extracts best practices and pitfalls
5. **Insight Generation**: Identifies trends and correlations
6. **Recommendation Creation**: Suggests proactive actions

## 🏆 Benefits

- **Reduce Bugs**: Learn from past mistakes
- **Save Time**: Estimate work accurately
- **Improve Quality**: Follow proven practices
- **Prevent Issues**: Proactive maintenance
- **Share Knowledge**: Searchable lessons learned
- **Make Better Decisions**: Data-driven insights

## 🔗 Integration Points

### Workflows
- `.github/workflows/code-archaeologist.yml` - Weekly learning runs
- PR review comments with insights
- Issue planning assistance

### Tools
- `tools/archaeology-learner.py` - Core learning engine
- `tools/archaeology-integration.py` - Workflow integration
- `tools/code-archaeologist.py` - Traditional archaeology

### Data
- `analysis/archaeology.json` - Historical decisions
- `analysis/archaeology-patterns.json` - Learned patterns

## 🚀 Future Enhancements

Potential improvements:

- A/B testing of recommendations
- Real-time accuracy tracking
- Machine learning model integration
- Team-specific pattern learning
- Cross-repository learning
- Automated issue creation for maintenance

## 📖 Learn More

- [Code Archaeologist Overview](CODE_ARCHAEOLOGIST.md)
- [Pattern Matcher](PATTERN_MATCHER.md)
- [Main README](../README.md)

---

**The entire git history is now a learning dataset!**

Turn every commit into knowledge, every success into a pattern, and every failure into a lesson.
