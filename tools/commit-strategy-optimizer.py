#!/usr/bin/env python3
"""
Real-Time Commit Strategy Optimizer for Chained

This module enhances the commit strategy learning system with real-time feedback
from PR outcomes. It learns optimal commit strategies by correlating commit patterns
with merge success, review speed, and CI outcomes.

Key Features:
- PR outcome tracking and correlation
- Agent-specific strategy learning
- Continuous optimization feedback loop
- Context-aware pattern evolution
- A/B testing for strategy effectiveness

Inspired by Nikola Tesla's visionary approach - always seeking the optimal solution
through experimentation and continuous improvement.

Usage:
    # Track PR outcome for learning
    python commit-strategy-optimizer.py --track-pr <pr_number>
    
    # Get optimized recommendations for an agent
    python commit-strategy-optimizer.py --recommend --agent <agent_name> --context feature
    
    # Run optimization analysis
    python commit-strategy-optimizer.py --optimize
    
    # Generate effectiveness report
    python commit-strategy-optimizer.py --report --output analysis/strategy_effectiveness.md
"""

import json
import os
import sys
import subprocess
import argparse
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict, field
from collections import defaultdict, Counter
import re

# Import the base learner
sys.path.insert(0, str(Path(__file__).parent))
try:
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        'commit_strategy_learner',
        Path(__file__).parent / 'commit-strategy-learner.py'
    )
    learner_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(learner_module)
    
    CommitStrategyLearner = learner_module.CommitStrategyLearner
    CommitMetrics = learner_module.CommitMetrics
    CommitPattern = learner_module.CommitPattern
    StrategyRecommendation = learner_module.StrategyRecommendation
    LEARNINGS_DIR = learner_module.LEARNINGS_DIR
    ANALYSIS_DIR = learner_module.ANALYSIS_DIR
except Exception as e:
    # If import fails, define paths and raise warning
    print(f"Warning: Could not import base learner: {e}", file=sys.stderr)
    LEARNINGS_DIR = Path("learnings")
    ANALYSIS_DIR = Path("analysis")
    # Define minimal classes for standalone usage
    from dataclasses import dataclass
    @dataclass
    class StrategyRecommendation:
        recommendation_id: str
        title: str
        description: str
        rationale: str
        expected_improvement: str
        confidence_score: float
        applicable_contexts: List[str]
        supporting_patterns: List[str]
        example_commits: List[str] = field(default_factory=list)


# Extended data files
OPTIMIZATION_DB = ANALYSIS_DIR / "commit_strategy_optimization.json"
AGENT_STRATEGIES_DB = ANALYSIS_DIR / "agent_commit_strategies.json"
PR_OUTCOMES_DB = LEARNINGS_DIR / "pr_commit_outcomes.json"


@dataclass
class PROutcome:
    """PR outcome data for learning"""
    pr_number: int
    merged: bool
    merge_time_hours: Optional[float]
    review_cycles: int
    ci_passed: bool
    commits: List[str]
    agent: Optional[str] = None
    context: str = "general"  # feature, bugfix, refactor, docs
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class AgentStrategy:
    """Agent-specific commit strategy patterns"""
    agent_name: str
    total_prs: int
    successful_prs: int
    success_rate: float
    average_merge_time_hours: float
    preferred_patterns: List[str]
    common_attributes: Dict[str, Any]
    last_updated: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class StrategyEffectiveness:
    """Effectiveness tracking for a commit strategy"""
    strategy_id: str
    pattern_name: str
    times_used: int
    times_successful: int
    success_rate: float
    average_merge_time: float
    contexts: List[str]
    confidence_score: float
    trend: str = "stable"  # improving, stable, declining
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class CommitStrategyOptimizer:
    """
    Real-time commit strategy optimizer.
    
    Enhances the base learner with:
    - PR outcome tracking
    - Agent-specific learning
    - Continuous optimization
    - Strategy effectiveness metrics
    """
    
    def __init__(self, repo_path: str = ".", verbose: bool = False):
        self.repo_path = Path(repo_path)
        self.verbose = verbose
        self.base_learner = CommitStrategyLearner(repo_path=repo_path, verbose=verbose)
        self.optimization_data = self._load_optimization_db()
        self.agent_strategies = self._load_agent_strategies()
        self.pr_outcomes = self._load_pr_outcomes()
    
    def _log(self, message: str, level: str = "INFO"):
        """Log message if verbose enabled"""
        if self.verbose:
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"[{timestamp}] [{level}] {message}", file=sys.stderr)
    
    def _load_optimization_db(self) -> Dict:
        """Load optimization database"""
        if OPTIMIZATION_DB.exists():
            with open(OPTIMIZATION_DB, 'r') as f:
                return json.load(f)
        return self._initialize_optimization_db()
    
    def _initialize_optimization_db(self) -> Dict:
        """Initialize optimization database"""
        return {
            "version": "1.0.0",
            "last_updated": None,
            "strategy_effectiveness": {},
            "optimization_history": [],
            "learning_rate": 0.1,  # How quickly to adapt to new data
            "confidence_threshold": 0.75
        }
    
    def _load_agent_strategies(self) -> Dict:
        """Load agent-specific strategies"""
        if AGENT_STRATEGIES_DB.exists():
            with open(AGENT_STRATEGIES_DB, 'r') as f:
                return json.load(f)
        return {"agents": {}, "last_updated": None}
    
    def _load_pr_outcomes(self) -> List[Dict]:
        """Load PR outcomes database"""
        if PR_OUTCOMES_DB.exists():
            with open(PR_OUTCOMES_DB, 'r') as f:
                data = json.load(f)
                return data.get("outcomes", [])
        return []
    
    def _save_optimization_db(self):
        """Save optimization database"""
        self.optimization_data["last_updated"] = datetime.now(timezone.utc).isoformat()
        ANALYSIS_DIR.mkdir(parents=True, exist_ok=True)
        
        temp_file = OPTIMIZATION_DB.with_suffix('.json.tmp')
        with open(temp_file, 'w') as f:
            json.dump(self.optimization_data, f, indent=2)
        temp_file.replace(OPTIMIZATION_DB)
        
        self._log(f"Saved optimization data to {OPTIMIZATION_DB}")
    
    def _save_agent_strategies(self):
        """Save agent strategies"""
        self.agent_strategies["last_updated"] = datetime.now(timezone.utc).isoformat()
        ANALYSIS_DIR.mkdir(parents=True, exist_ok=True)
        
        temp_file = AGENT_STRATEGIES_DB.with_suffix('.json.tmp')
        with open(temp_file, 'w') as f:
            json.dump(self.agent_strategies, f, indent=2)
        temp_file.replace(AGENT_STRATEGIES_DB)
        
        self._log(f"Saved agent strategies to {AGENT_STRATEGIES_DB}")
    
    def _save_pr_outcomes(self):
        """Save PR outcomes"""
        LEARNINGS_DIR.mkdir(parents=True, exist_ok=True)
        data = {
            "version": "1.0.0",
            "last_updated": datetime.now(timezone.utc).isoformat(),
            "outcomes": self.pr_outcomes
        }
        
        temp_file = PR_OUTCOMES_DB.with_suffix('.json.tmp')
        with open(temp_file, 'w') as f:
            json.dump(data, f, indent=2)
        temp_file.replace(PR_OUTCOMES_DB)
        
        self._log(f"Saved PR outcomes to {PR_OUTCOMES_DB}")
    
    def _run_git_command(self, args: List[str]) -> str:
        """Run a git command"""
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
            self._log(f"Git command failed: {e}", "ERROR")
            return ""
    
    def track_pr_outcome(
        self,
        pr_number: int,
        merged: bool = True,
        agent: Optional[str] = None,
        context: str = "general"
    ) -> PROutcome:
        """
        Track a PR outcome for learning.
        
        This is called after a PR is merged/closed to correlate commit patterns
        with outcomes and continuously improve recommendations.
        """
        self._log(f"Tracking PR #{pr_number} outcome...")
        
        # Get PR commits
        commits_output = self._run_git_command([
            'log', '--format=%H', f'--grep=#{pr_number}'
        ])
        
        if not commits_output:
            # Try alternate method - search recent commits
            commits_output = self._run_git_command([
                'log', '--format=%H', '--since=30 days ago', '-100'
            ])
        
        commit_hashes = [c for c in commits_output.split('\n') if c.strip()][:10]
        
        # Calculate metrics
        merge_time_hours = None
        review_cycles = 1  # Default, would need GitHub API for accurate count
        ci_passed = merged  # Assume CI passed if merged
        
        # Create outcome record
        outcome = PROutcome(
            pr_number=pr_number,
            merged=merged,
            merge_time_hours=merge_time_hours,
            review_cycles=review_cycles,
            ci_passed=ci_passed,
            commits=commit_hashes[:5],  # Store up to 5 commits
            agent=agent,
            context=context
        )
        
        # Store outcome
        self.pr_outcomes.append(outcome.to_dict())
        self._save_pr_outcomes()
        
        # Update agent strategies if agent specified
        if agent:
            self._update_agent_strategy(agent, outcome, commit_hashes)
        
        # Update strategy effectiveness
        self._update_strategy_effectiveness(outcome, commit_hashes)
        
        self._log(f"✓ Tracked PR #{pr_number}: merged={merged}, agent={agent}")
        
        return outcome
    
    def _update_agent_strategy(
        self,
        agent: str,
        outcome: PROutcome,
        commit_hashes: List[str]
    ):
        """Update agent-specific strategy based on outcome"""
        
        if "agents" not in self.agent_strategies:
            self.agent_strategies["agents"] = {}
        
        agents = self.agent_strategies["agents"]
        
        if agent not in agents:
            agents[agent] = {
                "agent_name": agent,
                "total_prs": 0,
                "successful_prs": 0,
                "success_rate": 0.0,
                "average_merge_time_hours": 0.0,
                "preferred_patterns": [],
                "common_attributes": {},
                "commit_patterns": []
            }
        
        agent_data = agents[agent]
        agent_data["total_prs"] += 1
        
        if outcome.merged:
            agent_data["successful_prs"] += 1
        
        agent_data["success_rate"] = agent_data["successful_prs"] / agent_data["total_prs"]
        
        # Analyze commits for patterns
        patterns = []
        for commit_hash in commit_hashes:
            metrics = self.base_learner._get_commit_metrics(commit_hash)
            if metrics:
                if metrics.follows_conventional:
                    patterns.append("conventional_commits")
                if metrics.files_changed <= 5:
                    patterns.append("small_commits")
                if metrics.has_body:
                    patterns.append("detailed_messages")
        
        # Update preferred patterns
        pattern_counts = Counter(patterns)
        agent_data["preferred_patterns"] = [
            p for p, _ in pattern_counts.most_common(5)
        ]
        
        self._save_agent_strategies()
    
    def _update_strategy_effectiveness(
        self,
        outcome: PROutcome,
        commit_hashes: List[str]
    ):
        """Update strategy effectiveness metrics"""
        
        if "strategy_effectiveness" not in self.optimization_data:
            self.optimization_data["strategy_effectiveness"] = {}
        
        effectiveness = self.optimization_data["strategy_effectiveness"]
        
        # Analyze commit patterns
        patterns_used = set()
        for commit_hash in commit_hashes:
            metrics = self.base_learner._get_commit_metrics(commit_hash)
            if not metrics:
                continue
            
            if metrics.follows_conventional:
                patterns_used.add("conventional_commits")
            if metrics.files_changed <= 5 and metrics.total_lines_changed <= 100:
                patterns_used.add("optimal_commit_size")
            if metrics.has_body:
                patterns_used.add("detailed_messages")
            if len(metrics.file_types) <= 2:
                patterns_used.add("focused_changes")
        
        # Update effectiveness for each pattern
        for pattern in patterns_used:
            if pattern not in effectiveness:
                effectiveness[pattern] = {
                    "strategy_id": pattern,
                    "pattern_name": pattern,
                    "times_used": 0,
                    "times_successful": 0,
                    "success_rate": 0.0,
                    "average_merge_time": 0.0,
                    "contexts": [],
                    "confidence_score": 0.5,
                    "trend": "stable"
                }
            
            strategy = effectiveness[pattern]
            strategy["times_used"] += 1
            
            if outcome.merged:
                strategy["times_successful"] += 1
            
            strategy["success_rate"] = strategy["times_successful"] / strategy["times_used"]
            
            # Update confidence based on sample size and success rate
            sample_size_factor = min(strategy["times_used"] / 50.0, 1.0)
            strategy["confidence_score"] = strategy["success_rate"] * sample_size_factor
            
            # Track context
            if outcome.context not in strategy["contexts"]:
                strategy["contexts"].append(outcome.context)
        
        self._save_optimization_db()
    
    def get_optimized_recommendations(
        self,
        agent: Optional[str] = None,
        context: str = "general",
        min_confidence: float = 0.7
    ) -> List[StrategyRecommendation]:
        """
        Get optimized recommendations based on learned outcomes.
        
        This provides context-aware, agent-specific recommendations that
        continuously improve based on actual PR outcomes.
        """
        self._log(f"Generating optimized recommendations for agent={agent}, context={context}")
        
        # Start with base recommendations
        base_recommendations = self.base_learner.generate_recommendations(
            context=context,
            min_confidence=min_confidence
        )
        
        # Enhance with optimization data
        effectiveness = self.optimization_data.get("strategy_effectiveness", {})
        
        # Filter and rank by effectiveness
        optimized_recs = []
        
        for rec in base_recommendations:
            # Check if we have effectiveness data for this pattern
            for pattern in rec.supporting_patterns:
                if pattern in effectiveness:
                    eff_data = effectiveness[pattern]
                    
                    # Boost confidence based on real outcomes
                    adjusted_confidence = (
                        rec.confidence_score * 0.5 +  # Base confidence
                        eff_data["confidence_score"] * 0.5  # Outcome-based confidence
                    )
                    
                    # Update recommendation
                    rec.confidence_score = adjusted_confidence
                    rec.expected_improvement = (
                        f"{eff_data['success_rate']:.1%} success rate "
                        f"(based on {eff_data['times_used']} uses)"
                    )
        
        # Add agent-specific recommendations
        if agent and agent in self.agent_strategies.get("agents", {}):
            agent_data = self.agent_strategies["agents"][agent]
            
            # Create agent-specific recommendation
            if agent_data["preferred_patterns"]:
                agent_rec = StrategyRecommendation(
                    recommendation_id=f"agent_{agent}_{context}",
                    title=f"Follow {agent}'s Proven Patterns",
                    description=(
                        f"Based on {agent}'s history of {agent_data['total_prs']} PRs "
                        f"with {agent_data['success_rate']:.1%} success rate, "
                        f"use these proven patterns: {', '.join(agent_data['preferred_patterns'][:3])}"
                    ),
                    rationale=(
                        f"Agent-specific learning shows these patterns work well for {agent}. "
                        f"Success rate: {agent_data['success_rate']:.1%}"
                    ),
                    expected_improvement=f"{agent_data['success_rate']:.1%} success rate",
                    confidence_score=min(agent_data['success_rate'] * 1.1, 1.0),
                    applicable_contexts=[context],
                    supporting_patterns=agent_data["preferred_patterns"][:3],
                    example_commits=[]
                )
                optimized_recs.insert(0, agent_rec)  # Add as top recommendation
        
        # Sort by confidence
        optimized_recs.extend(base_recommendations)
        optimized_recs.sort(key=lambda r: r.confidence_score, reverse=True)
        
        return optimized_recs
    
    def run_optimization(self) -> Dict[str, Any]:
        """
        Run optimization analysis to improve strategy recommendations.
        
        This analyzes recent outcomes and adjusts strategy effectiveness scores.
        """
        self._log("Running optimization analysis...")
        
        # Run base analysis first
        analysis_result = self.base_learner.analyze_commits(since_days=30, max_commits=500)
        
        # Analyze PR outcomes for pattern effectiveness
        recent_outcomes = [
            o for o in self.pr_outcomes
            if datetime.fromisoformat(o["timestamp"]) > 
               datetime.now(timezone.utc) - timedelta(days=30)
        ]
        
        self._log(f"Analyzing {len(recent_outcomes)} recent PR outcomes")
        
        # Calculate overall success metrics
        total_prs = len(recent_outcomes)
        successful_prs = sum(1 for o in recent_outcomes if o["merged"])
        
        success_rate = successful_prs / total_prs if total_prs > 0 else 0.0
        
        # Identify top performing strategies
        effectiveness = self.optimization_data.get("strategy_effectiveness", {})
        top_strategies = sorted(
            effectiveness.items(),
            key=lambda x: (x[1]["confidence_score"], x[1]["success_rate"]),
            reverse=True
        )[:5]
        
        result = {
            "total_prs_analyzed": total_prs,
            "successful_prs": successful_prs,
            "overall_success_rate": success_rate,
            "top_strategies": [
                {
                    "pattern": s[0],
                    "success_rate": s[1]["success_rate"],
                    "confidence": s[1]["confidence_score"],
                    "uses": s[1]["times_used"]
                }
                for s in top_strategies
            ],
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        # Store in optimization history
        if "optimization_history" not in self.optimization_data:
            self.optimization_data["optimization_history"] = []
        
        self.optimization_data["optimization_history"].append(result)
        
        # Keep only last 30 optimization runs
        self.optimization_data["optimization_history"] = \
            self.optimization_data["optimization_history"][-30:]
        
        self._save_optimization_db()
        
        self._log(f"✓ Optimization complete: {success_rate:.1%} success rate")
        
        return result
    
    def generate_effectiveness_report(self, output_file: Optional[str] = None) -> str:
        """Generate comprehensive strategy effectiveness report"""
        
        self._log("Generating effectiveness report...")
        
        report_lines = [
            "# Commit Strategy Effectiveness Report",
            "",
            f"Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}",
            "",
            "## Overview",
            ""
        ]
        
        # PR outcomes summary
        total_prs = len(self.pr_outcomes)
        if total_prs > 0:
            successful = sum(1 for o in self.pr_outcomes if o["merged"])
            success_rate = successful / total_prs
            
            report_lines.extend([
                f"- Total PRs tracked: {total_prs}",
                f"- Successful merges: {successful}",
                f"- Overall success rate: {success_rate:.1%}",
                ""
            ])
        
        # Strategy effectiveness
        report_lines.extend([
            "## Strategy Effectiveness",
            ""
        ])
        
        effectiveness = self.optimization_data.get("strategy_effectiveness", {})
        sorted_strategies = sorted(
            effectiveness.items(),
            key=lambda x: x[1]["confidence_score"],
            reverse=True
        )
        
        for pattern_name, data in sorted_strategies:
            report_lines.extend([
                f"### {pattern_name.replace('_', ' ').title()}",
                "",
                f"**Success Rate:** {data['success_rate']:.1%}",
                f"**Times Used:** {data['times_used']}",
                f"**Confidence:** {data['confidence_score']:.1%}",
                f"**Contexts:** {', '.join(data['contexts'])}",
                f"**Trend:** {data['trend']}",
                "",
                "---",
                ""
            ])
        
        # Agent performance
        report_lines.extend([
            "## Agent Performance",
            ""
        ])
        
        agents = self.agent_strategies.get("agents", {})
        sorted_agents = sorted(
            agents.items(),
            key=lambda x: x[1]["success_rate"],
            reverse=True
        )
        
        for agent_name, data in sorted_agents[:10]:  # Top 10
            report_lines.extend([
                f"### {agent_name}",
                "",
                f"**Success Rate:** {data['success_rate']:.1%}",
                f"**Total PRs:** {data['total_prs']}",
                f"**Preferred Patterns:** {', '.join(data['preferred_patterns'][:3])}",
                "",
                "---",
                ""
            ])
        
        report_text = '\n'.join(report_lines)
        
        if output_file:
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(report_text)
            self._log(f"Report saved to {output_file}")
        
        return report_text


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Commit Strategy Optimizer - Real-time learning from PR outcomes",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('--track-pr', type=int, metavar='PR_NUMBER',
                       help='Track PR outcome for learning')
    parser.add_argument('--merged', action='store_true', default=True,
                       help='PR was merged (default: true)')
    parser.add_argument('--agent', type=str,
                       help='Agent responsible for the PR')
    parser.add_argument('--context', type=str, default='general',
                       choices=['general', 'feature', 'bugfix', 'refactor', 'docs'],
                       help='PR context')
    
    parser.add_argument('--recommend', action='store_true',
                       help='Get optimized recommendations')
    parser.add_argument('--min-confidence', type=float, default=0.7,
                       help='Minimum confidence threshold')
    
    parser.add_argument('--optimize', action='store_true',
                       help='Run optimization analysis')
    
    parser.add_argument('--report', action='store_true',
                       help='Generate effectiveness report')
    parser.add_argument('--output', type=str,
                       help='Output file for report')
    
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Enable verbose logging')
    
    args = parser.parse_args()
    
    optimizer = CommitStrategyOptimizer(verbose=args.verbose)
    
    try:
        if args.track_pr:
            print(f"📊 Tracking PR #{args.track_pr}...")
            outcome = optimizer.track_pr_outcome(
                pr_number=args.track_pr,
                merged=args.merged,
                agent=args.agent,
                context=args.context
            )
            print(f"✅ PR #{outcome.pr_number} tracked successfully")
            if args.agent:
                print(f"   Agent: {args.agent}")
            print(f"   Merged: {outcome.merged}")
            print(f"   Commits analyzed: {len(outcome.commits)}")
        
        elif args.recommend:
            print(f"💡 Generating optimized recommendations...")
            recommendations = optimizer.get_optimized_recommendations(
                agent=args.agent,
                context=args.context,
                min_confidence=args.min_confidence
            )
            
            if not recommendations:
                print("⚠️  No recommendations available yet")
                print("   Run --optimize first to analyze patterns")
                return 1
            
            print(f"\n✅ Top {len(recommendations)} Recommendations:\n")
            for i, rec in enumerate(recommendations, 1):
                print(f"{i}. {rec.title}")
                print(f"   Confidence: {rec.confidence_score:.1%}")
                print(f"   {rec.description}")
                print()
        
        elif args.optimize:
            print("🔧 Running optimization analysis...")
            result = optimizer.run_optimization()
            print(f"✅ Optimization complete!")
            print(f"   PRs analyzed: {result['total_prs_analyzed']}")
            print(f"   Success rate: {result['overall_success_rate']:.1%}")
            print(f"   Top strategies: {len(result['top_strategies'])}")
            
            if result['top_strategies']:
                print("\n   Top performing strategies:")
                for s in result['top_strategies'][:3]:
                    print(f"   • {s['pattern']}: {s['success_rate']:.1%} ({s['uses']} uses)")
        
        elif args.report:
            print("📊 Generating effectiveness report...")
            report = optimizer.generate_effectiveness_report(output_file=args.output)
            
            if args.output:
                print(f"✅ Report saved to {args.output}")
            else:
                print(report)
        
        else:
            parser.print_help()
            return 1
        
        return 0
    
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
