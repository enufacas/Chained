#!/usr/bin/env python3
"""
Creativity & Innovation Metrics Analyzer for AI Agents

A production-grade system for measuring and tracking creative contributions in the
Chained agent ecosystem. Moves beyond random creativity traits to actual behavioral
measurement based on GitHub activity.

Architecture:
- Modular design for extensibility
- Pattern-based novelty detection
- Multi-dimensional creativity scoring
- Historical trend analysis
- Scalable for growing agent populations

Features:
- Novelty Detection: Identifies unique solution patterns
- Diversity Measurement: Tracks variety of approaches
- Impact Assessment: Measures breadth of improvements
- Learning Tracking: Monitors progressive skill development

Usage:
    python creativity-metrics-analyzer.py <agent_id> [--since DAYS]
    python creativity-metrics-analyzer.py --analyze-all
"""

import json
import os
import sys
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass, asdict, field
from collections import defaultdict, Counter
import hashlib

# Constants
METRICS_DIR = Path(".github/agent-system/metrics")
REGISTRY_FILE = Path(".github/agent-system/registry.json")
CREATIVITY_CACHE_DIR = METRICS_DIR / "creativity"

# Creativity scoring weights (can be tuned)
NOVELTY_WEIGHT = 0.35
DIVERSITY_WEIGHT = 0.25
IMPACT_WEIGHT = 0.25
LEARNING_WEIGHT = 0.15


@dataclass
class CreativityIndicators:
    """Specific indicators of creative behavior"""
    novel_patterns: List[str] = field(default_factory=list)
    unique_approaches: int = 0
    first_time_solutions: int = 0
    cross_domain_contributions: int = 0
    breakthrough_moments: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class CreativityScore:
    """Multi-dimensional creativity assessment"""
    novelty: float = 0.0  # How unique is the solution?
    diversity: float = 0.0  # Variety of approaches used
    impact: float = 0.0  # Breadth of system improvements
    learning: float = 0.0  # Progressive skill development
    overall: float = 0.0  # Weighted aggregate score
    
    def to_dict(self) -> Dict[str, float]:
        return asdict(self)


@dataclass
class CreativityMetrics:
    """Complete creativity assessment for an agent"""
    agent_id: str
    timestamp: str
    score: CreativityScore
    indicators: CreativityIndicators
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'agent_id': self.agent_id,
            'timestamp': self.timestamp,
            'score': self.score.to_dict(),
            'indicators': self.indicators.to_dict(),
            'metadata': self.metadata
        }


class CreativityAnalyzer:
    """
    Core creativity analysis engine.
    
    Analyzes GitHub activity to measure creative contributions:
    - Code pattern novelty detection
    - Solution diversity tracking
    - Impact breadth assessment
    - Learning progression monitoring
    """
    
    def __init__(self, repo: Optional[str] = None, github_token: Optional[str] = None):
        """
        Initialize creativity analyzer.
        
        Args:
            repo: Repository in format 'owner/repo'
            github_token: GitHub API token for accessing PR/issue data
        """
        self.repo = repo or os.environ.get('GITHUB_REPOSITORY', 'enufacas/Chained')
        self.github_token = github_token or os.environ.get('GITHUB_TOKEN', os.environ.get('GH_TOKEN'))
        
        # Ensure creativity cache directory exists
        CREATIVITY_CACHE_DIR.mkdir(parents=True, exist_ok=True)
        
        # Load pattern database for novelty detection
        self.pattern_db = self._load_pattern_database()
        
    def _load_pattern_database(self) -> Dict[str, Set[str]]:
        """
        Load historical patterns database for novelty comparison.
        
        Returns:
            Dict mapping pattern types to sets of known patterns
        """
        db_file = CREATIVITY_CACHE_DIR / "pattern_database.json"
        
        if db_file.exists():
            try:
                with open(db_file, 'r') as f:
                    data = json.load(f)
                    # Convert lists back to sets
                    return {k: set(v) for k, v in data.items()}
            except Exception as e:
                print(f"⚠️  Warning: Could not load pattern database: {e}", file=sys.stderr)
        
        # Initialize empty database
        return {
            'code_patterns': set(),
            'solution_approaches': set(),
            'architectural_patterns': set(),
            'problem_solving_strategies': set()
        }
    
    def _save_pattern_database(self) -> None:
        """Save pattern database to persistent storage"""
        db_file = CREATIVITY_CACHE_DIR / "pattern_database.json"
        
        try:
            # Convert sets to lists for JSON serialization
            data = {k: list(v) for k, v in self.pattern_db.items()}
            with open(db_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"⚠️  Warning: Could not save pattern database: {e}", file=sys.stderr)
    
    def _extract_code_patterns(self, code_diff: str) -> List[str]:
        """
        Extract code patterns from a diff.
        
        Patterns include:
        - Design patterns (factory, observer, decorator, etc.)
        - Architectural approaches (MVC, microservices, event-driven)
        - Algorithm choices (sorting, searching, optimization)
        - Data structures (trees, graphs, caches)
        
        Args:
            code_diff: Git diff content
            
        Returns:
            List of detected patterns
        """
        patterns = []
        
        # Pattern detection rules (simplified but functional)
        pattern_rules = {
            'factory_pattern': r'(class|def)\s+\w*[Ff]actory',
            'decorator_pattern': r'@\w+|class\s+\w*[Dd]ecorator',
            'observer_pattern': r'(class|def)\s+\w*[Oo]bserver|subscribe|notify',
            'singleton_pattern': r'_instance\s*=|__new__|metaclass',
            'strategy_pattern': r'class\s+\w*[Ss]trategy',
            'async_pattern': r'async\s+(def|with)|await\s+',
            'cache_pattern': r'@(lru_cache|cache)|Cache|Memoiz',
            'retry_pattern': r'@retry|RetryConfig|retry_with',
            'dataclass_pattern': r'@dataclass',
            'context_manager': r'__enter__|__exit__|with\s+\w+\(',
            'generator_pattern': r'yield\s+',
            'comprehension': r'\[.+for\s+.+in\s+.+\]|\{.+for\s+.+in\s+.+\}',
            'type_hints': r':\s*[A-Z]\w+(\[|,|\s|$)|->',
            'error_handling': r'try:|except\s+\w+:|finally:',
            'api_integration': r'requests\.|urllib\.|httpx\.|aiohttp\.',
            'testing_framework': r'def\s+test_|assert\s+|@pytest|@unittest',
            'logging_framework': r'logger\.|logging\.|print\(.*file=sys\.stderr',
            'config_management': r'ConfigParser|yaml\.load|json\.load.*config',
            'cli_framework': r'argparse|click\.|typer\.',
            'concurrency': r'Thread|Process|ThreadPool|ProcessPool|multiprocessing',
            'validation': r'validate|schema|pydantic|marshmallow'
        }
        
        for pattern_name, pattern_regex in pattern_rules.items():
            if re.search(pattern_regex, code_diff, re.IGNORECASE | re.MULTILINE):
                patterns.append(pattern_name)
        
        return patterns
    
    def _extract_solution_approaches(self, pr_data: Dict[str, Any]) -> List[str]:
        """
        Extract solution approaches from PR description and files changed.
        
        Approaches include:
        - Refactoring vs new feature
        - Test-driven development
        - Performance optimization
        - Security hardening
        - API design
        
        Args:
            pr_data: Pull request data from GitHub
            
        Returns:
            List of detected approaches
        """
        approaches = []
        
        title = pr_data.get('title', '').lower()
        body = pr_data.get('body', '').lower() if pr_data.get('body') else ''
        files_changed = pr_data.get('changed_files', 0)
        additions = pr_data.get('additions', 0)
        deletions = pr_data.get('deletions', 0)
        
        # Analyze PR metadata for approach indicators
        if 'refactor' in title or 'refactor' in body:
            approaches.append('refactoring')
        
        if 'test' in title or 'coverage' in body:
            approaches.append('test_driven')
        
        if 'performance' in title or 'optim' in title or 'speed' in body:
            approaches.append('performance_optimization')
        
        if 'security' in title or 'vulnerab' in body or 'cve' in body:
            approaches.append('security_hardening')
        
        if 'api' in title or 'endpoint' in body or 'interface' in title:
            approaches.append('api_design')
        
        if 'feature' in title or 'add' in title:
            approaches.append('feature_development')
        
        if 'fix' in title or 'bug' in title:
            approaches.append('bug_fixing')
        
        if 'doc' in title or 'readme' in title:
            approaches.append('documentation')
        
        if files_changed > 10:
            approaches.append('large_scale_change')
        
        if deletions > additions * 2:
            approaches.append('code_simplification')
        
        return approaches
    
    def _calculate_pattern_hash(self, pattern: str) -> str:
        """Calculate a hash for pattern comparison"""
        return hashlib.md5(pattern.encode()).hexdigest()[:16]
    
    def analyze_novelty(
        self,
        agent_id: str,
        recent_contributions: List[Dict[str, Any]],
        all_contributions_context: List[Dict[str, Any]]
    ) -> Tuple[float, List[str]]:
        """
        Analyze novelty of agent's contributions.
        
        Novelty is measured by:
        - New patterns not seen before in the ecosystem
        - Unique solutions compared to historical data
        - First-time implementation approaches
        
        Args:
            agent_id: Agent identifier
            recent_contributions: Recent PRs/contributions from agent
            all_contributions_context: All contributions in the ecosystem for comparison
            
        Returns:
            Tuple of (novelty_score, list of novel patterns detected)
        """
        novel_patterns = []
        total_patterns = 0
        
        for contrib in recent_contributions:
            # Extract patterns from this contribution
            code_diff = contrib.get('diff', '')
            patterns = self._extract_code_patterns(code_diff)
            
            for pattern in patterns:
                total_patterns += 1
                pattern_hash = self._calculate_pattern_hash(pattern)
                
                # Check if this pattern is novel (not in database)
                if pattern_hash not in self.pattern_db['code_patterns']:
                    novel_patterns.append(pattern)
                    # Add to database for future comparison
                    self.pattern_db['code_patterns'].add(pattern_hash)
            
            # Extract solution approaches
            approaches = self._extract_solution_approaches(contrib)
            for approach in approaches:
                total_patterns += 1
                approach_hash = self._calculate_pattern_hash(approach)
                
                if approach_hash not in self.pattern_db['solution_approaches']:
                    novel_patterns.append(f"approach:{approach}")
                    self.pattern_db['solution_approaches'].add(approach_hash)
        
        # Calculate novelty score (0.0 to 1.0)
        if total_patterns == 0:
            novelty_score = 0.0
        else:
            novelty_score = min(1.0, len(novel_patterns) / max(1, total_patterns) * 2.0)
        
        # Save updated pattern database
        self._save_pattern_database()
        
        return novelty_score, novel_patterns
    
    def analyze_diversity(
        self,
        agent_id: str,
        contributions: List[Dict[str, Any]]
    ) -> float:
        """
        Analyze diversity of agent's approaches.
        
        Diversity is measured by:
        - Variety of patterns used
        - Different types of contributions
        - Mix of technologies and approaches
        
        Args:
            agent_id: Agent identifier
            contributions: List of agent contributions
            
        Returns:
            Diversity score (0.0 to 1.0)
        """
        if not contributions:
            return 0.0
        
        unique_patterns = set()
        unique_approaches = set()
        file_types = set()
        
        for contrib in contributions:
            # Collect unique patterns
            code_diff = contrib.get('diff', '')
            patterns = self._extract_code_patterns(code_diff)
            unique_patterns.update(patterns)
            
            # Collect unique approaches
            approaches = self._extract_solution_approaches(contrib)
            unique_approaches.update(approaches)
            
            # Collect file types touched
            files = contrib.get('files', [])
            for file_path in files:
                ext = Path(file_path).suffix
                if ext:
                    file_types.add(ext)
        
        # Calculate diversity based on variety
        # More variety = higher score
        pattern_diversity = min(1.0, len(unique_patterns) / 10.0)  # 10+ patterns = max score
        approach_diversity = min(1.0, len(unique_approaches) / 6.0)  # 6+ approaches = max score
        filetype_diversity = min(1.0, len(file_types) / 5.0)  # 5+ file types = max score
        
        # Weighted average
        diversity_score = (
            pattern_diversity * 0.4 +
            approach_diversity * 0.4 +
            filetype_diversity * 0.2
        )
        
        return diversity_score
    
    def analyze_impact(
        self,
        agent_id: str,
        contributions: List[Dict[str, Any]]
    ) -> float:
        """
        Analyze impact breadth of agent's contributions.
        
        Impact is measured by:
        - Number of files positively affected
        - Breadth across different system components
        - Downstream benefits to other agents
        
        Args:
            agent_id: Agent identifier
            contributions: List of agent contributions
            
        Returns:
            Impact score (0.0 to 1.0)
        """
        if not contributions:
            return 0.0
        
        total_files_affected = 0
        unique_directories = set()
        large_scale_changes = 0
        
        for contrib in contributions:
            files = contrib.get('files', [])
            total_files_affected += len(files)
            
            # Track unique directories (system components)
            for file_path in files:
                directory = str(Path(file_path).parent)
                unique_directories.add(directory)
            
            # Track large-scale changes
            if contrib.get('changed_files', 0) > 5:
                large_scale_changes += 1
        
        # Calculate impact based on breadth
        files_impact = min(1.0, total_files_affected / 20.0)  # 20+ files = max score
        component_impact = min(1.0, len(unique_directories) / 8.0)  # 8+ components = max score
        scale_bonus = min(0.3, large_scale_changes * 0.1)  # Bonus for large changes
        
        impact_score = (files_impact * 0.5 + component_impact * 0.5 + scale_bonus)
        return min(1.0, impact_score)
    
    def analyze_learning(
        self,
        agent_id: str,
        contributions: List[Dict[str, Any]],
        historical_metrics: List[Dict[str, Any]]
    ) -> float:
        """
        Analyze learning progression of agent.
        
        Learning is measured by:
        - Progressive improvement in contributions
        - Building on previous work
        - Applying past lessons
        
        Args:
            agent_id: Agent identifier
            contributions: Recent contributions
            historical_metrics: Past creativity metrics for trend analysis
            
        Returns:
            Learning score (0.0 to 1.0)
        """
        if len(historical_metrics) < 2:
            # New agent - neutral score
            return 0.5
        
        # Sort by timestamp
        sorted_metrics = sorted(
            historical_metrics,
            key=lambda x: x.get('timestamp', '')
        )
        
        # Calculate trend in creativity scores
        scores = [m.get('score', {}).get('overall', 0) for m in sorted_metrics]
        
        if len(scores) < 2:
            return 0.5
        
        # Check for improvement trend
        improvements = 0
        for i in range(1, len(scores)):
            if scores[i] > scores[i-1]:
                improvements += 1
        
        improvement_rate = improvements / (len(scores) - 1)
        
        # Check for pattern reuse (learning from past)
        recent_patterns = set()
        past_patterns = set()
        
        for contrib in contributions[-3:]:  # Last 3 contributions
            patterns = self._extract_code_patterns(contrib.get('diff', ''))
            recent_patterns.update(patterns)
        
        for contrib in contributions[:-3] if len(contributions) > 3 else []:
            patterns = self._extract_code_patterns(contrib.get('diff', ''))
            past_patterns.update(patterns)
        
        # Learning involves both building on past AND adding new
        if past_patterns:
            reuse_rate = len(recent_patterns & past_patterns) / len(past_patterns)
            innovation_rate = len(recent_patterns - past_patterns) / max(1, len(recent_patterns))
            
            # Balance between reuse and innovation
            learning_score = (
                improvement_rate * 0.4 +
                reuse_rate * 0.3 +
                innovation_rate * 0.3
            )
        else:
            learning_score = improvement_rate
        
        return min(1.0, learning_score)
    
    def analyze_creativity(
        self,
        agent_id: str,
        contributions: List[Dict[str, Any]],
        ecosystem_context: Optional[Dict[str, Any]] = None
    ) -> CreativityMetrics:
        """
        Perform complete creativity analysis for an agent.
        
        Args:
            agent_id: Agent identifier
            contributions: List of agent's contributions (PRs, issues, etc.)
            ecosystem_context: Optional context about the broader ecosystem
            
        Returns:
            Complete CreativityMetrics object
        """
        print(f"🎨 Analyzing creativity for {agent_id}...", file=sys.stderr)
        
        # Get historical metrics for learning analysis
        historical_metrics = self._load_historical_creativity_metrics(agent_id)
        
        # Get ecosystem context for novelty comparison
        all_contributions = ecosystem_context.get('all_contributions', []) if ecosystem_context else []
        
        # Perform multi-dimensional analysis
        novelty_score, novel_patterns = self.analyze_novelty(
            agent_id,
            contributions,
            all_contributions
        )
        
        diversity_score = self.analyze_diversity(agent_id, contributions)
        impact_score = self.analyze_impact(agent_id, contributions)
        learning_score = self.analyze_learning(agent_id, contributions, historical_metrics)
        
        # Calculate overall creativity score
        overall_score = (
            novelty_score * NOVELTY_WEIGHT +
            diversity_score * DIVERSITY_WEIGHT +
            impact_score * IMPACT_WEIGHT +
            learning_score * LEARNING_WEIGHT
        )
        
        # Create score object
        score = CreativityScore(
            novelty=novelty_score,
            diversity=diversity_score,
            impact=impact_score,
            learning=learning_score,
            overall=overall_score
        )
        
        # Identify breakthrough moments
        breakthrough_moments = []
        if novelty_score > 0.7:
            breakthrough_moments.append(f"High novelty: {len(novel_patterns)} new patterns")
        if diversity_score > 0.8:
            breakthrough_moments.append("Exceptional diversity in approaches")
        if impact_score > 0.75:
            breakthrough_moments.append("Broad system-wide impact")
        
        # Create indicators object
        indicators = CreativityIndicators(
            novel_patterns=novel_patterns,
            unique_approaches=len(set(
                approach
                for contrib in contributions
                for approach in self._extract_solution_approaches(contrib)
            )),
            first_time_solutions=len([p for p in novel_patterns if not p.startswith('approach:')]),
            cross_domain_contributions=len(set(
                str(Path(f).parent)
                for contrib in contributions
                for f in contrib.get('files', [])
            )),
            breakthrough_moments=breakthrough_moments
        )
        
        # Create complete metrics
        metrics = CreativityMetrics(
            agent_id=agent_id,
            timestamp=datetime.now(timezone.utc).isoformat(),
            score=score,
            indicators=indicators,
            metadata={
                'contributions_analyzed': len(contributions),
                'weights': {
                    'novelty': NOVELTY_WEIGHT,
                    'diversity': DIVERSITY_WEIGHT,
                    'impact': IMPACT_WEIGHT,
                    'learning': LEARNING_WEIGHT
                }
            }
        )
        
        # Store metrics
        self.store_creativity_metrics(metrics)
        
        return metrics
    
    def _load_historical_creativity_metrics(self, agent_id: str) -> List[Dict[str, Any]]:
        """Load historical creativity metrics for an agent"""
        agent_creativity_dir = CREATIVITY_CACHE_DIR / agent_id
        
        if not agent_creativity_dir.exists():
            return []
        
        historical_metrics = []
        
        try:
            for metrics_file in sorted(agent_creativity_dir.glob("*.json")):
                if metrics_file.name == "latest.json":
                    continue
                
                with open(metrics_file, 'r') as f:
                    historical_metrics.append(json.load(f))
        except Exception as e:
            print(f"⚠️  Warning: Error loading historical metrics: {e}", file=sys.stderr)
        
        return historical_metrics
    
    def store_creativity_metrics(self, metrics: CreativityMetrics) -> None:
        """
        Store creativity metrics to persistent storage.
        
        Storage format: .github/agent-system/metrics/creativity/{agent_id}/{timestamp}.json
        """
        agent_creativity_dir = CREATIVITY_CACHE_DIR / metrics.agent_id
        agent_creativity_dir.mkdir(parents=True, exist_ok=True)
        
        # Use timestamp as filename (sortable)
        timestamp_str = metrics.timestamp.replace(':', '-').replace('.', '-')
        metrics_file = agent_creativity_dir / f"{timestamp_str}.json"
        
        try:
            with open(metrics_file, 'w') as f:
                json.dump(metrics.to_dict(), f, indent=2)
            
            # Also update latest.json for quick access
            latest_file = agent_creativity_dir / "latest.json"
            with open(latest_file, 'w') as f:
                json.dump(metrics.to_dict(), f, indent=2)
            
            print(f"✅ Creativity metrics stored: {metrics_file}", file=sys.stderr)
        
        except Exception as e:
            print(f"❌ Error storing creativity metrics: {e}", file=sys.stderr)
    
    def load_latest_creativity_metrics(self, agent_id: str) -> Optional[CreativityMetrics]:
        """Load the most recent creativity metrics for an agent"""
        latest_file = CREATIVITY_CACHE_DIR / agent_id / "latest.json"
        
        if not latest_file.exists():
            return None
        
        try:
            with open(latest_file, 'r') as f:
                data = json.load(f)
            
            return CreativityMetrics(
                agent_id=data['agent_id'],
                timestamp=data['timestamp'],
                score=CreativityScore(**data['score']),
                indicators=CreativityIndicators(**data['indicators']),
                metadata=data.get('metadata', {})
            )
        except Exception as e:
            print(f"❌ Error loading creativity metrics: {e}", file=sys.stderr)
            return None


def main():
    """CLI entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Creativity & Innovation Metrics Analyzer',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument(
        'agent_id',
        nargs='?',
        help='Agent ID to analyze'
    )
    parser.add_argument(
        '--analyze-all',
        action='store_true',
        help='Analyze all active agents'
    )
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output results as JSON'
    )
    
    args = parser.parse_args()
    
    # Initialize analyzer
    analyzer = CreativityAnalyzer()
    
    if args.analyze_all:
        print("📊 Analyzing creativity for all agents...")
        # This would integrate with the metrics collector
        print("Use this through agent-metrics-collector.py --evaluate-all")
    elif args.agent_id:
        # Load recent contributions (stub - would integrate with GitHub API)
        print(f"🎨 Analyzing creativity for {args.agent_id}")
        # This would fetch actual contributions from GitHub
        contributions = []  # Placeholder
        
        metrics = analyzer.analyze_creativity(args.agent_id, contributions)
        
        if args.json:
            print(json.dumps(metrics.to_dict(), indent=2))
        else:
            print(f"\n🎨 Creativity Analysis for {args.agent_id}")
            print("=" * 70)
            print(f"\n🌟 Creativity Scores:")
            print(f"  Novelty: {metrics.score.novelty:.2%}")
            print(f"  Diversity: {metrics.score.diversity:.2%}")
            print(f"  Impact: {metrics.score.impact:.2%}")
            print(f"  Learning: {metrics.score.learning:.2%}")
            print(f"\n  ⭐ Overall Creativity: {metrics.score.overall:.2%}")
            
            if metrics.indicators.breakthrough_moments:
                print(f"\n💡 Breakthrough Moments:")
                for moment in metrics.indicators.breakthrough_moments:
                    print(f"  - {moment}")
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == '__main__':
    main()
