#!/usr/bin/env python3
"""
Autonomous A/B Testing Demonstration

Creates a demo experiment to showcase the autonomous testing system.

Author: @accelerate-specialist
"""

import json
import sys
from pathlib import Path

# Add tools to path
sys.path.insert(0, str(Path(__file__).parent.parent / "tools"))

from ab_testing_engine import ABTestingEngine
from ab_testing_advanced import ThompsonSampling, BayesianABTest


def create_demo_experiment():
    """Create a demonstration experiment."""
    print("🔬 Creating Autonomous A/B Testing Demo Experiment\n")
    
    engine = ABTestingEngine()
    
    # Create a realistic experiment for workflow optimization
    variants = {
        "control": {
            "description": "Current configuration",
            "schedule": "0 */6 * * *",
            "timeout": 300,
            "max_retries": 3
        },
        "optimized": {
            "description": "Optimized configuration",
            "schedule": "0 */4 * * *",
            "timeout": 450,
            "max_retries": 4
        },
        "aggressive": {
            "description": "Aggressive configuration",
            "schedule": "0 */2 * * *",
            "timeout": 600,
            "max_retries": 5
        }
    }
    
    exp_id = engine.create_experiment(
        name="Demo: Workflow Schedule Optimization",
        description="Demonstrating autonomous A/B testing with different workflow configurations",
        variants=variants,
        metrics=["execution_time", "success_rate", "resource_usage"],
        workflow_name="demo-workflow"
    )
    
    print(f"✅ Created experiment: {exp_id}")
    print(f"   Variants: {len(variants)}")
    print(f"   Metrics: execution_time, success_rate, resource_usage\n")
    
    return exp_id


def simulate_data_collection(exp_id):
    """Simulate data collection for the demo experiment."""
    print("📊 Simulating data collection...\n")
    
    engine = ABTestingEngine()
    
    # Simulate 20 samples for each variant
    # Optimized variant performs best, aggressive is fast but less reliable
    import random
    
    for i in range(20):
        # Control: baseline performance
        engine.record_sample(
            experiment_id=exp_id,
            variant_name="control",
            metrics={
                "execution_time": random.gauss(100, 10),
                "success_rate": random.gauss(0.85, 0.05),
                "resource_usage": random.gauss(50, 5)
            },
            metadata={"sample": i}
        )
        
        # Optimized: 15% faster, 10% better success rate
        engine.record_sample(
            experiment_id=exp_id,
            variant_name="optimized",
            metrics={
                "execution_time": random.gauss(85, 8),
                "success_rate": random.gauss(0.93, 0.03),
                "resource_usage": random.gauss(55, 5)
            },
            metadata={"sample": i}
        )
        
        # Aggressive: fastest but lower success rate
        engine.record_sample(
            experiment_id=exp_id,
            variant_name="aggressive",
            metrics={
                "execution_time": random.gauss(70, 12),
                "success_rate": random.gauss(0.78, 0.08),
                "resource_usage": random.gauss(70, 8)
            },
            metadata={"sample": i}
        )
    
    print("✅ Simulated 20 samples per variant (60 total)")


def demonstrate_thompson_sampling(exp_id):
    """Demonstrate Thompson Sampling variant selection."""
    print("\n🎯 Thompson Sampling Demo\n")
    
    engine = ABTestingEngine()
    details = engine.get_experiment_details(exp_id)
    
    thompson = ThompsonSampling()
    
    # Initialize with experiment data
    for variant_name, variant_data in details["variants"].items():
        success_rates = variant_data["metrics"].get("success_rate", [])
        for rate in success_rates:
            thompson.update(variant_name, rate)
    
    # Show probabilities
    probs = thompson.get_probabilities()
    print("Learned probabilities:")
    for variant, prob in sorted(probs.items(), key=lambda x: x[1], reverse=True):
        print(f"  {variant:12s}: {prob:.3f}")
    
    # Simulate 100 selections
    print("\nVariant selection (100 trials):")
    selections = [thompson.select_variant(list(probs.keys())) for _ in range(100)]
    
    for variant in probs.keys():
        count = selections.count(variant)
        bar = "█" * (count // 2)
        print(f"  {variant:12s}: {count:3d} {bar}")
    
    print("\n✅ Thompson Sampling favors better performers while exploring")


def demonstrate_bayesian_analysis(exp_id):
    """Demonstrate Bayesian A/B testing."""
    print("\n🔍 Bayesian Analysis Demo\n")
    
    engine = ABTestingEngine()
    details = engine.get_experiment_details(exp_id)
    
    bayesian = BayesianABTest()
    
    # Compare optimized vs control
    control_data = details["variants"]["control"]
    optimized_data = details["variants"]["optimized"]
    
    control_successes = sum(1 for r in control_data["metrics"]["success_rate"] if r > 0.5)
    control_trials = control_data["total_samples"]
    
    optimized_successes = sum(1 for r in optimized_data["metrics"]["success_rate"] if r > 0.5)
    optimized_trials = optimized_data["total_samples"]
    
    prob = bayesian.probability_b_better_than_a(
        control_successes, control_trials,
        optimized_successes, optimized_trials
    )
    
    print("Comparing 'optimized' vs 'control':")
    print(f"  Control success rate: {control_successes}/{control_trials} = {control_successes/control_trials:.2%}")
    print(f"  Optimized success rate: {optimized_successes}/{optimized_trials} = {optimized_successes/optimized_trials:.2%}")
    print(f"  Probability optimized is better: {prob:.1%}")
    
    if prob > 0.95:
        print("  ✅ High confidence optimized is better!")
    elif prob > 0.80:
        print("  ⚖️  Moderate evidence optimized is better")
    else:
        print("  ⚠️  Not enough evidence yet")
    
    # Calculate credible intervals
    control_ci = bayesian.calculate_credible_interval(control_successes, control_trials)
    optimized_ci = bayesian.calculate_credible_interval(optimized_successes, optimized_trials)
    
    print(f"\n95% Credible Intervals:")
    print(f"  Control:   [{control_ci[0]:.3f}, {control_ci[1]:.3f}]")
    print(f"  Optimized: [{optimized_ci[0]:.3f}, {optimized_ci[1]:.3f}]")


def demonstrate_full_analysis(exp_id):
    """Demonstrate full experiment analysis with advanced methods."""
    print("\n📈 Full Analysis with Advanced Methods\n")
    
    engine = ABTestingEngine()
    
    # Run analysis with advanced methods
    analysis = engine.analyze_experiment(exp_id, use_advanced=True)
    
    print(f"Status: {analysis['status']}")
    
    if analysis['status'] == 'analyzed':
        print("\nVariant Statistics:")
        for variant, stats in analysis['variant_statistics'].items():
            print(f"\n  {variant}:")
            for metric, values in stats.items():
                if isinstance(values, dict):
                    print(f"    {metric}:")
                    for key, val in values.items():
                        if isinstance(val, float):
                            print(f"      {key}: {val:.2f}")
                        else:
                            print(f"      {key}: {val}")
        
        if analysis.get('winner'):
            winner = analysis['winner']
            print(f"\n🏆 Winner: {winner['variant']}")
            print(f"   Improvement: {winner['improvement']:.2%}")
            print(f"   Confidence: {winner['confidence']}")
        
        # Show advanced analysis
        if 'advanced_analysis' in analysis and 'error' not in analysis['advanced_analysis']:
            adv = analysis['advanced_analysis']
            
            print("\n🔬 Advanced Analysis:")
            
            if 'bayesian_analysis' in adv and adv['bayesian_analysis']:
                print("\n  Bayesian Comparisons:")
                for comparison, results in adv['bayesian_analysis'].items():
                    print(f"    {comparison}: {results['probability_better']:.2%} confidence")
            
            if 'sequential_test' in adv and adv['sequential_test']:
                seq = adv['sequential_test']
                print(f"\n  Sequential Test:")
                print(f"    Should stop: {seq['should_stop']}")
                print(f"    Recommendation: {seq['recommendation']}")
            
            if 'thompson_sampling' in adv and adv['thompson_sampling']:
                ts = adv['thompson_sampling']
                print(f"\n  Thompson Sampling:")
                print(f"    Recommended: {ts['recommended_variant']}")
                print(f"    Probabilities:")
                for variant, prob in ts['probabilities'].items():
                    print(f"      {variant}: {prob:.3f}")


def main():
    """Run the demonstration."""
    print("=" * 70)
    print("🤖 Autonomous A/B Testing System - Demonstration")
    print("=" * 70)
    print("\nBy @accelerate-specialist")
    print("Showcasing elegant algorithms for autonomous optimization\n")
    
    # Create demo experiment
    exp_id = create_demo_experiment()
    
    # Simulate data collection
    simulate_data_collection(exp_id)
    
    # Demonstrate Thompson Sampling
    demonstrate_thompson_sampling(exp_id)
    
    # Demonstrate Bayesian analysis
    demonstrate_bayesian_analysis(exp_id)
    
    # Show full analysis
    demonstrate_full_analysis(exp_id)
    
    print("\n" + "=" * 70)
    print("✨ Demo Complete!")
    print("=" * 70)
    print(f"\nExperiment ID: {exp_id}")
    print("View details: python3 tools/ab_testing_engine.py details", exp_id)
    print("List experiments: python3 tools/ab_testing_engine.py list")
    print("\n")


if __name__ == "__main__":
    main()
