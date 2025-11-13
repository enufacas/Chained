#!/usr/bin/env python3
"""
Mentorship Evaluation Tool

Evaluates mentorship effectiveness by tracking mentee performance improvements,
comparing mentored vs non-mentored agents, and calculating mentor success rates.

Features:
- Mentee performance tracking over time
- Mentor effectiveness scoring
- Comparative analysis (mentored vs non-mentored)
- Mentorship outcome evaluation
- Integration with agent evaluation system

Usage:
    python evaluate-mentorship.py [--mentorship-id ID] [--evaluate-all]
    python evaluate-mentorship.py --mentor-effectiveness <mentor_id>
    python evaluate-mentorship.py --mentee-progress <mentee_id>
"""

import json
import os
import sys
import argparse
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict


# Constants
REGISTRY_FILE = Path(".github/agent-system/registry.json")
MENTORSHIP_REGISTRY = Path(".github/agent-system/mentorship_registry.json")


@dataclass
class MentorshipOutcome:
    """Represents the outcome of a completed mentorship"""
    mentorship_id: str
    mentor_id: str
    mentee_id: str
    
    # Initial metrics (at start of mentorship)
    initial_score: float
    initial_issues_resolved: int
    initial_prs_merged: int
    
    # Final metrics (at end of mentorship)
    final_score: float
    final_issues_resolved: int
    final_prs_merged: int
    
    # Calculated improvements
    score_improvement: float
    issues_improvement: int
    prs_improvement: int
    
    # Evaluation
    success: bool
    completion_date: str
    duration_days: int
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class MentorshipEvaluator:
    """Evaluates mentorship effectiveness and outcomes"""
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.registry = self._load_registry()
        self.mentorship_registry = self._load_mentorship_registry()
    
    def _log(self, message: str, level: str = "INFO"):
        """Log message if verbose mode is enabled"""
        if self.verbose:
            print(f"[{level}] {message}")
    
    def _load_registry(self) -> Dict[str, Any]:
        """Load agent registry"""
        if not REGISTRY_FILE.exists():
            raise FileNotFoundError(f"Registry file not found: {REGISTRY_FILE}")
        
        with open(REGISTRY_FILE, 'r') as f:
            return json.load(f)
    
    def _load_mentorship_registry(self) -> Dict[str, Any]:
        """Load mentorship registry"""
        if not MENTORSHIP_REGISTRY.exists():
            self._log("Mentorship registry not found", "WARNING")
            return {
                "active_mentorships": [],
                "completed_mentorships": [],
                "mentorship_metrics": {}
            }
        
        with open(MENTORSHIP_REGISTRY, 'r') as f:
            return json.load(f)
    
    def _save_mentorship_registry(self):
        """Save mentorship registry"""
        self.mentorship_registry['last_updated'] = datetime.now(timezone.utc).isoformat()
        
        with open(MENTORSHIP_REGISTRY, 'w') as f:
            json.dump(self.mentorship_registry, f, indent=2)
        
        self._log(f"Saved mentorship registry")
    
    def get_agent_metrics(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get current metrics for an agent"""
        # Check active agents
        for agent in self.registry.get('agents', []):
            if agent['id'] == agent_id:
                return agent.get('metrics', {})
        
        # Check Hall of Fame
        for agent in self.registry.get('hall_of_fame', []):
            if agent['id'] == agent_id:
                return agent.get('metrics', {})
        
        return None
    
    def calculate_mentorship_duration(
        self, 
        start_date: str,
        end_date: Optional[str] = None
    ) -> int:
        """Calculate mentorship duration in days"""
        start = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        
        if end_date:
            end = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        else:
            end = datetime.now(timezone.utc)
        
        return (end - start).days
    
    def evaluate_mentorship(
        self, 
        mentorship: Dict[str, Any]
    ) -> Optional[MentorshipOutcome]:
        """Evaluate a single mentorship"""
        mentee_id = mentorship.get('mentee_id')
        mentor_id = mentorship.get('mentor_id')
        
        self._log(f"Evaluating mentorship: {mentor_id} → {mentee_id}")
        
        # Get initial metrics (stored in mentorship record)
        initial_metrics = mentorship.get('initial_metrics', {})
        initial_score = initial_metrics.get('overall_score', 0)
        initial_issues = initial_metrics.get('issues_resolved', 0)
        initial_prs = initial_metrics.get('prs_merged', 0)
        
        # Get current metrics
        current_metrics = self.get_agent_metrics(mentee_id)
        
        if not current_metrics:
            self._log(f"Could not find current metrics for {mentee_id}", "WARNING")
            return None
        
        final_score = current_metrics.get('overall_score', 0)
        final_issues = current_metrics.get('issues_resolved', 0)
        final_prs = current_metrics.get('prs_merged', 0)
        
        # Calculate improvements
        score_improvement = final_score - initial_score
        issues_improvement = final_issues - initial_issues
        prs_improvement = final_prs - initial_prs
        
        # Determine success
        config = self.mentorship_registry.get('config', {})
        success_threshold = config.get('success_threshold_improvement', 0.15)
        success = score_improvement >= success_threshold
        
        # Calculate duration
        start_date = mentorship.get('assigned_at')
        duration = self.calculate_mentorship_duration(start_date)
        
        outcome = MentorshipOutcome(
            mentorship_id=f"{mentor_id}_{mentee_id}",
            mentor_id=mentor_id,
            mentee_id=mentee_id,
            initial_score=initial_score,
            initial_issues_resolved=initial_issues,
            initial_prs_merged=initial_prs,
            final_score=final_score,
            final_issues_resolved=final_issues,
            final_prs_merged=final_prs,
            score_improvement=score_improvement,
            issues_improvement=issues_improvement,
            prs_improvement=prs_improvement,
            success=success,
            completion_date=datetime.now(timezone.utc).isoformat(),
            duration_days=duration
        )
        
        return outcome
    
    def complete_mentorship(
        self, 
        mentorship: Dict[str, Any],
        outcome: MentorshipOutcome
    ):
        """Mark mentorship as completed and record outcome"""
        # Update status
        mentorship['status'] = 'completed'
        mentorship['completed_at'] = outcome.completion_date
        mentorship['outcome'] = outcome.to_dict()
        
        # Move from active to completed
        active = self.mentorship_registry.get('active_mentorships', [])
        completed = self.mentorship_registry.get('completed_mentorships', [])
        
        # Remove from active
        self.mentorship_registry['active_mentorships'] = [
            m for m in active if m.get('mentee_id') != mentorship['mentee_id']
        ]
        
        # Add to completed
        completed.append(mentorship)
        self.mentorship_registry['completed_mentorships'] = completed
        
        self._log(f"Completed mentorship: {outcome.mentorship_id}")
    
    def calculate_mentor_effectiveness(
        self, 
        mentor_id: str
    ) -> Dict[str, Any]:
        """Calculate effectiveness score for a mentor"""
        completed = self.mentorship_registry.get('completed_mentorships', [])
        
        # Filter mentorships for this mentor
        mentor_mentorships = [
            m for m in completed if m.get('mentor_id') == mentor_id
        ]
        
        if not mentor_mentorships:
            return {
                'mentor_id': mentor_id,
                'total_mentorships': 0,
                'successful_mentorships': 0,
                'success_rate': 0.0,
                'avg_score_improvement': 0.0,
                'avg_duration_days': 0
            }
        
        # Calculate statistics
        total = len(mentor_mentorships)
        successful = sum(
            1 for m in mentor_mentorships 
            if m.get('outcome', {}).get('success', False)
        )
        
        score_improvements = [
            m.get('outcome', {}).get('score_improvement', 0)
            for m in mentor_mentorships
        ]
        avg_improvement = sum(score_improvements) / len(score_improvements) if score_improvements else 0
        
        durations = [
            m.get('outcome', {}).get('duration_days', 0)
            for m in mentor_mentorships
        ]
        avg_duration = sum(durations) / len(durations) if durations else 0
        
        return {
            'mentor_id': mentor_id,
            'total_mentorships': total,
            'successful_mentorships': successful,
            'success_rate': successful / total if total > 0 else 0.0,
            'avg_score_improvement': avg_improvement,
            'avg_duration_days': avg_duration
        }
    
    def track_mentee_progress(
        self, 
        mentee_id: str
    ) -> Optional[Dict[str, Any]]:
        """Track progress of a specific mentee"""
        # Find mentorship
        active = self.mentorship_registry.get('active_mentorships', [])
        completed = self.mentorship_registry.get('completed_mentorships', [])
        
        mentorship = None
        status = None
        
        for m in active:
            if m.get('mentee_id') == mentee_id:
                mentorship = m
                status = 'active'
                break
        
        if not mentorship:
            for m in completed:
                if m.get('mentee_id') == mentee_id:
                    mentorship = m
                    status = 'completed'
                    break
        
        if not mentorship:
            self._log(f"No mentorship found for {mentee_id}", "WARNING")
            return None
        
        # Get current metrics
        current_metrics = self.get_agent_metrics(mentee_id)
        if not current_metrics:
            return None
        
        # Calculate progress
        initial_metrics = mentorship.get('initial_metrics', {})
        initial_score = initial_metrics.get('overall_score', 0)
        current_score = current_metrics.get('overall_score', 0)
        
        duration = self.calculate_mentorship_duration(mentorship.get('assigned_at'))
        
        return {
            'mentee_id': mentee_id,
            'mentee_name': mentorship.get('mentee_name'),
            'mentor_id': mentorship.get('mentor_id'),
            'mentor_name': mentorship.get('mentor_name'),
            'status': status,
            'days_in_mentorship': duration,
            'initial_score': initial_score,
            'current_score': current_score,
            'score_improvement': current_score - initial_score,
            'issues_resolved': current_metrics.get('issues_resolved', 0),
            'prs_merged': current_metrics.get('prs_merged', 0)
        }
    
    def evaluate_all_active_mentorships(self) -> List[MentorshipOutcome]:
        """Evaluate all active mentorships that are ready for completion"""
        active = self.mentorship_registry.get('active_mentorships', [])
        config = self.mentorship_registry.get('config', {})
        mentorship_duration = config.get('mentorship_duration_days', 14)
        
        outcomes = []
        
        for mentorship in active:
            # Check if mentorship has been active long enough
            duration = self.calculate_mentorship_duration(mentorship.get('assigned_at'))
            
            if duration >= mentorship_duration:
                outcome = self.evaluate_mentorship(mentorship)
                
                if outcome:
                    self.complete_mentorship(mentorship, outcome)
                    outcomes.append(outcome)
        
        # Update global metrics
        if outcomes:
            self._update_global_metrics()
        
        # Save changes
        if outcomes:
            self._save_mentorship_registry()
        
        return outcomes
    
    def _update_global_metrics(self):
        """Update global mentorship metrics"""
        completed = self.mentorship_registry.get('completed_mentorships', [])
        active = self.mentorship_registry.get('active_mentorships', [])
        
        total = len(completed)
        successful = sum(
            1 for m in completed 
            if m.get('outcome', {}).get('success', False)
        )
        
        if total > 0:
            improvements = [
                m.get('outcome', {}).get('score_improvement', 0)
                for m in completed
            ]
            avg_improvement = sum(improvements) / len(improvements)
        else:
            avg_improvement = 0.0
        
        metrics = {
            'total_mentorships': total,
            'active_mentorships': len(active),
            'completed_mentorships': total,
            'success_rate': successful / total if total > 0 else 0.0,
            'avg_mentee_improvement': avg_improvement
        }
        
        self.mentorship_registry['mentorship_metrics'] = metrics
        self._log(f"Updated global metrics: {metrics}")
    
    def generate_mentorship_report(self) -> Dict[str, Any]:
        """Generate comprehensive mentorship system report"""
        metrics = self.mentorship_registry.get('mentorship_metrics', {})
        active = self.mentorship_registry.get('active_mentorships', [])
        completed = self.mentorship_registry.get('completed_mentorships', [])
        
        # Get all unique mentors
        all_mentors = set()
        for m in active + completed:
            all_mentors.add(m.get('mentor_id'))
        
        # Calculate mentor effectiveness
        mentor_stats = {}
        for mentor_id in all_mentors:
            mentor_stats[mentor_id] = self.calculate_mentor_effectiveness(mentor_id)
        
        return {
            'overall_metrics': metrics,
            'active_mentorships': len(active),
            'completed_mentorships': len(completed),
            'mentor_statistics': mentor_stats,
            'report_generated_at': datetime.now(timezone.utc).isoformat()
        }


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Evaluate mentorship effectiveness",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Evaluate all active mentorships ready for completion
  python evaluate-mentorship.py --evaluate-all
  
  # Check mentor effectiveness
  python evaluate-mentorship.py --mentor-effectiveness agent-123
  
  # Track mentee progress
  python evaluate-mentorship.py --mentee-progress agent-456
  
  # Generate full report
  python evaluate-mentorship.py --report
        """
    )
    
    parser.add_argument(
        '--evaluate-all',
        action='store_true',
        help='Evaluate all active mentorships ready for completion'
    )
    
    parser.add_argument(
        '--mentor-effectiveness',
        metavar='MENTOR_ID',
        help='Calculate effectiveness for a specific mentor'
    )
    
    parser.add_argument(
        '--mentee-progress',
        metavar='MENTEE_ID',
        help='Track progress for a specific mentee'
    )
    
    parser.add_argument(
        '--report',
        action='store_true',
        help='Generate comprehensive mentorship report'
    )
    
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output in JSON format'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    try:
        evaluator = MentorshipEvaluator(verbose=args.verbose)
        
        if args.evaluate_all:
            outcomes = evaluator.evaluate_all_active_mentorships()
            
            if args.json:
                print(json.dumps([o.to_dict() for o in outcomes], indent=2))
            else:
                print(f"\n✅ Evaluated {len(outcomes)} mentorships\n")
                for outcome in outcomes:
                    status = "✅ Success" if outcome.success else "⚠️  Needs Improvement"
                    print(f"{status}: {outcome.mentee_id}")
                    print(f"  Score: {outcome.initial_score:.2f} → {outcome.final_score:.2f} "
                          f"({outcome.score_improvement:+.2f})")
                    print(f"  Duration: {outcome.duration_days} days")
                    print()
        
        elif args.mentor_effectiveness:
            stats = evaluator.calculate_mentor_effectiveness(args.mentor_effectiveness)
            
            if args.json:
                print(json.dumps(stats, indent=2))
            else:
                print(f"\n📊 Mentor Effectiveness: {stats['mentor_id']}\n")
                print(f"  Total Mentorships: {stats['total_mentorships']}")
                print(f"  Successful: {stats['successful_mentorships']}")
                print(f"  Success Rate: {stats['success_rate']*100:.1f}%")
                print(f"  Avg Improvement: {stats['avg_score_improvement']:+.2f}")
                print(f"  Avg Duration: {stats['avg_duration_days']:.0f} days")
                print()
        
        elif args.mentee_progress:
            progress = evaluator.track_mentee_progress(args.mentee_progress)
            
            if progress:
                if args.json:
                    print(json.dumps(progress, indent=2))
                else:
                    print(f"\n📈 Mentee Progress: {progress['mentee_name']}\n")
                    print(f"  Mentor: {progress['mentor_name']}")
                    print(f"  Status: {progress['status'].title()}")
                    print(f"  Days in Program: {progress['days_in_mentorship']}")
                    print(f"  Score: {progress['initial_score']:.2f} → {progress['current_score']:.2f} "
                          f"({progress['score_improvement']:+.2f})")
                    print(f"  Issues Resolved: {progress['issues_resolved']}")
                    print(f"  PRs Merged: {progress['prs_merged']}")
                    print()
            else:
                print(f"❌ No mentorship found for {args.mentee_progress}")
                sys.exit(1)
        
        elif args.report:
            report = evaluator.generate_mentorship_report()
            
            if args.json:
                print(json.dumps(report, indent=2))
            else:
                print("\n📊 Mentorship System Report\n")
                print("Overall Metrics:")
                metrics = report['overall_metrics']
                print(f"  Total Mentorships: {metrics.get('total_mentorships', 0)}")
                print(f"  Active: {metrics.get('active_mentorships', 0)}")
                print(f"  Completed: {metrics.get('completed_mentorships', 0)}")
                print(f"  Success Rate: {metrics.get('success_rate', 0)*100:.1f}%")
                print(f"  Avg Improvement: {metrics.get('avg_mentee_improvement', 0):+.2f}")
                print()
        
        else:
            parser.print_help()
            sys.exit(1)
    
    except Exception as e:
        if args.json:
            print(json.dumps({'error': str(e)}))
        else:
            print(f"❌ Error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
