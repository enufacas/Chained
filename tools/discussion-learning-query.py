#!/usr/bin/env python3
"""
Discussion Learning Query API - Self-Documenting AI Extension

This module provides a query interface for the self-documenting AI system,
enabling programmatic access to discussion learnings, insights, and patterns.

Author: @create-botter
Approach: Inventive and visionary infrastructure design (Tesla-inspired)

Features:
- Query insights by type, tags, confidence, and date range
- Search knowledge graph for related insights
- Generate learning summaries and statistics
- Export learnings in various formats
"""

import json
import re
import os
import sys
import time
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict, field
from pathlib import Path
from collections import defaultdict, Counter
from enum import Enum


class InsightType(Enum):
    """Types of insights that can be queried."""
    TECHNICAL = "technical"
    PROCESS = "process"
    AGENT_BEHAVIOR = "agent_behavior"
    DECISION = "decision"
    ALL = "all"


class SortOrder(Enum):
    """Sort order for query results."""
    CONFIDENCE_DESC = "confidence_desc"
    CONFIDENCE_ASC = "confidence_asc"
    DATE_DESC = "date_desc"
    DATE_ASC = "date_asc"


@dataclass
class QueryResult:
    """Represents a query result with matched insights."""
    total_matches: int
    insights: List[Dict]
    query_time_ms: float
    filters_applied: Dict[str, Any]
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return asdict(self)


@dataclass
class LearningSummary:
    """Summary of learnings over a time period."""
    period_start: str
    period_end: str
    total_discussions: int
    total_insights: int
    insights_by_type: Dict[str, int]
    top_tags: List[Tuple[str, int]]
    average_quality_score: float
    key_decisions: List[str]
    trending_topics: List[str]
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return asdict(self)


class DiscussionLearningQuery:
    """
    Query interface for discussion learnings.
    
    Provides powerful search and aggregation capabilities over
    the self-documenting AI's knowledge base.
    """
    
    def __init__(self, learning_dir: str = 'learnings/discussions'):
        """
        Initialize the query interface.
        
        Args:
            learning_dir: Directory containing learning files
        """
        self.learning_dir = Path(learning_dir)
        self.cache: Dict[str, Any] = {}
        self._load_index()
    
    def _load_index(self):
        """Load or create the learnings index."""
        index_file = self.learning_dir / 'index.json'
        
        if index_file.exists():
            try:
                with open(index_file, 'r') as f:
                    self.index = json.load(f)
            except Exception as e:
                print(f"Warning: Could not load index: {e}", file=sys.stderr)
                self.index = self._build_index()
        else:
            self.index = self._build_index()
    
    def _build_index(self) -> Dict:
        """Build a fresh index from discussion files."""
        discussions = []
        
        for filepath in sorted(self.learning_dir.glob('discussion_issue_*.json'), reverse=True):
            # Skip enhancement files
            if '_enhancements' in filepath.name:
                continue
            
            try:
                with open(filepath, 'r') as f:
                    data = json.load(f)
                
                discussions.append({
                    'issue_number': data.get('issue_number'),
                    'issue_title': data.get('issue_title', ''),
                    'timestamp': data.get('timestamp', ''),
                    'insights_count': len(data.get('insights', [])),
                    'learning_quality': data.get('learning_quality', 0),
                    'file': str(filepath.name)
                })
            except Exception as e:
                print(f"Warning: Could not load {filepath}: {e}", file=sys.stderr)
        
        return {
            'last_updated': datetime.now(timezone.utc).isoformat(),
            'total_discussions': len(discussions),
            'discussions': discussions[:100]  # Keep last 100
        }
    
    def query_insights(
        self,
        insight_type: InsightType = InsightType.ALL,
        tags: Optional[List[str]] = None,
        min_confidence: float = 0.0,
        max_confidence: float = 1.0,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        search_text: Optional[str] = None,
        sort_by: SortOrder = SortOrder.DATE_DESC,
        limit: int = 100
    ) -> QueryResult:
        """
        Query insights from the learning database.
        
        Args:
            insight_type: Filter by insight type
            tags: Filter by tags (any match)
            min_confidence: Minimum confidence score
            max_confidence: Maximum confidence score
            date_from: Start date (ISO format)
            date_to: End date (ISO format)
            search_text: Text to search in content
            sort_by: Sort order for results
            limit: Maximum number of results
            
        Returns:
            QueryResult with matching insights
        """
        start_time = time.perf_counter()
        matched_insights = []
        
        # Parse date filters
        from_date = None
        to_date = None
        if date_from:
            try:
                from_date = datetime.fromisoformat(date_from.replace('Z', '+00:00'))
            except ValueError:
                pass
        if date_to:
            try:
                to_date = datetime.fromisoformat(date_to.replace('Z', '+00:00'))
            except ValueError:
                pass
        
        # Load and filter insights from all discussion files
        for filepath in self.learning_dir.glob('discussion_issue_*.json'):
            if '_enhancements' in filepath.name:
                continue
            
            try:
                with open(filepath, 'r') as f:
                    data = json.load(f)
                
                for insight in data.get('insights', []):
                    # Apply filters
                    if not self._matches_filters(
                        insight, insight_type, tags, min_confidence, 
                        max_confidence, from_date, to_date, search_text
                    ):
                        continue
                    
                    matched_insights.append(insight)
            except Exception:
                continue
        
        # Sort results
        matched_insights = self._sort_insights(matched_insights, sort_by)
        
        # Apply limit
        total_matches = len(matched_insights)
        matched_insights = matched_insights[:limit]
        
        # Calculate query time using perf_counter for accuracy
        query_time = (time.perf_counter() - start_time) * 1000
        
        # Build result
        return QueryResult(
            total_matches=total_matches,
            insights=matched_insights,
            query_time_ms=round(query_time, 2),
            filters_applied={
                'insight_type': insight_type.value,
                'tags': tags,
                'min_confidence': min_confidence,
                'max_confidence': max_confidence,
                'date_from': date_from,
                'date_to': date_to,
                'search_text': search_text,
                'limit': limit
            }
        )
    
    def _matches_filters(
        self,
        insight: Dict,
        insight_type: InsightType,
        tags: Optional[List[str]],
        min_confidence: float,
        max_confidence: float,
        from_date: Optional[datetime],
        to_date: Optional[datetime],
        search_text: Optional[str]
    ) -> bool:
        """Check if an insight matches all filters."""
        # Type filter
        if insight_type != InsightType.ALL:
            if insight.get('insight_type') != insight_type.value:
                return False
        
        # Tag filter (any match)
        if tags:
            insight_tags = set(insight.get('tags', []))
            if not insight_tags.intersection(set(tags)):
                return False
        
        # Confidence filter
        confidence = insight.get('confidence', 0)
        if confidence < min_confidence or confidence > max_confidence:
            return False
        
        # Date filter
        timestamp = insight.get('timestamp', '')
        if timestamp:
            try:
                insight_date = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                if from_date and insight_date < from_date:
                    return False
                if to_date and insight_date > to_date:
                    return False
            except ValueError:
                pass
        
        # Text search
        if search_text:
            content = insight.get('content', '').lower()
            if search_text.lower() not in content:
                return False
        
        return True
    
    def _sort_insights(
        self, 
        insights: List[Dict], 
        sort_by: SortOrder
    ) -> List[Dict]:
        """Sort insights by the specified order."""
        if sort_by == SortOrder.CONFIDENCE_DESC:
            return sorted(insights, key=lambda x: x.get('confidence', 0), reverse=True)
        elif sort_by == SortOrder.CONFIDENCE_ASC:
            return sorted(insights, key=lambda x: x.get('confidence', 0))
        elif sort_by == SortOrder.DATE_DESC:
            return sorted(insights, key=lambda x: x.get('timestamp', ''), reverse=True)
        elif sort_by == SortOrder.DATE_ASC:
            return sorted(insights, key=lambda x: x.get('timestamp', ''))
        
        return insights
    
    def get_summary(
        self,
        days: int = 30
    ) -> LearningSummary:
        """
        Generate a summary of learnings over a time period.
        
        Args:
            days: Number of days to look back
            
        Returns:
            LearningSummary with aggregated statistics
        """
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
        
        all_insights = []
        all_decisions = []
        quality_scores = []
        discussions_count = 0
        
        for filepath in self.learning_dir.glob('discussion_issue_*.json'):
            if '_enhancements' in filepath.name:
                continue
            
            try:
                with open(filepath, 'r') as f:
                    data = json.load(f)
                
                # Check if within timeframe
                timestamp = data.get('timestamp', '')
                if timestamp:
                    try:
                        file_date = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                        if file_date < cutoff_date:
                            continue
                    except ValueError:
                        pass
                
                # Collect data
                all_insights.extend(data.get('insights', []))
                all_decisions.extend(data.get('key_decisions', []))
                quality_scores.append(data.get('learning_quality', 0))
                discussions_count += 1
                
            except Exception:
                continue
        
        # Calculate statistics
        insights_by_type = defaultdict(int)
        tag_counts = defaultdict(int)
        
        for insight in all_insights:
            if isinstance(insight, dict):
                insights_by_type[insight.get('insight_type', 'unknown')] += 1
                for tag in insight.get('tags', []):
                    tag_counts[tag] += 1
        
        # Get top tags
        top_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        # Calculate average quality
        avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0.0
        
        # Identify trending topics (tags that appear most frequently)
        trending = [tag for tag, _ in top_tags[:5]]
        
        return LearningSummary(
            period_start=(datetime.now(timezone.utc) - timedelta(days=days)).isoformat(),
            period_end=datetime.now(timezone.utc).isoformat(),
            total_discussions=discussions_count,
            total_insights=len(all_insights),
            insights_by_type=dict(insights_by_type),
            top_tags=top_tags,
            average_quality_score=round(avg_quality, 3),
            key_decisions=all_decisions[:20],  # Top 20 decisions
            trending_topics=trending
        )
    
    def search_knowledge_graph(
        self,
        query_text: str,
        limit: int = 10
    ) -> List[Dict]:
        """
        Search the knowledge graph for related insights.
        
        Args:
            query_text: Text to search for
            limit: Maximum results to return
            
        Returns:
            List of matching insights with similarity scores
        """
        # Load knowledge graph
        kg_file = self.learning_dir / 'knowledge_graph.json'
        
        if not kg_file.exists():
            return []
        
        try:
            with open(kg_file, 'r') as f:
                knowledge_graph = json.load(f)
        except Exception:
            return []
        
        # Calculate similarity for each insight
        results = []
        query_words = set(re.findall(r'\w+', query_text.lower()))
        
        for insight_id, insight_data in knowledge_graph.get('insights', {}).items():
            content = insight_data.get('content', '')
            content_words = set(re.findall(r'\w+', content.lower()))
            
            # Jaccard similarity
            if query_words and content_words:
                intersection = query_words.intersection(content_words)
                union = query_words.union(content_words)
                similarity = len(intersection) / len(union) if union else 0.0
                
                if similarity > 0.1:  # Minimum threshold
                    results.append({
                        'insight_id': insight_id,
                        'content': content,
                        'confidence': insight_data.get('confidence', 0),
                        'tags': insight_data.get('tags', []),
                        'similarity_score': round(similarity, 3)
                    })
        
        # Sort by similarity and return top results
        results.sort(key=lambda x: x['similarity_score'], reverse=True)
        return results[:limit]
    
    def get_related_insights(
        self,
        insight_id: str,
        limit: int = 5
    ) -> List[Dict]:
        """
        Get insights related to a specific insight via knowledge graph.
        
        Args:
            insight_id: ID of the source insight
            limit: Maximum related insights to return
            
        Returns:
            List of related insights with connection info
        """
        kg_file = self.learning_dir / 'knowledge_graph.json'
        
        if not kg_file.exists():
            return []
        
        try:
            with open(kg_file, 'r') as f:
                knowledge_graph = json.load(f)
        except Exception:
            return []
        
        # Find connections from this insight
        related = []
        connections = knowledge_graph.get('connections', [])
        insights = knowledge_graph.get('insights', {})
        
        for conn in connections:
            if conn.get('source_insight_id') == insight_id:
                target_id = conn.get('target_insight_id')
                if target_id in insights:
                    related.append({
                        'insight_id': target_id,
                        'content': insights[target_id].get('content', ''),
                        'connection_type': conn.get('connection_type', 'related'),
                        'similarity_score': conn.get('similarity_score', 0)
                    })
        
        # Sort by similarity and return
        related.sort(key=lambda x: x['similarity_score'], reverse=True)
        return related[:limit]
    
    def export_learnings(
        self,
        format: str = 'json',
        days: int = 30
    ) -> str:
        """
        Export learnings in various formats.
        
        Args:
            format: Output format ('json', 'markdown', 'csv')
            days: Number of days to include
            
        Returns:
            Formatted export string
        """
        summary = self.get_summary(days=days)
        
        if format == 'json':
            return json.dumps(summary.to_dict(), indent=2)
        
        elif format == 'markdown':
            md = f"""# Discussion Learning Export

**Period:** {summary.period_start[:10]} to {summary.period_end[:10]}

## Statistics

- **Total Discussions:** {summary.total_discussions}
- **Total Insights:** {summary.total_insights}
- **Average Quality Score:** {summary.average_quality_score:.1%}

## Insights by Type

"""
            for insight_type, count in summary.insights_by_type.items():
                md += f"- **{insight_type.replace('_', ' ').title()}**: {count}\n"
            
            md += "\n## Top Tags\n\n"
            for tag, count in summary.top_tags:
                md += f"- {tag}: {count}\n"
            
            md += "\n## Trending Topics\n\n"
            for topic in summary.trending_topics:
                md += f"- {topic}\n"
            
            md += "\n## Key Decisions\n\n"
            for decision in summary.key_decisions[:10]:
                md += f"- {decision}\n"
            
            md += f"""

---

*Exported on {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}*
*Generated by @create-botter Discussion Learning Query API*
"""
            return md
        
        elif format == 'csv':
            lines = [
                'metric,value',
                f'total_discussions,{summary.total_discussions}',
                f'total_insights,{summary.total_insights}',
                f'average_quality_score,{summary.average_quality_score}'
            ]
            
            for insight_type, count in summary.insights_by_type.items():
                lines.append(f'insights_{insight_type},{count}')
            
            for tag, count in summary.top_tags[:5]:
                lines.append(f'tag_{tag},{count}')
            
            return '\n'.join(lines)
        
        else:
            raise ValueError(f"Unsupported format: {format}")


def main():
    """Main entry point for command-line usage."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Query discussion learnings from the self-documenting AI'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Query command
    query_parser = subparsers.add_parser('query', help='Query insights')
    query_parser.add_argument('--type', choices=['technical', 'process', 'agent_behavior', 'decision', 'all'],
                              default='all', help='Filter by insight type')
    query_parser.add_argument('--tags', nargs='+', help='Filter by tags')
    query_parser.add_argument('--min-confidence', type=float, default=0.0, help='Minimum confidence')
    query_parser.add_argument('--search', help='Text to search')
    query_parser.add_argument('--limit', type=int, default=10, help='Max results')
    
    # Summary command
    summary_parser = subparsers.add_parser('summary', help='Get learning summary')
    summary_parser.add_argument('--days', type=int, default=30, help='Days to include')
    
    # Search command
    search_parser = subparsers.add_parser('search', help='Search knowledge graph')
    search_parser.add_argument('query', help='Search query')
    search_parser.add_argument('--limit', type=int, default=10, help='Max results')
    
    # Export command
    export_parser = subparsers.add_parser('export', help='Export learnings')
    export_parser.add_argument('--format', choices=['json', 'markdown', 'csv'],
                               default='markdown', help='Export format')
    export_parser.add_argument('--days', type=int, default=30, help='Days to include')
    
    # Common args
    parser.add_argument('--learning-dir', default='learnings/discussions',
                        help='Directory containing learning files')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Create query interface
    query = DiscussionLearningQuery(learning_dir=args.learning_dir)
    
    if args.command == 'query':
        # Map CLI argument to InsightType enum with validation
        type_mapping = {
            'technical': InsightType.TECHNICAL,
            'process': InsightType.PROCESS,
            'agent_behavior': InsightType.AGENT_BEHAVIOR,
            'decision': InsightType.DECISION,
            'all': InsightType.ALL
        }
        insight_type = type_mapping.get(args.type, InsightType.ALL)
        
        result = query.query_insights(
            insight_type=insight_type,
            tags=args.tags,
            min_confidence=args.min_confidence,
            search_text=args.search,
            limit=args.limit
        )
        
        print(f"📊 Query Results ({result.total_matches} matches in {result.query_time_ms}ms)")
        print()
        for i, insight in enumerate(result.insights, 1):
            print(f"{i}. [{insight.get('insight_type', 'unknown')}] "
                  f"(confidence: {insight.get('confidence', 0):.1%})")
            print(f"   {insight.get('content', '')[:100]}...")
            if insight.get('tags'):
                print(f"   Tags: {', '.join(insight.get('tags', []))}")
            print()
    
    elif args.command == 'summary':
        summary = query.get_summary(days=args.days)
        
        print(f"📈 Learning Summary (Last {args.days} Days)")
        print(f"{'='*50}")
        print(f"Discussions Analyzed: {summary.total_discussions}")
        print(f"Total Insights: {summary.total_insights}")
        print(f"Average Quality: {summary.average_quality_score:.1%}")
        print()
        print("Insights by Type:")
        for t, count in summary.insights_by_type.items():
            print(f"  - {t}: {count}")
        print()
        print("Top Tags:", ', '.join(t for t, _ in summary.top_tags[:5]))
        print()
        print("Trending Topics:", ', '.join(summary.trending_topics))
    
    elif args.command == 'search':
        results = query.search_knowledge_graph(args.query, limit=args.limit)
        
        print(f"🔍 Search Results for '{args.query}'")
        print()
        for i, result in enumerate(results, 1):
            print(f"{i}. (similarity: {result['similarity_score']:.1%})")
            print(f"   {result['content'][:100]}...")
            print()
    
    elif args.command == 'export':
        output = query.export_learnings(format=args.format, days=args.days)
        print(output)
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
