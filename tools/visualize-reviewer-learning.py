#!/usr/bin/env python3
"""
Visualize Autonomous Code Reviewer Learning Progress

Generates visual reports showing how the reviewer improves over time:
- Criteria evolution
- Prediction accuracy trends
- Confidence progression
- Weight adjustments

Usage:
    python visualize-reviewer-learning.py --output learning-progress.md
    python visualize-reviewer-learning.py --format html --output progress.html

Author: @construct-specialist (Infrastructure enhancement)
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
import argparse


def load_review_criteria(criteria_file: Path) -> Dict[str, Any]:
    """Load current review criteria"""
    if not criteria_file.exists():
        return {}
    
    with open(criteria_file, 'r') as f:
        return json.load(f)


def load_review_history(history_dir: Path) -> List[Dict[str, Any]]:
    """Load all review history"""
    history = []
    
    if not history_dir.exists():
        return history
    
    # Load all outcome files
    for outcome_file in sorted(history_dir.glob('outcome_*.json')):
        try:
            with open(outcome_file, 'r') as f:
                history.append(json.load(f))
        except Exception as e:
            print(f"Error loading {outcome_file}: {e}", file=sys.stderr)
    
    return history


def generate_markdown_report(criteria: Dict[str, Any], history: List[Dict[str, Any]]) -> str:
    """Generate markdown visualization of learning progress"""
    
    lines = []
    lines.append("# 🤖 Autonomous Code Reviewer - Learning Progress")
    lines.append("")
    lines.append(f"**Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    lines.append("")
    
    # Summary stats
    lines.append("## 📊 Summary Statistics")
    lines.append("")
    total_reviews = len(history)
    lines.append(f"- **Total Reviews:** {total_reviews}")
    
    if history:
        outcomes = {}
        for h in history:
            outcome = h.get('outcome', 'unknown')
            outcomes[outcome] = outcomes.get(outcome, 0) + 1
        
        lines.append(f"- **Outcome Distribution:**")
        for outcome, count in sorted(outcomes.items()):
            pct = count / total_reviews * 100
            lines.append(f"  - {outcome}: {count} ({pct:.1f}%)")
    
    lines.append("")
    
    # Current criteria status
    if criteria and 'criteria' in criteria:
        lines.append("## 🎯 Current Review Criteria")
        lines.append("")
        lines.append("| Criterion | Weight | Threshold | Success Rate | Evaluations |")
        lines.append("|-----------|--------|-----------|--------------|-------------|")
        
        for criterion in criteria['criteria']:
            name = criterion['name']
            weight = criterion['weight'] * 100
            threshold = criterion['threshold'] * 100
            success = criterion.get('success_rate', 0) * 100
            evals = criterion.get('total_evaluations', 0)
            
            lines.append(f"| {name} | {weight:.1f}% | {threshold:.1f}% | {success:.1f}% | {evals} |")
        
        lines.append("")
        
        # Calculate overall confidence
        avg_success = sum(c.get('success_rate', 0) for c in criteria['criteria']) / len(criteria['criteria'])
        data_confidence = min(1.0, total_reviews / 50)
        overall_confidence = (avg_success * 0.6 + data_confidence * 0.4) * 100
        
        lines.append(f"**Overall Confidence:** {overall_confidence:.1f}%")
        lines.append("")
    
    # Learning trends
    if len(history) > 1:
        lines.append("## 📈 Learning Trends")
        lines.append("")
        
        # Accuracy over time
        lines.append("### Prediction Accuracy Evolution")
        lines.append("")
        lines.append("Recent prediction accuracy:")
        lines.append("")
        
        # Show last 10 predictions
        recent = history[-10:]
        for h in recent:
            pr_num = h.get('pr_number', 'unknown')
            score = h.get('review_score', 0) * 100
            outcome = h.get('outcome', 'unknown')
            timestamp = h.get('outcome_timestamp', '')[:10]
            
            outcome_emoji = "✅" if outcome in ['merged', 'revised'] else "❌"
            lines.append(f"- **PR #{pr_num}** ({timestamp}): Score {score:.1f}% → {outcome_emoji} {outcome}")
        
        lines.append("")
    
    # Recommendations
    lines.append("## 💡 Recommendations")
    lines.append("")
    
    if total_reviews < 10:
        lines.append("- ⚠️ **Limited data**: Need more reviews (current: {}, target: 50+)".format(total_reviews))
        lines.append("- 🎯 Continue collecting reviews to improve accuracy")
    elif total_reviews < 50:
        lines.append("- 📊 **Growing dataset**: Confidence improving (current: {}, target: 50+)".format(total_reviews))
        lines.append("- 🚀 System is learning and adapting")
    else:
        lines.append("- ✅ **Mature dataset**: System has sufficient data for reliable predictions")
        lines.append("- 🎓 Focus on fine-tuning criteria weights")
    
    if criteria and 'criteria' in criteria:
        # Check for criteria that need attention
        for criterion in criteria['criteria']:
            success_rate = criterion.get('success_rate', 0)
            evals = criterion.get('total_evaluations', 0)
            
            if evals > 5 and success_rate < 0.6:
                lines.append(f"- ⚠️ **{criterion['name']}**: Low success rate ({success_rate*100:.1f}%), consider adjusting patterns")
    
    lines.append("")
    lines.append("---")
    lines.append("*Generated by **@construct-specialist** visualization tool*")
    
    return '\n'.join(lines)


def main():
    """Main CLI interface"""
    parser = argparse.ArgumentParser(
        description="Visualize autonomous code reviewer learning progress"
    )
    parser.add_argument('--output', type=str, default='reviewer-learning-progress.md',
                        help='Output file path')
    parser.add_argument('--format', choices=['markdown', 'html'], default='markdown',
                        help='Output format')
    parser.add_argument('--criteria-file', type=str, default='learnings/review_criteria.json',
                        help='Path to criteria file')
    parser.add_argument('--history-dir', type=str, default='learnings/review_history',
                        help='Path to review history directory')
    
    args = parser.parse_args()
    
    # Load data
    criteria_file = Path(args.criteria_file)
    history_dir = Path(args.history_dir)
    
    criteria = load_review_criteria(criteria_file)
    history = load_review_history(history_dir)
    
    # Generate report
    if args.format == 'markdown':
        report = generate_markdown_report(criteria, history)
    else:
        print("HTML format not yet implemented", file=sys.stderr)
        sys.exit(1)
    
    # Write output
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w') as f:
        f.write(report)
    
    print(f"✅ Learning progress report generated: {output_path}")
    print(f"📊 Reviews analyzed: {len(history)}")
    print(f"🎯 Criteria tracked: {len(criteria.get('criteria', []))}")


if __name__ == '__main__':
    main()
