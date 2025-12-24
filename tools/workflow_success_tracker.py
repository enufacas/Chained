#!/usr/bin/env python3
"""
Workflow Success Rate Tracker
Created by @create-botter

This module tracks GitHub Actions workflow execution outcomes and
integrates with the self-evolving neural architecture system to
enable automatic workflow adaptation based on success rates.

Features:
- Fetches workflow run history from GitHub API
- Calculates rolling success rates
- Identifies workflows below performance threshold
- Triggers neural architecture evolution
- Records execution data for learning
"""

import json
import os
import sys
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import requests

# Add tools directory to path
sys.path.insert(0, os.path.dirname(__file__))

from self_evolving_neural_architecture import EvolvingArchitectureManager


class WorkflowSuccessTracker:
    """
    Tracks workflow execution success rates and integrates with
    neural architecture evolution system.
    """
    
    def __init__(self, repo_owner: str, repo_name: str, github_token: Optional[str] = None):
        """
        Initialize the workflow success tracker.
        
        Args:
            repo_owner: GitHub repository owner
            repo_name: GitHub repository name
            github_token: GitHub API token (or from GITHUB_TOKEN env var)
        """
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        self.github_token = github_token or os.environ.get('GITHUB_TOKEN', '')
        
        # GitHub API base URL
        self.api_base = f"https://api.github.com/repos/{repo_owner}/{repo_name}"
        
        # Headers for API requests
        self.headers = {
            'Accept': 'application/vnd.github.v3+json',
        }
        if self.github_token:
            self.headers['Authorization'] = f'token {self.github_token}'
        
        # Initialize architecture manager
        self.architecture_manager = EvolvingArchitectureManager()
        
        # Success rate threshold for evolution trigger
        self.success_threshold = 0.7
        
        # Minimum runs to consider for analysis
        self.min_runs = 5
    
    def fetch_workflow_runs(self, workflow_name: Optional[str] = None,
                           days: int = 7, max_runs: int = 100) -> List[Dict[str, Any]]:
        """
        Fetch recent workflow runs from GitHub API.
        
        Args:
            workflow_name: Specific workflow to fetch (None for all)
            days: Number of days of history to fetch
            max_runs: Maximum number of runs to fetch
        
        Returns:
            List of workflow run data
        """
        # GitHub API expects date in YYYY-MM-DD format for filters
        since = (datetime.now(timezone.utc) - timedelta(days=days)).strftime('%Y-%m-%d')
        
        url = f"{self.api_base}/actions/runs"
        params = {
            'per_page': min(max_runs, 100),
            'created': f'>{since}',
            'status': 'completed'
        }
        
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            runs = data.get('workflow_runs', [])
            
            # Filter by workflow name if specified
            if workflow_name:
                runs = [r for r in runs if r.get('name') == workflow_name]
            
            return runs
        
        except requests.RequestException as e:
            print(f"Error fetching workflow runs: {e}", file=sys.stderr)
            return []
    
    def calculate_success_rate(self, runs: List[Dict[str, Any]]) -> Tuple[float, int, int]:
        """
        Calculate success rate from workflow runs.
        
        Args:
            runs: List of workflow run data
        
        Returns:
            Tuple of (success_rate, successes, total)
        """
        if not runs:
            return 0.0, 0, 0
        
        total = len(runs)
        successes = sum(1 for r in runs if r.get('conclusion') == 'success')
        
        success_rate = successes / total if total > 0 else 0.0
        
        return success_rate, successes, total
    
    def get_workflow_stats(self, days: int = 7) -> Dict[str, Dict[str, Any]]:
        """
        Get success rate statistics for all workflows.
        
        Args:
            days: Number of days of history to analyze
        
        Returns:
            Dictionary mapping workflow name to stats
        """
        runs = self.fetch_workflow_runs(days=days)
        
        # Group runs by workflow
        workflow_runs = defaultdict(list)
        for run in runs:
            workflow_name = run.get('name', 'Unknown')
            workflow_runs[workflow_name].append(run)
        
        # Calculate stats for each workflow
        stats = {}
        for workflow_name, runs in workflow_runs.items():
            success_rate, successes, total = self.calculate_success_rate(runs)
            
            # Get timing information
            durations = []
            for run in runs:
                if run.get('run_started_at') and run.get('updated_at'):
                    try:
                        start = datetime.fromisoformat(run['run_started_at'].replace('Z', '+00:00'))
                        end = datetime.fromisoformat(run['updated_at'].replace('Z', '+00:00'))
                        duration = (end - start).total_seconds()
                        durations.append(duration)
                    except (ValueError, AttributeError) as e:
                        # Skip runs with invalid timestamps
                        continue
            
            avg_duration = sum(durations) / len(durations) if durations else 0
            
            stats[workflow_name] = {
                'success_rate': success_rate,
                'successes': successes,
                'total': total,
                'failures': total - successes,
                'avg_duration': avg_duration,
                'below_threshold': success_rate < self.success_threshold if total >= self.min_runs else False,
                'needs_evolution': success_rate < self.success_threshold and total >= self.min_runs
            }
        
        return stats
    
    def record_workflow_executions(self, days: int = 7):
        """
        Record recent workflow executions in neural architectures.
        
        Args:
            days: Number of days of history to record
        """
        print(f"\n📊 Recording workflow executions from last {days} days...")
        
        runs = self.fetch_workflow_runs(days=days)
        
        if not runs:
            print("⚠️  No workflow runs found")
            return
        
        # Group by workflow and record
        workflow_runs = defaultdict(list)
        for run in runs:
            workflow_name = run.get('name', 'Unknown')
            workflow_runs[workflow_name].append(run)
        
        recorded = 0
        for workflow_name, runs in workflow_runs.items():
            print(f"\n  Processing: {workflow_name}")
            
            for run in runs:
                success = run.get('conclusion') == 'success'
                
                # Create context from run data
                context = {
                    'run_id': run.get('id'),
                    'created_at': run.get('created_at'),
                    'conclusion': run.get('conclusion'),
                }
                
                # Record in neural architecture
                self.architecture_manager.record_execution(
                    workflow_name=workflow_name,
                    success=success,
                    context=context
                )
                recorded += 1
            
            print(f"    Recorded {len(runs)} executions")
        
        print(f"\n✅ Total executions recorded: {recorded}")
    
    def trigger_evolution_for_poor_performers(self) -> List[str]:
        """
        Trigger evolution for workflows with poor success rates.
        
        Returns:
            List of workflow names that underwent evolution
        """
        print("\n🧬 Checking for workflows needing evolution...")
        
        stats = self.get_workflow_stats()
        evolved = []
        
        for workflow_name, stat in stats.items():
            if stat['needs_evolution']:
                print(f"\n  ⚠️  {workflow_name}:")
                print(f"      Success rate: {stat['success_rate']:.1%} (threshold: {self.success_threshold:.1%})")
                print(f"      Runs: {stat['total']} ({stat['successes']} successes, {stat['failures']} failures)")
                
                # Get or create architecture
                arch = self.architecture_manager.get_or_create(workflow_name)
                
                # Check if architecture should evolve (public method would be better)
                should_evolve = (
                    len(arch.success_history) >= arch.config.min_data_for_evolution and
                    (arch.execution_count - arch.evolution_count * arch.config.evolution_interval) >= arch.config.evolution_interval and
                    arch.get_success_rate() < arch.config.success_rate_threshold
                )
                
                if should_evolve:
                    print(f"      🧬 Triggering evolution...")
                    arch.evolve()
                    evolved.append(workflow_name)
                else:
                    print(f"      ℹ️  Not ready for evolution yet (need more data or interval)")
        
        if not evolved:
            print("  ✅ All workflows performing above threshold")
        
        return evolved
    
    def generate_report(self, days: int = 7) -> str:
        """
        Generate a comprehensive workflow success rate report.
        
        Args:
            days: Number of days to analyze
        
        Returns:
            Formatted report string
        """
        stats = self.get_workflow_stats(days=days)
        
        lines = [
            f"\n📊 Workflow Success Rate Report",
            f"=" * 70,
            f"Repository: {self.repo_owner}/{self.repo_name}",
            f"Period: Last {days} days",
            f"Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}",
            f"",
            f"🎯 Performance Summary:",
            f"   Total workflows analyzed: {len(stats)}",
        ]
        
        # Count workflows by performance
        above_threshold = sum(1 for s in stats.values() 
                             if not s['below_threshold'] and s['total'] >= self.min_runs)
        below_threshold = sum(1 for s in stats.values() if s['below_threshold'])
        insufficient_data = sum(1 for s in stats.values() if s['total'] < self.min_runs)
        
        lines.extend([
            f"   Above threshold ({self.success_threshold:.0%}): {above_threshold}",
            f"   Below threshold: {below_threshold}",
            f"   Insufficient data: {insufficient_data}",
            f"",
            f"📋 Workflow Details:",
            f""
        ])
        
        # Sort workflows by success rate
        sorted_workflows = sorted(stats.items(), 
                                 key=lambda x: x[1]['success_rate'])
        
        for workflow_name, stat in sorted_workflows:
            status = "🟢" if not stat['below_threshold'] else "🔴"
            if stat['total'] < self.min_runs:
                status = "⚪"
            
            lines.append(f"   {status} {workflow_name}")
            lines.append(f"      Success rate: {stat['success_rate']:.1%} "
                        f"({stat['successes']}/{stat['total']} runs)")
            
            if stat['avg_duration'] > 0:
                mins = int(stat['avg_duration'] / 60)
                secs = int(stat['avg_duration'] % 60)
                lines.append(f"      Avg duration: {mins}m {secs}s")
            
            if stat['needs_evolution']:
                lines.append(f"      ⚠️  NEEDS EVOLUTION")
            
            lines.append("")
        
        lines.extend([
            "=" * 70,
            "🤖 Report generated by @create-botter's Workflow Success Tracker",
        ])
        
        return "\n".join(lines)
    
    def get_recommendations(self, workflow_name: str) -> Dict[str, Any]:
        """
        Get neural architecture recommendations for a workflow.
        
        Args:
            workflow_name: Name of the workflow
        
        Returns:
            Dictionary of recommended parameters
        """
        return self.architecture_manager.get_recommendations(workflow_name)


def main():
    """Main entry point for CLI usage."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Track workflow success rates and trigger neural evolution"
    )
    parser.add_argument(
        '--owner',
        default='enufacas',
        help='Repository owner (default: enufacas)'
    )
    parser.add_argument(
        '--repo',
        default='Chained',
        help='Repository name (default: Chained)'
    )
    parser.add_argument(
        '--days',
        type=int,
        default=7,
        help='Days of history to analyze (default: 7)'
    )
    parser.add_argument(
        '--record',
        action='store_true',
        help='Record recent executions in neural architectures'
    )
    parser.add_argument(
        '--evolve',
        action='store_true',
        help='Trigger evolution for poor performers'
    )
    parser.add_argument(
        '--report',
        action='store_true',
        help='Generate success rate report'
    )
    parser.add_argument(
        '--stats',
        action='store_true',
        help='Show workflow statistics'
    )
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output in JSON format'
    )
    
    args = parser.parse_args()
    
    tracker = WorkflowSuccessTracker(
        repo_owner=args.owner,
        repo_name=args.repo
    )
    
    if args.record:
        tracker.record_workflow_executions(days=args.days)
    
    if args.evolve:
        evolved = tracker.trigger_evolution_for_poor_performers()
        print(f"\n✅ Evolved {len(evolved)} workflow architectures")
    
    if args.report:
        report = tracker.generate_report(days=args.days)
        print(report)
    
    if args.stats:
        stats = tracker.get_workflow_stats(days=args.days)
        if args.json:
            print(json.dumps(stats, indent=2))
        else:
            print("\n📊 Workflow Statistics:\n")
            for workflow_name, stat in sorted(stats.items()):
                print(f"{workflow_name}:")
                print(f"  Success rate: {stat['success_rate']:.1%}")
                print(f"  Total runs: {stat['total']}")
                print(f"  Needs evolution: {stat['needs_evolution']}")
                print()
    
    if not (args.record or args.evolve or args.report or args.stats):
        parser.print_help()
        return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
