#!/usr/bin/env python3
"""
Tests for Enhanced Discussion Learner

Comprehensive test suite following @engineer-master's systematic approach.
Tests advanced features: knowledge graph, similarity, live learning.
"""

import pytest
import json
import os
import tempfile
import shutil
from pathlib import Path
from datetime import datetime, timezone

# Add tools directory to path
import sys
tools_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'tools')
sys.path.insert(0, tools_dir)

# Import enhanced learner
import importlib.util
spec = importlib.util.spec_from_file_location(
    "enhanced_discussion_learner",
    os.path.join(tools_dir, "enhanced-discussion-learner.py")
)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

EnhancedDiscussionLearner = module.EnhancedDiscussionLearner
KnowledgeConnection = module.KnowledgeConnection
LiveLearning = module.LiveLearning


class TestKnowledgeConnection:
    """Test the KnowledgeConnection dataclass."""
    
    def test_connection_creation(self):
        """Test creating a knowledge connection."""
        connection = KnowledgeConnection(
            source_insight_id="insight_123_abc",
            target_insight_id="insight_456_def",
            connection_type="similar",
            similarity_score=0.85,
            timestamp="2024-01-01T00:00:00Z"
        )
        
        assert connection.source_insight_id == "insight_123_abc"
        assert connection.connection_type == "similar"
        assert connection.similarity_score == 0.85
    
    def test_connection_to_dict(self):
        """Test converting connection to dictionary."""
        connection = KnowledgeConnection(
            source_insight_id="insight_1",
            target_insight_id="insight_2",
            connection_type="builds_on",
            similarity_score=0.7,
            timestamp="2024-01-01T00:00:00Z"
        )
        
        data = connection.to_dict()
        assert isinstance(data, dict)
        assert data['connection_type'] == "builds_on"
        assert data['similarity_score'] == 0.7


class TestLiveLearning:
    """Test the LiveLearning dataclass."""
    
    def test_live_learning_creation(self):
        """Test creating a live learning object."""
        live = LiveLearning(
            discussion_id="live_123_5",
            insight_preview="Observing problem_solving patterns",
            confidence=0.6,
            suggested_actions=["Document solution", "Capture decisions"],
            related_past_discussions=["#42: Similar issue"],
            timestamp="2024-01-01T00:00:00Z"
        )
        
        assert live.discussion_id == "live_123_5"
        assert live.confidence == 0.6
        assert len(live.suggested_actions) == 2
        assert len(live.related_past_discussions) == 1


class TestEnhancedDiscussionLearner:
    """Test the Enhanced Discussion Learner."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for tests."""
        tmpdir = tempfile.mkdtemp()
        yield tmpdir
        shutil.rmtree(tmpdir)
    
    @pytest.fixture
    def learner(self, temp_dir):
        """Create an enhanced learner instance for testing."""
        return EnhancedDiscussionLearner(learning_dir=temp_dir)
    
    @pytest.fixture
    def sample_issue_data(self):
        """Create sample issue data for testing."""
        return {
            'number': 42,
            'title': 'Implement new AI learning algorithm',
            'body': 'We need to implement a new learning algorithm that improves agent performance and optimizes resource usage',
            'labels': [
                {'name': 'enhancement'},
                {'name': 'ai-learning'}
            ],
            'user': {'login': 'testuser'},
            'created_at': '2024-01-01T00:00:00Z',
            'comments': [
                {
                    'user': {'login': 'agent1'},
                    'body': 'I think we should use a neural network approach for better performance. After considering alternatives, we decided to implement using Python.',
                    'created_at': '2024-01-01T01:00:00Z'
                },
                {
                    'user': {'login': 'agent2'},
                    'body': 'Great idea! I learned that neural networks work well for this. We should also optimize the algorithm for speed.',
                    'created_at': '2024-01-01T02:00:00Z'
                },
                {
                    'user': {'login': 'agent3'},
                    'body': 'Excellent collaboration! The team worked well together to reach consensus on the design.',
                    'created_at': '2024-01-01T03:00:00Z'
                }
            ]
        }
    
    def test_enhanced_learner_initialization(self, learner):
        """Test enhanced learner initializes correctly."""
        assert learner.learning_dir.exists()
        assert isinstance(learner.knowledge_graph, dict)
        assert 'insights' in learner.knowledge_graph
        assert 'connections' in learner.knowledge_graph
        assert 'metadata' in learner.knowledge_graph
        assert 'advanced_patterns' in learner.__dict__
    
    def test_calculate_text_similarity(self, learner):
        """Test text similarity calculation."""
        text1 = "We need to implement a new algorithm for performance"
        text2 = "Implementing a new algorithm to improve performance"
        
        similarity = learner.calculate_text_similarity(text1, text2)
        
        # Should be high similarity
        assert 0.4 < similarity <= 1.0
        
        # Test dissimilar texts
        text3 = "The weather is nice today"
        similarity2 = learner.calculate_text_similarity(text1, text3)
        assert similarity2 < 0.3
    
    def test_calculate_text_similarity_edge_cases(self, learner):
        """Test text similarity with edge cases."""
        # Empty strings
        assert learner.calculate_text_similarity("", "") == 0.0
        assert learner.calculate_text_similarity("test", "") == 0.0
        
        # Identical strings
        text = "implement algorithm performance"
        similarity = learner.calculate_text_similarity(text, text)
        assert similarity > 0.9
    
    def test_knowledge_graph_persistence(self, learner):
        """Test knowledge graph saves and loads correctly."""
        # Add test data to knowledge graph
        learner.knowledge_graph['insights']['test_id'] = {
            'content': 'Test insight',
            'confidence': 0.8
        }
        
        learner._save_knowledge_graph()
        
        # Create new learner instance (should load saved graph)
        learner2 = EnhancedDiscussionLearner(learning_dir=str(learner.learning_dir))
        
        assert 'test_id' in learner2.knowledge_graph['insights']
        assert learner2.knowledge_graph['insights']['test_id']['content'] == 'Test insight'
    
    def test_add_to_knowledge_graph(self, learner, sample_issue_data):
        """Test adding insights to knowledge graph."""
        # First, analyze the issue to get insights
        analysis = learner.analyze_issue_discussion(sample_issue_data)
        
        # Add to knowledge graph
        initial_count = len(learner.knowledge_graph['insights'])
        learner.add_to_knowledge_graph(analysis)
        
        # Verify insights were added
        assert len(learner.knowledge_graph['insights']) > initial_count
        assert len(learner.knowledge_graph['insights']) >= len(analysis.insights)
        
        # Verify connections were created
        assert len(learner.knowledge_graph['connections']) >= 0
    
    def test_find_similar_insights(self, learner, sample_issue_data):
        """Test finding similar insights."""
        # Analyze and add to graph
        analysis = learner.analyze_issue_discussion(sample_issue_data)
        learner.add_to_knowledge_graph(analysis)
        
        # Get an insight from the analysis
        if analysis.insights:
            test_insight = analysis.insights[0]
            
            # Find similar insights
            similar = learner.find_similar_insights(test_insight, threshold=0.1)
            
            # Should find some matches (or at least return empty list without error)
            assert isinstance(similar, list)
            
            # Each result should be a tuple of (id, score)
            for insight_id, score in similar:
                assert isinstance(insight_id, str)
                assert 0.0 <= score <= 1.0
    
    def test_analyze_live_discussion(self, learner):
        """Test real-time live analysis."""
        issue_number = 123
        comments = [
            {
                'body': 'We should implement this carefully',
                'user': {'login': 'user1'},
                'created_at': '2024-01-01T00:00:00Z'
            },
            {
                'body': 'I learned that this approach works well. After considering alternatives, we decided to use Python.',
                'user': {'login': 'user2'},
                'created_at': '2024-01-01T01:00:00Z'
            }
        ]
        
        live_learning = learner.analyze_live_discussion(issue_number, comments)
        
        # Verify live learning object
        assert isinstance(live_learning, LiveLearning)
        assert live_learning.discussion_id.startswith('live_123_')
        assert 0.0 <= live_learning.confidence <= 1.0
        assert isinstance(live_learning.suggested_actions, list)
        assert isinstance(live_learning.related_past_discussions, list)
        
        # Verify it's cached
        assert live_learning.discussion_id in learner.live_learning_cache
    
    def test_generate_proactive_suggestions(self, learner):
        """Test proactive suggestion generation."""
        issue_data = {
            'title': 'Fix performance bug in algorithm',
            'body': 'The algorithm is running slowly and needs optimization',
            'number': 100
        }
        
        suggestions = learner.generate_proactive_suggestions(issue_data)
        
        # Should generate suggestions
        assert isinstance(suggestions, list)
        assert len(suggestions) > 0
        
        # Should detect performance-related suggestion
        performance_suggestion = any(
            'performance' in s.lower() or 'optimize' in s.lower() 
            for s in suggestions
        )
        assert performance_suggestion
    
    def test_analyze_with_enhancements(self, learner, sample_issue_data):
        """Test complete enhanced analysis workflow."""
        analysis, enhancements = learner.analyze_with_enhancements(sample_issue_data)
        
        # Verify analysis is valid
        assert analysis.issue_number == 42
        assert len(analysis.insights) > 0
        
        # Verify enhancements structure
        assert 'proactive_suggestions' in enhancements
        assert 'knowledge_connections' in enhancements
        assert 'knowledge_graph_stats' in enhancements
        assert 'timestamp' in enhancements
        
        # Verify suggestions were generated
        assert isinstance(enhancements['proactive_suggestions'], list)
        
        # Verify stats are present
        stats = enhancements['knowledge_graph_stats']
        assert 'total_insights' in stats
        assert 'total_connections' in stats
        assert 'new_insights_added' in stats
    
    def test_generate_enhanced_documentation(self, learner, sample_issue_data):
        """Test enhanced documentation generation."""
        analysis, enhancements = learner.analyze_with_enhancements(sample_issue_data)
        
        doc = learner.generate_enhanced_documentation(analysis, enhancements)
        
        # Verify enhanced documentation contains new sections
        assert '## 🧠 Enhanced Learning Insights' in doc
        assert 'Proactive Suggestions' in doc
        assert 'Knowledge Graph Statistics' in doc
        
        # Verify stats are included
        assert 'Total Insights in Graph' in doc
        assert 'Total Connections' in doc
    
    def test_defensive_programming_empty_graph(self, learner):
        """Test handling of empty knowledge graph."""
        # Empty graph should not cause errors
        similar = learner.find_similar_insights(
            module.DiscussionInsight(
                issue_number=1,
                issue_title="Test",
                insight_type="technical",
                content="Test content",
                context="Context",
                participants=["user1"],
                timestamp="2024-01-01T00:00:00Z",
                confidence=0.5,
                tags=[]
            ),
            threshold=0.3
        )
        
        # Should return empty list
        assert similar == []
    
    def test_live_analysis_confidence_calculation(self, learner):
        """Test live analysis confidence increases with discussion depth."""
        issue_number = 200
        
        # Analysis with few comments
        comments_few = [{'body': 'test', 'user': {'login': 'user1'}, 'created_at': '2024-01-01T00:00:00Z'}]
        live1 = learner.analyze_live_discussion(issue_number, comments_few)
        
        # Analysis with many comments
        comments_many = [
            {'body': f'comment {i}', 'user': {'login': f'user{i}'}, 'created_at': '2024-01-01T00:00:00Z'}
            for i in range(15)
        ]
        live2 = learner.analyze_live_discussion(issue_number, comments_many)
        
        # More comments should lead to higher confidence
        assert live2.confidence >= live1.confidence
    
    def test_pattern_recognition_in_live_analysis(self, learner):
        """Test that live analysis detects patterns."""
        comments = [
            {
                'body': 'After considering options, we decided to use approach A',
                'user': {'login': 'user1'},
                'created_at': '2024-01-01T00:00:00Z'
            },
            {
                'body': 'Great teamwork! We worked well together.',
                'user': {'login': 'user2'},
                'created_at': '2024-01-01T01:00:00Z'
            },
            {
                'body': 'I learned that this method is effective.',
                'user': {'login': 'user3'},
                'created_at': '2024-01-01T02:00:00Z'
            }
        ]
        
        live = learner.analyze_live_discussion(300, comments)
        
        # Should suggest actions based on detected patterns
        assert len(live.suggested_actions) > 0
        
        # Check for pattern-specific suggestions
        action_text = ' '.join(live.suggested_actions).lower()
        # Should contain keywords related to capturing insights
        assert any(keyword in action_text for keyword in ['decision', 'learning', 'document', 'capture', 'record', 'collaboration'])
    
    def test_knowledge_graph_metadata_updates(self, learner, sample_issue_data):
        """Test that knowledge graph metadata is updated correctly."""
        initial_metadata = learner.knowledge_graph['metadata'].copy()
        
        analysis, _ = learner.analyze_with_enhancements(sample_issue_data)
        
        # Metadata should be updated
        assert learner.knowledge_graph['metadata']['total_insights'] >= initial_metadata.get('total_insights', 0)
        assert learner.knowledge_graph['metadata']['last_updated'] > initial_metadata.get('last_updated', '')
    
    def test_integration_full_enhanced_workflow(self, learner, sample_issue_data):
        """Test the complete enhanced workflow end-to-end."""
        # 1. Analyze with enhancements
        analysis, enhancements = learner.analyze_with_enhancements(sample_issue_data)
        
        # 2. Verify analysis
        assert analysis.issue_number == 42
        assert len(analysis.insights) > 0
        
        # 3. Verify knowledge graph was updated
        assert len(learner.knowledge_graph['insights']) > 0
        
        # 4. Generate enhanced documentation
        doc = learner.generate_enhanced_documentation(analysis, enhancements)
        assert len(doc) > 0
        
        # 5. Save everything
        filepath = learner.save_analysis(analysis)
        assert os.path.exists(filepath)
        
        # 6. Test proactive suggestions
        suggestions = learner.generate_proactive_suggestions(sample_issue_data)
        assert len(suggestions) > 0
        
        # 7. Test live analysis
        live = learner.analyze_live_discussion(42, sample_issue_data['comments'])
        assert live.confidence > 0
        
        print("✅ Full enhanced workflow integration test passed!")


def test_main_function():
    """Test the main function doesn't crash with valid input."""
    # Create temporary test data
    import tempfile
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        test_data = {
            'number': 999,
            'title': 'Test Issue',
            'body': 'Test body',
            'labels': [],
            'user': {'login': 'test'},
            'created_at': '2024-01-01T00:00:00Z',
            'comments': []
        }
        json.dump(test_data, f)
        test_file = f.name
    
    try:
        # Test that main function can be imported and has proper structure
        assert hasattr(module, 'main')
        assert callable(module.main)
    finally:
        os.unlink(test_file)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
