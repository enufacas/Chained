#!/usr/bin/env python3
"""
Self-Improving Code Analyzer for Chained

This analyzer learns from each merge, tracking code patterns and their
correlation with successful vs. problematic merges.
"""

import os
import sys
import json
import re
import ast
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any, Optional, Set
from collections import defaultdict
from functools import lru_cache


class CodeAnalyzer:
    """Analyzes code and learns from merge outcomes"""
    
    def __init__(self, patterns_file: str = "analysis/patterns.json"):
        self.patterns_file = patterns_file
        self.patterns_data = self._load_patterns()
        
    def _load_patterns(self) -> Dict:
        """Load the pattern database"""
        if os.path.exists(self.patterns_file):
            with open(self.patterns_file, 'r') as f:
                return json.load(f)
        return self._initialize_patterns()
    
    def _initialize_patterns(self) -> Dict:
        """Initialize pattern database with defaults"""
        return {
            "version": "1.0.0",
            "last_updated": None,
            "total_merges_analyzed": 0,
            "good_patterns": {
                "descriptive_variable_names": {
                    "count": 0,
                    "examples": [],
                    "correlation_with_success": 0.0
                },
                "comprehensive_docstrings": {
                    "count": 0,
                    "examples": [],
                    "correlation_with_success": 0.0
                },
                "error_handling": {
                    "count": 0,
                    "examples": [],
                    "correlation_with_success": 0.0
                },
                "modular_functions": {
                    "count": 0,
                    "examples": [],
                    "correlation_with_success": 0.0
                },
                "type_hints": {
                    "count": 0,
                    "examples": [],
                    "correlation_with_success": 0.0
                }
            },
            "bad_patterns": {
                "long_functions": {
                    "count": 0,
                    "examples": [],
                    "correlation_with_issues": 0.0
                },
                "deep_nesting": {
                    "count": 0,
                    "examples": [],
                    "correlation_with_issues": 0.0
                },
                "magic_numbers": {
                    "count": 0,
                    "examples": [],
                    "correlation_with_issues": 0.0
                },
                "unused_imports": {
                    "count": 0,
                    "examples": [],
                    "correlation_with_issues": 0.0
                },
                "inconsistent_naming": {
                    "count": 0,
                    "examples": [],
                    "correlation_with_issues": 0.0
                }
            },
            "merge_history": []
        }
    
    def _save_patterns(self):
        """Save the updated pattern database with proper error handling."""
        try:
            self.patterns_data["last_updated"] = datetime.now(timezone.utc).isoformat()
            
            # Ensure directory exists
            patterns_dir = os.path.dirname(self.patterns_file)
            if patterns_dir:
                os.makedirs(patterns_dir, exist_ok=True)
            
            # Write to temporary file first, then rename (atomic operation)
            temp_file = self.patterns_file + '.tmp'
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(self.patterns_data, f, indent=2)
            
            # Atomic rename
            os.replace(temp_file, self.patterns_file)
        except (IOError, OSError, json.JSONEncodeError) as e:
            # Clean up temp file if it exists
            temp_file = self.patterns_file + '.tmp'
            if os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except OSError:
                    pass
            raise IOError(f"Failed to save patterns: {e}")
    
    def analyze_python_file(self, filepath: str) -> Dict:
        """
        Analyze a Python file for patterns with proper error handling.
        
        Args:
            filepath: Path to the Python file to analyze
            
        Returns:
            Dictionary containing analysis results
            
        Raises:
            IOError: If the file cannot be read
            ValueError: If the file is not valid Python
        """
        # Validate filepath
        if not filepath:
            raise ValueError("File path cannot be empty")
        
        if not isinstance(filepath, str):
            raise ValueError(f"File path must be a string, got {type(filepath).__name__}")
        
        # Check file exists
        if not os.path.exists(filepath):
            raise IOError(f"File does not exist: {filepath}")
        
        if not os.path.isfile(filepath):
            raise IOError(f"Path is not a file: {filepath}")
        
        # Read file with proper error handling
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
        except (IOError, OSError, UnicodeDecodeError) as e:
            raise IOError(f"Failed to read file '{filepath}': {e}")
        
        results = {
            "file": filepath,
            "language": "python",
            "metrics": {},
            "patterns_found": {
                "good": [],
                "bad": []
            }
        }
        
        try:
            tree = ast.parse(content)
            results["metrics"]["total_lines"] = len(content.split('\n'))
            
            # Single-pass AST traversal for better performance
            # Collect all necessary information in one pass
            functions = []
            magic_numbers = []
            variable_names = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    functions.append(node)
                elif isinstance(node, ast.Constant) and isinstance(node.value, (int, float)) and not isinstance(node.value, bool):
                    if node.value not in [0, 1, -1, 2, 10, 100] and hasattr(node, 'lineno'):
                        magic_numbers.append(node)
                elif isinstance(node, ast.Name):
                    var_name = node.id
                    if len(var_name) > 3 and not var_name.startswith('_'):
                        variable_names.append(node)
            
            results["metrics"]["function_count"] = len(functions)
            
            # Process functions
            for func in functions:
                func_lines = func.end_lineno - func.lineno if hasattr(func, 'end_lineno') else 0
                
                # Check for long functions
                if func_lines > 50:
                    results["patterns_found"]["bad"].append({
                        "type": "long_functions",
                        "location": f"{func.name} at line {func.lineno}",
                        "details": f"{func_lines} lines"
                    })
                else:
                    results["patterns_found"]["good"].append({
                        "type": "modular_functions",
                        "location": f"{func.name} at line {func.lineno}",
                        "details": f"{func_lines} lines"
                    })
                
                # Check for docstrings
                docstring = ast.get_docstring(func)
                if docstring and len(docstring) > 20:
                    results["patterns_found"]["good"].append({
                        "type": "comprehensive_docstrings",
                        "location": f"{func.name} at line {func.lineno}",
                        "details": f"{len(docstring)} chars"
                    })
                
                # Check for type hints
                if func.returns or any(arg.annotation for arg in func.args.args):
                    results["patterns_found"]["good"].append({
                        "type": "type_hints",
                        "location": f"{func.name} at line {func.lineno}",
                        "details": "Has type hints"
                    })
                
                # Check for error handling
                has_try = any(isinstance(node, ast.Try) for node in ast.walk(func))
                if has_try:
                    results["patterns_found"]["good"].append({
                        "type": "error_handling",
                        "location": f"{func.name} at line {func.lineno}",
                        "details": "Uses try/except"
                    })
                
                # Check nesting depth
                max_depth = self._get_max_nesting_depth(func)
                if max_depth > 4:
                    results["patterns_found"]["bad"].append({
                        "type": "deep_nesting",
                        "location": f"{func.name} at line {func.lineno}",
                        "details": f"Depth: {max_depth}"
                    })
            
            # Process magic numbers collected in single pass
            for node in magic_numbers:
                results["patterns_found"]["bad"].append({
                    "type": "magic_numbers",
                    "location": f"line {node.lineno}",
                    "details": f"Number: {node.value}"
                })
            
            # Process variable names collected in single pass
            for node in variable_names:
                var_name = node.id
                results["patterns_found"]["good"].append({
                    "type": "descriptive_variable_names",
                    "location": f"line {node.lineno if hasattr(node, 'lineno') else 0}",
                    "details": f"Variable: {var_name}"
                })
        
        except SyntaxError as e:
            results["error"] = f"Syntax error: {str(e)}"
        except Exception as e:
            results["error"] = f"Analysis error: {str(e)}"
        
        return results
    
    def _get_max_nesting_depth(self, node: ast.AST, current_depth: int = 0) -> int:
        """Calculate maximum nesting depth in AST"""
        max_depth = current_depth
        
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.If, ast.For, ast.While, ast.With, ast.Try)):
                child_depth = self._get_max_nesting_depth(child, current_depth + 1)
                max_depth = max(max_depth, child_depth)
            else:
                child_depth = self._get_max_nesting_depth(child, current_depth)
                max_depth = max(max_depth, child_depth)
        
        return max_depth
    
    def analyze_directory(self, directory: str, extensions: List[str] = ['.py']) -> Dict:
        """
        Analyze all files in a directory with proper error handling.
        
        Args:
            directory: Path to the directory to analyze
            extensions: List of file extensions to analyze (default: ['.py'])
            
        Returns:
            Dictionary containing analysis results
            
        Raises:
            ValueError: If directory parameter is invalid
            IOError: If directory cannot be accessed
        """
        # Validate inputs
        if not directory:
            raise ValueError("Directory path cannot be empty")
        
        if not isinstance(directory, str):
            raise ValueError(f"Directory must be a string, got {type(directory).__name__}")
        
        if not os.path.exists(directory):
            raise IOError(f"Directory does not exist: {directory}")
        
        if not os.path.isdir(directory):
            raise IOError(f"Path is not a directory: {directory}")
        
        if not isinstance(extensions, list):
            raise ValueError(f"Extensions must be a list, got {type(extensions).__name__}")
        
        results = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "directory": directory,
            "files_analyzed": [],
            "errors": [],
            "summary": {
                "total_files": 0,
                "total_good_patterns": 0,
                "total_bad_patterns": 0,
                "pattern_breakdown": defaultdict(int)
            }
        }
        
        try:
            for root, dirs, files in os.walk(directory):
                # Skip hidden directories and common excludes
                dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', '__pycache__', 'venv']]
                
                for file in files:
                    if any(file.endswith(ext) for ext in extensions):
                        filepath = os.path.join(root, file)
                        
                        try:
                            if file.endswith('.py'):
                                analysis = self.analyze_python_file(filepath)
                                results["files_analyzed"].append(analysis)
                                
                                # Update summary
                                results["summary"]["total_files"] += 1
                                results["summary"]["total_good_patterns"] += len(analysis["patterns_found"]["good"])
                                results["summary"]["total_bad_patterns"] += len(analysis["patterns_found"]["bad"])
                                
                                for pattern in analysis["patterns_found"]["good"]:
                                    results["summary"]["pattern_breakdown"][f"good:{pattern['type']}"] += 1
                                
                                for pattern in analysis["patterns_found"]["bad"]:
                                    results["summary"]["pattern_breakdown"][f"bad:{pattern['type']}"] += 1
                        except Exception as e:
                            # Log error but continue processing other files
                            results["errors"].append({
                                "file": filepath,
                                "error": str(e)
                            })
        except OSError as e:
            raise IOError(f"Error walking directory '{directory}': {e}")
        
        return results
    
    def learn_from_merge(self, analysis_results: Dict, merge_successful: bool = True):
        """Update pattern database based on merge outcome"""
        self.patterns_data["total_merges_analyzed"] += 1
        
        # Store merge in history
        merge_record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "successful": merge_successful,
            "files_analyzed": analysis_results["summary"]["total_files"],
            "good_patterns": analysis_results["summary"]["total_good_patterns"],
            "bad_patterns": analysis_results["summary"]["total_bad_patterns"]
        }
        self.patterns_data["merge_history"].append(merge_record)
        
        # Keep only last 100 merges in history
        if len(self.patterns_data["merge_history"]) > 100:
            self.patterns_data["merge_history"] = self.patterns_data["merge_history"][-100:]
        
        # Update pattern counts and correlations
        for file_analysis in analysis_results["files_analyzed"]:
            for pattern in file_analysis["patterns_found"]["good"]:
                pattern_type = pattern["type"]
                if pattern_type in self.patterns_data["good_patterns"]:
                    self.patterns_data["good_patterns"][pattern_type]["count"] += 1
                    
                    # Update correlation (simple moving average)
                    current_corr = self.patterns_data["good_patterns"][pattern_type]["correlation_with_success"]
                    success_value = 1.0 if merge_successful else 0.0
                    weight = 0.1  # Learning rate
                    new_corr = current_corr * (1 - weight) + success_value * weight
                    self.patterns_data["good_patterns"][pattern_type]["correlation_with_success"] = new_corr
                    
                    # Store example (keep max 5)
                    examples = self.patterns_data["good_patterns"][pattern_type]["examples"]
                    if len(examples) < 5:
                        examples.append(pattern["location"])
            
            for pattern in file_analysis["patterns_found"]["bad"]:
                pattern_type = pattern["type"]
                if pattern_type in self.patterns_data["bad_patterns"]:
                    self.patterns_data["bad_patterns"][pattern_type]["count"] += 1
                    
                    # Update correlation
                    current_corr = self.patterns_data["bad_patterns"][pattern_type]["correlation_with_issues"]
                    issue_value = 0.0 if merge_successful else 1.0
                    weight = 0.1
                    new_corr = current_corr * (1 - weight) + issue_value * weight
                    self.patterns_data["bad_patterns"][pattern_type]["correlation_with_issues"] = new_corr
                    
                    # Store example (keep max 5)
                    examples = self.patterns_data["bad_patterns"][pattern_type]["examples"]
                    if len(examples) < 5:
                        examples.append(pattern["location"])
        
        self._save_patterns()
    
    def generate_report(self, analysis_results: Dict) -> str:
        """Generate a human-readable report"""
        report = []
        report.append("# Code Analysis Report")
        report.append(f"\n**Generated:** {analysis_results['timestamp']}")
        report.append(f"\n**Directory:** {analysis_results['directory']}")
        report.append(f"\n## Summary")
        report.append(f"- Files analyzed: {analysis_results['summary']['total_files']}")
        report.append(f"- Good patterns found: {analysis_results['summary']['total_good_patterns']}")
        report.append(f"- Bad patterns found: {analysis_results['summary']['total_bad_patterns']}")
        
        if analysis_results['summary']['pattern_breakdown']:
            report.append(f"\n## Pattern Breakdown")
            for pattern, count in sorted(analysis_results['summary']['pattern_breakdown'].items(), 
                                         key=lambda x: x[1], reverse=True):
                report.append(f"- {pattern}: {count}")
        
        # Add learning insights
        report.append(f"\n## Learning Insights")
        report.append(f"Total merges analyzed: {self.patterns_data['total_merges_analyzed']}")
        
        if self.patterns_data['total_merges_analyzed'] > 0:
            report.append(f"\n### Most Reliable Good Patterns")
            good_sorted = sorted(
                self.patterns_data['good_patterns'].items(),
                key=lambda x: x[1]['correlation_with_success'],
                reverse=True
            )[:3]
            
            for pattern_name, pattern_data in good_sorted:
                corr = pattern_data['correlation_with_success']
                count = pattern_data['count']
                report.append(f"- **{pattern_name}**: {corr:.2%} success correlation ({count} occurrences)")
            
            report.append(f"\n### Most Problematic Bad Patterns")
            bad_sorted = sorted(
                self.patterns_data['bad_patterns'].items(),
                key=lambda x: x[1]['correlation_with_issues'],
                reverse=True
            )[:3]
            
            for pattern_name, pattern_data in bad_sorted:
                corr = pattern_data['correlation_with_issues']
                count = pattern_data['count']
                report.append(f"- **{pattern_name}**: {corr:.2%} issue correlation ({count} occurrences)")
        
        report.append(f"\n## Recommendations")
        if analysis_results['summary']['total_bad_patterns'] > 0:
            report.append("- ⚠️ Consider refactoring code with detected bad patterns")
            report.append("- 📚 Review the pattern database for specific examples")
        
        if analysis_results['summary']['total_good_patterns'] > analysis_results['summary']['total_bad_patterns']:
            report.append("- ✅ Good pattern usage exceeds bad patterns - code quality looks solid!")
        
        return '\n'.join(report)


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Self-improving code analyzer')
    parser.add_argument('-d', '--directory', default='.', help='Directory to analyze')
    parser.add_argument('-f', '--file', help='Single file to analyze')
    parser.add_argument('-o', '--output', help='Output file for report')
    parser.add_argument('--learn', action='store_true', help='Learn from this merge (update patterns)')
    parser.add_argument('--success', action='store_true', default=True, help='Merge was successful (default: true)')
    parser.add_argument('--failure', action='store_true', help='Merge had issues (overrides --success)')
    
    args = parser.parse_args()
    
    analyzer = CodeAnalyzer()
    
    if args.file:
        # Analyze single file
        if args.file.endswith('.py'):
            result = analyzer.analyze_python_file(args.file)
            print(json.dumps(result, indent=2))
        else:
            print(f"Unsupported file type: {args.file}")
            sys.exit(1)
    else:
        # Analyze directory
        results = analyzer.analyze_directory(args.directory)
        
        # Generate report
        report = analyzer.generate_report(results)
        
        if args.output:
            with open(args.output, 'w') as f:
                f.write(report)
            print(f"Report saved to: {args.output}")
        else:
            print(report)
        
        # Learn from merge if requested
        if args.learn:
            merge_successful = not args.failure
            analyzer.learn_from_merge(results, merge_successful)
            print(f"\n✓ Learned from merge (successful: {merge_successful})")
            print(f"  Total merges analyzed: {analyzer.patterns_data['total_merges_analyzed']}")
        
        # Save detailed analysis
        analysis_file = f"analysis/merge_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json"
        os.makedirs('analysis', exist_ok=True)
        with open(analysis_file, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\nDetailed analysis saved to: {analysis_file}")


if __name__ == '__main__':
    main()
