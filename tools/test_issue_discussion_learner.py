#!/usr/bin/env python3
"""
Tests for Issue Discussion Learner

Comprehensive test suite following engineer-master's systematic approach.
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
tools_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'tools')
sys.path.insert(0, tools_dir)

# Import with proper module name
import importlib.util
spec = importlib.util.spec_from_file_location(
    "issue_discussion_learner",
    os.path.join(tools_dir, "issue-discussion-learner.py")
)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

IssueDiscussionLearner = module.IssueDiscussionLearner
DiscussionInsight = module.DiscussionInsight
DiscussionAnalysis = module.DiscussionAnalysis


class TestDiscussionInsight:
    """Test the DiscussionInsight dataclass."""
    
    def test_insight_creation(self):
        """Test creating a discussion insight."""
        insight = DiscussionInsight(
            issue_number=123,
            issue_title="Test Issue",
            insight_type="technical",
            content="This is a test insight about algorithms",
            context="Test context",
            participants=["user1"],
            timestamp="2024-01-01T00:00:00Z",
            confidence=0.8,
            tags=["algorithm", "python"]
        )
        
        assert insight.issue_number == 123
        assert insight.insight_type == "technical"
        assert insight.confidence == 0.8
        assert len(insight.tags) == 2
    
    def test_insight_to_dict(self):
        """Test converting insight to dictionary."""
        insight = DiscussionInsight(
            issue_number=123,
            issue_title="Test",
            insight_type="decision",
            content="Test content",
            context="Context",
            participants=["user1"],
            timestamp="2024-01-01T00:00:00Z",
            confidence=0.7,
            tags=["test"]
        )
        
        data = insight.to_dict()
        assert isinstance(data, dict)
        assert data['issue_number'] == 123
        assert data['confidence'] == 0.7


class TestIssueDiscussionLearner:
    """Test the main IssueDiscussionLearner class."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for tests."""
        tmpdir = tempfile.mkdtemp()
        yield tmpdir
        shutil.rmtree(tmpdir)
    
    @pytest.fixture
    def learner(self, temp_dir):
        """Create a learner instance for testing."""
        return IssueDiscussionLearner(learning_dir=temp_dir)
    
    @pytest.fixture
    def sample_issue_data(self):
        """Create sample issue data for testing."""
        return {
            'number': 42,
            'title': 'Implement new feature for AI learning',
            'body': 'We need to implement a new learning algorithm that improves agent performance',
            'labels': [
                {'name': 'enhancement'},
                {'name': 'ai'}
            ],
            'user': {
                'login': 'test-user'
            },
            'created_at': '2024-01-01T00:00:00Z',
            'comments': [
                {
                    'body': 'I agree with this approach. We should implement the algorithm using Python.',
                    'user': {'login': 'agent1'},
                    'created_at': '2024-01-01T01:00:00Z'
                },
                {
                    'body': 'After careful consideration, we decided to use a neural network approach.',
                    'user': {'login': 'agent2'},
                    'created_at': '2024-01-01T02:00:00Z'
                },
                {
                    'body': 'The implementation showed great performance improvements in testing.',
                    'user': {'login': 'agent3'},
                    'created_at': '2024-01-01T03:00:00Z'
                }
            ]
        }
    
    def test_learner_initialization(self, temp_dir):
        """Test learner initialization."""
        learner = IssueDiscussionLearner(learning_dir=temp_dir)
        
        assert learner.learning_dir.exists()
        assert isinstance(learner.known_patterns, dict)
        assert isinstance(learner.insight_keywords, dict)
    
    def test_extract_participants(self, learner, sample_issue_data):
        """Test extracting participants from issue."""
        participants = learner._extract_participants(
            sample_issue_data,
            sample_issue_data['comments']
        )
        
        assert len(participants) == 4  # issue author + 3 commenters
        assert 'test-user' in participants
        assert 'agent1' in participants
        assert 'agent2' in participants
        assert 'agent3' in participants
    
    def test_calculate_duration(self, learner, sample_issue_data):
        """Test calculating discussion duration."""
        duration = learner._calculate_duration(
            sample_issue_data,
            sample_issue_data['comments']
        )
        
        assert duration == 3.0  # 3 hours
    
    def test_classify_insight_type(self, learner):
        """Test insight type classification."""
        # Technical insight
        tech_text = "We need to implement a new algorithm for performance optimization"
        assert learner._classify_insight_type(tech_text) == 'technical'
        
        # Process insight
        process_text = "Our workflow needs to include automated testing procedures"
        assert learner._classify_insight_type(process_text) == 'process'
        
        # Agent behavior insight
        agent_text = "The agent showed excellent collaboration and coordination skills"
        assert learner._classify_insight_type(agent_text) == 'agent_behavior'
        
        # Decision insight
        decision_text = "We have decided to proceed with the agreed upon approach"
        assert learner._classify_insight_type(decision_text) == 'decision'
    
    def test_calculate_insight_confidence(self, learner):
        """Test confidence score calculation."""
        # High confidence (long, specific, with keywords)
        high_conf_text = "We specifically implemented the algorithm using Python to demonstrate improved performance"
        confidence = learner._calculate_insight_confidence(high_conf_text, 'technical')
        assert confidence > 0.7
        
        # Low confidence (short, vague)
        low_conf_text = "Maybe we could try something"
        confidence = learner._calculate_insight_confidence(low_conf_text, 'technical')
        assert confidence < 0.7
    
    def test_extract_tags(self, learner):
        """Test tag extraction from text."""
        text = "We implemented a Python API using GitHub workflows for agent automation"
        tags = learner._extract_tags(text)
        
        assert 'python' in tags
        assert 'api' in tags
        assert 'github' in tags
        assert 'workflow' in tags
        assert 'agent' in tags
    
    def test_extract_decisions(self, learner):
        """Test extracting key decisions."""
        comments = [
            {
                'body': 'After discussion, we decided to implement the feature using approach A.'
            },
            {
                'body': 'The team agreed to use Python for this implementation.'
            },
            {
                'body': 'We concluded that performance should be the primary concern.'
            }
        ]
        
        decisions = learner._extract_decisions(comments)
        assert len(decisions) >= 2
        assert any('implement' in d.lower() for d in decisions)
    
    def test_analyze_issue_discussion(self, learner, sample_issue_data):
        """Test full issue discussion analysis."""
        analysis = learner.analyze_issue_discussion(sample_issue_data)
        
        # Check basic properties
        assert isinstance(analysis, DiscussionAnalysis)
        assert analysis.issue_number == 42
        assert analysis.issue_title == 'Implement new feature for AI learning'
        assert analysis.total_comments == 3
        assert len(analysis.participants) == 4
        assert analysis.duration_hours == 3.0
        
        # Check insights were extracted
        assert len(analysis.insights) > 0
        
        # Check decisions were extracted
        assert len(analysis.key_decisions) > 0
        
        # Check learning quality score
        assert 0.0 <= analysis.learning_quality <= 1.0
    
    def test_save_analysis(self, learner, sample_issue_data):
        """Test saving analysis to file."""
        analysis = learner.analyze_issue_discussion(sample_issue_data)
        filepath = learner.save_analysis(analysis)
        
        # Check file was created
        assert os.path.exists(filepath)
        
        # Check file contains valid JSON
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        assert data['issue_number'] == 42
        assert data['total_comments'] == 3
        assert 'insights' in data
        assert 'key_decisions' in data
    
    def test_generate_documentation(self, learner, sample_issue_data):
        """Test generating markdown documentation."""
        analysis = learner.analyze_issue_discussion(sample_issue_data)
        doc = learner.generate_documentation(analysis)
        
        # Check documentation contains expected sections
        assert '# Discussion Learning:' in doc
        assert '## 📊 Discussion Metrics' in doc
        assert '## 💡 Key Insights' in doc
        assert '## 📚 Learning Summary' in doc
        
        # Check it includes issue details
        assert '#42' in doc
        assert 'Implement new feature for AI learning' in doc
    
    def test_consolidate_learnings(self, learner, sample_issue_data, temp_dir):
        """Test consolidating multiple discussions."""
        # Create and save multiple analyses
        for i in range(3):
            data = sample_issue_data.copy()
            data['number'] = 100 + i
            analysis = learner.analyze_issue_discussion(data)
            learner.save_analysis(analysis)
        
        # Consolidate learnings
        summary = learner.consolidate_learnings(days=7)
        
        # Check summary
        assert summary['issues_analyzed'] == 3
        assert summary['total_insights'] > 0
        assert 'insight_type_distribution' in summary
        assert 'top_tags' in summary
    
    def test_defensive_programming_empty_data(self, learner):
        """Test handling of empty/malformed data."""
        # Empty issue data
        empty_data = {
            'number': 999,
            'title': 'Empty Issue',
            'comments': []
        }
        
        # Should not crash
        analysis = learner.analyze_issue_discussion(empty_data)
        assert analysis.issue_number == 999
        assert analysis.total_comments == 0
        assert len(analysis.insights) == 0
    
    def test_defensive_programming_missing_fields(self, learner):
        """Test handling of missing fields in data."""
        # Data with missing fields
        incomplete_data = {
            'number': 888,
            # Missing title, body, labels, etc.
            'comments': [
                {
                    # Missing user
                    'body': 'Test comment'
                }
            ]
        }
        
        # Should not crash
        analysis = learner.analyze_issue_discussion(incomplete_data)
        assert analysis.issue_number == 888
        # Should gracefully handle missing data
    
    def test_learning_quality_calculation(self, learner):
        """Test learning quality score calculation."""
        # High quality: many insights, decisions, patterns
        high_quality_insights = [
            DiscussionInsight(
                issue_number=1, issue_title="Test",
                insight_type="technical", content="Test",
                context="", participants=[], timestamp="",
                confidence=0.9, tags=[]
            )
            for _ in range(15)
        ]
        
        score = learner._calculate_learning_quality(
            high_quality_insights,
            ["decision1", "decision2", "decision3"],
            ["pattern1", "pattern2"]
        )
        
        assert score > 0.5  # Should be high quality
        
        # Low quality: few insights
        low_quality_insights = [
            DiscussionInsight(
                issue_number=1, issue_title="Test",
                insight_type="technical", content="Test",
                context="", participants=[], timestamp="",
                confidence=0.3, tags=[]
            )
        ]
        
        score = learner._calculate_learning_quality(
            low_quality_insights, [], []
        )
        
        assert score < 0.3  # Should be low quality


class TestIntegration:
    """Integration tests for the complete workflow."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for tests."""
        tmpdir = tempfile.mkdtemp()
        yield tmpdir
        shutil.rmtree(tmpdir)
    
    def test_full_workflow(self, temp_dir):
        """Test the complete learning workflow."""
        # Create learner
        learner = IssueDiscussionLearner(learning_dir=temp_dir)
        
        # Create comprehensive issue data
        issue_data = {
            'number': 100,
            'title': 'Comprehensive Test Issue',
            'body': 'This issue discusses implementing a new algorithm for agent coordination',
            'labels': [
                {'name': 'enhancement'},
                {'name': 'ai'},
                {'name': 'agents'}
            ],
            'user': {'login': 'test-user'},
            'created_at': '2024-01-01T00:00:00Z',
            'comments': [
                {
                    'body': 'The algorithm should optimize for performance and use Python.',
                    'user': {'login': 'agent1'},
                    'created_at': '2024-01-01T01:00:00Z'
                },
                {
                    'body': 'After analysis, we decided to implement using a neural network approach.',
                    'user': {'login': 'agent2'},
                    'created_at': '2024-01-01T02:00:00Z'
                },
                {
                    'body': 'The testing workflow needs to include automated validation procedures.',
                    'user': {'login': 'agent3'},
                    'created_at': '2024-01-01T03:00:00Z'
                },
                {
                    'body': 'Agent collaboration was excellent, showing great coordination skills.',
                    'user': {'login': 'agent4'},
                    'created_at': '2024-01-01T04:00:00Z'
                }
            ]
        }
        
        # Analyze discussion
        analysis = learner.analyze_issue_discussion(issue_data)
        
        # Verify analysis quality
        assert analysis.issue_number == 100
        assert analysis.total_comments == 4
        assert len(analysis.participants) == 5  # 1 author + 4 commenters
        assert len(analysis.insights) > 0
        
        # Should have different types of insights
        insight_types = {i.insight_type for i in analysis.insights}
        assert len(insight_types) > 1  # Multiple types
        
        # Save analysis
        filepath = learner.save_analysis(analysis)
        assert os.path.exists(filepath)
        
        # Generate documentation
        doc = learner.generate_documentation(analysis)
        assert len(doc) > 500  # Should be substantial
        
        # Save documentation
        doc_path = filepath.replace('.json', '.md')
        with open(doc_path, 'w') as f:
            f.write(doc)
        assert os.path.exists(doc_path)
        
        # Consolidate learnings
        summary = learner.consolidate_learnings(days=7)
        assert summary['issues_analyzed'] == 1
        assert summary['total_insights'] == len(analysis.insights)
        
        print("\n✅ Full workflow test passed!")
        print(f"   - Extracted {len(analysis.insights)} insights")
        print(f"   - Identified {len(analysis.key_decisions)} decisions")
        print(f"   - Learning quality: {analysis.learning_quality:.1%}")


if __name__ == '__main__':
    # Run tests with pytest
    pytest.main([__file__, '-v', '--tb=short'])
