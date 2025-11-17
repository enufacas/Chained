#!/usr/bin/env python3
"""
Code Paradigm Translator for Chained

Translates code between different programming paradigms:
- Object-Oriented (OOP) ↔ Functional
- Imperative ↔ Declarative
- Procedural ↔ Object-Oriented

This enhances the autonomous system's ability to adapt and transform code patterns.

Enhanced by @accelerate-specialist with performance optimizations:
- Translation caching for efficiency
- Performance benchmarking and metrics
- Batch processing capabilities
- Resource usage tracking
"""

import ast
import re
import time
import hashlib
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from functools import lru_cache


class Paradigm(Enum):
    """Supported programming paradigms"""
    OBJECT_ORIENTED = "object_oriented"
    FUNCTIONAL = "functional"
    IMPERATIVE = "imperative"
    DECLARATIVE = "declarative"
    PROCEDURAL = "procedural"


@dataclass
class PerformanceMetrics:
    """Performance metrics for a translation operation"""
    translation_time_ms: float
    code_size_before: int
    code_size_after: int
    lines_before: int
    lines_after: int
    cache_hit: bool = False
    
    @property
    def size_reduction_percent(self) -> float:
        """Calculate size reduction percentage"""
        if self.code_size_before == 0:
            return 0.0
        return ((self.code_size_before - self.code_size_after) / self.code_size_before) * 100
    
    @property
    def line_reduction_percent(self) -> float:
        """Calculate line reduction percentage"""
        if self.lines_before == 0:
            return 0.0
        return ((self.lines_before - self.lines_after) / self.lines_before) * 100


@dataclass
class TranslationResult:
    """Result of a paradigm translation"""
    source_paradigm: Paradigm
    target_paradigm: Paradigm
    original_code: str
    translated_code: str
    transformations_applied: List[str]
    success: bool
    warnings: List[str]
    performance_metrics: Optional[PerformanceMetrics] = None
    
    def __str__(self):
        status = "✓ Success" if self.success else "✗ Failed"
        result = (f"Translation {status}: {self.source_paradigm.value} → {self.target_paradigm.value}\n"
                 f"Transformations: {len(self.transformations_applied)}\n"
                 f"Warnings: {len(self.warnings)}")
        
        if self.performance_metrics:
            result += f"\nPerformance: {self.performance_metrics.translation_time_ms:.2f}ms"
            if self.performance_metrics.cache_hit:
                result += " (cached)"
        
        return result


class ParadigmTranslator:
    """Translates code between different programming paradigms
    
    Enhanced by @accelerate-specialist with performance optimizations:
    - LRU cache for repeated translations
    - Performance metrics tracking
    - Batch processing support
    """
    
    def __init__(self, enable_cache: bool = True):
        self.enable_cache = enable_cache
        self.translation_cache: Dict[str, TranslationResult] = {}
        self.performance_stats: List[PerformanceMetrics] = []
        
        self.translation_strategies = {
            (Paradigm.OBJECT_ORIENTED, Paradigm.FUNCTIONAL): self._oop_to_functional,
            (Paradigm.FUNCTIONAL, Paradigm.OBJECT_ORIENTED): self._functional_to_oop,
            (Paradigm.IMPERATIVE, Paradigm.DECLARATIVE): self._imperative_to_declarative,
            (Paradigm.DECLARATIVE, Paradigm.IMPERATIVE): self._declarative_to_imperative,
            (Paradigm.PROCEDURAL, Paradigm.OBJECT_ORIENTED): self._procedural_to_oop,
            (Paradigm.OBJECT_ORIENTED, Paradigm.PROCEDURAL): self._oop_to_procedural,
        }
    
    def _get_cache_key(self, code: str, source: Paradigm, target: Paradigm) -> str:
        """Generate cache key for translation"""
        content = f"{source.value}:{target.value}:{code}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def clear_cache(self):
        """Clear the translation cache"""
        self.translation_cache.clear()
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get summary of performance statistics"""
        if not self.performance_stats:
            return {}
        
        total_time = sum(m.translation_time_ms for m in self.performance_stats)
        cache_hits = sum(1 for m in self.performance_stats if m.cache_hit)
        avg_time = total_time / len(self.performance_stats)
        
        size_reductions = [m.size_reduction_percent for m in self.performance_stats 
                          if m.code_size_before > 0]
        avg_size_reduction = sum(size_reductions) / len(size_reductions) if size_reductions else 0
        
        return {
            'total_translations': len(self.performance_stats),
            'cache_hits': cache_hits,
            'cache_hit_rate': cache_hits / len(self.performance_stats) * 100,
            'total_time_ms': total_time,
            'average_time_ms': avg_time,
            'average_size_reduction_percent': avg_size_reduction,
        }
    
    def translate(self, code: str, source: Paradigm, target: Paradigm) -> TranslationResult:
        """
        Translate code from source paradigm to target paradigm
        
        Enhanced by @accelerate-specialist with caching and performance tracking
        
        Args:
            code: Source code to translate
            source: Source paradigm
            target: Target paradigm
            
        Returns:
            TranslationResult with translated code and metadata
        """
        start_time = time.time()
        
        # Check cache first
        cache_key = self._get_cache_key(code, source, target)
        if self.enable_cache and cache_key in self.translation_cache:
            cached_result = self.translation_cache[cache_key]
            # Create new result with updated cache hit info
            elapsed_ms = (time.time() - start_time) * 1000
            metrics = PerformanceMetrics(
                translation_time_ms=elapsed_ms,
                code_size_before=len(code),
                code_size_after=len(cached_result.translated_code),
                lines_before=len(code.splitlines()),
                lines_after=len(cached_result.translated_code.splitlines()),
                cache_hit=True
            )
            self.performance_stats.append(metrics)
            
            return TranslationResult(
                source_paradigm=cached_result.source_paradigm,
                target_paradigm=cached_result.target_paradigm,
                original_code=cached_result.original_code,
                translated_code=cached_result.translated_code,
                transformations_applied=cached_result.transformations_applied,
                success=cached_result.success,
                warnings=cached_result.warnings,
                performance_metrics=metrics
            )
        
        transformations = []
        warnings = []
        
        if source == target:
            warnings.append("Source and target paradigms are the same")
            result = TranslationResult(
                source_paradigm=source,
                target_paradigm=target,
                original_code=code,
                translated_code=code,
                transformations_applied=transformations,
                success=True,
                warnings=warnings
            )
        elif (source, target) not in self.translation_strategies:
            warnings.append(f"No direct translation strategy from {source.value} to {target.value}")
            result = TranslationResult(
                source_paradigm=source,
                target_paradigm=target,
                original_code=code,
                translated_code=code,
                transformations_applied=transformations,
                success=False,
                warnings=warnings
            )
        else:
            try:
                translated_code, transformations = self.translation_strategies[(source, target)](code)
                result = TranslationResult(
                    source_paradigm=source,
                    target_paradigm=target,
                    original_code=code,
                    translated_code=translated_code,
                    transformations_applied=transformations,
                    success=True,
                    warnings=warnings
                )
            except Exception as e:
                warnings.append(f"Translation error: {str(e)}")
                result = TranslationResult(
                    source_paradigm=source,
                    target_paradigm=target,
                    original_code=code,
                    translated_code=code,
                    transformations_applied=transformations,
                    success=False,
                    warnings=warnings
                )
        
        # Calculate performance metrics
        elapsed_ms = (time.time() - start_time) * 1000
        metrics = PerformanceMetrics(
            translation_time_ms=elapsed_ms,
            code_size_before=len(code),
            code_size_after=len(result.translated_code),
            lines_before=len(code.splitlines()),
            lines_after=len(result.translated_code.splitlines()),
            cache_hit=False
        )
        result.performance_metrics = metrics
        self.performance_stats.append(metrics)
        
        # Cache successful translations
        if self.enable_cache and result.success:
            self.translation_cache[cache_key] = result
        
        return result
    
    def _oop_to_functional(self, code: str) -> Tuple[str, List[str]]:
        """Transform Object-Oriented code to Functional style"""
        transformations = []
        result = code
        
        # Transform class methods to pure functions
        class_pattern = r'class\s+(\w+)(?:\([^)]*\))?:\s*\n((?:\s{4}.*\n)*)'
        classes = re.finditer(class_pattern, result)
        
        for match in classes:
            class_name = match.group(1)
            class_body = match.group(2)
            
            # Extract methods
            method_pattern = r'(\s{4})def\s+(\w+)\(self(?:,\s*([^)]*))?\):\s*\n((?:\s{8}.*\n)*)'
            methods = re.finditer(method_pattern, class_body)
            
            functional_functions = []
            for method_match in methods:
                method_name = method_match.group(2)
                params = method_match.group(3) or ""
                body = method_match.group(4)
                
                # Skip __init__ and special methods for now
                if method_name.startswith('__'):
                    continue
                
                # Convert to pure function
                func_params = f"{class_name.lower()}_data" + (f", {params}" if params else "")
                functional_func = f"def {method_name}({func_params}):\n{body}"
                functional_functions.append(functional_func)
                transformations.append(f"Converted method {class_name}.{method_name} to pure function")
            
            if functional_functions:
                result = result.replace(match.group(0), '\n\n'.join(functional_functions))
        
        # Transform loops to map/filter/reduce patterns
        result, loop_transforms = self._transform_loops_to_functional(result)
        transformations.extend(loop_transforms)
        
        # Remove mutable state assignments where possible
        result, state_transforms = self._remove_mutable_state(result)
        transformations.extend(state_transforms)
        
        return result, transformations
    
    def _functional_to_oop(self, code: str) -> Tuple[str, List[str]]:
        """Transform Functional code to Object-Oriented style"""
        transformations = []
        result = code
        
        # Group related functions into classes
        func_pattern = r'def\s+(\w+)\(([^)]*)\):\s*\n((?:(?:\s{4}.*\n)|(?:\n))*)'
        functions = list(re.finditer(func_pattern, result))
        
        if functions:
            # Create a class to encapsulate related functions
            class_name = "DataProcessor"
            class_methods = []
            
            for match in functions:
                func_name = match.group(1)
                params = match.group(2)
                body = match.group(3)
                
                # Convert function to method
                # Remove data parameter if present (assuming it becomes self)
                method_params = re.sub(r'^(\w+_)?data(?:,\s*)?', '', params)
                method = f"    def {func_name}(self{', ' + method_params if method_params else ''}):\n"
                method += ''.join('    ' + line for line in body.split('\n') if line)
                class_methods.append(method)
                transformations.append(f"Converted function {func_name} to method")
            
            class_def = f"class {class_name}:\n    def __init__(self, data):\n        self.data = data\n\n"
            class_def += '\n\n'.join(class_methods)
            result = class_def
        
        return result, transformations
    
    def _imperative_to_declarative(self, code: str) -> Tuple[str, List[str]]:
        """Transform Imperative code to Declarative style"""
        transformations = []
        result = code
        
        # Transform explicit loops to comprehensions
        # Match for loops that build lists
        for_pattern = r'(\s*)(\w+)\s*=\s*\[\]\s*\n\1for\s+(\w+)\s+in\s+([^:]+):\s*\n\1\s{4}\2\.append\(([^)]+)\)'
        
        def replace_for_loop(match):
            indent = match.group(1)
            var_name = match.group(2)
            loop_var = match.group(3)
            iterable = match.group(4)
            append_expr = match.group(5)
            transformations.append(f"Converted for loop to list comprehension for {var_name}")
            return f"{indent}{var_name} = [{append_expr} for {loop_var} in {iterable}]"
        
        result = re.sub(for_pattern, replace_for_loop, result)
        
        # Transform filter loops to filter expressions
        filter_pattern = r'(\s*)(\w+)\s*=\s*\[\]\s*\n\1for\s+(\w+)\s+in\s+([^:]+):\s*\n\1\s{4}if\s+([^:]+):\s*\n\1\s{8}\2\.append\(\3\)'
        
        def replace_filter_loop(match):
            indent = match.group(1)
            var_name = match.group(2)
            loop_var = match.group(3)
            iterable = match.group(4)
            condition = match.group(5)
            transformations.append(f"Converted filter loop to list comprehension for {var_name}")
            return f"{indent}{var_name} = [{loop_var} for {loop_var} in {iterable} if {condition}]"
        
        result = re.sub(filter_pattern, replace_filter_loop, result)
        
        return result, transformations
    
    def _declarative_to_imperative(self, code: str) -> Tuple[str, List[str]]:
        """Transform Declarative code to Imperative style"""
        transformations = []
        result = code
        
        # Transform list comprehensions to explicit loops
        comp_pattern = r'(\s*)(\w+)\s*=\s*\[([^]]+)\s+for\s+(\w+)\s+in\s+([^]]+?)(?:\s+if\s+([^]]+))?\]'
        
        def replace_comprehension(match):
            indent = match.group(1)
            var_name = match.group(2)
            expr = match.group(3).strip()
            loop_var = match.group(4)
            iterable = match.group(5).strip()
            condition = match.group(6)
            
            transformations.append(f"Converted list comprehension to for loop for {var_name}")
            
            loop = f"{indent}{var_name} = []\n"
            loop += f"{indent}for {loop_var} in {iterable}:\n"
            if condition:
                loop += f"{indent}    if {condition.strip()}:\n"
                loop += f"{indent}        {var_name}.append({expr})"
            else:
                loop += f"{indent}    {var_name}.append({expr})"
            
            return loop
        
        result = re.sub(comp_pattern, replace_comprehension, result)
        
        return result, transformations
    
    def _procedural_to_oop(self, code: str) -> Tuple[str, List[str]]:
        """Transform Procedural code to Object-Oriented style"""
        transformations = []
        result = code
        
        # Group functions that work on the same data into a class
        func_pattern = r'def\s+(\w+)\(([^)]*)\):\s*\n((?:(?:\s{4}.*\n)|(?:\n))*)'
        functions = list(re.finditer(func_pattern, result))
        
        if functions:
            class_name = "DataHandler"
            class_body = f"class {class_name}:\n"
            class_body += "    def __init__(self):\n"
            class_body += "        pass\n\n"
            
            for match in functions:
                func_name = match.group(1)
                params = match.group(2)
                body = match.group(3)
                
                # Convert to method
                method = f"    def {func_name}(self{', ' + params if params else ''}):\n"
                method += ''.join('    ' + line for line in body.split('\n') if line) + '\n'
                class_body += method
                transformations.append(f"Encapsulated function {func_name} as method")
            
            result = class_body
        
        return result, transformations
    
    def _oop_to_procedural(self, code: str) -> Tuple[str, List[str]]:
        """Transform Object-Oriented code to Procedural style"""
        transformations = []
        result = code
        
        # Extract methods from classes and convert to standalone functions
        class_pattern = r'class\s+(\w+)(?:\([^)]*\))?:\s*\n((?:\s{4}.*\n)*)'
        classes = re.finditer(class_pattern, result)
        
        procedural_code = ""
        for match in classes:
            class_name = match.group(1)
            class_body = match.group(2)
            
            # Extract methods
            method_pattern = r'(\s{4})def\s+(\w+)\(self(?:,\s*([^)]*))?\):\s*\n((?:\s{8}.*\n)*)'
            methods = re.finditer(method_pattern, class_body)
            
            for method_match in methods:
                method_name = method_match.group(2)
                params = method_match.group(3) or ""
                body = method_match.group(4)
                
                # Skip __init__ and special methods
                if method_name.startswith('__'):
                    continue
                
                # Convert to procedural function
                func_params = f"data" + (f", {params}" if params else "")
                func = f"def {method_name}({func_params}):\n"
                func += body.replace('        ', '    ')  # Dedent
                procedural_code += func + '\n\n'
                transformations.append(f"Extracted method {class_name}.{method_name} as function")
        
        result = procedural_code if procedural_code else result
        return result, transformations
    
    def _transform_loops_to_functional(self, code: str) -> Tuple[str, List[str]]:
        """Transform imperative loops to functional patterns"""
        transformations = []
        result = code
        
        # Transform map patterns
        map_pattern = r'(\s*)(\w+)\s*=\s*\[\]\s*\n\1for\s+(\w+)\s+in\s+([^:]+):\s*\n\1\s{4}\2\.append\(([^)]+)\)'
        
        def replace_map(match):
            indent = match.group(1)
            var_name = match.group(2)
            loop_var = match.group(3)
            iterable = match.group(4)
            expr = match.group(5)
            transformations.append(f"Converted loop to map pattern for {var_name}")
            return f"{indent}{var_name} = list(map(lambda {loop_var}: {expr}, {iterable}))"
        
        result = re.sub(map_pattern, replace_map, result)
        
        return result, transformations
    
    def _remove_mutable_state(self, code: str) -> Tuple[str, List[str]]:
        """Attempt to remove mutable state where possible"""
        transformations = []
        result = code
        
        # Look for accumulator patterns that could use reduce
        # This is a simplified example
        accumulator_pattern = r'(\s*)(\w+)\s*=\s*([^\n]+)\s*\n\1for\s+(\w+)\s+in\s+([^:]+):\s*\n\1\s{4}\2\s*([+\-*/]|=\s*)=\s*([^\n]+)'
        
        matches = list(re.finditer(accumulator_pattern, result))
        if matches:
            transformations.append(f"Identified {len(matches)} potential immutable transformations")
        
        return result, transformations
    
    def detect_paradigm(self, code: str) -> Optional[Paradigm]:
        """
        Detect the primary paradigm of the given code
        
        Args:
            code: Source code to analyze
            
        Returns:
            Detected paradigm or None if unclear
        """
        try:
            tree = ast.parse(code)
        except SyntaxError:
            return None
        
        has_classes = any(isinstance(node, ast.ClassDef) for node in ast.walk(tree))
        has_functions = any(isinstance(node, ast.FunctionDef) for node in ast.walk(tree))
        
        # Count functional patterns
        functional_patterns = 0
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    if node.func.id in ['map', 'filter', 'reduce', 'lambda']:
                        functional_patterns += 1
            if isinstance(node, ast.Lambda):
                functional_patterns += 1
            if isinstance(node, ast.ListComp):
                functional_patterns += 1
        
        # Simple heuristic
        if has_classes:
            return Paradigm.OBJECT_ORIENTED
        elif functional_patterns > 2:
            return Paradigm.FUNCTIONAL
        elif has_functions:
            return Paradigm.PROCEDURAL
        else:
            return Paradigm.IMPERATIVE
    
    def translate_batch(self, translations: List[Tuple[str, Paradigm, Paradigm]]) -> List[TranslationResult]:
        """
        Batch translate multiple code snippets efficiently
        
        Enhanced by @accelerate-specialist for efficient batch processing
        
        Args:
            translations: List of (code, source_paradigm, target_paradigm) tuples
            
        Returns:
            List of TranslationResult objects
        """
        results = []
        for code, source, target in translations:
            result = self.translate(code, source, target)
            results.append(result)
        return results
    
    def benchmark_paradigm_performance(self, code: str, paradigms: List[Paradigm]) -> Dict[str, Any]:
        """
        Benchmark translation performance across multiple paradigms
        
        Args:
            code: Source code to translate
            paradigms: List of target paradigms to test
            
        Returns:
            Dictionary with benchmark results
        """
        source_paradigm = self.detect_paradigm(code)
        if not source_paradigm:
            return {'error': 'Could not detect source paradigm'}
        
        benchmarks = []
        for target in paradigms:
            if target == source_paradigm:
                continue
            
            result = self.translate(code, source_paradigm, target)
            if result.success and result.performance_metrics:
                benchmarks.append({
                    'target_paradigm': target.value,
                    'translation_time_ms': result.performance_metrics.translation_time_ms,
                    'size_reduction_percent': result.performance_metrics.size_reduction_percent,
                    'line_reduction_percent': result.performance_metrics.line_reduction_percent,
                    'transformations': len(result.transformations_applied)
                })
        
        return {
            'source_paradigm': source_paradigm.value,
            'benchmarks': benchmarks
        }



def main():
    """Example usage of the paradigm translator
    
    Enhanced by @accelerate-specialist with performance demonstrations
    """
    translator = ParadigmTranslator()
    
    # Example 1: OOP to Functional
    oop_code = """
class Calculator:
    def __init__(self, numbers):
        self.numbers = numbers
    
    def sum_positive(self):
        result = []
        for num in self.numbers:
            if num > 0:
                result.append(num)
        return sum(result)
    
    def multiply_by_two(self):
        result = []
        for num in self.numbers:
            result.append(num * 2)
        return result
"""
    
    print("=" * 80)
    print("Enhanced Paradigm Translator - Performance Demo (@accelerate-specialist)")
    print("=" * 80)
    
    print("\n" + "=" * 60)
    print("Example 1: Object-Oriented → Functional (with performance metrics)")
    print("=" * 60)
    result = translator.translate(oop_code, Paradigm.OBJECT_ORIENTED, Paradigm.FUNCTIONAL)
    print(result)
    print("\nOriginal code:")
    print(result.original_code)
    print("\nTranslated code:")
    print(result.translated_code)
    print("\nTransformations applied:")
    for t in result.transformations_applied:
        print(f"  - {t}")
    
    if result.performance_metrics:
        print(f"\n⚡ Performance Metrics:")
        print(f"  - Translation time: {result.performance_metrics.translation_time_ms:.2f}ms")
        print(f"  - Size reduction: {result.performance_metrics.size_reduction_percent:.1f}%")
        print(f"  - Line reduction: {result.performance_metrics.line_reduction_percent:.1f}%")
    
    # Example 2: Imperative to Declarative
    imperative_code = """
numbers = [1, 2, 3, 4, 5]
doubled = []
for n in numbers:
    doubled.append(n * 2)

evens = []
for n in numbers:
    if n % 2 == 0:
        evens.append(n)
"""
    
    print("\n" + "=" * 60)
    print("Example 2: Imperative → Declarative")
    print("=" * 60)
    result = translator.translate(imperative_code, Paradigm.IMPERATIVE, Paradigm.DECLARATIVE)
    print(result)
    print("\nOriginal code:")
    print(result.original_code)
    print("\nTranslated code:")
    print(result.translated_code)
    print("\nTransformations applied:")
    for t in result.transformations_applied:
        print(f"  - {t}")
    
    if result.performance_metrics:
        print(f"\n⚡ Performance Metrics:")
        print(f"  - Translation time: {result.performance_metrics.translation_time_ms:.2f}ms")
        print(f"  - Size reduction: {result.performance_metrics.size_reduction_percent:.1f}%")
    
    # Example 3: Test caching performance
    print("\n" + "=" * 60)
    print("Example 3: Cache Performance Test")
    print("=" * 60)
    
    # First translation (cache miss)
    result1 = translator.translate(imperative_code, Paradigm.IMPERATIVE, Paradigm.DECLARATIVE)
    print(f"First translation: {result1.performance_metrics.translation_time_ms:.2f}ms (cache miss)")
    
    # Second translation (cache hit)
    result2 = translator.translate(imperative_code, Paradigm.IMPERATIVE, Paradigm.DECLARATIVE)
    print(f"Second translation: {result2.performance_metrics.translation_time_ms:.2f}ms (cache hit)")
    
    speedup = result1.performance_metrics.translation_time_ms / result2.performance_metrics.translation_time_ms
    print(f"Cache speedup: {speedup:.1f}x faster")
    
    # Example 4: Batch translation
    print("\n" + "=" * 60)
    print("Example 4: Batch Translation Performance")
    print("=" * 60)
    
    batch_translations = [
        (imperative_code, Paradigm.IMPERATIVE, Paradigm.DECLARATIVE),
        (oop_code, Paradigm.OBJECT_ORIENTED, Paradigm.FUNCTIONAL),
        ("x = [i for i in range(10)]", Paradigm.DECLARATIVE, Paradigm.IMPERATIVE),
    ]
    
    batch_start = time.time()
    batch_results = translator.translate_batch(batch_translations)
    batch_time = (time.time() - batch_start) * 1000
    
    print(f"Batch translated {len(batch_results)} code snippets in {batch_time:.2f}ms")
    print(f"Average per translation: {batch_time / len(batch_results):.2f}ms")
    
    # Example 5: Performance summary
    print("\n" + "=" * 60)
    print("Example 5: Overall Performance Summary")
    print("=" * 60)
    
    summary = translator.get_performance_summary()
    if summary:
        print(f"Total translations: {summary['total_translations']}")
        print(f"Cache hits: {summary['cache_hits']} ({summary['cache_hit_rate']:.1f}%)")
        print(f"Total time: {summary['total_time_ms']:.2f}ms")
        print(f"Average time per translation: {summary['average_time_ms']:.2f}ms")
        print(f"Average code size reduction: {summary['average_size_reduction_percent']:.1f}%")
    
    # Example 6: Paradigm detection
    print("\n" + "=" * 60)
    print("Example 6: Paradigm Detection")
    print("=" * 60)
    detected = translator.detect_paradigm(oop_code)
    print(f"Detected paradigm for OOP code: {detected.value if detected else 'Unknown'}")
    
    detected = translator.detect_paradigm(imperative_code)
    print(f"Detected paradigm for imperative code: {detected.value if detected else 'Unknown'}")
    
    print("\n" + "=" * 80)
    print("✓ All examples completed - Performance optimizations by @accelerate-specialist")
    print("=" * 80)


if __name__ == "__main__":
    main()
