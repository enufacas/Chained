# AI Pattern Repetition Detection & Prevention System

## Overview

This system detects and prevents repetitive patterns in AI agent contributions to the Chained repository. It helps maintain diversity in approaches, code structures, and problem-solving strategies.

## Components

### 1. Core Tools

#### `tools/repetition-detector.py`
Analyzes git history to detect repetitive patterns in AI agent contributions.

**Features:**
- AST-based code structure similarity detection
- Commit message pattern analysis
- File modification sequence tracking
- Solution approach clustering
- Comprehensive JSON reporting

**Usage:**
```bash
python3 tools/repetition-detector.py -d . --since-days 30 -o analysis/repetition-report.json
```

**Options:**
- `-d, --directory`: Repository directory to analyze (default: current directory)
- `--since-days`: Number of days to look back in history (default: 30)
- `-o, --output`: Output file for JSON report (default: stdout)

#### `tools/uniqueness-scorer.py`
Calculates uniqueness scores for AI agent contributions.

**Features:**
- Structural uniqueness scoring
- Approach diversity measurement
- Innovation index calculation
- Comparative analysis across agents
- Threshold-based flagging

**Usage:**
```bash
# Score all agents
python3 tools/uniqueness-scorer.py -d . --threshold 30 -o analysis/uniqueness-scores.json

# Score specific agent
python3 tools/uniqueness-scorer.py -d . --agent-id copilot-swe-agent --threshold 30
```

**Options:**
- `-d, --directory`: Repository directory (default: current directory)
- `--agent-id`: Specific agent ID to score (default: score all agents)
- `--threshold`: Uniqueness threshold for flagging (default: 30.0)
- `--days`: Number of days to look back (default: 90)
- `-o, --output`: Output file for JSON report (default: stdout)

#### `tools/diversity-suggester.py`
Generates concrete suggestions for improving diversity based on analysis.

**Features:**
- Context-aware suggestions
- Pattern library integration
- Specific alternative approaches
- Markdown-formatted reports

**Usage:**
```bash
python3 tools/diversity-suggester.py \
  --repetition-report analysis/repetition-report.json \
  -o analysis/diversity-suggestions.md
```

**Options:**
- `--repetition-report`: Path to repetition detection report (required)
- `-d, --directory`: Repository directory (default: current directory)
- `-o, --output`: Output file for suggestions (default: stdout)

### 2. Automation Workflow

#### `.github/workflows/repetition-detector.yml`

Automated workflow that runs on:
- Pull requests (opened, synchronize)
- Schedule (every 6 hours)
- Manual trigger (workflow_dispatch)

**Features:**
- Automatic repetition detection
- Uniqueness scoring
- Diversity suggestions generation
- PR comments with results
- Issue creation for significant repetition
- Artifact upload for reports

**Manual Trigger:**
```bash
gh workflow run repetition-detector.yml -f days=30 -f threshold=30
```

### 3. Data Structure

#### `analysis/pattern-diversity.json`

Central repository for pattern diversity data.

**Structure:**
```json
{
  "version": "1.0.0",
  "diversity_metrics": {
    "overall_diversity_score": 0,
    "repetition_rate": 0,
    "innovation_index": 0
  },
  "agent_scores": {},
  "pattern_library": {
    "successful_diverse_approaches": [],
    "repetitive_patterns": []
  },
  "thresholds": {
    "uniqueness_minimum": 30,
    "diversity_target": 70,
    "innovation_bonus": 10
  }
}
```

## Scoring Metrics

### Uniqueness Score (0-100)
Overall measure combining:
- **Structural Uniqueness (30%)**: Code structure diversity
- **Approach Diversity (40%)**: Variety of problem-solving approaches
- **Innovation Index (30%)**: Unique contributions compared to other agents

### Thresholds
- **Below 30**: Flagged for high repetition
- **30-70**: Acceptable diversity
- **Above 70**: Target diversity level
- **Innovation Bonus**: +10 for truly unique approaches

## Reports Generated

### 1. Repetition Report (`repetition-report.json`)
- Commit message patterns
- Code similarity metrics
- File sequence patterns
- Solution approach clustering
- Repetition flags

### 2. Uniqueness Scores (`uniqueness-scores.json`)
- Per-agent scores
- Detailed metrics breakdown
- Flagged agents below threshold
- Comparative rankings

### 3. Diversity Suggestions (`diversity-suggestions.md`)
- Concrete alternative approaches
- Pattern recommendations
- Best practices from repository
- Agent-specific guidance

## Integration

### With Existing Analysis Tools
- Integrates with `code-analyzer.py` patterns
- Uses `pattern-matcher.py` detection concepts
- Stores data in existing `analysis/` directory
- Follows repository coding conventions

### With GitHub Workflows
- Works alongside other analysis workflows
- Shares artifact storage patterns
- Uses consistent permissions model
- Follows naming conventions

## Development

### Testing
```bash
# Test repetition detector
python3 tools/repetition-detector.py -d . --since-days 7 -o /tmp/test-rep.json

# Test uniqueness scorer
python3 tools/uniqueness-scorer.py -d . --days 7 -o /tmp/test-uniq.json

# Test diversity suggester
python3 tools/diversity-suggester.py --repetition-report /tmp/test-rep.json -o /tmp/test-sug.md
```

### Validation
```bash
# Validate workflow YAML
python3 -c "import yaml; yaml.safe_load(open('.github/workflows/repetition-detector.yml'))"

# Check tool executability
ls -l tools/repetition-detector.py tools/uniqueness-scorer.py tools/diversity-suggester.py
```

## Best Practices

### For AI Agents
1. **Monitor your scores**: Check `analysis/uniqueness-scores.json` regularly
2. **Review suggestions**: Read diversity suggestions when flagged
3. **Vary approaches**: Consciously use different problem-solving strategies
4. **Learn from patterns**: Study successful diverse approaches in pattern library
5. **Track improvement**: Monitor score trends over time

### For Maintainers
1. **Review reports**: Check analysis reports regularly
2. **Update thresholds**: Adjust based on team standards
3. **Enhance patterns**: Add successful patterns to library
4. **Refine detection**: Improve algorithms based on false positives
5. **Share insights**: Communicate findings to the team

## Troubleshooting

### Common Issues

**No agents detected:**
- Ensure git history exists
- Check date range (--since-days)
- Verify agent identification patterns

**Low scores despite diversity:**
- Review scoring algorithm
- Check pattern library
- Adjust thresholds

**False positives:**
- Refine detection patterns
- Update agent identification
- Improve AST comparison

## Future Enhancements

- Machine learning for pattern detection
- Real-time diversity scoring in PRs
- Agent recommendation system
- Historical trend analysis
- Cross-repository pattern analysis

## License

Part of the Chained autonomous AI agent system.

## Support

For issues or questions:
- Create an issue with label `ai-patterns`
- Check existing discussions
- Review analysis reports in `analysis/` directory
