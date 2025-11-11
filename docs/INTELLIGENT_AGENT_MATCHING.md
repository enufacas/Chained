# 🧠 Intelligent Agent Matching System

## Overview

The Chained repository includes an **Intelligent Agent Matching System** that automatically analyzes GitHub issues and matches them to the most appropriate specialized agent based on content analysis.

## How It Works

When an issue is created or updated, the system:

1. **Analyzes** the issue title and description
2. **Scores** the content against keyword patterns for each agent specialization
3. **Matches** the issue to the agent with the highest score
4. **Assigns** the issue to GitHub Copilot with agent-specific guidance
5. **Comments** on the issue with the matched agent information

## Agent Specializations

The system recognizes 10 specialized agent types:

| Agent | Specialization | Keywords |
|-------|---------------|----------|
| 🐛 **bug-hunter** | Finding and fixing bugs | bug, error, crash, fail, broken, exception |
| 🏗️ **feature-architect** | Designing and building features | feature, new, add, implement, create, build |
| 📚 **doc-master** | Creating documentation | documentation, docs, readme, guide, tutorial |
| ✅ **test-champion** | Writing and improving tests | test, coverage, unit test, qa, validation |
| ⚡ **performance-optimizer** | Optimizing performance | slow, optimize, speed, latency, bottleneck |
| 🛡️ **security-guardian** | Security vulnerabilities | security, vulnerability, exploit, authentication |
| 🎨 **code-poet** | Code readability and style | refactor, clean, readable, maintainable, style |
| ♻️ **refactor-wizard** | Code restructuring | refactor, duplicate, technical debt, simplify |
| 🔌 **integration-specialist** | External integrations | integration, api, webhook, external service |
| ✨ **ux-enhancer** | User experience improvements | ui, ux, usability, accessibility, design |

## Confidence Levels

The system assigns confidence levels based on match scores:

- **High** (score ≥ 5): Strong match with clear keywords
- **Medium** (score ≥ 3): Moderate match with some relevant terms
- **Low** (score < 3): Weak match or default assignment

## Usage

### Automatic Matching

The system runs automatically when:
- New issues are created
- The Copilot assignment workflow runs (every 3 hours)
- Manual workflow dispatch

### Manual Testing

You can test the matching system manually:

```bash
# Test with title only
python3 tools/match-issue-to-agent.py "Fix bug in authentication"

# Test with title and body
python3 tools/match-issue-to-agent.py "Add new feature" "We need to implement user profiles"
```

### Output Format

The tool returns JSON with match details:

```json
{
  "agent": "bug-hunter",
  "score": 7,
  "confidence": "high",
  "emoji": "🐛",
  "description": "Specialized agent for finding and fixing bugs...",
  "all_scores": { ... },
  "reason": "Matched based on issue content analysis"
}
```

## Algorithm

The matching algorithm uses a weighted scoring system:

1. **Keyword Matching** (1 point each): Checks for presence of keywords in lowercase text
2. **Pattern Matching** (2 points each): Uses regex patterns for more precise matching
3. **Title Emphasis**: Title content is weighted twice as heavily as body content
4. **Best Match**: Agent with highest score is selected

### Example Scoring

For issue: "Fix critical bug in user login"

```
bug-hunter: 4 points (keywords: "bug", "fix", patterns: "bug", "fix")
feature-architect: 0 points
security-guardian: 3 points (keywords: "login", patterns: "login")
...

Winner: bug-hunter (highest score)
```

## Integration with Workflows

The system integrates with the **Copilot Assignment Workflow** (`copilot-graphql-assign.yml`):

1. Workflow checks out the repository
2. Sets up Python and dependencies
3. For each issue:
   - Fetches issue title and body
   - Runs matching algorithm
   - Stores matched agent info
   - Adds comment with agent details
   - Assigns to Copilot with context

## Benefits

### For Autonomous Operation

- **Context-Aware**: Issues are handled with specialized knowledge
- **Better Quality**: Implementations follow agent-specific best practices
- **Transparency**: Users see which agent specialization was matched

### For Developers

- **Clear Guidance**: Contributors know which expertise area applies
- **Consistent Approach**: Similar issues handled consistently
- **Learning Tool**: Helps understand issue categorization

## Customization

### Adding Keywords

Edit `tools/match-issue-to-agent.py` and add to `AGENT_PATTERNS`:

```python
'your-agent': {
    'keywords': ['keyword1', 'keyword2', ...],
    'patterns': [r'\bpattern1\b', r'\bpattern2\b', ...]
}
```

### Adjusting Scoring

Modify the scoring weights in `calculate_match_score()`:
- Change keyword point value (currently 1)
- Change pattern point value (currently 2)
- Adjust confidence thresholds

### Creating New Agents

1. Create agent definition in `.github/agents/your-agent.md`
2. Add keywords/patterns to `AGENT_PATTERNS`
3. Test with sample issues

## Examples

### Bug Report
```
Title: "Login fails with error 500"
Body: "When users try to log in, they get a 500 error"

Match: bug-hunter (high confidence)
Reason: Keywords "fails", "error" trigger bug patterns
```

### Feature Request
```
Title: "Add dark mode to dashboard"
Body: "Implement a dark theme option for the main dashboard"

Match: feature-architect (high confidence)
Reason: Keywords "add", "implement" + "feature" indication
```

### Documentation
```
Title: "Update API docs"
Body: "The API documentation needs examples for authentication"

Match: doc-master (high confidence)
Reason: Strong documentation keywords present
```

## Troubleshooting

### Issue Not Matching Expected Agent

**Cause**: Keywords may not be triggering the expected agent

**Solution**: 
1. Test manually: `python3 tools/match-issue-to-agent.py "title" "body"`
2. Check `all_scores` in output to see scoring
3. Add more specific keywords to AGENT_PATTERNS
4. Use more descriptive issue titles/descriptions

### Low Confidence Matches

**Cause**: Issue description is vague or doesn't contain clear keywords

**Solution**:
- Write more descriptive issue titles
- Include specific technical terms in issue body
- Add labels manually to guide classification

### Default Agent Selected

**Cause**: No keywords matched any agent patterns

**Solution**:
- System defaults to `feature-architect` for general issues
- Add keywords to make issue more specific
- This is expected for very general or unique requests

## Future Enhancements

Potential improvements to the system:

- **Machine Learning**: Train on historical issues for better matching
- **Multi-Agent**: Allow issues to match multiple agents for collaboration
- **Learning Feedback**: Adjust weights based on successful completions
- **User Preferences**: Allow manual agent selection or override
- **Complexity Analysis**: Factor in issue complexity for agent assignment

## Related Documentation

- [Agent Definitions](../.github/agents/README.md)
- [Custom Agents Convention](./CUSTOM_AGENTS_CONVENTIONS.md)
- [Workflows Documentation](./WORKFLOWS.md)
- [Agent System Overview](../agents/README.md)

---

*Part of the Chained autonomous AI ecosystem - where intelligence meets automation.* 🚀
