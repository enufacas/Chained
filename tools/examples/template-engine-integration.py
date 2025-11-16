#!/usr/bin/env python3
"""
Template Engine Integration Example

Demonstrates how to use the template engine to generate boilerplate code
from examples in the Chained repository.

Created by @accelerate-specialist - Efficient examples for fast learning.
"""

import sys
from pathlib import Path

# Add tools directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import using exec to handle hyphenated names
import importlib.util

def load_module(file_path, module_name):
    """Load a Python module from a file path"""
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

tools_dir = Path(__file__).parent.parent
template_module = load_module(tools_dir / 'template-engine.py', 'template_engine')
TemplateEngine = template_module.TemplateEngine


def example_basic_usage():
    """Example 1: Basic template extraction and generation"""
    print("=" * 60)
    print("Example 1: Basic Usage")
    print("=" * 60)
    
    # Initialize the engine
    engine = TemplateEngine(examples_dir="tools/examples")
    
    # Extract templates
    count = engine.extract_templates()
    print(f"\n✅ Extracted {count} templates")
    
    # Get statistics
    stats = engine.get_statistics()
    print(f"\n📊 Statistics:")
    print(f"  Total templates: {stats['total_templates']}")
    print(f"  Categories: {', '.join(stats['categories'].keys())}")
    print(f"  Languages: {', '.join(stats['languages'].keys())}")


def example_find_templates():
    """Example 2: Finding specific templates"""
    print("\n" + "=" * 60)
    print("Example 2: Finding Templates")
    print("=" * 60)
    
    engine = TemplateEngine(examples_dir="tools/examples")
    engine.extract_templates()
    
    # Find Python functions
    print("\n🔍 Python function templates:")
    functions = engine.find_templates(category="function", language="python")
    for i, template in enumerate(functions[:5], 1):
        print(f"  {i}. {template.name} (from {Path(template.source_file).name})")
    
    # Find JavaScript templates
    print("\n🔍 JavaScript templates:")
    js_templates = engine.find_templates(language="javascript")
    for i, template in enumerate(js_templates[:3], 1):
        print(f"  {i}. {template.name} ({template.category})")
    
    # Find by name pattern
    print("\n🔍 Templates matching 'test' pattern:")
    test_templates = engine.find_templates(name_pattern=".*test.*")
    for i, template in enumerate(test_templates[:3], 1):
        print(f"  {i}. {template.name} ({template.language})")


def example_generate_code():
    """Example 3: Generating code from templates"""
    print("\n" + "=" * 60)
    print("Example 3: Code Generation")
    print("=" * 60)
    
    engine = TemplateEngine(examples_dir="tools/examples")
    engine.extract_templates()
    
    # Get a template
    templates = engine.find_templates(category="function", language="python")
    
    if templates:
        template = templates[0]
        print(f"\n📝 Using template: {template.name}")
        print(f"   Category: {template.category}")
        print(f"   Language: {template.language}")
        print(f"   Variables: {', '.join(template.variables) if template.variables else 'None'}")
        
        # Generate code
        variables = {var: f"new_{var}" for var in template.variables}
        generated = engine.generate_code(template.template_id, variables)
        
        if generated:
            print(f"\n⚡ Generated in {generated.generation_time_ms:.2f}ms")
            print(f"\n📄 Generated code preview:")
            print("-" * 60)
            # Show first 10 lines
            lines = generated.code.split('\n')[:10]
            for line in lines:
                print(line)
            if len(generated.code.split('\n')) > 10:
                print("...")
            print("-" * 60)


def example_performance_tracking():
    """Example 4: Performance tracking and metrics"""
    print("\n" + "=" * 60)
    print("Example 4: Performance Tracking")
    print("=" * 60)
    
    engine = TemplateEngine(examples_dir="tools/examples", enable_cache=True)
    
    import time
    
    # Measure extraction time
    start = time.time()
    count = engine.extract_templates()
    extraction_time = time.time() - start
    
    print(f"\n⏱️  Extraction Performance:")
    print(f"  Templates extracted: {count}")
    print(f"  Time taken: {extraction_time * 1000:.2f}ms")
    print(f"  Unique templates: {len(engine.templates)}")
    
    # Generate code multiple times to test generation performance
    templates = list(engine.templates.values())
    if templates:
        template = templates[0]
        variables = {var: f"test_{var}" for var in template.variables}
        
        times = []
        for _ in range(10):
            start = time.time()
            engine.generate_code(template.template_id, variables)
            times.append((time.time() - start) * 1000)
        
        print(f"\n⚡ Generation Performance (10 runs):")
        print(f"  Average: {sum(times) / len(times):.3f}ms")
        print(f"  Min: {min(times):.3f}ms")
        print(f"  Max: {max(times):.3f}ms")
        print(f"  Total: {sum(times):.3f}ms")


def example_most_used_templates():
    """Example 5: Most used templates"""
    print("\n" + "=" * 60)
    print("Example 5: Most Used Templates")
    print("=" * 60)
    
    engine = TemplateEngine(examples_dir="tools/examples")
    engine.extract_templates()
    
    # Generate some code to create usage data
    templates = list(engine.templates.values())
    if templates:
        # Use some templates multiple times
        for i in range(min(3, len(templates))):
            template = templates[i]
            variables = {var: f"test_{var}" for var in template.variables}
            for _ in range(i + 1):  # Use first template 1x, second 2x, third 3x
                engine.generate_code(template.template_id, variables)
    
    # Get statistics
    stats = engine.get_statistics()
    
    print("\n🏆 Most Used Templates:")
    for i, template_info in enumerate(stats['most_used_templates'], 1):
        print(f"  {i}. {template_info['name']}")
        print(f"     Category: {template_info['category']}")
        print(f"     Usage: {template_info['usage_count']} times")
        print(f"     Avg gen time: {template_info['avg_generation_time_ms']:.2f}ms")


def example_caching():
    """Example 6: Caching demonstration"""
    print("\n" + "=" * 60)
    print("Example 6: Caching Benefits")
    print("=" * 60)
    
    import time
    
    # First run without cache
    print("\n🔄 First run (extracting from files):")
    engine1 = TemplateEngine(
        examples_dir="tools/examples",
        cache_dir="tools/data/templates",
        enable_cache=True
    )
    start = time.time()
    count1 = engine1.extract_templates(force_refresh=True)
    time1 = time.time() - start
    print(f"  Time: {time1 * 1000:.2f}ms")
    print(f"  Templates: {len(engine1.templates)}")
    
    # Second run with cache
    print("\n⚡ Second run (loading from cache):")
    engine2 = TemplateEngine(
        examples_dir="tools/examples",
        cache_dir="tools/data/templates",
        enable_cache=True
    )
    start = time.time()
    count2 = engine2.extract_templates(force_refresh=False)
    time2 = time.time() - start
    print(f"  Time: {time2 * 1000:.2f}ms")
    print(f"  Templates: {len(engine2.templates)}")
    
    if time1 > 0:
        speedup = time1 / time2 if time2 > 0 else float('inf')
        print(f"\n🚀 Speedup: {speedup:.1f}x faster with cache")


def example_template_details():
    """Example 7: Exploring template details"""
    print("\n" + "=" * 60)
    print("Example 7: Template Details")
    print("=" * 60)
    
    engine = TemplateEngine(examples_dir="tools/examples")
    engine.extract_templates()
    
    # Get a template
    templates = list(engine.templates.values())
    if templates:
        template = templates[0]
        
        print(f"\n🔍 Template Details:")
        print(f"  ID: {template.template_id}")
        print(f"  Name: {template.name}")
        print(f"  Category: {template.category}")
        print(f"  Language: {template.language}")
        print(f"  Variables: {', '.join(template.variables) if template.variables else 'None'}")
        print(f"  Source: {template.source_file}")
        print(f"  Extracted: {template.extracted_at}")
        print(f"  Usage count: {template.usage_count}")
        print(f"  Success rate: {template.success_rate:.2%}")
        
        print(f"\n📝 Pattern Preview:")
        print("-" * 60)
        lines = template.pattern.split('\n')[:15]
        for line in lines:
            print(line)
        if len(template.pattern.split('\n')) > 15:
            print("...")
        print("-" * 60)


def main():
    """Run all examples"""
    print("\n🚀 Template Engine Integration Examples")
    print("⚡ Demonstrating efficient boilerplate generation")
    print("\nCreated by @accelerate-specialist\n")
    
    try:
        example_basic_usage()
        example_find_templates()
        example_generate_code()
        example_performance_tracking()
        example_most_used_templates()
        example_caching()
        example_template_details()
        
        print("\n" + "=" * 60)
        print("✅ All examples completed successfully!")
        print("=" * 60)
        print("\n💡 Tips:")
        print("  - Use caching in production for best performance")
        print("  - Track usage to find most valuable templates")
        print("  - Add your own examples to improve template quality")
        print("  - Combine with other Chained tools for maximum power")
        print("\n⚡ Happy coding with @accelerate-specialist!\n")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
