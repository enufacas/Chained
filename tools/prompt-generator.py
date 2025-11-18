#!/usr/bin/env python3
"""
Self-Improving Prompt Generator

Generates optimized prompts for GitHub Copilot interactions and learns from outcomes.
Tracks performance metrics to continuously improve prompt quality.

Enhanced by @engineer-master with learning integration and self-improvement capabilities.

Part of the Chained autonomous AI ecosystem.
Created by @engineer-master - systematic engineering approach inspired by Margaret Hamilton.
"""

import json
import os
import re
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path

# Import learning integration if available
try:
    from prompt_learning_integration import PromptLearningIntegrator
    LEARNING_INTEGRATION_AVAILABLE = True
except ImportError:
    LEARNING_INTEGRATION_AVAILABLE = False


@dataclass
class PromptTemplate:
    """Represents a prompt template with metadata"""
    template_id: str
    category: str  # e.g., "bug_fix", "feature", "refactor", "documentation"
    template: str
    success_count: int = 0
    failure_count: int = 0
    total_uses: int = 0
    avg_resolution_time: float = 0.0  # in hours
    created_at: str = ""
    last_used: str = ""
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate"""
        if self.total_uses == 0:
            return 0.0
        return self.success_count / self.total_uses
    
    @property
    def effectiveness_score(self) -> float:
        """Calculate overall effectiveness (0-1 scale)"""
        if self.total_uses == 0:
            return 0.5  # Neutral score for untested templates
        
        # Weight success rate heavily, but also consider usage count
        # More usage = more confidence in the score
        confidence_factor = min(1.0, self.total_uses / 10.0)
        base_score = self.success_rate * 0.7 + confidence_factor * 0.3
        
        # Penalty for very slow resolution times (>48 hours)
        if self.avg_resolution_time > 48:
            time_penalty = min(0.2, (self.avg_resolution_time - 48) / 240)
            base_score *= (1 - time_penalty)
        
        return base_score


@dataclass
class PromptOutcome:
    """Tracks the outcome of using a prompt"""
    prompt_id: str
    issue_number: int
    success: bool
    resolution_time_hours: float
    agent_used: Optional[str] = None
    error_type: Optional[str] = None
    timestamp: str = ""


class PromptGenerator:
    """
    Self-improving prompt generator for GitHub Copilot interactions.
    
    Features:
    - Template-based prompt generation
    - Performance tracking per template
    - Learning from successes and failures
    - Integration with learning system (TLDR, HN)
    - Agent-specific optimizations
    """
    
    def __init__(self, data_dir: str = "tools/data/prompts", enable_learning: bool = True):
        """Initialize the prompt generator"""
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.templates_file = self.data_dir / "templates.json"
        self.outcomes_file = self.data_dir / "outcomes.json"
        self.insights_file = self.data_dir / "insights.json"
        
        self.templates: Dict[str, PromptTemplate] = {}
        self.outcomes: List[PromptOutcome] = []
        self.insights: Dict[str, Any] = {}
        
        # Initialize learning integration
        self.learning_integrator = None
        if enable_learning and LEARNING_INTEGRATION_AVAILABLE:
            try:
                self.learning_integrator = PromptLearningIntegrator()
                self._refresh_learnings()
            except Exception as e:
                print(f"Warning: Could not initialize learning integration: {e}")
        
        self._load_data()
        self._initialize_default_templates()
    
    def _load_data(self):
        """Load existing data from files"""
        # Load templates
        if self.templates_file.exists():
            with open(self.templates_file, 'r') as f:
                data = json.load(f)
                self.templates = {
                    tid: PromptTemplate(**tdata) 
                    for tid, tdata in data.items()
                }
        
        # Load outcomes
        if self.outcomes_file.exists():
            with open(self.outcomes_file, 'r') as f:
                data = json.load(f)
                self.outcomes = [PromptOutcome(**o) for o in data]
        
        # Load insights
        if self.insights_file.exists():
            with open(self.insights_file, 'r') as f:
                self.insights = json.load(f)
    
    def _save_data(self):
        """Save all data to files"""
        # Save templates
        with open(self.templates_file, 'w') as f:
            json.dump(
                {tid: asdict(t) for tid, t in self.templates.items()},
                f,
                indent=2
            )
        
        # Save outcomes
        with open(self.outcomes_file, 'w') as f:
            json.dump(
                [asdict(o) for o in self.outcomes],
                f,
                indent=2
            )
        
        # Save insights
        with open(self.insights_file, 'w') as f:
            json.dump(self.insights, f, indent=2)
    
    def _initialize_default_templates(self):
        """Initialize default prompt templates if not present"""
        default_templates = [
            {
                "template_id": "bug_fix_systematic",
                "category": "bug_fix",
                "template": """**@{agent}** - Please fix this bug using a systematic approach:

1. **Analyze**: Reproduce and understand the bug's root cause
2. **Plan**: Design the minimal fix that addresses the root cause
3. **Implement**: Apply the fix with defensive programming
4. **Validate**: Test the fix thoroughly, including edge cases
5. **Document**: Add comments explaining the fix and any trade-offs

**Key Principles:**
- Make minimal, surgical changes
- Add tests to prevent regression
- Consider all failure modes
- Follow existing code patterns

Issue details:
{issue_body}"""
            },
            {
                "template_id": "feature_rigorous",
                "category": "feature",
                "template": """**@{agent}** - Please implement this feature with rigorous engineering:

1. **Requirements Analysis**: Understand all requirements and edge cases
2. **Architecture Design**: Plan the implementation structure
3. **Implementation**: Build with attention to detail and correctness
4. **Comprehensive Testing**: Test all functionality including error conditions
5. **Documentation**: Document the feature design and usage

**Engineering Standards:**
- Follow project conventions
- Write clean, maintainable code
- Include comprehensive tests
- Handle all error conditions
- Document design decisions

Feature request:
{issue_body}"""
            },
            {
                "template_id": "refactor_systematic",
                "category": "refactor",
                "template": """**@{agent}** - Please refactor this code systematically:

1. **Understand Current State**: Analyze existing code patterns
2. **Identify Issues**: Document code smells and technical debt
3. **Plan Refactoring**: Design improvements with minimal risk
4. **Execute**: Apply changes incrementally with tests
5. **Validate**: Ensure no behavior changes (only structure)

**Refactoring Principles:**
- Preserve existing behavior
- Make incremental changes
- Keep tests passing
- Improve readability and maintainability
- Follow established patterns

Refactoring target:
{issue_body}"""
            },
            {
                "template_id": "documentation_precise",
                "category": "documentation",
                "template": """**@{agent}** - Please create precise documentation:

1. **Understand Context**: Review the code/feature thoroughly
2. **Identify Audience**: Determine who needs this documentation
3. **Structure Content**: Organize information logically
4. **Write Clearly**: Use clear, concise language with examples
5. **Validate**: Ensure accuracy and completeness

**Documentation Standards:**
- Clear and concise language
- Practical examples
- Consistent formatting
- Accurate technical details
- Easy to navigate

Documentation needed for:
{issue_body}"""
            },
            {
                "template_id": "investigation_thorough",
                "category": "investigation",
                "template": """**@{agent}** - Please investigate this issue thoroughly:

1. **Gather Data**: Collect all relevant information and logs
2. **Analyze Patterns**: Look for trends and root causes
3. **Form Hypothesis**: Develop theories about the issue
4. **Test Theories**: Validate hypotheses with evidence
5. **Report Findings**: Document conclusions and recommendations

**Investigation Approach:**
- Follow evidence
- Document assumptions
- Test theories rigorously
- Provide clear conclusions
- Recommend next steps

Investigation target:
{issue_body}"""
            },
            {
                "template_id": "security_defensive",
                "category": "security",
                "template": """**@{agent}** - Please address this security issue with defensive programming:

1. **Threat Analysis**: Understand the security vulnerability
2. **Impact Assessment**: Determine severity and scope
3. **Design Fix**: Plan secure solution with defense in depth
4. **Implement**: Apply fix with security best practices
5. **Validate**: Test security measures thoroughly

**Security Principles:**
- Follow principle of least privilege
- Validate all inputs
- Use secure defaults
- Handle errors securely
- Document security decisions

Security issue:
{issue_body}"""
            }
        ]
        
        for template_data in default_templates:
            template_id = template_data["template_id"]
            if template_id not in self.templates:
                template_data["created_at"] = datetime.now(timezone.utc).isoformat()
                self.templates[template_id] = PromptTemplate(**template_data)
        
        # Save if we added new templates
        if default_templates:
            self._save_data()
    
    def generate_prompt(
        self,
        issue_body: str,
        category: str,
        agent: str = "engineer-master",
        learning_context: Optional[List[str]] = None,
        enable_learning_enhancement: bool = True
    ) -> Tuple[str, str]:
        """
        Generate an optimized prompt for a given issue.
        
        Args:
            issue_body: The issue description
            category: Issue category (bug_fix, feature, etc.)
            agent: The agent name to use (default: engineer-master)
            learning_context: Recent learnings to incorporate (optional)
            enable_learning_enhancement: Whether to auto-enhance with learnings
        
        Returns:
            Tuple of (prompt, template_id)
        """
        # Select best template for category
        template = self._select_best_template(category)
        
        # Generate prompt from template
        prompt = template.template.format(
            agent=agent,
            issue_body=issue_body
        )
        
        # Enhance with learning context if enabled
        if enable_learning_enhancement:
            prompt = self._enhance_with_learnings(prompt, learning_context, category)
        
        # Update template usage
        template.total_uses += 1
        template.last_used = datetime.now(timezone.utc).isoformat()
        self._save_data()
        
        return prompt, template.template_id
    
    def _select_best_template(self, category: str) -> PromptTemplate:
        """Select the best performing template for a category"""
        category_templates = [
            t for t in self.templates.values() 
            if t.category == category
        ]
        
        if not category_templates:
            # Fallback to a generic template or create one
            return self._get_or_create_generic_template(category)
        
        # Sort by effectiveness score
        category_templates.sort(
            key=lambda t: t.effectiveness_score,
            reverse=True
        )
        
        return category_templates[0]
    
    def _get_or_create_generic_template(self, category: str) -> PromptTemplate:
        """Get or create a generic template for a category"""
        template_id = f"{category}_generic"
        
        if template_id not in self.templates:
            self.templates[template_id] = PromptTemplate(
                template_id=template_id,
                category=category,
                template="""**@{agent}** - Please address this {category} issue:

{issue_body}

Follow best practices and the systematic approach defined in your agent profile.""".format(
                    agent="{agent}",
                    category=category,
                    issue_body="{issue_body}"
                ),
                created_at=datetime.now(timezone.utc).isoformat()
            )
            self._save_data()
        
        return self.templates[template_id]
    
    def _refresh_learnings(self, days: int = 7):
        """Refresh learnings from external sources"""
        if not self.learning_integrator:
            return
        
        try:
            # Extract new learnings
            new_insights = self.learning_integrator.extract_learnings_from_tldr(days)
            
            # Analyze trends
            self.learning_integrator.analyze_trending_topics(days)
            
            # Update insights
            stats = self.learning_integrator.get_learning_statistics()
            self.insights["learning_integration"] = {
                "last_refresh": datetime.now(timezone.utc).isoformat(),
                "total_insights": stats["total_insights"],
                "categories": stats["categories"]
            }
        except Exception as e:
            print(f"Warning: Could not refresh learnings: {e}")
    
    def _enhance_with_learnings(
        self,
        prompt: str,
        learning_context: Optional[List[str]],
        category: str = "feature"
    ) -> str:
        """Enhance prompt with recent learnings"""
        # If learning_context is explicitly provided (even if empty), use it and don't fall back to integrator
        if learning_context is not None:
            # Only add learning section if there are actual items
            if len(learning_context) > 0:
                learning_section = "\n\n**Recent Relevant Learnings:**\n"
                for idx, learning in enumerate(learning_context[:3], 1):
                    learning_section += f"{idx}. {learning}\n"
                
                learning_section += "\nConsider these recent insights when approaching this task.\n"
                
                return prompt + learning_section
            # If empty list explicitly provided, don't add any learnings
            return prompt
        
        # Get learnings from integrator if available (only when learning_context is None)
        if self.learning_integrator:
            try:
                # Get relevant insights
                insights = self.learning_integrator.get_relevant_insights(
                    prompt_category=category,
                    limit=3,
                    min_relevance=0.6
                )
                
                if insights:
                    learning_section = "\n\n**Recent Relevant Learnings:**\n"
                    for idx, insight in enumerate(insights, 1):
                        learning_section += f"{idx}. {insight.title}\n"
                    
                    learning_section += "\nConsider these recent insights from the tech community when approaching this task.\n"
                    
                    return prompt + learning_section
            except Exception as e:
                print(f"Warning: Could not enhance with learnings: {e}")
        
        return prompt
    
    def record_outcome(
        self,
        prompt_id: str,
        issue_number: int,
        success: bool,
        resolution_time_hours: float,
        agent_used: Optional[str] = None,
        error_type: Optional[str] = None
    ):
        """
        Record the outcome of using a prompt.
        
        Args:
            prompt_id: The template ID that was used
            issue_number: The GitHub issue number
            success: Whether the task was completed successfully
            resolution_time_hours: Time taken to resolve (in hours)
            agent_used: Which agent was used
            error_type: Type of error if failed
        """
        outcome = PromptOutcome(
            prompt_id=prompt_id,
            issue_number=issue_number,
            success=success,
            resolution_time_hours=resolution_time_hours,
            agent_used=agent_used,
            error_type=error_type,
            timestamp=datetime.now(timezone.utc).isoformat()
        )
        
        self.outcomes.append(outcome)
        
        # Update template statistics
        if prompt_id in self.templates:
            template = self.templates[prompt_id]
            if success:
                template.success_count += 1
            else:
                template.failure_count += 1
            
            # Update average resolution time (moving average)
            if template.avg_resolution_time == 0:
                template.avg_resolution_time = resolution_time_hours
            else:
                # Weighted average favoring recent data
                alpha = 0.3  # Weight for new data
                template.avg_resolution_time = (
                    alpha * resolution_time_hours +
                    (1 - alpha) * template.avg_resolution_time
                )
        
        self._save_data()
        self._update_insights()
    
    def _update_insights(self):
        """Update insights based on collected outcomes"""
        if not self.outcomes:
            return
        
        # Calculate recent performance (last 30 days)
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=30)
        recent_outcomes = [
            o for o in self.outcomes
            if datetime.fromisoformat(o.timestamp) > cutoff_date
        ]
        
        if not recent_outcomes:
            return
        
        # Overall statistics
        total_recent = len(recent_outcomes)
        successful_recent = sum(1 for o in recent_outcomes if o.success)
        
        self.insights["overall"] = {
            "total_prompts_used": total_recent,
            "success_rate": successful_recent / total_recent if total_recent > 0 else 0,
            "avg_resolution_time": sum(o.resolution_time_hours for o in recent_outcomes) / total_recent,
            "last_updated": datetime.now(timezone.utc).isoformat()
        }
        
        # Per-category insights
        category_stats = {}
        for template in self.templates.values():
            category = template.category
            if category not in category_stats:
                category_stats[category] = {
                    "best_template": template.template_id,
                    "success_rate": template.success_rate,
                    "avg_time": template.avg_resolution_time,
                    "total_uses": template.total_uses
                }
            elif template.effectiveness_score > self.templates[category_stats[category]["best_template"]].effectiveness_score:
                category_stats[category] = {
                    "best_template": template.template_id,
                    "success_rate": template.success_rate,
                    "avg_time": template.avg_resolution_time,
                    "total_uses": template.total_uses
                }
        
        self.insights["by_category"] = category_stats
        
        # Identify patterns in failures
        failures = [o for o in recent_outcomes if not o.success]
        if failures:
            error_counts = {}
            for failure in failures:
                error_type = failure.error_type or "unknown"
                error_counts[error_type] = error_counts.get(error_type, 0) + 1
            
            self.insights["common_failures"] = error_counts
        
        self._save_data()
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Generate a performance report"""
        report = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "templates": {},
            "insights": self.insights
        }
        
        # Sort templates by effectiveness
        sorted_templates = sorted(
            self.templates.values(),
            key=lambda t: t.effectiveness_score,
            reverse=True
        )
        
        for template in sorted_templates:
            report["templates"][template.template_id] = {
                "category": template.category,
                "success_rate": template.success_rate,
                "effectiveness_score": template.effectiveness_score,
                "total_uses": template.total_uses,
                "avg_resolution_time": template.avg_resolution_time
            }
        
        return report
    
    def optimize_templates(self):
        """
        Analyze performance and suggest template improvements.
        This is called periodically to evolve templates based on outcomes.
        """
        if len(self.outcomes) < 10:
            return []  # Need more data to optimize
        
        optimization_suggestions = []
        
        for template in self.templates.values():
            if template.total_uses < 5:
                continue  # Not enough data
            
            # Identify underperforming templates
            if template.effectiveness_score < 0.4:
                optimization_suggestions.append({
                    "template_id": template.template_id,
                    "issue": "low_effectiveness",
                    "score": template.effectiveness_score,
                    "recommendation": "Consider revising template or deprecating"
                })
            
            # Identify templates with high failure rates
            if template.success_rate < 0.5 and template.total_uses >= 5:
                # Analyze failure patterns
                template_failures = [
                    o for o in self.outcomes
                    if o.prompt_id == template.template_id and not o.success
                ]
                
                if template_failures:
                    error_types = {}
                    for failure in template_failures:
                        error_type = failure.error_type or "unknown"
                        error_types[error_type] = error_types.get(error_type, 0) + 1
                    
                    optimization_suggestions.append({
                        "template_id": template.template_id,
                        "issue": "high_failure_rate",
                        "success_rate": template.success_rate,
                        "common_errors": error_types,
                        "recommendation": f"Address common error patterns: {', '.join(error_types.keys())}"
                    })
        
        self.insights["optimization_suggestions"] = optimization_suggestions
        self._save_data()
        
        return optimization_suggestions
    
    def evolve_template(self, template_id: str, mutation_type: str = "enhance") -> Optional[PromptTemplate]:
        """
        Create an evolved version of a template based on performance data.
        
        Args:
            template_id: The template to evolve
            mutation_type: Type of evolution ("enhance", "simplify", "focus")
        
        Returns:
            New evolved PromptTemplate or None if evolution not possible
        """
        if template_id not in self.templates:
            return None
        
        base_template = self.templates[template_id]
        
        # Only evolve templates with sufficient data
        if base_template.total_uses < 10:
            return None
        
        # Create variation based on mutation type
        new_template_id = f"{template_id}_{mutation_type}_v2"
        
        # Don't create duplicates
        if new_template_id in self.templates:
            return None
        
        # Generate evolved template text based on performance insights
        evolved_text = self._mutate_template_text(
            base_template.template,
            mutation_type,
            base_template.category
        )
        
        if not evolved_text:
            return None
        
        # Create new template
        new_template = PromptTemplate(
            template_id=new_template_id,
            category=base_template.category,
            template=evolved_text,
            created_at=datetime.now(timezone.utc).isoformat()
        )
        
        self.templates[new_template_id] = new_template
        self._save_data()
        
        return new_template
    
    def _mutate_template_text(self, base_text: str, mutation_type: str, category: str) -> Optional[str]:
        """Mutate template text based on mutation type and learnings"""
        if mutation_type == "enhance":
            # Add more specific guidance based on category
            if category == "bug_fix":
                addition = "\n**Additional Debugging Steps:**\n- Check logs for stack traces\n- Verify input validation\n- Review recent code changes\n"
                return base_text + addition
            elif category == "feature":
                addition = "\n**Feature Development Best Practices:**\n- Start with minimal viable implementation\n- Add comprehensive tests from the start\n- Document API contracts clearly\n"
                return base_text + addition
        
        elif mutation_type == "simplify":
            # Remove less important sections for faster execution
            lines = base_text.split('\n')
            # Keep first 60% of lines (remove verbose explanations)
            simplified = '\n'.join(lines[:int(len(lines) * 0.6)])
            return simplified if len(simplified) > 100 else None
        
        elif mutation_type == "focus":
            # Emphasize the most critical aspects based on learnings
            if "**Key Principles:**" in base_text:
                # Already has focus section
                return None
            
            focus_section = "\n**CRITICAL FOCUS AREAS:**\n- Test your changes thoroughly\n- Follow existing patterns strictly\n- Document all assumptions\n"
            return base_text + focus_section
        
        return None
    
    def enable_ab_testing(self, template_id_a: str, template_id_b: str) -> Dict[str, Any]:
        """
        Enable A/B testing between two templates.
        
        Args:
            template_id_a: First template to test
            template_id_b: Second template to test
        
        Returns:
            A/B test configuration
        """
        if template_id_a not in self.templates or template_id_b not in self.templates:
            return {"error": "One or both templates not found"}
        
        ab_test_config = {
            "test_id": f"ab_{template_id_a}_vs_{template_id_b}",
            "template_a": template_id_a,
            "template_b": template_id_b,
            "start_date": datetime.now(timezone.utc).isoformat(),
            "status": "active",
            "results": {
                "a_uses": 0,
                "b_uses": 0,
                "a_success": 0,
                "b_success": 0
            }
        }
        
        # Store in insights
        if "ab_tests" not in self.insights:
            self.insights["ab_tests"] = []
        
        self.insights["ab_tests"].append(ab_test_config)
        self._save_data()
        
        return ab_test_config
    
    def get_ab_test_results(self, test_id: str) -> Optional[Dict[str, Any]]:
        """Get results of an A/B test"""
        if "ab_tests" not in self.insights:
            return None
        
        for test in self.insights["ab_tests"]:
            if test["test_id"] == test_id:
                # Calculate current results
                template_a = self.templates.get(test["template_a"])
                template_b = self.templates.get(test["template_b"])
                
                if template_a and template_b:
                    test["results"]["a_effectiveness"] = template_a.effectiveness_score
                    test["results"]["b_effectiveness"] = template_b.effectiveness_score
                    test["results"]["winner"] = "a" if template_a.effectiveness_score > template_b.effectiveness_score else "b"
                
                return test
        
        return None


def main():
    """CLI interface for the prompt generator"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Self-improving prompt generator for GitHub Copilot"
    )
    parser.add_argument(
        "command",
        choices=["generate", "record", "report", "optimize", "evolve", "ab-test", "refresh-learnings"],
        help="Command to execute"
    )
    parser.add_argument("--issue-body", help="Issue body for prompt generation")
    parser.add_argument("--category", help="Issue category")
    parser.add_argument("--agent", default="engineer-master", help="Agent to use")
    parser.add_argument("--prompt-id", help="Prompt ID for recording outcome")
    parser.add_argument("--issue-number", type=int, help="Issue number")
    parser.add_argument("--success", action="store_true", help="Task succeeded")
    parser.add_argument("--resolution-time", type=float, help="Resolution time in hours")
    parser.add_argument("--error-type", help="Error type if failed")
    parser.add_argument("--template-id", help="Template ID for evolution")
    parser.add_argument("--mutation", default="enhance", choices=["enhance", "simplify", "focus"], help="Mutation type")
    parser.add_argument("--template-a", help="First template for A/B testing")
    parser.add_argument("--template-b", help="Second template for A/B testing")
    parser.add_argument("--test-id", help="A/B test ID")
    parser.add_argument("--days", type=int, default=7, help="Days to look back for learnings")
    
    args = parser.parse_args()
    
    generator = PromptGenerator()
    
    if args.command == "generate":
        if not args.issue_body or not args.category:
            print("Error: --issue-body and --category required for generate")
            return 1
        
        prompt, template_id = generator.generate_prompt(
            args.issue_body,
            args.category,
            args.agent
        )
        
        print(f"Template ID: {template_id}")
        print(f"\nGenerated Prompt:\n{prompt}")
        
    elif args.command == "record":
        if not all([args.prompt_id, args.issue_number, args.resolution_time]):
            print("Error: --prompt-id, --issue-number, and --resolution-time required")
            return 1
        
        generator.record_outcome(
            args.prompt_id,
            args.issue_number,
            args.success,
            args.resolution_time,
            args.agent,
            args.error_type
        )
        print(f"Recorded outcome for prompt {args.prompt_id}")
        
    elif args.command == "report":
        report = generator.get_performance_report()
        print(json.dumps(report, indent=2))
        
    elif args.command == "optimize":
        suggestions = generator.optimize_templates()
        # Always output JSON for consistency
        print(json.dumps(suggestions if suggestions else [], indent=2))
    
    elif args.command == "evolve":
        if not args.template_id:
            print("Error: --template-id required for evolve")
            return 1
        
        new_template = generator.evolve_template(args.template_id, args.mutation)
        if new_template:
            print(f"Created evolved template: {new_template.template_id}")
            print(f"Category: {new_template.category}")
            print(f"\nTemplate text preview:")
            print(new_template.template[:300] + "...")
        else:
            print(f"Could not evolve template {args.template_id}")
    
    elif args.command == "ab-test":
        if args.test_id:
            # Get test results
            results = generator.get_ab_test_results(args.test_id)
            if results:
                print(json.dumps(results, indent=2))
            else:
                print(f"Test {args.test_id} not found")
        elif args.template_a and args.template_b:
            # Start new test
            config = generator.enable_ab_testing(args.template_a, args.template_b)
            print(json.dumps(config, indent=2))
        else:
            print("Error: Provide --test-id to view results or --template-a and --template-b to start test")
            return 1
    
    elif args.command == "refresh-learnings":
        if generator.learning_integrator:
            print(f"Refreshing learnings from last {args.days} days...")
            generator._refresh_learnings(args.days)
            stats = generator.learning_integrator.get_learning_statistics()
            print(f"Total insights: {stats['total_insights']}")
            print(f"Categories: {stats['categories']}")
        else:
            print("Learning integration not available")
    
    return 0


if __name__ == "__main__":
    exit(main())
