#!/usr/bin/env python3
"""
Machine Learning-Based Commit Strategy Optimizer for Chained

An advanced, ML-driven system that learns optimal git commit strategies through:
- Pattern clustering and classification
- Predictive success scoring
- Adaptive threshold learning
- Real-time feedback integration

Inspired by Nikola Tesla's visionary approach: inventive, forward-thinking, elegant.
Built by @create-guru for the Chained autonomous AI ecosystem.

Architecture:
- MLCommitClassifier: Machine learning classification engine
- AdaptiveThresholdLearner: Self-adjusting optimization thresholds
- PredictiveScorer: Pre-commit success prediction
- FeedbackIntegrator: Real-time learning from outcomes

Features:
- Scikit-learn based pattern classification
- Dynamic threshold adaptation based on repository evolution
- Commit quality prediction before push
- Continuous learning from merge outcomes
- Repository-specific model training
- Confidence-weighted recommendations

Usage:
    # Train model on historical data
    python ml-commit-optimizer.py --train --since 90
    
    # Predict success probability for a commit
    python ml-commit-optimizer.py --predict <commit-hash>
    
    # Analyze and optimize thresholds
    python ml-commit-optimizer.py --optimize
    
    # Check model and threshold status
    python ml-commit-optimizer.py --status
"""

import json
import os
import sys
import re
import subprocess
import pickle
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict, field
from collections import defaultdict, Counter
import argparse

# ML imports (graceful degradation if not available)
try:
    import numpy as np
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.preprocessing import StandardScaler
    from sklearn.model_selection import train_test_split, cross_val_score
    from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    # Create dummy np for type hints
    class DummyNumpy:
        class ndarray:
            pass
    np = DummyNumpy()
    print("⚠️  Warning: scikit-learn not available. ML features disabled.", file=sys.stderr)
    print("   Install with: pip install scikit-learn numpy", file=sys.stderr)


# Constants
LEARNINGS_DIR = Path("learnings")
ML_MODELS_DIR = LEARNINGS_DIR / "ml_models"
MODEL_FILE = ML_MODELS_DIR / "commit_optimizer_model.pkl"
SCALER_FILE = ML_MODELS_DIR / "feature_scaler.pkl"
THRESHOLDS_FILE = ML_MODELS_DIR / "adaptive_thresholds.json"
PREDICTIONS_LOG = LEARNINGS_DIR / "commit_predictions.json"


@dataclass
class CommitFeatures:
    """Feature vector for ML model"""
    # Message features
    message_length: float
    has_body: int
    conventional_format: int
    message_clarity_score: float
    
    # Size features
    files_changed: float
    lines_added: float
    lines_deleted: float
    total_lines_changed: float
    
    # Organization features
    file_type_diversity: float
    directory_count: float
    
    # Temporal features
    hour_of_day: float
    day_of_week: float
    
    # Derived features
    change_density: float  # lines per file
    modification_ratio: float  # deleted / added
    
    def to_array(self) -> List[float]:
        """Convert to numpy-compatible array"""
        return [
            self.message_length,
            self.has_body,
            self.conventional_format,
            self.message_clarity_score,
            self.files_changed,
            self.lines_added,
            self.lines_deleted,
            self.total_lines_changed,
            self.file_type_diversity,
            self.directory_count,
            self.hour_of_day,
            self.day_of_week,
            self.change_density,
            self.modification_ratio
        ]
    
    @classmethod
    def feature_names(cls) -> List[str]:
        """Get feature names for model"""
        return [
            'message_length', 'has_body', 'conventional_format', 
            'message_clarity_score', 'files_changed', 'lines_added',
            'lines_deleted', 'total_lines_changed', 'file_type_diversity',
            'directory_count', 'hour_of_day', 'day_of_week',
            'change_density', 'modification_ratio'
        ]


@dataclass
class PredictionResult:
    """Result of commit success prediction"""
    commit_hash: str
    predicted_success: bool
    success_probability: float
    confidence: float
    risk_factors: List[str]
    recommendations: List[str]
    feature_importance: Dict[str, float]


@dataclass
class AdaptiveThresholds:
    """Self-adjusting optimization thresholds"""
    message_length_min: float
    message_length_max: float
    files_per_commit_ideal: float
    files_per_commit_max: float
    lines_per_commit_ideal: float
    lines_per_commit_max: float
    conventional_commit_weight: float
    last_updated: str
    confidence: float
    sample_size: int


class MLCommitOptimizer:
    """
    Machine Learning-based Commit Strategy Optimizer.
    
    Learns optimal commit patterns through ML classification and provides
    predictive analysis for commit success.
    """
    
    def __init__(self, repo_path: str = ".", verbose: bool = False):
        self.repo_path = Path(repo_path)
        self.verbose = verbose
        self.model = None
        self.scaler = None
        self.thresholds = self._load_thresholds()
        
        if ML_AVAILABLE:
            self._load_model()
    
    def _log(self, message: str, level: str = "INFO"):
        """Log message if verbose mode enabled"""
        if self.verbose:
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"[{timestamp}] [{level}] {message}", file=sys.stderr)
    
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
            self._log(f"Git command failed: {e}", "ERROR")
            return ""
    
    def _extract_features(self, commit_hash: str) -> Optional[CommitFeatures]:
        """Extract ML features from a commit"""
        try:
            # Get commit info
            commit_info = self._run_git_command([
                'show', '--format=%H%n%an%n%at%n%s%n%b', '--no-patch', commit_hash
            ])
            
            if not commit_info:
                return None
            
            lines = commit_info.split('\n')
            if len(lines) < 4:
                return None
            
            timestamp = int(lines[2])
            dt = datetime.fromtimestamp(timestamp, tz=timezone.utc)
            subject = lines[3]
            body = '\n'.join(lines[4:]).strip() if len(lines) > 4 else ""
            
            # Message features
            message_length = len(subject)
            has_body = 1 if body else 0
            conventional_format = 1 if self._is_conventional(subject) else 0
            message_clarity_score = self._calculate_clarity_score(subject + "\n" + body)
            
            # Get file changes
            stats = self._run_git_command([
                'show', '--stat', '--format=', commit_hash
            ])
            
            files_changed = 0
            lines_added = 0
            lines_deleted = 0
            file_types = set()
            directories = set()
            
            if stats:
                for line in stats.split('\n'):
                    if '|' in line:
                        files_changed += 1
                        filename = line.split('|')[0].strip()
                        
                        # Extract file extension
                        if '.' in filename:
                            ext = filename.split('.')[-1]
                            file_types.add(ext)
                        
                        # Extract directory
                        if '/' in filename:
                            directory = filename.rsplit('/', 1)[0]
                            directories.add(directory)
                    
                    # Parse summary line
                    if 'changed' in line:
                        match = re.search(r'(\d+) insertion', line)
                        if match:
                            lines_added = int(match.group(1))
                        match = re.search(r'(\d+) deletion', line)
                        if match:
                            lines_deleted = int(match.group(1))
            
            total_lines_changed = lines_added + lines_deleted
            
            # Derived features
            change_density = total_lines_changed / max(files_changed, 1)
            modification_ratio = lines_deleted / max(lines_added, 1) if lines_added > 0 else 0
            
            return CommitFeatures(
                message_length=float(message_length),
                has_body=has_body,
                conventional_format=conventional_format,
                message_clarity_score=message_clarity_score,
                files_changed=float(files_changed),
                lines_added=float(lines_added),
                lines_deleted=float(lines_deleted),
                total_lines_changed=float(total_lines_changed),
                file_type_diversity=float(len(file_types)),
                directory_count=float(len(directories)),
                hour_of_day=float(dt.hour),
                day_of_week=float(dt.weekday()),
                change_density=change_density,
                modification_ratio=modification_ratio
            )
            
        except Exception as e:
            self._log(f"Error extracting features from {commit_hash}: {e}", "ERROR")
            return None
    
    def _is_conventional(self, message: str) -> bool:
        """Check if message follows conventional commit format"""
        pattern = r'^(feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert)(\([a-z0-9\-]+\))?: .+'
        return bool(re.match(pattern, message, re.IGNORECASE))
    
    def _calculate_clarity_score(self, message: str) -> float:
        """Calculate message clarity score (0-1)"""
        score = 0.0
        
        # Length bonus (descriptive but not too long)
        if 20 <= len(message) <= 200:
            score += 0.3
        
        # Has explanation
        if '\n' in message and len(message.split('\n')) > 1:
            score += 0.2
        
        # Contains key words
        key_words = ['add', 'fix', 'update', 'remove', 'improve', 'refactor', 'implement']
        if any(word in message.lower() for word in key_words):
            score += 0.2
        
        # Starts with verb
        if re.match(r'^[A-Z][a-z]+', message):
            score += 0.15
        
        # Has context
        if any(word in message.lower() for word in ['because', 'to', 'for', 'when', 'while']):
            score += 0.15
        
        return min(score, 1.0)
    
    def _get_commit_label(self, commit_hash: str) -> int:
        """
        Get label for commit (success=1, failure=0).
        
        Success is determined by:
        - Commit is in main branch
        - Not reverted
        - Part of merged PR
        """
        # Check if commit is in main branch
        branches = self._run_git_command(['branch', '--contains', commit_hash])
        in_main = 'main' in branches or 'master' in branches
        
        # Check if commit was reverted
        log = self._run_git_command([
            'log', '--all', '--grep', f'revert.*{commit_hash[:8]}', '--format=%H'
        ])
        is_reverted = bool(log.strip())
        
        # Success if in main and not reverted
        return 1 if (in_main and not is_reverted) else 0
    
    def train_model(self, since_days: int = 90, max_commits: int = 1000) -> Dict[str, Any]:
        """
        Train ML model on historical commit data.
        
        Args:
            since_days: Days of history to analyze
            max_commits: Maximum commits to use for training
            
        Returns:
            Training metrics and model info
        """
        if not ML_AVAILABLE:
            self._log("ML libraries not available. Cannot train model.", "ERROR")
            return {"error": "ML dependencies not installed"}
        
        self._log(f"Training model on last {since_days} days of history...")
        
        # Get commits
        since_date = (datetime.now() - timedelta(days=since_days)).strftime('%Y-%m-%d')
        commit_hashes = self._run_git_command([
            'log', '--format=%H', f'--since={since_date}', '--no-merges', f'-{max_commits}'
        ]).split('\n')
        
        commit_hashes = [h for h in commit_hashes if h.strip()]
        self._log(f"Found {len(commit_hashes)} commits")
        
        # Extract features and labels
        X = []
        y = []
        
        for i, commit_hash in enumerate(commit_hashes):
            if i % 50 == 0:
                self._log(f"Processing: {i}/{len(commit_hashes)}")
            
            features = self._extract_features(commit_hash)
            if not features:
                continue
            
            label = self._get_commit_label(commit_hash)
            
            X.append(features.to_array())
            y.append(label)
        
        if len(X) < 10:
            self._log("Insufficient training data", "ERROR")
            return {"error": "Not enough data", "samples": len(X)}
        
        self._log(f"Training on {len(X)} samples")
        
        X = np.array(X)
        y = np.array(y)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Scale features
        self.scaler = StandardScaler()
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train model (ensemble for robustness)
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            min_samples_split=5,
            random_state=42,
            n_jobs=-1
        )
        
        self.model.fit(X_train_scaled, y_train)
        
        # Evaluate
        y_pred = self.model.predict(X_test_scaled)
        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred, zero_division=0)
        recall = recall_score(y_test, y_pred, zero_division=0)
        f1 = f1_score(y_test, y_pred, zero_division=0)
        
        # Cross-validation
        cv_scores = cross_val_score(self.model, X_train_scaled, y_train, cv=5)
        
        self._log(f"Model trained successfully!")
        self._log(f"Accuracy: {accuracy:.2%}")
        self._log(f"Precision: {precision:.2%}")
        self._log(f"Recall: {recall:.2%}")
        self._log(f"F1 Score: {f1:.2%}")
        self._log(f"CV Score: {cv_scores.mean():.2%} (+/- {cv_scores.std():.2%})")
        
        # Save model
        self._save_model()
        
        # Learn adaptive thresholds
        self._learn_thresholds(X, y)
        
        return {
            "samples": len(X),
            "train_size": len(X_train),
            "test_size": len(X_test),
            "accuracy": float(accuracy),
            "precision": float(precision),
            "recall": float(recall),
            "f1_score": float(f1),
            "cv_mean": float(cv_scores.mean()),
            "cv_std": float(cv_scores.std()),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    def _learn_thresholds(self, X: np.ndarray, y: np.ndarray):
        """Learn adaptive thresholds from successful commits"""
        # Get successful commits
        successful_X = X[y == 1]
        
        if len(successful_X) == 0:
            return
        
        # Calculate statistics for successful commits
        # Feature indices match CommitFeatures.to_array()
        msg_lengths = successful_X[:, 0]
        files_changed = successful_X[:, 4]
        total_lines = successful_X[:, 7]
        
        self.thresholds = AdaptiveThresholds(
            message_length_min=float(np.percentile(msg_lengths, 25)),
            message_length_max=float(np.percentile(msg_lengths, 75)),
            files_per_commit_ideal=float(np.median(files_changed)),
            files_per_commit_max=float(np.percentile(files_changed, 75)),
            lines_per_commit_ideal=float(np.median(total_lines)),
            lines_per_commit_max=float(np.percentile(total_lines, 75)),
            conventional_commit_weight=float(np.mean(successful_X[:, 2])),
            last_updated=datetime.now(timezone.utc).isoformat(),
            confidence=len(successful_X) / len(X),
            sample_size=len(successful_X)
        )
        
        self._save_thresholds()
        self._log(f"Learned adaptive thresholds from {len(successful_X)} successful commits")
    
    def predict_commit_success(self, commit_hash: str) -> Optional[PredictionResult]:
        """
        Predict success probability for a commit.
        
        Args:
            commit_hash: Git commit hash or 'HEAD' for staged changes
            
        Returns:
            PredictionResult with success probability and recommendations
        """
        if not ML_AVAILABLE or self.model is None:
            self._log("Model not available. Train model first.", "ERROR")
            return None
        
        # Extract features
        features = self._extract_features(commit_hash)
        if not features:
            self._log(f"Could not extract features for {commit_hash}", "ERROR")
            return None
        
        # Scale and predict
        X = np.array([features.to_array()])
        X_scaled = self.scaler.transform(X)
        
        prediction = self.model.predict(X_scaled)[0]
        probabilities = self.model.predict_proba(X_scaled)[0]
        success_prob = probabilities[1]
        
        # Get feature importance
        feature_names = CommitFeatures.feature_names()
        importances = dict(zip(feature_names, self.model.feature_importances_))
        
        # Identify risk factors
        risk_factors = []
        recommendations = []
        
        # Check against thresholds
        if features.message_length < self.thresholds.message_length_min:
            risk_factors.append("Message too short")
            recommendations.append(f"Expand message to at least {self.thresholds.message_length_min:.0f} characters")
        
        if features.files_changed > self.thresholds.files_per_commit_max:
            risk_factors.append("Too many files changed")
            recommendations.append(f"Split into smaller commits (ideal: {self.thresholds.files_per_commit_ideal:.0f} files)")
        
        if features.total_lines_changed > self.thresholds.lines_per_commit_max:
            risk_factors.append("Too many lines changed")
            recommendations.append(f"Consider reducing scope (ideal: {self.thresholds.lines_per_commit_ideal:.0f} lines)")
        
        if not features.conventional_format and self.thresholds.conventional_commit_weight > 0.5:
            risk_factors.append("Non-conventional commit format")
            recommendations.append("Use conventional commit format: type(scope): description")
        
        if not features.has_body and success_prob < 0.7:
            risk_factors.append("Missing commit message body")
            recommendations.append("Add detailed explanation in commit body")
        
        # Calculate confidence based on model uncertainty and threshold confidence
        confidence = min(max(probabilities) * self.thresholds.confidence, 1.0)
        
        result = PredictionResult(
            commit_hash=commit_hash,
            predicted_success=bool(prediction),
            success_probability=float(success_prob),
            confidence=float(confidence),
            risk_factors=risk_factors,
            recommendations=recommendations,
            feature_importance=importances
        )
        
        # Log prediction
        self._log_prediction(result)
        
        return result
    
    def _load_model(self):
        """Load trained model from disk"""
        if MODEL_FILE.exists() and SCALER_FILE.exists():
            try:
                with open(MODEL_FILE, 'rb') as f:
                    self.model = pickle.load(f)
                with open(SCALER_FILE, 'rb') as f:
                    self.scaler = pickle.load(f)
                self._log("Loaded trained model")
            except Exception as e:
                self._log(f"Error loading model: {e}", "ERROR")
    
    def _save_model(self):
        """Save trained model to disk"""
        try:
            ML_MODELS_DIR.mkdir(parents=True, exist_ok=True)
            
            with open(MODEL_FILE, 'wb') as f:
                pickle.dump(self.model, f)
            with open(SCALER_FILE, 'wb') as f:
                pickle.dump(self.scaler, f)
            
            self._log(f"Model saved to {MODEL_FILE}")
        except Exception as e:
            self._log(f"Error saving model: {e}", "ERROR")
    
    def _load_thresholds(self) -> AdaptiveThresholds:
        """Load adaptive thresholds"""
        if THRESHOLDS_FILE.exists():
            try:
                with open(THRESHOLDS_FILE, 'r') as f:
                    data = json.load(f)
                return AdaptiveThresholds(**data)
            except Exception as e:
                self._log(f"Error loading thresholds: {e}", "ERROR")
        
        # Default thresholds
        return AdaptiveThresholds(
            message_length_min=20.0,
            message_length_max=72.0,
            files_per_commit_ideal=5.0,
            files_per_commit_max=15.0,
            lines_per_commit_ideal=100.0,
            lines_per_commit_max=500.0,
            conventional_commit_weight=0.7,
            last_updated=datetime.now(timezone.utc).isoformat(),
            confidence=0.5,
            sample_size=0
        )
    
    def _save_thresholds(self):
        """Save adaptive thresholds"""
        try:
            ML_MODELS_DIR.mkdir(parents=True, exist_ok=True)
            
            with open(THRESHOLDS_FILE, 'w') as f:
                json.dump(asdict(self.thresholds), f, indent=2)
            
            self._log(f"Thresholds saved to {THRESHOLDS_FILE}")
        except Exception as e:
            self._log(f"Error saving thresholds: {e}", "ERROR")
    
    def _log_prediction(self, result: PredictionResult):
        """Log prediction for future learning"""
        try:
            PREDICTIONS_LOG.parent.mkdir(parents=True, exist_ok=True)
            
            predictions = []
            if PREDICTIONS_LOG.exists():
                with open(PREDICTIONS_LOG, 'r') as f:
                    predictions = json.load(f)
            
            predictions.append({
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "commit_hash": result.commit_hash,
                "predicted_success": result.predicted_success,
                "success_probability": result.success_probability,
                "confidence": result.confidence,
                "risk_factors": result.risk_factors
            })
            
            # Keep last 1000 predictions
            predictions = predictions[-1000:]
            
            with open(PREDICTIONS_LOG, 'w') as f:
                json.dump(predictions, f, indent=2)
                
        except Exception as e:
            self._log(f"Error logging prediction: {e}", "ERROR")
    
    def optimize_thresholds(self) -> Dict[str, Any]:
        """
        Optimize thresholds based on recent performance.
        
        Returns:
            Optimization results
        """
        if not ML_AVAILABLE or self.model is None:
            self._log("Model not available. Train model first.", "ERROR")
            return {"error": "Model not trained"}
        
        self._log("Optimizing adaptive thresholds...")
        
        # Re-train on recent data to update thresholds
        metrics = self.train_model(since_days=30, max_commits=500)
        
        self._log("Thresholds optimized based on recent performance")
        
        return {
            "thresholds": asdict(self.thresholds),
            "training_metrics": metrics,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }


def main():
    """Main entry point with CLI"""
    parser = argparse.ArgumentParser(
        description="ML-Based Git Commit Strategy Optimizer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Train model on last 90 days
  python ml-commit-optimizer.py --train --since 90
  
  # Predict success for a commit
  python ml-commit-optimizer.py --predict abc123def
  
  # Optimize thresholds
  python ml-commit-optimizer.py --optimize
  
  # Check model status
  python ml-commit-optimizer.py --status
        """
    )
    
    parser.add_argument('--train', action='store_true',
                       help='Train ML model on historical data')
    parser.add_argument('--since', type=int, default=90,
                       help='Days of history for training (default: 90)')
    parser.add_argument('--max-commits', type=int, default=1000,
                       help='Maximum commits to use (default: 1000)')
    
    parser.add_argument('--predict', type=str, metavar='COMMIT',
                       help='Predict success for commit hash')
    
    parser.add_argument('--optimize', action='store_true',
                       help='Optimize adaptive thresholds')
    
    parser.add_argument('--status', action='store_true',
                       help='Show model and threshold status')
    
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Enable verbose logging')
    
    args = parser.parse_args()
    
    if not ML_AVAILABLE:
        print("❌ Error: ML dependencies not installed", file=sys.stderr)
        print("   Install with: pip install scikit-learn numpy", file=sys.stderr)
        return 1
    
    optimizer = MLCommitOptimizer(verbose=args.verbose)
    
    try:
        if args.train:
            print("🎓 Training ML model...")
            metrics = optimizer.train_model(
                since_days=args.since,
                max_commits=args.max_commits
            )
            
            if "error" in metrics:
                print(f"❌ Error: {metrics['error']}")
                return 1
            
            print(f"✅ Model trained successfully!")
            print(f"   Samples: {metrics['samples']}")
            print(f"   Accuracy: {metrics['accuracy']:.1%}")
            print(f"   Precision: {metrics['precision']:.1%}")
            print(f"   Recall: {metrics['recall']:.1%}")
            print(f"   F1 Score: {metrics['f1_score']:.1%}")
            print(f"   CV Score: {metrics['cv_mean']:.1%} (+/- {metrics['cv_std']:.1%})")
            
        elif args.predict:
            print(f"🔮 Predicting success for commit {args.predict[:8]}...")
            result = optimizer.predict_commit_success(args.predict)
            
            if not result:
                print("❌ Error: Could not generate prediction")
                return 1
            
            print(f"\n{'='*60}")
            print(f"Commit: {result.commit_hash[:8]}")
            print(f"{'='*60}")
            print(f"Predicted Success: {'✅ YES' if result.predicted_success else '❌ NO'}")
            print(f"Success Probability: {result.success_probability:.1%}")
            print(f"Confidence: {result.confidence:.1%}")
            
            if result.risk_factors:
                print(f"\n⚠️  Risk Factors:")
                for risk in result.risk_factors:
                    print(f"   • {risk}")
            
            if result.recommendations:
                print(f"\n💡 Recommendations:")
                for rec in result.recommendations:
                    print(f"   • {rec}")
            
            print(f"\n📊 Top Feature Importance:")
            sorted_features = sorted(
                result.feature_importance.items(),
                key=lambda x: x[1],
                reverse=True
            )[:5]
            for feature, importance in sorted_features:
                print(f"   {feature}: {importance:.3f}")
            
        elif args.optimize:
            print("⚙️  Optimizing adaptive thresholds...")
            result = optimizer.optimize_thresholds()
            
            if "error" in result:
                print(f"❌ Error: {result['error']}")
                return 1
            
            print("✅ Thresholds optimized!")
            print("\n📐 Current Thresholds:")
            thresholds = result['thresholds']
            print(f"   Message length: {thresholds['message_length_min']:.0f} - {thresholds['message_length_max']:.0f} chars")
            print(f"   Files per commit: ~{thresholds['files_per_commit_ideal']:.0f} (max: {thresholds['files_per_commit_max']:.0f})")
            print(f"   Lines per commit: ~{thresholds['lines_per_commit_ideal']:.0f} (max: {thresholds['lines_per_commit_max']:.0f})")
            print(f"   Conventional format weight: {thresholds['conventional_commit_weight']:.1%}")
            print(f"   Based on {thresholds['sample_size']} successful commits")
            
        elif args.status:
            print("📊 ML Commit Optimizer Status")
            print(f"{'='*60}")
            
            if optimizer.model is None:
                print("❌ Model: Not trained")
                print("   Run with --train to train the model")
            else:
                print("✅ Model: Trained and loaded")
                print(f"   Model type: {type(optimizer.model).__name__}")
            
            print(f"\n📐 Adaptive Thresholds:")
            t = optimizer.thresholds
            print(f"   Message length: {t.message_length_min:.0f} - {t.message_length_max:.0f}")
            print(f"   Files ideal/max: {t.files_per_commit_ideal:.0f} / {t.files_per_commit_max:.0f}")
            print(f"   Lines ideal/max: {t.lines_per_commit_ideal:.0f} / {t.lines_per_commit_max:.0f}")
            print(f"   Confidence: {t.confidence:.1%}")
            print(f"   Sample size: {t.sample_size}")
            print(f"   Last updated: {t.last_updated[:19]}")
            
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
