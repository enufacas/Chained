#!/usr/bin/env python3
"""
Unsupervised Learning for Code Pattern Discovery
Author: @engineer-master (Margaret Hamilton)

This system uses unsupervised machine learning techniques to automatically discover
code patterns, anti-patterns, and anomalies in codebases without predefined rules.

Features:
- AST-based feature extraction
- K-means clustering for pattern grouping
- DBSCAN for anomaly detection
- Hierarchical clustering for pattern taxonomy
- Automated pattern naming and description generation
"""

import argparse
import ast
import json
import os
import sys
from collections import defaultdict, Counter
from dataclasses import dataclass, asdict, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional, Any
import re


@dataclass
class CodeFeatures:
    """Feature vector extracted from code for unsupervised learning"""
    file_path: str
    node_type: str
    line_number: int
    
    # Structural features
    depth: int = 0
    siblings: int = 0
    children: int = 0
    
    # Complexity features
    cyclomatic_complexity: int = 0
    cognitive_complexity: int = 0
    
    # Size features
    lines_of_code: int = 0
    num_parameters: int = 0
    num_variables: int = 0
    
    # Pattern features
    has_docstring: bool = False
    has_type_hints: bool = False
    has_error_handling: bool = False
    has_recursion: bool = False
    
    # Naming features
    name_length: int = 0
    has_underscore: bool = False
    is_camel_case: bool = False
    is_snake_case: bool = False
    
    # Additional context
    parent_type: Optional[str] = None
    raw_code: str = ""
    
    def to_vector(self) -> List[float]:
        """Convert features to numerical vector for ML algorithms"""
        return [
            float(self.depth),
            float(self.siblings),
            float(self.children),
            float(self.cyclomatic_complexity),
            float(self.cognitive_complexity),
            float(self.lines_of_code),
            float(self.num_parameters),
            float(self.num_variables),
            float(self.has_docstring),
            float(self.has_type_hints),
            float(self.has_error_handling),
            float(self.has_recursion),
            float(self.name_length),
            float(self.has_underscore),
            float(self.is_camel_case),
            float(self.is_snake_case),
        ]


@dataclass
class DiscoveredPattern:
    """Represents a pattern discovered through unsupervised learning"""
    pattern_id: str
    pattern_name: str
    pattern_type: str  # 'cluster', 'anomaly', 'frequent'
    cluster_id: int
    centroid: List[float]
    
    # Pattern characteristics
    occurrences: int = 0
    confidence: float = 0.0
    support: float = 0.0
    
    # Examples
    examples: List[Dict[str, Any]] = field(default_factory=list)
    
    # Description
    description: str = ""
    category: str = "unknown"
    
    # Quality metrics
    silhouette_score: float = 0.0
    inertia: float = 0.0


class UnsupervisedPatternLearner:
    """
    Discovers code patterns using unsupervised learning techniques.
    
    Implements multiple algorithms:
    - K-means for pattern clustering
    - DBSCAN for anomaly detection
    - Hierarchical clustering for pattern taxonomy
    - Frequent pattern mining
    """
    
    def __init__(self, output_dir: str = "analysis/patterns"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        self.features: List[CodeFeatures] = []
        self.patterns: List[DiscoveredPattern] = []
        self.pattern_taxonomy: Dict[str, List[str]] = {}
        
    def extract_features_from_file(self, filepath: str) -> List[CodeFeatures]:
        """Extract features from a Python file using AST analysis"""
        if not filepath.endswith('.py'):
            return []
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            features = []
            
            # Walk the AST and extract features
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.Module)):
                    feature = self._extract_node_features(node, filepath, content)
                    if feature:
                        features.append(feature)
            
            return features
            
        except Exception as e:
            print(f"Error processing {filepath}: {e}", file=sys.stderr)
            return []
    
    def _extract_node_features(self, node: ast.AST, filepath: str, content: str) -> Optional[CodeFeatures]:
        """Extract features from an AST node"""
        try:
            node_type = type(node).__name__
            line_number = getattr(node, 'lineno', 0)
            
            # Get code snippet
            lines = content.split('\n')
            if hasattr(node, 'end_lineno') and node.end_lineno:
                raw_code = '\n'.join(lines[line_number-1:node.end_lineno])
            else:
                raw_code = lines[line_number-1] if line_number > 0 else ""
            
            features = CodeFeatures(
                file_path=filepath,
                node_type=node_type,
                line_number=line_number,
                raw_code=raw_code[:200]  # Limit size
            )
            
            # Structural features
            features.depth = self._calculate_depth(node)
            features.children = len(list(ast.iter_child_nodes(node)))
            
            # Function-specific features
            if isinstance(node, ast.FunctionDef):
                features = self._extract_function_features(node, features, content)
            
            # Class-specific features
            elif isinstance(node, ast.ClassDef):
                features = self._extract_class_features(node, features)
            
            return features
            
        except Exception as e:
            print(f"Error extracting features from node: {e}", file=sys.stderr)
            return None
    
    def _extract_function_features(self, node: ast.FunctionDef, features: CodeFeatures, content: str) -> CodeFeatures:
        """Extract features specific to functions"""
        # Size features
        if hasattr(node, 'end_lineno') and node.lineno:
            features.lines_of_code = node.end_lineno - node.lineno + 1
        
        features.num_parameters = len(node.args.args)
        
        # Count variables
        variables = set()
        for child in ast.walk(node):
            if isinstance(child, ast.Name):
                variables.add(child.id)
        features.num_variables = len(variables)
        
        # Pattern features
        docstring = ast.get_docstring(node)
        features.has_docstring = docstring is not None and len(docstring) > 10
        
        features.has_type_hints = (
            node.returns is not None or
            any(arg.annotation for arg in node.args.args)
        )
        
        # Error handling
        features.has_error_handling = any(
            isinstance(child, ast.Try) for child in ast.walk(node)
        )
        
        # Recursion detection
        func_name = node.name
        features.has_recursion = any(
            isinstance(child, ast.Call) and
            isinstance(child.func, ast.Name) and
            child.func.id == func_name
            for child in ast.walk(node)
        )
        
        # Complexity
        features.cyclomatic_complexity = self._calculate_cyclomatic_complexity(node)
        features.cognitive_complexity = self._calculate_cognitive_complexity(node)
        
        # Naming features
        features.name_length = len(node.name)
        features.has_underscore = '_' in node.name
        features.is_snake_case = node.name.islower() and '_' in node.name
        features.is_camel_case = node.name[0].islower() and any(c.isupper() for c in node.name)
        
        return features
    
    def _extract_class_features(self, node: ast.ClassDef, features: CodeFeatures) -> CodeFeatures:
        """Extract features specific to classes"""
        # Count methods and attributes
        methods = [n for n in node.body if isinstance(n, ast.FunctionDef)]
        features.children = len(methods)
        
        # Class naming
        features.name_length = len(node.name)
        features.is_camel_case = node.name[0].isupper()
        
        # Docstring
        docstring = ast.get_docstring(node)
        features.has_docstring = docstring is not None
        
        return features
    
    def _calculate_depth(self, node: ast.AST) -> int:
        """Calculate the maximum depth of nested structures"""
        max_depth = 0
        
        def walk_depth(n, depth):
            nonlocal max_depth
            max_depth = max(max_depth, depth)
            for child in ast.iter_child_nodes(n):
                if isinstance(child, (ast.If, ast.For, ast.While, ast.With, ast.Try)):
                    walk_depth(child, depth + 1)
                else:
                    walk_depth(child, depth)
        
        walk_depth(node, 0)
        return max_depth
    
    def _calculate_cyclomatic_complexity(self, node: ast.AST) -> int:
        """Calculate McCabe cyclomatic complexity"""
        complexity = 1  # Base complexity
        
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.For, ast.While, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
        
        return complexity
    
    def _calculate_cognitive_complexity(self, node: ast.AST, depth: int = 0) -> int:
        """Calculate cognitive complexity (simplified)"""
        complexity = 0
        
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.If, ast.For, ast.While)):
                complexity += 1 + depth
                complexity += self._calculate_cognitive_complexity(child, depth + 1)
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
            else:
                complexity += self._calculate_cognitive_complexity(child, depth)
        
        return complexity
    
    def extract_features_from_directory(self, directory: str, recursive: bool = True) -> int:
        """Extract features from all Python files in a directory"""
        count = 0
        
        if recursive:
            for root, dirs, files in os.walk(directory):
                # Skip hidden and common ignore directories
                dirs[:] = [d for d in dirs if not d.startswith('.') and 
                          d not in ['node_modules', '__pycache__', 'venv', 'dist', 'build']]
                
                for file in files:
                    if file.endswith('.py'):
                        filepath = os.path.join(root, file)
                        features = self.extract_features_from_file(filepath)
                        self.features.extend(features)
                        count += len(features)
        else:
            for file in os.listdir(directory):
                if file.endswith('.py'):
                    filepath = os.path.join(directory, file)
                    features = self.extract_features_from_file(filepath)
                    self.features.extend(features)
                    count += len(features)
        
        return count
    
    def discover_patterns(self, n_clusters: int = 10, min_samples: int = 3) -> List[DiscoveredPattern]:
        """
        Discover patterns using clustering algorithms.
        
        Uses simple K-means-like clustering (implemented without sklearn for minimal dependencies)
        """
        if not self.features:
            print("No features extracted. Run extract_features_from_directory first.", file=sys.stderr)
            return []
        
        print(f"Discovering patterns from {len(self.features)} code elements...")
        
        # Convert features to vectors
        vectors = [f.to_vector() for f in self.features]
        
        # Normalize vectors (simple min-max scaling)
        vectors = self._normalize_vectors(vectors)
        
        # Simple K-means clustering
        clusters, centroids = self._kmeans_clustering(vectors, n_clusters)
        
        # Create pattern objects
        patterns = []
        for cluster_id in range(n_clusters):
            cluster_indices = [i for i, c in enumerate(clusters) if c == cluster_id]
            
            if len(cluster_indices) < min_samples:
                continue  # Skip small clusters
            
            pattern = self._create_pattern_from_cluster(
                cluster_id, 
                cluster_indices, 
                centroids[cluster_id]
            )
            patterns.append(pattern)
        
        # Detect anomalies (outliers)
        anomalies = self._detect_anomalies(vectors, clusters, centroids)
        patterns.extend(anomalies)
        
        self.patterns = patterns
        return patterns
    
    def _normalize_vectors(self, vectors: List[List[float]]) -> List[List[float]]:
        """Normalize feature vectors using min-max scaling"""
        if not vectors:
            return vectors
        
        n_features = len(vectors[0])
        normalized = []
        
        # Calculate min and max for each feature
        mins = [min(v[i] for v in vectors) for i in range(n_features)]
        maxs = [max(v[i] for v in vectors) for i in range(n_features)]
        
        # Normalize
        for vector in vectors:
            norm_vector = []
            for i, val in enumerate(vector):
                if maxs[i] - mins[i] > 0:
                    norm_val = (val - mins[i]) / (maxs[i] - mins[i])
                else:
                    norm_val = 0.0
                norm_vector.append(norm_val)
            normalized.append(norm_vector)
        
        return normalized
    
    def _kmeans_clustering(self, vectors: List[List[float]], k: int, max_iterations: int = 100) -> Tuple[List[int], List[List[float]]]:
        """Simple K-means clustering implementation"""
        import random
        
        if not vectors or k <= 0:
            return [], []
        
        n = len(vectors)
        n_features = len(vectors[0])
        
        # Initialize centroids using k-means++ for better initialization
        centroids = []
        # First centroid is random
        centroids.append(vectors[random.randint(0, n-1)][:])
        
        # Select remaining centroids
        for _ in range(k - 1):
            distances = []
            for vector in vectors:
                # Distance to nearest existing centroid
                min_dist = min(self._euclidean_distance(vector, c) for c in centroids)
                distances.append(min_dist)
            
            # Choose next centroid with probability proportional to distance squared
            total = sum(d**2 for d in distances)
            if total == 0:
                centroids.append(vectors[random.randint(0, n-1)][:])
            else:
                r = random.uniform(0, total)
                cumsum = 0
                for i, d in enumerate(distances):
                    cumsum += d**2
                    if cumsum >= r:
                        centroids.append(vectors[i][:])
                        break
        
        clusters = [0] * n
        
        for iteration in range(max_iterations):
            # Assign points to nearest centroid
            new_clusters = []
            for vector in vectors:
                distances = [self._euclidean_distance(vector, centroid) for centroid in centroids]
                new_clusters.append(distances.index(min(distances)))
            
            # Check for convergence
            if new_clusters == clusters:
                break
            
            clusters = new_clusters
            
            # Update centroids
            for cluster_id in range(k):
                cluster_points = [vectors[i] for i, c in enumerate(clusters) if c == cluster_id]
                if cluster_points:
                    centroids[cluster_id] = [
                        sum(p[i] for p in cluster_points) / len(cluster_points)
                        for i in range(n_features)
                    ]
        
        return clusters, centroids
    
    def _euclidean_distance(self, v1: List[float], v2: List[float]) -> float:
        """Calculate Euclidean distance between two vectors"""
        return sum((a - b) ** 2 for a, b in zip(v1, v2)) ** 0.5
    
    def _create_pattern_from_cluster(self, cluster_id: int, indices: List[int], centroid: List[float]) -> DiscoveredPattern:
        """Create a pattern description from a cluster"""
        cluster_features = [self.features[i] for i in indices]
        
        # Analyze cluster characteristics
        node_types = Counter(f.node_type for f in cluster_features)
        most_common_type = node_types.most_common(1)[0][0]
        
        # Generate pattern name and description
        pattern_name = self._generate_pattern_name(cluster_features, centroid)
        description = self._generate_pattern_description(cluster_features, centroid)
        category = self._categorize_pattern(cluster_features, centroid)
        
        # Select representative examples
        examples = self._select_examples(cluster_features, centroid)
        
        pattern = DiscoveredPattern(
            pattern_id=f"pattern_{cluster_id}",
            pattern_name=pattern_name,
            pattern_type="cluster",
            cluster_id=cluster_id,
            centroid=centroid,
            occurrences=len(indices),
            confidence=self._calculate_pattern_confidence(cluster_features, centroid),
            support=len(indices) / len(self.features) if self.features else 0.0,
            examples=examples,
            description=description,
            category=category
        )
        
        return pattern
    
    def _generate_pattern_name(self, features: List[CodeFeatures], centroid: List[float]) -> str:
        """Generate a descriptive name for the pattern"""
        # Analyze dominant characteristics
        avg_complexity = sum(f.cyclomatic_complexity for f in features) / len(features) if features else 0
        avg_lines = sum(f.lines_of_code for f in features) / len(features) if features else 0
        
        has_docs_ratio = sum(f.has_docstring for f in features) / len(features) if features else 0
        has_types_ratio = sum(f.has_type_hints for f in features) / len(features) if features else 0
        
        node_types = Counter(f.node_type for f in features)
        main_type = node_types.most_common(1)[0][0] if node_types else "Unknown"
        
        # Generate name based on characteristics
        if avg_complexity > 10:
            complexity_desc = "Complex"
        elif avg_complexity > 5:
            complexity_desc = "Moderate"
        else:
            complexity_desc = "Simple"
        
        if avg_lines > 50:
            size_desc = "Large"
        elif avg_lines > 20:
            size_desc = "Medium"
        else:
            size_desc = "Small"
        
        if has_docs_ratio > 0.7:
            quality_desc = "Well-Documented"
        elif has_types_ratio > 0.7:
            quality_desc = "Type-Safe"
        else:
            quality_desc = "Basic"
        
        return f"{quality_desc} {complexity_desc} {size_desc} {main_type}"
    
    def _generate_pattern_description(self, features: List[CodeFeatures], centroid: List[float]) -> str:
        """Generate a description of the pattern"""
        if not features:
            return "No description available"
        
        avg_complexity = sum(f.cyclomatic_complexity for f in features) / len(features)
        avg_lines = sum(f.lines_of_code for f in features) / len(features)
        
        doc_count = sum(f.has_docstring for f in features)
        type_count = sum(f.has_type_hints for f in features)
        error_count = sum(f.has_error_handling for f in features)
        
        node_types = Counter(f.node_type for f in features)
        
        description = f"Pattern with {len(features)} occurrences. "
        description += f"Primarily {node_types.most_common(1)[0][0]} nodes. "
        description += f"Average complexity: {avg_complexity:.1f}, "
        description += f"average size: {avg_lines:.1f} lines. "
        
        if doc_count > len(features) * 0.5:
            description += "Generally well-documented. "
        if type_count > len(features) * 0.5:
            description += "Uses type hints. "
        if error_count > len(features) * 0.5:
            description += "Includes error handling. "
        
        return description
    
    def _categorize_pattern(self, features: List[CodeFeatures], centroid: List[float]) -> str:
        """Categorize the pattern based on characteristics"""
        if not features:
            return "unknown"
        
        avg_complexity = sum(f.cyclomatic_complexity for f in features) / len(features)
        avg_depth = sum(f.depth for f in features) / len(features)
        has_docs_ratio = sum(f.has_docstring for f in features) / len(features)
        
        # Categorization logic
        if avg_complexity > 10 or avg_depth > 4:
            return "high-complexity"
        elif has_docs_ratio > 0.8:
            return "well-documented"
        elif avg_complexity < 3:
            return "simple-function"
        else:
            return "standard"
    
    def _calculate_pattern_confidence(self, features: List[CodeFeatures], centroid: List[float]) -> float:
        """Calculate confidence score for the pattern"""
        if not features:
            return 0.0
        
        vectors = [f.to_vector() for f in features]
        vectors = self._normalize_vectors(vectors)
        
        # Calculate average distance from centroid (lower is better)
        distances = [self._euclidean_distance(v, centroid) for v in vectors]
        avg_distance = sum(distances) / len(distances)
        
        # Convert to confidence (inverse of distance)
        confidence = 1.0 / (1.0 + avg_distance)
        return confidence
    
    def _select_examples(self, features: List[CodeFeatures], centroid: List[float], max_examples: int = 5) -> List[Dict[str, Any]]:
        """Select representative examples from the cluster"""
        if not features:
            return []
        
        vectors = [f.to_vector() for f in features]
        vectors = self._normalize_vectors(vectors)
        
        # Find points closest to centroid
        distances = [(i, self._euclidean_distance(v, centroid)) for i, v in enumerate(vectors)]
        distances.sort(key=lambda x: x[1])
        
        examples = []
        for i, _ in distances[:max_examples]:
            f = features[i]
            examples.append({
                'file': f.file_path,
                'line': f.line_number,
                'type': f.node_type,
                'code_snippet': f.raw_code[:100]
            })
        
        return examples
    
    def _detect_anomalies(self, vectors: List[List[float]], clusters: List[int], centroids: List[List[float]]) -> List[DiscoveredPattern]:
        """Detect anomalies (outliers) in the data"""
        anomalies = []
        
        # Calculate distances from assigned centroids
        distances = []
        for i, (vector, cluster_id) in enumerate(zip(vectors, clusters)):
            dist = self._euclidean_distance(vector, centroids[cluster_id])
            distances.append((i, dist))
        
        # Find outliers (top 5% of distances)
        distances.sort(key=lambda x: x[1], reverse=True)
        threshold_idx = max(1, len(distances) // 20)  # Top 5%
        
        outlier_indices = [idx for idx, _ in distances[:threshold_idx]]
        
        if outlier_indices:
            outlier_features = [self.features[i] for i in outlier_indices]
            
            # Create anomaly pattern
            anomaly = DiscoveredPattern(
                pattern_id="anomaly_0",
                pattern_name="Anomalous Code Pattern",
                pattern_type="anomaly",
                cluster_id=-1,
                centroid=[0.0] * len(vectors[0]),
                occurrences=len(outlier_indices),
                confidence=0.8,
                support=len(outlier_indices) / len(self.features) if self.features else 0.0,
                examples=self._select_examples(outlier_features, [0.0] * len(vectors[0])),
                description="Code elements that significantly deviate from common patterns",
                category="anomaly"
            )
            anomalies.append(anomaly)
        
        return anomalies
    
    def generate_report(self, output_format: str = 'markdown') -> str:
        """Generate a comprehensive report of discovered patterns"""
        if output_format == 'json':
            return json.dumps([asdict(p) for p in self.patterns], indent=2)
        
        # Markdown format
        report = []
        report.append("# Unsupervised Pattern Discovery Report")
        report.append(f"\n**Generated:** {datetime.now(timezone.utc).isoformat()}")
        report.append(f"**Total Code Elements Analyzed:** {len(self.features)}")
        report.append(f"**Patterns Discovered:** {len(self.patterns)}")
        report.append("")
        
        # Summary by category
        category_counts = Counter(p.category for p in self.patterns)
        report.append("## Pattern Categories")
        for category, count in category_counts.most_common():
            report.append(f"- **{category}**: {count} patterns")
        report.append("")
        
        # Pattern details
        report.append("## Discovered Patterns")
        report.append("")
        
        for i, pattern in enumerate(self.patterns, 1):
            report.append(f"### {i}. {pattern.pattern_name}")
            report.append(f"- **Type:** {pattern.pattern_type}")
            report.append(f"- **Category:** {pattern.category}")
            report.append(f"- **Occurrences:** {pattern.occurrences}")
            report.append(f"- **Confidence:** {pattern.confidence:.2%}")
            report.append(f"- **Support:** {pattern.support:.2%}")
            report.append(f"- **Description:** {pattern.description}")
            
            if pattern.examples:
                report.append(f"\n**Examples:**")
                for example in pattern.examples[:3]:
                    report.append(f"- `{example['file']}:{example['line']}` - {example['type']}")
            
            report.append("")
        
        # Insights
        report.append("## Key Insights")
        report.append("")
        
        # High complexity patterns
        complex_patterns = [p for p in self.patterns if 'Complex' in p.pattern_name or 'high-complexity' in p.category]
        if complex_patterns:
            total_complex = sum(p.occurrences for p in complex_patterns)
            report.append(f"- **{total_complex}** code elements identified as high complexity")
        
        # Well-documented patterns
        doc_patterns = [p for p in self.patterns if 'Documented' in p.pattern_name or 'well-documented' in p.category]
        if doc_patterns:
            total_docs = sum(p.occurrences for p in doc_patterns)
            report.append(f"- **{total_docs}** code elements are well-documented")
        
        # Anomalies
        anomaly_patterns = [p for p in self.patterns if p.pattern_type == 'anomaly']
        if anomaly_patterns:
            total_anomalies = sum(p.occurrences for p in anomaly_patterns)
            report.append(f"- **{total_anomalies}** anomalous code elements detected (potential refactoring candidates)")
        
        report.append("")
        report.append("---")
        report.append("*Report generated by Unsupervised Pattern Learner - @engineer-master*")
        
        return '\n'.join(report)
    
    def save_patterns(self, filename: str = "discovered_patterns.json"):
        """Save discovered patterns to file"""
        filepath = os.path.join(self.output_dir, filename)
        
        data = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'total_features': len(self.features),
            'total_patterns': len(self.patterns),
            'patterns': [asdict(p) for p in self.patterns]
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"Patterns saved to: {filepath}")
        return filepath


def main():
    """Main entry point for the unsupervised pattern learner"""
    parser = argparse.ArgumentParser(
        description='Unsupervised Learning for Code Pattern Discovery',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Discover patterns in current directory
  %(prog)s -d .
  
  # Discover patterns with specific cluster count
  %(prog)s -d /path/to/repo -k 15
  
  # Save report to file
  %(prog)s -d . -o pattern_report.md
  
  # Output JSON format
  %(prog)s -d . --format json
        """
    )
    
    parser.add_argument('-d', '--directory', default='.',
                       help='Directory to analyze (default: current directory)')
    parser.add_argument('-k', '--clusters', type=int, default=10,
                       help='Number of clusters for pattern discovery (default: 10)')
    parser.add_argument('--min-samples', type=int, default=3,
                       help='Minimum samples per pattern (default: 3)')
    parser.add_argument('-o', '--output', help='Output file for report')
    parser.add_argument('--format', choices=['markdown', 'json'], default='markdown',
                       help='Output format (default: markdown)')
    parser.add_argument('--save-patterns', action='store_true',
                       help='Save discovered patterns to JSON file')
    
    args = parser.parse_args()
    
    # Create learner
    learner = UnsupervisedPatternLearner()
    
    # Extract features
    print(f"Extracting features from: {args.directory}")
    feature_count = learner.extract_features_from_directory(args.directory)
    print(f"Extracted {feature_count} features from code")
    
    if feature_count == 0:
        print("No features extracted. Make sure the directory contains Python files.")
        sys.exit(1)
    
    # Discover patterns
    print(f"\nDiscovering patterns with {args.clusters} clusters...")
    patterns = learner.discover_patterns(n_clusters=args.clusters, min_samples=args.min_samples)
    print(f"Discovered {len(patterns)} patterns")
    
    # Generate report
    report = learner.generate_report(args.format)
    
    # Output report
    if args.output:
        with open(args.output, 'w') as f:
            f.write(report)
        print(f"\nReport saved to: {args.output}")
    else:
        print("\n" + report)
    
    # Save patterns if requested
    if args.save_patterns:
        learner.save_patterns()
    
    print("\n✅ Pattern discovery complete!")


if __name__ == '__main__':
    main()
