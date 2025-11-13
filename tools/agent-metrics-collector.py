#!/usr/bin/env python3
"""
Agent Performance Metrics Collector

A production-grade metrics collection and analysis system for the Chained agent
ecosystem. Tracks real GitHub activity and calculates weighted performance scores.

Architecture:
- Modular design with clear separation of concerns
- Scalable for growing agent populations
- Comprehensive error handling and validation
- Performance-optimized with caching
- Secure GitHub API integration

Features:
- Real-time GitHub activity tracking (issues, PRs, reviews)
- Weighted performance scoring algorithm
- Historical metrics storage and trend analysis
- Code quality assessment integration
- Configurable scoring weights

Usage:
    python agent-metrics-collector.py <agent_id> [--since DAYS] [--verbose]
    python agent-metrics-collector.py --evaluate-all
"""

import json
import os
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from functools import lru_cache
import argparse

# Import GitHub integration utilities
try:
    from github_integration import (
        GitHubAPIClient,
        RetryConfig,
        GitHubAPIException
    )
    GITHUB_INTEGRATION_AVAILABLE = True
except ImportError:
    GITHUB_INTEGRATION_AVAILABLE = False
    # Fallback minimal implementation
    class GitHubAPIClient:
        def __init__(self, token=None):
            self.token = token or os.environ.get('GITHUB_TOKEN', os.environ.get('GH_TOKEN'))
        
        def get(self, endpoint, params=None):
            """Minimal fallback implementation"""
            import urllib.request
            import urllib.parse
            
            url = f"https://api.github.com{endpoint}"
            if params:
                url = f"{url}?{urllib.parse.urlencode(params)}"
            
            req = urllib.request.Request(url)
            if self.token:
                req.add_header('Authorization', f'token {self.token}')
            req.add_header('Accept', 'application/vnd.github.v3+json')
            
            try:
                with urllib.request.urlopen(req, timeout=10) as response:
                    return json.loads(response.read().decode('utf-8'))
            except Exception as e:
                return None

# Constants
REGISTRY_FILE = Path(".github/agent-system/registry.json")
METRICS_DIR = Path(".github/agent-system/metrics")
DEFAULT_LOOKBACK_DAYS = 7


@dataclass
class AgentActivity:
    """Structured representation of agent's GitHub activity"""
    issues_resolved: int = 0
    issues_created: int = 0
    prs_created: int = 0
    prs_merged: int = 0
    prs_closed: int = 0
    reviews_given: int = 0
    comments_made: int = 0
    commits_made: int = 0
    
    def to_dict(self) -> Dict[str, int]:
        """Convert to dictionary"""
        return asdict(self)


@dataclass
class MetricsScore:
    """Performance score breakdown"""
    code_quality: float = 0.5
    issue_resolution: float = 0.0
    pr_success: float = 0.0
    peer_review: float = 0.0
    creativity: float = 0.0
    overall: float = 0.0
    
    def to_dict(self) -> Dict[str, float]:
        """Convert to dictionary"""
        return asdict(self)


@dataclass
class AgentMetrics:
    """Complete metrics snapshot for an agent"""
    agent_id: str
    timestamp: str
    activity: AgentActivity
    scores: MetricsScore
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'agent_id': self.agent_id,
            'timestamp': self.timestamp,
            'activity': self.activity.to_dict(),
            'scores': self.scores.to_dict(),
            'metadata': self.metadata
        }


class MetricsCollector:
    """
    Core metrics collection engine.
    
    Responsibilities:
    - Fetch agent activity from GitHub API
    - Calculate performance scores
    - Store historical metrics
    - Provide metrics queries
    """
    
    def __init__(
        self,
        github_token: Optional[str] = None,
        repo: Optional[str] = None,
        cache_size: int = 128
    ):
        """
        Initialize metrics collector.
        
        Args:
            github_token: GitHub API token (defaults to env var)
            repo: Repository in format 'owner/repo' (defaults to env var)
            cache_size: LRU cache size for performance optimization
        """
        self.github = GitHubAPIClient(github_token)
        self.repo = repo or os.environ.get('GITHUB_REPOSITORY', 'enufacas/Chained')
        self.cache_size = cache_size
        
        # Load scoring configuration from registry
        self.weights = self._load_scoring_weights()
        
        # Initialize creativity analyzer with elegant error handling
        self.creativity_analyzer = None
        self.creativity_available = False
        
        try:
            self.creativity_analyzer = self._initialize_creativity_analyzer(github_token)
            self.creativity_available = True
        except (ImportError, FileNotFoundError, AttributeError) as e:
            print(f"⚠️  Warning: Creativity analyzer not available: {e}", file=sys.stderr)
        
        # Ensure metrics directory exists
        METRICS_DIR.mkdir(parents=True, exist_ok=True)
    
    def _initialize_creativity_analyzer(self, github_token: Optional[str]):
        """
        Initialize the creativity analyzer module.
        
        Handles the complexity of loading a hyphenated Python module with grace.
        Raises appropriate exceptions if initialization fails.
        """
        import importlib.util
        
        analyzer_path = Path(__file__).parent / "creativity-metrics-analyzer.py"
        
        spec = importlib.util.spec_from_file_location(
            "creativity_metrics_analyzer",
            analyzer_path
        )
        
        creativity_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(creativity_module)
        
        CreativityAnalyzer = creativity_module.CreativityAnalyzer
        return CreativityAnalyzer(repo=self.repo, github_token=github_token)
    
    def _load_scoring_weights(self) -> Dict[str, float]:
        """
        Load scoring weights from registry configuration.
        
        Returns default weights if registry is unavailable or missing configuration.
        This ensures the system always has sensible defaults to fall back on.
        """
        default_weights = {
            'code_quality': 0.30,
            'issue_resolution': 0.20,
            'pr_success': 0.20,
            'peer_review': 0.15,
            'creativity': 0.15
        }
        
        try:
            if not REGISTRY_FILE.exists():
                return default_weights
            
            with open(REGISTRY_FILE, 'r') as f:
                registry = json.load(f)
                weights = registry.get('config', {}).get('metrics_weight', {})
                
                # Return configured weights if present, otherwise defaults
                return weights if weights else default_weights
                
        except Exception as e:
            print(f"⚠️  Warning: Could not load scoring weights: {e}", file=sys.stderr)
            return default_weights
    
    def collect_agent_activity(
        self,
        agent_id: str,
        since_days: int = DEFAULT_LOOKBACK_DAYS
    ) -> AgentActivity:
        """
        Collect GitHub activity for an agent.
        
        Args:
            agent_id: Agent identifier
            since_days: Look back this many days
            
        Returns:
            AgentActivity object with collected data
        """
        activity = AgentActivity()
        
        # Calculate time range
        since_date = (datetime.now(timezone.utc) - timedelta(days=since_days)).isoformat()
        
        try:
            # Search for issues created by agent
            issues_created = self._search_issues(
                agent_id,
                'is:issue',
                f'author:{self._get_agent_github_user(agent_id)}',
                f'created:>={since_date}'
            )
            activity.issues_created = len(issues_created)
            
            # Search for issues resolved by agent (closed PRs that reference issues)
            issues_resolved = self._search_issues(
                agent_id,
                'is:issue',
                'is:closed',
                f'assignee:{self._get_agent_github_user(agent_id)}'
            )
            activity.issues_resolved = len(issues_resolved)
            
            # Search for PRs created by agent
            prs_created = self._search_issues(
                agent_id,
                'is:pr',
                f'author:{self._get_agent_github_user(agent_id)}',
                f'created:>={since_date}'
            )
            activity.prs_created = len(prs_created)
            
            # Count merged PRs
            prs_merged = [pr for pr in prs_created if pr.get('pull_request', {}).get('merged_at')]
            activity.prs_merged = len(prs_merged)
            
            # Search for reviews given by agent
            reviews = self._get_reviews_by_agent(agent_id, since_days)
            activity.reviews_given = len(reviews)
            
            # Get comments made
            comments = self._get_comments_by_agent(agent_id, since_days)
            activity.comments_made = len(comments)
            
        except Exception as e:
            print(f"⚠️  Warning: Error collecting activity for {agent_id}: {e}", file=sys.stderr)
        
        return activity
    
    def _get_agent_github_user(self, agent_id: str) -> str:
        """
        Map agent ID to GitHub username.
        
        For now, agents use github-actions[bot] as the actor.
        Future: Individual bot accounts per agent.
        """
        # Check if agent has custom GitHub username in registry
        try:
            if REGISTRY_FILE.exists():
                with open(REGISTRY_FILE, 'r') as f:
                    registry = json.load(f)
                    agents = registry.get('agents', [])
                    for agent in agents:
                        if agent.get('id') == agent_id:
                            return agent.get('github_user', 'github-actions[bot]')
        except Exception:
            pass
        
        return 'github-actions[bot]'
    
    def _search_issues(self, agent_id: str, *filters) -> List[Dict]:
        """
        Search GitHub issues/PRs with filters.
        
        Args:
            agent_id: Agent identifier for logging
            *filters: Search filter strings
            
        Returns:
            List of matching issues/PRs
        """
        query = f"repo:{self.repo} " + " ".join(filters)
        
        try:
            results = self.github.get('/search/issues', {'q': query, 'per_page': 100})
            if results and 'items' in results:
                return results['items']
        except Exception as e:
            print(f"⚠️  Warning: Search failed for {agent_id}: {e}", file=sys.stderr)
        
        return []
    
    def _get_reviews_by_agent(self, agent_id: str, since_days: int) -> List[Dict]:
        """
        Get PR reviews by agent.
        
        Note: GitHub API doesn't provide a direct way to search reviews by user,
        so we need to fetch recent PRs and check their reviews.
        """
        reviews = []
        
        try:
            # Get recent PRs in the repo
            prs = self.github.get(
                f'/repos/{self.repo}/pulls',
                {'state': 'all', 'per_page': 50, 'sort': 'updated', 'direction': 'desc'}
            )
            
            if not prs:
                return reviews
            
            agent_user = self._get_agent_github_user(agent_id)
            
            # Check reviews on each PR
            for pr in prs:
                pr_reviews = self.github.get(
                    f'/repos/{self.repo}/pulls/{pr["number"]}/reviews'
                )
                
                if pr_reviews:
                    agent_reviews = [r for r in pr_reviews if r.get('user', {}).get('login') == agent_user]
                    reviews.extend(agent_reviews)
        
        except Exception as e:
            print(f"⚠️  Warning: Error fetching reviews for {agent_id}: {e}", file=sys.stderr)
        
        return reviews
    
    def _get_comments_by_agent(self, agent_id: str, since_days: int) -> List[Dict]:
        """Get issue/PR comments by agent"""
        comments = []
        
        try:
            agent_user = self._get_agent_github_user(agent_id)
            since_date = (datetime.now(timezone.utc) - timedelta(days=since_days)).isoformat()
            
            # Search for comments (issues and PRs)
            result = self.github.get(
                f'/repos/{self.repo}/issues/comments',
                {'since': since_date, 'per_page': 100}
            )
            
            if result:
                comments = [c for c in result if c.get('user', {}).get('login') == agent_user]
        
        except Exception as e:
            print(f"⚠️  Warning: Error fetching comments for {agent_id}: {e}", file=sys.stderr)
        
        return comments
    
    def _collect_contributions_for_creativity(
        self,
        agent_id: str,
        since_days: int
    ) -> List[Dict[str, Any]]:
        """
        Collect contribution data for creativity analysis.
        
        Args:
            agent_id: Agent identifier
            since_days: Look back period
            
        Returns:
            List of contributions with metadata for creativity analysis
        """
        contributions = []
        
        try:
            agent_user = self._get_agent_github_user(agent_id)
            since_date = (datetime.now(timezone.utc) - timedelta(days=since_days)).isoformat()
            
            # Get PRs by agent
            prs = self._search_issues(
                agent_id,
                'is:pr',
                f'author:{agent_user}',
                f'created:>={since_date}'
            )
            
            for pr in prs:
                pr_number = pr['number']
                
                # Get PR details including files changed
                try:
                    pr_details = self.github.get(f'/repos/{self.repo}/pulls/{pr_number}')
                    
                    if not pr_details:
                        continue
                    
                    # Get list of files changed in PR
                    files_data = self.github.get(f'/repos/{self.repo}/pulls/{pr_number}/files')
                    
                    files = []
                    diff_content = ""
                    
                    if files_data:
                        for file_info in files_data:
                            files.append(file_info.get('filename', ''))
                            # Accumulate patch/diff content
                            if file_info.get('patch'):
                                diff_content += file_info.get('patch', '') + "\n"
                    
                    contribution = {
                        'type': 'pull_request',
                        'number': pr_number,
                        'title': pr.get('title', ''),
                        'body': pr.get('body', ''),
                        'files': files,
                        'diff': diff_content,
                        'changed_files': pr_details.get('changed_files', 0),
                        'additions': pr_details.get('additions', 0),
                        'deletions': pr_details.get('deletions', 0),
                        'merged': pr_details.get('merged', False),
                        'created_at': pr.get('created_at', ''),
                        'url': pr.get('html_url', '')
                    }
                    
                    contributions.append(contribution)
                
                except Exception as e:
                    print(f"⚠️  Warning: Error fetching PR {pr_number} details: {e}", file=sys.stderr)
                    continue
        
        except Exception as e:
            print(f"⚠️  Warning: Error collecting contributions for creativity: {e}", file=sys.stderr)
        
        return contributions
    
    def calculate_scores(
        self,
        activity: AgentActivity,
        agent_id: str,
        contributions: Optional[List[Dict[str, Any]]] = None
    ) -> MetricsScore:
        """
        Calculate performance scores from activity data.
        
        Each score component is calculated independently, then weighted
        to produce an overall score. This approach is clear and maintainable.
        
        Args:
            activity: Agent activity data
            agent_id: Agent identifier
            contributions: Optional contribution data for creativity analysis
            
        Returns:
            MetricsScore with all component scores and weighted overall
        """
        scores = MetricsScore()
        
        # Calculate each component score
        scores.code_quality = self._calculate_code_quality_score(activity)
        scores.issue_resolution = self._calculate_issue_resolution_score(activity)
        scores.pr_success = self._calculate_pr_success_score(activity)
        scores.peer_review = self._calculate_peer_review_score(activity)
        scores.creativity = self._calculate_creativity_score(agent_id, contributions)
        
        # Compute weighted overall score
        scores.overall = self._calculate_overall_score(scores)
        
        return scores
    
    def _calculate_code_quality_score(self, activity: AgentActivity) -> float:
        """
        Calculate code quality score based on PR merge success rate.
        
        High merge rates indicate code that passes review and meets standards.
        Future enhancement: Integrate static analysis metrics.
        """
        if activity.prs_created == 0:
            return 0.5  # Neutral score for agents without PRs
        
        merge_rate = activity.prs_merged / activity.prs_created
        return min(1.0, merge_rate * 1.2)  # Bonus for high merge rate
    
    def _calculate_issue_resolution_score(self, activity: AgentActivity) -> float:
        """
        Calculate issue resolution score.
        
        Rewards agents who resolve issues, especially those created by others.
        """
        if activity.issues_created > 0:
            resolution_rate = activity.issues_resolved / activity.issues_created
            return min(1.0, resolution_rate)
        
        if activity.issues_resolved > 0:
            # Resolving others' issues is valuable - normalize to 0-1 scale
            return min(1.0, activity.issues_resolved / 5.0)
        
        return 0.0
    
    def _calculate_pr_success_score(self, activity: AgentActivity) -> float:
        """Calculate PR success score - simple and direct"""
        if activity.prs_created == 0:
            return 0.0
        
        return activity.prs_merged / activity.prs_created
    
    def _calculate_peer_review_score(self, activity: AgentActivity) -> float:
        """
        Calculate peer review score.
        
        Normalize to 0-1 based on reasonable review activity (5+ reviews = 1.0)
        """
        return min(1.0, activity.reviews_given / 5.0)
    
    def _calculate_creativity_score(
        self,
        agent_id: str,
        contributions: Optional[List[Dict[str, Any]]]
    ) -> float:
        """
        Calculate creativity score using advanced analysis or fallback to traits.
        
        Creativity is the hardest metric to quantify, so we use multiple approaches:
        1. Advanced analysis if creativity analyzer is available
        2. Agent's creativity trait from registry as fallback
        3. Neutral 0.5 score if neither is available
        """
        # Try advanced creativity analysis first
        if self.creativity_available and contributions:
            score = self._analyze_creativity_advanced(agent_id, contributions)
            if score is not None:
                return score
        
        # Fallback to agent's creativity trait
        return self._get_creativity_trait_score(agent_id)
    
    def _analyze_creativity_advanced(
        self,
        agent_id: str,
        contributions: List[Dict[str, Any]]
    ) -> Optional[float]:
        """Perform advanced creativity analysis, returns None on failure"""
        try:
            creativity_metrics = self.creativity_analyzer.analyze_creativity(
                agent_id,
                contributions
            )
            return creativity_metrics.score.overall
        except Exception as e:
            print(f"⚠️  Warning: Creativity analysis failed for {agent_id}: {e}", file=sys.stderr)
            return None
    
    def _get_creativity_trait_score(self, agent_id: str) -> float:
        """
        Get creativity score from agent's trait in registry.
        
        Returns 0.5 (neutral) if not found.
        """
        try:
            if not REGISTRY_FILE.exists():
                return 0.5
            
            with open(REGISTRY_FILE, 'r') as f:
                registry = json.load(f)
            
            # Search for agent in both active and hall of fame
            all_agents = registry.get('agents', []) + registry.get('hall_of_fame', [])
            
            for agent in all_agents:
                if agent.get('id') == agent_id:
                    # Convert 0-100 trait to 0-1 score
                    creativity_trait = agent.get('traits', {}).get('creativity', 50)
                    return creativity_trait / 100.0
            
            return 0.5
            
        except Exception:
            return 0.5
    
    def _calculate_overall_score(self, scores: MetricsScore) -> float:
        """
        Calculate weighted overall score from component scores.
        
        Beautiful simplicity - weights times scores, summed.
        """
        return (
            scores.code_quality * self.weights['code_quality'] +
            scores.issue_resolution * self.weights['issue_resolution'] +
            scores.pr_success * self.weights['pr_success'] +
            scores.peer_review * self.weights['peer_review'] +
            scores.creativity * self.weights['creativity']
        )
    
    def collect_metrics(
        self,
        agent_id: str,
        since_days: int = DEFAULT_LOOKBACK_DAYS
    ) -> AgentMetrics:
        """
        Collect complete metrics snapshot for an agent.
        
        Args:
            agent_id: Agent identifier
            since_days: Look back period in days
            
        Returns:
            Complete AgentMetrics object
        """
        print(f"📊 Collecting metrics for {agent_id}...", file=sys.stderr)
        
        # Collect activity
        activity = self.collect_agent_activity(agent_id, since_days)
        
        # Collect contributions for creativity analysis
        contributions = None
        if self.creativity_available:
            contributions = self._collect_contributions_for_creativity(agent_id, since_days)
        
        # Calculate scores (including creativity if contributions available)
        scores = self.calculate_scores(activity, agent_id, contributions)
        
        # Create metrics snapshot
        metrics = AgentMetrics(
            agent_id=agent_id,
            timestamp=datetime.now(timezone.utc).isoformat(),
            activity=activity,
            scores=scores,
            metadata={
                'lookback_days': since_days,
                'repo': self.repo,
                'weights': self.weights,
                'creativity_enabled': self.creativity_available
            }
        )
        
        # Store metrics
        self.store_metrics(metrics)
        
        return metrics
    
    def store_metrics(self, metrics: AgentMetrics) -> None:
        """
        Store metrics snapshot to persistent storage.
        
        Storage format: .github/agent-system/metrics/{agent_id}/{timestamp}.json
        """
        agent_metrics_dir = METRICS_DIR / metrics.agent_id
        agent_metrics_dir.mkdir(parents=True, exist_ok=True)
        
        # Use timestamp as filename (sortable)
        timestamp_str = metrics.timestamp.replace(':', '-').replace('.', '-')
        metrics_file = agent_metrics_dir / f"{timestamp_str}.json"
        
        try:
            with open(metrics_file, 'w') as f:
                json.dump(metrics.to_dict(), f, indent=2)
            
            # Also update latest.json for quick access
            latest_file = agent_metrics_dir / "latest.json"
            with open(latest_file, 'w') as f:
                json.dump(metrics.to_dict(), f, indent=2)
            
            print(f"✅ Metrics stored: {metrics_file}", file=sys.stderr)
        
        except Exception as e:
            print(f"❌ Error storing metrics: {e}", file=sys.stderr)
    
    def load_latest_metrics(self, agent_id: str) -> Optional[AgentMetrics]:
        """Load the most recent metrics snapshot for an agent"""
        latest_file = METRICS_DIR / agent_id / "latest.json"
        
        if not latest_file.exists():
            return None
        
        try:
            with open(latest_file, 'r') as f:
                data = json.load(f)
            
            return AgentMetrics(
                agent_id=data['agent_id'],
                timestamp=data['timestamp'],
                activity=AgentActivity(**data['activity']),
                scores=MetricsScore(**data['scores']),
                metadata=data.get('metadata', {})
            )
        except Exception as e:
            print(f"❌ Error loading metrics: {e}", file=sys.stderr)
            return None
    
    def evaluate_all_agents(self, since_days: int = DEFAULT_LOOKBACK_DAYS) -> Dict[str, AgentMetrics]:
        """
        Evaluate all active agents in the registry.
        
        Returns:
            Dictionary mapping agent_id to AgentMetrics
        """
        results = {}
        
        if not REGISTRY_FILE.exists():
            print("❌ Registry file not found", file=sys.stderr)
            return results
        
        try:
            with open(REGISTRY_FILE, 'r') as f:
                registry = json.load(f)
            
            active_agents = [a for a in registry.get('agents', []) if a.get('status') == 'active']
            
            print(f"📊 Evaluating {len(active_agents)} active agents...", file=sys.stderr)
            
            for agent in active_agents:
                agent_id = agent['id']
                try:
                    metrics = self.collect_metrics(agent_id, since_days)
                    results[agent_id] = metrics
                    
                    # Update registry with new metrics
                    agent['metrics']['issues_resolved'] = metrics.activity.issues_resolved
                    agent['metrics']['prs_merged'] = metrics.activity.prs_merged
                    agent['metrics']['reviews_given'] = metrics.activity.reviews_given
                    agent['metrics']['code_quality_score'] = metrics.scores.code_quality
                    agent['metrics']['creativity_score'] = metrics.scores.creativity
                    agent['metrics']['overall_score'] = metrics.scores.overall
                
                except Exception as e:
                    print(f"❌ Error evaluating {agent_id}: {e}", file=sys.stderr)
            
            # Save updated registry
            with open(REGISTRY_FILE, 'w') as f:
                json.dump(registry, f, indent=2)
            
            print(f"✅ Evaluation complete! Updated {len(results)} agents.", file=sys.stderr)
        
        except Exception as e:
            print(f"❌ Error in evaluation: {e}", file=sys.stderr)
        
        return results


def main():
    """CLI entry point"""
    parser = argparse.ArgumentParser(
        description='Agent Performance Metrics Collector',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument(
        'agent_id',
        nargs='?',
        help='Agent ID to collect metrics for'
    )
    parser.add_argument(
        '--evaluate-all',
        action='store_true',
        help='Evaluate all active agents'
    )
    parser.add_argument(
        '--since',
        type=int,
        default=DEFAULT_LOOKBACK_DAYS,
        help=f'Look back N days (default: {DEFAULT_LOOKBACK_DAYS})'
    )
    parser.add_argument(
        '--verbose',
        '-v',
        action='store_true',
        help='Verbose output'
    )
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output results as JSON'
    )
    
    args = parser.parse_args()
    
    # Initialize collector
    collector = MetricsCollector()
    
    if args.evaluate_all:
        # Evaluate all agents
        results = collector.evaluate_all_agents(args.since)
        
        if args.json:
            print(json.dumps({k: v.to_dict() for k, v in results.items()}, indent=2))
        else:
            print("\n📊 Agent Performance Summary")
            print("=" * 70)
            for agent_id, metrics in sorted(results.items(), key=lambda x: x[1].scores.overall, reverse=True):
                print(f"\n{agent_id}:")
                print(f"  Overall Score: {metrics.scores.overall:.2%}")
                print(f"  Issues Resolved: {metrics.activity.issues_resolved}")
                print(f"  PRs Merged: {metrics.activity.prs_merged}")
                print(f"  Reviews Given: {metrics.activity.reviews_given}")
    
    elif args.agent_id:
        # Evaluate single agent
        metrics = collector.collect_metrics(args.agent_id, args.since)
        
        if args.json:
            print(json.dumps(metrics.to_dict(), indent=2))
        else:
            print(f"\n📊 Metrics for {args.agent_id}")
            print("=" * 70)
            print(f"\n📈 Activity (last {args.since} days):")
            print(f"  Issues Resolved: {metrics.activity.issues_resolved}")
            print(f"  Issues Created: {metrics.activity.issues_created}")
            print(f"  PRs Created: {metrics.activity.prs_created}")
            print(f"  PRs Merged: {metrics.activity.prs_merged}")
            print(f"  Reviews Given: {metrics.activity.reviews_given}")
            print(f"  Comments Made: {metrics.activity.comments_made}")
            
            print(f"\n🎯 Performance Scores:")
            print(f"  Code Quality: {metrics.scores.code_quality:.2%}")
            print(f"  Issue Resolution: {metrics.scores.issue_resolution:.2%}")
            print(f"  PR Success: {metrics.scores.pr_success:.2%}")
            print(f"  Peer Review: {metrics.scores.peer_review:.2%}")
            print(f"  🎨 Creativity: {metrics.scores.creativity:.2%}")
            print(f"\n  ⭐ Overall Score: {metrics.scores.overall:.2%}")
    
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == '__main__':
    main()
