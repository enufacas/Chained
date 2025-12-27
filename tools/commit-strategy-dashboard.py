#!/usr/bin/env python3
"""
Git Commit Strategy Dashboard - Visual Insights by @create-botter

A Tesla-inspired dashboard that illuminates commit patterns with elegance and power.
Transforms raw data into actionable insights through beautiful visualization.

Features:
- Real-time commit quality metrics
- Trend analysis with visual indicators
- Pattern recognition heatmaps
- Recommendation impact tracking
- Historical improvement charts
- Developer performance insights

Usage:
    python tools/commit-strategy-dashboard.py [--port 8000] [--no-browser]
    python tools/commit-strategy-dashboard.py --export-html dashboard.html
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
import argparse


def load_strategies_data() -> Dict[str, Any]:
    """Load commit strategies data"""
    strategies_file = Path("learnings/commit_strategies.json")
    if strategies_file.exists():
        with open(strategies_file, 'r') as f:
            return json.load(f)
    return {}


def load_patterns_data() -> Dict[str, Any]:
    """Load commit patterns data"""
    patterns_file = Path("analysis/commit_patterns.json")
    if patterns_file.exists():
        with open(patterns_file, 'r') as f:
            return json.load(f)
    return {}


def generate_dashboard_html(strategies: Dict, patterns: Dict) -> str:
    """Generate beautiful HTML dashboard inspired by Tesla's design language"""
    
    # Extract key metrics
    total_commits = strategies.get('total_commits_analyzed', 0)
    successful = strategies.get('successful_merges', 0)
    failed = strategies.get('failed_merges', 0)
    patterns_count = len(strategies.get('patterns_identified', []))
    success_rate = (successful / total_commits * 100) if total_commits > 0 else 0
    
    # Get learning history for trends
    history = strategies.get('learning_history', [])
    
    # Generate trend data
    trend_data = []
    if history:
        for entry in history[-10:]:  # Last 10 entries
            timestamp = entry.get('timestamp', '')
            success = entry.get('successful', 0)
            total = entry.get('commits_analyzed', 1)
            rate = (success / total * 100) if total > 0 else 0
            trend_data.append({
                'date': timestamp.split('T')[0] if 'T' in timestamp else timestamp[:10],
                'rate': rate
            })
    
    # Get patterns summary
    patterns_html = ""
    for pattern_dict in strategies.get('patterns_identified', []):
        pattern_name = pattern_dict.get('pattern_name', 'unknown')
        success_rate_pattern = pattern_dict.get('success_rate', 0) * 100
        confidence = pattern_dict.get('confidence_score', 0) * 100
        
        patterns_html += f"""
        <div class="pattern-card">
            <h3>{pattern_name.replace('_', ' ').title()}</h3>
            <div class="pattern-stats">
                <div class="stat">
                    <span class="stat-label">Success Rate</span>
                    <span class="stat-value">{success_rate_pattern:.1f}%</span>
                </div>
                <div class="stat">
                    <span class="stat-label">Confidence</span>
                    <span class="stat-value">{confidence:.1f}%</span>
                </div>
            </div>
            <div class="pattern-bar" style="width: {confidence:.0f}%"></div>
        </div>
        """
    
    # Get recommendations
    recommendations_html = ""
    for rec_dict in strategies.get('recommendations', []):
        title = rec_dict.get('title', 'Recommendation')
        description = rec_dict.get('description', '')
        confidence = rec_dict.get('confidence_score', 0) * 100
        trend = rec_dict.get('trend', 'stable')
        
        trend_emoji = "📈" if trend == "improving" else "📉" if trend == "declining" else "➡️"
        
        recommendations_html += f"""
        <div class="recommendation-card">
            <h4>{trend_emoji} {title}</h4>
            <p>{description}</p>
            <div class="confidence-badge">{confidence:.0f}% confidence</div>
        </div>
        """
    
    # Build trend chart data
    trend_chart_labels = [d['date'] for d in trend_data]
    trend_chart_values = [d['rate'] for d in trend_data]
    
    html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Git Commit Strategy Dashboard - by @create-botter</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #2d3748;
            line-height: 1.6;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}
        
        .header {{
            text-align: center;
            color: white;
            margin-bottom: 40px;
        }}
        
        .header h1 {{
            font-size: 3rem;
            font-weight: 700;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        }}
        
        .header p {{
            font-size: 1.2rem;
            opacity: 0.9;
        }}
        
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .metric-card {{
            background: white;
            border-radius: 12px;
            padding: 25px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.15);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }}
        
        .metric-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 15px 40px rgba(0,0,0,0.2);
        }}
        
        .metric-label {{
            font-size: 0.9rem;
            color: #718096;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 10px;
        }}
        
        .metric-value {{
            font-size: 3rem;
            font-weight: 700;
            color: #667eea;
        }}
        
        .metric-subvalue {{
            font-size: 1rem;
            color: #a0aec0;
            margin-top: 5px;
        }}
        
        .chart-container {{
            background: white;
            border-radius: 12px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.15);
        }}
        
        .chart-title {{
            font-size: 1.5rem;
            font-weight: 600;
            margin-bottom: 20px;
            color: #2d3748;
        }}
        
        .patterns-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .pattern-card {{
            background: white;
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 5px 20px rgba(0,0,0,0.1);
        }}
        
        .pattern-card h3 {{
            font-size: 1.2rem;
            margin-bottom: 15px;
            color: #2d3748;
        }}
        
        .pattern-stats {{
            display: flex;
            justify-content: space-between;
            margin-bottom: 15px;
        }}
        
        .stat {{
            text-align: center;
        }}
        
        .stat-label {{
            display: block;
            font-size: 0.8rem;
            color: #718096;
            margin-bottom: 5px;
        }}
        
        .stat-value {{
            display: block;
            font-size: 1.5rem;
            font-weight: 700;
            color: #667eea;
        }}
        
        .pattern-bar {{
            height: 8px;
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            border-radius: 4px;
            transition: width 0.5s ease;
        }}
        
        .recommendations-section {{
            background: white;
            border-radius: 12px;
            padding: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.15);
        }}
        
        .section-title {{
            font-size: 1.8rem;
            font-weight: 600;
            margin-bottom: 20px;
            color: #2d3748;
        }}
        
        .recommendation-card {{
            border-left: 4px solid #667eea;
            padding: 20px;
            margin-bottom: 15px;
            background: #f7fafc;
            border-radius: 8px;
        }}
        
        .recommendation-card h4 {{
            font-size: 1.2rem;
            margin-bottom: 10px;
            color: #2d3748;
        }}
        
        .recommendation-card p {{
            color: #4a5568;
            margin-bottom: 10px;
        }}
        
        .confidence-badge {{
            display: inline-block;
            background: #667eea;
            color: white;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.85rem;
            font-weight: 600;
        }}
        
        .footer {{
            text-align: center;
            color: white;
            margin-top: 40px;
            opacity: 0.8;
        }}
        
        .chart {{
            width: 100%;
            height: 300px;
        }}
        
        @media (max-width: 768px) {{
            .header h1 {{
                font-size: 2rem;
            }}
            
            .metrics-grid {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>⚡ Git Commit Strategy Dashboard</h1>
            <p>Powered by autonomous learning infrastructure by @create-botter</p>
        </div>
        
        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-label">Total Commits Analyzed</div>
                <div class="metric-value">{total_commits}</div>
            </div>
            
            <div class="metric-card">
                <div class="metric-label">Success Rate</div>
                <div class="metric-value">{success_rate:.1f}%</div>
                <div class="metric-subvalue">{successful} successful / {failed} failed</div>
            </div>
            
            <div class="metric-card">
                <div class="metric-label">Patterns Identified</div>
                <div class="metric-value">{patterns_count}</div>
            </div>
            
            <div class="metric-card">
                <div class="metric-label">Last Updated</div>
                <div class="metric-value" style="font-size: 1.2rem;">
                    {strategies.get('last_updated', 'N/A')[:10] if strategies.get('last_updated') else 'N/A'}
                </div>
            </div>
        </div>
        
        <div class="chart-container">
            <h2 class="chart-title">📈 Commit Quality Trend</h2>
            <canvas id="trendChart" class="chart"></canvas>
        </div>
        
        <div class="patterns-grid">
            {patterns_html if patterns_html else '<div class="pattern-card"><h3>No patterns identified yet</h3><p>Run analysis to discover patterns</p></div>'}
        </div>
        
        <div class="recommendations-section">
            <h2 class="section-title">💡 Top Recommendations</h2>
            {recommendations_html if recommendations_html else '<p>No recommendations available yet. Run analysis to generate recommendations.</p>'}
        </div>
        
        <div class="footer">
            <p>✨ Visionary infrastructure by <strong>@create-botter</strong></p>
            <p>Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
        </div>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <script>
        // Trend chart
        const ctx = document.getElementById('trendChart').getContext('2d');
        new Chart(ctx, {{
            type: 'line',
            data: {{
                labels: {json.dumps(trend_chart_labels)},
                datasets: [{{
                    label: 'Success Rate (%)',
                    data: {json.dumps(trend_chart_values)},
                    borderColor: '#667eea',
                    backgroundColor: 'rgba(102, 126, 234, 0.1)',
                    borderWidth: 3,
                    tension: 0.4,
                    fill: true,
                    pointRadius: 5,
                    pointHoverRadius: 7
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{
                        display: true,
                        position: 'top'
                    }},
                    tooltip: {{
                        mode: 'index',
                        intersect: false
                    }}
                }},
                scales: {{
                    y: {{
                        beginAtZero: true,
                        max: 100,
                        ticks: {{
                            callback: function(value) {{
                                return value + '%';
                            }}
                        }}
                    }}
                }}
            }}
        }});
        
        // Animate pattern bars on load
        window.addEventListener('load', () => {{
            const bars = document.querySelectorAll('.pattern-bar');
            bars.forEach((bar, index) => {{
                setTimeout(() => {{
                    bar.style.opacity = '1';
                }}, index * 100);
            }});
        }});
    </script>
</body>
</html>
    """
    
    return html


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Git Commit Strategy Dashboard - Visual Insights by @create-botter",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('--port', type=int, default=8000,
                       help='Port for local server (default: 8000)')
    parser.add_argument('--no-browser', action='store_true',
                       help='Do not open browser automatically')
    parser.add_argument('--export-html', type=str,
                       help='Export dashboard to HTML file')
    
    args = parser.parse_args()
    
    print("⚡ Git Commit Strategy Dashboard by @create-botter")
    print()
    
    # Load data
    print("📊 Loading data...")
    strategies = load_strategies_data()
    patterns = load_patterns_data()
    
    if not strategies:
        print("⚠️  No strategies data found. Run analysis first:")
        print("   python tools/commit-strategy-learner.py --analyze")
        return 1
    
    # Generate dashboard
    print("🎨 Generating dashboard...")
    html = generate_dashboard_html(strategies, patterns)
    
    if args.export_html:
        # Export to file
        output_path = Path(args.export_html)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(html)
        print(f"✅ Dashboard exported to {output_path}")
        return 0
    
    # Serve dashboard
    import http.server
    import socketserver
    import webbrowser
    from threading import Thread
    
    # Write temporary HTML
    temp_file = Path("/tmp/commit-dashboard.html")
    temp_file.write_text(html)
    
    class Handler(http.server.SimpleHTTPRequestHandler):
        def do_GET(self):
            if self.path == '/' or self.path == '/index.html':
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(html.encode())
            else:
                super().do_GET()
    
    # Start server
    port = args.port
    with socketserver.TCPServer(("", port), Handler) as httpd:
        url = f"http://localhost:{port}"
        print(f"🚀 Dashboard running at {url}")
        print("   Press Ctrl+C to stop")
        print()
        
        if not args.no_browser:
            Thread(target=lambda: webbrowser.open(url)).start()
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n✅ Dashboard stopped")
            return 0


if __name__ == '__main__':
    sys.exit(main())
