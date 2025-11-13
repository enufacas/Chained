#!/usr/bin/env python3
"""
Mentor Assignment Tool for Chained Agent Mentorship System

Matches newly spawned agents with Hall of Fame mentors to enable knowledge transfer
and accelerate learning in the autonomous AI ecosystem.

Features:
- Intelligent mentor-mentee matching based on specialization
- Capacity management for mentors
- Cross-specialization fallback matching
- Mentorship registry tracking
- Integration with agent spawner workflow

Usage:
    python assign-mentor.py <agent_id> [--specialization SPEC] [--verbose]
    python assign-mentor.py --check-capacity <mentor_id>
    python assign-mentor.py --list-available-mentors
"""

import json
import os
import sys
import argparse
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict


# Constants
REGISTRY_FILE = Path(".github/agent-system/registry.json")
MENTORSHIP_REGISTRY = Path(".github/agent-system/mentorship_registry.json")
KNOWLEDGE_TEMPLATES_DIR = Path(".github/agent-system/templates/knowledge")


@dataclass
class MentorshipAssignment:
    """Represents a mentor-mentee assignment"""
    mentee_id: str
    mentee_name: str
    mentee_specialization: str
    mentor_id: str
    mentor_name: str
    mentor_specialization: str
    assigned_at: str
    matching_type: str  # "exact" or "cross-specialization"
    status: str = "active"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)


class MentorAssigner:
    """Handles mentor-mentee matching and assignment"""
    
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
            self._log("Mentorship registry not found, creating new one", "WARNING")
            return {
                "version": "1.0.0",
                "active_mentorships": [],
                "completed_mentorships": [],
                "mentor_capacity": {},
                "mentorship_metrics": {
                    "total_mentorships": 0,
                    "active_mentorships": 0,
                    "completed_mentorships": 0,
                    "success_rate": 0.0,
                    "avg_mentee_improvement": 0.0
                },
                "config": {
                    "max_mentees_per_mentor": 3,
                    "mentorship_duration_days": 14,
                    "success_threshold_improvement": 0.15,
                    "hall_of_fame_mentor_requirement": 0.85
                },
                "last_updated": None
            }
        
        with open(MENTORSHIP_REGISTRY, 'r') as f:
            return json.load(f)
    
    def _save_mentorship_registry(self):
        """Save mentorship registry"""
        self.mentorship_registry['last_updated'] = datetime.now(timezone.utc).isoformat()
        
        # Ensure directory exists
        MENTORSHIP_REGISTRY.parent.mkdir(parents=True, exist_ok=True)
        
        with open(MENTORSHIP_REGISTRY, 'w') as f:
            json.dump(self.mentorship_registry, f, indent=2)
        
        self._log(f"Saved mentorship registry to {MENTORSHIP_REGISTRY}")
    
    def get_hall_of_fame_mentors(self) -> List[Dict[str, Any]]:
        """Get all Hall of Fame agents eligible to be mentors"""
        hall_of_fame = self.registry.get('hall_of_fame', [])
        
        # Filter for agents with score >= 85%
        config = self.mentorship_registry.get('config', {})
        threshold = config.get('hall_of_fame_mentor_requirement', 0.85)
        
        eligible_mentors = [
            agent for agent in hall_of_fame
            if agent.get('metrics', {}).get('overall_score', 0) >= threshold
        ]
        
        self._log(f"Found {len(eligible_mentors)} eligible Hall of Fame mentors")
        return eligible_mentors
    
    def get_mentor_capacity(self, mentor_id: str) -> Tuple[int, int]:
        """
        Get current mentee count and max capacity for a mentor
        Returns: (current_mentees, max_mentees)
        """
        config = self.mentorship_registry.get('config', {})
        max_capacity = config.get('max_mentees_per_mentor', 3)
        
        # Count active mentorships for this mentor
        active_mentorships = self.mentorship_registry.get('active_mentorships', [])
        current_count = sum(
            1 for m in active_mentorships 
            if m.get('mentor_id') == mentor_id and m.get('status') == 'active'
        )
        
        return (current_count, max_capacity)
    
    def find_mentor_by_specialization(
        self, 
        specialization: str,
        exact_match: bool = True
    ) -> Optional[Dict[str, Any]]:
        """
        Find an available mentor for the given specialization
        
        Args:
            specialization: The mentee's specialization
            exact_match: If True, only match same specialization; if False, any mentor
        
        Returns:
            Mentor agent dict or None if no mentor available
        """
        mentors = self.get_hall_of_fame_mentors()
        
        if not mentors:
            self._log("No Hall of Fame mentors available", "WARNING")
            return None
        
        # Try to find exact specialization match first
        if exact_match:
            matching_mentors = [
                m for m in mentors 
                if m.get('specialization') == specialization
            ]
        else:
            matching_mentors = mentors
        
        # Filter by capacity
        available_mentors = []
        for mentor in matching_mentors:
            current, max_capacity = self.get_mentor_capacity(mentor['id'])
            if current < max_capacity:
                available_mentors.append(mentor)
        
        if not available_mentors:
            self._log(
                f"No available mentors with capacity for {specialization}", 
                "WARNING"
            )
            return None
        
        # Select mentor with lowest current mentee count (load balancing)
        best_mentor = min(
            available_mentors,
            key=lambda m: self.get_mentor_capacity(m['id'])[0]
        )
        
        self._log(f"Selected mentor: {best_mentor.get('name')} ({best_mentor['id']})")
        return best_mentor
    
    def assign_mentor(
        self, 
        mentee_id: str,
        specialization: Optional[str] = None
    ) -> Optional[MentorshipAssignment]:
        """
        Assign a mentor to a new agent
        
        Args:
            mentee_id: The new agent's ID
            specialization: The agent's specialization (auto-detected if not provided)
        
        Returns:
            MentorshipAssignment or None if no mentor available
        """
        # Find mentee in registry
        mentee = None
        for agent in self.registry.get('agents', []):
            if agent['id'] == mentee_id:
                mentee = agent
                break
        
        if not mentee:
            self._log(f"Mentee {mentee_id} not found in registry", "ERROR")
            return None
        
        # Get specialization
        if not specialization:
            specialization = mentee.get('specialization')
        
        if not specialization:
            self._log(f"No specialization found for mentee {mentee_id}", "ERROR")
            return None
        
        self._log(f"Assigning mentor for {mentee.get('name')} ({specialization})")
        
        # Try exact match first
        mentor = self.find_mentor_by_specialization(specialization, exact_match=True)
        matching_type = "exact"
        
        # Fall back to cross-specialization if needed
        if not mentor:
            self._log("No exact match found, trying cross-specialization match")
            mentor = self.find_mentor_by_specialization(specialization, exact_match=False)
            matching_type = "cross-specialization"
        
        if not mentor:
            self._log("No mentor available for assignment", "WARNING")
            return None
        
        # Create mentorship assignment
        assignment = MentorshipAssignment(
            mentee_id=mentee_id,
            mentee_name=mentee.get('name', 'Unknown'),
            mentee_specialization=specialization,
            mentor_id=mentor['id'],
            mentor_name=mentor.get('name', 'Unknown'),
            mentor_specialization=mentor.get('specialization', 'Unknown'),
            assigned_at=datetime.now(timezone.utc).isoformat(),
            matching_type=matching_type,
            status="active"
        )
        
        # Add to active mentorships
        self.mentorship_registry['active_mentorships'].append(assignment.to_dict())
        
        # Update metrics
        metrics = self.mentorship_registry['mentorship_metrics']
        metrics['total_mentorships'] = metrics.get('total_mentorships', 0) + 1
        metrics['active_mentorships'] = len(self.mentorship_registry['active_mentorships'])
        
        # Save registry
        self._save_mentorship_registry()
        
        self._log(
            f"✅ Assigned mentor {mentor.get('name')} to {mentee.get('name')} "
            f"({matching_type} match)"
        )
        
        return assignment
    
    def list_available_mentors(self) -> List[Dict[str, Any]]:
        """List all available mentors with their capacity"""
        mentors = self.get_hall_of_fame_mentors()
        
        result = []
        for mentor in mentors:
            current, max_capacity = self.get_mentor_capacity(mentor['id'])
            result.append({
                'id': mentor['id'],
                'name': mentor.get('name', 'Unknown'),
                'specialization': mentor.get('specialization', 'Unknown'),
                'score': mentor.get('metrics', {}).get('overall_score', 0),
                'current_mentees': current,
                'max_mentees': max_capacity,
                'available': current < max_capacity
            })
        
        return result
    
    def check_capacity(self, mentor_id: str) -> Dict[str, Any]:
        """Check capacity for a specific mentor"""
        current, max_capacity = self.get_mentor_capacity(mentor_id)
        
        # Find mentor details
        mentors = self.get_hall_of_fame_mentors()
        mentor = next((m for m in mentors if m['id'] == mentor_id), None)
        
        if not mentor:
            return {
                'error': f"Mentor {mentor_id} not found in Hall of Fame"
            }
        
        return {
            'mentor_id': mentor_id,
            'mentor_name': mentor.get('name', 'Unknown'),
            'specialization': mentor.get('specialization', 'Unknown'),
            'current_mentees': current,
            'max_mentees': max_capacity,
            'available_slots': max_capacity - current,
            'at_capacity': current >= max_capacity
        }


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Assign mentors to newly spawned agents",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Assign mentor to a new agent
  python assign-mentor.py agent-1234567890
  
  # Assign mentor with explicit specialization
  python assign-mentor.py agent-1234567890 --specialization engineer-master
  
  # Check mentor capacity
  python assign-mentor.py --check-capacity agent-0987654321
  
  # List all available mentors
  python assign-mentor.py --list-available-mentors
        """
    )
    
    parser.add_argument(
        'agent_id',
        nargs='?',
        help='Agent ID to assign a mentor to'
    )
    
    parser.add_argument(
        '--specialization',
        help='Force specific specialization for matching'
    )
    
    parser.add_argument(
        '--check-capacity',
        metavar='MENTOR_ID',
        help='Check mentorship capacity for a specific mentor'
    )
    
    parser.add_argument(
        '--list-available-mentors',
        action='store_true',
        help='List all available mentors with capacity info'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output in JSON format'
    )
    
    args = parser.parse_args()
    
    try:
        assigner = MentorAssigner(verbose=args.verbose)
        
        # Handle different commands
        if args.list_available_mentors:
            mentors = assigner.list_available_mentors()
            if args.json:
                print(json.dumps(mentors, indent=2))
            else:
                print("\n🎓 Available Mentors:\n")
                for mentor in mentors:
                    status = "✅ Available" if mentor['available'] else "⛔ At Capacity"
                    print(f"  {status} {mentor['name']} ({mentor['specialization']})")
                    print(f"    Score: {mentor['score']*100:.1f}%")
                    print(f"    Capacity: {mentor['current_mentees']}/{mentor['max_mentees']}")
                    print()
        
        elif args.check_capacity:
            capacity = assigner.check_capacity(args.check_capacity)
            if args.json:
                print(json.dumps(capacity, indent=2))
            else:
                if 'error' in capacity:
                    print(f"❌ {capacity['error']}")
                    sys.exit(1)
                else:
                    print(f"\n📊 Mentor Capacity for {capacity['mentor_name']}:\n")
                    print(f"  Specialization: {capacity['specialization']}")
                    print(f"  Current Mentees: {capacity['current_mentees']}")
                    print(f"  Max Mentees: {capacity['max_mentees']}")
                    print(f"  Available Slots: {capacity['available_slots']}")
                    print(f"  Status: {'⛔ At Capacity' if capacity['at_capacity'] else '✅ Available'}")
        
        elif args.agent_id:
            assignment = assigner.assign_mentor(
                args.agent_id,
                specialization=args.specialization
            )
            
            if assignment:
                if args.json:
                    print(json.dumps(assignment.to_dict(), indent=2))
                else:
                    print(f"\n✅ Mentorship Assigned!\n")
                    print(f"  Mentee: {assignment.mentee_name} ({assignment.mentee_specialization})")
                    print(f"  Mentor: {assignment.mentor_name} ({assignment.mentor_specialization})")
                    print(f"  Match Type: {assignment.matching_type}")
                    print(f"  Assigned At: {assignment.assigned_at}")
                    print()
                sys.exit(0)
            else:
                if not args.json:
                    print("\n⚠️  No mentor available for assignment")
                    print("   Mentee will proceed without a mentor")
                sys.exit(1)
        
        else:
            parser.print_help()
            sys.exit(1)
    
    except Exception as e:
        if args.json:
            print(json.dumps({'error': str(e)}))
        else:
            print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
