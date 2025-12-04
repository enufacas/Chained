#!/usr/bin/env python3
"""
Tests for self-improving prompt generator enhancements.

Tests new features:
- Prompt quality scoring system
- Contextual prompt adaptation
- Auto-tuning integration

Created by @create-botter as part of the infrastructure enhancement.
"""

import json
import tempfile
import sys
from pathlib import Path
from datetime import datetime, timezone

# Add tools directory to path
tools_dir = Path(__file__).parent.parent / "tools"
sys.path.insert(0, str(tools_dir))

# Import modules
import importlib.util

def load_module(module_name, file_path):
    """Load a module from a file path"""
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_quality_scorer_initialization():
    """Test that quality scorer initializes correctly"""
    print("Testing quality scorer initialization...")
    
    try:
        pqs = load_module("prompt_quality_scorer", tools_dir / "prompt-quality-scorer.py")
        PromptQualityScorer = pqs.PromptQualityScorer
        
        with tempfile.TemporaryDirectory() as tmpdir:
            scorer = PromptQualityScorer(data_dir=tmpdir)
            assert scorer is not None
            assert scorer.data_dir == Path(tmpdir)
            
        print("✓ Quality scorer initialization test passed")
        return True
    except Exception as e:
        print(f"✗ Quality scorer initialization test failed: {e}")
        return False


def test_quality_scoring_with_data():
    """Test quality scoring with sample data"""
    print("Testing quality scoring with sample data...")
    
    try:
        pqs = load_module("prompt_quality_scorer", tools_dir / "prompt-quality-scorer.py")
        PromptQualityScorer = pqs.PromptQualityScorer
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create sample data
            templates_file = Path(tmpdir) / "templates.json"
            outcomes_file = Path(tmpdir) / "outcomes.json"
            
            # Sample template
            templates = {
                "test_template": {
                    "template_id": "test_template",
                    "category": "feature",
                    "template": "**@{agent}** - Test template with clear sections\n\n1. Step one\n2. Step two\n\n**Key Principles:**\n- Principle 1\n- Principle 2",
                    "success_count": 8,
                    "failure_count": 2,
                    "total_uses": 10,
                    "avg_resolution_time": 12.0
                }
            }
            
            # Sample outcomes
            outcomes = [
                {
                    "prompt_id": "test_template",
                    "issue_number": i,
                    "success": True,
                    "resolution_time_hours": 10 + i,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
                for i in range(8)
            ] + [
                {
                    "prompt_id": "test_template",
                    "issue_number": i + 100,
                    "success": False,
                    "resolution_time_hours": 20,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
                for i in range(2)
            ]
            
            with open(templates_file, 'w') as f:
                json.dump(templates, f)
            
            with open(outcomes_file, 'w') as f:
                json.dump(outcomes, f)
            
            # Test scoring
            scorer = PromptQualityScorer(data_dir=tmpdir)
            metrics = scorer.calculate_quality_metrics("test_template")
            
            assert metrics.template_id == "test_template"
            assert 0 <= metrics.overall_quality <= 1
            assert 0 <= metrics.resolution_score <= 1
            assert 0 <= metrics.efficiency_score <= 1
            assert 0 <= metrics.consistency_score <= 1
            assert metrics.sample_size == 10
            
            # Should have good scores given 80% success rate and reasonable time
            assert metrics.resolution_score > 0.6, f"Expected resolution_score > 0.6, got {metrics.resolution_score}"
            assert metrics.overall_quality > 0.5, f"Expected overall_quality > 0.5, got {metrics.overall_quality}"
            
            print(f"  Resolution score: {metrics.resolution_score:.3f}")
            print(f"  Efficiency score: {metrics.efficiency_score:.3f}")
            print(f"  Consistency score: {metrics.consistency_score:.3f}")
            print(f"  Overall quality: {metrics.overall_quality:.3f}")
            
        print("✓ Quality scoring with data test passed")
        return True
    except Exception as e:
        print(f"✗ Quality scoring with data test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_quality_report_generation():
    """Test quality report generation"""
    print("Testing quality report generation...")
    
    try:
        pqs = load_module("prompt_quality_scorer", tools_dir / "prompt-quality-scorer.py")
        PromptQualityScorer = pqs.PromptQualityScorer
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create minimal data
            templates_file = Path(tmpdir) / "templates.json"
            templates = {
                "template1": {
                    "template_id": "template1",
                    "category": "feature",
                    "template": "Test",
                    "total_uses": 0
                }
            }
            
            with open(templates_file, 'w') as f:
                json.dump(templates, f)
            
            scorer = PromptQualityScorer(data_dir=tmpdir)
            report = scorer.get_quality_report()
            
            assert "generated_at" in report
            assert "total_templates" in report
            assert "templates" in report
            assert len(report["templates"]) > 0
            
            template_report = report["templates"][0]
            assert "template_id" in template_report
            assert "overall_quality" in template_report
            assert "scores" in template_report
            assert "grade" in template_report
            
        print("✓ Quality report generation test passed")
        return True
    except Exception as e:
        print(f"✗ Quality report generation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_contextual_adapter_initialization():
    """Test contextual adapter initialization"""
    print("Testing contextual adapter initialization...")
    
    try:
        cpa = load_module("contextual_prompt_adapter", tools_dir / "contextual-prompt-adapter.py")
        ContextualPromptAdapter = cpa.ContextualPromptAdapter
        
        # Use the actual .github/agents directory
        adapter = ContextualPromptAdapter(agents_dir=".github/agents")
        assert adapter is not None
        
        # Should have loaded some agent profiles
        assert len(adapter.agent_profiles) > 0, "Should load agent profiles from .github/agents"
        
        print(f"  Loaded {len(adapter.agent_profiles)} agent profiles")
        
        print("✓ Contextual adapter initialization test passed")
        return True
    except Exception as e:
        print(f"✗ Contextual adapter initialization test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_prompt_adaptation():
    """Test prompt adaptation for specific agents"""
    print("Testing prompt adaptation...")
    
    try:
        cpa = load_module("contextual_prompt_adapter", tools_dir / "contextual-prompt-adapter.py")
        ContextualPromptAdapter = cpa.ContextualPromptAdapter
        
        adapter = ContextualPromptAdapter(agents_dir=".github/agents")
        
        base_prompt = "Fix this bug: {issue_body}"
        
        # Test adaptation for create-botter (if it exists)
        adapted = adapter.adapt_prompt_for_agent(
            base_prompt,
            "create-botter",
            issue_context={"labels": ["feature", "infrastructure"], "keywords": ["infrastructure"]}
        )
        
        assert adapted is not None
        # Adapted prompt should be longer (has additions) or same length
        assert len(adapted) >= len(base_prompt)
        
        print(f"  Base prompt length: {len(base_prompt)}")
        print(f"  Adapted prompt length: {len(adapted)}")
        
        # Test with unknown agent (should return base prompt)
        adapted_unknown = adapter.adapt_prompt_for_agent(
            base_prompt,
            "nonexistent-agent"
        )
        assert adapted_unknown == base_prompt
        
        print("✓ Prompt adaptation test passed")
        return True
    except Exception as e:
        print(f"✗ Prompt adaptation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_contextual_enhancement():
    """Test full contextual enhancement"""
    print("Testing full contextual enhancement...")
    
    try:
        cpa = load_module("contextual_prompt_adapter", tools_dir / "contextual-prompt-adapter.py")
        ContextualPromptAdapter = cpa.ContextualPromptAdapter
        
        adapter = ContextualPromptAdapter(agents_dir=".github/agents")
        
        base_prompt = "Implement this feature: {issue_body}"
        
        enhanced = adapter.enhance_prompt_with_context(
            base_prompt,
            "create-botter",
            issue_title="Add new infrastructure component",
            issue_labels=["feature", "infrastructure"],
            issue_body="We need to build a new infrastructure component for handling async tasks"
        )
        
        assert enhanced is not None
        assert len(enhanced) >= len(base_prompt)
        
        print(f"  Enhanced prompt length: {len(enhanced)}")
        print(f"  Enhancement added: {len(enhanced) - len(base_prompt)} characters")
        
        print("✓ Contextual enhancement test passed")
        return True
    except Exception as e:
        print(f"✗ Contextual enhancement test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """Run all tests and report results"""
    print("=" * 70)
    print("Running Self-Improving Prompt Generator Enhancement Tests")
    print("=" * 70)
    print()
    
    tests = [
        ("Quality Scorer Initialization", test_quality_scorer_initialization),
        ("Quality Scoring with Data", test_quality_scoring_with_data),
        ("Quality Report Generation", test_quality_report_generation),
        ("Contextual Adapter Initialization", test_contextual_adapter_initialization),
        ("Prompt Adaptation", test_prompt_adaptation),
        ("Contextual Enhancement", test_contextual_enhancement),
    ]
    
    results = []
    for test_name, test_func in tests:
        print()
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"✗ {test_name} crashed: {e}")
            results.append((test_name, False))
    
    print()
    print("=" * 70)
    print("Test Results Summary")
    print("=" * 70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    print()
    print(f"Total: {passed}/{total} tests passed ({passed/total*100:.0f}%)")
    
    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
