#!/usr/bin/env python3
"""
Interactive Meta-Coordinator Demo

Demonstrates the @meta-coordinator system with an interactive CLI.
Shows task analysis, decomposition, and agent assignment in real-time.

Usage:
    python3 tools/interactive_meta_demo.py
    python3 tools/interactive_meta_demo.py --task "your task description"
"""

import sys
import os
from pathlib import Path

# Add tools to path
sys.path.insert(0, str(Path(__file__).parent))

from meta_agent_coordinator import MetaAgentCoordinator, TaskComplexity


def print_header(text: str):
    """Print a formatted header"""
    width = 70
    print("\n" + "=" * width)
    print(text.center(width))
    print("=" * width + "\n")


def print_section(title: str):
    """Print a section title"""
    print(f"\n### {title}")
    print("-" * 70)


def display_task_analysis(plan, coordinator):
    """Display task analysis results"""
    print_section("Task Complexity Analysis")
    
    complexity_emoji = {
        TaskComplexity.SIMPLE: "🟢",
        TaskComplexity.MODERATE: "🟡",
        TaskComplexity.COMPLEX: "🟠",
        TaskComplexity.HIGHLY_COMPLEX: "🔴"
    }
    
    emoji = complexity_emoji.get(plan.complexity, "❓")
    print(f"Complexity Level: {emoji} {plan.complexity.value.upper()}")
    print(f"Sub-Tasks Identified: {len(plan.sub_tasks)}")
    print(f"Required Agents: {len(plan.required_agents)}")
    print(f"Estimated Duration: {plan.estimated_duration}")
    
    if plan.complexity == TaskComplexity.SIMPLE:
        print("\n💡 This is a simple task - single agent can handle it")
    elif plan.complexity == TaskComplexity.MODERATE:
        print("\n💡 This is moderately complex - one agent, but requires careful work")
    elif plan.complexity == TaskComplexity.COMPLEX:
        print("\n💡 This is complex - requires multiple agents working in sequence")
    else:
        print("\n💡 This is highly complex - requires coordinated multi-agent effort")


def display_subtasks(plan):
    """Display decomposed sub-tasks"""
    print_section("Sub-Task Breakdown")
    
    for i, subtask in enumerate(plan.sub_tasks, 1):
        print(f"\n{i}. {subtask.description}")
        print(f"   Priority: {'⭐' * min(subtask.priority, 10)} ({subtask.priority}/10)")
        print(f"   Effort: {subtask.estimated_effort.upper()}")
        print(f"   Specializations needed: {', '.join(['@' + s for s in subtask.required_specializations])}")
        
        if subtask.dependencies:
            print(f"   Dependencies: {', '.join(subtask.dependencies)}")
        else:
            print(f"   Dependencies: ✅ None - can start immediately")
        
        if subtask.completion_criteria:
            print(f"   Completion criteria:")
            for criterion in subtask.completion_criteria[:3]:  # Show first 3
                print(f"     • {criterion}")
            if len(subtask.completion_criteria) > 3:
                print(f"     ... and {len(subtask.completion_criteria) - 3} more")


def display_execution_plan(plan):
    """Display execution order and parallelization opportunities"""
    print_section("Execution Plan")
    
    print("Execution Order:")
    for i, task_id in enumerate(plan.execution_order, 1):
        subtask = next((st for st in plan.sub_tasks if st.id == task_id), None)
        if subtask:
            print(f"  {i}. {task_id}: {subtask.description[:50]}...")
    
    if plan.parallel_groups:
        print("\n🔀 Parallelization Opportunities:")
        for i, group in enumerate(plan.parallel_groups, 1):
            group_tasks = [next((st for st in plan.sub_tasks if st.id == tid), None) for tid in group]
            group_tasks = [t for t in group_tasks if t]
            if group_tasks:
                print(f"\n  Group {i} (can run concurrently):")
                for task in group_tasks:
                    print(f"    • {task.id}: {task.description[:45]}...")


def display_agent_assignments(coordination):
    """Display agent assignments"""
    print_section("Agent Assignments")
    
    assignments = coordination['assignments']
    plan = coordination['plan']
    
    print("The following agents have been selected:\n")
    
    for subtask in plan['sub_tasks']:
        agent_id = assignments.get(subtask['id'], 'TBD')
        print(f"✓ {subtask['id']}")
        print(f"  → Assigned to: @{agent_id}")
        print(f"  → Task: {subtask['description'][:60]}...")
        print()


def display_coordination_summary(coordination):
    """Display final coordination summary"""
    print_section("Coordination Summary")
    
    print(f"Coordination ID: {coordination['id']}")
    print(f"Status: {coordination['status'].upper()}")
    print(f"Created at: {coordination['created_at']}")
    print(f"\nTotal sub-tasks: {len(coordination['plan']['sub_tasks'])}")
    print(f"Total agents involved: {len(set(coordination['assignments'].values()))}")
    
    print("\n✅ Coordination plan created successfully!")
    print("Sub-issues can now be created for each agent.")


def run_interactive_demo(task_description: str = None, non_interactive: bool = False):
    """Run the interactive demo"""
    print_header("🎯 META-COORDINATOR INTERACTIVE DEMO")
    print("Part of the Chained Autonomous AI Ecosystem")
    print("Demonstrating intelligent multi-agent task coordination")
    
    # Get task description
    if not task_description:
        print("\nExample tasks you could try:")
        print("  1. Build a REST API with authentication")
        print("  2. Refactor the user management module")
        print("  3. Add documentation for the agent system")
        print("  4. Implement a complete user authentication system with JWT, rate limiting, and tests")
        print()
        
        task_description = input("Enter your task description (or press Enter for example #4): ").strip()
        
        if not task_description:
            task_description = "Implement a complete user authentication system with JWT-based auth, password hashing, rate limiting, comprehensive tests, and API documentation"
    
    print(f"\n📋 Task: {task_description}")
    
    # Initialize coordinator
    print("\n🔧 Initializing Meta-Coordinator...")
    coordinator = MetaAgentCoordinator()
    print("✓ Meta-Coordinator ready")
    
    # Step 1: Analyze and decompose
    print("\n⚙️  Step 1: Analyzing task complexity...")
    plan = coordinator.decompose_task(
        task_id="demo-task",
        task_description=task_description
    )
    print("✓ Analysis complete")
    
    display_task_analysis(plan, coordinator)
    
    if not non_interactive:
        input("\nPress Enter to see sub-task breakdown...")
    display_subtasks(plan)
    
    if not non_interactive:
        input("\nPress Enter to see execution plan...")
    display_execution_plan(plan)
    
    # Step 2: Select agents
    print("\n⚙️  Step 2: Selecting optimal agents...")
    coordination = coordinator.create_coordination(
        task_id="demo-task",
        task_description=task_description
    )
    print("✓ Agent selection complete")
    
    if not non_interactive:
        input("\nPress Enter to see agent assignments...")
    display_agent_assignments(coordination)
    
    if not non_interactive:
        input("\nPress Enter to see final summary...")
    display_coordination_summary(coordination)
    
    # Show next steps
    print_section("What Happens Next?")
    print("""
In a real workflow, the meta-agent-coordination.yml workflow would:

1. Create GitHub issues for each sub-task
2. Assign the selected agents via labels
3. Post the coordination plan as a comment
4. Monitor progress as agents complete their work
5. Coordinate integration of all contributions

Agents can be invoked directly via:
  - GitHub Copilot chat
  - Custom agent tools
  - Workflow automation
  - API calls
    """)
    
    print("\n" + "=" * 70)
    print("Demo complete! 🎉".center(70))
    print("=" * 70 + "\n")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Interactive Meta-Coordinator Demo",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 tools/interactive_meta_demo.py
  python3 tools/interactive_meta_demo.py --task "Build authentication API"
        """
    )
    
    parser.add_argument(
        '--task',
        help='Task description to analyze',
        default=None
    )
    
    parser.add_argument(
        '--non-interactive',
        action='store_true',
        help='Run in non-interactive mode (no input prompts)',
        default=False
    )
    
    args = parser.parse_args()
    
    try:
        run_interactive_demo(args.task, args.non_interactive)
    except KeyboardInterrupt:
        print("\n\n👋 Demo interrupted. Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
