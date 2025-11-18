#!/usr/bin/env python3
"""
Tests for Predictive Spawning Engine

Validates time-series forecasting, pattern recognition,
self-tuning, and predictive recommendations.

Created by @accelerate-specialist
"""

import sys
import json
from pathlib import Path
from datetime import datetime, timedelta

# Add tools directory to path
sys.path.insert(0, str(Path(__file__).parent / "tools"))

from predictive_spawning_engine import PredictiveSpawningEngine


def test_workload_forecasting():
    """Test workload forecasting with time-series prediction."""
    print("\n🧪 Test: Workload Forecasting")
    
    engine = PredictiveSpawningEngine()
    
    # Add some historical data
    for i in range(20):
        engine.record_observation('testing', 5.0 + i * 0.5)  # Increasing trend
    
    # Forecast
    forecast = engine.forecast_workload('testing', hours_ahead=12)
    
    print(f"  Predicted workload: {forecast['predicted_workload']:.2f}")
    print(f"  Confidence: {forecast['confidence']:.0%}")
    print(f"  Trend: {forecast['trend']}")
    
    assert forecast['predicted_workload'] > 0
    assert 0 <= forecast['confidence'] <= 1
    assert forecast['trend'] in ['increasing', 'decreasing', 'stable', 'insufficient_data']
    
    print("✅ Workload forecasting works correctly")


def test_insufficient_data_handling():
    """Test handling of insufficient data for prediction."""
    print("\n🧪 Test: Insufficient Data Handling")
    
    engine = PredictiveSpawningEngine()
    
    # Try to forecast with no data
    forecast = engine.forecast_workload('security', hours_ahead=6)
    
    print(f"  Trend with no data: {forecast['trend']}")
    
    assert forecast['trend'] == 'insufficient_data'
    assert forecast['confidence'] == 0.0
    
    print("✅ Insufficient data handling works correctly")


def test_pattern_recognition():
    """Test pattern recognition for daily cycles."""
    print("\n🧪 Test: Pattern Recognition")
    
    engine = PredictiveSpawningEngine()
    
    # Add data with daily pattern (peak at 9 AM and 2 PM)
    base_time = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    
    for day in range(7):
        for hour in range(24):
            timestamp = base_time + timedelta(days=day, hours=hour)
            # Simulate peaks at 9 and 14
            workload = 10 if hour in [9, 14] else 3
            
            observation = {
                'timestamp': timestamp.isoformat(),
                'category': 'api',
                'workload': workload
            }
            engine.history.append(observation)
    
    engine._save_history()
    
    # Detect patterns
    patterns = engine.detect_patterns('api')
    
    print(f"  Detected {len(patterns)} pattern(s)")
    if patterns:
        print(f"  Pattern type: {patterns[0]['type']}")
        print(f"  Peak hours: {patterns[0].get('peak_hours', [])}")
    
    assert len(patterns) > 0
    assert patterns[0]['type'] == 'daily_cycle'
    
    print("✅ Pattern recognition works correctly")


def test_predictive_recommendations():
    """Test predictive spawn recommendations."""
    print("\n🧪 Test: Predictive Recommendations")
    
    engine = PredictiveSpawningEngine()
    
    # Add data indicating high future workload
    for i in range(30):
        engine.record_observation('performance', 2.0 + i * 0.3)  # Increasing trend
    
    # Get recommendations
    recommendations = engine.get_predictive_recommendations()
    
    print(f"  Generated {len(recommendations)} recommendation(s)")
    if recommendations:
        rec = recommendations[0]
        print(f"  Category: {rec['category']}")
        print(f"  Agents needed: {rec['agents_needed']}")
        print(f"  Confidence: {rec['confidence']:.0%}")
    
    assert isinstance(recommendations, list)
    
    print("✅ Predictive recommendations work correctly")


def test_self_tuning():
    """Test self-tuning of parameters based on feedback."""
    print("\n🧪 Test: Self-Tuning Parameters")
    
    engine = PredictiveSpawningEngine()
    
    initial_threshold = engine.parameters['spawn_threshold']
    initial_lead_time = engine.parameters['lead_time_hours']
    
    print(f"  Initial threshold: {initial_threshold:.2f}")
    print(f"  Initial lead time: {initial_lead_time} hours")
    
    # Provide feedback indicating over-spawning
    for i in range(12):
        engine.update_performance_feedback('testing', {
            'spawns': 5,
            'actual_needed': 3,
            'prediction_accuracy': 0.65
        })
    
    new_threshold = engine.parameters['spawn_threshold']
    new_lead_time = engine.parameters['lead_time_hours']
    
    print(f"  New threshold: {new_threshold:.2f}")
    print(f"  New lead time: {new_lead_time} hours")
    
    # Threshold should increase (spawn less) when over-spawning
    # Lead time should increase when accuracy is low
    assert new_threshold >= initial_threshold or new_lead_time >= initial_lead_time
    
    print("✅ Self-tuning works correctly")


def test_resource_optimization():
    """Test resource-optimized spawn calculations."""
    print("\n🧪 Test: Resource Optimization")
    
    engine = PredictiveSpawningEngine()
    
    # Set known parameters
    engine.parameters['spawn_threshold'] = 5.0
    engine.parameters['target_utilization'] = 0.75
    
    # Add high workload data
    for i in range(20):
        engine.record_observation('security', 10.0)
    
    recommendations = engine.get_predictive_recommendations()
    
    if recommendations:
        security_recs = [r for r in recommendations if r['category'] == 'security']
        if security_recs:
            rec = security_recs[0]
            print(f"  Agents needed: {rec['agents_needed']}")
            print(f"  Predicted workload: {rec['predicted_workload']:.1f}")
            print(f"  Target utilization: 75%")
            
            # Verify reasonable agent count
            assert rec['agents_needed'] > 0
            assert rec['agents_needed'] < 10  # Should be reasonable
    
    print("✅ Resource optimization works correctly")


def test_emergent_behavior_analysis():
    """Test emergent behavior detection."""
    print("\n🧪 Test: Emergent Behavior Analysis")
    
    engine = PredictiveSpawningEngine()
    
    # Analyze emergent behaviors
    behaviors = engine.analyze_emergent_behaviors()
    
    print(f"  Found {len(behaviors)} behavior categories")
    
    assert 'collaboration_synergies' in behaviors
    assert 'cascade_effects' in behaviors
    assert 'optimal_compositions' in behaviors
    assert 'peak_patterns' in behaviors
    
    print("✅ Emergent behavior analysis works correctly")


def test_confidence_gating():
    """Test that low-confidence predictions are filtered out."""
    print("\n🧪 Test: Confidence Gating")
    
    engine = PredictiveSpawningEngine()
    
    # Set high confidence threshold
    engine.parameters['confidence_threshold'] = 0.9
    
    # Add minimal data (low confidence)
    for i in range(5):
        engine.record_observation('documentation', 3.0)
    
    recommendations = engine.get_predictive_recommendations()
    
    # Should get no recommendations due to low confidence
    doc_recs = [r for r in recommendations if r['category'] == 'documentation']
    
    print(f"  Recommendations with high confidence threshold: {len(doc_recs)}")
    
    # Confidence gating should filter low-confidence predictions
    assert len(doc_recs) == 0 or all(r['confidence'] >= 0.9 for r in doc_recs)
    
    print("✅ Confidence gating works correctly")


def test_feedback_persistence():
    """Test that feedback is persisted correctly."""
    print("\n🧪 Test: Feedback Persistence")
    
    engine = PredictiveSpawningEngine()
    
    # Add some feedback
    engine.update_performance_feedback('feature', {
        'spawns': 3,
        'actual_needed': 3,
        'prediction_accuracy': 0.92
    })
    
    initial_count = len(engine.feedback)
    
    # Create new engine instance (should load persisted feedback)
    engine2 = PredictiveSpawningEngine()
    
    print(f"  Feedback entries: {len(engine2.feedback)}")
    
    assert len(engine2.feedback) >= initial_count
    
    print("✅ Feedback persistence works correctly")


def test_prediction_report():
    """Test prediction report generation."""
    print("\n🧪 Test: Prediction Report Generation")
    
    engine = PredictiveSpawningEngine()
    
    # Add some data
    for i in range(15):
        engine.record_observation('api', 4.0 + i * 0.2)
    
    # Generate report
    report = engine.generate_prediction_report()
    
    print(f"  Report length: {len(report)} characters")
    
    assert len(report) > 100
    assert "PREDICTIVE SPAWNING REPORT" in report
    assert "Workload Forecasts" in report
    
    print("✅ Prediction report generation works correctly")


def run_all_tests():
    """Run all predictive spawning engine tests."""
    print("=" * 80)
    print("🧪 Testing Predictive Spawning Engine")
    print("=" * 80)
    
    tests = [
        test_workload_forecasting,
        test_insufficient_data_handling,
        test_pattern_recognition,
        test_predictive_recommendations,
        test_self_tuning,
        test_resource_optimization,
        test_emergent_behavior_analysis,
        test_confidence_gating,
        test_feedback_persistence,
        test_prediction_report,
    ]
    
    passed = 0
    failed = 0
    
    for test_func in tests:
        try:
            test_func()
            passed += 1
        except AssertionError as e:
            print(f"❌ Test failed: {e}")
            failed += 1
        except Exception as e:
            print(f"❌ Test error: {e}")
            failed += 1
    
    print("\n" + "=" * 80)
    print(f"📊 Test Results: {passed}/{len(tests)} passed")
    if failed == 0:
        print("✅ All tests passed!")
    else:
        print(f"❌ {failed} test(s) failed")
    print("=" * 80)
    
    return 0 if failed == 0 else 1


if __name__ == '__main__':
    sys.exit(run_all_tests())
