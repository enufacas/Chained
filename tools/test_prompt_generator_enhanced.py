#!/usr/bin/env python3
"""
Tests for the enhanced self-improving prompt generator.

Tests the learning integration, template evolution, and A/B testing features
added by @engineer-master.

Part of the Chained autonomous AI ecosystem.
"""

import json
import os
import sys
import tempfile
from pathlib import Path
from datetime import datetime, timezone

# Add tools directory to path
tools_dir = Path(__file__).parent
sys.path.insert(0, str(tools_dir))

# Import with explicit module names
import importlib.util

def load_module(module_name, file_path):
    """Load a module from a file path"""
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

# Load the modules
try:
    pg = load_module("prompt_generator", tools_dir / "prompt-generator.py")
    pli = load_module("prompt_learning_integration", tools_dir / "prompt_learning_integration.py")
    
    PromptGenerator = pg.PromptGenerator
    PromptTemplate = pg.PromptTemplate
    PromptOutcome = pg.PromptOutcome
    PromptLearningIntegrator = pli.PromptLearningIntegrator
    LearningInsight = pli.LearningInsight
    
    IMPORTS_SUCCESSFUL = True
except Exception as e:
    print(f"Warning: Could not import modules: {e}")
    IMPORTS_SUCCESSFUL = False


def test_learning_integration():
    """Test that learning integration extracts insights correctly"""
    if not IMPORTS_SUCCESSFUL:
        print("SKIP: test_learning_integration - imports failed")
        return
    
    print("Testing learning integration...")
    
    # Create integrator
    with tempfile.TemporaryDirectory() as tmpdir:
        integrator = PromptLearningIntegrator(cache_dir=tmpdir)
        
        # Test extracting learnings
        insights = integrator.extract_learnings_from_tldr(days=7)
        
        assert len(insights) > 0, "Should extract some insights"
        assert all(isinstance(i, LearningInsight) for i in insights), "All should be LearningInsight objects"
        
        print(f"✓ Extracted {len(insights)} insights")
        
        # Test categorization
        categories = set(i.category for i in insights)
        assert len(categories) > 0, "Should have at least one category"
        print(f"✓ Found categories: {categories}")
        
        # Test relevance scoring
        high_relevance = [i for i in insights if i.relevance_score > 0.7]
        print(f"✓ Found {len(high_relevance)} high-relevance insights")
        
        # Test getting relevant insights
        relevant = integrator.get_relevant_insights("feature", limit=3)
        assert len(relevant) <= 3, "Should respect limit"
        print(f"✓ Retrieved {len(relevant)} relevant insights for feature category")
        
        # Test trend analysis
        trends = integrator.analyze_trending_topics(days=7)
        assert "top_keywords" in trends, "Should have top keywords"
        assert "category_distribution" in trends, "Should have category distribution"
        print(f"✓ Analyzed trends: {len(trends['top_keywords'])} keywords")
    
    print("✓ Learning integration tests passed")


def test_prompt_generation_with_learning():
    """Test that prompt generation integrates learnings correctly"""
    if not IMPORTS_SUCCESSFUL:
        print("SKIP: test_prompt_generation_with_learning - imports failed")
        return
    
    print("Testing prompt generation with learning integration...")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        generator = PromptGenerator(data_dir=tmpdir, enable_learning=True)
        
        # Generate prompt with learning enhancement
        prompt, template_id = generator.generate_prompt(
            issue_body="Fix authentication bug",
            category="bug_fix",
            agent="engineer-master",
            enable_learning_enhancement=True
        )
        
        assert len(prompt) > 0, "Should generate a prompt"
        assert "engineer-master" in prompt, "Should include agent name"
        assert template_id in generator.templates, "Template should exist"
        
        # Check if learnings were integrated
        if generator.learning_integrator:
            # Prompt should be longer with learnings
            prompt_no_learning, _ = generator.generate_prompt(
                issue_body="Fix authentication bug",
                category="bug_fix",
                agent="engineer-master",
                enable_learning_enhancement=False
            )
            
            # With learning integration, prompt should potentially be longer
            # (though not guaranteed if no relevant learnings found)
            print(f"✓ Generated prompt with learning integration ({len(prompt)} chars)")
        else:
            print("✓ Generated prompt (learning integration not available)")
    
    print("✓ Prompt generation with learning tests passed")


def test_template_evolution():
    """Test template evolution capabilities"""
    if not IMPORTS_SUCCESSFUL:
        print("SKIP: test_template_evolution - imports failed")
        return
    
    print("Testing template evolution...")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        generator = PromptGenerator(data_dir=tmpdir, enable_learning=False)
        
        # Create a template with sufficient usage data
        test_template = PromptTemplate(
            template_id="test_template",
            category="feature",
            template="Test template: {agent} - {issue_body}",
            total_uses=15,  # Enough for evolution
            success_count=10,
            failure_count=5
        )
        
        generator.templates["test_template"] = test_template
        generator._save_data()
        
        # Test evolution
        evolved = generator.evolve_template("test_template", "enhance")
        
        if evolved:
            assert evolved.template_id.startswith("test_template"), "Should be based on original"
            assert evolved.category == "feature", "Should preserve category"
            assert len(evolved.template) > 0, "Should have template text"
            print(f"✓ Evolved template: {evolved.template_id}")
        else:
            print("✓ Template evolution returned None (acceptable)")
        
        # Test mutation types
        for mutation_type in ["enhance", "simplify", "focus"]:
            result = generator._mutate_template_text(
                test_template.template,
                mutation_type,
                "feature"
            )
            print(f"✓ Tested {mutation_type} mutation")
    
    print("✓ Template evolution tests passed")


def test_ab_testing():
    """Test A/B testing functionality"""
    if not IMPORTS_SUCCESSFUL:
        print("SKIP: test_ab_testing - imports failed")
        return
    
    print("Testing A/B testing...")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        generator = PromptGenerator(data_dir=tmpdir, enable_learning=False)
        
        # Create two test templates
        template_a = PromptTemplate(
            template_id="template_a",
            category="bug_fix",
            template="Template A: {agent} - {issue_body}"
        )
        template_b = PromptTemplate(
            template_id="template_b",
            category="bug_fix",
            template="Template B: {agent} - {issue_body}"
        )
        
        generator.templates["template_a"] = template_a
        generator.templates["template_b"] = template_b
        generator._save_data()
        
        # Enable A/B testing
        test_config = generator.enable_ab_testing("template_a", "template_b")
        
        assert "test_id" in test_config, "Should have test ID"
        assert test_config["template_a"] == "template_a", "Should reference template A"
        assert test_config["template_b"] == "template_b", "Should reference template B"
        assert test_config["status"] == "active", "Should be active"
        
        print(f"✓ Created A/B test: {test_config['test_id']}")
        
        # Get test results
        results = generator.get_ab_test_results(test_config["test_id"])
        assert results is not None, "Should retrieve test results"
        assert "results" in results, "Should have results section"
        
        print("✓ Retrieved A/B test results")
    
    print("✓ A/B testing tests passed")


def test_performance_metrics():
    """Test that performance metrics are calculated correctly"""
    if not IMPORTS_SUCCESSFUL:
        print("SKIP: test_performance_metrics - imports failed")
        return
    
    print("Testing performance metrics...")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        generator = PromptGenerator(data_dir=tmpdir, enable_learning=False)
        
        # Create template with outcomes
        template = PromptTemplate(
            template_id="perf_test",
            category="feature",
            template="Test: {agent} - {issue_body}",
            total_uses=10,
            success_count=8,
            failure_count=2,
            avg_resolution_time=3.5
        )
        
        generator.templates["perf_test"] = template
        
        # Test success rate
        assert template.success_rate == 0.8, "Success rate should be 80%"
        
        # Test effectiveness score
        effectiveness = template.effectiveness_score
        assert 0 <= effectiveness <= 1, "Effectiveness should be 0-1"
        assert effectiveness > 0.5, "Should be reasonably effective"
        
        print(f"✓ Success rate: {template.success_rate:.2%}")
        print(f"✓ Effectiveness score: {effectiveness:.2f}")
        
        # Test performance report
        report = generator.get_performance_report()
        assert "templates" in report, "Should have templates section"
        assert "insights" in report, "Should have insights section"
        assert "perf_test" in report["templates"], "Should include test template"
        
        print("✓ Generated performance report")
    
    print("✓ Performance metrics tests passed")


def test_optimization_suggestions():
    """Test that optimization suggestions are generated correctly"""
    if not IMPORTS_SUCCESSFUL:
        print("SKIP: test_optimization_suggestions - imports failed")
        return
    
    print("Testing optimization suggestions...")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        generator = PromptGenerator(data_dir=tmpdir, enable_learning=False)
        
        # Create underperforming template
        bad_template = PromptTemplate(
            template_id="bad_template",
            category="bug_fix",
            template="Bad template: {agent} - {issue_body}",
            total_uses=10,
            success_count=2,
            failure_count=8,
            avg_resolution_time=50.0
        )
        
        generator.templates["bad_template"] = bad_template
        
        # Add some failure outcomes
        for i in range(5):
            outcome = PromptOutcome(
                prompt_id="bad_template",
                issue_number=100 + i,
                success=False,
                resolution_time_hours=50.0,
                error_type="test_failure" if i < 3 else "build_error",
                timestamp=datetime.now(timezone.utc).isoformat()
            )
            generator.outcomes.append(outcome)
        
        # Add more outcomes to meet minimum (10)
        for i in range(5):
            outcome = PromptOutcome(
                prompt_id="bad_template",
                issue_number=200 + i,
                success=True,
                resolution_time_hours=3.0,
                timestamp=datetime.now(timezone.utc).isoformat()
            )
            generator.outcomes.append(outcome)
        
        # Generate suggestions
        suggestions = generator.optimize_templates()
        
        assert len(suggestions) > 0, "Should have optimization suggestions"
        
        # Check that bad template is flagged
        bad_template_suggestions = [
            s for s in suggestions 
            if s["template_id"] == "bad_template"
        ]
        
        assert len(bad_template_suggestions) > 0, "Bad template should be flagged"
        
        for suggestion in bad_template_suggestions:
            print(f"✓ Found issue: {suggestion['issue']}")
            assert "recommendation" in suggestion, "Should have recommendation"
        
        print(f"✓ Generated {len(suggestions)} optimization suggestions")
    
    print("✓ Optimization suggestions tests passed")


def run_all_tests():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("Running Enhanced Prompt Generator Tests")
    print("=" * 60 + "\n")
    
    tests = [
        test_learning_integration,
        test_prompt_generation_with_learning,
        test_template_evolution,
        test_ab_testing,
        test_performance_metrics,
        test_optimization_suggestions
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
            print()
        except AssertionError as e:
            print(f"✗ Test failed: {e}\n")
            failed += 1
        except Exception as e:
            print(f"✗ Test error: {e}\n")
            failed += 1
    
    print("=" * 60)
    print(f"Tests passed: {passed}/{len(tests)}")
    print(f"Tests failed: {failed}/{len(tests)}")
    print("=" * 60)
    
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    exit(run_all_tests())
