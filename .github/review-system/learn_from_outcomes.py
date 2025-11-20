#!/usr/bin/env python3
"""
Learning module for autonomous code reviewer.

Analyzes closed PRs, correlates review results with outcomes,
and evolves criteria based on effectiveness.

Created by: @workflows-tech-lead
"""

import json
import os
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, List, Any


def fetch_closed_prs(repo: str, days: int = 30) -> List[Dict[str, Any]]:
    """
    Fetch closed PRs from the last N days using GitHub CLI.
    
    Args:
        repo: Repository in format 'owner/repo'
        days: Number of days to look back
        
    Returns:
        List of PR information dicts
    """
    cutoff_date = (datetime.now(timezone.utc) - timedelta(days=days)).strftime('%Y-%m-%d')
    
    # Fetch closed PRs
    result = subprocess.run(
        [
            'gh', 'pr', 'list',
            '--repo', repo,
            '--state', 'closed',
            '--limit', '100',
            '--json', 'number,title,state,mergedAt,closedAt,author,labels',
            '--search', f'closed:>={cutoff_date}'
        ],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print(f"Error fetching PRs: {result.stderr}", file=sys.stderr)
        return []
    
    try:
        prs = json.loads(result.stdout)
        print(f"Fetched {len(prs)} closed PRs")
        return prs
    except json.JSONDecodeError as e:
        print(f"Error parsing PR data: {e}", file=sys.stderr)
        return []


def load_review_results(reviews_dir: Path) -> Dict[str, Dict[str, Any]]:
    """
    Load all review results from the reviews directory.
    
    Returns:
        Dict mapping PR number to review results
    """
    reviews = {}
    
    if not reviews_dir.exists():
        return reviews
    
    for review_file in reviews_dir.glob('pr-*.json'):
        try:
            # Extract PR number from filename (pr-123-timestamp.json)
            parts = review_file.stem.split('-')
            if len(parts) >= 2:
                pr_number = parts[1]
                
                with open(review_file, 'r') as f:
                    review_data = json.load(f)
                    
                # Store latest review for each PR
                if pr_number not in reviews:
                    reviews[pr_number] = review_data
                else:
                    # Keep the most recent review
                    existing_ts = reviews[pr_number].get('timestamp', '')
                    new_ts = review_data.get('timestamp', '')
                    if new_ts > existing_ts:
                        reviews[pr_number] = review_data
        except Exception as e:
            print(f"Warning: Could not load {review_file}: {e}", file=sys.stderr)
    
    return reviews


def calculate_effectiveness(
    reviews: Dict[str, Dict[str, Any]],
    prs: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Calculate effectiveness of criteria based on PR outcomes.
    
    Args:
        reviews: Review results by PR number
        prs: List of PR information
        
    Returns:
        Effectiveness metrics
    """
    # Create PR outcome map
    pr_outcomes = {}
    for pr in prs:
        pr_num = str(pr['number'])
        pr_outcomes[pr_num] = {
            'merged': pr.get('mergedAt') is not None,
            'closed_without_merge': pr.get('mergedAt') is None,
            'labels': [label['name'] for label in pr.get('labels', [])]
        }
    
    # Match reviews with outcomes
    matched_data = []
    for pr_num, review in reviews.items():
        if pr_num in pr_outcomes:
            outcome = pr_outcomes[pr_num]
            score = review.get('results', {}).get('overall_score', 0)
            
            matched_data.append({
                'pr_number': pr_num,
                'score': score,
                'merged': outcome['merged'],
                'review': review
            })
    
    print(f"Matched {len(matched_data)} reviews with outcomes")
    
    if not matched_data:
        return {
            'total_matched': 0,
            'merge_rate': 0,
            'correlation': 0,
            'category_effectiveness': {}
        }
    
    # Calculate overall merge rate
    merged_count = sum(1 for d in matched_data if d['merged'])
    merge_rate = merged_count / len(matched_data)
    
    # Calculate correlation between score and merge success
    # Simple correlation: do higher scores correlate with merges?
    merged_scores = [d['score'] for d in matched_data if d['merged']]
    rejected_scores = [d['score'] for d in matched_data if not d['merged']]
    
    avg_merged_score = sum(merged_scores) / len(merged_scores) if merged_scores else 0
    avg_rejected_score = sum(rejected_scores) / len(rejected_scores) if rejected_scores else 0
    
    # Correlation is the difference (higher is better)
    correlation = avg_merged_score - avg_rejected_score
    
    # Calculate per-category effectiveness
    category_effectiveness = {}
    
    for data in matched_data:
        categories = data.get('review', {}).get('results', {}).get('categories', {})
        for cat_name, cat_score in categories.items():
            if cat_name not in category_effectiveness:
                category_effectiveness[cat_name] = {
                    'merged_scores': [],
                    'rejected_scores': []
                }
            
            if data['merged']:
                category_effectiveness[cat_name]['merged_scores'].append(cat_score)
            else:
                category_effectiveness[cat_name]['rejected_scores'].append(cat_score)
    
    # Calculate effectiveness per category
    for cat_name, scores in category_effectiveness.items():
        merged = scores['merged_scores']
        rejected = scores['rejected_scores']
        
        avg_merged = sum(merged) / len(merged) if merged else 0
        avg_rejected = sum(rejected) / len(rejected) if rejected else 0
        
        # Effectiveness is how much better merged PRs score in this category
        effectiveness = avg_merged - avg_rejected
        
        category_effectiveness[cat_name] = {
            'effectiveness': effectiveness,
            'avg_merged_score': avg_merged,
            'avg_rejected_score': avg_rejected,
            'sample_size': len(merged) + len(rejected)
        }
    
    return {
        'total_matched': len(matched_data),
        'merge_rate': merge_rate,
        'correlation': correlation,
        'avg_merged_score': avg_merged_score,
        'avg_rejected_score': avg_rejected_score,
        'category_effectiveness': category_effectiveness
    }


def evolve_criteria(
    criteria: Dict[str, Any],
    effectiveness: Dict[str, Any],
    learning_rate: float = 0.1
) -> Dict[str, Any]:
    """
    Evolve criteria based on effectiveness metrics.
    
    Args:
        criteria: Current criteria configuration
        effectiveness: Effectiveness metrics
        learning_rate: How quickly to adapt (0.0 - 1.0)
        
    Returns:
        Updated criteria
    """
    category_eff = effectiveness.get('category_effectiveness', {})
    
    # Only evolve if we have enough data
    min_reviews = criteria.get('evolution_config', {}).get('min_reviews_before_adjustment', 10)
    if effectiveness.get('total_matched', 0) < min_reviews:
        print(f"Not enough data to evolve ({effectiveness.get('total_matched', 0)} < {min_reviews})")
        return criteria
    
    print("Evolving criteria based on effectiveness...")
    
    # Update category weights based on effectiveness
    for cat_name, cat_data in criteria['criteria'].items():
        if cat_name in category_eff:
            eff_data = category_eff[cat_name]
            eff_score = eff_data['effectiveness']
            
            # Adjust weight: increase for effective categories, decrease for ineffective
            current_weight = cat_data['weight']
            
            # Effectiveness > 0.1 = effective, < -0.1 = ineffective
            if eff_score > 0.1:
                # Increase weight
                adjustment = learning_rate * eff_score
                new_weight = min(2.0, current_weight + adjustment)
                print(f"  {cat_name}: effectiveness={eff_score:.3f}, weight {current_weight:.2f} → {new_weight:.2f}")
            elif eff_score < -0.1:
                # Decrease weight
                adjustment = learning_rate * abs(eff_score)
                new_weight = max(0.1, current_weight - adjustment)
                print(f"  {cat_name}: effectiveness={eff_score:.3f}, weight {current_weight:.2f} → {new_weight:.2f}")
            else:
                # Neutral - no change
                new_weight = current_weight
                print(f"  {cat_name}: effectiveness={eff_score:.3f}, weight unchanged at {current_weight:.2f}")
            
            cat_data['weight'] = new_weight
            cat_data['effectiveness_score'] = eff_score
    
    # Update metadata
    criteria['metadata']['total_reviews'] = effectiveness.get('total_matched', 0)
    criteria['metadata']['success_rate'] = effectiveness.get('merge_rate', 0)
    criteria['last_updated'] = datetime.now(timezone.utc).isoformat()
    
    # Add to history
    if 'effectiveness_history' not in criteria:
        criteria['effectiveness_history'] = []
    
    criteria['effectiveness_history'].append({
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'total_reviews': effectiveness.get('total_matched', 0),
        'merge_rate': effectiveness.get('merge_rate', 0),
        'correlation': effectiveness.get('correlation', 0),
        'category_effectiveness': {
            cat: data['effectiveness']
            for cat, data in category_eff.items()
        }
    })
    
    # Keep only last 50 history entries
    criteria['effectiveness_history'] = criteria['effectiveness_history'][-50:]
    
    return criteria


def generate_learning_report(
    effectiveness: Dict[str, Any],
    criteria_before: Dict[str, Any],
    criteria_after: Dict[str, Any]
) -> str:
    """Generate a markdown report of the learning process."""
    lines = []
    
    lines.append("# 🧠 Autonomous Reviewer Learning Report")
    lines.append("")
    lines.append(f"**Generated:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}")
    lines.append("")
    
    lines.append("## 📊 Overall Metrics")
    lines.append("")
    lines.append(f"- **Total Reviews Analyzed:** {effectiveness['total_matched']}")
    lines.append(f"- **Merge Rate:** {effectiveness['merge_rate']:.1%}")
    lines.append(f"- **Score Correlation:** {effectiveness['correlation']:.3f}")
    lines.append(f"- **Avg Score (Merged):** {effectiveness['avg_merged_score']:.1%}")
    lines.append(f"- **Avg Score (Rejected):** {effectiveness['avg_rejected_score']:.1%}")
    lines.append("")
    
    lines.append("## 🎯 Category Effectiveness")
    lines.append("")
    lines.append("| Category | Effectiveness | Merged Avg | Rejected Avg | Weight Change |")
    lines.append("|----------|--------------|------------|--------------|---------------|")
    
    for cat_name, eff_data in effectiveness['category_effectiveness'].items():
        eff = eff_data['effectiveness']
        merged_avg = eff_data['avg_merged_score']
        rejected_avg = eff_data['avg_rejected_score']
        
        weight_before = criteria_before['criteria'].get(cat_name, {}).get('weight', 0)
        weight_after = criteria_after['criteria'].get(cat_name, {}).get('weight', 0)
        weight_change = weight_after - weight_before
        
        eff_emoji = "✅" if eff > 0.1 else "⚠️" if eff < -0.1 else "➖"
        change_str = f"+{weight_change:.2f}" if weight_change > 0 else f"{weight_change:.2f}"
        
        lines.append(f"| {cat_name.replace('_', ' ').title()} {eff_emoji} | {eff:.3f} | {merged_avg:.1%} | {rejected_avg:.1%} | {change_str} |")
    
    lines.append("")
    lines.append("## 🔄 Criteria Evolution")
    lines.append("")
    
    any_changes = False
    for cat_name, cat_data in criteria_after['criteria'].items():
        weight_before = criteria_before['criteria'].get(cat_name, {}).get('weight', 0)
        weight_after = cat_data['weight']
        
        if abs(weight_after - weight_before) > 0.01:
            any_changes = True
            lines.append(f"- **{cat_name.replace('_', ' ').title()}**: weight {weight_before:.2f} → {weight_after:.2f}")
    
    if not any_changes:
        lines.append("No significant changes to criteria weights.")
    
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("*🤖 Generated by @workflows-tech-lead autonomous learning system*")
    
    return "\n".join(lines)


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Learn from PR outcomes')
    parser.add_argument('--repo', type=str, required=True, help='Repository (owner/repo)')
    parser.add_argument('--days', type=int, default=30, help='Days to look back')
    parser.add_argument('--criteria', type=str, default='.github/review-system/criteria.json', help='Criteria file')
    parser.add_argument('--learning-rate', type=float, default=0.1, help='Learning rate (0.0-1.0)')
    parser.add_argument('--output-report', type=str, help='Output report file')
    
    args = parser.parse_args()
    
    # Load current criteria
    criteria_path = Path(args.criteria)
    with open(criteria_path, 'r') as f:
        criteria_before = json.load(f)
    
    print("Current criteria loaded")
    print(f"Total reviews: {criteria_before['metadata']['total_reviews']}")
    print(f"Success rate: {criteria_before['metadata']['success_rate']:.1%}")
    print()
    
    # Fetch closed PRs
    print(f"Fetching closed PRs from last {args.days} days...")
    prs = fetch_closed_prs(args.repo, args.days)
    
    if not prs:
        print("No PRs found, exiting")
        return 0
    
    # Load review results
    print("Loading review results...")
    reviews_dir = criteria_path.parent / 'reviews'
    reviews = load_review_results(reviews_dir)
    print(f"Loaded {len(reviews)} review results")
    print()
    
    # Calculate effectiveness
    print("Calculating effectiveness...")
    effectiveness = calculate_effectiveness(reviews, prs)
    print()
    
    # Evolve criteria
    criteria_after = evolve_criteria(criteria_before, effectiveness, args.learning_rate)
    
    # Save updated criteria
    with open(criteria_path, 'w') as f:
        json.dump(criteria_after, f, indent=2)
    
    print(f"\n✅ Criteria updated: {criteria_path}")
    
    # Generate report
    report = generate_learning_report(effectiveness, criteria_before, criteria_after)
    
    if args.output_report:
        with open(args.output_report, 'w') as f:
            f.write(report)
        print(f"✅ Report saved: {args.output_report}")
    
    print("\n" + "="*60)
    print(report)
    print("="*60)
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
