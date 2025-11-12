#!/usr/bin/env python3
"""
Code Readability Scorer for Chained

Analyzes code readability using multiple metrics and provides actionable
improvement suggestions with priority levels.
"""

import os
import sys
import json
import ast
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict


class ReadabilityScorer:
    """Analyzes code readability and generates improvement suggestions"""
    
    def __init__(self):
        self.naming_keywords = {
            'good': ['calculate', 'process', 'validate', 'parse', 'format', 'convert', 
                    'generate', 'create', 'update', 'delete', 'fetch', 'load', 'save',
                    'build', 'handle', 'execute', 'initialize', 'configure'],
            'bad': ['func', 'method', 'do', 'run', 'go', 'tmp', 'temp', 'data', 'info',
                   'obj', 'val', 'var', 'thing', 'stuff', 'handle']
        }
    
    def analyze_file(self, filepath: str) -> Dict:
        """
        Analyze a Python file for readability.
        
        Args:
            filepath: Path to the Python file to analyze
            
        Returns:
            Dictionary containing readability analysis results
            
        Raises:
            IOError: If the file cannot be read
            ValueError: If the file is not valid Python
        """
        # Validate filepath
        if not filepath:
            raise ValueError("File path cannot be empty")
        
        if not isinstance(filepath, str):
            raise ValueError(f"File path must be a string, got {type(filepath).__name__}")
        
        if not os.path.exists(filepath):
            raise IOError(f"File does not exist: {filepath}")
        
        if not os.path.isfile(filepath):
            raise IOError(f"Path is not a file: {filepath}")
        
        # Read file
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
        except (IOError, OSError, UnicodeDecodeError) as e:
            raise IOError(f"Failed to read file '{filepath}': {e}")
        
        results = {
            "file": filepath,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "scores": {},
            "metrics": {},
            "suggestions": []
        }
        
        try:
            # Parse the file
            tree = ast.parse(content)
            lines = content.split('\n')
            
            # Analyze different aspects
            naming_score, naming_metrics, naming_suggestions = self._analyze_naming(tree, content)
            complexity_score, complexity_metrics, complexity_suggestions = self._analyze_complexity(tree)
            documentation_score, doc_metrics, doc_suggestions = self._analyze_documentation(tree)
            formatting_score, format_metrics, format_suggestions = self._analyze_formatting(lines)
            structure_score, structure_metrics, structure_suggestions = self._analyze_structure(tree, content)
            
            # Calculate overall score (weighted average)
            weights = {
                'naming': 0.25,
                'complexity': 0.25,
                'documentation': 0.20,
                'formatting': 0.15,
                'structure': 0.15
            }
            
            overall_score = (
                naming_score * weights['naming'] +
                complexity_score * weights['complexity'] +
                documentation_score * weights['documentation'] +
                formatting_score * weights['formatting'] +
                structure_score * weights['structure']
            )
            
            results["scores"] = {
                "overall": round(overall_score, 2),
                "naming": round(naming_score, 2),
                "complexity": round(complexity_score, 2),
                "documentation": round(documentation_score, 2),
                "formatting": round(formatting_score, 2),
                "structure": round(structure_score, 2)
            }
            
            results["metrics"] = {
                "naming": naming_metrics,
                "complexity": complexity_metrics,
                "documentation": doc_metrics,
                "formatting": format_metrics,
                "structure": structure_metrics
            }
            
            # Combine all suggestions and sort by priority
            all_suggestions = (
                naming_suggestions + 
                complexity_suggestions + 
                doc_suggestions + 
                format_suggestions + 
                structure_suggestions
            )
            
            # Sort by priority (high, medium, low)
            priority_order = {'high': 0, 'medium': 1, 'low': 2}
            results["suggestions"] = sorted(
                all_suggestions, 
                key=lambda x: priority_order.get(x['priority'], 3)
            )
            
        except SyntaxError as e:
            results["error"] = f"Syntax error: {str(e)}"
            results["scores"] = {"overall": 0}
        except Exception as e:
            results["error"] = f"Analysis error: {str(e)}"
            results["scores"] = {"overall": 0}
        
        return results
    
    def _analyze_naming(self, tree: ast.AST, content: str) -> Tuple[float, Dict, List]:
        """Analyze variable and function naming quality"""
        score = 100.0
        metrics = {
            "functions_analyzed": 0,
            "variables_analyzed": 0,
            "good_names": 0,
            "poor_names": 0,
            "single_char_vars": 0,
            "abbreviations": 0
        }
        suggestions = []
        
        # Analyze function names
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                metrics["functions_analyzed"] += 1
                func_name = node.name
                
                # Skip magic methods and private methods
                if func_name.startswith('__') and func_name.endswith('__'):
                    continue
                
                # Check function name quality
                if len(func_name) < 3 and not func_name.startswith('_'):
                    metrics["poor_names"] += 1
                    score -= 5
                    suggestions.append({
                        "category": "naming",
                        "priority": "high",
                        "line": node.lineno,
                        "issue": f"Function name '{func_name}' is too short",
                        "suggestion": "Use descriptive function names that explain what the function does",
                        "example": f"Consider: 'calculate_{func_name}' or 'process_{func_name}'"
                    })
                elif any(bad in func_name.lower() for bad in self.naming_keywords['bad']):
                    metrics["poor_names"] += 1
                    score -= 3
                    suggestions.append({
                        "category": "naming",
                        "priority": "medium",
                        "line": node.lineno,
                        "issue": f"Function name '{func_name}' uses generic term",
                        "suggestion": "Use more specific, descriptive names that indicate the function's purpose",
                        "example": "Replace generic terms like 'data', 'func', 'handle' with specific ones"
                    })
                elif not re.match(r'^[a-z_][a-z0-9_]*$', func_name):
                    score -= 2
                    suggestions.append({
                        "category": "naming",
                        "priority": "low",
                        "line": node.lineno,
                        "issue": f"Function name '{func_name}' doesn't follow snake_case convention",
                        "suggestion": "Use snake_case for function names (lowercase with underscores)",
                        "example": f"Consider: '{self._to_snake_case(func_name)}'"
                    })
                else:
                    metrics["good_names"] += 1
            
            # Analyze variable names
            elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
                metrics["variables_analyzed"] += 1
                var_name = node.id
                
                # Skip private variables
                if var_name.startswith('_'):
                    continue
                
                if len(var_name) == 1:
                    metrics["single_char_vars"] += 1
                    # Allow single chars in list comprehensions and common patterns
                    if not self._in_comprehension(node):
                        score -= 1
                        if hasattr(node, 'lineno'):
                            suggestions.append({
                                "category": "naming",
                                "priority": "medium",
                                "line": node.lineno,
                                "issue": f"Single-character variable name '{var_name}'",
                                "suggestion": "Use descriptive variable names except in loops or comprehensions",
                                "example": f"Consider a more descriptive name based on what '{var_name}' represents"
                            })
                elif len(var_name) < 3:
                    metrics["poor_names"] += 1
                    score -= 1
                else:
                    metrics["good_names"] += 1
        
        # Ensure score doesn't go below 0
        score = max(0, score)
        
        return score, metrics, suggestions
    
    def _analyze_complexity(self, tree: ast.AST) -> Tuple[float, Dict, List]:
        """Analyze code complexity"""
        score = 100.0
        metrics = {
            "functions": 0,
            "avg_cyclomatic_complexity": 0,
            "max_nesting_depth": 0,
            "long_functions": 0,
            "complex_functions": 0
        }
        suggestions = []
        
        complexities = []
        max_depth = 0
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                metrics["functions"] += 1
                
                # Calculate cyclomatic complexity
                complexity = self._calculate_cyclomatic_complexity(node)
                complexities.append(complexity)
                
                if complexity > 10:
                    metrics["complex_functions"] += 1
                    score -= 8
                    suggestions.append({
                        "category": "complexity",
                        "priority": "high",
                        "line": node.lineno,
                        "issue": f"Function '{node.name}' has high cyclomatic complexity ({complexity})",
                        "suggestion": "Break down into smaller functions or simplify logic",
                        "example": "Consider extracting complex conditional logic into separate functions"
                    })
                elif complexity > 7:
                    score -= 4
                    suggestions.append({
                        "category": "complexity",
                        "priority": "medium",
                        "line": node.lineno,
                        "issue": f"Function '{node.name}' has moderate complexity ({complexity})",
                        "suggestion": "Consider refactoring to reduce complexity",
                        "example": "Look for opportunities to extract helper functions"
                    })
                
                # Check function length
                if hasattr(node, 'end_lineno'):
                    func_lines = node.end_lineno - node.lineno
                    if func_lines > 50:
                        metrics["long_functions"] += 1
                        score -= 6
                        suggestions.append({
                            "category": "complexity",
                            "priority": "high",
                            "line": node.lineno,
                            "issue": f"Function '{node.name}' is too long ({func_lines} lines)",
                            "suggestion": "Break down into smaller, focused functions",
                            "example": "Functions should ideally be under 50 lines"
                        })
                
                # Check nesting depth
                depth = self._get_max_nesting_depth(node)
                max_depth = max(max_depth, depth)
                
                if depth > 4:
                    score -= 7
                    suggestions.append({
                        "category": "complexity",
                        "priority": "high",
                        "line": node.lineno,
                        "issue": f"Function '{node.name}' has deep nesting (depth: {depth})",
                        "suggestion": "Reduce nesting by using early returns or extracting nested logic",
                        "example": "Consider using guard clauses and early returns"
                    })
                elif depth > 3:
                    score -= 3
        
        if complexities:
            metrics["avg_cyclomatic_complexity"] = round(sum(complexities) / len(complexities), 2)
        metrics["max_nesting_depth"] = max_depth
        
        score = max(0, score)
        return score, metrics, suggestions
    
    def _analyze_documentation(self, tree: ast.AST) -> Tuple[float, Dict, List]:
        """Analyze documentation quality"""
        score = 100.0
        metrics = {
            "functions": 0,
            "documented_functions": 0,
            "classes": 0,
            "documented_classes": 0,
            "module_docstring": False,
            "avg_docstring_length": 0
        }
        suggestions = []
        
        docstring_lengths = []
        
        # Check module docstring
        module_docstring = ast.get_docstring(tree)
        if module_docstring:
            metrics["module_docstring"] = True
            docstring_lengths.append(len(module_docstring))
        else:
            score -= 10
            suggestions.append({
                "category": "documentation",
                "priority": "medium",
                "line": 1,
                "issue": "Missing module-level docstring",
                "suggestion": "Add a docstring at the top of the file describing its purpose",
                "example": '"""\\nModule description here\\n"""'
            })
        
        # Check function and class docstrings
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Skip private and magic methods
                if node.name.startswith('_'):
                    continue
                
                metrics["functions"] += 1
                docstring = ast.get_docstring(node)
                
                if docstring:
                    metrics["documented_functions"] += 1
                    docstring_lengths.append(len(docstring))
                    
                    # Check docstring quality
                    if len(docstring) < 20:
                        score -= 3
                        suggestions.append({
                            "category": "documentation",
                            "priority": "low",
                            "line": node.lineno,
                            "issue": f"Function '{node.name}' has minimal docstring",
                            "suggestion": "Expand docstring to include parameters, returns, and examples",
                            "example": "Include Args, Returns, and Raises sections"
                        })
                    
                    # Check for parameter documentation
                    if node.args.args and 'Args:' not in docstring and 'Parameters:' not in docstring:
                        score -= 2
                        suggestions.append({
                            "category": "documentation",
                            "priority": "low",
                            "line": node.lineno,
                            "issue": f"Function '{node.name}' docstring missing parameter documentation",
                            "suggestion": "Document function parameters in the docstring",
                            "example": "Add an 'Args:' section describing each parameter"
                        })
                else:
                    score -= 8
                    suggestions.append({
                        "category": "documentation",
                        "priority": "high",
                        "line": node.lineno,
                        "issue": f"Function '{node.name}' is missing docstring",
                        "suggestion": "Add a docstring describing what the function does",
                        "example": f'def {node.name}(...):\\n    """\\n    Description of what this function does\\n    """'
                    })
            
            elif isinstance(node, ast.ClassDef):
                metrics["classes"] += 1
                docstring = ast.get_docstring(node)
                
                if docstring:
                    metrics["documented_classes"] += 1
                    docstring_lengths.append(len(docstring))
                else:
                    score -= 10
                    suggestions.append({
                        "category": "documentation",
                        "priority": "high",
                        "line": node.lineno,
                        "issue": f"Class '{node.name}' is missing docstring",
                        "suggestion": "Add a docstring describing the class purpose and usage",
                        "example": f'class {node.name}:\\n    """\\n    Description of this class\\n    """'
                    })
        
        if docstring_lengths:
            metrics["avg_docstring_length"] = round(sum(docstring_lengths) / len(docstring_lengths), 2)
        
        score = max(0, score)
        return score, metrics, suggestions
    
    def _analyze_formatting(self, lines: List[str]) -> Tuple[float, Dict, List]:
        """Analyze code formatting"""
        score = 100.0
        metrics = {
            "total_lines": len(lines),
            "long_lines": 0,
            "trailing_whitespace": 0,
            "blank_lines": 0,
            "inconsistent_indentation": 0
        }
        suggestions = []
        
        indent_levels = []
        
        for i, line in enumerate(lines, 1):
            # Check line length
            if len(line) > 88:  # PEP 8 recommends 79, but 88 is Black's default
                metrics["long_lines"] += 1
                if len(line) > 120:
                    score -= 2
                    suggestions.append({
                        "category": "formatting",
                        "priority": "medium",
                        "line": i,
                        "issue": f"Line exceeds 120 characters ({len(line)} chars)",
                        "suggestion": "Break long lines into multiple lines",
                        "example": "Use line continuation or break into multiple statements"
                    })
                elif metrics["long_lines"] % 5 == 0:  # Report every 5th occurrence
                    score -= 0.5
            
            # Check trailing whitespace
            if line.rstrip() != line and line.strip():
                metrics["trailing_whitespace"] += 1
                if metrics["trailing_whitespace"] == 1:
                    score -= 1
                    suggestions.append({
                        "category": "formatting",
                        "priority": "low",
                        "line": i,
                        "issue": "Line has trailing whitespace",
                        "suggestion": "Remove trailing whitespace from lines",
                        "example": "Use your editor's trim whitespace feature"
                    })
            
            # Count blank lines
            if not line.strip():
                metrics["blank_lines"] += 1
            
            # Check indentation consistency
            if line.strip() and line[0] in (' ', '\t'):
                indent = len(line) - len(line.lstrip())
                if '\t' in line[:indent]:
                    metrics["inconsistent_indentation"] += 1
                    if metrics["inconsistent_indentation"] == 1:
                        score -= 5
                        suggestions.append({
                            "category": "formatting",
                            "priority": "high",
                            "line": i,
                            "issue": "File uses tabs for indentation",
                            "suggestion": "Use spaces instead of tabs (PEP 8)",
                            "example": "Configure your editor to use 4 spaces for indentation"
                        })
                else:
                    indent_levels.append(indent)
        
        # Check for consistent indentation levels
        if indent_levels:
            unique_indents = set(indent_levels)
            if len(unique_indents) > 1:
                # Check if indents are multiples of 4
                non_standard = [ind for ind in unique_indents if ind % 4 != 0]
                if non_standard:
                    score -= 3
                    suggestions.append({
                        "category": "formatting",
                        "priority": "medium",
                        "line": 0,
                        "issue": "Inconsistent indentation levels detected",
                        "suggestion": "Use consistent 4-space indentation",
                        "example": "All indentation should be in multiples of 4 spaces"
                    })
        
        score = max(0, score)
        return score, metrics, suggestions
    
    def _analyze_structure(self, tree: ast.AST, content: str) -> Tuple[float, Dict, List]:
        """Analyze code structure and organization"""
        score = 100.0
        metrics = {
            "imports": 0,
            "functions": 0,
            "classes": 0,
            "global_variables": 0,
            "import_organization": "good"
        }
        suggestions = []
        
        imports = []
        import_lines = []
        
        # Analyze imports
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                metrics["imports"] += 1
                if hasattr(node, 'lineno'):
                    import_lines.append(node.lineno)
                    imports.append(node)
        
        # Check if imports are at the top
        if import_lines:
            # Find first non-comment, non-blank line
            lines = content.split('\n')
            first_code_line = 0
            for i, line in enumerate(lines, 1):
                stripped = line.strip()
                if stripped and not stripped.startswith('#') and not stripped.startswith('"""') and not stripped.startswith("'''"):
                    first_code_line = i
                    break
            
            if import_lines and min(import_lines) > first_code_line + 5:
                score -= 5
                metrics["import_organization"] = "poor"
                suggestions.append({
                    "category": "structure",
                    "priority": "medium",
                    "line": min(import_lines),
                    "issue": "Imports are not at the top of the file",
                    "suggestion": "Move all imports to the top of the file after the module docstring",
                    "example": "Follow PEP 8: imports should be at the top"
                })
        
        # Check for global variables
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                # Check if it's at module level
                if isinstance(node.col_offset, int) and node.col_offset == 0:
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            # Skip constants (all caps)
                            if not target.id.isupper():
                                metrics["global_variables"] += 1
        
        if metrics["global_variables"] > 5:
            score -= 8
            suggestions.append({
                "category": "structure",
                "priority": "high",
                "line": 0,
                "issue": f"Too many global variables ({metrics['global_variables']})",
                "suggestion": "Reduce global variables by using classes or function parameters",
                "example": "Consider encapsulating state in classes or passing as parameters"
            })
        elif metrics["global_variables"] > 2:
            score -= 3
            suggestions.append({
                "category": "structure",
                "priority": "medium",
                "line": 0,
                "issue": f"Multiple global variables detected ({metrics['global_variables']})",
                "suggestion": "Consider reducing global state",
                "example": "Use constants (UPPER_CASE) or encapsulate in classes"
            })
        
        # Count classes and functions
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                metrics["classes"] += 1
            elif isinstance(node, ast.FunctionDef):
                if node.col_offset == 0:  # Module-level function
                    metrics["functions"] += 1
        
        # Check for proper organization (classes before functions at module level)
        # This is a simple heuristic
        if metrics["classes"] > 0 and metrics["functions"] > 3:
            score -= 2
            suggestions.append({
                "category": "structure",
                "priority": "low",
                "line": 0,
                "issue": "Consider organizing related functions into classes",
                "suggestion": "Group related functions into classes for better organization",
                "example": "If functions share state or purpose, make them class methods"
            })
        
        score = max(0, score)
        return score, metrics, suggestions
    
    def _calculate_cyclomatic_complexity(self, node: ast.AST) -> int:
        """Calculate cyclomatic complexity of a function"""
        complexity = 1  # Base complexity
        
        for child in ast.walk(node):
            # Add 1 for each decision point
            if isinstance(child, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                # Add for each boolean operator (and, or)
                complexity += len(child.values) - 1
            elif isinstance(child, (ast.ListComp, ast.DictComp, ast.SetComp, ast.GeneratorExp)):
                complexity += 1
        
        return complexity
    
    def _get_max_nesting_depth(self, node: ast.AST, current_depth: int = 0) -> int:
        """Calculate maximum nesting depth"""
        max_depth = current_depth
        
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.If, ast.For, ast.While, ast.With, ast.Try)):
                child_depth = self._get_max_nesting_depth(child, current_depth + 1)
                max_depth = max(max_depth, child_depth)
            else:
                child_depth = self._get_max_nesting_depth(child, current_depth)
                max_depth = max(max_depth, child_depth)
        
        return max_depth
    
    def _in_comprehension(self, node: ast.Name) -> bool:
        """Check if a node is inside a comprehension (simplified check)"""
        # This is a simplified check - in practice, you'd walk up the AST
        return False
    
    def _to_snake_case(self, name: str) -> str:
        """Convert a name to snake_case"""
        # Simple conversion
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
    
    def analyze_directory(self, directory: str, extensions: List[str] = ['.py']) -> Dict:
        """
        Analyze all files in a directory.
        
        Args:
            directory: Path to the directory to analyze
            extensions: List of file extensions to analyze
            
        Returns:
            Dictionary containing analysis results
            
        Raises:
            ValueError: If directory parameter is invalid
            IOError: If directory cannot be accessed
        """
        if not directory:
            raise ValueError("Directory path cannot be empty")
        
        if not isinstance(directory, str):
            raise ValueError(f"Directory must be a string, got {type(directory).__name__}")
        
        if not os.path.exists(directory):
            raise IOError(f"Directory does not exist: {directory}")
        
        if not os.path.isdir(directory):
            raise IOError(f"Path is not a directory: {directory}")
        
        results = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "directory": directory,
            "files_analyzed": [],
            "errors": [],
            "summary": {
                "total_files": 0,
                "avg_overall_score": 0,
                "avg_scores_by_category": {},
                "total_suggestions": 0,
                "suggestions_by_priority": {"high": 0, "medium": 0, "low": 0}
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
                            analysis = self.analyze_file(filepath)
                            results["files_analyzed"].append(analysis)
                            results["summary"]["total_files"] += 1
                            results["summary"]["total_suggestions"] += len(analysis["suggestions"])
                            
                            # Count suggestions by priority
                            for suggestion in analysis["suggestions"]:
                                priority = suggestion.get("priority", "low")
                                results["summary"]["suggestions_by_priority"][priority] += 1
                            
                        except Exception as e:
                            results["errors"].append({
                                "file": filepath,
                                "error": str(e)
                            })
        except OSError as e:
            raise IOError(f"Error walking directory '{directory}': {e}")
        
        # Calculate averages
        if results["files_analyzed"]:
            overall_scores = [f["scores"]["overall"] for f in results["files_analyzed"] if "overall" in f.get("scores", {})]
            if overall_scores:
                results["summary"]["avg_overall_score"] = round(sum(overall_scores) / len(overall_scores), 2)
            
            # Calculate category averages
            categories = ["naming", "complexity", "documentation", "formatting", "structure"]
            for category in categories:
                scores = [f["scores"][category] for f in results["files_analyzed"] 
                         if category in f.get("scores", {})]
                if scores:
                    results["summary"]["avg_scores_by_category"][category] = round(sum(scores) / len(scores), 2)
        
        return results
    
    def _get_grade_info(self, score: float) -> Tuple[str, str]:
        """Get grade and emoji for a score"""
        if score >= 90:
            return "A (Excellent)", "🌟"
        elif score >= 80:
            return "B (Good)", "✅"
        elif score >= 70:
            return "C (Fair)", "⚠️"
        elif score >= 60:
            return "D (Needs Improvement)", "⚠️"
        else:
            return "F (Poor)", "❌"
    
    def _generate_directory_report(self, analysis_results: Dict) -> List[str]:
        """Generate report for directory analysis"""
        report = []
        report.append("# Code Readability Report")
        report.append(f"\n**Generated:** {analysis_results['timestamp']}")
        report.append(f"**Directory:** {analysis_results['directory']}")
        
        summary = analysis_results["summary"]
        report.append("\n## Summary")
        report.append(f"- **Files Analyzed:** {summary['total_files']}")
        report.append(f"- **Average Overall Score:** {summary['avg_overall_score']}/100")
        report.append(f"- **Total Suggestions:** {summary['total_suggestions']}")
        
        grade, emoji = self._get_grade_info(summary['avg_overall_score'])
        report.append(f"\n**Overall Grade:** {emoji} {grade}")
        
        if summary["avg_scores_by_category"]:
            report.append("\n## Category Scores")
            for category, score in sorted(summary["avg_scores_by_category"].items(), 
                                         key=lambda x: x[1], reverse=True):
                bar = self._generate_score_bar(score)
                report.append(f"- **{category.title()}:** {score}/100 {bar}")
        
        report.append("\n## Suggestions by Priority")
        priorities = summary["suggestions_by_priority"]
        report.append(f"- 🔴 **High Priority:** {priorities['high']} issues")
        report.append(f"- 🟡 **Medium Priority:** {priorities['medium']} issues")
        report.append(f"- 🟢 **Low Priority:** {priorities['low']} issues")
        
        if analysis_results["files_analyzed"]:
            report.append("\n## File Analysis")
            for file_analysis in sorted(analysis_results["files_analyzed"], 
                                       key=lambda x: x["scores"]["overall"]):
                report.append(f"\n### {os.path.basename(file_analysis['file'])}")
                report.append(f"**Score:** {file_analysis['scores']['overall']}/100")
                
                if file_analysis["suggestions"]:
                    report.append(f"\n**Top Issues:**")
                    for suggestion in file_analysis["suggestions"][:3]:
                        priority_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}
                        emoji = priority_emoji.get(suggestion["priority"], "⚪")
                        report.append(f"- {emoji} Line {suggestion['line']}: {suggestion['issue']}")
        
        return report
    
    def _generate_single_file_report(self, analysis_results: Dict) -> List[str]:
        """Generate report for single file analysis"""
        report = []
        report.append(f"# Readability Report: {os.path.basename(analysis_results['file'])}")
        report.append(f"\n**Generated:** {analysis_results['timestamp']}")
        report.append(f"**File:** {analysis_results['file']}")
        
        overall_score = analysis_results["scores"]["overall"]
        report.append(f"\n## Overall Score: {overall_score}/100")
        
        grade, emoji = self._get_grade_info(overall_score)
        report.append(f"**Grade:** {grade} {emoji}")
        
        report.append("\n## Category Scores")
        scores = analysis_results["scores"]
        for category in ["naming", "complexity", "documentation", "formatting", "structure"]:
            if category in scores:
                score = scores[category]
                bar = self._generate_score_bar(score)
                report.append(f"- **{category.title()}:** {score}/100 {bar}")
        
        report.append("\n## Metrics")
        for category, metrics in analysis_results["metrics"].items():
            report.append(f"\n### {category.title()}")
            for metric, value in metrics.items():
                formatted_metric = metric.replace('_', ' ').title()
                report.append(f"- {formatted_metric}: {value}")
        
        if analysis_results["suggestions"]:
            self._add_suggestions_section(report, analysis_results["suggestions"])
        
        return report
    
    def _add_suggestions_section(self, report: List[str], suggestions: List[Dict]):
        """Add suggestions section to report"""
        report.append("\n## Improvement Suggestions")
        
        high_priority = [s for s in suggestions if s["priority"] == "high"]
        medium_priority = [s for s in suggestions if s["priority"] == "medium"]
        low_priority = [s for s in suggestions if s["priority"] == "low"]
        
        if high_priority:
            report.append("\n### 🔴 High Priority")
            for s in high_priority[:10]:
                report.append(f"\n**Line {s['line']}:** {s['issue']}")
                report.append(f"- *Suggestion:* {s['suggestion']}")
                if 'example' in s:
                    report.append(f"- *Example:* `{s['example']}`")
        
        if medium_priority:
            report.append("\n### 🟡 Medium Priority")
            for s in medium_priority[:10]:
                report.append(f"\n**Line {s['line']}:** {s['issue']}")
                report.append(f"- *Suggestion:* {s['suggestion']}")
        
        if low_priority:
            report.append("\n### 🟢 Low Priority")
            for s in low_priority[:5]:
                report.append(f"\n**Line {s['line']}:** {s['issue']}")
                report.append(f"- *Suggestion:* {s['suggestion']}")

    def generate_markdown_report(self, analysis_results: Dict) -> str:
        """Generate a markdown report from analysis results"""
        is_directory = "directory" in analysis_results
        
        if is_directory:
            report = self._generate_directory_report(analysis_results)
        else:
            report = self._generate_single_file_report(analysis_results)
        
        if "errors" in analysis_results and analysis_results["errors"]:
            report.append("\n## Errors")
            for error in analysis_results["errors"]:
                report.append(f"- **{error['file']}:** {error['error']}")
        
        return '\n'.join(report)
    
    def _generate_score_bar(self, score: float) -> str:
        """Generate a visual score bar"""
        filled = int(score / 10)
        empty = 10 - filled
        return '█' * filled + '░' * empty


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Code Readability Scorer - Analyze code readability and get improvement suggestions',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze a single file
  %(prog)s -f myfile.py
  
  # Analyze a directory
  %(prog)s -d ./src
  
  # Generate markdown report
  %(prog)s -d ./src --format markdown -o report.md
  
  # Output JSON for further processing
  %(prog)s -f myfile.py --format json
        """
    )
    
    parser.add_argument('-f', '--file', help='Single file to analyze')
    parser.add_argument('-d', '--directory', help='Directory to analyze (default: current directory)')
    parser.add_argument('-o', '--output', help='Output file for report (default: stdout)')
    parser.add_argument('--format', choices=['json', 'markdown'], default='markdown',
                       help='Output format (default: markdown)')
    parser.add_argument('--min-score', type=float, help='Minimum acceptable score (exit 1 if below)')
    
    args = parser.parse_args()
    
    scorer = ReadabilityScorer()
    
    try:
        if args.file:
            # Analyze single file
            results = scorer.analyze_file(args.file)
        elif args.directory:
            # Analyze directory
            results = scorer.analyze_directory(args.directory)
        else:
            # Default to current directory
            results = scorer.analyze_directory('.')
        
        # Generate output
        if args.format == 'json':
            output = json.dumps(results, indent=2)
        else:
            output = scorer.generate_markdown_report(results)
        
        # Write output
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(output)
            print(f"Report saved to: {args.output}")
        else:
            print(output)
        
        # Check minimum score
        if args.min_score:
            if args.file:
                score = results["scores"]["overall"]
            else:
                score = results["summary"]["avg_overall_score"]
            
            if score < args.min_score:
                print(f"\n❌ Score {score} is below minimum {args.min_score}", file=sys.stderr)
                sys.exit(1)
            else:
                print(f"\n✅ Score {score} meets minimum {args.min_score}")
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
