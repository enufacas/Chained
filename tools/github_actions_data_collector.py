#!/usr/bin/env python3
"""
GitHub Actions Workflow Data Collector
Created by @create-botter

Automatically collects real workflow execution data from GitHub Actions API
to feed the AI-powered workflow predictor with actual performance metrics.

This tool bridges the gap between simulated data and real execution data,
enabling the AI predictor to learn from actual workflow behavior patterns.

Features:
- Fetches recent workflow runs from GitHub Actions API
- Extracts execution times, success rates, and resource metrics
- Records data to the AI predictor's history file
- Supports both scheduled and on-demand collection
- Provides insights into workflow performance trends
"""

import os
import sys
import json
import argparse
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import subprocess

# Add tools directory to path
sys.path.insert(0, os.path.dirname(__file__))

try:
    from ai_workflow_predictor import AIWorkflowPredictor
except ImportError:
    AIWorkflowPredictor = None


@dataclass
class WorkflowRunData:
    """Data about a GitHub Actions workflow run."""
    workflow_name: str
    workflow_id: int
    run_id: int
    run_number: int
    status: str
    conclusion: str
    start_time: datetime
    end_time: Optional[datetime]
    duration_seconds: float
    event: str
    branch: str
    actor: str


# Constants for resource estimation
# These values are based on typical GitHub Actions runner characteristics
RESOURCE_CPU_BASE_PERCENT = 20        # Base CPU usage percentage
RESOURCE_CPU_PER_MINUTE = 5           # Additional CPU % per minute of runtime
RESOURCE_CPU_MAX_PERCENT = 90         # Maximum CPU usage cap
RESOURCE_MEMORY_BASE_MB = 256         # Base memory usage in MB
RESOURCE_MEMORY_PER_MINUTE = 50       # Additional memory per minute of runtime
RESOURCE_MEMORY_MAX_MB = 2048         # Maximum memory cap (2GB)


class GitHubActionsDataCollector:
    """
    Collects workflow execution data from GitHub Actions API.
    
    This collector fetches real workflow run data and records it
    to the AI predictor's history for learning and prediction.
    """
    
    def __init__(self, repo_root: str = None, owner: str = None, repo: str = None):
        """
        Initialize the data collector.
        
        Args:
            repo_root: Root directory of the repository
            owner: GitHub repository owner (optional, auto-detected)
            repo: GitHub repository name (optional, auto-detected)
        """
        if repo_root:
            self.repo_root = Path(repo_root)
        else:
            current = Path.cwd()
            while current != current.parent:
                if (current / '.git').exists():
                    self.repo_root = current
                    break
                current = current.parent
            else:
                self.repo_root = Path.cwd()
        
        # Detect owner/repo from git remote if not provided
        if owner and repo:
            self.owner = owner
            self.repo = repo
        else:
            self.owner, self.repo = self._detect_repo_info()
        
        # Initialize predictor for recording data
        if AIWorkflowPredictor:
            self.predictor = AIWorkflowPredictor(repo_root=str(self.repo_root))
        else:
            self.predictor = None
        
        # Collection history tracking
        self.collection_history_file = self.repo_root / '.github' / 'workflow-history' / 'collection_log.json'
        self.collection_history_file.parent.mkdir(parents=True, exist_ok=True)
    
    def _detect_repo_info(self) -> tuple:
        """Detect owner/repo from git remote."""
        try:
            result = subprocess.run(
                ['git', 'remote', 'get-url', 'origin'],
                capture_output=True,
                text=True,
                cwd=str(self.repo_root)
            )
            if result.returncode == 0:
                url = result.stdout.strip()
                # Parse GitHub URL (handles both https and ssh)
                if 'github.com' in url:
                    # Remove .git suffix
                    url = url.rstrip('.git')
                    # Extract owner/repo
                    if url.startswith('https://'):
                        parts = url.split('/')
                        return parts[-2], parts[-1]
                    elif 'git@' in url:
                        # ssh format: git@github.com:owner/repo
                        parts = url.split(':')[1].split('/')
                        return parts[0], parts[1]
        except Exception:
            pass
        
        return 'unknown', 'unknown'
    
    def _run_gh_command(self, args: List[str]) -> Optional[str]:
        """Run a gh CLI command and return output."""
        try:
            result = subprocess.run(
                ['gh'] + args,
                capture_output=True,
                text=True,
                cwd=str(self.repo_root)
            )
            if result.returncode == 0:
                return result.stdout
            else:
                print(f"Warning: gh command failed: {result.stderr}", file=sys.stderr)
                return None
        except FileNotFoundError:
            print("Warning: gh CLI not found. Please install GitHub CLI.", file=sys.stderr)
            return None
        except Exception as e:
            print(f"Warning: Error running gh command: {e}", file=sys.stderr)
            return None
    
    def fetch_workflow_runs(self, limit: int = 50, workflow_name: str = None) -> List[WorkflowRunData]:
        """
        Fetch recent workflow runs from GitHub Actions API.
        
        Args:
            limit: Maximum number of runs to fetch
            workflow_name: Optional filter for specific workflow
        
        Returns:
            List of WorkflowRunData objects
        """
        print(f"📥 Fetching workflow runs from GitHub Actions...")
        
        # Build gh command
        args = ['run', 'list', '--json', 
                'workflowName,workflowDatabaseId,databaseId,number,status,conclusion,'
                'createdAt,updatedAt,event,headBranch,actor',
                '--limit', str(limit)]
        
        if workflow_name:
            args.extend(['--workflow', workflow_name])
        
        output = self._run_gh_command(args)
        
        if not output:
            return []
        
        try:
            runs_data = json.loads(output)
        except json.JSONDecodeError as e:
            print(f"Warning: Could not parse gh output: {e}", file=sys.stderr)
            return []
        
        workflow_runs = []
        
        for run in runs_data:
            # Parse timestamps
            try:
                start_time = datetime.fromisoformat(run['createdAt'].replace('Z', '+00:00'))
                end_time = datetime.fromisoformat(run['updatedAt'].replace('Z', '+00:00'))
            except (KeyError, ValueError):
                continue
            
            # Calculate duration (only for completed runs)
            if run.get('status') == 'completed':
                duration_seconds = (end_time - start_time).total_seconds()
            else:
                duration_seconds = 0
            
            workflow_run = WorkflowRunData(
                workflow_name=run.get('workflowName', 'unknown'),
                workflow_id=run.get('workflowDatabaseId', 0),
                run_id=run.get('databaseId', 0),
                run_number=run.get('number', 0),
                status=run.get('status', 'unknown'),
                conclusion=run.get('conclusion', 'unknown') or 'unknown',
                start_time=start_time,
                end_time=end_time if run.get('status') == 'completed' else None,
                duration_seconds=duration_seconds,
                event=run.get('event', 'unknown'),
                branch=run.get('headBranch', 'unknown'),
                actor=self._extract_actor_name(run.get('actor'))
            )
            
            workflow_runs.append(workflow_run)
        
        print(f"✓ Fetched {len(workflow_runs)} workflow runs")
        return workflow_runs
    
    def _extract_actor_name(self, actor_data: Any) -> str:
        """Extract actor login from API response, handling various formats."""
        if isinstance(actor_data, dict):
            return actor_data.get('login', 'unknown')
        return 'unknown'
    
    def record_to_predictor(self, runs: List[WorkflowRunData]) -> int:
        """
        Record workflow runs to the AI predictor.
        
        Args:
            runs: List of workflow run data
        
        Returns:
            Number of runs recorded
        """
        if not self.predictor:
            print("Warning: AI predictor not available", file=sys.stderr)
            return 0
        
        recorded = 0
        
        for run in runs:
            # Only record completed runs
            if run.status != 'completed' or run.duration_seconds <= 0:
                continue
            
            # Determine success
            success = run.conclusion in ['success', 'neutral', 'skipped']
            
            # Resource usage estimation based on duration
            # Uses named constants for clarity and maintainability
            duration_minutes = run.duration_seconds / 60
            resource_usage = {
                'duration_seconds': run.duration_seconds,
                'event': run.event,
                'branch': run.branch,
                'actor': run.actor,
                'estimated_cpu_percent': min(
                    RESOURCE_CPU_MAX_PERCENT,
                    RESOURCE_CPU_BASE_PERCENT + duration_minutes * RESOURCE_CPU_PER_MINUTE
                ),
                'estimated_memory_mb': min(
                    RESOURCE_MEMORY_MAX_MB,
                    RESOURCE_MEMORY_BASE_MB + duration_minutes * RESOURCE_MEMORY_PER_MINUTE
                )
            }
            
            try:
                self.predictor.record_execution(
                    workflow_name=run.workflow_name,
                    start_time=run.start_time,
                    duration_seconds=run.duration_seconds,
                    success=success,
                    resource_usage=resource_usage
                )
                recorded += 1
            except Exception as e:
                print(f"Warning: Could not record run {run.run_id}: {e}", file=sys.stderr)
        
        print(f"✓ Recorded {recorded} workflow runs to AI predictor")
        return recorded
    
    def collect_and_record(self, limit: int = 50, workflow_name: str = None) -> Dict[str, Any]:
        """
        Collect workflow runs and record them to the predictor.
        
        Args:
            limit: Maximum number of runs to fetch
            workflow_name: Optional filter for specific workflow
        
        Returns:
            Collection summary
        """
        # Fetch runs
        runs = self.fetch_workflow_runs(limit=limit, workflow_name=workflow_name)
        
        if not runs:
            return {
                'status': 'no_data',
                'message': 'No workflow runs found',
                'runs_fetched': 0,
                'runs_recorded': 0
            }
        
        # Record to predictor
        recorded = self.record_to_predictor(runs)
        
        # Save collection log
        self._save_collection_log(len(runs), recorded)
        
        return {
            'status': 'success',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'runs_fetched': len(runs),
            'runs_recorded': recorded,
            'workflows': list(set(r.workflow_name for r in runs)),
            'date_range': {
                'earliest': min(r.start_time for r in runs).isoformat() if runs else None,
                'latest': max(r.start_time for r in runs).isoformat() if runs else None
            }
        }
    
    def _save_collection_log(self, fetched: int, recorded: int) -> None:
        """Save collection log for tracking."""
        try:
            log = []
            if self.collection_history_file.exists():
                with open(self.collection_history_file, 'r') as f:
                    log = json.load(f).get('collections', [])
            
            # Add new entry
            log.append({
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'runs_fetched': fetched,
                'runs_recorded': recorded
            })
            
            # Keep last 100 entries
            log = log[-100:]
            
            with open(self.collection_history_file, 'w') as f:
                json.dump({
                    'last_updated': datetime.now(timezone.utc).isoformat(),
                    'total_collections': len(log),
                    'collections': log
                }, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save collection log: {e}", file=sys.stderr)
    
    def get_workflow_stats(self) -> Dict[str, Any]:
        """
        Get statistics about collected workflow data.
        
        Returns:
            Dictionary with statistics
        """
        print("\n📊 Workflow Data Statistics")
        print("="*60)
        
        # Check if we have recorded data
        if not self.predictor or not self.predictor.execution_history:
            return {
                'status': 'no_data',
                'message': 'No workflow execution data available',
                'suggestion': 'Run --collect to fetch data from GitHub Actions'
            }
        
        history = self.predictor.execution_history
        
        # Aggregate stats
        workflow_stats = {}
        for exec_data in history:
            wf_name = exec_data.workflow_name
            if wf_name not in workflow_stats:
                workflow_stats[wf_name] = {
                    'total_runs': 0,
                    'successful_runs': 0,
                    'total_duration': 0,
                    'durations': []
                }
            
            workflow_stats[wf_name]['total_runs'] += 1
            if exec_data.success:
                workflow_stats[wf_name]['successful_runs'] += 1
            workflow_stats[wf_name]['total_duration'] += exec_data.duration_seconds
            workflow_stats[wf_name]['durations'].append(exec_data.duration_seconds)
        
        # Calculate averages and format output
        stats = {
            'total_executions': len(history),
            'unique_workflows': len(workflow_stats),
            'workflows': []
        }
        
        print(f"\n{'Workflow':<35} {'Runs':>8} {'Success':>10} {'Avg Duration':>15}")
        print("-"*70)
        
        for wf_name, wf_stats in sorted(workflow_stats.items()):
            avg_duration = wf_stats['total_duration'] / wf_stats['total_runs']
            success_rate = (wf_stats['successful_runs'] / wf_stats['total_runs']) * 100
            
            wf_short = wf_name[:33] + '..' if len(wf_name) > 35 else wf_name
            print(f"{wf_short:<35} {wf_stats['total_runs']:>8} {success_rate:>9.0f}% {avg_duration:>12.0f}s")
            
            stats['workflows'].append({
                'name': wf_name,
                'total_runs': wf_stats['total_runs'],
                'success_rate': success_rate,
                'avg_duration_seconds': avg_duration
            })
        
        print("-"*70)
        print(f"{'Total':<35} {stats['total_executions']:>8}")
        print("\n" + "="*60 + "\n")
        
        return stats
    
    def generate_collection_report(self) -> Dict[str, Any]:
        """Generate a comprehensive collection report."""
        print("\n" + "="*70)
        print("📊 GitHub Actions Data Collection Report")
        print("   Created by @create-botter")
        print("="*70 + "\n")
        
        report = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'repository': f"{self.owner}/{self.repo}",
            'collection_history': [],
            'workflow_stats': {}
        }
        
        # Load collection history
        if self.collection_history_file.exists():
            try:
                with open(self.collection_history_file, 'r') as f:
                    data = json.load(f)
                    report['collection_history'] = data.get('collections', [])[-10:]
                    
                    print(f"📅 Recent Collections:")
                    for entry in report['collection_history']:
                        print(f"  {entry['timestamp']}: {entry['runs_recorded']} runs recorded")
            except Exception as e:
                print(f"Warning: Could not load collection history: {e}")
        else:
            print("ℹ️  No previous collections found")
        
        # Get workflow stats
        print()
        report['workflow_stats'] = self.get_workflow_stats()
        
        return report


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='GitHub Actions Workflow Data Collector by @create-botter'
    )
    parser.add_argument(
        '--collect',
        action='store_true',
        help='Collect workflow runs from GitHub Actions'
    )
    parser.add_argument(
        '--limit',
        type=int,
        default=50,
        help='Maximum number of runs to fetch (default: 50)'
    )
    parser.add_argument(
        '--workflow',
        help='Filter by specific workflow name'
    )
    parser.add_argument(
        '--stats',
        action='store_true',
        help='Show workflow execution statistics'
    )
    parser.add_argument(
        '--report',
        action='store_true',
        help='Generate comprehensive collection report'
    )
    parser.add_argument(
        '--repo-root',
        help='Repository root directory'
    )
    parser.add_argument(
        '--owner',
        help='GitHub repository owner'
    )
    parser.add_argument(
        '--repo',
        help='GitHub repository name'
    )
    
    args = parser.parse_args()
    
    collector = GitHubActionsDataCollector(
        repo_root=args.repo_root,
        owner=args.owner,
        repo=args.repo
    )
    
    if args.collect:
        print("\n🚀 GitHub Actions Data Collector")
        print("   @create-botter")
        print("="*50 + "\n")
        
        result = collector.collect_and_record(
            limit=args.limit,
            workflow_name=args.workflow
        )
        
        print(f"\n📊 Collection Summary:")
        print(f"  Status: {result['status']}")
        print(f"  Runs Fetched: {result.get('runs_fetched', 0)}")
        print(f"  Runs Recorded: {result.get('runs_recorded', 0)}")
        
        if result.get('workflows'):
            print(f"  Workflows: {', '.join(result['workflows'][:5])}")
            if len(result['workflows']) > 5:
                print(f"    ... and {len(result['workflows']) - 5} more")
        
        print()
    
    if args.stats:
        collector.get_workflow_stats()
    
    if args.report:
        collector.generate_collection_report()
    
    if not (args.collect or args.stats or args.report):
        # Default: show help
        parser.print_help()


if __name__ == '__main__':
    main()
