#!/usr/bin/env python3
"""
Test suite for enhanced self-improving prompt generator.

Tests the new genetic algorithm, multi-dimensional scoring, and
automated feedback extraction features added by @construct-specialist.
"""

import sys
import os
import tempfile
import shutil
import json

# Add tools directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'tools'))

from prompt_self_improver import PromptSelfImprover, PromptQualityScore


def test_quality_assessment():
    """Test multi-dimensional quality assessment"""
    print("=" * 60)
    print("Test 1: Quality Assessment")
    print("=" * 60)
    
    improver = PromptSelfImprover(data_dir=tempfile.mkdtemp())
    
    # Test with a good prompt
    good_prompt = """**@engineer-master** - Please implement this feature:

1. **Analyze**: Review requirements carefully
2. **Design**: Plan the architecture
3. **Implement**: Build with tests
4. **Validate**: Test thoroughly

**Key Principles:**
- Follow conventions
- Write clean code
- Test everything
- Document decisions

Feature request: {issue_body}"""
    
    quality = improver.assess_prompt_quality(good_prompt, historical_success_rate=0.8)
    
    print(f"\nGood Prompt Quality:")
    print(f"  Clarity:       {quality.clarity:.2f}")
    print(f"  Completeness:  {quality.completeness:.2f}")
    print(f"  Actionability: {quality.actionability:.2f}")
    print(f"  Specificity:   {quality.specificity:.2f}")
    print(f"  Overall:       {quality.overall_score:.2f}")
    
    assert quality.overall_score > 0.6, "Good prompt should score above 0.6"
    
    # Test with a poor prompt
    poor_prompt = "Please do the task described in the issue."
    
    quality_poor = improver.assess_prompt_quality(poor_prompt, historical_success_rate=0.3)
    
    print(f"\nPoor Prompt Quality:")
    print(f"  Overall: {quality_poor.overall_score:.2f}")
    
    assert quality_poor.overall_score < quality.overall_score, "Poor prompt should score lower"
    
    print("\n✅ Quality assessment test passed")


def test_genetic_crossover():
    """Test genetic crossover between prompts"""
    print("\n" + "=" * 60)
    print("Test 2: Genetic Crossover")
    print("=" * 60)
    
    improver = PromptSelfImprover(data_dir=tempfile.mkdtemp())
    
    parent1 = """**@agent** - Instructions:

1. **Step 1**: Do something
2. **Step 2**: Do something else

**Key Principles:**
- Principle A
- Principle B"""
    
    parent2 = """**@agent** - Different instructions:

1. **Step X**: Different approach
2. **Step Y**: Another approach

**Key Principles:**
- Principle C
- Principle D"""
    
    offspring = improver.genetic_crossover(parent1, parent2)
    
    print(f"\nOffspring created (length: {len(offspring)} chars)")
    print(f"Contains elements from both parents: {('Step 1' in offspring or 'Step X' in offspring)}")
    
    assert len(offspring) > 50, "Offspring should have substantial content"
    print("\n✅ Genetic crossover test passed")


def test_mutation():
    """Test prompt mutation"""
    print("\n" + "=" * 60)
    print("Test 3: Prompt Mutation")
    print("=" * 60)
    
    improver = PromptSelfImprover(data_dir=tempfile.mkdtemp())
    
    original = """**@agent** - Instructions:

1. **Step 1**: First step
2. **Step 2**: Second step
3. **Step 3**: Third step

**Key Principles:**
- Principle 1
- Principle 2"""
    
    # Test minor mutation
    mutated = improver.mutate_prompt(original, mutation_strength=0.2)
    print(f"\nMinor mutation applied")
    print(f"Length changed: {abs(len(mutated) - len(original))} chars")
    
    # Test major mutation
    mutated_major = improver.mutate_prompt(original, mutation_strength=0.8)
    print(f"Major mutation applied")
    print(f"Length changed: {abs(len(mutated_major) - len(original))} chars")
    
    print("\n✅ Mutation test passed")


def test_feedback_extraction():
    """Test PR feedback extraction"""
    print("\n" + "=" * 60)
    print("Test 4: Feedback Extraction")
    print("=" * 60)
    
    improver = PromptSelfImprover(data_dir=tempfile.mkdtemp())
    
    # Test positive feedback
    positive_review = """
    Great work! The implementation is clear and thorough.
    Tests are comprehensive and cover edge cases well.
    Documentation is excellent.
    """
    
    feedback = improver.extract_feedback_from_pr_review(positive_review)
    
    print(f"\nPositive Review:")
    print(f"  Sentiment: {feedback['sentiment']}")
    print(f"  Positive patterns: {feedback['positive_patterns']}")
    print(f"  Suggestions: {len(feedback['suggestions'])}")
    
    assert feedback['sentiment'] == 'positive', "Should detect positive sentiment"
    
    # Test negative feedback
    negative_review = """
    The implementation is unclear and confusing.
    Missing important test cases.
    Needs more documentation.
    """
    
    feedback_neg = improver.extract_feedback_from_pr_review(negative_review)
    
    print(f"\nNegative Review:")
    print(f"  Sentiment: {feedback_neg['sentiment']}")
    print(f"  Negative patterns: {feedback_neg['negative_patterns']}")
    
    assert feedback_neg['sentiment'] == 'negative', "Should detect negative sentiment"
    
    print("\n✅ Feedback extraction test passed")


def test_evolution_generation():
    """Test genetic algorithm evolution"""
    print("\n" + "=" * 60)
    print("Test 5: Evolution Generation")
    print("=" * 60)
    
    improver = PromptSelfImprover(data_dir=tempfile.mkdtemp())
    
    # Create a population with fitness scores
    population = [
        ("Prompt A with good structure", 0.8),
        ("Prompt B also good", 0.7),
        ("Prompt C mediocre", 0.5),
        ("Prompt D weak", 0.3),
    ]
    
    print(f"\nStarting population: {len(population)} prompts")
    print(f"Fitness range: {min(p[1] for p in population):.2f} - {max(p[1] for p in population):.2f}")
    
    new_generation = improver.evolve_generation(population, target_size=6)
    
    print(f"New generation: {len(new_generation)} prompts")
    assert len(new_generation) == 6, "Should create target population size"
    
    print("\n✅ Evolution generation test passed")


def test_gene_fitness_update():
    """Test gene fitness updates"""
    print("\n" + "=" * 60)
    print("Test 6: Gene Fitness Update")
    print("=" * 60)
    
    improver = PromptSelfImprover(data_dir=tempfile.mkdtemp())
    
    # Get initial gene
    gene_id = list(improver.prompt_genes.keys())[0]
    initial_fitness = improver.prompt_genes[gene_id].fitness_score
    
    print(f"\nGene: {gene_id}")
    print(f"Initial fitness: {initial_fitness:.3f}")
    
    # Update with success
    for i in range(5):
        improver.update_gene_fitness(gene_id, success=True)
    
    new_fitness = improver.prompt_genes[gene_id].fitness_score
    print(f"After 5 successes: {new_fitness:.3f}")
    
    assert new_fitness > initial_fitness, "Fitness should increase with success"
    
    print("\n✅ Gene fitness update test passed")


def test_evolution_report():
    """Test evolution report generation"""
    print("\n" + "=" * 60)
    print("Test 7: Evolution Report")
    print("=" * 60)
    
    improver = PromptSelfImprover(data_dir=tempfile.mkdtemp())
    
    report = improver.get_evolution_report()
    
    print(f"\nEvolution Report:")
    print(f"  Total genes: {report['total_genes']}")
    print(f"  Avg gene fitness: {report['avg_gene_fitness']:.3f}")
    print(f"  Top genes: {len(report['top_genes'])}")
    print(f"  Evolution history: {len(report['evolution_history'])}")
    
    assert report['total_genes'] > 0, "Should have genes"
    assert 'top_genes' in report, "Should have top genes"
    
    print("\n✅ Evolution report test passed")


def run_all_tests():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("  Self-Improving Prompt Generator Tests")
    print("  Created by @construct-specialist")
    print("=" * 60)
    
    tests = [
        ("Quality Assessment", test_quality_assessment),
        ("Genetic Crossover", test_genetic_crossover),
        ("Mutation", test_mutation),
        ("Feedback Extraction", test_feedback_extraction),
        ("Evolution Generation", test_evolution_generation),
        ("Gene Fitness Update", test_gene_fitness_update),
        ("Evolution Report", test_evolution_report),
    ]
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        try:
            test_func()
            passed += 1
        except Exception as e:
            print(f"\n❌ Test failed: {name}")
            print(f"   Error: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"  Test Results: {passed} passed, {failed} failed")
    print("=" * 60 + "\n")
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
