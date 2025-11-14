#!/usr/bin/env python3
"""
Semantic Similarity Engine for Issue Matching

A rigorous TF-IDF based system for matching new issues to historical solutions.
Built with meticulous attention to correctness and performance.

Inspired by Margaret Hamilton's systematic approach to engineering.
"""

import json
import math
import re
from collections import defaultdict, Counter
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass, asdict
from datetime import datetime
import argparse


@dataclass
class IssueRecord:
    """Represents a historical issue with its solution."""
    issue_number: int
    title: str
    body: str
    labels: List[str]
    solution_summary: str
    agent_assigned: Optional[str]
    resolved_at: str
    pr_number: Optional[int] = None
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization."""
        return asdict(self)
    
    @staticmethod
    def from_dict(data: dict) -> 'IssueRecord':
        """Create IssueRecord from dictionary."""
        return IssueRecord(**data)


@dataclass
class SimilarityMatch:
    """Represents a similarity match result."""
    issue_number: int
    title: str
    similarity_score: float
    agent_assigned: Optional[str]
    solution_summary: str
    matching_terms: List[str]
    labels: List[str]
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization."""
        return asdict(self)


class SemanticSimilarityEngine:
    """
    TF-IDF based semantic similarity engine for matching issues.
    
    Uses a rigorous mathematical approach with:
    - Term Frequency - Inverse Document Frequency (TF-IDF)
    - Cosine similarity for document comparison
    - Stop word filtering
    - Stemming-like normalization
    """
    
    # Common stop words to filter out
    STOP_WORDS = {
        'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from',
        'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the',
        'to', 'was', 'will', 'with', 'this', 'but', 'they', 'have', 'had',
        'what', 'when', 'where', 'who', 'which', 'why', 'how'
    }
    
    def __init__(self, history_path: str = '.github/agent-system/issue_history.json'):
        """
        Initialize the semantic similarity engine.
        
        Args:
            history_path: Path to issue history JSON file
        """
        self.history_path = Path(history_path)
        self.issue_records: List[IssueRecord] = []
        self.document_terms: List[Set[str]] = []
        self.idf_scores: Dict[str, float] = {}
        self.tfidf_vectors: List[Dict[str, float]] = []
        
        self._load_history()
        self._build_index()
    
    def _load_history(self):
        """Load issue history from JSON file."""
        if not self.history_path.exists():
            print(f"History file not found: {self.history_path}")
            print("Starting with empty history.")
            return
        
        try:
            with open(self.history_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # Validate structure
            if not isinstance(data, dict) or 'issues' not in data:
                print("Invalid history file structure")
                return
            
            # Load issues
            for issue_data in data.get('issues', []):
                try:
                    issue = IssueRecord.from_dict(issue_data)
                    self.issue_records.append(issue)
                except Exception as e:
                    print(f"Error loading issue: {e}")
                    continue
                    
            print(f"Loaded {len(self.issue_records)} historical issues")
            
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON: {e}")
        except Exception as e:
            print(f"Error loading history: {e}")
    
    def _tokenize(self, text: str) -> List[str]:
        """
        Tokenize text into words with normalization.
        
        Args:
            text: Input text
            
        Returns:
            List of normalized tokens
        """
        if not text:
            return []
        
        # Convert to lowercase
        text = text.lower()
        
        # Remove special characters, keep alphanumeric and spaces
        text = re.sub(r'[^a-z0-9\s]', ' ', text)
        
        # Split into tokens
        tokens = text.split()
        
        # Filter stop words and short tokens
        tokens = [t for t in tokens if t not in self.STOP_WORDS and len(t) > 2]
        
        return tokens
    
    def _calculate_term_frequency(self, tokens: List[str]) -> Dict[str, float]:
        """
        Calculate term frequency for a document.
        
        Args:
            tokens: List of tokens
            
        Returns:
            Dictionary mapping terms to their frequency
        """
        if not tokens:
            return {}
        
        term_count = Counter(tokens)
        max_count = max(term_count.values())
        
        # Normalize by max frequency
        tf = {term: count / max_count for term, count in term_count.items()}
        
        return tf
    
    def _calculate_idf(self):
        """
        Calculate inverse document frequency for all terms.
        
        IDF(term) = log(N / df(term))
        where N is total documents and df is document frequency
        """
        if not self.document_terms:
            return
        
        n_documents = len(self.document_terms)
        
        # Count document frequency for each term
        doc_freq = defaultdict(int)
        for doc_terms in self.document_terms:
            for term in doc_terms:
                doc_freq[term] += 1
        
        # Calculate IDF
        self.idf_scores = {}
        for term, df in doc_freq.items():
            # Add 1 to avoid division by zero
            self.idf_scores[term] = math.log(n_documents / (df + 1))
    
    def _calculate_tfidf_vector(self, tokens: List[str]) -> Dict[str, float]:
        """
        Calculate TF-IDF vector for a document.
        
        Args:
            tokens: List of tokens
            
        Returns:
            Dictionary mapping terms to TF-IDF scores
        """
        tf = self._calculate_term_frequency(tokens)
        
        tfidf = {}
        for term, tf_score in tf.items():
            idf_score = self.idf_scores.get(term, 0)
            tfidf[term] = tf_score * idf_score
        
        return tfidf
    
    def _cosine_similarity(self, vec1: Dict[str, float], vec2: Dict[str, float]) -> float:
        """
        Calculate cosine similarity between two TF-IDF vectors.
        
        Args:
            vec1: First TF-IDF vector
            vec2: Second TF-IDF vector
            
        Returns:
            Cosine similarity score (0-1)
        """
        if not vec1 or not vec2:
            return 0.0
        
        # Get common terms
        common_terms = set(vec1.keys()) & set(vec2.keys())
        
        if not common_terms:
            return 0.0
        
        # Calculate dot product
        dot_product = sum(vec1[term] * vec2[term] for term in common_terms)
        
        # Calculate magnitudes
        magnitude1 = math.sqrt(sum(score ** 2 for score in vec1.values()))
        magnitude2 = math.sqrt(sum(score ** 2 for score in vec2.values()))
        
        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0
        
        # Calculate cosine similarity
        similarity = dot_product / (magnitude1 * magnitude2)
        
        # Ensure result is in [0, 1]
        return max(0.0, min(1.0, similarity))
    
    def _build_index(self):
        """Build TF-IDF index for all historical issues."""
        if not self.issue_records:
            return
        
        # Tokenize all documents
        self.document_terms = []
        for issue in self.issue_records:
            # Combine title, body, and solution for comprehensive matching
            combined_text = f"{issue.title} {issue.body} {issue.solution_summary}"
            tokens = self._tokenize(combined_text)
            self.document_terms.append(set(tokens))
        
        # Calculate IDF scores
        self._calculate_idf()
        
        # Calculate TF-IDF vectors for all documents
        self.tfidf_vectors = []
        for issue in self.issue_records:
            combined_text = f"{issue.title} {issue.body} {issue.solution_summary}"
            tokens = self._tokenize(combined_text)
            tfidf_vector = self._calculate_tfidf_vector(tokens)
            self.tfidf_vectors.append(tfidf_vector)
        
        print(f"Built index for {len(self.tfidf_vectors)} documents")
    
    def find_similar_issues(
        self, 
        title: str, 
        body: str = "", 
        top_k: int = 5,
        min_similarity: float = 0.1
    ) -> List[SimilarityMatch]:
        """
        Find similar historical issues.
        
        Args:
            title: Issue title
            body: Issue body/description
            top_k: Number of top matches to return
            min_similarity: Minimum similarity threshold
            
        Returns:
            List of similarity matches sorted by score
        """
        if not self.issue_records:
            return []
        
        # Tokenize query
        query_text = f"{title} {body}"
        query_tokens = self._tokenize(query_text)
        
        if not query_tokens:
            return []
        
        # Calculate TF-IDF vector for query
        query_vector = self._calculate_tfidf_vector(query_tokens)
        
        # Calculate similarity with all documents
        similarities = []
        for i, (issue, doc_vector) in enumerate(zip(self.issue_records, self.tfidf_vectors)):
            similarity = self._cosine_similarity(query_vector, doc_vector)
            
            if similarity >= min_similarity:
                # Find matching terms
                common_terms = set(query_vector.keys()) & set(doc_vector.keys())
                matching_terms = sorted(common_terms, 
                                       key=lambda t: query_vector[t] * doc_vector[t],
                                       reverse=True)[:5]
                
                match = SimilarityMatch(
                    issue_number=issue.issue_number,
                    title=issue.title,
                    similarity_score=similarity,
                    agent_assigned=issue.agent_assigned,
                    solution_summary=issue.solution_summary,
                    matching_terms=matching_terms,
                    labels=issue.labels
                )
                similarities.append(match)
        
        # Sort by similarity score
        similarities.sort(key=lambda x: x.similarity_score, reverse=True)
        
        return similarities[:top_k]
    
    def add_issue(self, issue: IssueRecord):
        """
        Add a new issue to the history.
        
        Args:
            issue: Issue record to add
        """
        self.issue_records.append(issue)
        self._build_index()  # Rebuild index
    
    def save_history(self):
        """Save issue history to JSON file."""
        # Ensure directory exists
        self.history_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Prepare data
        data = {
            'version': '1.0',
            'updated_at': datetime.utcnow().isoformat() + 'Z',
            'total_issues': len(self.issue_records),
            'issues': [issue.to_dict() for issue in self.issue_records]
        }
        
        # Write to file
        with open(self.history_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"Saved {len(self.issue_records)} issues to {self.history_path}")
    
    def get_statistics(self) -> Dict:
        """Get statistics about the issue history."""
        if not self.issue_records:
            return {
                'total_issues': 0,
                'total_terms': 0,
                'avg_terms_per_issue': 0,
                'agents': {}
            }
        
        # Count terms
        total_terms = sum(len(terms) for terms in self.document_terms)
        avg_terms = total_terms / len(self.document_terms) if self.document_terms else 0
        
        # Count by agent
        agent_counts = defaultdict(int)
        for issue in self.issue_records:
            if issue.agent_assigned:
                agent_counts[issue.agent_assigned] += 1
        
        return {
            'total_issues': len(self.issue_records),
            'total_unique_terms': len(self.idf_scores),
            'avg_terms_per_issue': round(avg_terms, 2),
            'agents': dict(agent_counts)
        }


def main():
    """Command-line interface for the semantic similarity engine."""
    parser = argparse.ArgumentParser(
        description='Semantic Similarity Engine for Issue Matching',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Search for similar issues
  %(prog)s search "API endpoint bug" --body "The API is returning 500 errors"
  
  # Add a resolved issue to history
  %(prog)s add --number 123 --title "Fix API bug" --solution "Updated error handling"
  
  # Show statistics
  %(prog)s stats
  
  # Initialize empty history
  %(prog)s init
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Search command
    search_parser = subparsers.add_parser('search', help='Search for similar issues')
    search_parser.add_argument('title', help='Issue title')
    search_parser.add_argument('--body', default='', help='Issue body')
    search_parser.add_argument('--top', type=int, default=5, help='Number of results')
    search_parser.add_argument('--min-score', type=float, default=0.1, help='Minimum similarity')
    
    # Add command
    add_parser = subparsers.add_parser('add', help='Add an issue to history')
    add_parser.add_argument('--number', type=int, required=True, help='Issue number')
    add_parser.add_argument('--title', required=True, help='Issue title')
    add_parser.add_argument('--body', default='', help='Issue body')
    add_parser.add_argument('--solution', required=True, help='Solution summary')
    add_parser.add_argument('--agent', help='Agent that resolved the issue')
    add_parser.add_argument('--labels', nargs='*', default=[], help='Issue labels')
    add_parser.add_argument('--pr', type=int, help='Associated PR number')
    
    # Stats command
    subparsers.add_parser('stats', help='Show statistics')
    
    # Init command
    subparsers.add_parser('init', help='Initialize empty history')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Initialize engine
    engine = SemanticSimilarityEngine()
    
    if args.command == 'search':
        matches = engine.find_similar_issues(
            args.title, 
            args.body,
            top_k=args.top,
            min_similarity=args.min_score
        )
        
        if not matches:
            print("No similar issues found.")
            return
        
        print(f"\n{'='*80}")
        print(f"Found {len(matches)} similar issue(s):")
        print(f"{'='*80}\n")
        
        for i, match in enumerate(matches, 1):
            print(f"{i}. Issue #{match.issue_number}: {match.title}")
            print(f"   Similarity: {match.similarity_score:.2%}")
            print(f"   Agent: {match.agent_assigned or 'N/A'}")
            print(f"   Matching terms: {', '.join(match.matching_terms[:5])}")
            print(f"   Solution: {match.solution_summary[:100]}...")
            print()
    
    elif args.command == 'add':
        issue = IssueRecord(
            issue_number=args.number,
            title=args.title,
            body=args.body,
            labels=args.labels,
            solution_summary=args.solution,
            agent_assigned=args.agent,
            resolved_at=datetime.utcnow().isoformat() + 'Z',
            pr_number=args.pr
        )
        
        engine.add_issue(issue)
        engine.save_history()
        print(f"Added issue #{args.number} to history")
    
    elif args.command == 'stats':
        stats = engine.get_statistics()
        print(json.dumps(stats, indent=2))
    
    elif args.command == 'init':
        engine.save_history()
        print("Initialized empty history file")


if __name__ == '__main__':
    main()
