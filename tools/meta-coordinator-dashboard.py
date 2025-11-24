#!/usr/bin/env python3
"""
Meta-Coordinator Metrics Dashboard

Displays current system health metrics and trends.

Usage:
    python3 tools/meta-coordinator-dashboard.py [--format text|json|markdown]

Output formats:
    text     - Human-readable text (default)
    json     - Machine-readable JSON
    markdown - Markdown for GitHub issues/PRs
"""

import sys
import json
import os
from datetime import datetime, timedelta
from typing import Dict, Any, List

# Add tools to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

try:
    from meta_coordinator_memory import MetaCoordinatorMemory
except ImportError:
    print("ERROR: Could not import meta_coordinator_memory", file=sys.stderr)
    print("Make sure you're running from repository root", file=sys.stderr)
    sys.exit(1)


def format_duration(hours: float) -> str:
    """Format duration in hours to human-readable string."""
    if hours == 0:
        return "0h"
    elif hours < 1:
        return f"{int(hours * 60)}m"
    elif hours < 24:
        return f"{hours:.1f}h"
    else:
        days = hours / 24
        return f"{days:.1f}d"


def calculate_trend(values: List[float], window: int = 5) -> str:
    """Calculate trend direction from recent values."""
    if len(values) < 2:
        return "→"  # Stable (not enough data)
    
    recent = values[-window:] if len(values) >= window else values
    
    if len(recent) < 2:
        return "→"
    
    # Simple linear trend
    first_half = sum(recent[:len(recent)//2]) / (len(recent)//2)
    second_half = sum(recent[len(recent)//2:]) / (len(recent) - len(recent)//2)
    
    if second_half > first_half * 1.1:
        return "↑"  # Increasing
    elif second_half < first_half * 0.9:
        return "↓"  # Decreasing
    else:
        return "→"  # Stable


def get_metrics_summary(memory: MetaCoordinatorMemory) -> Dict[str, Any]:
    """Get comprehensive metrics summary."""
    mem = memory.memory
    
    # Success score
    score = memory.calculate_success_score()
    score_factors = mem.get("success_score", {}).get("factors", {})
    
    # Cycle times
    cycle = mem.get("cycle_time_metrics", {})
    avg_pr_cycle = cycle.get("average_pr_cycle_time_hours", 0)
    avg_issue_cycle = cycle.get("average_issue_cycle_time_hours", 0)
    pr_cycles = cycle.get("pr_cycle_times", [])
    issue_cycles = cycle.get("issue_cycle_times", [])
    
    # Open counts
    counts = mem.get("open_count_metrics", {})
    snapshots = counts.get("snapshots", [])
    baseline_prs = counts.get("baseline_open_prs")
    baseline_issues = counts.get("baseline_open_issues")
    
    current_prs = None
    current_issues = None
    if snapshots:
        current_prs = snapshots[-1].get("open_prs")
        current_issues = snapshots[-1].get("open_issues")
    
    # Cleanup stats
    stale_prs_closed = counts.get("stale_prs_closed", 0)
    total_prs_closed = counts.get("prs_closed_count", 0)
    proactive_rate = (stale_prs_closed / total_prs_closed * 100) if total_prs_closed > 0 else 0
    
    # Trends
    pr_trend = counts.get("open_pr_trend", [])
    issue_trend = counts.get("open_issue_trend", [])
    pr_trend_dir = calculate_trend(pr_trend)
    issue_trend_dir = calculate_trend(issue_trend)
    
    # Recent activity
    runs = mem.get("runs", {})
    total_runs = runs.get("total_runs", 0)
    last_run = runs.get("last_run")
    last_run_time = last_run.get("timestamp") if last_run else None
    
    # PR patterns
    pr_patterns = mem.get("pr_patterns", {})
    total_prs_processed = pr_patterns.get("total_prs_processed", 0)
    tech_leads_assigned = pr_patterns.get("tech_leads_assigned", {})
    
    # Issue patterns
    issue_patterns = mem.get("issue_patterns", {})
    total_issues_processed = issue_patterns.get("total_issues_processed", 0)
    agents_assigned = issue_patterns.get("agents_assigned", {})
    
    return {
        "score": {
            "overall": score,
            "cycle_time": score_factors.get("cycle_time_score", 0),
            "reduction": score_factors.get("reduction_score", 0),
            "cleanup": score_factors.get("proactive_cleanup_score", 0),
        },
        "cycle_times": {
            "pr_avg_hours": avg_pr_cycle,
            "pr_avg_formatted": format_duration(avg_pr_cycle),
            "pr_count": len(pr_cycles),
            "issue_avg_hours": avg_issue_cycle,
            "issue_avg_formatted": format_duration(avg_issue_cycle),
            "issue_count": len(issue_cycles),
        },
        "open_counts": {
            "prs": {
                "current": current_prs,
                "baseline": baseline_prs,
                "delta": (current_prs - baseline_prs) if (current_prs and baseline_prs) else None,
                "trend": pr_trend_dir,
            },
            "issues": {
                "current": current_issues,
                "baseline": baseline_issues,
                "delta": (current_issues - baseline_issues) if (current_issues and baseline_issues) else None,
                "trend": issue_trend_dir,
            },
        },
        "cleanup": {
            "stale_prs_closed": stale_prs_closed,
            "total_prs_closed": total_prs_closed,
            "proactive_rate": proactive_rate,
        },
        "activity": {
            "total_runs": total_runs,
            "last_run": last_run_time,
            "prs_processed": total_prs_processed,
            "issues_processed": total_issues_processed,
            "tech_leads_count": len(tech_leads_assigned),
            "agents_count": len(agents_assigned),
        },
        "top_contributors": {
            "tech_leads": sorted(tech_leads_assigned.items(), key=lambda x: x[1], reverse=True)[:5],
            "agents": sorted(agents_assigned.items(), key=lambda x: x[1], reverse=True)[:5],
        }
    }


def format_text(metrics: Dict[str, Any]) -> str:
    """Format metrics as human-readable text."""
    score = metrics["score"]
    cycle = metrics["cycle_times"]
    counts = metrics["open_counts"]
    cleanup = metrics["cleanup"]
    activity = metrics["activity"]
    
    lines = [
        "=" * 60,
        "Meta-Coordinator System Dashboard",
        "=" * 60,
        "",
        "## 🎯 Overall Health",
        f"Success Score: {score['overall']:.1f}/100",
        "",
        "Score Breakdown:",
        f"  - Cycle Time:       {score['cycle_time']:.1f}/100",
        f"  - Reduction:        {score['reduction']:.1f}/100",
        f"  - Proactive Cleanup: {score['cleanup']:.1f}/100",
        "",
        "## ⏱️ Cycle Times",
        f"PR Average:    {cycle['pr_avg_formatted']} ({cycle['pr_count']} measured)",
        f"Issue Average: {cycle['issue_avg_formatted']} ({cycle['issue_count']} measured)",
        "",
        "## 📊 Open Counts",
        f"PRs:    {counts['prs']['current']} (baseline: {counts['prs']['baseline']}, "
        f"delta: {counts['prs']['delta']:+d} {counts['prs']['trend']})",
        f"Issues: {counts['issues']['current']} (baseline: {counts['issues']['baseline']}, "
        f"delta: {counts['issues']['delta']:+d} {counts['issues']['trend']})",
        "",
        "## 🧹 Cleanup Activity",
        f"Stale PRs Closed: {cleanup['stale_prs_closed']}/{cleanup['total_prs_closed']} "
        f"({cleanup['proactive_rate']:.1f}%)",
        "",
        "## 📈 System Activity",
        f"Total Runs:       {activity['total_runs']}",
        f"Last Run:         {activity['last_run']}",
        f"PRs Processed:    {activity['prs_processed']}",
        f"Issues Processed: {activity['issues_processed']}",
        "",
        "## 👥 Top Contributors",
        "Tech Leads:",
    ]
    
    for name, count in metrics["top_contributors"]["tech_leads"]:
        lines.append(f"  - {name}: {count} PRs")
    
    lines.append("")
    lines.append("Agents:")
    for name, count in metrics["top_contributors"]["agents"]:
        lines.append(f"  - {name}: {count} issues")
    
    lines.append("")
    lines.append("=" * 60)
    
    return "\n".join(lines)


def format_markdown(metrics: Dict[str, Any]) -> str:
    """Format metrics as markdown."""
    score = metrics["score"]
    cycle = metrics["cycle_times"]
    counts = metrics["open_counts"]
    cleanup = metrics["cleanup"]
    activity = metrics["activity"]
    
    # Status emoji based on score
    if score["overall"] >= 80:
        status = "🟢 HEALTHY"
    elif score["overall"] >= 60:
        status = "🟡 IMPROVING"
    else:
        status = "🔴 NEEDS ATTENTION"
    
    lines = [
        "# Meta-Coordinator System Dashboard",
        "",
        f"**Status:** {status}",
        f"**Success Score:** {score['overall']:.1f}/100",
        f"**Last Updated:** {activity['last_run']}",
        "",
        "## 🎯 Score Breakdown",
        "",
        f"| Component | Score | Target |",
        f"|-----------|-------|--------|",
        f"| Cycle Time | {score['cycle_time']:.1f}/100 | 100/100 |",
        f"| Reduction | {score['reduction']:.1f}/100 | 100/100 |",
        f"| Proactive Cleanup | {score['cleanup']:.1f}/100 | 100/100 |",
        "",
        "## ⏱️ Cycle Times",
        "",
        f"| Type | Average | Count | Target |",
        f"|------|---------|-------|--------|",
        f"| PRs | {cycle['pr_avg_formatted']} | {cycle['pr_count']} | <24h |",
        f"| Issues | {cycle['issue_avg_formatted']} | {cycle['issue_count']} | <48h |",
        "",
        "## 📊 Open Counts",
        "",
        f"| Type | Current | Baseline | Change | Trend |",
        f"|------|---------|----------|--------|-------|",
        f"| PRs | {counts['prs']['current']} | {counts['prs']['baseline']} | "
        f"{counts['prs']['delta']:+d} | {counts['prs']['trend']} |",
        f"| Issues | {counts['issues']['current']} | {counts['issues']['baseline']} | "
        f"{counts['issues']['delta']:+d} | {counts['issues']['trend']} |",
        "",
        "## 🧹 Cleanup Activity",
        "",
        f"- **Stale PRs Closed:** {cleanup['stale_prs_closed']}/{cleanup['total_prs_closed']} "
        f"({cleanup['proactive_rate']:.1f}%)",
        f"- **Target:** 20%+ proactive cleanup rate",
        "",
        "## 📈 System Activity",
        "",
        f"- **Total Runs:** {activity['total_runs']}",
        f"- **PRs Processed:** {activity['prs_processed']}",
        f"- **Issues Processed:** {activity['issues_processed']}",
        f"- **Active Tech Leads:** {activity['tech_leads_count']}",
        f"- **Active Agents:** {activity['agents_count']}",
        "",
    ]
    
    return "\n".join(lines)


def main():
    # Parse arguments
    output_format = "text"
    if len(sys.argv) > 1:
        if sys.argv[1] in ["--format", "-f"]:
            if len(sys.argv) > 2:
                output_format = sys.argv[2]
        elif sys.argv[1] in ["text", "json", "markdown"]:
            output_format = sys.argv[1]
    
    # Load memory
    try:
        memory = MetaCoordinatorMemory()
    except Exception as e:
        print(f"ERROR: Could not load memory: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Get metrics
    try:
        metrics = get_metrics_summary(memory)
    except Exception as e:
        print(f"ERROR: Could not calculate metrics: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    # Output in requested format
    if output_format == "json":
        print(json.dumps(metrics, indent=2, default=str))
    elif output_format == "markdown":
        print(format_markdown(metrics))
    else:  # text
        print(format_text(metrics))


if __name__ == "__main__":
    main()
