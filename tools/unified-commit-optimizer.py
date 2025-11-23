#!/usr/bin/env python3
"""
Unified Commit Strategy System - Integration Layer

Combines rule-based learning with ML-based optimization for optimal results:
- Uses commit-strategy-learner.py for pattern identification
- Uses ml-commit-optimizer.py for predictive analytics
- Provides unified recommendations combining both approaches
- Handles graceful degradation if ML unavailable

Built by @create-guru for the Chained ecosystem.

Usage:
    # Analyze and optimize (uses both systems)
    python unified-commit-optimizer.py --analyze
    
    # Get comprehensive recommendations
    python unified-commit-optimizer.py --recommend
    
    # Validate a specific commit
    python unified-commit-optimizer.py --validate <commit-hash>
    
    # Generate complete report
    python unified-commit-optimizer.py --report
"""

import json
import sys
import argparse
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
import importlib.util


def load_module(name: str, filepath: Path):
    """Dynamically load a module"""
    spec = importlib.util.spec_from_file_location(name, filepath)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class UnifiedCommitOptimizer:
    """
    Unified system combining rule-based and ML-based optimization.
    
    Provides best-of-both-worlds approach:
    - Rule-based patterns for explainability
    - ML predictions for accuracy
    - Combined recommendations for completeness
    """
    
    def __init__(self, repo_path: str = ".", verbose: bool = False):
        self.repo_path = Path(repo_path)
        self.verbose = verbose
        
        # Load commit strategy learner
        tools_dir = Path(__file__).parent
        learner_module = load_module(
            "commit_strategy_learner",
            tools_dir / "commit-strategy-learner.py"
        )
        self.strategy_learner = learner_module.CommitStrategyLearner(
            repo_path=repo_path,
            verbose=verbose
        )
        
        # Try to load ML optimizer
        self.ml_available = False
        try:
            optimizer_module = load_module(
                "ml_commit_optimizer",
                tools_dir / "ml-commit-optimizer.py"
            )
            if optimizer_module.ML_AVAILABLE:
                self.ml_optimizer = optimizer_module.MLCommitOptimizer(
                    repo_path=repo_path,
                    verbose=verbose
                )
                self.ml_available = True
                self._log("ML optimizer loaded successfully")
            else:
                self._log("ML optimizer available but dependencies missing")
        except Exception as e:
            self._log(f"ML optimizer not available: {e}")
    
    def _log(self, message: str):
        """Log message if verbose"""
        if self.verbose:
            print(f"[UnifiedOptimizer] {message}", file=sys.stderr)
    
    def analyze_comprehensive(
        self,
        since_days: int = 30,
        max_commits: int = 500,
        train_ml: bool = True
    ) -> Dict[str, Any]:
        """
        Run comprehensive analysis using both systems.
        
        Args:
            since_days: Days of history to analyze
            max_commits: Maximum commits to analyze
            train_ml: Whether to train ML model
            
        Returns:
            Combined analysis results
        """
        self._log("Running comprehensive analysis...")
        
        results = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "since_days": since_days,
            "max_commits": max_commits
        }
        
        # Run rule-based analysis
        self._log("Running pattern-based analysis...")
        rule_based = self.strategy_learner.analyze_commits(
            since_days=since_days,
            max_commits=max_commits
        )
        results["pattern_analysis"] = rule_based
        
        # Run ML analysis if available
        if self.ml_available and train_ml:
            self._log("Training ML model...")
            ml_results = self.ml_optimizer.train_model(
                since_days=since_days,
                max_commits=max_commits
            )
            results["ml_training"] = ml_results
        else:
            results["ml_training"] = None
            if not self.ml_available:
                self._log("ML analysis skipped (not available)")
        
        return results
    
    def get_unified_recommendations(
        self,
        context: str = "general",
        min_confidence: float = 0.7
    ) -> Dict[str, Any]:
        """
        Generate unified recommendations combining both systems.
        
        Args:
            context: Context for recommendations
            min_confidence: Minimum confidence threshold
            
        Returns:
            Combined recommendations
        """
        self._log("Generating unified recommendations...")
        
        recommendations = {
            "context": context,
            "min_confidence": min_confidence,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "pattern_based": [],
            "ml_based": [],
            "unified": []
        }
        
        # Get pattern-based recommendations
        pattern_recs = self.strategy_learner.generate_recommendations(
            context=context,
            min_confidence=min_confidence
        )
        
        for rec in pattern_recs:
            recommendations["pattern_based"].append({
                "title": rec.title,
                "description": rec.description,
                "confidence": rec.confidence_score,
                "source": "pattern_analysis"
            })
        
        # Get ML-based insights if available
        if self.ml_available and self.ml_optimizer.model is not None:
            thresholds = self.ml_optimizer.thresholds
            
            recommendations["ml_based"].append({
                "title": "ML-Optimized Message Length",
                "description": (
                    f"Keep message length between {thresholds.message_length_min:.0f}-"
                    f"{thresholds.message_length_max:.0f} characters based on ML analysis"
                ),
                "confidence": thresholds.confidence,
                "source": "ml_model"
            })
            
            recommendations["ml_based"].append({
                "title": "ML-Optimized Commit Size",
                "description": (
                    f"Aim for ~{thresholds.files_per_commit_ideal:.0f} files per commit "
                    f"(max: {thresholds.files_per_commit_max:.0f}) based on successful patterns"
                ),
                "confidence": thresholds.confidence,
                "source": "ml_model"
            })
        
        # Create unified recommendations (combine both approaches)
        self._create_unified_recommendations(recommendations)
        
        return recommendations
    
    def _create_unified_recommendations(self, recs: Dict[str, Any]):
        """Combine pattern and ML recommendations into unified list"""
        unified = []
        
        # Prioritize by confidence across both sources
        all_recs = recs["pattern_based"] + recs["ml_based"]
        all_recs.sort(key=lambda r: r["confidence"], reverse=True)
        
        # Deduplicate similar recommendations
        seen_titles = set()
        for rec in all_recs:
            title_key = rec["title"].lower()
            if title_key not in seen_titles:
                unified.append(rec)
                seen_titles.add(title_key)
        
        recs["unified"] = unified[:10]  # Top 10 recommendations
    
    def validate_commit(
        self,
        commit_hash: str,
        show_details: bool = True
    ) -> Dict[str, Any]:
        """
        Validate a commit using both systems.
        
        Args:
            commit_hash: Commit to validate
            show_details: Include detailed analysis
            
        Returns:
            Validation results
        """
        self._log(f"Validating commit {commit_hash[:8]}...")
        
        validation = {
            "commit_hash": commit_hash,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "pattern_check": {},
            "ml_prediction": {},
            "overall_assessment": {}
        }
        
        # Pattern-based validation
        metrics = self.strategy_learner._get_commit_metrics(commit_hash)
        if metrics:
            validation["pattern_check"] = {
                "follows_conventional": metrics.follows_conventional,
                "has_body": metrics.has_body,
                "files_changed": metrics.files_changed,
                "lines_changed": metrics.total_lines_changed,
                "message_length": metrics.message_length
            }
        
        # ML-based prediction
        if self.ml_available and self.ml_optimizer.model is not None:
            prediction = self.ml_optimizer.predict_commit_success(commit_hash)
            if prediction:
                validation["ml_prediction"] = {
                    "success_probability": prediction.success_probability,
                    "predicted_success": prediction.predicted_success,
                    "confidence": prediction.confidence,
                    "risk_factors": prediction.risk_factors,
                    "recommendations": prediction.recommendations
                }
        
        # Overall assessment
        self._create_overall_assessment(validation)
        
        return validation
    
    def _create_overall_assessment(self, validation: Dict[str, Any]):
        """Create overall assessment from validation results"""
        assessment = {
            "quality_score": 0.0,
            "risk_level": "unknown",
            "key_issues": [],
            "top_recommendations": []
        }
        
        # Calculate quality score
        score = 0.5  # Base score
        
        # Pattern checks
        if validation["pattern_check"]:
            pc = validation["pattern_check"]
            if pc.get("follows_conventional"):
                score += 0.15
            if pc.get("has_body"):
                score += 0.10
            if pc.get("files_changed", 100) <= 10:
                score += 0.10
            if pc.get("lines_changed", 1000) <= 300:
                score += 0.15
        
        # ML prediction
        if validation["ml_prediction"]:
            ml = validation["ml_prediction"]
            ml_score = ml.get("success_probability", 0.5)
            confidence = ml.get("confidence", 0.5)
            score = (score + ml_score * confidence) / 2
            
            # Add risk factors
            assessment["key_issues"].extend(ml.get("risk_factors", []))
            assessment["top_recommendations"].extend(ml.get("recommendations", []))
        
        assessment["quality_score"] = min(score, 1.0)
        
        # Determine risk level
        if score >= 0.8:
            assessment["risk_level"] = "low"
        elif score >= 0.6:
            assessment["risk_level"] = "medium"
        else:
            assessment["risk_level"] = "high"
        
        validation["overall_assessment"] = assessment
    
    def generate_report(self, output_file: Optional[str] = None) -> str:
        """
        Generate comprehensive report combining both systems.
        
        Args:
            output_file: Optional file to save report
            
        Returns:
            Report text
        """
        self._log("Generating comprehensive report...")
        
        lines = [
            "# Unified Git Commit Strategy Report",
            "",
            f"Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}",
            f"Repository: {self.repo_path.name}",
            "",
            "## Analysis Methods",
            ""
        ]
        
        # Pattern-based analysis
        rule_data = self.strategy_learner.strategies_data
        lines.extend([
            "### Pattern-Based Analysis",
            "",
            f"- Commits analyzed: {rule_data['total_commits_analyzed']}",
            f"- Successful merges: {rule_data['successful_merges']}",
            f"- Patterns identified: {len(rule_data['patterns_identified'])}",
            ""
        ])
        
        # ML analysis
        if self.ml_available and self.ml_optimizer.model is not None:
            thresholds = self.ml_optimizer.thresholds
            lines.extend([
                "### Machine Learning Analysis",
                "",
                f"- Model: RandomForestClassifier",
                f"- Adaptive thresholds: Active",
                f"- Sample size: {thresholds.sample_size}",
                f"- Confidence: {thresholds.confidence:.1%}",
                ""
            ])
        else:
            lines.extend([
                "### Machine Learning Analysis",
                "",
                "- Status: Not available (train with --train)",
                ""
            ])
        
        # Get recommendations
        recommendations = self.get_unified_recommendations()
        lines.extend([
            "## Top Recommendations",
            ""
        ])
        
        for i, rec in enumerate(recommendations["unified"][:5], 1):
            lines.extend([
                f"### {i}. {rec['title']}",
                "",
                f"**Source:** {rec['source']}",
                f"**Confidence:** {rec['confidence']:.1%}",
                "",
                rec['description'],
                "",
                "---",
                ""
            ])
        
        report_text = '\n'.join(lines)
        
        # Save if output file specified
        if output_file:
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(report_text)
            self._log(f"Report saved to {output_file}")
        
        return report_text


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Unified Git Commit Strategy Optimizer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run comprehensive analysis
  python unified-commit-optimizer.py --analyze
  
  # Get recommendations
  python unified-commit-optimizer.py --recommend --context feature
  
  # Validate a commit
  python unified-commit-optimizer.py --validate abc123def
  
  # Generate report
  python unified-commit-optimizer.py --report --output analysis/commit_report.md
        """
    )
    
    parser.add_argument('--analyze', action='store_true',
                       help='Run comprehensive analysis')
    parser.add_argument('--since', type=int, default=30,
                       help='Days of history to analyze (default: 30)')
    parser.add_argument('--max-commits', type=int, default=500,
                       help='Maximum commits to analyze (default: 500)')
    parser.add_argument('--no-ml-train', action='store_true',
                       help='Skip ML training during analysis')
    
    parser.add_argument('--recommend', action='store_true',
                       help='Generate recommendations')
    parser.add_argument('--context', type=str, default='general',
                       choices=['general', 'feature', 'bugfix', 'refactor', 'docs'],
                       help='Context for recommendations')
    
    parser.add_argument('--validate', type=str, metavar='COMMIT',
                       help='Validate specific commit')
    
    parser.add_argument('--report', action='store_true',
                       help='Generate comprehensive report')
    parser.add_argument('--output', type=str,
                       help='Output file for report')
    
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Enable verbose logging')
    
    args = parser.parse_args()
    
    optimizer = UnifiedCommitOptimizer(verbose=args.verbose)
    
    try:
        if args.analyze:
            print("🔍 Running comprehensive analysis...")
            results = optimizer.analyze_comprehensive(
                since_days=args.since,
                max_commits=args.max_commits,
                train_ml=not args.no_ml_train
            )
            
            print("✅ Analysis complete!")
            print(f"\n📊 Results:")
            pattern_data = results['pattern_analysis']
            print(f"   Commits analyzed: {pattern_data.get('total_analyzed', 0)}")
            print(f"   Successful: {pattern_data.get('successful', 0)}")
            print(f"   Patterns found: {pattern_data.get('patterns_found', 0)}")
            
            if results['ml_training']:
                print(f"\n🤖 ML Training:")
                print(f"   Accuracy: {results['ml_training']['accuracy']:.1%}")
                print(f"   F1 Score: {results['ml_training']['f1_score']:.1%}")
        
        elif args.recommend:
            print(f"💡 Generating recommendations for context: {args.context}")
            recommendations = optimizer.get_unified_recommendations(context=args.context)
            
            print(f"\n✅ Generated {len(recommendations['unified'])} recommendations:")
            print()
            
            for i, rec in enumerate(recommendations['unified'][:5], 1):
                print(f"{i}. {rec['title']}")
                print(f"   Source: {rec['source']}")
                print(f"   Confidence: {rec['confidence']:.1%}")
                print(f"   {rec['description']}")
                print()
        
        elif args.validate:
            print(f"🔍 Validating commit {args.validate[:8]}...")
            validation = optimizer.validate_commit(args.validate)
            
            print(f"\n{'='*60}")
            print(f"Commit: {validation['commit_hash'][:8]}")
            print(f"{'='*60}")
            
            assessment = validation['overall_assessment']
            print(f"\n📊 Quality Score: {assessment['quality_score']:.1%}")
            print(f"⚠️  Risk Level: {assessment['risk_level'].upper()}")
            
            if assessment['key_issues']:
                print(f"\n🔍 Key Issues:")
                for issue in assessment['key_issues']:
                    print(f"   • {issue}")
            
            if assessment['top_recommendations']:
                print(f"\n💡 Top Recommendations:")
                for rec in assessment['top_recommendations'][:3]:
                    print(f"   • {rec}")
        
        elif args.report:
            print("📊 Generating comprehensive report...")
            report = optimizer.generate_report(output_file=args.output)
            
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
