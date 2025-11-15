#!/usr/bin/env python3
"""
Tests for HN Insights Code Generator

Created by @investigate-champion
"""

import json
import os
import tempfile
import shutil
from pathlib import Path
import sys

# Add tools directory to path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from hn_code_generator import (
        HNCodeGenerator,
        CodeTemplate,
        GeneratedCode
    )
except ImportError:
    # Try with hyphen
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "hn_code_generator",
        Path(__file__).parent / "hn-code-generator.py"
    )
    hn_code_generator = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(hn_code_generator)
    HNCodeGenerator = hn_code_generator.HNCodeGenerator
    CodeTemplate = hn_code_generator.CodeTemplate
    GeneratedCode = hn_code_generator.GeneratedCode


def test_initialization():
    """Test generator initialization"""
    with tempfile.TemporaryDirectory() as tmpdir:
        generator = HNCodeGenerator(data_dir=tmpdir)
        
        # Should have initialized templates
        assert len(generator.templates) > 0, "Should have base templates"
        
        # Check template categories
        categories = {t.category for t in generator.templates}
        assert 'api' in categories, "Should have API template"
        assert 'data_processing' in categories, "Should have data processing template"
        
        print("✓ Initialization test passed")


def test_template_keyword_matching():
    """Test keyword matching in templates"""
    with tempfile.TemporaryDirectory() as tmpdir:
        generator = HNCodeGenerator(data_dir=tmpdir)
        
        # Find API template
        api_template = next(t for t in generator.templates if t.category == 'api')
        
        # Test matching
        score1 = api_template.matches_keywords("Build an API wrapper")
        score2 = api_template.matches_keywords("Create data visualization")
        
        assert score1 > 0, "Should match API keywords"
        assert score1 > score2, "API description should match better than visualization"
        
        print("✓ Keyword matching test passed")


def test_code_generation():
    """Test code generation"""
    with tempfile.TemporaryDirectory() as tmpdir:
        generator = HNCodeGenerator(data_dir=tmpdir)
        
        # Generate code
        generated = generator.generate_code(
            "Create an API wrapper",
            context={'class_name': 'TestAPI', 'api_name': 'GitHub'}
        )
        
        assert generated is not None, "Should generate code"
        assert 'TestAPI' in generated.code, "Should use provided class name"
        assert 'GitHub' in generated.code, "Should use provided API name"
        assert generated.confidence > 0, "Should have positive confidence"
        
        print("✓ Code generation test passed")


def test_hn_insights_analysis():
    """Test HN insights analysis"""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create mock learnings directory
        learnings_dir = Path(tmpdir) / "learnings"
        learnings_dir.mkdir()
        
        # Create mock HN data
        mock_data = {
            "timestamp": "2025-11-15T10:00:00Z",
            "source": "Hacker News",
            "learnings": [
                {
                    "title": "Building Fast APIs with Python",
                    "description": "Performance tips",
                    "url": "https://example.com/1"
                },
                {
                    "title": "Machine Learning for Beginners",
                    "description": "Getting started with ML",
                    "url": "https://example.com/2"
                },
                {
                    "title": "Docker Container Optimization",
                    "description": "Optimize your containers",
                    "url": "https://example.com/3"
                }
            ]
        }
        
        with open(learnings_dir / "hn_20251115_100000.json", 'w') as f:
            json.dump(mock_data, f)
        
        generator = HNCodeGenerator(data_dir=tmpdir)
        insights = generator.analyze_hn_insights(str(learnings_dir))
        
        assert insights['total_insights'] == 3, "Should find all insights"
        assert len(insights['top_topics']) > 0, "Should extract topics"
        assert len(insights['titles']) == 3, "Should capture all titles"
        
        print("✓ HN insights analysis test passed")


def test_learning_from_insights():
    """Test learning new templates from insights"""
    with tempfile.TemporaryDirectory() as tmpdir:
        generator = HNCodeGenerator(data_dir=tmpdir)
        
        initial_count = len(generator.templates)
        
        # Create insights with recurring topic
        insights = {
            'top_topics': [
                ('kubernetes', 10),  # High frequency topic
                ('docker', 8),
                ('python', 6)
            ],
            'urls': ['https://example.com/1', 'https://example.com/2']
        }
        
        generator.learn_from_insights(insights)
        
        # Should have learned new templates
        assert len(generator.templates) > initial_count, "Should create new templates"
        
        # Check if kubernetes template was created
        kube_templates = [t for t in generator.templates if 'kubernetes' in t.keywords]
        assert len(kube_templates) > 0, "Should create template for frequent topic"
        
        print("✓ Learning from insights test passed")


def test_statistics():
    """Test statistics generation"""
    with tempfile.TemporaryDirectory() as tmpdir:
        generator = HNCodeGenerator(data_dir=tmpdir)
        
        # Generate some code
        generator.generate_code("API wrapper", {'class_name': 'Test'})
        generator.generate_code("Data analyzer", {'class_name': 'Test'})
        
        stats = generator.get_statistics()
        
        assert stats['total_templates'] > 0, "Should have templates"
        assert stats['total_generated'] == 2, "Should have generated 2 items"
        assert stats['most_used_template'] is not None, "Should identify most used"
        assert stats['avg_confidence'] > 0, "Should calculate average confidence"
        
        print("✓ Statistics test passed")


def test_persistence():
    """Test data persistence"""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create generator and generate code
        generator1 = HNCodeGenerator(data_dir=tmpdir)
        generated = generator1.generate_code("API wrapper", {'class_name': 'Persist'})
        template_count = len(generator1.templates)
        
        # Create new generator instance
        generator2 = HNCodeGenerator(data_dir=tmpdir)
        
        # Should load saved data
        assert len(generator2.templates) == template_count, "Should load templates"
        assert len(generator2.generated_history) == 1, "Should load history"
        assert generator2.generated_history[0].code == generated.code, "Should match generated code"
        
        print("✓ Persistence test passed")


def test_template_usage_tracking():
    """Test template usage tracking"""
    with tempfile.TemporaryDirectory() as tmpdir:
        generator = HNCodeGenerator(data_dir=tmpdir)
        
        # Get initial usage count
        api_template = next(t for t in generator.templates if t.category == 'api')
        initial_usage = api_template.usage_count
        
        # Generate code using API template
        generator.generate_code("API wrapper", {'class_name': 'Track'})
        
        # Usage should increase
        assert api_template.usage_count == initial_usage + 1, "Should track usage"
        
        print("✓ Usage tracking test passed")


def test_confidence_scoring():
    """Test confidence scoring"""
    with tempfile.TemporaryDirectory() as tmpdir:
        generator = HNCodeGenerator(data_dir=tmpdir)
        
        # High confidence match
        gen1 = generator.generate_code(
            "Build an API wrapper with rate limiting",
            {'class_name': 'Test'}
        )
        
        # Low confidence match
        gen2 = generator.generate_code(
            "Something random",
            {'class_name': 'Test'}
        )
        
        if gen1 and gen2:
            assert gen1.confidence > gen2.confidence, "Better match should have higher confidence"
        elif gen1:
            assert gen1.confidence > 0, "Good match should have positive confidence"
        
        print("✓ Confidence scoring test passed")


def run_all_tests():
    """Run all tests"""
    tests = [
        test_initialization,
        test_template_keyword_matching,
        test_code_generation,
        test_hn_insights_analysis,
        test_learning_from_insights,
        test_statistics,
        test_persistence,
        test_template_usage_tracking,
        test_confidence_scoring
    ]
    
    print("🧪 Running HN Code Generator Tests\n")
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"✗ {test.__name__} failed: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ {test.__name__} error: {e}")
            failed += 1
    
    print(f"\n{'='*50}")
    print(f"Results: {passed} passed, {failed} failed")
    print(f"{'='*50}")
    
    return failed == 0


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
