#!/usr/bin/env python3
"""
Meta-Agent Coordinator

Coordinates multiple specialized AI agents to work together on complex tasks.
Provides intelligent task decomposition, agent selection, and collaboration management.

Features:
- Task analysis and decomposition into sub-tasks
- Intelligent agent selection based on specialization and performance
- Multi-agent collaboration coordination
- Dependency tracking between agent tasks
- Performance-based optimization
- Integration with existing agent system

Part of the Chained autonomous AI ecosystem.
"""

import json
import os
import sys
import re
from datetime import datetime, timezone
from typing import Dict, List, Optional, Set, Tuple, Any
from dataclasses import dataclass, field
from pathlib import Path
from enum import Enum


class TaskComplexity(Enum):
    """Complexity levels for tasks"""
    SIMPLE = "simple"          # Single agent, straightforward
    MODERATE = "moderate"      # Single agent, complex
    COMPLEX = "complex"        # Multiple agents, sequential
    HIGHLY_COMPLEX = "highly_complex"  # Multiple agents, parallel + sequential


class TaskStatus(Enum):
    """Status of coordinated tasks"""
    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class SubTask:
    """Represents a decomposed sub-task"""
    id: str
    description: str
    required_specializations: List[str]
    dependencies: List[str] = field(default_factory=list)
    priority: int = 1  # 1-10, higher = more important
    estimated_effort: str = "medium"  # low, medium, high
    status: TaskStatus = TaskStatus.PENDING
    assigned_agent: Optional[str] = None
    completion_criteria: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization"""
        return {
            'id': self.id,
            'description': self.description,
            'required_specializations': self.required_specializations,
            'dependencies': self.dependencies,
            'priority': self.priority,
            'estimated_effort': self.estimated_effort,
            'status': self.status.value,
            'assigned_agent': self.assigned_agent,
            'completion_criteria': self.completion_criteria
        }


@dataclass
class CoordinationPlan:
    """Plan for coordinating multiple agents on a task"""
    task_id: str
    complexity: TaskComplexity
    sub_tasks: List[SubTask]
    execution_order: List[str]  # Task IDs in execution order
    parallel_groups: List[List[str]] = field(default_factory=list)  # Groups that can run in parallel
    estimated_duration: str = "unknown"
    required_agents: Set[str] = field(default_factory=set)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization"""
        return {
            'task_id': self.task_id,
            'complexity': self.complexity.value,
            'sub_tasks': [st.to_dict() for st in self.sub_tasks],
            'execution_order': self.execution_order,
            'parallel_groups': self.parallel_groups,
            'estimated_duration': self.estimated_duration,
            'required_agents': list(self.required_agents)
        }


class MetaAgentCoordinator:
    """
    Coordinates multiple specialized agents to solve complex tasks.
    
    The coordinator analyzes tasks, decomposes them into sub-tasks, selects
    appropriate agents, and manages their collaboration.
    """
    
    # Keyword patterns for identifying task types
    TASK_PATTERNS = {
        'performance': r'\b(optim|performance|speed|slow|efficient|fast|latency|throughput)\b',
        'testing': r'\b(test|coverage|assert|validate|quality assurance|QA)\b',
        'review': r'\b(review|feedback|mentor|best practice|code quality)\b',
        'infrastructure': r'\b(infrastructure|feature|build|tool|pipeline|deploy)\b',
        'api': r'\b(api|endpoint|rest|graphql|interface|service)\b',
        'investigation': r'\b(investigate|analyze|debug|trace|pattern|metric)\b',
        'security': r'\b(security|secure|vulnerability|cve|exploit|auth|access control)\b',
        'refactor': r'\b(refactor|organize|clean|duplication|smell|structure)\b',
        'documentation': r'\b(document|guide|tutorial|readme|explain)\b'
    }
    
    # Specialization to agent type mapping
    SPECIALIZATION_MAP = {
        'performance': ['accelerate-master'],
        'testing': ['assert-specialist'],
        'review': ['coach-master', 'support-master'],
        'infrastructure': ['create-guru', 'engineer-master', 'engineer-wizard'],
        'api': ['engineer-master', 'engineer-wizard'],
        'investigation': ['investigate-champion'],
        'security': ['secure-specialist', 'monitor-champion'],
        'refactor': ['organize-guru'],
        'documentation': ['support-master']
    }
    
    def __init__(self, repo_root: str = None):
        """
        Initialize the meta-agent coordinator.
        
        Args:
            repo_root: Root directory of the repository
        """
        if repo_root:
            self.repo_root = Path(repo_root)
        else:
            # Detect repository root
            current = Path.cwd()
            while current != current.parent:
                if (current / '.git').exists():
                    self.repo_root = current
                    break
                current = current.parent
            else:
                self.repo_root = Path.cwd()
        
        self.registry_path = self.repo_root / '.github/agent-system/registry.json'
        self.coordination_log_path = self.repo_root / '.github/agent-system/coordination_log.json'
        
        # Load agent registry
        self.agents = self._load_agents()
        
        # Load or initialize coordination log
        self.coordination_log = self._load_coordination_log()
    
    def _load_agents(self) -> Dict:
        """Load active agents from registry"""
        try:
            with open(self.registry_path, 'r') as f:
                registry = json.load(f)
            return {
                agent['id']: agent
                for agent in registry.get('agents', [])
                if agent.get('status') == 'active'
            }
        except FileNotFoundError:
            print(f"Warning: Agent registry not found at {self.registry_path}", file=sys.stderr)
            return {}
    
    def _load_coordination_log(self) -> Dict:
        """Load or initialize coordination log"""
        if self.coordination_log_path.exists():
            try:
                with open(self.coordination_log_path, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                print(f"Warning: Invalid coordination log, creating new one", file=sys.stderr)
        
        return {
            'version': '1.0.0',
            'coordinations': [],
            'statistics': {
                'total_coordinations': 0,
                'successful_coordinations': 0,
                'failed_coordinations': 0,
                'avg_agents_per_task': 0.0
            }
        }
    
    def _save_coordination_log(self):
        """Save coordination log to disk"""
        self.coordination_log_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.coordination_log_path, 'w') as f:
            json.dump(self.coordination_log, f, indent=2)
    
    def analyze_task(self, task_description: str, task_context: Dict = None) -> TaskComplexity:
        """
        Analyze a task and determine its complexity.
        
        Args:
            task_description: The task description text
            task_context: Additional context (e.g., issue labels, comments)
        
        Returns:
            TaskComplexity level
        """
        # Count how many different specializations are needed
        task_lower = task_description.lower()
        if task_context:
            task_lower += " " + json.dumps(task_context).lower()
        
        matching_categories = set()
        for category, pattern in self.TASK_PATTERNS.items():
            if re.search(pattern, task_lower, re.IGNORECASE):
                matching_categories.add(category)
        
        # Determine complexity based on matches and task indicators
        num_categories = len(matching_categories)
        
        # Look for complexity indicators
        complexity_keywords = r'\b(multiple|complex|comprehensive|full|complete|entire|system-wide|end-to-end)\b'
        has_complexity_keywords = bool(re.search(complexity_keywords, task_lower, re.IGNORECASE))
        
        if num_categories == 0:
            return TaskComplexity.SIMPLE
        elif num_categories == 1:
            return TaskComplexity.SIMPLE
        elif num_categories == 2:
            # Two categories can be moderate or complex depending on keywords
            return TaskComplexity.COMPLEX if has_complexity_keywords else TaskComplexity.MODERATE
        elif num_categories <= 4:
            return TaskComplexity.COMPLEX
        else:
            return TaskComplexity.HIGHLY_COMPLEX
    
    def decompose_task(self, task_id: str, task_description: str, 
                      task_context: Dict = None) -> CoordinationPlan:
        """
        Decompose a task into sub-tasks and create a coordination plan.
        
        Args:
            task_id: Unique identifier for the task (e.g., issue number)
            task_description: The task description
            task_context: Additional context
        
        Returns:
            CoordinationPlan with sub-tasks and execution order
        """
        complexity = self.analyze_task(task_description, task_context)
        
        # Identify required specializations
        task_lower = task_description.lower()
        if task_context:
            task_lower += " " + json.dumps(task_context).lower()
        
        matching_categories = []
        for category, pattern in self.TASK_PATTERNS.items():
            if re.search(pattern, task_lower, re.IGNORECASE):
                matching_categories.append(category)
        
        # Create sub-tasks based on identified categories
        sub_tasks = []
        task_counter = 1
        
        for category in matching_categories:
            specializations = self.SPECIALIZATION_MAP.get(category, [])
            
            # Create a sub-task for this category
            sub_task = SubTask(
                id=f"{task_id}-subtask-{task_counter}",
                description=f"{category.capitalize()} work: {self._generate_subtask_description(category, task_description)}",
                required_specializations=specializations,
                priority=self._calculate_priority(category, matching_categories),
                estimated_effort=self._estimate_effort(category, complexity)
            )
            
            # Add completion criteria
            sub_task.completion_criteria = self._generate_completion_criteria(category)
            
            sub_tasks.append(sub_task)
            task_counter += 1
        
        # If no specific categories matched, create a generic sub-task
        if not sub_tasks:
            sub_tasks.append(SubTask(
                id=f"{task_id}-subtask-1",
                description=task_description,
                required_specializations=self._infer_specializations(task_description),
                priority=5,
                estimated_effort="medium"
            ))
        
        # Determine execution order and dependencies
        execution_order, parallel_groups = self._determine_execution_order(sub_tasks, matching_categories)
        
        # Collect required agents
        required_agents = set()
        for st in sub_tasks:
            required_agents.update(st.required_specializations)
        
        plan = CoordinationPlan(
            task_id=task_id,
            complexity=complexity,
            sub_tasks=sub_tasks,
            execution_order=execution_order,
            parallel_groups=parallel_groups,
            estimated_duration=self._estimate_duration(complexity, len(sub_tasks)),
            required_agents=required_agents
        )
        
        return plan
    
    def _generate_subtask_description(self, category: str, original_description: str) -> str:
        """Generate a specific description for a sub-task based on category"""
        templates = {
            'performance': 'Analyze and optimize performance bottlenecks',
            'testing': 'Add comprehensive tests and improve coverage',
            'review': 'Review code quality and provide feedback',
            'infrastructure': 'Implement infrastructure and tooling',
            'api': 'Design and implement API endpoints',
            'investigation': 'Investigate and analyze the issue',
            'security': 'Audit and fix security vulnerabilities',
            'refactor': 'Refactor and organize code structure',
            'documentation': 'Create or update documentation'
        }
        
        base_desc = templates.get(category, 'Complete the task')
        
        # Extract key phrases from original description (first 100 chars)
        excerpt = original_description[:100].strip()
        if len(original_description) > 100:
            excerpt += "..."
        
        return f"{base_desc} for: {excerpt}"
    
    def _calculate_priority(self, category: str, all_categories: List[str]) -> int:
        """Calculate priority for a sub-task based on category and context"""
        # Base priorities
        base_priorities = {
            'security': 10,
            'testing': 8,
            'investigation': 7,
            'infrastructure': 6,
            'api': 6,
            'performance': 5,
            'refactor': 4,
            'review': 3,
            'documentation': 2
        }
        
        priority = base_priorities.get(category, 5)
        
        # Adjust based on dependencies (security and testing should come first)
        if category in ['investigation', 'review']:
            priority += 2  # These often need to happen early
        
        return min(priority, 10)
    
    def _estimate_effort(self, category: str, complexity: TaskComplexity) -> str:
        """Estimate effort level for a sub-task"""
        base_efforts = {
            'investigation': 'low',
            'review': 'low',
            'documentation': 'low',
            'testing': 'medium',
            'refactor': 'medium',
            'performance': 'medium',
            'api': 'high',
            'infrastructure': 'high',
            'security': 'high'
        }
        
        base = base_efforts.get(category, 'medium')
        
        # Adjust based on overall complexity
        if complexity == TaskComplexity.HIGHLY_COMPLEX:
            if base == 'low':
                return 'medium'
            elif base == 'medium':
                return 'high'
        
        return base
    
    def _generate_completion_criteria(self, category: str) -> List[str]:
        """Generate completion criteria for a sub-task"""
        criteria_map = {
            'performance': [
                'Performance benchmarks show improvement',
                'No performance regressions introduced',
                'Optimization changes are documented'
            ],
            'testing': [
                'Test coverage increased',
                'All tests pass',
                'Edge cases are covered'
            ],
            'review': [
                'Code review completed',
                'Feedback addressed',
                'Best practices documented'
            ],
            'infrastructure': [
                'Feature implemented and tested',
                'Infrastructure is documented',
                'Integration tests pass'
            ],
            'api': [
                'API endpoints implemented',
                'API documentation complete',
                'API tests pass'
            ],
            'investigation': [
                'Root cause identified',
                'Analysis documented',
                'Recommendations provided'
            ],
            'security': [
                'Vulnerabilities fixed',
                'Security tests pass',
                'Security review completed'
            ],
            'refactor': [
                'Code duplication removed',
                'Code structure improved',
                'No functionality broken'
            ],
            'documentation': [
                'Documentation complete and accurate',
                'Examples provided',
                'Documentation reviewed'
            ]
        }
        
        return criteria_map.get(category, ['Task completed successfully'])
    
    def _infer_specializations(self, description: str) -> List[str]:
        """Infer required specializations from description"""
        # Default to general engineering agents if nothing specific matches
        return ['engineer-master', 'engineer-wizard']
    
    def _determine_execution_order(self, sub_tasks: List[SubTask], 
                                  categories: List[str]) -> Tuple[List[str], List[List[str]]]:
        """
        Determine execution order and identify parallel execution opportunities.
        
        Returns:
            Tuple of (execution_order, parallel_groups)
        """
        # Define dependency rules
        depends_on = {
            'investigation': [],
            'security': ['investigation'],
            'infrastructure': ['investigation', 'security'],
            'api': ['infrastructure', 'investigation'],
            'performance': ['api', 'infrastructure'],
            'refactor': ['investigation', 'testing'],
            'testing': ['api', 'infrastructure', 'performance'],
            'review': ['testing', 'refactor'],
            'documentation': ['review', 'testing']
        }
        
        # Build dependency graph
        for sub_task in sub_tasks:
            category = self._extract_category(sub_task.description)
            deps = depends_on.get(category, [])
            
            # Find sub-tasks that this depends on
            for dep_category in deps:
                for other_task in sub_tasks:
                    if other_task != sub_task:
                        other_category = self._extract_category(other_task.description)
                        if other_category == dep_category:
                            sub_task.dependencies.append(other_task.id)
        
        # Topological sort to get execution order
        execution_order = self._topological_sort(sub_tasks)
        
        # Identify parallel execution groups
        parallel_groups = self._identify_parallel_groups(sub_tasks, execution_order)
        
        return execution_order, parallel_groups
    
    def _extract_category(self, description: str) -> str:
        """Extract category from sub-task description"""
        desc_lower = description.lower()
        
        # Check for category keywords in order of specificity
        # Check for the category name at the start of description first (e.g., "Security work:")
        for category in self.TASK_PATTERNS.keys():
            if desc_lower.startswith(category):
                return category
        
        # Then check if category appears anywhere in the description
        for category in self.TASK_PATTERNS.keys():
            if category in desc_lower:
                return category
        
        return 'general'
    
    def _topological_sort(self, sub_tasks: List[SubTask]) -> List[str]:
        """Perform topological sort on sub-tasks based on dependencies"""
        # Build adjacency list
        task_map = {st.id: st for st in sub_tasks}
        in_degree = {st.id: len(st.dependencies) for st in sub_tasks}
        
        # Find tasks with no dependencies
        queue = [st.id for st in sub_tasks if len(st.dependencies) == 0]
        result = []
        
        while queue:
            # Sort by priority (descending) for stable ordering
            queue.sort(key=lambda tid: task_map[tid].priority, reverse=True)
            task_id = queue.pop(0)
            result.append(task_id)
            
            # Update in-degrees for dependent tasks
            for st in sub_tasks:
                if task_id in st.dependencies:
                    in_degree[st.id] -= 1
                    if in_degree[st.id] == 0:
                        queue.append(st.id)
        
        # If not all tasks are in result, there's a cycle - use original order
        if len(result) != len(sub_tasks):
            print("Warning: Cycle detected in task dependencies, using priority order", file=sys.stderr)
            result = sorted([st.id for st in sub_tasks], 
                          key=lambda tid: task_map[tid].priority, 
                          reverse=True)
        
        return result
    
    def _identify_parallel_groups(self, sub_tasks: List[SubTask], 
                                 execution_order: List[str]) -> List[List[str]]:
        """Identify groups of tasks that can run in parallel"""
        task_map = {st.id: st for st in sub_tasks}
        parallel_groups = []
        
        # Group tasks by dependency level
        levels = {}
        for task_id in execution_order:
            task = task_map[task_id]
            if not task.dependencies:
                level = 0
            else:
                level = max(levels.get(dep, 0) for dep in task.dependencies) + 1
            levels[task_id] = level
        
        # Group tasks at the same level
        max_level = max(levels.values()) if levels else 0
        for level in range(max_level + 1):
            level_tasks = [tid for tid, l in levels.items() if l == level]
            if len(level_tasks) > 1:
                parallel_groups.append(level_tasks)
        
        return parallel_groups
    
    def _estimate_duration(self, complexity: TaskComplexity, num_tasks: int) -> str:
        """
        Estimate duration for completing all tasks.
        
        Args:
            complexity: Task complexity level
            num_tasks: Number of sub-tasks
        
        Returns:
            Duration estimate string
        """
        # Base duration estimates in hours
        base_durations = {
            TaskComplexity.SIMPLE: 2,
            TaskComplexity.MODERATE: 6,
            TaskComplexity.COMPLEX: 16,
            TaskComplexity.HIGHLY_COMPLEX: 40
        }
        
        base = base_durations.get(complexity, 8)
        
        # Adjust for number of tasks (assuming some parallelism)
        adjusted = base + (num_tasks - 1) * 2
        
        if adjusted <= 4:
            return "short (< 4 hours)"
        elif adjusted <= 8:
            return "medium (4-8 hours)"
        elif adjusted <= 24:
            return "long (1-3 days)"
        else:
            return "very long (3+ days)"
    
    def select_agents(self, plan: CoordinationPlan) -> Dict[str, str]:
        """
        Select the best agents for each sub-task based on specialization and performance.
        
        Args:
            plan: CoordinationPlan with sub-tasks
        
        Returns:
            Dictionary mapping sub-task IDs to selected agent IDs
        """
        assignments = {}
        
        for sub_task in plan.sub_tasks:
            # Find agents with matching specialization
            candidates = []
            for agent_id, agent in self.agents.items():
                if agent['specialization'] in sub_task.required_specializations:
                    # Calculate agent score based on metrics
                    score = agent.get('metrics', {}).get('overall_score', 0.0)
                    candidates.append((agent_id, agent, score))
            
            if not candidates:
                print(f"Warning: No agent found for specializations {sub_task.required_specializations}", 
                      file=sys.stderr)
                continue
            
            # Select agent with highest score
            candidates.sort(key=lambda x: x[2], reverse=True)
            selected_agent_id = candidates[0][0]
            
            assignments[sub_task.id] = selected_agent_id
            sub_task.assigned_agent = selected_agent_id
        
        return assignments
    
    def create_coordination(self, task_id: str, task_description: str, 
                          task_context: Dict = None) -> Dict:
        """
        Create a full coordination plan for a task.
        
        Args:
            task_id: Unique task identifier
            task_description: Task description
            task_context: Additional context
        
        Returns:
            Dictionary with coordination plan and agent assignments
        """
        # Decompose task
        plan = self.decompose_task(task_id, task_description, task_context)
        
        # Select agents
        assignments = self.select_agents(plan)
        
        # Log coordination
        coordination = {
            'id': f"coord-{task_id}-{int(datetime.now(timezone.utc).timestamp())}",
            'task_id': task_id,
            'created_at': datetime.now(timezone.utc).isoformat(),
            'plan': plan.to_dict(),
            'assignments': assignments,
            'status': 'active'
        }
        
        self.coordination_log['coordinations'].append(coordination)
        self.coordination_log['statistics']['total_coordinations'] += 1
        
        # Calculate average agents per task
        total_agents = sum(len(c.get('assignments', {})) for c in self.coordination_log['coordinations'])
        total_coords = len(self.coordination_log['coordinations'])
        self.coordination_log['statistics']['avg_agents_per_task'] = total_agents / total_coords if total_coords > 0 else 0.0
        
        self._save_coordination_log()
        
        return coordination
    
    def get_coordination_summary(self, coordination_id: str = None) -> Dict:
        """
        Get a summary of a coordination or all coordinations.
        
        Args:
            coordination_id: Specific coordination ID, or None for all
        
        Returns:
            Summary dictionary
        """
        if coordination_id:
            coord = next((c for c in self.coordination_log['coordinations'] 
                         if c['id'] == coordination_id), None)
            if not coord:
                return {'error': f'Coordination {coordination_id} not found'}
            return coord
        else:
            return {
                'total_coordinations': len(self.coordination_log['coordinations']),
                'statistics': self.coordination_log['statistics'],
                'recent_coordinations': self.coordination_log['coordinations'][-5:]
            }


def main():
    """Command-line interface for meta-agent coordinator"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Meta-Agent Coordinator')
    parser.add_argument('command', choices=['coordinate', 'analyze', 'summary'],
                       help='Command to execute')
    parser.add_argument('--task-id', help='Task ID (e.g., issue number)')
    parser.add_argument('--description', help='Task description')
    parser.add_argument('--context', help='Additional context (JSON string)')
    parser.add_argument('--coordination-id', help='Coordination ID for summary')
    
    args = parser.parse_args()
    
    coordinator = MetaAgentCoordinator()
    
    if args.command == 'coordinate':
        if not args.task_id or not args.description:
            print("Error: --task-id and --description required for coordinate", file=sys.stderr)
            sys.exit(1)
        
        context = json.loads(args.context) if args.context else None
        coordination = coordinator.create_coordination(args.task_id, args.description, context)
        print(json.dumps(coordination, indent=2))
    
    elif args.command == 'analyze':
        if not args.description:
            print("Error: --description required for analyze", file=sys.stderr)
            sys.exit(1)
        
        context = json.loads(args.context) if args.context else None
        complexity = coordinator.analyze_task(args.description, context)
        plan = coordinator.decompose_task(args.task_id or "temp", args.description, context)
        
        result = {
            'complexity': complexity.value,
            'plan': plan.to_dict()
        }
        print(json.dumps(result, indent=2))
    
    elif args.command == 'summary':
        summary = coordinator.get_coordination_summary(args.coordination_id)
        print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
