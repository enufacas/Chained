# GitHub Trending Fetcher

A tool to fetch trending repositories from GitHub for the learning system.

## Overview

This tool scrapes GitHub's trending page to collect information about popular repositories. Since GitHub doesn't provide an official API for trending repos, we parse the HTML directly.

## Features

- **Multiple Language Support**: Fetch trending repos for specific languages (Python, JavaScript, Go, etc.)
- **Time Ranges**: Daily, weekly, or monthly trending repos
- **Rich Metadata**: Extracts repo name, description, stars, forks, language, and trending statistics
- **Rate Limiting**: Built-in delays to respect GitHub's servers
- **Learning Integration**: Outputs JSON format compatible with the existing learning system

## Usage

### Command Line

```bash
# Fetch overall trending repos
python3 tools/fetch-github-trending.py --max-repos 10

# Fetch trending Python repos
python3 tools/fetch-github-trending.py --language python --max-repos 20

# Fetch weekly trending repos
python3 tools/fetch-github-trending.py --since weekly

# Fetch for multiple languages
python3 tools/fetch-github-trending.py --languages python javascript go rust

# Save to file
python3 tools/fetch-github-trending.py --output learnings/trending.json
```

### Python API

```python
from fetch_github_trending import GitHubTrendingFetcher

fetcher = GitHubTrendingFetcher()

# Fetch daily trending Python repos
repos = fetcher.fetch_trending(language='python', since='daily', max_repos=10)

# Fetch for multiple languages
results = fetcher.fetch_multiple_languages(
    languages=['python', 'javascript', 'go'],
    since='daily',
    max_per_lang=5
)
```

## Output Format

```json
{
  "timestamp": "2025-11-14T04:29:38.998022+00:00",
  "source": "GitHub Trending",
  "since": "daily",
  "language_filter": "python",
  "repository_count": 5,
  "repositories": [
    {
      "url": "https://github.com/owner/repo",
      "owner": "owner",
      "name": "repo",
      "full_name": "owner/repo",
      "description": "Repository description...",
      "language": "Python",
      "stars": 12345,
      "stars_text": "12,345",
      "forks": 1234,
      "forks_text": "1,234",
      "stars_period": "275 stars today",
      "stars_period_count": 275,
      "built_by": ["contributor1", "contributor2"]
    }
  ]
}
```

## Integration with Learning System

This tool is integrated into the Combined Learning Workflow (`.github/workflows/combined-learning.yml`), which:

1. Fetches trending repos for multiple languages
2. Converts them to the learning system format
3. Combines them with TLDR and Hacker News data
4. Performs unified analysis
5. Creates consolidated issues and PRs

## How It Works

1. **HTTP Request**: Sends a GET request to `https://github.com/trending/{language}?since={timeframe}`
2. **HTML Parsing**: Uses BeautifulSoup to parse the response
3. **Data Extraction**: Finds repository articles and extracts metadata from structured HTML
4. **Normalization**: Converts strings like "1.2k" to integers (1200)
5. **Output**: Returns structured data as Python dictionaries

## Limitations

- **No Official API**: GitHub doesn't provide an API for trending, so this uses web scraping
- **Rate Limiting**: Be respectful of GitHub's servers; built-in delays are included
- **HTML Changes**: If GitHub changes their page structure, the parser may need updates
- **Public Data Only**: Only fetches publicly visible trending information

## Error Handling

The tool includes robust error handling:
- Network timeouts
- Malformed HTML
- Missing data fields
- Rate limiting responses

Errors are logged to stderr while maintaining valid JSON output.

## Security

- Uses proper User-Agent headers
- Respects robots.txt guidelines
- No authentication required (public data only)
- Timeouts prevent hanging requests

## Examples

### Fetch Top AI/ML Repos

```bash
python3 tools/fetch-github-trending.py \
  --languages python jupyter-notebook \
  --max-repos 10 \
  --output trending_ai.json
```

### Monitor Weekly Web Dev Trends

```bash
python3 tools/fetch-github-trending.py \
  --languages javascript typescript vue react \
  --since weekly \
  --output trending_webdev_weekly.json
```

### Get All Languages

```bash
python3 tools/fetch-github-trending.py \
  --since daily \
  --max-repos 25 \
  --output trending_all.json
```

## Maintenance

If GitHub changes their trending page structure, update the `_parse_repo_article()` method in the `GitHubTrendingFetcher` class. The current implementation uses CSS class names like:

- `Box-row` for repository articles
- `h3` for repository names
- `octicon-star` for star counts
- `octicon-repo-forked` for fork counts

## Contributing

When updating the parser:
1. Test with multiple languages
2. Verify all metadata fields
3. Check rate limiting still works
4. Update tests if needed

## See Also

- Combined Learning Workflow: `.github/workflows/combined-learning.yml`
- Other learning tools: `tools/fetch-web-content.py`
- Learning system docs: `learnings/README.md`
