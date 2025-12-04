# Self-Improving Prompt Generator - Quick Reference

**@create-botter** - Quick start guide for the enhanced prompt system

## 🚀 Quick Start

### Generate Optimized Prompt

```bash
# Basic usage
python3 tools/prompt-generator.py generate \
  --issue-body "Fix authentication bug in login flow" \
  --category bug_fix \
  --agent engineer-master

# With learning enhancement
python3 tools/prompt-generator.py generate \
  --issue-body "Add Redis caching layer" \
  --category feature \
  --agent create-botter
```

### Record Outcome

```bash
# Success
python3 tools/prompt-generator.py record \
  --prompt-id bug_fix_systematic \
  --issue-number 123 \
  --success \
  --resolution-time 8.5

# Failure
python3 tools/prompt-generator.py record \
  --prompt-id feature_rigorous \
  --issue-number 124 \
  --resolution-time 12.0 \
  --error-type "build_failure"
```

### Check Quality Scores

```bash
# Score all templates
python3 tools/prompt-quality-scorer.py score

# Get full report
python3 tools/prompt-quality-scorer.py report | jq .

# Check specific template
python3 tools/prompt-quality-scorer.py template \
  --template-id bug_fix_systematic
```

### Adapt Prompt for Agent

```bash
# Basic adaptation
python3 tools/contextual-prompt-adapter.py create-botter \
  --prompt "Implement feature X" \
  --labels "feature,infrastructure"

# With full context
python3 tools/contextual-prompt-adapter.py secure-specialist \
  --prompt "Fix security issue" \
  --labels "security,urgent" \
  --title "SQL injection vulnerability" \
  --body "User input not properly sanitized"
```

## 📊 Workflows

### Prompt Auto-Tuner

Runs automatically every Sunday at 3 AM UTC.

**Manual trigger:**
```bash
# Standard run
gh workflow run prompt-auto-tuner.yml

# Force evolution with limited data
gh workflow run prompt-auto-tuner.yml \
  -f force_evolution=true \
  -f min_effectiveness=0.3
```

### Performance Tracker

Runs daily at 2 AM UTC, or trigger manually:

```bash
# Standard tracking
gh workflow run prompt-performance-tracker.yml

# Analyze last 30 days with learning refresh
gh workflow run prompt-performance-tracker.yml \
  -f days_to_analyze=30 \
  -f refresh_learnings=true
```

## 🎯 Common Tasks

### View Template Performance

```bash
python3 tools/prompt-generator.py report | \
  jq '.templates | to_entries | sort_by(.value.effectiveness_score) | reverse | .[:5]'
```

### Identify Templates Needing Improvement

```bash
python3 tools/prompt-generator.py optimize | \
  jq '.[] | select(.issue == "low_effectiveness")'
```

### Check Overall System Health

```bash
# Get summary statistics
python3 tools/prompt-generator.py report | \
  jq '{
    total: .insights.overall.total_prompts_used,
    success_rate: (.insights.overall.success_rate * 100),
    avg_time: .insights.overall.avg_resolution_time
  }'
```

### Compare Template Effectiveness

```bash
# Get top 3 by category
python3 tools/prompt-quality-scorer.py report | \
  jq '.templates | group_by(.template_id | split("_")[0]) | 
      map({category: .[0].template_id | split("_")[0], 
           best: (sort_by(.overall_quality) | reverse | .[0])})'
```

## 🧪 Testing

```bash
# Run all enhancement tests
python3 tests/test_prompt_generator_enhancements.py

# Run specific test
python3 -c "
from tests.test_prompt_generator_enhancements import test_quality_scoring_with_data
test_quality_scoring_with_data()
"
```

## 📈 Monitoring

### Check Last Auto-Tune Results

```bash
# Find most recent tuning PR
gh pr list --label "prompt-generator,enhancement" --limit 1

# View tuning history
ls -lt tools/data/prompts/history/ | head -10
```

### View Quality Trends

```bash
# Compare current vs historical
diff \
  <(cat tools/data/prompts/history/report_latest.json | jq '.summary.avg_quality') \
  <(python3 tools/prompt-quality-scorer.py report | jq '.summary.avg_quality')
```

## 🔧 Troubleshooting

### Template Not Getting Used

Check if it has good quality score:
```bash
python3 tools/prompt-quality-scorer.py template --template-id YOUR_TEMPLATE_ID
```

### Low Success Rate

Analyze failure patterns:
```bash
python3 tools/prompt-generator.py optimize | \
  jq '.[] | select(.template_id == "YOUR_TEMPLATE_ID") | .common_errors'
```

### Auto-Tuner Not Running

Check workflow runs:
```bash
gh run list --workflow=prompt-auto-tuner.yml --limit 5
```

View logs:
```bash
gh run view $(gh run list --workflow=prompt-auto-tuner.yml --limit 1 --json databaseId -q '.[0].databaseId')
```

## 💡 Pro Tips

### 1. Warm Up Period

New templates need ~10 uses before meaningful optimization. During this period:
- They get neutral scores (0.5)
- Auto-tuner won't evolve them yet
- Focus on collecting data

### 2. A/B Testing

When auto-tuner creates variants:
- Original and evolved templates alternate usage
- Performance tracked independently
- Winner automatically selected after sufficient data

### 3. Learning Integration

Prompts automatically enhanced with:
- Recent TLDR insights (technology trends)
- Hacker News learnings (community wisdom)
- Repository-specific patterns

Refresh manually:
```bash
python3 tools/prompt-generator.py refresh-learnings --days 7
```

### 4. Quality Grades

Target grades by template category:
- Critical (bug_fix, security): Aim for B+ or higher
- Standard (feature, refactor): B- or higher acceptable
- Documentation: C+ or higher acceptable

### 5. Template Evolution

Mutation types serve different purposes:
- **Enhance**: Add more guidance (for unclear templates)
- **Focus**: Emphasize critical parts (for scattered templates)
- **Simplify**: Remove verbosity (for slow execution)

## 🔗 Integration Examples

### With Copilot Workflow

```yaml
- name: Generate optimized prompt
  run: |
    prompt=$(python3 tools/prompt-generator.py generate \
      --issue-body "$ISSUE_BODY" \
      --category "$CATEGORY" \
      --agent "$AGENT")
    
    # Further enhance with context
    enhanced=$(python3 tools/contextual-prompt-adapter.py "$AGENT" \
      --prompt "$prompt" \
      --labels "$LABELS" \
      --title "$TITLE")
```

### With Issue Assignment

```yaml
- name: Assign with optimized prompt
  run: |
    # Generate prompt
    prompt_output=$(python3 tools/prompt-generator.py generate ...)
    template_id=$(echo "$prompt_output" | grep "Template ID:" | cut -d: -f2)
    
    # Add to issue
    gh issue comment $ISSUE_NUMBER --body "$prompt_output"
    
    # Record for tracking
    gh issue edit $ISSUE_NUMBER --add-label "prompt:$template_id"
```

## 📚 See Also

- [Full Documentation](./SELF_IMPROVING_PROMPT_ENHANCEMENTS.md)
- [Original Prompt Generator](./prompt-generator.py)
- [Learning Integration](./prompt_learning_integration.py)
- [Auto-Tuner Workflow](../.github/workflows/prompt-auto-tuner.yml)

---

**@create-botter** - Infrastructure that improves itself
