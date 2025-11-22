#!/usr/bin/env python3
"""
Workflow Prediction Dashboard
Created by @APIs-architect

Generates an HTML dashboard visualizing workflow predictions,
execution history, and accuracy metrics.
"""

import os
import sys
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

# Add tools directory to path
sys.path.insert(0, os.path.dirname(__file__))

from workflow_orchestrator_api import WorkflowOrchestratorAPI


class PredictionDashboard:
    """Generate HTML dashboard for workflow predictions."""
    
    def __init__(self, repo_root: str = None):
        """Initialize dashboard generator."""
        if repo_root:
            self.repo_root = Path(repo_root)
        else:
            current = Path.cwd()
            while current != current.parent:
                if (current / '.git').exists():
                    self.repo_root = current
                    break
                current = current.parent
            else:
                self.repo_root = Path.cwd()
        
        self.api = WorkflowOrchestratorAPI(repo_root=str(self.repo_root))
        self.output_dir = self.repo_root / 'docs' / 'workflow-predictions'
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def get_workflow_list(self) -> List[str]:
        """Get list of workflows with data."""
        workflows = set()
        for execution in self.api.predictor.execution_history:
            workflows.add(execution.workflow_name)
        return sorted(list(workflows))
    
    def generate_html(self) -> str:
        """Generate HTML dashboard."""
        workflows = self.get_workflow_list()
        
        # Get predictions for all workflows
        predictions = {}
        insights = {}
        
        for workflow in workflows:
            pred_response = self.api.predict_execution_time(workflow)
            if pred_response.success:
                predictions[workflow] = pred_response.data
            
            insight_response = self.api.get_workflow_insights(workflow)
            if insight_response.success:
                insights[workflow] = insight_response.data
        
        # Get accuracy metrics
        accuracy_response = self.api.get_accuracy_metrics()
        accuracy_data = accuracy_response.data if accuracy_response.success else {}
        
        # Generate HTML
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Workflow Prediction Dashboard - @APIs-architect</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
            padding: 20px;
            min-height: 100vh;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}
        
        header {{
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            margin-bottom: 30px;
            text-align: center;
        }}
        
        h1 {{
            color: #667eea;
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        
        .subtitle {{
            color: #666;
            font-size: 1.1em;
        }}
        
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .metric-card {{
            background: white;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            text-align: center;
        }}
        
        .metric-value {{
            font-size: 3em;
            font-weight: bold;
            color: #667eea;
            margin: 10px 0;
        }}
        
        .metric-label {{
            color: #666;
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        
        .workflow-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 20px;
        }}
        
        .workflow-card {{
            background: white;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        
        .workflow-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            padding-bottom: 15px;
            border-bottom: 2px solid #f0f0f0;
        }}
        
        .workflow-name {{
            font-size: 1.3em;
            font-weight: bold;
            color: #333;
        }}
        
        .confidence-badge {{
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.9em;
            font-weight: bold;
        }}
        
        .confidence-high {{
            background: #10b981;
            color: white;
        }}
        
        .confidence-medium {{
            background: #f59e0b;
            color: white;
        }}
        
        .confidence-low {{
            background: #ef4444;
            color: white;
        }}
        
        .info-row {{
            display: flex;
            justify-content: space-between;
            padding: 10px 0;
            border-bottom: 1px solid #f0f0f0;
        }}
        
        .info-label {{
            color: #666;
            font-weight: 500;
        }}
        
        .info-value {{
            color: #333;
            font-weight: bold;
        }}
        
        .schedule {{
            background: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            margin-top: 15px;
            text-align: center;
            font-family: 'Courier New', monospace;
            font-size: 1.2em;
            color: #667eea;
        }}
        
        .reasoning {{
            margin-top: 15px;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 5px;
        }}
        
        .reasoning-title {{
            font-weight: bold;
            margin-bottom: 10px;
            color: #667eea;
        }}
        
        .reasoning-item {{
            padding: 5px 0;
            color: #666;
            line-height: 1.5;
        }}
        
        .reasoning-item::before {{
            content: "• ";
            color: #667eea;
            font-weight: bold;
        }}
        
        footer {{
            text-align: center;
            color: white;
            margin-top: 50px;
            padding: 20px;
        }}
        
        .timestamp {{
            margin-top: 10px;
            opacity: 0.8;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🔮 AI Workflow Orchestrator</h1>
            <p class="subtitle">Predicting Execution Times with Machine Learning</p>
            <p class="subtitle">Created by <strong>@APIs-architect</strong></p>
        </header>
        
        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-label">Total Workflows</div>
                <div class="metric-value">{len(workflows)}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Total Executions</div>
                <div class="metric-value">{len(self.api.predictor.execution_history)}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Prediction Accuracy</div>
                <div class="metric-value">{'N/A' if not accuracy_data else f"{accuracy_data.get('accuracy_score', 0)*100:.0f}%"}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Avg Error (MAE)</div>
                <div class="metric-value">{'--' if not accuracy_data else f"{accuracy_data.get('mean_absolute_error', 0):.0f}s"}</div>
            </div>
        </div>
        
        <div class="workflow-grid">
"""
        
        # Add workflow cards
        for workflow in workflows:
            pred = predictions.get(workflow, {})
            insight = insights.get(workflow, {})
            
            if not pred:
                continue
            
            confidence = pred.get('confidence', 0)
            if confidence >= 0.7:
                confidence_class = 'confidence-high'
                confidence_text = f'{confidence*100:.0f}% High'
            elif confidence >= 0.4:
                confidence_class = 'confidence-medium'
                confidence_text = f'{confidence*100:.0f}% Medium'
            else:
                confidence_class = 'confidence-low'
                confidence_text = f'{confidence*100:.0f}% Low'
            
            html += f"""
            <div class="workflow-card">
                <div class="workflow-header">
                    <div class="workflow-name">{workflow}</div>
                    <div class="confidence-badge {confidence_class}">{confidence_text}</div>
                </div>
                
                <div class="info-row">
                    <span class="info-label">Expected Duration</span>
                    <span class="info-value">{pred.get('expected_duration_seconds', 0):.0f}s</span>
                </div>
                
                <div class="info-row">
                    <span class="info-label">Success Rate</span>
                    <span class="info-value">{pred.get('predicted_success_rate', 0)*100:.0f}%</span>
                </div>
                
                <div class="info-row">
                    <span class="info-label">Resource Impact</span>
                    <span class="info-value">{pred.get('resource_impact', 'unknown').capitalize()}</span>
                </div>
"""
            
            if insight:
                html += f"""
                <div class="info-row">
                    <span class="info-label">Total Executions</span>
                    <span class="info-value">{insight.get('total_executions', 0)}</span>
                </div>
                
                <div class="info-row">
                    <span class="info-label">Average Duration</span>
                    <span class="info-value">{insight.get('average_duration', 0):.0f}s</span>
                </div>
"""
            
            html += f"""
                <div class="schedule">
                    {pred.get('recommended_schedule', 'N/A')}
                </div>
"""
            
            reasoning = pred.get('reasoning', [])
            if reasoning:
                html += """
                <div class="reasoning">
                    <div class="reasoning-title">💡 Reasoning</div>
"""
                for reason in reasoning[:3]:
                    html += f'                    <div class="reasoning-item">{reason}</div>\n'
                
                html += """
                </div>
"""
            
            html += """
            </div>
"""
        
        html += f"""
        </div>
        
        <footer>
            <p><strong>AI-Powered Workflow Orchestrator</strong></p>
            <p>Built with machine learning to optimize workflow scheduling</p>
            <p class="timestamp">Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
            <p>Created by <strong>@APIs-architect</strong> 🏭</p>
        </footer>
    </div>
</body>
</html>
"""
        
        return html
    
    def save_dashboard(self) -> Path:
        """Save dashboard to HTML file."""
        html = self.generate_html()
        output_file = self.output_dir / 'index.html'
        
        with open(output_file, 'w') as f:
            f.write(html)
        
        return output_file


def main():
    """Generate the dashboard."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Generate workflow prediction dashboard - @APIs-architect'
    )
    parser.add_argument('--output', help='Output directory (default: docs/workflow-predictions)')
    parser.add_argument('--simulate', action='store_true', help='Generate simulation data first')
    
    args = parser.parse_args()
    
    dashboard = PredictionDashboard()
    
    # Simulation parameters
    SIMULATION_WORKFLOWS = 10
    SIMULATION_EXECUTIONS = 100
    
    if args.simulate:
        print("🎲 Generating simulation data...")
        dashboard.api.predictor.simulate_execution_data(
            num_workflows=SIMULATION_WORKFLOWS, 
            num_executions=SIMULATION_EXECUTIONS
        )
        print("✓ Simulation data generated")
    
    print("\n🎨 Generating dashboard...")
    output_file = dashboard.save_dashboard()
    
    print(f"\n✅ Dashboard generated successfully!")
    print(f"📄 Location: {output_file}")
    print(f"🌐 Open in browser: file://{output_file.absolute()}")
    
    # Also output JSON data for API access
    json_file = dashboard.output_dir / 'data.json'
    
    workflows = dashboard.get_workflow_list()
    data = {
        'generated_at': datetime.now(timezone.utc).isoformat(),
        'total_workflows': len(workflows),
        'total_executions': len(dashboard.api.predictor.execution_history),
        'workflows': []
    }
    
    for workflow in workflows:
        pred_response = dashboard.api.predict_execution_time(workflow)
        if pred_response.success:
            data['workflows'].append(pred_response.data)
    
    with open(json_file, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"📊 Data JSON: {json_file}")
    print()


if __name__ == '__main__':
    main()
