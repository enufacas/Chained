#!/usr/bin/env python3
"""
GitHub Copilot Usage Tracker

Tracks GitHub Copilot API usage (premium requests) and calculates burn rate
to enable dynamic workflow scheduling.

Features:
- Check remaining premium requests
- Calculate burn rate based on usage history
- Determine if aggressive or conservative scheduling should be used
- Provide recommendations for workflow frequency
"""

import json
import os
import sys
import time
from datetime import datetime, timezone, timedelta
from typing import Dict, Optional, Any, Tuple
from dataclasses import dataclass
from github_integration import GitHubAPIClient


@dataclass
class UsageStats:
    """Statistics about API usage"""
    total_quota: int
    remaining: int
    used: int
    reset_date: datetime
    days_until_reset: float
    current_burn_rate: float  # requests per day
    projected_usage: int
    is_safe: bool
    recommended_mode: str  # 'aggressive', 'normal', 'conservative'
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'total_quota': self.total_quota,
            'remaining': self.remaining,
            'used': self.used,
            'reset_date': self.reset_date.isoformat(),
            'days_until_reset': round(self.days_until_reset, 2),
            'current_burn_rate': round(self.current_burn_rate, 2),
            'projected_usage': self.projected_usage,
            'is_safe': self.is_safe,
            'recommended_mode': self.recommended_mode
        }


class CopilotUsageTracker:
    """Track GitHub Copilot usage and provide scheduling recommendations"""
    
    def __init__(self, token: Optional[str] = None, history_file: str = 'tools/analysis/copilot_usage_history.json'):
        """
        Initialize the usage tracker.
        
        Args:
            token: GitHub token (defaults to COPILOT_PAT or GITHUB_TOKEN env var)
            history_file: Path to store usage history
        """
        self.token = token or os.environ.get('COPILOT_PAT') or os.environ.get('GITHUB_TOKEN') or os.environ.get('GH_TOKEN')
        self.history_file = history_file
        self.client = GitHubAPIClient(token=self.token)
        
        # Create analysis directory if it doesn't exist
        os.makedirs(os.path.dirname(history_file), exist_ok=True)
    
    def get_rate_limit_info(self) -> Dict[str, Any]:
        """
        Get current rate limit information from GitHub API.
        
        Returns:
            Rate limit information including remaining requests
        """
        try:
            rate_limit = self.client.get("/rate_limit")
            return rate_limit
        except Exception as e:
            print(f"Error fetching rate limit: {e}", file=sys.stderr)
            return None
    
    def get_copilot_usage_from_api(self, org: str) -> Optional[Dict[str, Any]]:
        """
        Get Copilot usage information from GitHub API.
        
        Args:
            org: Organization name
            
        Returns:
            Dictionary with usage information or None if unavailable
        """
        try:
            # Try to get Copilot metrics from the API
            metrics = self.client.get(f"/orgs/{org}/copilot/metrics")
            
            # Extract premium requests data from the last available day
            if not metrics or not isinstance(metrics, list) or len(metrics) == 0:
                print(f"No Copilot metrics data available from API", file=sys.stderr)
                return None
            
            # Get the most recent day's data
            latest = metrics[0] if isinstance(metrics, list) else metrics
            
            # Extract premium requests information
            result = {
                'date': latest.get('date'),
                'total_premium_requests': 0,
                'has_data': False
            }
            
            # Sum up premium requests across all breakdowns
            for breakdown in latest.get('breakdown', []):
                premium_requests = breakdown.get('premium_requests_count', 0)
                result['total_premium_requests'] += premium_requests
                if premium_requests > 0:
                    result['has_data'] = True
            
            return result if result['has_data'] else None
            
        except Exception as e:
            print(f"Error fetching Copilot metrics from API: {e}", file=sys.stderr)
            return None
    
    def _aggregate_monthly_usage(self, org: str, reset_day: int) -> int:
        """
        Aggregate premium requests from the current billing period.
        
        Args:
            org: Organization name
            reset_day: Day of month when quota resets
            
        Returns:
            Total premium requests used in current billing period
        """
        try:
            # Get metrics from GitHub API
            metrics = self.client.get(f"/orgs/{org}/copilot/metrics")
            
            if not metrics or not isinstance(metrics, list):
                print(f"No metrics data available from API", file=sys.stderr)
                return 0
            
            # Calculate billing period start date
            now = datetime.now(timezone.utc)
            if now.day >= reset_day:
                # Current billing period started on reset_day of current month
                period_start = datetime(now.year, now.month, reset_day, tzinfo=timezone.utc)
            else:
                # Current billing period started on reset_day of last month
                if now.month == 1:
                    period_start = datetime(now.year - 1, 12, reset_day, tzinfo=timezone.utc)
                else:
                    period_start = datetime(now.year, now.month - 1, reset_day, tzinfo=timezone.utc)
            
            # Aggregate premium requests from the billing period
            total_premium_requests = 0
            for day_data in metrics:
                # Parse the date from the metric
                metric_date_str = day_data.get('date')
                if not metric_date_str:
                    continue
                
                try:
                    metric_date = datetime.fromisoformat(metric_date_str.replace('Z', '+00:00'))
                except (ValueError, AttributeError, TypeError) as e:
                    # Skip invalid date formats
                    continue
                
                # Only count metrics from current billing period
                if metric_date >= period_start:
                    # Sum premium requests across all breakdowns for this day
                    for breakdown in day_data.get('breakdown', []):
                        total_premium_requests += breakdown.get('premium_requests_count', 0)
            
            return total_premium_requests
            
        except Exception as e:
            print(f"Error aggregating monthly usage: {e}", file=sys.stderr)
            return 0
    
    def estimate_copilot_usage(self, org: Optional[str] = None) -> UsageStats:
        """
        Estimate Copilot usage based on available information.
        
        Fetches actual usage from GitHub Copilot API if available, otherwise
        falls back to estimates based on:
        1. User-provided quota info (1500 for Pro+)
        2. Historical usage tracking
        3. Workflow execution counts
        
        Args:
            org: Organization name (defaults to GITHUB_REPOSITORY owner)
        
        Returns:
            UsageStats with current usage estimates
        """
        # Default quota for Pro+ (user mentioned 1500)
        total_quota = int(os.environ.get('COPILOT_MONTHLY_QUOTA', '1500'))
        
        # Reset date (user mentioned Dec 1st)
        reset_day = int(os.environ.get('COPILOT_RESET_DAY', '1'))
        now = datetime.now(timezone.utc)
        
        # Calculate next reset date
        if now.day >= reset_day:
            # Next month
            if now.month == 12:
                reset_date = datetime(now.year + 1, 1, reset_day, tzinfo=timezone.utc)
            else:
                reset_date = datetime(now.year, now.month + 1, reset_day, tzinfo=timezone.utc)
        else:
            # This month
            reset_date = datetime(now.year, now.month, reset_day, tzinfo=timezone.utc)
        
        days_until_reset = (reset_date - now).total_seconds() / 86400
        
        # Determine organization
        if not org:
            # Try to get from GITHUB_REPOSITORY env var (format: owner/repo)
            github_repo = os.environ.get('GITHUB_REPOSITORY', '')
            if '/' in github_repo:
                org = github_repo.split('/')[0]
        
        # Load usage history
        history = self._load_history()
        
        # Try to get actual usage from API
        api_data = None
        if org:
            api_data = self.get_copilot_usage_from_api(org)
        
        # Calculate used requests
        # Priority: API data > environment variable > history > default
        if api_data and api_data.get('has_data'):
            # Use API data - sum all premium requests from metrics
            # Note: The API returns daily data, we need to aggregate for the billing period
            used = self._aggregate_monthly_usage(org, reset_day)
            print(f"Using actual Copilot usage from API: {used} requests", file=sys.stderr)
        else:
            env_used = os.environ.get('COPILOT_REQUESTS_USED')
            if env_used:
                # Environment variable set - use it (allows manual updates)
                used = int(env_used)
                print(f"Using usage from environment variable: {used} requests", file=sys.stderr)
            else:
                # Use history if available, otherwise default
                used = history.get('current_used', 300)
                print(f"Using usage from history: {used} requests", file=sys.stderr)
        
        remaining = total_quota - used
        
        # Calculate burn rate (requests per day)
        # Calculate days elapsed in current billing cycle
        days_elapsed = max(0.1, 30 - days_until_reset)  # Assuming ~30 day month, min 0.1 to avoid division by zero
        current_burn_rate = used / days_elapsed
        
        # Project usage until reset
        projected_usage = used + (current_burn_rate * days_until_reset)
        
        # Determine if current usage is safe
        # Safe if projected usage is < 90% of quota
        is_safe = projected_usage < (total_quota * 0.9)
        
        # Determine recommended mode based on usage vs time elapsed
        usage_percentage = (used / total_quota) * 100
        time_percentage = (days_elapsed / 30) * 100
        
        # Calculate usage efficiency (should be ~1.0 if on track)
        # Higher than 1.0 means using too fast, lower means under-utilizing
        usage_efficiency = usage_percentage / time_percentage if time_percentage > 0 else 0
        
        # Determine mode based on efficiency and safety
        if usage_efficiency < 0.7:
            # Using less than 70% of expected - be aggressive
            recommended_mode = 'aggressive'
        elif usage_efficiency < 1.3:
            # Between 70-130% of expected - normal
            recommended_mode = 'normal'
        else:
            # Using more than 130% of expected - be conservative
            recommended_mode = 'conservative'
        
        # Override to conservative if projected to exceed quota
        if not is_safe:
            recommended_mode = 'conservative'
        
        stats = UsageStats(
            total_quota=total_quota,
            remaining=remaining,
            used=used,
            reset_date=reset_date,
            days_until_reset=days_until_reset,
            current_burn_rate=current_burn_rate,
            projected_usage=int(projected_usage),
            is_safe=is_safe,
            recommended_mode=recommended_mode
        )
        
        # Update history
        self._save_history(stats)
        
        return stats
    
    def _load_history(self) -> Dict[str, Any]:
        """Load usage history from file"""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError, OSError) as e:
                # Return empty dict if file is corrupted or unreadable
                pass
        return {}
    
    def _save_history(self, stats: UsageStats):
        """Save usage history to file"""
        history = self._load_history()
        
        # Update current stats
        history['current_used'] = stats.used
        history['last_check'] = datetime.now(timezone.utc).isoformat()
        
        # Add to timeline
        if 'timeline' not in history:
            history['timeline'] = []
        
        history['timeline'].append({
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'used': stats.used,
            'remaining': stats.remaining,
            'burn_rate': round(stats.current_burn_rate, 2),
            'mode': stats.recommended_mode
        })
        
        # Keep only last 100 entries
        history['timeline'] = history['timeline'][-100:]
        
        with open(self.history_file, 'w') as f:
            json.dump(history, f, indent=2)
    
    def get_workflow_frequencies(self, mode: Optional[str] = None) -> Dict[str, str]:
        """
        Get recommended workflow frequencies based on mode.
        
        Args:
            mode: 'aggressive', 'normal', or 'conservative'. If None, auto-determined.
        
        Returns:
            Dictionary of workflow name to cron schedule
        """
        if mode is None:
            stats = self.estimate_copilot_usage()
            mode = stats.recommended_mode
        
        frequencies = {
            'aggressive': {
                'learn-tldr': '0 */3 * * *',      # Every 3 hours
                'learn-hn': '0 */2 * * *',        # Every 2 hours
                'idea-generator': '0 */4 * * *',  # Every 4 hours
                'ai-idea-spawner': '0 */3 * * *', # Every 3 hours (AI focused!)
                'ai-friend': '0 */6 * * *',       # Every 6 hours
                'agent-spawner': '0 */2 * * *',   # Every 2 hours
            },
            'normal': {
                'learn-tldr': '0 8,20 * * *',     # 2x daily
                'learn-hn': '0 7,13,19 * * *',    # 3x daily
                'idea-generator': '0 10 * * *',   # Daily at 10 AM
                'ai-idea-spawner': '0 */4 * * *', # Every 4 hours
                'ai-friend': '0 14 * * *',        # Daily at 2 PM
                'agent-spawner': '0 */3 * * *',   # Every 3 hours
            },
            'conservative': {
                'learn-tldr': '0 12 * * *',       # Once daily at noon
                'learn-hn': '0 8,20 * * *',       # 2x daily
                'idea-generator': '0 10 * * 1,4', # Twice weekly
                'ai-idea-spawner': '0 10 * * *',  # Once daily
                'ai-friend': '0 14 * * 0',        # Weekly on Sunday
                'agent-spawner': '0 */6 * * *',   # Every 6 hours
            }
        }
        
        return frequencies.get(mode, frequencies['normal'])
    
    def print_status(self):
        """Print current usage status in a formatted way"""
        print("\n" + "="*70)
        print("🤖 GitHub Copilot Usage Tracker")
        print("="*70 + "\n")
        
        stats = self.estimate_copilot_usage()
        
        # Usage bar
        usage_percent = (stats.used / stats.total_quota) * 100
        bar_width = 50
        filled = int((usage_percent / 100) * bar_width)
        bar = "█" * filled + "░" * (bar_width - filled)
        
        print(f"📊 Usage: [{bar}] {usage_percent:.1f}%\n")
        
        print(f"Total Quota:       {stats.total_quota:,} requests")
        print(f"Used:              {stats.used:,} requests")
        print(f"Remaining:         {stats.remaining:,} requests")
        print(f"\n📅 Reset Date:      {stats.reset_date.strftime('%Y-%m-%d')}")
        print(f"Days Until Reset:  {stats.days_until_reset:.1f} days")
        print(f"\n🔥 Burn Rate:       {stats.current_burn_rate:.1f} requests/day")
        print(f"Projected Usage:   {stats.projected_usage:,} requests")
        
        # Status indicator
        if stats.is_safe:
            status_icon = "✅"
            status_text = "SAFE - On track or under budget"
        else:
            status_icon = "⚠️"
            status_text = "WARNING - May exceed quota"
        
        print(f"\n{status_icon} Status: {status_text}")
        
        # Mode recommendation
        mode_icons = {
            'aggressive': '🚀',
            'normal': '🎯',
            'conservative': '🛡️'
        }
        mode_icon = mode_icons.get(stats.recommended_mode, '🎯')
        
        print(f"\n{mode_icon} Recommended Mode: {stats.recommended_mode.upper()}")
        
        # Workflow frequencies
        print(f"\n📋 Recommended Workflow Frequencies:")
        frequencies = self.get_workflow_frequencies(stats.recommended_mode)
        for workflow, cron in frequencies.items():
            print(f"  • {workflow}: {cron}")
        
        print("\n" + "="*70 + "\n")
        
        return stats


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Track GitHub Copilot usage and provide scheduling recommendations'
    )
    parser.add_argument(
        '--token',
        help='GitHub token (or use COPILOT_PAT/GITHUB_TOKEN env var)'
    )
    parser.add_argument(
        '--org',
        help='Organization name (or use GITHUB_REPOSITORY env var)'
    )
    parser.add_argument(
        '--quota',
        type=int,
        help='Total monthly quota (default: 1500 for Pro+)'
    )
    parser.add_argument(
        '--used',
        type=int,
        help='Requests used so far (for manual tracking)'
    )
    parser.add_argument(
        '--reset-day',
        type=int,
        help='Day of month when quota resets (default: 1)'
    )
    parser.add_argument(
        '--mode',
        choices=['aggressive', 'normal', 'conservative'],
        help='Force a specific scheduling mode'
    )
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output results as JSON'
    )
    
    args = parser.parse_args()
    
    # Set environment variables if provided
    if args.quota:
        os.environ['COPILOT_MONTHLY_QUOTA'] = str(args.quota)
    if args.used:
        os.environ['COPILOT_REQUESTS_USED'] = str(args.used)
    if args.reset_day:
        os.environ['COPILOT_RESET_DAY'] = str(args.reset_day)
    
    # Create tracker
    tracker = CopilotUsageTracker(token=args.token)
    
    if args.json:
        # JSON output
        stats = tracker.estimate_copilot_usage(org=args.org)
        mode = args.mode or stats.recommended_mode
        frequencies = tracker.get_workflow_frequencies(mode)
        
        output = {
            'stats': stats.to_dict(),
            'frequencies': frequencies
        }
        print(json.dumps(output, indent=2))
    else:
        # Human-readable output
        stats = tracker.print_status()
        
        if args.mode:
            print(f"Note: Using forced mode '{args.mode}' instead of recommended '{stats.recommended_mode}'")


if __name__ == '__main__':
    main()
