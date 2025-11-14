# AI Agent Guide: Using PR Failure Intelligence

## 🎯 Purpose

This guide helps AI agents leverage the PR Failure Intelligence System to improve code generation quality by learning from past patterns and receiving proactive guidance.

## 🤖 For AI Agents: Quick Start

### Before Creating Any PR

**Step 1: Get Your Proactive Guidance**
```bash
python tools/pr-failure-intelligence.py \
  --proactive-guidance \
  --agent YOUR_AGENT_ID
```

**What you get**:
- Your current success rate
- Personalized best practices
- Patterns to avoid
- Key insights about your performance

**Example Output**:
```json
{
  "agent_id": "engineer-master",
  "success_rate": 0.80,
  "best_practices": [
    "Keep PRs small and focused (≤10 files)",
    "Always include tests with code changes",
    "Run linter and tests locally before creating PR",
    "Use conventional commit format (feat:, fix:, etc.)",
    "Update documentation when changing functionality"
  ],
  "avoid_patterns": [],
  "key_insights": [
    "Your success rate is excellent - maintain current practices"
  ],
  "profile_available": true
}
```

### Step 2: Assess Risk of Your Proposed Changes

Create a JSON file describing your changes:
```bash
cat > my_pr.json << 'EOF'
{
  "changed_files": 8,
  "files": [
    "src/authentication.py",
    "tests/test_authentication.py",
    "docs/authentication.md",
    "README.md"
  ],
  "title": "feat: add JWT authentication"
}
EOF
```

Run risk prediction:
```bash
python tools/pr-failure-intelligence.py \
  --predict-risk \
  --input my_pr.json
```

**Example Output**:
```json
{
  "overall_risk": 0.15,
  "risk_factors": {
    "small_size": 0.1,
    "has_tests": 0.1
  },
  "recommendations": [],
  "confidence": 0.6,
  "similar_failures": []
}
```

### Step 3: Interpret Risk Score

| Risk Score | Meaning | Action |
|-----------|---------|---------|
| 0.0 - 0.2 | ✅ Low Risk | Proceed with confidence |
| 0.2 - 0.4 | ⚠️ Medium Risk | Review recommendations |
| 0.4 - 0.6 | 🔶 High Risk | Apply all recommendations |
| 0.6 - 1.0 | 🚨 Very High Risk | Reconsider approach |

### Step 4: Apply Recommendations

**If you have recommendations**, address them before creating PR:

Example recommendations:
- "Add tests for the changes" → Create test files
- "Consider breaking this into smaller PRs" → Split into multiple PRs
- "Use conventional commit format in title" → Change title to "feat: ..."
- "Consider updating documentation" → Add/update docs

## 📋 Best Practices from Learned Patterns

### 1. PR Size (Critical)

**✅ DO**:
- Keep PRs ≤10 files changed (85-100% success rate)
- Split large changes into focused PRs
- Make incremental improvements

**❌ DON'T**:
- Create PRs with >20 files changed (20-40% success rate)
- Mix multiple features in one PR
- Make sweeping changes across codebase

**Example**:
```bash
# Bad: 25 files changed
- Refactor entire module
- Add new feature
- Fix multiple bugs
- Update documentation

# Good: 5 files changed per PR
PR 1: Refactor core logic (5 files)
PR 2: Add new feature (4 files)
PR 3: Fix critical bug (3 files)
PR 4: Update documentation (2 files)
```

### 2. Test Coverage (Essential)

**✅ DO**:
- Include tests with EVERY code change (+30% success rate)
- Aim for 1:2 test-to-code file ratio
- Test both happy path and edge cases

**❌ DON'T**:
- Submit code without tests (-60% success penalty)
- Add only minimal test coverage
- Skip testing "simple" changes

**Example**:
```
Good PR structure:
├── src/
│   └── authentication.py (150 lines)
├── tests/
│   └── test_authentication.py (200 lines)
└── docs/
    └── authentication.md
```

### 3. Documentation (Important)

**✅ DO**:
- Update README for new features (+20% success rate)
- Add inline documentation for complex logic
- Update API documentation

**❌ DON'T**:
- Submit feature PRs without docs
- Leave outdated documentation
- Skip docstrings

### 4. Naming Conventions (Professional)

**✅ DO**:
- Use conventional commit format (+15% success rate)
  - `feat:` for new features
  - `fix:` for bug fixes
  - `docs:` for documentation
  - `refactor:` for code restructuring
  - `test:` for test additions
  - `chore:` for maintenance

**❌ DON'T**:
- Use vague titles like "update code"
- Skip prefixes
- Use unclear descriptions

**Examples**:
```bash
✅ Good Titles:
- "feat: add JWT authentication to user service"
- "fix: resolve race condition in database connection"
- "docs: update API documentation for v2.0"
- "refactor: simplify error handling logic"
- "test: add integration tests for payment flow"

❌ Bad Titles:
- "update stuff"
- "changes"
- "fix bug"
- "improvements"
```

## 🎯 Decision Tree for PR Creation

```
Start: Ready to create PR?
│
├─ Is it ≤10 files?
│  ├─ Yes → ✅ Good
│  └─ No → 🔴 Split into smaller PRs
│
├─ Does it include tests?
│  ├─ Yes → ✅ Good
│  └─ No → 🔴 Add tests first
│
├─ Is documentation updated?
│  ├─ Yes → ✅ Good
│  └─ No → 🟡 Add documentation
│
├─ Using conventional commit format?
│  ├─ Yes → ✅ Good
│  └─ No → 🟡 Update title
│
└─ Run risk prediction
   ├─ Low risk (0.0-0.2) → ✅ Create PR
   ├─ Medium risk (0.2-0.4) → 🟡 Review and improve
   └─ High risk (>0.4) → 🔴 Address issues first
```

## 📊 Understanding Your Agent Profile

Your profile tracks:

### Success Rate
- **>80%**: Excellent - maintain current practices
- **60-80%**: Good - focus on consistency
- **40-60%**: Improving - follow best practices closely
- **<40%**: Needs work - review guidance carefully

### Common Failure Types
If your profile shows:
- **test_failure**: Add more comprehensive tests
- **review_rejection**: Follow code quality guidelines
- **merge_conflict**: Keep branch up to date
- **ci_failure**: Run CI checks locally first

### Improvement Trajectory
Track how you're improving over time:
- Upward trend → Keep doing what you're doing
- Flat trend → Try new approaches from best practices
- Downward trend → Review failures and adjust

## 🔄 Continuous Learning Workflow

### Weekly Cycle
1. **Sunday 00:30 UTC**: System analyzes all PRs
2. **Sunday morning**: New patterns and profiles available
3. **Throughout week**: Use guidance for new PRs
4. **Next Sunday**: See how you improved

### Per-PR Cycle
1. **Before coding**: Review your guidance
2. **During development**: Follow best practices
3. **Before creating PR**: Run risk prediction
4. **After PR closes**: Check if pattern was correct

## 🎓 Learning from Patterns

### Pattern: Small PRs
```
Pattern: "Small PRs (≤10 files) have 85-100% success rate"

Application:
- Before: 1 PR with 30 files → 40% success chance
- After: 3 PRs with 10 files each → 85% success chance

Result: 2.1x improvement in success rate
```

### Pattern: Test Coverage
```
Pattern: "PRs with tests have 30% higher success rate"

Application:
- Before: Code without tests → 50% success rate
- After: Code with tests → 80% success rate

Result: 1.6x improvement
```

### Pattern: Conventional Commits
```
Pattern: "Conventional commits have 15% higher success rate"

Application:
- Before: "update authentication" → 60% success rate
- After: "feat: add JWT authentication" → 75% success rate

Result: 1.25x improvement
```

## 🚨 Common Pitfalls to Avoid

### 1. Ignoring Risk Score
**Problem**: "My change is simple, I don't need to check"
**Reality**: Simple changes can have unexpected impacts
**Solution**: Always run risk prediction

### 2. Skipping Tests
**Problem**: "This change is too small for tests"
**Reality**: Small changes often break unexpectedly
**Solution**: Write tests for EVERY code change

### 3. Large PRs
**Problem**: "It's all related, should be one PR"
**Reality**: Large PRs are hard to review and often fail
**Solution**: Split into logical, small increments

### 4. Missing Documentation
**Problem**: "Code is self-documenting"
**Reality**: Others need context and examples
**Solution**: Update docs with code changes

## 💡 Pro Tips

### Tip 1: Start Small
Begin with the lowest-risk changes to build success history:
```
Week 1: Small bug fixes (≤5 files, with tests)
Week 2: Documentation improvements (≤3 files)
Week 3: Small features (≤10 files, with tests and docs)
Week 4+: Gradually increase complexity
```

### Tip 2: Use the Data
Check your profile regularly:
```bash
# Weekly check
python tools/pr-failure-intelligence.py \
  --proactive-guidance \
  --agent YOUR_AGENT_ID \
  | jq '.success_rate'
```

### Tip 3: Learn from Others
Study successful patterns from high-performing agents:
```bash
# View patterns
cat learnings/pr_intelligence/code_patterns.json | \
  jq '.patterns[] | select(.success_rate > 0.8)'
```

### Tip 4: Predict Before You Code
Run prediction on your planned changes BEFORE implementing:
```bash
# Plan your PR first
cat > plan.json << 'EOF'
{
  "changed_files": 12,
  "files": ["auth.py", "user.py", "..."],
  "title": "add authentication"
}
EOF

python tools/pr-failure-intelligence.py --predict-risk --input plan.json

# Adjust based on results
```

## 📈 Success Stories

### Agent A: From 45% to 85% Success Rate
**Before**:
- Large PRs (25+ files)
- No tests
- Vague titles

**After**:
- Small PRs (≤10 files)
- Comprehensive tests
- Conventional commits

**Result**: 1.9x improvement in 4 weeks

### Agent B: Maintained 90% Success Rate
**Strategy**:
- Always check guidance before coding
- Never skip risk prediction
- Follow best practices religiously
- Learn from every failure

**Result**: Consistent high performance

## 🎯 Your Action Plan

1. **Today**: Check your current profile
2. **This week**: Use guidance for all PRs
3. **Every PR**: Run risk prediction
4. **Weekly**: Review your improvement
5. **Monthly**: Analyze patterns and adjust

## 📚 Additional Resources

- **Full System Docs**: `tools/PR_FAILURE_INTELLIGENCE_README.md`
- **Pattern Analysis**: `learnings/pr_intelligence/code_patterns.json`
- **Your Profile**: `learnings/pr_intelligence/agent_profiles/YOUR_AGENT_ID.json`
- **Implementation Details**: `PR_FAILURE_INTELLIGENCE_IMPLEMENTATION.md`

---

**Remember**: The system learns from YOU. The more you use it and improve, the better the guidance becomes for all agents.

**Built by @engineer-master** - *Systematic learning for intelligent code generation*
