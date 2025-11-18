#!/usr/bin/env python3
"""
AI Contribution Uniqueness Scorer

Scores the uniqueness of AI agent contributions by comparing them against
the agent's own history and other agents' work.
"""

import argparse
import ast
import json
import os
import re
import subprocess
import sys
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, List, Any, Optional, Set, Tuple


# System actors to exclude from diversity analysis
# These are automation bots that perform repetitive tasks by design
EXCLUDED_ACTORS = [
    'github-actions',
    'github-actions[bot]',
    'dependabot',
    'dependabot[bot]',
    'renovate',
    'renovate[bot]',
]


class UniquenessScorer:
    """Scores uniqueness of AI agent contributions"""
    
    def __init__(self, repo_dir: str, agent_id: Optional[str] = None):
        self.repo_dir = Path(repo_dir)
        self.target_agent = agent_id
        self.agent_contributions = defaultdict(list)
        self.agent_approaches = defaultdict(set)
        self.agent_file_types = defaultdict(set)
        self.agent_commit_patterns = defaultdict(list)
        
    def _run_git_command(self, args: List[str]) -> str:
        """Run a git command and return output"""
        try:
            result = subprocess.run(
                ['git', '-C', str(self.repo_dir)] + args,
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            print(f"Git command failed: {e}", file=sys.stderr)
            return ""
    
    def _extract_agent_id(self, author_email: str, author_name: str) -> Optional[str]:
        """Extract agent ID from commit author information"""
        # Match patterns like: copilot-swe-agent[bot], github-actions[bot], etc.
        bot_match = re.search(r'(\w+(?:-\w+)*)\[bot\]', author_name)
        if bot_match:
            return bot_match.group(1)
        
        # Match email patterns
        email_match = re.search(r'\+(\w+)@', author_email)
        if email_match:
            return email_match.group(1).lower()
        
        # Check if it's a GitHub Actions bot
        if 'github-actions' in author_email or 'github-actions' in author_name:
            return 'github-actions'
            
        return None
    
    def collect_all_contributions(self, days: int = 90):
        """Collect contributions from all AI agents"""
        since_date = datetime.now(timezone.utc) - timedelta(days=days)
        since_str = since_date.strftime('%Y-%m-%d')
        
        log_output = self._run_git_command([
            'log',
            '--all',
            '--pretty=format:%H|%an|%ae|%s|%cd',
            '--date=iso',
            f'--since={since_str}'
        ])
        
        if not log_output:
            return
        
        for line in log_output.split('\n'):
            if not line:
                continue
                
            parts = line.split('|')
            if len(parts) < 5:
                continue
                
            commit_hash, author_name, author_email, message, date = parts
            agent_id = self._extract_agent_id(author_email, author_name)
            
            if not agent_id:
                continue
            
            # Get files changed
            files_output = self._run_git_command([
                'diff-tree',
                '--no-commit-id',
                '--name-only',
                '-r',
                commit_hash
            ])
            
            files = files_output.split('\n') if files_output else []
            
            contribution = {
                'commit_hash': commit_hash,
                'message': message,
                'date': date,
                'files': files
            }
            
            self.agent_contributions[agent_id].append(contribution)
            self.agent_commit_patterns[agent_id].append(message)
            
            # Extract approaches and file types
            self._extract_contribution_features(agent_id, contribution)
    
    def _extract_contribution_features(self, agent_id: str, contribution: Dict):
        """Extract features from a contribution for comparison"""
        msg = contribution['message'].lower()
        
        # Extract approach types
        approach_keywords = {
            'refactor': 'refactoring',
            'test': 'testing',
            'fix': 'bug_fixing',
            'bug': 'bug_fixing',
            'add': 'feature_addition',
            'implement': 'implementation',
            'create': 'creation',
            'update': 'updating',
            'remove': 'removal',
            'delete': 'deletion',
            'optimize': 'optimization',
            'improve': 'improvement',
            'enhance': 'enhancement',
            'workflow': 'workflow',
            'action': 'automation',
            'doc': 'documentation',
            'security': 'security',
            'performance': 'performance'
        }
        
        for keyword, approach in approach_keywords.items():
            if keyword in msg:
                self.agent_approaches[agent_id].add(approach)
        
        # Extract file types
        for file_path in contribution['files']:
            ext = Path(file_path).suffix
            if ext:
                self.agent_file_types[agent_id].add(ext)
    
    def calculate_structural_uniqueness(self, agent_id: str) -> float:
        """Calculate how unique an agent's code structures are"""
        if agent_id not in self.agent_contributions:
            return 0.0
        
        contributions = self.agent_contributions[agent_id]
        if not contributions:
            return 0.0
        
        # Count unique vs repeated patterns
        file_type_diversity = len(self.agent_file_types.get(agent_id, set()))
        
        # Analyze commit message diversity
        messages = self.agent_commit_patterns.get(agent_id, [])
        unique_messages = len(set(messages))
        total_messages = len(messages)
        
        message_diversity = (unique_messages / total_messages * 100) if total_messages > 0 else 0
        
        # Combine metrics
        structural_score = min(100, (file_type_diversity * 10 + message_diversity) / 2)
        
        return round(structural_score, 2)
    
    def calculate_approach_diversity(self, agent_id: str) -> float:
        """Calculate diversity of approaches used by the agent"""
        if agent_id not in self.agent_contributions:
            return 0.0
        
        approaches = self.agent_approaches.get(agent_id, set())
        contributions = self.agent_contributions.get(agent_id, [])
        
        if not contributions:
            return 0.0
        
        # Score based on unique approaches per contribution
        approach_count = len(approaches)
        contribution_count = len(contributions)
        
        # Higher score for more diverse approaches relative to contributions
        diversity_ratio = min(1.0, approach_count / max(contribution_count * 0.3, 1))
        diversity_score = diversity_ratio * 100
        
        return round(diversity_score, 2)
    
    def calculate_innovation_index(self, agent_id: str) -> float:
        """Calculate innovation index by comparing to other agents"""
        if agent_id not in self.agent_contributions:
            return 0.0
        
        agent_approaches = self.agent_approaches.get(agent_id, set())
        agent_file_types = self.agent_file_types.get(agent_id, set())
        
        # Collect approaches from other agents
        other_approaches = set()
        other_file_types = set()
        
        for other_id, approaches in self.agent_approaches.items():
            if other_id != agent_id:
                other_approaches.update(approaches)
        
        for other_id, file_types in self.agent_file_types.items():
            if other_id != agent_id:
                other_file_types.update(file_types)
        
        # Calculate uniqueness compared to others
        unique_approaches = agent_approaches - other_approaches
        common_approaches = agent_approaches & other_approaches
        
        unique_file_types = agent_file_types - other_file_types
        common_file_types = agent_file_types & other_file_types
        
        # Innovation score: balance of unique vs common
        if agent_approaches:
            approach_innovation = (len(unique_approaches) / len(agent_approaches)) * 50
        else:
            approach_innovation = 0
        
        if agent_file_types:
            file_type_innovation = (len(unique_file_types) / len(agent_file_types)) * 50
        else:
            file_type_innovation = 0
        
        innovation_score = approach_innovation + file_type_innovation
        
        return round(innovation_score, 2)
    
    def calculate_overall_score(self, agent_id: str) -> Dict[str, Any]:
        """Calculate overall uniqueness score for an agent"""
        structural = self.calculate_structural_uniqueness(agent_id)
        approach = self.calculate_approach_diversity(agent_id)
        innovation = self.calculate_innovation_index(agent_id)
        
        # Weighted average: structural 30%, approach 40%, innovation 30%
        overall = (structural * 0.3 + approach * 0.4 + innovation * 0.3)
        
        return {
            'agent_id': agent_id,
            'overall_score': round(overall, 2),
            'metrics': {
                'structural_uniqueness': structural,
                'approach_diversity': approach,
                'innovation_index': innovation
            },
            'details': {
                'total_contributions': len(self.agent_contributions.get(agent_id, [])),
                'unique_approaches': len(self.agent_approaches.get(agent_id, set())),
                'unique_file_types': len(self.agent_file_types.get(agent_id, set())),
                'approaches_used': list(self.agent_approaches.get(agent_id, set())),
                'file_types_used': list(self.agent_file_types.get(agent_id, set()))
            }
        }
    
    def score_all_agents(self, threshold: float = 30.0, min_contributions: int = 3) -> Dict[str, Any]:
        """Score all agents and flag those below threshold
        
        Filters out system automation bots that are not AI agents.
        Also filters out agents with insufficient contributions for meaningful diversity analysis.
        
        Args:
            threshold: Minimum score required to avoid flagging
            min_contributions: Minimum number of contributions required for diversity analysis (default: 3)
        """
        scores = {}
        flagged = []
        excluded_count = 0
        insufficient_data_count = 0
        
        for agent_id in self.agent_contributions.keys():
            # Skip system automation bots - they're not AI agents requiring diversity coaching
            if agent_id in EXCLUDED_ACTORS:
                excluded_count += 1
                continue
            
            # Calculate score for all agents (for reporting)
            score_data = self.calculate_overall_score(agent_id)
            scores[agent_id] = score_data
            
            # Only flag agents with sufficient contributions
            # Agents with < min_contributions don't have enough data for meaningful diversity analysis
            contribution_count = score_data['details']['total_contributions']
            
            if contribution_count < min_contributions:
                insufficient_data_count += 1
                # Add note to score data
                score_data['note'] = f'Insufficient data ({contribution_count} contributions, need {min_contributions}+)'
                continue
            
            # Flag agents with sufficient data but low diversity
            if score_data['overall_score'] < threshold:
                flagged.append({
                    'agent_id': agent_id,
                    'score': score_data['overall_score'],
                    'reason': self._generate_flag_reason(score_data)
                })
        
        return {
            'metadata': {
                'generated_at': datetime.now(timezone.utc).isoformat(),
                'repository': str(self.repo_dir),
                'threshold': threshold,
                'min_contributions': min_contributions,
                'total_agents_analyzed': len(scores),
                'excluded_system_bots': excluded_count,
                'insufficient_data_agents': insufficient_data_count
            },
            'scores': scores,
            'flagged_agents': flagged,
            'summary': {
                'average_score': round(
                    sum(s['overall_score'] for s in scores.values()) / len(scores), 2
                ) if scores else 0,
                'agents_below_threshold': len(flagged),
                'agents_above_threshold': len(scores) - len(flagged),
                'total_agents': len(scores)
            }
        }
    
    def _generate_flag_reason(self, score_data: Dict) -> str:
        """Generate human-readable reason for flagging"""
        reasons = []
        metrics = score_data['metrics']
        
        if metrics['structural_uniqueness'] < 30:
            reasons.append(f"low structural uniqueness ({metrics['structural_uniqueness']:.1f})")
        
        if metrics['approach_diversity'] < 30:
            reasons.append(f"low approach diversity ({metrics['approach_diversity']:.1f})")
        
        if metrics['innovation_index'] < 30:
            reasons.append(f"low innovation index ({metrics['innovation_index']:.1f})")
        
        return '; '.join(reasons) if reasons else 'overall score below threshold'
    
    def score_specific_agent(self, agent_id: str, threshold: float = 30.0) -> Dict[str, Any]:
        """Score a specific agent"""
        if agent_id not in self.agent_contributions:
            return {
                'error': f"Agent '{agent_id}' not found in repository history",
                'available_agents': list(self.agent_contributions.keys())
            }
        
        score_data = self.calculate_overall_score(agent_id)
        
        is_flagged = score_data['overall_score'] < threshold
        
        return {
            'metadata': {
                'generated_at': datetime.now(timezone.utc).isoformat(),
                'repository': str(self.repo_dir),
                'threshold': threshold
            },
            'agent_score': score_data,
            'flagged': is_flagged,
            'flag_reason': self._generate_flag_reason(score_data) if is_flagged else None,
            'comparison': {
                'percentile': self._calculate_percentile(score_data['overall_score']),
                'rank': self._calculate_rank(agent_id)
            }
        }
    
    def _calculate_percentile(self, score: float) -> float:
        """Calculate percentile ranking of score"""
        all_scores = [
            self.calculate_overall_score(aid)['overall_score']
            for aid in self.agent_contributions.keys()
        ]
        
        if not all_scores:
            return 0.0
        
        below_count = sum(1 for s in all_scores if s < score)
        percentile = (below_count / len(all_scores)) * 100
        
        return round(percentile, 2)
    
    def _calculate_rank(self, agent_id: str) -> int:
        """Calculate rank of agent (1 = highest score)"""
        all_scores = [
            (aid, self.calculate_overall_score(aid)['overall_score'])
            for aid in self.agent_contributions.keys()
        ]
        
        all_scores.sort(key=lambda x: x[1], reverse=True)
        
        for rank, (aid, _) in enumerate(all_scores, 1):
            if aid == agent_id:
                return rank
        
        return len(all_scores)


def main():
    parser = argparse.ArgumentParser(
        description='Score uniqueness of AI agent contributions'
    )
    parser.add_argument(
        '-d', '--directory',
        default='.',
        help='Repository directory to analyze (default: current directory)'
    )
    parser.add_argument(
        '--agent-id',
        help='Specific agent ID to score (default: score all agents)'
    )
    parser.add_argument(
        '--threshold',
        type=float,
        default=30.0,
        help='Uniqueness threshold for flagging (default: 30.0)'
    )
    parser.add_argument(
        '--days',
        type=int,
        default=90,
        help='Number of days to look back (default: 90)'
    )
    parser.add_argument(
        '--min-contributions',
        type=int,
        default=3,
        help='Minimum contributions required for diversity analysis (default: 3)'
    )
    parser.add_argument(
        '-o', '--output',
        help='Output file for JSON report (default: stdout)'
    )
    
    args = parser.parse_args()
    
    # Initialize scorer
    scorer = UniquenessScorer(args.directory, args.agent_id)
    
    # Collect contributions
    print("Collecting contributions from all agents...", file=sys.stderr)
    scorer.collect_all_contributions(args.days)
    
    # Generate scores
    print("Calculating uniqueness scores...", file=sys.stderr)
    
    if args.agent_id:
        report = scorer.score_specific_agent(args.agent_id, args.threshold)
    else:
        report = scorer.score_all_agents(args.threshold, args.min_contributions)
    
    # Output report
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"Report saved to {args.output}", file=sys.stderr)
    else:
        print(json.dumps(report, indent=2))
    
    # Exit with error code if agents are flagged
    if 'flagged_agents' in report and report['flagged_agents']:
        print(f"\n⚠️  {len(report['flagged_agents'])} agents below threshold", file=sys.stderr)
        return 1
    elif 'flagged' in report and report['flagged']:
        print(f"\n⚠️  Agent '{args.agent_id}' is below threshold", file=sys.stderr)
        return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
