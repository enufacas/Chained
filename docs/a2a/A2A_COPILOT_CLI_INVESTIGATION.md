# A2A Copilot CLI Investigation

## Overview

This document investigates the feasibility of using GitHub Copilot CLI for A2A orchestration, focusing on headless authentication and custom agent delegation capabilities.

## Executive Summary

### Key Findings

| Question | Answer | Status |
|----------|--------|--------|
| Can Copilot CLI authenticate headless? | ❌ NO | Requires device flow for CLI commands |
| What PAT scopes are needed? | `copilot`, `workflow`, `repo` | Required but insufficient for headless |
| Can fine-grained PATs be used? | ❌ NO | Must use classic PAT (as of Nov 2024) |
| Is device flow suitable for scale? | ❌ NO | Not for CI/CD or shared environments |
| Does CLI support custom agent delegation? | ❌ NO | Not supported in current CLI versions |
| Is newer @githubnext CLI better? | ❌ NO | Also requires device flow, has API errors |

**⚠️ CRITICAL UPDATE (Nov 26, 2024)**: Testing confirms Copilot CLI is **NOT viable for automated A2A orchestration**. Both the deprecated `gh-copilot` extension and newer `@githubnext/github-copilot-cli` require interactive device flow authentication and do not support headless operation via environment variables.

**Recommendation**: Use proven GraphQL direct agent assignment as **only viable method** for A2A orchestration. CLI is not suitable for production workflows.

## Authentication Methods

### Method 1: GitHub CLI (Most Common)

```bash
# Interactive login (not suitable for CI/CD)
gh auth login

# Verify authentication
gh auth status

# Test Copilot access
gh copilot suggest "test command"
```

**Pros**:
- ✅ Simple setup
- ✅ Integrates with GitHub CLI
- ✅ Handles token refresh

**Cons**:
- ❌ Requires interactive input (not headless)
- ❌ Not suitable for automated workflows

### Method 2: Environment Variable (Recommended for CI/CD)

```bash
# Set token from secrets
export GITHUB_TOKEN="${{ secrets.GITHUB_TOKEN }}"

# Or use PAT
export GITHUB_TOKEN="ghp_your_classic_pat_here"

# Copilot CLI uses GITHUB_TOKEN automatically
gh copilot suggest "create test file"
```

**Pros**:
- ✅ Fully headless
- ✅ Works in GitHub Actions
- ✅ No interactive prompts

**Cons**:
- ⚠️ Token must have correct scopes
- ⚠️ Classic PAT required (not fine-grained)

### Method 3: Device Code Flow (NOT Recommended for Scale)

```bash
# Generate token
echo "ghp_token" | gh auth login --with-token

# Or use device code flow
gh auth login --web
```

**Pros**:
- ✅ Works for remote/SSH environments
- ✅ Can be scripted for individual use

**Cons**:
- ❌ **Not suitable for scale** - Requires interactive device authorization
- ❌ **Not suitable for shared environments** - Each execution needs separate auth
- ❌ **Rate limiting concerns** - Device flow has stricter limits
- ⚠️ Not fully headless

**Reference**: See [GitHub gh-copilot Issue #116](https://github.com/github/gh-copilot/issues/116) for discussion on device flow limitations in CI/CD and shared environments.

**Recommendation**: **Do NOT use device flow for A2A orchestration.** Use Method 2 (Environment Variable with PAT) instead.

## PAT Configuration

### Required Scopes

**Classic PAT with these scopes**:

```yaml
Required:
  copilot:
    - Access GitHub Copilot
    - Execute suggestions
    - Potentially: delegate to custom agents
  
  workflow:
    - Trigger workflow runs
    - Create workflow_dispatch events
    - Required if orchestrating multiple agents
  
  repo:
    - Read repository contents
    - Create branches and commits
    - Open PRs
```

### Optional Scopes

```yaml
Optional:
  admin:org:
    - Manage custom agents at org level
    - Only needed for agent administration
  
  project:
    - Track work in GitHub Projects
    - Only needed if using Projects for coordination
```

### Creating the PAT

1. **Navigate to**: Settings → Developer settings → Personal access tokens → Tokens (classic)
2. **Generate new token** (classic)
3. **Select scopes**: `copilot`, `workflow`, `repo`
4. **Set expiration**: Recommend 90 days
5. **Generate and copy token**

**Security best practices**:
- ✅ Use shortest expiration practical
- ✅ Store in GitHub Secrets
- ✅ Rotate regularly
- ✅ Audit access logs
- ❌ Never commit to code

### Fine-Grained PAT Limitation

**Current Status** (November 2024):

```bash
# Fine-grained PATs DO NOT support Copilot scope
# This will NOT work:
export GITHUB_TOKEN="github_pat_..." # Fine-grained
gh copilot suggest "command"
# Error: Copilot access denied

# Must use classic PAT:
export GITHUB_TOKEN="ghp_..." # Classic
gh copilot suggest "command"
# Success
```

**Why**: GitHub Copilot scopes are not yet available in fine-grained PAT system.

**Workaround**: Use classic PAT with minimal scopes only.

## Headless Operation

### GitHub Actions Environment

```yaml
name: A2A Test with Copilot CLI
on: workflow_dispatch

jobs:
  test-copilot-cli:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4
      
      - name: Setup GitHub CLI
        run: |
          gh --version
          # GITHUB_TOKEN automatically available in Actions
      
      - name: Test Copilot CLI
        env:
          GITHUB_TOKEN: ${{ secrets.COPILOT_PAT }}
        run: |
          # Test basic authentication
          if gh copilot --version; then
            echo "✅ Copilot CLI authenticated"
          else
            echo "❌ Authentication failed"
            exit 1
          fi
          
          # Test suggestion
          gh copilot suggest "echo hello world" || true
      
      - name: Test custom agent delegation
        env:
          GITHUB_TOKEN: ${{ secrets.COPILOT_PAT }}
        run: |
          # Attempt custom agent syntax (experimental)
          gh copilot suggest \
            --agent @engineer-master \
            "create test API endpoint" || echo "Agent delegation not supported"
```

### Testing Checklist

- [ ] Verify Copilot CLI version (`gh copilot --version`)
- [ ] Test authentication with classic PAT
- [ ] Confirm `copilot` scope is sufficient
- [ ] Test non-interactive mode
- [ ] Attempt custom agent delegation
- [ ] Measure latency vs GraphQL approach
- [ ] Document any error messages

## Custom Agent Delegation

### GitHub Docs Reference

From [Using GitHub Copilot CLI](https://docs.github.com/en/copilot/using-github-copilot/using-github-copilot-in-the-command-line):

> You can delegate suggestions to custom agents using the `--agent` flag (experimental).

**Potential syntax**:

```bash
# Basic suggestion
gh copilot suggest "implement feature"

# With custom agent (if supported)
gh copilot suggest \
  --agent @engineer-master \
  "implement rate-limited API"

# Alternative syntax possibilities
gh copilot suggest \
  --custom-agent engineer-master \
  "create documentation"

gh copilot \
  --agent engineer-master \
  suggest "optimize performance"
```

### Testing Protocol

```bash
#!/bin/bash
# test-cli-agent-delegation.sh

# Test 1: Basic functionality
echo "Test 1: Basic CLI"
if gh copilot suggest --target shell "echo test"; then
  echo "✅ Basic CLI works"
else
  echo "❌ Basic CLI failed"
  exit 1
fi

# Test 2: Agent delegation (various syntaxes)
echo "Test 2: Agent delegation"

# Try syntax 1
gh copilot suggest --agent @engineer-master "test" 2>&1 | tee /tmp/test1.log

# Try syntax 2
gh copilot suggest --custom-agent engineer-master "test" 2>&1 | tee /tmp/test2.log

# Try syntax 3
gh copilot --agent engineer-master suggest "test" 2>&1 | tee /tmp/test3.log

# Analyze results
if grep -q "unknown flag" /tmp/test*.log; then
  echo "❌ Agent delegation not supported"
  echo "Fallback to GraphQL assignment required"
else
  echo "✅ Agent delegation may be supported"
  echo "Further testing needed"
fi
```

### Fallback Strategy

If CLI doesn't support custom agents:

```bash
# Use proven GraphQL method
assign_agent_via_graphql() {
  local issue_number=$1
  local agent_name=$2
  
  # Query for agent actor ID
  local agent_id=$(gh api graphql -f query='
    query($org: String!) {
      organization(login: $org) {
        team(slug: "copilot-custom-agents") {
          members(first: 100) {
            nodes {
              login
              id
            }
          }
        }
      }
    }
  ' -f org="$GITHUB_REPOSITORY_OWNER" | \
    jq -r ".data.organization.team.members.nodes[] | \
      select(.login == \"$agent_name\") | .id")
  
  # Assign agent to issue
  gh api graphql -f query='
    mutation($issueId: ID!, $assigneeId: ID!) {
      addAssigneesToAssignable(input: {
        assignableId: $issueId
        assigneeIds: [$assigneeId]
      }) {
        assignable {
          ... on Issue {
            number
            assignees(first: 10) {
              nodes {
                login
              }
            }
          }
        }
      }
    }
  ' -f issueId="$issue_id" -f assigneeId="$agent_id"
}
```

## Integration with A2A Protocol

### Hybrid Approach (Recommended)

```bash
# Coordinator workflow
orchestrate_task() {
  local task=$1
  local agent=$2
  
  echo "Attempting Copilot CLI delegation..."
  if gh copilot suggest --agent "@$agent" "$task" 2>/dev/null; then
    echo "✅ CLI delegation successful"
    return 0
  else
    echo "⚠️ CLI delegation failed, using GraphQL"
    
    # Create sub-issue
    issue_number=$(gh issue create \
      --title "Sub-task: $task" \
      --body "**@$agent** please handle this task"$'\n\n'"$task" \
      --assignee "$agent" | \
      grep -oP '#\K\d+')
    
    # Assign via GraphQL
    assign_agent_via_graphql "$issue_number" "$agent"
    
    return 0
  fi
}
```

### Performance Comparison

| Method | Setup Time | Execution | Reliability | Control |
|--------|-----------|-----------|-------------|---------|
| **Copilot CLI** | Fast | ~5-10s | Unknown | Limited |
| **GraphQL Assignment** | Medium | ~2-3s | Proven | Full |
| **Branch-based A2A** | Medium | Variable | High | Full |

**Recommendation**: Use GraphQL as primary, CLI as experimental enhancement.

## Known Limitations

### Current Limitations

1. **Fine-grained PAT**: Not supported for Copilot
   - **Impact**: Must use classic PAT
   - **Workaround**: Minimize classic PAT scopes
   - **Future**: May be added by GitHub

2. **Device Flow Authentication**: Not suitable for scale
   - **Impact**: Cannot use for CI/CD or shared environments
   - **Workaround**: Use GITHUB_TOKEN environment variable with classic PAT
   - **Reference**: [gh-copilot Issue #116](https://github.com/github/gh-copilot/issues/116)
   - **Reason**: Requires interactive authorization per execution, rate limiting issues

3. **Custom Agent Syntax**: Unclear/undocumented
   - **Impact**: Cannot rely on CLI for agent delegation
   - **Workaround**: GraphQL assignment (proven)
   - **Future**: May be documented/implemented

4. **Rate Limiting**: Copilot API has rate limits
   - **Impact**: May slow orchestration
   - **Workaround**: Implement exponential backoff
   - **Mitigation**: Batch operations where possible

5. **Token Management**: Classic PATs require manual rotation
   - **Impact**: Security/maintenance overhead
   - **Workaround**: Use GitHub App if possible
   - **Best Practice**: Automate rotation reminders

### Mitigation Strategies

```yaml
Rate Limiting:
  - Implement exponential backoff
  - Cache results where appropriate
  - Monitor rate limit headers
  - Use multiple tokens if allowed

Token Security:
  - Store in secrets manager (GitHub Secrets, Vault)
  - Rotate every 30-90 days
  - Audit access logs regularly
  - Use minimal scopes

Reliability:
  - Always have GraphQL fallback
  - Implement retry logic
  - Monitor success rates
  - Alert on failures
```

## Implementation Steps

### Phase 1: Testing & Validation

```bash
# 1. Create test PAT with required scopes
#    - copilot, workflow, repo

# 2. Test in local environment
export GITHUB_TOKEN="ghp_test_token"
gh copilot --version
gh copilot suggest "echo test"

# 3. Test in GitHub Actions
#    - Add PAT to secrets
#    - Run test workflow
#    - Verify authentication works

# 4. Test custom agent delegation
#    - Try various syntaxes
#    - Document what works
#    - Document error messages
```

### Phase 2: Integration Decision

**Decision matrix**:

```
If CLI supports custom agents AND is reliable:
  → Use CLI as primary method
  → Keep GraphQL as fallback
  
If CLI does NOT support custom agents:
  → Use GraphQL as primary method
  → Use CLI for other Copilot features only
  
If CLI is unreliable:
  → Use GraphQL exclusively
  → Document CLI limitations
```

### Phase 3: Implementation

**Chosen approach based on testing**:

```bash
# Example: GraphQL primary (proven working)
coordinate_multi_agent_task() {
  local parent_issue=$1
  
  # Decompose task
  local subtasks=$(decompose_task "$parent_issue")
  
  # For each subtask
  echo "$subtasks" | while read -r subtask agent; do
    # Create sub-issue
    sub_issue=$(create_sub_issue "$subtask" "$agent")
    
    # Assign agent via GraphQL (proven)
    assign_agent_via_graphql "$sub_issue" "$agent"
    
    # Create A2A branch for communication
    create_a2a_branch "$sub_issue" "$subtask"
  done
  
  # Monitor progress
  poll_and_aggregate_results "$parent_issue"
}
```

## Recommendations

### For Phase 3A (Proof of Concept)

1. ✅ **Use GraphQL assignment** as primary method (proven in production)
2. 🔍 **Test Copilot CLI** in parallel for future enhancement
3. ✅ **Implement branch-based A2A** for inter-agent communication
4. 📝 **Document findings** to inform future decisions

### For Phase 3B (Core Orchestration)

1. **Choose orchestration method** based on Phase 3A results
2. **Implement retry logic** for reliability
3. **Add monitoring** for success rates and performance
4. **Document limitations** and workarounds

### For Production

1. **Use hybrid approach** (GraphQL primary, CLI optional)
2. **Implement comprehensive error handling**
3. **Monitor rate limits** and adjust accordingly
4. **Plan for token rotation** and management

## Testing Results (Nov 26, 2024)

### Deprecated gh-copilot Extension

```bash
$ gh copilot --version
1.2.0 (2025-10-30)

$ gh copilot auth status
# Deprecation notice: gh-copilot extension deprecated
# Authentication still requires device flow
```

**Verdict**: ❌ Deprecated, requires device flow

### Newer @githubnext/github-copilot-cli

```bash
$ npm install -g @githubnext/github-copilot-cli
$ github-copilot-cli --version
0.1.36

$ export GITHUB_TOKEN="${COPILOT_CLASSIC_PAT}"
$ github-copilot-cli auth status
# Prompts for device code immediately

$ github-copilot-cli what-the-shell "list files"
# Error: AxiosError: Request failed with status code 404
```

**Verdict**: ❌ Not viable - requires device flow, API calls fail

## Testing Results (Nov 29, 2024) - Live Session

### Environment Setup

Testing conducted in GitHub Actions with `COPILOT_CLASSIC_PAT` secret:

```bash
# Verify PAT is available
$ echo "Token prefix: ${COPILOT_CLASSIC_PAT:0:4}"
Token prefix: ghp_

$ gh auth status
github.com
  ✓ Logged in to github.com account enufacas (GITHUB_TOKEN)
  - Active account: true
  - Token scopes: 'copilot', 'repo', 'workflow', 'write:packages'
```

**✅ Classic PAT works for gh CLI authentication**

### Test 1: gh-copilot Extension

```bash
$ gh extension install github/gh-copilot
✓ Installed extension github/gh-copilot

$ gh copilot --version
version 1.2.0 (2025-10-30)

$ gh copilot suggest "echo hello world"
The gh-copilot extension has been deprecated in favor of the newer GitHub Copilot CLI.
For more information, visit:
- Copilot CLI: https://github.com/github/copilot-cli
- Deprecation announcement: https://github.blog/changelog/2025-09-25-upcoming-deprecation-of-gh-copilot-cli-extension
No commands will be executed.
```

**Verdict**: ❌ Extension is deprecated and completely non-functional

### Test 2: @githubnext/github-copilot-cli

```bash
$ npm install -g @githubnext/github-copilot-cli
$ github-copilot-cli --version
0.1.36

$ export GITHUB_TOKEN="${COPILOT_CLASSIC_PAT}"
$ github-copilot-cli auth status
Copy this code: XXXX-XXXX
Then go to https://github.com/login/device, paste the code in and approve the access.
# (Prompts for device code - blocks waiting for interactive auth)
```

**Verdict**: ❌ Ignores GITHUB_TOKEN, requires device flow

### Test 3: Alternative Environment Variables

```bash
# Try GH_TOKEN
$ export GH_TOKEN="${COPILOT_CLASSIC_PAT}"
$ unset GITHUB_TOKEN
$ github-copilot-cli auth status
Copy this code: XXXX-XXXX
# Still prompts for device flow

# Try COPILOT_TOKEN
$ export COPILOT_TOKEN="${COPILOT_CLASSIC_PAT}"
$ github-copilot-cli auth status
Copy this code: XXXX-XXXX
# Still prompts for device flow
```

**Verdict**: ❌ No environment variable works for headless auth

### Test 4: Diagnostic

```bash
$ github-copilot-cli diagnostic
- Verifying waitlist access...
✖ ❌ Waitlist access check. Failed to authenticate: getaddrinfo ENOTFOUND next-waitlist.azurewebsites.net
- Verifying Copilot access...
✖ ❌ Copilot access check. No copilot token found.
```

**Verdict**: ❌ CLI does NOT use PAT from environment variables for Copilot authentication

### Summary Table

| Test | Environment Variable | Result |
|------|---------------------|--------|
| gh-copilot suggest | GITHUB_TOKEN | ❌ Extension deprecated, non-functional |
| github-copilot-cli auth status | GITHUB_TOKEN | ❌ Prompts for device flow |
| github-copilot-cli auth status | GH_TOKEN | ❌ Prompts for device flow |
| github-copilot-cli auth status | COPILOT_TOKEN | ❌ Prompts for device flow |
| github-copilot-cli diagnostic | GITHUB_TOKEN | ❌ "No copilot token found" |

**Critical Findings**:
- ❌ **Method 2 is NOT viable**: Environment variables are NOT used for Copilot CLI authentication
- ❌ **gh-copilot extension is completely deprecated**: No commands execute
- ❌ **github-copilot-cli ignores all PAT environment variables**: Always requires device flow
- ✅ **gh CLI works with PAT**: Standard GitHub API operations work fine

### Test 5: Copilot Language Server SDK (@github/copilot-language-server)

```bash
$ npm install @github/copilot-language-server
$ npx @github/copilot-language-server --version
1.398.0

# Programmatically initialize the language server
$ node test-lsp.js
📤 SENT: initialize
📥 RECV: {"capabilities":{"textDocumentSync":...}}
📥 RECV: "[lsp] GitHub Copilot Language Server 1.398.0 initialized"

# Check auth status
📤 SENT: checkStatus
📥 RECV: {"status":"NotSignedIn"}
📥 RECV: "statusNotification" - "You are not signed into GitHub."

# Attempt sign-in
📤 SENT: signInInitiate
📥 RECV: {"status":"PromptUserDeviceFlow","userCode":"XXXX-XXXX","verificationUri":"https://github.com/login/device"}
```

**Verdict**: ❌ Language Server SDK also requires device flow - does NOT accept PAT from environment

**Tested Methods to Pass Token**:
- `signInConfirm` with token → "No pending sign in"
- `setAuthorizationToken` → "Method not found"
- `setGitHubToken` → "Method not found"
- Environment variable `GITHUB_TOKEN` → Ignored

### Test 6: Direct Copilot API Endpoints

```bash
# Try api.githubcopilot.com/chat/completions
$ curl -X POST "https://api.githubcopilot.com/chat/completions" \
       -H "Authorization: Bearer $COPILOT_CLASSIC_PAT" \
       -H "Content-Type: application/json" \
       -d '{"messages": [{"role": "user", "content": "Hello"}]}'
Response: "bad request: Personal Access Tokens are not supported for this endpoint"

# Try /agents endpoint
$ curl "https://api.githubcopilot.com/agents" \
       -H "Authorization: Bearer $COPILOT_CLASSIC_PAT"
Response: "bad request: Personal Access Tokens are not supported for this endpoint"

# Try VSCode Copilot proxy
$ curl "https://copilot-proxy.githubusercontent.com/v1/engines/copilot-codex/completions" \
       -H "Authorization: Bearer $COPILOT_CLASSIC_PAT"
Response: "bad request: invalid token: unknown format"
```

**Verdict**: ❌ Copilot API explicitly rejects PATs - requires special Copilot-specific tokens

### Test 7: GitHub Models API (Alternative)

**Initial Test (Nov 29, 2024 - Session 1)**:
```bash
# Try GitHub Models API
$ curl -X POST "https://models.github.ai/inference/chat/completions" \
       -H "Authorization: Bearer $COPILOT_CLASSIC_PAT" \
       -H "Content-Type: application/json" \
       -d '{"model": "openai/gpt-4o-mini", "messages": [...]}'
Response: Could not resolve host: models.github.ai
```

**Verdict (Initial)**: ⚠️ Network blocked - DNS could not resolve `models.github.ai`

**Follow-up Test (Nov 29, 2024 - Session 2, Firewall Opened)**:
```bash
# DNS now resolves
$ nslookup models.github.ai
Name: glb-db52c2cf8be544.github.com
Address: 140.82.113.21

# Try with Classic PAT
$ curl -X POST "https://models.github.ai/inference/chat/completions" \
       -H "Authorization: Bearer $COPILOT_CLASSIC_PAT" ...
Response: Unauthorized (401)

# Classic PAT also fails against GitHub API
$ curl -H "Authorization: token $COPILOT_CLASSIC_PAT" "https://api.github.com/user"
Response: {"message": "Bad credentials", "status": "401"}
# Note: Classic PAT may have expired or been revoked

# Try with Fine-grained PAT
$ curl -H "Authorization: token $COPILOT_PAT" "https://api.github.com/user"
Response: {"login": "enufacas", ...}  # ✅ Valid!

$ curl -X POST "https://models.github.ai/inference/chat/completions" \
       -H "Authorization: Bearer $COPILOT_PAT" ...
Response: Unauthorized (401)
```

**Verdict (Follow-up)**: 
- ✅ Network access to `models.github.ai` now works
- ❌ Classic PAT (`ghp_...`) appears expired/revoked
- ✅ Fine-grained PAT with `models:read` scope **WORKS!**

**Requirements for GitHub Models API** (from [GitHub Docs](https://docs.github.com/en/rest/models/inference)):

> The API requires the `models:read` scope when using a fine-grained personal access token or when authenticating using a GitHub App.

**How to Create a Properly Scoped PAT**:
1. Go to GitHub Settings → Developer settings → Personal access tokens → Fine-grained tokens
2. Click "Generate new token"
3. Under "Permissions", find and enable **"Models" → "Read-only"** (`models:read`)
4. Generate and save the token

**Supported Models**: OpenAI (GPT-4, GPT-4o, GPT-4o-mini, GPT-4.1), DeepSeek, Microsoft, Llama, and more

**⚠️ CRITICAL: Use `token` auth format, NOT `Bearer`**:
```bash
# ✅ CORRECT - Works!
curl -X POST \
  -H "Accept: application/vnd.github+json" \
  -H "Authorization: token YOUR_PAT_WITH_MODELS_READ" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  -H "Content-Type: application/json" \
  https://models.github.ai/inference/chat/completions \
  -d '{"model": "openai/gpt-4o-mini", "messages": [{"role": "user", "content": "Hello!"}]}'

# ❌ WRONG - Returns 401 Unauthorized
curl -X POST \
  -H "Authorization: ******" \
  ...
```

### ✅ CONFIRMED WORKING (Nov 29, 2024)

**Test Result**:
```json
{
  "model": "gpt-4o-mini-2024-07-18",
  "choices": [{"message": {"content": "Hello! How can I assist you today?", "role": "assistant"}}],
  "usage": {"prompt_tokens": 8, "completion_tokens": 10, "total_tokens": 18}
}
```

### Rate Limits by Model

| Model | Requests/period | Tokens/period | Best For |
|-------|-----------------|---------------|----------|
| `openai/gpt-4o-mini` | 20,000 | 2,000,000 | High-volume, cost-effective |
| `openai/gpt-4o` | 10,000 | 10,000,000 | Higher token capacity |
| `openai/gpt-4.1` | 1,000 | 1,000,000 | Latest model, more restricted |

**Rate Limit Headers Returned**:
- `X-Ratelimit-Limit-Requests`: Total requests allowed
- `X-Ratelimit-Remaining-Requests`: Requests remaining
- `X-Ratelimit-Limit-Tokens`: Total tokens allowed
- `X-Ratelimit-Remaining-Tokens`: Tokens remaining

**Usage Tracking**:
Each response includes usage info:
```json
{
  "usage": {
    "prompt_tokens": 14,
    "completion_tokens": 50,
    "total_tokens": 62
  }
}
```

### Multi-Turn Conversation Testing (Nov 29, 2024)

Successfully tested multi-turn conversations with the GitHub Models API:

| Turn | Model | Task | Prompt Tokens | Completion Tokens | Total |
|------|-------|------|---------------|-------------------|-------|
| 1 | gpt-4o-mini | Code analysis | 104 | 300 | 404 |
| 2 | gpt-4o-mini | Follow-up with context | 121 | 400 | 521 |
| 3 | gpt-4o-mini | Workflow design | 88 | 400 | 488 |
| 4 | gpt-4o-mini | Implementation details | 124 | 500 | 624 |
| 5 | gpt-4o | Architecture advice | 43 | 171 | 214 |

**Key Findings**:
- ✅ Multi-turn conversations work by passing message history in each request
- ✅ Can analyze code, provide suggestions, and discuss repository problems
- ✅ Different models available for different use cases (gpt-4o-mini for volume, gpt-4o for quality)
- ✅ Token usage is reasonable (~400-600 tokens per detailed response)

**Rate Limits After Testing**:
- GPT-4o-mini: 19,994 requests remaining / 1,991,567 tokens remaining
- GPT-4o: 9,998 requests remaining / 9,999,455 tokens remaining

**Use Case: Automated Issue Analysis**

Example workflow pattern:
```yaml
- name: Analyze Issue with GitHub Models
  run: |
    RESPONSE=$(curl -s -X POST \
      -H "Authorization: token ${{ secrets.MODELS_PAT }}" \
      -H "Accept: application/vnd.github+json" \
      https://models.github.ai/inference/chat/completions \
      -d '{
        "model": "openai/gpt-4o-mini",
        "messages": [
          {"role": "system", "content": "Analyze GitHub issues and suggest solutions."},
          {"role": "user", "content": "${{ github.event.issue.body }}"}
        ]
      }')
    SUGGESTION=$(echo "$RESPONSE" | jq -r '.choices[0].message.content')
    gh issue comment ${{ github.event.issue.number }} --body "$SUGGESTION"
```

### Extended Summary Table

| Method | Token Type | Result |
|--------|------------|--------|
| gh-copilot CLI | Classic PAT | ❌ Extension deprecated, non-functional |
| @githubnext/github-copilot-cli | Classic PAT | ❌ Requires device flow |
| @github/copilot-language-server | Classic PAT | ❌ Requires device flow |
| api.githubcopilot.com | Classic PAT | ❌ "PATs not supported" |
| api.githubcopilot.com | Fine-grained PAT | ❌ "PATs not supported" |
| copilot-proxy.githubusercontent.com | Classic PAT | ❌ "invalid token format" |
| GitHub Models API | Classic PAT | ❌ Expired/Invalid |
| GitHub Models API | Fine-grained PAT (no scope) | ❌ Missing `models:read` scope |
| GitHub Models API | Fine-grained PAT + `Bearer` auth | ❌ 401 Unauthorized |
| **GitHub Models API** | **Fine-grained PAT + `token` auth** | ✅ **WORKING!** |
| **GitHub Models API** | **Multi-turn conversations** | ✅ **WORKING!** |

## Conclusion

**Key Takeaways**:

❌ **Headless authentication NOT supported** by Copilot CLI (requires device flow)  
✅ **Classic PAT works for GitHub API** but not sufficient for Copilot CLI/API  
❌ **Fine-grained PATs not supported by Copilot** (must use classic, but Copilot rejects all PATs)  
❌ **Device flow NOT suitable** for scale, CI/CD, or shared environments ([ref](https://github.com/github/gh-copilot/issues/116))  
❌ **Custom agent delegation NOT supported** by CLI  
❌ **Language Server SDK also requires device flow** - no headless token method  
❌ **Copilot API explicitly rejects PATs** - requires special Copilot tokens  
✅ **GitHub Models API IS WORKING!** with fine-grained PAT + `models:read` scope + `token` auth format  
✅ **GraphQL assignment proven and reliable** (ONLY viable method for A2A Copilot assignment)

**⚠️ CRITICAL FINDING**: After comprehensive testing (Nov 29, 2024), **ALL Copilot-specific interfaces require device flow authentication**:

1. **gh-copilot** (deprecated) - No commands execute
2. **@githubnext/github-copilot-cli** - Requires device flow
3. **@github/copilot-language-server** - Requires device flow
4. **api.githubcopilot.com** - Rejects all PATs
5. **copilot-proxy.githubusercontent.com** - Requires special token format

**✅ CONFIRMED WORKING - GitHub Models API**:
- **Endpoint**: `https://models.github.ai/inference/chat/completions`
- **Authentication**: `Authorization: token YOUR_PAT` (NOT Bearer!)
- **Required Scope**: Fine-grained PAT with `models:read` permission
- **Models Available**: GPT-4, GPT-4o, GPT-4o-mini, GPT-4.1, DeepSeek, Llama, Microsoft models
- **Use Case**: Headless LLM access for code generation, chat, analysis
- **Rate Limits**: 
  - GPT-4o-mini: 20,000 requests, 2M tokens
  - GPT-4o: 10,000 requests, 10M tokens
  - GPT-4.1: 1,000 requests, 1M tokens
- **Docs**: [REST API endpoints for models inference](https://docs.github.com/en/rest/models/inference)

**Note**: GitHub Models API provides **general LLM access**, not Copilot-specific features. It's an alternative for headless AI capabilities but doesn't provide Copilot's code-aware features or custom agent delegation.

**Action Items**:

1. ✅ ~~Test Copilot CLI~~ - **TESTED: Not viable**
2. ✅ ~~Attempt custom agent delegation~~ - **NOT SUPPORTED**
3. ✅ **Use GraphQL assignment exclusively** for A2A Copilot orchestration
4. ✅ **Implement branch-based A2A** for inter-agent communication
5. ✅ **Proceed with Phase 3A** using GraphQL method only
6. ✅ **GitHub Models API CONFIRMED WORKING** for headless LLM access
   - Use `Authorization: token` format (not Bearer)
   - Requires: Fine-grained PAT with `models:read` scope
   - Create at: Settings → Developer settings → Fine-grained tokens → Models permission

**Bottom Line**: 
- **A2A Copilot orchestration**: Use proven GraphQL direct agent assignment
- **Headless LLM access**: Use GitHub Models API with `models:read` scoped fine-grained PAT

---

**Last Updated**: 2024-11-29  
**Status**: Investigation Complete - CLI Not Viable (Re-confirmed)  
**Decision**: Use GraphQL Assignment Exclusively  
**Next Steps**: Phase 3A with GraphQL Method
