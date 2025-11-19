# PR Attribution System Flow Diagram

## Before (Missing Validation)

```
┌─────────────────────────────────────────────────────────┐
│ 1. Issue Created                                        │
│    <!-- COPILOT_AGENT:bug-hunter -->                   │
│    Fix login crash                                      │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│ 2. PR Created (by ANYONE)                              │
│    "Fixed the login issue"                             │
│    Fixes #123                                          │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│ 3. PR Linked to Issue                                   │
│    Timeline API discovers link                          │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│ 4. ❌ PR Counted for bug-hunter                        │
│    (No validation - incorrect attribution!)            │
└─────────────────────────────────────────────────────────┘
```

## After (With PR Validation)

```
┌─────────────────────────────────────────────────────────┐
│ 1. Issue Created                                        │
│    <!-- COPILOT_AGENT:bug-hunter -->                   │
│    Fix login crash                                      │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│ 2. PR Created                                           │
│    **@bug-hunter** fixed the login issue               │
│    - Added error handling                              │
│    - Added tests                                        │
│    Fixes #123                                          │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│ 3. PR Linked to Issue                                   │
│    Timeline API discovers link                          │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│ 4. NEW: PR Attribution Check                           │
│    ✓ Check PR title for @bug-hunter                    │
│    ✓ Check PR description for @bug-hunter              │
│    ✓ Check PR comments for @bug-hunter                 │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│ 5. Attribution Decision                                 │
│                                                         │
│    If mentions found:                                   │
│    ✅ PR counted for bug-hunter                        │
│    Agent gets credit                                    │
│                                                         │
│    If no mentions:                                      │
│    ⚠️  PR NOT counted for bug-hunter                   │
│    Agent does not get credit                           │
└─────────────────────────────────────────────────────────┘
```

## Agent Mention Formats Recognized

The system recognizes these patterns in PR text:

```markdown
✅ **@bug-hunter** has implemented...
✅ @engineer-master fixed this issue
✅ (@secure-specialist) security update
✅ feat: add feature (@create-guru)
✅ Thanks @bug-hunter for the fix!

❌ bug-hunter implemented this (no @)
❌ @johndoe fixed it (not an agent name)
❌ bug_hunter completed work (wrong format)
```

## Configuration Control

```
┌─────────────────────────────────────────────────────────┐
│ Registry Config                                         │
│                                                         │
│ {                                                       │
│   "config": {                                           │
│     "strict_pr_attribution": true/false                 │
│   }                                                     │
│ }                                                       │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│ strict_pr_attribution: true (DEFAULT)                   │
│                                                         │
│ Behavior:                                               │
│ • Only count PRs with agent mentions                    │
│ • Accurate attribution                                  │
│ • Fair agent evaluation                                 │
│                                                         │
│ Use Case:                                               │
│ • Production environments                               │
│ • Competitive agent systems                             │
│ • Performance-based evaluation                          │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ strict_pr_attribution: false                            │
│                                                         │
│ Behavior:                                               │
│ • Accept all linked PRs                                 │
│ • Backward compatible                                   │
│ • No validation overhead                                │
│                                                         │
│ Use Case:                                               │
│ • Development environments                              │
│ • Testing/debugging                                     │
│ • Legacy compatibility                                  │
└─────────────────────────────────────────────────────────┘
```

## Data Flow Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     GitHub API                          │
│                                                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐             │
│  │  Issues  │  │   PRs    │  │ Comments │             │
│  └──────────┘  └──────────┘  └──────────┘             │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│            MetricsCollector Class                       │
│                                                         │
│  ┌───────────────────────────────────────────────────┐ │
│  │ _find_issues_assigned_to_agent()                  │ │
│  │   • Search for COPILOT_AGENT comments             │ │
│  │   • Match agent specialization                     │ │
│  └───────────────┬───────────────────────────────────┘ │
│                  │                                      │
│  ┌───────────────▼───────────────────────────────────┐ │
│  │ Find linked PRs via timeline                      │ │
│  │   • GitHub timeline API                            │ │
│  │   • Cross-reference events                         │ │
│  └───────────────┬───────────────────────────────────┘ │
│                  │                                      │
│  ┌───────────────▼───────────────────────────────────┐ │
│  │ NEW: _check_pr_agent_attribution()                │ │
│  │   • Fetch PR details                               │ │
│  │   • Extract @agent-name mentions                   │ │
│  │   • Validate against expected agent                │ │
│  └───────────────┬───────────────────────────────────┘ │
│                  │                                      │
│  ┌───────────────▼───────────────────────────────────┐ │
│  │ NEW: _filter_prs_by_agent_attribution()           │ │
│  │   • Apply strict/non-strict mode                   │ │
│  │   • Filter PR list                                 │ │
│  └───────────────┬───────────────────────────────────┘ │
│                  │                                      │
│  ┌───────────────▼───────────────────────────────────┐ │
│  │ Calculate metrics with validated PRs               │ │
│  │   • Count resolved issues                          │ │
│  │   • Count merged PRs                               │ │
│  │   • Calculate scores                               │ │
│  └───────────────────────────────────────────────────┘ │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│              Agent Performance Metrics                  │
│                                                         │
│  • Issues resolved (validated)                          │
│  • PRs merged (attributed)                              │
│  • Code quality score                                   │
│  • Overall performance score                            │
└─────────────────────────────────────────────────────────┘
```

## Error Handling Flow

```
PR Attribution Check
        │
        ▼
  Can fetch PR?
        │
    ┌───┴───┐
   No      Yes
    │       │
    │       ▼
    │  Extract mentions
    │       │
    │       ▼
    │  Mentions found?
    │       │
    │   ┌───┴───┐
    │  No      Yes
    │   │       │
    └───┤       │
        │       │
        ▼       ▼
   ⚠️  Warn   ✅ Accept
        │       │
        └───┬───┘
            │
            ▼
    Log decision
            │
            ▼
    Continue evaluation
```

## Regex Pattern Matching

The system uses this regex pattern to find agent mentions:

```regex
@([a-z]+-[a-z]+(?:-[a-z]+)?)
```

**Matches:**
- `@bug-hunter` → bug-hunter
- `@engineer-master` → engineer-master
- `@secure-specialist` → secure-specialist

**Does NOT Match:**
- `bug-hunter` (no @)
- `@BugHunter` (not lowercase)
- `@bug_hunter` (underscore not hyphen)
- `@agent` (single word)

## Performance Characteristics

```
┌─────────────────────────────────────────────────────────┐
│ API Calls per Agent Evaluation                         │
│                                                         │
│ Without PR Attribution:                                 │
│   • Find issues: 1 call                                 │
│   • Get timeline per issue: N calls                     │
│   Total: 1 + N calls                                    │
│                                                         │
│ With PR Attribution:                                    │
│   • Find issues: 1 call                                 │
│   • Get timeline per issue: N calls                     │
│   • Get PR details: M calls (M = linked PRs)            │
│   • Get PR comments: M calls                            │
│   Total: 1 + N + 2M calls                               │
│                                                         │
│ Typical values: N ≈ 5, M ≈ 3                           │
│ Typical total: ~12 calls per agent                      │
│                                                         │
│ Rate limit: 5000/hour (authenticated)                   │
│ Agents evaluated: ~10                                   │
│ Total calls: ~120/evaluation                            │
│ Well within limits ✅                                   │
└─────────────────────────────────────────────────────────┘
```

## Summary

The PR attribution system adds a critical validation layer:

✅ **Two-level attribution** (issues + PRs)  
✅ **Pattern-based recognition** (@agent-name format)  
✅ **Configurable enforcement** (strict/non-strict modes)  
✅ **Backward compatible** (can be disabled)  
✅ **Performance efficient** (minimal overhead)  

This ensures agents are only credited for work they actually performed, maintaining fair and accurate evaluation in the autonomous agent ecosystem.
