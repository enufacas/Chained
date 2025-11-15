#!/usr/bin/env python3
"""
PR Content Analyzer - Smart PR Auto-Labeling System
Built by @assert-specialist

Specification:
    - Analyzes PR title, body, changed files, and diff content
    - Generates appropriate labels based on content patterns
    - Maintains label consistency and avoids duplicates
    - Handles edge cases gracefully (empty content, large diffs, etc.)

Invariants:
    - Output is always valid JSON
    - Labels are from the defined label set
    - Confidence scores are between 0.0 and 1.0
    - No duplicate labels in output
"""

import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple
from dataclasses import dataclass, asdict


@dataclass
class LabelRule:
    """Specification for a labeling rule."""
    label: str
    keywords: List[str]
    file_patterns: List[str]
    min_confidence: float = 0.6
    
    def __post_init__(self):
        """Validate invariants."""
        assert 0.0 <= self.min_confidence <= 1.0, "Confidence must be between 0 and 1"
        assert self.label, "Label cannot be empty"
        assert isinstance(self.keywords, list), "Keywords must be a list"
        assert isinstance(self.file_patterns, list), "File patterns must be a list"


@dataclass
class PRAnalysis:
    """Result of PR content analysis."""
    labels: List[str]
    confidence_scores: Dict[str, float]
    analysis_details: Dict[str, any]
    
    def __post_init__(self):
        """Validate invariants."""
        # No duplicate labels
        assert len(self.labels) == len(set(self.labels)), "Labels must be unique"
        # All confidence scores valid
        for score in self.confidence_scores.values():
            assert 0.0 <= score <= 1.0, f"Invalid confidence score: {score}"
        # All labels have confidence scores
        for label in self.labels:
            assert label in self.confidence_scores, f"Missing confidence for {label}"


class PRContentAnalyzer:
    """
    Analyzes PR content and suggests appropriate labels.
    
    Follows specification-driven approach with systematic edge case handling.
    """
    
    # Formal specification of labeling rules
    LABEL_RULES = [
        # Code Quality & Testing
        LabelRule(
            label="code-quality",
            keywords=["refactor", "clean", "improve", "optimize", "simplify", 
                     "complexity", "readability", "maintainability"],
            file_patterns=[r"\.py$", r"\.js$", r"\.ts$", r"\.java$", r"\.go$"]
        ),
        LabelRule(
            label="testing",
            keywords=["test", "spec", "coverage", "assertion", "mock", "stub"],
            file_patterns=[r"test_.*\.py$", r".*_test\.py$", r".*\.test\.js$", 
                          r".*\.spec\.ts$", r"tests/"]
        ),
        
        # Documentation
        LabelRule(
            label="documentation",
            keywords=["doc", "readme", "guide", "tutorial", "documentation",
                     "comment", "javadoc", "docstring"],
            file_patterns=[r"\.md$", r"docs/", r"README", r"CONTRIBUTING"]
        ),
        
        # Agent System
        LabelRule(
            label="agent-system",
            keywords=["agent", "spawner", "evaluator", "registry", "agent-system"],
            file_patterns=[r"\.github/agents/", r"\.github/agent-system/", 
                          r"agent.*\.py$", r".*agent.*\.yml$"]
        ),
        
        # Workflow & Automation
        LabelRule(
            label="workflow-optimization",
            keywords=["workflow", "automation", "ci/cd", "github actions", "pipeline"],
            file_patterns=[r"\.github/workflows/.*\.yml$", r"\.github/workflows/.*\.yaml$"]
        ),
        
        # Learning & AI
        LabelRule(
            label="learning",
            keywords=["learning", "ai", "insight", "pattern", "analysis", "intelligence"],
            file_patterns=[r"learnings/", r"learn.*\.py$", r".*intelligence.*"]
        ),
        
        # Security
        LabelRule(
            label="security",
            keywords=["security", "vulnerability", "cve", "auth", "permission",
                     "sanitize", "validate", "injection", "xss"],
            file_patterns=[r"security", r"auth"]
        ),
        
        # Performance
        LabelRule(
            label="performance",
            keywords=["performance", "speed", "optimize", "cache", "efficiency",
                     "latency", "throughput", "benchmark"],
            file_patterns=[r"benchmark", r"perf"]
        ),
        
        # Bug Fixes
        LabelRule(
            label="bug",
            keywords=["fix", "bug", "error", "crash", "issue", "problem", 
                     "broken", "regression"],
            file_patterns=[]
        ),
        
        # Enhancement/Feature
        LabelRule(
            label="enhancement",
            keywords=["add", "new", "feature", "implement", "create", "enhance"],
            file_patterns=[]
        ),
        
        # GitHub Pages
        LabelRule(
            label="pages-health",
            keywords=["github pages", "gh-pages", "pages", "site", "website"],
            file_patterns=[r"docs/.*\.html$", r"docs/.*\.js$", r"docs/.*\.css$"]
        ),
    ]
    
    def __init__(self):
        """Initialize analyzer with validation."""
        # Validate all rules
        for rule in self.LABEL_RULES:
            assert isinstance(rule, LabelRule), "Invalid rule type"
        
        # Pre-compile regex patterns for efficiency
        self.compiled_patterns = {}
        for rule in self.LABEL_RULES:
            self.compiled_patterns[rule.label] = [
                re.compile(pattern) for pattern in rule.file_patterns
            ]
    
    def analyze_pr(self, title: str, body: str, files: List[str], 
                   diff: str = "") -> PRAnalysis:
        """
        Analyze PR content and return suggested labels.
        
        Args:
            title: PR title
            body: PR body/description
            files: List of changed file paths
            diff: Full PR diff (optional)
        
        Returns:
            PRAnalysis with labels and confidence scores
        
        Preconditions:
            - title must be a string (can be empty)
            - body must be a string (can be empty)
            - files must be a list (can be empty)
            - diff must be a string (can be empty)
        
        Postconditions:
            - Returns valid PRAnalysis object
            - No duplicate labels
            - All confidence scores between 0 and 1
        """
        # Validate preconditions
        assert isinstance(title, str), "Title must be string"
        assert isinstance(body, str), "Body must be string"
        assert isinstance(files, list), "Files must be list"
        assert isinstance(diff, str), "Diff must be string"
        
        # Combine all text for analysis
        text = f"{title} {body} {diff}".lower()
        
        # Track scores for each label
        label_scores: Dict[str, float] = {}
        match_details: Dict[str, List[str]] = {}
        
        # Apply each rule
        for rule in self.LABEL_RULES:
            score = 0.0
            matches = []
            
            # Check keywords in text
            keyword_matches = sum(1 for kw in rule.keywords if kw in text)
            keyword_score = 0.0
            if keyword_matches > 0:
                # Scale keyword score: 1 match = 30%, 2 = 50%, 3+ = 70%+
                keyword_score = min(keyword_matches * 0.25, 0.7)
                matches.append(f"{keyword_matches} keyword(s)")
            
            # Check file patterns
            file_matches = 0
            file_score = 0.0
            for file_path in files:
                for pattern in self.compiled_patterns[rule.label]:
                    if pattern.search(file_path):
                        file_matches += 1
                        break
            
            if file_matches > 0 and files:
                # Scale file score: matches relative to total files
                file_score = min(file_matches / max(len(files), 1) * 0.5, 0.5)
                matches.append(f"{file_matches} file(s)")
            
            # Combined score: keywords can reach 70%, files add up to 50% more
            score = keyword_score + file_score
            
            # Both signals together boost confidence
            if keyword_score > 0 and file_score > 0:
                score = min(score * 1.2, 1.0)  # 20% boost for both signals
            
            # Store if above minimum confidence
            if score >= rule.min_confidence:
                label_scores[rule.label] = score
                match_details[rule.label] = matches
        
        # Sort labels by confidence (highest first)
        sorted_labels = sorted(label_scores.items(), key=lambda x: x[1], reverse=True)
        
        # Extract labels and scores
        labels = [label for label, _ in sorted_labels]
        confidence_scores = {label: score for label, score in sorted_labels}
        
        # Create analysis details
        analysis_details = {
            "title_length": len(title),
            "body_length": len(body),
            "files_changed": len(files),
            "diff_length": len(diff),
            "match_details": match_details,
            "total_rules_evaluated": len(self.LABEL_RULES),
            "labels_suggested": len(labels)
        }
        
        # Create result and validate invariants
        result = PRAnalysis(
            labels=labels,
            confidence_scores=confidence_scores,
            analysis_details=analysis_details
        )
        
        # Validate postconditions
        assert len(result.labels) == len(set(result.labels)), "Duplicate labels detected"
        for score in result.confidence_scores.values():
            assert 0.0 <= score <= 1.0, f"Invalid confidence: {score}"
        
        return result
    
    def analyze_from_json(self, pr_data: Dict) -> PRAnalysis:
        """
        Analyze PR from JSON data structure.
        
        Args:
            pr_data: Dictionary with title, body, files, and optional diff
        
        Returns:
            PRAnalysis result
        """
        # Validate input
        assert isinstance(pr_data, dict), "Input must be dictionary"
        
        # Extract fields with defaults for edge cases
        title = pr_data.get("title", "")
        body = pr_data.get("body", "")
        files = pr_data.get("files", [])
        diff = pr_data.get("diff", "")
        
        # Handle None values (edge case)
        title = title if title is not None else ""
        body = body if body is not None else ""
        files = files if files is not None else []
        diff = diff if diff is not None else ""
        
        return self.analyze_pr(title, body, files, diff)


def main():
    """
    Command-line interface for PR content analyzer.
    
    Reads JSON from stdin or file, outputs analysis to stdout.
    """
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Analyze PR content and suggest labels",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # From stdin
    echo '{"title": "Fix bug", "files": ["src/main.py"]}' | python pr-content-analyzer.py
    
    # From file
    python pr-content-analyzer.py --input pr_data.json
    
    # With output file
    python pr-content-analyzer.py --input pr_data.json --output labels.json
        """
    )
    
    parser.add_argument(
        "--input", "-i",
        help="Input JSON file (default: stdin)",
        type=str
    )
    
    parser.add_argument(
        "--output", "-o",
        help="Output JSON file (default: stdout)",
        type=str
    )
    
    parser.add_argument(
        "--verbose", "-v",
        help="Verbose output with analysis details",
        action="store_true"
    )
    
    args = parser.parse_args()
    
    # Read input
    try:
        if args.input:
            with open(args.input, 'r') as f:
                pr_data = json.load(f)
        else:
            pr_data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON input: {e}", file=sys.stderr)
        return 1
    except FileNotFoundError:
        print(f"Error: Input file not found: {args.input}", file=sys.stderr)
        return 1
    
    # Analyze
    try:
        analyzer = PRContentAnalyzer()
        result = analyzer.analyze_from_json(pr_data)
        
        # Prepare output
        output = {
            "labels": result.labels,
            "confidence_scores": result.confidence_scores
        }
        
        if args.verbose:
            output["analysis_details"] = result.analysis_details
        
        # Write output
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(output, f, indent=2)
            print(f"Analysis written to {args.output}", file=sys.stderr)
        else:
            print(json.dumps(output, indent=2))
        
        return 0
        
    except Exception as e:
        print(f"Error during analysis: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
