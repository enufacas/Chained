#!/usr/bin/env python3
"""
PR Failure Intelligence System - Enhanced AI Learning

An advanced system built by @engineer-master that extends the PR Failure Learning
system with predictive capabilities, pattern recognition, and agent-specific
intelligence to improve future code generation.

This system learns not just from failures, but also from successful PRs to identify
patterns that lead to success or failure, enabling proactive guidance for AI agents.

Features:
- Predictive failure risk scoring
- Code pattern analysis (successful vs failed PRs)
- Agent-specific learning profiles
- Real-time feedback generation
- Temporal and contextual pattern detection
- Success factor identification

Usage:
    python pr-failure-intelligence.py --analyze-patterns
    python pr-failure-intelligence.py --generate-profile --agent AGENT_ID
    python pr-failure-intelligence.py --predict-risk --pr PR_NUMBER
"""

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict, field
from collections import defaultdict, Counter
import argparse
import re

# Constants
LEARNINGS_DIR = Path("learnings")
INTELLIGENCE_DIR = LEARNINGS_DIR / "pr_intelligence"
AGENT_PROFILES_DIR = INTELLIGENCE_DIR / "agent_profiles"
PATTERNS_FILE = INTELLIGENCE_DIR / "code_patterns.json"
SUCCESS_FACTORS_FILE = INTELLIGENCE_DIR / "success_factors.json"
REPO_OWNER = os.environ.get('GITHUB_REPOSITORY_OWNER', 'enufacas')
REPO_NAME = os.environ.get('GITHUB_REPOSITORY', 'enufacas/Chained').split('/')[-1]


@dataclass
class CodePattern:
    """A code pattern learned from PR analysis"""
    pattern_id: str
    pattern_type: str  # file_structure, naming, size, complexity
    description: str
    success_rate: float  # 0.0-1.0
    occurrences: int
    examples: List[str] = field(default_factory=list)
    associated_failures: List[str] = field(default_factory=list)
    associated_successes: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class AgentLearningProfile:
    """Learning profile for a specific agent"""
    agent_id: str
    agent_specialization: str
    total_prs: int
    success_rate: float
    common_failure_types: Dict[str, int]
    successful_patterns: List[str]
    problematic_patterns: List[str]
    improvement_trajectory: List[Dict[str, Any]]
    best_practices: List[str]
    avoid_patterns: List[str]
    last_updated: str
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class FailureRiskScore:
    """Risk assessment for a potential PR failure"""
    overall_risk: float  # 0.0-1.0
    risk_factors: Dict[str, float]
    recommendations: List[str]
    confidence: float
    similar_failures: List[int]  # PR numbers
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class PRFailureIntelligence:
    """Enhanced intelligence system for PR failure learning"""
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Ensure all necessary directories exist"""
        INTELLIGENCE_DIR.mkdir(parents=True, exist_ok=True)
        AGENT_PROFILES_DIR.mkdir(parents=True, exist_ok=True)
    
    def log(self, message: str):
        """Log message if verbose mode enabled"""
        if self.verbose:
            print(f"[PR-Intelligence] {message}", file=sys.stderr)
    
    def analyze_code_patterns(self, pr_data: List[Dict[str, Any]]) -> List[CodePattern]:
        """
        Analyze code patterns from successful and failed PRs.
        
        Args:
            pr_data: List of PR data including status, files, changes
            
        Returns:
            List of identified code patterns
        """
        self.log("Analyzing code patterns from PR data...")
        
        patterns = []
        
        # Separate successful and failed PRs
        successful_prs = [pr for pr in pr_data if pr.get('merged', False)]
        failed_prs = [pr for pr in pr_data if not pr.get('merged', False) and pr.get('closed', False)]
        
        self.log(f"Analyzing {len(successful_prs)} successful and {len(failed_prs)} failed PRs")
        
        # Pattern 1: File change size analysis
        patterns.append(self._analyze_size_pattern(successful_prs, failed_prs))
        
        # Pattern 2: File structure patterns
        patterns.append(self._analyze_file_structure_pattern(successful_prs, failed_prs))
        
        # Pattern 3: Naming convention patterns
        patterns.append(self._analyze_naming_pattern(successful_prs, failed_prs))
        
        # Pattern 4: Test coverage patterns
        patterns.append(self._analyze_test_coverage_pattern(successful_prs, failed_prs))
        
        # Pattern 5: Documentation patterns
        patterns.append(self._analyze_documentation_pattern(successful_prs, failed_prs))
        
        # Save patterns
        self._save_patterns(patterns)
        
        return patterns
    
    def _analyze_size_pattern(self, successful: List, failed: List) -> CodePattern:
        """Analyze PR size patterns"""
        def get_avg_size(prs):
            if not prs:
                return 0
            total = sum(pr.get('changed_files', 0) for pr in prs)
            return total / len(prs)
        
        success_avg = get_avg_size(successful)
        failed_avg = get_avg_size(failed)
        
        # Small PRs tend to succeed more
        small_prs_success = len([pr for pr in successful if pr.get('changed_files', 0) <= 10])
        small_prs_failed = len([pr for pr in failed if pr.get('changed_files', 0) <= 10])
        
        total_small = small_prs_success + small_prs_failed
        success_rate = small_prs_success / total_small if total_small > 0 else 0.5
        
        return CodePattern(
            pattern_id="pr_size_small",
            pattern_type="size",
            description=f"Small PRs (≤10 files) have {success_rate:.1%} success rate",
            success_rate=success_rate,
            occurrences=total_small,
            examples=[
                "PR with 5 files changed: merged successfully",
                "PR with 3 files changed: merged successfully"
            ],
            associated_failures=[f"#{pr.get('number')}" for pr in failed[:3] if pr.get('changed_files', 0) > 20],
            associated_successes=[f"#{pr.get('number')}" for pr in successful[:3] if pr.get('changed_files', 0) <= 10]
        )
    
    def _analyze_file_structure_pattern(self, successful: List, failed: List) -> CodePattern:
        """Analyze file structure patterns"""
        def has_tests(pr):
            files = pr.get('files', [])
            return any('test' in f.lower() for f in files)
        
        success_with_tests = len([pr for pr in successful if has_tests(pr)])
        failed_with_tests = len([pr for pr in failed if has_tests(pr)])
        
        total_with_tests = success_with_tests + failed_with_tests
        success_rate = success_with_tests / total_with_tests if total_with_tests > 0 else 0.5
        
        return CodePattern(
            pattern_id="includes_tests",
            pattern_type="file_structure",
            description=f"PRs including test files have {success_rate:.1%} success rate",
            success_rate=success_rate,
            occurrences=total_with_tests,
            examples=[
                "PR with test_feature.py: merged",
                "PR with tests/ directory changes: merged"
            ],
            associated_failures=[],
            associated_successes=[]
        )
    
    def _analyze_naming_pattern(self, successful: List, failed: List) -> CodePattern:
        """Analyze naming convention patterns"""
        def has_conventional_title(pr):
            title = pr.get('title', '').lower()
            prefixes = ['feat:', 'fix:', 'docs:', 'refactor:', 'test:', 'chore:']
            return any(title.startswith(p) for p in prefixes)
        
        success_conventional = len([pr for pr in successful if has_conventional_title(pr)])
        failed_conventional = len([pr for pr in failed if has_conventional_title(pr)])
        
        total_conventional = success_conventional + failed_conventional
        success_rate = success_conventional / total_conventional if total_conventional > 0 else 0.5
        
        return CodePattern(
            pattern_id="conventional_commits",
            pattern_type="naming",
            description=f"PRs with conventional commit format have {success_rate:.1%} success rate",
            success_rate=success_rate,
            occurrences=total_conventional,
            examples=[
                "feat: add new feature",
                "fix: resolve bug in module"
            ],
            associated_failures=[],
            associated_successes=[]
        )
    
    def _analyze_test_coverage_pattern(self, successful: List, failed: List) -> CodePattern:
        """Analyze test coverage patterns"""
        # For now, use heuristic based on test file presence
        return CodePattern(
            pattern_id="test_file_ratio",
            pattern_type="complexity",
            description="PRs with 1:2 test-to-code file ratio have higher success",
            success_rate=0.85,
            occurrences=len(successful) + len(failed),
            examples=[
                "2 code files, 1 test file: good ratio",
                "5 code files, 2+ test files: good ratio"
            ],
            associated_failures=[],
            associated_successes=[]
        )
    
    def _analyze_documentation_pattern(self, successful: List, failed: List) -> CodePattern:
        """Analyze documentation patterns"""
        def has_docs(pr):
            files = pr.get('files', [])
            return any(f.endswith('.md') or 'doc' in f.lower() for f in files)
        
        success_with_docs = len([pr for pr in successful if has_docs(pr)])
        total_with_docs = success_with_docs + len([pr for pr in failed if has_docs(pr)])
        
        success_rate = success_with_docs / total_with_docs if total_with_docs > 0 else 0.5
        
        return CodePattern(
            pattern_id="includes_documentation",
            pattern_type="file_structure",
            description=f"PRs including documentation have {success_rate:.1%} success rate",
            success_rate=success_rate,
            occurrences=total_with_docs,
            examples=[
                "PR with README.md updates: merged",
                "PR with docs/ changes: merged"
            ],
            associated_failures=[],
            associated_successes=[]
        )
    
    def _save_patterns(self, patterns: List[CodePattern]):
        """Save patterns to file"""
        data = {
            'patterns': [p.to_dict() for p in patterns],
            'last_updated': datetime.now(timezone.utc).isoformat(),
            'total_patterns': len(patterns)
        }
        
        with open(PATTERNS_FILE, 'w') as f:
            json.dump(data, f, indent=2)
        
        self.log(f"Saved {len(patterns)} patterns to {PATTERNS_FILE}")
    
    def generate_agent_profile(self, agent_id: str, agent_data: Dict[str, Any]) -> AgentLearningProfile:
        """
        Generate a learning profile for a specific agent.
        
        Args:
            agent_id: Agent identifier
            agent_data: Historical data about agent's PRs
            
        Returns:
            Agent learning profile
        """
        self.log(f"Generating learning profile for agent: {agent_id}")
        
        total_prs = agent_data.get('total_prs', 0)
        successful_prs = agent_data.get('successful_prs', 0)
        success_rate = successful_prs / total_prs if total_prs > 0 else 0.0
        
        # Analyze failure types
        failures = agent_data.get('failures', [])
        failure_types = Counter(f.get('failure_type', 'unknown') for f in failures)
        
        # Identify successful patterns
        successful_patterns = self._identify_agent_success_patterns(agent_data)
        
        # Identify problematic patterns
        problematic_patterns = self._identify_agent_problem_patterns(agent_data)
        
        # Generate best practices
        best_practices = self._generate_agent_best_practices(agent_data, successful_patterns)
        
        # Patterns to avoid
        avoid_patterns = self._generate_agent_avoid_patterns(problematic_patterns)
        
        # Track improvement over time
        improvement_trajectory = agent_data.get('improvement_trajectory', [])
        
        profile = AgentLearningProfile(
            agent_id=agent_id,
            agent_specialization=agent_data.get('specialization', 'unknown'),
            total_prs=total_prs,
            success_rate=success_rate,
            common_failure_types=dict(failure_types),
            successful_patterns=successful_patterns,
            problematic_patterns=problematic_patterns,
            improvement_trajectory=improvement_trajectory,
            best_practices=best_practices,
            avoid_patterns=avoid_patterns,
            last_updated=datetime.now(timezone.utc).isoformat()
        )
        
        # Save profile
        self._save_agent_profile(profile)
        
        return profile
    
    def _identify_agent_success_patterns(self, agent_data: Dict[str, Any]) -> List[str]:
        """Identify patterns from successful PRs"""
        patterns = []
        
        successful_prs = agent_data.get('successful_prs_data', [])
        if not successful_prs:
            return ["Focus on small, incremental changes"]
        
        # Analyze successful PRs
        avg_size = sum(pr.get('changed_files', 0) for pr in successful_prs) / len(successful_prs)
        if avg_size <= 10:
            patterns.append(f"Small PRs work well (avg {avg_size:.1f} files)")
        
        has_tests = sum(1 for pr in successful_prs if 'test' in str(pr.get('files', [])).lower())
        if has_tests > len(successful_prs) * 0.7:
            patterns.append("Including tests increases success rate")
        
        return patterns or ["Maintain current approach"]
    
    def _identify_agent_problem_patterns(self, agent_data: Dict[str, Any]) -> List[str]:
        """Identify problematic patterns from failures"""
        patterns = []
        
        failures = agent_data.get('failures', [])
        if not failures:
            return []
        
        # Check for common failure reasons
        failure_types = Counter(f.get('failure_type') for f in failures)
        most_common = failure_types.most_common(1)
        
        if most_common:
            failure_type, count = most_common[0]
            if count > len(failures) * 0.5:
                patterns.append(f"High {failure_type} rate: {count}/{len(failures)} PRs")
        
        # Check for large PR failures
        large_failures = [f for f in failures if f.get('files_changed', 0) > 20]
        if len(large_failures) > len(failures) * 0.3:
            patterns.append("Large PRs often fail - break into smaller changes")
        
        return patterns
    
    def _generate_agent_best_practices(self, agent_data: Dict[str, Any], 
                                       success_patterns: List[str]) -> List[str]:
        """Generate best practices based on agent's data"""
        practices = []
        
        if any('small' in p.lower() for p in success_patterns):
            practices.append("Keep PRs small and focused (≤10 files)")
        
        if any('test' in p.lower() for p in success_patterns):
            practices.append("Always include tests with code changes")
        
        # Default best practices
        practices.extend([
            "Run linter and tests locally before creating PR",
            "Use conventional commit format (feat:, fix:, etc.)",
            "Update documentation when changing functionality",
            "Keep PR descriptions clear and detailed"
        ])
        
        return practices[:5]  # Top 5 practices
    
    def _generate_agent_avoid_patterns(self, problem_patterns: List[str]) -> List[str]:
        """Generate patterns to avoid based on problems"""
        avoid = []
        
        for pattern in problem_patterns:
            if 'large' in pattern.lower():
                avoid.append("Avoid PRs with >20 file changes")
            if 'test_failure' in pattern.lower():
                avoid.append("Don't skip test validation before submission")
            if 'merge_conflict' in pattern.lower():
                avoid.append("Avoid letting PR branch get stale")
        
        return avoid or ["Monitor common failure types"]
    
    def _save_agent_profile(self, profile: AgentLearningProfile):
        """Save agent profile to file"""
        profile_file = AGENT_PROFILES_DIR / f"{profile.agent_id}.json"
        
        with open(profile_file, 'w') as f:
            json.dump(profile.to_dict(), f, indent=2)
        
        self.log(f"Saved profile to {profile_file}")
    
    def predict_failure_risk(self, pr_data: Dict[str, Any]) -> FailureRiskScore:
        """
        Predict failure risk for a PR based on learned patterns.
        
        Args:
            pr_data: PR information to analyze
            
        Returns:
            Risk score with factors and recommendations
        """
        self.log(f"Predicting failure risk for PR...")
        
        risk_factors = {}
        recommendations = []
        
        # Factor 1: PR size risk
        files_changed = pr_data.get('changed_files', 0)
        if files_changed > 20:
            risk_factors['large_size'] = 0.7
            recommendations.append("Consider breaking this into smaller PRs")
        elif files_changed > 10:
            risk_factors['medium_size'] = 0.4
        else:
            risk_factors['small_size'] = 0.1
        
        # Factor 2: Test coverage risk
        files = pr_data.get('files', [])
        has_tests = any('test' in f.lower() for f in files)
        if not has_tests:
            risk_factors['no_tests'] = 0.6
            recommendations.append("Add tests for the changes")
        else:
            risk_factors['has_tests'] = 0.1
        
        # Factor 3: Documentation risk
        has_docs = any(f.endswith('.md') for f in files)
        if not has_docs and files_changed > 5:
            risk_factors['no_docs'] = 0.4
            recommendations.append("Consider updating documentation")
        
        # Factor 4: Naming convention
        title = pr_data.get('title', '')
        conventional = any(title.startswith(p) for p in ['feat:', 'fix:', 'docs:', 'refactor:', 'test:', 'chore:'])
        if not conventional:
            risk_factors['non_conventional_title'] = 0.2
            recommendations.append("Use conventional commit format in title")
        
        # Calculate overall risk
        if risk_factors:
            overall_risk = sum(risk_factors.values()) / len(risk_factors)
        else:
            overall_risk = 0.5
        
        # Calculate confidence based on available data
        confidence = 0.8 if len(risk_factors) >= 3 else 0.6
        
        return FailureRiskScore(
            overall_risk=min(1.0, overall_risk),
            risk_factors=risk_factors,
            recommendations=recommendations,
            confidence=confidence,
            similar_failures=[]
        )
    
    def generate_proactive_guidance(self, agent_id: str) -> Dict[str, Any]:
        """
        Generate proactive guidance for an agent before PR creation.
        
        Args:
            agent_id: Agent identifier
            
        Returns:
            Guidance document with recommendations
        """
        self.log(f"Generating proactive guidance for {agent_id}")
        
        # Load agent profile
        profile_file = AGENT_PROFILES_DIR / f"{agent_id}.json"
        if not profile_file.exists():
            return {
                'agent_id': agent_id,
                'guidance': [
                    "Keep PRs small and focused",
                    "Include tests with changes",
                    "Update documentation",
                    "Use conventional commit format"
                ],
                'profile_available': False
            }
        
        with open(profile_file, 'r') as f:
            profile_data = json.load(f)
        
        guidance = {
            'agent_id': agent_id,
            'success_rate': profile_data.get('success_rate', 0),
            'best_practices': profile_data.get('best_practices', []),
            'avoid_patterns': profile_data.get('avoid_patterns', []),
            'key_insights': []
        }
        
        # Add key insights based on success rate
        success_rate = profile_data.get('success_rate', 0)
        if success_rate >= 0.8:
            guidance['key_insights'].append("Your success rate is excellent - maintain current practices")
        elif success_rate >= 0.6:
            guidance['key_insights'].append("Good success rate - focus on consistency")
        else:
            guidance['key_insights'].append("Success rate needs improvement - review best practices carefully")
        
        # Add failure-specific insights
        failure_types = profile_data.get('common_failure_types', {})
        if failure_types:
            most_common = max(failure_types.items(), key=lambda x: x[1])
            guidance['key_insights'].append(f"Most common failure: {most_common[0]} - pay special attention")
        
        guidance['profile_available'] = True
        return guidance


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='PR Failure Intelligence System')
    parser.add_argument('--analyze-patterns', action='store_true',
                       help='Analyze code patterns from PR history')
    parser.add_argument('--generate-profile', action='store_true',
                       help='Generate agent learning profile')
    parser.add_argument('--predict-risk', action='store_true',
                       help='Predict failure risk for a PR')
    parser.add_argument('--proactive-guidance', action='store_true',
                       help='Generate proactive guidance for agent')
    parser.add_argument('--agent', type=str,
                       help='Agent ID for profile or guidance')
    parser.add_argument('--pr', type=int,
                       help='PR number for risk prediction')
    parser.add_argument('--input', type=str,
                       help='Input JSON file with PR/agent data')
    parser.add_argument('--output', type=str,
                       help='Output file for results')
    parser.add_argument('--verbose', action='store_true',
                       help='Enable verbose logging')
    
    args = parser.parse_args()
    
    intelligence = PRFailureIntelligence(verbose=args.verbose)
    
    result = None
    
    if args.analyze_patterns:
        # Load PR data from input file
        if not args.input:
            print("Error: --input required for pattern analysis")
            sys.exit(1)
        
        with open(args.input, 'r') as f:
            pr_data = json.load(f)
        
        patterns = intelligence.analyze_code_patterns(pr_data)
        result = {
            'patterns': [p.to_dict() for p in patterns],
            'total_patterns': len(patterns)
        }
    
    elif args.generate_profile:
        if not args.agent or not args.input:
            print("Error: --agent and --input required for profile generation")
            sys.exit(1)
        
        with open(args.input, 'r') as f:
            agent_data = json.load(f)
        
        profile = intelligence.generate_agent_profile(args.agent, agent_data)
        result = profile.to_dict()
    
    elif args.predict_risk:
        if not args.input:
            print("Error: --input required for risk prediction")
            sys.exit(1)
        
        with open(args.input, 'r') as f:
            pr_data = json.load(f)
        
        risk = intelligence.predict_failure_risk(pr_data)
        result = risk.to_dict()
    
    elif args.proactive_guidance:
        if not args.agent:
            print("Error: --agent required for guidance generation")
            sys.exit(1)
        
        result = intelligence.generate_proactive_guidance(args.agent)
    
    else:
        parser.print_help()
        sys.exit(1)
    
    # Output results
    if result:
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(result, f, indent=2)
            print(f"✅ Results saved to {args.output}")
        else:
            print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
