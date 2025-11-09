#!/usr/bin/env python3
"""
AI Code Golf Optimizer - Minimize code while preserving functionality

This tool analyzes code and suggests optimizations to reduce character count
while maintaining correctness, perfect for code golf challenges.
"""

import sys
import re
import argparse
import json
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict


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
    
    def to_dict(self):
        return asdict(self)


class CodeGolfOptimizer:
    """Main optimizer class for multiple languages"""
    
    def __init__(self):
        self.optimizations = {
            'python': self._optimize_python,
            'javascript': self._optimize_javascript,
            'js': self._optimize_javascript,
            'bash': self._optimize_bash,
            'sh': self._optimize_bash,
        }
    
    def optimize(self, code: str, language: str = 'python') -> OptimizationResult:
        """Optimize code for the specified language"""
        language = language.lower()
        
        if language not in self.optimizations:
            raise ValueError(f"Unsupported language: {language}. Supported: {list(self.optimizations.keys())}")
        
        original_chars = len(code)
        optimized_code, applied = self.optimizations[language](code)
        optimized_chars = len(optimized_code)
        
        reduction = ((original_chars - optimized_chars) / original_chars * 100) if original_chars > 0 else 0
        
        return OptimizationResult(
            original_code=code,
            optimized_code=optimized_code,
            original_chars=original_chars,
            optimized_chars=optimized_chars,
            reduction_percentage=round(reduction, 2),
            optimizations_applied=applied,
            language=language
        )
    
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


def format_output(result: OptimizationResult, format_type: str = 'text') -> str:
    """Format optimization results"""
    if format_type == 'json':
        return json.dumps(result.to_dict(), indent=2)
    
    # Text format
    lines = [
        "=" * 70,
        "CODE GOLF OPTIMIZATION RESULTS",
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
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description='AI Code Golf Optimizer - Minimize code while preserving functionality',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Optimize Python code from file
  %(prog)s -f script.py -l python
  
  # Optimize JavaScript code from stdin
  echo "function test() { return true; }" | %(prog)s -l javascript
  
  # Output as JSON
  %(prog)s -f script.py -l python --format json
  
  # Optimize bash script
  %(prog)s -f deploy.sh -l bash
        """
    )
    
    parser.add_argument('-f', '--file', help='Input file to optimize')
    parser.add_argument('-l', '--language', default='python',
                        choices=['python', 'javascript', 'js', 'bash', 'sh'],
                        help='Programming language (default: python)')
    parser.add_argument('--format', choices=['text', 'json'], default='text',
                        help='Output format (default: text)')
    parser.add_argument('-o', '--output', help='Output file (default: stdout)')
    
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
    
    # Optimize code
    optimizer = CodeGolfOptimizer()
    try:
        result = optimizer.optimize(code, args.language)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Format and output results
    output = format_output(result, args.format)
    
    if args.output:
        with open(args.output, 'w') as f:
            f.write(output)
        print(f"Results written to {args.output}")
    else:
        print(output)


if __name__ == '__main__':
    main()
