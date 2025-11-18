#!/usr/bin/env python3
"""
Mentorship System Demo

Demonstrates the Agent Mentorship System in action with simulated scenarios.
Shows mentor assignment, knowledge transfer, and evaluation processes.

Usage:
    python demo-mentorship.py [--scenario <name>]
    python demo-mentorship.py --list-scenarios
"""

import json
import argparse
from pathlib import Path
from datetime import datetime, timezone, timedelta
from typing import Dict, Any


class MentorshipDemo:
    """Demonstrates mentorship system capabilities"""
    
    def __init__(self):
        self.registry_file = Path(".github/agent-system/registry.json")
        self.mentorship_registry = Path(".github/agent-system/mentorship_registry.json")
        self.hall_of_fame = Path(".github/agent-system/hall_of_fame.json")
    
    def print_header(self, title: str):
        """Print formatted header"""
        print("\n" + "="*70)
        print(f"  {title}")
        print("="*70 + "\n")
    
    def print_section(self, title: str):
        """Print formatted section"""
        print(f"\n{'─'*70}")
        print(f"  {title}")
        print(f"{'─'*70}\n")
    
    def scenario_new_agent_spawn(self):
        """Scenario 1: New agent spawned and assigned mentor"""
        self.print_header("📖 SCENARIO 1: New Agent Spawning with Mentor Assignment")
        
        print("A new agent has just been spawned in the system...")
        print()
        
        # Simulate new agent
        new_agent = {
            "id": "agent-demo-12345",
            "name": "NewBie",
            "human_name": "Newbie Agent",
            "specialization": "engineer-master",
            "spawned_at": datetime.now(timezone.utc).isoformat(),
            "metrics": {
                "overall_score": 0.25,
                "issues_resolved": 0,
                "prs_merged": 0,
                "code_quality_score": 0.3
            }
        }
        
        print(f"🆕 New Agent Created:")
        print(f"   Name: {new_agent['human_name']}")
        print(f"   Specialization: {new_agent['specialization']}")
        print(f"   Initial Score: {new_agent['metrics']['overall_score']*100:.0f}%")
        print()
        
        self.print_section("🔍 Step 1: Finding Available Mentors")
        
        print("Searching Hall of Fame for available mentors...")
        print()
        
        # Load Hall of Fame
        if self.hall_of_fame.exists():
            with open(self.hall_of_fame, 'r') as f:
                hof_agents = json.load(f)
            
            # Find matching mentors
            exact_matches = [
                agent for agent in hof_agents
                if agent['specialization'] == new_agent['specialization']
            ]
            
            print(f"✅ Found {len(exact_matches)} exact specialization matches:")
            for agent in exact_matches[:3]:
                print(f"   • {agent.get('human_name', 'Unknown')} ({agent['specialization']}) - Score: {agent['metrics']['overall_score']*100:.1f}%")
            
            if exact_matches:
                selected_mentor = exact_matches[0]
                print()
                print(f"🎯 Selected Mentor: {selected_mentor.get('human_name', 'Unknown')}")
                print(f"   Specialization: {selected_mentor['specialization']}")
                print(f"   Score: {selected_mentor['metrics']['overall_score']*100:.1f}%")
                print(f"   Match Type: exact")
        else:
            print("⚠️ Hall of Fame file not found")
            return
        
        self.print_section("📚 Step 2: Providing Knowledge Template")
        
        knowledge_template = f".github/agent-system/templates/knowledge/{selected_mentor['specialization']}_{selected_mentor['id']}.md"
        
        print(f"Knowledge Template: {knowledge_template}")
        print()
        print("The mentee receives:")
        print("  ✓ Core approach and methodology")
        print("  ✓ Success patterns with examples")
        print("  ✓ Recommended tools and practices")
        print("  ✓ Common pitfalls to avoid")
        print("  ✓ Quality standards (Code Quality: {:.0f}%)".format(
            selected_mentor['metrics'].get('code_quality_score', 0.5) * 100
        ))
        print("  ✓ 2-week learning path")
        print()
        
        self.print_section("📝 Step 3: Recording Mentorship")
        
        mentorship_record = {
            "mentee_id": new_agent['id'],
            "mentee_name": new_agent['name'],
            "mentee_specialization": new_agent['specialization'],
            "mentor_id": selected_mentor['id'],
            "mentor_name": selected_mentor.get('human_name', 'Unknown'),
            "mentor_specialization": selected_mentor['specialization'],
            "assigned_at": datetime.now(timezone.utc).isoformat(),
            "matching_type": "exact",
            "status": "active",
            "initial_metrics": {
                "score": new_agent['metrics']['overall_score'],
                "issues_resolved": new_agent['metrics']['issues_resolved'],
                "prs_merged": new_agent['metrics']['prs_merged']
            }
        }
        
        print("Mentorship Record Created:")
        print(f"   Mentee: {mentorship_record['mentee_name']} ({mentorship_record['mentee_specialization']})")
        print(f"   Mentor: {mentorship_record['mentor_name']} ({mentorship_record['mentor_specialization']})")
        print(f"   Started: {mentorship_record['assigned_at'][:10]}")
        print(f"   Initial Score: {mentorship_record['initial_metrics']['score']*100:.0f}%")
        print()
        
        print("✅ Mentorship successfully established!")
        print()
        print("Next Steps for Mentee:")
        print("  1. Study the knowledge template thoroughly")
        print("  2. Review mentor's past work for examples")
        print("  3. Start with small, focused issues")
        print("  4. Apply learned patterns consistently")
        print("  5. Request feedback and iterate")
        print()
    
    def scenario_mentorship_progress(self):
        """Scenario 2: Mentee making progress over 14 days"""
        self.print_header("📖 SCENARIO 2: Mentorship Progress Over 14 Days")
        
        print("Following a mentee's journey through the mentorship program...")
        print()
        
        # Simulate progress timeline
        timeline = [
            {
                "day": 0,
                "score": 0.25,
                "issues": 0,
                "prs": 0,
                "event": "Mentorship started"
            },
            {
                "day": 3,
                "score": 0.28,
                "issues": 1,
                "prs": 0,
                "event": "First issue attempted, studying patterns"
            },
            {
                "day": 7,
                "score": 0.35,
                "issues": 2,
                "prs": 1,
                "event": "First PR merged! Applying learned patterns"
            },
            {
                "day": 10,
                "score": 0.41,
                "issues": 4,
                "prs": 3,
                "event": "Consistent progress, good code quality"
            },
            {
                "day": 14,
                "score": 0.48,
                "issues": 6,
                "prs": 5,
                "event": "Mentorship evaluation"
            }
        ]
        
        print("Progress Timeline:")
        print()
        
        for entry in timeline:
            day_str = f"Day {entry['day']:2d}".ljust(8)
            score_str = f"{entry['score']*100:.0f}%".ljust(5)
            
            # Progress bar
            progress = int(entry['score'] * 40)
            bar = "█" * progress + "░" * (40 - progress)
            
            print(f"{day_str} {score_str} {bar}")
            print(f"         Issues: {entry['issues']} | PRs: {entry['prs']}")
            print(f"         📌 {entry['event']}")
            print()
        
        self.print_section("📊 Evaluation Results")
        
        initial_score = timeline[0]['score']
        final_score = timeline[-1]['score']
        improvement = final_score - initial_score
        improvement_pct = (improvement / initial_score) * 100
        
        print(f"Initial Score:  {initial_score*100:.0f}%")
        print(f"Final Score:    {final_score*100:.0f}%")
        print(f"Improvement:    +{improvement*100:.0f}% (absolute)")
        print(f"Improvement:    +{improvement_pct:.1f}% (relative)")
        print()
        
        # Determine success
        target_improvement = 0.15
        if improvement >= target_improvement:
            print("🎉 SUCCESS! Mentorship completed successfully")
            print(f"   Exceeded target improvement of {target_improvement*100:.0f}%")
            print()
            print("Outcomes:")
            print("  ✅ Mentee demonstrated significant improvement")
            print("  ✅ Applied mentor's patterns effectively")
            print("  ✅ Ready to work independently")
            print("  ✅ Mentor effectiveness score increased")
        else:
            print("⚠️ Needs More Time")
            print(f"   Target: {target_improvement*100:.0f}% improvement")
            print(f"   Achieved: {improvement*100:.0f}%")
            print()
            print("Recommendations:")
            print("  • Continue mentorship for another 7 days")
            print("  • Focus on specific areas needing improvement")
            print("  • Review knowledge template again")
        
        print()
    
    def scenario_mentor_effectiveness(self):
        """Scenario 3: Tracking mentor effectiveness"""
        self.print_header("📖 SCENARIO 3: Mentor Effectiveness Tracking")
        
        print("Analyzing a mentor's impact on their mentees...")
        print()
        
        # Simulate mentor with multiple mentees
        mentor_stats = {
            "mentor_id": "agent-hof-456",
            "mentor_name": "Expert Ada",
            "specialization": "coach-master",
            "score": 0.875,
            "mentees": [
                {
                    "name": "Learner Alpha",
                    "initial_score": 0.22,
                    "final_score": 0.42,
                    "improvement": 0.20,
                    "outcome": "success"
                },
                {
                    "name": "Learner Beta",
                    "initial_score": 0.28,
                    "final_score": 0.45,
                    "improvement": 0.17,
                    "outcome": "success"
                },
                {
                    "name": "Learner Gamma",
                    "initial_score": 0.25,
                    "final_score": 0.38,
                    "improvement": 0.13,
                    "outcome": "incomplete"
                }
            ]
        }
        
        print(f"👨‍🏫 Mentor: {mentor_stats['mentor_name']}")
        print(f"   Specialization: {mentor_stats['specialization']}")
        print(f"   Score: {mentor_stats['score']*100:.1f}%")
        print()
        
        self.print_section("📈 Mentee Outcomes")
        
        for i, mentee in enumerate(mentor_stats['mentees'], 1):
            print(f"{i}. {mentee['name']}")
            print(f"   Initial: {mentee['initial_score']*100:.0f}% → Final: {mentee['final_score']*100:.0f}%")
            print(f"   Improvement: +{mentee['improvement']*100:.0f}%")
            
            if mentee['outcome'] == 'success':
                print(f"   Status: ✅ Success")
            else:
                print(f"   Status: ⚠️ Needs improvement")
            print()
        
        self.print_section("🏆 Mentor Metrics")
        
        total_mentees = len(mentor_stats['mentees'])
        successes = sum(1 for m in mentor_stats['mentees'] if m['outcome'] == 'success')
        success_rate = (successes / total_mentees) * 100
        avg_improvement = sum(m['improvement'] for m in mentor_stats['mentees']) / total_mentees
        
        print(f"Total Mentees:         {total_mentees}")
        print(f"Successful:            {successes}/{total_mentees} ({success_rate:.0f}%)")
        print(f"Average Improvement:   +{avg_improvement*100:.1f}%")
        print()
        
        # Effectiveness visualization
        print("Effectiveness Rating:")
        effectiveness = int(success_rate / 5)
        bar = "★" * effectiveness + "☆" * (20 - effectiveness)
        print(f"  {bar} {success_rate:.0f}%")
        print()
        
        if success_rate >= 80:
            print("🌟 EXCEPTIONAL MENTOR")
            print("   Impact: Consistently excellent results")
            print("   Recognition: Top mentor in the system")
        elif success_rate >= 60:
            print("👍 GOOD MENTOR")
            print("   Impact: Positive influence on mentees")
            print("   Recognition: Reliable knowledge transfer")
        else:
            print("📚 DEVELOPING MENTOR")
            print("   Impact: Room for improvement in approach")
            print("   Recommendation: Refine knowledge templates")
        
        print()
    
    def scenario_system_overview(self):
        """Scenario 4: System-wide overview"""
        self.print_header("📖 SCENARIO 4: System-Wide Mentorship Overview")
        
        print("Current state of the mentorship system...")
        print()
        
        # Load actual system state
        try:
            with open(self.mentorship_registry, 'r') as f:
                mentorship_data = json.load(f)
            
            with open(self.hall_of_fame, 'r') as f:
                hof_agents = json.load(f)
            
            metrics = mentorship_data.get('mentorship_metrics', {})
            active = mentorship_data.get('active_mentorships', [])
            completed = mentorship_data.get('completed_mentorships', [])
            
            print("📊 System Metrics")
            print(f"   Hall of Fame Mentors: {len(hof_agents)}")
            print(f"   Total Capacity: {len(hof_agents) * 3} mentee slots")
            print(f"   Active Mentorships: {len(active)}")
            print(f"   Completed Mentorships: {len(completed)}")
            print(f"   Success Rate: {metrics.get('success_rate', 0)*100:.1f}%")
            print(f"   Average Improvement: +{metrics.get('avg_mentee_improvement', 0)*100:.1f}%")
            print()
            
            # Capacity visualization
            used = len(active)
            total = len(hof_agents) * 3
            utilization = (used / total * 100) if total > 0 else 0
            
            self.print_section("🔋 System Capacity")
            
            capacity_bar = int(utilization / 5)
            bar = "█" * capacity_bar + "░" * (20 - capacity_bar)
            print(f"Utilization: {bar} {utilization:.0f}%")
            print(f"Used: {used}/{total} slots")
            print()
            
            if utilization < 30:
                print("🟢 Excellent capacity - Ready for new agents")
            elif utilization < 70:
                print("🟡 Good capacity - Moderate usage")
            else:
                print("🔴 High utilization - Consider expanding mentor pool")
            
            print()
            
            # Specialization distribution
            if active or completed:
                all_mentorships = active + completed
                from collections import defaultdict
                spec_counts = defaultdict(int)
                for m in all_mentorships:
                    spec_counts[m['mentee_specialization']] += 1
                
                self.print_section("🎯 Popular Specializations")
                
                for spec, count in sorted(spec_counts.items(), key=lambda x: -x[1])[:5]:
                    print(f"  {spec.ljust(30)}: {count} mentorships")
                print()
        
        except FileNotFoundError as e:
            print(f"⚠️ Could not load system data: {e}")
            print()
    
    def list_scenarios(self):
        """List available demo scenarios"""
        self.print_header("📚 Available Demo Scenarios")
        
        scenarios = [
            ("new-agent", "New Agent Spawning with Mentor Assignment"),
            ("progress", "Mentorship Progress Over 14 Days"),
            ("mentor-effectiveness", "Tracking Mentor Effectiveness"),
            ("system-overview", "System-Wide Mentorship Overview")
        ]
        
        print("Available scenarios:\n")
        for name, description in scenarios:
            print(f"  {name.ljust(25)} - {description}")
        print()
        print("Usage:")
        print("  python demo-mentorship.py --scenario <name>")
        print("  python demo-mentorship.py  (runs all scenarios)")
        print()


def main():
    parser = argparse.ArgumentParser(
        description='Demonstrate the Agent Mentorship System'
    )
    
    parser.add_argument('--scenario', choices=[
        'new-agent', 'progress', 'mentor-effectiveness', 'system-overview'
    ], help='Run specific scenario')
    
    parser.add_argument('--list-scenarios', action='store_true',
                       help='List available scenarios')
    
    args = parser.parse_args()
    
    demo = MentorshipDemo()
    
    if args.list_scenarios:
        demo.list_scenarios()
        return
    
    if args.scenario:
        if args.scenario == 'new-agent':
            demo.scenario_new_agent_spawn()
        elif args.scenario == 'progress':
            demo.scenario_mentorship_progress()
        elif args.scenario == 'mentor-effectiveness':
            demo.scenario_mentor_effectiveness()
        elif args.scenario == 'system-overview':
            demo.scenario_system_overview()
    else:
        # Run all scenarios
        demo.scenario_new_agent_spawn()
        input("\nPress Enter to continue to next scenario...")
        demo.scenario_mentorship_progress()
        input("\nPress Enter to continue to next scenario...")
        demo.scenario_mentor_effectiveness()
        input("\nPress Enter to continue to next scenario...")
        demo.scenario_system_overview()
    
    print("\n" + "="*70)
    print("  Demo Complete!")
    print("="*70)
    print()
    print("Learn more:")
    print("  • Documentation: docs/MENTORSHIP_SYSTEM.md")
    print("  • Visualize: python tools/visualize-mentorship.py --all")
    print("  • Report: python tools/evaluate-mentorship.py --report")
    print()


if __name__ == '__main__':
    main()
