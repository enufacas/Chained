#!/usr/bin/env python3
"""
Tech Lead Assignment Filter - Selective Assignment Logic

This script determines if a PR requires tech lead review based on selective criteria.
Goal: Reduce assignments from 13-39 to 5-15 per run by skipping trivial changes.

Usage:
    python3 tools/filter-tech-lead-assignment.py <pr_number>

Exit codes:
    0 - Tech lead review REQUIRED
    1 - Tech lead review SKIPPED (trivial change)
    2 - Error (treat as requiring review for safety)
"""

import sys
import json
import subprocess
import re
from typing import Dict, Any, Tuple, List

# Selective criteria
SKIP_PATTERNS = {
    "dependabot": r"dependabot",
    "typo_fix": r"(typo|spelling|grammar)",
    "docs_only": r"(docs?|readme|documentation|\.md$)",
    "formatting": r"(format|prettier|eslint|style)",
}

REQUIRE_PATTERNS = {
    "security": r"(security|vuln|cve|auth|crypto|password|token|secret)",
    "protected_paths": r"(\.github/workflows|\.github/agents|tools/.*\.py)",
}

# Thresholds
LARGE_PR_FILES = 10  # More than 10 files changed
LARGE_PR_LINES = 200  # More than 200 lines changed


def get_pr_details(pr_number: int) -> Dict[str, Any]:
    """Fetch PR details using gh CLI."""
    try:
        result = subprocess.run(
            [
                "gh", "pr", "view", str(pr_number),
                "--json", "title,body,files,additions,deletions,author,labels,isDraft"
            ],
            capture_output=True,
            text=True,
            check=True
        )
        return json.loads(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Failed to fetch PR #{pr_number}: {e}", file=sys.stderr)
        sys.exit(2)
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON response: {e}", file=sys.stderr)
        sys.exit(2)


def check_skip_patterns(text: str, pr_data: Dict[str, Any]) -> Tuple[bool, str]:
    """Check if PR matches skip patterns (trivial changes)."""
    text_lower = text.lower()
    
    # Check author
    author = pr_data.get("author", {}).get("login", "").lower()
    if "dependabot" in author:
        return True, "dependabot_pr"
    
    # Check title/body patterns
    for reason, pattern in SKIP_PATTERNS.items():
        if re.search(pattern, text_lower, re.IGNORECASE):
            return True, reason
    
    return False, ""


def check_require_patterns(text: str, files: List[Dict]) -> Tuple[bool, str]:
    """Check if PR matches require patterns (must have review)."""
    text_lower = text.lower()
    
    # Check security keywords
    if re.search(REQUIRE_PATTERNS["security"], text_lower, re.IGNORECASE):
        return True, "security_keywords"
    
    # Check protected paths
    for file_info in files:
        path = file_info.get("path", "")
        if re.search(REQUIRE_PATTERNS["protected_paths"], path, re.IGNORECASE):
            return True, f"protected_path:{path}"
    
    return False, ""


def get_pr_change_stats(pr_data: Dict[str, Any]) -> Tuple[int, int, int]:
    """
    Extract change statistics from PR data.
    
    Returns:
        (files_changed, additions, deletions)
    """
    files_changed = len(pr_data.get("files", []))
    additions = pr_data.get("additions", 0)
    deletions = pr_data.get("deletions", 0)
    return files_changed, additions, deletions


def is_large_pr(pr_data: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Check if PR is large enough to require review.
    
    Uses AND logic: Both many files AND many lines must be true.
    This ensures we only flag truly large PRs that need careful review.
    """
    files_changed, additions, deletions = get_pr_change_stats(pr_data)
    total_lines = additions + deletions
    
    if files_changed > LARGE_PR_FILES and total_lines > LARGE_PR_LINES:
        return True, f"large_pr:{files_changed}_files_{total_lines}_lines"
    
    return False, ""


def is_single_line_change(pr_data: Dict[str, Any]) -> Tuple[bool, str]:
    """Check if PR is a single-line change."""
    files_changed, additions, deletions = get_pr_change_stats(pr_data)
    
    if files_changed == 1 and additions + deletions <= 3:
        return True, "single_line_change"
    
    return False, ""


def is_docs_only(files: List[Dict]) -> Tuple[bool, str]:
    """Check if PR only modifies documentation files."""
    if not files:
        return False, ""
    
    doc_extensions = [".md", ".txt", ".rst", ".adoc"]
    doc_paths = ["docs/", "documentation/", "README"]
    
    for file_info in files:
        path = file_info.get("path", "")
        
        # Check if NOT a doc file
        is_doc = any(path.endswith(ext) for ext in doc_extensions)
        is_doc = is_doc or any(doc_path in path for doc_path in doc_paths)
        
        if not is_doc:
            return False, ""
    
    return True, "docs_only_changes"


def should_skip_review(pr_number: int) -> Tuple[bool, str, Dict[str, Any]]:
    """
    Determine if tech lead review should be skipped.
    
    Returns:
        (skip, reason, context)
    """
    pr_data = get_pr_details(pr_number)
    
    # Never skip drafts - they're WIP
    if pr_data.get("isDraft", False):
        return False, "draft_pr", {}
    
    title = pr_data.get("title", "")
    body = pr_data.get("body", "")
    files = pr_data.get("files", [])
    
    combined_text = f"{title} {body}"
    
    # Check if review is REQUIRED (security, protected paths, large PR)
    require, reason = check_require_patterns(combined_text, files)
    if require:
        return False, f"required:{reason}", {"pr_data": pr_data}
    
    large, reason = is_large_pr(pr_data)
    if large:
        return False, f"required:{reason}", {"pr_data": pr_data}
    
    # Check if review can be SKIPPED (trivial changes)
    skip, reason = check_skip_patterns(combined_text, pr_data)
    if skip:
        return True, f"skip:{reason}", {"pr_data": pr_data}
    
    single_line, reason = is_single_line_change(pr_data)
    if single_line:
        return True, f"skip:{reason}", {"pr_data": pr_data}
    
    docs_only, reason = is_docs_only(files)
    if docs_only:
        return True, f"skip:{reason}", {"pr_data": pr_data}
    
    # Default: require review (safety)
    return False, "default_require", {"pr_data": pr_data}


def main():
    if len(sys.argv) != 2:
        print("Usage: filter-tech-lead-assignment.py <pr_number>", file=sys.stderr)
        sys.exit(2)
    
    try:
        pr_number = int(sys.argv[1])
    except ValueError:
        print(f"ERROR: Invalid PR number: {sys.argv[1]}", file=sys.stderr)
        sys.exit(2)
    
    skip, reason, context = should_skip_review(pr_number)
    
    # Get PR stats
    pr_data = context.get("pr_data", {})
    files_changed, additions, deletions = get_pr_change_stats(pr_data)
    
    # Output decision
    if skip:
        print(f"SKIP: PR #{pr_number} - {reason}")
        print(json.dumps({
            "pr_number": pr_number,
            "decision": "skip",
            "reason": reason,
            "title": pr_data.get("title", ""),
            "files_changed": files_changed,
            "lines_changed": additions + deletions
        }, indent=2))
        sys.exit(1)  # Exit 1 = skip review
    else:
        print(f"REQUIRE: PR #{pr_number} - {reason}")
        print(json.dumps({
            "pr_number": pr_number,
            "decision": "require",
            "reason": reason,
            "title": pr_data.get("title", ""),
            "files_changed": files_changed,
            "lines_changed": additions + deletions
        }, indent=2))
        sys.exit(0)  # Exit 0 = require review


if __name__ == "__main__":
    main()
