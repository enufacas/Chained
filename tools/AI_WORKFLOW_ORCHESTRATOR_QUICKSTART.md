# AI Workflow Orchestrator - Quick Start Guide

**Created by @create-botter** 🏭

Get started with the AI-powered workflow orchestrator in 3 simple steps!

## 🚀 What You Get

An AI system that:
- 📊 **Automatically tracks** every workflow execution
- 🔮 **Predicts** optimal execution times
- 📈 **Learns continuously** from real data
- 🎯 **Provides actionable insights** for optimization

## ⚡ 3-Step Quick Start

### Step 1: Let It Collect Data (Automatic)

The system is **already running**! Every time a workflow completes, data is automatically recorded.

Wait for a few workflows to run (10-20 executions recommended for initial predictions).

### Step 2: Check System Status

```bash
python3 tools/workflow_prediction_service.py --status
```

You'll see:
- How many executions tracked
- Success rate
- Average duration
- Number of workflows monitored

### Step 3: Get Your First Predictions

```bash
# Predict all workflows
python3 tools/workflow_prediction_service.py --all

# Or predict a specific workflow
python3 tools/workflow_prediction_service.py --workflow "your-workflow-name"
```

## 🎯 Using the Live Dashboard

1. Go to **Actions** in your repo
2. Select **"AI Workflow Orchestrator - Live Predictions"**
3. Click **"Run workflow"**
4. Choose a mode:
   - `status` - Quick health check
   - `predict` - Get all predictions
   - `insights` - Deep workflow analysis
   - `dashboard` - Visual metrics overview

## 📊 Understanding Your Results

### Prediction Output

```
Workflow: daily-learning-reflection
Recommended Time: 0 6 * * *     ← Best schedule (6 AM daily)
Confidence: 85.0%                ← How confident the AI is
Expected Duration: 145.2s        ← How long it will take
Success Rate: 92.0%              ← Likelihood of success
Resource Impact: medium          ← Resource usage level
```

### Confidence Levels

- **80-100%** 🟢 High - Strong patterns, trust this
- **60-80%** 🟡 Medium - Good data, likely accurate
- **30-60%** 🟠 Low - Limited data, use cautiously
- **0-30%** 🔴 Very Low - Need more executions

## 🔧 Integration Examples

### Use in a Workflow

```yaml
- name: Check if good time to run
  run: |
    PRED=$(python3 tools/workflow_prediction_service.py --workflow "${{ github.workflow }}" --json)
    CONFIDENCE=$(echo $PRED | jq -r '.prediction.confidence')
    
    if (( $(echo "$CONFIDENCE > 0.7" | bc -l) )); then
      echo "✅ High confidence - good time to run"
    else
      echo "⚠️ Low confidence - consider rescheduling"
    fi
```

### Get JSON for External Tools

```bash
# Get machine-readable output
python3 tools/workflow_prediction_service.py --all --json > predictions.json

# Use in monitoring dashboards, alerting systems, etc.
```

## 📈 What Happens Next

1. **Automatic Learning**: Every workflow execution improves predictions
2. **Daily Monitoring**: System checks health at 6 AM UTC daily
3. **Data Updates**: Execution data is committed via automated PRs
4. **Continuous Improvement**: Predictions get more accurate over time

## 🎓 Tips for Best Results

### For Accurate Predictions
- ✅ Run workflows regularly (not just once)
- ✅ Let system collect 20+ executions per workflow
- ✅ Review predictions weekly as data grows
- ✅ Use high-confidence predictions (>70%)

### For Optimal Performance
- ✅ Schedule workflows based on AI recommendations
- ✅ Monitor success rates and adjust
- ✅ Check resource impact for load balancing
- ✅ Use insights to identify problematic workflows

## 📚 Learn More

- **Full Documentation**: `tools/AI_WORKFLOW_ORCHESTRATOR_PRODUCTION_README.md`
- **Original System**: `tools/AI_WORKFLOW_ORCHESTRATOR_README.md`
- **Workflow Files**:
  - `.github/workflows/workflow-execution-recorder.yml` (data collection)
  - `.github/workflows/ai-workflow-orchestrator-live.yml` (orchestrator)

## 🆘 Troubleshooting

### "No data available"
- **Solution**: Wait for workflows to run. System needs execution history.
- **Check**: `ls -la .github/workflow-history/executions.json`

### "Low confidence predictions"
- **Solution**: Normal for new workflows. Needs more executions (10-20+).
- **Action**: Keep running workflows, confidence will increase.

### "Execution recorder not triggering"
- **Check**: Verify workflow has `workflow_run` permissions
- **Check**: Look for "Workflow Execution Recorder" in Actions tab
- **Note**: It triggers AFTER other workflows complete

## 🎯 Success Checklist

After setup, you should see:
- [ ] `workflow-execution-recorder.yml` in Actions tab
- [ ] Data file exists: `.github/workflow-history/executions.json`
- [ ] Status command shows tracked executions
- [ ] Predictions generate with confidence scores
- [ ] Daily orchestrator runs appear in Actions

## 🚀 Next Steps

Once you have predictions:
1. **Apply Recommendations**: Update workflow schedules to optimal times
2. **Monitor Impact**: Check if success rates improve
3. **Iterate**: Refine based on real results
4. **Share**: Use insights to optimize team's workflows

---

**Ready to optimize? Run your first status check now!**

```bash
python3 tools/workflow_prediction_service.py --status
```

**@create-botter** 🏭 - *Building smarter infrastructure, one workflow at a time*
