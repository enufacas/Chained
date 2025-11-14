#!/usr/bin/env python3
"""
Archaeology Learner for Active Learning from Git History

This tool learns from repository history to identify patterns, predict outcomes,
and provide proactive recommendations.
"""

import os
import sys
import json
import re
import subprocess
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict, Counter
import statistics


class ArchaeologyLearner:
    """Learns from git history to identify patterns and make predictions"""
    
    def __init__(self, repo_path: str = ".", patterns_file: str = "analysis/archaeology-patterns.json"):
        self.repo_path = repo_path
        self.patterns_file = patterns_file
        self.patterns_data = self._load_patterns()
        
    def _load_patterns(self) -> Dict:
        """Load existing patterns database"""
        if os.path.exists(self.patterns_file):
            with open(self.patterns_file, 'r') as f:
                return json.load(f)
        return self._initialize_patterns()
    
    def _initialize_patterns(self) -> Dict:
        """Initialize patterns database"""
        return {
            "version": "1.0",
            "last_updated": None,
            "patterns": {
                "success": [],
                "failure": [],
                "evolution": []
            },
            "insights": [],
            "recommendations": [],
            "statistics": {
                "total_patterns": 0,
                "prediction_accuracy": 0.0,
                "recommendations_generated": 0,
                "predictions_made": 0,
                "predictions_validated": 0
            },
            "knowledge_base": {
                "best_practices": [],
                "common_pitfalls": [],
                "success_examples": [],
                "failure_examples": []
            },
            "timeline_data": {
                "feature_completion_times": [],
                "refactor_completion_times": [],
                "bugfix_completion_times": []
            }
        }
    
    def _save_patterns(self):
        """Save patterns database"""
        self.patterns_data["last_updated"] = datetime.now(timezone.utc).isoformat()
        
        # Ensure all expected keys exist
        if "statistics" not in self.patterns_data:
            self.patterns_data["statistics"] = {}
        
        # Merge with default statistics to ensure all keys exist
        default_stats = {
            "total_patterns": 0,
            "prediction_accuracy": 0.0,
            "recommendations_generated": 0,
            "predictions_made": 0,
            "predictions_validated": 0
        }
        for key, default_value in default_stats.items():
            if key not in self.patterns_data["statistics"]:
                self.patterns_data["statistics"][key] = default_value
        
        os.makedirs(os.path.dirname(self.patterns_file), exist_ok=True)
        with open(self.patterns_file, 'w') as f:
            json.dump(self.patterns_data, f, indent=2)
    
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
            
            files_changed = self._run_git_command([
                'diff-tree', '--no-commit-id', '--name-only', '-r', commit_hash
            ])
            
            if files_changed:
                commit_data["files_changed"] = files_changed.split('\n')
            
            stats = self._run_git_command([
                'show', '--format=', '--shortstat', commit_hash
            ])
            commit_data["stats"] = stats
            
            return commit_data
            
        except Exception as e:
            print(f"Error parsing commit {commit_hash}: {e}", file=sys.stderr)
            return None
    
    def _get_commit_parent(self, commit_hash: str) -> Optional[str]:
        """Get parent commit hash"""
        result = self._run_git_command(['rev-parse', f'{commit_hash}^'])
        return result if result else None
    
    def _get_commits_after(self, commit_hash: str, max_commits: int = 10) -> List[str]:
        """Get commits that came after the given commit"""
        result = self._run_git_command([
            'log', '--format=%H', f'{commit_hash}..HEAD', f'-{max_commits}'
        ])
        return result.split('\n') if result else []
    
    def _analyze_commit_outcome(self, commit: Dict, follow_up_commits: List[Dict]) -> Dict:
        """Analyze the outcome of a commit based on follow-up commits"""
        outcome = {
            "success": True,
            "fixes_needed": [],
            "improvements_made": [],
            "issues_introduced": []
        }
        
        # Check if follow-up commits fixed issues from this commit
        for follow_up in follow_up_commits:
            subject_lower = follow_up["subject"].lower()
            body_lower = follow_up["body"].lower()
            
            # Check for fixes related to original commit
            if any(keyword in subject_lower or keyword in body_lower 
                   for keyword in ['fix', 'bug', 'error', 'issue', 'problem', 'revert']):
                
                # Check if it mentions the same files
                common_files = set(commit["files_changed"]) & set(follow_up["files_changed"])
                if common_files:
                    outcome["success"] = False
                    outcome["fixes_needed"].append({
                        "commit": follow_up["hash"][:7],
                        "subject": follow_up["subject"],
                        "files": list(common_files)
                    })
            
            # Check for improvements
            if any(keyword in subject_lower for keyword in ['improve', 'enhance', 'optimize']):
                common_files = set(commit["files_changed"]) & set(follow_up["files_changed"])
                if common_files:
                    outcome["improvements_made"].append({
                        "commit": follow_up["hash"][:7],
                        "subject": follow_up["subject"]
                    })
        
        return outcome
    
    def learn_success_patterns(self, max_commits: int = 200) -> List[Dict]:
        """Learn patterns from successful commits"""
        print("Learning success patterns...")
        
        commit_hashes = self._run_git_command(['log', '--format=%H', f'-{max_commits}'])
        if not commit_hashes:
            return []
        
        commits = commit_hashes.split('\n')
        success_patterns = []
        
        # Analyze each commit and its outcome
        for i, commit_hash in enumerate(commits[:-10]):  # Leave some for follow-up analysis
            if i % 20 == 0:
                print(f"Analyzing commit {i+1}/{len(commits)-10}...")
            
            commit = self._parse_commit(commit_hash)
            if not commit:
                continue
            
            # Get follow-up commits to analyze outcome
            follow_up_hashes = commits[i+1:min(i+11, len(commits))]
            follow_up_commits = [self._parse_commit(h) for h in follow_up_hashes]
            follow_up_commits = [c for c in follow_up_commits if c]
            
            outcome = self._analyze_commit_outcome(commit, follow_up_commits)
            
            # If successful commit, extract pattern
            if outcome["success"] and not outcome["fixes_needed"]:
                pattern = self._extract_pattern(commit, outcome, "success")
                if pattern:
                    success_patterns.append(pattern)
        
        return success_patterns
    
    def learn_failure_patterns(self, max_commits: int = 200) -> List[Dict]:
        """Learn patterns from failed commits that needed fixes"""
        print("Learning failure patterns...")
        
        commit_hashes = self._run_git_command(['log', '--format=%H', f'-{max_commits}'])
        if not commit_hashes:
            return []
        
        commits = commit_hashes.split('\n')
        failure_patterns = []
        
        for i, commit_hash in enumerate(commits[:-10]):
            if i % 20 == 0:
                print(f"Analyzing commit {i+1}/{len(commits)-10}...")
            
            commit = self._parse_commit(commit_hash)
            if not commit:
                continue
            
            follow_up_hashes = commits[i+1:min(i+11, len(commits))]
            follow_up_commits = [self._parse_commit(h) for h in follow_up_hashes]
            follow_up_commits = [c for c in follow_up_commits if c]
            
            outcome = self._analyze_commit_outcome(commit, follow_up_commits)
            
            # If failed commit, extract pattern
            if not outcome["success"] and outcome["fixes_needed"]:
                pattern = self._extract_pattern(commit, outcome, "failure")
                if pattern:
                    failure_patterns.append(pattern)
        
        return failure_patterns
    
    def learn_evolution_patterns(self, max_commits: int = 500) -> List[Dict]:
        """Learn how code evolves over time"""
        print("Learning evolution patterns...")
        
        commit_hashes = self._run_git_command(['log', '--format=%H', f'-{max_commits}'])
        if not commit_hashes:
            return []
        
        commits = commit_hashes.split('\n')
        evolution_patterns = []
        
        # Track file evolution
        file_history = defaultdict(list)
        
        for i, commit_hash in enumerate(commits):
            if i % 50 == 0:
                print(f"Analyzing commit {i+1}/{len(commits)}...")
            
            commit = self._parse_commit(commit_hash)
            if not commit:
                continue
            
            # Track each file's changes
            for file in commit["files_changed"]:
                file_history[file].append({
                    "commit": commit["hash"][:7],
                    "timestamp": commit["timestamp"],
                    "subject": commit["subject"]
                })
        
        # Analyze file evolution patterns
        for file, history in file_history.items():
            if len(history) >= 3:  # Only files with multiple changes
                pattern = {
                    "pattern_type": "file_evolution",
                    "file": file,
                    "changes_count": len(history),
                    "first_seen": history[-1]["timestamp"],
                    "last_seen": history[0]["timestamp"],
                    "change_frequency": self._calculate_change_frequency(history),
                    "common_change_types": self._analyze_change_types(history)
                }
                evolution_patterns.append(pattern)
        
        return evolution_patterns
    
    def _extract_pattern(self, commit: Dict, outcome: Dict, pattern_type: str) -> Optional[Dict]:
        """Extract a learnable pattern from a commit"""
        pattern = {
            "pattern_type": pattern_type,
            "commit_hash": commit["hash"][:7],
            "timestamp": commit["timestamp"],
            "subject": commit["subject"],
            "files_changed": len(commit["files_changed"]),
            "file_types": list(set([Path(f).suffix for f in commit["files_changed"] if Path(f).suffix])),
            "outcome": outcome,
            "characteristics": {}
        }
        
        # Extract commit characteristics
        subject_lower = commit["subject"].lower()
        body_lower = commit["body"].lower()
        
        # Check for various indicators
        pattern["characteristics"]["is_refactor"] = any(
            kw in subject_lower for kw in ['refactor', 'restructure', 'reorganize']
        )
        pattern["characteristics"]["is_feature"] = any(
            kw in subject_lower for kw in ['add', 'implement', 'create', 'new feature']
        )
        pattern["characteristics"]["is_bug_fix"] = any(
            kw in subject_lower for kw in ['fix', 'bug', 'issue']
        )
        pattern["characteristics"]["has_tests"] = any(
            'test' in f.lower() for f in commit["files_changed"]
        )
        pattern["characteristics"]["large_change"] = len(commit["files_changed"]) > 5
        pattern["characteristics"]["has_documentation"] = 'why' in body_lower or 'because' in body_lower
        
        return pattern
    
    def _calculate_change_frequency(self, history: List[Dict]) -> str:
        """Calculate how frequently a file changes"""
        if len(history) < 2:
            return "rare"
        
        timestamps = [datetime.fromisoformat(h["timestamp"]) for h in history]
        timestamps.sort()
        
        time_diffs = [(timestamps[i+1] - timestamps[i]).days for i in range(len(timestamps)-1)]
        avg_days = statistics.mean(time_diffs) if time_diffs else 999
        
        if avg_days < 7:
            return "very_frequent"
        elif avg_days < 30:
            return "frequent"
        elif avg_days < 90:
            return "moderate"
        else:
            return "rare"
    
    def _analyze_change_types(self, history: List[Dict]) -> List[str]:
        """Analyze types of changes made to a file"""
        change_types = []
        
        for change in history:
            subject = change["subject"].lower()
            if any(kw in subject for kw in ['fix', 'bug']):
                change_types.append("bug_fix")
            elif any(kw in subject for kw in ['add', 'implement']):
                change_types.append("feature")
            elif any(kw in subject for kw in ['refactor', 'improve']):
                change_types.append("refactor")
            else:
                change_types.append("maintenance")
        
        # Return most common types
        counter = Counter(change_types)
        return [ct for ct, _ in counter.most_common(3)]
    
    def generate_insights(self, patterns: Dict) -> List[Dict]:
        """Generate insights from learned patterns"""
        insights = []
        
        success_patterns = patterns.get("success", [])
        failure_patterns = patterns.get("failure", [])
        evolution_patterns = patterns.get("evolution", [])
        
        # Insight 1: Success rate by commit type
        if success_patterns:
            refactor_success = sum(1 for p in success_patterns if p["characteristics"].get("is_refactor"))
            feature_success = sum(1 for p in success_patterns if p["characteristics"].get("is_feature"))
            
            insights.append({
                "type": "success_rate",
                "title": "Refactorings have high success rate",
                "description": f"Found {refactor_success} successful refactorings",
                "confidence": "high" if refactor_success > 10 else "medium",
                "actionable": True
            })
        
        # Insight 2: Testing correlation
        patterns_with_tests = [p for p in success_patterns if p["characteristics"].get("has_tests")]
        patterns_without_tests = [p for p in failure_patterns if not p["characteristics"].get("has_tests")]
        
        if patterns_with_tests or patterns_without_tests:
            insights.append({
                "type": "testing_importance",
                "title": "Tests correlate with success",
                "description": f"Commits with tests: {len(patterns_with_tests)} successes. Without tests: {len(patterns_without_tests)} failures",
                "confidence": "high",
                "actionable": True
            })
        
        # Insight 3: File change frequency
        if evolution_patterns:
            frequent_files = [p for p in evolution_patterns if p.get("change_frequency") in ["very_frequent", "frequent"]]
            if frequent_files:
                insights.append({
                    "type": "high_churn",
                    "title": "High churn files need attention",
                    "description": f"Found {len(frequent_files)} files with frequent changes",
                    "files": [p["file"] for p in frequent_files[:5]],
                    "confidence": "high",
                    "actionable": True
                })
        
        # Insight 4: Large change risk
        large_failures = [p for p in failure_patterns if p["characteristics"].get("large_change")]
        if large_failures:
            insights.append({
                "type": "change_size_risk",
                "title": "Large changes have higher failure rate",
                "description": f"Found {len(large_failures)} large changes that needed fixes",
                "recommendation": "Break large changes into smaller incremental commits",
                "confidence": "medium",
                "actionable": True
            })
        
        return insights
    
    def generate_recommendations(self, insights: List[Dict]) -> List[Dict]:
        """Generate actionable recommendations from insights"""
        recommendations = []
        
        for insight in insights:
            if not insight.get("actionable"):
                continue
            
            if insight["type"] == "success_rate":
                recommendations.append({
                    "priority": "medium",
                    "title": "Continue with incremental refactoring",
                    "description": "Historical data shows refactorings succeed frequently",
                    "action": "Schedule regular refactoring sessions",
                    "based_on": insight["title"]
                })
            
            elif insight["type"] == "testing_importance":
                recommendations.append({
                    "priority": "high",
                    "title": "Require tests for all changes",
                    "description": "Commits with tests have significantly higher success rates",
                    "action": "Add test coverage checks to CI/CD",
                    "based_on": insight["title"]
                })
            
            elif insight["type"] == "high_churn":
                recommendations.append({
                    "priority": "high",
                    "title": "Review high-churn files",
                    "description": f"Files that change frequently may need refactoring: {', '.join(insight.get('files', [])[:3])}",
                    "action": "Create issues for stabilizing high-churn files",
                    "based_on": insight["title"]
                })
            
            elif insight["type"] == "change_size_risk":
                recommendations.append({
                    "priority": "medium",
                    "title": "Break down large changes",
                    "description": "Large commits have higher failure rates",
                    "action": "Use feature flags for incremental delivery",
                    "based_on": insight["title"]
                })
        
        return recommendations
    
    def predict_outcome(self, commit_characteristics: Dict) -> Dict:
        """Predict the outcome of a commit based on learned patterns"""
        # Load existing patterns
        patterns = self.patterns_data.get("patterns", {})
        success_patterns = patterns.get("success", [])
        failure_patterns = patterns.get("failure", [])
        
        if not success_patterns and not failure_patterns:
            return {
                "prediction": "unknown",
                "confidence": 0.0,
                "reasoning": "Insufficient historical data"
            }
        
        # Calculate similarity scores
        success_score = self._calculate_similarity(commit_characteristics, success_patterns)
        failure_score = self._calculate_similarity(commit_characteristics, failure_patterns)
        
        total_score = success_score + failure_score
        if total_score == 0:
            return {
                "prediction": "unknown",
                "confidence": 0.0,
                "reasoning": "No similar patterns found"
            }
        
        success_probability = success_score / total_score
        
        if success_probability > 0.7:
            prediction = "success"
            confidence = success_probability
        elif success_probability < 0.3:
            prediction = "likely_needs_fixes"
            confidence = 1 - success_probability
        else:
            prediction = "uncertain"
            confidence = 0.5
        
        return {
            "prediction": prediction,
            "confidence": confidence,
            "success_probability": success_probability,
            "reasoning": f"Based on {len(success_patterns)} success and {len(failure_patterns)} failure patterns"
        }
    
    def _calculate_similarity(self, characteristics: Dict, patterns: List[Dict]) -> float:
        """Calculate similarity between characteristics and a set of patterns"""
        if not patterns:
            return 0.0
        
        similarity_scores = []
        
        for pattern in patterns:
            pattern_chars = pattern.get("characteristics", {})
            score = 0
            total = 0
            
            for key in characteristics:
                if key in pattern_chars:
                    total += 1
                    if characteristics[key] == pattern_chars[key]:
                        score += 1
            
            if total > 0:
                similarity_scores.append(score / total)
        
        return sum(similarity_scores) if similarity_scores else 0.0
    
    def assess_risk(self, commit_characteristics: Dict, files_changed: List[str] = None) -> Dict:
        """Assess risk level of a proposed change based on historical patterns"""
        prediction = self.predict_outcome(commit_characteristics)
        
        risk_factors = []
        risk_score = 0.0
        
        # Factor 1: Prediction confidence
        if prediction["prediction"] == "likely_needs_fixes":
            risk_factors.append("Historical patterns suggest high likelihood of requiring fixes")
            risk_score += 0.3
        elif prediction["prediction"] == "uncertain":
            risk_factors.append("Uncertain outcome based on limited similar patterns")
            risk_score += 0.15
        
        # Factor 2: Large change risk
        if commit_characteristics.get("large_change", False):
            risk_factors.append("Large change increases complexity and failure risk")
            risk_score += 0.2
        
        # Factor 3: Missing tests
        if not commit_characteristics.get("has_tests", False):
            risk_factors.append("No tests detected - historical data shows correlation with failures")
            risk_score += 0.25
        
        # Factor 4: High churn files
        if files_changed:
            evolution_patterns = self.patterns_data.get("patterns", {}).get("evolution", [])
            high_churn_files = [
                p["file"] for p in evolution_patterns 
                if p.get("change_frequency") in ["very_frequent", "frequent"]
            ]
            affected_high_churn = [f for f in files_changed if f in high_churn_files]
            
            if affected_high_churn:
                risk_factors.append(f"Modifying high-churn files: {', '.join(affected_high_churn[:3])}")
                risk_score += 0.15 * min(len(affected_high_churn) / len(files_changed), 1.0)
        
        # Factor 5: Missing documentation
        if not commit_characteristics.get("has_documentation", False):
            risk_factors.append("No documentation of reasoning - may impact future maintainability")
            risk_score += 0.1
        
        # Normalize risk score
        risk_score = min(risk_score, 1.0)
        
        # Determine risk level
        if risk_score < 0.3:
            risk_level = "low"
        elif risk_score < 0.6:
            risk_level = "medium"
        else:
            risk_level = "high"
        
        return {
            "risk_level": risk_level,
            "risk_score": risk_score,
            "risk_factors": risk_factors,
            "success_probability": prediction.get("success_probability", 0.5),
            "recommendation": self._get_risk_mitigation_recommendation(risk_level, risk_factors)
        }
    
    def _get_risk_mitigation_recommendation(self, risk_level: str, risk_factors: List[str]) -> str:
        """Get recommendation for mitigating identified risks"""
        if risk_level == "low":
            return "Change appears safe based on historical patterns. Proceed with normal review process."
        elif risk_level == "medium":
            recommendations = []
            if any("test" in factor.lower() for factor in risk_factors):
                recommendations.append("Add comprehensive test coverage")
            if any("large change" in factor.lower() for factor in risk_factors):
                recommendations.append("Consider breaking into smaller incremental changes")
            if any("documentation" in factor.lower() for factor in risk_factors):
                recommendations.append("Document reasoning and design decisions")
            return "Moderate risk detected. " + ". ".join(recommendations)
        else:
            return "High risk change. Strongly recommend: thorough testing, incremental delivery, detailed documentation, and careful code review before merging."
    
    def estimate_timeline(self, change_type: str, files_count: int = 1) -> Dict:
        """Estimate completion timeline based on historical data"""
        timeline_data = self.patterns_data.get("timeline_data", {})
        
        # Determine which historical data to use
        if change_type == "feature":
            historical_times = timeline_data.get("feature_completion_times", [])
            category = "feature implementation"
        elif change_type == "refactor":
            historical_times = timeline_data.get("refactor_completion_times", [])
            category = "refactoring"
        elif change_type == "bugfix":
            historical_times = timeline_data.get("bugfix_completion_times", [])
            category = "bug fix"
        else:
            historical_times = []
            category = "general change"
        
        if not historical_times:
            return {
                "estimated_days": None,
                "confidence": "low",
                "reasoning": f"Insufficient historical data for {category}",
                "range": None
            }
        
        # Calculate statistics
        avg_days = statistics.mean(historical_times)
        
        # Adjust for file count (more files typically take longer)
        file_multiplier = 1.0 + (0.1 * max(0, files_count - 3))
        estimated_days = avg_days * file_multiplier
        
        # Calculate range
        if len(historical_times) > 1:
            stdev = statistics.stdev(historical_times)
            lower_bound = max(0.5, estimated_days - stdev)
            upper_bound = estimated_days + stdev
            range_str = f"{lower_bound:.1f}-{upper_bound:.1f} days"
        else:
            range_str = f"~{estimated_days:.1f} days (single data point)"
        
        confidence = "high" if len(historical_times) >= 10 else "medium" if len(historical_times) >= 3 else "low"
        
        return {
            "estimated_days": round(estimated_days, 1),
            "confidence": confidence,
            "reasoning": f"Based on {len(historical_times)} similar {category} tasks",
            "range": range_str,
            "sample_size": len(historical_times)
        }
    
    def find_similar_changes(self, characteristics: Dict, max_results: int = 5) -> List[Dict]:
        """Find similar historical changes that can serve as examples"""
        all_patterns = []
        patterns = self.patterns_data.get("patterns", {})
        
        # Collect all patterns with success indicator
        for pattern in patterns.get("success", []):
            pattern_copy = pattern.copy()
            pattern_copy["outcome_type"] = "success"
            all_patterns.append(pattern_copy)
        
        for pattern in patterns.get("failure", []):
            pattern_copy = pattern.copy()
            pattern_copy["outcome_type"] = "failure"
            all_patterns.append(pattern_copy)
        
        # Calculate similarity for each pattern
        scored_patterns = []
        for pattern in all_patterns:
            similarity = self._calculate_similarity_score(characteristics, pattern.get("characteristics", {}))
            if similarity > 0.3:  # Minimum threshold
                scored_patterns.append({
                    "pattern": pattern,
                    "similarity": similarity
                })
        
        # Sort by similarity and return top results
        scored_patterns.sort(key=lambda x: x["similarity"], reverse=True)
        
        results = []
        for item in scored_patterns[:max_results]:
            pattern = item["pattern"]
            results.append({
                "commit_hash": pattern.get("commit_hash", "unknown"),
                "subject": pattern.get("subject", ""),
                "outcome": pattern["outcome_type"],
                "similarity": item["similarity"],
                "characteristics": pattern.get("characteristics", {}),
                "lessons_learned": self._extract_lessons_learned(pattern)
            })
        
        return results
    
    def _calculate_similarity_score(self, chars1: Dict, chars2: Dict) -> float:
        """Calculate similarity score between two characteristic sets"""
        if not chars1 or not chars2:
            return 0.0
        
        matching = 0
        total = len(set(chars1.keys()) | set(chars2.keys()))
        
        for key in chars1:
            if key in chars2 and chars1[key] == chars2[key]:
                matching += 1
        
        return matching / total if total > 0 else 0.0
    
    def _extract_lessons_learned(self, pattern: Dict) -> List[str]:
        """Extract lessons learned from a pattern"""
        lessons = []
        outcome = pattern.get("outcome", {})
        chars = pattern.get("characteristics", {})
        
        if pattern.get("outcome_type") == "success":
            if chars.get("has_tests"):
                lessons.append("Included comprehensive tests")
            if chars.get("has_documentation"):
                lessons.append("Well-documented reasoning")
            if not chars.get("large_change"):
                lessons.append("Kept changes small and focused")
        else:  # failure
            fixes_needed = outcome.get("fixes_needed", [])
            if fixes_needed:
                lessons.append(f"Required {len(fixes_needed)} follow-up fixes")
            if not chars.get("has_tests"):
                lessons.append("Lacked sufficient test coverage")
            if chars.get("large_change"):
                lessons.append("Change was too large - should have been incremental")
        
        return lessons if lessons else ["No specific lessons extracted"]
    
    def analyze_and_learn(self, max_commits: int = 200) -> Dict:
        """Main method to analyze repository and learn patterns"""
        print("Starting archaeology learning process...")
        print("=" * 60)
        
        # Learn patterns
        success_patterns = self.learn_success_patterns(max_commits)
        failure_patterns = self.learn_failure_patterns(max_commits)
        evolution_patterns = self.learn_evolution_patterns(max_commits)
        
        # Store patterns
        self.patterns_data["patterns"]["success"] = success_patterns
        self.patterns_data["patterns"]["failure"] = failure_patterns
        self.patterns_data["patterns"]["evolution"] = evolution_patterns
        
        # Extract timeline data from patterns
        self._extract_timeline_data(success_patterns + failure_patterns)
        
        # Build knowledge base
        self._build_knowledge_base(success_patterns, failure_patterns)
        
        # Generate insights
        insights = self.generate_insights(self.patterns_data["patterns"])
        self.patterns_data["insights"] = insights
        
        # Generate recommendations
        recommendations = self.generate_recommendations(insights)
        self.patterns_data["recommendations"] = recommendations
        
        # Update statistics
        self.patterns_data["statistics"]["total_patterns"] = (
            len(success_patterns) + len(failure_patterns) + len(evolution_patterns)
        )
        self.patterns_data["statistics"]["recommendations_generated"] = len(recommendations)
        
        # Save patterns
        self._save_patterns()
        
        result = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "patterns_learned": {
                "success": len(success_patterns),
                "failure": len(failure_patterns),
                "evolution": len(evolution_patterns)
            },
            "insights_generated": len(insights),
            "recommendations_generated": len(recommendations),
            "knowledge_base_entries": len(self.patterns_data["knowledge_base"]["best_practices"]),
            "patterns_file": self.patterns_file
        }
        
        print("\n" + "=" * 60)
        print("Learning complete!")
        print(f"Success patterns: {len(success_patterns)}")
        print(f"Failure patterns: {len(failure_patterns)}")
        print(f"Evolution patterns: {len(evolution_patterns)}")
        print(f"Insights generated: {len(insights)}")
        print(f"Recommendations generated: {len(recommendations)}")
        print(f"Knowledge base entries: {result['knowledge_base_entries']}")
        
        return result
    
    def _extract_timeline_data(self, patterns: List[Dict]):
        """Extract completion timeline data from patterns"""
        timeline_data = {
            "feature_completion_times": [],
            "refactor_completion_times": [],
            "bugfix_completion_times": []
        }
        
        for pattern in patterns:
            chars = pattern.get("characteristics", {})
            
            # Estimate time based on pattern (simplified - in real scenario would track actual times)
            # This is a heuristic based on file count and change characteristics
            files_changed = pattern.get("files_changed", 1)
            
            # Base time estimates (in days)
            if chars.get("is_feature"):
                # Features typically take longer
                base_time = 2.0
                estimated_time = base_time + (files_changed * 0.5)
                timeline_data["feature_completion_times"].append(min(estimated_time, 10.0))
            
            elif chars.get("is_refactor"):
                # Refactors vary based on size
                base_time = 1.5
                estimated_time = base_time + (files_changed * 0.3)
                timeline_data["refactor_completion_times"].append(min(estimated_time, 7.0))
            
            elif chars.get("is_bug_fix"):
                # Bug fixes are typically faster
                base_time = 0.5
                estimated_time = base_time + (files_changed * 0.2)
                timeline_data["bugfix_completion_times"].append(min(estimated_time, 3.0))
        
        self.patterns_data["timeline_data"] = timeline_data
    
    def _build_knowledge_base(self, success_patterns: List[Dict], failure_patterns: List[Dict]):
        """Build searchable knowledge base from patterns"""
        knowledge_base = {
            "best_practices": [],
            "common_pitfalls": [],
            "success_examples": [],
            "failure_examples": []
        }
        
        # Extract best practices from success patterns
        best_practices_set = set()
        
        for pattern in success_patterns:
            chars = pattern.get("characteristics", {})
            
            if chars.get("has_tests"):
                best_practices_set.add("Include comprehensive test coverage")
            
            if chars.get("has_documentation"):
                best_practices_set.add("Document reasoning and design decisions")
            
            if not chars.get("large_change"):
                best_practices_set.add("Keep changes small and incremental")
            
            if chars.get("is_refactor") and chars.get("has_tests"):
                best_practices_set.add("Always test refactorings to prevent regressions")
        
        knowledge_base["best_practices"] = [
            {"practice": practice, "evidence_count": sum(1 for p in success_patterns)} 
            for practice in best_practices_set
        ]
        
        # Extract common pitfalls from failure patterns
        pitfalls_set = set()
        
        for pattern in failure_patterns:
            chars = pattern.get("characteristics", {})
            outcome = pattern.get("outcome", {})
            
            if not chars.get("has_tests"):
                pitfalls_set.add("Skipping tests leads to bugs and rework")
            
            if chars.get("large_change"):
                pitfalls_set.add("Large changes are harder to review and more likely to introduce bugs")
            
            if len(outcome.get("fixes_needed", [])) > 1:
                pitfalls_set.add("Multiple follow-up fixes indicate insufficient initial testing")
        
        knowledge_base["common_pitfalls"] = [
            {"pitfall": pitfall, "occurrences": sum(1 for p in failure_patterns)}
            for pitfall in pitfalls_set
        ]
        
        # Store representative examples
        knowledge_base["success_examples"] = [
            {
                "commit": p.get("commit_hash"),
                "subject": p.get("subject"),
                "characteristics": p.get("characteristics"),
                "key_factors": self._identify_success_factors(p)
            }
            for p in success_patterns[:5]  # Top 5 examples
        ]
        
        knowledge_base["failure_examples"] = [
            {
                "commit": p.get("commit_hash"),
                "subject": p.get("subject"),
                "characteristics": p.get("characteristics"),
                "issues": [fix.get("subject") for fix in p.get("outcome", {}).get("fixes_needed", [])]
            }
            for p in failure_patterns[:5]  # Top 5 examples
        ]
        
        self.patterns_data["knowledge_base"] = knowledge_base
    
    def _identify_success_factors(self, pattern: Dict) -> List[str]:
        """Identify key factors contributing to success"""
        factors = []
        chars = pattern.get("characteristics", {})
        
        if chars.get("has_tests"):
            factors.append("Comprehensive testing")
        if chars.get("has_documentation"):
            factors.append("Well-documented")
        if not chars.get("large_change"):
            factors.append("Focused scope")
        if chars.get("is_refactor"):
            factors.append("Systematic refactoring")
        
        return factors if factors else ["Standard practices followed"]
    
    def search_knowledge_base(self, query: str, category: str = "all") -> List[Dict]:
        """Search knowledge base for relevant information"""
        results = []
        kb = self.patterns_data.get("knowledge_base", {})
        
        query_lower = query.lower()
        
        if category in ["all", "best_practices"]:
            for practice in kb.get("best_practices", []):
                if query_lower in practice["practice"].lower():
                    results.append({
                        "type": "best_practice",
                        "content": practice["practice"],
                        "evidence": practice["evidence_count"]
                    })
        
        if category in ["all", "common_pitfalls"]:
            for pitfall in kb.get("common_pitfalls", []):
                if query_lower in pitfall["pitfall"].lower():
                    results.append({
                        "type": "common_pitfall",
                        "content": pitfall["pitfall"],
                        "occurrences": pitfall["occurrences"]
                    })
        
        if category in ["all", "examples"]:
            for example in kb.get("success_examples", []):
                if query_lower in example["subject"].lower():
                    results.append({
                        "type": "success_example",
                        "commit": example["commit"],
                        "subject": example["subject"],
                        "key_factors": example["key_factors"]
                    })
            
            for example in kb.get("failure_examples", []):
                if query_lower in example["subject"].lower():
                    results.append({
                        "type": "failure_example",
                        "commit": example["commit"],
                        "subject": example["subject"],
                        "issues": example["issues"]
                    })
        
        return results
    
    def generate_report(self) -> str:
        """Generate human-readable report of learned patterns"""
        report = []
        report.append("# 🧠 Archaeology Learning Report")
        report.append(f"\n**Generated:** {datetime.now(timezone.utc).isoformat()}")
        report.append(f"**Last Updated:** {self.patterns_data.get('last_updated', 'Never')}")
        
        # Statistics
        stats = self.patterns_data.get("statistics", {})
        report.append(f"\n## 📊 Statistics")
        report.append(f"- Total patterns learned: {stats.get('total_patterns', 0)}")
        report.append(f"- Recommendations generated: {stats.get('recommendations_generated', 0)}")
        report.append(f"- Predictions made: {stats.get('predictions_made', 0)}")
        if stats.get('predictions_validated', 0) > 0:
            accuracy = stats.get('prediction_accuracy', 0.0)
            report.append(f"- Prediction accuracy: {accuracy:.1%}")
        
        # Patterns summary
        patterns = self.patterns_data.get("patterns", {})
        report.append(f"\n## 🔍 Learned Patterns")
        report.append(f"- ✅ Success patterns: {len(patterns.get('success', []))}")
        report.append(f"- ❌ Failure patterns: {len(patterns.get('failure', []))}")
        report.append(f"- 📈 Evolution patterns: {len(patterns.get('evolution', []))}")
        
        # Knowledge Base Summary
        kb = self.patterns_data.get("knowledge_base", {})
        report.append(f"\n## 📚 Knowledge Base")
        report.append(f"- Best practices: {len(kb.get('best_practices', []))}")
        report.append(f"- Common pitfalls: {len(kb.get('common_pitfalls', []))}")
        report.append(f"- Success examples: {len(kb.get('success_examples', []))}")
        report.append(f"- Failure examples: {len(kb.get('failure_examples', []))}")
        
        # Best Practices
        if kb.get("best_practices"):
            report.append(f"\n### 🌟 Top Best Practices")
            for i, practice in enumerate(kb["best_practices"][:5], 1):
                report.append(f"{i}. {practice['practice']}")
                report.append(f"   - Evidence from {practice['evidence_count']} successful changes")
        
        # Common Pitfalls
        if kb.get("common_pitfalls"):
            report.append(f"\n### ⚠️ Common Pitfalls to Avoid")
            for i, pitfall in enumerate(kb["common_pitfalls"][:5], 1):
                report.append(f"{i}. {pitfall['pitfall']}")
                report.append(f"   - Occurred in {pitfall['occurrences']} failed changes")
        
        # Timeline Data
        timeline = self.patterns_data.get("timeline_data", {})
        if any(timeline.values()):
            report.append(f"\n## ⏱️ Timeline Estimates")
            
            if timeline.get("feature_completion_times"):
                avg_feature = statistics.mean(timeline["feature_completion_times"])
                report.append(f"- Feature implementation: ~{avg_feature:.1f} days (based on {len(timeline['feature_completion_times'])} examples)")
            
            if timeline.get("refactor_completion_times"):
                avg_refactor = statistics.mean(timeline["refactor_completion_times"])
                report.append(f"- Refactoring: ~{avg_refactor:.1f} days (based on {len(timeline['refactor_completion_times'])} examples)")
            
            if timeline.get("bugfix_completion_times"):
                avg_bugfix = statistics.mean(timeline["bugfix_completion_times"])
                report.append(f"- Bug fixes: ~{avg_bugfix:.1f} days (based on {len(timeline['bugfix_completion_times'])} examples)")
        
        # Insights
        insights = self.patterns_data.get("insights", [])
        if insights:
            report.append(f"\n## 💡 Key Insights")
            for i, insight in enumerate(insights, 1):
                report.append(f"\n### {i}. {insight['title']}")
                report.append(f"**Type:** {insight['type']}")
                report.append(f"**Confidence:** {insight['confidence']}")
                report.append(f"**Description:** {insight['description']}")
                if 'recommendation' in insight:
                    report.append(f"**Recommendation:** {insight['recommendation']}")
        
        # Recommendations
        recommendations = self.patterns_data.get("recommendations", [])
        if recommendations:
            report.append(f"\n## 🎯 Proactive Recommendations")
            for i, rec in enumerate(recommendations, 1):
                report.append(f"\n### {i}. {rec['title']} [{rec['priority'].upper()}]")
                report.append(f"**Description:** {rec['description']}")
                report.append(f"**Action:** {rec['action']}")
                report.append(f"**Based on:** {rec['based_on']}")
        
        # Predictive Capabilities
        report.append(f"\n## 🔮 Predictive Capabilities")
        report.append("\nThis learning system can now:")
        report.append("- **Assess Risk**: Evaluate proposed changes against historical patterns")
        report.append("- **Estimate Timelines**: Predict completion time based on similar past work")
        report.append("- **Find Examples**: Locate similar historical changes for reference")
        report.append("- **Search Knowledge**: Query best practices and common pitfalls")
        
        # Usage Examples
        report.append(f"\n## 🛠️ Usage Examples")
        report.append("\n### Risk Assessment")
        report.append("```python")
        report.append("risk = learner.assess_risk({")
        report.append("    'is_feature': True,")
        report.append("    'has_tests': False,")
        report.append("    'large_change': True")
        report.append("})")
        report.append("```")
        
        report.append("\n### Timeline Estimation")
        report.append("```python")
        report.append("timeline = learner.estimate_timeline('feature', files_count=5)")
        report.append("```")
        
        report.append("\n### Find Similar Changes")
        report.append("```python")
        report.append("similar = learner.find_similar_changes({")
        report.append("    'is_refactor': True,")
        report.append("    'has_tests': True")
        report.append("})")
        report.append("```")
        
        return '\n'.join(report)


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Archaeology Learner - Learn from git history to predict and recommend'
    )
    parser.add_argument(
        '-d', '--directory',
        default='.',
        help='Repository directory to analyze (default: current directory)'
    )
    parser.add_argument(
        '-n', '--max-commits',
        type=int,
        default=200,
        help='Maximum number of commits to analyze (default: 200)'
    )
    parser.add_argument(
        '-o', '--output',
        help='Output file for report (default: stdout)'
    )
    parser.add_argument(
        '--predict',
        action='store_true',
        help='Show prediction example based on learned patterns'
    )
    parser.add_argument(
        '--assess-risk',
        action='store_true',
        help='Show risk assessment example'
    )
    parser.add_argument(
        '--estimate-timeline',
        action='store_true',
        help='Show timeline estimation example'
    )
    parser.add_argument(
        '--search',
        type=str,
        help='Search knowledge base for a term'
    )
    parser.add_argument(
        '--find-similar',
        action='store_true',
        help='Find similar historical changes'
    )
    
    args = parser.parse_args()
    
    # Initialize learner
    learner = ArchaeologyLearner(repo_path=args.directory)
    
    # Analyze and learn
    print(f"🧠 Starting archaeology learning...\n")
    results = learner.analyze_and_learn(max_commits=args.max_commits)
    
    # Generate report
    report = learner.generate_report()
    
    # Write output
    if args.output:
        with open(args.output, 'w') as f:
            f.write(report)
        print(f"\n✅ Report saved to: {args.output}")
    else:
        print(f"\n{report}")
    
    print(f"\n📁 Patterns database saved to: {learner.patterns_file}")
    
    # Show prediction example if requested
    if args.predict:
        print("\n" + "=" * 60)
        print("Example Prediction")
        print("=" * 60)
        
        example_commit = {
            "is_refactor": True,
            "is_feature": False,
            "is_bug_fix": False,
            "has_tests": True,
            "large_change": False,
            "has_documentation": True
        }
        
        prediction = learner.predict_outcome(example_commit)
        print(f"\nCommit characteristics: {example_commit}")
        print(f"\nPrediction: {prediction['prediction']}")
        print(f"Confidence: {prediction['confidence']:.1%}")
        print(f"Success probability: {prediction.get('success_probability', 0):.1%}")
        print(f"Reasoning: {prediction['reasoning']}")
    
    # Show risk assessment example if requested
    if args.assess_risk:
        print("\n" + "=" * 60)
        print("Example Risk Assessment")
        print("=" * 60)
        
        example_commit = {
            "is_feature": True,
            "has_tests": False,
            "large_change": True,
            "has_documentation": False
        }
        
        risk = learner.assess_risk(example_commit)
        print(f"\nCommit characteristics: {example_commit}")
        print(f"\nRisk level: {risk['risk_level'].upper()}")
        print(f"Risk score: {risk['risk_score']:.1%}")
        print(f"Success probability: {risk['success_probability']:.1%}")
        print(f"\nRisk factors:")
        for factor in risk['risk_factors']:
            print(f"  - {factor}")
        print(f"\nRecommendation: {risk['recommendation']}")
    
    # Show timeline estimation example if requested
    if args.estimate_timeline:
        print("\n" + "=" * 60)
        print("Example Timeline Estimation")
        print("=" * 60)
        
        for change_type in ['feature', 'refactor', 'bugfix']:
            timeline = learner.estimate_timeline(change_type, files_count=5)
            print(f"\n{change_type.capitalize()}:")
            if timeline['estimated_days']:
                print(f"  Estimated time: {timeline['estimated_days']} days")
                print(f"  Range: {timeline['range']}")
                print(f"  Confidence: {timeline['confidence']}")
                print(f"  {timeline['reasoning']}")
            else:
                print(f"  {timeline['reasoning']}")
    
    # Search knowledge base if requested
    if args.search:
        print("\n" + "=" * 60)
        print(f"Knowledge Base Search: '{args.search}'")
        print("=" * 60)
        
        results = learner.search_knowledge_base(args.search)
        if results:
            for result in results:
                print(f"\n[{result['type'].upper()}]")
                print(f"  {result['content']}")
                if 'evidence' in result:
                    print(f"  Evidence: {result['evidence']} cases")
                if 'occurrences' in result:
                    print(f"  Occurrences: {result['occurrences']} cases")
        else:
            print("\nNo results found.")
    
    # Find similar changes if requested
    if args.find_similar:
        print("\n" + "=" * 60)
        print("Example: Find Similar Changes")
        print("=" * 60)
        
        example_chars = {
            "is_refactor": True,
            "has_tests": True,
            "large_change": False
        }
        
        similar = learner.find_similar_changes(example_chars, max_results=3)
        print(f"\nLooking for changes similar to: {example_chars}")
        print(f"\nFound {len(similar)} similar changes:")
        
        for i, change in enumerate(similar, 1):
            print(f"\n{i}. {change['commit']}: {change['subject']}")
            print(f"   Outcome: {change['outcome']}")
            print(f"   Similarity: {change['similarity']:.1%}")
            print(f"   Lessons learned:")
            for lesson in change['lessons_learned']:
                print(f"     - {lesson}")


if __name__ == '__main__':
    main()
