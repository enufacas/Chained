#!/usr/bin/env python3
"""
Creativity & Innovation Leaderboard Generator

Generates visualizations and reports for agent creativity metrics:
- Top creative agents (hall of fame)
- Most innovative contributions
- Creativity trends over time
- Innovation velocity tracking

Usage:
    python creativity-leaderboard.py [--output FILE] [--format {markdown|json|html}]
"""

import json
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from collections import defaultdict
import argparse


# Constants
REGISTRY_FILE = Path(".github/agent-system/registry.json")
METRICS_DIR = Path(".github/agent-system/metrics")
CREATIVITY_CACHE_DIR = METRICS_DIR / "creativity"


def load_registry() -> Dict[str, Any]:
    """Load the agent registry"""
    if not REGISTRY_FILE.exists():
        return {'agents': [], 'hall_of_fame': []}
    
    with open(REGISTRY_FILE, 'r') as f:
        return json.load(f)


def load_agent_creativity_metrics(agent_id: str) -> Optional[Dict[str, Any]]:
    """Load latest creativity metrics for an agent"""
    latest_file = CREATIVITY_CACHE_DIR / agent_id / "latest.json"
    
    if not latest_file.exists():
        return None
    
    try:
        with open(latest_file, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"⚠️  Warning: Error loading metrics for {agent_id}: {e}", file=sys.stderr)
        return None


def load_all_creativity_metrics() -> Dict[str, List[Dict[str, Any]]]:
    """Load all creativity metrics for all agents"""
    all_metrics = defaultdict(list)
    
    if not CREATIVITY_CACHE_DIR.exists():
        return dict(all_metrics)
    
    for agent_dir in CREATIVITY_CACHE_DIR.iterdir():
        if not agent_dir.is_dir():
            continue
        
        agent_id = agent_dir.name
        
        for metrics_file in sorted(agent_dir.glob("*.json")):
            if metrics_file.name == "latest.json":
                continue
            
            try:
                with open(metrics_file, 'r') as f:
                    metrics = json.load(f)
                    all_metrics[agent_id].append(metrics)
            except Exception as e:
                print(f"⚠️  Warning: Error loading {metrics_file}: {e}", file=sys.stderr)
    
    return dict(all_metrics)


def calculate_innovation_velocity(metrics_history: List[Dict[str, Any]]) -> float:
    """
    Calculate innovation velocity - rate of new creative patterns over time.
    
    Args:
        metrics_history: List of historical creativity metrics
        
    Returns:
        Innovation velocity (new patterns per day)
    """
    if len(metrics_history) < 2:
        return 0.0
    
    # Sort by timestamp
    sorted_metrics = sorted(metrics_history, key=lambda x: x.get('timestamp', ''))
    
    # Count new patterns over time
    total_new_patterns = sum(
        len(m.get('indicators', {}).get('novel_patterns', []))
        for m in sorted_metrics
    )
    
    # Calculate time span
    try:
        first_time = datetime.fromisoformat(sorted_metrics[0]['timestamp'].replace('Z', '+00:00'))
        last_time = datetime.fromisoformat(sorted_metrics[-1]['timestamp'].replace('Z', '+00:00'))
        time_span_days = max(1, (last_time - first_time).total_seconds() / 86400)
        
        return total_new_patterns / time_span_days
    except Exception:
        return 0.0


def identify_breakthrough_contributions(all_metrics: Dict[str, List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
    """
    Identify breakthrough contributions across all agents.
    
    A breakthrough is defined as:
    - High novelty (>70%)
    - High impact (>75%)
    - Significant number of novel patterns
    
    Returns:
        List of breakthrough contributions with agent info
    """
    breakthroughs = []
    
    for agent_id, metrics_list in all_metrics.items():
        for metrics in metrics_list:
            score = metrics.get('score', {})
            indicators = metrics.get('indicators', {})
            
            novelty = score.get('novelty', 0)
            impact = score.get('impact', 0)
            novel_patterns = indicators.get('novel_patterns', [])
            
            # Check if this is a breakthrough
            if novelty > 0.7 and impact > 0.75 and len(novel_patterns) >= 3:
                breakthroughs.append({
                    'agent_id': agent_id,
                    'timestamp': metrics.get('timestamp'),
                    'novelty': novelty,
                    'impact': impact,
                    'diversity': score.get('diversity', 0),
                    'overall_creativity': score.get('overall', 0),
                    'novel_patterns': novel_patterns,
                    'breakthrough_moments': indicators.get('breakthrough_moments', [])
                })
    
    # Sort by overall creativity score
    breakthroughs.sort(key=lambda x: x['overall_creativity'], reverse=True)
    
    return breakthroughs


def generate_markdown_leaderboard(
    registry: Dict[str, Any],
    all_metrics: Dict[str, List[Dict[str, Any]]]
) -> str:
    """Generate markdown leaderboard report"""
    
    output = "# 🎨 Creativity & Innovation Leaderboard\n\n"
    output += f"**Generated**: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}\n\n"
    output += "---\n\n"
    
    # Top Creative Agents
    output += "## 🌟 Top Creative Agents\n\n"
    
    agent_creativity = []
    
    for agent_id in all_metrics.keys():
        metrics = load_agent_creativity_metrics(agent_id)
        if metrics:
            agent_name = "Unknown"
            specialization = "Unknown"
            
            # Find agent in registry
            for agent in registry.get('agents', []) + registry.get('hall_of_fame', []):
                if agent.get('id') == agent_id:
                    agent_name = agent.get('name', agent_id)
                    specialization = agent.get('specialization', 'Unknown')
                    break
            
            score = metrics.get('score', {})
            agent_creativity.append({
                'agent_id': agent_id,
                'agent_name': agent_name,
                'specialization': specialization,
                'creativity': score.get('overall', 0),
                'novelty': score.get('novelty', 0),
                'diversity': score.get('diversity', 0),
                'impact': score.get('impact', 0),
                'learning': score.get('learning', 0)
            })
    
    # Sort by creativity score
    agent_creativity.sort(key=lambda x: x['creativity'], reverse=True)
    
    if agent_creativity:
        output += "| Rank | Agent | Specialization | Creativity | Novelty | Diversity | Impact | Learning |\n"
        output += "|------|-------|----------------|------------|---------|-----------|--------|----------|\n"
        
        for idx, agent in enumerate(agent_creativity[:10], 1):
            medal = "🥇" if idx == 1 else "🥈" if idx == 2 else "🥉" if idx == 3 else f"{idx}."
            output += f"| {medal} | {agent['agent_name']} | {agent['specialization']} | "
            output += f"{agent['creativity']:.1%} | {agent['novelty']:.1%} | "
            output += f"{agent['diversity']:.1%} | {agent['impact']:.1%} | {agent['learning']:.1%} |\n"
    else:
        output += "*No creativity metrics available yet.*\n"
    
    output += "\n"
    
    # Breakthrough Contributions
    output += "## 💡 Breakthrough Contributions\n\n"
    
    breakthroughs = identify_breakthrough_contributions(all_metrics)
    
    if breakthroughs:
        output += "*Contributions with exceptional novelty and impact:*\n\n"
        
        for breakthrough in breakthroughs[:5]:
            agent_name = breakthrough['agent_id']
            
            # Find agent name
            for agent in registry.get('agents', []) + registry.get('hall_of_fame', []):
                if agent.get('id') == breakthrough['agent_id']:
                    agent_name = agent.get('name', agent_name)
                    break
            
            output += f"### {agent_name}\n\n"
            output += f"**Timestamp**: {breakthrough['timestamp']}\n\n"
            output += f"**Creativity Score**: {breakthrough['overall_creativity']:.1%}\n"
            output += f"- Novelty: {breakthrough['novelty']:.1%}\n"
            output += f"- Impact: {breakthrough['impact']:.1%}\n"
            output += f"- Diversity: {breakthrough['diversity']:.1%}\n\n"
            
            if breakthrough['novel_patterns']:
                output += f"**Novel Patterns** ({len(breakthrough['novel_patterns'])}):\n"
                for pattern in breakthrough['novel_patterns'][:5]:
                    output += f"- `{pattern}`\n"
                output += "\n"
            
            if breakthrough['breakthrough_moments']:
                output += "**Breakthrough Moments**:\n"
                for moment in breakthrough['breakthrough_moments']:
                    output += f"- {moment}\n"
                output += "\n"
    else:
        output += "*No breakthrough contributions identified yet.*\n\n"
    
    # Innovation Velocity
    output += "## 🚀 Innovation Velocity\n\n"
    output += "*Rate of new creative patterns over time:*\n\n"
    
    innovation_rates = []
    
    for agent_id, metrics_list in all_metrics.items():
        if len(metrics_list) >= 2:
            velocity = calculate_innovation_velocity(metrics_list)
            
            if velocity > 0:
                agent_name = agent_id
                
                # Find agent name
                for agent in registry.get('agents', []) + registry.get('hall_of_fame', []):
                    if agent.get('id') == agent_id:
                        agent_name = agent.get('name', agent_name)
                        break
                
                innovation_rates.append({
                    'agent_name': agent_name,
                    'velocity': velocity
                })
    
    innovation_rates.sort(key=lambda x: x['velocity'], reverse=True)
    
    if innovation_rates:
        output += "| Agent | New Patterns per Day |\n"
        output += "|-------|---------------------|\n"
        
        for rate in innovation_rates[:10]:
            output += f"| {rate['agent_name']} | {rate['velocity']:.2f} |\n"
    else:
        output += "*Not enough historical data to calculate innovation velocity.*\n"
    
    output += "\n---\n\n"
    output += "*🤖 Powered by the Chained Autonomous AI Ecosystem - Where creativity is measured, not assumed!*\n"
    
    return output


def generate_json_leaderboard(
    registry: Dict[str, Any],
    all_metrics: Dict[str, List[Dict[str, Any]]]
) -> Dict[str, Any]:
    """Generate JSON leaderboard data"""
    
    leaderboard = {
        'generated_at': datetime.now(timezone.utc).isoformat(),
        'top_creative_agents': [],
        'breakthrough_contributions': [],
        'innovation_velocity': []
    }
    
    # Top creative agents
    for agent_id in all_metrics.keys():
        metrics = load_agent_creativity_metrics(agent_id)
        if metrics:
            agent_name = agent_id
            specialization = "Unknown"
            
            for agent in registry.get('agents', []) + registry.get('hall_of_fame', []):
                if agent.get('id') == agent_id:
                    agent_name = agent.get('name', agent_id)
                    specialization = agent.get('specialization', 'Unknown')
                    break
            
            score = metrics.get('score', {})
            leaderboard['top_creative_agents'].append({
                'agent_id': agent_id,
                'agent_name': agent_name,
                'specialization': specialization,
                'creativity_score': score.get('overall', 0),
                'novelty': score.get('novelty', 0),
                'diversity': score.get('diversity', 0),
                'impact': score.get('impact', 0),
                'learning': score.get('learning', 0)
            })
    
    # Sort by creativity
    leaderboard['top_creative_agents'].sort(key=lambda x: x['creativity_score'], reverse=True)
    
    # Breakthrough contributions
    leaderboard['breakthrough_contributions'] = identify_breakthrough_contributions(all_metrics)
    
    # Innovation velocity
    for agent_id, metrics_list in all_metrics.items():
        if len(metrics_list) >= 2:
            velocity = calculate_innovation_velocity(metrics_list)
            
            if velocity > 0:
                leaderboard['innovation_velocity'].append({
                    'agent_id': agent_id,
                    'velocity': velocity
                })
    
    leaderboard['innovation_velocity'].sort(key=lambda x: x['velocity'], reverse=True)
    
    return leaderboard


def main():
    """CLI entry point"""
    parser = argparse.ArgumentParser(
        description='Creativity & Innovation Leaderboard Generator',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument(
        '--output',
        type=str,
        help='Output file (defaults to stdout)'
    )
    parser.add_argument(
        '--format',
        choices=['markdown', 'json', 'html'],
        default='markdown',
        help='Output format (default: markdown)'
    )
    
    args = parser.parse_args()
    
    print("🎨 Generating creativity leaderboard...", file=sys.stderr)
    
    # Load data
    registry = load_registry()
    all_metrics = load_all_creativity_metrics()
    
    print(f"📊 Loaded metrics for {len(all_metrics)} agents", file=sys.stderr)
    
    # Generate output
    if args.format == 'markdown':
        output = generate_markdown_leaderboard(registry, all_metrics)
    elif args.format == 'json':
        data = generate_json_leaderboard(registry, all_metrics)
        output = json.dumps(data, indent=2)
    else:
        print(f"❌ Format '{args.format}' not implemented yet", file=sys.stderr)
        sys.exit(1)
    
    # Write output
    if args.output:
        with open(args.output, 'w') as f:
            f.write(output)
        print(f"✅ Leaderboard written to {args.output}", file=sys.stderr)
    else:
        print(output)


if __name__ == '__main__':
    main()
