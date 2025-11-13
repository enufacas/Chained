#!/usr/bin/env python3
"""
Quick validation test for the refactored evaluation system.

This ensures the modules can be imported and basic functionality works.
"""

import sys
from pathlib import Path

# Add tools directory to path
sys.path.insert(0, str(Path(__file__).parent / 'tools'))


def test_imports():
    """Test that all modules can be imported"""
    print("Testing imports...")
    
    try:
        import agent_evaluator
        print("✅ agent_evaluator imported")
    except Exception as e:
        print(f"❌ agent_evaluator import failed: {e}")
        return False
    
    try:
        import profile_manager
        print("✅ profile_manager imported")
    except Exception as e:
        print(f"❌ profile_manager import failed: {e}")
        return False
    
    try:
        import report_generator
        print("✅ report_generator imported")
    except Exception as e:
        print(f"❌ report_generator import failed: {e}")
        return False
    
    try:
        import pr_body_generator
        print("✅ pr_body_generator imported")
    except Exception as e:
        print(f"❌ pr_body_generator import failed: {e}")
        return False
    
    return True


def test_dataclasses():
    """Test that dataclasses are properly defined"""
    print("\nTesting dataclasses...")
    
    try:
        from agent_evaluator import AgentFate, EvaluationResults, EvaluationThresholds
        
        # Create a test fate
        fate = AgentFate(
            agent_id="test-123",
            name="Test Agent",
            score=0.75,
            outcome="maintained"
        )
        
        assert fate.is_maintained()
        assert not fate.is_promoted()
        assert not fate.is_eliminated()
        print("✅ AgentFate works correctly")
        
        # Create test results
        results = EvaluationResults()
        results.promoted.append(fate)
        assert results.total_evaluated == 1
        print("✅ EvaluationResults works correctly")
        
        # Create test thresholds
        thresholds = EvaluationThresholds(elimination=0.3, promotion=0.85)
        assert thresholds.elimination == 0.3
        print("✅ EvaluationThresholds works correctly")
        
        return True
        
    except Exception as e:
        print(f"❌ Dataclass test failed: {e}")
        return False


def test_profile_manager():
    """Test ProfileManager class"""
    print("\nTesting ProfileManager...")
    
    try:
        from profile_manager import ProfileManager
        
        manager = ProfileManager()
        assert manager.PROFILES_DIR.name == "profiles"
        assert manager.ARCHIVE_DIR.name == "archive"
        print("✅ ProfileManager instantiates correctly")
        
        return True
        
    except Exception as e:
        print(f"❌ ProfileManager test failed: {e}")
        return False


def test_pr_body_generator():
    """Test PR body generation with mock data"""
    print("\nTesting PR body generator...")
    
    try:
        import json
        from pathlib import Path
        import pr_body_generator
        
        # Create mock evaluation results
        mock_results = {
            'promoted': [
                {'id': 'agent-1', 'name': 'Agent One', 'score': 0.90}
            ],
            'eliminated': [
                {'id': 'agent-2', 'name': 'Agent Two', 'score': 0.25}
            ],
            'maintained': [
                {'id': 'agent-3', 'name': 'Agent Three', 'score': 0.50}
            ]
        }
        
        # Write mock data
        mock_path = Path('/tmp/test_evaluation_results.json')
        with open(mock_path, 'w') as f:
            json.dump(mock_results, f)
        
        # Test individual section generators
        summary = pr_body_generator._create_summary(1, 1, 1)
        assert 'Promoted to Hall of Fame' in summary
        assert '1 agents' in summary
        print("✅ PR body summary generation works")
        
        promoted_section = pr_body_generator._create_promoted_section(mock_results['promoted'])
        assert 'Agent One' in promoted_section
        print("✅ PR body promoted section generation works")
        
        # Clean up
        mock_path.unlink()
        
        return True
        
    except Exception as e:
        print(f"❌ PR body generator test failed: {e}")
        return False


def main():
    """Run all tests"""
    print("🧪 Running Validation Tests for Refactored Evaluation System\n")
    print("=" * 70)
    
    all_pass = True
    
    all_pass &= test_imports()
    all_pass &= test_dataclasses()
    all_pass &= test_profile_manager()
    all_pass &= test_pr_body_generator()
    
    print("\n" + "=" * 70)
    
    if all_pass:
        print("✅ All validation tests passed!")
        return 0
    else:
        print("❌ Some tests failed")
        return 1


if __name__ == '__main__':
    sys.exit(main())
