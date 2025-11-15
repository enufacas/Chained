#!/usr/bin/env python3
"""
Demonstration of HN Insights Code Generator

Shows how the transformer-inspired code generator learns from
Hacker News insights and generates relevant code.

Created by @investigate-champion
"""

import sys
from pathlib import Path

# Add tools to path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from hn_code_generator import HNCodeGenerator
except ImportError:
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "hn_code_generator",
        Path(__file__).parent / "hn-code-generator.py"
    )
    hn_code_generator = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(hn_code_generator)
    HNCodeGenerator = hn_code_generator.HNCodeGenerator


def demo_basic_generation():
    """Demonstrate basic code generation"""
    print("="*70)
    print("DEMO 1: Basic Code Generation")
    print("="*70)
    print()
    
    generator = HNCodeGenerator()
    
    # Generate API wrapper
    print("📝 Generating API wrapper code...")
    gen = generator.generate_code(
        "Create an API wrapper with rate limiting",
        context={
            'class_name': 'HackerNewsAPI',
            'api_name': 'Hacker News'
        }
    )
    
    if gen:
        print(f"✓ Generated code (confidence: {gen.confidence:.2f})")
        print(f"  Template: {gen.template_used}")
        print(f"  Description: {gen.description}")
        print()
        print("Code preview:")
        print("-" * 70)
        print(gen.code[:500] + "...")
        print("-" * 70)
    print()


def demo_hn_insights_analysis():
    """Demonstrate HN insights analysis"""
    print("="*70)
    print("DEMO 2: HN Insights Analysis")
    print("="*70)
    print()
    
    generator = HNCodeGenerator()
    
    print("📊 Analyzing recent HN insights...")
    insights = generator.analyze_hn_insights()
    
    print(f"✓ Found {insights['total_insights']} insights from Hacker News")
    print()
    print("Top 10 trending topics:")
    for i, (topic, count) in enumerate(insights['top_topics'][:10], 1):
        print(f"  {i}. {topic}: {count} mentions")
    print()
    
    print("Recent insight titles:")
    for title in insights['titles'][:5]:
        print(f"  • {title}")
    print()


def demo_learning():
    """Demonstrate learning from insights"""
    print("="*70)
    print("DEMO 3: Learning New Patterns")
    print("="*70)
    print()
    
    generator = HNCodeGenerator()
    
    initial_count = len(generator.templates)
    print(f"Initial templates: {initial_count}")
    print()
    
    print("🧠 Analyzing HN insights for patterns...")
    insights = generator.analyze_hn_insights()
    
    print(f"Found {len(insights['top_topics'])} unique topics")
    print()
    
    print("Learning new templates from recurring topics...")
    generator.learn_from_insights(insights)
    
    new_count = len(generator.templates)
    learned = new_count - initial_count
    
    print(f"✓ Learned {learned} new template(s)")
    print(f"Total templates: {new_count}")
    print()
    
    if learned > 0:
        print("New templates created for:")
        for template in generator.templates[initial_count:]:
            print(f"  • {template.template_id}: {', '.join(template.keywords)}")
    print()


def demo_multiple_generations():
    """Demonstrate multiple code generations"""
    print("="*70)
    print("DEMO 4: Multiple Code Generations")
    print("="*70)
    print()
    
    generator = HNCodeGenerator()
    
    examples = [
        ("Build a data analyzer", {'class_name': 'InsightsAnalyzer', 'data_type': 'HN insights'}),
        ("Create ML model wrapper", {'class_name': 'CodePredictor', 'model_name': 'CodeGen'}),
        ("Build monitoring tool", {'class_name': 'SystemMonitor', 'system_name': 'Chained'}),
        ("API wrapper for REST service", {'class_name': 'GitHubAPI', 'api_name': 'GitHub'})
    ]
    
    print("Generating multiple code examples...")
    print()
    
    for desc, context in examples:
        gen = generator.generate_code(desc, context)
        if gen:
            class_name = context.get('class_name', 'Unknown')
            print(f"✓ {class_name}")
            print(f"  Template: {gen.template_used}")
            print(f"  Confidence: {gen.confidence:.2f}")
            print()
    
    print(f"Total generated: {len(generator.generated_history)} code snippets")
    print()


def demo_statistics():
    """Demonstrate statistics"""
    print("="*70)
    print("DEMO 5: Generation Statistics")
    print("="*70)
    print()
    
    generator = HNCodeGenerator()
    
    # Generate some examples
    for i in range(3):
        generator.generate_code(
            "API wrapper",
            {'class_name': f'API{i}'}
        )
    
    stats = generator.get_statistics()
    
    print("📈 Code Generation Statistics:")
    print()
    print(f"  Total templates: {stats['total_templates']}")
    print(f"  Total generated: {stats['total_generated']}")
    print(f"  Average confidence: {stats['avg_confidence']:.2f}")
    print()
    
    print("Templates by category:")
    for category, count in stats['templates_by_category'].items():
        print(f"  • {category}: {count}")
    print()
    
    print(f"Most used template: {stats['most_used_template']}")
    print()


def demo_complete_workflow():
    """Demonstrate complete workflow"""
    print("="*70)
    print("DEMO 6: Complete Workflow")
    print("="*70)
    print()
    
    generator = HNCodeGenerator()
    
    print("Step 1: Analyze HN insights")
    insights = generator.analyze_hn_insights()
    print(f"  ✓ Found {insights['total_insights']} insights")
    print()
    
    print("Step 2: Learn patterns")
    generator.learn_from_insights(insights)
    print(f"  ✓ Learned patterns, now have {len(generator.templates)} templates")
    print()
    
    print("Step 3: Generate code based on insights")
    
    # Use top topics to generate relevant code
    top_topics = [topic for topic, count in insights['top_topics'][:3]]
    print(f"  Top topics: {', '.join(top_topics)}")
    print()
    
    for topic in top_topics[:2]:
        desc = f"Build tool for {topic}"
        gen = generator.generate_code(desc, {'class_name': f'{topic.title()}Tool'})
        if gen:
            print(f"  ✓ Generated {topic} tool (confidence: {gen.confidence:.2f})")
    print()
    
    print("Step 4: Review statistics")
    stats = generator.get_statistics()
    print(f"  Final stats: {stats['total_generated']} generated, {stats['total_templates']} templates")
    print()


def main():
    """Run all demonstrations"""
    print()
    print("🎭 HN Insights Code Generator - Interactive Demo")
    print("Created by @investigate-champion")
    print()
    
    demos = [
        demo_basic_generation,
        demo_hn_insights_analysis,
        demo_learning,
        demo_multiple_generations,
        demo_statistics,
        demo_complete_workflow
    ]
    
    for demo in demos:
        try:
            demo()
        except Exception as e:
            print(f"⚠️  Demo error: {e}")
            print()
    
    print("="*70)
    print("✅ Demo Complete!")
    print("="*70)
    print()
    print("💡 Next steps:")
    print("  • Run: ./tools/hn-code-generator.py --analyze")
    print("  • Run: ./tools/hn-code-generator.py --generate 'Your description'")
    print("  • Run: ./tools/hn-code-generator.py --learn")
    print("  • Run: ./tools/hn-code-generator.py --stats")
    print()


if __name__ == '__main__':
    main()
