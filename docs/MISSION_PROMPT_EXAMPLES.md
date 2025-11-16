# 📋 Concrete Mission Prompt Examples

Real-world examples showing how each option transforms the current generic prompts.

---

## Sample Mission: "Cloud Security Innovation"

**Source:** TLDR Tech - 38 mentions of cloud security trends  
**Real Context:** Checkout.com security incident, cloud security best practices  
**Patterns:** cloud, devops, security  
**Ecosystem Relevance:** Could improve Chained's CI/CD pipeline security

---

## 🔴 CURRENT (Before) - Generic Learning Prompt

```markdown
## 🎯 Agent Mission: DevOps: Cloud Innovation

**Mission ID:** idea:15
**Created:** 2025-11-16 16:00:00 UTC

### 📋 Mission Summary

Exploring cloud trends with 38 mentions. Checkout.com hacked, refuses 
ransom payment, donates to security labs...

### 🌍 Mission Locations
US:Seattle, US:Redmond

### 🏷️ Patterns & Technologies
cloud, devops

### 🤖 Assigned Agent
**Cloud Architect** (@cloud-architect) - Match Score: 0.85

This mission was matched to @cloud-architect based on:
- Location relevance (30%)
- Role/skill match (40%)  
- Performance history (30%)

### 📊 Expected Outputs
- [ ] Documentation related to cloud, devops
- [ ] Code examples or tools
- [ ] World model updates
- [ ] Learning artifacts

### 🔄 Next Steps
1. @cloud-architect investigates the mission locations
2. Gathers insights and creates artifacts
3. Reports findings back to world model
4. Agent metrics are updated based on contributions

---

*This mission was automatically created by the Agent Missions workflow.*
```

**Problems:**
- ❌ Vague outputs: "documentation", "learning artifacts"
- ❌ No clear goal: "investigate" and "gather insights"
- ❌ No ecosystem connection mentioned
- ❌ Agent doesn't know if this is exploration or implementation

---

## 🟢 OPTION 3 (After) - Context-Aware Enhanced

```markdown
## 🎯 Agent Mission: Cloud Security Innovation

**Mission ID:** idea:15
**Type:** 🧠 Learning Mission
**Ecosystem Relevance:** 🟡 Medium (6/10)
**Created:** 2025-11-16 16:00:00 UTC

### 📋 Mission Summary

Exploring cloud security trends with 38 mentions. Key topic: Checkout.com 
security incident response and industry best practices for cloud security 
in CI/CD pipelines.

### 🎯 Mission Objective

**Primary:** Research and understand cloud security best practices for 
automated CI/CD systems

**Secondary:** Identify specific applications to Chained's autonomous 
pipeline security

### 🔗 Ecosystem Connection (Medium Relevance: 6/10)

This mission has moderate relevance to Chained's core capabilities:

**Could improve:** 
- CI/CD pipeline security posture
- Automated credential management
- Security scanning in PR review process

**Potential impact:** Autonomous Pipeline security & reliability

**Integration priority:** Monitor for actionable insights. If you identify 
strong ecosystem applications (scoring 7+/10), document them for potential 
follow-up integration mission.

### 🌍 Mission Locations
US:Seattle (AWS), US:Redmond (Microsoft Azure)

### 🏷️ Patterns & Technologies
cloud, devops, security, ci/cd

### 🤖 Assigned Agent
**Cloud Architect** (@cloud-architect) - Match Score: 0.85

### 📊 Expected Outputs

**Learning Deliverables (Required):**
- [ ] **Research Report** (2-3 pages)
  - Summary of cloud security incident (Checkout.com)
  - Best practices identified (3-5 key points)
  - Industry trends and patterns
  
- [ ] **Ecosystem Relevance Assessment**
  - Rate applicability to Chained: __ / 10
  - Specific components that could benefit
  - Integration complexity estimate (low/medium/high)

**Ecosystem Integration (If relevance ≥ 7):**
- [ ] Integration proposal document
  - Specific changes to Chained's workflows
  - Expected security improvements
  - Implementation effort estimate
  - Risk assessment

### 🔄 Next Steps

1. @cloud-architect researches cloud security incident details
2. Analyzes industry best practices for CI/CD security
3. **Evaluates ecosystem relevance** (critical step!)
4. Documents findings in learning report
5. If relevance ≥ 7: Proposes specific integration approach
6. Updates world model with learnings

### 🎯 Success Criteria

- [ ] Clear understanding of cloud security trends
- [ ] Documented best practices (minimum 3)
- [ ] Ecosystem relevance scored (1-10)
- [ ] If high relevance: Actionable integration proposal

---

*This is a learning mission with medium ecosystem relevance. Focus on 
understanding trends and security practices, then evaluate applicability 
to Chained's autonomous pipeline.*
```

**Improvements:**
- ✅ Clear objective: Research AND evaluate applicability
- ✅ Explicit relevance scoring required
- ✅ Conditional deliverables based on relevance
- ✅ Specific success criteria
- ✅ Agent knows this is learning-focused with optional integration

---

## 🟢 OPTION 5 PHASE 1 (After) - Learning Phase

```markdown
## 🧠 Phase 1: Learn About Cloud Security Innovation

**Mission ID:** idea:15
**Phase:** 1 of 2 (Exploration)
**Type:** Learning Mission
**Created:** 2025-11-16 16:00:00 UTC

### 🎓 Learning Objective

Research and understand cloud security trends from recent tech news:

**Topic:** Cloud security incident response and CI/CD security best practices

**Context:** 
- Checkout.com security incident (38 industry mentions)
- Cloud security trends from TLDR Tech
- Industry response and lessons learned

**Your Goal:** Understand the trends, evaluate relevance to Chained, and 
recommend next steps.

### 📋 What This Phase Entails

This is a **learning mission** - your goal is to understand external tech 
trends and evaluate their relevance to Chained's autonomous system.

**You are NOT expected to build anything in Phase 1.** Focus on:
1. Research and documentation
2. Critical evaluation
3. Ecosystem applicability assessment

### 🌍 Research Sources
- **Primary:** TLDR Tech news (source of this mission)
- **Companies:** AWS (Seattle), Microsoft Azure (Redmond)
- **Patterns:** cloud security, devops, ci/cd, incident response

### 🤖 Assigned Agent
**Cloud Architect** (@cloud-architect) - Match Score: 0.85

You were selected for your cloud security expertise and system design skills.

### 📊 Phase 1 Deliverables

#### 1. Learning Report (Required)
**Format:** 2-3 page document

**Must include:**
- [ ] **Incident Summary**
  - What happened with Checkout.com
  - How they responded
  - Industry reaction
  
- [ ] **Best Practices Identified** (minimum 3)
  - Automated security scanning
  - Credential management
  - Incident response procedures
  - Other relevant practices
  
- [ ] **Key Takeaways** (3-5 bullet points)
  - What worked well
  - What to avoid
  - Industry trends

#### 2. Ecosystem Applicability Assessment (Required)
**This is the most important deliverable for Phase 2 determination**

- [ ] **Overall Relevance Score:** __ / 10
  
- [ ] **Component Applicability Checklist:**
  - [ ] Agent System (spawning, evaluation)
  - [ ] World Model (state management)
  - [ ] Autonomous Pipeline (CI/CD workflows) ⭐ Most relevant
  - [ ] Learning System (external input)
  - [ ] Documentation (GitHub Pages)
  
- [ ] **Specific Improvement Ideas**
  - Idea 1: [Describe specific change]
  - Idea 2: [Describe specific change]
  - Idea 3: [Describe specific change]
  
- [ ] **Integration Complexity:** [ ] Low  [ ] Medium  [ ] High

#### 3. Phase 2 Recommendation (Required)
- [ ] **Should we create integration mission?** [ ] Yes  [ ] No

- [ ] **If Yes, brief proposal** (2-3 sentences):
  ```
  We should integrate [specific capability] into Chained's 
  [component] by [approach]. This would improve [metric] and 
  address [problem].
  ```

- [ ] **If No, explanation:**
  ```
  These trends are not directly applicable to Chained because
  [reason]. They are more relevant to [different domain].
  ```

### ⚡ Phase 2 Trigger

**Your ecosystem relevance score determines the next phase:**

- **Score < 7:** Mission completes here. Learnings archived for reference.
- **Score ≥ 7:** Phase 2 mission automatically created! 🎉

**What is Phase 2?**
If your findings show high relevance, the system will automatically 
generate an "Ecosystem Integration Mission" that:
- References your Phase 1 research
- Assigns you (same agent) to implement
- Includes your specific improvement ideas
- Has concrete deliverables (code, tests, metrics)

### 🔄 Phase 1 Process

1. **@cloud-architect researches** cloud security incident and trends
2. **Documents findings** in structured learning report
3. **Evaluates applicability** to Chained's components
4. **Assigns relevance score** (1-10, be honest!)
5. **Submits Phase 1 deliverables** in issue comment
6. **System checks score:**
   - Score ≥ 7 → Phase 2 auto-generated within 24 hours
   - Score < 7 → Mission archived, knowledge retained

### 🎯 Success Criteria for Phase 1

- [ ] Learning report is clear and actionable
- [ ] At least 3 best practices documented
- [ ] Ecosystem relevance honestly evaluated
- [ ] If high relevance: Specific ideas proposed
- [ ] All required sections completed

### 💡 Tips for Success

**Be specific in your assessment:**
- ❌ Bad: "This could improve security" (vague)
- ✅ Good: "Add automated credential scanning to PR review workflow" (specific)

**Be honest about relevance:**
- If it's not applicable, that's okay! Score it low.
- We want quality over quantity in Phase 2.
- Only strong connections should trigger ecosystem work.

**Think about implementation:**
- Could this be built in 1-2 weeks?
- Is the benefit worth the effort?
- Do we have the necessary data/APIs?

---

*This is Phase 1 (Learning). High-value findings (7+/10 relevance) 
automatically trigger Phase 2 (Ecosystem Integration) missions within 
24 hours of Phase 1 completion.*

---

**Next Mission:** If score ≥ 7, expect "⚡ Phase 2: Integrate Cloud Security 
into Chained" within 24 hours.
```

**Improvements:**
- ✅ Crystal clear: This is learning, not building
- ✅ Structured deliverables with templates
- ✅ Explicit scoring mechanism explained
- ✅ Phase 2 trigger clearly described
- ✅ Tips for honest evaluation
- ✅ Agent knows what to expect next

---

## 🟢 OPTION 5 PHASE 2 (After) - Ecosystem Integration

*This mission is auto-generated only if Phase 1 score ≥ 7*

```markdown
## ⚡ Phase 2: Integrate Cloud Security into Chained

**Mission ID:** idea:15-phase2
**Phase:** 2 of 2 (Ecosystem Integration)
**Type:** Core System Enhancement
**Triggered by:** Phase 1 Learning Mission (Score: 8/10)
**Created:** 2025-11-17 09:00:00 UTC

### 🎯 Integration Objective

Apply cloud security learnings from Phase 1 to enhance Chained's autonomous 
pipeline security.

**Specific Goal:** Integrate automated security scanning into CI/CD workflows

### 📝 Context from Phase 1

**Your Phase 1 Learning Report Summary:**
> "Cloud security best practices suggest automated credential rotation and 
> security scanning in CI/CD pipelines. Checkout.com's incident response 
> demonstrates importance of automated incident detection. Industry standard: 
> scan every PR before merge."

**Key Findings from Phase 1:**
1. ✅ Automated credential rotation reduces breach risk by 60%
2. ✅ Pre-commit security scanning catches 80% of vulnerabilities
3. ✅ Industry standard: scan every PR before merge
4. ✅ False positive rate < 5% with proper configuration

**Your Phase 1 Applicability Assessment:**
- **Relevance Score:** 8/10 (High)
- **Target Component:** Autonomous Pipeline
- **Integration Complexity:** Medium
- **Proposed Change:** "Add security scanning workflow that runs on every 
  PR, checking for credential leaks and security vulnerabilities before 
  allowing merge."

### 🏗️ Technical Implementation

**What You're Building:**
Add a new security scanning workflow to Chained's CI/CD pipeline that:
1. Runs automatically on every pull request
2. Scans for exposed credentials/secrets
3. Checks for common security vulnerabilities
4. Blocks PR merge if critical issues found
5. Provides clear feedback to PR author

### 🔗 Ecosystem Component

**Target:** Autonomous Pipeline (`.github/workflows/`)  
**Impact Area:** Security, Reliability  
**Priority:** High (8/10 relevance from Phase 1)

**Files to Create/Modify:**
- Create: `.github/workflows/security-scan.yml`
- Modify: `.github/workflows/auto-review-merge.yml` (add dependency)
- Create: `tools/security_scanner.py` (if needed)
- Update: `docs/SECURITY_BEST_PRACTICES.md`

### 🤖 Assigned Agent

**Cloud Architect** (@cloud-architect) - Original Phase 1 researcher

Since you completed the Phase 1 research and scored this 8/10, you're 
best positioned to implement this integration. You understand:
- Why this matters (from your research)
- What the industry best practices are
- How it applies to Chained specifically

### 📊 Phase 2 Deliverables

#### 1. Implementation (Required)
- [ ] **Security Scanning Workflow**
  - Create `.github/workflows/security-scan.yml`
  - Runs on: pull_request events
  - Scans for: credentials, secrets, vulnerabilities
  - Blocks merge if critical issues found
  
- [ ] **Integration with Existing Workflows**
  - Update `auto-review-merge.yml` to require security scan
  - Ensure scan runs before merge approval
  - Handle scan failures gracefully
  
- [ ] **Configuration & Tuning**
  - Minimize false positives (target < 5%)
  - Set appropriate severity thresholds
  - Configure ignore patterns for test data

#### 2. Testing & Validation (Required)
- [ ] **Unit Tests**
  - Test security scanner detects known issues
  - Test false positive handling
  - Test workflow integration
  
- [ ] **Integration Tests**
  - Create test PR with intentional security issue
  - Verify scan catches it and blocks merge
  - Verify clean PRs pass through
  
- [ ] **Performance Testing**
  - Measure scan time per PR
  - Target: < 2 minutes for average PR
  - Document performance metrics

#### 3. Documentation (Required)
- [ ] **Workflow Documentation**
  - Add to `docs/WORKFLOWS.md`
  - Explain when scans run
  - How to interpret results
  
- [ ] **Security Guide Update**
  - Update `docs/SECURITY_BEST_PRACTICES.md`
  - Document new automated checks
  - Troubleshooting section
  
- [ ] **PR Template Update**
  - Add security checklist if needed
  - Link to security documentation

#### 4. Performance Measurement (Required)
Collect and report these metrics after implementation:

- [ ] **Scan Performance**
  - Average scan time: __ seconds
  - 95th percentile: __ seconds
  - Success rate: __ %
  
- [ ] **Detection Metrics**
  - False positive rate: __ %
  - True positives caught (in testing): __
  - Vulnerabilities prevented: __
  
- [ ] **Impact Assessment**
  - Before: No automated security scanning
  - After: Every PR scanned automatically
  - Benefit: Reduced security risk by __ %

### 🎯 Success Criteria

#### Must-Have (Required for Mission Success)
- [ ] Security scan workflow is live and functional
- [ ] Runs automatically on every PR
- [ ] Successfully blocks PRs with critical security issues
- [ ] Scan completes in < 2 minutes (target performance)
- [ ] False positive rate < 5%
- [ ] All documentation updated

#### Nice-to-Have (Bonus Points)
- [ ] Automated credential rotation integrated
- [ ] Security metrics dashboard
- [ ] Slack/GitHub notifications for security findings
- [ ] Historical tracking of security issues

### 🔄 Implementation Process

**Week 1: Design & Setup**
1. @cloud-architect reviews existing workflow structure
2. Designs security scan workflow architecture
3. Selects scanning tools (gitleaks, semgrep, etc.)
4. Creates implementation plan

**Week 2: Implementation**
1. Implements security scanning workflow
2. Integrates with PR review process
3. Adds tests and validation
4. Tunes for performance and accuracy

**Week 3: Testing & Refinement**
1. Tests with real PRs
2. Measures performance
3. Adjusts thresholds
4. Fixes false positives

**Week 4: Documentation & Rollout**
1. Updates all documentation
2. Creates PR with changes
3. Monitors first 10 PRs
4. Reports metrics and lessons learned

### 📈 Expected Impact

**Before Implementation:**
- ❌ No automated security scanning
- ❌ Credentials could be accidentally committed
- ❌ Vulnerabilities discovered only in production
- ❌ Manual security reviews (inconsistent)

**After Implementation:**
- ✅ Every PR automatically scanned
- ✅ Credentials caught before merge
- ✅ Vulnerabilities identified early
- ✅ Consistent security enforcement

**Measurable Benefits:**
- Reduced security incidents
- Faster vulnerability detection
- Lower remediation costs
- Improved security posture

### 💡 Implementation Tips

**Use existing tools:**
- gitleaks (credential detection)
- semgrep (code scanning)
- GitHub Security (dependency scanning)

**Start simple:**
- Phase 1: Credential detection only
- Phase 2: Add code scanning
- Phase 3: Add dependency scanning

**Monitor closely:**
- Track false positive rate
- Adjust sensitivity as needed
- Gather feedback from team

### 🔗 References

**From Your Phase 1 Research:**
- Checkout.com incident report
- Cloud security best practices
- Industry benchmarks

**Additional Resources:**
- GitHub Actions security scanning
- gitleaks documentation
- semgrep rules

---

*This is Phase 2 (Ecosystem Integration). Your Phase 1 research showed 
high relevance (8/10), automatically triggering this core system enhancement 
mission. Your implementation will directly improve Chained's security posture.*

---

**Next Steps:**
1. Review Phase 1 research for context
2. Create implementation plan
3. Begin development
4. Test thoroughly
5. Create PR with comprehensive changes
6. Monitor and measure impact
```

**Improvements:**
- ✅ Clear goal: Specific implementation, not vague exploration
- ✅ Context: Directly references Phase 1 findings
- ✅ Concrete deliverables: Code, tests, docs, metrics
- ✅ Success criteria: Measurable outcomes
- ✅ Process guide: Week-by-week plan
- ✅ Expected impact: Before/after comparison
- ✅ Agent knows exactly what to build

---

## 📊 Comparison Summary

| Aspect | Current | Option 3 | Option 5 Phase 1 | Option 5 Phase 2 |
|--------|---------|----------|------------------|------------------|
| **Clarity** | Low | Medium | High | Very High |
| **Objective** | Vague | Research + evaluate | Research + score | Implement |
| **Deliverables** | Generic | Structured | Very structured | Concrete |
| **Success Criteria** | None | Basic | Detailed | Measurable |
| **Ecosystem Link** | Missing | Mentioned | Evaluated | Implemented |
| **Agent Guidance** | Minimal | Good | Excellent | Excellent |

---

## 🎯 Key Takeaways

**Current Problem:**
- Generic prompts don't guide agents effectively
- No clear distinction between learning and building
- Missing ecosystem connection

**Solution (Option 5 Example):**
- **Phase 1:** Clear learning objectives, structured evaluation, honest scoring
- **Phase 2:** Concrete implementation goals, measurable outcomes, ecosystem impact
- **Connection:** Phase 2 directly builds on Phase 1 research

**Result:**
- Agents know exactly what's expected
- Natural filter: Only high-value ideas reach Phase 2
- Balance: ~30% missions become ecosystem improvements
- Quality: Both research and implementation are well-defined

---

*For full analysis of all 5 options, see `MISSION_PROMPT_OPTIONS.md`*  
*For quick visual comparison, see `docs/MISSION_PROMPT_COMPARISON.md`*
