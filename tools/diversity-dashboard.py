#!/usr/bin/env python3
"""
AI Diversity Dashboard Generator

Creates a visual dashboard showing diversity trends, agent rankings,
and pattern analysis for the autonomous AI system.

Created by @investigate-champion for comprehensive visualization.
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional


class DiversityDashboard:
    """Generates diversity metrics dashboard"""
    
    def __init__(self, repo_dir: str):
        self.repo_dir = Path(repo_dir)
        self.analysis_dir = self.repo_dir / 'analysis'
        self.trends_data = None
        self.latest_report = None
        self.uniqueness_scores = None
        self.pattern_library = None
        
    def load_data(self):
        """Load all necessary data files"""
        # Load trends
        trends_file = self.analysis_dir / 'diversity-trends.json'
        if trends_file.exists():
            with open(trends_file, 'r') as f:
                self.trends_data = json.load(f)
        
        # Load latest repetition report
        history_dir = self.analysis_dir / 'repetition-history'
        latest_file = history_dir / 'latest.json' if history_dir.exists() else None
        
        if not latest_file or not latest_file.exists():
            # Try the main analysis directory
            latest_file = self.analysis_dir / 'repetition-report.json'
        
        if latest_file.exists():
            with open(latest_file, 'r') as f:
                self.latest_report = json.load(f)
        
        # Load uniqueness scores
        scores_file = self.analysis_dir / 'uniqueness-scores.json'
        if scores_file.exists():
            with open(scores_file, 'r') as f:
                self.uniqueness_scores = json.load(f)
        
        # Load pattern library
        pattern_file = self.analysis_dir / 'pattern-diversity.json'
        if pattern_file.exists():
            with open(pattern_file, 'r') as f:
                self.pattern_library = json.load(f)
    
    def generate_overview_section(self) -> str:
        """Generate overview section with key metrics"""
        lines = [
            "# 🎨 AI Diversity Dashboard",
            "",
            f"**Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}",
            "",
            "## 📊 Overview",
            ""
        ]
        
        if self.trends_data:
            diversity = self.trends_data.get('diversity_trend', {})
            innovation = self.trends_data.get('innovation_trend', {})
            
            lines.extend([
                "| Metric | Value | Trend |",
                "|--------|-------|-------|"
            ])
            
            # Diversity score
            div_score = diversity.get('current_score', 0)
            div_trend = diversity.get('trend', 'unknown')
            div_emoji = self._trend_emoji(div_trend)
            lines.append(f"| **Diversity Score** | {div_score:.1f}/100 | {div_emoji} {div_trend.title()} |")
            
            # Innovation index
            innov_score = innovation.get('current_average', 0)
            innov_trend = innovation.get('trend', 'unknown')
            innov_emoji = self._trend_emoji(innov_trend)
            lines.append(f"| **Innovation Index** | {innov_score:.1f}% | {innov_emoji} {innov_trend.title()} |")
            
            # Snapshots analyzed
            snapshots = self.trends_data.get('metadata', {}).get('snapshots_analyzed', 0)
            lines.append(f"| **Data Points** | {snapshots} | 📈 Tracking |")
            
        else:
            lines.append("_No trend data available. Generate trends first using `trend-analyzer.py`._")
        
        lines.append("")
        return "\n".join(lines)
    
    def generate_agent_rankings(self) -> str:
        """Generate agent uniqueness rankings"""
        lines = [
            "## 🏆 Agent Uniqueness Rankings",
            "",
            "Top performing agents by uniqueness score:",
            ""
        ]
        
        if not self.uniqueness_scores or 'scores' not in self.uniqueness_scores:
            lines.append("_No agent scores available._")
            return "\n".join(lines)
        
        # Sort agents by score
        scores = self.uniqueness_scores['scores']
        sorted_agents = sorted(
            scores.items(),
            key=lambda x: x[1].get('overall_score', 0),
            reverse=True
        )
        
        lines.extend([
            "| Rank | Agent | Score | Diversity | Innovation | Status |",
            "|------|-------|-------|-----------|------------|--------|"
        ])
        
        threshold = self.uniqueness_scores.get('metadata', {}).get('threshold', 30)
        
        for i, (agent_id, data) in enumerate(sorted_agents[:10], 1):
            score = data.get('overall_score', 0)
            metrics = data.get('metrics', {})
            approach_div = metrics.get('approach_diversity', 0)
            innovation = metrics.get('innovation_index', 0)
            
            # Status emoji
            if score >= 70:
                status = "🌟 Excellent"
            elif score >= threshold:
                status = "✅ Good"
            else:
                status = "⚠️  Needs Improvement"
            
            lines.append(
                f"| {i} | `{agent_id}` | {score:.1f} | {approach_div:.1f} | "
                f"{innovation} | {status} |"
            )
        
        lines.append("")
        return "\n".join(lines)
    
    def generate_trend_charts(self) -> str:
        """Generate ASCII/markdown trend visualizations"""
        lines = [
            "## 📈 Diversity Trends",
            ""
        ]
        
        if not self.trends_data:
            lines.append("_No trend data available._")
            return "\n".join(lines)
        
        diversity = self.trends_data.get('diversity_trend', {})
        data_points = diversity.get('data_points', [])
        
        if not data_points:
            lines.append("_Insufficient data for trends. Need at least 2 data points._")
            return "\n".join(lines)
        
        # Show trend summary
        lines.extend([
            "### Diversity Score Over Time",
            "",
            f"**Current Score:** {diversity.get('current_score', 0):.1f}/100",
            f"**Change:** {diversity.get('change', 0):+.1f} points",
            f"**Trend:** {self._trend_emoji(diversity.get('trend', 'unknown'))} "
            f"{diversity.get('trend', 'unknown').title()}",
            ""
        ])
        
        # Simple sparkline chart
        if len(data_points) >= 3:
            lines.append("```")
            lines.append(self._create_sparkline(
                [p['score'] for p in data_points],
                "Diversity Score"
            ))
            lines.append("```")
            lines.append("")
        
        # Innovation trend
        innovation = self.trends_data.get('innovation_trend', {})
        innov_points = innovation.get('data_points', [])
        
        if innov_points:
            lines.extend([
                "### Innovation Index Over Time",
                "",
                f"**Current Average:** {innovation.get('current_average', 0):.1f}%",
                f"**Change:** {innovation.get('change', 0):+.1f}%",
                f"**Trend:** {self._trend_emoji(innovation.get('trend', 'unknown'))} "
                f"{innovation.get('trend', 'unknown').title()}",
                ""
            ])
            
            if len(innov_points) >= 3:
                lines.append("```")
                lines.append(self._create_sparkline(
                    [p['index'] for p in innov_points],
                    "Innovation %"
                ))
                lines.append("```")
                lines.append("")
        
        return "\n".join(lines)
    
    def generate_pattern_library(self) -> str:
        """Generate pattern library section"""
        lines = [
            "## 📚 Pattern Library",
            "",
            "Successful diverse approaches and patterns to avoid:",
            ""
        ]
        
        if not self.pattern_library:
            lines.append("_No pattern library loaded._")
            return "\n".join(lines)
        
        # Successful patterns
        successful = self.pattern_library.get('pattern_library', {}).get(
            'successful_diverse_approaches', []
        )
        
        if successful:
            lines.extend([
                "### ✅ Successful Diverse Approaches",
                ""
            ])
            
            for pattern in successful[:5]:  # Top 5
                lines.extend([
                    f"#### {pattern.get('description', 'Unknown')}",
                    f"**Success Rate:** {pattern.get('success_rate', 0):.0%}",
                    "",
                    "Examples:",
                ])
                
                for example in pattern.get('examples', [])[:3]:
                    lines.append(f"- {example}")
                
                lines.append("")
        
        # Repetitive patterns to avoid
        repetitive = self.pattern_library.get('pattern_library', {}).get(
            'repetitive_patterns', []
        )
        
        if repetitive:
            lines.extend([
                "### ⚠️  Patterns to Avoid",
                ""
            ])
            
            for pattern in repetitive[:3]:  # Top 3
                lines.extend([
                    f"**{pattern.get('description', 'Unknown')}**",
                    f"- ⚠️  {pattern.get('warning', 'No details')}",
                    ""
                ])
        
        return "\n".join(lines)
    
    def generate_recommendations(self) -> str:
        """Generate recommendations section"""
        lines = [
            "## 💡 Recommendations",
            ""
        ]
        
        if self.trends_data and 'recommendations' in self.trends_data:
            recommendations = self.trends_data['recommendations']
            if recommendations:
                for rec in recommendations:
                    lines.append(f"- {rec}")
                lines.append("")
            else:
                lines.append("✅ All metrics look good! No specific recommendations at this time.")
                lines.append("")
        else:
            # Generate basic recommendations from current data
            if self.uniqueness_scores:
                flagged = self.uniqueness_scores.get('summary', {}).get(
                    'agents_below_threshold', 0
                )
                if flagged > 0:
                    lines.append(
                        f"- ⚠️  {flagged} agent(s) below uniqueness threshold. "
                        "Consider diversity prompts."
                    )
                else:
                    lines.append("- ✅ All agents above uniqueness threshold!")
                lines.append("")
        
        return "\n".join(lines)
    
    def generate_footer(self) -> str:
        """Generate dashboard footer"""
        lines = [
            "---",
            "",
            "## 🔧 Tools & Documentation",
            "",
            "- **Run Analysis:** `python tools/repetition-detector.py -d . --since-days 30`",
            "- **Score Uniqueness:** `python tools/uniqueness-scorer.py -d . --threshold 30`",
            "- **Analyze Trends:** `python tools/trend-analyzer.py -d . --days 90`",
            "- **Update Dashboard:** `python tools/diversity-dashboard.py -d .`",
            "",
            "---",
            "",
            f"*Generated by @investigate-champion's Diversity Dashboard Generator*",
            f"*Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}*"
        ]
        
        return "\n".join(lines)
    
    def generate_dashboard(self) -> str:
        """Generate complete dashboard"""
        sections = [
            self.generate_overview_section(),
            self.generate_agent_rankings(),
            self.generate_trend_charts(),
            self.generate_pattern_library(),
            self.generate_recommendations(),
            self.generate_footer()
        ]
        
        return "\n".join(sections)
    
    def _trend_emoji(self, trend: str) -> str:
        """Get emoji for trend"""
        emoji_map = {
            'improving': '📈',
            'increasing': '📈',
            'declining': '📉',
            'decreasing': '📉',
            'stable': '➡️',
            'new': '🆕',
            'insufficient_data': '❓',
            'unknown': '❓'
        }
        return emoji_map.get(trend, '❓')
    
    def _create_sparkline(self, values: List[float], label: str) -> str:
        """Create simple ASCII sparkline chart"""
        if not values or len(values) < 2:
            return "Insufficient data"
        
        # Normalize to 0-10 range for visualization
        min_val = min(values)
        max_val = max(values)
        range_val = max_val - min_val if max_val != min_val else 1
        
        normalized = [(v - min_val) / range_val * 10 for v in values]
        
        # Create chart
        lines = []
        lines.append(f"{label} Trend (last {len(values)} data points)")
        lines.append("")
        
        # Y-axis and bars
        for level in range(10, -1, -1):
            line = f"{level * 10:3.0f}% |"
            for val in normalized:
                if val >= level:
                    line += "█"
                else:
                    line += " "
            lines.append(line)
        
        # X-axis
        lines.append("     +" + "-" * len(values))
        
        # Show actual values
        lines.append(f"\nMin: {min_val:.1f}  Max: {max_val:.1f}  Latest: {values[-1]:.1f}")
        
        return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description='Generate diversity metrics dashboard'
    )
    parser.add_argument(
        '-d', '--directory',
        default='.',
        help='Repository directory (default: current directory)'
    )
    parser.add_argument(
        '-o', '--output',
        help='Output file for dashboard (markdown, default: docs/diversity-dashboard.md)'
    )
    
    args = parser.parse_args()
    
    # Initialize dashboard generator
    generator = DiversityDashboard(args.directory)
    
    # Load data
    print("Loading diversity data...", file=sys.stderr)
    generator.load_data()
    
    # Generate dashboard
    print("Generating dashboard...", file=sys.stderr)
    dashboard = generator.generate_dashboard()
    
    # Determine output path
    if args.output:
        output_path = Path(args.output)
    else:
        output_path = Path(args.directory) / 'docs' / 'diversity-dashboard.md'
    
    # Save dashboard
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w') as f:
        f.write(dashboard)
    
    print(f"Dashboard saved to {output_path}", file=sys.stderr)
    print("\n✅ Dashboard generated successfully!", file=sys.stderr)
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
