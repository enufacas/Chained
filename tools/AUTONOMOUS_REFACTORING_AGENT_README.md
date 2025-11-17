# Autonomous Refactoring Agent

## Overview

The Autonomous Refactoring Agent is an intelligent system that learns code style preferences from your repository's history and external sources, then autonomously suggests and applies refactorings to improve code quality.

**Author:** @restructure-master  
**Inspired by:** Martin Fowler - clarity-seeking and pragmatic approach to refactoring

## Key Features

### 🧠 Learning Capabilities

The agent learns from multiple sources:

1. **PR History Learning**
   - Analyzes successfully merged PRs
   - Extracts code style patterns
   - Tracks success rates of different styles
   - Builds confidence through repetition

2. **Discussion Learning**
   - Parses issue and PR discussions
   - Extracts code style insights
   - Learns from team decisions
   - Integrates human preferences

3. **External Learning**
   - Learns from TLDR tech news
   - Incorporates Hacker News insights
   - Adapts industry best practices
   - Stays current with trends

4. **Self-Improvement**
   - Tracks refactoring outcomes
   - Adjusts confidence based on success
   - Evolves preferences over time
   - Learns from mistakes

### 🎯 Refactoring Capabilities

The agent provides:

- **Style Preference Analysis** - Identifies code style patterns
- **Automated Suggestions** - Generates actionable refactorings
- **Confidence Scoring** - Prioritizes high-confidence changes
- **Success Tracking** - Monitors refactoring outcomes
- **Report Generation** - Creates comprehensive refactoring reports

### 📊 Tracked Preferences

The agent learns and tracks:

- **Indentation style** (spaces vs tabs, indent size)
- **Naming conventions** (snake_case, camelCase, PascalCase)
- **Line length** preferences
- **Whitespace** patterns
- **Comment styles**
- **Import organization**
- **Function structure**
- **Docstring conventions**
- **Type hint usage**
- **Error handling patterns**

## Installation

The agent is part of the Chained tools suite and requires:

```bash
# Core dependencies (already included in Chained)
pip install -r requirements.txt
```

## Usage

### Basic Commands

```bash
# Learn from repository history and external sources
python3 tools/autonomous-refactoring-agent.py learn

# Analyze a specific file
python3 tools/autonomous-refactoring-agent.py analyze --source path/to/file.py

# Generate a refactoring report for a directory
python3 tools/autonomous-refactoring-agent.py report --source path/to/directory

# Show summary of learned preferences
python3 tools/autonomous-refactoring-agent.py summary
```

### Python API

```python
from tools.autonomous_refactoring_agent import (
    StylePreferenceLearner,
    AutoRefactorer
)

# Initialize the learner
learner = StylePreferenceLearner()

# Learn from a PR
pr_data = {
    'number': 123,
    'merged': True,
    'files_changed': ['file1.py', 'file2.py'],
    'commit_sha': 'abc123'
}
learner.learn_from_pr_history(pr_data)

# Learn from external sources
learner.learn_from_external_source('learnings/tldr_latest.json')

# Create a refactorer
refactorer = AutoRefactorer(learner)

# Analyze a file
analysis = refactorer.analyze_file('path/to/file.py')
print(f"Suggestions: {len(analysis['suggestions'])}")

# Generate a report
report = refactorer.generate_refactoring_report('.')
print(f"Files analyzed: {report['files_analyzed']}")
print(f"Total suggestions: {report['total_suggestions']}")
```

## Architecture

### Components

```
┌─────────────────────────────────────────────────────────┐
│         Autonomous Refactoring Agent                     │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌────────────────────────────────────────────────┐    │
│  │      StylePreferenceLearner                     │    │
│  │  - Learn from PR history                        │    │
│  │  - Learn from discussions                       │    │
│  │  - Learn from external sources                  │    │
│  │  - Track preferences and confidence             │    │
│  └────────────────────────────────────────────────┘    │
│                        │                                 │
│                        ▼                                 │
│  ┌────────────────────────────────────────────────┐    │
│  │       AutoRefactorer                            │    │
│  │  - Analyze files                                │    │
│  │  - Generate suggestions                         │    │
│  │  - Create refactoring reports                   │    │
│  │  - Apply learned preferences                    │    │
│  └────────────────────────────────────────────────┘    │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

### Data Structures

#### StylePreference

```python
@dataclass
class StylePreference:
    preference_type: str      # Type of preference
    value: Any                # Preferred value
    confidence: float         # 0.0 to 1.0
    occurrences: int          # Times seen
    last_seen: str           # ISO timestamp
    sources: List[str]       # Where learned from
    success_rate: float      # Success in merged PRs
```

#### RefactoringPattern

```python
@dataclass
class RefactoringPattern:
    pattern_name: str
    description: str
    before_pattern: str      # Regex or AST pattern
    after_pattern: str       # Replacement pattern
    confidence: float
    success_count: int
    failure_count: int
    learned_from: List[str]
    category: str           # e.g., "naming", "structure"
```

## Learning Process

### 1. Pattern Extraction

The agent extracts style features from code:

```python
# Indentation analysis
indent_size, indent_type = analyze_indentation(code)

# Naming convention detection
variable_naming = detect_naming_pattern(variables)
function_naming = detect_naming_pattern(functions)
class_naming = detect_naming_pattern(classes)

# Structural analysis
avg_function_length = calculate_avg_function_length(tree)
max_line_length = find_max_line_length(lines)
```

### 2. Confidence Building

Confidence increases with repeated observations:

```python
# Initial observation
confidence = 0.1

# After 10 occurrences
confidence = min(1.0, occurrences / 100.0)  # 0.1

# After 100 occurrences  
confidence = 1.0  # Maximum confidence
```

### 3. Success Rate Tracking

Success rate is calculated from merge outcomes:

```python
# Successful merge
success_rate = (success_rate * (occurrences - 1) + 1.0) / occurrences

# Failed merge (not currently implemented, but planned)
success_rate = (success_rate * (occurrences - 1) + 0.0) / occurrences
```

### 4. Preference Updates

Preferences are updated incrementally:

```python
# Categorical values (e.g., naming convention)
if same_as_existing:
    occurrences += 1
    confidence = min(1.0, occurrences / 50.0)

# Numeric values (e.g., line length)
value = (old_value * occurrences + new_value) / (occurrences + 1)
occurrences += 1
```

## Integration with Chained

### Workflow Integration

The agent integrates with Chained's autonomous pipeline:

```yaml
# Example workflow integration
- name: Learn from repository
  run: python3 tools/autonomous-refactoring-agent.py learn

- name: Generate refactoring report
  run: |
    python3 tools/autonomous-refactoring-agent.py report \
      --output analysis/refactoring_report.json

- name: Create refactoring PR
  if: refactoring_suggestions_exist
  run: |
    # Create PR with suggested refactorings
    # (Implementation in future enhancement)
```

### Learning Sources

The agent taps into existing learning mechanisms:

- **learnings/discussions/** - Issue and PR discussions
- **learnings/tldr_*.json** - TLDR tech news
- **learnings/hn_*.json** - Hacker News articles
- **analysis/patterns.json** - Code pattern database

### Data Storage

Learned data is stored in:

- **analysis/style_preferences.json** - Learned style preferences
- **analysis/refactoring_patterns.json** - Refactoring patterns
- **analysis/refactoring_report.json** - Latest refactoring report

## Examples

### Example 1: Learning from PR History

```python
# Simulate learning from a successful PR
learner = StylePreferenceLearner()

pr_data = {
    'number': 456,
    'merged': True,
    'files_changed': ['tools/my_tool.py'],
    'commit_sha': 'def456'
}

learner.learn_from_pr_history(pr_data)

# Check what was learned
summary = learner.get_preferences_summary()
print(f"Learned {summary['total_preferences']} preferences")
```

### Example 2: Generating Suggestions

```python
# Analyze a file and get suggestions
refactorer = AutoRefactorer(learner)
analysis = refactorer.analyze_file('tools/example.py')

for suggestion in analysis['suggestions']:
    print(f"Type: {suggestion['type']}")
    print(f"Current: {suggestion['current']}")
    print(f"Suggested: {suggestion['suggested']}")
    print(f"Confidence: {suggestion['confidence']:.2f}")
    print(f"Rationale: {suggestion['rationale']}")
    print()
```

### Example 3: Repository-Wide Report

```python
# Generate a comprehensive report
refactorer = AutoRefactorer(learner)
report = refactorer.generate_refactoring_report('.')

print(f"=== Refactoring Opportunities ===")
print(f"Files analyzed: {report['files_analyzed']}")
print(f"Total suggestions: {report['total_suggestions']}")

print(f"\nSuggestions by type:")
for stype, count in report['suggestions_by_type'].items():
    print(f"  {stype}: {count}")

print(f"\nHigh priority files ({len(report['high_priority_files'])}):")
for file_info in report['high_priority_files'][:5]:
    print(f"  {file_info['filepath']}: {file_info['high_confidence_count']} suggestions")
```

## Testing

The agent includes comprehensive tests:

```bash
# Run all tests
python3 tools/test_autonomous_refactoring_agent.py

# Tests cover:
# - Initialization and persistence
# - Learning from various sources
# - Confidence building
# - Success rate tracking
# - Suggestion generation
# - Report creation
```

## Future Enhancements

### Planned Features

1. **Automatic PR Creation**
   - Apply high-confidence refactorings automatically
   - Create PRs with detailed explanations
   - Include before/after comparisons

2. **Pattern Learning**
   - Learn common refactoring patterns
   - Detect anti-patterns
   - Suggest structural improvements

3. **Team Preference Weighting**
   - Weight preferences by team member expertise
   - Track individual style preferences
   - Resolve conflicting preferences

4. **ML-Based Analysis**
   - Use NLP for better insight extraction
   - Implement similarity-based learning
   - Predict refactoring success probability

5. **Real-Time Feedback**
   - Learn from code review comments
   - Adjust based on rejected suggestions
   - Improve from merge conflicts

## Performance Considerations

### Efficiency

- Incremental learning: Only processes changed files
- Caching: Stores learned preferences for reuse
- Lazy loading: Loads data on demand
- Parallel processing: Can analyze multiple files concurrently

### Resource Usage

- Memory: ~10-50MB for typical repository
- Storage: ~100KB-1MB for learned preferences
- CPU: Minimal overhead, mostly during learning phase

## Contributing

To extend the agent:

1. **Add new preference types** in `StylePreference`
2. **Implement new learning sources** in `StylePreferenceLearner`
3. **Add new refactoring patterns** in `RefactoringPattern`
4. **Extend suggestion generation** in `AutoRefactorer`

## License

Part of the Chained project. See main repository LICENSE.

## Credits

- **Author:** @restructure-master
- **Inspired by:** Martin Fowler's refactoring principles
- **Built on:** Existing Chained code analysis tools
- **Integrates with:** Chained's autonomous learning pipeline

---

*"Refactoring is a disciplined technique for restructuring an existing body of code, altering its internal structure without changing its external behavior."* - Martin Fowler

**@restructure-master** - Bringing clarity through systematic refactoring 🗂️
