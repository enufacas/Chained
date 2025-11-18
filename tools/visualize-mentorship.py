#!/usr/bin/env python3
"""
Mentorship Visualization Tool

Creates visual representations of mentorship relationships, capacity,
and effectiveness metrics for the Chained Agent Mentorship System.

Features:
- Text-based mentorship tree visualization
- Mentor capacity dashboard
- Success rate charts (ASCII)
- Active mentorship status board

Usage:
    python visualize-mentorship.py [--tree] [--dashboard] [--stats]
    python visualize-mentorship.py --mentor-detail <mentor_id>
    python visualize-mentorship.py --export-graph
"""

import json
import os
import sys
import argparse
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any, Optional
from collections import defaultdict


# Constants
REGISTRY_FILE = Path(".github/agent-system/registry.json")
MENTORSHIP_REGISTRY = Path(".github/agent-system/mentorship_registry.json")
HALL_OF_FAME_FILE = Path(".github/agent-system/hall_of_fame.json")


class MentorshipVisualizer:
    """Visualizes mentorship relationships and metrics"""
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.registry = self._load_registry()
        self.mentorship_registry = self._load_mentorship_registry()
        self.hall_of_fame = self._load_hall_of_fame()
    
    def _log(self, message: str, level: str = "INFO"):
        """Log message if verbose mode is enabled"""
        if self.verbose:
            print(f"[{level}] {message}")
    
    def _load_registry(self) -> Dict[str, Any]:
        """Load agent registry"""
        if not REGISTRY_FILE.exists():
            return {"agents": []}
        
        with open(REGISTRY_FILE, 'r') as f:
            return json.load(f)
    
    def _load_mentorship_registry(self) -> Dict[str, Any]:
        """Load mentorship registry"""
        if not MENTORSHIP_REGISTRY.exists():
            return {
                "active_mentorships": [],
                "completed_mentorships": [],
                "mentor_capacity": {},
                "mentorship_metrics": {}
            }
        
        with open(MENTORSHIP_REGISTRY, 'r') as f:
            return json.load(f)
    
    def _load_hall_of_fame(self) -> List[Dict[str, Any]]:
        """Load Hall of Fame agents"""
        if not HALL_OF_FAME_FILE.exists():
            return []
        
        with open(HALL_OF_FAME_FILE, 'r') as f:
            return json.load(f)
    
    def display_mentorship_tree(self):
        """Display mentorship relationships as a tree"""
        print("\n" + "="*70)
        print("🌳 MENTORSHIP TREE")
        print("="*70 + "\n")
        
        active = self.mentorship_registry.get('active_mentorships', [])
        
        if not active:
            print("   No active mentorships currently.\n")
            return
        
        # Group mentees by mentor
        mentor_tree = defaultdict(list)
        for mentorship in active:
            mentor_id = mentorship['mentor_id']
            mentor_tree[mentor_id].append(mentorship)
        
        # Display each mentor and their mentees
        for mentor_id, mentees in sorted(mentor_tree.items()):
            mentor_info = mentees[0]  # Get mentor info from first mentee
            mentor_name = mentor_info['mentor_name']
            mentor_spec = mentor_info['mentor_specialization']
            
            print(f"👨‍🏫 {mentor_name} ({mentor_spec})")
            print(f"   ID: {mentor_id}")
            print(f"   Mentees: {len(mentees)}/3")
            print("   │")
            
            for i, mentorship in enumerate(mentees):
                is_last = (i == len(mentees) - 1)
                prefix = "   └─" if is_last else "   ├─"
                
                mentee_name = mentorship['mentee_name']
                mentee_spec = mentorship['mentee_specialization']
                match_type = mentorship['matching_type']
                assigned_at = mentorship['assigned_at'][:10]  # Date only
                
                match_emoji = "🎯" if match_type == "exact" else "🔀"
                
                print(f"{prefix} {match_emoji} {mentee_name} ({mentee_spec})")
                print(f"   {'  ' if is_last else '│ '} └─ Assigned: {assigned_at}")
            
            print()
    
    def display_capacity_dashboard(self):
        """Display mentor capacity overview"""
        print("\n" + "="*70)
        print("📊 MENTOR CAPACITY DASHBOARD")
        print("="*70 + "\n")
        
        mentor_capacity = self.mentorship_registry.get('mentor_capacity', {})
        
        # Get all Hall of Fame agents as potential mentors
        available_mentors = []
        for agent in self.hall_of_fame:
            agent_id = agent['id']
            current_load = mentor_capacity.get(agent_id, 0)
            available_mentors.append({
                'id': agent_id,
                'name': agent.get('human_name', agent.get('name', 'Unknown')),
                'specialization': agent['specialization'],
                'score': agent['metrics']['overall_score'],
                'load': current_load,
                'capacity': 3 - current_load
            })
        
        # Sort by load (most loaded first)
        available_mentors.sort(key=lambda x: (-x['load'], -x['score']))
        
        print(f"Total Mentors: {len(available_mentors)}")
        print(f"Total Capacity: {len(available_mentors) * 3} slots")
        print(f"Used: {sum(m['load'] for m in available_mentors)} slots")
        print(f"Available: {sum(m['capacity'] for m in available_mentors)} slots")
        print()
        
        # Display each mentor
        print("Mentor                        Spec                Load      Capacity    Score")
        print("-" * 80)
        
        for mentor in available_mentors:
            name = mentor['name'][:25].ljust(25)
            spec = mentor['specialization'][:18].ljust(18)
            
            # Capacity bar
            load = mentor['load']
            total = 3
            bar = "█" * load + "░" * (total - load)
            capacity_str = f"{bar} {load}/3"
            
            # Score
            score = f"{mentor['score']*100:.1f}%"
            
            # Status emoji
            if load >= 3:
                status = "🔴"  # Full
            elif load >= 2:
                status = "🟡"  # Busy
            else:
                status = "🟢"  # Available
            
            print(f"{status} {name}  {spec}  {capacity_str.ljust(12)}  {score}")
        
        print()
    
    def display_statistics(self):
        """Display mentorship statistics"""
        print("\n" + "="*70)
        print("📈 MENTORSHIP STATISTICS")
        print("="*70 + "\n")
        
        metrics = self.mentorship_registry.get('mentorship_metrics', {})
        active = self.mentorship_registry.get('active_mentorships', [])
        completed = self.mentorship_registry.get('completed_mentorships', [])
        
        # Overall stats
        print("📊 Overall Metrics")
        print("-" * 40)
        print(f"Total Mentorships:     {metrics.get('total_mentorships', 0)}")
        print(f"Active:                {metrics.get('active_mentorships', 0)}")
        print(f"Completed:             {metrics.get('completed_mentorships', 0)}")
        print(f"Success Rate:          {metrics.get('success_rate', 0)*100:.1f}%")
        print(f"Avg Improvement:       +{metrics.get('avg_mentee_improvement', 0)*100:.1f}%")
        print()
        
        # Success distribution (if completed mentorships exist)
        if completed:
            successes = sum(1 for m in completed if m.get('outcome', {}).get('success', False))
            success_rate = (successes / len(completed)) * 100
            
            print("✅ Completion Analysis")
            print("-" * 40)
            print(f"Successful:            {successes}/{len(completed)} ({success_rate:.1f}%)")
            print(f"Need Improvement:      {len(completed) - successes}/{len(completed)}")
            print()
            
            # ASCII chart of success distribution
            print("Success Distribution:")
            bar_success = "█" * int(success_rate / 5)
            bar_fail = "░" * (20 - int(success_rate / 5))
            print(f"  Success    {bar_success}{bar_fail} {success_rate:.0f}%")
            print(f"  Incomplete {bar_fail}{bar_success} {100-success_rate:.0f}%")
            print()
        
        # Specialization breakdown
        if active or completed:
            all_mentorships = active + completed
            spec_counts = defaultdict(int)
            for m in all_mentorships:
                spec_counts[m['mentee_specialization']] += 1
            
            print("🎯 By Specialization")
            print("-" * 40)
            for spec, count in sorted(spec_counts.items(), key=lambda x: -x[1])[:5]:
                print(f"  {spec.ljust(25)}: {count}")
            print()
        
        # Matching type distribution
        if active:
            exact_matches = sum(1 for m in active if m['matching_type'] == 'exact')
            cross_matches = len(active) - exact_matches
            
            print("🔀 Matching Type Distribution")
            print("-" * 40)
            print(f"Exact Match:           {exact_matches}/{len(active)} ({exact_matches/len(active)*100:.0f}%)")
            print(f"Cross-Specialization:  {cross_matches}/{len(active)} ({cross_matches/len(active)*100:.0f}%)")
            print()
    
    def display_mentor_detail(self, mentor_id: str):
        """Display detailed information about a specific mentor"""
        print("\n" + "="*70)
        print(f"👨‍🏫 MENTOR DETAIL: {mentor_id}")
        print("="*70 + "\n")
        
        # Find mentor in Hall of Fame
        mentor = None
        for agent in self.hall_of_fame:
            if agent['id'] == mentor_id:
                mentor = agent
                break
        
        if not mentor:
            print(f"❌ Mentor {mentor_id} not found in Hall of Fame")
            return
        
        # Mentor info
        print("📋 Mentor Information")
        print("-" * 40)
        print(f"Name:           {mentor.get('human_name', 'Unknown')}")
        print(f"Specialization: {mentor['specialization']}")
        print(f"Score:          {mentor['metrics']['overall_score']*100:.1f}%")
        print(f"Issues Resolved: {mentor['metrics']['issues_resolved']}")
        print(f"PRs Merged:     {mentor['metrics']['prs_merged']}")
        print()
        
        # Current mentees
        active = self.mentorship_registry.get('active_mentorships', [])
        mentor_mentees = [m for m in active if m['mentor_id'] == mentor_id]
        
        print(f"👥 Current Mentees: {len(mentor_mentees)}/3")
        print("-" * 40)
        if mentor_mentees:
            for mentorship in mentor_mentees:
                print(f"  • {mentorship['mentee_name']} ({mentorship['mentee_specialization']})")
                print(f"    Match: {mentorship['matching_type']}")
                print(f"    Since: {mentorship['assigned_at'][:10]}")
        else:
            print("  No active mentees")
        print()
        
        # Past mentees (if any)
        completed = self.mentorship_registry.get('completed_mentorships', [])
        past_mentees = [m for m in completed if m['mentor_id'] == mentor_id]
        
        if past_mentees:
            successes = sum(1 for m in past_mentees if m.get('outcome', {}).get('success', False))
            success_rate = (successes / len(past_mentees)) * 100
            
            print(f"📊 Mentorship History: {len(past_mentees)} completed")
            print("-" * 40)
            print(f"Success Rate: {success_rate:.0f}% ({successes}/{len(past_mentees)})")
            print()
    
    def export_graph_data(self):
        """Export mentorship data in graph format (JSON)"""
        print("\n" + "="*70)
        print("📤 EXPORTING GRAPH DATA")
        print("="*70 + "\n")
        
        active = self.mentorship_registry.get('active_mentorships', [])
        
        # Build graph structure
        nodes = []
        edges = []
        
        # Add mentor nodes
        mentor_ids = set(m['mentor_id'] for m in active)
        for mentor_id in mentor_ids:
            # Find mentor details
            mentor = next((a for a in self.hall_of_fame if a['id'] == mentor_id), None)
            if mentor:
                nodes.append({
                    'id': mentor_id,
                    'label': mentor.get('human_name', 'Unknown'),
                    'type': 'mentor',
                    'specialization': mentor['specialization'],
                    'score': mentor['metrics']['overall_score']
                })
        
        # Add mentee nodes and edges
        for mentorship in active:
            # Mentee node
            nodes.append({
                'id': mentorship['mentee_id'],
                'label': mentorship['mentee_name'],
                'type': 'mentee',
                'specialization': mentorship['mentee_specialization']
            })
            
            # Mentorship edge
            edges.append({
                'from': mentorship['mentor_id'],
                'to': mentorship['mentee_id'],
                'type': mentorship['matching_type'],
                'assigned_at': mentorship['assigned_at']
            })
        
        graph_data = {
            'nodes': nodes,
            'edges': edges,
            'metadata': {
                'total_mentorships': len(active),
                'total_mentors': len(mentor_ids),
                'generated_at': datetime.now(timezone.utc).isoformat()
            }
        }
        
        # Save to file
        output_file = Path('mentorship_graph.json')
        with open(output_file, 'w') as f:
            json.dump(graph_data, f, indent=2)
        
        print(f"✅ Graph data exported to: {output_file}")
        print(f"   Nodes: {len(nodes)}")
        print(f"   Edges: {len(edges)}")
        print()


def main():
    parser = argparse.ArgumentParser(
        description='Visualize Agent Mentorship System relationships and metrics'
    )
    
    # Display options
    parser.add_argument('--tree', action='store_true',
                       help='Display mentorship tree')
    parser.add_argument('--dashboard', action='store_true',
                       help='Display mentor capacity dashboard')
    parser.add_argument('--stats', action='store_true',
                       help='Display statistics')
    parser.add_argument('--all', action='store_true',
                       help='Display all visualizations')
    
    # Detail options
    parser.add_argument('--mentor-detail', metavar='MENTOR_ID',
                       help='Show detailed info for specific mentor')
    
    # Export options
    parser.add_argument('--export-graph', action='store_true',
                       help='Export graph data to JSON file')
    
    # General options
    parser.add_argument('--verbose', action='store_true',
                       help='Enable verbose output')
    
    args = parser.parse_args()
    
    # Create visualizer
    viz = MentorshipVisualizer(verbose=args.verbose)
    
    # If no specific option, show all
    show_all = args.all or not any([
        args.tree, args.dashboard, args.stats,
        args.mentor_detail, args.export_graph
    ])
    
    # Display requested visualizations
    if show_all or args.tree:
        viz.display_mentorship_tree()
    
    if show_all or args.dashboard:
        viz.display_capacity_dashboard()
    
    if show_all or args.stats:
        viz.display_statistics()
    
    if args.mentor_detail:
        viz.display_mentor_detail(args.mentor_detail)
    
    if args.export_graph:
        viz.export_graph_data()
    
    print()


if __name__ == '__main__':
    main()
