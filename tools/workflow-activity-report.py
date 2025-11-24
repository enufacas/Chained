#!/usr/bin/env python3
"""
Workflow Activity Report Generator
Created by @create-guru

Generates a comprehensive workflow activity report to help evaluate
candidate workflows for archival. Analyzes workflows based on:
- Last run date and time since last run
- Total number of runs
- Run frequency (daily/weekly average)
- Success/failure rate
- Workflow state (active/disabled)
- Trigger types (schedule, manual, push, etc.)

Usage:
    python3 tools/workflow-activity-report.py [options]

Options:
    --owner OWNER       Repository owner (default: from git remote)
    --repo REPO         Repository name (default: from git remote)
    --json              Output as JSON only
    --min-days N        Minimum days inactive to flag (default: 30)
    --format FORMAT     Output format: text, json, markdown, or both (default: text)
    --top N             Show top N workflows per category (default: 20)
    --output FILE       Output file path
    --token TOKEN       GitHub token (default: from COPILOT_PAT or GITHUB_TOKEN env)
"""

import argparse
import json
import os
import subprocess
import sys
import urllib.request
import urllib.error
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict


@dataclass
class WorkflowActivity:
    """Activity metrics for a single workflow."""
    workflow_id: int
    name: str
    path: str
    state: str  # active, disabled, deleted
    created_at: str
    updated_at: str
    total_runs: int
    last_run_date: Optional[str]
    days_since_last_run: Optional[int]
    success_count: int
    failure_count: int
    skipped_count: int
    cancelled_count: int
    success_rate: float
    trigger_types: List[str]
    avg_runs_per_day: float
    avg_runs_per_week: float
    archival_score: float  # Higher = more likely candidate for archival
    archival_reasons: List[str]


class WorkflowActivityReporter:
    """
    Generates workflow activity reports for archival decisions.
    
    This tool analyzes GitHub Actions workflows to identify candidates
    for archival based on activity patterns, success rates, and usage.
    """
    
    def __init__(self, owner: str, repo: str, min_inactive_days: int = 30, token: str = None):
        """
        Initialize the reporter.
        
        Args:
            owner: Repository owner
            repo: Repository name
            min_inactive_days: Minimum days of inactivity to flag
            token: GitHub token (defaults to COPILOT_PAT or GITHUB_TOKEN env var)
        """
        self.owner = owner
        self.repo = repo
        self.min_inactive_days = min_inactive_days
        self.workflows: List[WorkflowActivity] = []
        # Priority: passed token > COPILOT_PAT > GITHUB_TOKEN > GH_TOKEN
        self.token = token or os.environ.get('COPILOT_PAT') or os.environ.get('GITHUB_TOKEN') or os.environ.get('GH_TOKEN')
        
        if not self.token:
            print("Warning: No GitHub token found. API calls may fail or be rate-limited.", file=sys.stderr)
    
    def _github_api_get(self, endpoint: str) -> Tuple[bool, any]:
        """
        Make a GET request to the GitHub API.
        
        Args:
            endpoint: API endpoint (e.g., /repos/owner/repo/actions/workflows)
            
        Returns:
            Tuple of (success, data or error message)
        """
        url = f"https://api.github.com{endpoint}"
        
        headers = {
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'workflow-activity-report'
        }
        
        if self.token:
            headers['Authorization'] = f'token {self.token}'
        
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=60) as response:
                data = json.loads(response.read().decode('utf-8'))
                return True, data
        except urllib.error.HTTPError as e:
            if e.code == 403:
                return False, "API rate limit or authentication issue. Check COPILOT_PAT or GITHUB_TOKEN."
            elif e.code == 404:
                return False, f"Resource not found: {endpoint}"
            else:
                return False, f"HTTP error {e.code}: {e.reason}"
        except urllib.error.URLError as e:
            return False, f"URL error: {e.reason}"
        except json.JSONDecodeError as e:
            return False, f"JSON decode error: {e}"
        except Exception as e:
            return False, f"Error: {e}"
    
    def fetch_workflows(self) -> bool:
        """Fetch all workflows from the repository with pagination."""
        all_workflows = []
        page = 1
        per_page = 100  # Maximum allowed by GitHub API
        
        while True:
            success, data = self._github_api_get(
                f'/repos/{self.owner}/{self.repo}/actions/workflows?page={page}&per_page={per_page}'
            )
            
            if not success:
                print(f"Error fetching workflows: {data}", file=sys.stderr)
                return False
            
            workflows_page = data.get('workflows', [])
            all_workflows.extend(workflows_page)
            
            total_count = data.get('total_count', 0)
            print(f"  Page {page}: fetched {len(workflows_page)} workflows (total: {len(all_workflows)}/{total_count})", file=sys.stderr)
            
            # Check if we've fetched all workflows
            if len(all_workflows) >= total_count or len(workflows_page) == 0:
                break
            
            page += 1
        
        print(f"Found {len(all_workflows)} workflows", file=sys.stderr)
        
        # Process each workflow
        for wf_data in all_workflows:
            activity = self._analyze_workflow(wf_data)
            if activity:
                self.workflows.append(activity)
        
        # Sort by archival score (highest first)
        self.workflows.sort(key=lambda x: x.archival_score, reverse=True)
        
        return True
    
    def _analyze_workflow(self, wf_data: Dict) -> Optional[WorkflowActivity]:
        """Analyze a single workflow and compute activity metrics."""
        workflow_id = wf_data.get('id')
        name = wf_data.get('name', 'Unknown')
        path = wf_data.get('path', '')
        state = wf_data.get('state', 'unknown')
        created_at = wf_data.get('created_at', '')
        updated_at = wf_data.get('updated_at', '')
        
        print(f"  Analyzing: {name}", file=sys.stderr)
        
        # Fetch workflow runs (most recent)
        success, runs_data = self._github_api_get(
            f'/repos/{self.owner}/{self.repo}/actions/workflows/{workflow_id}/runs?per_page=100'
        )
        
        runs = []
        total_runs = 0
        if success:
            runs = runs_data.get('workflow_runs', [])[:100]
            total_runs = runs_data.get('total_count', len(runs))
        
        # Calculate metrics from runs
        last_run_date = None
        days_since_last_run = None
        success_count = 0
        failure_count = 0
        skipped_count = 0
        cancelled_count = 0
        trigger_types = set()
        
        now = datetime.now(timezone.utc)
        
        for run in runs:
            conclusion = run.get('conclusion', '')
            event = run.get('event', '')
            created = run.get('created_at', '')
            
            trigger_types.add(event)
            
            if conclusion == 'success':
                success_count += 1
            elif conclusion == 'failure':
                failure_count += 1
            elif conclusion == 'skipped':
                skipped_count += 1
            elif conclusion == 'cancelled':
                cancelled_count += 1
            
            if last_run_date is None and created:
                last_run_date = created
        
        # Calculate days since last run
        if last_run_date:
            try:
                last_dt = datetime.fromisoformat(last_run_date.replace('Z', '+00:00'))
                days_since_last_run = (now - last_dt).days
            except (ValueError, TypeError):
                days_since_last_run = None
        
        # Calculate success rate
        completed_runs = success_count + failure_count
        success_rate = (success_count / completed_runs * 100) if completed_runs > 0 else 0.0
        
        # Calculate run frequency
        if total_runs > 0 and created_at:
            try:
                created_dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                days_active = (now - created_dt).days
                if days_active > 0:
                    avg_runs_per_day = total_runs / days_active
                    avg_runs_per_week = total_runs / (days_active / 7) if days_active >= 7 else total_runs
                else:
                    avg_runs_per_day = total_runs
                    avg_runs_per_week = total_runs
            except (ValueError, TypeError):
                avg_runs_per_day = 0.0
                avg_runs_per_week = 0.0
        else:
            avg_runs_per_day = 0.0
            avg_runs_per_week = 0.0
        
        # Calculate archival score and reasons
        archival_score, archival_reasons = self._calculate_archival_score(
            state=state,
            total_runs=total_runs,
            days_since_last_run=days_since_last_run,
            success_rate=success_rate,
            trigger_types=list(trigger_types),
            avg_runs_per_week=avg_runs_per_week
        )
        
        return WorkflowActivity(
            workflow_id=workflow_id,
            name=name,
            path=path,
            state=state,
            created_at=created_at,
            updated_at=updated_at,
            total_runs=total_runs,
            last_run_date=last_run_date,
            days_since_last_run=days_since_last_run,
            success_count=success_count,
            failure_count=failure_count,
            skipped_count=skipped_count,
            cancelled_count=cancelled_count,
            success_rate=round(success_rate, 1),
            trigger_types=sorted(trigger_types),
            avg_runs_per_day=round(avg_runs_per_day, 2),
            avg_runs_per_week=round(avg_runs_per_week, 2),
            archival_score=round(archival_score, 1),
            archival_reasons=archival_reasons
        )
    
    def _calculate_archival_score(
        self,
        state: str,
        total_runs: int,
        days_since_last_run: Optional[int],
        success_rate: float,
        trigger_types: List[str],
        avg_runs_per_week: float
    ) -> Tuple[float, List[str]]:
        """
        Calculate archival score and reasons.
        
        Higher score = more likely candidate for archival.
        Score ranges from 0 to 100.
        """
        score = 0.0
        reasons = []
        
        # Already disabled workflows
        if state == 'disabled':
            score += 30
            reasons.append("Workflow is disabled")
        
        # Inactivity (major factor)
        if days_since_last_run is not None:
            if days_since_last_run >= 90:
                score += 35
                reasons.append(f"No runs in {days_since_last_run} days (90+ days)")
            elif days_since_last_run >= 60:
                score += 25
                reasons.append(f"No runs in {days_since_last_run} days (60+ days)")
            elif days_since_last_run >= self.min_inactive_days:
                score += 15
                reasons.append(f"No runs in {days_since_last_run} days ({self.min_inactive_days}+ days)")
        elif total_runs == 0:
            score += 40
            reasons.append("Never been run")
        
        # Low usage
        if total_runs == 0:
            score += 20
            reasons.append("Zero total runs")
        elif total_runs <= 5:
            score += 10
            reasons.append(f"Very low usage ({total_runs} total runs)")
        elif total_runs <= 20:
            score += 5
            reasons.append(f"Low usage ({total_runs} total runs)")
        
        # Low frequency (if runs exist)
        if total_runs > 0 and avg_runs_per_week < 0.1:
            score += 10
            reasons.append("Runs less than once per 10 weeks")
        
        # High failure rate (might indicate abandoned/broken workflow)
        if total_runs >= 5 and success_rate < 20:
            score += 15
            reasons.append(f"Very low success rate ({success_rate:.0f}%)")
        elif total_runs >= 5 and success_rate < 50:
            score += 5
            reasons.append(f"Low success rate ({success_rate:.0f}%)")
        
        # Manual-only with no recent runs
        if trigger_types == ['workflow_dispatch'] and days_since_last_run and days_since_last_run > 60:
            score += 10
            reasons.append("Manual-only workflow with no recent use")
        
        # Cap score at 100
        score = min(score, 100)
        
        return score, reasons
    
    def generate_text_report(self, top_n: int = 20) -> str:
        """Generate human-readable text report."""
        lines = []
        
        # Header
        lines.append("=" * 80)
        lines.append("📊 WORKFLOW ACTIVITY REPORT FOR ARCHIVAL DECISIONS")
        lines.append(f"   Repository: {self.owner}/{self.repo}")
        lines.append(f"   Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}")
        lines.append(f"   Created by: @create-guru")
        lines.append("=" * 80)
        lines.append("")
        
        # Summary statistics
        total = len(self.workflows)
        active = sum(1 for w in self.workflows if w.state == 'active')
        disabled = sum(1 for w in self.workflows if w.state == 'disabled')
        never_run = sum(1 for w in self.workflows if w.total_runs == 0)
        inactive_30d = sum(1 for w in self.workflows 
                          if w.days_since_last_run and w.days_since_last_run >= 30)
        inactive_60d = sum(1 for w in self.workflows 
                          if w.days_since_last_run and w.days_since_last_run >= 60)
        high_archival = sum(1 for w in self.workflows if w.archival_score >= 50)
        
        lines.append("📈 SUMMARY STATISTICS")
        lines.append("-" * 40)
        lines.append(f"  Total Workflows:        {total}")
        lines.append(f"  Active:                 {active}")
        lines.append(f"  Disabled:               {disabled}")
        lines.append(f"  Never Run:              {never_run}")
        lines.append(f"  Inactive 30+ days:      {inactive_30d}")
        lines.append(f"  Inactive 60+ days:      {inactive_60d}")
        lines.append(f"  High Archival Score:    {high_archival} (score >= 50)")
        lines.append("")
        
        # Top archival candidates
        lines.append("🗃️  TOP ARCHIVAL CANDIDATES")
        lines.append("-" * 80)
        lines.append(f"{'#':<3} {'Score':<6} {'Name':<35} {'Last Run':<12} {'Runs':<6} {'Rate'}")
        lines.append("-" * 80)
        
        for i, wf in enumerate(self.workflows[:top_n], 1):
            last_run = f"{wf.days_since_last_run}d ago" if wf.days_since_last_run else "Never"
            rate = f"{wf.success_rate:.0f}%" if wf.total_runs > 0 else "N/A"
            name = wf.name[:33] + ".." if len(wf.name) > 35 else wf.name
            lines.append(f"{i:<3} {wf.archival_score:>5.0f}  {name:<35} {last_run:<12} {wf.total_runs:<6} {rate}")
            
            # Show reasons for top candidates
            if i <= 5 and wf.archival_reasons:
                for reason in wf.archival_reasons[:3]:
                    lines.append(f"        └─ {reason}")
        
        lines.append("")
        
        # Recently active workflows (for comparison)
        recent = [w for w in self.workflows if w.days_since_last_run is not None 
                  and w.days_since_last_run < 7 and w.archival_score < 20]
        recent.sort(key=lambda x: x.days_since_last_run or 0)
        
        if recent:
            lines.append("✅ RECENTLY ACTIVE WORKFLOWS (Low Archival Risk)")
            lines.append("-" * 80)
            lines.append(f"{'Name':<40} {'Last Run':<12} {'Runs':<8} {'Rate':<8} {'Avg/Week'}")
            lines.append("-" * 80)
            
            for wf in recent[:10]:
                last_run = f"{wf.days_since_last_run}d ago" if wf.days_since_last_run else "Never"
                rate = f"{wf.success_rate:.0f}%"
                name = wf.name[:38] + ".." if len(wf.name) > 40 else wf.name
                lines.append(f"{name:<40} {last_run:<12} {wf.total_runs:<8} {rate:<8} {wf.avg_runs_per_week:.1f}")
            
            lines.append("")
        
        # Trigger type distribution
        trigger_counts = {}
        for wf in self.workflows:
            for trigger in wf.trigger_types:
                trigger_counts[trigger] = trigger_counts.get(trigger, 0) + 1
        
        lines.append("🔄 TRIGGER TYPE DISTRIBUTION")
        lines.append("-" * 40)
        for trigger, count in sorted(trigger_counts.items(), key=lambda x: -x[1]):
            lines.append(f"  {trigger:<20} {count:>4} workflows")
        lines.append("")
        
        # Footer
        lines.append("=" * 80)
        lines.append("💡 ARCHIVAL RECOMMENDATIONS")
        lines.append("-" * 80)
        lines.append("• Score >= 70: Strong archival candidate - review and likely archive")
        lines.append("• Score 50-69: Moderate candidate - investigate before archiving")
        lines.append("• Score 30-49: Low priority - may need optimization, not archival")
        lines.append("• Score < 30:  Active/healthy - no action needed")
        lines.append("")
        lines.append("Before archiving, verify:")
        lines.append("  1. No active dependencies from other workflows")
        lines.append("  2. Not a manual-only workflow that's still useful")
        lines.append("  3. Check if workflow was recently created (may not have runs yet)")
        lines.append("=" * 80)
        
        return "\n".join(lines)
    
    def generate_json_report(self) -> Dict:
        """Generate JSON report for programmatic use."""
        return {
            'metadata': {
                'owner': self.owner,
                'repo': self.repo,
                'generated_at': datetime.now(timezone.utc).isoformat(),
                'min_inactive_days': self.min_inactive_days,
                'created_by': '@create-guru'
            },
            'summary': {
                'total_workflows': len(self.workflows),
                'active_workflows': sum(1 for w in self.workflows if w.state == 'active'),
                'disabled_workflows': sum(1 for w in self.workflows if w.state == 'disabled'),
                'never_run': sum(1 for w in self.workflows if w.total_runs == 0),
                'inactive_30d': sum(1 for w in self.workflows 
                                   if w.days_since_last_run and w.days_since_last_run >= 30),
                'inactive_60d': sum(1 for w in self.workflows 
                                   if w.days_since_last_run and w.days_since_last_run >= 60),
                'high_archival_candidates': sum(1 for w in self.workflows if w.archival_score >= 50),
            },
            'workflows': [asdict(w) for w in self.workflows],
            'archival_candidates': {
                'high': [asdict(w) for w in self.workflows if w.archival_score >= 70],
                'medium': [asdict(w) for w in self.workflows if 50 <= w.archival_score < 70],
                'low': [asdict(w) for w in self.workflows if 30 <= w.archival_score < 50],
            }
        }
    
    def generate_markdown_report(self, top_n: int = 20) -> str:
        """Generate markdown report for documentation."""
        lines = []
        
        # Header
        lines.append("# 📊 Workflow Activity Report for Archival Decisions")
        lines.append("")
        lines.append(f"**Repository:** `{self.owner}/{self.repo}`")
        lines.append(f"**Generated:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}")
        lines.append(f"**Created by:** @create-guru")
        lines.append("")
        
        # Summary statistics
        total = len(self.workflows)
        active = sum(1 for w in self.workflows if w.state == 'active')
        disabled = sum(1 for w in self.workflows if w.state == 'disabled')
        never_run = sum(1 for w in self.workflows if w.total_runs == 0)
        inactive_30d = sum(1 for w in self.workflows 
                          if w.days_since_last_run and w.days_since_last_run >= 30)
        inactive_60d = sum(1 for w in self.workflows 
                          if w.days_since_last_run and w.days_since_last_run >= 60)
        high_archival = sum(1 for w in self.workflows if w.archival_score >= 50)
        
        lines.append("## 📈 Summary Statistics")
        lines.append("")
        lines.append("| Metric | Value |")
        lines.append("|--------|-------|")
        lines.append(f"| Total Workflows | {total} |")
        lines.append(f"| Active | {active} |")
        lines.append(f"| Disabled | {disabled} |")
        lines.append(f"| Never Run | {never_run} |")
        lines.append(f"| Inactive 30+ days | {inactive_30d} |")
        lines.append(f"| Inactive 60+ days | {inactive_60d} |")
        lines.append(f"| High Archival Score (≥50) | {high_archival} |")
        lines.append("")
        
        # Archival candidates table
        lines.append("## 🗃️ Top Archival Candidates")
        lines.append("")
        lines.append("Workflows sorted by archival score (higher = stronger candidate for archival):")
        lines.append("")
        lines.append("| # | Score | Workflow Name | Last Run | Total Runs | Success Rate | State |")
        lines.append("|---|-------|---------------|----------|------------|--------------|-------|")
        
        for i, wf in enumerate(self.workflows[:top_n], 1):
            last_run = f"{wf.days_since_last_run}d ago" if wf.days_since_last_run else "Never"
            rate = f"{wf.success_rate:.0f}%" if wf.total_runs > 0 else "N/A"
            name = wf.name[:40] + "…" if len(wf.name) > 40 else wf.name
            state_emoji = "🔴" if wf.state == 'disabled' else "🟢"
            lines.append(f"| {i} | {wf.archival_score:.0f} | {name} | {last_run} | {wf.total_runs} | {rate} | {state_emoji} {wf.state} |")
        
        lines.append("")
        
        # Top 5 detailed reasons
        lines.append("### Top 5 Archival Candidates - Detailed Reasons")
        lines.append("")
        
        for i, wf in enumerate(self.workflows[:5], 1):
            lines.append(f"#### {i}. {wf.name}")
            lines.append(f"- **Score:** {wf.archival_score:.0f}")
            lines.append(f"- **Path:** `{wf.path}`")
            lines.append(f"- **State:** {wf.state}")
            lines.append(f"- **Total Runs:** {wf.total_runs}")
            if wf.days_since_last_run:
                lines.append(f"- **Days Since Last Run:** {wf.days_since_last_run}")
            if wf.archival_reasons:
                lines.append("- **Reasons:**")
                for reason in wf.archival_reasons:
                    lines.append(f"  - {reason}")
            lines.append("")
        
        # Recently active workflows
        recent = [w for w in self.workflows if w.days_since_last_run is not None 
                  and w.days_since_last_run < 7 and w.archival_score < 20]
        recent.sort(key=lambda x: x.days_since_last_run or 0)
        
        if recent:
            lines.append("## ✅ Recently Active Workflows (Low Archival Risk)")
            lines.append("")
            lines.append("| Workflow Name | Last Run | Total Runs | Success Rate | Avg/Week |")
            lines.append("|---------------|----------|------------|--------------|----------|")
            
            for wf in recent[:10]:
                last_run = f"{wf.days_since_last_run}d ago" if wf.days_since_last_run else "Never"
                rate = f"{wf.success_rate:.0f}%"
                name = wf.name[:40] + "…" if len(wf.name) > 40 else wf.name
                lines.append(f"| {name} | {last_run} | {wf.total_runs} | {rate} | {wf.avg_runs_per_week:.1f} |")
            
            lines.append("")
        
        # Trigger type distribution
        trigger_counts = {}
        for wf in self.workflows:
            for trigger in wf.trigger_types:
                trigger_counts[trigger] = trigger_counts.get(trigger, 0) + 1
        
        lines.append("## 🔄 Trigger Type Distribution")
        lines.append("")
        lines.append("| Trigger Type | Workflow Count |")
        lines.append("|--------------|----------------|")
        for trigger, count in sorted(trigger_counts.items(), key=lambda x: -x[1]):
            lines.append(f"| `{trigger}` | {count} |")
        lines.append("")
        
        # Recommendations
        lines.append("## 💡 Archival Recommendations")
        lines.append("")
        lines.append("| Score Range | Recommendation |")
        lines.append("|-------------|----------------|")
        lines.append("| ≥ 70 | **Strong archival candidate** - Review and likely archive |")
        lines.append("| 50-69 | **Moderate candidate** - Investigate before archiving |")
        lines.append("| 30-49 | **Low priority** - May need optimization, not archival |")
        lines.append("| < 30 | **Active/healthy** - No action needed |")
        lines.append("")
        lines.append("### Before Archiving, Verify:")
        lines.append("")
        lines.append("1. ✅ No active dependencies from other workflows")
        lines.append("2. ✅ Not a manual-only workflow that's still useful")
        lines.append("3. ✅ Workflow was not recently created (may not have runs yet)")
        lines.append("4. ✅ Confirm with team if workflow serves a purpose not reflected in runs")
        lines.append("")
        lines.append("---")
        lines.append("")
        lines.append("*Report generated by `tools/workflow-activity-report.py` - Created by @create-guru*")
        
        return "\n".join(lines)


def get_repo_info() -> Tuple[str, str]:
    """Get owner and repo from git remote."""
    try:
        result = subprocess.run(
            ['git', 'remote', 'get-url', 'origin'],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            url = result.stdout.strip()
            # Handle various URL formats
            if 'github.com' in url:
                # Extract owner/repo from URL
                parts = url.replace('.git', '').split('github.com')[-1]
                parts = parts.strip('/:').split('/')
                if len(parts) >= 2:
                    return parts[0], parts[1]
    except Exception:
        pass
    
    return '', ''


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Workflow Activity Report Generator by @create-guru'
    )
    parser.add_argument(
        '--owner',
        help='Repository owner'
    )
    parser.add_argument(
        '--repo',
        help='Repository name'
    )
    parser.add_argument(
        '--min-days',
        type=int,
        default=30,
        help='Minimum days inactive to flag (default: 30)'
    )
    parser.add_argument(
        '--format',
        choices=['text', 'json', 'markdown', 'both'],
        default='text',
        help='Output format (default: text)'
    )
    parser.add_argument(
        '--top',
        type=int,
        default=20,
        help='Show top N workflows per category (default: 20)'
    )
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output JSON only (shortcut for --format json)'
    )
    parser.add_argument(
        '--markdown',
        action='store_true',
        help='Output Markdown only (shortcut for --format markdown)'
    )
    parser.add_argument(
        '--output',
        help='Output file path'
    )
    parser.add_argument(
        '--token',
        help='GitHub token (or use COPILOT_PAT/GITHUB_TOKEN env var)'
    )
    
    args = parser.parse_args()
    
    # Handle format shortcuts
    if args.json:
        args.format = 'json'
    elif args.markdown:
        args.format = 'markdown'
    
    # Get owner/repo
    owner = args.owner
    repo = args.repo
    
    if not owner or not repo:
        default_owner, default_repo = get_repo_info()
        owner = owner or default_owner
        repo = repo or default_repo
    
    if not owner or not repo:
        print("Error: Could not determine repository. Use --owner and --repo", file=sys.stderr)
        sys.exit(1)
    
    # Generate report
    reporter = WorkflowActivityReporter(
        owner=owner,
        repo=repo,
        min_inactive_days=args.min_days,
        token=args.token
    )
    
    print(f"Fetching workflows for {owner}/{repo}...", file=sys.stderr)
    
    if not reporter.fetch_workflows():
        print("Error: Failed to fetch workflows", file=sys.stderr)
        sys.exit(1)
    
    print(f"Analyzed {len(reporter.workflows)} workflows\n", file=sys.stderr)
    
    # Generate output based on format
    output_content = ""
    
    if args.format == 'text':
        output_content = reporter.generate_text_report(top_n=args.top)
    elif args.format == 'json':
        json_report = reporter.generate_json_report()
        output_content = json.dumps(json_report, indent=2)
    elif args.format == 'markdown':
        output_content = reporter.generate_markdown_report(top_n=args.top)
    elif args.format == 'both':
        output_content = reporter.generate_text_report(top_n=args.top)
        output_content += "\n\n" + "=" * 80 + "\n"
        output_content += "JSON OUTPUT (for programmatic use)\n"
        output_content += "=" * 80 + "\n"
        output_content += json.dumps(reporter.generate_json_report(), indent=2)
    
    # Write to file or stdout
    if args.output:
        with open(args.output, 'w') as f:
            f.write(output_content)
        print(f"Report saved to: {args.output}", file=sys.stderr)
    else:
        print(output_content)


if __name__ == '__main__':
    main()
