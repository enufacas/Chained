#!/usr/bin/env python3
"""
Example demonstrating the Autonomous Refactoring Agent in action.

This script shows how the agent learns from code and generates suggestions.
"""

import os
import sys
import json
import tempfile
from pathlib import Path

# Add tools directory to path
tools_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'tools'))
sys.path.insert(0, tools_path)

# Import the module using importlib
import importlib.util
spec = importlib.util.spec_from_file_location(
    "autonomous_refactoring_agent",
    os.path.join(tools_path, "autonomous-refactoring-agent.py")
)
agent_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(agent_module)

StylePreferenceLearner = agent_module.StylePreferenceLearner
AutoRefactorer = agent_module.AutoRefactorer
StylePreference = agent_module.StylePreference


def example_1_learn_from_good_code():
    """Example 1: Learning from well-styled code."""
    print("\n" + "="*70)
    print("Example 1: Learning from Well-Styled Code")
    print("="*70)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a learner
        prefs_file = os.path.join(tmpdir, "preferences.json")
        patterns_file = os.path.join(tmpdir, "patterns.json")
        learner = StylePreferenceLearner(prefs_file, patterns_file)
        
        # Create a well-styled Python file
        good_code = '''
"""Module demonstrating good Python style."""

from typing import List, Dict, Optional
import os
import sys


def calculate_average(numbers: List[float]) -> float:
    """Calculate the average of a list of numbers.
    
    Args:
        numbers: List of numbers to average
        
    Returns:
        The average value
        
    Raises:
        ValueError: If the list is empty
    """
    if not numbers:
        raise ValueError("Cannot calculate average of empty list")
    
    return sum(numbers) / len(numbers)


def process_data(data: Dict[str, any]) -> Dict[str, any]:
    """Process data with error handling.
    
    Args:
        data: Input data dictionary
        
    Returns:
        Processed data dictionary
    """
    try:
        result = {
            'processed': True,
            'count': len(data),
            'keys': list(data.keys())
        }
        return result
    except Exception as e:
        print(f"Error processing data: {e}")
        return {}


class DataProcessor:
    """Processes various types of data."""
    
    def __init__(self, config: Optional[Dict] = None):
        """Initialize the processor.
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self.processed_count = 0
    
    def process(self, item: Dict) -> Dict:
        """Process a single item.
        
        Args:
            item: Item to process
            
        Returns:
            Processed item
        """
        self.processed_count += 1
        return {**item, 'processed': True}
'''
        
        # Save the good code
        good_file = os.path.join(tmpdir, "good_example.py")
        with open(good_file, 'w') as f:
            f.write(good_code)
        
        # Simulate learning from a successful PR
        pr_data = {
            'number': 1,
            'merged': True,
            'files_changed': [good_file],
            'commit_sha': 'abc123'
        }
        
        print("\nLearning from a successful PR with well-styled code...")
        learner.learn_from_pr_history(pr_data)
        
        # Show what was learned
        summary = learner.get_preferences_summary()
        print(f"\n✓ Learned {summary['total_preferences']} style preferences")
        
        if summary['top_preferences']:
            print("\nTop learned preferences:")
            for pref in summary['top_preferences'][:5]:
                print(f"  • {pref['type']}: {pref['value']}")
                print(f"    Confidence: {pref['confidence']:.2f}, Occurrences: {pref['occurrences']}")


def example_2_learn_from_external_sources():
    """Example 2: Learning from external tech sources."""
    print("\n" + "="*70)
    print("Example 2: Learning from External Tech Sources")
    print("="*70)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a learner
        prefs_file = os.path.join(tmpdir, "preferences.json")
        patterns_file = os.path.join(tmpdir, "patterns.json")
        learner = StylePreferenceLearner(prefs_file, patterns_file)
        
        # Create a mock external learning source
        external_learning = {
            "timestamp": "2025-11-17T00:00:00Z",
            "source": "Tech Best Practices",
            "learnings": [
                {
                    "title": "Modern Python Best Practices",
                    "content": (
                        "Industry experts recommend using type hints for better code quality and "
                        "maintainability. Comprehensive docstrings help teams collaborate effectively. "
                        "Proper error handling prevents production issues. Clean code principles "
                        "emphasize modularity and readability."
                    ),
                    "source": "Tech Conference"
                },
                {
                    "title": "Code Quality Standards",
                    "content": (
                        "Studies show that code with type hints has 15% fewer bugs. "
                        "Projects with good docstrings are easier to maintain. "
                        "Error handling best practices reduce production incidents by 40%."
                    ),
                    "source": "Research Paper"
                }
            ]
        }
        
        # Save the external learning
        learning_file = os.path.join(tmpdir, "external_learning.json")
        with open(learning_file, 'w') as f:
            json.dump(external_learning, f)
        
        print("\nLearning from external tech sources (TLDR-style)...")
        learner.learn_from_external_source(learning_file)
        
        # Show what was learned
        external_prefs = [
            (k, v) for k, v in learner.preferences.items() 
            if k.startswith('external_')
        ]
        
        print(f"\n✓ Learned {len(external_prefs)} preferences from external sources")
        
        if external_prefs:
            print("\nExternal preferences learned:")
            for key, pref in external_prefs[:5]:
                print(f"  • {pref.preference_type}: {pref.value}")
                print(f"    Confidence: {pref.confidence:.2f}, Source: {pref.sources[0]}")


def example_3_generate_suggestions():
    """Example 3: Generating refactoring suggestions."""
    print("\n" + "="*70)
    print("Example 3: Generating Refactoring Suggestions")
    print("="*70)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a learner with some preferences
        prefs_file = os.path.join(tmpdir, "preferences.json")
        patterns_file = os.path.join(tmpdir, "patterns.json")
        learner = StylePreferenceLearner(prefs_file, patterns_file)
        
        # Set up learned preferences (simulating learned patterns)
        learner.preferences["naming_function_naming"] = StylePreference(
            preference_type="naming_function_naming",
            value="snake_case",
            confidence=0.9,
            occurrences=100,
            last_seen="2025-11-17T00:00:00Z",
            sources=["repo_history"],
            success_rate=0.95
        )
        
        learner.preferences["indentation_style"] = StylePreference(
            preference_type="indentation",
            value="spaces_4",
            confidence=0.85,
            occurrences=150,
            last_seen="2025-11-17T00:00:00Z",
            sources=["repo_history"],
            success_rate=0.92
        )
        
        # Create a file with style that doesn't match preferences
        bad_style_code = '''
def myFunction(x, y):
  result = x + y
  return result

def AnotherFunction(data):
  processedData = []
  for item in data:
    processedData.append(item * 2)
  return processedData
'''
        
        bad_file = os.path.join(tmpdir, "needs_refactoring.py")
        with open(bad_file, 'w') as f:
            f.write(bad_style_code)
        
        print("\nAnalyzing code that doesn't match learned preferences...")
        
        # Create refactorer and analyze
        refactorer = AutoRefactorer(learner)
        analysis = refactorer.analyze_file(bad_file)
        
        suggestions = analysis['suggestions']
        print(f"\n✓ Generated {len(suggestions)} refactoring suggestions")
        
        if suggestions:
            print("\nRefactoring suggestions:")
            for i, sugg in enumerate(suggestions, 1):
                print(f"\n  {i}. {sugg['type'].replace('_', ' ').title()}")
                print(f"     Current: {sugg['current']}")
                print(f"     Suggested: {sugg['suggested']}")
                print(f"     Confidence: {sugg['confidence']:.1%}")
                print(f"     Rationale: {sugg['rationale']}")


def example_4_comprehensive_report():
    """Example 4: Generating a comprehensive refactoring report."""
    print("\n" + "="*70)
    print("Example 4: Comprehensive Refactoring Report")
    print("="*70)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a learner with preferences
        prefs_file = os.path.join(tmpdir, "preferences.json")
        patterns_file = os.path.join(tmpdir, "patterns.json")
        learner = StylePreferenceLearner(prefs_file, patterns_file)
        
        # Set up learned preferences
        learner.preferences["naming_function_naming"] = StylePreference(
            preference_type="naming_function_naming",
            value="snake_case",
            confidence=0.9,
            occurrences=100,
            last_seen="2025-11-17T00:00:00Z",
            sources=["repo_history"],
            success_rate=0.95
        )
        
        # Create a test project with multiple files
        test_project = os.path.join(tmpdir, "test_project")
        os.makedirs(test_project)
        
        files = {
            "module1.py": "def myFunc(x): return x * 2",
            "module2.py": "def AnotherFunc(y): return y + 1",
            "module3.py": "def ProcessData(data): return data",
        }
        
        for filename, content in files.items():
            filepath = os.path.join(test_project, filename)
            with open(filepath, 'w') as f:
                f.write(content)
        
        print("\nGenerating refactoring report for test project...")
        
        # Generate report
        refactorer = AutoRefactorer(learner)
        report = refactorer.generate_refactoring_report(test_project)
        
        print(f"\n✓ Report generated successfully")
        print(f"\n  Files analyzed: {report['files_analyzed']}")
        print(f"  Total suggestions: {report['total_suggestions']}")
        
        if report['suggestions_by_type']:
            print(f"\n  Suggestions by type:")
            for stype, count in sorted(
                report['suggestions_by_type'].items(), 
                key=lambda x: x[1], 
                reverse=True
            ):
                print(f"    • {stype}: {count}")
        
        if report['high_priority_files']:
            print(f"\n  High priority files ({len(report['high_priority_files'])}):")
            for file_info in report['high_priority_files'][:3]:
                print(f"    • {os.path.basename(file_info['filepath'])}: "
                      f"{file_info['high_confidence_count']} high-confidence suggestions")


def main():
    """Run all examples."""
    print("\n" + "="*70)
    print("Autonomous Refactoring Agent - Examples")
    print("="*70)
    print("\nThese examples demonstrate the agent's learning and refactoring capabilities.")
    
    try:
        example_1_learn_from_good_code()
        example_2_learn_from_external_sources()
        example_3_generate_suggestions()
        example_4_comprehensive_report()
        
        print("\n" + "="*70)
        print("All examples completed successfully! ✓")
        print("="*70)
        print("\nThe autonomous refactoring agent can:")
        print("  • Learn code style preferences from successful PRs")
        print("  • Integrate external best practices from tech sources")
        print("  • Generate intelligent refactoring suggestions")
        print("  • Create comprehensive refactoring reports")
        print("  • Build confidence through repeated observations")
        print("  • Track success rates for data-driven decisions")
        print("\n" + "="*70)
        
    except Exception as e:
        print(f"\n✗ Error running examples: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
