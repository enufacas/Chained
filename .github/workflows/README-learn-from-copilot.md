# Learn from GitHub Copilot Workflow

## Overview

The `learn-from-copilot.yml` workflow automatically collects learnings about GitHub Copilot from multiple authoritative sources to enhance the autonomous system's understanding of GitHub Copilot capabilities.

**Workflow Owner:** @workflows-tech-lead  
**Status:** ✅ Production Ready  
**Grade:** A- (Excellent with continuous improvements)

## Purpose

This workflow enables the autonomous AI system to continuously learn about GitHub Copilot by:

1. **Fetching Content** from multiple sources:
   - 📖 Official GitHub Copilot documentation
   - 💬 Reddit r/GithubCopilot community discussions
   - 🗣️ GitHub Community forum posts

2. **Processing & Validation**:
   - Intelligently parsing and cleaning content
   - Validating quality with acceptance rate tracking
   - Filtering out low-quality or irrelevant content

3. **Trend Analysis**:
   - Identifying hot themes across all learnings
   - Detecting emerging technologies and patterns
   - Scoring topics by relevance and momentum

4. **Documentation & Visibility**:
   - Creating issues to document learning sessions
   - Generating PRs with learning updates
   - Providing comprehensive activity logs

## Schedule

The workflow runs **twice daily** on a fixed schedule:
- **09:00 UTC** (Morning run)
- **21:00 UTC** (Evening run)

```yaml
schedule:
  - cron: '0 9,21 * * *'
```

### Manual Triggering

The workflow can also be triggered manually via `workflow_dispatch` with configurable parameters:

```yaml
docs_count: '5'        # Number of documentation topics (1-50)
reddit_count: '5'      # Number of Reddit posts (1-50)
discussions_count: '5' # Number of GitHub discussions (1-50)
```

## Security

### Permissions

The workflow requires specific permissions documented inline:

```yaml
permissions:
  contents: write       # Required: Create branches and push commits
  issues: write         # Required: Create learning documentation issues
  pull-requests: write  # Required: Create PRs for learnings
```

### Secret Handling

- Uses `GITHUB_TOKEN` secret for authenticated API requests
- Token is scoped to the repository only
- No external API keys required

### Security Features

✅ **Input Validation**: All workflow inputs are validated (numeric, 1-50 range)  
✅ **Branch Protection**: Creates PRs instead of pushing directly to main  
✅ **Injection Prevention**: Uses heredoc syntax for embedded Python scripts  
✅ **Isolation**: Temporary files stored in `/tmp` directory  
✅ **Explicit Permissions**: Minimum required permissions defined  

## Reliability

### Timeout Protection

```yaml
timeout-minutes: 30  # Prevents infinite runs if external APIs hang
```

### Error Handling

- **Conditional Steps**: Steps run only if data is available
- **Always() Logging**: Final step logs activity regardless of outcome
- **Graceful Failures**: Missing files handled with fallbacks
- **Error Messages**: Clear messages with `|| echo` patterns

### Resilience Features

✅ **Multi-source Fetching**: Independent fetch from each source  
✅ **Validation Gates**: Quality checks before processing  
✅ **Commit Safety**: Checks for changes before creating branches  
✅ **Step Conditions**: Prevents cascading failures  

## Performance

### Optimization Features

✅ **Dependency Caching**: Pip cache enabled for faster runs  
✅ **Incremental Updates**: Only commits when changes detected  
✅ **Efficient Parsing**: Batch processing of learnings  
✅ **Smart Analysis**: 7-day lookback window for trends  

### Resource Usage

- **Typical Runtime**: 5-10 minutes
- **Network Requests**: ~15-20 API calls per run
- **Storage Impact**: ~50KB per learning session
- **CPU/Memory**: Low usage (parsing and analysis)

## Data Flow

```
┌─────────────────────────────────────────────────────────────┐
│ 1. FETCH                                                    │
│    ├─ GitHub Copilot Docs (5 topics)                       │
│    ├─ Reddit r/GithubCopilot (5 posts)                     │
│    └─ GitHub Discussions (5 threads)                       │
├─────────────────────────────────────────────────────────────┤
│ 2. PARSE & CLEAN                                           │
│    ├─ IntelligentContentParser                            │
│    ├─ Quality validation                                   │
│    └─ Acceptance rate calculation                          │
├─────────────────────────────────────────────────────────────┤
│ 3. ANALYZE TRENDS                                          │
│    ├─ ThematicAnalyzer (7-day lookback)                   │
│    ├─ Technology scoring                                   │
│    └─ Hot theme detection                                  │
├─────────────────────────────────────────────────────────────┤
│ 4. DOCUMENT                                                │
│    ├─ Create learning issue                                │
│    ├─ Generate PR with updates                             │
│    └─ Log activity                                         │
└─────────────────────────────────────────────────────────────┘
```

## Output Files

### Learning Files

**Format:** `learnings/copilot_YYYYMMDD_HHMMSS.json`

Contains:
- Raw learnings from all sources
- Parsed and cleaned content
- Source counts and metadata
- Parsing statistics

### Analysis Files

**Format:** `learnings/analysis_YYYYMMDD_HHMMSS.json`

Contains:
- Top technologies (scored)
- Top companies (scored)
- Notable personalities
- Emerging topics
- Hot themes for agent spawning

### Documentation

- **Issues**: Created with learning summary and hot themes
- **PRs**: Branch with learning updates and analysis
- **Logs**: Workflow output with detailed activity

## Integration Points

### Upstream Dependencies

- `tools/fetch-github-copilot.py` - Content fetching script
- `tools/intelligent-content-parser.py` - Quality validation
- `tools/thematic-analyzer.py` - Trend analysis
- `tools/build-learnings-book.py` - Documentation generation

### Downstream Consumers

- Mission generation workflows
- Agent assignment system
- Learnings book generator
- Autonomous pipeline orchestrator

## Monitoring

### Success Indicators

✅ Learning count > 0  
✅ Acceptance rate > 80%  
✅ Hot themes identified  
✅ PR created successfully  
✅ Issue created successfully  

### Failure Scenarios

❌ **All sources fail**: Check network connectivity  
❌ **Parsing fails**: Check content format changes  
❌ **Analysis fails**: Check data file structure  
❌ **PR creation fails**: Check branch protection settings  
❌ **Issue creation fails**: Check permissions  

### Logs & Debugging

1. **Workflow Logs**: Check GitHub Actions run details
2. **Step Outputs**: Review each step's output for errors
3. **Generated Files**: Inspect `learnings/` directory
4. **Final Summary**: Check "Log learning activity" step

## Maintenance

### Regular Tasks

- **Weekly**: Review learning quality and acceptance rates
- **Monthly**: Adjust source counts based on quality
- **Quarterly**: Update dependencies and tools
- **As Needed**: Adjust schedule based on API rate limits

### Dependency Updates

Current dependencies:
- Python 3.11
- beautifulsoup4 >= 4.11.0
- requests >= 2.28.0
- lxml >= 4.9.0
- html5lib >= 1.1

Update via: `pip install --upgrade -r requirements.txt`

### API Rate Limits

**GitHub API**: 5,000 requests/hour (authenticated)  
**Reddit API**: 60 requests/minute (unauthenticated)  
**Current Usage**: ~20 requests per run = 40 requests/day  
**Buffer**: Well within limits  

## Troubleshooting

### Common Issues

**Issue**: "No learnings fetched"  
**Solution**: Check source availability, try manual trigger  

**Issue**: "Low acceptance rate"  
**Solution**: Review content quality, adjust filters  

**Issue**: "Timeout exceeded"  
**Solution**: Check external API response times  

**Issue**: "Branch protection violation"  
**Solution**: Verify workflow creates branches, not direct pushes  

**Issue**: "Permission denied"  
**Solution**: Check `contents`, `issues`, `pull-requests` permissions  

### Debug Mode

To enable verbose logging, add to step:
```yaml
run: |
  set -x  # Enable bash debug mode
  # ... existing commands
```

## Best Practices Compliance

### ✅ Implemented Best Practices

1. **Security**
   - Input validation
   - Secret handling
   - Injection prevention
   - Explicit permissions

2. **Reliability**
   - Timeout protection
   - Error handling
   - Conditional execution
   - Always() logging

3. **Performance**
   - Dependency caching
   - Incremental updates
   - Efficient parsing
   - Smart analysis

4. **Documentation**
   - Inline comments
   - Clear step names
   - README documentation
   - Comprehensive logging

### 🔄 Continuous Improvements

Future enhancements under consideration:
- Workflow chaining for learning pipeline
- Failure notifications (Slack/Discord)
- Advanced rate limit handling
- Performance metrics collection
- A/B testing for different learning strategies

## Contact & Support

**Workflow Owner:** @workflows-tech-lead  
**Issue Tracking:** GitHub Issues with label `workflow:learn-from-copilot`  
**Documentation:** This README and inline workflow comments  

## Related Documentation

- [Branch Protection Rules](.github/instructions/branch-protection.instructions.md)
- [Workflow Agent Assignment](.github/instructions/workflow-agent-assignment.instructions.md)
- [Agent Issue Updates](.github/instructions/agent-issue-updates.instructions.md)

---

*Last Updated: 2025-11-19*  
*Reviewed By: @workflows-tech-lead*  
*Status: ✅ Production Ready*
