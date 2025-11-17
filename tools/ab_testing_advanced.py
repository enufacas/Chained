#!/usr/bin/env python3
"""
Advanced A/B Testing Algorithms

This module implements advanced statistical methods for A/B testing:
- Multi-Armed Bandit (Thompson Sampling)
- Bayesian A/B Testing
- Sequential Testing
- Confidence Intervals

Author: @accelerate-specialist
Inspired by: Edsger Dijkstra - Elegant, efficient, systematic
"""

import json
import math
import random
from typing import Dict, List, Tuple, Optional, Any
from pathlib import Path


class ThompsonSampling:
    """
    Multi-Armed Bandit using Thompson Sampling for adaptive variant selection.
    
    This allows the system to balance exploration (trying new variants) with
    exploitation (using the best known variant) in an optimal Bayesian way.
    """
    
    def __init__(self):
        """Initialize Thompson Sampling algorithm."""
        self.variant_stats = {}
    
    def update(self, variant_name: str, reward: float) -> None:
        """
        Update variant statistics with a new reward.
        
        Args:
            variant_name: Name of the variant
            reward: Reward value (0.0 to 1.0 for binary outcomes)
        """
        if variant_name not in self.variant_stats:
            # Beta distribution parameters: alpha (successes), beta (failures)
            self.variant_stats[variant_name] = {"alpha": 1, "beta": 1}
        
        stats = self.variant_stats[variant_name]
        
        # Update Beta distribution parameters
        if reward > 0.5:  # Success
            stats["alpha"] += 1
        else:  # Failure
            stats["beta"] += 1
    
    def select_variant(self, available_variants: List[str]) -> str:
        """
        Select a variant using Thompson Sampling.
        
        Args:
            available_variants: List of variant names to choose from
        
        Returns:
            Selected variant name
        """
        if not available_variants:
            raise ValueError("No variants available for selection")
        
        # Initialize stats for new variants
        for variant in available_variants:
            if variant not in self.variant_stats:
                self.variant_stats[variant] = {"alpha": 1, "beta": 1}
        
        # Sample from Beta distribution for each variant
        samples = {}
        for variant in available_variants:
            stats = self.variant_stats[variant]
            # Beta distribution sampling (simplified using random)
            # In production, use scipy.stats.beta.rvs()
            sample = self._beta_sample(stats["alpha"], stats["beta"])
            samples[variant] = sample
        
        # Select variant with highest sample
        best_variant = max(samples.keys(), key=lambda k: samples[k])
        return best_variant
    
    def _beta_sample(self, alpha: float, beta: float) -> float:
        """
        Simple Beta distribution sampling using gamma distributions.
        For production, use scipy.stats.beta.rvs()
        """
        # Simplified sampling - in production use scipy
        # Beta(alpha, beta) = Gamma(alpha) / (Gamma(alpha) + Gamma(beta))
        x = random.gammavariate(alpha, 1)
        y = random.gammavariate(beta, 1)
        return x / (x + y) if (x + y) > 0 else 0.5
    
    def get_probabilities(self) -> Dict[str, float]:
        """Get current probability estimates for each variant."""
        probabilities = {}
        for variant, stats in self.variant_stats.items():
            # Expected value of Beta distribution
            alpha = stats["alpha"]
            beta = stats["beta"]
            probabilities[variant] = alpha / (alpha + beta)
        return probabilities


class BayesianABTest:
    """
    Bayesian A/B testing with credible intervals.
    
    Provides more intuitive interpretation than frequentist approaches:
    - Probability that variant A is better than variant B
    - Credible intervals for effect sizes
    - No p-hacking issues
    """
    
    def __init__(self):
        """Initialize Bayesian A/B test."""
        pass
    
    def calculate_credible_interval(
        self,
        successes: int,
        trials: int,
        confidence: float = 0.95
    ) -> Tuple[float, float]:
        """
        Calculate Bayesian credible interval for success rate.
        
        Args:
            successes: Number of successes
            trials: Total number of trials
            confidence: Confidence level (default 95%)
        
        Returns:
            Tuple of (lower_bound, upper_bound)
        """
        if trials == 0:
            return (0.0, 1.0)
        
        # Using Beta distribution with Jeffrey's prior
        alpha = successes + 0.5
        beta = trials - successes + 0.5
        
        # Calculate percentiles (simplified - in production use scipy.stats.beta.ppf)
        lower_percentile = (1 - confidence) / 2
        upper_percentile = 1 - lower_percentile
        
        # Approximate quantiles using normal approximation
        mean = alpha / (alpha + beta)
        variance = (alpha * beta) / ((alpha + beta) ** 2 * (alpha + beta + 1))
        std = math.sqrt(variance)
        
        # Z-scores for confidence interval
        z = 1.96 if confidence == 0.95 else 2.576  # 95% or 99%
        
        lower = max(0.0, mean - z * std)
        upper = min(1.0, mean + z * std)
        
        return (lower, upper)
    
    def probability_b_better_than_a(
        self,
        a_successes: int,
        a_trials: int,
        b_successes: int,
        b_trials: int,
        num_samples: int = 10000
    ) -> float:
        """
        Calculate probability that variant B is better than variant A.
        
        Args:
            a_successes: Successes for variant A
            a_trials: Trials for variant A
            b_successes: Successes for variant B
            b_trials: Trials for variant B
            num_samples: Number of Monte Carlo samples
        
        Returns:
            Probability that B > A (0.0 to 1.0)
        """
        if a_trials == 0 or b_trials == 0:
            return 0.5
        
        # Beta distributions for each variant
        alpha_a = a_successes + 1
        beta_a = a_trials - a_successes + 1
        alpha_b = b_successes + 1
        beta_b = b_trials - b_successes + 1
        
        # Monte Carlo sampling
        b_better_count = 0
        for _ in range(num_samples):
            sample_a = random.betavariate(alpha_a, beta_a)
            sample_b = random.betavariate(alpha_b, beta_b)
            if sample_b > sample_a:
                b_better_count += 1
        
        return b_better_count / num_samples


class SequentialTesting:
    """
    Sequential testing for early stopping.
    
    Allows stopping experiments early when there's strong evidence
    for a winner, saving resources while maintaining statistical rigor.
    """
    
    def __init__(
        self,
        alpha: float = 0.05,
        beta: float = 0.20,
        min_effect_size: float = 0.05
    ):
        """
        Initialize sequential testing.
        
        Args:
            alpha: Type I error rate (false positive)
            beta: Type II error rate (false negative)
            min_effect_size: Minimum detectable effect size
        """
        self.alpha = alpha
        self.beta = beta
        self.min_effect_size = min_effect_size
    
    def should_stop(
        self,
        control_successes: int,
        control_trials: int,
        variant_successes: int,
        variant_trials: int
    ) -> Tuple[bool, Optional[str]]:
        """
        Determine if experiment should stop early.
        
        Args:
            control_successes: Successes in control group
            control_trials: Trials in control group
            variant_successes: Successes in variant group
            variant_trials: Trials in variant group
        
        Returns:
            Tuple of (should_stop, winner) where winner is 'control', 'variant', or None
        """
        if control_trials < 10 or variant_trials < 10:
            # Need minimum data
            return (False, None)
        
        # Calculate rates
        control_rate = control_successes / control_trials if control_trials > 0 else 0
        variant_rate = variant_successes / variant_trials if variant_trials > 0 else 0
        
        # Calculate effect size
        effect_size = abs(variant_rate - control_rate)
        
        if effect_size < self.min_effect_size:
            # Effect too small to matter
            return (False, None)
        
        # Use Bayesian approach to decide
        bayesian = BayesianABTest()
        prob_variant_better = bayesian.probability_b_better_than_a(
            control_successes, control_trials,
            variant_successes, variant_trials
        )
        
        # Strong evidence for variant
        if prob_variant_better > (1 - self.alpha):
            return (True, 'variant')
        
        # Strong evidence for control
        if prob_variant_better < self.alpha:
            return (True, 'control')
        
        # Not enough evidence yet
        return (False, None)


class ConfidenceIntervals:
    """Calculate confidence intervals for various metrics."""
    
    @staticmethod
    def proportion_ci(
        successes: int,
        trials: int,
        confidence: float = 0.95
    ) -> Tuple[float, float]:
        """
        Calculate confidence interval for a proportion using Wilson score interval.
        
        More accurate than normal approximation for small samples.
        
        Args:
            successes: Number of successes
            trials: Total trials
            confidence: Confidence level
        
        Returns:
            Tuple of (lower_bound, upper_bound)
        """
        if trials == 0:
            return (0.0, 1.0)
        
        p = successes / trials
        n = trials
        
        # Z-score for confidence level
        z = 1.96 if confidence == 0.95 else 2.576
        
        # Wilson score interval
        denominator = 1 + z**2 / n
        center = (p + z**2 / (2*n)) / denominator
        margin = z * math.sqrt((p * (1-p) / n + z**2 / (4*n**2))) / denominator
        
        lower = max(0.0, center - margin)
        upper = min(1.0, center + margin)
        
        return (lower, upper)
    
    @staticmethod
    def mean_ci(
        values: List[float],
        confidence: float = 0.95
    ) -> Tuple[float, float]:
        """
        Calculate confidence interval for a mean.
        
        Args:
            values: List of observed values
            confidence: Confidence level
        
        Returns:
            Tuple of (lower_bound, upper_bound)
        """
        if not values:
            return (0.0, 0.0)
        
        n = len(values)
        mean = sum(values) / n
        
        if n == 1:
            return (mean, mean)
        
        # Calculate standard error
        variance = sum((x - mean) ** 2 for x in values) / (n - 1)
        se = math.sqrt(variance / n)
        
        # T-score (approximated as Z for large samples)
        t = 1.96 if confidence == 0.95 else 2.576
        
        margin = t * se
        
        return (mean - margin, mean + margin)


def integrate_advanced_analysis(experiment_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Enhance experiment analysis with advanced statistical methods.
    
    Args:
        experiment_data: Experiment data from ABTestingEngine
    
    Returns:
        Enhanced analysis with advanced metrics
    """
    results = {
        "bayesian_analysis": {},
        "sequential_test": {},
        "confidence_intervals": {},
        "thompson_sampling": {}
    }
    
    variants = experiment_data.get("variants", {})
    metrics = experiment_data.get("metrics", [])
    
    if not variants or not metrics:
        return results
    
    # Bayesian Analysis
    bayesian = BayesianABTest()
    
    # Compare all variant pairs
    variant_names = list(variants.keys())
    if len(variant_names) >= 2:
        control = variant_names[0]
        
        for variant in variant_names[1:]:
            control_data = variants[control]
            variant_data = variants[variant]
            
            # Assuming 'success_rate' metric exists
            if 'success_rate' in metrics:
                control_successes = sum(1 for m in control_data.get("metrics", {}).get("success_rate", []) if m > 0.5)
                control_trials = control_data.get("total_samples", 0)
                
                variant_successes = sum(1 for m in variant_data.get("metrics", {}).get("success_rate", []) if m > 0.5)
                variant_trials = variant_data.get("total_samples", 0)
                
                prob = bayesian.probability_b_better_than_a(
                    control_successes, control_trials,
                    variant_successes, variant_trials
                )
                
                results["bayesian_analysis"][f"{variant}_vs_{control}"] = {
                    "probability_better": prob,
                    "confidence": "high" if prob > 0.95 or prob < 0.05 else "medium" if prob > 0.8 or prob < 0.2 else "low"
                }
    
    # Sequential Testing
    if len(variant_names) >= 2:
        sequential = SequentialTesting()
        control = variant_names[0]
        variant = variant_names[1]
        
        control_data = variants[control]
        variant_data = variants[variant]
        
        if 'success_rate' in metrics:
            control_successes = sum(1 for m in control_data.get("metrics", {}).get("success_rate", []) if m > 0.5)
            control_trials = control_data.get("total_samples", 0)
            
            variant_successes = sum(1 for m in variant_data.get("metrics", {}).get("success_rate", []) if m > 0.5)
            variant_trials = variant_data.get("total_samples", 0)
            
            should_stop, winner = sequential.should_stop(
                control_successes, control_trials,
                variant_successes, variant_trials
            )
            
            results["sequential_test"] = {
                "should_stop": should_stop,
                "winner": winner,
                "recommendation": "Stop experiment early" if should_stop else "Continue collecting data"
            }
    
    # Confidence Intervals
    ci_calc = ConfidenceIntervals()
    
    for variant_name, variant_data in variants.items():
        variant_ci = {}
        
        for metric in metrics:
            metric_values = variant_data.get("metrics", {}).get(metric, [])
            
            if metric == "success_rate":
                # Binary metric
                successes = sum(1 for v in metric_values if v > 0.5)
                trials = len(metric_values)
                lower, upper = ci_calc.proportion_ci(successes, trials)
            else:
                # Continuous metric
                if metric_values:
                    lower, upper = ci_calc.mean_ci(metric_values)
                else:
                    lower, upper = (0.0, 0.0)
            
            variant_ci[metric] = {
                "lower": lower,
                "upper": upper,
                "width": upper - lower
            }
        
        results["confidence_intervals"][variant_name] = variant_ci
    
    # Thompson Sampling Recommendations
    thompson = ThompsonSampling()
    
    # Initialize with experiment data
    for variant_name, variant_data in variants.items():
        if 'success_rate' in metrics:
            for rate in variant_data.get("metrics", {}).get("success_rate", []):
                thompson.update(variant_name, rate)
    
    results["thompson_sampling"] = {
        "probabilities": thompson.get_probabilities(),
        "recommended_variant": thompson.select_variant(list(variants.keys())) if variants else None
    }
    
    return results


def main():
    """CLI interface for advanced A/B testing."""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: ab_testing_advanced.py <command> [args...]")
        print("\nCommands:")
        print("  thompson-select <variant1> <variant2> ... - Select variant using Thompson Sampling")
        print("  bayesian-compare <exp_id> - Bayesian analysis of experiment")
        print("  sequential-test <exp_id> - Check if experiment should stop early")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "thompson-select":
        variants = sys.argv[2:]
        if len(variants) < 2:
            print("Error: Need at least 2 variants")
            sys.exit(1)
        
        thompson = ThompsonSampling()
        selected = thompson.select_variant(variants)
        print(json.dumps({"selected_variant": selected}))
    
    elif command == "bayesian-compare":
        # Would integrate with ABTestingEngine
        print("Bayesian comparison - integration pending")
    
    elif command == "sequential-test":
        # Would integrate with ABTestingEngine
        print("Sequential testing - integration pending")
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
