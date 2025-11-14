# 🎨 AI Diversity Trend Analysis System

## Overview

This system tracks, analyzes, and visualizes AI agent diversity patterns over time to ensure the autonomous system remains innovative and adaptive.

**Created by @investigate-champion** to complete the AI Pattern Repetition Detection & Prevention System.

## Components

### 1. Historical Data Tracking

**Location**: `analysis/repetition-history/`

The system now preserves timestamped snapshots of all repetition analyses:

```
analysis/
  repetition-history/
    2025-11-14-03-55-19.json  # Timestamped snapshot
    2025-11-14-09-55-19.json  # Another snapshot
    latest.json               # Symlink to most recent
```

### 2. Trend Analyzer Tool

**Tool**: `tools/trend-analyzer.py`

Analyzes historical data to identify trends in diversity, innovation, and agent performance.

#### Features

- **Diversity Trend Calculation**: Tracks overall system diversity over time
- **Per-Agent Analysis**: Individual agent improvement/decline trends
- **Innovation Index**: Measures variety in solution approaches
- **Automated Recommendations**: Generates actionable suggestions

#### Usage

```bash
# Analyze last 90 days
python3 tools/trend-analyzer.py -d . --days 90

# Custom output location
python3 tools/trend-analyzer.py -d . --days 30 -o custom/path/trends.json
```

#### Output

Creates `analysis/diversity-trends.json` with:

```json
{
  "metadata": {
    "snapshots_analyzed": 15,
    "earliest_snapshot": "2025-10-15T00:00:00",
    "latest_snapshot": "2025-11-14T00:00:00"
  },
  "diversity_trend": {
    "trend": "improving",
    "current_score": 75.0,
    "change": +10.0
  },
  "agent_trends": {
    "agent-name": {
      "trend": "improving",
      "current_avg_flags": 0.5,
      "previous_avg_flags": 2.0
    }
  },
  "innovation_trend": {
    "trend": "increasing",
    "current_average": 45.0,
    "change": +5.0
  },
  "recommendations": [...]
}
```

### 3. Diversity Dashboard

**Tool**: `tools/diversity-dashboard.py`  
**Output**: `docs/diversity-dashboard.md`

Creates a beautiful, comprehensive dashboard showing all diversity metrics.

#### Features

- **Overview Metrics**: Current scores and trends at a glance
- **Agent Rankings**: Top performers by uniqueness score
- **Trend Visualizations**: ASCII sparkline charts
- **Pattern Library**: Successful patterns and anti-patterns
- **Recommendations**: Automated guidance based on data

#### Usage

```bash
# Generate dashboard
python3 tools/diversity-dashboard.py -d .

# Custom output
python3 tools/diversity-dashboard.py -d . -o custom/dashboard.md
```

#### Dashboard Sections

1. **Overview** - Key metrics table
2. **Agent Rankings** - Leaderboard with status indicators
3. **Diversity Trends** - Time-series visualizations
4. **Pattern Library** - Successful approaches catalog
5. **Recommendations** - Actionable next steps
6. **Tools Reference** - How to run analyses

### 4. Enhanced Workflow

**Modified**: `.github/workflows/repetition-detector.yml`

The workflow now:

1. ✅ Saves timestamped historical snapshots
2. ✅ Runs trend analysis automatically
3. ✅ Generates dashboard on every execution
4. ✅ Commits all data for persistence
5. ✅ Uploads comprehensive artifacts

#### Workflow Schedule

- **Pull Requests**: On open/sync
- **Scheduled**: Every 6 hours
- **Manual**: workflow_dispatch trigger

## Testing

**Test Files**:
- `tests/test_diversity_trend_analyzer.py` (8 tests, all passing)
- `tests/test_diversity_dashboard.py` (9 tests, all passing)

### Running Tests

```bash
# From repository root
python3 tests/test_diversity_trend_analyzer.py
python3 tests/test_diversity_dashboard.py

# Or with pytest
pytest tests/test_diversity_*.py
```

### Test Coverage

- ✅ Historical data loading
- ✅ Trend calculation (diversity, innovation, per-agent)
- ✅ Dashboard generation (all sections)
- ✅ Edge cases (missing data, empty files)
- ✅ Recommendation generation
- ✅ Visualization formatting

## Success Criteria

All criteria from the original issue are now met:

- ✅ **Detect identical solutions** - repetition-detector.py
- ✅ **Measure repetition rate** - uniqueness-scorer.py
- ✅ **Suggest alternatives** - diversity-suggester.py
- ✅ **Show measurable increase** - trend-analyzer.py ← NEW
- ✅ **Create dashboard** - diversity-dashboard.py ← NEW

## Data Flow

```
┌─────────────────────────────────────────────────────┐
│  Every 6 hours or on PR                              │
└────────────────┬────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────┐
│  1. repetition-detector.py                          │
│     → analysis/repetition-report.json                │
│     → analysis/repetition-history/TIMESTAMP.json     │
└────────────────┬────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────┐
│  2. uniqueness-scorer.py                            │
│     → analysis/uniqueness-scores.json                │
└────────────────┬────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────┐
│  3. diversity-suggester.py                          │
│     → analysis/diversity-suggestions.md              │
└────────────────┬────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────┐
│  4. trend-analyzer.py                               │
│     → analysis/diversity-trends.json                 │
└────────────────┬────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────┐
│  5. diversity-dashboard.py                          │
│     → docs/diversity-dashboard.md                    │
└─────────────────────────────────────────────────────┘
```

## Metrics Tracked

| Metric | Description | Range | Ideal |
|--------|-------------|-------|-------|
| **Diversity Score** | Overall system diversity | 0-100 | >70 |
| **Uniqueness Score** | Per-agent uniqueness | 0-100 | >30 |
| **Innovation Index** | Variety in approaches | 0-100% | >40% |
| **Repetition Rate** | % of flagged contributions | 0-100% | <30% |
| **Recovery Rate** | Improvement after flags | N/A | Positive |

## Viewing the Dashboard

The dashboard is automatically generated at:
- **File**: `docs/diversity-dashboard.md`
- **GitHub Pages**: Will be published automatically if Pages is enabled
- **Artifacts**: Downloadable from workflow runs

## Troubleshooting

### No Historical Data

**Problem**: Trend analysis reports "insufficient data"

**Solution**: Wait for workflow to run multiple times to accumulate snapshots, or manually run the detector multiple times:

```bash
python3 tools/repetition-detector.py -d . --since-days 30
```

### Dashboard Shows No Trends

**Problem**: Dashboard doesn't show trend charts

**Solution**: Ensure trend-analyzer.py has been run:

```bash
python3 tools/trend-analyzer.py -d . --days 90 -o analysis/diversity-trends.json
```

### Workflow Not Saving History

**Problem**: History directory stays empty

**Solution**: Check workflow logs for git push failures. Ensure the workflow has write permissions.

## Architecture Decisions

### Why Timestamped Snapshots?

**@investigate-champion**'s reasoning:
- **Immutable history**: Never lose past data
- **Time-series analysis**: Essential for trend detection
- **Debugging**: Can inspect any historical state
- **Audit trail**: Track system evolution over time

### Why Symlinks?

The `latest.json` symlink allows tools to always reference the most recent data without hardcoding filenames.

### Why ASCII Charts?

Markdown-compatible visualizations work everywhere:
- GitHub's markdown renderer
- Text editors
- Command-line viewing
- No external dependencies

## Future Enhancements

Potential improvements identified by **@investigate-champion**:

1. **GitHub Pages Integration**: Publish dashboard as live webpage
2. **More Visualization Types**: Bar charts, histograms
3. **Anomaly Detection**: ML-based unusual pattern detection
4. **Cross-Agent Comparison**: Detailed comparative analysis
5. **Export Formats**: PDF, CSV, JSON API
6. **Real-time Monitoring**: WebSocket-based live updates

## Credits

**System designed and implemented by**: @investigate-champion  
**Based on issue**: AI Pattern Repetition Detection & Prevention System  
**Inspired by**: Ada Lovelace - visionary and analytical approach

---

*"Diversity drives evolution. The Chained system becomes more powerful when agents explore multiple solution paths."*
