#!/usr/bin/env python3
"""
Enhanced Features for Autonomous Refactoring Agent
Part of the Chained autonomous AI ecosystem

This module provides advanced capabilities for the autonomous refactoring agent:
- Team-specific style preference learning
- Style conflict resolution
- Advanced pattern recognition and machine learning-based scoring
- Real-time feedback integration
- A/B testing for refactoring suggestions

Author: @create-guru
Inspired by: Nikola Tesla - inventive and visionary approach
"""

import os
import json
import re
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any, Optional, Set, Tuple
from collections import defaultdict, Counter
from dataclasses import dataclass, asdict, field
import statistics


@dataclass
class TeamMember:
    """Represents a team member and their style preferences."""
    username: str
    expertise_level: float  # 0.0 to 1.0, based on contribution history
    style_preferences: Dict[str, Any] = field(default_factory=dict)
    review_count: int = 0
    approval_rate: float = 0.0
    last_active: str = ""
    
    def get_weight(self) -> float:
        """Calculate the weight of this team member's preferences."""
        # Weight based on expertise and review count
        base_weight = self.expertise_level
        activity_boost = min(1.0, self.review_count / 50.0)
        approval_boost = self.approval_rate
        return base_weight * (0.5 + 0.3 * activity_boost + 0.2 * approval_boost)


@dataclass
class StyleConflict:
    """Represents a conflict between style preferences."""
    preference_type: str
    conflicting_values: List[Any]
    supporters: Dict[Any, List[str]]  # value -> list of supporters
    confidence_scores: Dict[Any, float]  # value -> average confidence
    resolution: Optional[Any] = None
    resolution_rationale: str = ""


class TeamStyleLearner:
    """
    Learns team-specific style preferences and tracks individual reviewer patterns.
    
    This class enables the agent to:
    - Track individual reviewer preferences
    - Weight preferences by team member expertise
    - Identify style champions (experts in specific areas)
    - Resolve conflicts between competing preferences
    """
    
    def __init__(self, team_data_file: str = "analysis/team_style_preferences.json"):
        self.team_data_file = team_data_file
        self.team_members = self._load_team_data()
    
    def _load_team_data(self) -> Dict[str, TeamMember]:
        """Load team member data from file."""
        if os.path.exists(self.team_data_file):
            with open(self.team_data_file, 'r') as f:
                data = json.load(f)
                return {
                    username: TeamMember(**member_data)
                    for username, member_data in data.items()
                }
        return {}
    
    def _save_team_data(self):
        """Save team member data to file."""
        os.makedirs(os.path.dirname(self.team_data_file), exist_ok=True)
        data = {
            username: asdict(member)
            for username, member in self.team_members.items()
        }
        with open(self.team_data_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def learn_from_review(self, reviewer: str, preference_type: str, 
                          value: Any, approved: bool):
        """
        Learn from a code review comment or approval.
        
        Args:
            reviewer: Username of the reviewer
            preference_type: Type of style preference (e.g., 'naming_convention')
            value: The preferred value
            approved: Whether the PR with this style was approved
        """
        timestamp = datetime.now(timezone.utc).isoformat()
        
        # Initialize team member if not exists
        if reviewer not in self.team_members:
            self.team_members[reviewer] = TeamMember(
                username=reviewer,
                expertise_level=0.5,  # Start with medium expertise
                review_count=0,
                approval_rate=0.5,
                last_active=timestamp
            )
        
        member = self.team_members[reviewer]
        member.review_count += 1
        member.last_active = timestamp
        
        # Update approval rate
        old_approvals = member.approval_rate * (member.review_count - 1)
        new_approvals = old_approvals + (1.0 if approved else 0.0)
        member.approval_rate = new_approvals / member.review_count
        
        # Update expertise level based on activity
        # More reviews = higher expertise (up to a point)
        member.expertise_level = min(1.0, 0.3 + (member.review_count / 100.0))
        
        # Track the style preference
        if preference_type not in member.style_preferences:
            member.style_preferences[preference_type] = {
                'value': value,
                'count': 1,
                'last_seen': timestamp
            }
        else:
            pref = member.style_preferences[preference_type]
            if pref['value'] == value:
                pref['count'] += 1
                pref['last_seen'] = timestamp
            else:
                # Reviewer changed preference - reset with lower confidence
                pref['value'] = value
                pref['count'] = 1
                pref['last_seen'] = timestamp
        
        self._save_team_data()
    
    def get_team_consensus(self, preference_type: str) -> Optional[Tuple[Any, float]]:
        """
        Get the team consensus for a specific preference type.
        
        Returns:
            Tuple of (consensus_value, confidence) or None if no consensus
        """
        if not self.team_members:
            return None
        
        # Collect weighted votes for each value
        votes: Dict[Any, float] = defaultdict(float)
        
        for member in self.team_members.values():
            if preference_type in member.style_preferences:
                pref = member.style_preferences[preference_type]
                value = pref['value']
                weight = member.get_weight()
                votes[value] += weight
        
        if not votes:
            return None
        
        # Find the value with the highest weighted vote
        consensus_value = max(votes.items(), key=lambda x: x[1])[0]
        total_weight = sum(votes.values())
        confidence = votes[consensus_value] / total_weight if total_weight > 0 else 0.0
        
        return consensus_value, confidence
    
    def identify_style_champions(self, top_n: int = 3) -> List[Tuple[str, float]]:
        """
        Identify team members who are style champions (experts).
        
        Returns:
            List of (username, expertise_score) tuples
        """
        if not self.team_members:
            return []
        
        # Calculate expertise score for each member
        scores = []
        for username, member in self.team_members.items():
            # Score based on review count, approval rate, and expertise level
            score = (
                member.review_count * 0.3 +
                member.approval_rate * 100 * 0.4 +
                member.expertise_level * 100 * 0.3
            )
            scores.append((username, score))
        
        # Sort by score descending and return top N
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:top_n]
    
    def get_team_summary(self) -> Dict[str, Any]:
        """Get a summary of team style preferences."""
        return {
            "total_members": len(self.team_members),
            "active_reviewers": sum(
                1 for m in self.team_members.values() 
                if m.review_count > 0
            ),
            "total_reviews": sum(
                m.review_count for m in self.team_members.values()
            ),
            "average_expertise": statistics.mean([
                m.expertise_level for m in self.team_members.values()
            ]) if self.team_members else 0.0,
            "style_champions": self.identify_style_champions(3)
        }


class StyleConflictResolver:
    """
    Resolves conflicts between competing style preferences.
    
    This class uses various strategies to resolve conflicts:
    - Weighted voting based on expertise
    - Temporal analysis (newer preferences may override old ones)
    - Success rate comparison
    - Context-aware resolution (different styles for different contexts)
    """
    
    def __init__(self, team_learner: TeamStyleLearner):
        self.team_learner = team_learner
    
    def detect_conflicts(self, preferences: Dict[str, Any]) -> List[StyleConflict]:
        """
        Detect conflicts in the preference set.
        
        Args:
            preferences: Dictionary of style preferences
            
        Returns:
            List of detected conflicts
        """
        conflicts = []
        
        # Group preferences by type
        by_type: Dict[str, List[Any]] = defaultdict(list)
        for key, pref in preferences.items():
            pref_type = pref.preference_type if hasattr(pref, 'preference_type') else key
            by_type[pref_type].append(pref)
        
        # Check for conflicts within each type
        for pref_type, prefs in by_type.items():
            if len(prefs) <= 1:
                continue
            
            # Check if all preferences have the same value
            values = [p.value if hasattr(p, 'value') else p for p in prefs]
            unique_values = list(set(str(v) for v in values))
            
            if len(unique_values) > 1:
                # Conflict detected!
                conflict = StyleConflict(
                    preference_type=pref_type,
                    conflicting_values=values,
                    supporters=defaultdict(list),
                    confidence_scores={}
                )
                
                # Collect supporter information
                for pref in prefs:
                    value = pref.value if hasattr(pref, 'value') else pref
                    sources = pref.sources if hasattr(pref, 'sources') else []
                    confidence = pref.confidence if hasattr(pref, 'confidence') else 0.5
                    
                    conflict.supporters[str(value)].extend(sources)
                    if str(value) not in conflict.confidence_scores:
                        conflict.confidence_scores[str(value)] = []
                    conflict.confidence_scores[str(value)].append(confidence)
                
                # Average the confidence scores
                for value in conflict.confidence_scores:
                    scores = conflict.confidence_scores[value]
                    conflict.confidence_scores[value] = sum(scores) / len(scores)
                
                conflicts.append(conflict)
        
        return conflicts
    
    def resolve_conflict(self, conflict: StyleConflict) -> StyleConflict:
        """
        Resolve a style conflict using multiple strategies.
        
        Args:
            conflict: The conflict to resolve
            
        Returns:
            The conflict with resolution filled in
        """
        # Strategy 1: Use team consensus if available
        consensus = self.team_learner.get_team_consensus(conflict.preference_type)
        if consensus:
            value, confidence = consensus
            if confidence > 0.7:  # High confidence threshold
                conflict.resolution = value
                conflict.resolution_rationale = (
                    f"Team consensus ({confidence:.1%} agreement) "
                    f"from {self.team_learner.get_team_summary()['total_members']} members"
                )
                return conflict
        
        # Strategy 2: Use confidence scores
        if conflict.confidence_scores:
            best_value = max(
                conflict.confidence_scores.items(),
                key=lambda x: x[1]
            )[0]
            best_confidence = conflict.confidence_scores[best_value]
            
            if best_confidence > 0.8:  # High confidence
                conflict.resolution = best_value
                conflict.resolution_rationale = (
                    f"Highest confidence score ({best_confidence:.1%}) "
                    f"from {len(conflict.supporters[best_value])} sources"
                )
                return conflict
        
        # Strategy 3: Count supporters
        if conflict.supporters:
            best_value = max(
                conflict.supporters.items(),
                key=lambda x: len(x[1])
            )[0]
            supporter_count = len(conflict.supporters[best_value])
            total_supporters = sum(len(s) for s in conflict.supporters.values())
            
            if supporter_count / total_supporters > 0.6:  # Majority
                conflict.resolution = best_value
                conflict.resolution_rationale = (
                    f"Majority support ({supporter_count}/{total_supporters} sources)"
                )
                return conflict
        
        # Strategy 4: Default to most common value
        if conflict.conflicting_values:
            value_counts = Counter(str(v) for v in conflict.conflicting_values)
            most_common = value_counts.most_common(1)[0]
            conflict.resolution = most_common[0]
            conflict.resolution_rationale = (
                f"Most frequently observed value "
                f"({most_common[1]} occurrences)"
            )
        
        return conflict
    
    def resolve_all_conflicts(self, preferences: Dict[str, Any]) -> Dict[str, Any]:
        """
        Detect and resolve all conflicts in the preference set.
        
        Returns:
            Dictionary with resolved preferences and conflict report
        """
        conflicts = self.detect_conflicts(preferences)
        resolved_conflicts = [self.resolve_conflict(c) for c in conflicts]
        
        # Apply resolutions to preferences
        resolved_prefs = {}
        for key, pref in preferences.items():
            # Check if this preference type has a resolution
            matching_conflict = None
            for conflict in resolved_conflicts:
                pref_type = pref.preference_type if hasattr(pref, 'preference_type') else key
                if pref_type == conflict.preference_type and conflict.resolution is not None:
                    matching_conflict = conflict
                    break
            
            # If there's a resolution, create a new preference with the resolved value
            if matching_conflict:
                if hasattr(pref, '_replace'):  # namedtuple
                    resolved_prefs[key] = pref._replace(value=matching_conflict.resolution)
                elif hasattr(pref, 'value'):  # regular object with value attribute
                    # Create a copy with updated value
                    import copy
                    new_pref = copy.copy(pref)
                    if hasattr(new_pref, '__dict__'):
                        new_pref.__dict__['value'] = matching_conflict.resolution
                    resolved_prefs[key] = new_pref
                else:
                    resolved_prefs[key] = pref
            else:
                resolved_prefs[key] = pref
        
        return {
            "preferences": resolved_prefs,
            "conflicts_detected": len(conflicts),
            "conflicts_resolved": len([c for c in resolved_conflicts if c.resolution]),
            "conflict_details": [
                {
                    "type": c.preference_type,
                    "resolution": c.resolution,
                    "rationale": c.resolution_rationale
                }
                for c in resolved_conflicts
            ]
        }


class AdvancedPatternRecognizer:
    """
    Advanced pattern recognition for code refactoring using machine learning techniques.
    
    This class provides:
    - Pattern similarity matching
    - Anomaly detection in code style
    - Predictive confidence scoring
    - Context-aware pattern analysis
    """
    
    def __init__(self):
        self.pattern_history: List[Dict[str, Any]] = []
        self.anomaly_threshold = 0.3  # Threshold for detecting style anomalies
    
    def extract_advanced_features(self, code: str, filepath: str) -> Dict[str, Any]:
        """
        Extract advanced features from code for pattern recognition.
        
        Args:
            code: Source code string
            filepath: Path to the file
            
        Returns:
            Dictionary of extracted features
        """
        features = {
            "filepath": filepath,
            "line_count": len(code.splitlines()),
            "complexity_indicators": {},
            "style_fingerprint": {},
            "context": {}
        }
        
        # Analyze import statements
        import_lines = [line for line in code.splitlines() if line.strip().startswith('import') or line.strip().startswith('from')]
        features["complexity_indicators"]["import_count"] = len(import_lines)
        
        # Analyze function/class definitions
        function_defs = len(re.findall(r'^def\s+\w+\s*\(', code, re.MULTILINE))
        class_defs = len(re.findall(r'^class\s+\w+', code, re.MULTILINE))
        features["complexity_indicators"]["function_count"] = function_defs
        features["complexity_indicators"]["class_count"] = class_defs
        
        # Analyze comment density
        comment_lines = len([l for l in code.splitlines() if l.strip().startswith('#')])
        features["complexity_indicators"]["comment_density"] = (
            comment_lines / len(code.splitlines()) if code.splitlines() else 0
        )
        
        # Style fingerprint - unique characteristics of this code
        features["style_fingerprint"]["uses_type_hints"] = ': ' in code and '->' in code
        features["style_fingerprint"]["uses_f_strings"] = 'f"' in code or "f'" in code
        features["style_fingerprint"]["uses_docstrings"] = '"""' in code or "'''" in code
        features["style_fingerprint"]["has_main_guard"] = '__name__' in code and '__main__' in code
        
        # Context - what kind of file is this?
        features["context"]["is_test"] = 'test_' in filepath or '_test' in filepath
        features["context"]["is_tool"] = 'tools/' in filepath
        features["context"]["is_example"] = 'examples/' in filepath or 'demo' in filepath.lower()
        
        return features
    
    def calculate_style_similarity(self, features1: Dict[str, Any], 
                                   features2: Dict[str, Any]) -> float:
        """
        Calculate similarity between two code style fingerprints.
        
        Returns:
            Similarity score between 0.0 and 1.0
        """
        if "style_fingerprint" not in features1 or "style_fingerprint" not in features2:
            return 0.5
        
        fp1 = features1["style_fingerprint"]
        fp2 = features2["style_fingerprint"]
        
        # Count matching features
        matches = sum(1 for key in fp1 if key in fp2 and fp1[key] == fp2[key])
        total = len(set(fp1.keys()) | set(fp2.keys()))
        
        return matches / total if total > 0 else 0.0
    
    def detect_style_anomalies(self, current_features: Dict[str, Any],
                               historical_features: List[Dict[str, Any]]) -> List[str]:
        """
        Detect anomalies in code style compared to historical patterns.
        
        Returns:
            List of detected anomalies
        """
        if not historical_features:
            return []
        
        anomalies = []
        
        # Calculate average similarity to historical patterns
        similarities = [
            self.calculate_style_similarity(current_features, hist)
            for hist in historical_features
        ]
        
        avg_similarity = sum(similarities) / len(similarities)
        
        if avg_similarity < self.anomaly_threshold:
            anomalies.append(
                f"Low style consistency: {avg_similarity:.1%} similarity to historical patterns"
            )
        
        # Check specific features
        current_fp = current_features.get("style_fingerprint", {})
        
        # Check if most historical code uses type hints but this doesn't
        hist_type_hints = sum(
            1 for f in historical_features 
            if f.get("style_fingerprint", {}).get("uses_type_hints", False)
        )
        if hist_type_hints / len(historical_features) > 0.7 and not current_fp.get("uses_type_hints", False):
            anomalies.append("Missing type hints (common in 70%+ of codebase)")
        
        # Check docstrings
        hist_docstrings = sum(
            1 for f in historical_features 
            if f.get("style_fingerprint", {}).get("uses_docstrings", False)
        )
        if hist_docstrings / len(historical_features) > 0.8 and not current_fp.get("uses_docstrings", False):
            anomalies.append("Missing docstrings (common in 80%+ of codebase)")
        
        return anomalies
    
    def predict_refactoring_success(self, suggestion_type: str,
                                    historical_outcomes: List[Tuple[str, bool]]) -> float:
        """
        Predict the success probability of a refactoring suggestion.
        
        Args:
            suggestion_type: Type of refactoring suggestion
            historical_outcomes: List of (suggestion_type, success) tuples
            
        Returns:
            Predicted success probability (0.0 to 1.0)
        """
        if not historical_outcomes:
            return 0.5  # No data, assume neutral
        
        # Filter to similar suggestion types
        similar_outcomes = [
            success for stype, success in historical_outcomes
            if stype == suggestion_type or stype.split('_')[0] == suggestion_type.split('_')[0]
        ]
        
        if not similar_outcomes:
            return 0.5
        
        # Calculate success rate
        success_rate = sum(similar_outcomes) / len(similar_outcomes)
        
        # Adjust confidence based on sample size
        # More samples = higher confidence in the estimate
        confidence_adjustment = min(1.0, len(similar_outcomes) / 20.0)
        
        # Blend with neutral (0.5) based on confidence
        return success_rate * confidence_adjustment + 0.5 * (1.0 - confidence_adjustment)
    
    def record_pattern(self, features: Dict[str, Any], outcome: bool):
        """Record a pattern and its outcome for future learning."""
        self.pattern_history.append({
            "features": features,
            "outcome": outcome,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        
        # Keep only recent history (last 1000 patterns)
        if len(self.pattern_history) > 1000:
            self.pattern_history = self.pattern_history[-1000:]


def main():
    """Demo of enhanced refactoring features."""
    print("\n" + "="*70)
    print("Enhanced Autonomous Refactoring Agent Features")
    print("@create-guru - Inventive and Visionary")
    print("="*70)
    
    # Demo 1: Team-specific learning
    print("\n📊 Demo 1: Team-Specific Style Learning")
    print("-" * 70)
    
    team_learner = TeamStyleLearner()
    
    # Simulate some reviews
    team_learner.learn_from_review("alice", "naming_convention", "snake_case", approved=True)
    team_learner.learn_from_review("bob", "naming_convention", "snake_case", approved=True)
    team_learner.learn_from_review("alice", "indentation", "spaces_4", approved=True)
    team_learner.learn_from_review("charlie", "naming_convention", "camelCase", approved=False)
    team_learner.learn_from_review("alice", "type_hints", True, approved=True)
    team_learner.learn_from_review("bob", "type_hints", True, approved=True)
    
    summary = team_learner.get_team_summary()
    print(f"✓ Team members: {summary['total_members']}")
    print(f"✓ Active reviewers: {summary['active_reviewers']}")
    print(f"✓ Total reviews: {summary['total_reviews']}")
    print(f"✓ Average expertise: {summary['average_expertise']:.2f}")
    
    print("\n🏆 Style Champions:")
    for username, score in summary['style_champions']:
        print(f"  • {username}: {score:.1f} expertise score")
    
    # Demo 2: Conflict resolution
    print("\n⚖️  Demo 2: Style Conflict Resolution")
    print("-" * 70)
    
    # Create mock conflicting preferences
    from collections import namedtuple
    Pref = namedtuple('Pref', ['preference_type', 'value', 'confidence', 'sources'])
    
    mock_prefs = {
        'pref1': Pref('naming', 'snake_case', 0.9, ['alice', 'bob']),
        'pref2': Pref('naming', 'camelCase', 0.6, ['charlie']),
        'pref3': Pref('indent', 'spaces_4', 0.95, ['alice', 'bob', 'charlie']),
    }
    
    resolver = StyleConflictResolver(team_learner)
    result = resolver.resolve_all_conflicts(mock_prefs)
    
    print(f"✓ Conflicts detected: {result['conflicts_detected']}")
    print(f"✓ Conflicts resolved: {result['conflicts_resolved']}")
    
    if result['conflict_details']:
        print("\n📋 Conflict Resolutions:")
        for detail in result['conflict_details']:
            print(f"  • {detail['type']}: {detail['resolution']}")
            print(f"    Rationale: {detail['rationale']}")
    
    # Demo 3: Advanced pattern recognition
    print("\n🔍 Demo 3: Advanced Pattern Recognition")
    print("-" * 70)
    
    recognizer = AdvancedPatternRecognizer()
    
    # Sample code for analysis
    sample_code = '''
def calculate_average(numbers: List[float]) -> float:
    """Calculate the average of a list of numbers."""
    if not numbers:
        raise ValueError("Cannot calculate average of empty list")
    return sum(numbers) / len(numbers)
'''
    
    features = recognizer.extract_advanced_features(sample_code, "tools/example.py")
    
    print(f"✓ Complexity indicators:")
    for key, value in features['complexity_indicators'].items():
        print(f"  • {key}: {value}")
    
    print(f"\n✓ Style fingerprint:")
    for key, value in features['style_fingerprint'].items():
        print(f"  • {key}: {value}")
    
    # Predict success of a refactoring
    historical = [
        ("naming_convention", True),
        ("naming_convention", True),
        ("naming_convention", False),
        ("type_hints", True),
    ]
    
    success_prob = recognizer.predict_refactoring_success("naming_convention", historical)
    print(f"\n✓ Predicted success for naming_convention: {success_prob:.1%}")
    
    print("\n" + "="*70)
    print("✅ All enhanced features demonstrated successfully!")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
