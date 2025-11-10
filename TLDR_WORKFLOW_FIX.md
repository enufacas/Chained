# TLDR Learning Workflow Fix

## Problem
The TLDR learning workflow (`learn-from-tldr.yml`) was running successfully but collecting 0 learnings on every execution. All recent learning files showed empty arrays:

```json
{
  "timestamp": "2025-11-10T20:28:54.968122+00:00",
  "source": "TLDR Tech",
  "learnings": [],
  "trends": []
}
```

## Root Cause
The RSS feed URLs used in the workflow were outdated. TLDR changed their RSS feed URL structure:

**Old format (not working):**
- `https://tldr.tech/tech/rss`
- `https://tldr.tech/ai/rss`
- `https://tldr.tech/devops/rss`

**New format (correct):**
- `https://tldr.tech/api/rss/tech`
- `https://tldr.tech/api/rss/ai`
- `https://tldr.tech/api/rss/devops`

## Solution
Updated the RSS feed URLs in `.github/workflows/learn-from-tldr.yml` to use the correct `/api/rss/` path format.

## Changes Made
```diff
- 'https://tldr.tech/tech/rss',
- 'https://tldr.tech/ai/rss',
- 'https://tldr.tech/devops/rss'
+ 'https://tldr.tech/api/rss/tech',
+ 'https://tldr.tech/api/rss/ai',
+ 'https://tldr.tech/api/rss/devops'
```

## Testing
The fix cannot be fully tested in the local development sandbox due to network restrictions (DNS resolution fails for external domains). However:

1. ✅ YAML syntax is valid (verified with yamllint)
2. ✅ No security issues detected (verified with CodeQL)
3. ✅ URL format confirmed via web research
4. ✅ The Hacker News learning workflow works with similar external API calls

## Expected Outcome
When the workflow runs on GitHub Actions (which has full internet access), it should now successfully:
1. Fetch RSS feeds from TLDR Tech using the updated URLs
2. Extract learnings from the fetched items
3. Create learning files with actual content instead of empty arrays
4. Generate learning issues and PRs with meaningful content

## Next Steps
1. Wait for the next scheduled run (twice daily at 8 AM and 8 PM UTC)
2. Or trigger a manual run via workflow_dispatch
3. Verify that learnings are collected (check the generated JSON files)
4. Monitor workflow logs for any errors

## References
- TLDR Tech RSS Feed Documentation: https://tldr.tech/api/rss/tech
- Related Project: https://github.com/Bullrich/tldr-rss (alternative RSS feed aggregator)

## Related Files
- Workflow: `.github/workflows/learn-from-tldr.yml`
- Learnings Directory: `learnings/`
- Documentation: `learnings/README.md`
