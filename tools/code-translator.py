#!/usr/bin/env python3
"""
Cross-Language Code Translator and Comparison Tool

This tool translates code between different programming languages
and provides comparison functionality to analyze differences.
"""

import sys
import re
import argparse
import json
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict
from difflib import unified_diff


@dataclass
class TranslationResult:
    """Results from code translation"""
    original_code: str
    translated_code: str
    source_language: str
    target_language: str
    translation_notes: List[str]
    
    def to_dict(self):
        return asdict(self)


@dataclass
class ComparisonResult:
    """Results from code comparison"""
    code1: str
    code2: str
    language1: str
    language2: str
    differences: List[str]
    similarity_score: float
    
    def to_dict(self):
        return asdict(self)


class CodeTranslator:
    """Main translator class for multiple languages"""
    
    def __init__(self):
        self.translators = {
            ('python', 'javascript'): self._python_to_javascript,
            ('python', 'js'): self._python_to_javascript,
            ('javascript', 'python'): self._javascript_to_python,
            ('js', 'python'): self._javascript_to_python,
            ('python', 'bash'): self._python_to_bash,
            ('bash', 'python'): self._bash_to_python,
            ('javascript', 'bash'): self._javascript_to_bash,
            ('bash', 'javascript'): self._bash_to_javascript,
        }
    
    def translate(self, code: str, source_lang: str, target_lang: str) -> TranslationResult:
        """Translate code from source language to target language"""
        source_lang = source_lang.lower()
        target_lang = target_lang.lower()
        
        # Normalize language names
        if source_lang == 'js':
            source_lang = 'javascript'
        if target_lang == 'js':
            target_lang = 'javascript'
        if source_lang == 'sh':
            source_lang = 'bash'
        if target_lang == 'sh':
            target_lang = 'bash'
        
        key = (source_lang, target_lang)
        if key not in self.translators:
            raise ValueError(f"Translation from {source_lang} to {target_lang} not supported")
        
        translated_code, notes = self.translators[key](code)
        
        return TranslationResult(
            original_code=code,
            translated_code=translated_code,
            source_language=source_lang,
            target_language=target_lang,
            translation_notes=notes
        )
    
    def compare(self, code1: str, code2: str, lang1: str, lang2: str) -> ComparisonResult:
        """Compare two code snippets across languages"""
        differences = list(unified_diff(
            code1.splitlines(keepends=True),
            code2.splitlines(keepends=True),
            fromfile=f'{lang1} code',
            tofile=f'{lang2} code',
            lineterm=''
        ))
        
        # Calculate similarity score (simple line-based comparison)
        lines1 = set(code1.strip().split('\n'))
        lines2 = set(code2.strip().split('\n'))
        
        if len(lines1) == 0 and len(lines2) == 0:
            similarity = 100.0
        elif len(lines1) == 0 or len(lines2) == 0:
            similarity = 0.0
        else:
            common_lines = lines1.intersection(lines2)
            total_lines = lines1.union(lines2)
            similarity = (len(common_lines) / len(total_lines)) * 100 if total_lines else 0.0
        
        return ComparisonResult(
            code1=code1,
            code2=code2,
            language1=lang1,
            language2=lang2,
            differences=differences,
            similarity_score=round(similarity, 2)
        )
    
    def _python_to_javascript(self, code: str) -> Tuple[str, List[str]]:
        """Translate Python code to JavaScript"""
        notes = []
        translated = code
        
        # Replace print statements
        if 'print(' in translated:
            translated = re.sub(r'print\((.*?)\)', r'console.log(\1)', translated)
            notes.append("Converted print() to console.log()")
        
        # Replace def with function
        if 'def ' in translated:
            translated = re.sub(r'def\s+(\w+)\s*\((.*?)\):', r'function \1(\2) {', translated)
            notes.append("Converted def to function")
        
        # Replace True/False with true/false
        if 'True' in translated or 'False' in translated:
            translated = translated.replace('True', 'true').replace('False', 'false')
            notes.append("Converted True/False to true/false")
        
        # Replace None with null
        if 'None' in translated:
            translated = translated.replace('None', 'null')
            notes.append("Converted None to null")
        
        # Replace elif with else if
        if 'elif ' in translated:
            translated = re.sub(r'elif\s+', 'else if ', translated)
            notes.append("Converted elif to else if")
        
        # Add closing braces for functions and control structures
        if 'function ' in translated or 'if ' in translated or 'else if ' in translated:
            lines = translated.split('\n')
            result_lines = []
            indent_stack = []
            
            for i, line in enumerate(lines):
                stripped = line.lstrip()
                current_indent = len(line) - len(stripped)
                
                # Check if we need to close previous blocks
                while indent_stack and current_indent <= indent_stack[-1]:
                    prev_indent = indent_stack.pop()
                    result_lines.append(' ' * prev_indent + '}')
                
                # Add current line
                result_lines.append(line)
                
                # Track new blocks
                if stripped.startswith('function ') or stripped.startswith('if ') or stripped.startswith('else if ') or stripped.startswith('else'):
                    if '{' in line:
                        indent_stack.append(current_indent)
            
            # Close any remaining blocks
            while indent_stack:
                prev_indent = indent_stack.pop()
                result_lines.append(' ' * prev_indent + '}')
            
            translated = '\n'.join(result_lines)
        
        # Replace string formatting
        if 'f"' in translated or "f'" in translated:
            # Basic f-string to template literal conversion
            translated = re.sub(r'f"([^"]*)"', r'`\1`', translated)
            translated = re.sub(r"f'([^']*)'", r'`\1`', translated)
            translated = re.sub(r'\{(\w+)\}', r'${\1}', translated)
            notes.append("Converted f-strings to template literals")
        
        # Replace list comprehensions (basic cases)
        # This is a simplified conversion
        if '[' in translated and 'for' in translated and 'in' in translated:
            notes.append("List comprehensions may need manual conversion to map/filter")
        
        # Add semicolons at end of statements (optional in JS but good practice)
        lines = translated.split('\n')
        result_lines = []
        for line in lines:
            stripped = line.strip()
            if stripped and not stripped.endswith(('{', '}', ';')) and not stripped.startswith('//'):
                line = line.rstrip() + ';'
            result_lines.append(line)
        translated = '\n'.join(result_lines)
        
        # Replace range() with array generation
        if 'range(' in translated:
            notes.append("range() needs manual conversion to Array.from() or similar")
        
        # Replace len() with .length
        if 'len(' in translated:
            translated = re.sub(r'len\((\w+)\)', r'\1.length', translated)
            notes.append("Converted len() to .length")
        
        return translated, notes
    
    def _javascript_to_python(self, code: str) -> Tuple[str, List[str]]:
        """Translate JavaScript code to Python"""
        notes = []
        translated = code
        
        # Remove semicolons
        if ';' in translated:
            translated = translated.replace(';', '')
            notes.append("Removed semicolons")
        
        # Replace console.log with print
        if 'console.log(' in translated:
            translated = re.sub(r'console\.log\((.*?)\)', r'print(\1)', translated)
            notes.append("Converted console.log() to print()")
        
        # Replace function with def
        if 'function ' in translated:
            translated = re.sub(r'function\s+(\w+)\s*\((.*?)\)\s*\{', r'def \1(\2):', translated)
            notes.append("Converted function to def")
        
        # Replace true/false with True/False
        if 'true' in translated or 'false' in translated:
            translated = re.sub(r'\btrue\b', 'True', translated)
            translated = re.sub(r'\bfalse\b', 'False', translated)
            notes.append("Converted true/false to True/False")
        
        # Replace null/undefined with None
        if 'null' in translated or 'undefined' in translated:
            translated = re.sub(r'\bnull\b', 'None', translated)
            translated = re.sub(r'\bundefined\b', 'None', translated)
            notes.append("Converted null/undefined to None")
        
        # Remove braces and adjust indentation
        if '{' in translated or '}' in translated:
            lines = translated.split('\n')
            result_lines = []
            indent_level = 0
            
            for line in lines:
                stripped = line.strip()
                
                # Skip closing braces
                if stripped == '}':
                    indent_level = max(0, indent_level - 1)
                    continue
                
                # Remove opening braces
                if '{' in stripped:
                    stripped = stripped.replace('{', '').strip()
                
                # Add proper indentation
                if stripped:
                    result_lines.append('    ' * indent_level + stripped)
                    
                    # Increase indent after control structures
                    if stripped.endswith(':'):
                        indent_level += 1
                else:
                    result_lines.append('')
                
                # Decrease indent for certain keywords
                if stripped.startswith(('else:', 'elif ', 'except:', 'finally:')):
                    # These are already at the right level
                    pass
            
            translated = '\n'.join(result_lines)
            notes.append("Converted braces to Python indentation")
        
        # Replace else if with elif
        if 'else if ' in translated:
            translated = re.sub(r'else if\s+', 'elif ', translated)
            notes.append("Converted else if to elif")
        
        # Replace template literals with f-strings
        if '`' in translated:
            translated = re.sub(r'`([^`]*)`', r'f"\1"', translated)
            translated = re.sub(r'\$\{(\w+)\}', r'{\1}', translated)
            notes.append("Converted template literals to f-strings")
        
        # Replace .length with len()
        if '.length' in translated:
            translated = re.sub(r'(\w+)\.length', r'len(\1)', translated)
            notes.append("Converted .length to len()")
        
        # Replace var/let/const with simple assignment
        if any(keyword in translated for keyword in ['var ', 'let ', 'const ']):
            translated = re.sub(r'\b(var|let|const)\s+', '', translated)
            notes.append("Removed var/let/const declarations")
        
        return translated, notes
    
    def _python_to_bash(self, code: str) -> Tuple[str, List[str]]:
        """Translate Python code to Bash (basic support)"""
        notes = ["Python to Bash translation is basic and may require manual adjustment"]
        translated = code
        
        # Add shebang if not present
        if not translated.startswith('#!'):
            translated = '#!/bin/bash\n' + translated
            notes.append("Added shebang")
        
        # Replace print with echo
        if 'print(' in translated:
            translated = re.sub(r'print\((.*?)\)', r'echo \1', translated)
            notes.append("Converted print() to echo")
        
        # Basic variable assignment
        translated = re.sub(r'(\w+)\s*=\s*(["\'].*?["\'])', r'\1=\2', translated)
        
        return translated, notes
    
    def _bash_to_python(self, code: str) -> Tuple[str, List[str]]:
        """Translate Bash code to Python (basic support)"""
        notes = ["Bash to Python translation is basic and may require manual adjustment"]
        translated = code
        
        # Remove shebang
        if translated.startswith('#!/'):
            lines = translated.split('\n')
            translated = '\n'.join(lines[1:])
            notes.append("Removed shebang")
        
        # Replace echo with print
        if 'echo ' in translated:
            translated = re.sub(r'echo\s+(.*?)$', r'print(\1)', translated, flags=re.MULTILINE)
            notes.append("Converted echo to print()")
        
        return translated, notes
    
    def _javascript_to_bash(self, code: str) -> Tuple[str, List[str]]:
        """Translate JavaScript code to Bash (basic support)"""
        notes = ["JavaScript to Bash translation is basic and may require manual adjustment"]
        translated = code
        
        # Add shebang if not present
        if not translated.startswith('#!'):
            translated = '#!/bin/bash\n' + translated
            notes.append("Added shebang")
        
        # Replace console.log with echo
        if 'console.log(' in translated:
            translated = re.sub(r'console\.log\((.*?)\)', r'echo \1', translated)
            notes.append("Converted console.log() to echo")
        
        return translated, notes
    
    def _bash_to_javascript(self, code: str) -> Tuple[str, List[str]]:
        """Translate Bash code to JavaScript (basic support)"""
        notes = ["Bash to JavaScript translation is basic and may require manual adjustment"]
        translated = code
        
        # Remove shebang
        if translated.startswith('#!/'):
            lines = translated.split('\n')
            translated = '\n'.join(lines[1:])
            notes.append("Removed shebang")
        
        # Replace echo with console.log
        if 'echo ' in translated:
            translated = re.sub(r'echo\s+(.*?)$', r'console.log(\1);', translated, flags=re.MULTILINE)
            notes.append("Converted echo to console.log()")
        
        return translated, notes


def format_output(result, output_format='text'):
    """Format the result for output"""
    if output_format == 'json':
        return json.dumps(result.to_dict(), indent=2)
    else:
        if isinstance(result, TranslationResult):
            lines = [
                f"Translation: {result.source_language} → {result.target_language}",
                "=" * 60,
                "",
                "Original Code:",
                "-" * 60,
                result.original_code,
                "",
                "Translated Code:",
                "-" * 60,
                result.translated_code,
                "",
                "Translation Notes:",
                "-" * 60,
            ]
            for note in result.translation_notes:
                lines.append(f"  • {note}")
            return '\n'.join(lines)
        elif isinstance(result, ComparisonResult):
            lines = [
                f"Comparison: {result.language1} vs {result.language2}",
                "=" * 60,
                "",
                f"Similarity Score: {result.similarity_score}%",
                "",
                "Differences:",
                "-" * 60,
            ]
            if result.differences:
                lines.extend(result.differences)
            else:
                lines.append("No differences found")
            return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(
        description='Cross-language code translator and comparison tool'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Translate command
    translate_parser = subparsers.add_parser('translate', help='Translate code between languages')
    translate_parser.add_argument('-f', '--file', help='Input file to translate')
    translate_parser.add_argument('-s', '--source', required=True, help='Source language')
    translate_parser.add_argument('-t', '--target', required=True, help='Target language')
    translate_parser.add_argument('--format', choices=['text', 'json'], default='text', help='Output format')
    translate_parser.add_argument('-o', '--output', help='Output file (default: stdout)')
    
    # Compare command
    compare_parser = subparsers.add_parser('compare', help='Compare code across languages')
    compare_parser.add_argument('-f1', '--file1', required=True, help='First file to compare')
    compare_parser.add_argument('-l1', '--lang1', required=True, help='Language of first file')
    compare_parser.add_argument('-f2', '--file2', required=True, help='Second file to compare')
    compare_parser.add_argument('-l2', '--lang2', required=True, help='Language of second file')
    compare_parser.add_argument('--format', choices=['text', 'json'], default='text', help='Output format')
    compare_parser.add_argument('-o', '--output', help='Output file (default: stdout)')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    translator = CodeTranslator()
    
    try:
        if args.command == 'translate':
            # Read input code
            if args.file:
                with open(args.file, 'r') as f:
                    code = f.read()
            else:
                code = sys.stdin.read()
            
            # Translate
            result = translator.translate(code, args.source, args.target)
            output = format_output(result, args.format)
            
        elif args.command == 'compare':
            # Read both files
            with open(args.file1, 'r') as f:
                code1 = f.read()
            with open(args.file2, 'r') as f:
                code2 = f.read()
            
            # Compare
            result = translator.compare(code1, code2, args.lang1, args.lang2)
            output = format_output(result, args.format)
        
        # Write output
        if args.output:
            with open(args.output, 'w') as f:
                f.write(output)
        else:
            print(output)
        
        return 0
    
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
