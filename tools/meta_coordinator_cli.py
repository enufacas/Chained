#!/usr/bin/env python3
"""
Meta-Coordinator CLI Tool

Interactive command-line interface for using the meta-agent coordination system.
Makes it easy to analyze tasks, create coordination plans, and visualize agent assignments.

Created by @create-guru with Tesla-inspired innovation.

Usage:
    python3 meta_coordinator_cli.py analyze "task description"
    python3 meta_coordinator_cli.py coordinate issue-123 "build authentication system"
    python3 meta_coordinator_cli.py visualize issue-123
    python3 meta_coordinator_cli.py stats

Part of the Chained autonomous AI ecosystem.
"""

import sys
import json
import argparse
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime, timezone

# Import the core coordination system
sys.path.insert(0, str(Path(__file__).parent))
from meta_agent_coordinator import (
    MetaAgentCoordinator,
    TaskComplexity,
    CoordinationPlan,
    SubTask
)


class Colors:
    """ANSI color codes for terminal output"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'


class MetaCoordinatorCLI:
    """Interactive CLI for the meta-coordination system"""
    
    def __init__(self):
        self.coordinator = MetaAgentCoordinator()
        
    def print_header(self, text: str):
        """Print a styled header"""
        print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.CYAN}{text}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.END}\n")
    
    def print_success(self, text: str):
        """Print success message"""
        print(f"{Colors.GREEN}✓ {text}{Colors.END}")
    
    def print_warning(self, text: str):
        """Print warning message"""
        print(f"{Colors.YELLOW}⚠ {text}{Colors.END}")
    
    def print_error(self, text: str):
        """Print error message"""
        print(f"{Colors.RED}✗ {text}{Colors.END}")
    
    def print_info(self, text: str):
        """Print info message"""
        print(f"{Colors.CYAN}ℹ {text}{Colors.END}")
    
    def analyze_task(self, task_description: str) -> Dict:
        """Analyze a task and show complexity assessment"""
        self.print_header("🔍 Task Analysis")
        
        print(f"{Colors.BOLD}Task Description:{Colors.END}")
        print(f"  {task_description[:200]}{'...' if len(task_description) > 200 else ''}\n")
        
        # Create a temporary plan for analysis
        plan = self.coordinator.decompose_task(
            task_id=f"analysis-{datetime.now(timezone.utc).timestamp()}",
            task_description=task_description
        )
        
        # Display complexity
        complexity_colors = {
            TaskComplexity.SIMPLE: Colors.GREEN,
            TaskComplexity.MODERATE: Colors.CYAN,
            TaskComplexity.COMPLEX: Colors.YELLOW,
            TaskComplexity.HIGHLY_COMPLEX: Colors.RED
        }
        color = complexity_colors.get(plan.complexity, Colors.CYAN)
        print(f"{Colors.BOLD}Complexity Level:{Colors.END} {color}{plan.complexity.value.upper()}{Colors.END}")
        
        # Display subtasks
        print(f"\n{Colors.BOLD}Sub-Tasks Identified:{Colors.END} {len(plan.sub_tasks)}")
        for i, subtask in enumerate(plan.sub_tasks, 1):
            print(f"\n  {Colors.BOLD}{i}. {subtask.description}{Colors.END}")
            print(f"     Specializations: {Colors.CYAN}{', '.join(subtask.required_specializations)}{Colors.END}")
            print(f"     Priority: {Colors.YELLOW}{'⭐' * subtask.priority}{Colors.END}")
            print(f"     Effort: {subtask.estimated_effort}")
        
        # Display required agents
        print(f"\n{Colors.BOLD}Required Agent Specializations:{Colors.END}")
        for spec in plan.required_agents:
            print(f"  • {Colors.GREEN}{spec}{Colors.END}")
        
        # Display execution order
        if plan.execution_order:
            print(f"\n{Colors.BOLD}Execution Sequence:{Colors.END}")
            for i, task_id in enumerate(plan.execution_order, 1):
                print(f"  {i}. {task_id}")
        
        # Display parallel opportunities
        if plan.parallel_groups:
            print(f"\n{Colors.BOLD}Parallel Execution Opportunities:{Colors.END}")
            for i, group in enumerate(plan.parallel_groups, 1):
                print(f"  Group {i}: {', '.join(group)}")
        
        self.print_success(f"\nAnalysis complete! Estimated duration: {plan.estimated_duration}")
        
        return {
            'complexity': plan.complexity.value,
            'subtask_count': len(plan.sub_tasks),
            'required_agents': list(plan.required_agents),
            'estimated_duration': plan.estimated_duration
        }
    
    def create_coordination(self, task_id: str, task_description: str, auto_assign: bool = True) -> CoordinationPlan:
        """Create a coordination plan and optionally assign agents"""
        self.print_header(f"🎯 Creating Coordination Plan: {task_id}")
        
        # Decompose the task
        plan = self.coordinator.decompose_task(task_id, task_description)
        
        self.print_success(f"Created plan with {len(plan.sub_tasks)} sub-tasks")
        
        # Auto-assign agents if requested
        if auto_assign:
            self.print_info("Auto-assigning agents based on specializations...")
            assignments = self.coordinator.select_agents(plan)
            
            print(f"\n{Colors.BOLD}Agent Assignments:{Colors.END}")
            for subtask_id, agent_id in assignments.items():
                subtask = next((st for st in plan.sub_tasks if st.id == subtask_id), None)
                if subtask:
                    print(f"  • {Colors.CYAN}{subtask.description[:60]}{Colors.END}")
                    print(f"    → Agent: {Colors.GREEN}{agent_id}{Colors.END}")
        
        # Record the coordination using create_coordination
        coordination = self.coordinator.create_coordination(task_id, task_description)
        self.print_success(f"\nCoordination plan saved!")
        
        return plan
    
    def visualize_plan(self, task_id: str):
        """Visualize a coordination plan in ASCII art"""
        self.print_header(f"📊 Coordination Plan Visualization: {task_id}")
        
        # Load the coordination log
        log_file = Path('.github/agent-system/coordination_log.json')
        if not log_file.exists():
            self.print_error("No coordination log found. Create a coordination first.")
            return
        
        with open(log_file) as f:
            log = json.load(f)
        
        # Find the coordination
        coordination = next((c for c in log.get('coordinations', []) if c['task_id'] == task_id), None)
        if not coordination:
            self.print_error(f"No coordination found for task: {task_id}")
            return
        
        # Extract plan from coordination structure
        plan = coordination.get('plan', coordination)  # Handle both structures
        
        # Draw the plan
        print(f"{Colors.BOLD}Task:{Colors.END} {task_id}")
        print(f"{Colors.BOLD}Complexity:{Colors.END} {plan.get('complexity', 'unknown')}")
        print(f"{Colors.BOLD}Sub-tasks:{Colors.END} {len(plan.get('sub_tasks', []))}\n")
        
        # Draw task tree
        print(f"{Colors.BOLD}Execution Flow:{Colors.END}\n")
        for i, subtask in enumerate(plan.get('sub_tasks', []), 1):
            # Draw connection lines
            if i == 1:
                print("  ┌─────")
            elif i == len(plan.get('sub_tasks', [])):
                print("  └─────")
            else:
                print("  ├─────")
            
            # Draw task box
            print(f"  │ {Colors.BOLD}{subtask['description'][:50]}{Colors.END}")
            print(f"  │ Specs: {Colors.CYAN}{', '.join(subtask['required_specializations'][:2])}{Colors.END}")
            if subtask.get('assigned_agent'):
                print(f"  │ Agent: {Colors.GREEN}{subtask['assigned_agent']}{Colors.END}")
            print(f"  │")
        
        self.print_success("\nVisualization complete!")
    
    def show_statistics(self):
        """Display coordination statistics"""
        self.print_header("📈 Meta-Coordinator Statistics")
        
        # Load the coordination log
        log_file = Path('.github/agent-system/coordination_log.json')
        if not log_file.exists():
            self.print_error("No coordination log found. Create coordinations to see statistics.")
            return
        
        with open(log_file) as f:
            log = json.load(f)
        
        stats = log.get('statistics', {})
        
        print(f"{Colors.BOLD}Total Coordinations:{Colors.END} {stats.get('total_coordinations', 0)}")
        print(f"{Colors.BOLD}Average Agents per Task:{Colors.END} {stats.get('avg_agents_per_task', 0):.1f}")
        print(f"{Colors.BOLD}Average Sub-tasks:{Colors.END} {stats.get('avg_subtasks', 0):.1f}")
        print(f"{Colors.BOLD}Success Rate:{Colors.END} {stats.get('success_rate', 0):.1%}")
        
        # Complexity breakdown
        complexity_counts = stats.get('complexity_breakdown', {})
        if complexity_counts:
            print(f"\n{Colors.BOLD}Complexity Breakdown:{Colors.END}")
            for complexity, count in complexity_counts.items():
                print(f"  {complexity}: {count}")
        
        # Most used specializations
        print(f"\n{Colors.BOLD}Most Requested Specializations:{Colors.END}")
        spec_counts = stats.get('specialization_usage', {})
        for spec, count in sorted(spec_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"  {Colors.GREEN}{spec}{Colors.END}: {count} times")
        
        self.print_success("\nStatistics displayed!")
    
    def interactive_mode(self):
        """Run in interactive mode"""
        self.print_header("🚀 Meta-Coordinator Interactive Mode")
        print(f"{Colors.BOLD}Commands:{Colors.END}")
        print("  analyze  - Analyze task complexity")
        print("  coord    - Create coordination plan")
        print("  viz      - Visualize a plan")
        print("  stats    - Show statistics")
        print("  help     - Show this help")
        print("  exit     - Exit interactive mode\n")
        
        while True:
            try:
                cmd = input(f"{Colors.CYAN}meta-coord>{Colors.END} ").strip().lower()
                
                if cmd in ['exit', 'quit', 'q']:
                    self.print_success("Goodbye!")
                    break
                elif cmd == 'help':
                    self.interactive_mode()
                    return
                elif cmd == 'analyze':
                    task = input("Enter task description: ")
                    self.analyze_task(task)
                elif cmd == 'coord':
                    task_id = input("Enter task ID: ")
                    task_desc = input("Enter task description: ")
                    self.create_coordination(task_id, task_desc)
                elif cmd == 'viz':
                    task_id = input("Enter task ID: ")
                    self.visualize_plan(task_id)
                elif cmd == 'stats':
                    self.show_statistics()
                else:
                    self.print_warning(f"Unknown command: {cmd}. Type 'help' for commands.")
            except KeyboardInterrupt:
                print("\n")
                self.print_success("Goodbye!")
                break
            except Exception as e:
                self.print_error(f"Error: {e}")


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description='Meta-Coordinator CLI - Coordinate specialized AI agents',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze a task's complexity
  python3 meta_coordinator_cli.py analyze "Build secure API with tests"
  
  # Create a coordination plan
  python3 meta_coordinator_cli.py coordinate issue-123 "Implement authentication system"
  
  # Visualize a plan
  python3 meta_coordinator_cli.py visualize issue-123
  
  # Show statistics
  python3 meta_coordinator_cli.py stats
  
  # Interactive mode
  python3 meta_coordinator_cli.py interactive

Created by @create-guru - Channeling Tesla's vision for autonomous coordination
        """
    )
    
    parser.add_argument('command', nargs='?', choices=['analyze', 'coordinate', 'visualize', 'stats', 'interactive'],
                       help='Command to execute')
    parser.add_argument('args', nargs='*', help='Command arguments')
    parser.add_argument('--no-color', action='store_true', help='Disable colored output')
    
    args = parser.parse_args()
    
    # Disable colors if requested
    if args.no_color:
        for attr in dir(Colors):
            if not attr.startswith('_'):
                setattr(Colors, attr, '')
    
    cli = MetaCoordinatorCLI()
    
    if not args.command or args.command == 'interactive':
        cli.interactive_mode()
    elif args.command == 'analyze':
        if not args.args:
            print("Error: Task description required")
            sys.exit(1)
        task_desc = ' '.join(args.args)
        cli.analyze_task(task_desc)
    elif args.command == 'coordinate':
        if len(args.args) < 2:
            print("Error: Task ID and description required")
            sys.exit(1)
        task_id = args.args[0]
        task_desc = ' '.join(args.args[1:])
        cli.create_coordination(task_id, task_desc)
    elif args.command == 'visualize':
        if not args.args:
            print("Error: Task ID required")
            sys.exit(1)
        task_id = args.args[0]
        cli.visualize_plan(task_id)
    elif args.command == 'stats':
        cli.show_statistics()


if __name__ == '__main__':
    main()
