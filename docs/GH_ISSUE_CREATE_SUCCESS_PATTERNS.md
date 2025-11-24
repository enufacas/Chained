# GitHub Issue Create Success Patterns

## Overview

This document analyzes successful implementations of `gh issue create` across the repository to identify best practices and common patterns that lead to reliable issue creation.

## Successful Implementations

### 1. Meta-Coordinator Workflow (✅ Working)

**File:** `.github/workflows/meta-coordinator.yml`  
**Last Fixed:** Commit 2bc16099 (2025-11-23)

#### Key Success Factors

1. **Body File Approach**
   ```bash
   # Write body to temporary file
   echo "$ISSUE_BODY" > /tmp/issue_body.md
   
   # Use --body-file instead of --body
   issue_url=$(gh issue create \
     --repo "${GITHUB_REPOSITORY}" \
     --title "${ISSUE_TITLE}" \
     --body-file /tmp/issue_body.md \
     --label "meta-coordination,automated,system-orchestration" 2>&1)
   ```

2. **Error Handling**
   ```bash
   if [ $? -ne 0 ] || [ -z "${issue_url}" ]; then
     echo "❌ Failed to create coordination issue"
     echo "Error output: ${issue_url}"
     exit 1
   fi
   ```

3. **Output Parsing**
   ```bash
   # Robust extraction of issue number
   issue_number=$(echo "${issue_url}" | grep -oP '/issues/\K\d+' | head -1)
   
   if [ -z "${issue_number}" ]; then
     echo "❌ Could not extract issue number from: ${issue_url}"
     exit 1
   fi
   ```

4. **Separate Assignment**
   - Does NOT use `--assignee` flag
   - Uses separate GraphQL API call for assignment (more reliable)

---

### 2. Autonomous Pipeline Workflow (✅ Working)

**File:** `.github/workflows/autonomous-pipeline.yml`

#### Key Success Factors

1. **Inline Body for PRs (Not Issues)**
   ```bash
   # Note: This is for PR creation, not issue creation
   PR_URL=$(gh pr create \
     --title "🧠 Learning Pipeline - $(date +%Y-%m-%d)" \
     --body "## 🧠 Autonomous Learning Pipeline
   
   **Total Learnings:** ${{ steps.analyze.outputs.total_learnings }}
   [...]
   " \
     --label "automated,learning,pipeline,auto-merge,copilot" \
     --base main \
     --head "$BRANCH_NAME")
   ```

2. **Clean Output Extraction**
   ```bash
   PR_NUMBER=$(echo "$PR_URL" | grep -oE '[0-9]+$')
   ```

---

### 3. Create Mission Issues Tool (✅ Working)

**File:** `tools/create_mission_issues.py`

#### Key Success Factors

1. **Label Pre-Creation**
   ```python
   # Ensure all labels exist BEFORE creating issues
   for label in sorted(all_labels):
       ensure_label_exists(label, color, description)
   ```

2. **Subprocess Error Handling**
   ```python
   try:
       result = subprocess.run(
           ['gh', 'issue', 'create', 
            '--title', title,
            '--body', issue_body,
            '--label', labels_str],
           capture_output=True,
           text=True,
           check=True
       )
       issue_url = result.stdout.strip()
   except subprocess.CalledProcessError as e:
       print(f"  ⚠️  Failed to create issue: {e.stderr}")
   ```

3. **Issue Number Extraction**
   ```python
   # Extract from URL: https://github.com/owner/repo/issues/123
   issue_number = issue_url.split('/')[-1] if issue_url else None
   ```

---

## Common Success Patterns

### Pattern 1: Use --body-file for Large Content

**When to use:**
- Issue body > 1000 characters
- Body contains special characters, quotes, or shell metacharacters
- Multi-line content with variable substitution

**Implementation:**
```bash
# 1. Write content to temp file
cat > /tmp/issue_body.md <<'EOF'
Your issue content here
Can have multiple lines
Can have $variables (if you want literal $, use <<'EOF')
EOF

# 2. Substitute variables if needed
sed -i "s/\${VAR}/${VAR}/g" /tmp/issue_body.md

# 3. Create issue
gh issue create \
  --title "Title" \
  --body-file /tmp/issue_body.md \
  --label "labels"
```

### Pattern 2: Inline --body for Simple Content

**When to use:**
- Issue body < 500 characters
- Simple text without complex quoting
- No variable substitution needed

**Implementation:**
```bash
gh issue create \
  --title "Simple issue" \
  --body "Short description here" \
  --label "bug"
```

### Pattern 3: Robust Error Handling

**Always include:**
```bash
# 1. Capture both stdout and stderr
output=$(gh issue create [...] 2>&1)
exit_code=$?

# 2. Check for errors
if [ $exit_code -ne 0 ] || [ -z "$output" ]; then
    echo "❌ Failed to create issue"
    echo "Error: $output"
    exit 1
fi

# 3. Validate output
issue_number=$(echo "$output" | grep -oP '/issues/\K\d+')
if [ -z "$issue_number" ]; then
    echo "❌ Could not parse issue number"
    exit 1
fi
```

### Pattern 4: Separate Assignment from Creation

**Problem:** `--assignee` flag often fails with permissions issues

**Solution:**
```bash
# 1. Create issue WITHOUT --assignee
issue_url=$(gh issue create \
  --title "Title" \
  --body-file /tmp/body.md \
  --label "labels")

issue_number=$(extract_number "$issue_url")

# 2. Assign separately using GraphQL or dedicated tool
./tools/assign-copilot-to-issue.sh "$issue_number"
```

---

## Permission Best Practices

### Token Requirements

For `gh issue create`:
- **Required scopes:** `repo` or `public_repo`
- **For assignment:** May need additional permissions

### Token Selection

```bash
# Prefer COPILOT_PAT for assignment capabilities
GH_TOKEN: ${{ secrets.COPILOT_PAT || secrets.GITHUB_TOKEN }}

# GITHUB_TOKEN works for basic creation
GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

---

## Label Management

### Pre-Create Labels

**Always ensure labels exist before creating issues:**

```bash
# Check if label exists
if ! gh label list | grep -q "^${label_name}"; then
    gh label create "$label_name" \
      --color "$color" \
      --description "$description"
fi
```

**Or in Python:**
```python
def ensure_label_exists(label_name, color, description):
    result = subprocess.run(['gh', 'label', 'list', '--search', label_name],
                          capture_output=True, text=True)
    if label_name not in result.stdout:
        subprocess.run(['gh', 'label', 'create', label_name,
                       '--color', color, '--description', description])
```

---

## Output Extraction Patterns

### Reliable Issue Number Extraction

```bash
# Method 1: Perl regex (most reliable)
issue_number=$(echo "$issue_url" | grep -oP '/issues/\K\d+' | head -1)

# Method 2: Standard regex
issue_number=$(echo "$issue_url" | grep -oE '[0-9]+$')

# Method 3: URL parsing
issue_number=$(echo "$issue_url" | awk -F'/' '{print $NF}')
```

### Validation

```bash
# Always validate extraction succeeded
if [ -z "$issue_number" ]; then
    echo "❌ Could not extract issue number from: $issue_url"
    exit 1
fi

# Optionally validate it's a number
if ! [[ "$issue_number" =~ ^[0-9]+$ ]]; then
    echo "❌ Invalid issue number: $issue_number"
    exit 1
fi
```

---

## Testing Recommendations

### Unit Tests

1. Test argument validation
2. Test body format handling
3. Test error conditions
4. Test output parsing

### Integration Tests

1. Test with real (or mock) GitHub API
2. Test permission scenarios
3. Test label creation flow
4. Test assignment flow

---

## Common Pitfalls to Avoid

### ❌ Anti-Pattern 1: Inline Body with Complex Content

```bash
# BAD: Shell quoting nightmare
gh issue create \
  --body "Line 1
Line 2 with $var
Line 3 with \"quotes\""
```

**Fix:** Use --body-file

### ❌ Anti-Pattern 2: No Error Checking

```bash
# BAD: Silent failures
issue_url=$(gh issue create [...])
echo "Created issue: $issue_url"
```

**Fix:** Check exit codes and validate output

### ❌ Anti-Pattern 3: Using --assignee Flag

```bash
# BAD: Often fails silently
gh issue create \
  --title "Title" \
  --body "Body" \
  --assignee copilot  # May fail due to permissions
```

**Fix:** Assign separately using GraphQL API

### ❌ Anti-Pattern 4: Missing Label Pre-Creation

```bash
# BAD: Will fail if label doesn't exist
gh issue create \
  --label "non-existent-label"  # Error!
```

**Fix:** Ensure labels exist first

---

## Migration Checklist

To update an existing workflow to use best practices:

- [ ] Use `--body-file` for bodies > 1000 chars
- [ ] Add comprehensive error handling
- [ ] Validate all extracted values
- [ ] Remove `--assignee` flag, assign separately
- [ ] Ensure labels exist before creation
- [ ] Add logging for debugging
- [ ] Test with both success and failure cases
- [ ] Document any special requirements

---

## Related Files

- `.github/workflows/meta-coordinator.yml` - Reference implementation
- `.github/workflows/autonomous-pipeline.yml` - PR creation examples
- `tools/create_mission_issues.py` - Python implementation
- `tools/gh-issue-create-wrapper.sh` - Reusable wrapper script
- `tests/test_gh_issue_create_wrapper.sh` - Test suite

---

## References

- [GitHub CLI Issue Docs](https://cli.github.com/manual/gh_issue_create)
- [GitHub API Permissions](https://docs.github.com/en/rest/overview/permissions-required-for-github-apps)
- Recent fix: Commit 2bc16099 - "Fix meta-coordinator issue creation using --body-file"
