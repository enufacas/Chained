#!/usr/bin/env python3
"""
Issue Discussion Learner - Self-Documenting AI System

This module learns from GitHub issue discussions, extracting insights,
patterns, and knowledge to improve the autonomous AI system.

Author: @engineer-master
Approach: Rigorous and systematic, with defensive programming
"""

import json
import re
import os
import sys
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
from collections import defaultdict


@dataclass
class DiscussionInsight:
    """Represents a learning insight extracted from a discussion."""
    issue_number: int
    issue_title: str
    insight_type: str  # 'technical', 'process', 'agent_behavior', 'decision'
    content: str
    context: str
    participants: List[str]
    timestamp: str
    confidence: float  # 0.0 to 1.0
    tags: List[str]
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return asdict(self)


@dataclass
class DiscussionAnalysis:
    """Complete analysis of an issue discussion."""
    issue_number: int
    issue_title: str
    issue_labels: List[str]
    total_comments: int
    participants: List[str]
    duration_hours: float
    insights: List[DiscussionInsight]
    key_decisions: List[str]
    patterns_identified: List[str]
    learning_quality: float  # 0.0 to 1.0
    timestamp: str
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        data = asdict(self)
        data['insights'] = [i.to_dict() if hasattr(i, 'to_dict') else i 
                            for i in self.insights]
        return data


class IssueDiscussionLearner:
    """
    Learns from GitHub issue discussions to improve the AI system.
    
    This class implements a systematic approach to extracting knowledge
    from issue discussions, identifying patterns, and generating
    self-documentation.
    """
    
    def __init__(self, learning_dir: str = 'learnings/discussions'):
        """
        Initialize the Issue Discussion Learner.
        
        Args:
            learning_dir: Directory to store learned insights
        """
        self.learning_dir = Path(learning_dir)
        self.learning_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize pattern recognition
        self.known_patterns = self._load_known_patterns()
        
        # Insight classification keywords
        self.insight_keywords = {
            'technical': [
                'implementation', 'algorithm', 'architecture', 'design',
                'performance', 'optimization', 'bug', 'fix', 'code',
                'API', 'database', 'function', 'class', 'module'
            ],
            'process': [
                'workflow', 'process', 'procedure', 'methodology',
                'approach', 'strategy', 'pipeline', 'automation',
                'testing', 'deployment', 'CI/CD', 'review'
            ],
            'agent_behavior': [
                'agent', 'personality', 'communication', 'collaboration',
                'coordination', 'assignment', 'specialization', 'competition'
            ],
            'decision': [
                'decided', 'agreed', 'concluded', 'resolved', 'chosen',
                'selected', 'determined', 'consensus', 'approved'
            ]
        }
    
    def _load_known_patterns(self) -> Dict[str, List[str]]:
        """
        Load known discussion patterns from previous learnings.
        
        Returns:
            Dictionary of pattern categories and examples
        """
        patterns_file = self.learning_dir / 'known_patterns.json'
        
        if patterns_file.exists():
            try:
                with open(patterns_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Warning: Could not load patterns: {e}", file=sys.stderr)
        
        # Default patterns
        return {
            'agent_selection': [
                'agent X was chosen because',
                'matched to agent based on',
                'assigned to agent for'
            ],
            'technical_debate': [
                'approach A vs approach B',
                'trade-off between',
                'considered alternatives'
            ],
            'consensus_building': [
                'agreed that',
                'team consensus',
                'decided together'
            ],
            'knowledge_sharing': [
                'learned that',
                'discovered that',
                'found out that'
            ]
        }
    
    def analyze_issue_discussion(self, issue_data: Dict) -> DiscussionAnalysis:
        """
        Analyze a complete issue discussion and extract learnings.
        
        Args:
            issue_data: Dictionary containing issue details and comments
            
        Returns:
            DiscussionAnalysis object with extracted insights
        """
        # Extract basic issue information
        issue_number = issue_data.get('number', 0)
        issue_title = issue_data.get('title', '')
        issue_labels = [label.get('name', '') for label in issue_data.get('labels', [])]
        comments = issue_data.get('comments', [])
        
        # Calculate discussion metrics
        total_comments = len(comments)
        participants = self._extract_participants(issue_data, comments)
        duration_hours = self._calculate_duration(issue_data, comments)
        
        # Extract insights from discussion
        insights = self._extract_insights(
            issue_number, issue_title, issue_data, comments
        )
        
        # Identify key decisions
        key_decisions = self._extract_decisions(comments)
        
        # Identify patterns
        patterns_identified = self._identify_patterns(comments)
        
        # Calculate learning quality score
        learning_quality = self._calculate_learning_quality(
            insights, key_decisions, patterns_identified
        )
        
        # Create analysis object
        analysis = DiscussionAnalysis(
            issue_number=issue_number,
            issue_title=issue_title,
            issue_labels=issue_labels,
            total_comments=total_comments,
            participants=participants,
            duration_hours=duration_hours,
            insights=insights,
            key_decisions=key_decisions,
            patterns_identified=patterns_identified,
            learning_quality=learning_quality,
            timestamp=datetime.now(timezone.utc).isoformat()
        )
        
        return analysis
    
    def _extract_participants(self, issue_data: Dict, comments: List[Dict]) -> List[str]:
        """Extract unique participants from issue and comments."""
        participants = set()
        
        # Add issue author
        if 'user' in issue_data and 'login' in issue_data['user']:
            participants.add(issue_data['user']['login'])
        
        # Add comment authors
        for comment in comments:
            if 'user' in comment and 'login' in comment['user']:
                participants.add(comment['user']['login'])
        
        return sorted(list(participants))
    
    def _calculate_duration(self, issue_data: Dict, comments: List[Dict]) -> float:
        """Calculate discussion duration in hours."""
        try:
            created_at = issue_data.get('created_at', '')
            
            if not comments:
                return 0.0
            
            # Get last comment timestamp
            last_comment = comments[-1]
            updated_at = last_comment.get('created_at', created_at)
            
            # Parse timestamps
            from datetime import datetime
            start = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            end = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
            
            # Calculate duration
            duration = (end - start).total_seconds() / 3600.0
            return round(duration, 2)
            
        except Exception as e:
            print(f"Warning: Could not calculate duration: {e}", file=sys.stderr)
            return 0.0
    
    def _extract_insights(
        self, 
        issue_number: int,
        issue_title: str,
        issue_data: Dict,
        comments: List[Dict]
    ) -> List[DiscussionInsight]:
        """
        Extract valuable insights from discussion.
        
        Uses keyword matching, pattern recognition, and context analysis.
        """
        insights = []
        
        # Analyze issue body
        issue_body = issue_data.get('body', '')
        if issue_body:
            body_insights = self._analyze_text_for_insights(
                issue_number, issue_title, issue_body,
                'issue_author', issue_data.get('created_at', '')
            )
            insights.extend(body_insights)
        
        # Analyze each comment
        for comment in comments:
            comment_body = comment.get('body', '')
            author = comment.get('user', {}).get('login', 'unknown')
            timestamp = comment.get('created_at', '')
            
            if comment_body:
                comment_insights = self._analyze_text_for_insights(
                    issue_number, issue_title, comment_body, author, timestamp
                )
                insights.extend(comment_insights)
        
        return insights
    
    def _analyze_text_for_insights(
        self,
        issue_number: int,
        issue_title: str,
        text: str,
        author: str,
        timestamp: str
    ) -> List[DiscussionInsight]:
        """
        Analyze text content for insights.
        
        This method implements defensive text analysis with error handling.
        """
        insights = []
        
        try:
            # Split into sentences
            sentences = re.split(r'[.!?]+', text)
            
            for sentence in sentences:
                sentence = sentence.strip()
                if len(sentence) < 20:  # Skip very short sentences
                    continue
                
                # Classify insight type
                insight_type = self._classify_insight_type(sentence)
                if not insight_type:
                    continue
                
                # Calculate confidence
                confidence = self._calculate_insight_confidence(sentence, insight_type)
                if confidence < 0.3:  # Skip low confidence insights
                    continue
                
                # Extract tags
                tags = self._extract_tags(sentence)
                
                # Create insight
                insight = DiscussionInsight(
                    issue_number=issue_number,
                    issue_title=issue_title,
                    insight_type=insight_type,
                    content=sentence,
                    context=text[:200],  # First 200 chars for context
                    participants=[author],
                    timestamp=timestamp,
                    confidence=confidence,
                    tags=tags
                )
                
                insights.append(insight)
        
        except Exception as e:
            print(f"Warning: Error analyzing text: {e}", file=sys.stderr)
        
        return insights
    
    def _classify_insight_type(self, text: str) -> Optional[str]:
        """Classify the type of insight based on keywords."""
        text_lower = text.lower()
        
        # Count keyword matches for each type
        type_scores = {}
        for insight_type, keywords in self.insight_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            if score > 0:
                type_scores[insight_type] = score
        
        if not type_scores:
            return None
        
        # Return type with highest score
        return max(type_scores.items(), key=lambda x: x[1])[0]
    
    def _calculate_insight_confidence(self, text: str, insight_type: str) -> float:
        """
        Calculate confidence score for an insight.
        
        Based on multiple factors:
        - Keyword density
        - Text length
        - Specificity indicators
        """
        confidence = 0.5  # Base confidence
        
        # Keyword density bonus
        text_lower = text.lower()
        keywords = self.insight_keywords.get(insight_type, [])
        keyword_count = sum(1 for keyword in keywords if keyword in text_lower)
        confidence += min(0.3, keyword_count * 0.1)
        
        # Length bonus (longer insights tend to be more detailed)
        if len(text) > 100:
            confidence += 0.1
        
        # Specificity indicators
        specificity_markers = [
            'specifically', 'exactly', 'precisely', 'clearly',
            'demonstrated', 'proved', 'showed', 'revealed'
        ]
        if any(marker in text_lower for marker in specificity_markers):
            confidence += 0.1
        
        return min(1.0, confidence)
    
    def _extract_tags(self, text: str) -> List[str]:
        """Extract relevant tags from text."""
        tags = []
        text_lower = text.lower()
        
        # Technology tags
        tech_keywords = [
            'python', 'javascript', 'github', 'api', 'workflow',
            'agent', 'ai', 'ml', 'learning', 'automation'
        ]
        for tech in tech_keywords:
            if tech in text_lower:
                tags.append(tech)
        
        return tags[:5]  # Limit to 5 tags
    
    def _extract_decisions(self, comments: List[Dict]) -> List[str]:
        """Extract key decisions made during discussion."""
        decisions = []
        
        decision_patterns = [
            r'decided to\s+(.+?)(?:[.!]|$)',
            r'agreed to\s+(.+?)(?:[.!]|$)',
            r'concluded that\s+(.+?)(?:[.!]|$)',
            r'resolved to\s+(.+?)(?:[.!]|$)',
            r'will\s+(.+?)(?:[.!]|$)',
        ]
        
        for comment in comments:
            body = comment.get('body', '')
            
            for pattern in decision_patterns:
                matches = re.finditer(pattern, body, re.IGNORECASE)
                for match in matches:
                    decision = match.group(1).strip()
                    if len(decision) > 10 and decision not in decisions:
                        decisions.append(decision)
        
        return decisions[:10]  # Limit to top 10
    
    def _identify_patterns(self, comments: List[Dict]) -> List[str]:
        """Identify discussion patterns using known patterns."""
        identified = []
        
        # Combine all comment text
        full_text = ' '.join(
            comment.get('body', '') for comment in comments
        ).lower()
        
        # Check against known patterns
        for pattern_type, patterns in self.known_patterns.items():
            for pattern in patterns:
                if pattern.lower() in full_text:
                    identified.append(f"{pattern_type}: {pattern}")
        
        return identified
    
    def _calculate_learning_quality(
        self,
        insights: List[DiscussionInsight],
        decisions: List[str],
        patterns: List[str]
    ) -> float:
        """
        Calculate overall learning quality score.
        
        Factors:
        - Number and confidence of insights
        - Number of key decisions
        - Number of patterns identified
        """
        score = 0.0
        
        # Insights contribution (max 0.5)
        if insights:
            avg_confidence = sum(i.confidence for i in insights) / len(insights)
            insight_score = min(0.5, (len(insights) / 20.0) * avg_confidence)
            score += insight_score
        
        # Decisions contribution (max 0.3)
        decision_score = min(0.3, len(decisions) / 10.0 * 0.3)
        score += decision_score
        
        # Patterns contribution (max 0.2)
        pattern_score = min(0.2, len(patterns) / 5.0 * 0.2)
        score += pattern_score
        
        return round(score, 3)
    
    def save_analysis(self, analysis: DiscussionAnalysis) -> str:
        """
        Save discussion analysis to learning database.
        
        Args:
            analysis: DiscussionAnalysis object to save
            
        Returns:
            Path to saved file
        """
        # Create filename
        timestamp = datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')
        filename = f"discussion_issue_{analysis.issue_number}_{timestamp}.json"
        filepath = self.learning_dir / filename
        
        # Save to file
        try:
            with open(filepath, 'w') as f:
                json.dump(analysis.to_dict(), f, indent=2)
            
            print(f"✅ Saved analysis to {filepath}")
            return str(filepath)
            
        except Exception as e:
            print(f"❌ Error saving analysis: {e}", file=sys.stderr)
            raise
    
    def generate_documentation(self, analysis: DiscussionAnalysis) -> str:
        """
        Generate markdown documentation from analysis.
        
        This creates human-readable documentation that captures
        the key learnings from the discussion.
        """
        doc = f"""# Discussion Learning: {analysis.issue_title}

**Issue:** #{analysis.issue_number}
**Date:** {analysis.timestamp}
**Participants:** {', '.join(analysis.participants)}
**Duration:** {analysis.duration_hours} hours
**Learning Quality:** {analysis.learning_quality:.1%}

## 📊 Discussion Metrics

- **Total Comments:** {analysis.total_comments}
- **Insights Extracted:** {len(analysis.insights)}
- **Key Decisions:** {len(analysis.key_decisions)}
- **Patterns Identified:** {len(analysis.patterns_identified)}

## 💡 Key Insights

"""
        
        # Group insights by type
        insights_by_type = defaultdict(list)
        for insight in analysis.insights:
            insights_by_type[insight.insight_type].append(insight)
        
        for insight_type, insights in sorted(insights_by_type.items()):
            doc += f"\n### {insight_type.replace('_', ' ').title()}\n\n"
            for insight in insights[:5]:  # Top 5 per type
                doc += f"- {insight.content}\n"
                doc += f"  - *Confidence: {insight.confidence:.1%}, Tags: {', '.join(insight.tags)}*\n"
        
        # Add key decisions
        if analysis.key_decisions:
            doc += "\n## 🎯 Key Decisions\n\n"
            for decision in analysis.key_decisions:
                doc += f"- {decision}\n"
        
        # Add patterns
        if analysis.patterns_identified:
            doc += "\n## 🔍 Patterns Identified\n\n"
            for pattern in analysis.patterns_identified:
                doc += f"- {pattern}\n"
        
        # Add learnings summary
        doc += f"""

## 📚 Learning Summary

This discussion provided valuable insights into {', '.join(analysis.issue_labels)} topics.
The AI system learned from {len(analysis.insights)} insights with an average 
confidence of {sum(i.confidence for i in analysis.insights) / len(analysis.insights):.1%}.

### What the AI Learned

"""
        
        # Summarize by insight type
        for insight_type, insights in insights_by_type.items():
            doc += f"- **{insight_type.replace('_', ' ').title()}**: "
            doc += f"{len(insights)} insights about "
            
            # Get common tags
            all_tags = [tag for i in insights for tag in i.tags]
            common_tags = [tag for tag in set(all_tags) if all_tags.count(tag) >= 2]
            if common_tags:
                doc += f"{', '.join(common_tags[:3])}\n"
            else:
                doc += "various technical aspects\n"
        
        doc += """

---

*This documentation was automatically generated by the Self-Documenting AI system.*
*The AI learns from every discussion to continuously improve.*
"""
        
        return doc
    
    def consolidate_learnings(self, days: int = 7) -> Dict:
        """
        Consolidate learnings from multiple discussions.
        
        Args:
            days: Number of days to look back
            
        Returns:
            Consolidated learning summary
        """
        from datetime import timedelta
        
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
        
        # Load all discussion files
        all_insights = []
        all_decisions = []
        all_patterns = []
        issues_analyzed = 0
        
        for filepath in self.learning_dir.glob('discussion_issue_*.json'):
            try:
                with open(filepath, 'r') as f:
                    data = json.load(f)
                
                # Check if within timeframe
                timestamp = data.get('timestamp', '')
                if timestamp:
                    file_date = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    if file_date < cutoff_date:
                        continue
                
                # Collect data
                all_insights.extend(data.get('insights', []))
                all_decisions.extend(data.get('key_decisions', []))
                all_patterns.extend(data.get('patterns_identified', []))
                issues_analyzed += 1
                
            except Exception as e:
                print(f"Warning: Could not load {filepath}: {e}", file=sys.stderr)
        
        # Analyze consolidated data
        insight_types = defaultdict(int)
        common_tags = defaultdict(int)
        
        for insight in all_insights:
            if isinstance(insight, dict):
                insight_types[insight.get('insight_type', 'unknown')] += 1
                for tag in insight.get('tags', []):
                    common_tags[tag] += 1
        
        # Create summary
        summary = {
            'period_days': days,
            'issues_analyzed': issues_analyzed,
            'total_insights': len(all_insights),
            'total_decisions': len(all_decisions),
            'total_patterns': len(all_patterns),
            'insight_type_distribution': dict(insight_types),
            'top_tags': dict(sorted(common_tags.items(), 
                                   key=lambda x: x[1], 
                                   reverse=True)[:10]),
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        
        return summary


def main():
    """Main entry point for command-line usage."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Learn from GitHub issue discussions'
    )
    parser.add_argument(
        'issue_file',
        help='JSON file containing issue data'
    )
    parser.add_argument(
        '--output-dir',
        default='learnings/discussions',
        help='Output directory for learnings'
    )
    parser.add_argument(
        '--generate-doc',
        action='store_true',
        help='Generate markdown documentation'
    )
    
    args = parser.parse_args()
    
    # Load issue data
    try:
        with open(args.issue_file, 'r') as f:
            issue_data = json.load(f)
    except Exception as e:
        print(f"❌ Error loading issue file: {e}", file=sys.stderr)
        return 1
    
    # Create learner
    learner = IssueDiscussionLearner(learning_dir=args.output_dir)
    
    # Analyze discussion
    print(f"🔍 Analyzing issue #{issue_data.get('number', 'unknown')}...")
    analysis = learner.analyze_issue_discussion(issue_data)
    
    # Save analysis
    filepath = learner.save_analysis(analysis)
    
    # Generate documentation if requested
    if args.generate_doc:
        doc = learner.generate_documentation(analysis)
        doc_path = filepath.replace('.json', '.md')
        with open(doc_path, 'w') as f:
            f.write(doc)
        print(f"📄 Generated documentation: {doc_path}")
    
    # Print summary
    print(f"\n📊 Analysis Complete:")
    print(f"  - Insights extracted: {len(analysis.insights)}")
    print(f"  - Key decisions: {len(analysis.key_decisions)}")
    print(f"  - Patterns identified: {len(analysis.patterns_identified)}")
    print(f"  - Learning quality: {analysis.learning_quality:.1%}")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
