#!/usr/bin/env python3
"""
Monitor Mentorship Dashboard - Real-time mentorship system monitoring

This tool provides a comprehensive real-time dashboard for monitoring the
agent mentorship program, including active mentorships, knowledge transfer
effectiveness, and mentor utilization.

Usage:
    python tools/monitor-mentorship-dashboard.py [options]

Options:
    --refresh SECONDS    Auto-refresh interval (default: 60)
    --export FILE        Export dashboard data to JSON file
    --compact            Use compact view for CI/CD
    --focus AREA         Focus on specific area: mentors|mentees|effectiveness|all

Examples:
    # Launch interactive dashboard
    python tools/monitor-mentorship-dashboard.py

    # Auto-refresh every 30 seconds
    python tools/monitor-mentorship-dashboard.py --refresh 30

    # Export data for external processing
    python tools/monitor-mentorship-dashboard.py --export dashboard.json

    # Compact view for CI/CD logs
    python tools/monitor-mentorship-dashboard.py --compact

Author: @create-guru
"""

import json
import os
import sys
import time
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional

# Repository paths
REPO_ROOT = Path(__file__).parent.parent
AGENT_SYSTEM_DIR = REPO_ROOT / ".github" / "agent-system"
MENTORSHIP_REGISTRY = AGENT_SYSTEM_DIR / "mentorship_registry.json"
HALL_OF_FAME_FILE = AGENT_SYSTEM_DIR / "hall_of_fame.json"
KNOWLEDGE_TEMPLATES_DIR = AGENT_SYSTEM_DIR / "templates" / "knowledge"


class MentorshipDashboard:
    """Real-time monitoring dashboard for the mentorship system."""

    def __init__(self):
        """Initialize the dashboard."""
        self.mentorships = self.load_mentorships()
        self.hall_of_fame = self.load_hall_of_fame()
        self.knowledge_templates = self.list_knowledge_templates()

    def load_mentorships(self) -> Dict[str, Any]:
        """Load mentorship registry."""
        if MENTORSHIP_REGISTRY.exists():
            with open(MENTORSHIP_REGISTRY, "r") as f:
                return json.load(f)
        return {"mentorships": [], "last_updated": None}

    def load_hall_of_fame(self) -> List[Dict[str, Any]]:
        """Load Hall of Fame agents."""
        if HALL_OF_FAME_FILE.exists():
            with open(HALL_OF_FAME_FILE, "r") as f:
                data = json.load(f)
                # Handle both list and dict formats
                if isinstance(data, list):
                    return data
                return data.get("agents", [])
        return []

    def list_knowledge_templates(self) -> List[str]:
        """List available knowledge templates."""
        if KNOWLEDGE_TEMPLATES_DIR.exists():
            return [
                f.stem for f in KNOWLEDGE_TEMPLATES_DIR.glob("*.md")
            ]
        return []

    def get_active_mentorships(self) -> List[Dict[str, Any]]:
        """Get list of active mentorships."""
        return [
            m for m in self.mentorships.get("mentorships", [])
            if m.get("status") == "active"
        ]

    def get_completed_mentorships(self) -> List[Dict[str, Any]]:
        """Get list of completed mentorships."""
        return [
            m for m in self.mentorships.get("mentorships", [])
            if m.get("status") == "completed"
        ]

    def get_mentor_utilization(self) -> Dict[str, Any]:
        """Calculate mentor utilization metrics."""
        active = self.get_active_mentorships()
        
        # Count mentees per mentor
        mentor_loads = {}
        for m in active:
            mentor_id = m.get("mentor_id")
            if mentor_id:
                mentor_loads[mentor_id] = mentor_loads.get(mentor_id, 0) + 1

        # Calculate utilization
        max_capacity = 3  # Each mentor can handle up to 3 mentees
        total_mentors = len(self.hall_of_fame)
        total_capacity = total_mentors * max_capacity
        used_capacity = len(active)
        
        return {
            "total_mentors": total_mentors,
            "total_capacity": total_capacity,
            "used_capacity": used_capacity,
            "available_capacity": total_capacity - used_capacity,
            "utilization_pct": (used_capacity / total_capacity * 100) if total_capacity > 0 else 0,
            "mentor_loads": mentor_loads,
            "overloaded_mentors": [
                m_id for m_id, load in mentor_loads.items() if load > max_capacity
            ]
        }

    def get_effectiveness_metrics(self) -> Dict[str, Any]:
        """Calculate mentorship effectiveness metrics."""
        completed = self.get_completed_mentorships()
        
        if not completed:
            return {
                "total_completed": 0,
                "success_count": 0,
                "success_rate": 0.0,
                "avg_improvement": 0.0,
                "avg_duration_days": 0
            }

        success_count = sum(1 for m in completed if m.get("success", False))
        improvements = [
            m.get("mentee_improvement_pct", 0) for m in completed
            if m.get("mentee_improvement_pct") is not None
        ]
        
        # Calculate average duration
        durations = []
        for m in completed:
            start = m.get("start_date")
            end = m.get("end_date")
            if start and end:
                try:
                    start_dt = datetime.fromisoformat(start)
                    end_dt = datetime.fromisoformat(end)
                    durations.append((end_dt - start_dt).days)
                except:
                    pass

        return {
            "total_completed": len(completed),
            "success_count": success_count,
            "success_rate": (success_count / len(completed) * 100) if completed else 0.0,
            "avg_improvement": sum(improvements) / len(improvements) if improvements else 0.0,
            "avg_duration_days": sum(durations) / len(durations) if durations else 0
        }

    def get_mentor_rankings(self) -> List[Dict[str, Any]]:
        """Get mentor rankings by effectiveness."""
        completed = self.get_completed_mentorships()
        
        # Group by mentor
        mentor_stats = {}
        for m in completed:
            mentor_id = m.get("mentor_id")
            if not mentor_id:
                continue
                
            if mentor_id not in mentor_stats:
                mentor_stats[mentor_id] = {
                    "mentor_id": mentor_id,
                    "total_mentees": 0,
                    "successful": 0,
                    "improvements": []
                }
            
            mentor_stats[mentor_id]["total_mentees"] += 1
            if m.get("success"):
                mentor_stats[mentor_id]["successful"] += 1
            
            improvement = m.get("mentee_improvement_pct")
            if improvement is not None:
                mentor_stats[mentor_id]["improvements"].append(improvement)

        # Calculate success rates
        rankings = []
        for mentor_id, stats in mentor_stats.items():
            total = stats["total_mentees"]
            success_rate = (stats["successful"] / total * 100) if total > 0 else 0
            avg_improvement = (
                sum(stats["improvements"]) / len(stats["improvements"])
                if stats["improvements"] else 0
            )
            
            # Find mentor details
            mentor_agent = next(
                (a for a in self.hall_of_fame if a.get("agent_id") == mentor_id),
                None
            )
            
            rankings.append({
                "mentor_id": mentor_id,
                "mentor_name": mentor_agent.get("inspired_by", "Unknown") if mentor_agent else "Unknown",
                "specialization": mentor_agent.get("specialization", "Unknown") if mentor_agent else "Unknown",
                "total_mentees": total,
                "successful": stats["successful"],
                "success_rate": success_rate,
                "avg_improvement": avg_improvement
            })

        # Sort by success rate, then improvement
        rankings.sort(key=lambda x: (x["success_rate"], x["avg_improvement"]), reverse=True)
        return rankings

    def display_header(self, compact: bool = False):
        """Display dashboard header."""
        if compact:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Mentorship Dashboard")
        else:
            print("\n" + "=" * 80)
            print("📊 AGENT MENTORSHIP PROGRAM - MONITORING DASHBOARD")
            print("=" * 80)
            print(f"Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"Data Source: {MENTORSHIP_REGISTRY}")
            print("=" * 80 + "\n")

    def display_overview(self, compact: bool = False):
        """Display system overview."""
        active = self.get_active_mentorships()
        completed = self.get_completed_mentorships()
        utilization = self.get_mentor_utilization()
        effectiveness = self.get_effectiveness_metrics()

        if compact:
            print(f"Active: {len(active)} | Completed: {len(completed)} | "
                  f"Utilization: {utilization['utilization_pct']:.1f}% | "
                  f"Success Rate: {effectiveness['success_rate']:.1f}%")
        else:
            print("🎯 SYSTEM OVERVIEW")
            print("-" * 80)
            print(f"  Total Mentors:           {utilization['total_mentors']}")
            print(f"  Total Capacity:          {utilization['total_capacity']} slots")
            print(f"  Knowledge Templates:     {len(self.knowledge_templates)}")
            print()
            print(f"  Active Mentorships:      {len(active)}")
            print(f"  Completed Mentorships:   {len(completed)}")
            print(f"  Capacity Utilization:    {utilization['utilization_pct']:.1f}%")
            print()
            print(f"  Overall Success Rate:    {effectiveness['success_rate']:.1f}%")
            print(f"  Avg Improvement:         +{effectiveness['avg_improvement']:.1f}%")
            print(f"  Avg Duration:            {effectiveness['avg_duration_days']:.0f} days")
            print()

    def display_mentor_utilization(self, compact: bool = False):
        """Display mentor utilization details."""
        utilization = self.get_mentor_utilization()
        active = self.get_active_mentorships()

        if compact:
            overloaded = len(utilization['overloaded_mentors'])
            if overloaded > 0:
                print(f"⚠️  {overloaded} mentor(s) overloaded!")
        else:
            print("👨‍🏫 MENTOR UTILIZATION")
            print("-" * 80)
            
            if not utilization['mentor_loads']:
                print("  No mentors currently assigned.")
            else:
                for mentor_id, load in sorted(
                    utilization['mentor_loads'].items(),
                    key=lambda x: x[1],
                    reverse=True
                ):
                    # Find mentor details
                    mentor = next(
                        (a for a in self.hall_of_fame if a.get("agent_id") == mentor_id),
                        None
                    )
                    name = mentor.get("inspired_by", "Unknown") if mentor else mentor_id
                    spec = mentor.get("specialization", "Unknown") if mentor else "Unknown"
                    
                    status = "🔴" if load > 3 else "🟢"
                    bar = "█" * load + "░" * (3 - min(load, 3))
                    print(f"  {status} {name:<20} {spec:<20} {bar} {load}/3")
            print()

    def display_active_mentorships(self, compact: bool = False):
        """Display active mentorships."""
        active = self.get_active_mentorships()

        if compact:
            if active:
                print(f"{len(active)} active mentorship(s)")
        else:
            print("🎓 ACTIVE MENTORSHIPS")
            print("-" * 80)
            
            if not active:
                print("  No active mentorships at this time.")
            else:
                for m in active:
                    mentor = next(
                        (a for a in self.hall_of_fame if a.get("agent_id") == m.get("mentor_id")),
                        None
                    )
                    mentor_name = mentor.get("inspired_by", "Unknown") if mentor else "Unknown"
                    
                    start_date = m.get("start_date", "Unknown")
                    mentee_id = m.get("mentee_id", "Unknown")
                    
                    # Calculate days active
                    days_active = "N/A"
                    if start_date:
                        try:
                            start_dt = datetime.fromisoformat(start_date)
                            days_active = (datetime.now() - start_dt).days
                        except:
                            pass
                    
                    print(f"  🎯 {mentee_id}")
                    print(f"     Mentor: {mentor_name} ({m.get('mentor_specialization', 'Unknown')})")
                    print(f"     Started: {start_date} ({days_active} days)")
                    print()
            print()

    def display_effectiveness(self, compact: bool = False):
        """Display effectiveness metrics and rankings."""
        rankings = self.get_mentor_rankings()

        if compact:
            if rankings:
                top = rankings[0]
                print(f"Top mentor: {top['mentor_name']} ({top['success_rate']:.0f}% success)")
        else:
            print("📈 MENTOR EFFECTIVENESS RANKINGS")
            print("-" * 80)
            
            if not rankings:
                print("  No completed mentorships to rank.")
            else:
                print(f"  {'Rank':<6} {'Mentor':<20} {'Spec':<20} {'Mentees':<10} {'Success Rate':<15} {'Avg Improvement'}")
                print("  " + "-" * 78)
                
                for idx, rank in enumerate(rankings, 1):
                    medal = "🥇" if idx == 1 else "🥈" if idx == 2 else "🥉" if idx == 3 else "  "
                    print(f"  {medal} {idx:<3} {rank['mentor_name']:<20} "
                          f"{rank['specialization']:<20} {rank['total_mentees']:<10} "
                          f"{rank['success_rate']:>6.1f}% {rank['successful']:>2}/{rank['total_mentees']:<3} "
                          f"+{rank['avg_improvement']:>5.1f}%")
            print()

    def display_knowledge_base(self, compact: bool = False):
        """Display knowledge base status."""
        if compact:
            print(f"{len(self.knowledge_templates)} knowledge template(s)")
        else:
            print("📚 KNOWLEDGE BASE")
            print("-" * 80)
            print(f"  Total Templates: {len(self.knowledge_templates)}")
            print(f"  Location: {KNOWLEDGE_TEMPLATES_DIR}")
            
            if self.knowledge_templates:
                print("\n  Available Templates:")
                for template in sorted(self.knowledge_templates)[:10]:
                    print(f"    • {template}")
                if len(self.knowledge_templates) > 10:
                    print(f"    ... and {len(self.knowledge_templates) - 10} more")
            print()

    def display_all(self, compact: bool = False):
        """Display complete dashboard."""
        self.display_header(compact)
        self.display_overview(compact)
        
        if not compact:
            self.display_mentor_utilization(compact)
            self.display_active_mentorships(compact)
            self.display_effectiveness(compact)
            self.display_knowledge_base(compact)

    def export_data(self, output_file: str):
        """Export dashboard data to JSON."""
        data = {
            "timestamp": datetime.now().isoformat(),
            "overview": {
                "active_mentorships": len(self.get_active_mentorships()),
                "completed_mentorships": len(self.get_completed_mentorships()),
                "total_mentors": len(self.hall_of_fame),
                "knowledge_templates": len(self.knowledge_templates)
            },
            "utilization": self.get_mentor_utilization(),
            "effectiveness": self.get_effectiveness_metrics(),
            "mentor_rankings": self.get_mentor_rankings(),
            "active_mentorships": self.get_active_mentorships(),
            "completed_mentorships": self.get_completed_mentorships()
        }

        with open(output_file, "w") as f:
            json.dump(data, f, indent=2)
        
        print(f"✅ Dashboard data exported to: {output_file}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Monitor agent mentorship program dashboard",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument(
        "--refresh",
        type=int,
        metavar="SECONDS",
        help="Auto-refresh interval in seconds"
    )
    parser.add_argument(
        "--export",
        type=str,
        metavar="FILE",
        help="Export dashboard data to JSON file"
    )
    parser.add_argument(
        "--compact",
        action="store_true",
        help="Use compact view for CI/CD"
    )
    parser.add_argument(
        "--focus",
        choices=["mentors", "mentees", "effectiveness", "all"],
        default="all",
        help="Focus on specific dashboard area"
    )

    args = parser.parse_args()

    dashboard = MentorshipDashboard()

    # Export mode
    if args.export:
        dashboard.export_data(args.export)
        return

    # Display mode
    try:
        while True:
            # Clear screen for refresh (only in non-compact mode)
            if args.refresh and not args.compact:
                os.system('clear' if os.name == 'posix' else 'cls')

            # Display selected view
            if args.focus == "all":
                dashboard.display_all(args.compact)
            elif args.focus == "mentors":
                dashboard.display_header(args.compact)
                dashboard.display_mentor_utilization(args.compact)
            elif args.focus == "mentees":
                dashboard.display_header(args.compact)
                dashboard.display_active_mentorships(args.compact)
            elif args.focus == "effectiveness":
                dashboard.display_header(args.compact)
                dashboard.display_effectiveness(args.compact)

            # Auto-refresh or exit
            if args.refresh:
                if not args.compact:
                    print(f"Refreshing in {args.refresh} seconds... (Ctrl+C to exit)")
                time.sleep(args.refresh)
                dashboard = MentorshipDashboard()  # Reload data
            else:
                break

    except KeyboardInterrupt:
        print("\n\nDashboard stopped.")
        sys.exit(0)


if __name__ == "__main__":
    main()
