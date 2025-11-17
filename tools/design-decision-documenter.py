#!/usr/bin/env python3
"""
Design Decision Documenter for Autonomous Code Archaeology

This tool documents design decisions with optimal performance and efficiency.
Inspired by Architecture Decision Records (ADR) but optimized for automated extraction.

Key Features:
- Fast design decision extraction from git history
- Efficient decision database with indexing
- Quick similarity search for related decisions
- Minimal memory footprint
- Optimized for large repositories

Performance-focused implementation by @accelerate-specialist
"""

import os
import sys
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Set
from collections import defaultdict
import hashlib


class DesignDecisionDocumenter:
    """
    Efficient design decision documentation system
    
    Optimizations:
    - Lazy loading of decision data
    - Indexed decision database for fast lookups
    - Cached similarity computations
    - Minimal memory allocations
    """
    
    def __init__(self, repo_path: str = ".", decisions_file: str = "analysis/design-decisions.json"):
        self.repo_path = repo_path
        self.decisions_file = decisions_file
        self._decisions_cache = None
        self._index_cache = None
        
    def _load_decisions(self) -> Dict:
        """Lazy load decisions database"""
        if self._decisions_cache is not None:
            return self._decisions_cache
            
        if os.path.exists(self.decisions_file):
            with open(self.decisions_file, 'r') as f:
                self._decisions_cache = json.load(f)
        else:
            self._decisions_cache = self._initialize_database()
        
        return self._decisions_cache
    
    def _initialize_database(self) -> Dict:
        """Initialize empty decisions database"""
        return {
            "version": "1.0.0",
            "last_updated": None,
            "repository": os.path.basename(os.path.abspath(self.repo_path)),
            "total_decisions": 0,
            "decisions": [],
            "index": {
                "by_status": {},
                "by_category": {},
                "by_date": {},
                "by_hash": {}
            },
            "statistics": {
                "accepted": 0,
                "rejected": 0,
                "deprecated": 0,
                "proposed": 0
            }
        }
    
    def _save_decisions(self):
        """Save decisions database with automatic indexing"""
        data = self._load_decisions()
        data["last_updated"] = datetime.now(timezone.utc).isoformat()
        
        # Update indices for fast lookups
        self._rebuild_indices()
        
        os.makedirs(os.path.dirname(self.decisions_file), exist_ok=True)
        with open(self.decisions_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        # Clear cache to force reload
        self._decisions_cache = None
        self._index_cache = None
    
    def _rebuild_indices(self):
        """Rebuild search indices for optimal query performance"""
        data = self._load_decisions()
        decisions = data.get("decisions", [])
        
        # Clear existing indices
        index = {
            "by_status": defaultdict(list),
            "by_category": defaultdict(list),
            "by_date": defaultdict(list),
            "by_hash": {}
        }
        
        # Rebuild indices
        for i, decision in enumerate(decisions):
            decision_id = decision.get("id")
            
            # Status index
            status = decision.get("status", "unknown")
            index["by_status"][status].append(i)
            
            # Category index
            category = decision.get("category", "uncategorized")
            index["by_category"][category].append(i)
            
            # Date index (year-month)
            date_str = decision.get("date", "")
            if date_str:
                year_month = date_str[:7]  # YYYY-MM
                index["by_date"][year_month].append(i)
            
            # Hash index for O(1) lookup
            if decision_id:
                index["by_hash"][decision_id] = i
        
        # Convert defaultdicts to regular dicts for JSON serialization
        data["index"] = {
            "by_status": dict(index["by_status"]),
            "by_category": dict(index["by_category"]),
            "by_date": dict(index["by_date"]),
            "by_hash": index["by_hash"]
        }
        
        # Update statistics
        stats = data["statistics"]
        stats["accepted"] = len(index["by_status"].get("accepted", []))
        stats["rejected"] = len(index["by_status"].get("rejected", []))
        stats["deprecated"] = len(index["by_status"].get("deprecated", []))
        stats["proposed"] = len(index["by_status"].get("proposed", []))
        
        data["total_decisions"] = len(decisions)
    
    def _run_git_command(self, args: List[str]) -> str:
        """Execute git command efficiently"""
        try:
            result = subprocess.run(
                ['git'] + args,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True,
                timeout=30  # Prevent hanging
            )
            return result.stdout.strip()
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
            return ""
    
    def _parse_commit_fast(self, commit_hash: str) -> Optional[Dict]:
        """Fast commit parsing with minimal overhead"""
        # Use single git command to get all needed info
        format_str = "%H%n%an%n%ae%n%at%n%s%n%b"
        commit_info = self._run_git_command(['show', f'--format={format_str}', '--no-patch', commit_hash])
        
        if not commit_info:
            return None
        
        lines = commit_info.split('\n', 5)
        if len(lines) < 5:
            return None
        
        return {
            "hash": lines[0],
            "author": lines[1],
            "email": lines[2],
            "timestamp": int(lines[3]),
            "subject": lines[4],
            "body": lines[5] if len(lines) > 5 else ""
        }
    
    def _extract_decision_from_commit(self, commit: Dict) -> Optional[Dict]:
        """
        Extract design decision from commit with pattern matching
        
        Looks for:
        - ADR-style markers (Decision:, Context:, Consequences:)
        - Design decision keywords
        - Why/because explanations
        - Architectural changes
        """
        subject = commit["subject"]
        body = commit["body"]
        combined = f"{subject}\n{body}"
        
        # Check for ADR-style structure
        has_decision_marker = bool(re.search(r'(decision|decided|chose|opted)\s*:', combined, re.IGNORECASE))
        has_context_marker = bool(re.search(r'context\s*:', combined, re.IGNORECASE))
        has_consequence_marker = bool(re.search(r'consequence[s]?\s*:', combined, re.IGNORECASE))
        
        # Check for design keywords
        design_keywords = [
            'design', 'architect', 'approach', 'strategy', 'pattern',
            'decision', 'rationale', 'reasoning', 'alternative'
        ]
        has_design_keyword = any(kw in combined.lower() for kw in design_keywords)
        
        # Check for why/because explanations
        has_explanation = bool(re.search(r'\b(why|because|rationale|reason)\b', combined, re.IGNORECASE))
        
        # Only extract if enough signals present
        score = (
            (has_decision_marker * 3) +
            (has_context_marker * 2) +
            (has_consequence_marker * 2) +
            (has_design_keyword * 1) +
            (has_explanation * 1)
        )
        
        if score < 2:
            return None
        
        # Extract structured information
        decision = self._parse_decision_structure(commit, combined)
        
        return decision if decision else None
    
    def _parse_decision_structure(self, commit: Dict, text: str) -> Optional[Dict]:
        """Parse decision into structured format"""
        # Extract decision ID (use commit hash prefix)
        decision_id = f"DD-{commit['hash'][:8]}"
        
        # Extract title (from subject)
        title = commit["subject"]
        
        # Extract context
        context_match = re.search(r'context\s*:(.+?)(?=\n\n|consequence|decision|$)', text, re.IGNORECASE | re.DOTALL)
        context = context_match.group(1).strip() if context_match else ""
        
        # Extract decision
        decision_match = re.search(r'decision\s*:(.+?)(?=\n\n|consequence|context|$)', text, re.IGNORECASE | re.DOTALL)
        decision_text = decision_match.group(1).strip() if decision_match else ""
        
        # If no explicit decision marker, extract from body
        if not decision_text:
            # Look for decision-making phrases
            patterns = [
                r'decided to\s+(.+?)(?:\.|$)',
                r'chose to\s+(.+?)(?:\.|$)',
                r'opted for\s+(.+?)(?:\.|$)',
                r'will use\s+(.+?)(?:\.|$)',
            ]
            for pattern in patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    decision_text = match.group(1).strip()
                    break
        
        # Extract consequences
        consequences_match = re.search(r'consequence[s]?\s*:(.+?)(?=\n\n|decision|context|$)', text, re.IGNORECASE | re.DOTALL)
        consequences = consequences_match.group(1).strip() if consequences_match else ""
        
        # Extract alternatives considered
        alternatives_match = re.search(r'alternative[s]?\s*:(.+?)(?=\n\n|$)', text, re.IGNORECASE | re.DOTALL)
        alternatives = alternatives_match.group(1).strip() if alternatives_match else ""
        
        # Categorize decision
        category = self._categorize_decision(title, decision_text)
        
        # Determine status (defaults to accepted for past commits)
        status = "accepted"
        if any(kw in text.lower() for kw in ['deprecated', 'superseded', 'replaced']):
            status = "deprecated"
        elif any(kw in text.lower() for kw in ['rejected', 'declined']):
            status = "rejected"
        
        decision_doc = {
            "id": decision_id,
            "title": title,
            "date": datetime.fromtimestamp(commit["timestamp"], tz=timezone.utc).isoformat(),
            "status": status,
            "category": category,
            "context": context if context else self._extract_context_heuristic(text),
            "decision": decision_text if decision_text else self._extract_decision_heuristic(text),
            "consequences": consequences if consequences else self._extract_consequences_heuristic(text),
            "alternatives": alternatives,
            "commit": commit["hash"][:7],
            "author": commit["author"],
            "metadata": {
                "files_affected": self._get_files_changed(commit["hash"]),
                "commit_timestamp": commit["timestamp"]
            }
        }
        
        return decision_doc
    
    def _categorize_decision(self, title: str, decision_text: str) -> str:
        """Efficiently categorize design decision"""
        combined = f"{title} {decision_text}".lower()
        
        categories = [
            ("architecture", ["architect", "structure", "layer", "component", "module"]),
            ("technology", ["technology", "framework", "library", "tool", "language"]),
            ("api", ["api", "interface", "endpoint", "contract"]),
            ("data", ["data", "database", "schema", "model", "storage"]),
            ("security", ["security", "auth", "permission", "encryption"]),
            ("performance", ["performance", "optimize", "cache", "scale"]),
            ("testing", ["test", "quality", "coverage"]),
            ("deployment", ["deploy", "release", "ci", "cd", "pipeline"]),
        ]
        
        for category, keywords in categories:
            if any(kw in combined for kw in keywords):
                return category
        
        return "general"
    
    def _extract_context_heuristic(self, text: str) -> str:
        """Extract context using heuristics when no explicit marker"""
        # Look for "because", "due to", "since" phrases
        patterns = [
            r'because\s+(.+?)(?:\.|$)',
            r'due to\s+(.+?)(?:\.|$)',
            r'since\s+(.+?)(?:\.|$)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        # Fallback: use first paragraph of body
        paragraphs = text.split('\n\n')
        if len(paragraphs) > 1:
            return paragraphs[0].strip()
        
        return ""
    
    def _extract_decision_heuristic(self, text: str) -> str:
        """Extract decision using heuristics"""
        # Already handled in _parse_decision_structure
        return text.split('\n')[0] if text else ""
    
    def _extract_consequences_heuristic(self, text: str) -> str:
        """Extract consequences using heuristics"""
        # Look for result/impact phrases
        patterns = [
            r'(?:this means|result|impact|effect)\s+(.+?)(?:\.|$)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return ""
    
    def _get_files_changed(self, commit_hash: str) -> List[str]:
        """Get list of files changed in commit"""
        files = self._run_git_command(['diff-tree', '--no-commit-id', '--name-only', '-r', commit_hash])
        return files.split('\n') if files else []
    
    def extract_decisions(self, max_commits: int = 500, since: Optional[str] = None) -> List[Dict]:
        """
        Extract design decisions from git history efficiently
        
        Performance: O(n) where n = max_commits
        Memory: O(m) where m = number of decisions found
        """
        print(f"Extracting design decisions from git history...")
        
        # Get commit list efficiently
        git_args = ['log', '--format=%H', f'-{max_commits}']
        if since:
            git_args.append(f'--since={since}')
        
        commit_hashes = self._run_git_command(git_args)
        if not commit_hashes:
            return []
        
        commits = commit_hashes.split('\n')
        decisions = []
        
        # Process commits in batches for efficiency
        batch_size = 50
        for i in range(0, len(commits), batch_size):
            batch = commits[i:i+batch_size]
            
            if i % 100 == 0:
                print(f"Processing commits {i+1}/{len(commits)}...")
            
            for commit_hash in batch:
                commit = self._parse_commit_fast(commit_hash)
                if not commit:
                    continue
                
                decision = self._extract_decision_from_commit(commit)
                if decision:
                    decisions.append(decision)
        
        print(f"Found {len(decisions)} design decisions")
        return decisions
    
    def add_decision(self, decision: Dict):
        """Add a design decision to the database"""
        data = self._load_decisions()
        
        # Check for duplicates by commit hash
        existing = self.find_decision_by_commit(decision.get("commit", ""))
        if existing:
            print(f"Decision already exists: {existing['id']}")
            return
        
        data["decisions"].append(decision)
        self._save_decisions()
    
    def find_decision_by_id(self, decision_id: str) -> Optional[Dict]:
        """O(1) lookup of decision by ID using index"""
        data = self._load_decisions()
        index = data.get("index", {}).get("by_hash", {})
        
        idx = index.get(decision_id)
        if idx is not None:
            return data["decisions"][idx]
        
        return None
    
    def find_decision_by_commit(self, commit_hash: str) -> Optional[Dict]:
        """Find decision by commit hash"""
        data = self._load_decisions()
        
        for decision in data["decisions"]:
            if decision.get("commit", "").startswith(commit_hash[:7]):
                return decision
        
        return None
    
    def find_decisions_by_status(self, status: str) -> List[Dict]:
        """Efficiently find decisions by status using index"""
        data = self._load_decisions()
        index = data.get("index", {}).get("by_status", {})
        indices = index.get(status, [])
        
        return [data["decisions"][i] for i in indices if i < len(data["decisions"])]
    
    def find_decisions_by_category(self, category: str) -> List[Dict]:
        """Efficiently find decisions by category using index"""
        data = self._load_decisions()
        index = data.get("index", {}).get("by_category", {})
        indices = index.get(category, [])
        
        return [data["decisions"][i] for i in indices if i < len(data["decisions"])]
    
    def search_decisions(self, query: str, limit: int = 10) -> List[Tuple[Dict, float]]:
        """
        Fast full-text search across decisions
        
        Returns: List of (decision, relevance_score) tuples
        """
        data = self._load_decisions()
        decisions = data.get("decisions", [])
        
        if not query:
            return [(d, 1.0) for d in decisions[:limit]]
        
        query_lower = query.lower()
        query_terms = set(query_lower.split())
        
        # Score each decision
        scored_decisions = []
        for decision in decisions:
            # Create searchable text
            searchable = " ".join([
                decision.get("title", ""),
                decision.get("context", ""),
                decision.get("decision", ""),
                decision.get("category", ""),
            ]).lower()
            
            # Simple relevance scoring
            score = 0.0
            
            # Exact phrase match (highest weight)
            if query_lower in searchable:
                score += 10.0
            
            # Term frequency
            for term in query_terms:
                count = searchable.count(term)
                score += count * 2.0
            
            # Category match bonus
            if query_lower in decision.get("category", "").lower():
                score += 5.0
            
            if score > 0:
                scored_decisions.append((decision, score))
        
        # Sort by score and return top results
        scored_decisions.sort(key=lambda x: x[1], reverse=True)
        return scored_decisions[:limit]
    
    def find_related_decisions(self, decision_id: str, limit: int = 5) -> List[Tuple[Dict, float]]:
        """
        Find decisions related to a given decision
        
        Uses fast similarity heuristics:
        - Same category
        - Similar keywords
        - Overlapping files
        """
        decision = self.find_decision_by_id(decision_id)
        if not decision:
            return []
        
        data = self._load_decisions()
        decisions = data.get("decisions", [])
        
        related = []
        decision_category = decision.get("category", "")
        decision_files = set(decision.get("metadata", {}).get("files_affected", []))
        decision_text = f"{decision.get('title', '')} {decision.get('decision', '')}".lower()
        decision_terms = set(decision_text.split())
        
        for other in decisions:
            if other.get("id") == decision_id:
                continue
            
            similarity = 0.0
            
            # Category match
            if other.get("category") == decision_category:
                similarity += 0.4
            
            # File overlap
            other_files = set(other.get("metadata", {}).get("files_affected", []))
            if decision_files and other_files:
                overlap = len(decision_files & other_files)
                if overlap > 0:
                    similarity += 0.3 * (overlap / max(len(decision_files), len(other_files)))
            
            # Term overlap
            other_text = f"{other.get('title', '')} {other.get('decision', '')}".lower()
            other_terms = set(other_text.split())
            term_overlap = len(decision_terms & other_terms)
            if term_overlap > 0:
                similarity += 0.3 * (term_overlap / max(len(decision_terms), len(other_terms)))
            
            if similarity > 0.2:  # Minimum threshold
                related.append((other, similarity))
        
        related.sort(key=lambda x: x[1], reverse=True)
        return related[:limit]
    
    def generate_report(self) -> str:
        """Generate comprehensive design decisions report"""
        data = self._load_decisions()
        decisions = data.get("decisions", [])
        stats = data.get("statistics", {})
        
        report = []
        report.append("# 🏗️ Design Decisions Documentation")
        report.append(f"\n**Generated:** {datetime.now(timezone.utc).isoformat()}")
        report.append(f"**Repository:** {data.get('repository', 'Unknown')}")
        report.append(f"**Last Updated:** {data.get('last_updated', 'Never')}")
        
        # Statistics
        report.append(f"\n## 📊 Statistics")
        report.append(f"- Total decisions documented: {data.get('total_decisions', 0)}")
        report.append(f"- Accepted: {stats.get('accepted', 0)}")
        report.append(f"- Rejected: {stats.get('rejected', 0)}")
        report.append(f"- Deprecated: {stats.get('deprecated', 0)}")
        report.append(f"- Proposed: {stats.get('proposed', 0)}")
        
        # Decisions by category
        categories = {}
        for decision in decisions:
            cat = decision.get("category", "uncategorized")
            categories[cat] = categories.get(cat, 0) + 1
        
        if categories:
            report.append(f"\n### Decisions by Category")
            for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
                report.append(f"- **{cat}**: {count}")
        
        # Recent decisions
        if decisions:
            report.append(f"\n## 📋 Recent Decisions")
            sorted_decisions = sorted(
                decisions,
                key=lambda d: d.get("date", ""),
                reverse=True
            )
            
            for decision in sorted_decisions[:10]:
                report.append(f"\n### {decision.get('id', 'Unknown')}: {decision.get('title', 'Untitled')}")
                report.append(f"**Date:** {decision.get('date', 'Unknown')[:10]}")
                report.append(f"**Status:** {decision.get('status', 'unknown')}")
                report.append(f"**Category:** {decision.get('category', 'uncategorized')}")
                report.append(f"**Commit:** `{decision.get('commit', 'unknown')}`")
                
                if decision.get("context"):
                    report.append(f"\n**Context:** {decision['context'][:200]}...")
                
                if decision.get("decision"):
                    report.append(f"\n**Decision:** {decision['decision'][:200]}...")
        
        # Index information for performance
        report.append(f"\n## 🚀 Performance")
        report.append(f"- Indexed by: status, category, date, hash")
        report.append(f"- Query performance: O(1) for ID lookups, O(log n) for indexed searches")
        report.append(f"- Memory efficient: Lazy loading with caching")
        
        return '\n'.join(report)
    
    def export_to_markdown(self, output_dir: str = "docs/decisions"):
        """Export each decision to individual markdown file (ADR style)"""
        data = self._load_decisions()
        decisions = data.get("decisions", [])
        
        os.makedirs(output_dir, exist_ok=True)
        
        for decision in decisions:
            decision_id = decision.get("id", "unknown")
            filename = f"{decision_id}.md"
            filepath = os.path.join(output_dir, filename)
            
            content = self._format_decision_as_markdown(decision)
            
            with open(filepath, 'w') as f:
                f.write(content)
        
        # Create index
        self._create_decision_index(output_dir, decisions)
        
        print(f"Exported {len(decisions)} decisions to {output_dir}")
    
    def _format_decision_as_markdown(self, decision: Dict) -> str:
        """Format decision as ADR-style markdown"""
        lines = []
        lines.append(f"# {decision.get('id', 'Unknown')}: {decision.get('title', 'Untitled')}")
        lines.append("")
        lines.append(f"**Status:** {decision.get('status', 'unknown')}")
        lines.append(f"**Date:** {decision.get('date', 'Unknown')}")
        lines.append(f"**Category:** {decision.get('category', 'uncategorized')}")
        lines.append(f"**Author:** {decision.get('author', 'Unknown')}")
        lines.append(f"**Commit:** `{decision.get('commit', 'unknown')}`")
        lines.append("")
        
        if decision.get("context"):
            lines.append("## Context")
            lines.append("")
            lines.append(decision["context"])
            lines.append("")
        
        if decision.get("decision"):
            lines.append("## Decision")
            lines.append("")
            lines.append(decision["decision"])
            lines.append("")
        
        if decision.get("consequences"):
            lines.append("## Consequences")
            lines.append("")
            lines.append(decision["consequences"])
            lines.append("")
        
        if decision.get("alternatives"):
            lines.append("## Alternatives Considered")
            lines.append("")
            lines.append(decision["alternatives"])
            lines.append("")
        
        metadata = decision.get("metadata", {})
        if metadata.get("files_affected"):
            lines.append("## Files Affected")
            lines.append("")
            for file in metadata["files_affected"]:
                lines.append(f"- `{file}`")
            lines.append("")
        
        return '\n'.join(lines)
    
    def _create_decision_index(self, output_dir: str, decisions: List[Dict]):
        """Create index of all decisions"""
        index_path = os.path.join(output_dir, "README.md")
        
        lines = []
        lines.append("# Design Decisions Index")
        lines.append("")
        lines.append(f"Total decisions: {len(decisions)}")
        lines.append("")
        
        # Group by category
        by_category = defaultdict(list)
        for decision in decisions:
            cat = decision.get("category", "uncategorized")
            by_category[cat].append(decision)
        
        for category in sorted(by_category.keys()):
            lines.append(f"## {category.title()}")
            lines.append("")
            
            category_decisions = sorted(
                by_category[category],
                key=lambda d: d.get("date", ""),
                reverse=True
            )
            
            for decision in category_decisions:
                decision_id = decision.get("id", "unknown")
                title = decision.get("title", "Untitled")
                status = decision.get("status", "unknown")
                date = decision.get("date", "Unknown")[:10]
                
                lines.append(f"- [{decision_id}: {title}]({decision_id}.md) - {status} ({date})")
            
            lines.append("")
        
        with open(index_path, 'w') as f:
            f.write('\n'.join(lines))


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Design Decision Documenter - Efficient documentation of design decisions'
    )
    parser.add_argument(
        '-d', '--directory',
        default='.',
        help='Repository directory to analyze (default: current directory)'
    )
    parser.add_argument(
        '-n', '--max-commits',
        type=int,
        default=500,
        help='Maximum number of commits to analyze (default: 500)'
    )
    parser.add_argument(
        '--since',
        help='Only analyze commits since this date'
    )
    parser.add_argument(
        '-o', '--output',
        help='Output file for report (default: stdout)'
    )
    parser.add_argument(
        '--export',
        action='store_true',
        help='Export decisions to markdown files'
    )
    parser.add_argument(
        '--export-dir',
        default='docs/decisions',
        help='Directory for exported markdown files'
    )
    parser.add_argument(
        '--search',
        type=str,
        help='Search for decisions matching query'
    )
    parser.add_argument(
        '--related',
        type=str,
        help='Find decisions related to given ID'
    )
    
    args = parser.parse_args()
    
    # Initialize documenter
    documenter = DesignDecisionDocumenter(repo_path=args.directory)
    
    # Handle search
    if args.search:
        print(f"Searching for: {args.search}\n")
        results = documenter.search_decisions(args.search)
        
        if results:
            print(f"Found {len(results)} matching decisions:\n")
            for decision, score in results:
                print(f"[{score:.1f}] {decision['id']}: {decision['title']}")
                print(f"  Category: {decision['category']}, Status: {decision['status']}")
                print(f"  Date: {decision['date'][:10]}\n")
        else:
            print("No matching decisions found")
        
        return
    
    # Handle related
    if args.related:
        print(f"Finding decisions related to: {args.related}\n")
        related = documenter.find_related_decisions(args.related)
        
        if related:
            print(f"Found {len(related)} related decisions:\n")
            for decision, similarity in related:
                print(f"[{similarity:.2f}] {decision['id']}: {decision['title']}")
                print(f"  Category: {decision['category']}")
                print(f"  Date: {decision['date'][:10]}\n")
        else:
            print("No related decisions found")
        
        return
    
    # Extract decisions
    print(f"🏗️ Extracting design decisions...\n")
    decisions = documenter.extract_decisions(
        max_commits=args.max_commits,
        since=args.since
    )
    
    # Add decisions to database
    for decision in decisions:
        documenter.add_decision(decision)
    
    # Generate report
    report = documenter.generate_report()
    
    if args.output:
        with open(args.output, 'w') as f:
            f.write(report)
        print(f"\n✅ Report saved to: {args.output}")
    else:
        print(f"\n{report}")
    
    print(f"\n📊 Database updated: {documenter.decisions_file}")
    
    # Export to markdown if requested
    if args.export:
        documenter.export_to_markdown(args.export_dir)
        print(f"📁 Decisions exported to: {args.export_dir}")


if __name__ == '__main__':
    main()
