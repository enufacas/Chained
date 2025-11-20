# Product Owner Agent

## Overview

The **@product-owner** agent is a specialized agent in the Chained autonomous system that transforms vague, general issues into structured, actionable requirements.

Inspired by Marty Cagan's product management principles, this agent deeply understands the Chained system architecture and can clarify ambiguous requests into well-structured user stories.

## How It Works

**⚠️ IMPORTANT: Two-Phase Process**

The product owner operates in a two-phase workflow:

### Phase 1: Product Owner Enhancement (Current Agent)

1. **Issue Created** - User creates an issue with vague or general requirements
2. **Agent Matching** - `match-issue-to-agent.py` analyzes the issue content
3. **Pattern Detection** - If vague language is detected, @product-owner is selected
4. **Assignment** - Copilot assigned with @product-owner directive
5. **Enhancement** - Product owner transforms the issue into structured format
6. **Handoff Actions** - **CRITICAL**: PO must remove labels and unassign to trigger Phase 2

### Phase 2: Specialist Implementation (Automatic)

7. **Re-assignment Trigger** - Workflow detects issue without `copilot-assigned` label
8. **Re-matching** - Agent matcher analyzes ENHANCED content (now much clearer)
9. **Specialist Selection** - Appropriate specialist matched (e.g., @accelerate-master)
10. **Implementation** - Specialist agent implements the actual solution

### Critical Gap Warning

**Without proper handoff, work stops at Phase 1.** The product owner agent MUST:
- Remove `copilot-assigned` and `agent:product-owner` labels
- Unassign Copilot from the issue
- Add completion comment with specialist recommendation
- Keep issue OPEN

See [Workflow Analysis](PRODUCT_OWNER_WORKFLOW_ANALYSIS.md) for complete technical details and troubleshooting.

## When Product Owner is Selected

The agent matching system selects @product-owner when issues contain:

### Keywords
- Vague language: "improve", "enhance", "better", "fix", "update"
- Unclear direction: "should", "could", "maybe", "somehow"
- General requests: "make it work", "optimize", "clean up"
- Missing specifics: short descriptions, no criteria, ambiguous terms

### Patterns
- Questions without context: "How can we...?", "What about...?"
- Statements lacking detail: "This is bad", "Needs work"
- Requests without acceptance criteria
- Very short issue bodies (< 100 characters)

## Enhancement Template

When assigned, @product-owner transforms:

**Before:**
```
Title: Performance is bad
Body: The site is slow. Make it faster.
```

**After:**
```markdown
# Performance is bad - Enhanced by @product-owner

## 📋 Original Request
<details>
<summary>View original</summary>
The site is slow. Make it faster.
</details>

## 🎯 User Story
As a user,
I want pages to load quickly,
So that I can work efficiently without delays.

## 📖 Context & Background
- Current issue: Users experiencing slow page loads
- Impact: Reduced productivity, potential user frustration
- System involved: Web application frontend and backend

## ✅ Acceptance Criteria
- [ ] Identify top 3 performance bottlenecks
- [ ] Reduce page load time by at least 30%
- [ ] API response time under 200ms (p95)
- [ ] Performance metrics tracked and documented

## 🔧 Technical Considerations
- Profile application to identify bottlenecks
- Consider: Database queries, API calls, rendering performance
- May need: Caching, query optimization, code splitting
- Must maintain: Current functionality and data integrity

## 🧪 Testing Requirements
- [ ] Performance benchmarks established
- [ ] Load testing conducted
- [ ] Metrics validated across different scenarios

---
*Enhanced by @product-owner - Ready for specialist assignment*
```

**Note:** The product-owner does NOT recommend a specific agent. After enhancement, the `match-issue-to-agent.py` system automatically re-analyzes the structured content and selects the best specialist (e.g., @accelerate-master for performance).

## Agent Definition

The full agent definition is located at `.github/agents/product-owner.md` and includes:

- **Personality**: Product-focused, user-centric, clarity-driven (inspired by Marty Cagan)
- **Specialization**: Requirements clarification, story writing, acceptance criteria
- **Deep Knowledge**: Chained system architecture, agent capabilities, autonomous workflows
- **Approach**: Preserve original, add structure, enable re-assignment for specialist matching

## Configuration

### Matching Patterns

Defined in `tools/match-issue-to-agent.py`:

```python
'product-owner': {
    'keywords': [
        'vague', 'unclear', 'general', 'improve', 'enhance', 'better',
        'fix', 'update', 'should', 'could', 'maybe', 'somehow',
        'optimize', 'clean', 'refactor', 'organize', 'clarify',
        'requirements', 'specification', 'detail', 'unclear',
        'ambiguous', 'confusing', 'explain', 'understand'
    ],
    'patterns': [
        r'\bimprove\b', r'\benhance\b', r'\bbetter\b', r'\bshould\b',
        r'\bcould\b', r'\bmaybe\b', r'\bsomehow\b', r'\boptimi[sz]e\b',
        r'\bclean', r'\brefactor\b', r'\borganize\b', r'\bclarify\b',
        r'\bvague\b', r'\bunclear\b', r'\bambiguous\b', r'\bgeneral\b',
        r'\bconfus', r'\bexplain\b', r'\bunderstand\b',
        r'\bhow\s+(?:can|do|does|should)', r'\bwhat\s+(?:if|about)',
        r'\bneed\s+to\b', r'\bwant\s+to\b', r'\bmake\s+it\b'
    ]
}
```

### Agent Scoring

When vague language is detected:
- **Keywords**: 1 point each
- **Patterns**: 2 points each
- **High confidence**: score ≥ 5
- **Medium confidence**: score ≥ 3

## Use Cases

### Ideal For
- ✅ General improvement requests: "Make the dashboard better"
- ✅ Vague bug reports: "Something is broken"
- ✅ Optimization requests: "Improve performance"
- ✅ Unclear feature requests: "Add better error handling"
- ✅ Questions without context: "How can we make this faster?"

### Not Needed For
- ❌ Well-structured issues with clear acceptance criteria
- ❌ Issues with specific technical details
- ❌ Bug reports with reproduction steps
- ❌ Feature requests with defined requirements

## Integration with Agent System

The product owner agent integrates seamlessly with the existing agent assignment workflow:

### Normal Flow (Specific Issue)
```
Issue: "Add POST /api/v1/users endpoint with JWT auth"
  ↓
Agent Matching: High specificity detected
  ↓
Selected: @APIs-architect
  ↓
Implementation: Direct work on specific requirement
```

### Product Owner Flow (Vague Issue)
```
Issue: "Improve the API"
  ↓
Agent Matching: Vague language detected
  ↓
Selected: @product-owner
  ↓
Enhancement: Transforms into structured requirement
  ↓
Re-assignment: Labels removed, issue ready for re-matching
  ↓
Agent Matching (2nd pass): Analyzes enhanced content
  ↓
Selected: Appropriate specialist (e.g., @APIs-architect)
  ↓
Implementation: Specialist works on clarified requirement
```

## Testing

To test the product owner agent matching:

```bash
cd /home/runner/work/Chained/Chained
python3 tools/match-issue-to-agent.py "Improve performance" "The system is slow"
```

Expected output:
```json
{
  "agent": "product-owner",
  "score": 12,
  "confidence": "high"
}
```

## Maintenance

### Adding Keywords
To detect additional vague patterns, edit `tools/match-issue-to-agent.py`:

```python
'product-owner': {
    'keywords': [
        # Add new keywords here
        'needs work', 'could be better', 'not working well'
    ],
    # ...
}
```

### Adjusting Agent Definition
To modify the enhancement template or agent personality, edit `.github/agents/product-owner.md`.

### Disabling
To disable the product owner agent:

1. Comment out patterns in `tools/match-issue-to-agent.py`
2. Or remove the agent definition file

## Benefits

1. **Better Agent Matching** - Clear requirements lead to better specialist selection
2. **Faster Resolution** - Less back-and-forth for clarification
3. **Consistent Format** - All issues follow standard structure
4. **Knowledge Capture** - Original intent preserved while adding structure
5. **Reduced Ambiguity** - Vague requests transformed into actionable stories

## Comparison with Other Options

This implementation uses **Option 2: Specialized Agent Only**

- ✅ Simple: Product owner is just another specialized agent
- ✅ Efficient: Only triggered when patterns detect vagueness
- ✅ Non-intrusive: No pre-processing, standard agent flow
- ✅ Selective: Well-structured issues bypass enhancement
- ✅ Flexible: Can be assigned manually if needed

**Alternative (Not Implemented):**
- Option 1: Pre-processing workflow that runs on ALL issues
- Option 3: Hybrid approach with smart routing

The specialized agent approach was chosen for its simplicity and efficiency.

## Examples

See the agent definition file (`.github/agents/product-owner.md`) for comprehensive examples of transformations across different issue types:
- Performance issues
- Bug reports
- Feature requests
- Architecture questions
- Documentation needs

---

*🤖 Product Owner Agent - Transforming vague issues into actionable requirements*
