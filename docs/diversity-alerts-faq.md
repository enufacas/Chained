# 🎨 AI Agent Diversity Alerts - Frequently Asked Questions

**Created by:** @support-master  
**Purpose:** Help users understand and respond to diversity alerts appropriately

---

## What is a Diversity Alert?

A **diversity alert** is an automated notification that an AI agent's contributions show low diversity in their approach, structure, or innovation compared to established thresholds.

**What it measures:**
- **Structural Uniqueness**: Variety in file types and commit patterns
- **Approach Diversity**: Different problem-solving strategies used
- **Innovation Index**: Unique contributions compared to other agents

**What it doesn't measure:**
- Code quality
- Bug count
- PR success rate
- Overall performance

---

## Understanding Diversity Scores

### Score Components

| Metric | Weight | What It Measures | Good Score |
|--------|--------|------------------|------------|
| **Structural Uniqueness** | 30% | File type diversity, commit message variety | 40+ |
| **Approach Diversity** | 40% | Different solution approaches | 40+ |
| **Innovation Index** | 30% | Unique patterns vs other agents | 30+ |
| **Overall Score** | 100% | Weighted average of above | 30+ |

### Score Interpretation

- **85+**: Excellent diversity (Hall of Fame level)
- **60-84**: Good diversity (healthy variation)
- **30-59**: Acceptable diversity (meets threshold)
- **Below 30**: Low diversity (coaching recommended)

---

## When Should I Take Action?

### ✅ Take Action If:

1. **Agent has 3+ contributions** in the analysis period
2. **Score is genuinely below 30** with current data
3. **Agent appears in `flagged_agents` list** in the analysis file
4. **Metrics are consistent** when re-running analysis

**What to do:**
- Review `analysis/diversity-suggestions.md` for specific recommendations
- Examine agent's recent contributions to identify patterns
- Consider assigning diverse issue types to the agent
- Learn from high-performing agents' approaches

### ⚠️ Question the Alert If:

1. **Agent has fewer than 3 contributions**
   - Alert may be premature
   - Insufficient data for reliable analysis

2. **Agent doesn't appear in git history**
   - Possible stale or test data
   - Verify agent actually exists

3. **Scores don't match when re-running analysis**
   - Data may be corrupted or outdated
   - Run `python3 tools/uniqueness-scorer.py -d .` to verify

4. **`flagged_agents` list is empty**
   - Issue created incorrectly
   - No agents actually need coaching

---

## Common Scenarios

### Scenario 1: "Insufficient data" Alert

**Situation:** Alert created but analysis shows "Insufficient data (1 contributions, need 3+)"

**Explanation:** Agent hasn't contributed enough for meaningful diversity analysis. The system requires minimum 3 contributions to establish patterns.

**Action:** Dismiss the alert. Wait for more contributions.

**When to revisit:** After agent has 3+ contributions in the analysis period.

### Scenario 2: New Agent with Low Score

**Situation:** Agent with exactly 3-5 contributions shows low diversity score

**Explanation:** Small sample size can produce unreliable scores. Patterns haven't fully emerged yet.

**Action:** Monitor but don't over-react. Consider it informational.

**When to take seriously:** After agent has 10+ contributions with consistently low scores.

### Scenario 3: Specialized Agent

**Situation:** Agent focused on specific domain (e.g., only security fixes) shows low diversity

**Explanation:** Specialization can legitimately result in lower diversity scores. This may be intentional and valuable.

**Action:** Consider whether diversity is appropriate for this agent's role. Some specialization is beneficial.

**Alternative:** Adjust expectations or create agent-specific thresholds.

### Scenario 4: High-Quality Work, Low Diversity

**Situation:** Agent produces excellent results but scores low on diversity metrics

**Explanation:** Diversity and quality are independent metrics. An agent can excel at one without the other.

**Action:** Balance diversity coaching with recognition of quality work. Don't sacrifice quality for diversity.

**Best approach:** Gradually introduce variety while maintaining quality standards.

---

## How to Verify an Alert

### Step 1: Check the Analysis Files

```bash
# View the uniqueness scores
cat analysis/uniqueness-scores.json

# Look for your agent in "flagged_agents"
jq '.flagged_agents[] | select(.agent_id == "your-agent-id")' analysis/uniqueness-scores.json
```

### Step 2: Run Manual Analysis

```bash
# Run scorer with current data
python3 tools/uniqueness-scorer.py -d . --days 30 --threshold 30 --min-contributions 3

# Check for your agent in output
```

### Step 3: Verify Git History

```bash
# Check agent's commits in last 30 days
git log --all --author="agent-name" --since="30 days ago" --oneline

# Count contributions
git log --all --author="agent-name" --since="30 days ago" --oneline | wc -l
```

### Step 4: Compare Results

- Issue claims match analysis files? ✅ Legitimate alert
- Scores differ significantly? ⚠️ Possible false positive
- Agent not in git history? ❌ Definitely false positive
- Insufficient data note present? ⚠️ Premature alert

---

## Minimum Data Requirements

For reliable diversity analysis, the system needs:

### Per-Agent Requirements

- **Minimum contributions**: 3+
- **Ideal contributions**: 10+
- **Multiple file types**: For structural uniqueness
- **Varied approaches**: For approach diversity

### Repository Requirements

- **Multiple agents**: For innovation index calculation
- **Active development**: Regular commits over time
- **Diverse work**: Not all the same type of changes

### Timeline Considerations

- **Short term (< 1 month)**: Insufficient data likely
- **Medium term (1-3 months)**: Minimum threshold possible
- **Long term (3+ months)**: Reliable patterns emerge

---

## What Causes False Positives?

### Common Causes

1. **Repository too new**
   - Only a few commits total
   - Not enough data for any agent

2. **Manual testing**
   - Test issues created with example data
   - Data doesn't match actual repository

3. **Stale data**
   - Analysis based on old repository state
   - Git history has changed since analysis

4. **Data file corruption**
   - Temporary issues during workflow run
   - Analysis files don't match git history

5. **Workflow bugs**
   - Logic errors in issue creation
   - Validation steps skipped

### Prevention Measures

The system has multiple safeguards:
- ✅ Excludes system bots
- ✅ Requires minimum 3 contributions
- ✅ Validates data before creating issues
- ✅ Marks insufficient data explicitly

---

## Understanding the Workflow

### When Analysis Runs

- **PR Events**: On pull request open/synchronize
- **Scheduled**: Every 6 hours
- **Manual**: Via workflow_dispatch

### What It Does

1. **Collects contributions** from git history
2. **Calculates scores** for all agents
3. **Filters out** system bots and insufficient data
4. **Flags agents** below threshold with sufficient data
5. **Creates issue** only if flagged agents exist
6. **Generates reports** in `analysis/` directory

### Data Flow

```
Git History
    ↓
Collect Contributions (repetition-detector.py)
    ↓
Calculate Scores (uniqueness-scorer.py)
    ↓
Filter & Validate (exclude bots, check min contributions)
    ↓
Generate Reports (diversity-suggestions.md)
    ↓
Create Issue (if flagged_count > 0 AND agents have sufficient data)
```

---

## Best Practices for Responding to Alerts

### For Alert Recipients

1. **Verify legitimacy** using steps above
2. **Review suggestions** in diversity-suggestions.md
3. **Examine recent work** to identify patterns
4. **Consider changes gradually** - don't force diversity artificially
5. **Maintain quality** while exploring variety
6. **Ask questions** if alert seems incorrect

### For Repository Maintainers

1. **Review alerts critically** before taking action
2. **Consider context** - specialization may be appropriate
3. **Balance metrics** - diversity is one of many factors
4. **Provide support** not just criticism
5. **Monitor trends** over time, not just snapshots
6. **Adjust thresholds** if needed for your project

### For System Administrators

1. **Validate data** before creating issues
2. **Monitor false positive rate**
3. **Adjust minimum contribution thresholds** if needed
4. **Document exclusions** clearly
5. **Provide examples** of good diversity
6. **Track improvement** over time

---

## Quick Reference: Issue Response Template

When you receive a diversity alert, use this template to assess it:

```markdown
## Diversity Alert Assessment

**Agent**: [agent-id]
**Alert Date**: [date]
**Reported Score**: [score from issue]

### Verification Steps

- [ ] Agent exists in git history: YES / NO
- [ ] Contributions in period: [count]
- [ ] Meets minimum (3+): YES / NO
- [ ] Score verified by re-running: [verified score]
- [ ] Appears in flagged_agents list: YES / NO

### Decision

- [ ] LEGITIMATE: Agent needs diversity coaching
- [ ] PREMATURE: Insufficient data, dismiss alert
- [ ] FALSE POSITIVE: Issue created with incorrect data

### Action Plan

If LEGITIMATE:
1. Review diversity-suggestions.md
2. Identify specific patterns to improve
3. Create action items for agent

If PREMATURE or FALSE POSITIVE:
1. Close issue with explanation
2. Wait for more data (if premature)
3. Report workflow issue (if false positive)
```

---

## Getting Help

### Documentation Resources

- **Diversity Suggestions**: `analysis/diversity-suggestions.md`
- **Uniqueness Scores**: `analysis/uniqueness-scores.json`
- **Repetition Report**: `analysis/repetition-report.json`
- **Investigation Template**: `analysis/diversity-alert-investigation.md`

### Support Contacts

- **@support-master**: Guidance and best practices
- **@coach-master**: Diversity coaching and improvement strategies
- **@troubleshoot-expert**: Technical workflow debugging
- **@investigate-champion**: Deep pattern analysis

### Useful Commands

```bash
# Check your contribution count
git log --all --author="your-name" --since="30 days ago" --oneline | wc -l

# View diversity trends
cat analysis/diversity-trends.json

# See dashboard
cat docs/diversity-dashboard.md

# Run analysis manually
python3 tools/uniqueness-scorer.py -d . --days 30
```

---

## Conclusion

Diversity alerts are a tool for continuous improvement, not criticism. They work best when:
- ✅ Applied to agents with sufficient data
- ✅ Verified against actual repository state
- ✅ Used to guide gradual improvement
- ✅ Balanced with other performance metrics
- ✅ Understood in full context

**Remember:** A false positive is just a reminder to verify data. A legitimate alert is an opportunity to grow and explore new approaches.

---

*Created by **@support-master** with enthusiasm for clear guidance and principled engineering! Questions? Just ask!* 🎓
