# Combined Learning Workflow

A unified workflow that combines multiple learning sources into a single, efficient learning session.

## Overview

The Combined Learning Workflow fetches insights from three major sources:

1. **GitHub Trending** - What developers are building
2. **TLDR Tech** - Curated tech news and articles
3. **Hacker News** - Community discussions and stories

All sources are processed together, analyzed for trends, and consolidated into a single PR and issue.

## Benefits

### Before: Separate Workflows
- ❌ Multiple workflow runs (3+ per day)
- ❌ Separate PRs and issues for each source
- ❌ Fragmented analysis
- ❌ Higher CI/CD resource usage
- ❌ Harder to see cross-source patterns

### After: Combined Workflow
- ✅ Single workflow run (2x per day)
- ✅ Unified PR and issue
- ✅ Cross-source topic analysis
- ✅ Lower resource usage
- ✅ Better pattern recognition

## Schedule

Runs automatically twice daily:
- **8:00 AM UTC** - Morning learning session
- **8:00 PM UTC** - Evening learning session

## Manual Triggering

You can manually trigger the workflow with custom options:

```yaml
# Go to Actions > Combined Learning Workflow > Run workflow
Options:
  - Include GitHub Trending: true/false
  - Include TLDR Tech: true/false
  - Include Hacker News: true/false
```

This allows you to fetch from specific sources if needed.

## What It Does

### Step 1: Fetch GitHub Trending
- Fetches trending repos for Python, JavaScript, Go, Rust, TypeScript
- Gets overall trending (all languages)
- Extracts repo metadata: stars, forks, description, trending stats
- Saves to `learnings/github_trending_TIMESTAMP.json`

**Output**: ~35-40 trending repositories

### Step 2: Fetch TLDR Tech
- Fetches from TLDR Tech and AI newsletters via RSS
- Gets top 5 articles from each feed
- Attempts to fetch full article content
- Saves to `learnings/tldr_TIMESTAMP.json`

**Output**: ~10 curated tech articles

### Step 3: Fetch Hacker News
- Fetches top 30 stories from Hacker News API
- Includes score, author, comment count
- Saves to `learnings/hn_TIMESTAMP.json`

**Output**: ~30 top stories

### Step 4: Analyze Combined Learnings
- Loads all learnings from current session
- Analyzes for topics:
  - AI/ML
  - Web Development
  - Backend/APIs
  - DevOps
  - Programming Languages
  - Security
- Identifies top trending topics
- Saves analysis to `learnings/combined_analysis_TIMESTAMP.json`

### Step 5: Create Issue
- Creates issue with summary of all learnings
- Includes sample items from each source
- Shows topic analysis results
- Links to all learning files

### Step 6: Create PR
- Rebuilds learnings book
- Commits all new learning files
- Creates PR with detailed summary
- Auto-labels for merging

## Output Files

Each run creates several files in the `learnings/` directory:

```
learnings/
├── github_trending_20251114_082530.json    # GitHub trending repos
├── tldr_20251114_082545.json               # TLDR articles
├── hn_20251114_082600.json                 # Hacker News stories
└── combined_analysis_20251114_082615.json  # Unified analysis
```

## Data Format

All learning files follow a consistent format:

```json
{
  "timestamp": "2025-11-14T08:25:30.123456+00:00",
  "source": "Source Name",
  "learnings": [
    {
      "title": "Learning title",
      "description": "Description or content",
      "url": "https://example.com",
      "source": "Source Name",
      "metadata": {
        // Source-specific fields
      }
    }
  ]
}
```

### GitHub Trending Metadata
```json
"metadata": {
  "full_name": "owner/repo",
  "language": "Python",
  "stars": 12345,
  "forks": 1234,
  "stars_today": 275,
  "trending_filter": "python"
}
```

### Hacker News Metadata
```json
"metadata": {
  "score": 234,
  "by": "username",
  "descendants": 45  // comment count
}
```

## Topic Analysis

The analysis step categorizes learnings into topics:

- **AI/ML**: AI, machine learning, LLMs, GPT, neural networks
- **Web Dev**: JavaScript, TypeScript, React, Vue, frontend
- **Backend**: APIs, servers, databases, Postgres, Redis
- **DevOps**: Docker, Kubernetes, CI/CD, GitHub Actions
- **Languages**: Python, Go, Rust, Java, C++
- **Security**: Vulnerabilities, authentication, encryption

Results show:
- Total mentions per topic
- Top 5 trending topics
- Distribution across sources

## Integration with Existing System

The Combined Learning Workflow:

1. ✅ Uses existing tools (when applicable)
2. ✅ Outputs to same `learnings/` directory
3. ✅ Compatible with learnings book builder
4. ✅ Follows same PR/issue patterns
5. ✅ Uses same labeling conventions

## Resource Usage

### Single Run Metrics
- **Duration**: ~5-8 minutes
- **API Calls**: 
  - GitHub: ~50-70 HTTP requests (trending pages)
  - TLDR: ~2 RSS feeds + article fetches
  - Hacker News: ~30-35 API calls
- **Storage**: ~100-200KB per session
- **Output**: 4 JSON files, 1 issue, 1 PR

### Daily Total
- **Runs**: 2 per day
- **Learnings**: ~160 items per day
- **Storage**: ~400KB per day

Compare to 3 separate workflows × 2 runs each = 6 total runs/day.

## Dependencies

Required Python packages:
```bash
pip install beautifulsoup4 requests feedparser lxml html5lib
```

All dependencies are already in `requirements.txt`.

## Monitoring

Check workflow status:
```bash
# View recent runs
gh run list --workflow=combined-learning.yml

# View specific run
gh run view <run-id>

# View logs
gh run view <run-id> --log
```

## Troubleshooting

### Issue: No learnings fetched
**Solution**: Check network connectivity and source availability

### Issue: Analysis fails
**Solution**: Ensure learning files exist with valid JSON

### Issue: PR creation fails
**Solution**: Check GitHub token permissions (needs `contents: write`)

### Issue: Import errors
**Solution**: Verify all dependencies are installed

## Configuration

### Adjust Fetching Amounts

Edit the workflow file to change:

```yaml
# GitHub trending
max_repos=10  # Change from default 5

# TLDR articles
for item in root.findall('.//item')[:10]:  # Change from [:5]

# Hacker News
top_story_ids = response.json()[:50]  # Change from [:30]
```

### Change Schedule

Modify the cron expressions:
```yaml
on:
  schedule:
    - cron: '0 6,18 * * *'  # 6 AM and 6 PM instead
```

### Add More Languages

In the GitHub trending step:
```python
languages = ['python', 'javascript', 'go', 'rust', 'typescript', 'java', 'cpp']
```

## Examples

### Manual Run for Specific Source

Only GitHub trending:
```
1. Go to Actions
2. Select "Learning: Combined Sources"
3. Click "Run workflow"
4. Uncheck TLDR and Hacker News
5. Run
```

### Testing Locally

```bash
# Test GitHub trending fetch
python3 tools/fetch-github-trending.py --language python --max-repos 5

# Simulate workflow (create test files)
mkdir -p learnings
python3 tools/fetch-github-trending.py --output learnings/test_trending.json
```

## Future Enhancements

Potential improvements:
- [ ] Add more language filters
- [ ] Include Reddit tech discussions
- [ ] Add weekly summary aggregation
- [ ] Implement learning deduplication
- [ ] Add sentiment analysis
- [ ] Create visualization dashboard

## Migration from Separate Workflows

If you want to deprecate the old workflows:

1. ✅ Verify combined workflow runs successfully
2. ✅ Check all sources are included
3. ✅ Confirm PRs and issues are created
4. ❓ Optionally disable old workflows:
   - `learn-from-tldr.yml`
   - `learn-from-hackernews.yml`
   - (Keep `daily-learning-reflection.yml` - it's complementary)

## See Also

- GitHub Trending Fetcher: `tools/fetch-github-trending.py`
- TLDR Learning: `.github/workflows/learn-from-tldr.yml`
- Hacker News Learning: `.github/workflows/learn-from-hackernews.yml`
- Learning System: `learnings/README.md`
- Tool Documentation: `tools/GITHUB_TRENDING_FETCHER_README.md`

---

*This combined workflow makes the learning system more efficient while providing richer insights from multiple sources! 🚀*
