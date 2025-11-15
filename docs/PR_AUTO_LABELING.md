# 🏷️ Smart PR Auto-Labeling System

> **Built by @assert-specialist with specification-driven approach**
> 
> Automatically analyzes PR content and applies appropriate labels based on systematic rules and confidence scoring.

## Overview

The Smart PR Auto-Labeling system analyzes pull request titles, descriptions, and changed files to automatically suggest and apply relevant labels. This improves PR organization, searchability, and workflow automation.

## Features

✅ **Content Analysis**: Examines PR title, body, and file changes
✅ **Confidence Scoring**: Each label has a confidence score (0-100%)
✅ **Multiple Labels**: Can apply multiple relevant labels to a single PR
✅ **Non-Destructive**: Never removes manually-added labels
✅ **Edge Case Handling**: Gracefully handles empty PRs, large changes, etc.
✅ **Systematic Testing**: Comprehensive test suite with 16+ test cases

## Supported Labels

The system can automatically detect and apply these labels:

### Code & Quality
- **code-quality**: Refactoring, cleanup, optimization, maintainability improvements
- **testing**: Test additions, test coverage improvements, test infrastructure
- **bug**: Bug fixes, error corrections, crash fixes
- **enhancement**: New features, capabilities, functionality additions

### Documentation
- **documentation**: README updates, documentation changes, guides, tutorials

### System Components
- **agent-system**: Changes to `.github/agents/` or agent infrastructure
- **workflow-optimization**: GitHub Actions workflow changes and improvements
- **pages-health**: GitHub Pages site changes (HTML, CSS, JS in `docs/`)

### Specialized
- **security**: Security fixes, vulnerability patches, auth changes
- **performance**: Performance improvements, optimization, caching
- **learning**: AI learning, pattern analysis, intelligence gathering

## How It Works

### 1. Content Analysis

The system analyzes:
- **PR Title**: Primary indicator of intent
- **PR Body**: Detailed description and context
- **Changed Files**: File paths and extensions
- **Diff Content**: Actual code changes (optional)

### 2. Rule-Based Matching

Each label has:
- **Keywords**: Terms that indicate the label (e.g., "refactor", "test", "fix")
- **File Patterns**: Regex patterns matching relevant files
- **Confidence Threshold**: Minimum score required (usually 0.6 or 60%)

### 3. Confidence Scoring

```
Score = (Keyword Score * Weight) + (File Pattern Score * Weight) + Bonus

Keyword Score: Number of matched keywords (scaled)
File Score: Proportion of matching files (scaled)
Bonus: +20% when both keywords AND files match
```

### 4. Label Application

Labels are applied if:
- Confidence score ≥ threshold (typically 60%)
- Label not already present (non-destructive)
- PR is not a draft (saves resources)

## Usage

### Automatic Triggering

The workflow runs automatically on:
- PR opened
- PR synchronized (new commits)
- PR reopened
- PR edited

### Manual Triggering

```bash
# Trigger workflow for specific PR
gh workflow run pr-auto-labeler.yml -f pr_number=123
```

### Analyzing Locally

```bash
# Analyze a PR
echo '{
  "title": "Fix bug in authentication",
  "body": "Resolve login crash issue",
  "files": ["src/auth.py", "tests/test_auth.py"]
}' | python3 tools/pr-content-analyzer.py

# With file input
python3 tools/pr-content-analyzer.py --input pr_data.json --verbose

# Output to file
python3 tools/pr-content-analyzer.py --input pr_data.json --output labels.json
```

## Testing

### Run Test Suite

```bash
# Run comprehensive tests
python3 tests/test_pr_auto_labeler.py
```

### Test Coverage

The test suite includes:
- ✅ **Edge Cases**: Empty PRs, large PRs, None values
- ✅ **Label Detection**: All 11 label categories tested
- ✅ **Invariants**: No duplicates, valid confidence scores
- ✅ **Boundaries**: Confidence thresholds, scoring limits
- ✅ **JSON Handling**: Input validation, error cases

### Test Results

```
Passed: 16/16
Failed: 0/16

✅ All tests passed! System is specification-compliant.
```

## Architecture

### Components

```
┌─────────────────────────────────────────────────┐
│          PR Auto-Labeling System                │
├─────────────────────────────────────────────────┤
│                                                 │
│  ┌──────────────────┐    ┌─────────────────┐  │
│  │  GitHub Actions  │───▶│  Python Tool    │  │
│  │  Workflow        │    │  (Analyzer)     │  │
│  └──────────────────┘    └─────────────────┘  │
│         │                         │             │
│         │                         ▼             │
│         │                 ┌─────────────────┐  │
│         │                 │  Label Rules    │  │
│         │                 │  Engine         │  │
│         │                 └─────────────────┘  │
│         ▼                         │             │
│  ┌──────────────────┐            ▼             │
│  │  Apply Labels    │    ┌─────────────────┐  │
│  │  to PR           │◀───│  Confidence     │  │
│  └──────────────────┘    │  Scoring        │  │
│                           └─────────────────┘  │
└─────────────────────────────────────────────────┘
```

### Data Flow

1. **PR Event** → Workflow triggered
2. **Fetch Data** → Get PR details via GitHub API
3. **Analyze** → Run content analyzer tool
4. **Score** → Calculate confidence for each label
5. **Filter** → Keep labels above threshold
6. **Apply** → Add new labels to PR (skip existing)
7. **Comment** → Post analysis details (optional)

## Specifications

### Invariants

The system maintains these invariants:
- ✅ No duplicate labels in output
- ✅ All confidence scores between 0.0 and 1.0
- ✅ All labels have confidence scores
- ✅ Output is always valid JSON
- ✅ Labels are from the defined label set

### Preconditions

- PR must exist and be accessible
- PR must not be a draft (workflow level)
- GitHub token must have PR write permissions

### Postconditions

- Labels applied to PR (if any suggested)
- No existing labels removed
- Analysis comment posted (if labels suggested)
- Workflow summary generated

## Configuration

### Adjusting Confidence Thresholds

Edit `tools/pr-content-analyzer.py`:

```python
LabelRule(
    label="your-label",
    keywords=["keyword1", "keyword2"],
    file_patterns=[r"\.py$"],
    min_confidence=0.7  # Adjust threshold (0.0-1.0)
)
```

### Adding New Labels

1. Add rule to `LABEL_RULES` in `pr-content-analyzer.py`
2. Add test case to `tests/test_pr_auto_labeler.py`
3. Run tests to validate
4. Update this documentation

### Excluding File Paths

Edit `.github/workflows/pr-auto-labeler.yml`:

```yaml
paths-ignore:
  - 'docs/**'
  - 'learnings/**'
  - '**.md'  # Exclude all markdown files
```

## Troubleshooting

### Labels Not Applied

**Symptom**: Workflow runs but no labels added

**Possible Causes**:
1. **Low Confidence**: Scores below threshold (60%)
   - *Solution*: Add more relevant keywords or files
2. **Labels Already Present**: System is non-destructive
   - *Solution*: Remove existing labels if needed
3. **Draft PR**: Workflow skips draft PRs
   - *Solution*: Mark PR as ready for review

**Debug**:
```bash
# Check analysis locally
python3 tools/pr-content-analyzer.py --input pr_data.json --verbose
```

### Wrong Labels Applied

**Symptom**: Incorrect or unexpected labels

**Possible Causes**:
1. **Keyword Overlap**: Similar keywords in multiple rules
   - *Solution*: Review LABEL_RULES for conflicts
2. **File Pattern Match**: Files matching unexpected patterns
   - *Solution*: Make patterns more specific

**Debug**:
```bash
# Run with verbose output
python3 tools/pr-content-analyzer.py --input pr_data.json --verbose

# Check match_details in output
cat output.json | jq '.analysis_details.match_details'
```

### Workflow Fails

**Symptom**: Workflow run shows failure

**Check**:
1. Python syntax errors in tool
2. GitHub API rate limits
3. Permission issues (pull-requests: write)

**Logs**:
```bash
# View workflow logs
gh run view <run-id> --log
```

## Performance

### Efficiency
- **Analysis Time**: ~1-2 seconds per PR
- **API Calls**: 2-3 per workflow run
- **Resource Usage**: Minimal (Python script)

### Scalability
- ✅ Handles PRs with 100+ files
- ✅ Processes multiple keywords efficiently
- ✅ Regex patterns pre-compiled for speed

## Best Practices

### For PR Authors

1. **Clear Titles**: Use descriptive titles with key terms
2. **Detailed Descriptions**: Explain what and why
3. **Logical File Organization**: Group related changes

### For Repository Maintainers

1. **Review Suggested Labels**: Verify accuracy
2. **Adjust Thresholds**: Tune for your workflow
3. **Monitor Performance**: Check false positives/negatives
4. **Keep Rules Updated**: Add labels as needed

### For Developers

1. **Test Changes**: Run test suite before committing
2. **Validate Invariants**: Ensure all assertions pass
3. **Document Rules**: Explain new label rules
4. **Consider Edge Cases**: Test empty/large/unusual inputs

## Future Enhancements

Potential improvements:
- 🔮 Machine learning-based labeling
- 🔮 Historical pattern analysis
- 🔮 Author-specific preferences
- 🔮 Diff content analysis (semantic)
- 🔮 Integration with CI/CD status

## References

- [LABELS.md](../LABELS.md) - Complete label reference
- [.github/workflows/pr-auto-labeler.yml](../.github/workflows/pr-auto-labeler.yml) - Workflow definition
- [tools/pr-content-analyzer.py](../tools/pr-content-analyzer.py) - Analyzer implementation
- [tests/test_pr_auto_labeler.py](../tests/test_pr_auto_labeler.py) - Test suite

## Credits

Built by **@assert-specialist** following Leslie Lamport's specification-driven approach:
- Formal specifications defined first
- Systematic edge case analysis
- Comprehensive test coverage
- Invariant checking throughout
- Clear documentation of behavior

---

*"A system is only as good as its specification and test coverage."* - @assert-specialist

**Back to [Main Documentation](INDEX.md)**
