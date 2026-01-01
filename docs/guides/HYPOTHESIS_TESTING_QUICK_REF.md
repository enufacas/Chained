# AI Code Pattern Hypothesis Testing - Quick Reference

**@create-champion** | Production Ready ✅

## 🚀 Quick Start

```bash
# Run locally
python3 tools/hypothesis_testing_engine.py

# Run with custom settings
python3 tools/hypothesis_testing_engine.py \
  --num-hypotheses 20 \
  --max-files 200 \
  --output results.json

# Trigger workflow
gh workflow run code-pattern-hypothesis-testing.yml
```

## 📊 What It Does

1. **Analyzes** Python code in repository
2. **Generates** hypotheses about code patterns
3. **Tests** hypotheses statistically
4. **Creates** issues for validated patterns
5. **Learns** from results over time

## 🎯 Hypothesis Types

| Type | Example |
|------|---------|
| **Correlation** | "High complexity → Low test coverage" |
| **Threshold** | "Functions > 50 lines → Multiple responsibilities" |
| **Pattern** | "Short names → Missing documentation" |

## 📈 Demo Results

- **Analyzed:** 421 functions
- **Generated:** 9 hypotheses
- **Validated:** 5 hypotheses (55.6%)
- **Confidence:** 95% for all validated

### Top Findings

1. Short names lack documentation
2. Long names indicate complexity
3. 50+ lines = multiple responsibilities
4. Complexity > 10 = testing difficulties
5. Clear naming = better maintainability

## ⚙️ Configuration

| Setting | Default | Description |
|---------|---------|-------------|
| `num_hypotheses` | 15 | Hypotheses to generate |
| `max_files` | 150 | Files to analyze |
| `create_issues` | true | Auto-create issues |

## 📅 Schedule

- **Automatic:** Every Sunday 6 AM UTC
- **Manual:** Via workflow_dispatch

## 📚 Documentation

- **Workflow Guide:** `docs/workflows/CODE_PATTERN_HYPOTHESIS_TESTING.md`
- **Tool Docs:** `tools/HYPOTHESIS_TESTING_ENGINE_README.md`
- **Demo Results:** `learnings/hypothesis_testing/DEMO_RESULTS_SUMMARY.md`

## 🧪 Testing

```bash
# Run all tests
python3 tests/test_hypothesis_testing_engine.py
python3 tests/test_code_pattern_hypothesis_workflow.py

# Expected: 21 tests, all passing ✅
```

## 💡 Use Cases

- **Code Quality:** Find patterns affecting quality
- **Refactoring:** Identify targets for improvement
- **Standards:** Validate coding guidelines
- **Learning:** Track quality evolution

## 🎓 Example Output

```
🔬 Hypothesis Testing Results

✓ Validated: 5/9 (55.6%)

🏆 Top Hypotheses:
1. Short naming → Lower documentation (95% confidence)
2. Long naming → Higher complexity (95% confidence)
3. 50+ lines → Multiple responsibilities (95% confidence)

💡 Recommendations:
• Refactor functions > 50 lines
• Reduce complexity > 10
• Improve documentation
```

## 🔗 Related

- Workflow: `.github/workflows/code-pattern-hypothesis-testing.yml`
- Engine: `tools/hypothesis_testing_engine.py`
- Tests: `tests/test_*.py`

---

**Agent:** @create-champion | **Status:** Production Ready ✅
