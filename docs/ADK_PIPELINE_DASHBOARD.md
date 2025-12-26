# 🎨 ADK Pipeline Dashboard - @create-botter's Vision

**A Tesla-inspired monitoring dashboard for the ADK A2A Blog Pipeline**

## 🌟 Overview

The ADK Pipeline Dashboard provides real-time monitoring, health checks, and historical analytics for the autonomous A2A blog generation pipeline. Built by **@create-botter** with elegance and innovation in mind.

## 🚀 Quick Start

### Installation

```bash
# Install dependencies
pip install httpx

# Make executable
chmod +x tools/adk-pipeline-dashboard.py
```

### Basic Usage

```bash
# Check agent health
./tools/adk-pipeline-dashboard.py health

# View pipeline status
./tools/adk-pipeline-dashboard.py status

# Full dashboard view
./tools/adk-pipeline-dashboard.py dashboard

# Quick system check (returns 0 if all healthy)
./tools/adk-pipeline-dashboard.py check
```

## 📋 Commands

### `health` - Agent Health Check

Checks the health of all A2A agents:
- 🔬 Academic Research Agent
- 📈 Google Trends Agent  
- ✍️ Blog Writer Agent

**Output:**
- Connection status
- Response time
- Agent version
- Available skills
- Error details (if any)

**Example:**
```bash
$ ./tools/adk-pipeline-dashboard.py health

================================================================================
  🏥 Agent Health Status
================================================================================

✅ All agents are healthy and operational!

🔬 Academic Research Agent
   URL: http://localhost:8081
   Status: ✅ HEALTHY
   Response Time: 45ms
   Version: 1.0.0
   Skills: discover-topics, analyze-topic

📈 Google Trends Agent
   URL: http://localhost:8083
   Status: ✅ HEALTHY
   Response Time: 52ms
   Version: 1.0.0
   Skills: analyze-trends, get-keywords

✍️ Blog Writer Agent
   URL: http://localhost:8082
   Status: ✅ HEALTHY
   Response Time: 48ms
   Version: 1.0.0
   Skills: write-blog, deploy-blog
```

### `status` - Pipeline Status

Analyzes pipeline execution history from the tracking issue:
- Total run count
- Recent execution timestamps
- Run mode (simulation vs cloud run)
- Success/failure status

**Example:**
```bash
$ ./tools/adk-pipeline-dashboard.py status

================================================================================
  📊 Pipeline Execution Status
================================================================================

📋 Tracking Issue: #4065
🔄 Total Runs Analyzed: 15

Recent Pipeline Runs:

  1. Run at 2025-12-26T12:00:00Z
     Mode: simulation

  2. Run at 2025-12-26T06:00:00Z
     Mode: cloud run

  3. Run at 2025-12-26T00:00:00Z
     Mode: simulation
```

### `dashboard` - Full Dashboard

Combines health check and pipeline status with summary:

**Example:**
```bash
$ ./tools/adk-pipeline-dashboard.py dashboard

# Shows full health status + pipeline status + summary

================================================================================
  📈 Dashboard Summary
================================================================================

🏥 Agent Health: 3/3 healthy (100%)
📊 Pipeline Runs: 15 tracked

✨ Powered by @create-botter - Visionary Infrastructure
```

### `check` - Quick Check

Quick validation for CI/CD and automation:
- Returns exit code 0 if all agents healthy
- Returns exit code 1 if any agent unhealthy

**Example:**
```bash
$ ./tools/adk-pipeline-dashboard.py check && echo "All good!" || echo "Issues detected"

🔍 Checking agent health...
✅ All systems operational!
All good!
```

## 🎯 Options

### `--issue NUMBER`

Specify tracking issue number explicitly:
```bash
./tools/adk-pipeline-dashboard.py status --issue 4065
```

**Default:** Auto-detects issue with label `adk-pipeline`

### `--timeout SECONDS`

Set timeout for agent health checks:
```bash
./tools/adk-pipeline-dashboard.py health --timeout 5.0
```

**Default:** 10.0 seconds

## 🔧 Configuration

### Agent URLs

Agents are discovered via environment variables:

```bash
export ACADEMIC_RESEARCH_URL=https://research-agent.example.com
export GOOGLE_TRENDS_URL=https://trends-agent.example.com
export BLOG_WRITER_URL=https://writer-agent.example.com
```

**Defaults:**
- Academic Research: `http://localhost:8081`
- Google Trends: `http://localhost:8083`
- Blog Writer: `http://localhost:8082`

### Tracking Issue

The dashboard finds the tracking issue by searching for label `adk-pipeline`. 

If multiple issues exist, specify with `--issue`.

## 🏗️ Architecture

### Health Checking

```
Dashboard
    │
    ├──► Academic Research Agent
    │         GET /health
    │         GET /.well-known/agent.json
    │
    ├──► Google Trends Agent
    │         GET /health
    │         GET /.well-known/agent.json
    │
    └──► Blog Writer Agent
              GET /health
              GET /.well-known/agent.json
```

### Status Analysis

```
Dashboard
    │
    └──► GitHub CLI (gh)
              gh issue list --label adk-pipeline
              gh issue view <number> --json comments
              │
              └──► Parse run history
                   Extract metrics
                   Calculate statistics
```

## 🎭 Integration Patterns

### CI/CD Health Check

Add to your workflow:

```yaml
- name: Check ADK Pipeline Health
  run: |
    pip install httpx
    ./tools/adk-pipeline-dashboard.py check
```

### Pre-Deployment Validation

```bash
#!/bin/bash
# Ensure agents are healthy before deploying

echo "Validating agent health..."
./tools/adk-pipeline-dashboard.py check

if [ $? -eq 0 ]; then
  echo "✅ Agents healthy - proceeding with deployment"
  ./deploy.sh
else
  echo "❌ Agents unhealthy - aborting deployment"
  exit 1
fi
```

### Monitoring Script

```bash
#!/bin/bash
# Periodic health monitoring

while true; do
  ./tools/adk-pipeline-dashboard.py dashboard
  echo ""
  echo "Next check in 5 minutes..."
  sleep 300
done
```

### Slack/Discord Notifications

```bash
#!/bin/bash
# Send health status to Slack

STATUS=$(./tools/adk-pipeline-dashboard.py check 2>&1)
if [ $? -ne 0 ]; then
  curl -X POST -H 'Content-type: application/json' \
    --data "{\"text\":\"⚠️ ADK Pipeline Alert: $STATUS\"}" \
    $SLACK_WEBHOOK_URL
fi
```

## 🧪 Testing

### Test Locally

```bash
# Start simulated agents
cd infrastructure/docker/adk-agents
python academic-research/agent.py &
python google-trends/agent.py &
python blog-writer/agent.py &

# Wait for startup
sleep 5

# Check health
./tools/adk-pipeline-dashboard.py health

# Should show all agents healthy
```

### Test with Cloud Run

```bash
# Set Cloud Run URLs
export ACADEMIC_RESEARCH_URL=https://chained-academic-research-xxx.run.app
export GOOGLE_TRENDS_URL=https://chained-google-trends-xxx.run.app
export BLOG_WRITER_URL=https://chained-blog-writer-xxx.run.app

# Check health
./tools/adk-pipeline-dashboard.py health
```

## 🎓 Understanding the Output

### Health Status Indicators

- ✅ **HEALTHY** - Agent responding normally
- ❌ **UNHEALTHY** - Agent not responding or error

### Response Times

- **< 100ms** - Excellent
- **100-500ms** - Good
- **500-1000ms** - Acceptable
- **> 1000ms** - Slow (check network/agent load)

### Common Errors

**"Timeout"**
- Agent not responding within timeout period
- Check agent is running
- Increase timeout with `--timeout`

**"HTTP Error: 404"**
- Endpoint not found
- Check agent URL is correct
- Verify agent version supports A2A protocol

**"Connection refused"**
- Agent not running
- Check port configuration
- Verify firewall settings

## 🌟 Advanced Usage

### JSON Output

For programmatic consumption:

```python
import subprocess
import json

result = subprocess.run(
    ["./tools/adk-pipeline-dashboard.py", "check"],
    capture_output=True,
    text=True
)

# Parse output for monitoring systems
if result.returncode == 0:
    print("All healthy")
else:
    print("Issues detected")
```

### Custom Health Checks

Extend the dashboard by modifying `AgentHealthChecker`:

```python
class CustomHealthChecker(AgentHealthChecker):
    async def check_agent_health(self, agent_id: str) -> Dict:
        result = await super().check_agent_health(agent_id)
        
        # Add custom checks
        if result["healthy"]:
            # Check database connectivity
            # Check API rate limits
            # Check disk space
            pass
        
        return result
```

## 📚 Related Documentation

- **Pipeline Workflow:** `.github/workflows/adk-a2a-blog-pipeline.yml`
- **Tracking Guide:** `docs/ADK_PIPELINE_TRACKING_GUIDE.md`
- **Implementation:** `docs/ADK_A2A_PIPELINE_IMPLEMENTATION.md`
- **Quick Reference:** `docs/ADK_PIPELINE_QUICK_REF.md`
- **Agent Directory:** `infrastructure/docker/adk-agents/`

## 🎨 Design Philosophy

**@create-botter's Tesla-Inspired Principles:**

1. **Elegance** - Clean, intuitive interface
2. **Power** - Comprehensive monitoring capabilities
3. **Innovation** - Forward-thinking architecture
4. **Reliability** - Robust error handling
5. **Scalability** - Easily extensible

## 🤝 Contributing

Enhance the dashboard:

1. Add new agent types to `AGENTS` configuration
2. Implement custom health checks
3. Add new visualization modes
4. Integrate with external monitoring systems

## 💡 Tips & Tricks

### Tip #1: Alias for Quick Access
```bash
echo "alias adk-health='./tools/adk-pipeline-dashboard.py check'" >> ~/.bashrc
```

### Tip #2: Watch Mode
```bash
watch -n 60 ./tools/adk-pipeline-dashboard.py dashboard
```

### Tip #3: Health Check in Pre-commit Hook
```bash
# .git/hooks/pre-push
./tools/adk-pipeline-dashboard.py check || {
  echo "⚠️ Agents not healthy - push anyway? (y/N)"
  read -r response
  [ "$response" = "y" ] || exit 1
}
```

## 🆘 Troubleshooting

### Dashboard Won't Run

**Problem:** `ModuleNotFoundError: No module named 'httpx'`

**Solution:**
```bash
pip install httpx
```

### Can't Find Tracking Issue

**Problem:** "Could not find tracking issue"

**Solution:**
1. Check issue has label `adk-pipeline`
2. Specify issue number: `--issue 4065`
3. Verify `gh` CLI is configured

### All Agents Show Unhealthy

**Problem:** All agents timeout

**Solution:**
1. Verify agents are running
2. Check network connectivity
3. Increase timeout: `--timeout 30`
4. Check firewall/security groups

---

**✨ Built by @create-botter** - Bringing visionary infrastructure to life

*"The present is theirs; the future, for which I really worked, is mine." - Nikola Tesla*

---

**Last Updated:** 2025-12-26  
**Version:** 1.0.0  
**Status:** ✅ Production Ready
