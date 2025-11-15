#!/usr/bin/env python3
"""
Enhanced Issue Discussion Learner - Advanced Self-Documenting AI

This module extends the existing issue-discussion-learner with:
1. Advanced pattern recognition using similarity algorithms
2. Real-time learning during active discussions
3. Knowledge graph connections for related insights
4. Proactive learning suggestions

Author: @engineer-master
Approach: Rigorous, systematic, with innovative enhancements
"""

import json
import re
import os
import sys
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass, asdict, field
from pathlib import Path
from collections import defaultdict, Counter
import hashlib

# Import base learner
tools_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, tools_dir)
import importlib.util
spec = importlib.util.spec_from_file_location(
    "issue_discussion_learner",
    os.path.join(tools_dir, "issue-discussion-learner.py")
)
base_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(base_module)

# Import base classes
IssueDiscussionLearner = base_module.IssueDiscussionLearner
DiscussionInsight = base_module.DiscussionInsight
DiscussionAnalysis = base_module.DiscussionAnalysis


@dataclass
class KnowledgeConnection:
    """Represents a connection between two insights in the knowledge graph."""
    source_insight_id: str
    target_insight_id: str
    connection_type: str  # 'similar', 'contradicts', 'builds_on', 'related'
    similarity_score: float  # 0.0 to 1.0
    timestamp: str
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return asdict(self)


@dataclass
class LiveLearning:
    """Represents real-time learning extracted during active discussion."""
    discussion_id: str
    insight_preview: str
    confidence: float
    suggested_actions: List[str]
    related_past_discussions: List[str]
    timestamp: str
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return asdict(self)


class EnhancedDiscussionLearner(IssueDiscussionLearner):
    """
    Enhanced learner with advanced pattern recognition and real-time learning.
    
    Extends the base IssueDiscussionLearner with:
    - Sophisticated similarity algorithms
    - Knowledge graph connections
    - Real-time learning during discussions
    - Proactive suggestion generation
    """
    
    def __init__(self, learning_dir: str = 'learnings/discussions'):
        """
        Initialize the Enhanced Discussion Learner.
        
        Args:
            learning_dir: Directory to store learned insights
        """
        super().__init__(learning_dir)
        
        # Knowledge graph storage
        self.knowledge_graph_file = self.learning_dir / 'knowledge_graph.json'
        self.knowledge_graph = self._load_knowledge_graph()
        
        # Real-time learning cache
        self.live_learning_cache = {}
        
        # Enhanced pattern recognition
        self.advanced_patterns = {
            'problem_solving': [
                r'solved by\s+(\w+)',
                r'fixed by\s+(\w+)',
                r'resolved through\s+(.+?)(?:[.!]|$)',
            ],
            'collaboration_success': [
                r'great teamwork',
                r'excellent collaboration',
                r'worked well together',
                r'coordinated effectively'
            ],
            'learning_moment': [
                r'learned that\s+(.+?)(?:[.!]|$)',
                r'discovered\s+(.+?)(?:[.!]|$)',
                r'realized\s+(.+?)(?:[.!]|$)',
            ],
            'decision_making': [
                r'after considering\s+(.+?), we decided',
                r'evaluated\s+(.+?)\s+and chose',
                r'compared\s+(.+?)\s+and selected',
            ]
        }
    
    def _load_knowledge_graph(self) -> Dict:
        """Load the knowledge graph from disk."""
        if self.knowledge_graph_file.exists():
            try:
                with open(self.knowledge_graph_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Warning: Could not load knowledge graph: {e}", file=sys.stderr)
        
        return {
            'insights': {},  # insight_id -> insight data
            'connections': [],  # list of KnowledgeConnection objects
            'metadata': {
                'created': datetime.now(timezone.utc).isoformat(),
                'last_updated': datetime.now(timezone.utc).isoformat(),
                'total_insights': 0,
                'total_connections': 0
            }
        }
    
    def _save_knowledge_graph(self):
        """Save the knowledge graph to disk."""
        try:
            self.knowledge_graph['metadata']['last_updated'] = datetime.now(timezone.utc).isoformat()
            with open(self.knowledge_graph_file, 'w') as f:
                json.dump(self.knowledge_graph, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save knowledge graph: {e}", file=sys.stderr)
    
    def _generate_insight_id(self, insight: DiscussionInsight) -> str:
        """Generate a unique ID for an insight."""
        content_hash = hashlib.sha256(
            f"{insight.issue_number}_{insight.content}_{insight.timestamp}".encode()
        ).hexdigest()[:12]
        return f"insight_{insight.issue_number}_{content_hash}"
    
    def calculate_text_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate similarity between two text strings.
        
        Uses a combination of:
        - Jaccard similarity (word overlap)
        - Common keyword density
        - Structural similarity
        
        Returns:
            Similarity score from 0.0 to 1.0
        """
        # Normalize text
        words1 = set(re.findall(r'\w+', text1.lower()))
        words2 = set(re.findall(r'\w+', text2.lower()))
        
        if not words1 or not words2:
            return 0.0
        
        # Jaccard similarity
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        jaccard = len(intersection) / len(union) if union else 0.0
        
        # Keyword overlap (weighted more heavily)
        important_words = {'implement', 'algorithm', 'performance', 'bug', 'fix', 
                          'optimize', 'design', 'architecture', 'test', 'deploy'}
        important_overlap = len(intersection.intersection(important_words))
        keyword_bonus = min(0.3, important_overlap * 0.1)
        
        # Final similarity
        return min(1.0, jaccard + keyword_bonus)
    
    def find_similar_insights(
        self, 
        insight: DiscussionInsight, 
        threshold: float = 0.3
    ) -> List[Tuple[str, float]]:
        """
        Find insights similar to the given one.
        
        Args:
            insight: The insight to compare against
            threshold: Minimum similarity score to consider
            
        Returns:
            List of (insight_id, similarity_score) tuples
        """
        similar = []
        
        for insight_id, stored_data in self.knowledge_graph['insights'].items():
            # Skip if it's the same insight
            if insight_id == self._generate_insight_id(insight):
                continue
            
            # Calculate similarity
            similarity = self.calculate_text_similarity(
                insight.content,
                stored_data.get('content', '')
            )
            
            # Add to results if above threshold
            if similarity >= threshold:
                similar.append((insight_id, similarity))
        
        # Sort by similarity (descending)
        similar.sort(key=lambda x: x[1], reverse=True)
        
        return similar
    
    def add_to_knowledge_graph(self, analysis: DiscussionAnalysis):
        """
        Add insights from an analysis to the knowledge graph.
        
        This creates nodes for insights and edges for connections.
        """
        print("🔗 Building knowledge graph connections...")
        
        new_connections = []
        
        for insight in analysis.insights:
            # Generate insight ID
            insight_id = self._generate_insight_id(insight)
            
            # Add to knowledge graph
            self.knowledge_graph['insights'][insight_id] = {
                'issue_number': insight.issue_number,
                'issue_title': insight.issue_title,
                'insight_type': insight.insight_type,
                'content': insight.content,
                'confidence': insight.confidence,
                'tags': insight.tags,
                'timestamp': insight.timestamp
            }
            
            # Find similar insights
            similar_insights = self.find_similar_insights(insight, threshold=0.4)
            
            # Create connections
            for target_id, similarity in similar_insights[:5]:  # Top 5 connections
                connection = KnowledgeConnection(
                    source_insight_id=insight_id,
                    target_insight_id=target_id,
                    connection_type='similar',
                    similarity_score=similarity,
                    timestamp=datetime.now(timezone.utc).isoformat()
                )
                new_connections.append(connection.to_dict())
        
        # Add new connections to graph
        self.knowledge_graph['connections'].extend(new_connections)
        
        # Update metadata
        self.knowledge_graph['metadata']['total_insights'] = len(
            self.knowledge_graph['insights']
        )
        self.knowledge_graph['metadata']['total_connections'] = len(
            self.knowledge_graph['connections']
        )
        
        # Save graph
        self._save_knowledge_graph()
        
        print(f"✅ Added {len(analysis.insights)} insights to knowledge graph")
        print(f"   Created {len(new_connections)} new connections")
    
    def analyze_live_discussion(
        self, 
        issue_number: int,
        current_comments: List[Dict]
    ) -> LiveLearning:
        """
        Perform real-time analysis of an ongoing discussion.
        
        This provides immediate insights as discussions happen.
        
        Args:
            issue_number: Issue being discussed
            current_comments: List of comments so far
            
        Returns:
            LiveLearning object with real-time insights
        """
        discussion_id = f"live_{issue_number}_{len(current_comments)}"
        
        # Extract quick insights from recent comments
        recent_text = ' '.join(
            comment.get('body', '') for comment in current_comments[-5:]
        )
        
        # Identify emerging patterns
        emerging_patterns = []
        for pattern_type, patterns in self.advanced_patterns.items():
            for pattern in patterns:
                # Handle both string patterns and regex patterns
                if isinstance(pattern, str):
                    if pattern.lower() in recent_text.lower():
                        emerging_patterns.append(pattern_type)
                else:
                    # It's a regex pattern
                    import re
                    if re.search(pattern, recent_text, re.IGNORECASE):
                        emerging_patterns.append(pattern_type)
        
        # Generate insight preview
        if emerging_patterns:
            insight_preview = f"Observing {', '.join(set(emerging_patterns))} patterns"
        else:
            insight_preview = "Discussion ongoing, gathering insights"
        
        # Calculate confidence based on discussion depth
        confidence = min(0.9, len(current_comments) / 10.0 * 0.8 + 0.1)
        
        # Suggest actions based on patterns
        suggested_actions = []
        unique_patterns = set(emerging_patterns)
        if 'problem_solving' in unique_patterns:
            suggested_actions.append("Document the solution approach being discussed")
        if 'decision_making' in unique_patterns:
            suggested_actions.append("Capture the decision rationale")
        if 'learning_moment' in unique_patterns:
            suggested_actions.append("Record this learning for future reference")
        if 'collaboration_success' in unique_patterns:
            suggested_actions.append("Capture successful collaboration patterns")
        
        # Find related past discussions
        related_past = self._find_related_discussions(recent_text)
        
        # Create live learning object
        live_learning = LiveLearning(
            discussion_id=discussion_id,
            insight_preview=insight_preview,
            confidence=confidence,
            suggested_actions=suggested_actions,
            related_past_discussions=related_past[:3],  # Top 3
            timestamp=datetime.now(timezone.utc).isoformat()
        )
        
        # Cache for later
        self.live_learning_cache[discussion_id] = live_learning
        
        return live_learning
    
    def _find_related_discussions(self, text: str, limit: int = 5) -> List[str]:
        """Find past discussions related to the current text."""
        related = []
        
        # Load past discussion files
        for filepath in self.learning_dir.glob('discussion_issue_*.json'):
            try:
                with open(filepath, 'r') as f:
                    data = json.load(f)
                
                # Calculate similarity with issue title and key decisions
                title = data.get('issue_title', '')
                decisions = ' '.join(data.get('key_decisions', []))
                combined_text = f"{title} {decisions}"
                
                similarity = self.calculate_text_similarity(text, combined_text)
                
                if similarity > 0.3:
                    related.append((
                        f"#{data.get('issue_number')}: {title}",
                        similarity
                    ))
            except Exception:
                continue
        
        # Sort by similarity and return top matches
        related.sort(key=lambda x: x[1], reverse=True)
        return [item[0] for item in related[:limit]]
    
    def generate_proactive_suggestions(
        self,
        issue_data: Dict
    ) -> List[str]:
        """
        Generate proactive suggestions based on issue content and past learnings.
        
        Args:
            issue_data: The issue to generate suggestions for
            
        Returns:
            List of actionable suggestions
        """
        suggestions = []
        
        issue_title = issue_data.get('title', '')
        issue_body = issue_data.get('body', '')
        combined_text = f"{issue_title} {issue_body}"
        
        # Find similar past discussions
        related = self._find_related_discussions(combined_text, limit=3)
        
        if related:
            suggestions.append(
                f"📚 Similar discussions found: {', '.join(related)}"
            )
        
        # Check for common patterns in issue text
        text_lower = combined_text.lower()
        
        if any(word in text_lower for word in ['performance', 'slow', 'optimize']):
            suggestions.append(
                "⚡ Consider documenting performance metrics and benchmarks"
            )
        
        if any(word in text_lower for word in ['bug', 'error', 'issue', 'problem']):
            suggestions.append(
                "🐛 Document steps to reproduce and expected vs actual behavior"
            )
        
        if any(word in text_lower for word in ['feature', 'implement', 'add']):
            suggestions.append(
                "🎯 Define clear acceptance criteria and test cases"
            )
        
        if any(word in text_lower for word in ['refactor', 'clean', 'improve']):
            suggestions.append(
                "🔨 Document the current state and desired improvements"
            )
        
        # Add knowledge graph insights
        if self.knowledge_graph['insights']:
            # Find insights with high overlap in tags
            issue_tags = self._extract_tags(combined_text)
            matching_insights = []
            
            for insight_id, insight_data in self.knowledge_graph['insights'].items():
                insight_tags = set(insight_data.get('tags', []))
                overlap = len(set(issue_tags).intersection(insight_tags))
                if overlap >= 2:
                    matching_insights.append(insight_data['content'])
            
            if matching_insights:
                suggestions.append(
                    f"💡 Related past insights: {matching_insights[0][:80]}..."
                )
        
        return suggestions
    
    def analyze_with_enhancements(
        self,
        issue_data: Dict
    ) -> Tuple[DiscussionAnalysis, Dict]:
        """
        Analyze issue discussion with all enhancements.
        
        Args:
            issue_data: Complete issue data
            
        Returns:
            Tuple of (DiscussionAnalysis, enhancements_dict)
        """
        # Base analysis
        analysis = self.analyze_issue_discussion(issue_data)
        
        # Add to knowledge graph
        self.add_to_knowledge_graph(analysis)
        
        # Generate proactive suggestions
        suggestions = self.generate_proactive_suggestions(issue_data)
        
        # Find knowledge connections for insights
        insight_connections = {}
        for insight in analysis.insights:
            insight_id = self._generate_insight_id(insight)
            similar = self.find_similar_insights(insight, threshold=0.4)
            if similar:
                insight_connections[insight_id] = [
                    {'target_id': target, 'similarity': score}
                    for target, score in similar[:3]
                ]
        
        # Compile enhancements
        enhancements = {
            'proactive_suggestions': suggestions,
            'knowledge_connections': insight_connections,
            'knowledge_graph_stats': {
                'total_insights': len(self.knowledge_graph['insights']),
                'total_connections': len(self.knowledge_graph['connections']),
                'new_insights_added': len(analysis.insights)
            },
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        
        return analysis, enhancements
    
    def generate_enhanced_documentation(
        self,
        analysis: DiscussionAnalysis,
        enhancements: Dict
    ) -> str:
        """
        Generate enhanced documentation with knowledge graph insights.
        
        Extends base documentation with connections and suggestions.
        """
        # Get base documentation
        base_doc = self.generate_documentation(analysis)
        
        # Add enhancements section
        enhanced_section = """

## 🧠 Enhanced Learning Insights

### Proactive Suggestions

"""
        
        for suggestion in enhancements.get('proactive_suggestions', []):
            enhanced_section += f"- {suggestion}\n"
        
        # Add knowledge graph insights
        connections = enhancements.get('knowledge_connections', {})
        if connections:
            enhanced_section += """

### Knowledge Graph Connections

This discussion connects to previous learnings:

"""
            for insight_id, related in list(connections.items())[:5]:
                enhanced_section += f"\n**Insight:** {insight_id}\n"
                for conn in related:
                    enhanced_section += f"  - Connected to {conn['target_id']} "
                    enhanced_section += f"(similarity: {conn['similarity']:.1%})\n"
        
        # Add stats
        stats = enhancements.get('knowledge_graph_stats', {})
        enhanced_section += f"""

### Knowledge Graph Statistics

- **Total Insights in Graph**: {stats.get('total_insights', 0)}
- **Total Connections**: {stats.get('total_connections', 0)}
- **New Insights from This Discussion**: {stats.get('new_insights_added', 0)}

"""
        
        # Insert enhanced section before the final note
        final_note_index = base_doc.rfind('---\n\n*This documentation')
        if final_note_index > 0:
            enhanced_doc = (
                base_doc[:final_note_index] +
                enhanced_section +
                base_doc[final_note_index:]
            )
        else:
            enhanced_doc = base_doc + enhanced_section
        
        return enhanced_doc


def main():
    """Main entry point for command-line usage."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Enhanced learning from GitHub issue discussions'
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
        '--live-analysis',
        action='store_true',
        help='Perform live analysis of ongoing discussion'
    )
    
    args = parser.parse_args()
    
    # Load issue data
    try:
        with open(args.issue_file, 'r') as f:
            issue_data = json.load(f)
    except Exception as e:
        print(f"❌ Error loading issue file: {e}", file=sys.stderr)
        return 1
    
    # Create enhanced learner
    learner = EnhancedDiscussionLearner(learning_dir=args.output_dir)
    
    print(f"🚀 Enhanced analysis of issue #{issue_data.get('number', 'unknown')}...")
    
    if args.live_analysis:
        # Live analysis
        comments = issue_data.get('comments', [])
        live_learning = learner.analyze_live_discussion(
            issue_data.get('number', 0),
            comments
        )
        
        print(f"\n📡 Live Learning:")
        print(f"  - Insight: {live_learning.insight_preview}")
        print(f"  - Confidence: {live_learning.confidence:.1%}")
        print(f"  - Suggested Actions: {len(live_learning.suggested_actions)}")
        
        # Save live learning
        live_file = f"{args.output_dir}/live_learning_{issue_data.get('number')}.json"
        with open(live_file, 'w') as f:
            json.dump(live_learning.to_dict(), f, indent=2)
        print(f"  - Saved to: {live_file}")
    else:
        # Full enhanced analysis
        analysis, enhancements = learner.analyze_with_enhancements(issue_data)
        
        # Save analysis
        filepath = learner.save_analysis(analysis)
        
        # Generate enhanced documentation
        doc = learner.generate_enhanced_documentation(analysis, enhancements)
        doc_path = filepath.replace('.json', '.md')
        with open(doc_path, 'w') as f:
            f.write(doc)
        print(f"📄 Generated enhanced documentation: {doc_path}")
        
        # Save enhancements separately
        enhancements_path = filepath.replace('.json', '_enhancements.json')
        with open(enhancements_path, 'w') as f:
            json.dump(enhancements, f, indent=2)
        print(f"🔗 Saved enhancements: {enhancements_path}")
        
        # Print summary
        print(f"\n📊 Enhanced Analysis Complete:")
        print(f"  - Insights extracted: {len(analysis.insights)}")
        print(f"  - Knowledge connections: {len(enhancements['knowledge_connections'])}")
        print(f"  - Proactive suggestions: {len(enhancements['proactive_suggestions'])}")
        print(f"  - Learning quality: {analysis.learning_quality:.1%}")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
