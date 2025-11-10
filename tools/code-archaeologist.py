#!/usr/bin/env python3
"""
AI Code Archaeologist for Chained

This tool analyzes git history to document legacy decisions, tracking why
code exists, how architecture evolved, and what technical debt remains.
"""

import os
import sys
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict


class CodeArchaeologist:
    """Analyzes git history to document legacy decisions"""
    
    def __init__(self, repo_path: str = ".", archaeology_file: str = "analysis/archaeology.json"):
        self.repo_path = repo_path
        self.archaeology_file = archaeology_file
        self.archaeology_data = self._load_archaeology()
        
    def _load_archaeology(self) -> Dict:
        """Load existing archaeology database"""
        if os.path.exists(self.archaeology_file):
            with open(self.archaeology_file, 'r') as f:
                return json.load(f)
        return self._initialize_archaeology()
    
    def _initialize_archaeology(self) -> Dict:
        """Initialize archaeology database"""
        return {
            "version": "1.0.0",
            "last_updated": None,
            "repository": os.path.basename(os.path.abspath(self.repo_path)),
            "total_commits_analyzed": 0,
            "architectural_decisions": [],
            "technical_debt": [],
            "legacy_patterns": [],
            "code_evolution": {
                "major_refactors": [],
                "feature_additions": [],
                "bug_fixes": []
            },
            "decision_timeline": []
        }
    
    def _save_archaeology(self):
        """Save archaeology database"""
        self.archaeology_data["last_updated"] = datetime.now(timezone.utc).isoformat()
        os.makedirs(os.path.dirname(self.archaeology_file), exist_ok=True)
        with open(self.archaeology_file, 'w') as f:
            json.dump(self.archaeology_data, f, indent=2)
    
    def _run_git_command(self, args: List[str]) -> str:
        """Run a git command and return output"""
        try:
            result = subprocess.run(
                ['git'] + args,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            print(f"Git command failed: {e}", file=sys.stderr)
            return ""
    
    def _parse_commit(self, commit_hash: str) -> Optional[Dict]:
        """Parse detailed information from a commit"""
        try:
            # Get commit details
            commit_info = self._run_git_command([
                'show', '--format=%H%n%an%n%ae%n%at%n%s%n%b', '--no-patch', commit_hash
            ])
            
            if not commit_info:
                return None
            
            lines = commit_info.split('\n')
            if len(lines) < 5:
                return None
            
            commit_data = {
                "hash": lines[0],
                "author": lines[1],
                "email": lines[2],
                "timestamp": datetime.fromtimestamp(int(lines[3]), tz=timezone.utc).isoformat(),
                "subject": lines[4],
                "body": '\n'.join(lines[5:]).strip() if len(lines) > 5 else "",
                "files_changed": []
            }
            
            # Get files changed
            files_changed = self._run_git_command([
                'diff-tree', '--no-commit-id', '--name-only', '-r', commit_hash
            ])
            
            if files_changed:
                commit_data["files_changed"] = files_changed.split('\n')
            
            # Get statistics
            stats = self._run_git_command([
                'show', '--format=', '--shortstat', commit_hash
            ])
            
            commit_data["stats"] = stats
            
            return commit_data
            
        except Exception as e:
            print(f"Error parsing commit {commit_hash}: {e}", file=sys.stderr)
            return None
    
    def _categorize_commit(self, commit: Dict) -> str:
        """Categorize a commit based on its content"""
        subject = commit["subject"].lower()
        body = commit["body"].lower()
        combined = f"{subject} {body}"
        
        # Architectural decision indicators
        arch_keywords = [
            'architect', 'design', 'refactor', 'restructure', 'migrate',
            'consolidate', 'organize', 'pattern', 'approach', 'strategy'
        ]
        
        # Technical debt indicators
        debt_keywords = [
            'todo', 'fixme', 'hack', 'workaround', 'temporary', 'quick fix',
            'debt', 'legacy', 'deprecated'
        ]
        
        # Feature addition indicators
        feature_keywords = [
            'add', 'implement', 'create', 'new', 'feature', 'introduce',
            'support', 'enable'
        ]
        
        # Bug fix indicators
        bug_keywords = [
            'fix', 'bug', 'issue', 'error', 'problem', 'resolve', 'correct',
            'patch'
        ]
        
        # Check categories
        if any(keyword in combined for keyword in arch_keywords):
            return "architectural"
        elif any(keyword in combined for keyword in debt_keywords):
            return "technical_debt"
        elif any(keyword in combined for keyword in bug_keywords):
            return "bug_fix"
        elif any(keyword in combined for keyword in feature_keywords):
            return "feature"
        else:
            return "maintenance"
    
    def _extract_decisions(self, commit: Dict) -> List[Dict]:
        """Extract decision information from commit"""
        decisions = []
        combined_text = f"{commit['subject']}\n{commit['body']}"
        
        # Look for decision patterns
        decision_patterns = [
            r'(?:decided to|chose to|opted for|changed to|migrated to|switched to)\s+(.+?)(?:\.|$)',
            r'(?:because|since|as|due to)\s+(.+?)(?:\.|$)',
            r'(?:reason|rationale):\s*(.+?)(?:\.|$)',
            r'why:\s*(.+?)(?:\.|$)',
        ]
        
        for pattern in decision_patterns:
            matches = re.findall(pattern, combined_text, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                decisions.append({
                    "type": "explicit_decision",
                    "content": match.strip(),
                    "commit": commit["hash"][:7],
                    "timestamp": commit["timestamp"]
                })
        
        return decisions
    
    def _extract_technical_debt(self, commit: Dict) -> List[Dict]:
        """Extract technical debt mentions from commit"""
        debt_items = []
        combined_text = f"{commit['subject']}\n{commit['body']}"
        
        # Look for debt patterns
        debt_patterns = [
            r'TODO:\s*(.+?)(?:\n|$)',
            r'FIXME:\s*(.+?)(?:\n|$)',
            r'HACK:\s*(.+?)(?:\n|$)',
            r'workaround for\s+(.+?)(?:\.|$)',
            r'temporary\s+(.+?)(?:\.|$)',
        ]
        
        for pattern in debt_patterns:
            matches = re.findall(pattern, combined_text, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                debt_items.append({
                    "type": "technical_debt",
                    "description": match.strip(),
                    "commit": commit["hash"][:7],
                    "timestamp": commit["timestamp"],
                    "files": commit["files_changed"]
                })
        
        return debt_items
    
    def analyze_repository(self, max_commits: int = 100, since: Optional[str] = None) -> Dict:
        """Analyze repository history to document decisions"""
        print(f"Analyzing repository history...")
        
        # Get commit list
        git_args = ['log', '--format=%H', f'-{max_commits}']
        if since:
            git_args.append(f'--since={since}')
        
        commit_hashes = self._run_git_command(git_args)
        
        if not commit_hashes:
            print("No commits found")
            return {"error": "No commits found"}
        
        commits = commit_hashes.split('\n')
        total_commits = len(commits)
        
        print(f"Found {total_commits} commits to analyze")
        
        results = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "commits_analyzed": total_commits,
            "architectural_decisions": [],
            "technical_debt": [],
            "code_evolution": {
                "major_refactors": [],
                "feature_additions": [],
                "bug_fixes": [],
                "maintenance": []
            },
            "statistics": {
                "total_commits": total_commits,
                "by_category": defaultdict(int),
                "by_author": defaultdict(int),
                "files_most_changed": defaultdict(int)
            }
        }
        
        # Analyze each commit
        for i, commit_hash in enumerate(commits):
            if i % 10 == 0:
                print(f"Processing commit {i+1}/{total_commits}...")
            
            commit = self._parse_commit(commit_hash)
            if not commit:
                continue
            
            # Categorize commit
            category = self._categorize_commit(commit)
            results["statistics"]["by_category"][category] += 1
            results["statistics"]["by_author"][commit["author"]] += 1
            
            # Track file changes
            for file in commit["files_changed"]:
                results["statistics"]["files_most_changed"][file] += 1
            
            # Extract decisions
            decisions = self._extract_decisions(commit)
            if decisions:
                results["architectural_decisions"].extend(decisions)
            
            # Extract technical debt
            debt = self._extract_technical_debt(commit)
            if debt:
                results["technical_debt"].extend(debt)
            
            # Categorize in evolution
            commit_summary = {
                "hash": commit["hash"][:7],
                "subject": commit["subject"],
                "author": commit["author"],
                "timestamp": commit["timestamp"],
                "files_changed": len(commit["files_changed"]),
                "stats": commit["stats"]
            }
            
            if category == "architectural":
                results["code_evolution"]["major_refactors"].append(commit_summary)
            elif category == "feature":
                results["code_evolution"]["feature_additions"].append(commit_summary)
            elif category == "bug_fix":
                results["code_evolution"]["bug_fixes"].append(commit_summary)
            else:
                results["code_evolution"]["maintenance"].append(commit_summary)
        
        # Update archaeology data
        self.archaeology_data["total_commits_analyzed"] = total_commits
        self.archaeology_data["architectural_decisions"] = results["architectural_decisions"]
        self.archaeology_data["technical_debt"] = results["technical_debt"]
        self.archaeology_data["code_evolution"] = results["code_evolution"]
        
        # Create decision timeline
        timeline = []
        for decision in results["architectural_decisions"]:
            timeline.append({
                "timestamp": decision["timestamp"],
                "type": "decision",
                "content": decision["content"],
                "commit": decision["commit"]
            })
        
        for debt in results["technical_debt"]:
            timeline.append({
                "timestamp": debt["timestamp"],
                "type": "debt",
                "content": debt["description"],
                "commit": debt["commit"]
            })
        
        # Sort timeline by timestamp
        timeline.sort(key=lambda x: x["timestamp"])
        self.archaeology_data["decision_timeline"] = timeline
        
        self._save_archaeology()
        
        return results
    
    def generate_report(self, results: Dict) -> str:
        """Generate human-readable archaeology report"""
        report = []
        report.append("# 🏛️ Code Archaeology Report")
        report.append(f"\n**Generated:** {results['timestamp']}")
        report.append(f"\n**Repository:** {self.archaeology_data['repository']}")
        
        # Summary
        report.append(f"\n## 📊 Summary")
        report.append(f"- Total commits analyzed: {results['commits_analyzed']}")
        report.append(f"- Architectural decisions found: {len(results['architectural_decisions'])}")
        report.append(f"- Technical debt items found: {len(results['technical_debt'])}")
        
        # Statistics
        stats = results["statistics"]
        report.append(f"\n## 📈 Statistics")
        
        report.append(f"\n### Commits by Category")
        for category, count in sorted(stats["by_category"].items(), key=lambda x: x[1], reverse=True):
            report.append(f"- **{category}**: {count} commits")
        
        report.append(f"\n### Top Contributors")
        for author, count in sorted(stats["by_author"].items(), key=lambda x: x[1], reverse=True)[:5]:
            report.append(f"- **{author}**: {count} commits")
        
        report.append(f"\n### Most Changed Files")
        for file, count in sorted(stats["files_most_changed"].items(), key=lambda x: x[1], reverse=True)[:10]:
            report.append(f"- `{file}`: {count} changes")
        
        # Architectural Decisions
        if results["architectural_decisions"]:
            report.append(f"\n## 🏗️ Architectural Decisions")
            report.append(f"\nFound {len(results['architectural_decisions'])} documented decisions:\n")
            
            for i, decision in enumerate(results["architectural_decisions"][:10], 1):
                report.append(f"{i}. **{decision['content']}**")
                report.append(f"   - Commit: `{decision['commit']}`")
                report.append(f"   - Date: {decision['timestamp'][:10]}\n")
        
        # Technical Debt
        if results["technical_debt"]:
            report.append(f"\n## ⚠️ Technical Debt")
            report.append(f"\nFound {len(results['technical_debt'])} technical debt items:\n")
            
            for i, debt in enumerate(results["technical_debt"][:10], 1):
                report.append(f"{i}. **{debt['description']}**")
                report.append(f"   - Commit: `{debt['commit']}`")
                report.append(f"   - Date: {debt['timestamp'][:10]}")
                if debt["files"]:
                    report.append(f"   - Files: {', '.join(debt['files'][:3])}\n")
        
        # Code Evolution
        evolution = results["code_evolution"]
        report.append(f"\n## 📜 Code Evolution")
        
        if evolution["major_refactors"]:
            report.append(f"\n### Major Refactors ({len(evolution['major_refactors'])})")
            for refactor in evolution["major_refactors"][:5]:
                report.append(f"- `{refactor['hash']}`: {refactor['subject']} ({refactor['timestamp'][:10]})")
        
        if evolution["feature_additions"]:
            report.append(f"\n### Feature Additions ({len(evolution['feature_additions'])})")
            for feature in evolution["feature_additions"][:5]:
                report.append(f"- `{feature['hash']}`: {feature['subject']} ({feature['timestamp'][:10]})")
        
        if evolution["bug_fixes"]:
            report.append(f"\n### Bug Fixes ({len(evolution['bug_fixes'])})")
            for fix in evolution["bug_fixes"][:5]:
                report.append(f"- `{fix['hash']}`: {fix['subject']} ({fix['timestamp'][:10]})")
        
        # Insights
        report.append(f"\n## 💡 Insights")
        
        if results["architectural_decisions"]:
            report.append("- 📝 This repository has documented architectural decisions in commit messages")
        else:
            report.append("- ⚠️ Few explicit architectural decisions found - consider documenting reasoning in commits")
        
        if len(results["technical_debt"]) > 0:
            report.append(f"- ⚠️ {len(results['technical_debt'])} technical debt items identified - consider addressing them")
        
        refactor_ratio = stats["by_category"].get("architectural", 0) / max(results["commits_analyzed"], 1)
        if refactor_ratio > 0.2:
            report.append(f"- 🏗️ High refactoring activity ({refactor_ratio:.1%}) suggests active code improvement")
        
        # Recommendations
        report.append(f"\n## 🎯 Recommendations")
        
        if not results["architectural_decisions"]:
            report.append("- 📚 Document architectural decisions in commit messages using clear language")
            report.append("- 💬 Include 'why' explanations, not just 'what' changes")
        
        if results["technical_debt"]:
            report.append(f"- 🔧 Address {len(results['technical_debt'])} documented technical debt items")
            report.append("- 📋 Create issues for TODO/FIXME items to track them properly")
        
        report.append("- 📖 Continue documenting legacy decisions for future maintainers")
        report.append("- 🔍 Run this tool regularly to track decision evolution")
        
        return '\n'.join(report)


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='AI Code Archaeologist - Document legacy decisions from git history'
    )
    parser.add_argument(
        '-d', '--directory',
        default='.',
        help='Repository directory to analyze (default: current directory)'
    )
    parser.add_argument(
        '-n', '--max-commits',
        type=int,
        default=100,
        help='Maximum number of commits to analyze (default: 100)'
    )
    parser.add_argument(
        '--since',
        help='Only analyze commits since this date (e.g., "2023-01-01", "1 month ago")'
    )
    parser.add_argument(
        '-o', '--output',
        help='Output file for report (default: stdout)'
    )
    parser.add_argument(
        '--format',
        choices=['text', 'json'],
        default='text',
        help='Output format (default: text)'
    )
    
    args = parser.parse_args()
    
    # Initialize archaeologist
    archaeologist = CodeArchaeologist(repo_path=args.directory)
    
    # Analyze repository
    print(f"🏛️ Starting code archaeology...\n")
    results = archaeologist.analyze_repository(
        max_commits=args.max_commits,
        since=args.since
    )
    
    if "error" in results:
        print(f"Error: {results['error']}", file=sys.stderr)
        sys.exit(1)
    
    # Generate output
    if args.format == 'json':
        output = json.dumps(results, indent=2)
    else:
        output = archaeologist.generate_report(results)
    
    # Write output
    if args.output:
        with open(args.output, 'w') as f:
            f.write(output)
        print(f"\n✅ Report saved to: {args.output}")
    else:
        print(output)
    
    # Save detailed analysis
    analysis_file = f"analysis/archaeology_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json"
    os.makedirs('analysis', exist_ok=True)
    with open(analysis_file, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\n📁 Detailed analysis saved to: {analysis_file}")
    print(f"📊 Archaeology database updated: {archaeologist.archaeology_file}")


if __name__ == '__main__':
    main()
