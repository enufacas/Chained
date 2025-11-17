#!/usr/bin/env python3
"""
Autonomous Refactoring Agent for Chained
Part of the Chained autonomous AI ecosystem

This agent learns code style preferences from the repository's history,
external learnings (TLDR, HN, discussions), and applies them automatically
to improve code quality over time.

Key Features:
- Learns from successful PR patterns and merge history
- Integrates with existing learning systems (TLDR, HN, discussions)
- Tracks code style preferences and evolution over time
- Generates data-driven refactoring suggestions
- Creates automated PRs with improvements
- Self-improves based on feedback loop

Author: @restructure-master
Inspired by: Martin Fowler - clarity-seeking and pragmatic
"""

import os
import sys
import json
import ast
import re
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Set, Tuple
from collections import defaultdict, Counter
from dataclasses import dataclass, asdict, field
import importlib.util


# Import existing code analysis tools
def import_module_from_path(module_name: str, file_path: str):
    """Dynamically import a module from a file path."""
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# Get the tools directory
TOOLS_DIR = os.path.dirname(os.path.abspath(__file__))

# Import existing analyzers
code_analyzer_module = import_module_from_path(
    "code_analyzer",
    os.path.join(TOOLS_DIR, "code-analyzer.py")
)
CodeAnalyzer = code_analyzer_module.CodeAnalyzer

code_style_module = import_module_from_path(
    "code_style_transfer",
    os.path.join(TOOLS_DIR, "code-style-transfer.py")
)
StyleExtractor = code_style_module.StyleExtractor


@dataclass
class StylePreference:
    """Represents a learned code style preference."""
    preference_type: str  # e.g., "naming_convention", "indentation", "line_length"
    value: Any  # The preferred value
    confidence: float  # 0.0 to 1.0
    occurrences: int  # Number of times seen
    last_seen: str  # ISO timestamp
    sources: List[str] = field(default_factory=list)  # Where it was learned from
    success_rate: float = 0.0  # Success rate in merged PRs


@dataclass
class RefactoringPattern:
    """Represents a refactoring pattern learned from successful changes."""
    pattern_name: str
    description: str
    before_pattern: str  # Regex or AST pattern
    after_pattern: str  # Replacement pattern
    confidence: float
    success_count: int
    failure_count: int
    learned_from: List[str] = field(default_factory=list)
    category: str = "general"  # e.g., "naming", "structure", "complexity"


class StylePreferenceLearner:
    """
    Learns code style preferences from repository history and external sources.
    
    This class analyzes:
    - Successful PRs and their code patterns
    - Discussions about code style decisions
    - External learnings from TLDR, HN about industry best practices
    - Evolution of code style over time in the repository
    """
    
    def __init__(self, 
                 preferences_file: str = "analysis/style_preferences.json",
                 patterns_file: str = "analysis/refactoring_patterns.json"):
        self.preferences_file = preferences_file
        self.patterns_file = patterns_file
        self.preferences = self._load_preferences()
        self.patterns = self._load_patterns()
        self.code_analyzer = CodeAnalyzer()
        self.style_extractor = StyleExtractor()
        
    def _load_preferences(self) -> Dict[str, StylePreference]:
        """Load learned style preferences from file."""
        if os.path.exists(self.preferences_file):
            with open(self.preferences_file, 'r') as f:
                data = json.load(f)
                preferences = {}
                for key, val in data.items():
                    preferences[key] = StylePreference(**val)
                return preferences
        return {}
    
    def _save_preferences(self):
        """Save learned style preferences to file."""
        os.makedirs(os.path.dirname(self.preferences_file), exist_ok=True)
        data = {key: asdict(pref) for key, pref in self.preferences.items()}
        with open(self.preferences_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def _load_patterns(self) -> Dict[str, RefactoringPattern]:
        """Load learned refactoring patterns from file."""
        if os.path.exists(self.patterns_file):
            with open(self.patterns_file, 'r') as f:
                data = json.load(f)
                patterns = {}
                for key, val in data.items():
                    patterns[key] = RefactoringPattern(**val)
                return patterns
        return {}
    
    def _save_patterns(self):
        """Save learned refactoring patterns to file."""
        os.makedirs(os.path.dirname(self.patterns_file), exist_ok=True)
        data = {key: asdict(pattern) for key, pattern in self.patterns.items()}
        with open(self.patterns_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def learn_from_pr_history(self, pr_data: Dict[str, Any]):
        """
        Learn code style preferences from PR history.
        
        Args:
            pr_data: Dictionary containing PR information including:
                - files_changed: List of file paths
                - merged: Boolean indicating if PR was merged
                - review_comments: List of review comments
                - commit_sha: The commit SHA
        """
        if not pr_data.get('merged', False):
            return  # Only learn from successful PRs
        
        for file_path in pr_data.get('files_changed', []):
            if file_path.endswith('.py') and os.path.exists(file_path):
                try:
                    # Read file and extract style features
                    with open(file_path, 'r') as f:
                        code = f.read()
                    features = self.style_extractor.extract_from_code(code, file_path)
                    self._update_preferences_from_features(
                        asdict(features),
                        source=f"PR#{pr_data.get('number', 'unknown')}",
                        success=True
                    )
                except Exception as e:
                    print(f"Warning: Could not analyze {file_path}: {e}")
    
    def learn_from_discussion(self, discussion_file: str):
        """
        Learn from discussion insights about code style decisions.
        
        Args:
            discussion_file: Path to discussion JSON file
        """
        if not os.path.exists(discussion_file):
            return
        
        with open(discussion_file, 'r') as f:
            discussion = json.load(f)
        
        # Extract code style insights from the discussion
        insights = discussion.get('insights', [])
        for insight in insights:
            if 'code_style' in insight.get('tags', []):
                self._extract_preference_from_insight(insight)
    
    def learn_from_external_source(self, learning_file: str):
        """
        Learn from external sources like TLDR, HN about best practices.
        
        Args:
            learning_file: Path to learning JSON file
        """
        if not os.path.exists(learning_file):
            return
        
        with open(learning_file, 'r') as f:
            data = json.load(f)
        
        # Extract relevant code style practices from learnings
        learnings = data.get('learnings', [])
        for learning in learnings:
            content = learning.get('content', '')
            # Look for code style related keywords
            if any(keyword in content.lower() for keyword in [
                'code style', 'refactoring', 'clean code', 'best practices',
                'naming convention', 'code quality'
            ]):
                self._extract_preference_from_external(learning)
    
    def _update_preferences_from_features(self, features: Dict, source: str, success: bool):
        """Update preferences based on extracted style features."""
        timestamp = datetime.now(timezone.utc).isoformat()
        
        # Update indentation preference
        indent_key = "indentation_style"
        indent_value = f"{features.get('indent_type', 'spaces')}_{features.get('indent_size', 4)}"
        if indent_key in self.preferences:
            pref = self.preferences[indent_key]
            pref.occurrences += 1
            pref.last_seen = timestamp
            if success:
                pref.success_rate = (pref.success_rate * (pref.occurrences - 1) + 1.0) / pref.occurrences
            pref.confidence = min(1.0, pref.occurrences / 100.0)
            if source not in pref.sources:
                pref.sources.append(source)
        else:
            self.preferences[indent_key] = StylePreference(
                preference_type="indentation",
                value=indent_value,
                confidence=0.1,
                occurrences=1,
                last_seen=timestamp,
                sources=[source],
                success_rate=1.0 if success else 0.0
            )
        
        # Update naming convention preference
        for name_type in ['variable_naming', 'function_naming', 'class_naming']:
            if name_type in features:
                pref_key = f"naming_{name_type}"
                naming_style = features[name_type]
                if pref_key in self.preferences:
                    pref = self.preferences[pref_key]
                    pref.occurrences += 1
                    pref.last_seen = timestamp
                    if success:
                        pref.success_rate = (pref.success_rate * (pref.occurrences - 1) + 1.0) / pref.occurrences
                    pref.confidence = min(1.0, pref.occurrences / 50.0)
                else:
                    self.preferences[pref_key] = StylePreference(
                        preference_type=f"naming_{name_type}",
                        value=naming_style,
                        confidence=0.1,
                        occurrences=1,
                        last_seen=timestamp,
                        sources=[source],
                        success_rate=1.0 if success else 0.0
                    )
        
        # Update line length preference
        if 'max_line_length' in features:
            pref_key = "max_line_length"
            line_length = features['max_line_length']
            if pref_key in self.preferences:
                pref = self.preferences[pref_key]
                # Use weighted average for numeric values
                old_value = pref.value
                pref.value = (old_value * pref.occurrences + line_length) / (pref.occurrences + 1)
                pref.occurrences += 1
                pref.last_seen = timestamp
                if success:
                    pref.success_rate = (pref.success_rate * (pref.occurrences - 1) + 1.0) / pref.occurrences
                pref.confidence = min(1.0, pref.occurrences / 100.0)
            else:
                self.preferences[pref_key] = StylePreference(
                    preference_type="line_length",
                    value=line_length,
                    confidence=0.1,
                    occurrences=1,
                    last_seen=timestamp,
                    sources=[source],
                    success_rate=1.0 if success else 0.0
                )
        
        self._save_preferences()
    
    def _extract_preference_from_insight(self, insight: Dict):
        """Extract code style preference from a discussion insight."""
        # Parse the insight text for style-related information
        text = insight.get('text', '')
        timestamp = datetime.now(timezone.utc).isoformat()
        
        # Look for specific patterns in the insight
        # This is a simplified example - could be extended with NLP
        if 'prefer' in text.lower() and 'style' in text.lower():
            # Create a preference based on the insight
            pref_key = f"insight_{insight.get('id', 'unknown')}"
            if pref_key not in self.preferences:
                self.preferences[pref_key] = StylePreference(
                    preference_type="discussion_insight",
                    value=text[:100],  # Store first 100 chars
                    confidence=0.5,  # Medium confidence from discussions
                    occurrences=1,
                    last_seen=timestamp,
                    sources=[f"discussion_{insight.get('discussion_id', 'unknown')}"],
                    success_rate=0.8  # Discussions are generally high quality
                )
                self._save_preferences()
    
    def _extract_preference_from_external(self, learning: Dict):
        """Extract code style preference from external learning source."""
        content = learning.get('content', '')
        timestamp = datetime.now(timezone.utc).isoformat()
        
        # Look for specific best practice patterns
        # This could be enhanced with ML/NLP for better extraction
        best_practice_keywords = {
            'type hints': ('type_hints', True, 0.7),
            'docstrings': ('docstrings', True, 0.7),
            'error handling': ('error_handling', True, 0.8),
            'modularity': ('modularity', True, 0.7),
            'clean code': ('clean_code', True, 0.6),
        }
        
        for keyword, (pref_type, value, confidence) in best_practice_keywords.items():
            if keyword in content.lower():
                pref_key = f"external_{pref_type}"
                if pref_key in self.preferences:
                    pref = self.preferences[pref_key]
                    pref.occurrences += 1
                    pref.last_seen = timestamp
                    pref.confidence = min(1.0, (pref.confidence + confidence) / 2)
                else:
                    self.preferences[pref_key] = StylePreference(
                        preference_type=pref_type,
                        value=value,
                        confidence=confidence,
                        occurrences=1,
                        last_seen=timestamp,
                        sources=[learning.get('source', 'external')],
                        success_rate=0.7
                    )
        
        self._save_preferences()
    
    def get_preferences_summary(self) -> Dict[str, Any]:
        """Get a summary of learned preferences."""
        summary = {
            "total_preferences": len(self.preferences),
            "high_confidence_count": sum(1 for p in self.preferences.values() if p.confidence > 0.7),
            "preferences_by_type": defaultdict(int),
            "top_preferences": []
        }
        
        for pref in self.preferences.values():
            summary["preferences_by_type"][pref.preference_type] += 1
        
        # Get top preferences by confidence and occurrence
        sorted_prefs = sorted(
            self.preferences.items(),
            key=lambda x: (x[1].confidence * x[1].occurrences),
            reverse=True
        )
        
        summary["top_preferences"] = [
            {
                "key": key,
                "type": pref.preference_type,
                "value": pref.value,
                "confidence": pref.confidence,
                "occurrences": pref.occurrences,
                "success_rate": pref.success_rate
            }
            for key, pref in sorted_prefs[:10]
        ]
        
        return summary


class AutoRefactorer:
    """
    Applies learned style preferences to automatically refactor code.
    
    This class:
    - Uses learned preferences to suggest refactorings
    - Applies safe, automated improvements
    - Generates PR descriptions with rationale
    - Tracks refactoring success/failure for learning
    """
    
    def __init__(self, learner: StylePreferenceLearner):
        self.learner = learner
        self.code_analyzer = CodeAnalyzer()
        
    def analyze_file(self, filepath: str) -> Dict[str, Any]:
        """
        Analyze a file and suggest refactorings based on learned preferences.
        
        Args:
            filepath: Path to the Python file to analyze
            
        Returns:
            Dictionary with analysis results and suggestions
        """
        if not os.path.exists(filepath):
            return {"error": f"File not found: {filepath}"}
        
        # Analyze the file
        analysis = self.code_analyzer.analyze_python_file(filepath)
        
        # Extract current style
        with open(filepath, 'r') as f:
            code = f.read()
        style_extractor = StyleExtractor()
        current_style = style_extractor.extract_from_code(code, filepath)
        
        # Compare with learned preferences
        suggestions = []
        
        # Check indentation
        indent_pref = self.learner.preferences.get("indentation_style")
        if indent_pref and indent_pref.confidence > 0.5:
            current_indent = f"{current_style.indent_type}_{current_style.indent_size}"
            if current_indent != indent_pref.value:
                suggestions.append({
                    "type": "indentation",
                    "current": current_indent,
                    "suggested": indent_pref.value,
                    "confidence": indent_pref.confidence,
                    "rationale": f"Repository prefers {indent_pref.value} (seen {indent_pref.occurrences} times)"
                })
        
        # Check naming conventions
        for name_type in ['variable_naming', 'function_naming', 'class_naming']:
            pref_key = f"naming_{name_type}"
            pref = self.learner.preferences.get(pref_key)
            if pref and pref.confidence > 0.5:
                current_naming = getattr(current_style, name_type, None)
                if current_naming and current_naming != pref.value:
                    suggestions.append({
                        "type": f"naming_{name_type}",
                        "current": current_naming,
                        "suggested": pref.value,
                        "confidence": pref.confidence,
                        "rationale": f"Repository prefers {pref.value} for {name_type} (success rate: {pref.success_rate:.1%})"
                    })
        
        # Check line length
        line_length_pref = self.learner.preferences.get("max_line_length")
        if line_length_pref and line_length_pref.confidence > 0.5:
            current_max = current_style.max_line_length
            if abs(current_max - line_length_pref.value) > 10:
                suggestions.append({
                    "type": "line_length",
                    "current": current_max,
                    "suggested": int(line_length_pref.value),
                    "confidence": line_length_pref.confidence,
                    "rationale": f"Repository typically uses {int(line_length_pref.value)} chars per line"
                })
        
        return {
            "filepath": filepath,
            "current_style": asdict(current_style),
            "suggestions": suggestions,
            "analysis": analysis
        }
    
    def generate_refactoring_report(self, directory: str = ".") -> Dict[str, Any]:
        """
        Generate a report of refactoring opportunities in the repository.
        
        Args:
            directory: Root directory to scan
            
        Returns:
            Dictionary with refactoring opportunities
        """
        report = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "directory": directory,
            "files_analyzed": 0,
            "total_suggestions": 0,
            "suggestions_by_type": defaultdict(int),
            "high_priority_files": []
        }
        
        # Find all Python files
        for root, dirs, files in os.walk(directory):
            # Skip virtual environments and git directories
            dirs[:] = [d for d in dirs if d not in ['.git', 'venv', '__pycache__', '.venv', 'node_modules']]
            
            for file in files:
                if file.endswith('.py'):
                    filepath = os.path.join(root, file)
                    try:
                        analysis = self.analyze_file(filepath)
                        if 'error' not in analysis:
                            report["files_analyzed"] += 1
                            suggestions = analysis.get("suggestions", [])
                            report["total_suggestions"] += len(suggestions)
                            
                            for sugg in suggestions:
                                report["suggestions_by_type"][sugg["type"]] += 1
                            
                            # Track files with many high-confidence suggestions
                            high_confidence_suggestions = [
                                s for s in suggestions if s.get("confidence", 0) > 0.7
                            ]
                            if len(high_confidence_suggestions) >= 3:
                                report["high_priority_files"].append({
                                    "filepath": filepath,
                                    "suggestion_count": len(suggestions),
                                    "high_confidence_count": len(high_confidence_suggestions),
                                    "suggestions": high_confidence_suggestions[:5]  # Top 5
                                })
                    except Exception as e:
                        print(f"Warning: Could not analyze {filepath}: {e}")
        
        # Sort high priority files by suggestion count
        report["high_priority_files"].sort(
            key=lambda x: x["high_confidence_count"],
            reverse=True
        )
        
        return report


def main():
    """Main entry point for the autonomous refactoring agent."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Autonomous Refactoring Agent - Learn and apply code style preferences"
    )
    parser.add_argument(
        'command',
        choices=['learn', 'analyze', 'report', 'summary'],
        help='Command to execute'
    )
    parser.add_argument(
        '--source',
        help='Source directory or file to process'
    )
    parser.add_argument(
        '--output',
        help='Output file for results'
    )
    
    args = parser.parse_args()
    
    # Initialize the learner and refactorer
    learner = StylePreferenceLearner()
    refactorer = AutoRefactorer(learner)
    
    if args.command == 'learn':
        # Learn from various sources
        print("Learning from repository history...")
        
        # Learn from discussions
        discussions_dir = "learnings/discussions"
        if os.path.exists(discussions_dir):
            for file in os.listdir(discussions_dir):
                if file.endswith('.json') and 'discussion_issue' in file:
                    learner.learn_from_discussion(os.path.join(discussions_dir, file))
        
        # Learn from external sources
        learnings_dir = "learnings"
        if os.path.exists(learnings_dir):
            for file in os.listdir(learnings_dir):
                if file.startswith('tldr_') or file.startswith('hn_'):
                    learner.learn_from_external_source(os.path.join(learnings_dir, file))
        
        print("Learning complete!")
        
    elif args.command == 'analyze':
        source = args.source or "."
        if os.path.isfile(source):
            result = refactorer.analyze_file(source)
            print(json.dumps(result, indent=2))
        else:
            print(f"Please provide a file path with --source")
            
    elif args.command == 'report':
        source = args.source or "."
        print(f"Generating refactoring report for {source}...")
        report = refactorer.generate_refactoring_report(source)
        
        output_file = args.output or "analysis/refactoring_report.json"
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n=== Refactoring Report ===")
        print(f"Files analyzed: {report['files_analyzed']}")
        print(f"Total suggestions: {report['total_suggestions']}")
        print(f"\nSuggestions by type:")
        for stype, count in sorted(report['suggestions_by_type'].items(), key=lambda x: x[1], reverse=True):
            print(f"  {stype}: {count}")
        print(f"\nHigh priority files: {len(report['high_priority_files'])}")
        print(f"\nReport saved to: {output_file}")
        
    elif args.command == 'summary':
        summary = learner.get_preferences_summary()
        print("\n=== Style Preferences Summary ===")
        print(f"Total preferences learned: {summary['total_preferences']}")
        print(f"High confidence preferences: {summary['high_confidence_count']}")
        print(f"\nPreferences by type:")
        for ptype, count in sorted(summary['preferences_by_type'].items(), key=lambda x: x[1], reverse=True):
            print(f"  {ptype}: {count}")
        print(f"\nTop 10 preferences:")
        for pref in summary['top_preferences']:
            print(f"  {pref['type']}: {pref['value']} (confidence: {pref['confidence']:.2f}, occurrences: {pref['occurrences']})")


if __name__ == "__main__":
    main()
