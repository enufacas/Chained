#!/usr/bin/env python3
"""
Demo: Meta-Agent Coordination in Action

This script demonstrates how the meta-agent coordinator works by analyzing
different types of tasks and showing the coordination plans it creates.

Part of the Chained autonomous AI ecosystem.
"""

import sys
import os
import json

# Add tools to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'tools'))

from meta_agent_coordinator import MetaAgentCoordinator, TaskComplexity


def demo_simple_task():
    """Demonstrate coordination for a simple task"""
    print("=" * 80)
    print("DEMO 1: Simple Task (Single Agent)")
    print("=" * 80)
    
    coordinator = MetaAgentCoordinator()
    
    task = "Add README documentation for the project setup"
    print(f"\nTask: {task}\n")
    
    plan = coordinator.decompose_task("demo-1", task)
    
    print(f"Complexity: {plan.complexity.value}")
    print(f"Subtasks: {len(plan.sub_tasks)}")
    print(f"Required Agents: {', '.join(plan.required_agents)}")
    print(f"Estimated Duration: {plan.estimated_duration}")
    
    for subtask in plan.sub_tasks:
        print(f"\n  → {subtask.description}")
        print(f"    Specializations: {', '.join(subtask.required_specializations)}")
        print(f"    Effort: {subtask.estimated_effort}")
    
    print("\n✓ Simple tasks go to a single agent\n")


def demo_moderate_task():
    """Demonstrate coordination for a moderate task"""
    print("=" * 80)
    print("DEMO 2: Moderate Task (Single Agent, Complex)")
    print("=" * 80)
    
    coordinator = MetaAgentCoordinator()
    
    task = "Refactor the codebase to eliminate duplication and improve code organization"
    print(f"\nTask: {task}\n")
    
    plan = coordinator.decompose_task("demo-2", task)
    
    print(f"Complexity: {plan.complexity.value}")
    print(f"Subtasks: {len(plan.sub_tasks)}")
    print(f"Required Agents: {', '.join(plan.required_agents)}")
    print(f"Estimated Duration: {plan.estimated_duration}")
    
    for subtask in plan.sub_tasks:
        print(f"\n  → {subtask.description}")
        print(f"    Specializations: {', '.join(subtask.required_specializations)}")
        print(f"    Priority: {subtask.priority}/10")
    
    print("\n✓ Moderate tasks may still use one agent but with higher effort\n")


def demo_complex_task():
    """Demonstrate coordination for a complex task"""
    print("=" * 80)
    print("DEMO 3: Complex Task (Multiple Agents, Dependencies)")
    print("=" * 80)
    
    coordinator = MetaAgentCoordinator()
    
    task = """
    Build a complete authentication API:
    - Security audit of current authentication
    - Design secure API endpoints
    - Implement with performance optimizations
    - Add comprehensive test coverage
    - Document the API
    """
    print(f"\nTask: {task}\n")
    
    plan = coordinator.decompose_task("demo-3", task)
    
    print(f"Complexity: {plan.complexity.value}")
    print(f"Subtasks: {len(plan.sub_tasks)}")
    print(f"Required Agents: {', '.join(plan.required_agents)}")
    print(f"Estimated Duration: {plan.estimated_duration}")
    
    print(f"\n📋 Subtasks and Dependencies:")
    for i, subtask in enumerate(plan.sub_tasks, 1):
        print(f"\n  {i}. {subtask.description}")
        print(f"     Specializations: {', '.join(subtask.required_specializations)}")
        print(f"     Dependencies: {', '.join(subtask.dependencies) if subtask.dependencies else 'None'}")
        print(f"     Priority: {subtask.priority}/10")
        print(f"     Effort: {subtask.estimated_effort}")
    
    print(f"\n🔄 Execution Order:")
    print(f"  {' → '.join(plan.execution_order)}")
    
    if plan.parallel_groups:
        print(f"\n⚡ Parallel Opportunities:")
        for i, group in enumerate(plan.parallel_groups, 1):
            print(f"  Group {i}: {', '.join(group)} (can run concurrently)")
    
    print("\n✓ Complex tasks coordinate multiple specialized agents\n")


def demo_highly_complex_task():
    """Demonstrate coordination for a highly complex task"""
    print("=" * 80)
    print("DEMO 4: Highly Complex Task (Full Coordination)")
    print("=" * 80)
    
    coordinator = MetaAgentCoordinator()
    
    task = """
    Implement a comprehensive user management system:
    - Investigate current user patterns and requirements
    - Security audit and threat modeling
    - Design scalable database schema
    - Build RESTful API with GraphQL support
    - Implement real-time WebSocket notifications
    - Add rate limiting and DDoS protection
    - Optimize performance for 10k+ concurrent users
    - Create comprehensive unit and integration tests
    - Write API documentation and user guides
    - Set up monitoring and alerting
    """
    print(f"\nTask: {task}\n")
    
    coordination = coordinator.create_coordination("demo-4", task)
    plan = coordination['plan']
    assignments = coordination['assignments']
    
    print(f"Coordination ID: {coordination['coordination_id']}")
    print(f"Complexity: {plan.complexity.value}")
    print(f"Subtasks: {len(plan.sub_tasks)}")
    print(f"Required Agents: {len(plan.required_agents)}")
    print(f"Estimated Duration: {plan.estimated_duration}")
    
    print(f"\n👥 Agent Assignments:")
    for subtask in plan.sub_tasks:
        agent = assignments.get(subtask.id, 'unassigned')
        print(f"  • {subtask.description[:60]}...")
        print(f"    → Assigned to: @{agent}")
    
    print(f"\n🔄 Coordination Flow:")
    print("  1. @meta-coordinator analyzes and decomposes the task")
    print("  2. Specialists are assigned based on required skills")
    print("  3. Dependencies determine execution order")
    print("  4. Some tasks can run in parallel")
    print("  5. @meta-coordinator integrates all contributions")
    
    print("\n✓ Highly complex tasks leverage the full agent hierarchy\n")


def demo_delegation_chain():
    """Demonstrate hierarchical delegation"""
    print("=" * 80)
    print("DEMO 5: Hierarchical Delegation")
    print("=" * 80)
    
    print("\nHierarchical Agent System:")
    print("""
    ┌─────────────────────────────────────────────────┐
    │            COORDINATOR TIER                      │
    │  @meta-coordinator  @coach-master               │
    └────────────────┬────────────────────────────────┘
                     │
                     ▼
    ┌─────────────────────────────────────────────────┐
    │            SPECIALIST TIER                       │
    │  @engineer-master  @secure-specialist           │
    │  @create-guru      @organize-guru               │
    └────────────────┬────────────────────────────────┘
                     │
                     ▼
    ┌─────────────────────────────────────────────────┐
    │              WORKER TIER                         │
    │  @accelerate-master  @assert-specialist         │
    │  @refactor-champion  @document-ninja            │
    └─────────────────────────────────────────────────┘
    """)
    
    print("Example Delegation Chain:")
    print("  1. Issue arrives: 'Build secure payment API'")
    print("  2. @meta-coordinator analyzes → Complexity: HIGHLY_COMPLEX")
    print("  3. @meta-coordinator delegates to:")
    print("     • @engineer-master (API design)")
    print("     • @secure-specialist (security audit)")
    print("  4. @engineer-master sub-delegates to:")
    print("     • @assert-specialist (API tests)")
    print("  5. @secure-specialist sub-delegates to:")
    print("     • @monitor-champion (security monitoring)")
    print("  6. All agents complete their work")
    print("  7. @meta-coordinator integrates contributions")
    print("  8. Final PR merged ✓")
    
    print("\n✓ Hierarchical delegation enables scalable collaboration\n")


def main():
    """Run all demonstrations"""
    print("\n" + "🎯" * 40)
    print("\n  META-AGENT COORDINATION SYSTEM DEMONSTRATION")
    print("  Part of the Chained Autonomous AI Ecosystem\n")
    print("🎯" * 40 + "\n")
    
    try:
        demo_simple_task()
        input("\nPress Enter to continue...")
        
        demo_moderate_task()
        input("\nPress Enter to continue...")
        
        demo_complex_task()
        input("\nPress Enter to continue...")
        
        demo_highly_complex_task()
        input("\nPress Enter to continue...")
        
        demo_delegation_chain()
        
        print("\n" + "=" * 80)
        print("DEMONSTRATION COMPLETE")
        print("=" * 80)
        print("\nTo see the meta-agent coordinator in action:")
        print("  • Create a complex issue on GitHub")
        print("  • The meta-agent-coordination workflow will detect it")
        print("  • Watch as @meta-coordinator creates sub-tasks")
        print("  • Observe specialized agents collaborate")
        print("\nFor more information:")
        print("  • tools/META_AGENT_COORDINATOR_README.md")
        print("  • tools/HIERARCHICAL_AGENT_SYSTEM_README.md")
        print("  • .github/agents/meta-coordinator.md")
        print()
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Demo interrupted by user\n")
        sys.exit(0)


if __name__ == '__main__':
    main()
