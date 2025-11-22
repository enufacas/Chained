#!/usr/bin/env python3
"""
Prompt Reinforcement Learning Module

Learns from PR review feedback and issue outcomes to continuously improve prompts.
Implements reinforcement learning principles for autonomous prompt optimization.

Part of the self-improving prompt generator system.
Created by @APIs-architect - rigorous and innovative approach inspired by Margaret Hamilton.
"""

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict


@dataclass
class PromptFeedback:
    """Represents feedback on a prompt's effectiveness"""
    prompt_id: str
    issue_number: int
    feedback_type: str  # "pr_review", "issue_resolution", "build_failure", "test_failure"
    sentiment: str  # "positive", "negative", "neutral"
    feedback_text: str
    extracted_patterns: List[str]  # Patterns identified from feedback
    timestamp: str
    

@dataclass
class PromptPattern:
    """Represents a pattern found in successful or unsuccessful prompts"""
    pattern: str
    pattern_type: str  # "structure", "keyword", "instruction", "constraint"
    success_count: int = 0
    failure_count: int = 0
    contexts: List[str] = None  # Categories where pattern works well
    
    def __post_init__(self):
        if self.contexts is None:
            self.contexts = []
    
    @property
    def effectiveness(self) -> float:
        """Calculate pattern effectiveness (0-1)"""
        total = self.success_count + self.failure_count
        if total == 0:
            return 0.5  # Neutral for untested patterns
        return self.success_count / total


class PromptReinforcementLearner:
    """
    Learns from outcomes to improve prompt generation through reinforcement.
    
    Features:
    - Extract patterns from successful prompts
    - Identify anti-patterns from failures
    - Calculate pattern effectiveness scores
    - Generate optimization recommendations
    - Auto-prune low-performing patterns
    - Track diversity to prevent convergence
    """
    
    def __init__(self, data_dir: str = "tools/data/prompts"):
        """Initialize the reinforcement learner"""
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.feedback_file = self.data_dir / "feedback.json"
        self.patterns_file = self.data_dir / "patterns.json"
        self.metrics_file = self.data_dir / "reinforcement_metrics.json"
        
        self.feedback_history: List[PromptFeedback] = []
        self.patterns: Dict[str, PromptPattern] = {}
        self.metrics: Dict[str, Any] = {}
        
        self._load_data()
    
    def _load_data(self):
        """Load existing reinforcement learning data"""
        if self.feedback_file.exists():
            try:
                with open(self.feedback_file, 'r') as f:
                    data = json.load(f)
                    self.feedback_history = [PromptFeedback(**fb) for fb in data]
            except Exception as e:
                print(f"Warning: Could not load feedback: {e}")
        
        if self.patterns_file.exists():
            try:
                with open(self.patterns_file, 'r') as f:
                    data = json.load(f)
                    self.patterns = {
                        pid: PromptPattern(**pdata)
                        for pid, pdata in data.items()
                    }
            except Exception as e:
                print(f"Warning: Could not load patterns: {e}")
        
        if self.metrics_file.exists():
            try:
                with open(self.metrics_file, 'r') as f:
                    self.metrics = json.load(f)
            except Exception as e:
                print(f"Warning: Could not load metrics: {e}")
    
    def _save_data(self):
        """Save all reinforcement learning data"""
        try:
            with open(self.feedback_file, 'w') as f:
                json.dump(
                    [asdict(fb) for fb in self.feedback_history],
                    f,
                    indent=2
                )
            
            with open(self.patterns_file, 'w') as f:
                json.dump(
                    {pid: asdict(p) for pid, p in self.patterns.items()},
                    f,
                    indent=2
                )
            
            with open(self.metrics_file, 'w') as f:
                json.dump(self.metrics, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save data: {e}")
    
    def record_feedback(
        self,
        prompt_id: str,
        issue_number: int,
        feedback_type: str,
        sentiment: str,
        feedback_text: str
    ):
        """
        Record feedback on a prompt's effectiveness.
        
        Args:
            prompt_id: The template ID used
            issue_number: GitHub issue number
            feedback_type: Type of feedback source
            sentiment: positive/negative/neutral
            feedback_text: The actual feedback content
        """
        # Extract patterns from feedback
        patterns = self._extract_patterns_from_feedback(feedback_text, sentiment)
        
        feedback = PromptFeedback(
            prompt_id=prompt_id,
            issue_number=issue_number,
            feedback_type=feedback_type,
            sentiment=sentiment,
            feedback_text=feedback_text,
            extracted_patterns=patterns,
            timestamp=datetime.now(timezone.utc).isoformat()
        )
        
        self.feedback_history.append(feedback)
        
        # Update pattern statistics
        self._update_patterns(patterns, sentiment == "positive")
        
        self._save_data()
    
    def _extract_patterns_from_feedback(
        self,
        feedback_text: str,
        sentiment: str
    ) -> List[str]:
        """Extract actionable patterns from feedback text"""
        patterns = []
        
        # Common positive patterns
        positive_keywords = [
            "clear", "detailed", "thorough", "systematic",
            "well-structured", "comprehensive", "precise"
        ]
        
        # Common negative patterns
        negative_keywords = [
            "unclear", "vague", "missing", "incomplete",
            "confusing", "ambiguous", "insufficient"
        ]
        
        text_lower = feedback_text.lower()
        
        if sentiment == "positive":
            for keyword in positive_keywords:
                if keyword in text_lower:
                    patterns.append(f"emphasis_{keyword}")
        else:
            for keyword in negative_keywords:
                if keyword in text_lower:
                    patterns.append(f"avoid_{keyword}")
        
        # Extract structural patterns
        if "step" in text_lower or "steps" in text_lower:
            if sentiment == "positive":
                patterns.append("structure_step_by_step")
            else:
                patterns.append("avoid_missing_steps")
        
        if "example" in text_lower:
            if sentiment == "positive":
                patterns.append("include_examples")
        
        if "test" in text_lower:
            if sentiment == "positive":
                patterns.append("emphasize_testing")
        
        return patterns
    
    def _update_patterns(self, pattern_list: List[str], is_success: bool):
        """Update pattern statistics based on outcome"""
        for pattern in pattern_list:
            if pattern not in self.patterns:
                self.patterns[pattern] = PromptPattern(
                    pattern=pattern,
                    pattern_type=self._classify_pattern(pattern)
                )
            
            if is_success:
                self.patterns[pattern].success_count += 1
            else:
                self.patterns[pattern].failure_count += 1
    
    def _classify_pattern(self, pattern: str) -> str:
        """Classify a pattern into a type"""
        if pattern.startswith("structure_"):
            return "structure"
        elif pattern.startswith("emphasis_"):
            return "keyword"
        elif pattern.startswith("include_"):
            return "instruction"
        elif pattern.startswith("avoid_"):
            return "constraint"
        else:
            return "general"
    
    def get_top_patterns(
        self,
        category: Optional[str] = None,
        min_effectiveness: float = 0.6,
        limit: int = 10
    ) -> List[PromptPattern]:
        """
        Get the most effective patterns.
        
        Args:
            category: Filter by prompt category (optional)
            min_effectiveness: Minimum effectiveness score
            limit: Maximum number of patterns to return
        
        Returns:
            List of top-performing patterns
        """
        # Filter patterns by effectiveness and category
        candidates = []
        
        for pattern in self.patterns.values():
            # Require minimum sample size
            if pattern.success_count + pattern.failure_count < 3:
                continue
            
            if pattern.effectiveness < min_effectiveness:
                continue
            
            if category and category not in pattern.contexts:
                # Check if pattern should be added to this category
                if pattern.success_count >= 3:
                    pattern.contexts.append(category)
            
            candidates.append(pattern)
        
        # Sort by effectiveness
        candidates.sort(key=lambda p: p.effectiveness, reverse=True)
        
        return candidates[:limit]
    
    def get_anti_patterns(
        self,
        min_failures: int = 3
    ) -> List[PromptPattern]:
        """
        Get patterns associated with failures (anti-patterns).
        
        Args:
            min_failures: Minimum failure count to consider
        
        Returns:
            List of anti-patterns to avoid
        """
        anti_patterns = []
        
        for pattern in self.patterns.values():
            if pattern.failure_count >= min_failures:
                if pattern.effectiveness < 0.4:
                    anti_patterns.append(pattern)
        
        # Sort by failure count (most problematic first)
        anti_patterns.sort(key=lambda p: p.failure_count, reverse=True)
        
        return anti_patterns
    
    def generate_optimization_recommendations(
        self,
        prompt_id: str
    ) -> List[Dict[str, Any]]:
        """
        Generate specific recommendations to optimize a prompt.
        
        Args:
            prompt_id: The prompt template to optimize
        
        Returns:
            List of optimization recommendations
        """
        recommendations = []
        
        # Analyze feedback for this prompt
        prompt_feedback = [
            fb for fb in self.feedback_history
            if fb.prompt_id == prompt_id
        ]
        
        if not prompt_feedback:
            return recommendations
        
        # Calculate sentiment distribution
        positive = sum(1 for fb in prompt_feedback if fb.sentiment == "positive")
        negative = sum(1 for fb in prompt_feedback if fb.sentiment == "negative")
        total = len(prompt_feedback)
        
        if negative > positive:
            recommendations.append({
                "type": "sentiment",
                "priority": "high",
                "message": f"Prompt has {negative}/{total} negative feedback",
                "action": "Review and revise prompt structure"
            })
        
        # Find common failure patterns
        failure_patterns = defaultdict(int)
        for fb in prompt_feedback:
            if fb.sentiment == "negative":
                for pattern in fb.extracted_patterns:
                    failure_patterns[pattern] += 1
        
        for pattern, count in failure_patterns.items():
            if count >= 2:
                recommendations.append({
                    "type": "pattern",
                    "priority": "medium",
                    "pattern": pattern,
                    "occurrences": count,
                    "action": f"Address recurring issue: {pattern}"
                })
        
        # Suggest incorporating successful patterns
        top_patterns = self.get_top_patterns(limit=5)
        for pattern in top_patterns:
            if pattern.pattern_type in ["structure", "instruction"]:
                recommendations.append({
                    "type": "enhancement",
                    "priority": "low",
                    "pattern": pattern.pattern,
                    "effectiveness": pattern.effectiveness,
                    "action": f"Consider incorporating: {pattern.pattern}"
                })
        
        return recommendations
    
    def calculate_diversity_score(self) -> float:
        """
        Calculate diversity score to prevent prompt convergence.
        
        Returns:
            Diversity score (0-1, higher is more diverse)
        """
        if not self.patterns:
            return 1.0
        
        # Count pattern types
        type_counts = defaultdict(int)
        for pattern in self.patterns.values():
            type_counts[pattern.pattern_type] += 1
        
        # Calculate entropy (diversity measure)
        total = sum(type_counts.values())
        if total == 0:
            return 1.0
        
        # Shannon entropy
        entropy = 0.0
        for count in type_counts.values():
            if count > 0:
                p = count / total
                import math
                entropy -= p * math.log2(p)
        
        # Normalize to 0-1 range
        # Maximum entropy is log2(num_types)
        num_types = len(type_counts)
        max_entropy = math.log2(num_types) if num_types > 1 else 1.0
        diversity = entropy / max_entropy if max_entropy > 0 else 0.0
        
        # Ensure in valid range
        diversity = max(0.0, min(1.0, diversity))
        
        return diversity
    
    def prune_ineffective_patterns(
        self,
        min_samples: int = 10,
        effectiveness_threshold: float = 0.3
    ) -> List[str]:
        """
        Remove patterns that consistently perform poorly.
        
        Args:
            min_samples: Minimum samples before considering pruning
            effectiveness_threshold: Patterns below this are pruned
        
        Returns:
            List of pruned pattern IDs
        """
        pruned = []
        
        for pattern_id, pattern in list(self.patterns.items()):
            total_samples = pattern.success_count + pattern.failure_count
            
            if total_samples >= min_samples:
                if pattern.effectiveness < effectiveness_threshold:
                    pruned.append(pattern_id)
                    del self.patterns[pattern_id]
        
        if pruned:
            self._save_data()
            
            # Update metrics
            self.metrics["last_pruning"] = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "patterns_pruned": len(pruned),
                "pruned_ids": pruned
            }
            self._save_data()
        
        return pruned
    
    def get_reinforcement_metrics(self) -> Dict[str, Any]:
        """Get current reinforcement learning metrics"""
        total_patterns = len(self.patterns)
        effective_patterns = sum(
            1 for p in self.patterns.values()
            if p.effectiveness >= 0.6 and (p.success_count + p.failure_count) >= 3
        )
        
        diversity_score = self.calculate_diversity_score()
        
        return {
            "total_feedback": len(self.feedback_history),
            "total_patterns": total_patterns,
            "effective_patterns": effective_patterns,
            "diversity_score": diversity_score,
            "pattern_types": {
                ptype: sum(1 for p in self.patterns.values() if p.pattern_type == ptype)
                for ptype in ["structure", "keyword", "instruction", "constraint", "general"]
            },
            "last_updated": datetime.now(timezone.utc).isoformat()
        }


def main():
    """CLI interface for prompt reinforcement learning"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Prompt reinforcement learning system"
    )
    parser.add_argument(
        "command",
        choices=["record", "patterns", "anti-patterns", "optimize", "metrics", "prune"],
        help="Command to execute"
    )
    parser.add_argument("--prompt-id", help="Prompt template ID")
    parser.add_argument("--issue-number", type=int, help="Issue number")
    parser.add_argument("--feedback-type", help="Type of feedback")
    parser.add_argument("--sentiment", choices=["positive", "negative", "neutral"], help="Feedback sentiment")
    parser.add_argument("--feedback-text", help="Feedback content")
    parser.add_argument("--category", help="Prompt category for filtering")
    parser.add_argument("--limit", type=int, default=10, help="Limit results")
    
    args = parser.parse_args()
    
    learner = PromptReinforcementLearner()
    
    if args.command == "record":
        if not all([args.prompt_id, args.issue_number, args.feedback_type, args.sentiment, args.feedback_text]):
            print("Error: record requires --prompt-id, --issue-number, --feedback-type, --sentiment, --feedback-text")
            return 1
        
        learner.record_feedback(
            args.prompt_id,
            args.issue_number,
            args.feedback_type,
            args.sentiment,
            args.feedback_text
        )
        print(f"✓ Recorded feedback for {args.prompt_id}")
    
    elif args.command == "patterns":
        patterns = learner.get_top_patterns(category=args.category, limit=args.limit)
        print(json.dumps([asdict(p) for p in patterns], indent=2))
    
    elif args.command == "anti-patterns":
        anti_patterns = learner.get_anti_patterns()
        print(json.dumps([asdict(p) for p in anti_patterns], indent=2))
    
    elif args.command == "optimize":
        if not args.prompt_id:
            print("Error: --prompt-id required for optimize")
            return 1
        
        recommendations = learner.generate_optimization_recommendations(args.prompt_id)
        print(json.dumps(recommendations, indent=2))
    
    elif args.command == "metrics":
        metrics = learner.get_reinforcement_metrics()
        print(json.dumps(metrics, indent=2))
    
    elif args.command == "prune":
        pruned = learner.prune_ineffective_patterns()
        print(f"Pruned {len(pruned)} ineffective patterns")
        if pruned:
            print("Pruned pattern IDs:")
            for pid in pruned:
                print(f"  - {pid}")
    
    return 0


if __name__ == "__main__":
    exit(main())
