#!/usr/bin/env python3
"""
Meta-Coordination Examples

Practical examples demonstrating the meta-agent coordination system.
Shows real-world scenarios and how the system coordinates multiple agents.

Created by @create-guru with Tesla-inspired innovation.

Part of the Chained autonomous AI ecosystem.
"""

import sys
from pathlib import Path

# Import the meta-coordinator
sys.path.insert(0, str(Path(__file__).parent.parent))
from meta_agent_coordinator import MetaAgentCoordinator


def example_1_simple_task():
    """Example 1: Simple task - single agent"""
    print("\n" + "="*70)
    print("EXAMPLE 1: Simple Task - Fix a Bug")
    print("="*70 + "\n")
    
    coordinator = MetaAgentCoordinator()
    
    task = """
    Fix a bug in the user profile endpoint where the email field is not 
    being validated properly. Add unit tests to verify the fix.
    """
    
    plan = coordinator.decompose_task("issue-simple-bug", task)
    
    print(f"Complexity: {plan.complexity.value}")
    print(f"Sub-tasks: {len(plan.sub_tasks)}")
    print(f"Estimated Duration: {plan.estimated_duration}")
    print(f"\nRequired Agents: {', '.join(plan.required_agents)}")
    
    print("\n✓ This simple task can be handled by a single agent\n")


def example_2_api_development():
    """Example 2: Complex task - API development with multiple concerns"""
    print("\n" + "="*70)
    print("EXAMPLE 2: Complex Task - Build Authentication API")
    print("="*70 + "\n")
    
    coordinator = MetaAgentCoordinator()
    
    task = """
    Build a complete authentication system:
    - Design secure REST API endpoints for login, logout, and token refresh
    - Implement JWT token generation and validation
    - Add rate limiting to prevent brute force attacks
    - Create comprehensive test suite with unit and integration tests
    - Document all API endpoints with OpenAPI/Swagger
    - Add security audit for common vulnerabilities (SQL injection, XSS, etc.)
    """
    
    plan = coordinator.decompose_task("issue-auth-api", task)
    
    print(f"Complexity: {plan.complexity.value}")
    print(f"Sub-tasks: {len(plan.sub_tasks)}")
    print(f"Estimated Duration: {plan.estimated_duration}")
    
    print(f"\nSub-Task Breakdown:")
    for i, subtask in enumerate(plan.sub_tasks, 1):
        print(f"\n{i}. {subtask.description}")
        print(f"   Specializations: {', '.join(subtask.required_specializations)}")
        print(f"   Priority: {subtask.priority}/10")
        print(f"   Effort: {subtask.estimated_effort}")
    
    print(f"\nExecution Order:")
    for i, task_id in enumerate(plan.execution_order, 1):
        print(f"  {i}. {task_id}")
    
    if plan.parallel_groups:
        print(f"\nParallel Execution Opportunities:")
        for i, group in enumerate(plan.parallel_groups, 1):
            print(f"  Group {i}: {len(group)} tasks can run in parallel")
    
    print("\n✓ This complex task requires coordination of multiple specialized agents\n")


def example_3_refactoring_project():
    """Example 3: Highly complex task - major refactoring"""
    print("\n" + "="*70)
    print("EXAMPLE 3: Highly Complex Task - Major Refactoring")
    print("="*70 + "\n")
    
    coordinator = MetaAgentCoordinator()
    
    task = """
    Refactor the legacy codebase to improve maintainability:
    - Analyze current code structure and identify problem areas
    - Break monolithic modules into smaller, focused components
    - Extract duplicate code into reusable utilities
    - Improve code organization and file structure
    - Update all imports and references
    - Add comprehensive tests for refactored code
    - Update documentation to reflect new structure
    - Ensure no functionality is broken (regression testing)
    - Optimize performance of refactored components
    """
    
    plan = coordinator.decompose_task("issue-refactoring", task)
    
    print(f"Complexity: {plan.complexity.value}")
    print(f"Sub-tasks: {len(plan.sub_tasks)}")
    print(f"Estimated Duration: {plan.estimated_duration}")
    
    print(f"\nRequired Agent Specializations: {len(plan.required_agents)}")
    for spec in sorted(plan.required_agents):
        print(f"  • {spec}")
    
    print(f"\nSub-Task Summary:")
    for i, subtask in enumerate(plan.sub_tasks, 1):
        print(f"  {i}. {subtask.description[:60]}...")
    
    print("\n✓ This highly complex task requires careful coordination across many agents\n")


def example_4_agent_selection():
    """Example 4: Demonstrate agent selection based on specialization"""
    print("\n" + "="*70)
    print("EXAMPLE 4: Agent Selection Demo")
    print("="*70 + "\n")
    
    coordinator = MetaAgentCoordinator()
    
    task = """
    Implement a new feature with security and performance requirements:
    - Create secure API endpoint
    - Optimize for high performance
    - Add comprehensive tests
    """
    
    plan = coordinator.decompose_task("issue-feature", task)
    
    print(f"Task requires {len(plan.sub_tasks)} specialized agents\n")
    
    # Select agents
    assignments = coordinator.select_agents(plan)
    
    print("Agent Assignments:")
    for subtask_id, agent_id in assignments.items():
        subtask = next((st for st in plan.sub_tasks if st.id == subtask_id), None)
        if subtask:
            print(f"\n  Sub-task: {subtask.description[:50]}...")
            print(f"  Required: {', '.join(subtask.required_specializations)}")
            print(f"  Assigned: {agent_id}")
    
    print("\n✓ Agents selected based on specialization match and performance history\n")


def example_5_coordination_workflow():
    """Example 5: Complete coordination workflow"""
    print("\n" + "="*70)
    print("EXAMPLE 5: Complete Coordination Workflow")
    print("="*70 + "\n")
    
    coordinator = MetaAgentCoordinator()
    
    task = """
    Add payment processing to the e-commerce platform:
    - Integrate Stripe payment gateway
    - Create secure payment endpoints
    - Add payment confirmation emails
    - Implement refund processing
    - Add tests for payment flows
    - Document payment API
    """
    
    print("Step 1: Analyze task complexity")
    plan = coordinator.decompose_task("issue-payment", task)
    print(f"  → Complexity: {plan.complexity.value}")
    print(f"  → Sub-tasks identified: {len(plan.sub_tasks)}")
    
    print("\nStep 2: Identify required specializations")
    print(f"  → Agents needed: {len(plan.required_agents)}")
    for spec in plan.required_agents:
        print(f"    • {spec}")
    
    print("\nStep 3: Select best agents for each sub-task")
    assignments = coordinator.select_agents(plan)
    print(f"  → {len(assignments)} assignments made")
    
    print("\nStep 4: Create coordination record")
    coordination = coordinator.create_coordination("issue-payment", task)
    print(f"  → Coordination ID: {coordination['id']}")
    print(f"  → Status: {coordination['status']}")
    
    print("\n✓ Complete workflow: analyze → select → coordinate\n")


def example_6_dependency_management():
    """Example 6: Tasks with dependencies"""
    print("\n" + "="*70)
    print("EXAMPLE 6: Dependency Management")
    print("="*70 + "\n")
    
    coordinator = MetaAgentCoordinator()
    
    task = """
    Build a complete data pipeline:
    - Design database schema
    - Implement data collection API
    - Create data processing jobs
    - Build analytics dashboard
    - Add monitoring and alerts
    """
    
    plan = coordinator.decompose_task("issue-pipeline", task)
    
    print("Execution Order (handling dependencies):")
    for i, task_id in enumerate(plan.execution_order, 1):
        subtask = next((st for st in plan.sub_tasks if st.id == task_id), None)
        if subtask:
            print(f"\n  Step {i}: {subtask.description[:50]}...")
            if subtask.dependencies:
                print(f"    Depends on: {', '.join(subtask.dependencies)}")
            else:
                print(f"    No dependencies - can start immediately")
    
    print("\n✓ Dependencies tracked to ensure correct execution order\n")


def main():
    """Run all examples"""
    print("\n" + "="*70)
    print("META-COORDINATOR EXAMPLES")
    print("Demonstrating multi-agent coordination capabilities")
    print("Created by @create-guru")
    print("="*70)
    
    try:
        example_1_simple_task()
        example_2_api_development()
        example_3_refactoring_project()
        example_4_agent_selection()
        example_5_coordination_workflow()
        example_6_dependency_management()
        
        print("\n" + "="*70)
        print("All examples completed successfully! ✨")
        print("="*70 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
