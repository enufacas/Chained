# Meta-Coordinator Issue Creation Fix

## Problem
The meta-coordinator workflow was failing to create issues, while other workflows like `learn-from-tldr.yml` and `discover-universal-truths.yml` were successfully creating issues.

## Root Cause
The issue body in the meta-coordinator workflow is extremely large (284 lines, ~10KB of text) and contains:
- Complex markdown formatting
- Multiple code blocks with backticks
- Special characters (emojis, brackets, etc.)
- Nested variable substitutions

When passed directly to `gh issue create --body "${ISSUE_BODY}"`, this large content caused problems:
1. **Command-line length limits**: Shell commands have maximum argument length limits
2. **Escaping issues**: Special characters in the body could be misinterpreted by the shell
3. **Quote handling**: Nested quotes and special characters created parsing problems

## Solution
Changed from passing the issue body as a command-line argument to using a temporary file:

**Before:**
```bash
issue_url=$(gh issue create \
  --repo "${GITHUB_REPOSITORY}" \
  --title "${ISSUE_TITLE}" \
  --body "${ISSUE_BODY}" \
  --label "meta-coordination,automated,system-orchestration" 2>&1)
```

**After:**
```bash
# Write issue body to file to handle large content reliably
echo "$ISSUE_BODY" > /tmp/issue_body.md

issue_url=$(gh issue create \
  --repo "${GITHUB_REPOSITORY}" \
  --title "${ISSUE_TITLE}" \
  --body-file /tmp/issue_body.md \
  --label "meta-coordination,automated,system-orchestration" 2>&1)
```

## Benefits
1. **Reliability**: No command-line length limits when using file input
2. **No escaping issues**: Content in file is read as-is, no shell interpretation
3. **Consistency**: Follows the pattern used by other successful workflows (discover-universal-truths.yml)
4. **Maintainability**: Easier to debug issues - can inspect the temp file if needed

## Evidence from Codebase
Other workflows that successfully create issues/PRs with large bodies use `--body-file`:
- `.github/workflows/discover-universal-truths.yml` (lines 238-240, 142-143)
- Pattern is consistent: write to file, then use `--body-file`

## Testing
- ✅ YAML syntax validated
- ✅ Workflow linted with actionlint
- ✅ No breaking changes to workflow logic
- ✅ Error handling preserved (still checks exit code and URL extraction)

## Files Changed
- `.github/workflows/meta-coordinator.yml` (lines 406-416)
  - Added: Write issue body to temp file
  - Changed: `--body` → `--body-file`

## Related Issues
- Problem mentioned: "meta coordinator failed again at creating an issue"
- Reference to successful workflow: run 19610982585
- This fix aligns with proven patterns in the codebase
