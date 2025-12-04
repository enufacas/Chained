#!/usr/bin/env python3
"""
Tests for Discussion Learning Query API

Comprehensive test suite for the query interface following @create-botter's
innovative infrastructure approach with thorough validation.
"""

import pytest
import json
import os
import tempfile
import shutil
from pathlib import Path
from datetime import datetime, timezone, timedelta

# Add tools directory to path
import sys
tools_dir = os.path.dirname(os.path.abspath(__file__))
if tools_dir not in sys.path:
    sys.path.insert(0, tools_dir)

# Import query module
import importlib.util
spec = importlib.util.spec_from_file_location(
    "discussion_learning_query",
    os.path.join(tools_dir, "discussion-learning-query.py")
)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

DiscussionLearningQuery = module.DiscussionLearningQuery
InsightType = module.InsightType
SortOrder = module.SortOrder
QueryResult = module.QueryResult
LearningSummary = module.LearningSummary


class TestInsightType:
    """Test the InsightType enum."""
    
    def test_all_types_exist(self):
        """Verify all expected insight types exist."""
        assert InsightType.TECHNICAL.value == "technical"
        assert InsightType.PROCESS.value == "process"
        assert InsightType.AGENT_BEHAVIOR.value == "agent_behavior"
        assert InsightType.DECISION.value == "decision"
        assert InsightType.ALL.value == "all"


class TestQueryResult:
    """Test the QueryResult dataclass."""
    
    def test_query_result_creation(self):
        """Test creating a query result."""
        result = QueryResult(
            total_matches=10,
            insights=[{'content': 'test'}],
            query_time_ms=5.5,
            filters_applied={'limit': 10}
        )
        
        assert result.total_matches == 10
        assert len(result.insights) == 1
        assert result.query_time_ms == 5.5
    
    def test_query_result_to_dict(self):
        """Test converting query result to dictionary."""
        result = QueryResult(
            total_matches=5,
            insights=[],
            query_time_ms=1.0,
            filters_applied={}
        )
        
        data = result.to_dict()
        assert isinstance(data, dict)
        assert data['total_matches'] == 5


class TestLearningSummary:
    """Test the LearningSummary dataclass."""
    
    def test_learning_summary_creation(self):
        """Test creating a learning summary."""
        summary = LearningSummary(
            period_start="2024-01-01T00:00:00Z",
            period_end="2024-01-31T00:00:00Z",
            total_discussions=10,
            total_insights=50,
            insights_by_type={'technical': 25, 'decision': 25},
            top_tags=[('python', 10), ('api', 8)],
            average_quality_score=0.75,
            key_decisions=['decision 1', 'decision 2'],
            trending_topics=['python', 'api']
        )
        
        assert summary.total_discussions == 10
        assert summary.total_insights == 50
        assert summary.average_quality_score == 0.75


class TestDiscussionLearningQuery:
    """Test the main DiscussionLearningQuery class."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory with test data."""
        tmpdir = tempfile.mkdtemp()
        
        # Create sample discussion files
        sample_discussions = [
            {
                'issue_number': 1,
                'issue_title': 'Implement new algorithm',
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'learning_quality': 0.8,
                'insights': [
                    {
                        'issue_number': 1,
                        'issue_title': 'Implement new algorithm',
                        'insight_type': 'technical',
                        'content': 'We implemented the algorithm using Python for better performance',
                        'context': 'Algorithm discussion',
                        'participants': ['user1'],
                        'timestamp': datetime.now(timezone.utc).isoformat(),
                        'confidence': 0.85,
                        'tags': ['python', 'algorithm', 'performance']
                    },
                    {
                        'issue_number': 1,
                        'issue_title': 'Implement new algorithm',
                        'insight_type': 'decision',
                        'content': 'We decided to use Python for this implementation',
                        'context': 'Decision context',
                        'participants': ['user2'],
                        'timestamp': datetime.now(timezone.utc).isoformat(),
                        'confidence': 0.9,
                        'tags': ['python', 'decision']
                    }
                ],
                'key_decisions': ['Use Python for implementation']
            },
            {
                'issue_number': 2,
                'issue_title': 'Improve workflow automation',
                'timestamp': (datetime.now(timezone.utc) - timedelta(days=5)).isoformat(),
                'learning_quality': 0.7,
                'insights': [
                    {
                        'issue_number': 2,
                        'issue_title': 'Improve workflow automation',
                        'insight_type': 'process',
                        'content': 'The workflow was improved with automated testing procedures',
                        'context': 'Process improvement',
                        'participants': ['user3'],
                        'timestamp': (datetime.now(timezone.utc) - timedelta(days=5)).isoformat(),
                        'confidence': 0.75,
                        'tags': ['workflow', 'automation', 'testing']
                    }
                ],
                'key_decisions': ['Implement automated testing']
            },
            {
                'issue_number': 3,
                'issue_title': 'Agent collaboration patterns',
                'timestamp': (datetime.now(timezone.utc) - timedelta(days=10)).isoformat(),
                'learning_quality': 0.65,
                'insights': [
                    {
                        'issue_number': 3,
                        'issue_title': 'Agent collaboration patterns',
                        'insight_type': 'agent_behavior',
                        'content': 'The agents showed excellent collaboration and coordination skills',
                        'context': 'Agent behavior analysis',
                        'participants': ['user4'],
                        'timestamp': (datetime.now(timezone.utc) - timedelta(days=10)).isoformat(),
                        'confidence': 0.6,
                        'tags': ['agent', 'collaboration']
                    }
                ],
                'key_decisions': ['Improve agent coordination']
            }
        ]
        
        for i, discussion in enumerate(sample_discussions):
            filepath = os.path.join(
                tmpdir, 
                f"discussion_issue_{discussion['issue_number']}_20240101_00000{i}.json"
            )
            with open(filepath, 'w') as f:
                json.dump(discussion, f)
        
        # Create sample knowledge graph
        kg = {
            'insights': {
                'insight_1_abc': {
                    'content': 'Python is great for algorithms',
                    'confidence': 0.8,
                    'tags': ['python', 'algorithm']
                },
                'insight_2_def': {
                    'content': 'Automation improves workflow efficiency',
                    'confidence': 0.7,
                    'tags': ['automation', 'workflow']
                }
            },
            'connections': [
                {
                    'source_insight_id': 'insight_1_abc',
                    'target_insight_id': 'insight_2_def',
                    'connection_type': 'related',
                    'similarity_score': 0.4
                }
            ],
            'metadata': {
                'total_insights': 2,
                'total_connections': 1
            }
        }
        
        with open(os.path.join(tmpdir, 'knowledge_graph.json'), 'w') as f:
            json.dump(kg, f)
        
        yield tmpdir
        shutil.rmtree(tmpdir)
    
    @pytest.fixture
    def query(self, temp_dir):
        """Create a query instance with test data."""
        return DiscussionLearningQuery(learning_dir=temp_dir)
    
    def test_query_initialization(self, temp_dir):
        """Test query interface initialization."""
        query = DiscussionLearningQuery(learning_dir=temp_dir)
        
        assert query.learning_dir.exists()
        assert isinstance(query.index, dict)
    
    def test_query_all_insights(self, query):
        """Test querying all insights."""
        result = query.query_insights()
        
        assert isinstance(result, QueryResult)
        assert result.total_matches >= 3  # At least 3 insights in test data
        assert len(result.insights) <= 100  # Default limit
    
    def test_query_by_type(self, query):
        """Test filtering insights by type."""
        result = query.query_insights(insight_type=InsightType.TECHNICAL)
        
        assert result.total_matches >= 1
        for insight in result.insights:
            assert insight.get('insight_type') == 'technical'
    
    def test_query_by_tags(self, query):
        """Test filtering insights by tags."""
        result = query.query_insights(tags=['python'])
        
        assert result.total_matches >= 1
        for insight in result.insights:
            assert 'python' in insight.get('tags', [])
    
    def test_query_by_confidence(self, query):
        """Test filtering insights by confidence."""
        result = query.query_insights(min_confidence=0.8)
        
        for insight in result.insights:
            assert insight.get('confidence', 0) >= 0.8
    
    def test_query_with_search_text(self, query):
        """Test text search in insights."""
        result = query.query_insights(search_text='algorithm')
        
        assert result.total_matches >= 1
        for insight in result.insights:
            assert 'algorithm' in insight.get('content', '').lower()
    
    def test_query_with_limit(self, query):
        """Test limiting query results."""
        result = query.query_insights(limit=2)
        
        assert len(result.insights) <= 2
    
    def test_query_sort_by_confidence(self, query):
        """Test sorting by confidence."""
        result = query.query_insights(sort_by=SortOrder.CONFIDENCE_DESC)
        
        if len(result.insights) >= 2:
            for i in range(len(result.insights) - 1):
                assert (result.insights[i].get('confidence', 0) >= 
                        result.insights[i + 1].get('confidence', 0))
    
    def test_get_summary(self, query):
        """Test getting learning summary."""
        summary = query.get_summary(days=30)
        
        assert isinstance(summary, LearningSummary)
        assert summary.total_discussions >= 1
        assert summary.total_insights >= 1
        assert 0.0 <= summary.average_quality_score <= 1.0
        assert isinstance(summary.insights_by_type, dict)
        assert isinstance(summary.top_tags, list)
        assert isinstance(summary.trending_topics, list)
    
    def test_search_knowledge_graph(self, query):
        """Test searching the knowledge graph."""
        results = query.search_knowledge_graph('python algorithm')
        
        assert isinstance(results, list)
        if results:
            for r in results:
                assert 'insight_id' in r
                assert 'similarity_score' in r
    
    def test_get_related_insights(self, query):
        """Test getting related insights."""
        results = query.get_related_insights('insight_1_abc')
        
        assert isinstance(results, list)
        if results:
            for r in results:
                assert 'insight_id' in r
                assert 'connection_type' in r
    
    def test_export_json(self, query):
        """Test exporting learnings as JSON."""
        output = query.export_learnings(format='json', days=30)
        
        data = json.loads(output)
        assert 'total_discussions' in data
        assert 'total_insights' in data
    
    def test_export_markdown(self, query):
        """Test exporting learnings as Markdown."""
        output = query.export_learnings(format='markdown', days=30)
        
        assert '# Discussion Learning Export' in output
        assert 'Statistics' in output
        assert '@create-botter' in output
    
    def test_export_csv(self, query):
        """Test exporting learnings as CSV."""
        output = query.export_learnings(format='csv', days=30)
        
        assert 'metric,value' in output
        assert 'total_discussions' in output
    
    def test_export_invalid_format(self, query):
        """Test that invalid format raises error."""
        with pytest.raises(ValueError):
            query.export_learnings(format='invalid', days=30)
    
    def test_empty_directory(self):
        """Test handling of empty learning directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            query = DiscussionLearningQuery(learning_dir=tmpdir)
            
            result = query.query_insights()
            assert result.total_matches == 0
            assert result.insights == []
    
    def test_query_time_measurement(self, query):
        """Test that query time is measured."""
        result = query.query_insights()
        
        assert result.query_time_ms >= 0
    
    def test_filters_applied_tracking(self, query):
        """Test that applied filters are tracked."""
        result = query.query_insights(
            insight_type=InsightType.TECHNICAL,
            min_confidence=0.5,
            limit=5
        )
        
        assert result.filters_applied['insight_type'] == 'technical'
        assert result.filters_applied['min_confidence'] == 0.5
        assert result.filters_applied['limit'] == 5


class TestQueryIntegration:
    """Integration tests for the complete query workflow."""
    
    @pytest.fixture
    def temp_dir_with_data(self):
        """Create a temporary directory with comprehensive test data."""
        tmpdir = tempfile.mkdtemp()
        
        # Create multiple discussion files with varied data
        for i in range(5):
            discussion = {
                'issue_number': i + 1,
                'issue_title': f'Test issue {i + 1}',
                'timestamp': (datetime.now(timezone.utc) - timedelta(days=i)).isoformat(),
                'learning_quality': 0.5 + (i * 0.1),
                'insights': [
                    {
                        'issue_number': i + 1,
                        'insight_type': ['technical', 'process', 'decision', 'agent_behavior'][i % 4],
                        'content': f'Test insight content {i + 1} about algorithms and performance',
                        'timestamp': (datetime.now(timezone.utc) - timedelta(days=i)).isoformat(),
                        'confidence': 0.6 + (i * 0.05),
                        'tags': ['python', 'algorithm', 'test']
                    }
                ],
                'key_decisions': [f'Decision {i + 1}']
            }
            
            filepath = os.path.join(tmpdir, f'discussion_issue_{i+1}_2024.json')
            with open(filepath, 'w') as f:
                json.dump(discussion, f)
        
        yield tmpdir
        shutil.rmtree(tmpdir)
    
    def test_full_workflow(self, temp_dir_with_data):
        """Test complete query workflow."""
        query = DiscussionLearningQuery(learning_dir=temp_dir_with_data)
        
        # 1. Query all insights
        all_results = query.query_insights()
        assert all_results.total_matches >= 5
        
        # 2. Query specific types
        tech_results = query.query_insights(insight_type=InsightType.TECHNICAL)
        assert tech_results.total_matches >= 1
        
        # 3. Get summary
        summary = query.get_summary(days=30)
        assert summary.total_discussions >= 5
        
        # 4. Export in different formats
        json_export = query.export_learnings(format='json')
        assert json.loads(json_export)
        
        md_export = query.export_learnings(format='markdown')
        assert '# Discussion Learning Export' in md_export
        
        csv_export = query.export_learnings(format='csv')
        assert 'metric,value' in csv_export
        
        print("✅ Full workflow integration test passed!")


def test_main_function():
    """Test the main function structure."""
    assert hasattr(module, 'main')
    assert callable(module.main)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
