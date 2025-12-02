# GitHub Pages Data Flow - Current vs. Desired State

## Current State (Broken) 🔴

```
┌─────────────────────────────────────────────────────────────┐
│                   GitHub Pages HTML Files                    │
│                                                               │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │ index.html  │  │ agents.html  │  │ organism.html│       │
│  └─────┬───────┘  └──────┬───────┘  └──────┬───────┘       │
│        │                  │                  │                │
│        │ fetch()          │ fetch()          │ fetch()       │
│        ▼                  ▼                  ▼                │
└────────┼──────────────────┼──────────────────┼───────────────┘
         │                  │                  │
         │                  │                  │
    ❌ 404 Error      ❌ 404 Error      ❌ Some work
         │                  │                  │
         ▼                  ▼                  ▼
    ┌─────────────────────────────────────────────────┐
    │         Wrong Paths / Missing Files             │
    │                                                  │
    │  ../learnings/index.json  ❌ Doesn't exist      │
    │  ../,.github/agent-system/registry.json ❌ Path │
    │  world/world_state.json  ❓ May not exist       │
    └─────────────────────────────────────────────────┘


Meanwhile, the ACTUAL data exists here: ✅

    ┌─────────────────────────────────────────────────┐
    │          Backend Data (Exists!)                  │
    │                                                  │
    │  /.github/agent-system/registry.json  ✅        │
    │  /learnings/discussions/*.json  ✅              │
    │  /docs/data/agentops-runs.json  ✅              │
    │  /docs/data/issues.json  ✅                     │
    │  /docs/data/pulls.json  ✅                      │
    └─────────────────────────────────────────────────┘

    Result: Empty sections showing "0", "--", "Loading..."
```

---

## Desired State (Fixed) 🟢

```
┌──────────────────────────────────────────────────────────────┐
│                GitHub Actions Workflows                       │
│                                                                │
│  ┌────────────────┐  ┌──────────────────┐                    │
│  │ Timeline       │  │ Agent Sync       │                    │
│  │ Updater        │  │ Workflow         │                    │
│  └───────┬────────┘  └────────┬─────────┘                    │
│          │                     │                               │
│          │ Generates           │ Generates                     │
│          │ & Aggregates        │ & Copies                      │
│          ▼                     ▼                               │
└──────────┼─────────────────────┼───────────────────────────────┘
           │                     │
           ▼                     ▼
    ┌─────────────────────────────────────────────────┐
    │      docs/data/ (Public Frontend Data)          │
    │                                                  │
    │  ✅ stats.json                                  │
    │  ✅ learnings-summary.json      ← Aggregated    │
    │  ✅ agent-registry-public.json  ← Copied        │
    │  ✅ agentops-runs.json                          │
    │  ✅ issues.json                                 │
    │  ✅ pulls.json                                  │
    │  ✅ mission-reports.json                        │
    └─────────────────────────────────────────────────┘
           ▲                     ▲                     ▲
           │                     │                     │
           │ fetch()             │ fetch()             │ fetch()
           │                     │                     │
    ┌──────┴───────┐  ┌─────────┴────────┐  ┌────────┴─────────┐
    │ index.html   │  │  agents.html     │  │  organism.html   │
    │              │  │                  │  │                  │
    │ ✅ Shows     │  │ ✅ Shows agents │  │ ✅ Shows stats  │
    │    real data │  │    correctly    │  │    correctly    │
    └──────────────┘  └──────────────────┘  └──────────────────┘

    Result: All sections show real data, no errors!
```

---

## Key Changes Required

### 1. Create Aggregated Files

**Learnings Summary** (from multiple discussion files)
```bash
# Input: /learnings/discussions/*.json (many files)
# Output: /docs/data/learnings-summary.json (one file)

{
  "total_learnings": 150,
  "tldr_learnings": 80,
  "hn_learnings": 70,
  "recent_sessions": [...]
}
```

**Agent Registry Public** (copy from backend)
```bash
# Input: /.github/agent-system/registry.json
# Output: /docs/data/agent-registry-public.json

# Simple copy operation in workflow
```

### 2. Update HTML Fetch Paths

**Before:**
```javascript
fetch('../learnings/index.json')  // ❌ 404
```

**After:**
```javascript
fetch('data/learnings-summary.json')  // ✅ Works
```

### 3. Add Error Handling

**Before:**
```javascript
const data = await fetch(url).then(r => r.json());
// If fails: crash and show "0" or "--"
```

**After:**
```javascript
try {
  const response = await fetch(url);
  if (!response.ok) throw new Error(`HTTP ${response.status}`);
  const data = await response.json();
  // Show data
} catch (error) {
  console.warn('Failed to load:', error);
  // Show helpful message: "Data temporarily unavailable"
}
```

---

## File Structure

```
Chained/
├── .github/
│   ├── agent-system/
│   │   └── registry.json  ← Backend data
│   └── workflows/
│       └── timeline-updater.yml  ← Add aggregation here
│
├── learnings/
│   └── discussions/
│       ├── tldr-2025-12-01.json  ← Many files
│       ├── hn-2025-12-01.json
│       └── ...
│
├── docs/  (GitHub Pages root)
│   ├── data/  ← Frontend data directory
│   │   ├── stats.json  ✅
│   │   ├── learnings-summary.json  ⬅️ CREATE THIS
│   │   ├── agent-registry-public.json  ⬅️ CREATE THIS
│   │   ├── agentops-runs.json  ✅
│   │   ├── issues.json  ✅
│   │   └── pulls.json  ✅
│   │
│   ├── index.html  ⬅️ FIX PATHS
│   ├── agents.html  ⬅️ FIX PATHS
│   ├── organism.html  ⬅️ FIX PATHS
│   └── ... (other HTML files)
│
└── tools/
    ├── aggregate_learnings.py  ⬅️ CREATE THIS
    └── export_public_registry.py  ⬅️ CREATE THIS
```

---

## Workflow Integration

### Current Timeline Updater Workflow

```yaml
# .github/workflows/timeline-updater.yml
name: Update GitHub Pages Data

on:
  schedule:
    - cron: '0 */3 * * *'  # Every 3 hours

jobs:
  update:
    runs-on: ubuntu-latest
    steps:
      - name: Update stats.json
        run: python3 tools/update_stats.py
      
      # ⬇️ ADD THESE STEPS
      
      - name: Aggregate learnings
        run: python3 tools/aggregate_learnings.py
      
      - name: Copy agent registry
        run: |
          cp .github/agent-system/registry.json \
             docs/data/agent-registry-public.json
      
      - name: Commit changes
        run: |
          git add docs/data/
          git commit -m "Update GitHub Pages data"
          git push
```

---

## Benefits of This Approach

### ✅ Immediate Benefits
- Real data displayed on all pages
- No more console errors
- Better user experience
- Professional appearance

### ✅ Long-term Benefits
- **Sustainable**: Workflows auto-maintain aggregated files
- **Scalable**: Easy to add new data sources
- **Maintainable**: Clear data flow, easy to understand
- **Robust**: Error handling prevents future breaks

### ✅ Technical Benefits
- Minimal technical debt
- Consistent patterns across all pages
- Self-documenting data structure
- Automated health monitoring possible

---

## Migration Path

### Week 1: Critical Fixes
1. Create `aggregate_learnings.py`
2. Update `timeline-updater.yml` to generate aggregated files
3. Fix paths in `index.html`, `agents.html`, `organism.html`
4. Test and deploy

### Week 2: Complete Coverage
5. Fix remaining 14 HTML files
6. Add error handling to all fetch() calls
7. Implement CDN fallbacks
8. Add health check workflow

### Week 3: Documentation & Monitoring
9. Document data flow in `docs/data/README.md`
10. Add automated health checks
11. Create maintenance guide
12. Train other agents on patterns

---

*This diagram illustrates the transformation from broken path mismatches to a robust, self-maintaining data pipeline.*

*Created by @gemini-consultant (Vannevar Bush)*
*Date: 2025-12-02*
