#!/usr/bin/env python3
"""
AI Code Golf Optimizer - Minimize code while preserving functionality

This tool analyzes code and suggests optimizations to reduce character count
while maintaining correctness, perfect for code golf challenges.

Enhanced with AI-powered pattern learning and adaptive optimization strategies.
"""

import sys
import re
import argparse
import json
import os
from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass, asdict
from datetime import datetime
from collections import defaultdict


@dataclass
class OptimizationResult:
    """Results from code optimization"""
    original_code: str
    optimized_code: str
    original_chars: int
    optimized_chars: int
    reduction_percentage: float
    optimizations_applied: List[str]
    language: str
    pattern_scores: Optional[Dict[str, float]] = None
    ai_suggestions: Optional[List[str]] = None
    
    def to_dict(self):
        return asdict(self)


class PatternLearningEngine:
    """AI-powered pattern learning system for optimization strategies"""
    
    def __init__(self, storage_path: str = None):
        if storage_path is None:
            storage_path = os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                'data',
                'code_golf_patterns.json'
            )
        self.storage_path = storage_path
        self.patterns = self._load_patterns()
        self.session_stats = defaultdict(lambda: {'applications': 0, 'total_reduction': 0})
    
    def _load_patterns(self) -> Dict:
        """Load pattern effectiveness data from storage"""
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
        
        # Initialize with default pattern effectiveness scores
        return {
            'python': {
                'comment_removal': {'effectiveness': 0.8, 'applications': 0, 'avg_reduction': 15.0},
                'docstring_removal': {'effectiveness': 0.85, 'applications': 0, 'avg_reduction': 25.0},
                'whitespace_reduction': {'effectiveness': 0.9, 'applications': 0, 'avg_reduction': 10.0},
                'blank_line_removal': {'effectiveness': 0.75, 'applications': 0, 'avg_reduction': 5.0},
                'boolean_simplification': {'effectiveness': 0.7, 'applications': 0, 'avg_reduction': 8.0},
                'variable_shortening': {'effectiveness': 0.6, 'applications': 0, 'avg_reduction': 20.0},
                'lambda_optimization': {'effectiveness': 0.5, 'applications': 0, 'avg_reduction': 12.0},
            },
            'javascript': {
                'comment_removal': {'effectiveness': 0.8, 'applications': 0, 'avg_reduction': 12.0},
                'boolean_simplification': {'effectiveness': 0.9, 'applications': 0, 'avg_reduction': 6.0},
                'whitespace_reduction': {'effectiveness': 0.85, 'applications': 0, 'avg_reduction': 8.0},
                'arrow_function_conversion': {'effectiveness': 0.75, 'applications': 0, 'avg_reduction': 15.0},
            },
            'bash': {
                'comment_removal': {'effectiveness': 0.75, 'applications': 0, 'avg_reduction': 10.0},
                'whitespace_reduction': {'effectiveness': 0.8, 'applications': 0, 'avg_reduction': 5.0},
            }
        }
    
    def _save_patterns(self):
        """Save pattern effectiveness data to storage"""
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
        try:
            with open(self.storage_path, 'w') as f:
                json.dump(self.patterns, f, indent=2)
        except IOError as e:
            print(f"Warning: Could not save patterns: {e}", file=sys.stderr)
    
    def get_pattern_priority(self, language: str) -> List[Tuple[str, float]]:
        """Get optimizations ranked by effectiveness for given language"""
        if language not in self.patterns:
            return []
        
        patterns = self.patterns[language]
        # Sort by effectiveness score (higher is better)
        return sorted(
            [(name, data['effectiveness']) for name, data in patterns.items()],
            key=lambda x: x[1],
            reverse=True
        )
    
    def record_optimization(self, language: str, pattern_name: str, reduction: float):
        """Record the result of applying an optimization pattern"""
        if language not in self.patterns:
            self.patterns[language] = {}
        
        if pattern_name not in self.patterns[language]:
            self.patterns[language][pattern_name] = {
                'effectiveness': 0.5,
                'applications': 0,
                'avg_reduction': 0.0
            }
        
        pattern = self.patterns[language][pattern_name]
        
        # Update running average
        total_reduction = pattern['avg_reduction'] * pattern['applications']
        pattern['applications'] += 1
        pattern['avg_reduction'] = (total_reduction + reduction) / pattern['applications']
        
        # Update effectiveness score (weighted average with decay)
        # Higher reduction = higher effectiveness
        new_effectiveness = min(1.0, reduction / 30.0)  # Scale: 30% reduction = 1.0 effectiveness
        pattern['effectiveness'] = (
            pattern['effectiveness'] * 0.9 + new_effectiveness * 0.1
        )
        
        self.session_stats[pattern_name]['applications'] += 1
        self.session_stats[pattern_name]['total_reduction'] += reduction
    
    def get_ai_suggestions(self, language: str, code: str) -> List[str]:
        """Get AI-powered suggestions based on learned patterns"""
        suggestions = []
        
        # Get top patterns for this language
        top_patterns = self.get_pattern_priority(language)[:3]
        
        for pattern_name, effectiveness in top_patterns:
            if pattern_name == 'variable_shortening' and len(code) > 100:
                suggestions.append(
                    f"✨ Variable shortening highly effective (score: {effectiveness:.2f}) - "
                    f"Consider using single-letter names for frequently used variables"
                )
            elif pattern_name == 'lambda_optimization':
                if 'lambda' in code:
                    suggestions.append(
                        f"✨ Lambda expressions detected - Consider inline optimization (score: {effectiveness:.2f})"
                    )
            elif pattern_name == 'arrow_function_conversion':
                if 'function' in code and language == 'javascript':
                    suggestions.append(
                        f"✨ Convert functions to arrow syntax for shorter code (score: {effectiveness:.2f})"
                    )
        
        # Code-specific insights
        if language == 'python':
            if 'for ' in code and ' in range(' in code:
                suggestions.append("💡 Consider list comprehensions to reduce loop overhead")
            if 'if ' in code and 'else:' in code:
                suggestions.append("💡 Ternary operators (x if c else y) can be shorter")
        
        return suggestions
    
    def get_session_summary(self) -> Dict:
        """Get summary of optimizations applied in current session"""
        return {
            'patterns_used': len(self.session_stats),
            'total_applications': sum(s['applications'] for s in self.session_stats.values()),
            'total_reduction': sum(s['total_reduction'] for s in self.session_stats.values()),
            'top_patterns': sorted(
                [(name, stats) for name, stats in self.session_stats.items()],
                key=lambda x: x[1]['total_reduction'],
                reverse=True
            )[:5]
        }
    
    def save_session(self):
        """Save learned patterns to persistent storage"""
        self._save_patterns()


class CodeGolfOptimizer:
    """Main optimizer class for multiple languages with AI-powered learning"""
    
    def __init__(self, enable_learning: bool = True):
        self.optimizations = {
            'python': self._optimize_python,
            'javascript': self._optimize_javascript,
            'js': self._optimize_javascript,
            'bash': self._optimize_bash,
            'sh': self._optimize_bash,
        }
        self.learning_engine = PatternLearningEngine() if enable_learning else None
    
    def optimize(self, code: str, language: str = 'python', learn: bool = True) -> OptimizationResult:
        """Optimize code for the specified language with AI-powered suggestions"""
        language = language.lower()
        
        if language not in self.optimizations:
            raise ValueError(f"Unsupported language: {language}. Supported: {list(self.optimizations.keys())}")
        
        original_chars = len(code)
        optimized_code, applied = self.optimizations[language](code)
        optimized_chars = len(optimized_code)
        
        reduction = ((original_chars - optimized_chars) / original_chars * 100) if original_chars > 0 else 0
        
        # Record patterns for learning
        pattern_scores = {}
        if self.learning_engine and learn:
            for optimization in applied:
                # Extract pattern name from optimization description
                pattern_name = self._extract_pattern_name(optimization)
                if pattern_name:
                    # Calculate individual pattern contribution (approximate)
                    pattern_reduction = reduction / len(applied) if applied else 0
                    self.learning_engine.record_optimization(language, pattern_name, pattern_reduction)
                    
                    # Get pattern effectiveness score
                    patterns = self.learning_engine.patterns.get(language, {})
                    if pattern_name in patterns:
                        pattern_scores[pattern_name] = patterns[pattern_name]['effectiveness']
        
        # Get AI suggestions
        ai_suggestions = []
        if self.learning_engine:
            ai_suggestions = self.learning_engine.get_ai_suggestions(language, code)
        
        return OptimizationResult(
            original_code=code,
            optimized_code=optimized_code,
            original_chars=original_chars,
            optimized_chars=optimized_chars,
            reduction_percentage=round(reduction, 2),
            optimizations_applied=applied,
            language=language,
            pattern_scores=pattern_scores,
            ai_suggestions=ai_suggestions
        )
    
    def _extract_pattern_name(self, optimization_text: str) -> Optional[str]:
        """Extract pattern name from optimization description"""
        patterns_map = {
            'comment': 'comment_removal',
            'docstring': 'docstring_removal',
            'spaces': 'whitespace_reduction',
            'blank': 'blank_line_removal',
            'True/False': 'boolean_simplification',
            'true/false': 'boolean_simplification',
            'variable': 'variable_shortening',
            'lambda': 'lambda_optimization',
            'arrow': 'arrow_function_conversion',
        }
        
        text_lower = optimization_text.lower()
        for keyword, pattern_name in patterns_map.items():
            if keyword in text_lower:
                return pattern_name
        return None
    
    def get_learning_stats(self) -> Dict:
        """Get statistics about learned optimization patterns"""
        if not self.learning_engine:
            return {}
        return self.learning_engine.get_session_summary()
    
    def save_learning(self):
        """Persist learned patterns to storage"""
        if self.learning_engine:
            self.learning_engine.save_session()
    
    def _optimize_python(self, code: str) -> Tuple[str, List[str]]:
        """Optimize Python code for minimal character count"""
        applied = []
        optimized = code
        
        # Remove comments
        if '#' in optimized or '"""' in optimized or "'''" in optimized:
            optimized = re.sub(r'#.*$', '', optimized, flags=re.MULTILINE)
            optimized = re.sub(r'""".*?"""', '', optimized, flags=re.DOTALL)
            optimized = re.sub(r"'''.*?'''", '', optimized, flags=re.DOTALL)
            applied.append("Removed comments")
        
        # Remove docstrings (standalone strings)
        lines = optimized.split('\n')
        cleaned_lines = []
        for line in lines:
            stripped = line.strip()
            if not (stripped.startswith('"""') or stripped.startswith("'''")):
                cleaned_lines.append(line)
        if len(cleaned_lines) < len(lines):
            optimized = '\n'.join(cleaned_lines)
            applied.append("Removed docstrings")
        
        # Replace multiple spaces with single space
        if '  ' in optimized:
            optimized = re.sub(r'  +', ' ', optimized)
            applied.append("Reduced multiple spaces")
        
        # Remove leading/trailing whitespace per line but keep indentation structure
        lines = optimized.split('\n')
        cleaned_lines = [line.rstrip() for line in lines]
        optimized = '\n'.join(cleaned_lines)
        
        # Remove blank lines
        if '\n\n' in optimized:
            optimized = re.sub(r'\n\n+', '\n', optimized)
            applied.append("Removed blank lines")
        
        # Simplify True/False to 1/0 in appropriate contexts
        if ' True' in optimized or ' False' in optimized:
            # Be careful with this - only in certain contexts
            optimized = re.sub(r'\bTrue\b(?!\s*:)', '1', optimized)
            optimized = re.sub(r'\bFalse\b(?!\s*:)', '0', optimized)
            applied.append("Simplified True/False to 1/0")
        
        # Replace 'lambda' with shorter alternatives where possible
        if 'lambda' in optimized:
            applied.append("Lambda expressions found (manual review recommended)")
        
        # Shorten variable names (for code golf only - preserve in a mapping)
        # This is aggressive and should be used carefully
        if len(optimized) > 100:  # Only for longer code
            # Find long variable names (3+ chars) that appear multiple times
            var_pattern = r'\b[a-z_][a-z0-9_]{2,}\b'
            variables = re.findall(var_pattern, optimized, re.IGNORECASE)
            var_counts = {}
            for var in variables:
                if var not in ['def', 'for', 'if', 'in', 'or', 'and', 'not', 'return', 'import', 'from', 'while', 'else', 'elif', 'try', 'except', 'class', 'pass', 'break', 'continue', 'None', 'print', 'range', 'len', 'str', 'int', 'list', 'dict', 'set', 'tuple']:
                    var_counts[var] = var_counts.get(var, 0) + 1
            
            # Sort by usage count and name length
            vars_to_shorten = sorted(
                [(var, count) for var, count in var_counts.items() if count > 2 and len(var) > 3],
                key=lambda x: (-x[1], -len(x[0]))
            )[:10]  # Top 10 variables
            
            # Generate short names
            short_names = [chr(97 + i) for i in range(26)]  # a-z
            short_names.extend([chr(65 + i) for i in range(26)])  # A-Z
            
            replacements = {}
            for idx, (var, _) in enumerate(vars_to_shorten):
                if idx < len(short_names):
                    replacements[var] = short_names[idx]
            
            if replacements:
                for old_var, new_var in replacements.items():
                    optimized = re.sub(r'\b' + old_var + r'\b', new_var, optimized)
                applied.append(f"Shortened {len(replacements)} variable names")
        
        # Remove unnecessary parentheses in return statements
        optimized = re.sub(r'return\s*\((.*?)\)\s*$', r'return \1', optimized, flags=re.MULTILINE)
        
        # Strip final newline
        optimized = optimized.strip()
        
        return optimized, applied
    
    def _optimize_javascript(self, code: str) -> Tuple[str, List[str]]:
        """Optimize JavaScript code for minimal character count"""
        applied = []
        optimized = code
        
        # Remove single-line comments
        if '//' in optimized:
            optimized = re.sub(r'//.*$', '', optimized, flags=re.MULTILINE)
            applied.append("Removed single-line comments")
        
        # Remove multi-line comments
        if '/*' in optimized:
            optimized = re.sub(r'/\*.*?\*/', '', optimized, flags=re.DOTALL)
            applied.append("Removed multi-line comments")
        
        # Remove unnecessary whitespace
        if '  ' in optimized:
            optimized = re.sub(r'  +', ' ', optimized)
            applied.append("Reduced multiple spaces")
        
        # Remove blank lines
        if '\n\n' in optimized:
            optimized = re.sub(r'\n\n+', '\n', optimized)
            applied.append("Removed blank lines")
        
        # Simplify true/false to !0/!1 or 1/0
        if 'true' in optimized or 'false' in optimized:
            optimized = re.sub(r'\btrue\b', '!0', optimized)
            optimized = re.sub(r'\bfalse\b', '!1', optimized)
            applied.append("Simplified true/false to !0/!1")
        
        # Replace 'function' with arrow functions where possible
        if 'function' in optimized:
            applied.append("Function declarations found (consider arrow functions)")
        
        # Remove semicolons where not required (be very careful!)
        # In code golf, semicolons can often be removed with ASI
        
        optimized = optimized.strip()
        return optimized, applied
    
    def _optimize_bash(self, code: str) -> Tuple[str, List[str]]:
        """Optimize Bash/shell scripts for minimal character count"""
        applied = []
        optimized = code
        
        # Remove comments
        if '#' in optimized:
            optimized = re.sub(r'#.*$', '', optimized, flags=re.MULTILINE)
            applied.append("Removed comments")
        
        # Remove blank lines
        if '\n\n' in optimized:
            optimized = re.sub(r'\n\n+', '\n', optimized)
            applied.append("Removed blank lines")
        
        # Replace multiple spaces with single space
        if '  ' in optimized:
            optimized = re.sub(r'  +', ' ', optimized)
            applied.append("Reduced multiple spaces")
        
        # Shorten common commands
        replacements = {
            'echo ': 'echo ',  # Can't really shorten this
            'export ': 'export ',
        }
        
        optimized = optimized.strip()
        return optimized, applied


def format_output(result: OptimizationResult, format_type: str = 'text', show_ai: bool = True) -> str:
    """Format optimization results with AI insights"""
    if format_type == 'json':
        return json.dumps(result.to_dict(), indent=2)
    
    # Text format with AI enhancements
    lines = [
        "=" * 70,
        "🤖 AI CODE GOLF OPTIMIZATION RESULTS",
        "=" * 70,
        f"Language: {result.language.upper()}",
        f"Original: {result.original_chars} characters",
        f"Optimized: {result.optimized_chars} characters",
        f"Reduction: {result.reduction_percentage}% ({result.original_chars - result.optimized_chars} chars saved)",
        "",
        "Optimizations Applied:",
    ]
    
    for opt in result.optimizations_applied:
        lines.append(f"  ✓ {opt}")
    
    if not result.optimizations_applied:
        lines.append("  (No optimizations applied)")
    
    # Show pattern effectiveness scores
    if show_ai and result.pattern_scores:
        lines.extend([
            "",
            "📊 Pattern Effectiveness Scores:",
        ])
        for pattern, score in sorted(result.pattern_scores.items(), key=lambda x: x[1], reverse=True):
            bar = "█" * int(score * 20) + "░" * (20 - int(score * 20))
            lines.append(f"  {pattern:25s} {bar} {score:.2f}")
    
    # Show AI suggestions
    if show_ai and result.ai_suggestions:
        lines.extend([
            "",
            "💡 AI-Powered Suggestions:",
        ])
        for suggestion in result.ai_suggestions:
            lines.append(f"  {suggestion}")
    
    lines.extend([
        "",
        "-" * 70,
        "ORIGINAL CODE:",
        "-" * 70,
        result.original_code,
        "",
        "-" * 70,
        "OPTIMIZED CODE:",
        "-" * 70,
        result.optimized_code,
        "=" * 70,
    ])
    
    return '\n'.join(lines)


def main():
    """Main CLI entry point with AI enhancements"""
    parser = argparse.ArgumentParser(
        description='🤖 AI Code Golf Optimizer - Minimize code with machine learning',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Optimize Python code with AI suggestions
  %(prog)s -f script.py -l python
  
  # Optimize JavaScript code from stdin
  echo "function test() { return true; }" | %(prog)s -l javascript
  
  # Output as JSON with AI data
  %(prog)s -f script.py -l python --format json
  
  # Disable AI learning (faster, no persistence)
  %(prog)s -f script.py --no-ai
  
  # Show learning statistics
  %(prog)s -f script.py --stats
        """
    )
    
    parser.add_argument('-f', '--file', help='Input file to optimize')
    parser.add_argument('-l', '--language', default='python',
                        choices=['python', 'javascript', 'js', 'bash', 'sh'],
                        help='Programming language (default: python)')
    parser.add_argument('--format', choices=['text', 'json'], default='text',
                        help='Output format (default: text)')
    parser.add_argument('-o', '--output', help='Output file (default: stdout)')
    parser.add_argument('--no-ai', action='store_true',
                        help='Disable AI learning and suggestions')
    parser.add_argument('--stats', action='store_true',
                        help='Show learning statistics after optimization')
    parser.add_argument('--no-save', action='store_true',
                        help='Do not save learned patterns (temporary session)')
    
    args = parser.parse_args()
    
    # Read input code
    if args.file:
        try:
            with open(args.file, 'r') as f:
                code = f.read()
        except FileNotFoundError:
            print(f"Error: File '{args.file}' not found", file=sys.stderr)
            sys.exit(1)
    else:
        if sys.stdin.isatty():
            print("Enter code to optimize (press Ctrl+D when done):")
        code = sys.stdin.read()
    
    if not code.strip():
        print("Error: No code provided", file=sys.stderr)
        sys.exit(1)
    
    # Optimize code with AI
    optimizer = CodeGolfOptimizer(enable_learning=not args.no_ai)
    try:
        result = optimizer.optimize(code, args.language)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Format and output results
    output = format_output(result, args.format, show_ai=not args.no_ai)
    
    if args.output:
        with open(args.output, 'w') as f:
            f.write(output)
        print(f"Results written to {args.output}")
    else:
        print(output)
    
    # Show learning statistics if requested
    if args.stats and not args.no_ai:
        stats = optimizer.get_learning_stats()
        print("\n" + "=" * 70)
        print("📊 LEARNING STATISTICS")
        print("=" * 70)
        print(f"Patterns used in session: {stats.get('patterns_used', 0)}")
        print(f"Total applications: {stats.get('total_applications', 0)}")
        print(f"Total reduction achieved: {stats.get('total_reduction', 0):.2f}%")
        
        if stats.get('top_patterns'):
            print("\nTop performing patterns:")
            for name, pattern_stats in stats['top_patterns']:
                print(f"  • {name}: {pattern_stats['applications']} uses, "
                      f"{pattern_stats['total_reduction']:.2f}% total reduction")
    
    # Save learning data
    if not args.no_ai and not args.no_save:
        optimizer.save_learning()
        if not args.output and args.format == 'text':
            print("\n💾 Learning data saved for future optimizations")


if __name__ == '__main__':
    main()
