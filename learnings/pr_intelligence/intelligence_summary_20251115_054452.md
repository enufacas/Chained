# PR Failure Intelligence Summary

**Generated**: $(date -u +"%Y-%m-%d %H:%M:%S UTC")
**Run**: 20

## 📊 Analysis Results

### Code Patterns Analyzed
- **Total PRs analyzed**: 100
- **Patterns identified**: $(cat learnings/pr_intelligence/code_patterns.json 2>/dev/null | jq '.total_patterns // 0')

### Agent Profiles Generated
- **Profiles created**: 
- **Location**: `learnings/pr_intelligence/agent_profiles/`

## 🎯 Key Insights

### Success Patterns
$(cat learnings/pr_intelligence/code_patterns.json 2>/dev/null | jq -r '
  .patterns[]? 
  | select(.success_rate > 0.7) 
  | "- \(.description)"
' || echo "No high-success patterns identified yet")

### Risk Factors
$(cat learnings/pr_intelligence/code_patterns.json 2>/dev/null | jq -r '
  .patterns[]? 
  | select(.success_rate < 0.5) 
  | "- \(.description)"
' || echo "No high-risk patterns identified yet")

## 📚 Available Data

- **Code Patterns**: `learnings/pr_intelligence/code_patterns.json`
- **Agent Profiles**: `learnings/pr_intelligence/agent_profiles/*.json`
- **PR History**: `learnings/pr_intelligence/pr_history_20251115_054448.json`

## 🚀 Using the Intelligence

### For Agents
```bash
# Get proactive guidance
python tools/pr-failure-intelligence.py --proactive-guidance --agent YOUR_AGENT_ID

# Predict PR risk
python tools/pr-failure-intelligence.py --predict-risk --input your_pr_data.json
```

### For Analysis
```bash
# View patterns
cat learnings/pr_intelligence/code_patterns.json | jq '.patterns'

# View agent profile
cat learnings/pr_intelligence/agent_profiles/AGENT_ID.json
```

---

*Built by **@engineer-master** - Systematic learning for intelligent code generation*
