#!/usr/bin/env python3
"""
Self-Improving Prompt Generator - Orchestrator

Comprehensive self-improving system that generates, tracks, learns, and optimizes
prompts for GitHub Copilot. Integrates all prompt-related components into a
unified system with continuous improvement capabilities.

Features:
- Template-based prompt generation with agent specialization
- Performance tracking and quality scoring
- Learning integration from TLDR, Hacker News, and past outcomes
- Contextual adaptation based on issue details
- A/B testing for template variations
- Automated feedback loops for continuous improvement

Architecture:
  Generate → Track → Learn → Adapt → Improve (feedback loop)

Created by @create-botter - infrastructure creation inspired by Nikola Tesla.
Part of the Chained autonomous AI ecosystem.
"""

import json
import os
import random
import statistics
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict

# Import existing components
try:
    from prompt_learning_integration import PromptLearningIntegrator
    LEARNING_AVAILABLE = True
except ImportError:
    LEARNING_AVAILABLE = False
    print("Warning: Learning integration not available")

try:
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "prompt_quality_scorer",
        Path(__file__).parent / "prompt-quality-scorer.py"
    )
    quality_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(quality_module)
    PromptQualityScorer = quality_module.PromptQualityScorer
    QUALITY_SCORER_AVAILABLE = True
except Exception:
    QUALITY_SCORER_AVAILABLE = False
    print("Warning: Quality scorer not available")

try:
    from contextual_prompt_adapter import ContextualPromptAdapter
    ADAPTER_AVAILABLE = True
except ImportError:
    ADAPTER_AVAILABLE = False
    print("Warning: Contextual adapter not available")


@dataclass
class PromptGenerationRequest:
    """Request for prompt generation"""
    issue_number: int
    issue_title: str
    issue_body: str
    issue_labels: List[str]
    agent_name: str
    category: Optional[str] = None


@dataclass
class GeneratedPrompt:
    """Generated prompt with metadata"""
    prompt_id: str
    prompt_text: str
    template_id: str
    agent_name: str
    category: str
    quality_score: float
    generated_at: str
    learning_insights_used: int = 0
    ab_test_variant: Optional[str] = None


@dataclass
class PromptFeedback:
    """Feedback on prompt performance"""
    prompt_id: str
    success: bool
    resolution_time_hours: float
    quality_rating: Optional[float] = None  # 0-1 scale
    notes: Optional[str] = None


class SelfImprovingPromptGenerator:
    """
    Orchestrates the self-improving prompt generation system.
    
    Components:
    1. Template Management - Base prompt templates by category
    2. Learning Integration - Extract insights from external sources
    3. Quality Scoring - Track and score prompt effectiveness
    4. Contextual Adaptation - Customize prompts for agents/issues
    5. A/B Testing - Test prompt variations
    6. Feedback Loop - Learn from outcomes to improve
    """
    
    def __init__(self, data_dir: str = "tools/data/prompts"):
        """Initialize the self-improving prompt generator"""
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Data files
        self.templates_file = self.data_dir / "templates.json"
        self.prompts_file = self.data_dir / "generated_prompts.json"
        self.feedback_file = self.data_dir / "prompt_feedback.json"
        self.ab_tests_file = self.data_dir / "ab_tests.json"
        self.config_file = self.data_dir / "generator_config.json"
        
        # State
        self.templates: Dict[str, Any] = {}
        self.generated_prompts: List[GeneratedPrompt] = []
        self.feedback: List[PromptFeedback] = []
        self.ab_tests: Dict[str, Any] = {}
        self.config: Dict[str, Any] = {}
        
        # Initialize components
        self.learning_integrator = None
        self.quality_scorer = None
        self.contextual_adapter = None
        
        if LEARNING_AVAILABLE:
            try:
                self.learning_integrator = PromptLearningIntegrator()
            except Exception as e:
                print(f"Warning: Could not initialize learning integrator: {e}")
        
        if QUALITY_SCORER_AVAILABLE:
            try:
                self.quality_scorer = PromptQualityScorer(data_dir=str(self.data_dir))
            except Exception as e:
                print(f"Warning: Could not initialize quality scorer: {e}")
        
        if ADAPTER_AVAILABLE:
            try:
                self.contextual_adapter = ContextualPromptAdapter()
            except Exception as e:
                print(f"Warning: Could not initialize contextual adapter: {e}")
        
        # Load data and initialize defaults
        self._initialize_defaults()
        self._load_data()
    
    def _load_data(self):
        """Load all data files"""
        # Only load templates if file exists, otherwise keep defaults
        if self.templates_file.exists():
            with open(self.templates_file, 'r') as f:
                loaded_templates = json.load(f)
                # Merge with defaults, prioritizing loaded data
                for key, value in loaded_templates.items():
                    self.templates[key] = value
        
        if self.prompts_file.exists():
            with open(self.prompts_file, 'r') as f:
                data = json.load(f)
                self.generated_prompts = [GeneratedPrompt(**p) for p in data]
        
        if self.feedback_file.exists():
            with open(self.feedback_file, 'r') as f:
                data = json.load(f)
                self.feedback = [PromptFeedback(**f) for f in data]
        
        if self.ab_tests_file.exists():
            with open(self.ab_tests_file, 'r') as f:
                self.ab_tests = json.load(f)
        
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                loaded_config = json.load(f)
                # Merge with defaults, prioritizing loaded data
                for key, value in loaded_config.items():
                    self.config[key] = value
    
    def _save_data(self):
        """Save all data files"""
        with open(self.templates_file, 'w') as f:
            json.dump(self.templates, f, indent=2)
        
        with open(self.prompts_file, 'w') as f:
            json.dump([asdict(p) for p in self.generated_prompts], f, indent=2)
        
        with open(self.feedback_file, 'w') as f:
            json.dump([asdict(f) for f in self.feedback], f, indent=2)
        
        with open(self.ab_tests_file, 'w') as f:
            json.dump(self.ab_tests, f, indent=2)
        
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def _initialize_defaults(self):
        """Initialize default templates and configuration"""
        if not self.templates:
            self.templates = {
                "feature": {
                    "template_id": "feature_v1",
                    "template": """**@{agent_name}** - Implement new feature

## 🎯 Feature Request

{issue_body}

## 📝 Implementation Guidance

1. **Design**: Plan the architecture and approach
2. **Implement**: Build the feature with clean, maintainable code
3. **Test**: Add comprehensive tests for the new functionality
4. **Document**: Update documentation and add usage examples
5. **Validate**: Ensure the feature works as expected

## ✅ Success Criteria

- Feature works as specified
- Tests cover edge cases
- Documentation is clear
- Code follows repository conventions""",
                    "success_count": 0,
                    "total_uses": 0
                },
                "bug_fix": {
                    "template_id": "bug_fix_v1",
                    "template": """**@{agent_name}** - Fix bug

## 🐛 Bug Report

{issue_body}

## 🔍 Debugging Steps

1. **Reproduce**: Verify the bug exists and understand the conditions
2. **Diagnose**: Identify the root cause
3. **Fix**: Implement a targeted fix
4. **Test**: Add tests to prevent regression
5. **Verify**: Confirm the bug is resolved

## ⚠️ Important

- Preserve existing functionality
- Add regression tests
- Document the fix if non-obvious""",
                    "success_count": 0,
                    "total_uses": 0
                }
            }
        
        if not self.config:
            self.config = {
                "ab_testing_enabled": True,
                "ab_test_traffic_split": 0.2,  # 20% traffic to test variants
                "learning_refresh_interval_hours": 24,
                "quality_threshold": 0.6,
                "auto_improve_enabled": True,
                "last_learning_refresh": None
            }
    
    def generate_prompt(self, request: PromptGenerationRequest) -> GeneratedPrompt:
        """
        Generate an optimized prompt for the given request.
        
        This is the main entry point that orchestrates all components:
        1. Select best template based on category and performance
        2. Integrate learning insights if available
        3. Apply contextual adaptation for agent and issue
        4. Apply A/B testing if enabled
        5. Calculate quality score
        6. Return generated prompt
        
        Args:
            request: PromptGenerationRequest with issue details
            
        Returns:
            GeneratedPrompt with optimized prompt text
        """
        # Determine category if not specified
        category = request.category or self._detect_category(
            request.issue_labels,
            request.issue_title
        )
        
        # Select template (with A/B testing)
        template, ab_variant = self._select_template(category)
        template_id = template.get("template_id", f"{category}_default")
        
        # Start with base template
        prompt_text = template["template"]
        
        # Replace placeholders
        prompt_text = prompt_text.replace("{agent_name}", request.agent_name)
        prompt_text = prompt_text.replace("{issue_body}", request.issue_body)
        
        # Integrate learning insights
        learning_count = 0
        if self.learning_integrator:
            insights = self._get_learning_insights(category)
            if insights:
                learning_section = self._format_learning_insights(insights)
                prompt_text += "\n\n" + learning_section
                learning_count = len(insights)
        
        # Apply contextual adaptation
        if self.contextual_adapter:
            prompt_text = self.contextual_adapter.enhance_prompt_with_context(
                prompt_text,
                request.agent_name,
                request.issue_title,
                request.issue_labels,
                request.issue_body
            )
        
        # Calculate quality score
        quality_score = self._estimate_quality_score(template_id, category)
        
        # Create prompt ID
        prompt_id = f"prompt_{request.issue_number}_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"
        
        # Create generated prompt
        generated = GeneratedPrompt(
            prompt_id=prompt_id,
            prompt_text=prompt_text,
            template_id=template_id,
            agent_name=request.agent_name,
            category=category,
            quality_score=quality_score,
            generated_at=datetime.now(timezone.utc).isoformat(),
            learning_insights_used=learning_count,
            ab_test_variant=ab_variant
        )
        
        # Save
        self.generated_prompts.append(generated)
        self._save_data()
        
        # Update template usage stats
        self._update_template_usage(template_id)
        
        return generated
    
    def _detect_category(self, labels: List[str], title: str) -> str:
        """Detect issue category from labels and title"""
        label_map = {
            'bug': 'bug_fix',
            'feature': 'feature',
            'refactor': 'refactor',
            'documentation': 'documentation',
            'security': 'security',
            'performance': 'performance'
        }
        
        # Check labels first
        for label in labels:
            label_lower = label.lower()
            if label_lower in label_map:
                return label_map[label_lower]
        
        # Check title keywords
        title_lower = title.lower()
        if any(word in title_lower for word in ['bug', 'fix', 'error', 'issue']):
            return 'bug_fix'
        if any(word in title_lower for word in ['feature', 'add', 'implement']):
            return 'feature'
        if any(word in title_lower for word in ['refactor', 'clean', 'improve']):
            return 'refactor'
        if any(word in title_lower for word in ['docs', 'documentation']):
            return 'documentation'
        
        # Default
        return 'feature'
    
    def _select_template(self, category: str) -> Tuple[Dict[str, Any], Optional[str]]:
        """
        Select the best template for the category.
        
        Implements A/B testing if enabled and variants are available.
        
        Returns:
            Tuple of (template, ab_variant_name)
        """
        # Get base template
        if category not in self.templates:
            category = 'feature'  # Fallback
        
        base_template = self.templates[category]
        
        # Check if A/B testing is enabled and we have variants
        if not self.config.get("ab_testing_enabled", True):
            return base_template, None
        
        # Check for A/B test variants
        ab_test_key = f"{category}_ab_test"
        if ab_test_key in self.ab_tests:
            # Decide whether to use variant
            if random.random() < self.config.get("ab_test_traffic_split", 0.2):
                variants = self.ab_tests[ab_test_key].get("variants", [])
                if variants:
                    variant = random.choice(variants)
                    return variant, variant.get("variant_name", "unknown")
        
        return base_template, None
    
    def _get_learning_insights(self, category: str, limit: int = 3) -> List[Any]:
        """Get relevant learning insights for the category"""
        if not self.learning_integrator:
            return []
        
        try:
            # Refresh learnings if needed
            self._maybe_refresh_learnings()
            
            # Get relevant insights
            insights = self.learning_integrator.get_relevant_insights(
                category,
                limit=limit,
                min_relevance=0.6
            )
            
            return insights
        except Exception as e:
            print(f"Warning: Could not get learning insights: {e}")
            return []
    
    def _format_learning_insights(self, insights: List[Any]) -> str:
        """Format learning insights for inclusion in prompt"""
        if not insights:
            return ""
        
        section = "## 💡 Recent Insights\n\n"
        section += "Consider these recent learnings when implementing:\n\n"
        
        for insight in insights[:3]:
            section += f"- **{insight.title}**: {insight.description}\n"
        
        return section
    
    def _estimate_quality_score(self, template_id: str, category: str) -> float:
        """Estimate quality score for a template"""
        if not self.quality_scorer:
            return 0.7  # Default neutral-good score
        
        try:
            metrics = self.quality_scorer.calculate_quality_metrics(template_id)
            return metrics.overall_quality
        except Exception:
            # Fallback to simple calculation based on template stats
            template = self.templates.get(category, {})
            total_uses = template.get("total_uses", 0)
            success_count = template.get("success_count", 0)
            
            if total_uses == 0:
                return 0.7  # Neutral score for new templates
            
            return success_count / total_uses
    
    def _update_template_usage(self, template_id: str):
        """Update template usage counter"""
        for category, template in self.templates.items():
            if template.get("template_id") == template_id:
                template["total_uses"] = template.get("total_uses", 0) + 1
                self._save_data()
                break
    
    def _maybe_refresh_learnings(self):
        """Refresh learnings if interval has passed"""
        if not self.learning_integrator:
            return
        
        interval_hours = self.config.get("learning_refresh_interval_hours", 24)
        last_refresh = self.config.get("last_learning_refresh")
        
        should_refresh = True
        if last_refresh:
            try:
                last_refresh_dt = datetime.fromisoformat(last_refresh)
                hours_since = (datetime.now(timezone.utc) - last_refresh_dt).total_seconds() / 3600
                should_refresh = hours_since >= interval_hours
            except Exception:
                pass
        
        if should_refresh:
            try:
                self.learning_integrator.extract_learnings_from_tldr(days=7)
                self.learning_integrator.analyze_trending_topics(days=7)
                self.config["last_learning_refresh"] = datetime.now(timezone.utc).isoformat()
                self._save_data()
            except Exception as e:
                print(f"Warning: Could not refresh learnings: {e}")
    
    def record_feedback(self, feedback: PromptFeedback):
        """
        Record feedback on a prompt's performance.
        
        This triggers the improvement loop:
        1. Record the feedback
        2. Update template success stats
        3. Trigger auto-improvement if enabled
        
        Args:
            feedback: PromptFeedback with outcome data
        """
        # Save feedback
        self.feedback.append(feedback)
        
        # Find the corresponding prompt
        prompt = None
        for p in self.generated_prompts:
            if p.prompt_id == feedback.prompt_id:
                prompt = p
                break
        
        if not prompt:
            print(f"Warning: Prompt {feedback.prompt_id} not found")
            self._save_data()
            return
        
        # Update template stats
        template = None
        for category, tpl in self.templates.items():
            if tpl.get("template_id") == prompt.template_id:
                template = tpl
                break
        
        if template:
            if feedback.success:
                template["success_count"] = template.get("success_count", 0) + 1
        
        # Save
        self._save_data()
        
        # Trigger auto-improvement if enabled
        if self.config.get("auto_improve_enabled", True):
            self._auto_improve()
    
    def _auto_improve(self):
        """
        Automatically improve templates based on feedback.
        
        Analyzes recent feedback to:
        1. Identify underperforming templates
        2. Test variations for low-performing templates
        3. Promote high-performing variants to defaults
        """
        if not self.feedback:
            return
        
        # Group feedback by template
        template_feedback = {}
        for fb in self.feedback[-50:]:  # Look at recent 50 feedback items
            # Find prompt
            prompt = None
            for p in self.generated_prompts:
                if p.prompt_id == fb.prompt_id:
                    prompt = p
                    break
            
            if prompt:
                tid = prompt.template_id
                if tid not in template_feedback:
                    template_feedback[tid] = []
                template_feedback[tid].append(fb)
        
        # Identify templates needing improvement
        threshold = self.config.get("quality_threshold", 0.6)
        
        for template_id, feedbacks in template_feedback.items():
            if len(feedbacks) < 5:  # Need minimum sample size
                continue
            
            success_rate = sum(1 for f in feedbacks if f.success) / len(feedbacks)
            
            if success_rate < threshold:
                print(f"Template {template_id} below threshold: {success_rate:.2f}")
                # Could trigger variant creation here
                # For now, just log it
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Generate comprehensive performance report"""
        report = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "total_prompts_generated": len(self.generated_prompts),
            "total_feedback_received": len(self.feedback),
            "templates": {},
            "learning_integration": {},
            "ab_tests": {},
            "overall_metrics": {}
        }
        
        # Template performance
        for category, template in self.templates.items():
            template_id = template.get("template_id", category)
            
            # Get feedback for this template
            template_feedbacks = []
            for fb in self.feedback:
                for p in self.generated_prompts:
                    if p.prompt_id == fb.prompt_id and p.template_id == template_id:
                        template_feedbacks.append(fb)
            
            success_count = sum(1 for f in template_feedbacks if f.success)
            total = len(template_feedbacks)
            
            report["templates"][template_id] = {
                "category": category,
                "total_uses": template.get("total_uses", 0),
                "feedback_count": total,
                "success_count": success_count,
                "success_rate": success_count / total if total > 0 else 0,
                "quality_score": self._estimate_quality_score(template_id, category)
            }
        
        # Overall metrics
        if self.feedback:
            total_success = sum(1 for f in self.feedback if f.success)
            report["overall_metrics"]["success_rate"] = total_success / len(self.feedback)
            
            avg_resolution_time = statistics.mean(
                f.resolution_time_hours for f in self.feedback
            )
            report["overall_metrics"]["avg_resolution_time_hours"] = avg_resolution_time
        
        # Learning integration stats
        if self.learning_integrator:
            stats = self.learning_integrator.get_learning_statistics()
            report["learning_integration"] = stats
        
        return report


def main():
    """CLI interface for the self-improving prompt generator"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Self-improving prompt generator for GitHub Copilot"
    )
    parser.add_argument(
        "command",
        choices=["generate", "feedback", "report", "refresh"],
        help="Command to execute"
    )
    
    # Generate command args
    parser.add_argument("--issue", type=int, help="Issue number")
    parser.add_argument("--title", help="Issue title")
    parser.add_argument("--body", help="Issue body")
    parser.add_argument("--labels", help="Comma-separated labels")
    parser.add_argument("--agent", help="Agent name")
    parser.add_argument("--category", help="Issue category")
    
    # Feedback command args
    parser.add_argument("--prompt-id", help="Prompt ID for feedback")
    parser.add_argument("--success", type=bool, help="Was prompt successful")
    parser.add_argument("--resolution-time", type=float, help="Resolution time in hours")
    
    args = parser.parse_args()
    
    generator = SelfImprovingPromptGenerator()
    
    if args.command == "generate":
        if not all([args.issue, args.title, args.agent]):
            print("Error: --issue, --title, and --agent required for generate")
            return 1
        
        request = PromptGenerationRequest(
            issue_number=args.issue,
            issue_title=args.title,
            issue_body=args.body or "",
            issue_labels=args.labels.split(',') if args.labels else [],
            agent_name=args.agent,
            category=args.category
        )
        
        prompt = generator.generate_prompt(request)
        
        print(f"Generated prompt {prompt.prompt_id}")
        print(f"Quality score: {prompt.quality_score:.2f}")
        print(f"Learning insights: {prompt.learning_insights_used}")
        print("\n" + "="*70)
        print(prompt.prompt_text)
        print("="*70)
    
    elif args.command == "feedback":
        if not all([args.prompt_id, args.success is not None, args.resolution_time]):
            print("Error: --prompt-id, --success, and --resolution-time required")
            return 1
        
        feedback = PromptFeedback(
            prompt_id=args.prompt_id,
            success=args.success,
            resolution_time_hours=args.resolution_time
        )
        
        generator.record_feedback(feedback)
        print(f"✓ Recorded feedback for {args.prompt_id}")
    
    elif args.command == "report":
        report = generator.get_performance_report()
        print(json.dumps(report, indent=2))
    
    elif args.command == "refresh":
        if generator.learning_integrator:
            generator.learning_integrator.extract_learnings_from_tldr(days=7)
            generator.learning_integrator.analyze_trending_topics(days=7)
            generator.config["last_learning_refresh"] = datetime.now(timezone.utc).isoformat()
            generator._save_data()
            print("✓ Learnings refreshed")
        else:
            print("Learning integration not available")
    
    return 0


if __name__ == "__main__":
    exit(main())
