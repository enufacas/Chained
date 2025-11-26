# A2A Testing Workflows Guide

This guide explains the 4 test workflow options available for validating the A2A (Agent-to-Agent) Protocol implementation.

## 🚀 Quick Start

All test workflows now run **automatically on push** to the `copilot/implement-agent-orchestration` branch, making testing easier during development.

## 📋 Test Workflow Options

### 1. Quick Validation ⚡
**File:** `a2a-test-quick-validation.yml`  
**Duration:** ~2-3 minutes  
**Trigger:** Push to branch or `workflow_dispatch`

**What it tests:**
- ✅ Agent card generation (102 agents)
- ✅ Discovery service registration
- ✅ Basic import validation
- ✅ Port assignment consistency

**Best for:** Smoke testing, rapid feedback, PR validation

**Manual run:**
```bash
gh workflow run a2a-test-quick-validation.yml --ref copilot/implement-agent-orchestration
```

---

### 2. Tier 1 Integration 🔬
**File:** `a2a-test-tier1-integration.yml`  
**Duration:** ~5-7 minutes  
**Trigger:** Push to branch or `workflow_dispatch`

**What it tests:**
- ✅ Agent server startup (5 agents)
- ✅ Discovery service with live agents
- ✅ Client-server HTTP communication patterns
- ✅ Multi-agent orchestration simulation
- ✅ Performance benchmarks

**Best for:** Deep validation, performance testing

**Manual run:**
```bash
gh workflow run a2a-test-tier1-integration.yml --ref copilot/implement-agent-orchestration
```

---

### 3. Multi-Agent Collaboration Demo 🤝
**File:** `a2a-test-multi-agent-demo.yml`  
**Duration:** ~3-4 minutes  
**Trigger:** Push to branch or `workflow_dispatch`

**What it tests:**
- ✅ Real 3-agent collaboration scenario
- ✅ Task delegation patterns
- ✅ Result aggregation
- ✅ Agent coordination

**Scenario:** Design secure REST API with:
- **@engineer-master** - Designs API endpoints
- **@secure-specialist** - Reviews security implications
- **@organize-guru** - Structures code layout

**Best for:** Demonstrating multi-agent capabilities, end-to-end patterns

**Manual run:**
```bash
gh workflow run a2a-test-multi-agent-demo.yml --ref copilot/implement-agent-orchestration
```

---

### 4. Full Test Suite 🎯
**File:** `a2a-test-full-suite.yml`  
**Duration:** ~8-10 minutes  
**Trigger:** Push to branch, PR to main, or `workflow_dispatch`

**What it tests:**
- ✅ All unit tests (agent cards, discovery, tier1)
- ✅ Multi-agent collaboration
- ✅ Performance benchmarks
- ✅ Integration validation

**Best for:** Pre-merge validation, release testing, comprehensive coverage

**Manual run:**
```bash
gh workflow run a2a-test-full-suite.yml --ref copilot/implement-agent-orchestration
```

---

## 📊 Test Coverage Comparison

| Test Type | Quick | Tier 1 | Multi-Agent | Full Suite |
|-----------|-------|--------|-------------|------------|
| Agent Cards | ✅ | ✅ | ✅ | ✅ |
| Discovery | ✅ | ✅ | ✅ | ✅ |
| Server Startup | ❌ | ✅ | ❌ | ✅ |
| HTTP Communication | ❌ | ✅ | ❌ | ✅ |
| Multi-Agent Demo | ❌ | ❌ | ✅ | ✅ |
| Performance Bench | ❌ | ✅ | ❌ | ✅ |
| **Duration** | ~2min | ~6min | ~3min | ~10min |
| **Auto-runs on push** | ✅ | ✅ | ✅ | ✅ |

---

## 🎯 Recommended Testing Strategy

### During Development (PR Branch)
1. **Every push automatically triggers workflows** based on file changes
2. **Watch the Actions tab** for automatic test results
3. **Use Quick Validation** as your smoke test indicator
4. **Use Tier 1 Integration** for deeper validation of changes

### Manual Testing
If you need to run tests manually (e.g., without code changes):
```bash
# Quick feedback
gh workflow run a2a-test-quick-validation.yml --ref copilot/implement-agent-orchestration

# Deep validation
gh workflow run a2a-test-tier1-integration.yml --ref copilot/implement-agent-orchestration

# Demo capabilities
gh workflow run a2a-test-multi-agent-demo.yml --ref copilot/implement-agent-orchestration

# Comprehensive check
gh workflow run a2a-test-full-suite.yml --ref copilot/implement-agent-orchestration
```

### Pre-Merge
- **Full Test Suite** runs automatically on PR to main
- Review all test results before merging
- Ensure all tests pass

---

## 🔍 What You'll Learn

### From Quick Validation:
- Are all agent cards valid?
- Does discovery registration work?
- Any import or syntax errors?
- **Time saved:** Catches basic issues in 2 minutes

### From Tier 1 Integration:
- Can agents start as HTTP servers?
- Does discovery find live agents?
- What's the actual performance?
- Are there any port conflicts?
- **Time saved:** Deep validation without manual setup

### From Multi-Agent Demo:
- How do agents coordinate?
- What does task delegation look like?
- How are results aggregated?
- Real-world collaboration patterns
- **Time saved:** See end-to-end flow in action

### From Full Suite:
- Complete system health
- All integration points working
- Performance characteristics
- Production readiness
- **Time saved:** Comprehensive validation in one run

---

## 🐛 Troubleshooting

### Workflow not showing in Actions tab?
- Push a small change to trigger workflow (e.g., add comment to test file)
- Workflows only run when files in their `paths` filter change

### Workflow showing "skipped"?
- Check the `paths` filter in the workflow
- Your changes might not match the file patterns

### Test failures?
1. Check the specific step that failed in the Actions log
2. Common issues:
   - Missing dependencies (check requirements.txt)
   - Import errors (check Python path)
   - Agent definition changes (update tests)

### Manual workflow dispatch not working?
- This is expected for PR branches (GitHub limitation)
- Use push triggers instead (automatically configured)
- See: https://github.com/orgs/community/discussions/25746

---

## 📈 Performance Expectations

Based on Phase 2B testing:

```
Agent card generation:     ~1-2ms per card
Discovery registration:    ~5-8ms per agent
Setup overhead (5 agents): ~50ms total
Communication (localhost): <1ms latency
Tier 1 advantage:          1000x faster than Tier 2
```

---

## 🎉 Success Criteria

All tests should pass with these results:

- ✅ **Agent Cards:** 102/102 agents generate valid cards
- ✅ **Discovery:** All agents register and can be found
- ✅ **Server Creation:** No port conflicts (7 collisions acceptable)
- ✅ **Performance:** Setup < 10ms per agent, latency < 1ms
- ✅ **Multi-Agent:** 3-agent collaboration completes successfully

---

## 📚 Related Documentation

- `docs/A2A_PHASE_2B_TESTING_SUMMARY.md` - Testing results and findings
- `docs/A2A_GITHUB_RUNNERS_ARCHITECTURE.md` - Three-tier architecture
- `docs/A2A_INTEGRATION_README.md` - Quick start guide
- `tests/` - Test source files

---

**Note:** These workflows are configured with push triggers specifically for the PR branch to work around GitHub's workflow_dispatch limitation. After merge to main, they'll continue working with both push and manual dispatch triggers.
