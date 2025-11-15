#!/usr/bin/env python3
"""
Tests for AI Diversity Trend Analyzer

Created by @investigate-champion to validate trend analysis functionality.

Test Coverage:
- Historical data loading and parsing
- Diversity trend calculation
- Agent-specific trend analysis
- Innovation index tracking
- Recommendation generation
- Edge cases (insufficient data, missing files)
"""

import sys
import os
import json
import tempfile
import shutil
from pathlib import Path
from datetime import datetime, timedelta
import importlib.util

# Load the trend analyzer module
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'tools'))
try:
    import trend_analyzer as ta
except ImportError:
    # Alternative: load directly if module import fails
    spec = importlib.util.spec_from_file_location(
        "trend_analyzer",
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools", "trend-analyzer.py")
    )
    ta = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(ta)

TrendAnalyzer = ta.TrendAnalyzer


class TestTrendAnalyzer:
    """Test suite for TrendAnalyzer"""
    
    @staticmethod
    def create_test_snapshot(timestamp, agents=2, flags=0, contributions=5):
        """Helper to create test snapshot data"""
        return {
            "metadata": {
                "generated_at": timestamp.isoformat(),
                "repository": ".",
                "analysis_period_days": 30
            },
            "summary": {
                "total_agents": agents,
                "total_contributions": contributions,
                "agents": [f"agent-{i}" for i in range(agents)]
            },
            "repetition_flags": [
                {"agent_id": f"agent-0", "severity": "high"}
                for _ in range(flags)
            ],
            "solution_approaches": {
                f"approach-{i}": {"count": 1}
                for i in range(contributions // 2)
            }
        }
    
    @staticmethod
    def test_load_empty_history():
        """Test: Load historical data from empty directory"""
        with tempfile.TemporaryDirectory() as tmpdir:
            analyzer = TrendAnalyzer(tmpdir)
            
            # Create empty history directory
            history_dir = Path(tmpdir) / 'analysis' / 'repetition-history'
            history_dir.mkdir(parents=True, exist_ok=True)
            
            snapshots = analyzer.load_historical_data(days=30)
            
            assert snapshots == [], "Should return empty list for empty history"
            print("✓ Empty history test passed")
    
    @staticmethod
    def test_load_valid_snapshots():
        """Test: Load valid historical snapshots"""
        with tempfile.TemporaryDirectory() as tmpdir:
            analyzer = TrendAnalyzer(tmpdir)
            history_dir = Path(tmpdir) / 'analysis' / 'repetition-history'
            history_dir.mkdir(parents=True, exist_ok=True)
            
            # Create test snapshots
            now = datetime.now()
            snapshots_data = [
                (now - timedelta(days=2), 2, 0, 5),
                (now - timedelta(days=1), 2, 1, 6),
                (now, 3, 2, 7)
            ]
            
            for timestamp, agents, flags, contribs in snapshots_data:
                filename = timestamp.strftime('%Y-%m-%d-%H-%M-%S') + '.json'
                snapshot = TestTrendAnalyzer.create_test_snapshot(
                    timestamp, agents, flags, contribs
                )
                with open(history_dir / filename, 'w') as f:
                    json.dump(snapshot, f)
            
            loaded = analyzer.load_historical_data(days=30)
            
            assert len(loaded) == 3, f"Should load 3 snapshots, got {len(loaded)}"
            assert all('_timestamp' in s for s in loaded), "All snapshots should have timestamp"
            print("✓ Valid snapshots loading test passed")
    
    @staticmethod
    def test_diversity_trend_insufficient_data():
        """Test: Diversity trend with insufficient data"""
        with tempfile.TemporaryDirectory() as tmpdir:
            analyzer = TrendAnalyzer(tmpdir)
            analyzer.historical_data = []
            
            trend = analyzer.calculate_diversity_trend()
            
            assert trend['trend'] == 'insufficient_data', "Should detect insufficient data"
            assert trend['change'] == 0, "Change should be 0 for no data"
            print("✓ Insufficient data test passed")
    
    @staticmethod
    def test_diversity_trend_improving():
        """Test: Calculate improving diversity trend"""
        with tempfile.TemporaryDirectory() as tmpdir:
            analyzer = TrendAnalyzer(tmpdir)
            
            # Create trend: decreasing flags = improving diversity
            now = datetime.now()
            analyzer.historical_data = [
                {
                    '_timestamp': now - timedelta(days=5),
                    'summary': {'total_agents': 2, 'total_contributions': 10},
                    'repetition_flags': [{'agent_id': 'agent-1'}] * 5  # 5 flags
                },
                {
                    '_timestamp': now,
                    'summary': {'total_agents': 2, 'total_contributions': 10},
                    'repetition_flags': []  # 0 flags
                }
            ]
            
            trend = analyzer.calculate_diversity_trend()
            
            assert trend['trend'] == 'improving', f"Should be improving, got {trend['trend']}"
            assert trend['change'] > 0, "Change should be positive for improvement"
            print("✓ Improving diversity trend test passed")
    
    @staticmethod
    def test_agent_trends():
        """Test: Calculate per-agent trends"""
        with tempfile.TemporaryDirectory() as tmpdir:
            analyzer = TrendAnalyzer(tmpdir)
            
            now = datetime.now()
            analyzer.historical_data = [
                {
                    '_timestamp': now - timedelta(days=10),
                    'summary': {'agents': ['agent-1', 'agent-2']},
                    'repetition_flags': [
                        {'agent_id': 'agent-1'},
                        {'agent_id': 'agent-1'}
                    ]
                },
                {
                    '_timestamp': now - timedelta(days=9),
                    'summary': {'agents': ['agent-1', 'agent-2']},
                    'repetition_flags': [
                        {'agent_id': 'agent-1'},
                        {'agent_id': 'agent-1'}
                    ]
                },
                {
                    '_timestamp': now - timedelta(days=8),
                    'summary': {'agents': ['agent-1', 'agent-2']},
                    'repetition_flags': [
                        {'agent_id': 'agent-1'},
                        {'agent_id': 'agent-1'}
                    ]
                },
                {
                    '_timestamp': now - timedelta(days=5),
                    'summary': {'agents': ['agent-1', 'agent-2']},
                    'repetition_flags': []
                },
                {
                    '_timestamp': now - timedelta(days=2),
                    'summary': {'agents': ['agent-1', 'agent-2']},
                    'repetition_flags': []
                },
                {
                    '_timestamp': now,
                    'summary': {'agents': ['agent-1', 'agent-2']},
                    'repetition_flags': []
                }
            ]
            
            agent_trends = analyzer.calculate_agent_trends()
            
            assert 'agent-1' in agent_trends, "Should have trend for agent-1"
            # Check that there's a trend (stable or improving both ok for this test)
            assert agent_trends['agent-1']['trend'] in ['improving', 'stable'], \
                f"Agent-1 should be improving or stable, got {agent_trends['agent-1']['trend']}"
            print("✓ Agent trends test passed")
    
    @staticmethod
    def test_innovation_trend():
        """Test: Calculate innovation index trend"""
        with tempfile.TemporaryDirectory() as tmpdir:
            analyzer = TrendAnalyzer(tmpdir)
            
            now = datetime.now()
            analyzer.historical_data = [
                {
                    '_timestamp': now - timedelta(days=10),
                    'summary': {'total_contributions': 10},
                    'solution_approaches': {'approach-1': {}}  # 1 unique approach = 10%
                },
                {
                    '_timestamp': now - timedelta(days=9),
                    'summary': {'total_contributions': 10},
                    'solution_approaches': {'approach-1': {}}  # 1 unique approach = 10%
                },
                {
                    '_timestamp': now - timedelta(days=8),
                    'summary': {'total_contributions': 10},
                    'solution_approaches': {'approach-1': {}}  # 1 unique approach = 10%
                },
                {
                    '_timestamp': now - timedelta(days=2),
                    'summary': {'total_contributions': 10},
                    'solution_approaches': {
                        'approach-1': {},
                        'approach-2': {},
                        'approach-3': {},
                        'approach-4': {}
                    }  # 4 unique approaches = 40%
                },
                {
                    '_timestamp': now - timedelta(days=1),
                    'summary': {'total_contributions': 10},
                    'solution_approaches': {
                        'approach-1': {},
                        'approach-2': {},
                        'approach-3': {},
                        'approach-4': {},
                        'approach-5': {}
                    }  # 5 unique approaches = 50%
                },
                {
                    '_timestamp': now,
                    'summary': {'total_contributions': 10},
                    'solution_approaches': {
                        'approach-1': {},
                        'approach-2': {},
                        'approach-3': {},
                        'approach-4': {},
                        'approach-5': {},
                        'approach-6': {}
                    }  # 6 unique approaches = 60%
                }
            ]
            
            trend = analyzer.calculate_innovation_trend()
            
            assert trend['trend'] == 'increasing', f"Should be increasing, got {trend['trend']}"
            assert trend['change'] > 5, f"Change should be > 5, got {trend['change']}"
            print("✓ Innovation trend test passed")
    
    @staticmethod
    def test_generate_summary_report():
        """Test: Generate comprehensive summary report"""
        with tempfile.TemporaryDirectory() as tmpdir:
            analyzer = TrendAnalyzer(tmpdir)
            
            now = datetime.now()
            analyzer.historical_data = [
                {
                    '_timestamp': now - timedelta(days=1),
                    'summary': {'total_agents': 2, 'total_contributions': 5, 'agents': []},
                    'repetition_flags': [],
                    'solution_approaches': {}
                },
                {
                    '_timestamp': now,
                    'summary': {'total_agents': 2, 'total_contributions': 5, 'agents': []},
                    'repetition_flags': [],
                    'solution_approaches': {}
                }
            ]
            
            report = analyzer.generate_summary_report()
            
            assert 'metadata' in report, "Report should have metadata"
            assert 'diversity_trend' in report, "Report should have diversity trend"
            assert 'agent_trends' in report, "Report should have agent trends"
            assert 'innovation_trend' in report, "Report should have innovation trend"
            assert 'recommendations' in report, "Report should have recommendations"
            assert report['metadata']['snapshots_analyzed'] == 2
            print("✓ Summary report generation test passed")
    
    @staticmethod
    def test_recommendations_generation():
        """Test: Generate recommendations based on trends"""
        with tempfile.TemporaryDirectory() as tmpdir:
            analyzer = TrendAnalyzer(tmpdir)
            
            # Test declining diversity
            analyzer.historical_data = [
                {
                    '_timestamp': datetime.now() - timedelta(days=5),
                    'summary': {'total_agents': 2, 'total_contributions': 10, 'agents': []},
                    'repetition_flags': [],
                    'solution_approaches': {'a': {}, 'b': {}}
                },
                {
                    '_timestamp': datetime.now(),
                    'summary': {'total_agents': 2, 'total_contributions': 10, 'agents': []},
                    'repetition_flags': [{'agent_id': 'a'}] * 8,  # High flags
                    'solution_approaches': {'a': {}}  # Less approaches
                }
            ]
            
            recommendations = analyzer._generate_recommendations()
            
            assert len(recommendations) > 0, "Should generate recommendations"
            assert any('declining' in rec.lower() or 'decreasing' in rec.lower() 
                      for rec in recommendations), "Should warn about declining trend"
            print("✓ Recommendations generation test passed")


def run_all_tests():
    """Run all test cases"""
    test_methods = [
        method for method in dir(TestTrendAnalyzer)
        if method.startswith('test_') and callable(getattr(TestTrendAnalyzer, method))
    ]
    
    print(f"\n🧪 Running {len(test_methods)} tests for TrendAnalyzer...\n")
    
    passed = 0
    failed = 0
    
    for test_name in test_methods:
        try:
            test_method = getattr(TestTrendAnalyzer, test_name)
            test_method()
            passed += 1
        except AssertionError as e:
            print(f"✗ {test_name} failed: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ {test_name} error: {e}")
            failed += 1
    
    print(f"\n{'='*60}")
    print(f"Test Results: {passed} passed, {failed} failed")
    print(f"{'='*60}\n")
    
    return failed == 0


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
