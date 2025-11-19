#!/usr/bin/env python3
"""
A/B Testing Visualization Dashboard Generator

Creates an HTML dashboard for visualizing A/B testing experiments and results.

Author: @workflows-tech-lead
Inspired by: Martha Graham - Choreographic precision in data presentation
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime

# Add tools to path
sys.path.insert(0, str(Path(__file__).parent))
from ab_testing_engine import ABTestingEngine


class DashboardGenerator:
    """
    Generates HTML dashboards for A/B testing visualization.
    """
    
    def __init__(self):
        """Initialize the dashboard generator."""
        self.engine = ABTestingEngine()
    
    def generate_dashboard(self, output_path: str = "docs/ab-testing-dashboard.html") -> None:
        """
        Generate the A/B testing dashboard HTML.
        
        Args:
            output_path: Path to save the HTML dashboard
        """
        experiments = self.engine.list_experiments()
        
        html = self._generate_html(experiments)
        
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w') as f:
            f.write(html)
        
        print(f"✅ Dashboard generated: {output_path}")
    
    def _generate_html(self, experiments: List[Dict[str, Any]]) -> str:
        """
        Generate complete HTML for the dashboard.
        
        Args:
            experiments: List of experiments
        
        Returns:
            Complete HTML string
        """
        active_experiments = [e for e in experiments if e["status"] == "active"]
        completed_experiments = [e for e in experiments if e["status"] == "completed"]
        
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>A/B Testing Dashboard - Chained</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            color: #333;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        
        .header {{
            background: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }}
        
        h1 {{
            color: #667eea;
            margin-bottom: 10px;
        }}
        
        .subtitle {{
            color: #666;
            font-size: 14px;
        }}
        
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .stat-card {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            text-align: center;
        }}
        
        .stat-number {{
            font-size: 36px;
            font-weight: bold;
            color: #667eea;
        }}
        
        .stat-label {{
            color: #666;
            font-size: 14px;
            margin-top: 5px;
        }}
        
        .section {{
            background: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }}
        
        .section-title {{
            font-size: 24px;
            color: #333;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #f0f0f0;
        }}
        
        .experiment {{
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 15px;
            transition: all 0.3s ease;
        }}
        
        .experiment:hover {{
            border-color: #667eea;
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.1);
        }}
        
        .experiment-header {{
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 15px;
        }}
        
        .experiment-title {{
            font-size: 18px;
            font-weight: 600;
            color: #333;
            flex: 1;
        }}
        
        .status-badge {{
            display: inline-block;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
            text-transform: uppercase;
        }}
        
        .status-active {{
            background: #e3f2fd;
            color: #1976d2;
        }}
        
        .status-completed {{
            background: #e8f5e9;
            color: #388e3c;
        }}
        
        .experiment-meta {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin-top: 15px;
        }}
        
        .meta-item {{
            display: flex;
            flex-direction: column;
        }}
        
        .meta-label {{
            font-size: 11px;
            color: #999;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 5px;
        }}
        
        .meta-value {{
            font-size: 14px;
            color: #333;
            font-weight: 500;
        }}
        
        .variants {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 10px;
            margin-top: 15px;
        }}
        
        .variant {{
            background: #f9f9f9;
            padding: 12px;
            border-radius: 6px;
            border: 2px solid transparent;
        }}
        
        .variant-winner {{
            border-color: #4caf50;
            background: #e8f5e9;
        }}
        
        .variant-name {{
            font-weight: 600;
            color: #667eea;
            margin-bottom: 5px;
        }}
        
        .variant-samples {{
            font-size: 12px;
            color: #666;
        }}
        
        .winner-badge {{
            display: inline-block;
            background: #4caf50;
            color: white;
            padding: 3px 8px;
            border-radius: 4px;
            font-size: 11px;
            font-weight: 600;
            margin-left: 5px;
        }}
        
        .empty-state {{
            text-align: center;
            padding: 40px;
            color: #999;
        }}
        
        .timestamp {{
            color: #999;
            font-size: 12px;
            text-align: center;
            margin-top: 30px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔬 A/B Testing Dashboard</h1>
            <p class="subtitle">Autonomous workflow configuration optimization • Chained AI System</p>
        </div>
        
        <div class="stats">
            <div class="stat-card">
                <div class="stat-number">{len(experiments)}</div>
                <div class="stat-label">Total Experiments</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{len(active_experiments)}</div>
                <div class="stat-label">Active</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{len(completed_experiments)}</div>
                <div class="stat-label">Completed</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{self._count_winners(completed_experiments)}</div>
                <div class="stat-label">Winners Detected</div>
            </div>
        </div>
        
        <div class="section">
            <h2 class="section-title">🟢 Active Experiments</h2>
            {self._render_experiments(active_experiments, "active")}
        </div>
        
        <div class="section">
            <h2 class="section-title">✅ Completed Experiments</h2>
            {self._render_experiments(completed_experiments, "completed")}
        </div>
        
        <p class="timestamp">
            Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}
        </p>
    </div>
</body>
</html>
"""
        return html
    
    def _render_experiments(self, experiments: List[Dict[str, Any]], status: str) -> str:
        """
        Render experiments list HTML.
        
        Args:
            experiments: List of experiments to render
            status: Experiment status for styling
        
        Returns:
            HTML string for experiments
        """
        if not experiments:
            return '<div class="empty-state">No experiments in this category</div>'
        
        html_parts = []
        
        for exp in experiments:
            # Get detailed information
            try:
                details = self.engine.get_experiment_details(exp["id"])
            except:
                details = exp
            
            winner_variant = None
            if details.get("results") and "winner" in details["results"]:
                winner_variant = details["results"]["winner"]
            
            # Build variants HTML
            variants_html = []
            for variant_name, variant_data in details.get("variants", {}).items():
                is_winner = variant_name == winner_variant
                winner_class = " variant-winner" if is_winner else ""
                winner_badge = ' <span class="winner-badge">WINNER</span>' if is_winner else ""
                
                samples = variant_data.get("total_samples", 0)
                
                variants_html.append(f'''
                <div class="variant{winner_class}">
                    <div class="variant-name">{variant_name}{winner_badge}</div>
                    <div class="variant-samples">{samples} samples</div>
                </div>
                ''')
            
            # Build experiment card HTML
            exp_html = f'''
            <div class="experiment">
                <div class="experiment-header">
                    <div class="experiment-title">{details.get("name", "Unnamed Experiment")}</div>
                    <span class="status-badge status-{status}">{status}</span>
                </div>
                <div class="experiment-meta">
                    <div class="meta-item">
                        <div class="meta-label">Workflow</div>
                        <div class="meta-value">{details.get("workflow_name", "N/A")}</div>
                    </div>
                    <div class="meta-item">
                        <div class="meta-label">Created</div>
                        <div class="meta-value">{self._format_date(details.get("created_at"))}</div>
                    </div>
                    <div class="meta-item">
                        <div class="meta-label">Variants</div>
                        <div class="meta-value">{len(details.get("variants", {}))}</div>
                    </div>
                </div>
                <div class="variants">
                    {''.join(variants_html)}
                </div>
            </div>
            '''
            
            html_parts.append(exp_html)
        
        return '\n'.join(html_parts)
    
    def _count_winners(self, experiments: List[Dict[str, Any]]) -> int:
        """Count experiments with detected winners."""
        count = 0
        for exp in experiments:
            try:
                details = self.engine.get_experiment_details(exp["id"])
                if details.get("results") and "winner" in details["results"]:
                    count += 1
            except:
                pass
        return count
    
    def _format_date(self, date_str: str) -> str:
        """Format ISO date string for display."""
        if not date_str:
            return "N/A"
        
        try:
            dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            return dt.strftime('%Y-%m-%d')
        except:
            return date_str


def main():
    """CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Generate A/B Testing Dashboard"
    )
    parser.add_argument(
        "--output",
        default="docs/ab-testing-dashboard.html",
        help="Output path for HTML dashboard (default: docs/ab-testing-dashboard.html)"
    )
    
    args = parser.parse_args()
    
    generator = DashboardGenerator()
    generator.generate_dashboard(args.output)
    
    return 0


if __name__ == "__main__":
    exit(main())
