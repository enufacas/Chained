# A2A Tier 2 Transport: Branch-Based vs Issue-Based

## Overview

For **Tier 2 (GitHub-Mediated A2A)** cross-runner communication, we have two viable options:

1. **Issue-Based** (currently implemented)
2. **Branch-Based** (alternative approach)

Both work within GitHub Actions constraints. This document compares them and provides implementation for both.

## Comparison

### Issue-Based Transport (Current Implementation)

**Architecture:**
```
Agent A → Create Issue → GitHub
          ↓
    Workflow triggered
          ↓
Agent B executes → Post comment
          ↓
Agent A polls issue → Reads result
```

**Pros:**
- ✅ Native task tracking UI
- ✅ Discussion/comments built-in
- ✅ Searchable and discoverable
- ✅ Labels for status management
- ✅ Built-in notifications
- ✅ Audit trail visible to humans
- ✅ Can trigger workflows via labels

**Cons:**
- ❌ Clutters issue tracker
- ❌ Issues persist (need manual cleanup)
- ❌ Visible to all (may expose internal tasks)
- ❌ Cannot easily store binary artifacts

**API Usage:**
- Create task: 1 call
- Poll status: ~12 calls/minute
- Post result: 1-2 calls
- **Total**: ~15 calls per task = **~333 tasks/hour**

---

### Branch-Based Transport (Alternative)

**Architecture:**
```
Agent A → Create branch → Write task file → Push
          ↓
    Workflow triggered (push event)
          ↓
Agent B executes → Write result file → Push
          ↓
Agent A polls branch → Reads result → Deletes branch
```

**Pros:**
- ✅ Cleaner (no issue clutter)
- ✅ Git-native (familiar tools)
- ✅ Easy cleanup (delete branch)
- ✅ Supports file-based artifacts
- ✅ Can store binary data
- ✅ Less visible (unprotected branch)
- ✅ Atomic operations via git

**Cons:**
- ❌ No native task tracking UI
- ❌ Manual status management
- ❌ Less discoverable (hidden in branches)
- ❌ No built-in notifications
- ❌ Requires branch protection bypass
- ❌ More complex cleanup

**API Usage:**
- Create branch: 1 call
- Write task: 1 call
- Poll status: ~12 calls/minute
- Read result: 1 call
- Delete branch: 1 call
- **Total**: ~16 calls per task = **~312 tasks/hour**

---

## Detailed Analysis

### Branch Structure

```
a2a-tasks/
├── task-{uuid}/
│   ├── task.json          # Input task data
│   ├── status.json        # Status (submitted, working, completed)
│   ├── result.json        # Output result
│   └── artifacts/         # Optional binary artifacts
│       └── file1.bin
```

### Workflow Integration

**Branch-Based Workflow Trigger:**
```yaml
on:
  push:
    branches:
      - 'a2a-tasks/**'
    paths:
      - '**/task.json'
```

**Issue-Based Workflow Trigger:**
```yaml
on:
  issues:
    types: [opened, labeled]
  workflow_dispatch:
```

### Security Considerations

**Branch-Based:**
- Requires write access to repository
- Unprotected branches can be created/deleted
- Task data visible in git history (until branch deleted)
- Can use `.gitattributes` to mark files as non-diffable

**Issue-Based:**
- Requires issue creation permission
- Issues are always public (in public repos)
- Issues create permanent record (even if closed)
- Can use private repos for sensitive tasks

### Performance

**Branch-Based:**
- **Pros**: Git operations are atomic
- **Pros**: Can batch multiple files in single commit
- **Cons**: Git history overhead
- **Cons**: Branch listing can be slow with many branches

**Issue-Based:**
- **Pros**: Lightweight (no git operations)
- **Pros**: Native indexing and search
- **Cons**: Issue list can get cluttered
- **Cons**: No atomic multi-object updates

### Use Cases

**Branch-Based is Better For:**
- 🎯 Tasks that generate artifacts (files, binaries)
- 🎯 Need to avoid issue tracker clutter
- 🎯 Want automatic cleanup
- 🎯 Private/internal tasks
- 🎯 Large result payloads

**Issue-Based is Better For:**
- 🎯 Need visibility and tracking
- 🎯 Want discussion/comments
- 🎯 Need notifications
- 🎯 Human-in-the-loop approval
- 🎯 Audit requirements

---

## Implementation Comparison

### API Calls Breakdown

**Issue-Based:**
```python
# Create task
POST /repos/{owner}/{repo}/issues                    # 1 call

# Poll for completion (5-second intervals)
GET /repos/{owner}/{repo}/issues/{number}            # ~720 calls/hour

# Read result
GET /repos/{owner}/{repo}/issues/{number}/comments   # 1 call

# Total per task: ~15 API calls
# Capacity: 5000/15 = ~333 tasks/hour
```

**Branch-Based:**
```python
# Create branch
POST /repos/{owner}/{repo}/git/refs                  # 1 call

# Write task
PUT /repos/{owner}/{repo}/contents/{path}            # 1 call

# Poll for completion (5-second intervals)
GET /repos/{owner}/{repo}/contents/{path}            # ~720 calls/hour

# Read result
GET /repos/{owner}/{repo}/contents/{path}            # 1 call

# Delete branch
DELETE /repos/{owner}/{repo}/git/refs/{ref}          # 1 call

# Total per task: ~16 API calls
# Capacity: 5000/16 = ~312 tasks/hour
```

**Verdict:** Similar API usage, both viable within rate limits.

---

## Hybrid Approach (Recommended)

**Use both transports based on task requirements:**

```python
class A2ATransportFactory:
    @staticmethod
    def create(transport_type: str, **kwargs):
        if transport_type == "issue":
            return GitHubIssueTransport(**kwargs)
        elif transport_type == "branch":
            return GitHubBranchTransport(**kwargs)
        else:
            raise ValueError(f"Unknown transport: {transport_type}")

# Usage
if task.needs_visibility:
    transport = A2ATransportFactory.create("issue", ...)
else:
    transport = A2ATransportFactory.create("branch", ...)
```

**Decision Matrix:**

| Requirement | Use Issue-Based | Use Branch-Based |
|-------------|----------------|------------------|
| Need tracking UI | ✅ | ❌ |
| Need comments/discussion | ✅ | ❌ |
| Avoid clutter | ❌ | ✅ |
| Binary artifacts | ❌ | ✅ |
| Automatic cleanup | ❌ | ✅ |
| Notifications | ✅ | ❌ |
| Private tasks | ⚠️ | ✅ |

---

## Branch Protection Considerations

### Unprotected Branch Strategy

**Default branch protection rules:**
```yaml
# .github/branch-protection.yml
# Protected branches: main, develop, release/*
# Unprotected: a2a-tasks/* (ephemeral task branches)
```

**Benefits:**
- Agents can create/delete branches freely
- No admin intervention needed
- Tasks are isolated from main codebase

**Risks:**
- Could be abused if tokens are leaked
- Need to monitor branch creation rate

**Mitigation:**
```python
# Rate limiting in transport layer
class BranchTaskRateLimiter:
    max_branches_per_hour = 100
    
    def check_rate_limit(self):
        recent_branches = self.count_recent_branches(hours=1)
        if recent_branches >= self.max_branches_per_hour:
            raise RateLimitError("Too many task branches")
```

---

## Implementation Plan

### Phase 1: Add Branch Transport (Parallel to Issues)
1. Create `tools/a2a/github_branch_transport.py`
2. Implement `GitHubBranchTransport` class
3. Update workflow to support both triggers
4. Add tests

### Phase 2: Hybrid Strategy
1. Add transport factory
2. Update client to choose transport
3. Add configuration for default transport
4. Document use cases

### Phase 3: Optimization
1. Webhook support (replace polling)
2. Branch caching strategy
3. Automatic cleanup of old branches

---

## Recommendation

**Implement both, default to issue-based:**

1. **Keep issue-based as default** for:
   - Better UX (tracking, comments, search)
   - Human-friendly audit trail
   - Native GitHub integration

2. **Add branch-based as option** for:
   - Tasks with artifacts
   - High-volume scenarios
   - Private/internal tasks

3. **Let users choose** via configuration:
   ```python
   A2A_TRANSPORT = os.getenv("A2A_TRANSPORT", "issue")  # or "branch"
   ```

---

## Next Steps

1. ✅ Document both approaches (this file)
2. ⬜ Implement `GitHubBranchTransport`
3. ⬜ Add transport factory pattern
4. ⬜ Update workflows to support both
5. ⬜ Add configuration options
6. ⬜ Performance testing
7. ⬜ User documentation

---

**Conclusion:** Both approaches are viable and complement each other. Branch-based transport is an excellent alternative that avoids issue clutter while maintaining GitHub Actions compatibility.
