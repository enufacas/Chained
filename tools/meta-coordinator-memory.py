#!/usr/bin/env python3
"""
Meta-Coordinator Memory System (Concurrent-Safe)

Provides non-blocking, persistent memory for the meta-coordinator-system agent
across workflow runs. Handles concurrent access from multiple workflow instances.

CONCURRENCY STRATEGY:
- File-based locking with timeouts
- Optimistic concurrency with retry
- Last-write-wins for aggregates
- Append-only for lists (merge on conflict)
- Session isolation with final merge

This enables the meta-coordinator to:
- Track historical patterns and trends
- Learn from past decisions and outcomes
- Maintain context across sessions
- Make data-driven orchestration decisions
- Avoid repeating mistakes
- Handle multiple concurrent sessions safely
"""

import json
import os
import time
import fcntl
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
from collections import defaultdict
import hashlib


class ConcurrentMemoryError(Exception):
    """Raised when concurrent memory operation fails."""
    pass


class MetaCoordinatorMemory:
    """Concurrent-safe memory system for meta-coordinator agent."""
    
    def __init__(self, 
                 memory_file: str = ".github/agent-system/meta-coordinator-memory.json",
                 session_id: Optional[str] = None,
                 lock_timeout: int = 30):
        self.memory_file = Path(memory_file)
        self.memory_file.parent.mkdir(parents=True, exist_ok=True)
        self.lock_file = Path(str(self.memory_file) + ".lock")
        self.lock_timeout = lock_timeout
        
        # Generate unique session ID
        self.session_id = session_id or self._generate_session_id()
        
        # Session-local changes (not yet persisted)
        self.session_changes = {
            "pr_assignments": [],
            "issue_assignments": [],
            "feedback_issues": [],
            "exceptions": [],
            "decisions": [],
            "learnings": []
        }
        
        self.memory = self._load_memory()
    
    def _generate_session_id(self) -> str:
        """Generate unique session ID."""
        timestamp = datetime.utcnow().isoformat()
        pid = os.getpid()
        random_data = os.urandom(8).hex()
        return hashlib.sha256(f"{timestamp}-{pid}-{random_data}".encode()).hexdigest()[:16]
    
    def _acquire_lock(self, timeout: Optional[int] = None) -> bool:
        """Acquire file lock with timeout."""
        timeout = timeout or self.lock_timeout
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                # Create lock file
                lock_fd = os.open(self.lock_file, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                os.write(lock_fd, f"{self.session_id}\n{datetime.utcnow().isoformat()}".encode())
                os.close(lock_fd)
                return True
            except FileExistsError:
                # Lock exists, check if stale
                if self._is_lock_stale():
                    self._release_lock(force=True)
                    continue
                time.sleep(0.5)
        
        return False
    
    def _release_lock(self, force: bool = False):
        """Release file lock."""
        try:
            if force or self.lock_file.exists():
                self.lock_file.unlink(missing_ok=True)
        except Exception as e:
            print(f"⚠️ Warning: Failed to release lock: {e}")
    
    def _is_lock_stale(self) -> bool:
        """Check if lock file is stale (older than 5 minutes)."""
        try:
            if not self.lock_file.exists():
                return False
            
            # Check file age
            mtime = self.lock_file.stat().st_mtime
            age_seconds = time.time() - mtime
            
            # Lock is stale if older than 5 minutes
            return age_seconds > 300
        except Exception:
            return False
    
    def _load_memory(self) -> Dict[str, Any]:
        """Load memory from disk with retry on concurrent access."""
        max_retries = 3
        retry_delay = 1
        
        for attempt in range(max_retries):
            try:
                if self.memory_file.exists():
                    with open(self.memory_file, 'r') as f:
                        return json.load(f)
                else:
                    return self._initialize_memory()
            except json.JSONDecodeError as e:
                print(f"⚠️ JSON decode error (attempt {attempt + 1}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    continue
                return self._initialize_memory()
            except Exception as e:
                print(f"⚠️ Error loading memory (attempt {attempt + 1}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    continue
                return self._initialize_memory()
        
        return self._initialize_memory()
    
    def _initialize_memory(self) -> Dict[str, Any]:
        """Initialize empty memory structure."""
        return {
            "version": "1.1",  # Updated for cycle time & open count tracking
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
            },
            "cycle_time_metrics": {
                "pr_cycle_times": [],  # List of {pr_num, created_at, closed_at, duration_hours}
                "issue_cycle_times": [],  # List of {issue_num, created_at, closed_at, duration_hours}
                "average_pr_cycle_time_hours": 0,
                "average_issue_cycle_time_hours": 0,
                "cycle_time_trend": []  # Track over time
            },
            "open_count_metrics": {
                "snapshots": [],  # List of {timestamp, open_prs, open_issues}
                "open_pr_trend": [],  # Track open PR count over time
                "open_issue_trend": [],  # Track open issue count over time
                "prs_closed_count": 0,  # Total PRs closed by meta-coordinator
                "issues_closed_count": 0,  # Total issues closed by meta-coordinator
                "stale_prs_closed": 0,  # Stale PRs proactively closed
                "baseline_open_prs": None,  # Starting count for reduction target
                "baseline_open_issues": None  # Starting count for reduction target
            },
            "success_score": {
                "current_score": 0,  # Composite score based on cycle time + reduction
                "score_history": [],  # Track score over time
                "factors": {
                    "cycle_time_score": 0,  # Lower cycle time = higher score
                    "reduction_score": 0,  # More reduction = higher score
                    "proactive_cleanup_score": 0  # More cleanup = higher score
                }
            }
        }
    
    def save(self, merge_strategy: str = "append_lists"):
        """
        Save memory to disk with concurrent-safe merge.
        
        Args:
            merge_strategy: How to handle concurrent updates
                - "append_lists": Merge list additions (default)
                - "last_write_wins": Latest write overwrites
                - "fail_on_conflict": Raise error if conflict detected
        """
        max_retries = 3
        
        for attempt in range(max_retries):
            try:
                # Acquire lock
                if not self._acquire_lock():
                    if merge_strategy == "fail_on_conflict":
                        raise ConcurrentMemoryError("Could not acquire lock")
                    print(f"⚠️ Lock timeout (attempt {attempt + 1}), retrying...")
                    continue
                
                try:
                    # Reload current state (may have changed since we loaded)
                    current_memory = self._load_memory_unsafe()
                    
                    # Merge session changes
                    merged_memory = self._merge_memories(current_memory, self.memory, merge_strategy)
                    
                    # Update timestamp
                    merged_memory["last_updated"] = datetime.utcnow().isoformat()
                    
                    # Write atomically
                    temp_file = self.memory_file.with_suffix('.tmp')
                    with open(temp_file, 'w') as f:
                        json.dump(merged_memory, f, indent=2, default=str)
                    temp_file.replace(self.memory_file)
                    
                    # Update in-memory state
                    self.memory = merged_memory
                    
                    return True
                    
                finally:
                    # Always release lock
                    self._release_lock()
            
            except Exception as e:
                print(f"⚠️ Error saving memory (attempt {attempt + 1}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(1)
                    continue
                return False
        
        return False
    
    def _load_memory_unsafe(self) -> Dict[str, Any]:
        """Load memory without lock (assumes caller holds lock)."""
        if self.memory_file.exists():
            with open(self.memory_file, 'r') as f:
                return json.load(f)
        return self._initialize_memory()
    
    def _merge_memories(self, 
                       current: Dict[str, Any], 
                       session: Dict[str, Any],
                       strategy: str) -> Dict[str, Any]:
        """
        Merge current memory with session changes.
        
        Strategies:
        - append_lists: Merge list additions, last-write-wins for scalars
        - last_write_wins: Session completely overwrites current
        - fail_on_conflict: Not used here (handled in save)
        """
        if strategy == "last_write_wins":
            return session
        
        # Default: append_lists strategy
        merged = current.copy()
        
        # Merge runs (additive counters)
        if "runs" in session:
            merged["runs"]["total_runs"] = current.get("runs", {}).get("total_runs", 0) + 1
            if session["runs"].get("last_run"):
                merged["runs"]["last_run"] = session["runs"]["last_run"]
                if session["runs"]["last_run"].get("success"):
                    merged["runs"]["successful_runs"] = current.get("runs", {}).get("successful_runs", 0) + 1
                else:
                    merged["runs"]["failed_runs"] = current.get("runs", {}).get("failed_runs", 0) + 1
        
        # Merge PR patterns (additive)
        if "pr_patterns" in session:
            merged["pr_patterns"]["total_prs_processed"] = \
                current.get("pr_patterns", {}).get("total_prs_processed", 0) + \
                len(self.session_changes.get("pr_assignments", []))
            
            # Merge tech_leads_assigned counts
            for lead, count in session.get("pr_patterns", {}).get("tech_leads_assigned", {}).items():
                current_count = current.get("pr_patterns", {}).get("tech_leads_assigned", {}).get(lead, 0)
                merged["pr_patterns"]["tech_leads_assigned"][lead] = current_count + count
            
            # Merge complexity_distribution
            for complexity, count in session.get("pr_patterns", {}).get("complexity_distribution", {}).items():
                current_count = current.get("pr_patterns", {}).get("complexity_distribution", {}).get(complexity, 0)
                merged["pr_patterns"]["complexity_distribution"][complexity] = current_count + count
        
        # Merge issue patterns (additive)
        if "issue_patterns" in session:
            merged["issue_patterns"]["total_issues_processed"] = \
                current.get("issue_patterns", {}).get("total_issues_processed", 0) + \
                len(self.session_changes.get("issue_assignments", []))
            
            # Merge agents_assigned counts
            for agent, count in session.get("issue_patterns", {}).get("agents_assigned", {}).items():
                current_count = current.get("issue_patterns", {}).get("agents_assigned", {}).get(agent, 0)
                merged["issue_patterns"]["agents_assigned"][agent] = current_count + count
            
            # Append assignment_times (keep last 100)
            current_times = current.get("issue_patterns", {}).get("assignment_times", [])
            session_times = session.get("issue_patterns", {}).get("assignment_times", [])
            merged["issue_patterns"]["assignment_times"] = (current_times + session_times)[-100:]
        
        # Merge feedback issues (additive)
        if "feedback_issues" in session:
            merged["feedback_issues"]["total_created"] = \
                current.get("feedback_issues", {}).get("total_created", 0) + \
                len(self.session_changes.get("feedback_issues", []))
            
            merged["feedback_issues"]["duplicate_prevented"] = \
                current.get("feedback_issues", {}).get("duplicate_prevented", 0) + \
                session.get("feedback_issues", {}).get("duplicate_prevented", 0)
            
            # Merge by_tech_lead counts
            for lead, count in session.get("feedback_issues", {}).get("by_tech_lead", {}).items():
                current_count = current.get("feedback_issues", {}).get("by_tech_lead", {}).get(lead, 0)
                merged["feedback_issues"]["by_tech_lead"][lead] = current_count + count
        
        # Merge exceptions (append recent, keep last 50)
        current_exceptions = current.get("exceptions", {}).get("recent", [])
        session_exceptions = session.get("exceptions", {}).get("recent", [])
        merged["exceptions"]["recent"] = (current_exceptions + session_exceptions)[-50:]
        merged["exceptions"]["total_handled"] = \
            current.get("exceptions", {}).get("total_handled", 0) + len(session_exceptions)
        
        # Merge exception counts
        for exc_type, count in session.get("exceptions", {}).get("by_type", {}).items():
            current_count = current.get("exceptions", {}).get("by_type", {}).get(exc_type, 0)
            merged["exceptions"]["by_type"][exc_type] = current_count + count
        
        # Merge decisions (append recent, keep last 100)
        current_decisions = current.get("decisions", {}).get("recent", [])
        session_decisions = session.get("decisions", {}).get("recent", [])
        merged["decisions"]["recent"] = (current_decisions + session_decisions)[-100:]
        
        # Merge learnings (append insights, keep last 50)
        current_insights = current.get("learnings", {}).get("insights", [])
        session_insights = session.get("learnings", {}).get("insights", [])
        merged["learnings"]["insights"] = (current_insights + session_insights)[-50:]
        
        # Merge recommendations (append, keep last 20)
        current_recs = current.get("learnings", {}).get("recommendations", [])
        session_recs = session.get("learnings", {}).get("recommendations", [])
        merged["learnings"]["recommendations"] = (current_recs + session_recs)[-20:]
        
        # System health: last write wins (most recent check)
        if "system_health" in session and session["system_health"].get("last_check"):
            merged["system_health"] = session["system_health"]
        
        return merged
    
    def record_run(self, success: bool, duration_seconds: float, actions_taken: int):
        """Record a coordination run."""
        self.memory["runs"]["last_run"] = {
            "timestamp": datetime.utcnow().isoformat(),
            "success": success,
            "duration_seconds": duration_seconds,
            "actions_taken": actions_taken,
            "session_id": self.session_id
        }
        
        # Note: total_runs incremented during merge
        # Average duration will be recalculated from all runs
        
        self.save()
    
    def record_pr_assignment(self, pr_number: int, tech_lead: str, 
                            complexity: str, files_changed: int):
        """Record a tech lead assignment to a PR."""
        # Track in session
        self.session_changes["pr_assignments"].append({
            "pr_number": pr_number,
            "tech_lead": tech_lead,
            "complexity": complexity,
            "files_changed": files_changed,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # Update in-memory counts (will be merged later)
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
    
    def record_issue_assignment(self, issue_number: int, agent: str, 
                               match_score: float):
        """Record an agent assignment to an issue."""
        # Track in session
        self.session_changes["issue_assignments"].append({
            "issue_number": issue_number,
            "agent": agent,
            "score": match_score,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # Update in-memory counts (will be merged later)
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
    
    def record_feedback_issue(self, pr_number: int, issue_number: int, 
                             tech_lead: str, agent: str):
        """Record creation of a feedback issue."""
        # Track in session
        self.session_changes["feedback_issues"].append({
            "pr_number": pr_number,
            "issue_number": issue_number,
            "tech_lead": tech_lead,
            "agent": agent,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # Update in-memory counts (will be merged later)
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
    
    def record_duplicate_prevented(self, pr_number: int):
        """Record that a duplicate feedback issue was prevented."""
        self.memory["feedback_issues"]["duplicate_prevented"] += 1
        self._record_decision(
            "duplicate_prevented",
            f"Prevented duplicate feedback issue for PR #{pr_number}",
            {"pr_number": pr_number}
        )
    
    def record_exception(self, exception_type: str, description: str, 
                        context: Dict[str, Any]):
        """Record an exception that was handled."""
        # Track in session
        self.session_changes["exceptions"].append({
            "type": exception_type,
            "description": description,
            "context": context,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # Update in-memory (will be merged later)
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
    
    def _record_decision(self, decision_type: str, description: str, 
                        context: Dict[str, Any]):
        """Record a decision made by the meta-coordinator."""
        # Track in session
        decision = {
            "type": decision_type,
            "description": description,
            "context": context,
            "timestamp": datetime.utcnow().isoformat(),
            "session_id": self.session_id
        }
        
        self.session_changes["decisions"].append(decision)
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
            "timestamp": datetime.utcnow().isoformat(),
            "session_id": self.session_id
        }
        
        self.session_changes["learnings"].append(learning)
        self.memory["learnings"]["insights"].append(learning)
        
        # Keep only last 50 insights
        if len(self.memory["learnings"]["insights"]) > 50:
            self.memory["learnings"]["insights"] = \
                self.memory["learnings"]["insights"][-50:]
    
    def add_recommendation(self, recommendation: str, priority: str = "medium"):
        """Add a recommendation for system improvement."""
        rec = {
            "recommendation": recommendation,
            "priority": priority,
            "timestamp": datetime.utcnow().isoformat(),
            "status": "pending",
            "session_id": self.session_id
        }
        
        self.memory["learnings"]["recommendations"].append(rec)
        
        # Keep only last 20 recommendations
        if len(self.memory["learnings"]["recommendations"]) > 20:
            self.memory["learnings"]["recommendations"] = \
                self.memory["learnings"]["recommendations"][-20:]
    
    def update_system_health(self, consistency_score: float, 
                            issues: List[str]):
        """Update system health metrics."""
        self.memory["system_health"]["last_check"] = datetime.utcnow().isoformat()
        self.memory["system_health"]["consistency_score"] = consistency_score
        self.memory["system_health"]["issues_detected"] = issues
    
    def commit(self):
        """
        Commit all session changes to persistent storage.
        Call this at the end of a workflow run to persist all changes.
        """
        return self.save(merge_strategy="append_lists")
    
    def get_session_summary(self) -> Dict[str, Any]:
        """Get summary of changes made in this session."""
        return {
            "session_id": self.session_id,
            "pr_assignments": len(self.session_changes["pr_assignments"]),
            "issue_assignments": len(self.session_changes["issue_assignments"]),
            "feedback_issues": len(self.session_changes["feedback_issues"]),
            "exceptions": len(self.session_changes["exceptions"]),
            "decisions": len(self.session_changes["decisions"]),
            "learnings": len(self.session_changes["learnings"])
        }
    
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
    
    def record_open_counts(self, open_prs: int, open_issues: int):
        """
        Record current open PR and issue counts.
        
        This is the PRIMARY SUCCESS METRIC - reducing these counts over time.
        Call this at the start and end of each coordination run.
        """
        snapshot = {
            "timestamp": datetime.utcnow().isoformat(),
            "open_prs": open_prs,
            "open_issues": open_issues
        }
        
        # Ensure keys exist (for backwards compatibility)
        if "open_count_metrics" not in self.memory:
            self.memory["open_count_metrics"] = {
                "snapshots": [],
                "open_pr_trend": [],
                "open_issue_trend": [],
                "prs_closed_count": 0,
                "issues_closed_count": 0,
                "stale_prs_closed": 0,
                "baseline_open_prs": None,
                "baseline_open_issues": None
            }
        
        self.memory["open_count_metrics"]["snapshots"].append(snapshot)
        self.memory["open_count_metrics"]["open_pr_trend"].append(open_prs)
        self.memory["open_count_metrics"]["open_issue_trend"].append(open_issues)
        
        # Set baseline if first measurement
        if self.memory["open_count_metrics"]["baseline_open_prs"] is None:
            self.memory["open_count_metrics"]["baseline_open_prs"] = open_prs
        if self.memory["open_count_metrics"]["baseline_open_issues"] is None:
            self.memory["open_count_metrics"]["baseline_open_issues"] = open_issues
        
        # Keep last 100 snapshots
        if len(self.memory["open_count_metrics"]["snapshots"]) > 100:
            self.memory["open_count_metrics"]["snapshots"] = \
                self.memory["open_count_metrics"]["snapshots"][-100:]
            self.memory["open_count_metrics"]["open_pr_trend"] = \
                self.memory["open_count_metrics"]["open_pr_trend"][-100:]
            self.memory["open_count_metrics"]["open_issue_trend"] = \
                self.memory["open_count_metrics"]["open_issue_trend"][-100:]
    
    def record_pr_closed(self, pr_number: int, created_at: str, closed_at: str = None, 
                        is_stale: bool = False):
        """
        Record a PR being closed and calculate cycle time.
        
        Args:
            pr_number: PR number
            created_at: ISO timestamp when PR was created
            closed_at: ISO timestamp when PR was closed (defaults to now)
            is_stale: Whether this was a stale PR proactively closed
        """
        if closed_at is None:
            closed_at = datetime.utcnow().isoformat()
        
        # Ensure keys exist
        if "cycle_time_metrics" not in self.memory:
            self.memory["cycle_time_metrics"] = {
                "pr_cycle_times": [],
                "issue_cycle_times": [],
                "average_pr_cycle_time_hours": 0,
                "average_issue_cycle_time_hours": 0,
                "cycle_time_trend": []
            }
        
        if "open_count_metrics" not in self.memory:
            self.memory["open_count_metrics"] = {
                "snapshots": [],
                "open_pr_trend": [],
                "open_issue_trend": [],
                "prs_closed_count": 0,
                "issues_closed_count": 0,
                "stale_prs_closed": 0,
                "baseline_open_prs": None,
                "baseline_open_issues": None
            }
        
        # Calculate cycle time in hours
        try:
            created = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            closed = datetime.fromisoformat(closed_at.replace('Z', '+00:00'))
            duration_hours = (closed - created).total_seconds() / 3600
        except (ValueError, TypeError, AttributeError) as e:
            print(f"Warning: Could not parse timestamps for PR {pr_number}: {e}")
            duration_hours = 0
        
        # Record cycle time
        cycle_record = {
            "pr_number": pr_number,
            "created_at": created_at,
            "closed_at": closed_at,
            "duration_hours": duration_hours,
            "is_stale": is_stale
        }
        
        self.memory["cycle_time_metrics"]["pr_cycle_times"].append(cycle_record)
        
        # Update counts
        self.memory["open_count_metrics"]["prs_closed_count"] += 1
        if is_stale:
            self.memory["open_count_metrics"]["stale_prs_closed"] += 1
        
        # Recalculate average (last 50 PRs)
        recent_cycles = [
            r["duration_hours"] 
            for r in self.memory["cycle_time_metrics"]["pr_cycle_times"][-50:]
            if r["duration_hours"] > 0
        ]
        if recent_cycles:
            self.memory["cycle_time_metrics"]["average_pr_cycle_time_hours"] = \
                sum(recent_cycles) / len(recent_cycles)
        
        # Keep last 100
        if len(self.memory["cycle_time_metrics"]["pr_cycle_times"]) > 100:
            self.memory["cycle_time_metrics"]["pr_cycle_times"] = \
                self.memory["cycle_time_metrics"]["pr_cycle_times"][-100:]
    
    def record_issue_closed(self, issue_number: int, created_at: str, closed_at: str = None):
        """
        Record an issue being closed and calculate cycle time.
        
        Args:
            issue_number: Issue number
            created_at: ISO timestamp when issue was created
            closed_at: ISO timestamp when issue was closed (defaults to now)
        """
        if closed_at is None:
            closed_at = datetime.utcnow().isoformat()
        
        # Ensure keys exist
        if "cycle_time_metrics" not in self.memory:
            self.memory["cycle_time_metrics"] = {
                "pr_cycle_times": [],
                "issue_cycle_times": [],
                "average_pr_cycle_time_hours": 0,
                "average_issue_cycle_time_hours": 0,
                "cycle_time_trend": []
            }
        
        if "open_count_metrics" not in self.memory:
            self.memory["open_count_metrics"] = {
                "snapshots": [],
                "open_pr_trend": [],
                "open_issue_trend": [],
                "prs_closed_count": 0,
                "issues_closed_count": 0,
                "stale_prs_closed": 0,
                "baseline_open_prs": None,
                "baseline_open_issues": None
            }
        
        # Calculate cycle time in hours
        try:
            created = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            closed = datetime.fromisoformat(closed_at.replace('Z', '+00:00'))
            duration_hours = (closed - created).total_seconds() / 3600
        except (ValueError, TypeError, AttributeError) as e:
            print(f"Warning: Could not parse timestamps for issue {issue_number}: {e}")
            duration_hours = 0
        
        # Record cycle time
        cycle_record = {
            "issue_number": issue_number,
            "created_at": created_at,
            "closed_at": closed_at,
            "duration_hours": duration_hours
        }
        
        self.memory["cycle_time_metrics"]["issue_cycle_times"].append(cycle_record)
        self.memory["open_count_metrics"]["issues_closed_count"] += 1
        
        # Recalculate average (last 50 issues)
        recent_cycles = [
            r["duration_hours"] 
            for r in self.memory["cycle_time_metrics"]["issue_cycle_times"][-50:]
            if r["duration_hours"] > 0
        ]
        if recent_cycles:
            self.memory["cycle_time_metrics"]["average_issue_cycle_time_hours"] = \
                sum(recent_cycles) / len(recent_cycles)
        
        # Keep last 100
        if len(self.memory["cycle_time_metrics"]["issue_cycle_times"]) > 100:
            self.memory["cycle_time_metrics"]["issue_cycle_times"] = \
                self.memory["cycle_time_metrics"]["issue_cycle_times"][-100:]
    
    def calculate_success_score(self) -> float:
        """
        Calculate overall success score based on cycle time and open count reduction.
        
        Score components:
        1. Cycle Time Score (40%): Lower average cycle time = higher score
        2. Reduction Score (40%): More reduction in open counts = higher score  
        3. Proactive Cleanup Score (20%): More stale PRs closed = higher score
        
        Returns:
            Score from 0-100, where 100 is best
        """
        # Ensure keys exist
        if "cycle_time_metrics" not in self.memory:
            self.memory["cycle_time_metrics"] = {
                "pr_cycle_times": [],
                "issue_cycle_times": [],
                "average_pr_cycle_time_hours": 0,
                "average_issue_cycle_time_hours": 0,
                "cycle_time_trend": []
            }
        
        if "open_count_metrics" not in self.memory:
            self.memory["open_count_metrics"] = {
                "snapshots": [],
                "open_pr_trend": [],
                "open_issue_trend": [],
                "prs_closed_count": 0,
                "issues_closed_count": 0,
                "stale_prs_closed": 0,
                "baseline_open_prs": None,
                "baseline_open_issues": None
            }
        
        if "success_score" not in self.memory:
            self.memory["success_score"] = {
                "current_score": 0,
                "score_history": [],
                "factors": {
                    "cycle_time_score": 0,
                    "reduction_score": 0,
                    "proactive_cleanup_score": 0
                }
            }
        
        # 1. Cycle Time Score (lower is better)
        avg_pr_cycle = self.memory["cycle_time_metrics"]["average_pr_cycle_time_hours"]
        avg_issue_cycle = self.memory["cycle_time_metrics"]["average_issue_cycle_time_hours"]
        
        # Target: 24 hours for PRs, 48 hours for issues
        pr_target = 24
        issue_target = 48
        
        pr_cycle_score = max(0, 100 - (avg_pr_cycle / pr_target * 100)) if avg_pr_cycle > 0 else 50
        issue_cycle_score = max(0, 100 - (avg_issue_cycle / issue_target * 100)) if avg_issue_cycle > 0 else 50
        cycle_time_score = (pr_cycle_score + issue_cycle_score) / 2
        
        # 2. Reduction Score (more reduction is better)
        baseline_prs = self.memory["open_count_metrics"].get("baseline_open_prs", 0)
        baseline_issues = self.memory["open_count_metrics"].get("baseline_open_issues", 0)
        
        current_prs = self.memory["open_count_metrics"]["open_pr_trend"][-1] if self.memory["open_count_metrics"]["open_pr_trend"] else baseline_prs
        current_issues = self.memory["open_count_metrics"]["open_issue_trend"][-1] if self.memory["open_count_metrics"]["open_issue_trend"] else baseline_issues
        
        if baseline_prs and baseline_prs > 0:
            pr_reduction_pct = ((baseline_prs - current_prs) / baseline_prs) * 100
        else:
            pr_reduction_pct = 0
        
        if baseline_issues and baseline_issues > 0:
            issue_reduction_pct = ((baseline_issues - current_issues) / baseline_issues) * 100
        else:
            issue_reduction_pct = 0
        
        # Score: 50% reduction = 100 points, -50% (increase) = 0 points
        reduction_score = max(0, min(100, 50 + pr_reduction_pct + issue_reduction_pct))
        
        # 3. Proactive Cleanup Score
        stale_closed = self.memory["open_count_metrics"]["stale_prs_closed"]
        total_closed = self.memory["open_count_metrics"]["prs_closed_count"]
        
        if total_closed > 0:
            proactive_rate = (stale_closed / total_closed) * 100
            proactive_cleanup_score = min(100, proactive_rate * 5)  # 20% stale = 100 points
        else:
            proactive_cleanup_score = 0
        
        # Weighted average
        overall_score = (
            cycle_time_score * 0.4 +
            reduction_score * 0.4 +
            proactive_cleanup_score * 0.2
        )
        
        # Update memory
        self.memory["success_score"]["current_score"] = overall_score
        self.memory["success_score"]["factors"] = {
            "cycle_time_score": cycle_time_score,
            "reduction_score": reduction_score,
            "proactive_cleanup_score": proactive_cleanup_score
        }
        
        self.memory["success_score"]["score_history"].append({
            "timestamp": datetime.utcnow().isoformat(),
            "score": overall_score,
            "factors": self.memory["success_score"]["factors"].copy()
        })
        
        # Keep last 50 scores
        if len(self.memory["success_score"]["score_history"]) > 50:
            self.memory["success_score"]["score_history"] = \
                self.memory["success_score"]["score_history"][-50:]
        
        return overall_score
    
    def get_success_summary(self) -> str:
        """Get a summary of success metrics."""
        score = self.calculate_success_score()
        
        cycle = self.memory.get("cycle_time_metrics", {})
        counts = self.memory.get("open_count_metrics", {})
        factors = self.memory.get("success_score", {}).get("factors", {})
        
        avg_pr_cycle = cycle.get("average_pr_cycle_time_hours", 0)
        avg_issue_cycle = cycle.get("average_issue_cycle_time_hours", 0)
        
        baseline_prs = counts.get("baseline_open_prs") or 0
        current_prs = counts.get("open_pr_trend", [baseline_prs])[-1] if counts.get("open_pr_trend") else baseline_prs
        baseline_issues = counts.get("baseline_open_issues") or 0
        current_issues = counts.get("open_issue_trend", [baseline_issues])[-1] if counts.get("open_issue_trend") else baseline_issues
        
        stale_closed = counts.get("stale_prs_closed", 0)
        total_closed = counts.get("prs_closed_count", 0)
        
        # Handle None values
        pr_delta = (current_prs - baseline_prs) if (current_prs is not None and baseline_prs is not None) else 0
        issue_delta = (current_issues - baseline_issues) if (current_issues is not None and baseline_issues is not None) else 0
        
        return f"""
## 🎯 Success Metrics Summary

**Overall Success Score: {score:.1f}/100**

### Cycle Time Performance (Target: 24h PRs, 48h issues)
- Average PR cycle time: {avg_pr_cycle:.1f} hours
- Average issue cycle time: {avg_issue_cycle:.1f} hours
- Cycle Time Score: {factors.get('cycle_time_score', 0):.1f}/100

### Open Count Reduction (Target: -50%)
- PRs: {baseline_prs} → {current_prs} ({pr_delta:+d})
- Issues: {baseline_issues} → {current_issues} ({issue_delta:+d})
- Reduction Score: {factors.get('reduction_score', 0):.1f}/100

### Proactive Cleanup
- Stale PRs closed: {stale_closed}/{total_closed}
- Proactive rate: {(stale_closed/total_closed*100) if total_closed > 0 else 0:.1f}%
- Cleanup Score: {factors.get('proactive_cleanup_score', 0):.1f}/100
"""
    
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
    
    elif command == "success":
        print(memory.get_success_summary())
    
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
        print("Available commands: summary, success, trends, agent, tech-lead, patterns, context")
        sys.exit(1)


if __name__ == "__main__":
    main()
