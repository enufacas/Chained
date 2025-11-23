# Quick Reference: gh issue create

One-page reference for reliable GitHub issue creation.

## ✅ Use the Wrapper (Recommended)

```bash
# Most reliable method
tools/gh-issue-create-wrapper.sh \
  --title "Your Issue Title" \
  --body-file /tmp/issue_body.md \
  --label "bug,automated" \
  --repo "${GITHUB_REPOSITORY}"
```

Enable debug logging: `DEBUG=1`

## Pattern 1: Simple Issue

For content &lt; 500 chars, no special characters:

```yaml
- name: Create simple issue
  run: |
    issue_url=$(gh issue create \
      --repo ${{ github.repository }} \
      --title "Bug report" \
      --body "Short description" \
      --label "bug" 2>&1)
    
    [[ $? -ne 0 ]] && { echo "Failed: $issue_url"; exit 1; }
    issue_number=$(echo "$issue_url" | grep -oE '[0-9]+$')
```

## Pattern 2: Complex Issue

For large/complex content or with variables:

```yaml
- name: Create complex issue
  run: |
    cat > /tmp/issue_body.md <<'EOF'
    ## Description
    Details here with $variables
    EOF
    
    sed -i "s/\$variables/${variables}/g" /tmp/issue_body.md
    
    issue_url=$(gh issue create \
      --repo ${{ github.repository }} \
      --title "Title" \
      --body-file /tmp/issue_body.md \
      --label "automated" 2>&1)
    
    [[ $? -ne 0 ]] && { echo "Failed: $issue_url"; exit 1; }
```

## Pattern 3: With Assignment

```yaml
- name: Create and assign
  run: |
    # 1. Create (NO --assignee!)
    issue_url=$(gh issue create --body-file /tmp/body.md ...)
    issue_number=$(echo "$issue_url" | grep -oE '[0-9]+$')
    
    # 2. Assign separately
    ./tools/assign-copilot-to-issue.sh "$issue_number"
```

## Pattern 4: With Dynamic Labels

```yaml
- name: Ensure labels exist
  run: |
    for label in "label1" "label2"; do
      gh label list | grep -q "^$label" || \
        gh label create "$label" --color "0E8A16"
    done
    
    gh issue create --label "label1,label2" ...
```

## ❌ Common Mistakes

**DON'T:**
```bash
# Inline body with complex content
gh issue create --body "Line1\nLine2 with \"quotes\""  # FAILS

# Using --assignee flag
gh issue create --assignee copilot  # FAILS SILENTLY

# Missing label pre-creation
gh issue create --label "non-existent"  # FAILS

# No error checking
issue_url=$(gh issue create ...)
echo "Created: $issue_url"  # MAY BE EMPTY!
```

**DO:**
```bash
# Use --body-file
echo "$content" > /tmp/body.md
gh issue create --body-file /tmp/body.md

# Assign separately
issue_number=$(...)
./tools/assign-copilot-to-issue.sh "$issue_number"

# Pre-create labels
gh label create "label" || true
gh issue create --label "label"

# Always check errors
output=$(gh issue create ... 2>&1)
[[ $? -ne 0 ]] && { echo "Failed: $output"; exit 1; }
```

## Error Handling Template

```bash
# Capture output and exit code
output=$(gh issue create [...] 2>&1)
exit_code=$?

# Validate success
if [ $exit_code -ne 0 ] || [ -z "$output" ]; then
    echo "❌ Failed to create issue"
    echo "Error: $output"
    exit 1
fi

# Extract and validate issue number
issue_number=$(echo "$output" | grep -oP '/issues/\K\d+' | head -1)

if [ -z "$issue_number" ]; then
    echo "❌ Could not extract issue number"
    exit 1
fi

echo "✅ Created issue #$issue_number"
```

## Permissions

```yaml
# In workflow file
permissions:
  contents: write  # For commits
  issues: write    # For issue creation
  pull-requests: write  # If creating PRs

# Prefer COPILOT_PAT for assignment capabilities
env:
  GH_TOKEN: ${{ secrets.COPILOT_PAT || secrets.GITHUB_TOKEN }}
```

## Testing

```bash
# Test the wrapper
./tests/test_gh_issue_create_wrapper.sh

# Manual test
DEBUG=1 tools/gh-issue-create-wrapper.sh \
  --title "TEST" \
  --body "Test body" \
  --repo "owner/repo"
```

## Documentation

- **Patterns:** `docs/GH_ISSUE_CREATE_SUCCESS_PATTERNS.md`
- **Guide:** `docs/GH_ISSUE_CREATE_IMPLEMENTATION_GUIDE.md`
- **Summary:** `docs/gh-issue-create-fix-summary.md`

## Help

```bash
# Get help
tools/gh-issue-create-wrapper.sh --help

# Enable debug mode
DEBUG=1 tools/gh-issue-create-wrapper.sh [...]
```

---

**Key Takeaway:** Use `--body-file` for complex content, never use `--assignee`, always check errors.
