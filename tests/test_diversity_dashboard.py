#!/usr/bin/env python3
"""
Tests for AI Diversity Dashboard Generator

Created by @investigate-champion to validate dashboard generation.

Test Coverage:
- Data loading from multiple sources
- Dashboard section generation
- Trend visualization formatting
- Agent ranking calculation
- Pattern library display
- Edge cases (missing data, empty metrics)
"""

import sys
import os
import json
import tempfile
from pathlib import Path
import importlib.util

# Load the dashboard module
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'tools'))
try:
    import diversity_dashboard as dd
except ImportError:
    spec = importlib.util.spec_from_file_location(
        "diversity_dashboard",
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools", "diversity-dashboard.py")
    )
    dd = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(dd)

DiversityDashboard = dd.DiversityDashboard


class TestDiversityDashboard:
    """Test suite for DiversityDashboard"""
    
    @staticmethod
    def create_test_data(tmpdir):
        """Helper to create test data files"""
        analysis_dir = Path(tmpdir) / 'analysis'
        analysis_dir.mkdir(parents=True, exist_ok=True)
        
        # Create trends data
        trends = {
            "diversity_trend": {
                "trend": "improving",
                "current_score": 75.0,
                "previous_score": 65.0,
                "change": 10.0,
                "data_points": [
                    {"timestamp": "2025-11-01T00:00:00", "score": 65.0},
                    {"timestamp": "2025-11-14T00:00:00", "score": 75.0}
                ]
            },
            "innovation_trend": {
                "trend": "stable",
                "current_average": 50.0,
                "previous_average": 48.0,
                "change": 2.0,
                "data_points": []
            },
            "metadata": {
                "snapshots_analyzed": 10
            },
            "recommendations": ["Test recommendation"]
        }
        with open(analysis_dir / 'diversity-trends.json', 'w') as f:
            json.dump(trends, f)
        
        # Create uniqueness scores
        scores = {
            "metadata": {"threshold": 30.0},
            "scores": {
                "agent-1": {
                    "overall_score": 85.0,
                    "metrics": {
                        "approach_diversity": 75.0,
                        "innovation_index": 5
                    }
                },
                "agent-2": {
                    "overall_score": 25.0,
                    "metrics": {
                        "approach_diversity": 20.0,
                        "innovation_index": 1
                    }
                }
            }
        }
        with open(analysis_dir / 'uniqueness-scores.json', 'w') as f:
            json.dump(scores, f)
        
        # Create pattern library
        patterns = {
            "pattern_library": {
                "successful_diverse_approaches": [
                    {
                        "description": "Test pattern",
                        "success_rate": 0.9,
                        "examples": ["Example 1", "Example 2"]
                    }
                ],
                "repetitive_patterns": [
                    {
                        "description": "Bad pattern",
                        "warning": "Don't do this"
                    }
                ]
            }
        }
        with open(analysis_dir / 'pattern-diversity.json', 'w') as f:
            json.dump(patterns, f)
    
    @staticmethod
    def test_load_data_all_files():
        """Test: Load all data files successfully"""
        with tempfile.TemporaryDirectory() as tmpdir:
            TestDiversityDashboard.create_test_data(tmpdir)
            dashboard = DiversityDashboard(tmpdir)
            dashboard.load_data()
            
            assert dashboard.trends_data is not None, "Should load trends data"
            assert dashboard.uniqueness_scores is not None, "Should load scores"
            assert dashboard.pattern_library is not None, "Should load patterns"
            print("✓ Data loading test passed")
    
    @staticmethod
    def test_load_data_missing_files():
        """Test: Handle missing data files gracefully"""
        with tempfile.TemporaryDirectory() as tmpdir:
            dashboard = DiversityDashboard(tmpdir)
            # Don't create any files
            dashboard.load_data()
            
            # Should not crash, just have None values
            assert dashboard.trends_data is None, "Trends should be None if missing"
            print("✓ Missing files handling test passed")
    
    @staticmethod
    def test_generate_overview_with_data():
        """Test: Generate overview section with data"""
        with tempfile.TemporaryDirectory() as tmpdir:
            TestDiversityDashboard.create_test_data(tmpdir)
            dashboard = DiversityDashboard(tmpdir)
            dashboard.load_data()
            
            overview = dashboard.generate_overview_section()
            
            assert "# 🎨 AI Diversity Dashboard" in overview, "Should have title"
            assert "Diversity Score" in overview, "Should have diversity metric"
            assert "Innovation Index" in overview, "Should have innovation metric"
            assert "75.0/100" in overview, "Should show correct diversity score"
            print("✓ Overview generation test passed")
    
    @staticmethod
    def test_generate_overview_no_data():
        """Test: Generate overview section without data"""
        with tempfile.TemporaryDirectory() as tmpdir:
            dashboard = DiversityDashboard(tmpdir)
            dashboard.load_data()
            
            overview = dashboard.generate_overview_section()
            
            assert "# 🎨 AI Diversity Dashboard" in overview, "Should have title"
            assert "No trend data available" in overview, "Should indicate missing data"
            print("✓ Overview without data test passed")
    
    @staticmethod
    def test_generate_agent_rankings():
        """Test: Generate agent rankings table"""
        with tempfile.TemporaryDirectory() as tmpdir:
            TestDiversityDashboard.create_test_data(tmpdir)
            dashboard = DiversityDashboard(tmpdir)
            dashboard.load_data()
            
            rankings = dashboard.generate_agent_rankings()
            
            assert "Agent Uniqueness Rankings" in rankings, "Should have section title"
            assert "agent-1" in rankings, "Should list agent-1"
            assert "85.0" in rankings, "Should show agent-1 score"
            assert "🌟 Excellent" in rankings, "High score should get excellent status"
            assert "⚠️  Needs Improvement" in rankings, "Low score should get warning"
            print("✓ Agent rankings test passed")
    
    @staticmethod
    def test_generate_pattern_library():
        """Test: Generate pattern library section"""
        with tempfile.TemporaryDirectory() as tmpdir:
            TestDiversityDashboard.create_test_data(tmpdir)
            dashboard = DiversityDashboard(tmpdir)
            dashboard.load_data()
            
            library = dashboard.generate_pattern_library()
            
            assert "Pattern Library" in library, "Should have section title"
            assert "Test pattern" in library, "Should show successful pattern"
            assert "Bad pattern" in library, "Should show repetitive pattern"
            assert "90%" in library, "Should show success rate"
            print("✓ Pattern library test passed")
    
    @staticmethod
    def test_generate_complete_dashboard():
        """Test: Generate complete dashboard"""
        with tempfile.TemporaryDirectory() as tmpdir:
            TestDiversityDashboard.create_test_data(tmpdir)
            dashboard = DiversityDashboard(tmpdir)
            dashboard.load_data()
            
            complete = dashboard.generate_dashboard()
            
            # Check all sections are present
            assert "# 🎨 AI Diversity Dashboard" in complete
            assert "## 📊 Overview" in complete
            assert "## 🏆 Agent Uniqueness Rankings" in complete
            assert "## 📈 Diversity Trends" in complete
            assert "## 📚 Pattern Library" in complete
            assert "## 💡 Recommendations" in complete
            assert "@investigate-champion" in complete
            print("✓ Complete dashboard generation test passed")
    
    @staticmethod
    def test_trend_emoji():
        """Test: Trend emoji selection"""
        dashboard = DiversityDashboard('.')
        
        assert dashboard._trend_emoji('improving') == '📈'
        assert dashboard._trend_emoji('declining') == '📉'
        assert dashboard._trend_emoji('stable') == '➡️'
        assert dashboard._trend_emoji('unknown') == '❓'
        print("✓ Trend emoji test passed")
    
    @staticmethod
    def test_create_sparkline():
        """Test: ASCII sparkline creation"""
        dashboard = DiversityDashboard('.')
        
        values = [10, 20, 30, 40, 50]
        sparkline = dashboard._create_sparkline(values, "Test")
        
        assert "Test" in sparkline, "Should include label"
        assert "Min: 10" in sparkline, "Should show min value"
        assert "Max: 50" in sparkline, "Should show max value"
        assert "Latest: 50" in sparkline, "Should show latest value"
        print("✓ Sparkline creation test passed")


def run_all_tests():
    """Run all test cases"""
    test_methods = [
        method for method in dir(TestDiversityDashboard)
        if method.startswith('test_') and callable(getattr(TestDiversityDashboard, method))
    ]
    
    print(f"\n🧪 Running {len(test_methods)} tests for DiversityDashboard...\n")
    
    passed = 0
    failed = 0
    
    for test_name in test_methods:
        try:
            test_method = getattr(TestDiversityDashboard, test_name)
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
