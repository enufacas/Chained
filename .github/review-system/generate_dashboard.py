#!/usr/bin/env python3
"""
Generate dashboard for autonomous reviewer effectiveness trends.

Created by: @workflows-tech-lead
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any


def load_criteria_with_history(criteria_path: Path) -> Dict[str, Any]:
    """Load criteria including effectiveness history."""
    with open(criteria_path, 'r') as f:
        return json.load(f)


def generate_html_dashboard(criteria: Dict[str, Any]) -> str:
    """Generate HTML dashboard with effectiveness trends."""
    
    history = criteria.get('effectiveness_history', [])
    categories = criteria.get('criteria', {})
    
    # Generate HTML
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Autonomous Reviewer Dashboard - @workflows-tech-lead</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            padding: 40px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
        }}
        h1 {{
            color: #667eea;
            margin-bottom: 10px;
            font-size: 2.5em;
        }}
        .subtitle {{
            color: #666;
            margin-bottom: 30px;
            font-size: 1.1em;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }}
        .stat-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 25px;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        .stat-label {{
            font-size: 0.9em;
            opacity: 0.9;
            margin-bottom: 8px;
        }}
        .stat-value {{
            font-size: 2.5em;
            font-weight: bold;
            margin-bottom: 5px;
        }}
        .stat-change {{
            font-size: 0.85em;
            opacity: 0.8;
        }}
        .section {{
            margin-bottom: 40px;
        }}
        .section-title {{
            font-size: 1.8em;
            color: #667eea;
            margin-bottom: 20px;
            border-bottom: 2px solid #eee;
            padding-bottom: 10px;
        }}
        .category-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .category-card {{
            border: 2px solid #eee;
            border-radius: 8px;
            padding: 20px;
            transition: transform 0.2s, box-shadow 0.2s;
        }}
        .category-card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 6px 12px rgba(0,0,0,0.1);
        }}
        .category-name {{
            font-size: 1.2em;
            font-weight: bold;
            color: #333;
            margin-bottom: 15px;
        }}
        .metric {{
            display: flex;
            justify-content: space-between;
            margin-bottom: 10px;
            padding: 8px 0;
            border-bottom: 1px solid #f0f0f0;
        }}
        .metric-label {{
            color: #666;
        }}
        .metric-value {{
            font-weight: bold;
            color: #667eea;
        }}
        .chart {{
            background: #f8f9fa;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 20px;
        }}
        .bar {{
            height: 30px;
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            border-radius: 4px;
            margin: 10px 0;
            display: flex;
            align-items: center;
            padding-left: 10px;
            color: white;
            font-weight: bold;
        }}
        .history-table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }}
        .history-table th {{
            background: #667eea;
            color: white;
            padding: 12px;
            text-align: left;
            font-weight: 600;
        }}
        .history-table td {{
            padding: 12px;
            border-bottom: 1px solid #eee;
        }}
        .history-table tr:hover {{
            background: #f8f9fa;
        }}
        .badge {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 0.85em;
            font-weight: 600;
        }}
        .badge-success {{
            background: #d4edda;
            color: #155724;
        }}
        .badge-warning {{
            background: #fff3cd;
            color: #856404;
        }}
        .badge-info {{
            background: #d1ecf1;
            color: #0c5460;
        }}
        .footer {{
            text-align: center;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 2px solid #eee;
            color: #666;
        }}
        .emoji {{
            font-size: 1.5em;
            margin-right: 8px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1><span class="emoji">🤖</span>Autonomous Code Reviewer Dashboard</h1>
        <p class="subtitle">Self-improving review criteria powered by @workflows-tech-lead</p>
        
        <!-- Overall Stats -->
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-label">Total Reviews</div>
                <div class="stat-value">{criteria['metadata']['total_reviews']}</div>
                <div class="stat-change">Reviews performed</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Success Rate</div>
                <div class="stat-value">{criteria['metadata']['success_rate']:.1%}</div>
                <div class="stat-change">PRs merged after review</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Criteria Version</div>
                <div class="stat-value">{criteria['version']}</div>
                <div class="stat-change">Evolution iterations</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Last Updated</div>
                <div class="stat-value">{datetime.fromisoformat(criteria['last_updated'].rstrip('Z')).strftime('%m/%d')}</div>
                <div class="stat-change">{datetime.fromisoformat(criteria['last_updated'].rstrip('Z')).strftime('%H:%M UTC')}</div>
            </div>
        </div>
        
        <!-- Category Performance -->
        <div class="section">
            <h2 class="section-title">📊 Category Performance</h2>
            <div class="category-grid">
"""
    
    # Add category cards
    for cat_name, cat_data in categories.items():
        display_name = cat_name.replace('_', ' ').title()
        weight = cat_data.get('weight', 1.0)
        threshold = cat_data.get('threshold', 0.5)
        checks_count = len(cat_data.get('checks', []))
        effectiveness = cat_data.get('effectiveness_score', 0)
        
        # Determine badge
        if effectiveness > 0.1:
            badge_class = 'badge-success'
            badge_text = 'Effective'
        elif effectiveness < -0.1:
            badge_class = 'badge-warning'
            badge_text = 'Ineffective'
        else:
            badge_class = 'badge-info'
            badge_text = 'Neutral'
        
        html += f"""
                <div class="category-card">
                    <div class="category-name">{display_name} <span class="badge {badge_class}">{badge_text}</span></div>
                    <div class="metric">
                        <span class="metric-label">Weight</span>
                        <span class="metric-value">{weight:.2f}</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Threshold</span>
                        <span class="metric-value">{threshold:.0%}</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Checks</span>
                        <span class="metric-value">{checks_count}</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Effectiveness</span>
                        <span class="metric-value">{effectiveness:+.3f}</span>
                    </div>
                </div>
"""
    
    html += """
            </div>
        </div>
        
        <!-- Weight Comparison -->
        <div class="section">
            <h2 class="section-title">⚖️ Category Weights</h2>
            <div class="chart">
"""
    
    # Sort categories by weight
    sorted_cats = sorted(categories.items(), key=lambda x: x[1].get('weight', 1.0), reverse=True)
    max_weight = max(cat[1].get('weight', 1.0) for cat in sorted_cats)
    
    for cat_name, cat_data in sorted_cats:
        display_name = cat_name.replace('_', ' ').title()
        weight = cat_data.get('weight', 1.0)
        width_percent = (weight / max_weight) * 100
        
        html += f"""
                <div class="bar" style="width: {width_percent}%">
                    {display_name}: {weight:.2f}
                </div>
"""
    
    html += """
            </div>
        </div>
"""
    
    # Add effectiveness history if available
    if history:
        html += """
        <!-- Effectiveness History -->
        <div class="section">
            <h2 class="section-title">📈 Evolution History</h2>
            <table class="history-table">
                <thead>
                    <tr>
                        <th>Date</th>
                        <th>Total Reviews</th>
                        <th>Merge Rate</th>
                        <th>Correlation</th>
                        <th>Top Effective Category</th>
                    </tr>
                </thead>
                <tbody>
"""
        
        # Show last 20 history entries
        for entry in reversed(history[-20:]):
            timestamp = datetime.fromisoformat(entry['timestamp'].rstrip('Z')).strftime('%Y-%m-%d %H:%M')
            total_reviews = entry.get('total_reviews', 0)
            merge_rate = entry.get('merge_rate', 0)
            correlation = entry.get('correlation', 0)
            
            # Find top effective category
            cat_eff = entry.get('category_effectiveness', {})
            if cat_eff:
                top_cat = max(cat_eff.items(), key=lambda x: x[1])
                top_cat_name = top_cat[0].replace('_', ' ').title()
                top_cat_eff = top_cat[1]
                top_cat_str = f"{top_cat_name} ({top_cat_eff:+.3f})"
            else:
                top_cat_str = "N/A"
            
            html += f"""
                    <tr>
                        <td>{timestamp}</td>
                        <td>{total_reviews}</td>
                        <td>{merge_rate:.1%}</td>
                        <td>{correlation:+.3f}</td>
                        <td>{top_cat_str}</td>
                    </tr>
"""
        
        html += """
                </tbody>
            </table>
        </div>
"""
    
    html += f"""
        <!-- Footer -->
        <div class="footer">
            <p><strong>🤖 Autonomous Code Reviewer</strong></p>
            <p>Self-improving criteria powered by machine learning</p>
            <p>Created by <strong>@workflows-tech-lead</strong></p>
            <p style="font-size: 0.9em; color: #999; margin-top: 10px;">
                Last updated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}
            </p>
        </div>
    </div>
</body>
</html>
"""
    
    return html


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate dashboard for reviewer effectiveness')
    parser.add_argument('--criteria', type=str, default='.github/review-system/criteria.json', help='Criteria file')
    parser.add_argument('--output', type=str, default='docs/reviewer-dashboard.html', help='Output HTML file')
    
    args = parser.parse_args()
    
    # Load criteria
    criteria_path = Path(args.criteria)
    if not criteria_path.exists():
        print(f"Error: Criteria file not found: {criteria_path}", file=sys.stderr)
        return 1
    
    criteria = load_criteria_with_history(criteria_path)
    
    # Generate dashboard
    html = generate_html_dashboard(criteria)
    
    # Write output
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w') as f:
        f.write(html)
    
    print(f"✅ Dashboard generated: {output_path}")
    
    # Show stats
    print(f"\nStats:")
    print(f"  Total Reviews: {criteria['metadata']['total_reviews']}")
    print(f"  Success Rate: {criteria['metadata']['success_rate']:.1%}")
    print(f"  Categories: {len(criteria['criteria'])}")
    print(f"  History Entries: {len(criteria.get('effectiveness_history', []))}")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
