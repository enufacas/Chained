# Custom Agent Usage Analyzer

A tool to analyze and verify custom agent usage in GitHub Copilot workflows.

## Overview

This tool helps investigate whether custom agents are being properly utilized when GitHub Copilot is assigned to issues. It analyzes:
- Issue bodies and comments
- PR descriptions
- Labels and assignees
- Agent mentions and directives

## Installation

No installation required. The tool uses standard Python libraries and the GitHub CLI.

### Prerequisites

- Python 3.6+
- GitHub CLI (`gh`) installed and authenticated
- Access to the repository

## Usage

### Analyze a Specific Issue

```bash
python tools/analyze-custom-agent-usage.py --issue 123
```

This will analyze issue #123 and show:
- Whether Copilot is assigned
- Which custom agents are mentioned
- Evidence from labels, comments, and body
- Related PRs and their agent mentions

### Analyze Multiple Issues

```bash
# Analyze last 50 Copilot-assigned issues (default)
python tools/analyze-custom-agent-usage.py

# Analyze last 20 issues
python tools/analyze-custom-agent-usage.py --limit 20

# Show all issues, not just Copilot-assigned ones
python tools/analyze-custom-agent-usage.py --limit 20 --verbose
```

### Output Example

```
================================================================================
CUSTOM AGENT USAGE ANALYSIS REPORT
================================================================================

Total issues analyzed: 25
Issues assigned to Copilot: 23
Issues with custom agent mentions: 21

Custom agent usage rate: 91.3% (21/23)

────────────────────────────────────────────────────────────────────────────────
CUSTOM AGENT FREQUENCY
────────────────────────────────────────────────────────────────────────────────
  assert-specialist: 8 mentions
  create-guru: 5 mentions
  engineer-master: 4 mentions
  secure-specialist: 3 mentions
  accelerate-master: 1 mentions

────────────────────────────────────────────────────────────────────────────────
DETAILED ANALYSIS
────────────────────────────────────────────────────────────────────────────────

Issue #123: Improve test coverage
  Created: 2024-01-15T10:30:00Z
  Closed: 2024-01-15T14:20:00Z
  ✅ Assigned to Copilot
  ✅ Custom agent mentioned: assert-specialist
  Evidence:
    - Assigned to: github-copilot[bot]
    - Has 'copilot-assigned' label
    - Agent labels: agent:assert-specialist
    - Custom agents in issue body: assert-specialist
  Related PRs (1):
    PR #124: Add comprehensive test suite for auth module
      Author: github-copilot[bot]
      Custom agents: assert-specialist
      - PR created by: github-copilot[bot]
      - Custom agents in PR body: assert-specialist
```

## How It Works

### Detection Methods

The analyzer extracts custom agent mentions from:

1. **HTML Comment Directives**
   ```html
   <!-- COPILOT_AGENT:assert-specialist -->
   ```

2. **@Mentions**
   ```markdown
   @assert-specialist please help with this
   ```

3. **Labels**
   ```
   agent:assert-specialist
   ```

4. **Path References**
   ```markdown
   .github/agents/assert-specialist.md
   ```

5. **Bold Text**
   ```markdown
   **assert-specialist** custom agent
   ```

### Analysis Process

1. Fetches issues with `copilot-assigned` label (or specific issue)
2. Extracts custom agent mentions from all sources
3. Fetches related PRs
4. Generates comprehensive report with evidence
5. Calculates usage statistics

## Options

```
--issue ISSUE_NUM     Analyze a specific issue number
--limit NUM           Number of issues to analyze (default: 50)
--verbose            Show all issues, not just Copilot-assigned
```

## Output Files

The tool generates reports to stdout. Redirect to save:

```bash
python tools/analyze-custom-agent-usage.py --limit 100 > usage-report.txt
```

## Understanding the Results

### Key Metrics

- **Total issues analyzed**: Number of issues examined
- **Issues assigned to Copilot**: Count of Copilot assignments
- **Custom agent usage rate**: Percentage with agent mentions
- **Custom agent frequency**: How often each agent is used

### Evidence Types

- **Assignment**: Issue assigned to Copilot (user or bot)
- **Labels**: Issue has `copilot-assigned` or `agent:*` labels
- **Body mentions**: Custom agents found in issue description
- **Comment mentions**: Custom agents found in issue comments
- **PR references**: Custom agents found in related PRs

## Troubleshooting

### "No Copilot-assigned issues found"

This means:
1. No issues have the `copilot-assigned` label, OR
2. GitHub CLI is not authenticated, OR
3. You don't have read access to the repository

**Solution**: Ensure `gh auth login` is configured properly.

### "gh: To use GitHub CLI in a GitHub Actions workflow..."

This means the `GH_TOKEN` environment variable is not set.

**Solution (in GitHub Actions)**:
```yaml
env:
  GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

**Solution (locally)**:
```bash
export GH_TOKEN=$(gh auth token)
```

## Related Documentation

- [Evidence Report](../CUSTOM_AGENT_USAGE_EVIDENCE.md) - Detailed evidence of custom agent usage
- [Summary](../CUSTOM_AGENT_USAGE_SUMMARY.md) - Quick reference guide
- [Custom Agents](../.github/agents/README.md) - Agent definitions
- [Copilot Instructions](../.github/copilot-instructions.md) - How Copilot uses agents

## Examples

### Check if a specific issue uses custom agents

```bash
python tools/analyze-custom-agent-usage.py --issue 456
```

### Generate a usage report for the last month

```bash
python tools/analyze-custom-agent-usage.py --limit 100 --verbose > monthly-report.txt
```

### Quick check of recent activity

```bash
python tools/analyze-custom-agent-usage.py --limit 10
```

## Testing

Run the test suite:

```bash
python tests/test_custom_agent_usage_analyzer.py
```

Expected output: `Ran 17 tests in 0.002s OK`

## Contributing

This tool is part of the Chained autonomous AI ecosystem. When making changes:

1. Maintain backward compatibility
2. Add tests for new features
3. Update this README
4. Follow existing code style

## License

Same license as the main repository (see LICENSE file).

## Support

For issues or questions:
1. Check the [FAQ](../FAQ.md)
2. Review the [Evidence Report](../CUSTOM_AGENT_USAGE_EVIDENCE.md)
3. Open an issue in the repository

---

**Note**: This tool proves that custom agents ARE being used by GitHub Copilot, contrary to initial concerns. See the Evidence Report for complete analysis.
