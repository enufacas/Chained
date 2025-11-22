#!/usr/bin/env python3
"""
Demo: Self-Improving Prompt Generator with Reinforcement Learning

Demonstrates the complete workflow of prompt generation, outcome recording,
pattern learning, and continuous optimization.

Created by @APIs-architect - demonstrating rigorous engineering in action.
"""

import sys
import os
import tempfile
import shutil

# Add tools directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'tools'))

import importlib.util

spec = importlib.util.spec_from_file_location(
    "prompt_generator",
    os.path.join(os.path.dirname(__file__), '..', 'tools', 'prompt-generator.py')
)
prompt_generator_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(prompt_generator_module)

PromptGenerator = prompt_generator_module.PromptGenerator


def print_section(title):
    """Print a section header"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")


def demo_basic_generation():
    """Demo 1: Basic prompt generation"""
    print_section("Demo 1: Basic Prompt Generation")
    
    # Create temp directory for demo
    temp_dir = tempfile.mkdtemp()
    
    try:
        # Initialize generator with reinforcement learning
        generator = PromptGenerator(
            data_dir=temp_dir,
            enable_learning=False,  # Disable to avoid external dependencies
            enable_reinforcement=True
        )
        
        print("Generating prompt for bug fix...")
        prompt, template_id = generator.generate_prompt(
            issue_body="User authentication fails when using special characters in password",
            category="bug_fix",
            agent="engineer-master"
        )
        
        print(f"\nTemplate Used: {template_id}")
        print(f"\nGenerated Prompt:\n{'-'*60}")
        print(prompt[:500] + "..." if len(prompt) > 500 else prompt)
        
    finally:
        shutil.rmtree(temp_dir)


def demo_outcome_recording():
    """Demo 2: Recording outcomes with feedback"""
    print_section("Demo 2: Recording Outcomes and Learning")
    
    temp_dir = tempfile.mkdtemp()
    
    try:
        generator = PromptGenerator(
            data_dir=temp_dir,
            enable_learning=False,
            enable_reinforcement=True
        )
        
        # Simulate several successful outcomes
        print("Recording successful outcomes with feedback...\n")
        
        success_scenarios = [
            {
                "prompt_id": "bug_fix_systematic",
                "issue": 101,
                "feedback": "Clear step-by-step approach made debugging straightforward"
            },
            {
                "prompt_id": "bug_fix_systematic",
                "issue": 102,
                "feedback": "Systematic methodology with thorough testing led to quick resolution"
            },
            {
                "prompt_id": "bug_fix_systematic",
                "issue": 103,
                "feedback": "Comprehensive approach with examples helped identify root cause"
            },
        ]
        
        for scenario in success_scenarios:
            generator.record_outcome(
                prompt_id=scenario["prompt_id"],
                issue_number=scenario["issue"],
                success=True,
                resolution_time_hours=2.5,
                agent_used="engineer-master",
                feedback_text=scenario["feedback"]
            )
            print(f"✓ Issue #{scenario['issue']}: {scenario['feedback']}")
        
        # Check what patterns were learned
        print("\nLearned Patterns:")
        if generator.reinforcement_learner:
            patterns = generator.reinforcement_learner.get_top_patterns(limit=5)
            for pattern in patterns:
                print(f"  • {pattern.pattern}: {pattern.effectiveness:.0%} effective")
        
    finally:
        shutil.rmtree(temp_dir)


def demo_pattern_enhancement():
    """Demo 3: Prompt enhancement with learned patterns"""
    print_section("Demo 3: Enhanced Prompts with Learned Patterns")
    
    temp_dir = tempfile.mkdtemp()
    
    try:
        generator = PromptGenerator(
            data_dir=temp_dir,
            enable_learning=False,
            enable_reinforcement=True
        )
        
        # First, teach the system some patterns
        print("Teaching the system successful patterns...\n")
        
        for i in range(5):
            generator.record_outcome(
                prompt_id="feature_rigorous",
                issue_number=200 + i,
                success=True,
                resolution_time_hours=4.0,
                feedback_text="Clear structure with step-by-step guidance and comprehensive testing"
            )
        
        print("✓ System learned from 5 successful outcomes\n")
        
        # Now generate a new prompt
        print("Generating enhanced prompt for feature development...")
        prompt, template_id = generator.generate_prompt(
            issue_body="Implement user profile editing functionality",
            category="feature",
            agent="create-guru"
        )
        
        print(f"\nEnhanced Prompt:\n{'-'*60}")
        
        # Show the enhancement section
        if "Key Success Patterns" in prompt:
            idx = prompt.find("Key Success Patterns")
            relevant_section = prompt[idx:idx+300]
            print(relevant_section + "...")
        else:
            print("(Enhancement will appear after more patterns are learned)")
        
    finally:
        shutil.rmtree(temp_dir)


def demo_optimization():
    """Demo 4: Optimization recommendations"""
    print_section("Demo 4: Optimization Recommendations")
    
    temp_dir = tempfile.mkdtemp()
    
    try:
        generator = PromptGenerator(
            data_dir=temp_dir,
            enable_learning=False,
            enable_reinforcement=True
        )
        
        # Simulate mixed outcomes
        print("Recording mixed outcomes for documentation template...\n")
        
        # Some successes
        for i in range(3):
            generator.record_outcome(
                prompt_id="documentation_precise",
                issue_number=300 + i,
                success=True,
                resolution_time_hours=1.5,
                feedback_text="Clear and comprehensive documentation with examples"
            )
            print(f"✓ Issue #{300+i}: Success")
        
        # Some failures
        for i in range(3):
            generator.record_outcome(
                prompt_id="documentation_precise",
                issue_number=310 + i,
                success=False,
                resolution_time_hours=3.0,
                error_type="incomplete",
                feedback_text="Documentation was missing important details and unclear"
            )
            print(f"✗ Issue #{310+i}: Failure (missing details)")
        
        print("\nGenerating optimization recommendations...")
        
        if generator.reinforcement_learner:
            recommendations = generator.reinforcement_learner.generate_optimization_recommendations(
                "documentation_precise"
            )
            
            print(f"\nRecommendations ({len(recommendations)} found):")
            for rec in recommendations[:5]:  # Show top 5
                priority_icon = "🔴" if rec['priority'] == 'high' else "🟡" if rec['priority'] == 'medium' else "🟢"
                print(f"  {priority_icon} [{rec['priority'].upper()}] {rec['action']}")
        
    finally:
        shutil.rmtree(temp_dir)


def demo_diversity_tracking():
    """Demo 5: Diversity tracking"""
    print_section("Demo 5: Pattern Diversity Tracking")
    
    temp_dir = tempfile.mkdtemp()
    
    try:
        generator = PromptGenerator(
            data_dir=temp_dir,
            enable_learning=False,
            enable_reinforcement=True
        )
        
        # Record diverse feedback to create various pattern types
        print("Recording diverse feedback types...\n")
        
        diverse_feedback = [
            ("Clear structure helped", "positive"),
            ("Good examples provided", "positive"),
            ("Comprehensive testing approach", "positive"),
            ("Step-by-step guidance", "positive"),
            ("Thorough documentation", "positive"),
        ]
        
        for i, (feedback, sentiment) in enumerate(diverse_feedback):
            generator.record_outcome(
                prompt_id="security_defensive",
                issue_number=400 + i,
                success=True,
                resolution_time_hours=3.0,
                feedback_text=feedback
            )
            print(f"✓ Recorded: {feedback}")
        
        if generator.reinforcement_learner:
            diversity = generator.reinforcement_learner.calculate_diversity_score()
            
            print(f"\nPattern Diversity Score: {diversity:.2f}")
            print("(1.0 = maximum diversity, 0.0 = convergence to single pattern)")
            
            # Get pattern type distribution
            metrics = generator.reinforcement_learner.get_reinforcement_metrics()
            print("\nPattern Type Distribution:")
            for ptype, count in metrics['pattern_types'].items():
                if count > 0:
                    print(f"  • {ptype}: {count} patterns")
        
    finally:
        shutil.rmtree(temp_dir)


def demo_complete_workflow():
    """Demo 6: Complete workflow"""
    print_section("Demo 6: Complete Autonomous Workflow")
    
    temp_dir = tempfile.mkdtemp()
    
    try:
        generator = PromptGenerator(
            data_dir=temp_dir,
            enable_learning=False,
            enable_reinforcement=True
        )
        
        print("Simulating complete autonomous improvement cycle...\n")
        
        # Step 1: Initial generation
        print("STEP 1: Generate initial prompt")
        prompt1, template_id = generator.generate_prompt(
            issue_body="Refactor authentication module for better maintainability",
            category="refactor",
            agent="organize-guru"
        )
        print(f"✓ Generated prompt using {template_id}")
        
        # Step 2: Record outcomes
        print("\nSTEP 2: Record multiple outcomes")
        for i in range(8):
            success = i < 6  # 75% success rate
            feedback = "Clear refactoring guidelines" if success else "Guidelines were unclear"
            
            generator.record_outcome(
                prompt_id=template_id,
                issue_number=500 + i,
                success=success,
                resolution_time_hours=3.0 if success else 5.0,
                feedback_text=feedback
            )
        
        print(f"✓ Recorded 8 outcomes (6 successes, 2 failures)")
        
        # Step 3: Learn patterns
        print("\nSTEP 3: Extract learned patterns")
        if generator.reinforcement_learner:
            patterns = generator.reinforcement_learner.get_top_patterns(limit=3)
            print(f"✓ Learned {len(patterns)} effective patterns")
        
        # Step 4: Generate optimizations
        print("\nSTEP 4: Generate optimization suggestions")
        suggestions = generator.optimize_templates()
        print(f"✓ Generated {len(suggestions)} optimization suggestions")
        
        # Step 5: Generate improved prompt
        print("\nSTEP 5: Generate enhanced prompt with learned patterns")
        prompt2, _ = generator.generate_prompt(
            issue_body="Refactor API endpoints for consistency",
            category="refactor",
            agent="organize-guru"
        )
        
        enhanced = "Key Success Patterns" in prompt2
        print(f"✓ Generated {'enhanced' if enhanced else 'standard'} prompt")
        
        # Step 6: Performance metrics
        print("\nSTEP 6: Review performance metrics")
        report = generator.get_performance_report()
        
        if 'reinforcement' in report:
            rl_metrics = report['reinforcement']
            print(f"✓ Total feedback: {rl_metrics['total_feedback']}")
            print(f"✓ Effective patterns: {rl_metrics['effective_patterns']}")
            print(f"✓ Diversity score: {rl_metrics['diversity_score']:.2f}")
        
        print("\n" + "="*60)
        print("  Autonomous improvement cycle complete!")
        print("  System continuously learns and optimizes prompts.")
        print("="*60)
        
    finally:
        shutil.rmtree(temp_dir)


def main():
    """Run all demos"""
    print("\n" + "="*60)
    print("  SELF-IMPROVING PROMPT GENERATOR")
    print("  Reinforcement Learning Demo")
    print("  Created by @APIs-architect")
    print("="*60)
    
    demos = [
        ("Basic Generation", demo_basic_generation),
        ("Outcome Recording", demo_outcome_recording),
        ("Pattern Enhancement", demo_pattern_enhancement),
        ("Optimization", demo_optimization),
        ("Diversity Tracking", demo_diversity_tracking),
        ("Complete Workflow", demo_complete_workflow),
    ]
    
    for name, demo_func in demos:
        try:
            demo_func()
        except Exception as e:
            print(f"\nError in {name} demo: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "="*60)
    print("  Demo complete! System is ready for production use.")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
