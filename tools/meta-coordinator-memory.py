#!/usr/bin/env python3
"""
Meta-Coordinator Memory System

Provides non-blocking, persistent memory for the meta-coordinator-system agent
across workflow runs. Stores system state, decisions, patterns, and learnings.

This enables the meta-coordinator to:
- Track historical patterns and trends
- Learn from past decisions and outcomes
- Maintain context across sessions
- Make data-driven orchestration decisions
- Avoid repeating mistakes
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
from collections import defaultdict


class MetaCoordinatorMemory:
    """Non-blocking memory system for meta-coordinator agent."""
    
    def __init__(self, memory_file: str = ".github/agent-system/meta-coordinator-memory.json"):
        self.memory_file = Path(memory_file)
        self.memory_file.parent.mkdir(parents=True, exist_ok=True)
        self.memory = self._load_memory()
    
    def _load_memory(self) -> Dict[str, Any]:
        """Load memory from disk, create if doesn't exist."""
        if self.memory_file.exists():
            try:
                with open(self.memory_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️ Error loading memory: {e}")
                return self._initialize_memory()
        return self._initialize_memory()
    
    def _initialize_memory(self) -> Dict[str, Any]:
        """Initialize empty memory structure."""
        return {
            "version": "1.0",
            "created_at": datetime.utcnow().isoformat(),
            "last_updated": datetime.utcnow().isoformat(),
            "runs": {
                "total_runs": 0,
                "successful_runs": 0,
                "failed_runs": 0,
                "last_run": None,
                "average_duration_seconds": 0
            },
            "pr_patterns": {
                "total_prs_processed": 0,
                "tech_leads_assigned": defaultdict(int),
                "complexity_distribution": defaultdict(int),
                "review_cycles": defaultdict(int),
                "approval_times": []
            },
            "issue_patterns": {
                "total_issues_processed": 0,
                "agents_assigned": defaultdict(int),
                "agent_success_rates": defaultdict(float),
                "assignment_times": []
            },
            "feedback_issues": {
                "total_created": 0,
                "by_tech_lead": defaultdict(int),
                "resolution_times": [],
                "duplicate_prevented": 0
            },
            "exceptions": {
                "total_handled": 0,
                "by_type": defaultdict(int),
                "recent": []
            },
            "decisions": {
                "recent": [],
                "patterns": {}
            },
            "learnings": {
                "insights": [],
                "recommendations": []
            },
            "system_health": {
                "last_check": None,
                "consistency_score": 1.0,
                "issues_detected": []
            }
        }
    
    def save(self):
        """Save memory to disk (non-blocking)."""
        try:
            self.memory["last_updated"] = datetime.utcnow().isoformat()
            
            # Write to temporary file first, then rename (atomic)
            temp_file = self.memory_file.with_suffix('.tmp')
            with open(temp_file, 'w') as f:
                json.dump(self.memory, f, indent=2, default=str)
            temp_file.replace(self.memory_file)
            
            return True
        except Exception as e:
            print(f"⚠️ Error saving memory: {e}")
            return False
    
    def record_run(self, success: bool, duration_seconds: float, actions_taken: int):
        """Record a coordination run."""
        self.memory["runs"]["total_runs"] += 1
        if success:
            self.memory["runs"]["successful_runs"] += 1
        else:
            self.memory["runs"]["failed_runs"] += 1
        
        self.memory["runs"]["last_run"] = {
            "timestamp": datetime.utcnow().isoformat(),
            "success": success,
            "duration_seconds": duration_seconds,
            "actions_taken": actions_taken
        }
        
        # Update average duration
        total = self.memory["runs"]["total_runs"]
        current_avg = self.memory["runs"]["average_duration_seconds"]
        self.memory["runs"]["average_duration_seconds"] = (
            (current_avg * (total - 1) + duration_seconds) / total
        )
        
        self.save()
    
    def record_pr_assignment(self, pr_number: int, tech_lead: str, 
                            complexity: str, files_changed: int):
        """Record a tech lead assignment to a PR."""
        self.memory["pr_patterns"]["total_prs_processed"] += 1
        self.memory["pr_patterns"]["tech_leads_assigned"][tech_lead] = \
            self.memory["pr_patterns"]["tech_leads_assigned"].get(tech_lead, 0) + 1
        self.memory["pr_patterns"]["complexity_distribution"][complexity] = \
            self.memory["pr_patterns"]["complexity_distribution"].get(complexity, 0) + 1
        
        self._record_decision(
            "pr_assignment",
            f"Assigned PR #{pr_number} to {tech_lead}",
            {
                "pr_number": pr_number,
                "tech_lead": tech_lead,
                "complexity": complexity,
                "files_changed": files_changed
            }
        )
        
        self.save()
    
    def record_issue_assignment(self, issue_number: int, agent: str, 
                               match_score: float):
        """Record an agent assignment to an issue."""
        self.memory["issue_patterns"]["total_issues_processed"] += 1
        self.memory["issue_patterns"]["agents_assigned"][agent] = \
            self.memory["issue_patterns"]["agents_assigned"].get(agent, 0) + 1
        
        # Track assignment time
        self.memory["issue_patterns"]["assignment_times"].append({
            "issue": issue_number,
            "agent": agent,
            "timestamp": datetime.utcnow().isoformat(),
            "score": match_score
        })
        
        # Keep only last 100 assignments
        if len(self.memory["issue_patterns"]["assignment_times"]) > 100:
            self.memory["issue_patterns"]["assignment_times"] = \
                self.memory["issue_patterns"]["assignment_times"][-100:]
        
        self._record_decision(
            "issue_assignment",
            f"Assigned issue #{issue_number} to {agent} (score: {match_score:.2f})",
            {
                "issue_number": issue_number,
                "agent": agent,
                "score": match_score
            }
        )
        
        self.save()
    
    def record_feedback_issue(self, pr_number: int, issue_number: int, 
                             tech_lead: str, agent: str):
        """Record creation of a feedback issue."""
        self.memory["feedback_issues"]["total_created"] += 1
        self.memory["feedback_issues"]["by_tech_lead"][tech_lead] = \
            self.memory["feedback_issues"]["by_tech_lead"].get(tech_lead, 0) + 1
        
        self._record_decision(
            "feedback_issue",
            f"Created feedback issue #{issue_number} for PR #{pr_number}",
            {
                "pr_number": pr_number,
                "issue_number": issue_number,
                "tech_lead": tech_lead,
                "agent": agent
            }
        )
        
        self.save()
    
    def record_duplicate_prevented(self, pr_number: int):
        """Record that a duplicate feedback issue was prevented."""
        self.memory["feedback_issues"]["duplicate_prevented"] += 1
        self._record_decision(
            "duplicate_prevented",
            f"Prevented duplicate feedback issue for PR #{pr_number}",
            {"pr_number": pr_number}
        )
        self.save()
    
    def record_exception(self, exception_type: str, description: str, 
                        context: Dict[str, Any]):
        """Record an exception that was handled."""
        self.memory["exceptions"]["total_handled"] += 1
        self.memory["exceptions"]["by_type"][exception_type] = \
            self.memory["exceptions"]["by_type"].get(exception_type, 0) + 1
        
        exception_record = {
            "type": exception_type,
            "description": description,
            "context": context,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        self.memory["exceptions"]["recent"].append(exception_record)
        
        # Keep only last 50 exceptions
        if len(self.memory["exceptions"]["recent"]) > 50:
            self.memory["exceptions"]["recent"] = \
                self.memory["exceptions"]["recent"][-50:]
        
        self.save()
    
    def _record_decision(self, decision_type: str, description: str, 
                        context: Dict[str, Any]):
        """Record a decision made by the meta-coordinator."""
        decision = {
            "type": decision_type,
            "description": description,
            "context": context,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        self.memory["decisions"]["recent"].append(decision)
        
        # Keep only last 100 decisions
        if len(self.memory["decisions"]["recent"]) > 100:
            self.memory["decisions"]["recent"] = \
                self.memory["decisions"]["recent"][-100:]
    
    def add_learning(self, insight: str, evidence: Dict[str, Any]):
        """Add a learning or insight."""
        learning = {
            "insight": insight,
            "evidence": evidence,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        self.memory["learnings"]["insights"].append(learning)
        
        # Keep only last 50 insights
        if len(self.memory["learnings"]["insights"]) > 50:
            self.memory["learnings"]["insights"] = \
                self.memory["learnings"]["insights"][-50:]
        
        self.save()
    
    def add_recommendation(self, recommendation: str, priority: str = "medium"):
        """Add a recommendation for system improvement."""
        rec = {
            "recommendation": recommendation,
            "priority": priority,
            "timestamp": datetime.utcnow().isoformat(),
            "status": "pending"
        }
        
        self.memory["learnings"]["recommendations"].append(rec)
        
        # Keep only last 20 recommendations
        if len(self.memory["learnings"]["recommendations"]) > 20:
            self.memory["learnings"]["recommendations"] = \
                self.memory["learnings"]["recommendations"][-20:]
        
        self.save()
    
    def update_system_health(self, consistency_score: float, 
                            issues: List[str]):
        """Update system health metrics."""
        self.memory["system_health"]["last_check"] = datetime.utcnow().isoformat()
        self.memory["system_health"]["consistency_score"] = consistency_score
        self.memory["system_health"]["issues_detected"] = issues
        
        self.save()
    
    def get_agent_performance(self, agent: str) -> Dict[str, Any]:
        """Get performance data for a specific agent."""
        assignments = self.memory["issue_patterns"]["agents_assigned"].get(agent, 0)
        success_rate = self.memory["issue_patterns"]["agent_success_rates"].get(agent, 0.0)
        
        # Get recent assignments
        recent = [
            a for a in self.memory["issue_patterns"]["assignment_times"]
            if a["agent"] == agent
        ][-10:]
        
        return {
            "agent": agent,
            "total_assignments": assignments,
            "success_rate": success_rate,
            "recent_assignments": recent
        }
    
    def get_tech_lead_stats(self, tech_lead: str) -> Dict[str, Any]:
        """Get statistics for a specific tech lead."""
        assignments = self.memory["pr_patterns"]["tech_leads_assigned"].get(tech_lead, 0)
        feedback_requests = self.memory["feedback_issues"]["by_tech_lead"].get(tech_lead, 0)
        
        return {
            "tech_lead": tech_lead,
            "total_pr_assignments": assignments,
            "feedback_requests": feedback_requests,
            "feedback_rate": feedback_requests / assignments if assignments > 0 else 0
        }
    
    def get_recent_patterns(self, limit: int = 20) -> Dict[str, Any]:
        """Get recent decision patterns."""
        return {
            "recent_decisions": self.memory["decisions"]["recent"][-limit:],
            "recent_exceptions": self.memory["exceptions"]["recent"][-limit:],
            "recent_insights": self.memory["learnings"]["insights"][-limit:]
        }
    
    def get_summary(self) -> str:
        """Get a human-readable summary of memory."""
        runs = self.memory["runs"]
        prs = self.memory["pr_patterns"]
        issues = self.memory["issue_patterns"]
        feedback = self.memory["feedback_issues"]
        exceptions = self.memory["exceptions"]
        health = self.memory["system_health"]
        
        summary = f"""
# Meta-Coordinator Memory Summary

## Run Statistics
- Total runs: {runs['total_runs']}
- Success rate: {runs['successful_runs'] / runs['total_runs'] * 100 if runs['total_runs'] > 0 else 0:.1f}%
- Average duration: {runs['average_duration_seconds']:.1f} seconds
- Last run: {runs['last_run']['timestamp'] if runs['last_run'] else 'Never'}

## PR Processing
- Total PRs processed: {prs['total_prs_processed']}
- Tech leads assigned: {len(prs['tech_leads_assigned'])} unique
- Most active tech lead: {max(prs['tech_leads_assigned'].items(), key=lambda x: x[1])[0] if prs['tech_leads_assigned'] else 'None'} ({max(prs['tech_leads_assigned'].values(), default=0)} PRs)

## Issue Processing
- Total issues processed: {issues['total_issues_processed']}
- Agents assigned: {len(issues['agents_assigned'])} unique
- Most active agent: {max(issues['agents_assigned'].items(), key=lambda x: x[1])[0] if issues['agents_assigned'] else 'None'} ({max(issues['agents_assigned'].values(), default=0)} issues)

## Feedback Issues
- Total created: {feedback['total_created']}
- Duplicates prevented: {feedback['duplicate_prevented']}

## Exception Handling
- Total exceptions: {exceptions['total_handled']}
- Most common: {max(exceptions['by_type'].items(), key=lambda x: x[1])[0] if exceptions['by_type'] else 'None'} ({max(exceptions['by_type'].values(), default=0)} times)

## System Health
- Last check: {health['last_check'] or 'Never'}
- Consistency score: {health['consistency_score']:.2f}
- Issues detected: {len(health['issues_detected'])}

## Recent Insights
{self._format_insights()}

## Recommendations
{self._format_recommendations()}
"""
        return summary.strip()
    
    def _format_insights(self) -> str:
        """Format recent insights for display."""
        insights = self.memory["learnings"]["insights"][-5:]
        if not insights:
            return "- No insights recorded yet"
        
        return "\n".join([
            f"- {i['insight']} ({i['timestamp'][:10]})"
            for i in insights
        ])
    
    def _format_recommendations(self) -> str:
        """Format pending recommendations for display."""
        recs = [
            r for r in self.memory["learnings"]["recommendations"]
            if r.get("status") == "pending"
        ][-5:]
        
        if not recs:
            return "- No pending recommendations"
        
        return "\n".join([
            f"- [{r['priority'].upper()}] {r['recommendation']}"
            for r in recs
        ])
    
    def analyze_trends(self) -> Dict[str, Any]:
        """Analyze trends and patterns from memory."""
        trends = {}
        
        # PR trends
        if self.memory["pr_patterns"]["total_prs_processed"] > 10:
            complexity_dist = self.memory["pr_patterns"]["complexity_distribution"]
            total = sum(complexity_dist.values())
            trends["pr_complexity"] = {
                level: count / total * 100
                for level, count in complexity_dist.items()
            }
        
        # Agent performance trends
        agent_assignments = self.memory["issue_patterns"]["agents_assigned"]
        if agent_assignments:
            total_assignments = sum(agent_assignments.values())
            trends["agent_utilization"] = {
                agent: count / total_assignments * 100
                for agent, count in sorted(
                    agent_assignments.items(),
                    key=lambda x: x[1],
                    reverse=True
                )[:10]
            }
        
        # Exception trends
        exception_types = self.memory["exceptions"]["by_type"]
        if exception_types:
            total_exceptions = sum(exception_types.values())
            trends["exception_distribution"] = {
                exc_type: count / total_exceptions * 100
                for exc_type, count in sorted(
                    exception_types.items(),
                    key=lambda x: x[1],
                    reverse=True
                )
            }
        
        return trends
    
    def get_context_for_decision(self, decision_type: str) -> Dict[str, Any]:
        """Get relevant historical context for a decision type."""
        # Get recent similar decisions
        similar = [
            d for d in self.memory["decisions"]["recent"]
            if d["type"] == decision_type
        ][-10:]
        
        # Get any related learnings
        related_insights = [
            i for i in self.memory["learnings"]["insights"]
            if decision_type in i["insight"].lower()
        ][-5:]
        
        return {
            "recent_similar_decisions": similar,
            "related_insights": related_insights,
            "patterns": self.memory["decisions"]["patterns"].get(decision_type, {})
        }


def main():
    """CLI interface for memory system."""
    import sys
    
    memory = MetaCoordinatorMemory()
    
    if len(sys.argv) < 2:
        print(memory.get_summary())
        return
    
    command = sys.argv[1]
    
    if command == "summary":
        print(memory.get_summary())
    
    elif command == "trends":
        trends = memory.analyze_trends()
        print(json.dumps(trends, indent=2))
    
    elif command == "agent":
        if len(sys.argv) < 3:
            print("Usage: meta-coordinator-memory.py agent <agent-name>")
            sys.exit(1)
        agent = sys.argv[2]
        stats = memory.get_agent_performance(agent)
        print(json.dumps(stats, indent=2))
    
    elif command == "tech-lead":
        if len(sys.argv) < 3:
            print("Usage: meta-coordinator-memory.py tech-lead <tech-lead-name>")
            sys.exit(1)
        tech_lead = sys.argv[2]
        stats = memory.get_tech_lead_stats(tech_lead)
        print(json.dumps(stats, indent=2))
    
    elif command == "patterns":
        patterns = memory.get_recent_patterns()
        print(json.dumps(patterns, indent=2, default=str))
    
    elif command == "context":
        if len(sys.argv) < 3:
            print("Usage: meta-coordinator-memory.py context <decision-type>")
            sys.exit(1)
        decision_type = sys.argv[2]
        context = memory.get_context_for_decision(decision_type)
        print(json.dumps(context, indent=2, default=str))
    
    else:
        print(f"Unknown command: {command}")
        print("Available commands: summary, trends, agent, tech-lead, patterns, context")
        sys.exit(1)


if __name__ == "__main__":
    main()
