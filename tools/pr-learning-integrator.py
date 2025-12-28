#!/usr/bin/env python3
"""
PR Learning Integrator - Connect Learning to Code Generation

Built by @create-botter to bridge the gap between PR failure learning
and active code generation. This tool extracts insights from historical
PR data and formats them for injection into issue assignments, providing
AI agents with proactive guidance based on past successes and failures.

Features:
- Load and analyze PR failure history
- Extract agent-specific learning profiles
- Generate proactive warnings for common pitfalls
- Surface success patterns from similar PRs
- Format guidance for GitHub issue injection
- Support real-time and scheduled modes

Usage:
    # Get guidance for a specific agent
    python pr-learning-integrator.py --agent create-botter --issue-title "Add new feature"
    
    # Get guidance for an issue number
    python pr-learning-integrator.py --issue 123
    
    # Generate formatted issue body section
    python pr-learning-integrator.py --agent engineer-master --format issue-body
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from collections import Counter
import argparse


# Constants
LEARNINGS_DIR = Path("learnings")
PR_FAILURES_FILE = LEARNINGS_DIR / "pr_failures.json"
INTELLIGENCE_DIR = LEARNINGS_DIR / "pr_intelligence"
AGENT_PROFILES_DIR = INTELLIGENCE_DIR / "agent_profiles"
PATTERNS_FILE = INTELLIGENCE_DIR / "code_patterns.json"
AGENT_SYSTEM_DIR = Path(".github/agent-system")
REGISTRY_FILE = AGENT_SYSTEM_DIR / "registry.json"


@dataclass
class ProactiveWarning:
    """Warning based on historical failures"""
    warning_type: str  # failure_rate, common_pitfall, code_quality, review_issue
    severity: str  # high, medium, low
    message: str
    examples: List[str] = field(default_factory=list)
    mitigation: str = ""
    
    def to_markdown(self) -> str:
        """Format as markdown for issue body"""
        emoji = "🔴" if self.severity == "high" else "🟡" if self.severity == "medium" else "🔵"
        md = f"- {emoji} {self.message}"
        if self.examples:
            md += f" (Examples: {', '.join(f'#{ex}' for ex in self.examples[:3])})"
        return md


@dataclass
class SuccessPattern:
    """Success pattern from historical PRs"""
    pattern_type: str  # code_structure, test_coverage, documentation, size
    description: str
    success_rate: float
    recommendation: str
    examples: List[str] = field(default_factory=list)
    
    def to_markdown(self) -> str:
        """Format as markdown for issue body"""
        rate_pct = int(self.success_rate * 100)
        md = f"- {self.description} have {rate_pct}% success rate"
        if self.examples:
            md += f" (e.g., {', '.join(f'#{ex}' for ex in self.examples[:2])})"
        return md


@dataclass
class AgentGuidance:
    """Complete guidance package for an agent"""
    agent_id: str
    agent_specialization: str
    warnings: List[ProactiveWarning] = field(default_factory=list)
    success_patterns: List[SuccessPattern] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    stats: Dict[str, Any] = field(default_factory=dict)
    
    def to_issue_body_section(self) -> str:
        """Format complete guidance for GitHub issue body"""
        sections = []
        
        # Warnings section
        if self.warnings:
            sections.append("### ⚠️ Proactive Warnings\n")
            sections.append(f"Based on historical PR failures, **@{self.agent_id}** should be aware of:\n")
            for warning in self.warnings:
                sections.append(warning.to_markdown())
            sections.append("")
        
        # Recommendations section
        if self.recommendations:
            sections.append("### ✅ Recommended Approach\n")
            for rec in self.recommendations:
                sections.append(f"- ✅ {rec}")
            sections.append("")
        
        # Success patterns section
        if self.success_patterns:
            sections.append("### 🎯 Success Patterns\n")
            sections.append("PRs that follow these patterns have high success rates:\n")
            for pattern in self.success_patterns:
                sections.append(pattern.to_markdown())
            sections.append("")
        
        # Stats section
        if self.stats:
            sections.append("### 📊 Historical Performance\n")
            if 'total_prs' in self.stats:
                sections.append(f"- **Total PRs**: {self.stats['total_prs']}")
            if 'success_rate' in self.stats:
                rate = int(self.stats['success_rate'] * 100)
                sections.append(f"- **Success Rate**: {rate}%")
            if 'recent_failures' in self.stats and self.stats['recent_failures'] > 0:
                sections.append(f"- **Recent Failures**: {self.stats['recent_failures']}")
            sections.append("")
        
        return "\n".join(sections)


class PRLearningIntegrator:
    """Main class for integrating PR learning into code generation"""
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.pr_failures = []
        self.code_patterns = []
        self.agent_profiles = {}
        
        # Load data
        self._load_pr_failures()
        self._load_code_patterns()
        self._load_agent_profiles()
    
    def log(self, message: str):
        """Log message if verbose mode enabled"""
        if self.verbose:
            print(f"[Learning-Integrator] {message}", file=sys.stderr)
    
    def _load_pr_failures(self):
        """Load PR failure data"""
        if not PR_FAILURES_FILE.exists():
            self.log("No PR failures file found")
            return
        
        try:
            with open(PR_FAILURES_FILE, 'r') as f:
                data = json.load(f)
                self.pr_failures = data.get('failures', [])
                self.log(f"Loaded {len(self.pr_failures)} PR failures")
        except (FileNotFoundError, json.JSONDecodeError, IOError) as e:
            self.log(f"Error loading PR failures: {e}")
    
    def _load_code_patterns(self):
        """Load code pattern analysis"""
        if not PATTERNS_FILE.exists():
            self.log("No code patterns file found")
            return
        
        try:
            with open(PATTERNS_FILE, 'r') as f:
                data = json.load(f)
                self.code_patterns = data.get('patterns', [])
                self.log(f"Loaded {len(self.code_patterns)} code patterns")
        except (FileNotFoundError, json.JSONDecodeError, IOError) as e:
            self.log(f"Error loading code patterns: {e}")
    
    def _load_agent_profiles(self):
        """Load agent learning profiles"""
        if not AGENT_PROFILES_DIR.exists():
            self.log("No agent profiles directory found")
            return
        
        for profile_file in AGENT_PROFILES_DIR.glob('*.json'):
            try:
                with open(profile_file, 'r') as f:
                    profile = json.load(f)
                    agent_id = profile.get('agent_id')
                    if agent_id:
                        self.agent_profiles[agent_id] = profile
            except (FileNotFoundError, json.JSONDecodeError, IOError) as e:
                self.log(f"Error loading profile {profile_file}: {e}")
        
        self.log(f"Loaded {len(self.agent_profiles)} agent profiles")
    
    def generate_warnings_for_agent(self, agent_id: str) -> List[ProactiveWarning]:
        """Generate proactive warnings for a specific agent"""
        warnings = []
        
        # Get agent-specific failures
        agent_failures = [
            f for f in self.pr_failures 
            if f.get('agent_id') == agent_id or f.get('agent_specialization') == agent_id
        ]
        
        if not agent_failures:
            self.log(f"No failures found for agent {agent_id}")
            return warnings
        
        # Analyze failure patterns
        failure_types = Counter(f.get('failure_type') for f in agent_failures)
        
        # Review rejection warning
        review_rejections = failure_types.get('review_rejection', 0)
        if review_rejections >= 3:
            examples = [str(f.get('pr_number')) for f in agent_failures 
                       if f.get('failure_type') == 'review_rejection'][:3]
            warnings.append(ProactiveWarning(
                warning_type='review_issue',
                severity='high' if review_rejections >= 5 else 'medium',
                message=f"You have {review_rejections} past review rejections. Follow code review guidelines carefully.",
                examples=examples,
                mitigation="Review existing code patterns, add comprehensive tests, update documentation"
            ))
        
        # CI/Test failure warning
        ci_failures = failure_types.get('ci_failure', 0) + failure_types.get('test_failure', 0)
        if ci_failures >= 2:
            examples = [str(f.get('pr_number')) for f in agent_failures 
                       if f.get('failure_type') in ['ci_failure', 'test_failure']][:3]
            warnings.append(ProactiveWarning(
                warning_type='ci_failure',
                severity='high' if ci_failures >= 4 else 'medium',
                message=f"You have {ci_failures} past CI/test failures. Run tests locally before submitting.",
                examples=examples,
                mitigation="Run all tests locally, check CI logs for common issues"
            ))
        
        # Merge conflict warning
        merge_conflicts = failure_types.get('merge_conflict', 0)
        if merge_conflicts >= 2:
            examples = [str(f.get('pr_number')) for f in agent_failures 
                       if f.get('failure_type') == 'merge_conflict'][:3]
            warnings.append(ProactiveWarning(
                warning_type='merge_conflict',
                severity='low',
                message=f"You have {merge_conflicts} past merge conflicts. Sync with main branch regularly.",
                examples=examples,
                mitigation="Rebase on main before starting work, keep PRs small"
            ))
        
        # Large PR warning (from failures data)
        large_pr_failures = [f for f in agent_failures if f.get('files_changed', 0) > 20]
        if len(large_pr_failures) >= 2:
            examples = [str(f.get('pr_number')) for f in large_pr_failures][:3]
            warnings.append(ProactiveWarning(
                warning_type='code_quality',
                severity='medium',
                message=f"{len(large_pr_failures)} of your failed PRs had >20 files. Keep changes focused and small.",
                examples=examples,
                mitigation="Break large changes into smaller, focused PRs"
            ))
        
        return warnings
    
    def generate_success_patterns(self, agent_id: Optional[str] = None) -> List[SuccessPattern]:
        """Generate success patterns from code analysis"""
        patterns = []
        
        # Extract high-success patterns from code patterns data
        for pattern in self.code_patterns:
            success_rate = pattern.get('success_rate', 0)
            if success_rate >= 0.7:  # 70% or higher success rate
                pattern_type = pattern.get('pattern_type', 'general')
                description = pattern.get('description', 'Unknown pattern')
                examples = pattern.get('associated_successes', [])[:2]
                
                patterns.append(SuccessPattern(
                    pattern_type=pattern_type,
                    description=description,
                    success_rate=success_rate,
                    recommendation=f"Follow this pattern for better success",
                    examples=examples
                ))
        
        # Add general success patterns if no specific ones found
        if not patterns:
            # Default patterns based on repository conventions
            patterns.extend([
                SuccessPattern(
                    pattern_type='size',
                    description='Small PRs (≤10 files)',
                    success_rate=0.85,
                    recommendation='Keep changes focused and reviewable',
                    examples=[]
                ),
                SuccessPattern(
                    pattern_type='test_coverage',
                    description='PRs including test files',
                    success_rate=0.90,
                    recommendation='Add tests for all new functionality',
                    examples=[]
                ),
                SuccessPattern(
                    pattern_type='commit_format',
                    description='PRs with conventional commit format',
                    success_rate=0.88,
                    recommendation='Use conventional commits (feat:, fix:, docs:, etc.)',
                    examples=[]
                )
            ])
        
        return patterns
    
    def generate_recommendations(self, agent_id: str) -> List[str]:
        """Generate general recommendations for an agent"""
        recommendations = [
            "Follow repository conventions",
            "Write clear, maintainable code",
            "Include tests for new functionality",
        ]
        
        # Add agent-specific recommendations from profile
        if agent_id in self.agent_profiles:
            profile = self.agent_profiles[agent_id]
            if 'best_practices' in profile:
                recommendations.extend(profile['best_practices'][:3])
        
        return recommendations[:5]  # Limit to top 5
    
    def get_agent_stats(self, agent_id: str) -> Dict[str, Any]:
        """Get statistical data for an agent"""
        # Constants for readability
        DAYS_FOR_RECENT = 30
        SECONDS_PER_DAY = 86400
        
        stats = {}
        
        # Count agent PRs
        agent_failures = [
            f for f in self.pr_failures 
            if f.get('agent_id') == agent_id or f.get('agent_specialization') == agent_id
        ]
        
        stats['total_failures'] = len(agent_failures)
        
        # Recent failures (last 30 days)
        recent_failures = []
        if agent_failures:
            # Calculate cutoff timestamp (in seconds)
            cutoff = datetime.now(timezone.utc).timestamp() - (DAYS_FOR_RECENT * SECONDS_PER_DAY)
            recent_failures = [
                f for f in agent_failures 
                if f.get('closed_at') and 
                datetime.fromisoformat(f['closed_at'].replace('Z', '+00:00')).timestamp() > cutoff
            ]
        stats['recent_failures'] = len(recent_failures)
        
        # Load from profile if available
        if agent_id in self.agent_profiles:
            profile = self.agent_profiles[agent_id]
            stats['total_prs'] = profile.get('total_prs', 0)
            stats['success_rate'] = profile.get('success_rate', 0)
        
        return stats
    
    def generate_guidance(self, agent_id: str, issue_title: Optional[str] = None) -> AgentGuidance:
        """
        Generate complete guidance package for an agent.
        
        Args:
            agent_id: Agent identifier (e.g., 'create-botter', 'engineer-master')
            issue_title: Optional issue title for context-specific guidance
            
        Returns:
            AgentGuidance object with warnings, patterns, and recommendations
        """
        self.log(f"Generating guidance for agent: {agent_id}")
        
        # Generate components
        warnings = self.generate_warnings_for_agent(agent_id)
        success_patterns = self.generate_success_patterns(agent_id)
        recommendations = self.generate_recommendations(agent_id)
        stats = self.get_agent_stats(agent_id)
        
        guidance = AgentGuidance(
            agent_id=agent_id,
            agent_specialization=agent_id,
            warnings=warnings,
            success_patterns=success_patterns,
            recommendations=recommendations,
            stats=stats
        )
        
        self.log(f"Generated {len(warnings)} warnings, {len(success_patterns)} patterns")
        return guidance


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='PR Learning Integrator - Bridge learning to code generation'
    )
    parser.add_argument('--agent', type=str, required=True,
                       help='Agent ID to generate guidance for')
    parser.add_argument('--issue-title', type=str,
                       help='Issue title for context')
    parser.add_argument('--format', choices=['json', 'issue-body', 'markdown'],
                       default='issue-body',
                       help='Output format')
    parser.add_argument('--verbose', action='store_true',
                       help='Enable verbose logging')
    
    args = parser.parse_args()
    
    # Initialize integrator
    integrator = PRLearningIntegrator(verbose=args.verbose)
    
    # Generate guidance
    guidance = integrator.generate_guidance(
        agent_id=args.agent,
        issue_title=args.issue_title
    )
    
    # Output in requested format
    if args.format == 'json':
        output = {
            'agent_id': guidance.agent_id,
            'warnings': [w.__dict__ for w in guidance.warnings],
            'success_patterns': [p.__dict__ for p in guidance.success_patterns],
            'recommendations': guidance.recommendations,
            'stats': guidance.stats
        }
        print(json.dumps(output, indent=2))
    
    elif args.format == 'issue-body':
        print(guidance.to_issue_body_section())
    
    elif args.format == 'markdown':
        print(f"# Guidance for @{guidance.agent_id}\n")
        print(guidance.to_issue_body_section())
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
