# Intelligent Learning System - Quick Reference

## 🚀 Command Quick Reference

### Content Parser
```bash
# Parse a learning file
python3 tools/intelligent-content-parser.py learnings/tldr_YYYYMMDD.json

# Show statistics
python3 tools/intelligent-content-parser.py learnings/tldr_YYYYMMDD.json --stats

# Save cleaned version
python3 tools/intelligent-content-parser.py input.json -o output.json --stats
```

### Thematic Analyzer
```bash
# Analyze last 7 days (default)
python3 tools/thematic-analyzer.py learnings/

# Analyze custom time period
python3 tools/thematic-analyzer.py learnings/ --days 14

# Save as JSON
python3 tools/thematic-analyzer.py learnings/ -o analysis.json --json

# Pretty print to console
python3 tools/thematic-analyzer.py learnings/ --days 7
```

### Dynamic Agent Spawner
```bash
# Dry run (preview)
python3 tools/dynamic-agent-spawner.py -a analysis.json --dry-run

# Spawn agents
python3 tools/dynamic-agent-spawner.py -a analysis.json

# Custom threshold
python3 tools/dynamic-agent-spawner.py -a analysis.json --spawn-threshold 70.0

# Custom agents directory
python3 tools/dynamic-agent-spawner.py -a analysis.json --agents-dir .github/agents
```

## 🧪 Testing

```bash
# Run all tests
python3 tests/test_intelligent_content_parser.py
python3 tests/test_thematic_analyzer.py
python3 tests/test_dynamic_agent_spawner.py

# Or with pytest
pytest tests/test_intelligent_*.py tests/test_thematic_*.py tests/test_dynamic_*.py -v
```

## 📊 Key Metrics

### Content Quality
- **Acceptance Rate**: % of learnings that pass quality checks
- **Confidence Score**: 0.0-1.0 quality rating per learning
- **Typical Acceptance**: 70-90% for HN, 10-30% for TLDR (due to ads)

### Trend Analysis
- **Mention Count**: How many times topic appears
- **Momentum**: -1.0 (declining) to +1.0 (accelerating)
- **Trend Score**: 0-100 overall score
- **Hot Theme Threshold**: Usually 3+ AI/ML or 2+ security trends

### Agent Spawning
- **Default Threshold**: 50.0 (proposal score)
- **Minimum Mentions**: Usually 5+ for viable proposal
- **Momentum Bonus**: +15 points per +0.5 momentum
- **Diversity Bonus**: +3 points per unique source

## 🎯 Hot Themes

| Theme | Trigger | Agent Type |
|-------|---------|------------|
| ai-agents | 3+ AI/ML trends + 'agents' keyword | Agent Orchestrator |
| llm-specialist | 3+ AI/ML trends + 'llm'/'gpt' | LLM Architect |
| security-automation | 2+ security trends | Security Automation Specialist |
| rust-specialist | Rust in top lang trends | Rust Systems Engineer |
| go-specialist | Go in top lang trends | Go Concurrency Expert |
| cloud-infrastructure | 3+ DevOps trends | Cloud Infrastructure Architect |
| data-engineering | 2+ database trends | Data Pipeline Engineer |

## 🔍 Common Patterns

### Ad Detection Patterns
- `(sponsor)`, `(sponsored)`
- `sign up now`, `register now`
- `get $X credits`
- `join us for`, `download now`
- Product names: supabase, orkes, qa wolf, warp, workos

### Emoji Cleaning
- Automatically handles malformed Unicode: `\udXXX`
- Preserves real emojis when possible
- Normalizes to NFKC form

### Quality Checks
- Title length &gt; 10 chars (after cleaning)
- Content length &gt; 50 chars for acceptance
- No pure promotional content
- Valid URL preferred

## 📁 File Locations

```
tools/
  ├── intelligent-content-parser.py
  ├── thematic-analyzer.py
  ├── dynamic-agent-spawner.py
  └── INTELLIGENT_LEARNING_SYSTEM.md (full docs)

tests/
  ├── test_intelligent_content_parser.py (17 tests)
  ├── test_thematic_analyzer.py (14 tests)
  └── test_dynamic_agent_spawner.py (16 tests)

.github/workflows/
  ├── learn-from-tldr.yml (integrated)
  └── learn-from-hackernews.yml (integrated)

learnings/
  ├── tldr_*.json (raw + parsed)
  ├── hn_*.json (raw + parsed)
  └── analysis_*.json (trend analysis)
```

## 🐛 Troubleshooting

### Parser rejects all content
- Check if content is mostly sponsor/ad material
- TLDR newsletters often have 80%+ ad content - this is normal
- HN should have 70-90% acceptance rate

### Analyzer finds no trends
- Need at least 2 mentions to create a trend
- Increase lookback period: `--days 14`
- Check that learnings have timestamps

### Spawner creates no proposals
- Check spawn threshold (default: 50.0)
- Lower threshold: `--spawn-threshold 30.0`
- Verify hot themes in analysis output
- Check if agents already exist

### Import errors
- Files use hyphens, import with `importlib.util`
- See test files for proper import pattern
- Ensure Python 3.11+ (works with 3.12)

## 💡 Tips

1. **Run analyzer after every learning collection** to track trends
2. **Lower spawn threshold** (30-40) during experimentation
3. **Use dry-run** to preview before creating agents
4. **Check analysis.hot_themes** to see what's trending
5. **Monitor acceptance_rate** to gauge content quality

## 🔗 Related Docs

- [Full System Documentation](INTELLIGENT_LEARNING_SYSTEM.md)
- [Agent System Guide](../.github/agents/README.md)
- [Main README](../README.md)

---

*Quick reference for the Intelligent Learning System*
