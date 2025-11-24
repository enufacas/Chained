#!/usr/bin/env python3
"""
Prompt Quality Scorer

Advanced quality metrics for prompt templates based on multiple factors:
- Resolution success rate
- Time to resolution
- Agent satisfaction (implicit from outcomes)
- Learning integration effectiveness
- Template clarity and structure

Part of the self-improving prompt generator system.
Created by @create-guru - infrastructure creation inspired by Nikola Tesla.
"""

import json
import re
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timezone


@dataclass
class PromptQualityMetrics:
    """Quality metrics for a prompt template"""
    template_id: str
    
    # Success metrics (0-1 scale)
    resolution_score: float  # Based on success rate
    efficiency_score: float  # Based on resolution time
    consistency_score: float  # Based on variance in outcomes
    learning_score: float  # Based on learning integration effectiveness
    structure_score: float  # Based on template structure quality
    
    # Composite score
    overall_quality: float
    
    # Metadata
    sample_size: int
    last_updated: str


class PromptQualityScorer:
    """
    Evaluates prompt quality using multiple dimensions.
    
    Quality dimensions:
    1. Resolution Success (40%) - How often prompts lead to successful outcomes
    2. Efficiency (25%) - How quickly issues get resolved
    3. Consistency (15%) - How stable the results are
    4. Learning Integration (10%) - How well learning insights are applied
    5. Structure (10%) - Quality of the template structure itself
    """
    
    # Weights for composite score
    WEIGHTS = {
        'resolution': 0.40,
        'efficiency': 0.25,
        'consistency': 0.15,
        'learning': 0.10,
        'structure': 0.10
    }
    
    # Thresholds for efficiency scoring (hours)
    EXCELLENT_TIME = 6.0
    GOOD_TIME = 24.0
    ACCEPTABLE_TIME = 72.0
    
    def __init__(self, data_dir: str = "tools/data/prompts"):
        """Initialize the quality scorer"""
        self.data_dir = Path(data_dir)
        self.templates_file = self.data_dir / "templates.json"
        self.outcomes_file = self.data_dir / "outcomes.json"
        self.quality_file = self.data_dir / "quality_metrics.json"
        
        self.templates = {}
        self.outcomes = []
        self.quality_metrics = {}
        
        self._load_data()
    
    def _load_data(self):
        """Load prompt data from files"""
        # Load templates
        if self.templates_file.exists():
            with open(self.templates_file, 'r') as f:
                self.templates = json.load(f)
        
        # Load outcomes
        if self.outcomes_file.exists():
            with open(self.outcomes_file, 'r') as f:
                self.outcomes = json.load(f)
        
        # Load existing quality metrics
        if self.quality_file.exists():
            with open(self.quality_file, 'r') as f:
                data = json.load(f)
                self.quality_metrics = {
                    tid: PromptQualityMetrics(**metrics)
                    for tid, metrics in data.items()
                }
    
    def _save_quality_metrics(self):
        """Save quality metrics to file"""
        with open(self.quality_file, 'w') as f:
            json.dump(
                {tid: asdict(m) for tid, m in self.quality_metrics.items()},
                f,
                indent=2
            )
    
    def calculate_resolution_score(self, template_id: str) -> Tuple[float, int]:
        """
        Calculate resolution success score (0-1).
        
        Returns:
            Tuple of (score, sample_size)
        """
        template_outcomes = [
            o for o in self.outcomes
            if o.get('prompt_id') == template_id
        ]
        
        if not template_outcomes:
            return 0.5, 0  # Neutral score for new templates
        
        successes = sum(1 for o in template_outcomes if o.get('success', False))
        total = len(template_outcomes)
        
        # Calculate base success rate
        success_rate = successes / total
        
        # Apply confidence adjustment based on sample size
        # More samples = more confidence in the score
        confidence = min(1.0, total / 20.0)  # Full confidence at 20+ samples
        
        # Weighted score: success_rate weighted by confidence
        # New templates (low confidence) regress toward 0.5
        score = success_rate * confidence + 0.5 * (1 - confidence)
        
        return score, total
    
    def calculate_efficiency_score(self, template_id: str) -> float:
        """
        Calculate efficiency score based on resolution time (0-1).
        
        Scoring:
        - < 6 hours: 1.0 (excellent)
        - 6-24 hours: 0.8-1.0 (good)
        - 24-72 hours: 0.5-0.8 (acceptable)
        - > 72 hours: 0.0-0.5 (poor)
        """
        template_outcomes = [
            o for o in self.outcomes
            if o.get('prompt_id') == template_id and o.get('success', False)
        ]
        
        if not template_outcomes:
            return 0.5  # Neutral score
        
        # Calculate average resolution time
        times = [o.get('resolution_time_hours', 0) for o in template_outcomes]
        avg_time = sum(times) / len(times)
        
        # Score based on time thresholds
        if avg_time <= self.EXCELLENT_TIME:
            score = 1.0
        elif avg_time <= self.GOOD_TIME:
            # Linear interpolation between excellent and good
            ratio = (avg_time - self.EXCELLENT_TIME) / (self.GOOD_TIME - self.EXCELLENT_TIME)
            score = 1.0 - (ratio * 0.2)
        elif avg_time <= self.ACCEPTABLE_TIME:
            # Linear interpolation between good and acceptable
            ratio = (avg_time - self.GOOD_TIME) / (self.ACCEPTABLE_TIME - self.GOOD_TIME)
            score = 0.8 - (ratio * 0.3)
        else:
            # Poor performance, scale down from 0.5
            excess = min(avg_time - self.ACCEPTABLE_TIME, 168)  # Cap at 1 week
            ratio = excess / 168
            score = 0.5 * (1 - ratio)
        
        return max(0.0, score)
    
    def calculate_consistency_score(self, template_id: str) -> float:
        """
        Calculate consistency score based on variance in outcomes (0-1).
        
        High consistency = similar outcomes across uses
        Low consistency = unpredictable results
        """
        template_outcomes = [
            o for o in self.outcomes
            if o.get('prompt_id') == template_id
        ]
        
        if len(template_outcomes) < 3:
            return 0.5  # Need at least 3 samples for consistency
        
        # Measure consistency in success rate
        successes = [1 if o.get('success', False) else 0 for o in template_outcomes]
        
        # Calculate success rate variance
        mean_success = sum(successes) / len(successes)
        variance = sum((s - mean_success) ** 2 for s in successes) / len(successes)
        std_dev = variance ** 0.5
        
        # Convert to score (lower variance = higher score)
        # Perfect consistency (all same result) = 1.0
        # Maximum variance (50/50 split) = 0.0
        max_std_dev = 0.5  # Maximum theoretical std dev for binary outcomes
        consistency_score = 1.0 - (std_dev / max_std_dev)
        
        # Also consider time consistency if we have successful outcomes
        successful_outcomes = [o for o in template_outcomes if o.get('success', False)]
        if len(successful_outcomes) >= 3:
            times = [o.get('resolution_time_hours', 0) for o in successful_outcomes]
            mean_time = sum(times) / len(times)
            time_variance = sum((t - mean_time) ** 2 for t in times) / len(times)
            time_std_dev = time_variance ** 0.5
            
            # Normalize by mean (coefficient of variation)
            if mean_time > 0:
                time_cv = time_std_dev / mean_time
                # Score time consistency (lower CV = higher score)
                time_consistency = 1.0 - min(1.0, time_cv)
                
                # Average success and time consistency
                consistency_score = (consistency_score + time_consistency) / 2
        
        return consistency_score
    
    def calculate_learning_score(self, template_id: str) -> float:
        """
        Calculate learning integration effectiveness score (0-1).
        
        Measures how well the template incorporates and benefits from
        learning insights (TLDR, HN data).
        """
        # Check if template has learning integration
        template = self.templates.get(template_id, {})
        template_text = template.get('template', '')
        
        # Look for learning-related sections in template
        has_learning_section = 'learning' in template_text.lower()
        has_recent_insights = 'recent' in template_text.lower() and 'insights' in template_text.lower()
        
        base_score = 0.5
        
        if has_learning_section or has_recent_insights:
            base_score = 0.7  # Template is designed for learning integration
            
            # Check if learning actually improves outcomes
            template_outcomes = [
                o for o in self.outcomes
                if o.get('prompt_id') == template_id
            ]
            
            if len(template_outcomes) >= 5:
                # Compare early vs recent outcomes to see if learning helps
                sorted_outcomes = sorted(
                    template_outcomes,
                    key=lambda o: o.get('timestamp', '')
                )
                
                early_outcomes = sorted_outcomes[:len(sorted_outcomes)//2]
                recent_outcomes = sorted_outcomes[len(sorted_outcomes)//2:]
                
                early_success = sum(1 for o in early_outcomes if o.get('success', False)) / len(early_outcomes)
                recent_success = sum(1 for o in recent_outcomes if o.get('success', False)) / len(recent_outcomes)
                
                # If success rate improved, learning is effective
                if recent_success > early_success:
                    improvement = recent_success - early_success
                    base_score = min(1.0, 0.7 + improvement)
        
        return base_score
    
    def calculate_structure_score(self, template_id: str) -> float:
        """
        Calculate template structure quality score (0-1).
        
        Evaluates:
        - Clear sections and organization
        - Use of formatting (bold, lists)
        - Agent mention presence
        - Actionable instructions
        - Appropriate length
        """
        template = self.templates.get(template_id, {})
        template_text = template.get('template', '')
        
        if not template_text:
            return 0.0
        
        score = 0.0
        
        # Check for clear sections (headers with **)
        sections = re.findall(r'\*\*[^*]+\*\*', template_text)
        if len(sections) >= 3:
            score += 0.2
        elif len(sections) >= 1:
            score += 0.1
        
        # Check for agent mention
        if '@{agent}' in template_text or '**@' in template_text:
            score += 0.2
        
        # Check for lists/structure
        has_numbered_list = bool(re.search(r'^\d+\.', template_text, re.MULTILINE))
        has_bulleted_list = bool(re.search(r'^[\*\-]', template_text, re.MULTILINE))
        if has_numbered_list or has_bulleted_list:
            score += 0.2
        
        # Check for actionable verbs
        action_verbs = ['analyze', 'design', 'implement', 'test', 'validate', 'document', 'review', 'fix']
        action_count = sum(1 for verb in action_verbs if verb in template_text.lower())
        if action_count >= 4:
            score += 0.2
        elif action_count >= 2:
            score += 0.1
        
        # Check length appropriateness (not too short, not too long)
        length = len(template_text)
        if 200 <= length <= 1500:
            score += 0.2
        elif 100 <= length < 200 or 1500 < length <= 2000:
            score += 0.1
        
        return min(1.0, score)
    
    def calculate_quality_metrics(self, template_id: str) -> PromptQualityMetrics:
        """
        Calculate comprehensive quality metrics for a template.
        
        Args:
            template_id: The template to evaluate
            
        Returns:
            PromptQualityMetrics object with all scores
        """
        # Calculate individual scores
        resolution_score, sample_size = self.calculate_resolution_score(template_id)
        efficiency_score = self.calculate_efficiency_score(template_id)
        consistency_score = self.calculate_consistency_score(template_id)
        learning_score = self.calculate_learning_score(template_id)
        structure_score = self.calculate_structure_score(template_id)
        
        # Calculate weighted overall quality
        overall_quality = (
            resolution_score * self.WEIGHTS['resolution'] +
            efficiency_score * self.WEIGHTS['efficiency'] +
            consistency_score * self.WEIGHTS['consistency'] +
            learning_score * self.WEIGHTS['learning'] +
            structure_score * self.WEIGHTS['structure']
        )
        
        return PromptQualityMetrics(
            template_id=template_id,
            resolution_score=resolution_score,
            efficiency_score=efficiency_score,
            consistency_score=consistency_score,
            learning_score=learning_score,
            structure_score=structure_score,
            overall_quality=overall_quality,
            sample_size=sample_size,
            last_updated=datetime.now(timezone.utc).isoformat()
        )
    
    def score_all_templates(self) -> Dict[str, PromptQualityMetrics]:
        """Score all available templates and save results"""
        for template_id in self.templates.keys():
            metrics = self.calculate_quality_metrics(template_id)
            self.quality_metrics[template_id] = metrics
        
        self._save_quality_metrics()
        return self.quality_metrics
    
    def get_quality_report(self) -> Dict:
        """Generate a comprehensive quality report"""
        if not self.quality_metrics:
            self.score_all_templates()
        
        # Sort templates by overall quality
        sorted_templates = sorted(
            self.quality_metrics.values(),
            key=lambda m: m.overall_quality,
            reverse=True
        )
        
        report = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "total_templates": len(sorted_templates),
            "templates": []
        }
        
        for metrics in sorted_templates:
            report["templates"].append({
                "template_id": metrics.template_id,
                "overall_quality": round(metrics.overall_quality, 3),
                "scores": {
                    "resolution": round(metrics.resolution_score, 3),
                    "efficiency": round(metrics.efficiency_score, 3),
                    "consistency": round(metrics.consistency_score, 3),
                    "learning": round(metrics.learning_score, 3),
                    "structure": round(metrics.structure_score, 3)
                },
                "sample_size": metrics.sample_size,
                "grade": self._get_quality_grade(metrics.overall_quality)
            })
        
        # Calculate summary statistics
        if sorted_templates:
            report["summary"] = {
                "avg_quality": round(
                    sum(m.overall_quality for m in sorted_templates) / len(sorted_templates),
                    3
                ),
                "highest_quality": round(sorted_templates[0].overall_quality, 3),
                "lowest_quality": round(sorted_templates[-1].overall_quality, 3),
                "grades": self._count_grades(sorted_templates)
            }
        
        return report
    
    def _get_quality_grade(self, score: float) -> str:
        """Convert quality score to letter grade"""
        if score >= 0.9:
            return "A+"
        elif score >= 0.85:
            return "A"
        elif score >= 0.80:
            return "A-"
        elif score >= 0.75:
            return "B+"
        elif score >= 0.70:
            return "B"
        elif score >= 0.65:
            return "B-"
        elif score >= 0.60:
            return "C+"
        elif score >= 0.55:
            return "C"
        elif score >= 0.50:
            return "C-"
        else:
            return "D"
    
    def _count_grades(self, metrics_list: List[PromptQualityMetrics]) -> Dict[str, int]:
        """Count distribution of quality grades"""
        grades = {}
        for metrics in metrics_list:
            grade = self._get_quality_grade(metrics.overall_quality)
            grades[grade] = grades.get(grade, 0) + 1
        return grades


def main():
    """CLI interface for the quality scorer"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Prompt quality scorer - evaluate template effectiveness"
    )
    parser.add_argument(
        "command",
        choices=["score", "report", "template"],
        help="Command to execute"
    )
    parser.add_argument(
        "--template-id",
        help="Specific template to score (for 'template' command)"
    )
    
    args = parser.parse_args()
    
    scorer = PromptQualityScorer()
    
    if args.command == "score":
        print("📊 Scoring all templates...")
        metrics = scorer.score_all_templates()
        print(f"✓ Scored {len(metrics)} templates")
        
        # Show summary
        sorted_metrics = sorted(
            metrics.values(),
            key=lambda m: m.overall_quality,
            reverse=True
        )
        
        print("\nTop 5 Templates:")
        for m in sorted_metrics[:5]:
            grade = scorer._get_quality_grade(m.overall_quality)
            print(f"  {m.template_id}: {m.overall_quality:.3f} ({grade}) - {m.sample_size} samples")
    
    elif args.command == "report":
        report = scorer.get_quality_report()
        print(json.dumps(report, indent=2))
    
    elif args.command == "template":
        if not args.template_id:
            print("Error: --template-id required for 'template' command")
            return 1
        
        metrics = scorer.calculate_quality_metrics(args.template_id)
        
        print(f"\n📊 Quality Metrics for: {metrics.template_id}")
        print(f"{'='*60}")
        print(f"Overall Quality: {metrics.overall_quality:.3f} ({scorer._get_quality_grade(metrics.overall_quality)})")
        print(f"Sample Size: {metrics.sample_size}")
        print(f"\nDimensional Scores:")
        print(f"  Resolution:   {metrics.resolution_score:.3f} (40% weight)")
        print(f"  Efficiency:   {metrics.efficiency_score:.3f} (25% weight)")
        print(f"  Consistency:  {metrics.consistency_score:.3f} (15% weight)")
        print(f"  Learning:     {metrics.learning_score:.3f} (10% weight)")
        print(f"  Structure:    {metrics.structure_score:.3f} (10% weight)")
    
    return 0


if __name__ == "__main__":
    exit(main())
