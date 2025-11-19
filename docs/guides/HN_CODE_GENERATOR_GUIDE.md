# HN Insights Code Generator

> A transformer-inspired code generation system that learns from Hacker News insights

**Created by @investigate-champion** - Analytical investigation approach inspired by Ada Lovelace

---

## 🎯 Overview

The HN Insights Code Generator is a lightweight, transformer-inspired system that:

1. **Learns** from Hacker News discussions and trending topics
2. **Generates** relevant code snippets and tools
3. **Adapts** by creating new templates based on recurring patterns
4. **Tracks** usage and confidence metrics for continuous improvement

### Why "Transformer-Inspired"?

While this implementation doesn't use actual neural networks (to keep dependencies minimal), it simulates the key concepts of transformer models:

- **Attention Mechanism**: Keyword matching and relevance scoring
- **Context Understanding**: Analysis of HN insights and patterns
- **Generation**: Template-based code synthesis with context filling
- **Learning**: Pattern extraction and template creation from data

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Input Layer                          │
│  ┌─────────────────────────────────────────────┐       │
│  │  HN Insights (JSON)                         │       │
│  │  - Titles, descriptions, URLs               │       │
│  │  - Metadata (scores, discussions)           │       │
│  └─────────────────────────────────────────────┘       │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│              Attention/Analysis Layer                    │
│  ┌─────────────────────────────────────────────┐       │
│  │  Topic Extraction                           │       │
│  │  - Keyword frequency analysis               │       │
│  │  - Pattern recognition                      │       │
│  │  - Relevance scoring                        │       │
│  └─────────────────────────────────────────────┘       │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│               Template Selection Layer                   │
│  ┌─────────────────────────────────────────────┐       │
│  │  Template Matching                          │       │
│  │  - Keyword similarity scoring               │       │
│  │  - Best template selection                  │       │
│  │  - Confidence calculation                   │       │
│  └─────────────────────────────────────────────┘       │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│               Generation Layer                           │
│  ┌─────────────────────────────────────────────┐       │
│  │  Code Synthesis                             │       │
│  │  - Template filling with context            │       │
│  │  - Variable substitution                    │       │
│  │  - Code formatting                          │       │
│  └─────────────────────────────────────────────┘       │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│                   Output Layer                           │
│  ┌─────────────────────────────────────────────┐       │
│  │  Generated Code                             │       │
│  │  - Complete Python classes                  │       │
│  │  - Usage tracking                           │       │
│  │  - Confidence metrics                       │       │
│  └─────────────────────────────────────────────┘       │
└─────────────────────────────────────────────────────────┘
```

## 📦 Components

### 1. CodeTemplate

Represents a reusable code template:

```python
@dataclass
class CodeTemplate:
    template_id: str
    category: str
    description: str
    code_template: str
    keywords: List[str]
    source_insights: List[str]
    usage_count: int
```

### 2. HNCodeGenerator

Main generator class with four key methods:

- `analyze_hn_insights()`: Extract patterns from HN data
- `generate_code()`: Generate code from description
- `learn_from_insights()`: Create new templates
- `get_statistics()`: Track performance metrics

### 3. Data Flow

```
HN Insights → Analysis → Template Selection → Code Generation → Output
     ↓           ↓              ↓                   ↓             ↓
  learnings/  topics &      best match         fill template   Python
   hn_*.json  keywords      + confidence        + context       code
```

## 🚀 Usage

### Command Line Interface

```bash
# Analyze HN insights
./tools/hn-code-generator.py --analyze

# Generate code
./tools/hn-code-generator.py --generate "Build an API wrapper" --class-name MyAPI

# Learn from insights
./tools/hn-code-generator.py --learn

# View statistics
./tools/hn-code-generator.py --stats
```

### Programmatic Usage

```python
from hn_code_generator import HNCodeGenerator

# Initialize
generator = HNCodeGenerator()

# Analyze insights
insights = generator.analyze_hn_insights()
print(f"Found {insights['total_insights']} insights")

# Generate code
code = generator.generate_code(
    "Create a data analyzer",
    context={'class_name': 'DataAnalyzer', 'data_type': 'JSON'}
)

print(code.code)

# Learn patterns
generator.learn_from_insights(insights)

# Get stats
stats = generator.get_statistics()
print(f"Templates: {stats['total_templates']}")
```

## 📊 Examples

### Example 1: API Wrapper Generation

**Input:**
```python
generator.generate_code(
    "Build API wrapper with rate limiting",
    context={'class_name': 'GitHubAPI', 'api_name': 'GitHub'}
)
```

**Output:**
```python
import requests
import time
from functools import wraps

class GitHubAPI:
    '''API wrapper for GitHub'''
    
    def __init__(self, api_key: str, rate_limit: int = 60):
        self.api_key = api_key
        self.rate_limit = rate_limit
        self.last_request_time = 0
    
    # ... (complete implementation)
```

### Example 2: Data Analyzer Generation

**Input:**
```python
generator.generate_code(
    "Create data analysis tool",
    context={'class_name': 'InsightsAnalyzer', 'data_type': 'HN insights'}
)
```

**Output:**
```python
import json
from collections import Counter

class InsightsAnalyzer:
    '''Analyzer for HN insights data'''
    
    def __init__(self, data_path: str):
        self.data_path = data_path
        self.data = []
        self._load_data()
    
    # ... (complete implementation)
```

## 🧪 Testing

Run the comprehensive test suite:

```bash
python3 tools/test_hn_code_generator.py
```

Tests cover:
- ✓ Initialization
- ✓ Template keyword matching
- ✓ Code generation
- ✓ HN insights analysis
- ✓ Learning from patterns
- ✓ Statistics tracking
- ✓ Data persistence
- ✓ Usage tracking
- ✓ Confidence scoring

## 🎭 Demo

Run the interactive demonstration:

```bash
python3 tools/demo_hn_code_generator.py
```

The demo shows:
1. Basic code generation
2. HN insights analysis
3. Learning new patterns
4. Multiple generations
5. Statistics tracking
6. Complete workflow

## 📈 Performance Metrics

The generator tracks:

- **Usage count**: How often each template is used
- **Confidence scores**: Match quality (0-1 scale)
- **Template categories**: Distribution of template types
- **Generation history**: All generated code snippets

### Sample Statistics

```
Total templates: 14
Total generated: 50
Average confidence: 0.65

By category:
  • api: 1 template, 20 uses
  • data_processing: 1 template, 15 uses
  • ml: 1 template, 8 uses
  • devops: 1 template, 7 uses
  • learned: 10 templates (from HN insights)
```

## 🔬 How It Works (Technical Details)

### Attention Mechanism (Keyword Matching)

The system simulates attention by scoring keyword matches:

```python
def matches_keywords(self, text: str) -> float:
    text_lower = text.lower()
    matches = sum(1 for kw in self.keywords if kw.lower() in text_lower)
    return matches / len(self.keywords)
```

Higher scores → Better match → Higher confidence

### Learning from Insights

The system learns by:

1. **Frequency analysis**: Count topic occurrences
2. **Threshold filtering**: Topics appearing 5+ times
3. **Template creation**: Generate new code templates
4. **Source tracking**: Link templates to HN insights

```python
def learn_from_insights(self, insights):
    for topic, count in insights['top_topics']:
        if count >= 5:  # High frequency
            create_new_template(topic)
```

### Code Generation Process

1. **Input**: Description + context
2. **Scoring**: Match against all templates
3. **Selection**: Choose highest scoring template
4. **Generation**: Fill template with context variables
5. **Output**: Complete Python code

## 🎯 Integration with Chained

### Data Sources

Uses existing HN learning infrastructure:
- Reads from `learnings/hn_*.json` files
- Analyzes patterns from multiple learning sessions
- Extracts topics, titles, and URLs

### Workflow Integration

Can be triggered by:
- GitHub Actions workflows
- Manual CLI usage
- Programmatic API calls
- Learning-based agent spawner

### Future Enhancements

Potential integrations:
- Auto-generate tools from trending HN topics
- Create GitHub issues with generated code
- Update learnings book with code examples
- Feed into agent system for automated implementation

## 📝 Template Categories

Current template types:

1. **API Wrappers** (`api`)
   - REST API clients
   - Rate limiting
   - Authentication

2. **Data Processing** (`data_processing`)
   - JSON analyzers
   - Data filters
   - Statistical analysis

3. **Machine Learning** (`ml`)
   - Model wrappers
   - Prediction caching
   - Result tracking

4. **DevOps** (`devops`)
   - Monitoring tools
   - Alerting systems
   - Metric tracking

5. **Learned** (`learned`)
   - Dynamically created from HN insights
   - Topic-specific tools
   - Community-driven patterns

## 🔮 Design Philosophy

### Lightweight Implementation

- **No heavy ML dependencies**: Works with standard library
- **Fast execution**: Template-based generation is instant
- **Minimal storage**: JSON-based persistence
- **Easy deployment**: Single Python file

### Transformer-Inspired Concepts

- **Attention**: Keyword matching simulates attention mechanism
- **Context**: Template selection considers full context
- **Generation**: Sequential token-like code assembly
- **Learning**: Pattern extraction mimics training

### Extensibility

Easy to extend:
- Add new templates
- Customize categories
- Enhance scoring algorithms
- Integrate with ML models (future)

## 🤝 Contributing

This tool is part of the Chained autonomous AI ecosystem. To enhance it:

1. Add new code templates
2. Improve keyword matching
3. Enhance learning algorithms
4. Add more test cases
5. Integrate with other tools

## 📚 Related Tools

- `prompt-generator.py`: Self-improving prompt generation
- `build-learnings-book.py`: Curate HN insights
- `archaeology-learner.py`: Learn from code history
- `unsupervised_pattern_learner.py`: Pattern discovery

## 🎓 Educational Value

This implementation demonstrates:

- Transformer concepts without heavy dependencies
- Practical code generation techniques
- Learning from community insights
- Metrics-driven improvement
- Clean architecture patterns

## 🔗 Resources

- [HN Insights Data](../../learnings/)
- [Learnings Book](../../learnings/book/)
- [Agent Profiles](../../.github/agents/)
- [Test Suite](./test_hn_code_generator.py)
- [Demo Script](./demo_hn_code_generator.py)

---

**@investigate-champion**: *"By analyzing patterns in community discussions, we can generate relevant tools that solve real problems. This is the essence of data-driven development."*

*Created as part of the Chained autonomous AI ecosystem - where AI learns, adapts, and creates.*
