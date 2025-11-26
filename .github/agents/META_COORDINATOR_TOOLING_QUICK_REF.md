# Meta-Coordinator Tooling Quick Reference

## CRITICAL: Use These Scripts - They Are Deterministic

### Auto-Merge: tools/auto-merge-pr.sh
**Purpose:** Check eligibility AND execute merge in one operation

**Usage:**
```bash
export GH_TOKEN="${COPILOT_PAT}"

# Auto-merge a single PR
./tools/auto-merge-pr.sh 123

# Process multiple PRs
for pr_num in $(gh pr list --json number --jq '.[].number'); do
  ./tools/auto-merge-pr.sh "$pr_num" || true
done
```

**Exit Codes:**
- `0` = Merged successfully
- `1` = Not eligible (see output)
- `2` = Eligible but merge failed
- `3` = Usage error

**Key Features:**
- ✅ Checks WIP markers BEFORE marking draft ready
- ✅ Waits 3 seconds after marking ready for status calculation
- ✅ Handles UNKNOWN mergeable status automatically
- ✅ Posts success comment after merge
- ✅ Clear output explaining decisions

### Check Eligibility Only: tools/check-pr-merge-eligibility.sh
**Purpose:** Check if PR is eligible (without merging)

**Usage:**
```bash
if ./tools/check-pr-merge-eligibility.sh 123; then
  echo "PR is eligible for merge"
fi
```

**When to use:** When you need to check eligibility but not merge (e.g., reporting, filtering)

### Cleanup Stale PRs: tools/cleanup-stale-prs.sh
**Purpose:** Proactively close stale PRs

**Usage:**
```bash
# Real cleanup
./tools/cleanup-stale-prs.sh

# Dry run (no changes)
./tools/cleanup-stale-prs.sh --dry-run
```

**Output:** Creates `/tmp/cleanup_summary.json` with counts

## Common Patterns

### Pattern 1: Batch Auto-Merge
```bash
# Get potentially eligible PRs
candidate_prs=$(gh pr list --state open --json number,mergeable,isDraft \
  --jq '.[] | select(.mergeable == "MERGEABLE" or (.mergeable == "UNKNOWN" and .isDraft == true)) | .number')

# Try to merge each
merged=0
for pr in $candidate_prs; do
  if ./tools/auto-merge-pr.sh "$pr"; then
    merged=$((merged + 1))
    echo "✅ Merged PR #$pr"
  fi
done

echo "Merged ${merged} PRs"
```

### Pattern 2: Filter Eligible PRs
```bash
# Get list of eligible PRs without merging
eligible_prs=""
for pr in $(gh pr list --json number --jq '.[].number'); do
  if ./tools/check-pr-merge-eligibility.sh "$pr" 2>/dev/null; then
    eligible_prs="${eligible_prs} ${pr}"
  fi
done

echo "Eligible PRs: ${eligible_prs}"
```

### Pattern 3: Cleanup Then Merge
```bash
# Step 1: Clean up stale PRs
./tools/cleanup-stale-prs.sh

# Step 2: Auto-merge remaining eligible PRs
for pr in $(gh pr list --json number --jq '.[].number'); do
  ./tools/auto-merge-pr.sh "$pr" || true
done
```

## Decision Logic Comparison

| Criteria | check-pr-merge-eligibility.sh | auto-merge-pr.sh |
|----------|------------------------------|------------------|
| Open state | ✅ | ✅ |
| No WIP markers | ✅ Checks after marking ready | ✅ Checks BEFORE marking ready |
| Trusted author | ✅ | ✅ |
| Draft handling | ✅ Marks ready | ✅ Marks ready (safer) |
| Mergeable status | ✅ | ✅ |
| CI checks | ✅ | ✅ |
| **Merge execution** | ❌ No | ✅ Yes |
| **Success comment** | ❌ No | ✅ Yes |

## Troubleshooting

### "Mergeable status is UNKNOWN"
**Cause:** GitHub hasn't finished calculating merge status

**Solution:** 
1. Wait 5-10 seconds
2. Try again
3. Script automatically marks draft ready and waits, but may need more time

### "Has WIP marker in title"
**Cause:** PR title contains WIP, [WIP], [DNM], or similar

**Solution:**
1. Remove WIP marker from title
2. Run script again
3. PR will become eligible

### "Not from trusted author"
**Cause:** PR author is not repository owner or copilot/github-actions

**Solution:** This is a security requirement. Only trusted sources can auto-merge.

### "CI checks failed"
**Cause:** Some status checks didn't pass

**Solution:**
1. Check PR checks tab
2. Fix failing checks
3. Wait for checks to complete
4. Run script again

## Integration with Memory System

After merging PRs, record in memory:
```bash
# Get PR details
pr_data=$(gh pr view "$pr_num" --json createdAt --jq '.')
created_at=$(echo "$pr_data" | jq -r '.createdAt')

# Record in memory
python3 << 'PYPYTHON'
import sys
sys.path.insert(0, 'tools')
from meta_coordinator_memory import MetaCoordinatorMemory
memory = MetaCoordinatorMemory()
memory.record_pr_closed(pr_num, created_at, is_stale=False)
memory.save()
PYPYTHON
```

## See Also

- `tools/AUTO_MERGE_PR_README.md` - Detailed auto-merge documentation
- `.github/agents/meta-coordinator-system.md` - Full agent definition
- `.github/workflows/meta-coordinator.yml` - Workflow integration
