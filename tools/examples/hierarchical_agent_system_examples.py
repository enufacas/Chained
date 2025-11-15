#!/usr/bin/env python3
"""
Hierarchical Agent System Examples

Demonstrates the usage of the hierarchical agent system with coordinators,
specialists, and workers.

Part of the Chained autonomous AI ecosystem.
"""

import sys
from pathlib import Path

# Add tools directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from hierarchical_agent_system import HierarchicalAgentSystem, AgentRole


def example_1_simple_task():
    """Example 1: Simple documentation task"""
    print("\n" + "="*60)
    print("Example 1: Simple Documentation Task")
    print("="*60 + "\n")
    
    system = HierarchicalAgentSystem()
    
    # Create plan for simple task
    plan, chain = system.create_hierarchical_plan(
        task_id="doc-001",
        task_description="Update README with installation instructions"
    )
    
    print(f"Task Complexity: {plan.complexity.value}")
    print(f"Coordinator: {chain.coordinator_id}")
    print(f"Number of subtasks: {len(plan.sub_tasks)}")
    print(f"\nHierarchy levels: {len(chain.hierarchy)}")
    
    for level in chain.hierarchy:
        print(f"\nLevel {level.get('level', 'N/A')}:")
        if 'agent_id' in level:
            print(f"  Agent: {level['agent_id']}")
            print(f"  Role: {level['role']}")


def example_2_complex_feature():
    """Example 2: Complex feature development"""
    print("\n" + "="*60)
    print("Example 2: Complex Feature Development")
    print("="*60 + "\n")
    
    system = HierarchicalAgentSystem()
    
    # Create plan for complex task
    plan, chain = system.create_hierarchical_plan(
        task_id="feature-001",
        task_description="""
        Implement user authentication system:
        - Security audit of existing code
        - API design and implementation
        - Database schema design
        - Unit and integration tests
        - Performance optimization
        - Comprehensive documentation
        """,
        task_context={'labels': ['feature', 'security', 'api']}
    )
    
    print(f"Task Complexity: {plan.complexity.value}")
    print(f"Coordinator: {chain.coordinator_id}")
    print(f"Number of subtasks: {len(plan.sub_tasks)}")
    print(f"\nSubtasks breakdown:")
    
    for i, subtask in enumerate(plan.sub_tasks, 1):
        print(f"\n{i}. {subtask.description[:80]}...")
        print(f"   Required specializations: {', '.join(subtask.required_specializations)}")
        print(f"   Priority: {subtask.priority}")
        print(f"   Estimated effort: {subtask.estimated_effort}")


def example_3_delegation():
    """Example 3: Task delegation"""
    print("\n" + "="*60)
    print("Example 3: Task Delegation")
    print("="*60 + "\n")
    
    system = HierarchicalAgentSystem()
    
    # Get coordinators and specialists
    coordinators = system.get_coordinator_agents()
    specialists = system.get_specialist_agents()
    
    if coordinators and specialists:
        coordinator_id = coordinators[0]
        specialist_id = specialists[0]
        
        print(f"Coordinator: {coordinator_id}")
        print(f"  Role: {system.agent_tiers[coordinator_id].role.value}")
        print(f"  Specialization: {system.agent_tiers[coordinator_id].specialization}")
        print(f"\nSpecialist: {specialist_id}")
        print(f"  Role: {system.agent_tiers[specialist_id].role.value}")
        print(f"  Specialization: {system.agent_tiers[specialist_id].specialization}")
        
        # Delegate task
        delegation = system.delegate_task(
            from_agent=coordinator_id,
            to_agent=specialist_id,
            task_description="Implement secure authentication endpoints",
            context={'priority': 'high', 'deadline': '2025-11-20'}
        )
        
        print(f"\nDelegation created:")
        print(f"  ID: {delegation['delegation_id']}")
        print(f"  From: {delegation['from_role']} → To: {delegation['to_role']}")
        print(f"  Status: {delegation['status']}")
        print(f"  Created: {delegation['created_at']}")


def example_4_escalation():
    """Example 4: Task escalation"""
    print("\n" + "="*60)
    print("Example 4: Task Escalation")
    print("="*60 + "\n")
    
    system = HierarchicalAgentSystem()
    
    # Get workers
    workers = system.get_worker_agents()
    
    if workers:
        worker_id = workers[0]
        worker_tier = system.agent_tiers[worker_id]
        
        print(f"Worker: {worker_id}")
        print(f"  Role: {worker_tier.role.value}")
        print(f"  Specialization: {worker_tier.specialization}")
        print(f"  Reports to: {worker_tier.reports_to.value if worker_tier.reports_to else 'None'}")
        
        # Escalate task
        escalation = system.escalate_task(
            from_agent=worker_id,
            task_id="subtask-789",
            reason="Task complexity exceeds worker capability - requires architectural decisions"
        )
        
        print(f"\nEscalation created:")
        print(f"  ID: {escalation['escalation_id']}")
        print(f"  From: {escalation['from_role']} → To: {escalation['to_role']}")
        print(f"  Target agent: {escalation['to_agent']}")
        print(f"  Reason: {escalation['reason']}")


def example_5_hierarchy_overview():
    """Example 5: Hierarchy overview"""
    print("\n" + "="*60)
    print("Example 5: Hierarchy Overview")
    print("="*60 + "\n")
    
    system = HierarchicalAgentSystem()
    
    # Get summary
    summary = system.get_hierarchy_summary()
    
    print(f"Total agents: {summary['total_agents']}")
    print(f"\nAgents by role:")
    for role, count in summary['by_role'].items():
        print(f"  {role}: {count}")
    
    print(f"\nCoordinator agents:")
    for agent in summary['coordinator_agents']:
        print(f"  - {agent['agent_id']} ({agent['specialization']})")
    
    print(f"\nSpecialist agents:")
    for agent in summary['specialist_agents']:
        print(f"  - {agent['agent_id']} ({agent['specialization']})")
    
    print(f"\nWorker agents:")
    for agent in summary['worker_agents']:
        print(f"  - {agent['agent_id']} ({agent['specialization']})")
    
    print(f"\nDelegation statistics:")
    stats = summary['statistics']
    print(f"  Total delegations: {stats['total_delegations']}")
    print(f"  Successful: {stats['successful_delegations']}")
    print(f"  Escalations: {stats['escalations']}")


def example_6_role_filtering():
    """Example 6: Filtering agents by role and specialization"""
    print("\n" + "="*60)
    print("Example 6: Filtering Agents by Role")
    print("="*60 + "\n")
    
    system = HierarchicalAgentSystem()
    
    # Get specialists with specific specialization
    print("Engineer specialists:")
    engineers = system.get_specialist_agents('engineer-master')
    for agent_id in engineers:
        tier = system.agent_tiers[agent_id]
        agent = system.base_coordinator.agents[agent_id]
        score = agent.get('metrics', {}).get('overall_score', 0)
        print(f"  - {agent_id}: {tier.specialization} (score: {score:.2f})")
    
    print("\nPerformance workers:")
    perf_workers = system.get_worker_agents('accelerate-master')
    for agent_id in perf_workers:
        tier = system.agent_tiers[agent_id]
        agent = system.base_coordinator.agents[agent_id]
        score = agent.get('metrics', {}).get('overall_score', 0)
        print(f"  - {agent_id}: {tier.specialization} (score: {score:.2f})")


def example_7_multi_level_coordination():
    """Example 7: Multi-level coordination scenario"""
    print("\n" + "="*60)
    print("Example 7: Multi-Level Coordination")
    print("="*60 + "\n")
    
    system = HierarchicalAgentSystem()
    
    # Simulate a complex task that requires all three tiers
    print("Scenario: Building a complete authentication system")
    print("\nLevel 0 - Coordinator receives task:")
    print("  → Analyzes requirements")
    print("  → Breaks down into sub-tasks")
    print("  → Assigns to specialists")
    
    print("\nLevel 1 - Specialists receive sub-tasks:")
    print("  → Engineer-master: API design and implementation")
    print("  → Secure-specialist: Security audit and fixes")
    print("  → Create-guru: Database schema design")
    
    print("\nLevel 2 - Specialists delegate to workers:")
    print("  → Engineer-master delegates to:")
    print("     • Assert-specialist: Write API tests")
    print("     • Accelerate-master: Optimize API performance")
    print("  → Secure-specialist delegates to:")
    print("     • Assert-specialist: Write security tests")
    print("  → Support-master coordinates:")
    print("     • Document-ninja: Write API documentation")
    
    print("\nCoordination flow:")
    coordinators = system.get_coordinator_agents()
    specialists = system.get_specialist_agents()
    workers = system.get_worker_agents()
    
    print(f"  {len(coordinators)} coordinator(s) manage")
    print(f"  {len(specialists)} specialist(s) who oversee")
    print(f"  {len(workers)} worker(s) executing tasks")


def main():
    """Run all examples"""
    print("\n" + "="*60)
    print("Hierarchical Agent System - Usage Examples")
    print("="*60)
    
    examples = [
        example_1_simple_task,
        example_2_complex_feature,
        example_3_delegation,
        example_4_escalation,
        example_5_hierarchy_overview,
        example_6_role_filtering,
        example_7_multi_level_coordination,
    ]
    
    for example in examples:
        try:
            example()
        except Exception as e:
            print(f"\nError in {example.__name__}: {e}")
    
    print("\n" + "="*60)
    print("Examples completed!")
    print("="*60 + "\n")


if __name__ == '__main__':
    main()
