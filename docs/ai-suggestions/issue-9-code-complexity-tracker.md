---
title: 📈 Code Complexity Tracker - Monitor Quality Trends Over Time
labels: enhancement, ai-suggested, copilot, quality
---

## 🎯 Suggestion from AI Friend

[AI Friend conversation from 2025-11-15](../ai-conversations/conversation_20251115_091234.json) suggested: **"Create a code complexity tracker that monitors changes over time"**

**Key Insight**: "Your autonomous AI system is fascinating! I suggest adding a feature to analyze code quality trends over time. This could help identify patterns in how the AI evolves and learns."

## 📌 Current State

We currently have:
- Code archaeology that analyzes historical patterns (`.github/workflows/code-archaeologist.yml`)
- Agent evaluation based on PR success and review quality
- No systematic tracking of code complexity metrics
- No trend analysis of code quality over time
- No correlation between agent behavior and code maintainability

## 💡 Proposed Enhancement

Implement a **Code Complexity Tracker** that monitors code quality evolution:

### 1. **Complexity Metrics Collection**

Track multiple dimensions of code quality:

- **Cyclomatic Complexity**: Measure code path complexity
- **Cognitive Complexity**: Assess code readability and understandability
- **Code Churn**: Track how often files change (instability indicator)
- **Maintainability Index**: Calculate overall maintainability score
- **Technical Debt**: Identify and quantify technical debt accumulation
- **Test Coverage**: Monitor test coverage trends
- **Documentation Quality**: Assess comment and doc completeness

### 2. **Trend Analysis**

Monitor how metrics change over time:

- **Per-File Trends**: Track complexity evolution of individual files
- **Per-Agent Trends**: See which agents produce maintainable code
- **System-Wide Trends**: Is the overall codebase improving or degrading?
- **Correlation Analysis**: Link complexity to bug rates, PR success, etc.

### 3. **Visualization Dashboard**

Create interactive visualizations in GitHub Pages:

```html
<!-- docs/code-quality-trends.html -->
- Line charts showing complexity trends over time
- Heatmaps of file complexity (which files are most complex?)
- Agent leaderboard (who writes the most maintainable code?)
- Correlation charts (complexity vs. bugs, complexity vs. review time)
- Improvement/regression indicators
```

### 4. **Integration with Agent System**

Use complexity data to improve agent behavior:

- **Agent Evaluation**: Factor code quality into agent scores
- **Learning Signals**: Teach agents what maintainable code looks like
- **Spawner Guidance**: Generate agents with maintainability focus
- **Alerts**: Notify when complexity increases significantly

## 🔧 Implementation Ideas

```yaml
# New workflow: .github/workflows/code-complexity-tracker.yml

name: "Code Complexity Tracker"

on:
  push:
    branches: [main]
  schedule:
    - cron: '0 2 * * *'  # Daily at 2 AM
  workflow_dispatch:

jobs:
  track-complexity:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
        with:
          fetch-depth: 0  # Need full history for trends
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install complexity tools
        run: |
          pip install radon lizard mccabe
          pip install pandas matplotlib seaborn
      
      - name: Analyze code complexity
        run: python tools/complexity-tracker.py analyze
        # Calculates all complexity metrics for current code
      
      - name: Calculate trends
        run: python tools/complexity-tracker.py trends
        # Compares with historical data to identify trends
      
      - name: Generate visualizations
        run: python tools/complexity-tracker.py visualize
        # Creates charts and dashboards
      
      - name: Correlate with agent data
        run: python tools/complexity-tracker.py correlate-agents
        # Links complexity to agent contributions
      
      - name: Update GitHub Pages
        run: |
          cp complexity-report.html docs/code-quality-trends.html
          cp complexity-data.json docs/data/complexity.json
      
      - name: Create PR if significant changes
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          if python tools/complexity-tracker.py should-alert; then
            # Complexity increased significantly
            python tools/complexity-tracker.py create-alert-issue
          fi
```

```python
# tools/complexity-tracker.py

import subprocess
import json
import os
from datetime import datetime
from pathlib import Path
import pandas as pd

class ComplexityTracker:
    def __init__(self):
        self.history_file = 'docs/data/complexity-history.json'
        self.current_metrics = {}
        
    def analyze_complexity(self):
        """Analyze current codebase complexity"""
        metrics = {
            'timestamp': datetime.utcnow().isoformat(),
            'files': {}
        }
        
        # Use radon for cyclomatic complexity
        result = subprocess.run(
            ['radon', 'cc', '.', '-j'],
            capture_output=True, text=True
        )
        cc_data = json.loads(result.stdout)
        
        # Use radon for maintainability index
        result = subprocess.run(
            ['radon', 'mi', '.', '-j'],
            capture_output=True, text=True
        )
        mi_data = json.loads(result.stdout)
        
        # Combine metrics per file
        for filepath, functions in cc_data.items():
            if filepath.endswith('.py'):
                metrics['files'][filepath] = {
                    'cyclomatic_complexity': sum(f['complexity'] for f in functions),
                    'function_count': len(functions),
                    'maintainability_index': mi_data.get(filepath, {}).get('mi', 0),
                    'complexity_per_function': sum(f['complexity'] for f in functions) / len(functions) if functions else 0
                }
        
        self.current_metrics = metrics
        return metrics
    
    def calculate_trends(self):
        """Compare current metrics with historical data"""
        if not os.path.exists(self.history_file):
            return {'status': 'first_run', 'trends': []}
        
        with open(self.history_file, 'r') as f:
            history = json.load(f)
        
        trends = []
        
        # Analyze each file's trend
        for filepath, current in self.current_metrics['files'].items():
            historical = self.get_file_history(filepath, history)
            
            if len(historical) > 0:
                trend = self.analyze_file_trend(filepath, current, historical)
                trends.append(trend)
        
        return {
            'status': 'analyzed',
            'trends': trends,
            'summary': self.summarize_trends(trends)
        }
    
    def analyze_file_trend(self, filepath, current, historical):
        """Analyze trend for a single file"""
        # Get last 10 data points
        recent = historical[-10:]
        
        cc_values = [h['cyclomatic_complexity'] for h in recent]
        mi_values = [h['maintainability_index'] for h in recent]
        
        return {
            'filepath': filepath,
            'current_complexity': current['cyclomatic_complexity'],
            'complexity_trend': 'increasing' if current['cyclomatic_complexity'] > sum(cc_values)/len(cc_values) else 'decreasing',
            'current_maintainability': current['maintainability_index'],
            'maintainability_trend': 'improving' if current['maintainability_index'] > sum(mi_values)/len(mi_values) else 'degrading',
            'alert': self.should_alert_on_file(current, recent)
        }
    
    def correlate_with_agents(self):
        """Link complexity metrics to agent contributions"""
        # Read agent registry
        with open('.github/agent-system/registry.json', 'r') as f:
            registry = json.load(f)
        
        # Get git blame data to see who touched which files
        agent_complexity = {}
        
        for filepath in self.current_metrics['files'].keys():
            # Get git blame for this file
            result = subprocess.run(
                ['git', 'log', '--format=%an', filepath],
                capture_output=True, text=True
            )
            
            contributors = result.stdout.strip().split('\n')
            
            # Map to agent if possible
            # (Simplified - real implementation would be more sophisticated)
            for agent in registry['agents']:
                if any(agent['name'] in c for c in contributors):
                    if agent['name'] not in agent_complexity:
                        agent_complexity[agent['name']] = {
                            'files': [],
                            'avg_complexity': 0
                        }
                    
                    agent_complexity[agent['name']]['files'].append({
                        'file': filepath,
                        'complexity': self.current_metrics['files'][filepath]['cyclomatic_complexity']
                    })
        
        # Calculate averages
        for agent in agent_complexity:
            complexities = [f['complexity'] for f in agent_complexity[agent]['files']]
            agent_complexity[agent]['avg_complexity'] = sum(complexities) / len(complexities)
        
        return agent_complexity
    
    def generate_visualization(self):
        """Create HTML dashboard with charts"""
        import matplotlib.pyplot as plt
        import seaborn as sns
        
        # Load historical data
        with open(self.history_file, 'r') as f:
            history = json.load(f)
        
        # Create trend charts
        html = self.create_dashboard_html(history)
        
        with open('complexity-report.html', 'w') as f:
            f.write(html)
        
        return 'complexity-report.html'
    
    def should_alert(self):
        """Determine if complexity increase warrants an alert"""
        trends = self.calculate_trends()
        
        if trends['status'] != 'analyzed':
            return False
        
        # Count files with degrading trends
        degrading = sum(1 for t in trends['trends'] if t['alert'])
        
        # Alert if more than 20% of files are degrading
        return degrading > len(trends['trends']) * 0.2
```

## 📊 Success Metrics

- Complexity metrics tracked for all Python files
- Historical trend data spanning multiple months
- Correlation between agent behavior and code quality
- Interactive dashboard showing trends and patterns
- Alerts when complexity increases significantly
- Agent evaluation includes maintainability scores
- Measurable improvement in overall code quality over time

## 🎨 Why This Matters

The AI's evolution is only as good as the code it produces! By tracking complexity:
- **Objective Quality Measurement**: Know if the code is getting better or worse
- **Agent Accountability**: Identify which agents write maintainable code
- **Learning Signal**: Teach the system what good code looks like
- **Early Warning**: Catch complexity increases before they become problems
- **Transparency**: Show stakeholders that AI produces quality code
- **Self-Improvement**: The AI can learn from its own quality trends

## 🔗 Related

- Code archaeology: `.github/workflows/code-archaeologist.yml`
- Agent evaluator: `.github/workflows/agent-evaluator.yml`
- Agent registry: `.github/agent-system/registry.json`
- [Source AI Friend conversation](../ai-conversations/conversation_20251115_091234.json)

## 💭 Future Enhancements

- **Predictive Analysis**: Predict which files are likely to become complex
- **Refactoring Recommendations**: Suggest specific refactorings to reduce complexity
- **Language Support**: Extend beyond Python to JavaScript, YAML, etc.
- **Real-time Feedback**: Provide complexity feedback in PR reviews
- **Complexity Budget**: Set and enforce complexity limits per file/module
