#!/usr/bin/env python3
"""
AI Diversity Trend Analyzer

Analyzes historical repetition detection data to identify trends in
AI agent diversity, uniqueness, and innovation over time.

Created by @investigate-champion for comprehensive pattern analysis.
"""

import argparse
import json
import sys
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import statistics


class TrendAnalyzer:
    """Analyzes diversity trends from historical data"""
    
    def __init__(self, repo_dir: str):
        self.repo_dir = Path(repo_dir)
        self.history_dir = self.repo_dir / 'analysis' / 'repetition-history'
        self.historical_data = []
        
    def load_historical_data(self, days: int = 90) -> List[Dict]:
        """Load all historical snapshots within the specified time range"""
        if not self.history_dir.exists():
            print(f"Warning: History directory does not exist: {self.history_dir}", 
                  file=sys.stderr)
            return []
        
        cutoff_date = datetime.now() - timedelta(days=days)
        snapshots = []
        
        for json_file in sorted(self.history_dir.glob('*.json')):
            # Skip 'latest.json' if it's a symlink
            if json_file.name == 'latest.json':
                continue
                
            try:
                with open(json_file, 'r') as f:
                    data = json.load(f)
                    
                # Parse timestamp from filename (format: YYYY-MM-DD-HH-MM-SS.json)
                timestamp_str = json_file.stem  # Remove .json extension
                try:
                    timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d-%H-%M-%S')
                except ValueError:
                    # If filename doesn't match format, try to get from metadata
                    if 'metadata' in data and 'generated_at' in data['metadata']:
                        timestamp = datetime.fromisoformat(
                            data['metadata']['generated_at'].replace('Z', '+00:00')
                        )
                    else:
                        continue
                
                if timestamp >= cutoff_date:
                    data['_timestamp'] = timestamp
                    data['_filename'] = json_file.name
                    snapshots.append(data)
                    
            except (json.JSONDecodeError, KeyError, ValueError) as e:
                print(f"Warning: Could not load {json_file}: {e}", file=sys.stderr)
                continue
        
        return snapshots
    
    def calculate_diversity_trend(self) -> Dict[str, Any]:
        """Calculate overall diversity trend from historical data"""
        if not self.historical_data:
            return {
                'trend': 'insufficient_data',
                'change': 0,
                'current_score': 0,
                'previous_score': 0
            }
        
        # Get diversity scores over time
        scores_by_time = []
        for snapshot in self.historical_data:
            if 'summary' in snapshot and 'total_agents' in snapshot['summary']:
                total_agents = snapshot['summary']['total_agents']
                flags = len(snapshot.get('repetition_flags', []))
                
                # Simple diversity score: fewer flags = higher diversity
                if total_agents > 0:
                    diversity_score = max(0, 100 - (flags / total_agents * 100))
                else:
                    diversity_score = 50  # Neutral when no agents
                
                scores_by_time.append({
                    'timestamp': snapshot['_timestamp'],
                    'score': diversity_score,
                    'agents': total_agents,
                    'flags': flags
                })
        
        if len(scores_by_time) < 2:
            return {
                'trend': 'insufficient_data',
                'change': 0,
                'current_score': scores_by_time[0]['score'] if scores_by_time else 0,
                'previous_score': 0,
                'data_points': scores_by_time
            }
        
        # Calculate trend
        recent_score = scores_by_time[-1]['score']
        older_score = scores_by_time[0]['score']
        change = recent_score - older_score
        
        # Determine trend direction
        if change > 10:
            trend = 'improving'
        elif change < -10:
            trend = 'declining'
        else:
            trend = 'stable'
        
        return {
            'trend': trend,
            'change': change,
            'current_score': recent_score,
            'previous_score': older_score,
            'data_points': scores_by_time,
            'average_score': statistics.mean([s['score'] for s in scores_by_time]),
            'score_stdev': statistics.stdev([s['score'] for s in scores_by_time]) 
                          if len(scores_by_time) > 1 else 0
        }
    
    def calculate_agent_trends(self) -> Dict[str, Any]:
        """Calculate per-agent diversity trends"""
        agent_history = defaultdict(list)
        
        for snapshot in self.historical_data:
            timestamp = snapshot['_timestamp']
            
            # Track agents mentioned in the snapshot
            if 'summary' in snapshot and 'agents' in snapshot['summary']:
                for agent_id in snapshot['summary']['agents']:
                    # Count flags for this agent
                    agent_flags = [
                        f for f in snapshot.get('repetition_flags', [])
                        if f.get('agent_id') == agent_id
                    ]
                    
                    agent_history[agent_id].append({
                        'timestamp': timestamp,
                        'flags': len(agent_flags),
                        'total_contributions': 1  # Simplified
                    })
        
        # Analyze trends per agent
        agent_trends = {}
        for agent_id, history in agent_history.items():
            if len(history) < 2:
                agent_trends[agent_id] = {
                    'trend': 'new',
                    'data_points': len(history)
                }
                continue
            
            # Calculate flag trend
            recent_flags = statistics.mean([h['flags'] for h in history[-3:]])
            older_flags = statistics.mean([h['flags'] for h in history[:3]])
            
            if recent_flags < older_flags - 0.5:
                trend = 'improving'
            elif recent_flags > older_flags + 0.5:
                trend = 'declining'
            else:
                trend = 'stable'
            
            agent_trends[agent_id] = {
                'trend': trend,
                'current_avg_flags': recent_flags,
                'previous_avg_flags': older_flags,
                'total_data_points': len(history),
                'history': history
            }
        
        return agent_trends
    
    def calculate_innovation_trend(self) -> Dict[str, Any]:
        """Calculate innovation index trends"""
        innovation_scores = []
        
        for snapshot in self.historical_data:
            # Count unique patterns or approaches
            unique_approaches = len(snapshot.get('solution_approaches', {}))
            total_contributions = snapshot.get('summary', {}).get('total_contributions', 0)
            
            if total_contributions > 0:
                innovation_index = (unique_approaches / total_contributions) * 100
            else:
                innovation_index = 0
            
            innovation_scores.append({
                'timestamp': snapshot['_timestamp'],
                'index': innovation_index,
                'unique_approaches': unique_approaches,
                'total_contributions': total_contributions
            })
        
        if not innovation_scores:
            return {'trend': 'insufficient_data', 'data_points': []}
        
        # Calculate trend
        if len(innovation_scores) >= 2:
            recent_avg = statistics.mean([s['index'] for s in innovation_scores[-3:]])
            older_avg = statistics.mean([s['index'] for s in innovation_scores[:3]])
            change = recent_avg - older_avg
            
            if change > 5:
                trend = 'increasing'
            elif change < -5:
                trend = 'decreasing'
            else:
                trend = 'stable'
        else:
            trend = 'insufficient_data'
            change = 0
            recent_avg = innovation_scores[0]['index']
            older_avg = recent_avg
        
        return {
            'trend': trend,
            'change': change,
            'current_average': recent_avg,
            'previous_average': older_avg,
            'data_points': innovation_scores
        }
    
    def generate_summary_report(self) -> Dict[str, Any]:
        """Generate comprehensive trend analysis report"""
        return {
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'analysis_period_days': len(self.historical_data),
                'snapshots_analyzed': len(self.historical_data),
                'earliest_snapshot': self.historical_data[0]['_timestamp'].isoformat() 
                                   if self.historical_data else None,
                'latest_snapshot': self.historical_data[-1]['_timestamp'].isoformat() 
                                 if self.historical_data else None
            },
            'diversity_trend': self.calculate_diversity_trend(),
            'agent_trends': self.calculate_agent_trends(),
            'innovation_trend': self.calculate_innovation_trend(),
            'recommendations': self._generate_recommendations()
        }
    
    def _generate_recommendations(self) -> List[str]:
        """Generate actionable recommendations based on trends"""
        recommendations = []
        
        diversity_trend = self.calculate_diversity_trend()
        
        if diversity_trend['trend'] == 'declining':
            recommendations.append(
                "⚠️  Diversity is declining. Consider injecting diversity prompts "
                "into agent instructions."
            )
        elif diversity_trend['trend'] == 'improving':
            recommendations.append(
                "✅ Diversity is improving! Continue current approach."
            )
        
        innovation_trend = self.calculate_innovation_trend()
        if innovation_trend['trend'] == 'decreasing':
            recommendations.append(
                "💡 Innovation index is decreasing. Encourage agents to explore "
                "new patterns and approaches."
            )
        
        if diversity_trend['trend'] == 'insufficient_data':
            recommendations.append(
                "📊 Insufficient historical data. Continue collecting data for "
                "at least 7 days to establish trends."
            )
        
        return recommendations
    
    def save_trends(self, output_path: Path):
        """Save trend analysis to file"""
        report = self.generate_summary_report()
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        return report


def main():
    parser = argparse.ArgumentParser(
        description='Analyze diversity trends from historical repetition detection data'
    )
    parser.add_argument(
        '-d', '--directory',
        default='.',
        help='Repository directory (default: current directory)'
    )
    parser.add_argument(
        '--days',
        type=int,
        default=90,
        help='Number of days of history to analyze (default: 90)'
    )
    parser.add_argument(
        '-o', '--output',
        help='Output file for trend analysis (JSON, default: analysis/diversity-trends.json)'
    )
    
    args = parser.parse_args()
    
    # Initialize analyzer
    analyzer = TrendAnalyzer(args.directory)
    
    # Load historical data
    print(f"Loading historical data (last {args.days} days)...", file=sys.stderr)
    analyzer.historical_data = analyzer.load_historical_data(args.days)
    
    if not analyzer.historical_data:
        print("⚠️  No historical data found. Run repetition detector first to generate data.", 
              file=sys.stderr)
        return 1
    
    print(f"Loaded {len(analyzer.historical_data)} snapshots", file=sys.stderr)
    
    # Generate trend analysis
    print("Analyzing trends...", file=sys.stderr)
    
    # Determine output path
    if args.output:
        output_path = Path(args.output)
    else:
        output_path = Path(args.directory) / 'analysis' / 'diversity-trends.json'
    
    # Save report
    report = analyzer.save_trends(output_path)
    print(f"Trend analysis saved to {output_path}", file=sys.stderr)
    
    # Print summary
    diversity = report['diversity_trend']
    innovation = report['innovation_trend']
    
    print(f"\n📊 Trend Analysis Summary:", file=sys.stderr)
    print(f"   Diversity Trend: {diversity['trend']}", file=sys.stderr)
    print(f"   Innovation Trend: {innovation['trend']}", file=sys.stderr)
    print(f"   Snapshots Analyzed: {len(analyzer.historical_data)}", file=sys.stderr)
    
    if report['recommendations']:
        print(f"\n💡 Recommendations:", file=sys.stderr)
        for rec in report['recommendations']:
            print(f"   {rec}", file=sys.stderr)
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
