#!/usr/bin/env python3
"""
Comprehensive tests for Creativity & Innovation Metrics Analyzer

Test Coverage:
- Pattern extraction and detection
- Novelty analysis
- Diversity measurement
- Impact assessment
- Learning progression tracking
- Integration with metrics system
"""

import sys
import os
import json
import tempfile
import shutil
from pathlib import Path
from datetime import datetime, timezone
import importlib.util

# Load the creativity analyzer module
spec = importlib.util.spec_from_file_location(
    "creativity_metrics_analyzer",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "tools", "creativity-metrics-analyzer.py")
)
creativity_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(creativity_module)

CreativityAnalyzer = creativity_module.CreativityAnalyzer
CreativityScore = creativity_module.CreativityScore
CreativityIndicators = creativity_module.CreativityIndicators
CreativityMetrics = creativity_module.CreativityMetrics


def test_creativity_score_dataclass():
    """Test CreativityScore dataclass creation and serialization"""
    score = CreativityScore(
        novelty=0.8,
        diversity=0.7,
        impact=0.6,
        learning=0.5,
        overall=0.65
    )
    
    assert score.novelty == 0.8
    assert score.diversity == 0.7
    assert score.impact == 0.6
    assert score.learning == 0.5
    assert score.overall == 0.65
    
    # Test serialization
    data = score.to_dict()
    assert data['novelty'] == 0.8
    assert data['overall'] == 0.65
    
    print("✅ CreativityScore dataclass test passed")


def test_creativity_indicators_dataclass():
    """Test CreativityIndicators dataclass"""
    indicators = CreativityIndicators(
        novel_patterns=['factory_pattern', 'async_pattern'],
        unique_approaches=5,
        first_time_solutions=3,
        cross_domain_contributions=4,
        breakthrough_moments=['High novelty detected']
    )
    
    assert len(indicators.novel_patterns) == 2
    assert indicators.unique_approaches == 5
    assert indicators.first_time_solutions == 3
    
    # Test serialization
    data = indicators.to_dict()
    assert len(data['novel_patterns']) == 2
    
    print("✅ CreativityIndicators dataclass test passed")


def test_pattern_extraction():
    """Test code pattern extraction from diffs"""
    analyzer = CreativityAnalyzer()
    
    # Test factory pattern detection
    code_diff = """
    +class AgentFactory:
    +    def create_agent(self, agent_type):
    +        return agent_type()
    """
    
    patterns = analyzer._extract_code_patterns(code_diff)
    assert 'factory_pattern' in patterns
    
    # Test async pattern detection
    code_diff2 = """
    +async def fetch_data(url):
    +    async with aiohttp.ClientSession() as session:
    +        return await session.get(url)
    """
    
    patterns2 = analyzer._extract_code_patterns(code_diff2)
    assert 'async_pattern' in patterns2
    
    # Test decorator pattern
    code_diff3 = """
    +@dataclass
    +class AgentMetrics:
    +    score: float = 0.0
    """
    
    patterns3 = analyzer._extract_code_patterns(code_diff3)
    assert 'dataclass_pattern' in patterns3
    
    print("✅ Pattern extraction test passed")


def test_solution_approach_extraction():
    """Test solution approach extraction from PR metadata"""
    analyzer = CreativityAnalyzer()
    
    # Test refactoring detection
    pr_data = {
        'title': 'Refactor agent metrics collector',
        'body': 'Improved code organization and readability',
        'changed_files': 3,
        'additions': 50,
        'deletions': 30
    }
    
    approaches = analyzer._extract_solution_approaches(pr_data)
    assert 'refactoring' in approaches
    
    # Test feature development
    pr_data2 = {
        'title': 'Add creativity metrics analyzer',
        'body': 'New feature for measuring agent creativity',
        'changed_files': 5,
        'additions': 500,
        'deletions': 10
    }
    
    approaches2 = analyzer._extract_solution_approaches(pr_data2)
    assert 'feature_development' in approaches2
    
    # Test performance optimization
    pr_data3 = {
        'title': 'Optimize database queries for performance',
        'body': 'Reduced query time by 50% through caching',
        'changed_files': 2,
        'additions': 80,
        'deletions': 20
    }
    
    approaches3 = analyzer._extract_solution_approaches(pr_data3)
    assert 'performance_optimization' in approaches3
    
    print("✅ Solution approach extraction test passed")


def test_novelty_analysis():
    """Test novelty scoring"""
    # Use a fresh analyzer with empty database
    import tempfile
    original_cache_dir = creativity_module.CREATIVITY_CACHE_DIR
    
    with tempfile.TemporaryDirectory() as tmpdir:
        creativity_module.CREATIVITY_CACHE_DIR = Path(tmpdir) / "creativity"
        
        try:
            analyzer = CreativityAnalyzer()
            
            # Create test contributions with different patterns
            contributions = [
                {
                    'diff': """
                    +@dataclass
                    +class NewAgent:
                    +    creativity: float
                    +    
                    +async def analyze():
                    +    await process()
                    """,
                    'title': 'Add new agent system',
                    'body': 'Implementing novel approach',
                    'files': ['agents/new_agent.py']
                }
            ]
            
            novelty_score, novel_patterns = analyzer.analyze_novelty(
                'test-agent',
                contributions,
                []  # Empty context = all patterns are novel
            )
            
            assert novelty_score > 0.0, f"Expected novelty_score > 0.0, got {novelty_score}"
            assert len(novel_patterns) > 0, f"Expected novel patterns, got {novel_patterns}"
            
            print(f"✅ Novelty analysis test passed (score: {novelty_score:.2f}, patterns: {len(novel_patterns)})")
        
        finally:
            creativity_module.CREATIVITY_CACHE_DIR = original_cache_dir


def test_diversity_analysis():
    """Test diversity scoring"""
    analyzer = CreativityAnalyzer()
    
    # Diverse contributions touching multiple areas
    contributions = [
        {
            'diff': '@dataclass\nclass Agent:\n    pass',
            'title': 'Add agent class',
            'body': 'Feature development',
            'files': ['agents/core.py', 'agents/base.py']
        },
        {
            'diff': 'async def fetch():\n    await get()',
            'title': 'Refactor API client',
            'body': 'Performance optimization',
            'files': ['api/client.py']
        },
        {
            'diff': 'def test_agent():\n    assert True',
            'title': 'Add tests',
            'body': 'Testing',
            'files': ['tests/test_agent.py', 'tests/test_api.py']
        }
    ]
    
    diversity_score = analyzer.analyze_diversity('test-agent', contributions)
    
    assert diversity_score > 0.0
    assert diversity_score <= 1.0
    
    print(f"✅ Diversity analysis test passed (score: {diversity_score:.2f})")


def test_impact_analysis():
    """Test impact scoring"""
    analyzer = CreativityAnalyzer()
    
    # High impact contribution affecting many files
    contributions = [
        {
            'diff': 'refactor code',
            'title': 'Large refactor',
            'body': 'System-wide improvements',
            'files': [
                'src/agents/agent1.py',
                'src/agents/agent2.py',
                'src/core/metrics.py',
                'src/core/analyzer.py',
                'src/utils/helpers.py',
                'tests/test_agents.py',
                'tests/test_metrics.py',
                'docs/README.md'
            ],
            'changed_files': 8
        }
    ]
    
    impact_score = analyzer.analyze_impact('test-agent', contributions)
    
    assert impact_score > 0.0
    assert impact_score <= 1.0
    
    print(f"✅ Impact analysis test passed (score: {impact_score:.2f})")


def test_learning_analysis():
    """Test learning progression tracking"""
    analyzer = CreativityAnalyzer()
    
    # Historical metrics showing improvement
    historical_metrics = [
        {
            'timestamp': '2024-01-01T00:00:00Z',
            'score': {'overall': 0.3}
        },
        {
            'timestamp': '2024-01-02T00:00:00Z',
            'score': {'overall': 0.5}
        },
        {
            'timestamp': '2024-01-03T00:00:00Z',
            'score': {'overall': 0.7}
        }
    ]
    
    contributions = [
        {
            'diff': 'some code',
            'title': 'Improvement',
            'body': 'Better approach',
            'files': ['test.py']
        }
    ]
    
    learning_score = analyzer.analyze_learning(
        'test-agent',
        contributions,
        historical_metrics
    )
    
    assert learning_score > 0.5  # Should show improvement
    assert learning_score <= 1.0
    
    print(f"✅ Learning analysis test passed (score: {learning_score:.2f})")


def test_complete_creativity_analysis():
    """Test full creativity analysis workflow"""
    analyzer = CreativityAnalyzer()
    
    # Create comprehensive test contributions
    contributions = [
        {
            'diff': """
            +@dataclass
            +class CreativityAnalyzer:
            +    def analyze(self):
            +        async with session:
            +            await process()
            """,
            'title': 'Add creativity analyzer',
            'body': 'New feature for measuring creativity with async processing',
            'files': [
                'tools/creativity_analyzer.py',
                'tools/metrics.py',
                'tests/test_creativity.py'
            ],
            'changed_files': 3,
            'additions': 200,
            'deletions': 10
        }
    ]
    
    metrics = analyzer.analyze_creativity(
        'test-agent-123',
        contributions,
        ecosystem_context={'all_contributions': []}
    )
    
    # Verify structure
    assert metrics.agent_id == 'test-agent-123'
    assert metrics.timestamp is not None
    assert isinstance(metrics.score, CreativityScore)
    assert isinstance(metrics.indicators, CreativityIndicators)
    
    # Verify scores are in valid range
    assert 0.0 <= metrics.score.novelty <= 1.0
    assert 0.0 <= metrics.score.diversity <= 1.0
    assert 0.0 <= metrics.score.impact <= 1.0
    assert 0.0 <= metrics.score.learning <= 1.0
    assert 0.0 <= metrics.score.overall <= 1.0
    
    # Verify indicators
    assert isinstance(metrics.indicators.novel_patterns, list)
    assert metrics.indicators.unique_approaches >= 0
    
    print(f"✅ Complete creativity analysis test passed")
    print(f"   Novelty: {metrics.score.novelty:.2%}")
    print(f"   Diversity: {metrics.score.diversity:.2%}")
    print(f"   Impact: {metrics.score.impact:.2%}")
    print(f"   Learning: {metrics.score.learning:.2%}")
    print(f"   Overall: {metrics.score.overall:.2%}")


def test_pattern_database_persistence():
    """Test pattern database saving and loading"""
    # Create temporary directory for testing
    with tempfile.TemporaryDirectory() as tmpdir:
        # Override the cache directory
        original_cache_dir = creativity_module.CREATIVITY_CACHE_DIR
        creativity_module.CREATIVITY_CACHE_DIR = Path(tmpdir) / "creativity"
        
        try:
            analyzer = CreativityAnalyzer()
            
            # Add some patterns
            analyzer.pattern_db['code_patterns'].add('test_pattern_1')
            analyzer.pattern_db['code_patterns'].add('test_pattern_2')
            analyzer._save_pattern_database()
            
            # Create new analyzer to test loading
            analyzer2 = CreativityAnalyzer()
            
            # Verify patterns were loaded
            assert 'test_pattern_1' in analyzer2.pattern_db['code_patterns']
            assert 'test_pattern_2' in analyzer2.pattern_db['code_patterns']
            
            print("✅ Pattern database persistence test passed")
        
        finally:
            # Restore original cache directory
            creativity_module.CREATIVITY_CACHE_DIR = original_cache_dir


def test_creativity_metrics_serialization():
    """Test CreativityMetrics serialization"""
    score = CreativityScore(
        novelty=0.8,
        diversity=0.7,
        impact=0.6,
        learning=0.5,
        overall=0.65
    )
    
    indicators = CreativityIndicators(
        novel_patterns=['pattern1', 'pattern2'],
        unique_approaches=5,
        first_time_solutions=3,
        cross_domain_contributions=4,
        breakthrough_moments=['Breakthrough 1']
    )
    
    metrics = CreativityMetrics(
        agent_id='test-agent',
        timestamp=datetime.now(timezone.utc).isoformat(),
        score=score,
        indicators=indicators,
        metadata={'test': 'data'}
    )
    
    # Test serialization
    data = metrics.to_dict()
    
    assert data['agent_id'] == 'test-agent'
    assert data['score']['novelty'] == 0.8
    assert data['indicators']['unique_approaches'] == 5
    assert data['metadata']['test'] == 'data'
    
    # Test JSON serialization
    json_str = json.dumps(data, indent=2)
    assert 'test-agent' in json_str
    
    print("✅ CreativityMetrics serialization test passed")


def run_all_tests():
    """Run all creativity metrics tests"""
    print("\n🎨 Running Creativity Metrics Tests\n")
    print("=" * 70)
    
    tests = [
        test_creativity_score_dataclass,
        test_creativity_indicators_dataclass,
        test_pattern_extraction,
        test_solution_approach_extraction,
        test_novelty_analysis,
        test_diversity_analysis,
        test_impact_analysis,
        test_learning_analysis,
        test_complete_creativity_analysis,
        test_pattern_database_persistence,
        test_creativity_metrics_serialization
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"❌ {test.__name__} failed: {e}")
            failed += 1
        except Exception as e:
            print(f"❌ {test.__name__} error: {e}")
            failed += 1
    
    print("\n" + "=" * 70)
    print(f"\n📊 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("✅ All tests passed!")
        return 0
    else:
        print(f"❌ {failed} test(s) failed")
        return 1


if __name__ == '__main__':
    sys.exit(run_all_tests())
