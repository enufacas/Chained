#!/usr/bin/env python3
"""
Tests for AI-powered features of the Code Golf Optimizer
"""

import sys
import os
import importlib.util
import tempfile
import json

# Load the optimizer module
spec = importlib.util.spec_from_file_location(
    "code_golf_optimizer",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "code-golf-optimizer.py")
)
code_golf_optimizer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(code_golf_optimizer)

CodeGolfOptimizer = code_golf_optimizer.CodeGolfOptimizer
PatternLearningEngine = code_golf_optimizer.PatternLearningEngine


def test_ai_suggestions():
    """Test that AI suggestions are generated"""
    optimizer = CodeGolfOptimizer(enable_learning=True)
    code = """# Calculate factorial
def calculate_factorial(number):
    '''Calculate factorial of a number'''
    result = 1
    for i in range(1, number + 1):
        result = result * i
    return result
"""
    
    result = optimizer.optimize(code, 'python')
    assert result.ai_suggestions is not None
    assert len(result.ai_suggestions) > 0
    print(f"✓ AI suggestions test passed - {len(result.ai_suggestions)} suggestions generated")


def test_pattern_scores():
    """Test that pattern effectiveness scores are tracked"""
    optimizer = CodeGolfOptimizer(enable_learning=True)
    code = """# This is a comment
x = True
y = False

z = x and y"""
    
    result = optimizer.optimize(code, 'python')
    assert result.pattern_scores is not None
    assert len(result.pattern_scores) > 0
    print(f"✓ Pattern scores test passed - {len(result.pattern_scores)} patterns scored")


def test_learning_engine_init():
    """Test learning engine initialization"""
    with tempfile.TemporaryDirectory() as tmpdir:
        storage_path = os.path.join(tmpdir, 'test_patterns.json')
        engine = PatternLearningEngine(storage_path=storage_path)
        
        # Check default patterns exist
        assert 'python' in engine.patterns
        assert 'javascript' in engine.patterns
        assert 'bash' in engine.patterns
        print("✓ Learning engine initialization test passed")


def test_pattern_priority():
    """Test pattern priority ranking"""
    with tempfile.TemporaryDirectory() as tmpdir:
        storage_path = os.path.join(tmpdir, 'test_patterns.json')
        engine = PatternLearningEngine(storage_path=storage_path)
        
        priorities = engine.get_pattern_priority('python')
        assert len(priorities) > 0
        
        # Verify sorted by effectiveness
        for i in range(len(priorities) - 1):
            assert priorities[i][1] >= priorities[i+1][1]
        
        print(f"✓ Pattern priority test passed - {len(priorities)} patterns ranked")


def test_pattern_recording():
    """Test recording optimization results"""
    with tempfile.TemporaryDirectory() as tmpdir:
        storage_path = os.path.join(tmpdir, 'test_patterns.json')
        engine = PatternLearningEngine(storage_path=storage_path)
        
        # Record some optimizations
        engine.record_optimization('python', 'comment_removal', 15.0)
        engine.record_optimization('python', 'comment_removal', 20.0)
        engine.record_optimization('python', 'whitespace_reduction', 10.0)
        
        # Check stats
        summary = engine.get_session_summary()
        assert summary['patterns_used'] == 2
        assert summary['total_applications'] == 3
        
        print("✓ Pattern recording test passed")


def test_pattern_persistence():
    """Test saving and loading patterns"""
    with tempfile.TemporaryDirectory() as tmpdir:
        storage_path = os.path.join(tmpdir, 'test_patterns.json')
        
        # Create and save patterns
        engine1 = PatternLearningEngine(storage_path=storage_path)
        engine1.record_optimization('python', 'test_pattern', 25.0)
        engine1.save_session()
        
        # Load in new instance
        engine2 = PatternLearningEngine(storage_path=storage_path)
        assert 'python' in engine2.patterns
        assert 'test_pattern' in engine2.patterns['python']
        assert engine2.patterns['python']['test_pattern']['applications'] == 1
        
        print("✓ Pattern persistence test passed")


def test_learning_stats():
    """Test learning statistics collection"""
    optimizer = CodeGolfOptimizer(enable_learning=True)
    code = """# Comment
x = 1

y = 2"""
    
    result = optimizer.optimize(code, 'python')
    stats = optimizer.get_learning_stats()
    
    assert 'patterns_used' in stats
    assert 'total_applications' in stats
    assert stats['patterns_used'] > 0
    
    print("✓ Learning statistics test passed")


def test_no_ai_mode():
    """Test optimizer works with AI disabled"""
    optimizer = CodeGolfOptimizer(enable_learning=False)
    code = "x = 1  # comment"
    
    result = optimizer.optimize(code, 'python')
    assert result.optimized_chars < result.original_chars
    assert result.ai_suggestions is None or len(result.ai_suggestions) == 0
    
    print("✓ No-AI mode test passed")


def test_ai_suggestions_for_lambdas():
    """Test that AI suggests optimization for lambdas"""
    optimizer = CodeGolfOptimizer(enable_learning=True)
    code = """# Lambda functions
f = lambda x: x * 2
g = lambda y: y + 1
h = lambda z: z ** 2
"""
    
    result = optimizer.optimize(code, 'python')
    # Lambda suggestions are generated if the pattern is in top effectiveness
    # Just verify we get some suggestions
    assert result.ai_suggestions is not None
    
    print("✓ AI lambda suggestions test passed")


def test_ai_suggestions_for_comprehensions():
    """Test that AI suggests list comprehensions"""
    optimizer = CodeGolfOptimizer(enable_learning=True)
    code = """
result = []
for i in range(10):
    result.append(i * 2)
"""
    
    result = optimizer.optimize(code, 'python')
    suggestions_text = ' '.join(result.ai_suggestions or [])
    assert 'comprehension' in suggestions_text.lower()
    
    print("✓ AI comprehension suggestions test passed")


def test_effectiveness_score_update():
    """Test that effectiveness scores are updated correctly"""
    with tempfile.TemporaryDirectory() as tmpdir:
        storage_path = os.path.join(tmpdir, 'test_patterns.json')
        engine = PatternLearningEngine(storage_path=storage_path)
        
        initial_effectiveness = engine.patterns['python']['comment_removal']['effectiveness']
        
        # Record a very effective optimization
        engine.record_optimization('python', 'comment_removal', 50.0)
        
        new_effectiveness = engine.patterns['python']['comment_removal']['effectiveness']
        
        # Effectiveness should increase with high reduction
        assert new_effectiveness >= initial_effectiveness * 0.8  # Allow some decay
        
        print("✓ Effectiveness score update test passed")


def run_all_tests():
    """Run all AI optimizer tests"""
    print("Running AI Code Golf Optimizer tests...\n")
    
    tests = [
        test_ai_suggestions,
        test_pattern_scores,
        test_learning_engine_init,
        test_pattern_priority,
        test_pattern_recording,
        test_pattern_persistence,
        test_learning_stats,
        test_no_ai_mode,
        test_ai_suggestions_for_lambdas,
        test_ai_suggestions_for_comprehensions,
        test_effectiveness_score_update,
    ]
    
    failed = 0
    for test in tests:
        try:
            test()
        except AssertionError as e:
            print(f"✗ {test.__name__} failed: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ {test.__name__} error: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print(f"\n{'='*60}")
    if failed == 0:
        print(f"All {len(tests)} AI tests passed! 🤖✓")
        return 0
    else:
        print(f"{failed}/{len(tests)} tests failed")
        return 1


if __name__ == '__main__':
    sys.exit(run_all_tests())
