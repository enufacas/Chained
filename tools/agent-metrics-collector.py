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
import re
import sys
from pathlib import Path

# Add tools directory to path for registry manager
sys.path.insert(0, str(Path(__file__).parent))

import time
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from functools import lru_cache
import argparse

# Import registry manager
try:
    from registry_manager import RegistryManager
    REGISTRY_MANAGER_AVAILABLE = True
except ImportError:
    REGISTRY_MANAGER_AVAILABLE = False

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
        
        def get(self, endpoint, params=None, headers=None):
            """Minimal fallback implementation with support for custom headers"""
            import urllib.request
            import urllib.error
            import urllib.parse
            
            url = f"https://api.github.com{endpoint}"
            if params:
                url = f"{url}?{urllib.parse.urlencode(params)}"
            
            req = urllib.request.Request(url)
            if self.token:
                req.add_header('Authorization', f'token {self.token}')
            
            # Set default Accept header
            req.add_header('Accept', 'application/vnd.github.v3+json')
            
            # Override with custom headers if provided
            if headers:
                for key, value in headers.items():
                    req.add_header(key, value)
            
            try:
                with urllib.request.urlopen(req, timeout=10) as response:
                    return json.loads(response.read().decode('utf-8'))
            except urllib.error.HTTPError as e:
                # Log HTTP errors with details for debugging
                print(f"⚠️  GitHub API HTTP {e.code}: {e.reason} for {endpoint}", file=sys.stderr)
                if e.code == 403:
                    print(f"⚠️  API rate limit or authentication issue. Check GITHUB_TOKEN.", file=sys.stderr)
                return None
            except Exception as e:
                print(f"⚠️  GitHub API error for {endpoint}: {e}", file=sys.stderr)
                return None

# Constants
METRICS_DIR = Path(".github/agent-system/metrics")
REGISTRY_FILE = Path(".github/agent-system/registry.json")
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
        
        # Initialize caches for batch evaluation optimization
        self._issue_cache: Dict[int, Dict] = {}  # issue_number -> issue_details
        self._pr_cache: Dict[int, Dict] = {}  # pr_number -> pr_details
        self._timeline_cache: Dict[int, List] = {}  # issue_number -> timeline events
        self._api_call_count = 0  # Track API calls for monitoring
        
        # Check GitHub API connectivity
        self._check_github_api_access()
        
        # Load scoring configuration from registry
        self.weights = self._load_scoring_weights()
        
        # Initialize creativity analyzer
        try:
            from pathlib import Path
            import sys
            import importlib.util
            
            # Handle hyphenated filename
            analyzer_path = Path(__file__).parent / "creativity-metrics-analyzer.py"
            spec = importlib.util.spec_from_file_location(
                "creativity_metrics_analyzer",
                analyzer_path
            )
            creativity_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(creativity_module)
            
            CreativityAnalyzer = creativity_module.CreativityAnalyzer
            self.creativity_analyzer = CreativityAnalyzer(repo=self.repo, github_token=github_token)
            self.creativity_available = True
        except (ImportError, FileNotFoundError, AttributeError) as e:
            print(f"⚠️  Warning: Creativity analyzer not available: {e}", file=sys.stderr)
            self.creativity_analyzer = None
            self.creativity_available = False
        
        # Ensure metrics directory exists
        METRICS_DIR.mkdir(parents=True, exist_ok=True)
    
    def _check_github_api_access(self) -> bool:
        """
        Check if GitHub API is accessible with current token.
        
        Returns:
            True if API is accessible, False otherwise
        """
        try:
            # Simple API call to check connectivity
            result = self.github.get('/rate_limit')
            if result:
                rate = result.get('rate', {})
                remaining = rate.get('remaining', 0)
                limit = rate.get('limit', 0)
                print(f"✅ GitHub API accessible. Rate limit: {remaining}/{limit}", file=sys.stderr)
                
                if remaining < 100:
                    print(f"⚠️  Warning: Low rate limit remaining ({remaining})", file=sys.stderr)
                    print(f"⚠️  Consider reducing evaluation frequency or optimizing queries", file=sys.stderr)
                
                return True
            else:
                print(f"⚠️  Warning: GitHub API not accessible. PR attribution may be inaccurate.", file=sys.stderr)
                return False
        except Exception as e:
            print(f"⚠️  Warning: Could not check GitHub API access: {e}", file=sys.stderr)
            return False
    
    def clear_caches(self) -> None:
        """
        Clear all internal caches.
        
        This should be called between separate evaluation runs to ensure fresh data.
        """
        self._issue_cache.clear()
        self._pr_cache.clear()
        self._timeline_cache.clear()
        self._api_call_count = 0
        print("🔄 Caches cleared", file=sys.stderr)
    
    def get_api_stats(self) -> Dict[str, Any]:
        """
        Get statistics about API usage during this session.
        
        Returns:
            Dictionary with API usage stats
        """
        return {
            'api_calls': self._api_call_count,
            'cached_issues': len(self._issue_cache),
            'cached_prs': len(self._pr_cache),
            'cached_timelines': len(self._timeline_cache)
        }
    
    def _load_scoring_weights(self) -> Dict[str, float]:
        """Load scoring weights from registry configuration"""
        try:
            if REGISTRY_MANAGER_AVAILABLE:
                registry = RegistryManager()
                config = registry.get_config()
                return config.get('metrics_weight', {})
        except Exception as e:
            print(f"⚠️  Warning: Could not load scoring weights: {e}", file=sys.stderr)
        
        # Default weights (updated to include creativity)
        return {
            'code_quality': 0.30,
            'issue_resolution': 0.20,
            'pr_success': 0.20,
            'peer_review': 0.15,
            'creativity': 0.15
        }
    
    def _get_agent_specialization(self, agent_id: str) -> Optional[str]:
        """
        Get the specialization for an agent from the registry.
        
        Args:
            agent_id: Agent identifier
            
        Returns:
            Specialization name or None
        """
        try:
            if REGISTRY_MANAGER_AVAILABLE:
                registry = RegistryManager()
                agent = registry.get_agent(agent_id)
                if agent:
                    return agent.get('specialization')
                    
                # Check hall of fame too
                hall_of_fame = registry.get_hall_of_fame()
                for agent in hall_of_fame:
                    if agent.get('id') == agent_id:
                        return agent.get('specialization')
        except Exception as e:
            print(f"⚠️  Warning: Could not get specialization for {agent_id}: {e}", file=sys.stderr)
        
        return None
    
    def _batch_fetch_all_agent_issues(self, since_days: int) -> Dict[str, List[Dict]]:
        """
        Pre-fetch ALL agent-work issues once and distribute to agents.
        
        OPTIMIZED: Uses search body to avoid fetching individual issues.
        This is a critical optimization that reduces O(n*m) API calls to O(m) calls,
        where n = number of agents and m = number of issues.
        
        Args:
            since_days: Look back period
            
        Returns:
            Dictionary mapping agent_id to list of assigned issues
        """
        print(f"🔄 Batch fetching all agent-work issues (last {since_days} days)...")
        
        agent_issues_map = {}
        since_date = (datetime.now(timezone.utc) - timedelta(days=since_days)).isoformat()
        
        # Build agent specialization -> agent_id map for quick lookup
        specialization_to_agent = {}
        try:
            if REGISTRY_MANAGER_AVAILABLE:
                registry = RegistryManager()
                active_agents = registry.list_agents(status='active')
                for agent in active_agents:
                    spec = agent.get('specialization', '').lower()
                    if spec:
                        specialization_to_agent[spec] = {
                            'id': agent['id'],
                            'name': agent['name']
                        }
        except Exception as e:
            print(f"⚠️  Warning: Could not load agent registry: {e}", file=sys.stderr)
            return agent_issues_map
        
        try:
            # Fetch all agent-work issues in a single search
            all_issues = self._search_issues(
                'batch_fetch',
                'is:issue',
                'label:agent-work',
                f'created:>={since_date}'
            )
            self._api_call_count += 1
            
            print(f"📋 Found {len(all_issues)} total agent-work issues")
            
            # OPTIMIZATION: Search results already include body, use it directly
            # Only fetch full details if body is missing
            for issue in all_issues:
                issue_number = issue.get('number')
                if not issue_number:
                    continue
                
                # Try to use body from search results first (much faster!)
                body = issue.get('body', '')
                
                # If body is missing or truncated, fetch full details
                if not body or len(body) < 50:  # Likely truncated
                    # Check cache first
                    if issue_number in self._issue_cache:
                        issue_details = self._issue_cache[issue_number]
                        body = issue_details.get('body', '')
                    else:
                        # Fetch if not cached
                        issue_details = self.github.get(f'/repos/{self.repo}/issues/{issue_number}')
                        self._api_call_count += 1
                        if issue_details:
                            self._issue_cache[issue_number] = issue_details
                            body = issue_details.get('body', '')
                            issue = issue_details  # Use full details
                        else:
                            continue
                else:
                    # Cache the search result
                    self._issue_cache[issue_number] = issue
                
                # Extract COPILOT_AGENT assignment from body
                # Format: <!-- COPILOT_AGENT:specialization_name -->
                pattern = r'<!--\s*COPILOT_AGENT:\s*([a-z\-]+)\s*-->'
                match = re.search(pattern, body, re.IGNORECASE)
                
                if match:
                    specialization = match.group(1).lower()
                    
                    # Quick lookup in pre-built map
                    agent_info = specialization_to_agent.get(specialization)
                    if agent_info:
                        agent_id = agent_info['id']
                        if agent_id not in agent_issues_map:
                            agent_issues_map[agent_id] = []
                        agent_issues_map[agent_id].append(issue)
                        print(f"  ✅ Issue #{issue_number} → {agent_info['name']}", file=sys.stderr)
            
            print(f"✅ Distributed issues to {len(agent_issues_map)} agents")
            print(f"📊 API calls so far: {self._api_call_count}")
            
        except Exception as e:
            print(f"⚠️  Warning: Batch fetch failed: {e}", file=sys.stderr)
        
        return agent_issues_map
    
    def _is_strict_pr_attribution_enabled(self) -> bool:
        """
        Check if strict PR attribution checking is enabled in config.
        
        Returns:
            True if strict attribution is enabled, False otherwise
        """
        try:
            if REGISTRY_MANAGER_AVAILABLE:
                registry = RegistryManager()
                config = registry.get_config()
                return config.get('strict_pr_attribution', True)  # Default to True
        except Exception as e:
            print(f"⚠️  Warning: Could not load config: {e}", file=sys.stderr)
        
        # Default to True for security and accuracy
        return True
    
    def _find_issues_assigned_to_agent(
        self,
        agent_id: str,
        since_days: int,
        use_batch_cache: bool = False,
        batch_cache: Optional[Dict[str, List[Dict]]] = None
    ) -> List[Dict]:
        """
        Find issues assigned to this agent via COPILOT_AGENT comment.
        
        This method searches for issues that contain the agent's specialization
        in a COPILOT_AGENT comment, which is how custom agents are assigned.
        
        Args:
            agent_id: Agent identifier
            since_days: Look back period
            use_batch_cache: If True, use pre-fetched batch cache instead of searching
            batch_cache: Pre-fetched issues map from batch operation
            
        Returns:
            List of issues assigned to this agent
        """
        # Use batch cache if available (optimization for evaluate_all_agents)
        if use_batch_cache and batch_cache is not None:
            cached_issues = batch_cache.get(agent_id, [])
            print(f"✅ Using batch cache for {agent_id}: {len(cached_issues)} issues (0 API calls)", file=sys.stderr)
            return cached_issues
        
        # Fallback to individual agent search (for single-agent metrics)
        assigned_issues = []
        specialization = self._get_agent_specialization(agent_id)
        
        if not specialization:
            print(f"⚠️  Warning: No specialization found for {agent_id}", file=sys.stderr)
            return assigned_issues
        
        print(f"🔍 [FALLBACK] Looking for issues assigned to agent {agent_id} (specialization: {specialization})", file=sys.stderr)
        
        try:
            since_date = (datetime.now(timezone.utc) - timedelta(days=since_days)).isoformat()
            
            # Search for all issues with agent-work label created in timeframe
            issues = self._search_issues(
                agent_id,
                'is:issue',
                'label:agent-work',
                f'created:>={since_date}'
            )
            self._api_call_count += 1
            
            print(f"📋 Found {len(issues)} total agent-work issues in timeframe", file=sys.stderr)
            
            # Filter issues by checking body for COPILOT_AGENT comment
            for issue in issues:
                issue_number = issue.get('number')
                if not issue_number:
                    continue
                
                # Check cache first
                if issue_number in self._issue_cache:
                    issue_details = self._issue_cache[issue_number]
                else:
                    # Fetch full issue details to get body
                    try:
                        issue_details = self.github.get(f'/repos/{self.repo}/issues/{issue_number}')
                        self._api_call_count += 1
                        if issue_details:
                            self._issue_cache[issue_number] = issue_details
                    except Exception as e:
                        print(f"⚠️  Warning: Error fetching issue {issue_number}: {e}", file=sys.stderr)
                        continue
                
                if not issue_details:
                    continue
                
                body = issue_details.get('body', '')
                
                # Check for COPILOT_AGENT comment with this agent's specialization
                # Format: <!-- COPILOT_AGENT:specialization_name -->
                pattern = rf'<!--\s*COPILOT_AGENT:\s*{re.escape(specialization)}\s*-->'
                if re.search(pattern, body, re.IGNORECASE):
                    assigned_issues.append(issue_details)
                    print(f"  ✅ Issue #{issue_number} assigned to {specialization}", file=sys.stderr)
            
            print(f"✅ Found {len(assigned_issues)} issues assigned to {agent_id}", file=sys.stderr)
        
        except Exception as e:
            print(f"⚠️  Warning: Error finding assigned issues for {agent_id}: {e}", file=sys.stderr)
        
        return assigned_issues
    
    def _extract_agent_mentions_from_text(self, text: str) -> List[str]:
        """
        Extract agent mentions from text (PR description, comments, etc.).
        
        Looks for @agent-name patterns where agent-name matches known specializations.
        
        Args:
            text: Text to search for agent mentions
            
        Returns:
            List of agent specializations mentioned
        """
        if not text:
            return []
        
        # Pattern matches @agent-name format (e.g., @engineer-master, @bug-hunter)
        # Agents are identified by their specialization names
        pattern = r'@([a-z]+-[a-z]+(?:-[a-z]+)?)'
        matches = re.findall(pattern, text.lower())
        
        return list(set(matches))  # Return unique mentions
    
    def _check_pr_agent_attribution(
        self,
        pr_number: int,
        expected_specialization: str
    ) -> bool:
        """
        Check if a PR was actually done by the expected agent.
        
        This examines:
        1. PR description for @agent-name mentions
        2. PR comments for @agent-name mentions
        3. Commit messages for @agent-name mentions (future enhancement)
        
        Args:
            pr_number: PR number to check
            expected_specialization: The specialization we expect to see mentioned
            
        Returns:
            True if the PR was attributed to the expected agent, False otherwise
        """
        try:
            # Get PR details including description
            pr_details = self.github.get(f'/repos/{self.repo}/pulls/{pr_number}')
            if not pr_details:
                return False
            
            pr_body = pr_details.get('body', '')
            pr_title = pr_details.get('title', '')
            
            # Check PR title and description for agent mentions
            title_mentions = self._extract_agent_mentions_from_text(pr_title)
            body_mentions = self._extract_agent_mentions_from_text(pr_body)
            
            if expected_specialization in title_mentions or expected_specialization in body_mentions:
                print(f"  ✅ PR #{pr_number} attributed to {expected_specialization} (title/description)", file=sys.stderr)
                return True
            
            # Get PR comments
            try:
                comments = self.github.get(f'/repos/{self.repo}/issues/{pr_number}/comments')
                if comments:
                    for comment in comments:
                        comment_body = comment.get('body', '')
                        comment_mentions = self._extract_agent_mentions_from_text(comment_body)
                        
                        if expected_specialization in comment_mentions:
                            print(f"  ✅ PR #{pr_number} attributed to {expected_specialization} (comments)", file=sys.stderr)
                            return True
            except Exception as e:
                print(f"  ⚠️  Warning: Could not fetch comments for PR {pr_number}: {e}", file=sys.stderr)
            
            # If we get here, no clear attribution found
            print(f"  ⚠️  PR #{pr_number} has no clear attribution to {expected_specialization}", file=sys.stderr)
            return False
            
        except Exception as e:
            print(f"⚠️  Warning: Error checking PR attribution for #{pr_number}: {e}", file=sys.stderr)
            return False
    
    def _filter_prs_by_agent_attribution(
        self,
        prs: List[Dict],
        expected_specialization: str,
        strict_mode: bool = True
    ) -> List[Dict]:
        """
        Filter PRs to only include those actually done by the expected agent.
        
        Args:
            prs: List of PR data dictionaries
            expected_specialization: The specialization to filter for
            strict_mode: If True, only count PRs with clear attribution
            
        Returns:
            Filtered list of PRs
        """
        if not strict_mode:
            # In non-strict mode, accept all PRs (backward compatible behavior)
            return prs
        
        print(f"🔍 Filtering {len(prs)} PRs for {expected_specialization} attribution...", file=sys.stderr)
        
        attributed_prs = []
        for pr in prs:
            pr_number = pr.get('number')
            if not pr_number:
                continue
            
            if self._check_pr_agent_attribution(pr_number, expected_specialization):
                attributed_prs.append(pr)
        
        print(f"  📊 {len(attributed_prs)}/{len(prs)} PRs have clear attribution to {expected_specialization}", file=sys.stderr)
        
        return attributed_prs
    
    def collect_agent_activity(
        self,
        agent_id: str,
        since_days: int = DEFAULT_LOOKBACK_DAYS,
        use_batch_cache: bool = False,
        batch_cache: Optional[Dict[str, List[Dict]]] = None
    ) -> AgentActivity:
        """
        Collect GitHub activity for an agent.
        
        This method now uses COPILOT_AGENT comments to attribute work to agents.
        
        Args:
            agent_id: Agent identifier
            since_days: Look back this many days
            use_batch_cache: If True, use pre-fetched batch cache
            batch_cache: Pre-fetched issues map from batch operation
            
        Returns:
            AgentActivity object with collected data
        """
        activity = AgentActivity()
        
        # Calculate time range
        since_date = (datetime.now(timezone.utc) - timedelta(days=since_days)).isoformat()
        
        try:
            # Find issues assigned to this agent (using cache if available)
            assigned_issues = self._find_issues_assigned_to_agent(
                agent_id, 
                since_days,
                use_batch_cache=use_batch_cache,
                batch_cache=batch_cache
            )
            activity.issues_created = len(assigned_issues)
            
            # SHORT-CIRCUIT OPTIMIZATION: If agent has no assigned issues, skip expensive PR/review lookups
            if len(assigned_issues) == 0:
                print(f"⚡ Short-circuit: {agent_id} has no assigned issues, skipping PR/review lookups")
                return activity  # Return early with all zeros
            
            # Count resolved issues (closed ones)
            resolved_issues = [issue for issue in assigned_issues if issue.get('state') == 'closed']
            activity.issues_resolved = len(resolved_issues)
            
            # Find PRs that close issues assigned to this agent
            # OPTIMIZED: Smarter fallback strategy to minimize expensive timeline API calls
            prs_for_agent = []
            pr_numbers_from_issues = set()
            issues_needing_search = []  # Defer expensive operations
            
            # Phase 1: Quick body scan for PR references (fastest, no extra API calls)
            for issue in assigned_issues:
                issue_number = issue.get('number')
                body = issue.get('body', '')
                pr_refs = re.findall(r'#(\d+)', body)
                found_pr_for_issue = False
                
                for pr_ref in pr_refs:
                    pr_number = int(pr_ref)
                    if pr_number != issue_number and pr_number not in pr_numbers_from_issues:
                        # Verify it's actually a PR (check cache first)
                        if pr_number in self._pr_cache:
                            pr_data = self._pr_cache[pr_number]
                            if pr_data.get('pull_request'):
                                prs_for_agent.append(pr_data)
                                pr_numbers_from_issues.add(pr_number)
                                found_pr_for_issue = True
                                print(f"  ✅ Found PR #{pr_number} via issue body reference", file=sys.stderr)
                
                # Track issues that need more expensive searches
                if not found_pr_for_issue:
                    issues_needing_search.append(issue)
            
            # Phase 2: Batch PR search (if needed, more efficient than timeline)
            if issues_needing_search and len(issues_needing_search) <= 10:
                try:
                    # Build search query for multiple issues at once
                    issue_numbers_query = ' OR '.join([f'#{issue.get("number")}' for issue in issues_needing_search])
                    
                    search_results = self._search_issues(
                        agent_id,
                        'is:pr',
                        f'({issue_numbers_query})'
                    )
                    self._api_call_count += 1
                    
                    for pr in search_results:
                        pr_number = pr.get('number')
                        if pr_number and pr_number not in pr_numbers_from_issues:
                            # Cache this PR
                            if pr_number not in self._pr_cache:
                                self._pr_cache[pr_number] = pr
                            prs_for_agent.append(pr)
                            pr_numbers_from_issues.add(pr_number)
                            print(f"  ✅ Found PR #{pr_number} via batch search", file=sys.stderr)
                    
                    # Update list - remove issues we found PRs for
                    found_issue_numbers = set()
                    for pr in search_results:
                        pr_body = pr.get('body', '').lower()
                        for issue in issues_needing_search:
                            if f'#{issue.get("number")}' in pr_body:
                                found_issue_numbers.add(issue.get('number'))
                    
                    issues_needing_search = [
                        issue for issue in issues_needing_search 
                        if issue.get('number') not in found_issue_numbers
                    ]
                
                except Exception as e:
                    print(f"⚠️  Warning: Batch PR search failed: {e}", file=sys.stderr)
            
            # Phase 3: Timeline API for remaining closed issues (most expensive, minimal use)
            # Only use for closed issues that likely have PRs, limit to 3 calls
            closed_issues = [issue for issue in issues_needing_search if issue.get('state') == 'closed']
            for issue in closed_issues[:3]:  # Strict limit on timeline calls
                issue_number = issue.get('number')
                try:
                    # Check cache first
                    if issue_number in self._timeline_cache:
                        timeline = self._timeline_cache[issue_number]
                    else:
                        # Only fetch timeline if we haven't cached it yet
                        timeline = self.github.get(
                            f'/repos/{self.repo}/issues/{issue_number}/timeline',
                            headers={'Accept': 'application/vnd.github.mockingbird-preview+json'}
                        )
                        self._api_call_count += 1
                        if timeline:
                            self._timeline_cache[issue_number] = timeline
                    
                    if timeline:
                        for event in timeline:
                            if event.get('event') == 'cross-referenced':
                                source = event.get('source', {})
                                if source.get('type') == 'issue' and source.get('issue', {}).get('pull_request'):
                                    pr_data = source.get('issue')
                                    pr_number = pr_data.get('number')
                                    if pr_number and pr_number not in pr_numbers_from_issues:
                                        # Check cache for full PR details
                                        if pr_number in self._pr_cache:
                                            full_pr = self._pr_cache[pr_number]
                                        else:
                                            try:
                                                full_pr = self.github.get(f'/repos/{self.repo}/pulls/{pr_number}')
                                                self._api_call_count += 1
                                                if full_pr:
                                                    self._pr_cache[pr_number] = full_pr
                                            except Exception as e:
                                                full_pr = pr_data  # Fallback to partial data
                                        
                                        if full_pr:
                                            prs_for_agent.append(full_pr)
                                            pr_numbers_from_issues.add(pr_number)
                                            merge_status = "merged" if full_pr.get('merged_at') else "open/closed"
                                            print(f"  ✅ Found PR #{pr_number} ({merge_status}) via timeline for issue #{issue_number}", file=sys.stderr)
                except Exception as e:
                    print(f"⚠️  Warning: Timeline API failed for issue {issue_number}: {e}", file=sys.stderr)
            
            # Method 4: Git-based fallback when GitHub API is unavailable
            if len(prs_for_agent) == 0 and len(assigned_issues) > 0:
                print(f"🔧 GitHub API yielded no PRs, trying git-based fallback...", file=sys.stderr)
                git_prs = self._find_prs_via_git(agent_id, assigned_issues)
                for pr_info in git_prs:
                    pr_number = pr_info.get('number')
                    if pr_number and pr_number not in pr_numbers_from_issues:
                        prs_for_agent.append(pr_info)
                        pr_numbers_from_issues.add(pr_number)
                        print(f"  ✅ Found PR #{pr_number} via git log", file=sys.stderr)
            
            print(f"📊 Found {len(prs_for_agent)} PRs linked to {len(assigned_issues)} assigned issues", file=sys.stderr)
            
            activity.prs_created = len(prs_for_agent)
            
            # Count merged PRs
            prs_merged = []
            for pr in prs_for_agent:
                if pr.get('source') == 'git_log':
                    prs_merged.append(pr)
                elif pr.get('merged_at'):
                    prs_merged.append(pr)
                elif pr.get('pull_request', {}).get('merged_at'):
                    prs_merged.append(pr)
                elif pr.get('state') == 'closed' and pr.get('merged', False):
                    prs_merged.append(pr)
            
            activity.prs_merged = len(prs_merged)
            print(f"  ✅ {len(prs_merged)} PRs were merged", file=sys.stderr)
            
            # SHORT-CIRCUIT OPTIMIZATION: Only look for reviews if agent has PR activity
            # Reviews are expensive to fetch since we have to check multiple PRs
            if activity.prs_created > 0 or activity.issues_resolved > 5:
                # Search for reviews given by agent
                reviews = self._get_reviews_by_agent(agent_id, since_days)
                activity.reviews_given = len(reviews)
            else:
                print(f"⚡ Short-circuit: Skipping review lookup (no significant PR activity)")
                activity.reviews_given = 0
            
            # Get comments made by agent on assigned issues
            # SHORT-CIRCUIT: Only fetch if we have assigned issues
            comments_count = 0
            if len(assigned_issues) > 0:
                for issue in assigned_issues:
                    issue_number = issue.get('number')
                    try:
                        comments = self.github.get(f'/repos/{self.repo}/issues/{issue_number}/comments')
                        self._api_call_count += 1
                        if comments:
                            agent_user = self._get_agent_github_user(agent_id)
                            agent_comments = [c for c in comments if c.get('user', {}).get('login') == agent_user]
                            comments_count += len(agent_comments)
                    except Exception:
                        pass
            else:
                print(f"⚡ Short-circuit: Skipping comment lookup (no assigned issues)")
            
            activity.comments_made = comments_count
            
            # Log activity summary
            print(f"📊 Activity summary for {agent_id}:")
            print(f"  - Issues assigned: {activity.issues_created}")
            print(f"  - Issues resolved: {activity.issues_resolved}")
            print(f"  - PRs created: {activity.prs_created}")
            print(f"  - PRs merged: {activity.prs_merged}")
            print(f"  - Reviews given: {activity.reviews_given}")
            print(f"  - Comments made: {activity.comments_made}")
            print(f"  - API calls used: {self._api_call_count}")
            
        except Exception as e:
            print(f"⚠️  Warning: Error collecting activity for {agent_id}: {e}", file=sys.stderr)
        
        return activity
    
    def _find_prs_via_git(self, agent_id: str, assigned_issues: List[Dict]) -> List[Dict]:
        """
        Fallback method to find PRs using git log when GitHub API is unavailable.
        
        This method:
        1. Parses commit messages for issue references (Fixes #123, Closes #456, etc.)
        2. Extracts PR numbers from merge commits
        3. Returns PR info for PRs that resolved assigned issues
        
        Args:
            agent_id: Agent identifier
            assigned_issues: List of issues assigned to this agent
            
        Returns:
            List of PR info dictionaries
        """
        import subprocess
        import re
        
        prs_found = []
        
        # Extract issue numbers from assigned issues
        issue_numbers = {issue.get('number') for issue in assigned_issues if issue.get('number')}
        if not issue_numbers:
            return prs_found
        
        try:
            # Get git log with commit messages
            # Look for merge commits and issue references
            result = subprocess.run(
                ['git', 'log', '--merges', '--grep', '#[0-9]', '--oneline', '-n', '500'],
                capture_output=True,
                text=True,
                timeout=10,
                cwd='.'
            )
            
            if result.returncode != 0:
                print(f"⚠️  Git log failed: {result.stderr}", file=sys.stderr)
                return prs_found
            
            # Parse merge commits to find PR numbers and issue references
            # Format: "Merge pull request #123 from branch"
            # Or commits like: "Fix #456: Description"
            merge_pr_pattern = re.compile(r'Merge pull request #(\d+)')
            issue_ref_patterns = [
                re.compile(r'(?:Fix|Fixes|Close|Closes|Resolve|Resolves)\s+#(\d+)', re.IGNORECASE),
                re.compile(r'#(\d+)'),  # Fallback: any #number
            ]
            
            lines = result.stdout.strip().split('\n')
            for line in lines:
                if not line.strip():
                    continue
                    
                # Try to find PR number from merge commit
                merge_match = merge_pr_pattern.search(line)
                if merge_match:
                    pr_number = int(merge_match.group(1))
                    
                    # Check if this merge commit mentions any of our issues
                    for pattern in issue_ref_patterns:
                        issue_matches = pattern.findall(line)
                        for issue_num_str in issue_matches:
                            issue_num = int(issue_num_str)
                            if issue_num in issue_numbers:
                                # Found a PR that closed one of our issues!
                                pr_info = {
                                    'number': pr_number,
                                    'issue_number': issue_num,
                                    'pull_request': {
                                        'merged_at': True  # Assume merged if in git log
                                    },
                                    'state': 'closed',
                                    'source': 'git_log'
                                }
                                prs_found.append(pr_info)
                                print(f"    🔍 Git log: PR #{pr_number} → Issue #{issue_num}", file=sys.stderr)
                                break  # Found match for this PR, move to next line
        
        except subprocess.TimeoutExpired:
            print(f"⚠️  Git log timeout", file=sys.stderr)
        except Exception as e:
            print(f"⚠️  Error parsing git log: {e}", file=sys.stderr)
        
        return prs_found
    
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
        
        Scoring algorithm:
        - Code Quality: Based on PR merge rate and code analysis (future)
        - Issue Resolution: Issues resolved / issues created ratio
        - PR Success: PRs merged / PRs created ratio
        - Peer Review: Normalized review activity
        - Creativity: Novel patterns, diversity, impact, learning (if available)
        
        Args:
            activity: Agent activity data
            agent_id: Agent identifier
            contributions: Optional list of contribution data for creativity analysis
            
        Returns:
            MetricsScore with calculated scores
        """
        scores = MetricsScore()
        
        # Code Quality Score
        # For now, based on PR merge success rate
        # Future: Integrate with code-analyzer.py for static analysis
        if activity.prs_created > 0:
            merge_rate = activity.prs_merged / activity.prs_created
            scores.code_quality = min(1.0, merge_rate * 1.2)  # Bonus for high merge rate
        else:
            scores.code_quality = 0.5  # Neutral score for new agents
        
        # Issue Resolution Score
        if activity.issues_created > 0:
            resolution_rate = activity.issues_resolved / activity.issues_created
            scores.issue_resolution = min(1.0, resolution_rate)
        elif activity.issues_resolved > 0:
            # Agent is resolving issues created by others - good!
            scores.issue_resolution = min(1.0, activity.issues_resolved / 5.0)
        else:
            scores.issue_resolution = 0.0
        
        # PR Success Score
        if activity.prs_created > 0:
            pr_success_rate = activity.prs_merged / activity.prs_created
            scores.pr_success = pr_success_rate
        else:
            scores.pr_success = 0.0
        
        # Peer Review Score
        # Normalize to 0-1 based on reasonable review activity (5+ reviews = 1.0)
        scores.peer_review = min(1.0, activity.reviews_given / 5.0)
        
        # Creativity Score
        if self.creativity_available and contributions:
            try:
                creativity_metrics = self.creativity_analyzer.analyze_creativity(
                    agent_id, 
                    contributions
                )
                scores.creativity = creativity_metrics.score.overall
            except Exception as e:
                print(f"⚠️  Warning: Creativity analysis failed for {agent_id}: {e}", file=sys.stderr)
                scores.creativity = 0.5  # Neutral score on error
        else:
            # Fallback: Use randomized trait from registry as baseline
            try:
                if REGISTRY_FILE.exists():
                    with open(REGISTRY_FILE, 'r') as f:
                        registry = json.load(f)
                        agents = registry.get('agents', [])
                        for agent in agents:
                            if agent.get('id') == agent_id:
                                # Convert 0-100 trait to 0-1 score
                                creativity_trait = agent.get('traits', {}).get('creativity', 50)
                                scores.creativity = creativity_trait / 100.0
                                break
                        else:
                            scores.creativity = 0.5
            except Exception:
                scores.creativity = 0.5
        
        # Calculate weighted overall score
        scores.overall = (
            scores.code_quality * self.weights.get('code_quality', 0.30) +
            scores.issue_resolution * self.weights.get('issue_resolution', 0.20) +
            scores.pr_success * self.weights.get('pr_success', 0.20) +
            scores.peer_review * self.weights.get('peer_review', 0.15) +
            scores.creativity * self.weights.get('creativity', 0.15)
        )
        
        return scores
    
    def collect_metrics(
        self,
        agent_id: str,
        since_days: int = DEFAULT_LOOKBACK_DAYS,
        use_batch_cache: bool = False,
        batch_cache: Optional[Dict[str, List[Dict]]] = None
    ) -> AgentMetrics:
        """
        Collect complete metrics snapshot for an agent.
        
        Args:
            agent_id: Agent identifier
            since_days: Look back period in days
            use_batch_cache: If True, use pre-fetched batch cache
            batch_cache: Pre-fetched issues map from batch operation
            
        Returns:
            Complete AgentMetrics object
        """
        print(f"📊 Collecting metrics for {agent_id}...")
        
        # Collect activity (with batch cache if available)
        activity = self.collect_agent_activity(
            agent_id, 
            since_days,
            use_batch_cache=use_batch_cache,
            batch_cache=batch_cache
        )
        
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
                'creativity_enabled': self.creativity_available,
                'api_calls': self._api_call_count
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
        
        This method uses batch optimization to minimize API calls:
        - Fetches all agent-work issues once
        - Distributes them to agents
        - Uses caching for repeated data access
        
        Returns:
            Dictionary mapping agent_id to AgentMetrics
        """
        results = {}
        
        try:
            if REGISTRY_MANAGER_AVAILABLE:
                registry = RegistryManager()
                active_agents = registry.list_agents(status='active')
            else:
                print("❌ Registry manager not available", file=sys.stderr)
                return results
            
            total_agents = len(active_agents)
            print(f"📊 Evaluating {total_agents} active agents...", file=sys.stderr)
            
            # OPTIMIZATION: Batch fetch all issues once, then distribute to agents
            print(f"🚀 Starting batch optimization...")
            batch_cache = self._batch_fetch_all_agent_issues(since_days)
            print(f"✅ Batch fetch complete. Starting agent evaluation...")
            
            for idx, agent in enumerate(active_agents, 1):
                agent_id = agent['id']
                agent_name = agent.get('name', agent_id)
                
                print(f"\n{'='*70}", file=sys.stderr)
                print(f"📊 Evaluating agent {idx}/{total_agents}: {agent_name}", file=sys.stderr)
                print(f"{'='*70}", file=sys.stderr)
                
                try:
                    # Use batch cache to avoid redundant API calls
                    metrics = self.collect_metrics(
                        agent_id, 
                        since_days,
                        use_batch_cache=True,
                        batch_cache=batch_cache
                    )
                    results[agent_id] = metrics
                    
                    print(f"✅ [{idx}/{total_agents}] Collected metrics for {agent_name}: score={metrics.scores.overall:.2%}", file=sys.stderr)
                
                except Exception as e:
                    print(f"❌ Error evaluating {agent_id}: {e}", file=sys.stderr)
            
            print(f"✅ Evaluation complete! Collected metrics for {len(results)} agents.")
            print(f"📊 Total API calls used: {self._api_call_count}")
            print(f"ℹ️  Note: Registry updates are handled by the evaluator workflow", file=sys.stderr)
        
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
