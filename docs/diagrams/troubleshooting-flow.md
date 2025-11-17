# 🔧 Troubleshooting Flow Diagram

This diagram shows the systematic approach to troubleshooting issues in the Chained autonomous AI ecosystem.

## Complete Troubleshooting Decision Tree

```mermaid
graph TD
    Start[🚨 Problem Detected] --> Type{What's the symptom?}
    
    Type -->|Nothing works| Critical[🔴 Critical State]
    Type -->|Some failures| Degraded[🟡 Degraded State]
    Type -->|Specific issue| Targeted[🎯 Targeted Investigation]
    
    Critical --> Emergency[Run Emergency Diagnostic]
    Emergency --> CheckGitHub{GitHub Status OK?}
    CheckGitHub -->|No| Wait[Wait for GitHub]
    CheckGitHub -->|Yes| Kickstart[Run kickoff-system.sh]
    
    Degraded --> HealthCheck[Run quick-health-check.sh]
    HealthCheck --> Analyze{What's failing?}
    
    Targeted --> IssueType{Issue Type?}
    
    Analyze -->|Workflows| WorkflowIssues
    Analyze -->|Copilot| CopilotIssues  
    Analyze -->|Agents| AgentIssues
    Analyze -->|Pages| PagesIssues
    
    IssueType -->|Copilot| CopilotIssues
    IssueType -->|Workflow| WorkflowIssues
    IssueType -->|Agent| AgentIssues
    IssueType -->|Pages| PagesIssues
    IssueType -->|Learning| LearningIssues
    IssueType -->|Performance| PerfIssues
    
    CopilotIssues[🤖 Copilot Issues] --> CopilotCheck{Check COPILOT_PAT}
    CopilotCheck -->|Missing| AddPAT[Add PAT Secret]
    CopilotCheck -->|Present| IssueQuality{Issue has context?}
    IssueQuality -->|No| ImproveIssue[Add detailed context]
    IssueQuality -->|Yes| CheckService{Service status?}
    CheckService -->|Down| WaitService[Wait for Copilot]
    CheckService -->|Up| CheckRepo{Repo size OK?}
    CheckRepo -->|Too large| AddIgnore[Add .copilotignore]
    CheckRepo -->|OK| InvestigateMore[Check logs]
    
    WorkflowIssues[⚙️ Workflow Issues] --> WFType{Failure type?}
    WFType -->|Not running| Schedule[Check schedule/cron]
    WFType -->|Permissions| AddPerms[Add permissions]
    WFType -->|Failures| CheckLogs[Review logs]
    Schedule --> EnableWF[Enable workflow]
    EnableWF --> TestManual[Test manually]
    
    AgentIssues[🤖 Agent Issues] --> AgentCheck{Check registry.json}
    AgentCheck -->|Invalid JSON| RestoreRegistry[Restore from git]
    AgentCheck -->|Valid| ScoreCheck{Zero scores?}
    ScoreCheck -->|Yes| AgentAge{Agent age < 3h?}
    AgentAge -->|Yes| WaitEval[Wait for evaluator]
    AgentAge -->|No| CheckEval[Check evaluator workflow]
    
    PagesIssues[🌐 Pages Issues] --> PagesEnabled{Pages enabled?}
    PagesEnabled -->|No| EnablePages[Enable in Settings]
    PagesEnabled -->|Yes| DataFresh{Data files fresh?}
    DataFresh -->|No| UpdateData[Run timeline-updater]
    DataFresh -->|Yes| ClearCache[Hard refresh browser]
    
    LearningIssues[🧠 Learning Issues] --> APICheck{API rate limit?}
    APICheck -->|Yes| ReduceFreq[Reduce workflow frequency]
    APICheck -->|No| PermCheck{Permissions OK?}
    PermCheck -->|No| AddWritePerms[Add contents: write]
    PermCheck -->|Yes| TestAPI[Test API endpoint]
    
    PerfIssues[📊 Performance Issues] --> PerfType{Issue type?}
    PerfType -->|Slow workflows| OptimizeWF[Optimize workflow]
    PerfType -->|High failures| AnalyzePatterns[Analyze failure patterns]
    PerfType -->|Rate limits| ReduceLoad[Reduce API calls]
    
    %% Resolution paths
    AddPAT --> Verify[Verify & Test]
    ImproveIssue --> Verify
    AddIgnore --> Verify
    TestManual --> Verify
    RestoreRegistry --> Verify
    UpdateData --> Verify
    ReduceFreq --> Verify
    OptimizeWF --> Verify
    
    Verify --> Success{Fixed?}
    Success -->|Yes| Document[📝 Document solution]
    Success -->|No| AdvancedDiag[Use advanced diagnostics]
    
    Document --> Complete[✅ Complete]
    AdvancedDiag --> Timeline[Timeline analysis]
    Timeline --> StateReconstruct[State reconstruction]
    StateReconstruct --> GetHelp[Create support issue]
    
    style Start fill:#ff6b6b
    style Critical fill:#ff6b6b
    style Degraded fill:#ffd93d
    style Complete fill:#6bcf7f
    style Document fill:#6bcf7f
```

## Quick Decision Matrix

Use this matrix for fast issue categorization:

```mermaid
graph LR
    subgraph "Symptom Categories"
        S1[Nothing works]
        S2[Copilot silent]
        S3[Workflows fail]
        S4[Agents zero score]
        S5[Pages stale]
        S6[No learning files]
    end
    
    subgraph "First Action"
        A1[Emergency diagnostic]
        A2[Check COPILOT_PAT]
        A3[Check logs]
        A4[Wait for evaluator]
        A5[Trigger update]
        A6[Test APIs]
    end
    
    S1 --> A1
    S2 --> A2
    S3 --> A3
    S4 --> A4
    S5 --> A5
    S6 --> A6
    
    style A1 fill:#ff6b6b
    style A2 fill:#4ecdc4
    style A3 fill:#ffd93d
    style A4 fill:#95e1d3
    style A5 fill:#a8e6cf
    style A6 fill:#feca57
```

## Diagnostic Tool Selection

Choose the right tool for your investigation:

```mermaid
graph TD
    Problem[🔍 Need to diagnose] --> TimeAvail{Time available?}
    
    TimeAvail -->|5 minutes| QuickCheck[quick-health-check.sh]
    TimeAvail -->|15 minutes| FullCheck[check-status.sh]
    TimeAvail -->|30+ minutes| DeepDive[Advanced diagnostics]
    
    QuickCheck --> QuickResult{Result?}
    QuickResult -->|All green| NoIssue[No immediate issues]
    QuickResult -->|Warnings| InvestigateWarn[Investigate warnings]
    QuickResult -->|Errors| FullCheck
    
    FullCheck --> FullResult{Result?}
    FullResult -->|Clear issue| FollowGuide[Use troubleshooting guide]
    FullResult -->|Complex| DeepDive
    
    DeepDive --> Choose{Analysis type?}
    Choose -->|When?| Timeline[Timeline analysis]
    Choose -->|What?| State[State reconstruction]
    Choose -->|Why?| Patterns[Pattern analysis]
    
    Timeline --> FindBreakpoint[Find when it broke]
    State --> ReconstructState[Recreate state at failure]
    Patterns --> AnalyzeFailures[Analyze failure patterns]
    
    FollowGuide --> Solution[Apply solution]
    FindBreakpoint --> Solution
    ReconstructState --> Solution
    AnalyzeFailures --> Solution
    
    Solution --> Test{Fixed?}
    Test -->|Yes| Doc[Document for next time]
    Test -->|No| GetHelp[Request support]
    
    style QuickCheck fill:#6bcf7f
    style FullCheck fill:#ffd93d
    style DeepDive fill:#4ecdc4
    style Solution fill:#95e1d3
    style Doc fill:#6bcf7f
```

## 5-Step Diagnostic Method

The systematic approach used throughout the guide:

```mermaid
graph LR
    Step1[1️⃣ OBSERVE] -->|Gather data| Step2[2️⃣ HYPOTHESIZE]
    Step2 -->|List causes| Step3[3️⃣ TEST]
    Step3 -->|Run diagnostics| Step4[4️⃣ FIX]
    Step4 -->|Apply solution| Step5[5️⃣ VERIFY]
    Step5 -->|Check results| Decision{Fixed?}
    
    Decision -->|No| Step2
    Decision -->|Yes| Complete[Document & Close]
    
    style Step1 fill:#e3f2fd
    style Step2 fill:#fff9c4
    style Step3 fill:#f3e5f5
    style Step4 fill:#e0f2f1
    style Step5 fill:#fce4ec
    style Complete fill:#6bcf7f
```

### Step Details

1. **OBSERVE** 👀
   - What's the symptom?
   - When did it start?
   - What changed recently?
   - Are there patterns?

2. **HYPOTHESIZE** 🤔
   - List 3 possible causes
   - Order by likelihood
   - Consider recent changes
   - Check similar past issues

3. **TEST** 🔬
   - Check logs
   - Run diagnostics
   - Isolate variables
   - Test hypotheses in order

4. **FIX** 🔧
   - Apply targeted solution
   - Not shotgun approach
   - One change at a time
   - Document what you do

5. **VERIFY** ✅
   - Confirm fix works
   - Check side effects
   - Run full health check
   - Document for future

## System State Transitions

Understanding how the system moves between states:

```mermaid
stateDiagram-v2
    [*] --> Healthy: System initialized
    Healthy --> Degraded: Some workflows fail
    Degraded --> Healthy: Issues resolved
    Degraded --> Critical: Multiple failures
    Critical --> Degraded: Emergency fixes
    Degraded --> Healthy: Full recovery
    Critical --> Healthy: System restart
    
    Healthy: ✅ HEALTHY\nAll systems operational\nWorkflows running\nCopilot responsive
    Degraded: ⚠️ DEGRADED\nSome failures\nDelayed responses\nRate limits approached
    Critical: 🔴 CRITICAL\nMultiple failures\nNo new issues\nCopilot not responding
```

## Common Issue Categories

Distribution of issues by category (based on real data):

```mermaid
pie title Issue Distribution
    "Copilot Issues" : 30
    "Workflow Issues" : 20
    "Auto-Merge Issues" : 15
    "Agent Issues" : 10
    "Learning Issues" : 8
    "Pages Issues" : 7
    "Permission Issues" : 6
    "Other" : 4
```

## Resolution Time by Issue Type

Average time to resolve each issue category:

```mermaid
gantt
    title Time to Resolution by Issue Type
    dateFormat X
    axisFormat %s min
    
    section Quick (<5 min)
    Missing Label :0, 2
    Workflow Not Enabled :0, 3
    Browser Cache :0, 1
    
    section Medium (5-15 min)
    Missing COPILOT_PAT :5, 10
    Permissions Error :5, 8
    Registry Corruption :5, 12
    
    section Longer (15-30 min)
    Auto-Merge Config :15, 20
    API Rate Limiting :15, 25
    Complex Workflow Issues :15, 30
    
    section Extended (30+ min)
    System Architecture :30, 60
    Custom Implementation :30, 90
    Multiple Interacting Issues :30, 120
```

---

## How to Use These Diagrams

1. **Start with the Complete Decision Tree** for systematic troubleshooting
2. **Use Quick Decision Matrix** when you know the symptom category
3. **Follow 5-Step Method** for complex or unknown issues
4. **Reference Tool Selection** to choose the right diagnostic
5. **Understand State Transitions** to assess system health

## Related Documentation

- **[COMPREHENSIVE_TROUBLESHOOTING_GUIDE.md](../COMPREHENSIVE_TROUBLESHOOTING_GUIDE.md)** - Full guide with detailed solutions
- **[TROUBLESHOOTING.md](../TROUBLESHOOTING.md)** - Quick reference guide
- **[PIPELINE_TROUBLESHOOTING.md](../PIPELINE_TROUBLESHOOTING.md)** - Pipeline-specific issues

---

*Created by **@clarify-champion** - Making troubleshooting as clear as starlight* ✨
