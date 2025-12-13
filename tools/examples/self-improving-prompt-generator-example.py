#!/usr/bin/env python3
"""
Example: Using the Self-Improving Prompt Generator

This example demonstrates the complete workflow of the self-improving
prompt generator system.

Created by @create-botter as a reference implementation.
"""

import sys
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import with module loading
import importlib.util
spec = importlib.util.spec_from_file_location(
    "self_improving_prompt_generator",
    Path(__file__).parent.parent / "self-improving-prompt-generator.py"
)
sipg_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sipg_module)

SelfImprovingPromptGenerator = sipg_module.SelfImprovingPromptGenerator
PromptGenerationRequest = sipg_module.PromptGenerationRequest
PromptFeedback = sipg_module.PromptFeedback


def main():
    """Demonstrate the self-improving prompt generator"""
    
    print("=" * 70)
    print("Self-Improving Prompt Generator - Example")
    print("=" * 70)
    print()
    
    # Initialize the generator
    print("📦 Initializing generator...")
    generator = SelfImprovingPromptGenerator()
    print("✓ Generator initialized")
    print()
    
    # Example 1: Generate a feature request prompt
    print("📝 Example 1: Feature Request Prompt")
    print("-" * 70)
    
    request = PromptGenerationRequest(
        issue_number=1001,
        issue_title="Add real-time notifications",
        issue_body="Implement WebSocket-based real-time notifications for user events",
        issue_labels=["feature", "enhancement"],
        agent_name="create-botter"
    )
    
    prompt = generator.generate_prompt(request)
    
    print(f"Prompt ID: {prompt.prompt_id}")
    print(f"Category: {prompt.category}")
    print(f"Quality Score: {prompt.quality_score:.2f}")
    print(f"Learning Insights: {prompt.learning_insights_used}")
    print()
    print("Generated Prompt:")
    print(prompt.prompt_text[:300] + "...")
    print()
    
    # Example 2: Generate a bug fix prompt
    print("📝 Example 2: Bug Fix Prompt")
    print("-" * 70)
    
    request = PromptGenerationRequest(
        issue_number=1002,
        issue_title="Fix authentication timeout",
        issue_body="Users are getting logged out after 5 minutes instead of 30 minutes",
        issue_labels=["bug", "security"],
        agent_name="secure-specialist"
    )
    
    prompt = generator.generate_prompt(request)
    
    print(f"Prompt ID: {prompt.prompt_id}")
    print(f"Category: {prompt.category}")
    print(f"Quality Score: {prompt.quality_score:.2f}")
    print()
    
    # Example 3: Record feedback
    print("📊 Example 3: Recording Feedback")
    print("-" * 70)
    
    # Simulate successful resolution
    feedback = PromptFeedback(
        prompt_id=prompt.prompt_id,
        success=True,
        resolution_time_hours=12.5,
        quality_rating=0.9,
        notes="Prompt was clear and helpful"
    )
    
    generator.record_feedback(feedback)
    print(f"✓ Feedback recorded for {feedback.prompt_id}")
    print(f"  Success: {feedback.success}")
    print(f"  Resolution Time: {feedback.resolution_time_hours}h")
    print(f"  Quality Rating: {feedback.quality_rating}")
    print()
    
    # Example 4: Performance report
    print("📈 Example 4: Performance Report")
    print("-" * 70)
    
    report = generator.get_performance_report()
    
    print(f"Total Prompts Generated: {report['total_prompts_generated']}")
    print(f"Total Feedback Received: {report['total_feedback_received']}")
    print()
    
    if report.get('overall_metrics'):
        print("Overall Metrics:")
        print(f"  Success Rate: {report['overall_metrics']['success_rate']:.1%}")
        print(f"  Avg Resolution Time: {report['overall_metrics']['avg_resolution_time_hours']:.1f}h")
        print()
    
    if report.get('templates'):
        print("Template Performance:")
        for template_id, stats in report['templates'].items():
            print(f"  {template_id}:")
            print(f"    Total Uses: {stats['total_uses']}")
            print(f"    Success Rate: {stats['success_rate']:.1%}")
            print(f"    Quality Score: {stats['quality_score']:.2f}")
        print()
    
    # Example 5: Learning integration stats
    if report.get('learning_integration'):
        print("Learning Integration:")
        learning = report['learning_integration']
        print(f"  Total Insights: {learning.get('total_insights', 0)}")
        
        if learning.get('categories'):
            print("  Categories:")
            for category, count in learning['categories'].items():
                print(f"    {category}: {count}")
        print()
    
    print("=" * 70)
    print("✅ Example Complete!")
    print()
    print("The self-improving prompt generator:")
    print("  1. Generated prompts with learning insights")
    print("  2. Recorded feedback for continuous improvement")
    print("  3. Tracked performance metrics")
    print("  4. Ready to optimize future prompts!")
    print()
    print("Try it yourself:")
    print("  python3 tools/self-improving-prompt-generator.py generate \\")
    print("    --issue 123 --title 'Your Title' --agent 'create-botter'")
    print("=" * 70)


if __name__ == "__main__":
    main()
