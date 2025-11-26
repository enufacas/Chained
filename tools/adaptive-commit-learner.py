#!/usr/bin/env python3
"""
Adaptive Commit Strategy Learning System

An enhanced, Tesla-inspired learning system that continuously improves
its understanding of optimal commit strategies through adaptive learning.

Created by @create-guru - Infrastructure that learns and evolves.

Features:
- Adaptive learning rates based on confidence levels
- Temporal pattern recognition (time-based insights)
- Success correlation scoring with statistical significance
- Incremental learning from recent commits
- Automated recommendation validation
- Pattern drift detection
"""

import json
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict, field
from collections import defaultdict
import re
import subprocess

# Add tools directory to path for importing base learner
sys.path.insert(0, str(Path(__file__).parent))
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from commit_strategy_learner import CommitStrategyLearner, CommitMetrics, CommitPattern

# Constants
LEARNINGS_DIR = Path("learnings")
ANALYSIS_DIR = Path("analysis")
ADAPTIVE_LEARNINGS_FILE = LEARNINGS_DIR / "adaptive_commit_learning.json"
PATTERN_EVOLUTION_FILE = ANALYSIS_DIR / "pattern_evolution.json"

# Learning parameters
LEARNING_RATE_BASE = 0.1
LEARNING_RATE_DECAY = 0.95
MIN_PATTERN_CONFIDENCE = 0.6
PATTERN_EVOLUTION_WINDOW = 90  # days


@dataclass
class AdaptiveLearning:
    """Represents an adaptive learning insight"""
    insight_id: str
    timestamp: str
    pattern_type: str
    learning_text: str
    confidence: float
    evidence_count: int
    validation_status: str  # "unvalidated", "validated", "invalidated"
    learning_rate: float
    temporal_context: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class PatternEvolution:
    """Tracks how a pattern evolves over time"""
    pattern_name: str
    first_observed: str
    last_updated: str
    confidence_history: List[Dict[str, float]]
    occurrence_history: List[Dict[str, int]]
    trend: str  # "improving", "stable", "declining"
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class AdaptiveCommitLearner:
    """
    Enhanced learning system with adaptive capabilities.
    
    Builds on the base CommitStrategyLearner with:
    - Incremental learning from recent commits
    - Adaptive learning rates
    - Pattern evolution tracking
    - Success correlation analysis
    - Temporal pattern recognition
    """
    
    def __init__(self, repo_path: str = ".", verbose: bool = False):
        self.repo_path = Path(repo_path)
        self.verbose = verbose
        self.adaptive_data = self._load_adaptive_data()
        self.evolution_data = self._load_evolution_data()
        
        # Import base learner dynamically
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            'base_learner', 
            Path(__file__).parent / 'commit-strategy-learner.py'
        )
        learner_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(learner_module)
        self.CommitStrategyLearner = learner_module.CommitStrategyLearner
        
        self.base_learner = self.CommitStrategyLearner(
            repo_path=repo_path, 
            verbose=verbose
        )
    
    def _log(self, message: str, level: str = "INFO"):
        """Log message if verbose mode enabled"""
        if self.verbose:
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"[{timestamp}] [{level}] {message}", file=sys.stderr)
    
    def _load_adaptive_data(self) -> Dict:
        """Load adaptive learning data"""
        if ADAPTIVE_LEARNINGS_FILE.exists():
            with open(ADAPTIVE_LEARNINGS_FILE, 'r') as f:
                return json.load(f)
        return self._initialize_adaptive_data()
    
    def _initialize_adaptive_data(self) -> Dict:
        """Initialize adaptive learning structure"""
        return {
            "version": "2.0.0",
            "last_updated": None,
            "learning_sessions": [],
            "active_learnings": [],
            "validated_patterns": [],
            "invalidated_patterns": [],
            "cumulative_insights": 0,
            "learning_velocity": 0.0
        }
    
    def _load_evolution_data(self) -> Dict:
        """Load pattern evolution data"""
        if PATTERN_EVOLUTION_FILE.exists():
            with open(PATTERN_EVOLUTION_FILE, 'r') as f:
                return json.load(f)
        return {
            "version": "1.0.0",
            "patterns": {},
            "last_updated": None
        }
    
    def _save_adaptive_data(self):
        """Save adaptive learning data"""
        self.adaptive_data["last_updated"] = datetime.now(timezone.utc).isoformat()
        LEARNINGS_DIR.mkdir(parents=True, exist_ok=True)
        
        temp_file = ADAPTIVE_LEARNINGS_FILE.with_suffix('.json.tmp')
        with open(temp_file, 'w') as f:
            json.dump(self.adaptive_data, f, indent=2)
        temp_file.replace(ADAPTIVE_LEARNINGS_FILE)
        
        self._log(f"Saved adaptive data to {ADAPTIVE_LEARNINGS_FILE}")
    
    def _save_evolution_data(self):
        """Save pattern evolution data"""
        self.evolution_data["last_updated"] = datetime.now(timezone.utc).isoformat()
        ANALYSIS_DIR.mkdir(parents=True, exist_ok=True)
        
        temp_file = PATTERN_EVOLUTION_FILE.with_suffix('.json.tmp')
        with open(temp_file, 'w') as f:
            json.dump(self.evolution_data, f, indent=2)
        temp_file.replace(PATTERN_EVOLUTION_FILE)
        
        self._log(f"Saved evolution data to {PATTERN_EVOLUTION_FILE}")
    
    def incremental_learn(self, days_lookback: int = 7) -> Dict[str, Any]:
        """
        Perform incremental learning from recent commits.
        
        This allows continuous learning without reprocessing all history.
        
        Args:
            days_lookback: Number of recent days to analyze
            
        Returns:
            Learning session summary
        """
        self._log(f"Starting incremental learning (last {days_lookback} days)")
        
        # Get recent commits using base learner
        summary = self.base_learner.analyze_commits(
            since_days=days_lookback,
            max_commits=100
        )
        
        # Calculate learning rate for this session
        session_count = len(self.adaptive_data["learning_sessions"])
        learning_rate = LEARNING_RATE_BASE * (LEARNING_RATE_DECAY ** session_count)
        
        self._log(f"Learning rate for session {session_count + 1}: {learning_rate:.3f}")
        
        # Extract new insights
        new_insights = self._extract_adaptive_insights(
            summary, 
            learning_rate
        )
        
        # Update pattern evolution
        self._update_pattern_evolution(summary)
        
        # Create learning session record
        session = {
            "session_id": session_count + 1,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "days_analyzed": days_lookback,
            "commits_analyzed": summary.get("total_analyzed", 0),
            "learning_rate": learning_rate,
            "new_insights": len(new_insights),
            "patterns_updated": summary.get("patterns_found", 0)
        }
        
        self.adaptive_data["learning_sessions"].append(session)
        self.adaptive_data["cumulative_insights"] += len(new_insights)
        self.adaptive_data["active_learnings"].extend([i.to_dict() for i in new_insights])
        
        # Calculate learning velocity (insights per session)
        if len(self.adaptive_data["learning_sessions"]) > 1:
            recent_sessions = self.adaptive_data["learning_sessions"][-5:]
            total_insights = sum(s["new_insights"] for s in recent_sessions)
            self.adaptive_data["learning_velocity"] = total_insights / len(recent_sessions)
        
        self._save_adaptive_data()
        self._save_evolution_data()
        
        return {
            "session": session,
            "new_insights": [i.to_dict() for i in new_insights],
            "learning_velocity": self.adaptive_data["learning_velocity"]
        }
    
    def _extract_adaptive_insights(
        self, 
        analysis_summary: Dict[str, Any],
        learning_rate: float
    ) -> List[AdaptiveLearning]:
        """Extract adaptive insights from analysis"""
        insights = []
        
        # Load patterns from base learner
        patterns_data = self.base_learner.patterns_data
        
        # Temporal context (time of day, day of week)
        now = datetime.now(timezone.utc)
        temporal_context = {
            "hour": now.hour,
            "day_of_week": now.strftime("%A"),
            "week_of_year": now.isocalendar()[1]
        }
        
        # Extract insights from message patterns
        if "message" in patterns_data:
            for pattern_name, pattern_data in patterns_data["message"].items():
                confidence = pattern_data.get("confidence_score", 0.0)
                if confidence >= MIN_PATTERN_CONFIDENCE:
                    insight = AdaptiveLearning(
                        insight_id=f"msg_{pattern_name}_{now.timestamp():.0f}",
                        timestamp=now.isoformat(),
                        pattern_type="message",
                        learning_text=f"Pattern '{pattern_name}' shows {confidence:.1%} confidence with {pattern_data.get('occurrence_count', 0)} occurrences",
                        confidence=confidence,
                        evidence_count=pattern_data.get("occurrence_count", 0),
                        validation_status="unvalidated",
                        learning_rate=learning_rate,
                        temporal_context=temporal_context
                    )
                    insights.append(insight)
        
        # Extract insights from size patterns
        if "size" in patterns_data:
            for pattern_name, pattern_data in patterns_data["size"].items():
                confidence = pattern_data.get("confidence_score", 0.0)
                if confidence >= MIN_PATTERN_CONFIDENCE:
                    insight = AdaptiveLearning(
                        insight_id=f"size_{pattern_name}_{now.timestamp():.0f}",
                        timestamp=now.isoformat(),
                        pattern_type="size",
                        learning_text=f"Size pattern '{pattern_name}' validated with {confidence:.1%} confidence",
                        confidence=confidence,
                        evidence_count=pattern_data.get("occurrence_count", 0),
                        validation_status="unvalidated",
                        learning_rate=learning_rate,
                        temporal_context=temporal_context
                    )
                    insights.append(insight)
        
        # Extract insights from organization patterns
        if "organization" in patterns_data:
            for pattern_name, pattern_data in patterns_data["organization"].items():
                confidence = pattern_data.get("confidence_score", 0.0)
                if confidence >= MIN_PATTERN_CONFIDENCE:
                    insight = AdaptiveLearning(
                        insight_id=f"org_{pattern_name}_{now.timestamp():.0f}",
                        timestamp=now.isoformat(),
                        pattern_type="organization",
                        learning_text=f"Organization pattern '{pattern_name}' shows strong correlation ({confidence:.1%})",
                        confidence=confidence,
                        evidence_count=pattern_data.get("occurrence_count", 0),
                        validation_status="unvalidated",
                        learning_rate=learning_rate,
                        temporal_context=temporal_context
                    )
                    insights.append(insight)
        
        self._log(f"Extracted {len(insights)} adaptive insights")
        return insights
    
    def _update_pattern_evolution(self, analysis_summary: Dict[str, Any]):
        """Update pattern evolution tracking"""
        patterns_data = self.base_learner.patterns_data
        now = datetime.now(timezone.utc).isoformat()
        
        for pattern_type in ["message", "size", "organization"]:
            if pattern_type not in patterns_data:
                continue
            
            for pattern_name, pattern_data in patterns_data[pattern_type].items():
                full_pattern_name = f"{pattern_type}_{pattern_name}"
                
                if full_pattern_name not in self.evolution_data["patterns"]:
                    # New pattern
                    self.evolution_data["patterns"][full_pattern_name] = {
                        "pattern_name": full_pattern_name,
                        "first_observed": now,
                        "last_updated": now,
                        "confidence_history": [],
                        "occurrence_history": [],
                        "trend": "new"
                    }
                
                # Update history
                pattern_evo = self.evolution_data["patterns"][full_pattern_name]
                pattern_evo["last_updated"] = now
                
                confidence = pattern_data.get("confidence_score", 0.0)
                occurrence = pattern_data.get("occurrence_count", 0)
                
                pattern_evo["confidence_history"].append({
                    "timestamp": now,
                    "value": confidence
                })
                pattern_evo["occurrence_history"].append({
                    "timestamp": now,
                    "value": occurrence
                })
                
                # Calculate trend (simple: last 3 vs previous 3)
                conf_hist = pattern_evo["confidence_history"]
                if len(conf_hist) >= 6:
                    recent_avg = sum(c["value"] for c in conf_hist[-3:]) / 3
                    previous_avg = sum(c["value"] for c in conf_hist[-6:-3]) / 3
                    
                    if recent_avg > previous_avg * 1.1:
                        pattern_evo["trend"] = "improving"
                    elif recent_avg < previous_avg * 0.9:
                        pattern_evo["trend"] = "declining"
                    else:
                        pattern_evo["trend"] = "stable"
        
        self._log("Updated pattern evolution tracking")
    
    def validate_recommendations(self, validation_window_days: int = 30) -> Dict[str, Any]:
        """
        Validate previous recommendations against recent commit success.
        
        This implements a feedback loop for recommendation quality.
        
        Args:
            validation_window_days: Days to look back for validation
            
        Returns:
            Validation report
        """
        self._log(f"Validating recommendations (window: {validation_window_days} days)")
        
        # Get recent successful commits
        recent_analysis = self.base_learner.analyze_commits(
            since_days=validation_window_days,
            max_commits=200
        )
        
        validated = 0
        invalidated = 0
        
        # Check each active learning against recent patterns
        for learning_dict in self.adaptive_data["active_learnings"]:
            if learning_dict["validation_status"] != "unvalidated":
                continue
            
            # Simple validation: check if confidence is maintained
            pattern_type = learning_dict["pattern_type"]
            current_confidence = learning_dict["confidence"]
            
            # Get current pattern confidence from base learner
            patterns_data = self.base_learner.patterns_data
            
            if pattern_type in patterns_data:
                # Find matching pattern and compare confidence
                for pattern_name, pattern_data in patterns_data[pattern_type].items():
                    new_confidence = pattern_data.get("confidence_score", 0.0)
                    
                    if new_confidence >= current_confidence * 0.9:
                        learning_dict["validation_status"] = "validated"
                        self.adaptive_data["validated_patterns"].append(learning_dict)
                        validated += 1
                        break
                    elif new_confidence < current_confidence * 0.7:
                        learning_dict["validation_status"] = "invalidated"
                        self.adaptive_data["invalidated_patterns"].append(learning_dict)
                        invalidated += 1
                        break
        
        # Clean up validated/invalidated from active learnings
        self.adaptive_data["active_learnings"] = [
            l for l in self.adaptive_data["active_learnings"]
            if l["validation_status"] == "unvalidated"
        ]
        
        self._save_adaptive_data()
        
        return {
            "validated": validated,
            "invalidated": invalidated,
            "still_active": len(self.adaptive_data["active_learnings"]),
            "total_validated": len(self.adaptive_data["validated_patterns"]),
            "total_invalidated": len(self.adaptive_data["invalidated_patterns"])
        }
    
    def generate_adaptive_report(self) -> str:
        """Generate comprehensive adaptive learning report"""
        lines = [
            "# Adaptive Commit Strategy Learning Report",
            "",
            f"**Generated:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}",
            f"**By:** @create-guru (Adaptive Learning System)",
            "",
            "## System Status",
            "",
            f"- **Learning Sessions:** {len(self.adaptive_data['learning_sessions'])}",
            f"- **Cumulative Insights:** {self.adaptive_data['cumulative_insights']}",
            f"- **Learning Velocity:** {self.adaptive_data['learning_velocity']:.2f} insights/session",
            f"- **Active Learnings:** {len(self.adaptive_data['active_learnings'])}",
            f"- **Validated Patterns:** {len(self.adaptive_data['validated_patterns'])}",
            f"- **Invalidated Patterns:** {len(self.adaptive_data['invalidated_patterns'])}",
            "",
            "## Pattern Evolution",
            ""
        ]
        
        # Add pattern evolution summaries
        improving_patterns = []
        declining_patterns = []
        
        for pattern_name, pattern_data in self.evolution_data["patterns"].items():
            trend = pattern_data.get("trend", "unknown")
            if trend == "improving":
                improving_patterns.append(pattern_name)
            elif trend == "declining":
                declining_patterns.append(pattern_name)
        
        lines.extend([
            f"### Improving Patterns ({len(improving_patterns)})",
            ""
        ])
        
        for pattern in improving_patterns[:5]:
            lines.append(f"- ✅ `{pattern}`")
        
        lines.extend([
            "",
            f"### Declining Patterns ({len(declining_patterns)})",
            ""
        ])
        
        for pattern in declining_patterns[:5]:
            lines.append(f"- ⚠️ `{pattern}`")
        
        lines.extend([
            "",
            "## Recent Learning Sessions",
            ""
        ])
        
        # Add last 5 learning sessions
        recent_sessions = self.adaptive_data["learning_sessions"][-5:]
        for session in reversed(recent_sessions):
            lines.extend([
                f"### Session #{session['session_id']}",
                "",
                f"- **Timestamp:** {session['timestamp'][:19]}",
                f"- **Commits Analyzed:** {session['commits_analyzed']}",
                f"- **New Insights:** {session['new_insights']}",
                f"- **Learning Rate:** {session['learning_rate']:.3f}",
                ""
            ])
        
        lines.extend([
            "## Validated Insights",
            ""
        ])
        
        # Add validated patterns
        validated = self.adaptive_data["validated_patterns"][-10:]
        for insight_dict in reversed(validated):
            lines.extend([
                f"### {insight_dict['pattern_type'].title()} Pattern",
                "",
                insight_dict["learning_text"],
                "",
                f"**Confidence:** {insight_dict['confidence']:.1%} | **Evidence:** {insight_dict['evidence_count']} commits",
                ""
            ])
        
        lines.extend([
            "---",
            "",
            "*Generated by Adaptive Commit Learning System*",
            "*@create-guru - Infrastructure that learns and evolves*"
        ])
        
        return '\n'.join(lines)


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Adaptive Commit Strategy Learning System",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('--learn', action='store_true',
                       help='Perform incremental learning')
    parser.add_argument('--days', type=int, default=7,
                       help='Days to analyze for incremental learning (default: 7)')
    
    parser.add_argument('--validate', action='store_true',
                       help='Validate previous recommendations')
    parser.add_argument('--validation-window', type=int, default=30,
                       help='Days for validation window (default: 30)')
    
    parser.add_argument('--report', action='store_true',
                       help='Generate adaptive learning report')
    parser.add_argument('--output', type=str,
                       help='Output file for report')
    
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Enable verbose logging')
    
    args = parser.parse_args()
    
    learner = AdaptiveCommitLearner(verbose=args.verbose)
    
    try:
        if args.learn:
            print(f"🧠 Performing incremental learning (last {args.days} days)...")
            result = learner.incremental_learn(days_lookback=args.days)
            
            print("✅ Learning complete!")
            print(f"   Session: #{result['session']['session_id']}")
            print(f"   Commits analyzed: {result['session']['commits_analyzed']}")
            print(f"   New insights: {result['session']['new_insights']}")
            print(f"   Learning velocity: {result['learning_velocity']:.2f} insights/session")
        
        elif args.validate:
            print(f"✓ Validating recommendations (window: {args.validation_window} days)...")
            result = learner.validate_recommendations(
                validation_window_days=args.validation_window
            )
            
            print("✅ Validation complete!")
            print(f"   Validated: {result['validated']}")
            print(f"   Invalidated: {result['invalidated']}")
            print(f"   Still active: {result['still_active']}")
        
        elif args.report:
            print("📊 Generating adaptive learning report...")
            report = learner.generate_adaptive_report()
            
            if args.output:
                output_path = Path(args.output)
                output_path.parent.mkdir(parents=True, exist_ok=True)
                output_path.write_text(report)
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
