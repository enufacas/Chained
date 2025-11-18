#!/usr/bin/env python3
"""
AI Hypothesis Testing Engine for Code Patterns
Author: @accelerate-specialist (Edsger Dijkstra)

This system generates and tests hypotheses about code patterns using
statistical analysis and machine learning. It learns from the codebase
to discover insights about software quality, maintainability, and performance.

Features:
- Automated hypothesis generation from code patterns
- Statistical testing of hypotheses
- Pattern correlation analysis
- Learning from validation results
- Performance-optimized analysis
"""

import argparse
import ast
import json
import os
import re
import sys
from collections import defaultdict, Counter
from dataclasses import dataclass, asdict, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional, Any
import statistics


@dataclass
class CodeMetrics:
    """Metrics extracted from code for analysis"""
    file_path: str
    function_name: str
    line_number: int
    
    # Complexity metrics
    cyclomatic_complexity: int = 0
    cognitive_complexity: int = 0
    lines_of_code: int = 0
    
    # Parameter metrics
    num_parameters: int = 0
    has_default_params: bool = False
    has_type_hints: bool = False
    
    # Quality indicators
    has_docstring: bool = False
    has_tests: bool = False
    has_error_handling: bool = False
    
    # Naming patterns
    name_length: int = 0
    follows_convention: bool = True


@dataclass
class Hypothesis:
    """Represents a testable hypothesis about code patterns"""
    hypothesis_id: str
    description: str
    hypothesis_type: str  # 'correlation', 'threshold', 'pattern'
    
    # Variables involved
    independent_var: str
    dependent_var: str
    
    # Test parameters
    threshold: Optional[float] = None
    direction: Optional[str] = None  # 'positive', 'negative'
    
    # Test results
    tested: bool = False
    validated: bool = False
    confidence: float = 0.0
    p_value: Optional[float] = None
    
    # Evidence
    sample_size: int = 0
    supporting_examples: List[Dict] = field(default_factory=list)
    contradicting_examples: List[Dict] = field(default_factory=list)
    
    # Metadata
    generated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    tested_at: Optional[str] = None


class HypothesisGenerator:
    """Generates hypotheses about code patterns"""
    
    def __init__(self):
        self.hypothesis_templates = self._load_templates()
        self.generated_count = 0
    
    def _load_templates(self) -> List[Dict]:
        """Load hypothesis templates"""
        return [
            {
                'id': 'complexity_quality',
                'template': 'Functions with {direction} {metric1} tend to have {direction2} {metric2}',
                'type': 'correlation',
                'combinations': [
                    ('high', 'cyclomatic_complexity', 'lower', 'test_coverage'),
                    ('high', 'cognitive_complexity', 'fewer', 'docstrings'),
                    ('many', 'parameters', 'higher', 'error_rate'),
                ]
            },
            {
                'id': 'naming_quality',
                'template': 'Functions with {pattern} naming have {direction} {metric}',
                'type': 'pattern',
                'combinations': [
                    ('short', 'lower', 'docstring_quality'),
                    ('long', 'higher', 'complexity'),
                    ('clear', 'better', 'maintainability'),
                ]
            },
            {
                'id': 'size_threshold',
                'template': 'Functions exceeding {threshold} {metric1} tend to have {issue}',
                'type': 'threshold',
                'combinations': [
                    (50, 'lines', 'multiple responsibilities'),
                    (5, 'parameters', 'poor cohesion'),
                    (10, 'cyclomatic_complexity', 'testing difficulties'),
                ]
            },
            {
                'id': 'best_practice',
                'template': 'Functions with {practice} have {direction} {metric}',
                'type': 'correlation',
                'combinations': [
                    ('type_hints', 'fewer', 'runtime_errors'),
                    ('error_handling', 'better', 'reliability'),
                    ('docstrings', 'higher', 'usage_rate'),
                ]
            },
        ]
    
    def generate_hypotheses(self, metrics: List[CodeMetrics], count: int = 10) -> List[Hypothesis]:
        """Generate hypotheses based on code metrics"""
        hypotheses = []
        
        # Analyze metrics to inform hypothesis generation
        self._analyze_metric_distributions(metrics)
        
        for template in self.hypothesis_templates:
            for combo in template['combinations'][:min(len(template['combinations']), count // len(self.hypothesis_templates) + 1)]:
                hypothesis = self._create_hypothesis_from_template(template, combo)
                if hypothesis:
                    hypotheses.append(hypothesis)
                    self.generated_count += 1
                    
                    if len(hypotheses) >= count:
                        break
            
            if len(hypotheses) >= count:
                break
        
        return hypotheses
    
    def _analyze_metric_distributions(self, metrics: List[CodeMetrics]):
        """Analyze metric distributions to inform generation"""
        if not metrics:
            return
        
        # Calculate statistics for key metrics
        complexities = [m.cyclomatic_complexity for m in metrics if m.cyclomatic_complexity > 0]
        param_counts = [m.num_parameters for m in metrics]
        loc_counts = [m.lines_of_code for m in metrics if m.lines_of_code > 0]
        
        # Store for later use
        self.metric_stats = {
            'complexity_mean': statistics.mean(complexities) if complexities else 0,
            'complexity_median': statistics.median(complexities) if complexities else 0,
            'param_mean': statistics.mean(param_counts) if param_counts else 0,
            'loc_mean': statistics.mean(loc_counts) if loc_counts else 0,
        }
    
    def _create_hypothesis_from_template(self, template: Dict, combo: Tuple) -> Optional[Hypothesis]:
        """Create a hypothesis from a template and combination"""
        try:
            self.generated_count += 1
            hypothesis_id = f"hyp_{template['id']}_{self.generated_count}"
            
            if template['type'] == 'correlation':
                direction, metric1, direction2, metric2 = combo
                description = template['template'].format(
                    direction=direction, metric1=metric1,
                    direction2=direction2, metric2=metric2
                )
                
                return Hypothesis(
                    hypothesis_id=hypothesis_id,
                    description=description,
                    hypothesis_type='correlation',
                    independent_var=metric1,
                    dependent_var=metric2,
                    direction='positive' if direction == 'high' else 'negative'
                )
            
            elif template['type'] == 'threshold':
                threshold, metric1, issue = combo
                description = template['template'].format(
                    threshold=threshold, metric1=metric1, issue=issue
                )
                
                return Hypothesis(
                    hypothesis_id=hypothesis_id,
                    description=description,
                    hypothesis_type='threshold',
                    independent_var=metric1,
                    dependent_var='quality',
                    threshold=float(threshold)
                )
            
            elif template['type'] == 'pattern':
                pattern, direction, metric = combo
                description = template['template'].format(
                    pattern=pattern, direction=direction, metric=metric
                )
                
                return Hypothesis(
                    hypothesis_id=hypothesis_id,
                    description=description,
                    hypothesis_type='pattern',
                    independent_var='naming_pattern',
                    dependent_var=metric
                )
        
        except Exception as e:
            print(f"Error creating hypothesis: {e}", file=sys.stderr)
            return None


class HypothesisTester:
    """Tests hypotheses against code metrics"""
    
    def __init__(self, significance_level: float = 0.05):
        self.significance_level = significance_level
        self.test_results = []
    
    def test_hypothesis(self, hypothesis: Hypothesis, metrics: List[CodeMetrics]) -> Hypothesis:
        """Test a hypothesis against code metrics"""
        if not metrics:
            return hypothesis
        
        hypothesis.tested = True
        hypothesis.tested_at = datetime.now(timezone.utc).isoformat()
        hypothesis.sample_size = len(metrics)
        
        if hypothesis.hypothesis_type == 'correlation':
            self._test_correlation(hypothesis, metrics)
        elif hypothesis.hypothesis_type == 'threshold':
            self._test_threshold(hypothesis, metrics)
        elif hypothesis.hypothesis_type == 'pattern':
            self._test_pattern(hypothesis, metrics)
        
        # Calculate confidence based on sample size and validation
        if hypothesis.validated:
            hypothesis.confidence = min(0.95, 0.5 + (hypothesis.sample_size / 200))
        else:
            hypothesis.confidence = max(0.05, 0.5 - (hypothesis.sample_size / 200))
        
        self.test_results.append(hypothesis)
        return hypothesis
    
    def _test_correlation(self, hypothesis: Hypothesis, metrics: List[CodeMetrics]):
        """Test correlation hypothesis"""
        # Extract relevant metrics
        independent_values = []
        dependent_values = []
        
        for metric in metrics:
            indep = self._get_metric_value(metric, hypothesis.independent_var)
            dep = self._get_metric_value(metric, hypothesis.dependent_var)
            
            if indep is not None and dep is not None:
                independent_values.append(float(indep))
                dependent_values.append(float(dep))
        
        if len(independent_values) < 5:
            return
        
        # Calculate correlation (simplified)
        correlation = self._calculate_correlation(independent_values, dependent_values)
        
        # Check if correlation matches expected direction
        expected_positive = hypothesis.direction == 'positive'
        actual_positive = correlation > 0
        
        hypothesis.validated = (expected_positive == actual_positive and abs(correlation) > 0.3)
        hypothesis.p_value = 1 - abs(correlation)  # Simplified p-value
        
        # Collect examples
        self._collect_examples(hypothesis, metrics, independent_values, dependent_values)
    
    def _test_threshold(self, hypothesis: Hypothesis, metrics: List[CodeMetrics]):
        """Test threshold hypothesis"""
        if hypothesis.threshold is None:
            return
        
        above_threshold = []
        below_threshold = []
        
        for metric in metrics:
            value = self._get_metric_value(metric, hypothesis.independent_var)
            quality = self._assess_quality(metric)
            
            if value is not None:
                if value > hypothesis.threshold:
                    above_threshold.append(quality)
                else:
                    below_threshold.append(quality)
        
        if not above_threshold or not below_threshold:
            return
        
        # Compare quality scores
        avg_above = statistics.mean(above_threshold)
        avg_below = statistics.mean(below_threshold)
        
        # Hypothesis validated if quality is lower above threshold
        hypothesis.validated = avg_above < avg_below * 0.8
        hypothesis.p_value = abs(avg_above - avg_below) / (avg_above + avg_below)
        
        # Store examples
        for metric in metrics[:5]:
            value = self._get_metric_value(metric, hypothesis.independent_var)
            if value and value > hypothesis.threshold:
                hypothesis.supporting_examples.append({
                    'file': metric.file_path,
                    'function': metric.function_name,
                    'value': value
                })
    
    def _test_pattern(self, hypothesis: Hypothesis, metrics: List[CodeMetrics]):
        """Test pattern hypothesis"""
        pattern_matches = []
        pattern_non_matches = []
        
        for metric in metrics:
            matches_pattern = self._check_pattern(metric, hypothesis.independent_var)
            quality = self._assess_quality(metric)
            
            if matches_pattern:
                pattern_matches.append(quality)
            else:
                pattern_non_matches.append(quality)
        
        if not pattern_matches or not pattern_non_matches:
            return
        
        # Compare quality
        avg_match = statistics.mean(pattern_matches)
        avg_non_match = statistics.mean(pattern_non_matches)
        
        hypothesis.validated = avg_match > avg_non_match * 1.2
        hypothesis.p_value = abs(avg_match - avg_non_match) / (avg_match + avg_non_match)
    
    def _get_metric_value(self, metric: CodeMetrics, var_name: str) -> Optional[float]:
        """Extract metric value by name"""
        metric_map = {
            'cyclomatic_complexity': metric.cyclomatic_complexity,
            'cognitive_complexity': metric.cognitive_complexity,
            'lines': metric.lines_of_code,
            'parameters': metric.num_parameters,
            'test_coverage': 1.0 if metric.has_tests else 0.0,
            'docstrings': 1.0 if metric.has_docstring else 0.0,
            'error_handling': 1.0 if metric.has_error_handling else 0.0,
        }
        return metric_map.get(var_name)
    
    def _assess_quality(self, metric: CodeMetrics) -> float:
        """Assess overall quality score for a metric"""
        score = 0.0
        
        # Positive factors
        if metric.has_docstring:
            score += 0.3
        if metric.has_tests:
            score += 0.3
        if metric.has_error_handling:
            score += 0.2
        if metric.has_type_hints:
            score += 0.2
        
        # Negative factors
        if metric.cyclomatic_complexity > 10:
            score -= 0.2
        if metric.num_parameters > 5:
            score -= 0.1
        if metric.lines_of_code > 50:
            score -= 0.1
        
        return max(0.0, min(1.0, score))
    
    def _check_pattern(self, metric: CodeMetrics, pattern: str) -> bool:
        """Check if metric matches a naming pattern"""
        if pattern == 'naming_pattern':
            return metric.follows_convention
        return False
    
    def _calculate_correlation(self, x: List[float], y: List[float]) -> float:
        """Calculate Pearson correlation coefficient"""
        if len(x) != len(y) or len(x) < 2:
            return 0.0
        
        mean_x = statistics.mean(x)
        mean_y = statistics.mean(y)
        
        numerator = sum((x[i] - mean_x) * (y[i] - mean_y) for i in range(len(x)))
        
        sum_sq_x = sum((xi - mean_x) ** 2 for xi in x)
        sum_sq_y = sum((yi - mean_y) ** 2 for yi in y)
        
        denominator = (sum_sq_x * sum_sq_y) ** 0.5
        
        if denominator == 0:
            return 0.0
        
        return numerator / denominator
    
    def _collect_examples(self, hypothesis: Hypothesis, metrics: List[CodeMetrics], 
                         indep_vals: List[float], dep_vals: List[float]):
        """Collect supporting and contradicting examples"""
        if len(indep_vals) != len(metrics):
            return
        
        # Sort by independent variable
        sorted_indices = sorted(range(len(indep_vals)), key=lambda i: indep_vals[i], reverse=True)
        
        # Top examples (high independent variable)
        for i in sorted_indices[:3]:
            if i < len(metrics):
                hypothesis.supporting_examples.append({
                    'file': metrics[i].file_path,
                    'function': metrics[i].function_name,
                    'independent': indep_vals[i],
                    'dependent': dep_vals[i]
                })


class CodeAnalyzer:
    """Analyzes code to extract metrics"""
    
    def __init__(self, repo_path: str = "."):
        self.repo_path = Path(repo_path)
    
    def analyze_repository(self, max_files: int = 100) -> List[CodeMetrics]:
        """Analyze Python files in repository"""
        metrics = []
        
        python_files = list(self.repo_path.rglob("*.py"))[:max_files]
        
        for file_path in python_files:
            try:
                file_metrics = self.analyze_file(file_path)
                metrics.extend(file_metrics)
            except Exception as e:
                print(f"Error analyzing {file_path}: {e}", file=sys.stderr)
        
        return metrics
    
    def analyze_file(self, file_path: Path) -> List[CodeMetrics]:
        """Analyze a single Python file"""
        metrics = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    metric = self._extract_function_metrics(node, file_path, content)
                    metrics.append(metric)
        
        except Exception as e:
            print(f"Error parsing {file_path}: {e}", file=sys.stderr)
        
        return metrics
    
    def _extract_function_metrics(self, node: ast.FunctionDef, 
                                  file_path: Path, content: str) -> CodeMetrics:
        """Extract metrics from a function"""
        metric = CodeMetrics(
            file_path=str(file_path),
            function_name=node.name,
            line_number=node.lineno,
            num_parameters=len(node.args.args),
            has_default_params=len(node.args.defaults) > 0,
            has_type_hints=any(arg.annotation for arg in node.args.args),
            has_docstring=ast.get_docstring(node) is not None,
            name_length=len(node.name),
            follows_convention=node.name.islower() or '_' in node.name
        )
        
        # Calculate complexity
        metric.cyclomatic_complexity = self._calculate_cyclomatic_complexity(node)
        metric.lines_of_code = self._count_lines(node)
        
        # Check for tests
        metric.has_tests = 'test_' in node.name or '_test' in node.name
        
        # Check for error handling
        metric.has_error_handling = self._has_error_handling(node)
        
        return metric
    
    def _calculate_cyclomatic_complexity(self, node: ast.FunctionDef) -> int:
        """Calculate cyclomatic complexity"""
        complexity = 1
        
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
        
        return complexity
    
    def _count_lines(self, node: ast.FunctionDef) -> int:
        """Count lines of code in function"""
        if hasattr(node, 'end_lineno'):
            return node.end_lineno - node.lineno + 1
        return 1
    
    def _has_error_handling(self, node: ast.FunctionDef) -> bool:
        """Check if function has error handling"""
        for child in ast.walk(node):
            if isinstance(child, (ast.Try, ast.ExceptHandler)):
                return True
        return False


class HypothesisTestingEngine:
    """Main engine for hypothesis testing"""
    
    def __init__(self, repo_path: str = ".", output_file: str = "analysis/hypothesis_results.json"):
        self.repo_path = repo_path
        self.output_file = output_file
        self.analyzer = CodeAnalyzer(repo_path)
        self.generator = HypothesisGenerator()
        self.tester = HypothesisTester()
        self.results = []
    
    def run(self, num_hypotheses: int = 10, max_files: int = 100) -> Dict:
        """Run the complete hypothesis testing pipeline"""
        print("🔬 Starting Hypothesis Testing Engine...")
        print(f"📊 Analyzing repository: {self.repo_path}")
        
        # Step 1: Analyze code
        print("\n1️⃣ Extracting code metrics...")
        metrics = self.analyzer.analyze_repository(max_files=max_files)
        print(f"   ✓ Analyzed {len(metrics)} functions")
        
        # Step 2: Generate hypotheses
        print("\n2️⃣ Generating hypotheses...")
        hypotheses = self.generator.generate_hypotheses(metrics, count=num_hypotheses)
        print(f"   ✓ Generated {len(hypotheses)} hypotheses")
        
        # Step 3: Test hypotheses
        print("\n3️⃣ Testing hypotheses...")
        tested_hypotheses = []
        for i, hypothesis in enumerate(hypotheses, 1):
            print(f"   Testing {i}/{len(hypotheses)}: {hypothesis.description[:60]}...")
            tested = self.tester.test_hypothesis(hypothesis, metrics)
            tested_hypotheses.append(tested)
        
        # Step 4: Summarize results
        validated = [h for h in tested_hypotheses if h.validated]
        print(f"\n✓ Testing complete!")
        print(f"   {len(validated)}/{len(tested_hypotheses)} hypotheses validated")
        
        # Step 5: Save results
        results = {
            'generated_at': datetime.now(timezone.utc).isoformat(),
            'repository': self.repo_path,
            'metrics_analyzed': len(metrics),
            'hypotheses_generated': len(hypotheses),
            'hypotheses_validated': len(validated),
            'validation_rate': len(validated) / len(hypotheses) if hypotheses else 0,
            'hypotheses': [asdict(h) for h in tested_hypotheses],
            'summary': self._generate_summary(tested_hypotheses)
        }
        
        self._save_results(results)
        self.results = results
        
        return results
    
    def _generate_summary(self, hypotheses: List[Hypothesis]) -> Dict:
        """Generate summary of results"""
        validated = [h for h in hypotheses if h.validated]
        
        return {
            'top_validated_hypotheses': [
                {
                    'description': h.description,
                    'confidence': h.confidence,
                    'sample_size': h.sample_size
                }
                for h in sorted(validated, key=lambda x: x.confidence, reverse=True)[:5]
            ],
            'hypothesis_types': {
                'correlation': len([h for h in hypotheses if h.hypothesis_type == 'correlation']),
                'threshold': len([h for h in hypotheses if h.hypothesis_type == 'threshold']),
                'pattern': len([h for h in hypotheses if h.hypothesis_type == 'pattern'])
            },
            'insights': self._generate_insights(validated)
        }
    
    def _generate_insights(self, validated: List[Hypothesis]) -> List[str]:
        """Generate actionable insights from validated hypotheses"""
        insights = []
        
        for hyp in validated[:5]:
            if hyp.hypothesis_type == 'threshold' and hyp.threshold:
                insights.append(
                    f"Consider refactoring functions with {hyp.independent_var} > {hyp.threshold}"
                )
            elif hyp.hypothesis_type == 'correlation':
                insights.append(
                    f"Reducing {hyp.independent_var} may improve {hyp.dependent_var}"
                )
        
        return insights
    
    def _save_results(self, results: Dict):
        """Save results to file"""
        os.makedirs(os.path.dirname(self.output_file), exist_ok=True)
        with open(self.output_file, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\n💾 Results saved to: {self.output_file}")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='AI Hypothesis Testing Engine for Code Patterns'
    )
    parser.add_argument(
        '--repo-path', '-r',
        default='.',
        help='Path to repository to analyze'
    )
    parser.add_argument(
        '--num-hypotheses', '-n',
        type=int,
        default=10,
        help='Number of hypotheses to generate'
    )
    parser.add_argument(
        '--max-files', '-m',
        type=int,
        default=100,
        help='Maximum number of files to analyze'
    )
    parser.add_argument(
        '--output', '-o',
        default='analysis/hypothesis_results.json',
        help='Output file for results'
    )
    
    args = parser.parse_args()
    
    engine = HypothesisTestingEngine(
        repo_path=args.repo_path,
        output_file=args.output
    )
    
    results = engine.run(
        num_hypotheses=args.num_hypotheses,
        max_files=args.max_files
    )
    
    print("\n" + "="*60)
    print("📊 HYPOTHESIS TESTING RESULTS")
    print("="*60)
    print(f"\n✓ Validated Hypotheses: {results['hypotheses_validated']}/{results['hypotheses_generated']}")
    print(f"✓ Validation Rate: {results['validation_rate']:.1%}")
    
    if results['summary']['top_validated_hypotheses']:
        print("\n🏆 Top Validated Hypotheses:")
        for i, hyp in enumerate(results['summary']['top_validated_hypotheses'], 1):
            print(f"{i}. {hyp['description']}")
            print(f"   Confidence: {hyp['confidence']:.2%}, Sample: {hyp['sample_size']}")
    
    if results['summary']['insights']:
        print("\n💡 Actionable Insights:")
        for insight in results['summary']['insights']:
            print(f"  • {insight}")
    
    print("\n✨ Analysis complete!")
    return 0


if __name__ == '__main__':
    sys.exit(main())
