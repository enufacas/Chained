#!/usr/bin/env python3
"""
Demo: AI Hypothesis Testing Engine
Author: @accelerate-specialist

This demo showcases the hypothesis testing engine's capabilities
by analyzing a sample codebase and generating insights.
"""

import sys
import os
import tempfile
from pathlib import Path

# Add tools to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'tools'))

from hypothesis_testing_engine import HypothesisTestingEngine


def create_sample_codebase(temp_dir: Path):
    """Create a sample codebase for demonstration"""
    
    # Good quality code
    (temp_dir / "good_module.py").write_text('''
def add_numbers(x: int, y: int) -> int:
    """Add two numbers together.
    
    Args:
        x: First number
        y: Second number
    
    Returns:
        Sum of x and y
    """
    try:
        return x + y
    except TypeError:
        return 0

def multiply(a: int, b: int) -> int:
    """Multiply two numbers."""
    return a * b

def test_add_numbers():
    """Test the add_numbers function."""
    assert add_numbers(2, 3) == 5
    assert add_numbers(-1, 1) == 0
''')
    
    # Medium quality code
    (temp_dir / "medium_module.py").write_text('''
def process_data(data, config):
    """Process data with configuration."""
    result = []
    
    if config.get('filter'):
        for item in data:
            if item > 0:
                result.append(item * 2)
    else:
        for item in data:
            result.append(item)
    
    return result

def validate_input(x, y, z):
    if x:
        if y:
            if z:
                return True
    return False

def calculate(a, b, c, d):
    """Complex calculation."""
    result = a
    if b > 0:
        result += b
    if c > 0:
        result *= c
    if d > 0:
        result -= d
    return result
''')
    
    # Poor quality code
    (temp_dir / "poor_module.py").write_text('''
def f(a, b, c, d, e, f, g, h):
    x = a
    if b:
        if c:
            if d:
                if e:
                    if f:
                        if g:
                            x = h
    y = x + 1
    z = y * 2
    w = z - 3
    v = w / 4
    u = v + a
    t = u * b
    s = t - c
    r = s + d
    q = r * e
    p = q - f
    o = p + g
    n = o * h
    m = n - a
    l = m + b
    k = l * c
    j = k - d
    i = j + e
    result = i * f
    return result

def do_stuff(x, y):
    a = x + y
    b = a * 2
    c = b - 3
    d = c / 4
    e = d + 5
    f = e * 6
    g = f - 7
    h = g + 8
    i = h * 9
    j = i - 10
    return j

def xyz():
    pass
''')
    
    print("✅ Created sample codebase:")
    print(f"   - good_module.py (high quality)")
    print(f"   - medium_module.py (medium quality)")
    print(f"   - poor_module.py (poor quality)")


def main():
    """Run the demonstration"""
    print("=" * 70)
    print("🔬 AI HYPOTHESIS TESTING ENGINE - DEMO")
    print("=" * 70)
    print()
    print("This demo shows how the engine generates and tests hypotheses")
    print("about code patterns to discover insights automatically.")
    print()
    
    # Create temporary directory with sample code
    temp_dir = Path(tempfile.mkdtemp())
    print(f"📁 Creating sample codebase in: {temp_dir}")
    print()
    
    try:
        create_sample_codebase(temp_dir)
        print()
        
        # Run hypothesis testing
        output_file = temp_dir / "results.json"
        
        print("🚀 Running Hypothesis Testing Engine...")
        print("-" * 70)
        print()
        
        engine = HypothesisTestingEngine(
            repo_path=str(temp_dir),
            output_file=str(output_file)
        )
        
        results = engine.run(num_hypotheses=12, max_files=10)
        
        print()
        print("=" * 70)
        print("📊 DETAILED RESULTS")
        print("=" * 70)
        print()
        
        # Show metrics
        print(f"📈 Metrics Analyzed: {results['metrics_analyzed']} functions")
        print(f"🧪 Hypotheses Generated: {results['hypotheses_generated']}")
        print(f"✅ Hypotheses Validated: {results['hypotheses_validated']}")
        print(f"📊 Validation Rate: {results['validation_rate']:.1%}")
        print()
        
        # Show validated hypotheses
        validated = [h for h in results['hypotheses'] if h['validated']]
        
        if validated:
            print("🏆 VALIDATED HYPOTHESES:")
            print("-" * 70)
            for i, hyp in enumerate(sorted(validated, key=lambda x: x['confidence'], reverse=True), 1):
                print(f"\n{i}. {hyp['description']}")
                print(f"   Type: {hyp['hypothesis_type']}")
                print(f"   Confidence: {hyp['confidence']:.1%}")
                print(f"   Sample Size: {hyp['sample_size']}")
                print(f"   P-value: {hyp['p_value']:.3f}" if hyp['p_value'] else "")
                
                if hyp['supporting_examples']:
                    print(f"   Examples:")
                    for ex in hyp['supporting_examples'][:2]:
                        func = ex.get('function', 'unknown')
                        print(f"     - {func}")
        
        # Show insights
        print()
        print("💡 ACTIONABLE INSIGHTS:")
        print("-" * 70)
        if results['summary']['insights']:
            for insight in results['summary']['insights']:
                print(f"  • {insight}")
        else:
            print("  • Continue monitoring code patterns")
            print("  • Consider running with more hypotheses")
        
        # Show rejected hypotheses (learning opportunities)
        print()
        print("🔍 REJECTED HYPOTHESES (Learning from what didn't validate):")
        print("-" * 70)
        rejected = [h for h in results['hypotheses'] if not h['validated']]
        for i, hyp in enumerate(rejected[:3], 1):
            print(f"\n{i}. {hyp['description']}")
            print(f"   Why rejected: Data didn't support this hypothesis")
            print(f"   This tells us the codebase doesn't follow this anti-pattern")
        
        # Summary
        print()
        print("=" * 70)
        print("📝 SUMMARY")
        print("=" * 70)
        print()
        print("The hypothesis testing engine:")
        print("  ✓ Automatically discovered code patterns")
        print("  ✓ Generated testable hypotheses")
        print("  ✓ Validated hypotheses with statistical testing")
        print("  ✓ Provided actionable insights")
        print("  ✓ Learned from both validated and rejected hypotheses")
        print()
        print("This demonstrates how AI can discover insights about code")
        print("quality without predefined rules - it learns from the data!")
        print()
        print(f"💾 Full results saved to: {output_file}")
        print()
        
        # Offer to clean up
        print("=" * 70)
        cleanup = input("Clean up temporary files? (y/n): ").lower().strip()
        
        if cleanup == 'y':
            import shutil
            shutil.rmtree(temp_dir)
            print("✓ Cleaned up temporary files")
        else:
            print(f"✓ Files preserved at: {temp_dir}")
    
    except Exception as e:
        print(f"❌ Error during demo: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1
    
    print()
    print("🎉 Demo complete!")
    print()
    print("Try it on your own repository:")
    print("  python3 tools/hypothesis_testing_engine.py --repo-path /your/repo")
    print()
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
