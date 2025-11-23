# Practical Guide: Implementing Reliable Issue Creation

This guide shows step-by-step how to implement reliable GitHub issue creation in workflows, based on successful patterns from the repository.

## Quick Start: Use the Wrapper Script

The easiest and most reliable way is to use the provided wrapper:

```yaml
- name: Create issue with comprehensive logging
  env:
    GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
    GITHUB_REPOSITORY: ${{ github.repository }}
    DEBUG: 1  # Enable detailed logging
  run: |
    # Create body content
    cat > /tmp/issue_body.md <<'EOF'
    ## Issue Description
    
    This is the issue body with full markdown support.
    
    - Can have lists
    - Can have code blocks
    - Can reference variables after creation
    EOF
    
    # Use the wrapper
    tools/gh-issue-create-wrapper.sh \
      --title "My Issue Title" \
      --body-file /tmp/issue_body.md \
      --label "bug,automated" \
      --repo "$GITHUB_REPOSITORY"
```

## Implementation Patterns

### Pattern 1: Simple Issue (Short Content)

**Use Case:** Quick issues with simple, short descriptions

```yaml
- name: Create simple issue
  env:
    GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
  run: |
    issue_url=$(gh issue create \
      --repo ${{ github.repository }} \
      --title "Simple bug report" \
      --body "This is a simple description without special characters" \
      --label "bug,automated" \
      2>&1)
    
    if [ $? -ne 0 ]; then
      echo "❌ Failed to create issue: $issue_url"
      exit 1
    fi
    
    issue_number=$(echo "$issue_url" | grep -oE '[0-9]+$')
    echo "✅ Created issue #$issue_number"
    echo "issue_number=$issue_number" >> $GITHUB_OUTPUT
```

### Pattern 2: Complex Issue (Large Content, Variables)

**Use Case:** Detailed issues with markdown, variables, multi-line content

```yaml
- name: Create complex issue
  env:
    GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
  run: |
    # Define variables
    RUN_ID="${{ github.run_id }}"
    TIMESTAMP=$(date -u +"%Y-%m-%d %H:%M:%S UTC")
    
    # Create body with heredoc (prevents quoting issues)
    cat > /tmp/issue_body.md <<'EOF'
    ## Detailed Issue Report
    
    **Run ID:** ${RUN_ID}
    **Timestamp:** ${TIMESTAMP}
    
    ### Problem Description
    
    This issue was automatically created because...
    
    ### Steps to Reproduce
    
    1. First step
    2. Second step
    3. Third step
    
    ### Expected Behavior
    
    The system should...
    
    ### Actual Behavior
    
    Instead, it...
    
    ### Additional Context
    
    ```bash
    # Relevant command output
    Some output here
    ```
    
    ### Related Links
    
    - [Workflow Run](${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }})
    EOF
    
    # Substitute variables
    sed -i "s|\${RUN_ID}|${RUN_ID}|g" /tmp/issue_body.md
    sed -i "s|\${TIMESTAMP}|${TIMESTAMP}|g" /tmp/issue_body.md
    
    # Create issue using --body-file
    issue_url=$(gh issue create \
      --repo ${{ github.repository }} \
      --title "Automated Report - $(date +%Y-%m-%d)" \
      --body-file /tmp/issue_body.md \
      --label "automated,report" \
      2>&1)
    
    exit_code=$?
    
    if [ $exit_code -ne 0 ] || [ -z "$issue_url" ]; then
      echo "❌ Failed to create issue"
      echo "Error: $issue_url"
      exit 1
    fi
    
    # Extract and validate issue number
    issue_number=$(echo "$issue_url" | grep -oP '/issues/\K\d+' | head -1)
    
    if [ -z "$issue_number" ]; then
      echo "❌ Could not extract issue number from: $issue_url"
      exit 1
    fi
    
    echo "✅ Created issue #$issue_number"
    echo "   URL: $issue_url"
    echo "issue_number=$issue_number" >> $GITHUB_OUTPUT
```

### Pattern 3: Issue with Copilot Assignment

**Use Case:** Creating issue and assigning to Copilot for automated work

```yaml
- name: Create and assign issue
  env:
    GH_TOKEN: ${{ secrets.COPILOT_PAT || secrets.GITHUB_TOKEN }}
    GITHUB_REPOSITORY: ${{ github.repository }}
  run: |
    # Create issue body
    cat > /tmp/issue_body.md <<'EOF'
    ## Task for Copilot
    
    > **🤖 Agent Profile**: Please use the **@engineer-master** agent.
    >
    > **IMPORTANT**: Always mention **@engineer-master** by name in all work.
    
    ### Task Description
    
    Please implement the following feature...
    
    ### Acceptance Criteria
    
    - [ ] Feature X implemented
    - [ ] Tests added
    - [ ] Documentation updated
    EOF
    
    # Create issue (WITHOUT --assignee)
    echo "Creating issue..."
    issue_url=$(gh issue create \
      --repo "${GITHUB_REPOSITORY}" \
      --title "Implement Feature X" \
      --body-file /tmp/issue_body.md \
      --label "enhancement,automated" \
      2>&1)
    
    if [ $? -ne 0 ] || [ -z "$issue_url" ]; then
      echo "❌ Failed to create issue: $issue_url"
      exit 1
    fi
    
    issue_number=$(echo "$issue_url" | grep -oP '/issues/\K\d+' | head -1)
    
    if [ -z "$issue_number" ]; then
      echo "❌ Could not extract issue number"
      exit 1
    fi
    
    echo "✅ Created issue #$issue_number"
    
    # Assign Copilot separately (more reliable than --assignee)
    echo "Assigning Copilot to issue..."
    
    if [ -f tools/assign-copilot-to-issue.sh ]; then
      chmod +x tools/assign-copilot-to-issue.sh
      ./tools/assign-copilot-to-issue.sh "$issue_number" "engineer-master" || {
        echo "⚠️ Assignment failed, but issue was created"
      }
    else
      echo "⚠️ Assignment tool not found, skipping"
    fi
    
    echo "issue_number=$issue_number" >> $GITHUB_OUTPUT
```

### Pattern 4: Issue with Dynamic Labels

**Use Case:** Creating issues with labels that may not exist yet

```yaml
- name: Create issue with dynamic labels
  env:
    GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
  run: |
    # Define labels needed
    LABELS=("automated" "priority-high" "workflow-generated")
    LABEL_COLORS=("FBCA04" "D73A4A" "0E8A16")
    
    # Ensure all labels exist
    echo "Ensuring labels exist..."
    for i in "${!LABELS[@]}"; do
      label="${LABELS[$i]}"
      color="${LABEL_COLORS[$i]}"
      
      if ! gh label list --repo ${{ github.repository }} | grep -q "^${label}"; then
        echo "Creating label: $label"
        gh label create "$label" \
          --color "$color" \
          --description "Auto-generated label" \
          --repo ${{ github.repository }} || echo "Label may already exist"
      fi
    done
    
    # Now create issue with labels
    label_string=$(IFS=,; echo "${LABELS[*]}")
    
    issue_url=$(gh issue create \
      --repo ${{ github.repository }} \
      --title "Issue with validated labels" \
      --body "This issue has pre-validated labels" \
      --label "$label_string" \
      2>&1)
    
    if [ $? -ne 0 ]; then
      echo "❌ Failed: $issue_url"
      exit 1
    fi
    
    issue_number=$(echo "$issue_url" | grep -oE '[0-9]+$')
    echo "✅ Created issue #$issue_number with labels: $label_string"
```

## Python Implementation

For Python tools, use subprocess with proper error handling:

```python
import subprocess
import sys

def create_github_issue(title, body, labels, repo):
    """
    Create a GitHub issue with comprehensive error handling.
    
    Args:
        title: Issue title
        body: Issue body (can be large/complex)
        labels: Comma-separated string of labels
        repo: Repository in format "owner/name"
    
    Returns:
        tuple: (success: bool, issue_number: str or None, error: str or None)
    """
    # Write body to temporary file
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        f.write(body)
        body_file = f.name
    
    try:
        # Create issue using --body-file
        result = subprocess.run(
            [
                'gh', 'issue', 'create',
                '--repo', repo,
                '--title', title,
                '--body-file', body_file,
                '--label', labels
            ],
            capture_output=True,
            text=True,
            check=False  # Don't raise on non-zero exit
        )
        
        if result.returncode != 0:
            return False, None, f"gh CLI failed: {result.stderr}"
        
        issue_url = result.stdout.strip()
        
        if not issue_url:
            return False, None, "No output from gh CLI"
        
        # Extract issue number from URL
        import re
        match = re.search(r'/issues/(\d+)$', issue_url)
        if not match:
            return False, None, f"Could not parse issue number from: {issue_url}"
        
        issue_number = match.group(1)
        
        print(f"✅ Created issue #{issue_number}")
        print(f"   URL: {issue_url}")
        
        return True, issue_number, None
        
    except Exception as e:
        return False, None, f"Exception: {str(e)}"
    
    finally:
        # Clean up temp file
        import os
        if os.path.exists(body_file):
            os.unlink(body_file)

# Usage example
if __name__ == '__main__':
    success, issue_num, error = create_github_issue(
        title="Test Issue",
        body="## Test\n\nThis is a test issue with markdown.",
        labels="test,automated",
        repo="owner/repo"
    )
    
    if not success:
        print(f"❌ Failed: {error}", file=sys.stderr)
        sys.exit(1)
    
    print(f"Issue created: #{issue_num}")
```

## Testing Your Implementation

### Manual Test

```bash
# Set environment
export GH_TOKEN="your-token-here"
export GITHUB_REPOSITORY="owner/repo"
export DEBUG=1

# Create test body
cat > /tmp/test_body.md <<'EOF'
## Test Issue

This is a test issue for validation.

**Purpose:** Verify issue creation works correctly

### Checklist
- [ ] Issue created successfully
- [ ] Labels applied
- [ ] Body formatted correctly
EOF

# Test with wrapper
./tools/gh-issue-create-wrapper.sh \
  --title "TEST: Manual Validation" \
  --body-file /tmp/test_body.md \
  --label "test,manual-validation" \
  --repo "$GITHUB_REPOSITORY"
```

### Automated Test

```bash
# Run test suite
./tests/test_gh_issue_create_wrapper.sh

# Run Python tests
python3 tests/test_mission_issue_creation.py
```

## Troubleshooting

### Issue: "Permission denied" errors

**Solution:**
```yaml
# Use COPILOT_PAT instead of GITHUB_TOKEN
env:
  GH_TOKEN: ${{ secrets.COPILOT_PAT || secrets.GITHUB_TOKEN }}
```

### Issue: Labels not found

**Solution:** Ensure labels exist before creating issue (see Pattern 4)

### Issue: Body contains unescaped quotes

**Solution:** Use `--body-file` instead of `--body`

### Issue: Cannot extract issue number

**Solution:** Check URL format and use robust regex:
```bash
issue_number=$(echo "$issue_url" | grep -oP '/issues/\K\d+' | head -1)
```

### Issue: Silent failures

**Solution:** Always check exit codes and validate output:
```bash
exit_code=$?
if [ $exit_code -ne 0 ] || [ -z "$output" ]; then
    echo "❌ Failed"
    exit 1
fi
```

## See Also

- [Success Patterns Documentation](./GH_ISSUE_CREATE_SUCCESS_PATTERNS.md)
- [GitHub CLI Documentation](https://cli.github.com/manual/gh_issue_create)
- [Wrapper Script](../tools/gh-issue-create-wrapper.sh)
- [Test Suite](../tests/test_gh_issue_create_wrapper.sh)
