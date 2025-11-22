#!/usr/bin/env python3
"""
Agent Learning API - Proactive PR Failure Intelligence

Built by @APIs-architect to enable AI agents to learn from historical PR failures
and improve code generation quality before starting work.

This API provides:
- Proactive guidance queries for agents before task start
- Real-time risk assessment for proposed changes
- Historical learning insights relevant to specific tasks
- Agent-specific improvement recommendations

Architecture:
- RESTful-style CLI interface for workflow integration
- Integrates with existing PR failure learning data
- Provides structured, actionable guidance
- Ensures reliability with fallback mechanisms

Usage:
    # Get proactive guidance for an agent about to start work
    python agent-learning-api.py query --agent AGENT_ID --task-type TYPE --task-description "..."
    
    # Get risk assessment for specific file changes
    python agent-learning-api.py assess-risk --agent AGENT_ID --files file1.py,file2.md
    
    # Get agent-specific best practices
    python agent-learning-api.py best-practices --agent AGENT_ID
    
    # Get warnings about common pitfalls
    python agent-learning-api.py warnings --agent AGENT_ID --task-type TYPE

Examples:
    python agent-learning-api.py query --agent engineer-master --task-type "api-development" \\
        --task-description "Create REST API endpoint for user management"
    
    python agent-learning-api.py assess-risk --agent secure-specialist \\
        --files "src/auth.py,tests/test_auth.py"
"""

import json
import sys
import argparse
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, asdict
from collections import defaultdict, Counter


# Constants
LEARNINGS_DIR = Path("learnings")
PR_FAILURES_FILE = LEARNINGS_DIR / "pr_failures.json"
INTELLIGENCE_DIR = LEARNINGS_DIR / "pr_intelligence"
AGENT_PROFILES_DIR = INTELLIGENCE_DIR / "agent_profiles"
PATTERNS_FILE = INTELLIGENCE_DIR / "code_patterns.json"


@dataclass
class ProactiveGuidance:
    """Structured guidance for an agent before starting work"""
    agent_id: str
    task_type: str
    confidence: float
    risk_level: str  # low, medium, high
    recommendations: List[str]
    warnings: List[str]
    best_practices: List[str]
    similar_failures: List[Dict[str, Any]]
    success_patterns: List[str]
    timestamp: str
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)


@dataclass
class RiskAssessment:
    """Risk assessment for specific file changes"""
    overall_risk: float  # 0.0-1.0
    file_risks: Dict[str, float]
    risk_factors: List[str]
    recommendations: List[str]
    similar_issues: List[int]  # PR numbers
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)


class AgentLearningAPI:
    """
    API for agents to query learning from historical PR failures.
    
    Built by @APIs-architect with focus on:
    - Reliability: Always returns useful guidance, even with limited data
    - Clarity: Structured, actionable responses
    - Integration: Works seamlessly with existing workflows
    - Performance: Fast query responses
    """
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self._load_learning_data()
    
    def log(self, message: str):
        """Log message if verbose mode enabled"""
        if self.verbose:
            print(f"[Agent-Learning-API] {message}", file=sys.stderr)
    
    def _load_learning_data(self):
        """Load all learning data sources"""
        self.log("Loading learning data...")
        
        # Load PR failures
        self.pr_failures = []
        if PR_FAILURES_FILE.exists():
            try:
                with open(PR_FAILURES_FILE) as f:
                    data = json.load(f)
                    self.pr_failures = data.get('failures', [])
                self.log(f"Loaded {len(self.pr_failures)} PR failures")
            except Exception as e:
                self.log(f"Warning: Could not load PR failures: {e}")
        
        # Load code patterns
        self.code_patterns = []
        if PATTERNS_FILE.exists():
            try:
                with open(PATTERNS_FILE) as f:
                    data = json.load(f)
                    self.code_patterns = data.get('patterns', [])
                self.log(f"Loaded {len(self.code_patterns)} code patterns")
            except Exception as e:
                self.log(f"Warning: Could not load code patterns: {e}")
        
        # Load agent profiles
        self.agent_profiles = {}
        if AGENT_PROFILES_DIR.exists():
            for profile_file in AGENT_PROFILES_DIR.glob("*.json"):
                try:
                    with open(profile_file) as f:
                        profile = json.load(f)
                        agent_id = profile.get('agent_id')
                        if agent_id:
                            self.agent_profiles[agent_id] = profile
                except Exception as e:
                    self.log(f"Warning: Could not load profile {profile_file}: {e}")
            self.log(f"Loaded {len(self.agent_profiles)} agent profiles")
    
    def query_guidance(
        self, 
        agent_id: str, 
        task_type: str, 
        task_description: str = ""
    ) -> ProactiveGuidance:
        """
        Get proactive guidance for an agent before starting work.
        
        Args:
            agent_id: The agent requesting guidance
            task_type: Type of task (e.g., "api-development", "refactoring", "testing")
            task_description: Optional description of the task
            
        Returns:
            ProactiveGuidance with recommendations and warnings
        """
        self.log(f"Querying guidance for agent={agent_id}, task={task_type}")
        
        recommendations = []
        warnings = []
        best_practices = []
        similar_failures = []
        success_patterns = []
        
        # Get agent-specific insights
        if agent_id in self.agent_profiles:
            profile = self.agent_profiles[agent_id]
            
            # Extract best practices from agent profile
            if 'best_practices' in profile:
                best_practices.extend(profile['best_practices'])
            
            # Extract patterns to avoid
            if 'avoid_patterns' in profile:
                for pattern in profile['avoid_patterns']:
                    warnings.append(f"⚠️ Avoid: {pattern}")
        
        # Analyze historical failures for this agent
        agent_failures = [
            f for f in self.pr_failures 
            if f.get('agent_id') == agent_id or f.get('author', '').lower() == 'copilot'
        ]
        
        if agent_failures:
            # Extract common failure types
            failure_types = Counter(f.get('failure_type', 'unknown') for f in agent_failures)
            
            if 'ci_failure' in failure_types and failure_types['ci_failure'] > 0:
                warnings.append(f"⚠️ You have {failure_types['ci_failure']} past CI failures. Ensure tests pass locally.")
            
            if 'review_rejection' in failure_types and failure_types['review_rejection'] > 0:
                warnings.append(f"⚠️ You have {failure_types['review_rejection']} past review rejections. Follow code review guidelines carefully.")
            
            # Get most recent failures as similar examples
            recent_failures = sorted(
                agent_failures, 
                key=lambda x: x.get('closed_at', ''), 
                reverse=True
            )[:3]
            
            for failure in recent_failures:
                similar_failures.append({
                    'pr_number': failure.get('pr_number'),
                    'title': failure.get('title'),
                    'failure_type': failure.get('failure_type'),
                    'lesson': f"Review PR #{failure.get('pr_number')} to avoid similar issues"
                })
        
        # Add task-type specific recommendations
        task_recommendations = self._get_task_type_recommendations(task_type)
        recommendations.extend(task_recommendations)
        
        # Add general best practices
        general_practices = self._get_general_best_practices()
        best_practices.extend(general_practices)
        
        # Analyze code patterns for success indicators
        high_success_patterns = [
            p for p in self.code_patterns 
            if p.get('success_rate', 0) > 0.7
        ]
        for pattern in high_success_patterns[:3]:
            success_patterns.append(pattern.get('description', 'Unknown pattern'))
        
        # Calculate risk level
        risk_score = len(agent_failures) / max(len(self.pr_failures), 1) if self.pr_failures else 0
        if risk_score > 0.3:
            risk_level = "high"
        elif risk_score > 0.15:
            risk_level = "medium"
        else:
            risk_level = "low"
        
        # Calculate confidence based on data availability
        confidence = 0.5  # Base confidence
        if agent_id in self.agent_profiles:
            confidence += 0.2
        if agent_failures:
            confidence += 0.2
        if self.code_patterns:
            confidence += 0.1
        
        return ProactiveGuidance(
            agent_id=agent_id,
            task_type=task_type,
            confidence=min(confidence, 1.0),
            risk_level=risk_level,
            recommendations=recommendations or ["Follow repository contribution guidelines"],
            warnings=warnings or ["No specific warnings - you're doing well!"],
            best_practices=best_practices,
            similar_failures=similar_failures,
            success_patterns=success_patterns,
            timestamp=datetime.now(timezone.utc).isoformat()
        )
    
    def assess_file_risk(self, agent_id: str, files: List[str]) -> RiskAssessment:
        """
        Assess risk for specific file changes.
        
        Args:
            agent_id: The agent making the changes
            files: List of file paths to be modified
            
        Returns:
            RiskAssessment with file-specific risk scores
        """
        self.log(f"Assessing risk for {len(files)} files")
        
        file_risks = {}
        risk_factors = []
        recommendations = []
        similar_issues = []
        
        # Analyze each file
        for file_path in files:
            risk = 0.0
            
            # Check if file has been involved in past failures
            # Note: This is a simple heuristic - could be optimized with indexed lookups for large datasets
            failures_with_file = [
                f for f in self.pr_failures
                if file_path in str(f.get('failure_details', {}))
            ]
            
            if failures_with_file:
                risk += 0.3
                risk_factors.append(f"File {file_path} was involved in {len(failures_with_file)} past failures")
                similar_issues.extend([f.get('pr_number') for f in failures_with_file[:2]])
            
            # Check file extension risk patterns
            if file_path.endswith('.py'):
                # Python files - check for common issues
                if 'test' not in file_path:
                    recommendations.append(f"Add tests for {file_path}")
            elif file_path.endswith('.yml') or file_path.endswith('.yaml'):
                risk += 0.1
                recommendations.append(f"Validate YAML syntax for {file_path}")
            
            # Check file location risk
            if '.github/workflows' in file_path:
                risk += 0.2
                risk_factors.append(f"Workflow file {file_path} requires extra care")
                recommendations.append(f"Test workflow {file_path} thoroughly before committing")
            
            file_risks[file_path] = min(risk, 1.0)
        
        overall_risk = sum(file_risks.values()) / len(file_risks) if file_risks else 0.0
        
        return RiskAssessment(
            overall_risk=overall_risk,
            file_risks=file_risks,
            risk_factors=risk_factors or ["No significant risk factors identified"],
            recommendations=recommendations or ["Changes look safe - proceed with testing"],
            similar_issues=list(set(similar_issues))
        )
    
    def get_best_practices(self, agent_id: str) -> List[str]:
        """Get agent-specific best practices"""
        practices = []
        
        if agent_id in self.agent_profiles:
            profile = self.agent_profiles[agent_id]
            practices.extend(profile.get('best_practices', []))
        
        practices.extend(self._get_general_best_practices())
        
        return practices
    
    def get_warnings(self, agent_id: str, task_type: str = "") -> List[str]:
        """Get warnings about common pitfalls"""
        warnings = []
        
        # Agent-specific warnings
        if agent_id in self.agent_profiles:
            profile = self.agent_profiles[agent_id]
            for pattern in profile.get('avoid_patterns', []):
                warnings.append(f"⚠️ Avoid: {pattern}")
        
        # Task-type specific warnings
        if task_type:
            if 'api' in task_type.lower():
                warnings.append("⚠️ Ensure proper input validation and error handling")
            if 'refactor' in task_type.lower():
                warnings.append("⚠️ Don't change behavior - only structure")
            if 'security' in task_type.lower():
                warnings.append("⚠️ Follow OWASP security best practices")
        
        # General warnings from failure patterns
        review_rejections = len([f for f in self.pr_failures if f.get('failure_type') == 'review_rejection'])
        if review_rejections > 10:
            warnings.append(f"⚠️ {review_rejections} recent PRs were rejected in review - focus on code quality")
        
        return warnings or ["No specific warnings - keep up the good work!"]
    
    def _get_task_type_recommendations(self, task_type: str) -> List[str]:
        """Get recommendations specific to task type"""
        recommendations = []
        
        task_lower = task_type.lower()
        
        if 'api' in task_lower:
            recommendations.extend([
                "✅ Design clear, RESTful endpoints",
                "✅ Include comprehensive error handling",
                "✅ Add request/response validation",
                "✅ Document API with examples"
            ])
        elif 'refactor' in task_lower:
            recommendations.extend([
                "✅ Make small, focused changes",
                "✅ Don't change behavior, only structure",
                "✅ Run all tests before and after",
                "✅ Document what and why you refactored"
            ])
        elif 'test' in task_lower:
            recommendations.extend([
                "✅ Test both success and failure cases",
                "✅ Include edge cases",
                "✅ Keep tests independent and isolated",
                "✅ Use descriptive test names"
            ])
        elif 'security' in task_lower:
            recommendations.extend([
                "✅ Validate all inputs",
                "✅ Use parameterized queries",
                "✅ Don't expose sensitive data in logs",
                "✅ Follow principle of least privilege"
            ])
        else:
            recommendations.extend([
                "✅ Follow repository conventions",
                "✅ Write clear, maintainable code",
                "✅ Include tests for new functionality"
            ])
        
        return recommendations
    
    def _get_general_best_practices(self) -> List[str]:
        """Get general best practices applicable to all agents"""
        return [
            "📚 Read existing code to understand patterns",
            "🧪 Test locally before committing",
            "📝 Write clear commit messages",
            "🔍 Review your own changes before creating PR",
            "💬 Respond to review feedback constructively",
            "🎯 Keep PRs focused on single purpose",
            "📊 Include test coverage for new code"
        ]


def main():
    """CLI interface for the Agent Learning API"""
    parser = argparse.ArgumentParser(
        description="Agent Learning API - Proactive PR Failure Intelligence",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Get proactive guidance
    python agent-learning-api.py query --agent engineer-master --task-type api-development
    
    # Assess risk for files
    python agent-learning-api.py assess-risk --agent secure-specialist --files auth.py,tests/test_auth.py
    
    # Get best practices
    python agent-learning-api.py best-practices --agent organize-guru
    
    # Get warnings
    python agent-learning-api.py warnings --agent refactor-champion --task-type refactoring
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Query command
    query_parser = subparsers.add_parser('query', help='Get proactive guidance')
    query_parser.add_argument('--agent', required=True, help='Agent ID')
    query_parser.add_argument('--task-type', required=True, help='Type of task')
    query_parser.add_argument('--task-description', default='', help='Task description')
    query_parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    
    # Assess risk command
    risk_parser = subparsers.add_parser('assess-risk', help='Assess risk for file changes')
    risk_parser.add_argument('--agent', required=True, help='Agent ID')
    risk_parser.add_argument('--files', required=True, help='Comma-separated list of files')
    risk_parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    
    # Best practices command
    practices_parser = subparsers.add_parser('best-practices', help='Get best practices')
    practices_parser.add_argument('--agent', required=True, help='Agent ID')
    practices_parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    
    # Warnings command
    warnings_parser = subparsers.add_parser('warnings', help='Get warnings')
    warnings_parser.add_argument('--agent', required=True, help='Agent ID')
    warnings_parser.add_argument('--task-type', default='', help='Type of task')
    warnings_parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Initialize API
    api = AgentLearningAPI(verbose=args.verbose)
    
    # Execute command
    if args.command == 'query':
        guidance = api.query_guidance(
            args.agent,
            args.task_type,
            args.task_description
        )
        print(guidance.to_json())
    
    elif args.command == 'assess-risk':
        files = [f.strip() for f in args.files.split(',')]
        risk = api.assess_file_risk(args.agent, files)
        print(risk.to_json())
    
    elif args.command == 'best-practices':
        practices = api.get_best_practices(args.agent)
        print(json.dumps({'agent_id': args.agent, 'best_practices': practices}, indent=2))
    
    elif args.command == 'warnings':
        warnings = api.get_warnings(args.agent, args.task_type)
        print(json.dumps({'agent_id': args.agent, 'warnings': warnings}, indent=2))


if __name__ == '__main__':
    main()
