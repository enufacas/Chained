#!/usr/bin/env python3
"""
Issue Clustering System for Automatic Categorization
Author: @engineer-master (Margaret Hamilton)

A rigorous machine learning system for automatically clustering and categorizing
similar issues using TF-IDF, K-means clustering, and hierarchical analysis.

This system builds upon the semantic similarity engine to provide:
- Automatic issue categorization
- Similar issue detection
- Category taxonomy generation
- Label suggestion
- Cluster quality metrics

Inspired by Margaret Hamilton's systematic approach to engineering reliable systems.
"""

import json
import os
import sys
import math
import argparse
from collections import defaultdict, Counter
from dataclasses import dataclass, asdict, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Set, Any
import re


@dataclass
class IssueData:
    """Represents an issue for clustering"""
    issue_number: int
    title: str
    body: str
    labels: List[str]
    state: str = "open"
    created_at: Optional[str] = None
    author: Optional[str] = None
    
    def to_dict(self):
        return asdict(self)
    
    @staticmethod
    def from_dict(data: dict) -> 'IssueData':
        return IssueData(**data)


@dataclass
class IssueCluster:
    """Represents a cluster of similar issues"""
    cluster_id: int
    cluster_name: str
    centroid: List[float]
    issue_ids: List[int]
    size: int
    suggested_labels: List[str]
    common_terms: List[str]
    category: str
    confidence: float
    description: str
    
    def to_dict(self):
        return asdict(self)


@dataclass
class ClusteringMetrics:
    """Quality metrics for clustering results"""
    silhouette_score: float
    inertia: float
    num_clusters: int
    num_issues: int
    avg_cluster_size: float
    cluster_sizes: List[int]
    label_distribution: Dict[str, int]
    
    def to_dict(self):
        return asdict(self)


class IssueClusteringSystem:
    """
    Advanced clustering system for automatic issue categorization.
    
    Uses a combination of:
    - TF-IDF for text representation
    - K-means for primary clustering
    - Hierarchical clustering for taxonomy
    - Label co-occurrence for category naming
    - Cosine similarity for quality assessment
    """
    
    # Common stop words (enhanced for issue text)
    STOP_WORDS = {
        'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from',
        'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the',
        'to', 'was', 'will', 'with', 'this', 'but', 'they', 'have', 'had',
        'what', 'when', 'where', 'who', 'which', 'why', 'how', 'should',
        'would', 'could', 'can', 'do', 'does', 'did', 'been', 'being',
        'am', 'an', 'the', 'or', 'not', 'we', 'us', 'our', 'ours'
    }
    
    # Common technical terms that should be kept
    TECHNICAL_TERMS = {
        'api', 'bug', 'fix', 'error', 'test', 'docs', 'ci', 'cd',
        'performance', 'security', 'feature', 'enhancement', 'refactor',
        'database', 'cache', 'auth', 'authentication', 'authorization',
        'endpoint', 'query', 'workflow', 'pipeline', 'deploy', 'deployment'
    }
    
    def __init__(self, output_dir: str = "analysis/clustering"):
        """
        Initialize the issue clustering system.
        
        Args:
            output_dir: Directory for output files
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.issues: List[IssueData] = []
        self.clusters: List[IssueCluster] = []
        self.document_terms: List[Set[str]] = []
        self.idf_scores: Dict[str, float] = {}
        self.tfidf_vectors: List[Dict[str, float]] = []
        self.metrics: Optional[ClusteringMetrics] = None
        
    def load_issues_from_github(self, issues_data: List[Dict[str, Any]]):
        """
        Load issues from GitHub API response format.
        
        Args:
            issues_data: List of issue dictionaries from GitHub API
        """
        self.issues = []
        for issue_dict in issues_data:
            try:
                issue = IssueData(
                    issue_number=issue_dict.get('number', 0),
                    title=issue_dict.get('title', ''),
                    body=issue_dict.get('body', '') or '',
                    labels=[label.get('name', '') for label in issue_dict.get('labels', [])],
                    state=issue_dict.get('state', 'open'),
                    created_at=issue_dict.get('created_at'),
                    author=issue_dict.get('user', {}).get('login')
                )
                self.issues.append(issue)
            except Exception as e:
                print(f"Error loading issue: {e}", file=sys.stderr)
                continue
        
        print(f"Loaded {len(self.issues)} issues for clustering")
    
    def load_issues_from_file(self, filepath: str):
        """
        Load issues from JSON file.
        
        Args:
            filepath: Path to JSON file with issues
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Handle different JSON structures
            if isinstance(data, list):
                issues_list = data
            elif isinstance(data, dict) and 'issues' in data:
                issues_list = data['issues']
            else:
                print("Invalid JSON structure", file=sys.stderr)
                return
            
            self.load_issues_from_github(issues_list)
            
        except Exception as e:
            print(f"Error loading issues from file: {e}", file=sys.stderr)
    
    def _tokenize(self, text: str) -> List[str]:
        """
        Tokenize text into normalized tokens.
        
        Args:
            text: Input text
            
        Returns:
            List of tokens
        """
        if not text:
            return []
        
        # Convert to lowercase
        text = text.lower()
        
        # Remove URLs
        text = re.sub(r'https?://\S+', '', text)
        
        # Remove special characters, keep alphanumeric and spaces
        text = re.sub(r'[^a-z0-9\s]', ' ', text)
        
        # Split into tokens
        tokens = text.split()
        
        # Filter stop words but keep technical terms
        tokens = [
            t for t in tokens 
            if (len(t) > 2 and t not in self.STOP_WORDS) or t in self.TECHNICAL_TERMS
        ]
        
        return tokens
    
    def _calculate_term_frequency(self, tokens: List[str]) -> Dict[str, float]:
        """Calculate normalized term frequency."""
        if not tokens:
            return {}
        
        term_count = Counter(tokens)
        max_count = max(term_count.values())
        
        # Normalize by max frequency
        tf = {term: count / max_count for term, count in term_count.items()}
        
        return tf
    
    def _calculate_idf(self):
        """Calculate inverse document frequency for all terms."""
        if not self.document_terms:
            return
        
        n_documents = len(self.document_terms)
        
        # Count document frequency
        doc_freq = defaultdict(int)
        for doc_terms in self.document_terms:
            for term in doc_terms:
                doc_freq[term] += 1
        
        # Calculate IDF with smoothing
        self.idf_scores = {}
        for term, df in doc_freq.items():
            self.idf_scores[term] = math.log((n_documents + 1) / (df + 1)) + 1
    
    def _calculate_tfidf_vector(self, tokens: List[str]) -> Dict[str, float]:
        """Calculate TF-IDF vector for document."""
        tf = self._calculate_term_frequency(tokens)
        
        tfidf = {}
        for term, tf_score in tf.items():
            idf_score = self.idf_scores.get(term, 0)
            tfidf[term] = tf_score * idf_score
        
        return tfidf
    
    def _build_tfidf_index(self):
        """Build TF-IDF index for all issues."""
        if not self.issues:
            return
        
        print("Building TF-IDF index...")
        
        # Tokenize all documents
        self.document_terms = []
        for issue in self.issues:
            combined_text = f"{issue.title} {issue.body}"
            tokens = self._tokenize(combined_text)
            self.document_terms.append(set(tokens))
        
        # Calculate IDF scores
        self._calculate_idf()
        
        # Calculate TF-IDF vectors
        self.tfidf_vectors = []
        for issue in self.issues:
            combined_text = f"{issue.title} {issue.body}"
            tokens = self._tokenize(combined_text)
            tfidf_vector = self._calculate_tfidf_vector(tokens)
            self.tfidf_vectors.append(tfidf_vector)
        
        print(f"Built index with {len(self.idf_scores)} unique terms")
    
    def _normalize_vectors(self, vectors: List[Dict[str, float]]) -> List[List[float]]:
        """
        Convert sparse TF-IDF vectors to normalized dense vectors.
        
        Args:
            vectors: List of sparse TF-IDF vectors
            
        Returns:
            List of normalized dense vectors
        """
        if not vectors:
            return []
        
        # Get all unique terms
        all_terms = sorted(set(term for vec in vectors for term in vec.keys()))
        term_to_idx = {term: idx for idx, term in enumerate(all_terms)}
        
        # Convert to dense vectors
        dense_vectors = []
        for vec in vectors:
            dense = [0.0] * len(all_terms)
            for term, value in vec.items():
                if term in term_to_idx:
                    dense[term_to_idx[term]] = value
            dense_vectors.append(dense)
        
        # Normalize using L2 norm
        normalized = []
        for vec in dense_vectors:
            norm = math.sqrt(sum(x**2 for x in vec))
            if norm > 0:
                normalized.append([x / norm for x in vec])
            else:
                normalized.append(vec)
        
        return normalized
    
    def _euclidean_distance(self, v1: List[float], v2: List[float]) -> float:
        """Calculate Euclidean distance between vectors."""
        return math.sqrt(sum((a - b) ** 2 for a, b in zip(v1, v2)))
    
    def _cosine_similarity(self, v1: List[float], v2: List[float]) -> float:
        """Calculate cosine similarity between vectors."""
        if not v1 or not v2:
            return 0.0
        
        dot_product = sum(a * b for a, b in zip(v1, v2))
        magnitude1 = math.sqrt(sum(x**2 for x in v1))
        magnitude2 = math.sqrt(sum(x**2 for x in v2))
        
        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0
        
        return dot_product / (magnitude1 * magnitude2)
    
    def _kmeans_clustering(
        self, 
        vectors: List[List[float]], 
        k: int, 
        max_iterations: int = 100
    ) -> Tuple[List[int], List[List[float]]]:
        """
        K-means clustering implementation with K-means++ initialization.
        
        Args:
            vectors: List of feature vectors
            k: Number of clusters
            max_iterations: Maximum iterations
            
        Returns:
            Tuple of (cluster assignments, centroids)
        """
        import random
        
        if not vectors or k <= 0:
            return [], []
        
        n = len(vectors)
        n_features = len(vectors[0])
        
        # K-means++ initialization
        centroids = []
        centroids.append(vectors[random.randint(0, n-1)][:])
        
        for _ in range(k - 1):
            distances = []
            for vector in vectors:
                min_dist = min(self._euclidean_distance(vector, c) for c in centroids)
                distances.append(min_dist)
            
            # Select next centroid proportional to distance squared
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
        
        # K-means iterations
        for iteration in range(max_iterations):
            # Assign to nearest centroid
            new_clusters = []
            for vector in vectors:
                distances = [self._euclidean_distance(vector, centroid) for centroid in centroids]
                new_clusters.append(distances.index(min(distances)))
            
            # Check convergence
            if new_clusters == clusters:
                print(f"K-means converged in {iteration + 1} iterations")
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
    
    def _calculate_silhouette_score(
        self, 
        vectors: List[List[float]], 
        clusters: List[int]
    ) -> float:
        """
        Calculate average silhouette score for clustering quality.
        
        Args:
            vectors: List of feature vectors
            clusters: Cluster assignments
            
        Returns:
            Average silhouette score (-1 to 1, higher is better)
        """
        if len(set(clusters)) < 2:
            return 0.0
        
        n = len(vectors)
        silhouette_scores = []
        
        for i in range(n):
            cluster_i = clusters[i]
            
            # Calculate average distance to points in same cluster (a)
            same_cluster = [j for j in range(n) if clusters[j] == cluster_i and j != i]
            if not same_cluster:
                continue
            
            a = sum(self._euclidean_distance(vectors[i], vectors[j]) for j in same_cluster) / len(same_cluster)
            
            # Calculate average distance to nearest other cluster (b)
            other_clusters = set(clusters) - {cluster_i}
            b_scores = []
            
            for other_cluster in other_clusters:
                other_points = [j for j in range(n) if clusters[j] == other_cluster]
                if other_points:
                    b_other = sum(self._euclidean_distance(vectors[i], vectors[j]) for j in other_points) / len(other_points)
                    b_scores.append(b_other)
            
            if not b_scores:
                continue
            
            b = min(b_scores)
            
            # Calculate silhouette score
            s = (b - a) / max(a, b) if max(a, b) > 0 else 0
            silhouette_scores.append(s)
        
        return sum(silhouette_scores) / len(silhouette_scores) if silhouette_scores else 0.0
    
    def _generate_cluster_name(
        self, 
        cluster_issues: List[IssueData], 
        cluster_tokens: List[str]
    ) -> str:
        """
        Generate descriptive name for cluster.
        
        Args:
            cluster_issues: Issues in cluster
            cluster_tokens: Common tokens in cluster
            
        Returns:
            Cluster name
        """
        # Count labels
        label_counts = Counter()
        for issue in cluster_issues:
            label_counts.update(issue.labels)
        
        # Get most common labels
        common_labels = [label for label, count in label_counts.most_common(3) if count > 1]
        
        # Get most common terms (excluding stop words)
        term_counts = Counter(cluster_tokens)
        common_terms = [term for term, count in term_counts.most_common(5) if count > 1]
        
        # Generate name
        if common_labels:
            return f"{common_labels[0].title()} Issues"
        elif common_terms:
            return f"{common_terms[0].title()}-Related Issues"
        else:
            return "Miscellaneous Issues"
    
    def _categorize_cluster(self, cluster_issues: List[IssueData]) -> str:
        """
        Determine category of cluster based on labels and content.
        
        Args:
            cluster_issues: Issues in cluster
            
        Returns:
            Category name
        """
        # Analyze labels
        all_labels = [label for issue in cluster_issues for label in issue.labels]
        label_counts = Counter(all_labels)
        
        # Category mapping
        category_keywords = {
            'bug': ['bug', 'error', 'fix', 'broken', 'issue'],
            'feature': ['feature', 'enhancement', 'request', 'add'],
            'documentation': ['docs', 'documentation', 'readme', 'guide'],
            'performance': ['performance', 'slow', 'optimization', 'speed'],
            'security': ['security', 'vulnerability', 'cve', 'exploit'],
            'testing': ['test', 'testing', 'coverage', 'qa'],
            'ci/cd': ['ci', 'cd', 'workflow', 'pipeline', 'deployment'],
            'refactor': ['refactor', 'cleanup', 'technical-debt', 'code-quality']
        }
        
        # Score categories
        category_scores = defaultdict(int)
        for label, count in label_counts.items():
            label_lower = label.lower()
            for category, keywords in category_keywords.items():
                if any(kw in label_lower for kw in keywords):
                    category_scores[category] += count
        
        # Return highest scoring category
        if category_scores:
            return max(category_scores.items(), key=lambda x: x[1])[0]
        else:
            return 'general'
    
    def perform_clustering(
        self, 
        n_clusters: int = 5, 
        min_cluster_size: int = 2
    ) -> List[IssueCluster]:
        """
        Perform K-means clustering on issues.
        
        Args:
            n_clusters: Target number of clusters
            min_cluster_size: Minimum issues per cluster
            
        Returns:
            List of issue clusters
        """
        if not self.issues:
            print("No issues loaded. Use load_issues_from_file() first.", file=sys.stderr)
            return []
        
        if len(self.issues) < n_clusters:
            print(f"Warning: Only {len(self.issues)} issues, using {len(self.issues)} clusters")
            n_clusters = len(self.issues)
        
        # Build TF-IDF index
        self._build_tfidf_index()
        
        # Convert to normalized vectors
        print(f"Clustering {len(self.issues)} issues into {n_clusters} clusters...")
        normalized_vectors = self._normalize_vectors(self.tfidf_vectors)
        
        # Perform K-means clustering
        cluster_assignments, centroids = self._kmeans_clustering(normalized_vectors, n_clusters)
        
        # Calculate quality metrics
        silhouette = self._calculate_silhouette_score(normalized_vectors, cluster_assignments)
        
        # Calculate inertia (sum of squared distances to centroids)
        inertia = 0.0
        for i, (vector, cluster_id) in enumerate(zip(normalized_vectors, cluster_assignments)):
            inertia += self._euclidean_distance(vector, centroids[cluster_id]) ** 2
        
        print(f"Silhouette score: {silhouette:.3f}")
        print(f"Inertia: {inertia:.3f}")
        
        # Create cluster objects
        self.clusters = []
        cluster_sizes = []
        
        for cluster_id in range(n_clusters):
            cluster_indices = [i for i, c in enumerate(cluster_assignments) if c == cluster_id]
            
            if len(cluster_indices) < min_cluster_size:
                continue
            
            cluster_issues = [self.issues[i] for i in cluster_indices]
            cluster_issue_ids = [issue.issue_number for issue in cluster_issues]
            
            # Get all tokens for this cluster
            cluster_tokens = []
            for i in cluster_indices:
                combined_text = f"{self.issues[i].title} {self.issues[i].body}"
                cluster_tokens.extend(self._tokenize(combined_text))
            
            # Find most common terms
            term_counts = Counter(cluster_tokens)
            common_terms = [term for term, count in term_counts.most_common(10)]
            
            # Suggest labels based on co-occurrence
            label_counts = Counter()
            for issue in cluster_issues:
                label_counts.update(issue.labels)
            suggested_labels = [label for label, count in label_counts.most_common(5)]
            
            # Generate cluster properties
            cluster_name = self._generate_cluster_name(cluster_issues, cluster_tokens)
            category = self._categorize_cluster(cluster_issues)
            
            # Calculate confidence as average similarity to centroid
            similarities = [
                self._cosine_similarity(normalized_vectors[i], centroids[cluster_id])
                for i in cluster_indices
            ]
            confidence = sum(similarities) / len(similarities) if similarities else 0.0
            
            # Generate description
            description = f"Cluster of {len(cluster_indices)} issues related to {category}. "
            if suggested_labels:
                description += f"Common labels: {', '.join(suggested_labels[:3])}. "
            description += f"Key terms: {', '.join(common_terms[:5])}."
            
            cluster = IssueCluster(
                cluster_id=cluster_id,
                cluster_name=cluster_name,
                centroid=centroids[cluster_id],
                issue_ids=cluster_issue_ids,
                size=len(cluster_indices),
                suggested_labels=suggested_labels,
                common_terms=common_terms,
                category=category,
                confidence=confidence,
                description=description
            )
            
            self.clusters.append(cluster)
            cluster_sizes.append(len(cluster_indices))
        
        # Calculate overall metrics
        all_labels = [label for issue in self.issues for label in issue.labels]
        label_distribution = dict(Counter(all_labels).most_common(10))
        
        self.metrics = ClusteringMetrics(
            silhouette_score=silhouette,
            inertia=inertia,
            num_clusters=len(self.clusters),
            num_issues=len(self.issues),
            avg_cluster_size=sum(cluster_sizes) / len(cluster_sizes) if cluster_sizes else 0,
            cluster_sizes=cluster_sizes,
            label_distribution=label_distribution
        )
        
        print(f"\nCreated {len(self.clusters)} clusters")
        print(f"Average cluster size: {self.metrics.avg_cluster_size:.1f}")
        
        return self.clusters
    
    def predict_cluster(self, issue_title: str, issue_body: str = "") -> Optional[IssueCluster]:
        """
        Predict which cluster a new issue belongs to.
        
        Args:
            issue_title: Issue title
            issue_body: Issue body
            
        Returns:
            Most similar cluster or None
        """
        if not self.clusters or not self.tfidf_vectors:
            print("No clusters available. Run perform_clustering() first.", file=sys.stderr)
            return None
        
        # Tokenize and create TF-IDF vector for new issue
        combined_text = f"{issue_title} {issue_body}"
        tokens = self._tokenize(combined_text)
        tfidf_vector = self._calculate_tfidf_vector(tokens)
        
        # Convert to dense normalized vector
        all_terms = sorted(self.idf_scores.keys())
        term_to_idx = {term: idx for idx, term in enumerate(all_terms)}
        
        dense_vector = [0.0] * len(all_terms)
        for term, value in tfidf_vector.items():
            if term in term_to_idx:
                dense_vector[term_to_idx[term]] = value
        
        # Normalize
        norm = math.sqrt(sum(x**2 for x in dense_vector))
        if norm > 0:
            dense_vector = [x / norm for x in dense_vector]
        
        # Find nearest cluster centroid
        best_cluster = None
        min_distance = float('inf')
        
        for cluster in self.clusters:
            distance = self._euclidean_distance(dense_vector, cluster.centroid)
            if distance < min_distance:
                min_distance = distance
                best_cluster = cluster
        
        return best_cluster
    
    def save_results(self, output_file: str = "clustering_results.json"):
        """
        Save clustering results to JSON file.
        
        Args:
            output_file: Output filename
        """
        filepath = self.output_dir / output_file
        
        results = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'num_issues': len(self.issues),
            'num_clusters': len(self.clusters),
            'metrics': self.metrics.to_dict() if self.metrics else None,
            'clusters': [cluster.to_dict() for cluster in self.clusters]
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"\nResults saved to: {filepath}")
        return str(filepath)
    
    def generate_report(self) -> str:
        """
        Generate comprehensive clustering report.
        
        Returns:
            Markdown formatted report
        """
        if not self.clusters:
            return "No clustering results available."
        
        report = []
        report.append("# Issue Clustering Analysis Report")
        report.append(f"\n**Generated:** {datetime.now(timezone.utc).isoformat()}")
        report.append(f"**System:** Issue Clustering System (@engineer-master)")
        report.append("")
        
        # Summary
        report.append("## Executive Summary")
        report.append(f"- **Total Issues Analyzed:** {len(self.issues)}")
        report.append(f"- **Clusters Identified:** {len(self.clusters)}")
        
        if self.metrics:
            report.append(f"- **Clustering Quality (Silhouette Score):** {self.metrics.silhouette_score:.3f}")
            report.append(f"- **Average Cluster Size:** {self.metrics.avg_cluster_size:.1f}")
        report.append("")
        
        # Quality assessment
        if self.metrics and self.metrics.silhouette_score > 0:
            quality = "Excellent" if self.metrics.silhouette_score > 0.5 else \
                     "Good" if self.metrics.silhouette_score > 0.3 else "Fair"
            report.append(f"**Clustering Quality:** {quality}")
            report.append("")
        
        # Cluster details
        report.append("## Identified Clusters")
        report.append("")
        
        for i, cluster in enumerate(sorted(self.clusters, key=lambda c: c.size, reverse=True), 1):
            report.append(f"### {i}. {cluster.cluster_name}")
            report.append(f"- **Category:** {cluster.category}")
            report.append(f"- **Size:** {cluster.size} issues")
            report.append(f"- **Confidence:** {cluster.confidence:.2%}")
            report.append(f"- **Issues:** #{', #'.join(map(str, cluster.issue_ids[:10]))}")
            if len(cluster.issue_ids) > 10:
                report.append(f"  _(and {len(cluster.issue_ids) - 10} more)_")
            
            if cluster.suggested_labels:
                report.append(f"- **Suggested Labels:** {', '.join(cluster.suggested_labels[:5])}")
            
            if cluster.common_terms:
                report.append(f"- **Key Terms:** {', '.join(cluster.common_terms[:8])}")
            
            report.append(f"- **Description:** {cluster.description}")
            report.append("")
        
        # Label distribution
        if self.metrics and self.metrics.label_distribution:
            report.append("## Label Distribution")
            for label, count in sorted(self.metrics.label_distribution.items(), 
                                       key=lambda x: x[1], reverse=True):
                report.append(f"- **{label}:** {count} issues")
            report.append("")
        
        # Recommendations
        report.append("## Recommendations")
        report.append("")
        report.append("Based on the clustering analysis:")
        report.append("")
        
        # Find largest clusters
        large_clusters = [c for c in self.clusters if c.size > self.metrics.avg_cluster_size]
        if large_clusters:
            report.append(f"1. **Focus Areas:** The following categories have high issue volume:")
            for cluster in sorted(large_clusters, key=lambda c: c.size, reverse=True)[:3]:
                report.append(f"   - {cluster.cluster_name}: {cluster.size} issues")
        
        # Suggest new labels
        unlabeled_clusters = [c for c in self.clusters if not any(
            label in ['bug', 'feature', 'enhancement', 'documentation']
            for label in c.suggested_labels
        )]
        if unlabeled_clusters:
            report.append(f"\n2. **Label Suggestions:** Consider adding labels to improve organization")
        
        report.append("")
        report.append("---")
        report.append("*Generated by Issue Clustering System - @engineer-master*")
        
        return '\n'.join(report)


def main():
    """Command-line interface for issue clustering system."""
    parser = argparse.ArgumentParser(
        description='Issue Clustering System for Automatic Categorization',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Cluster issues from JSON file
  %(prog)s cluster --input issues.json --clusters 5
  
  # Predict cluster for new issue
  %(prog)s predict --input issues.json --title "API bug" --body "Endpoint fails"
  
  # Generate report
  %(prog)s cluster --input issues.json --report clustering_report.md
  
  # Save results to JSON
  %(prog)s cluster --input issues.json --output results.json
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Cluster command
    cluster_parser = subparsers.add_parser('cluster', help='Perform clustering')
    cluster_parser.add_argument('--input', required=True, help='Input JSON file with issues')
    cluster_parser.add_argument('--clusters', type=int, default=5, help='Number of clusters')
    cluster_parser.add_argument('--min-size', type=int, default=2, help='Min cluster size')
    cluster_parser.add_argument('--output', help='Output JSON file')
    cluster_parser.add_argument('--report', help='Generate markdown report to file')
    
    # Predict command
    predict_parser = subparsers.add_parser('predict', help='Predict cluster for new issue')
    predict_parser.add_argument('--input', required=True, help='Input JSON file with clustered issues')
    predict_parser.add_argument('--title', required=True, help='Issue title')
    predict_parser.add_argument('--body', default='', help='Issue body')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Initialize system
    system = IssueClusteringSystem()
    
    if args.command == 'cluster':
        # Load issues
        system.load_issues_from_file(args.input)
        
        if len(system.issues) == 0:
            print("No issues loaded. Exiting.", file=sys.stderr)
            sys.exit(1)
        
        # Perform clustering
        clusters = system.perform_clustering(
            n_clusters=args.clusters,
            min_cluster_size=args.min_size
        )
        
        # Save results
        if args.output:
            system.save_results(args.output)
        
        # Generate report
        if args.report:
            report = system.generate_report()
            with open(args.report, 'w') as f:
                f.write(report)
            print(f"Report saved to: {args.report}")
        else:
            print("\n" + system.generate_report())
    
    elif args.command == 'predict':
        # Load previous clustering results
        system.load_issues_from_file(args.input)
        
        # Need to re-cluster to build index
        print("Building clustering model...")
        system.perform_clustering()
        
        # Predict cluster
        cluster = system.predict_cluster(args.title, args.body)
        
        if cluster:
            print(f"\n{'='*80}")
            print(f"Predicted Cluster: {cluster.cluster_name}")
            print(f"{'='*80}")
            print(f"Category: {cluster.category}")
            print(f"Confidence: {cluster.confidence:.2%}")
            print(f"Suggested Labels: {', '.join(cluster.suggested_labels[:5])}")
            print(f"Description: {cluster.description}")
            print()
        else:
            print("Could not predict cluster.")
    
    print("\n✅ Clustering complete!")


if __name__ == '__main__':
    main()
