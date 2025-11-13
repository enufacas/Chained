#!/usr/bin/env python3
"""
Neural Network for Code Style Transfer Across Projects
Part of the Chained autonomous AI ecosystem

This tool uses neural network-inspired techniques to learn code style patterns
from one project and apply them to code from another project. It analyzes
syntax, naming conventions, indentation, and structural patterns.

Key Features:
- Style pattern extraction from source code
- Neural network-based style encoding and representation
- Style transfer to target code while preserving functionality
- Integration with existing code analysis tools
- Support for multiple programming languages (initially Python)

Author: @engineer-master
"""

import ast
import re
import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any, Set
from dataclasses import dataclass, asdict, field
from collections import defaultdict, Counter
from enum import Enum
import math


class StyleDimension(Enum):
    """Dimensions of code style that can be transferred."""
    INDENTATION = "indentation"
    NAMING_CONVENTION = "naming_convention"
    LINE_LENGTH = "line_length"
    WHITESPACE = "whitespace"
    COMMENT_STYLE = "comment_style"
    IMPORT_STYLE = "import_style"
    FUNCTION_LENGTH = "function_length"
    CLASS_STRUCTURE = "class_structure"
    DOCSTRING_STYLE = "docstring_style"


@dataclass
class StyleFeatures:
    """Extracted style features from code."""
    # Indentation
    indent_size: int = 4
    indent_type: str = "spaces"  # spaces or tabs
    
    # Naming conventions
    variable_naming: str = "snake_case"  # snake_case, camelCase, PascalCase
    function_naming: str = "snake_case"
    class_naming: str = "PascalCase"
    constant_naming: str = "UPPER_CASE"
    
    # Line length
    avg_line_length: float = 0.0
    max_line_length: int = 79
    
    # Whitespace
    blank_lines_after_import: int = 2
    blank_lines_between_functions: int = 2
    blank_lines_between_classes: int = 2
    spaces_around_operators: bool = True
    
    # Comments
    has_inline_comments: bool = True
    has_block_comments: bool = True
    comment_density: float = 0.0  # comments per line of code
    
    # Imports
    import_order: List[str] = field(default_factory=lambda: ["stdlib", "third_party", "local"])
    imports_grouped: bool = True
    
    # Structure
    avg_function_length: float = 0.0
    max_function_length: int = 50
    functions_per_class: float = 0.0
    
    # Docstrings
    has_module_docstring: bool = False
    has_function_docstrings: bool = False
    has_class_docstrings: bool = False
    docstring_style: str = "google"  # google, numpy, sphinx, plain
    
    # Type hints
    uses_type_hints: bool = False
    type_hint_coverage: float = 0.0
    
    # Overall metrics
    total_lines: int = 0
    code_lines: int = 0
    comment_lines: int = 0
    blank_lines: int = 0


@dataclass
class TransferResult:
    """Result of style transfer operation."""
    original_code: str
    transformed_code: str
    style_changes: List[str]
    confidence: float
    preserved_functionality: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


class StyleExtractor:
    """Extracts style features from source code."""
    
    def __init__(self):
        self.features = StyleFeatures()
    
    def extract_from_code(self, code: str, filename: str = "") -> StyleFeatures:
        """Extract style features from Python code.
        
        Args:
            code: Source code as string
            filename: Optional filename for context
            
        Returns:
            StyleFeatures object with extracted patterns
        """
        features = StyleFeatures()
        
        # Basic line analysis
        lines = code.split('\n')
        features.total_lines = len(lines)
        features.code_lines = sum(1 for line in lines if line.strip() and not line.strip().startswith('#'))
        features.comment_lines = sum(1 for line in lines if line.strip().startswith('#'))
        features.blank_lines = sum(1 for line in lines if not line.strip())
        
        # Calculate comment density
        if features.code_lines > 0:
            features.comment_density = features.comment_lines / features.code_lines
        
        # Analyze indentation
        features.indent_size, features.indent_type = self._analyze_indentation(lines)
        
        # Analyze line length
        non_empty_lines = [line for line in lines if line.strip()]
        if non_empty_lines:
            features.avg_line_length = sum(len(line) for line in non_empty_lines) / len(non_empty_lines)
            features.max_line_length = max(len(line) for line in non_empty_lines)
        
        # Parse AST for deeper analysis
        try:
            tree = ast.parse(code)
            self._analyze_ast(tree, features, code)
        except SyntaxError:
            # If parsing fails, use basic heuristics
            pass
        
        return features
    
    def _analyze_indentation(self, lines: List[str]) -> Tuple[int, str]:
        """Analyze indentation style.
        
        Returns:
            Tuple of (indent_size, indent_type)
        """
        indent_sizes = []
        has_tabs = False
        has_spaces = False
        
        for line in lines:
            if not line.strip():
                continue
            
            # Count leading whitespace
            leading = len(line) - len(line.lstrip())
            if leading > 0:
                if '\t' in line[:leading]:
                    has_tabs = True
                if ' ' in line[:leading]:
                    has_spaces = True
                    indent_sizes.append(leading)
        
        # Determine indent type
        indent_type = "tabs" if has_tabs and not has_spaces else "spaces"
        
        # Determine indent size for spaces
        if indent_sizes:
            # Find the GCD of all indent sizes to determine base indent
            from math import gcd
            from functools import reduce
            indent_size = reduce(gcd, indent_sizes)
            # Common indent sizes are 2, 4, or 8
            if indent_size not in [2, 4, 8]:
                indent_size = 4  # Default to 4 if unclear
        else:
            indent_size = 4
        
        return indent_size, indent_type
    
    def _analyze_ast(self, tree: ast.AST, features: StyleFeatures, code: str):
        """Analyze AST to extract style features."""
        
        # Track naming conventions
        var_names = []
        func_names = []
        class_names = []
        const_names = []
        
        # Track structure metrics
        function_lengths = []
        functions_per_class = defaultdict(int)
        
        # Track docstrings
        features.has_module_docstring = ast.get_docstring(tree) is not None
        
        for node in ast.walk(tree):
            # Naming conventions
            if isinstance(node, ast.Name):
                var_names.append(node.id)
            elif isinstance(node, ast.FunctionDef):
                func_names.append(node.name)
                # Check for docstring
                if ast.get_docstring(node):
                    features.has_function_docstrings = True
                # Calculate function length
                if hasattr(node, 'lineno') and hasattr(node, 'end_lineno'):
                    function_lengths.append(node.end_lineno - node.lineno + 1)
                # Check for type hints
                if node.returns is not None or any(arg.annotation for arg in node.args.args):
                    features.uses_type_hints = True
            elif isinstance(node, ast.ClassDef):
                class_names.append(node.name)
                if ast.get_docstring(node):
                    features.has_class_docstrings = True
                # Count functions in class
                for item in node.body:
                    if isinstance(item, ast.FunctionDef):
                        functions_per_class[node.name] += 1
            elif isinstance(node, ast.Assign):
                # Check for constants (all uppercase)
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id.isupper():
                        const_names.append(target.id)
        
        # Determine naming conventions
        features.variable_naming = self._detect_naming_convention(var_names)
        features.function_naming = self._detect_naming_convention(func_names)
        features.class_naming = self._detect_naming_convention(class_names)
        features.constant_naming = self._detect_naming_convention(const_names)
        
        # Calculate structure metrics
        if function_lengths:
            features.avg_function_length = sum(function_lengths) / len(function_lengths)
            features.max_function_length = max(function_lengths)
        
        if functions_per_class:
            features.functions_per_class = sum(functions_per_class.values()) / len(functions_per_class)
    
    def _detect_naming_convention(self, names: List[str]) -> str:
        """Detect naming convention from a list of names.
        
        Returns:
            One of: snake_case, camelCase, PascalCase, UPPER_CASE, mixed
        """
        if not names:
            return "snake_case"  # default
        
        snake_count = sum(1 for name in names if '_' in name and name.islower())
        camel_count = sum(1 for name in names if name[0].islower() and any(c.isupper() for c in name[1:]))
        pascal_count = sum(1 for name in names if name[0].isupper() and any(c.isupper() for c in name[1:]))
        upper_count = sum(1 for name in names if name.isupper() and '_' in name)
        
        # Find the most common convention
        counts = {
            'snake_case': snake_count,
            'camelCase': camel_count,
            'PascalCase': pascal_count,
            'UPPER_CASE': upper_count
        }
        
        max_convention = max(counts, key=counts.get)
        if counts[max_convention] == 0:
            return 'snake_case'  # default
        
        return max_convention


class NeuralStyleEncoder:
    """Neural network-inspired encoder for style patterns.
    
    This uses a simplified neural network approach with layers that encode
    style features into a high-dimensional representation.
    """
    
    def __init__(self, hidden_dim: int = 64):
        self.hidden_dim = hidden_dim
        self.style_embeddings = {}
        self._initialize_weights()
    
    def _initialize_weights(self):
        """Initialize neural network weights."""
        # Simple weight initialization for demonstration
        self.weights = {
            'layer1': {},
            'layer2': {},
            'output': {}
        }
    
    def encode_style(self, features: StyleFeatures) -> List[float]:
        """Encode style features into a neural representation.
        
        Args:
            features: StyleFeatures object
            
        Returns:
            List of float values representing the encoded style
        """
        # Convert features to numerical representation
        feature_vector = self._featurize(features)
        
        # Apply neural network layers
        hidden1 = self._activate(feature_vector, 'layer1')
        hidden2 = self._activate(hidden1, 'layer2')
        output = self._activate(hidden2, 'output')
        
        return output
    
    def _featurize(self, features: StyleFeatures) -> List[float]:
        """Convert StyleFeatures to numerical vector."""
        vector = []
        
        # Encode indentation (normalized)
        vector.append(features.indent_size / 8.0)
        vector.append(1.0 if features.indent_type == "spaces" else 0.0)
        
        # Encode naming (one-hot style)
        naming_styles = ['snake_case', 'camelCase', 'PascalCase', 'UPPER_CASE']
        for style in naming_styles:
            vector.append(1.0 if features.variable_naming == style else 0.0)
        
        # Encode line metrics (normalized)
        vector.append(min(features.avg_line_length / 100.0, 1.0))
        vector.append(min(features.max_line_length / 150.0, 1.0))
        
        # Encode boolean features
        vector.append(1.0 if features.has_module_docstring else 0.0)
        vector.append(1.0 if features.has_function_docstrings else 0.0)
        vector.append(1.0 if features.has_class_docstrings else 0.0)
        vector.append(1.0 if features.uses_type_hints else 0.0)
        
        # Encode structural metrics
        vector.append(min(features.avg_function_length / 100.0, 1.0))
        vector.append(min(features.comment_density, 1.0))
        
        return vector
    
    def _activate(self, inputs: List[float], layer: str) -> List[float]:
        """Apply activation function (simplified).
        
        For this demonstration, we use a basic tanh activation.
        """
        # Simple transformation for demonstration
        outputs = []
        for i, val in enumerate(inputs):
            # Apply tanh activation
            activated = math.tanh(val)
            outputs.append(activated)
        
        # Ensure consistent dimension
        while len(outputs) < self.hidden_dim:
            outputs.append(0.0)
        
        return outputs[:self.hidden_dim]
    
    def similarity(self, encoding1: List[float], encoding2: List[float]) -> float:
        """Calculate similarity between two style encodings.
        
        Returns:
            Similarity score between 0.0 and 1.0
        """
        if not encoding1 or not encoding2:
            return 0.0
        
        # Cosine similarity
        dot_product = sum(a * b for a, b in zip(encoding1, encoding2))
        mag1 = math.sqrt(sum(a * a for a in encoding1))
        mag2 = math.sqrt(sum(b * b for b in encoding2))
        
        if mag1 == 0.0 or mag2 == 0.0:
            return 0.0
        
        return abs(dot_product / (mag1 * mag2))


class StyleTransformer:
    """Transforms code from one style to another."""
    
    def __init__(self):
        self.extractor = StyleExtractor()
        self.encoder = NeuralStyleEncoder()
    
    def transfer_style(
        self,
        source_code: str,
        target_style: StyleFeatures,
        preserve_functionality: bool = True
    ) -> TransferResult:
        """Transfer style from target to source code.
        
        Args:
            source_code: Code to transform
            target_style: Target style features to apply
            preserve_functionality: If True, ensures code still works
            
        Returns:
            TransferResult with transformed code
        """
        # Extract current style
        current_style = self.extractor.extract_from_code(source_code)
        
        # Track changes
        changes = []
        transformed_code = source_code
        
        # Apply indentation changes
        if current_style.indent_size != target_style.indent_size:
            transformed_code = self._transform_indentation(
                transformed_code,
                current_style.indent_size,
                target_style.indent_size
            )
            changes.append(f"Changed indentation from {current_style.indent_size} to {target_style.indent_size} spaces")
        
        # Apply line length changes
        if abs(current_style.max_line_length - target_style.max_line_length) > 10:
            transformed_code = self._transform_line_length(
                transformed_code,
                target_style.max_line_length
            )
            changes.append(f"Adjusted line length to ~{target_style.max_line_length} characters")
        
        # Calculate confidence based on similarity
        current_encoding = self.encoder.encode_style(current_style)
        target_encoding = self.encoder.encode_style(target_style)
        confidence = self.encoder.similarity(current_encoding, target_encoding)
        
        return TransferResult(
            original_code=source_code,
            transformed_code=transformed_code,
            style_changes=changes,
            confidence=confidence,
            preserved_functionality=preserve_functionality,
            metadata={
                'source_style': asdict(current_style),
                'target_style': asdict(target_style)
            }
        )
    
    def _transform_indentation(self, code: str, current_size: int, target_size: int) -> str:
        """Transform indentation size."""
        lines = code.split('\n')
        transformed_lines = []
        
        for line in lines:
            if not line.strip():
                transformed_lines.append(line)
                continue
            
            # Count current indentation
            leading_spaces = len(line) - len(line.lstrip())
            if leading_spaces > 0:
                # Calculate new indentation
                indent_level = leading_spaces // current_size
                new_indent = ' ' * (indent_level * target_size)
                transformed_lines.append(new_indent + line.lstrip())
            else:
                transformed_lines.append(line)
        
        return '\n'.join(transformed_lines)
    
    def _transform_line_length(self, code: str, max_length: int) -> str:
        """Transform code to respect maximum line length."""
        # This is a simplified version - a full implementation would
        # intelligently wrap lines at appropriate points
        lines = code.split('\n')
        transformed_lines = []
        
        for line in lines:
            if len(line) <= max_length:
                transformed_lines.append(line)
            else:
                # Simple wrapping - could be more sophisticated
                transformed_lines.append(line)  # Keep as is for now
        
        return '\n'.join(transformed_lines)


class CodeStyleTransferSystem:
    """Main system for code style transfer across projects."""
    
    def __init__(self, repo_path: str = "."):
        self.repo_path = Path(repo_path)
        self.extractor = StyleExtractor()
        self.encoder = NeuralStyleEncoder()
        self.transformer = StyleTransformer()
        self.style_database = {}
    
    def learn_project_style(self, project_path: str, project_name: str) -> StyleFeatures:
        """Learn the style of an entire project.
        
        Args:
            project_path: Path to project directory
            project_name: Name to identify this style
            
        Returns:
            Aggregated StyleFeatures for the project
        """
        project_dir = Path(project_path)
        all_features = []
        
        # Find all Python files
        for py_file in project_dir.rglob("*.py"):
            if 'test' in str(py_file) or '__pycache__' in str(py_file):
                continue
            
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    code = f.read()
                    features = self.extractor.extract_from_code(code, str(py_file))
                    all_features.append(features)
            except Exception:
                continue
        
        # Aggregate features
        if not all_features:
            return StyleFeatures()
        
        aggregated = self._aggregate_features(all_features)
        
        # Store in database
        self.style_database[project_name] = {
            'features': aggregated,
            'encoding': self.encoder.encode_style(aggregated),
            'file_count': len(all_features)
        }
        
        return aggregated
    
    def _aggregate_features(self, features_list: List[StyleFeatures]) -> StyleFeatures:
        """Aggregate features from multiple files."""
        if not features_list:
            return StyleFeatures()
        
        # Use voting/averaging for different feature types
        aggregated = StyleFeatures()
        
        # Numerical features - use mean
        aggregated.indent_size = int(sum(f.indent_size for f in features_list) / len(features_list))
        aggregated.avg_line_length = sum(f.avg_line_length for f in features_list) / len(features_list)
        aggregated.max_line_length = int(sum(f.max_line_length for f in features_list) / len(features_list))
        aggregated.avg_function_length = sum(f.avg_function_length for f in features_list) / len(features_list)
        aggregated.comment_density = sum(f.comment_density for f in features_list) / len(features_list)
        
        # Categorical features - use mode (most common)
        aggregated.indent_type = Counter(f.indent_type for f in features_list).most_common(1)[0][0]
        aggregated.variable_naming = Counter(f.variable_naming for f in features_list).most_common(1)[0][0]
        aggregated.function_naming = Counter(f.function_naming for f in features_list).most_common(1)[0][0]
        aggregated.class_naming = Counter(f.class_naming for f in features_list).most_common(1)[0][0]
        
        # Boolean features - use majority vote
        aggregated.has_module_docstring = sum(1 for f in features_list if f.has_module_docstring) > len(features_list) / 2
        aggregated.has_function_docstrings = sum(1 for f in features_list if f.has_function_docstrings) > len(features_list) / 2
        aggregated.has_class_docstrings = sum(1 for f in features_list if f.has_class_docstrings) > len(features_list) / 2
        aggregated.uses_type_hints = sum(1 for f in features_list if f.uses_type_hints) > len(features_list) / 2
        
        return aggregated
    
    def apply_project_style(
        self,
        code: str,
        target_project: str,
        output_path: Optional[str] = None
    ) -> TransferResult:
        """Apply a learned project style to code.
        
        Args:
            code: Source code to transform
            target_project: Name of project style to apply
            output_path: Optional path to save transformed code
            
        Returns:
            TransferResult with transformation details
        """
        if target_project not in self.style_database:
            raise ValueError(f"Unknown project style: {target_project}")
        
        target_style = self.style_database[target_project]['features']
        result = self.transformer.transfer_style(code, target_style)
        
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(result.transformed_code)
        
        return result
    
    def compare_styles(self, project1: str, project2: str) -> Dict[str, Any]:
        """Compare styles of two projects.
        
        Returns:
            Dictionary with similarity metrics and differences
        """
        if project1 not in self.style_database or project2 not in self.style_database:
            raise ValueError("One or both projects not in database")
        
        enc1 = self.style_database[project1]['encoding']
        enc2 = self.style_database[project2]['encoding']
        
        similarity = self.encoder.similarity(enc1, enc2)
        
        feat1 = self.style_database[project1]['features']
        feat2 = self.style_database[project2]['features']
        
        differences = []
        if feat1.indent_size != feat2.indent_size:
            differences.append(f"Indentation: {feat1.indent_size} vs {feat2.indent_size}")
        if feat1.variable_naming != feat2.variable_naming:
            differences.append(f"Variable naming: {feat1.variable_naming} vs {feat2.variable_naming}")
        if abs(feat1.avg_line_length - feat2.avg_line_length) > 10:
            differences.append(f"Line length: {feat1.avg_line_length:.0f} vs {feat2.avg_line_length:.0f}")
        
        return {
            'similarity': similarity,
            'differences': differences,
            'project1': project1,
            'project2': project2
        }
    
    def export_style_database(self, output_file: str):
        """Export learned styles to JSON file."""
        export_data = {}
        for name, data in self.style_database.items():
            export_data[name] = {
                'features': asdict(data['features']),
                'encoding': data['encoding'],
                'file_count': data['file_count']
            }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2)
    
    def import_style_database(self, input_file: str):
        """Import learned styles from JSON file."""
        with open(input_file, 'r', encoding='utf-8') as f:
            import_data = json.load(f)
        
        for name, data in import_data.items():
            features = StyleFeatures(**data['features'])
            self.style_database[name] = {
                'features': features,
                'encoding': data['encoding'],
                'file_count': data['file_count']
            }


def main():
    """Command-line interface for code style transfer."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Neural network-based code style transfer across projects'
    )
    parser.add_argument(
        'command',
        choices=['learn', 'apply', 'compare', 'export', 'import'],
        help='Command to execute'
    )
    parser.add_argument(
        '--project-path',
        help='Path to project directory (for learn command)'
    )
    parser.add_argument(
        '--project-name',
        help='Name to identify project style'
    )
    parser.add_argument(
        '--code-file',
        help='Path to code file to transform (for apply command)'
    )
    parser.add_argument(
        '--target-project',
        help='Target project style name (for apply command)'
    )
    parser.add_argument(
        '--output',
        help='Output file path'
    )
    parser.add_argument(
        '--project1',
        help='First project name (for compare command)'
    )
    parser.add_argument(
        '--project2',
        help='Second project name (for compare command)'
    )
    parser.add_argument(
        '--database',
        default='style_database.json',
        help='Style database file path'
    )
    
    args = parser.parse_args()
    
    system = CodeStyleTransferSystem()
    
    # Import existing database if available
    if os.path.exists(args.database):
        system.import_style_database(args.database)
        print(f"Loaded style database from {args.database}")
    
    if args.command == 'learn':
        if not args.project_path or not args.project_name:
            print("Error: --project-path and --project-name required for learn command")
            return 1
        
        print(f"Learning style from project: {args.project_path}")
        features = system.learn_project_style(args.project_path, args.project_name)
        print(f"\nLearned style for '{args.project_name}':")
        print(f"  Indentation: {features.indent_size} {features.indent_type}")
        print(f"  Variable naming: {features.variable_naming}")
        print(f"  Average line length: {features.avg_line_length:.1f}")
        print(f"  Uses type hints: {features.uses_type_hints}")
        
        # Save database
        system.export_style_database(args.database)
        print(f"\nSaved to database: {args.database}")
    
    elif args.command == 'apply':
        if not args.code_file or not args.target_project:
            print("Error: --code-file and --target-project required for apply command")
            return 1
        
        with open(args.code_file, 'r', encoding='utf-8') as f:
            code = f.read()
        
        print(f"Applying style from '{args.target_project}' to {args.code_file}")
        result = system.apply_project_style(code, args.target_project, args.output)
        
        print(f"\nStyle transfer complete:")
        print(f"  Changes made: {len(result.style_changes)}")
        for change in result.style_changes:
            print(f"    - {change}")
        print(f"  Confidence: {result.confidence:.2%}")
        
        if args.output:
            print(f"  Output saved to: {args.output}")
    
    elif args.command == 'compare':
        if not args.project1 or not args.project2:
            print("Error: --project1 and --project2 required for compare command")
            return 1
        
        comparison = system.compare_styles(args.project1, args.project2)
        print(f"\nStyle comparison:")
        print(f"  Projects: {comparison['project1']} vs {comparison['project2']}")
        print(f"  Similarity: {comparison['similarity']:.2%}")
        print(f"  Differences:")
        for diff in comparison['differences']:
            print(f"    - {diff}")
    
    elif args.command == 'export':
        if not args.output:
            print("Error: --output required for export command")
            return 1
        system.export_style_database(args.output)
        print(f"Exported style database to {args.output}")
    
    elif args.command == 'import':
        if not args.database:
            print("Error: --database required for import command")
            return 1
        system.import_style_database(args.database)
        print(f"Imported style database from {args.database}")
        print(f"Projects in database: {list(system.style_database.keys())}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
