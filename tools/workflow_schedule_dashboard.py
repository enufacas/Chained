#!/usr/bin/env python3
"""
Workflow Schedule Optimization Dashboard
Created by @create-guru

Provides visualization and analysis of meta-learning optimization results.
Generates HTML dashboards showing schedule optimization progress and effectiveness.
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from collections import defaultdict

# Add tools directory to path
sys.path.insert(0, os.path.dirname(__file__))

try:
    from meta_learning_scheduler import MetaLearningScheduler
    from ai_workflow_predictor import AIWorkflowPredictor
    from workflow_execution_tracker import WorkflowExecutionTracker
except ImportError as e:
    print(f"Warning: Could not import required modules: {e}", file=sys.stderr)


class WorkflowScheduleDashboard:
    """
    Generate interactive dashboards for workflow schedule optimization.
    
    Visualizes:
    - Strategy performance over time
    - Prediction accuracy trends
    - Optimization recommendations
    - Learning progress metrics
    """
    
    def __init__(self, repo_root: str = None):
        """
        Initialize the dashboard generator.
        
        Args:
            repo_root: Root directory of the repository
        """
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
        
        self.output_dir = self.repo_root / 'docs' / 'data'
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize components
        try:
            self.scheduler = MetaLearningScheduler(repo_root=str(self.repo_root))
            self.predictor = AIWorkflowPredictor(repo_root=str(self.repo_root))
            self.tracker = WorkflowExecutionTracker(repo_root=str(self.repo_root))
        except Exception as e:
            print(f"Warning: Could not initialize meta-learning components: {e}", file=sys.stderr)
            self.scheduler = None
            self.predictor = None
            self.tracker = None
    
    def generate_optimization_data(self) -> Dict[str, Any]:
        """
        Generate comprehensive optimization data for visualization.
        
        Returns:
            Dictionary with all optimization metrics
        """
        if not self.scheduler:
            return {
                'error': 'Meta-learning scheduler not available',
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
        
        # Get meta-learning report
        report = self.scheduler.generate_meta_learning_report()
        
        # Get workflow-specific recommendations
        workflows = self._get_workflow_list()
        recommendations = []
        
        for workflow in workflows[:10]:  # Top 10 workflows
            try:
                result = self.scheduler.generate_optimized_schedule(
                    workflow, 
                    report['best_strategy']
                )
                recommendations.append({
                    'workflow': workflow,
                    'current_schedule': self._get_current_schedule(workflow),
                    'recommended_schedule': result.recommended_time,
                    'confidence': result.confidence * 100,
                    'expected_duration': result.expected_duration,
                    'reasoning': result.reasoning[:3]
                })
            except Exception as e:
                print(f"Warning: Could not generate recommendation for {workflow}: {e}", file=sys.stderr)
        
        # Compile comprehensive data
        data = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'meta_learning': {
                'best_strategy': report['best_strategy'],
                'total_strategies': len(report['strategies']),
                'accuracy_metrics': report['accuracy_metrics'],
                'strategies': report['strategies'],
                'learning_log_size': report['learning_log_size']
            },
            'recommendations': recommendations,
            'workflow_stats': {
                'total_workflows': len(workflows),
                'optimized_workflows': len(recommendations)
            }
        }
        
        return data
    
    def _get_workflow_list(self) -> List[str]:
        """Get list of workflows from repository."""
        workflows_dir = self.repo_root / '.github' / 'workflows'
        if not workflows_dir.exists():
            return []
        
        workflows = []
        for workflow_file in workflows_dir.glob('*.yml'):
            workflow_name = workflow_file.stem
            workflows.append(workflow_name)
        
        return sorted(workflows)
    
    def _get_current_schedule(self, workflow_name: str) -> Optional[str]:
        """
        Get current schedule from workflow file.
        
        Args:
            workflow_name: Name of the workflow
            
        Returns:
            Current cron schedule or None
        """
        workflow_file = self.repo_root / '.github' / 'workflows' / f'{workflow_name}.yml'
        if not workflow_file.exists():
            return None
        
        try:
            import yaml
            with open(workflow_file) as f:
                workflow_data = yaml.safe_load(f)
            
            if 'on' in workflow_data and 'schedule' in workflow_data['on']:
                schedules = workflow_data['on']['schedule']
                if schedules and len(schedules) > 0:
                    return schedules[0].get('cron', None)
        except Exception as e:
            print(f"Warning: Could not read schedule from {workflow_file}: {e}", file=sys.stderr)
        
        return None
    
    def generate_json_data(self) -> str:
        """
        Generate JSON data file for dashboard.
        
        Returns:
            Path to generated JSON file
        """
        print("📊 Generating optimization dashboard data...")
        
        data = self.generate_optimization_data()
        
        output_file = self.output_dir / 'workflow-optimization.json'
        with open(output_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"✅ Dashboard data saved to {output_file}")
        
        return str(output_file)
    
    def generate_html_dashboard(self) -> str:
        """
        Generate complete HTML dashboard.
        
        Returns:
            Path to generated HTML file
        """
        print("🎨 Generating HTML dashboard...")
        
        data = self.generate_optimization_data()
        
        html_content = self._create_html_dashboard(data)
        
        output_file = self.repo_root / 'docs' / 'workflow-optimization.html'
        with open(output_file, 'w') as f:
            f.write(html_content)
        
        print(f"✅ Dashboard saved to {output_file}")
        
        return str(output_file)
    
    def _create_html_dashboard(self, data: Dict[str, Any]) -> str:
        """
        Create HTML dashboard from optimization data.
        
        Args:
            data: Optimization data dictionary
            
        Returns:
            HTML content as string
        """
        timestamp = datetime.fromisoformat(data['timestamp']).strftime('%Y-%m-%d %H:%M UTC')
        
        # Build strategies table
        strategies_rows = ""
        if 'strategies' in data['meta_learning']:
            for name, strategy in data['meta_learning']['strategies'].items():
                trend_icon = "📈" if strategy['trend'] == "improving" else "📉" if strategy['trend'] == "declining" else "➡️"
                is_best = name == data['meta_learning']['best_strategy']
                row_class = 'best-strategy' if is_best else ''
                
                strategies_rows += f"""
                <tr class="{row_class}">
                    <td>{'🏆 ' if is_best else ''}<code>{name}</code></td>
                    <td>{strategy['performance']:.1f}%</td>
                    <td>{trend_icon} {strategy['trend']}</td>
                    <td>{strategy['history_length']}</td>
                </tr>
                """
        
        # Build recommendations table
        recommendations_rows = ""
        for rec in data.get('recommendations', []):
            current = rec.get('current_schedule', 'None')
            recommended = rec['recommended_schedule']
            changed = current != recommended
            
            recommendations_rows += f"""
            <tr>
                <td><code>{rec['workflow']}</code></td>
                <td><code>{current}</code></td>
                <td class="{'highlight' if changed else ''}"><code>{recommended}</code></td>
                <td>{rec['confidence']:.0f}%</td>
                <td>{rec['expected_duration']:.0f}s</td>
            </tr>
            """
        
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Workflow Schedule Optimization Dashboard</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            line-height: 1.6;
            color: #333;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }}
        
        header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}
        
        header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        
        header p {{
            font-size: 1.1em;
            opacity: 0.9;
        }}
        
        .timestamp {{
            background: rgba(255,255,255,0.2);
            padding: 10px 20px;
            border-radius: 20px;
            display: inline-block;
            margin-top: 15px;
        }}
        
        .content {{
            padding: 40px;
        }}
        
        .metrics {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }}
        
        .metric-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        
        .metric-card h3 {{
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 1px;
            opacity: 0.9;
            margin-bottom: 10px;
        }}
        
        .metric-card .value {{
            font-size: 2.5em;
            font-weight: bold;
            margin-bottom: 5px;
        }}
        
        .metric-card .label {{
            font-size: 0.9em;
            opacity: 0.8;
        }}
        
        section {{
            margin-bottom: 40px;
        }}
        
        section h2 {{
            font-size: 1.8em;
            margin-bottom: 20px;
            color: #667eea;
            border-bottom: 3px solid #667eea;
            padding-bottom: 10px;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            background: white;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            border-radius: 8px;
            overflow: hidden;
        }}
        
        thead {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }}
        
        th, td {{
            padding: 15px;
            text-align: left;
        }}
        
        tbody tr:nth-child(even) {{
            background: #f8f9fa;
        }}
        
        tbody tr:hover {{
            background: #e9ecef;
        }}
        
        .best-strategy {{
            background: #fff3cd !important;
            font-weight: bold;
        }}
        
        .highlight {{
            background: #d4edda;
            font-weight: bold;
        }}
        
        code {{
            background: #f4f4f4;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
        }}
        
        footer {{
            background: #f8f9fa;
            padding: 30px;
            text-align: center;
            color: #6c757d;
            border-top: 1px solid #dee2e6;
        }}
        
        footer p {{
            margin-bottom: 10px;
        }}
        
        .icon {{
            font-size: 1.2em;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🎓 Workflow Schedule Optimization Dashboard</h1>
            <p>Meta-Learning System Performance Metrics</p>
            <div class="timestamp">📅 Last Updated: {timestamp}</div>
        </header>
        
        <div class="content">
            <div class="metrics">
                <div class="metric-card">
                    <h3>🏆 Best Strategy</h3>
                    <div class="value">{data['meta_learning']['best_strategy']}</div>
                    <div class="label">Current optimal approach</div>
                </div>
                
                <div class="metric-card">
                    <h3>📊 Accuracy Score</h3>
                    <div class="value">{data['meta_learning']['accuracy_metrics']['accuracy_score']:.1f}%</div>
                    <div class="label">Prediction accuracy</div>
                </div>
                
                <div class="metric-card">
                    <h3>🧠 Total Strategies</h3>
                    <div class="value">{data['meta_learning']['total_strategies']}</div>
                    <div class="label">Learned approaches</div>
                </div>
                
                <div class="metric-card">
                    <h3>🔬 Predictions</h3>
                    <div class="value">{data['meta_learning']['accuracy_metrics']['total_predictions']}</div>
                    <div class="label">Total analyzed</div>
                </div>
            </div>
            
            <section>
                <h2>🧠 Learned Strategies Performance</h2>
                <table>
                    <thead>
                        <tr>
                            <th>Strategy</th>
                            <th>Performance</th>
                            <th>Trend</th>
                            <th>Data Points</th>
                        </tr>
                    </thead>
                    <tbody>
                        {strategies_rows}
                    </tbody>
                </table>
            </section>
            
            <section>
                <h2>🎯 Schedule Optimization Recommendations</h2>
                <table>
                    <thead>
                        <tr>
                            <th>Workflow</th>
                            <th>Current Schedule</th>
                            <th>Recommended</th>
                            <th>Confidence</th>
                            <th>Est. Duration</th>
                        </tr>
                    </thead>
                    <tbody>
                        {recommendations_rows}
                    </tbody>
                </table>
            </section>
            
            <section>
                <h2>📈 Learning Progress</h2>
                <table>
                    <thead>
                        <tr>
                            <th>Metric</th>
                            <th>Value</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>Total Predictions</td>
                            <td>{data['meta_learning']['accuracy_metrics']['total_predictions']}</td>
                        </tr>
                        <tr>
                            <td>Mean Error</td>
                            <td>{data['meta_learning']['accuracy_metrics']['mean_error']:.1f}%</td>
                        </tr>
                        <tr>
                            <td>Excellent Predictions (≤10%)</td>
                            <td>{data['meta_learning']['accuracy_metrics'].get('excellent_predictions', 0)}</td>
                        </tr>
                        <tr>
                            <td>Good Predictions (10-25%)</td>
                            <td>{data['meta_learning']['accuracy_metrics'].get('good_predictions', 0)}</td>
                        </tr>
                        <tr>
                            <td>Learning Events</td>
                            <td>{data['meta_learning']['learning_log_size']}</td>
                        </tr>
                    </tbody>
                </table>
            </section>
        </div>
        
        <footer>
            <p><strong>🤖 Created by @create-guru</strong></p>
            <p>Meta-learning system continuously optimizes workflow schedules</p>
            <p>Part of the Chained autonomous AI ecosystem</p>
        </footer>
    </div>
</body>
</html>
"""
        
        return html
    
    def generate_summary_report(self) -> Dict[str, Any]:
        """
        Generate a concise summary report.
        
        Returns:
            Summary dictionary
        """
        data = self.generate_optimization_data()
        
        summary = {
            'timestamp': data['timestamp'],
            'best_strategy': data['meta_learning']['best_strategy'],
            'accuracy_score': data['meta_learning']['accuracy_metrics']['accuracy_score'],
            'total_strategies': data['meta_learning']['total_strategies'],
            'total_predictions': data['meta_learning']['accuracy_metrics']['total_predictions'],
            'recommendations_count': len(data.get('recommendations', [])),
            'learning_events': data['meta_learning']['learning_log_size']
        }
        
        return summary


def main():
    """Main function for CLI usage."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Workflow Schedule Optimization Dashboard - @create-guru'
    )
    parser.add_argument('--repo-root', help='Repository root directory')
    parser.add_argument('--json', action='store_true', help='Generate JSON data file')
    parser.add_argument('--html', action='store_true', help='Generate HTML dashboard')
    parser.add_argument('--summary', action='store_true', help='Print summary report')
    parser.add_argument('--all', action='store_true', help='Generate all outputs')
    
    args = parser.parse_args()
    
    # Initialize dashboard
    dashboard = WorkflowScheduleDashboard(repo_root=args.repo_root)
    
    if args.all or args.json:
        json_file = dashboard.generate_json_data()
        print(f"📊 JSON data: {json_file}")
    
    if args.all or args.html:
        html_file = dashboard.generate_html_dashboard()
        print(f"🎨 HTML dashboard: {html_file}")
    
    if args.all or args.summary:
        summary = dashboard.generate_summary_report()
        print("\n" + "="*70)
        print("📊 Workflow Schedule Optimization Summary")
        print("="*70)
        print(f"Timestamp: {summary['timestamp']}")
        print(f"Best Strategy: {summary['best_strategy']}")
        print(f"Accuracy Score: {summary['accuracy_score']:.1f}%")
        print(f"Total Strategies: {summary['total_strategies']}")
        print(f"Total Predictions: {summary['total_predictions']}")
        print(f"Recommendations: {summary['recommendations_count']}")
        print(f"Learning Events: {summary['learning_events']}")
        print("="*70)
    
    if not (args.json or args.html or args.summary or args.all):
        parser.print_help()


if __name__ == '__main__':
    main()
