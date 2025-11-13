#!/usr/bin/env python3
"""
Example integration of prompt generator with Chained workflows.

This demonstrates how the prompt generator can be integrated into
the existing Copilot assignment workflow.

Created by @engineer-master as a reference implementation.
"""

import json
import sys
import os
from datetime import datetime, timezone
from pathlib import Path

# Add tools to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'tools'))

# Import with proper module name handling
import importlib.util
spec = importlib.util.spec_from_file_location(
    "prompt_generator",
    os.path.join(os.path.dirname(__file__), '..', '..', 'tools', 'prompt-generator.py')
)
prompt_generator_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(prompt_generator_module)

PromptGenerator = prompt_generator_module.PromptGenerator


def detect_category_from_labels(labels):
    """Detect issue category from GitHub labels"""
    label_map = {
        'bug': 'bug_fix',
        'feature': 'feature',
        'refactor': 'refactor',
        'documentation': 'documentation',
        'investigation': 'investigation',
        'security': 'security'
    }
    
    for label in labels:
        if label.lower() in label_map:
            return label_map[label.lower()]
    
    # Default to feature if no category label
    return 'feature'


def extract_learning_context(learnings_dir='learnings', days=7):
    """Extract recent learnings from TLDR and HN files"""
    learnings_path = Path(learnings_dir)
    if not learnings_path.exists():
        return []
    
    cutoff_date = datetime.now(timezone.utc).timestamp() - (days * 86400)
    recent_learnings = []
    
    # Find recent learning files
    for file in learnings_path.glob('*.json'):
        if file.stat().st_mtime < cutoff_date:
            continue
        
        try:
            with open(file) as f:
                data = json.load(f)
                
                # Extract learnings or trends
                if 'learnings' in data and data['learnings']:
                    recent_learnings.extend(data['learnings'][:3])
                elif 'trends' in data and data['trends']:
                    recent_learnings.extend(data['trends'][:3])
        except Exception as e:
            print(f"Warning: Could not parse {file}: {e}", file=sys.stderr)
    
    return recent_learnings[:5]  # Return top 5 most recent


def generate_enhanced_prompt(issue_number, issue_body, labels, agent):
    """
    Generate an enhanced prompt for Copilot assignment.
    
    This demonstrates the complete integration:
    1. Detect category from labels
    2. Load recent learnings
    3. Generate optimized prompt
    4. Return prompt and metadata
    """
    # Initialize generator
    generator = PromptGenerator()
    
    # Detect category
    category = detect_category_from_labels(labels)
    print(f"📋 Detected category: {category}", file=sys.stderr)
    
    # Extract learning context
    learning_context = extract_learning_context()
    if learning_context:
        print(f"🧠 Found {len(learning_context)} recent learnings", file=sys.stderr)
    
    # Generate prompt
    prompt, template_id = generator.generate_prompt(
        issue_body=issue_body,
        category=category,
        agent=agent,
        learning_context=learning_context if learning_context else None
    )
    
    print(f"✅ Generated prompt using template: {template_id}", file=sys.stderr)
    
    return {
        'prompt': prompt,
        'template_id': template_id,
        'category': category,
        'agent': agent,
        'issue_number': issue_number,
        'learnings_included': len(learning_context) if learning_context else 0
    }


def record_task_outcome(template_id, issue_number, success, resolution_time_hours, agent, error_type=None):
    """
    Record the outcome of a task after completion.
    
    This would be called after a PR is merged or an issue is closed.
    """
    generator = PromptGenerator()
    
    generator.record_outcome(
        prompt_id=template_id,
        issue_number=issue_number,
        success=success,
        resolution_time_hours=resolution_time_hours,
        agent_used=agent,
        error_type=error_type
    )
    
    print(f"✅ Recorded outcome for template {template_id}", file=sys.stderr)
    
    # Get updated performance
    report = generator.get_performance_report()
    if template_id in report['templates']:
        stats = report['templates'][template_id]
        print(f"   Success rate: {stats['success_rate']:.1%}", file=sys.stderr)
        print(f"   Effectiveness: {stats['effectiveness_score']:.2f}", file=sys.stderr)


def main():
    """Example usage demonstrating the integration"""
    
    print("=" * 60)
    print("Self-Improving Prompt Generator - Integration Example")
    print("=" * 60)
    print()
    
    # Example 1: Generate prompt for a bug fix
    print("Example 1: Bug Fix")
    print("-" * 60)
    
    result = generate_enhanced_prompt(
        issue_number=123,
        issue_body="Users are experiencing login failures with 500 errors. The issue appears to be related to session management.",
        labels=['bug', 'high-priority'],
        agent='engineer-master'
    )
    
    print("\nGenerated Prompt Preview:")
    print(result['prompt'][:300] + "...")
    print(f"\nMetadata:")
    print(f"  Template: {result['template_id']}")
    print(f"  Category: {result['category']}")
    print(f"  Learnings: {result['learnings_included']}")
    print()
    
    # Example 2: Generate prompt for a feature
    print("\nExample 2: Feature Implementation")
    print("-" * 60)
    
    result2 = generate_enhanced_prompt(
        issue_number=456,
        issue_body="Implement dark mode support across the application with user preference persistence.",
        labels=['feature', 'enhancement'],
        agent='create-guru'
    )
    
    print(f"Template: {result2['template_id']}")
    print(f"Category: {result2['category']}")
    print()
    
    # Example 3: Record a successful outcome
    print("Example 3: Recording Outcome")
    print("-" * 60)
    
    record_task_outcome(
        template_id=result['template_id'],
        issue_number=123,
        success=True,
        resolution_time_hours=4.5,
        agent='engineer-master'
    )
    print()
    
    # Example 4: Record a failed outcome
    print("Example 4: Recording Failure")
    print("-" * 60)
    
    record_task_outcome(
        template_id='bug_fix_systematic',
        issue_number=789,
        success=False,
        resolution_time_hours=2.0,
        agent='engineer-master',
        error_type='test_failures'
    )
    print()
    
    # Example 5: Get performance report
    print("Example 5: Performance Report")
    print("-" * 60)
    
    generator = PromptGenerator()
    report = generator.get_performance_report()
    
    print(f"\nTotal templates: {len(report['templates'])}")
    
    # Show top performing templates
    sorted_templates = sorted(
        report['templates'].items(),
        key=lambda x: x[1]['effectiveness_score'],
        reverse=True
    )[:3]
    
    print("\nTop 3 Templates by Effectiveness:")
    for template_id, stats in sorted_templates:
        print(f"  {template_id}:")
        print(f"    Success Rate: {stats['success_rate']:.1%}")
        print(f"    Effectiveness: {stats['effectiveness_score']:.2f}")
        print(f"    Uses: {stats['total_uses']}")
    
    print()
    print("=" * 60)
    print("Integration example complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
