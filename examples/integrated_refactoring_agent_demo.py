#!/usr/bin/env python3
"""
Integrated Demo: Autonomous Refactoring Agent with Enhanced Features

This demo shows how the enhanced features (team learning, conflict resolution,
and advanced pattern recognition) integrate with the existing autonomous 
refactoring agent to create a more intelligent and team-aware system.

Author: @create-botter
Inspired by: Nikola Tesla - inventive and visionary
"""

import os
import sys
import tempfile
from pathlib import Path

# Add tools directory to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'tools'))

# Import base autonomous refactoring agent
import importlib.util
spec = importlib.util.spec_from_file_location(
    "autonomous_refactoring_agent",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools", "autonomous-refactoring-agent.py")
)
base_agent = importlib.util.module_from_spec(spec)
spec.loader.exec_module(base_agent)

# Import enhanced features
spec2 = importlib.util.spec_from_file_location(
    "enhanced_refactoring_features",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools", "enhanced-refactoring-features.py")
)
enhanced = importlib.util.module_from_spec(spec2)
spec2.loader.exec_module(enhanced)

StylePreferenceLearner = base_agent.StylePreferenceLearner
AutoRefactorer = base_agent.AutoRefactorer
TeamStyleLearner = enhanced.TeamStyleLearner
StyleConflictResolver = enhanced.StyleConflictResolver
AdvancedPatternRecognizer = enhanced.AdvancedPatternRecognizer


def print_section(title):
    """Print a formatted section header."""
    print(f"\n{'=' * 70}")
    print(f"  {title}")
    print(f"{'=' * 70}\n")


def demo_integrated_learning():
    """Demonstrate integrated learning from multiple sources."""
    print_section("Demo 1: Integrated Multi-Source Learning")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Initialize all components
        prefs_file = os.path.join(tmpdir, "preferences.json")
        patterns_file = os.path.join(tmpdir, "patterns.json")
        team_file = os.path.join(tmpdir, "team.json")
        
        base_learner = StylePreferenceLearner(prefs_file, patterns_file)
        team_learner = TeamStyleLearner(team_file)
        recognizer = AdvancedPatternRecognizer()
        
        # Simulate learning from a PR with team context
        print("📚 Learning from PR #123...")
        
        # Create a temporary file with good code
        good_code = '''
"""Module with clean Python style."""

from typing import List, Optional
import os

def calculate_sum(numbers: List[int]) -> int:
    """Calculate the sum of a list of numbers.
    
    Args:
        numbers: List of integers to sum
        
    Returns:
        The sum of all numbers
    """
    return sum(numbers)


def process_data(data: List[str]) -> Optional[List[str]]:
    """Process a list of data items.
    
    Args:
        data: List of strings to process
        
    Returns:
        Processed list or None if empty
    """
    if not data:
        return None
    return [item.strip().lower() for item in data]
'''
        
        # Save code to temp file
        temp_code_file = os.path.join(tmpdir, "good_code.py")
        with open(temp_code_file, 'w') as f:
            f.write(good_code)
        
        # Base learner: Learn from the PR
        pr_data = {
            'number': 123,
            'merged': True,
            'files_changed': [temp_code_file],
            'commit_sha': 'abc123def456'
        }
        base_learner.learn_from_pr_history(pr_data)
        
        # Team learner: Track who reviewed and approved
        team_learner.learn_from_review("alice", "naming_convention", "snake_case", approved=True)
        team_learner.learn_from_review("bob", "type_hints", True, approved=True)
        team_learner.learn_from_review("alice", "docstrings", True, approved=True)
        
        # Pattern recognizer: Extract and record patterns
        features = recognizer.extract_advanced_features(good_code, temp_code_file)
        recognizer.record_pattern(features, outcome=True)
        
        print(f"✓ Base learner: {len(base_learner.preferences)} preferences")
        print(f"✓ Team learner: {len(team_learner.team_members)} team members tracked")
        print(f"✓ Pattern recognizer: {len(recognizer.pattern_history)} patterns recorded")
        
        # Show what was learned
        print("\n📊 Base Learner Preferences:")
        summary = base_learner.get_preferences_summary()
        for pref in summary['top_preferences'][:3]:
            print(f"  • {pref['type']}: {pref['value']}")
            print(f"    Confidence: {pref['confidence']:.1%}, Success: {pref['success_rate']:.1%}")
        
        print("\n👥 Team Consensus:")
        for pref_type in ['naming_convention', 'type_hints', 'docstrings']:
            consensus = team_learner.get_team_consensus(pref_type)
            if consensus:
                value, confidence = consensus
                print(f"  • {pref_type}: {value} ({confidence:.1%} confidence)")


def demo_conflict_resolution_workflow():
    """Demonstrate the conflict resolution workflow."""
    print_section("Demo 2: Intelligent Conflict Resolution")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        prefs_file = os.path.join(tmpdir, "preferences.json")
        patterns_file = os.path.join(tmpdir, "patterns.json")
        team_file = os.path.join(tmpdir, "team.json")
        
        base_learner = StylePreferenceLearner(prefs_file, patterns_file)
        team_learner = TeamStyleLearner(team_file)
        resolver = StyleConflictResolver(team_learner)
        
        print("⚠️  Simulating conflicting preferences...")
        
        # Create conflicting preferences
        # Alice (expert) prefers snake_case
        team_learner.learn_from_review("alice", "naming", "snake_case", approved=True)
        team_learner.learn_from_review("alice", "naming", "snake_case", approved=True)
        team_learner.learn_from_review("alice", "naming", "snake_case", approved=True)
        
        # Bob (less experienced) prefers camelCase
        team_learner.learn_from_review("bob", "naming", "camelCase", approved=False)
        
        # Charlie (medium experience) agrees with Alice
        team_learner.learn_from_review("charlie", "naming", "snake_case", approved=True)
        team_learner.learn_from_review("charlie", "naming", "snake_case", approved=True)
        
        print(f"✓ Team members with preferences:")
        for username, member in team_learner.team_members.items():
            weight = member.get_weight()
            print(f"  • {username}: weight={weight:.2f}, reviews={member.review_count}")
        
        # Manually create mock conflicting preferences for demonstration
        from collections import namedtuple
        Pref = namedtuple('Pref', ['preference_type', 'value', 'confidence', 'sources'])
        
        mock_prefs = {
            'pref_alice': Pref('naming', 'snake_case', 0.9, ['alice', 'charlie']),
            'pref_bob': Pref('naming', 'camelCase', 0.6, ['bob']),
        }
        
        # Resolve conflicts
        result = resolver.resolve_all_conflicts(mock_prefs)
        
        print(f"\n🔧 Conflict Resolution Results:")
        print(f"  Conflicts detected: {result['conflicts_detected']}")
        print(f"  Conflicts resolved: {result['conflicts_resolved']}")
        
        for detail in result['conflict_details']:
            print(f"\n  📋 {detail['type']}:")
            print(f"     Resolution: {detail['resolution']}")
            print(f"     Rationale: {detail['rationale']}")


def demo_anomaly_detection_workflow():
    """Demonstrate anomaly detection in code."""
    print_section("Demo 3: Anomaly Detection and Pattern Analysis")
    
    recognizer = AdvancedPatternRecognizer()
    
    print("📖 Building historical pattern database...")
    
    # Create historical patterns with consistent style
    historical_code_samples = [
        '''
def function_one(x: int, y: int) -> int:
    """Calculate sum with type hints."""
    return x + y
''',
        '''
def function_two(a: str, b: str) -> str:
    """Concatenate strings with type hints."""
    return a + b
''',
        '''
def function_three(items: List[int]) -> int:
    """Sum list items with type hints."""
    return sum(items)
''',
    ]
    
    historical_features = []
    for i, code in enumerate(historical_code_samples):
        features = recognizer.extract_advanced_features(code, f"file{i}.py")
        historical_features.append(features)
        recognizer.record_pattern(features, outcome=True)
    
    print(f"✓ Built database with {len(historical_features)} historical patterns")
    
    # Analyze new code that deviates from the norm
    print("\n🔍 Analyzing new code for anomalies...")
    
    anomalous_code = '''
def badFunction(x, y):
    # No type hints, no docstring, camelCase
    return x+y
'''
    
    current_features = recognizer.extract_advanced_features(anomalous_code, "new_file.py")
    
    # Detect anomalies
    anomalies = recognizer.detect_style_anomalies(current_features, historical_features)
    
    print(f"⚠️  Detected {len(anomalies)} style anomalies:")
    for anomaly in anomalies:
        print(f"  • {anomaly}")
    
    # Calculate similarity to historical patterns
    print(f"\n📊 Style Similarity Analysis:")
    for i, hist_features in enumerate(historical_features):
        similarity = recognizer.calculate_style_similarity(current_features, hist_features)
        print(f"  • Similarity to file{i}.py: {similarity:.1%}")


def demo_success_prediction():
    """Demonstrate refactoring success prediction."""
    print_section("Demo 4: Refactoring Success Prediction")
    
    recognizer = AdvancedPatternRecognizer()
    
    print("📈 Building historical outcome database...")
    
    # Simulate historical refactoring outcomes
    historical_outcomes = [
        # Naming convention refactorings - mostly successful
        ("naming_convention", True),
        ("naming_convention", True),
        ("naming_convention", True),
        ("naming_convention", True),
        ("naming_convention", False),  # One failure
        
        # Type hints additions - mixed success
        ("type_hints", True),
        ("type_hints", True),
        ("type_hints", False),
        ("type_hints", False),
        
        # Indentation fixes - always successful
        ("indentation", True),
        ("indentation", True),
        ("indentation", True),
    ]
    
    print(f"✓ Loaded {len(historical_outcomes)} historical outcomes")
    
    # Predict success for different refactoring types
    print(f"\n🎯 Success Predictions:")
    
    refactoring_types = ["naming_convention", "type_hints", "indentation", "unknown_type"]
    
    for ref_type in refactoring_types:
        success_prob = recognizer.predict_refactoring_success(ref_type, historical_outcomes)
        confidence = "High" if success_prob > 0.7 else "Medium" if success_prob > 0.5 else "Low"
        print(f"  • {ref_type}: {success_prob:.1%} (Confidence: {confidence})")


def demo_end_to_end_workflow():
    """Demonstrate complete end-to-end workflow."""
    print_section("Demo 5: Complete End-to-End Workflow")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Initialize all components
        prefs_file = os.path.join(tmpdir, "preferences.json")
        patterns_file = os.path.join(tmpdir, "patterns.json")
        team_file = os.path.join(tmpdir, "team.json")
        
        base_learner = StylePreferenceLearner(prefs_file, patterns_file)
        team_learner = TeamStyleLearner(team_file)
        resolver = StyleConflictResolver(team_learner)
        recognizer = AdvancedPatternRecognizer()
        refactorer = AutoRefactorer(base_learner)
        
        print("🚀 Starting integrated refactoring workflow...")
        
        # Step 1: Learn from repository
        print("\n1️⃣  Learning from repository...")
        
        # Simulate learning from a file
        sample_code = '''
from typing import List

def calculate_average(numbers: List[float]) -> float:
    """Calculate average of numbers."""
    if not numbers:
        raise ValueError("Empty list")
    return sum(numbers) / len(numbers)
'''
        
        temp_file = os.path.join(tmpdir, "sample.py")
        with open(temp_file, 'w') as f:
            f.write(sample_code)
        
        pr_data = {
            'number': 456,
            'merged': True,
            'files_changed': [temp_file],
            'commit_sha': 'xyz789'
        }
        base_learner.learn_from_pr_history(pr_data)
        team_learner.learn_from_review("alice", "type_hints", True, approved=True)
        
        features = recognizer.extract_advanced_features(sample_code, temp_file)
        recognizer.record_pattern(features, outcome=True)
        
        print(f"   ✓ Learned preferences from repository")
        
        # Step 2: Resolve any conflicts
        print("\n2️⃣  Resolving preference conflicts...")
        result = resolver.resolve_all_conflicts(base_learner.preferences)
        print(f"   ✓ Resolved {result['conflicts_resolved']} conflicts")
        
        # Step 3: Analyze a new file
        print("\n3️⃣  Analyzing new code...")
        
        new_code = '''
def myFunction(x, y):
    result = x + y
    return result
'''
        
        new_file = os.path.join(tmpdir, "new_code.py")
        with open(new_file, 'w') as f:
            f.write(new_code)
        
        analysis = refactorer.analyze_file(new_file)
        new_features = recognizer.extract_advanced_features(new_code, new_file)
        anomalies = recognizer.detect_style_anomalies(new_features, [features])
        
        print(f"   ✓ Generated {len(analysis['suggestions'])} refactoring suggestions")
        print(f"   ✓ Detected {len(anomalies)} style anomalies")
        
        # Step 4: Predict success
        print("\n4️⃣  Predicting refactoring success...")
        
        if analysis['suggestions']:
            for sugg in analysis['suggestions']:
                success_prob = recognizer.predict_refactoring_success(
                    sugg['type'],
                    [("type_hints", True), (sugg['type'], True)]
                )
                print(f"   • {sugg['type']}: {success_prob:.1%} success probability")
        
        # Step 5: Generate report
        print("\n5️⃣  Generating comprehensive report...")
        
        print(f"\n   📊 Final Report:")
        print(f"   • Preferences learned: {len(base_learner.preferences)}")
        print(f"   • Team members tracked: {len(team_learner.team_members)}")
        print(f"   • Patterns recorded: {len(recognizer.pattern_history)}")
        print(f"   • Suggestions generated: {len(analysis['suggestions'])}")
        print(f"   • Anomalies detected: {len(anomalies)}")
        
        print(f"\n   ✅ Workflow completed successfully!")


def main():
    """Run all integrated demos."""
    print("""
╔══════════════════════════════════════════════════════════════════╗
║   Integrated Autonomous Refactoring Agent Demo                   ║
║   Base Agent + Enhanced Features                                 ║
║   @create-botter                                                    ║
╚══════════════════════════════════════════════════════════════════╝
    """)
    
    try:
        demo_integrated_learning()
        demo_conflict_resolution_workflow()
        demo_anomaly_detection_workflow()
        demo_success_prediction()
        demo_end_to_end_workflow()
        
        print_section("All Demos Completed Successfully!")
        
        print("✨ Key Achievements:")
        print("  1. ✓ Multi-source learning integration")
        print("  2. ✓ Intelligent conflict resolution")
        print("  3. ✓ Advanced anomaly detection")
        print("  4. ✓ Predictive success scoring")
        print("  5. ✓ Complete end-to-end workflow")
        
        print("\n🎯 The enhanced autonomous refactoring agent is ready!")
        print("   • Team-aware style learning")
        print("   • Conflict resolution with rationale")
        print("   • ML-based pattern recognition")
        print("   • Predictive refactoring success")
        
        print("\n" + "=" * 70)
        
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
