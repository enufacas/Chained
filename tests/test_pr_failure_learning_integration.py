#!/usr/bin/env python3
"""
Tests for PR Failure Learning Integration

Comprehensive test suite for the pr-failure-learning-integration module
that enables AI agents to learn from historical PR failures.
"""

import json
import pytest
import sys
from pathlib import Path
from datetime import datetime, timezone
from unittest.mock import patch, MagicMock
import tempfile
import shutil

# Add tools directory to path
tools_path = Path(__file__).parent.parent / 'tools'
sys.path.insert(0, str(tools_path))

# Import with fallback for module name issues
try:
    from pr_failure_learning_integration import (
        LearningContext,
        ImprovementChecklist,
        PRFailureLearningIntegration,
        LEARNINGS_DIR,
        INTELLIGENCE_DIR,
        AGENT_PROFILES_DIR
    )
    import pr_failure_learning_integration as integration_module
except ModuleNotFoundError:
    # Try with absolute import
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "pr_failure_learning_integration",
        tools_path / "pr-failure-learning-integration.py"
    )
    integration_module = importlib.util.module_from_spec(spec)
    sys.modules['pr_failure_learning_integration'] = integration_module
    spec.loader.exec_module(integration_module)
    LearningContext = integration_module.LearningContext
    ImprovementChecklist = integration_module.ImprovementChecklist
    PRFailureLearningIntegration = integration_module.PRFailureLearningIntegration
    LEARNINGS_DIR = integration_module.LEARNINGS_DIR
    INTELLIGENCE_DIR = integration_module.INTELLIGENCE_DIR
    AGENT_PROFILES_DIR = integration_module.AGENT_PROFILES_DIR


@pytest.fixture
def temp_learnings_dir(tmp_path):
    """Create a temporary learnings directory structure"""
    learnings_dir = tmp_path / "learnings"
    learnings_dir.mkdir()
    
    intelligence_dir = learnings_dir / "pr_intelligence"
    intelligence_dir.mkdir()
    
    agent_profiles_dir = intelligence_dir / "agent_profiles"
    agent_profiles_dir.mkdir()
    
    return learnings_dir


@pytest.fixture
def sample_failures():
    """Create sample PR failures data"""
    return {
        'failures': [
            {
                'pr_number': 101,
                'title': 'Fix API endpoint',
                'author': 'dev1',
                'agent_specialization': 'engineer-master',
                'failure_type': 'test_failure',
                'check_runs': [{'name': 'pytest', 'conclusion': 'failure'}],
                'files_changed': 5,
                'labels': ['copilot', 'agent:engineer-master']
            },
            {
                'pr_number': 102,
                'title': 'Update docs',
                'author': 'dev2',
                'agent_specialization': 'support-master',
                'failure_type': 'review_rejection',
                'review_comments': [{'body': 'Missing test coverage', 'state': 'CHANGES_REQUESTED'}],
                'files_changed': 2,
                'labels': ['copilot']
            },
            {
                'pr_number': 103,
                'title': 'Large refactor',
                'author': 'dev3',
                'agent_specialization': 'organize-guru',
                'failure_type': 'merge_conflict',
                'files_changed': 50,
                'labels': []
            },
            {
                'pr_number': 104,
                'title': 'CI fix',
                'author': 'dev4',
                'agent_specialization': 'engineer-master',
                'failure_type': 'ci_failure',
                'files_changed': 3,
                'labels': ['agent:engineer-master']
            },
        ],
        'last_updated': datetime.now(timezone.utc).isoformat(),
        'total_count': 4
    }


@pytest.fixture
def sample_patterns():
    """Create sample code patterns data"""
    return {
        'patterns': [
            {
                'pattern_id': 'pr_size_small',
                'pattern_type': 'size',
                'description': 'Small PRs (≤10 files) have 100.0% success rate',
                'success_rate': 1.0,
                'occurrences': 10
            },
            {
                'pattern_id': 'includes_tests',
                'pattern_type': 'file_structure',
                'description': 'PRs including test files have 100.0% success rate',
                'success_rate': 1.0,
                'occurrences': 8
            },
            {
                'pattern_id': 'conventional_commits',
                'pattern_type': 'naming',
                'description': 'PRs with conventional commit format have 100.0% success rate',
                'success_rate': 1.0,
                'occurrences': 12
            }
        ],
        'last_updated': datetime.now(timezone.utc).isoformat(),
        'total_patterns': 3
    }


@pytest.fixture
def integration_with_data(temp_learnings_dir, sample_failures, sample_patterns):
    """Create integration instance with sample data"""
    # Save sample failures
    failures_file = temp_learnings_dir / "pr_failures.json"
    with open(failures_file, 'w') as f:
        json.dump(sample_failures, f)
    
    # Save sample patterns
    patterns_file = temp_learnings_dir / "pr_intelligence" / "code_patterns.json"
    with open(patterns_file, 'w') as f:
        json.dump(sample_patterns, f)
    
    # Patch the module constants
    with patch.object(integration_module, 'LEARNINGS_DIR', temp_learnings_dir):
        with patch.object(integration_module, 'PR_FAILURES_FILE', failures_file):
            with patch.object(integration_module, 'INTELLIGENCE_DIR', temp_learnings_dir / "pr_intelligence"):
                with patch.object(integration_module, 'PATTERNS_FILE', patterns_file):
                    with patch.object(integration_module, 'AGENT_LEARNING_TRACKER_FILE', 
                                     temp_learnings_dir / "pr_intelligence" / "agent_learning_tracker.json"):
                        integration = PRFailureLearningIntegration(verbose=False)
                        # Manually set the loaded data
                        integration.failures = sample_failures['failures']
                        integration.patterns = sample_patterns['patterns']
                        yield integration


class TestLearningContextDataclass:
    """Test LearningContext dataclass"""
    
    def test_creation_with_defaults(self):
        """Test LearningContext creation with default values"""
        context = LearningContext(agent_id='test-agent')
        assert context.agent_id == 'test-agent'
        assert context.issue_number is None
        assert context.proactive_warnings == []
        assert context.recommended_approach == []
        assert context.past_failures_count == 0
        assert context.confidence_score == 0.5
        assert context.generated_at != ""
    
    def test_creation_with_all_fields(self):
        """Test LearningContext with all fields specified"""
        context = LearningContext(
            agent_id='engineer-master',
            issue_number=123,
            proactive_warnings=['Warning 1', 'Warning 2'],
            recommended_approach=['Approach 1'],
            success_patterns=['Pattern 1'],
            past_failures_count=5,
            past_rejections_count=3,
            improvement_trajectory='improving',
            confidence_score=0.8,
            generated_at='2025-11-25T00:00:00+00:00'
        )
        assert context.agent_id == 'engineer-master'
        assert context.issue_number == 123
        assert len(context.proactive_warnings) == 2
        assert context.past_failures_count == 5
        assert context.improvement_trajectory == 'improving'
    
    def test_to_dict(self):
        """Test LearningContext serialization to dict"""
        context = LearningContext(
            agent_id='test',
            proactive_warnings=['Warning']
        )
        data = context.to_dict()
        assert isinstance(data, dict)
        assert data['agent_id'] == 'test'
        assert data['proactive_warnings'] == ['Warning']
    
    def test_to_json(self):
        """Test LearningContext serialization to JSON"""
        context = LearningContext(agent_id='test')
        json_str = context.to_json()
        assert isinstance(json_str, str)
        parsed = json.loads(json_str)
        assert parsed['agent_id'] == 'test'
    
    def test_to_markdown(self):
        """Test LearningContext markdown generation"""
        context = LearningContext(
            agent_id='engineer-master',
            proactive_warnings=['You have 3 past failures'],
            recommended_approach=['Follow conventions'],
            success_patterns=['Small PRs succeed more']
        )
        markdown = context.to_markdown()
        assert '### ⚠️ Proactive Warnings' in markdown
        assert '@engineer-master' in markdown
        assert '### ✅ Recommended Approach' in markdown
        assert '### 🎯 Success Patterns' in markdown


class TestImprovementChecklistDataclass:
    """Test ImprovementChecklist dataclass"""
    
    def test_creation_with_defaults(self):
        """Test ImprovementChecklist creation with defaults"""
        checklist = ImprovementChecklist(agent_id='test')
        assert checklist.agent_id == 'test'
        assert checklist.checklist_items == []
        assert checklist.priority_focus == []
    
    def test_to_dict(self):
        """Test ImprovementChecklist serialization"""
        checklist = ImprovementChecklist(
            agent_id='test',
            checklist_items=[{'text': 'Item 1', 'priority': 'high'}]
        )
        data = checklist.to_dict()
        assert data['agent_id'] == 'test'
        assert len(data['checklist_items']) == 1
    
    def test_to_markdown(self):
        """Test ImprovementChecklist markdown generation"""
        checklist = ImprovementChecklist(
            agent_id='test',
            checklist_items=[
                {'text': 'Run tests', 'priority': 'high'},
                {'text': 'Update docs', 'priority': 'medium'}
            ],
            priority_focus=['Focus on testing']
        )
        markdown = checklist.to_markdown()
        assert '## 📋 Pre-Submission Checklist' in markdown
        assert '🎯 Focus on testing' in markdown
        assert '🔴 Run tests' in markdown
        assert '🟡 Update docs' in markdown


class TestPRFailureLearningIntegration:
    """Test PRFailureLearningIntegration main class"""
    
    def test_initialization(self, temp_learnings_dir):
        """Test integration initialization"""
        with patch.object(integration_module, 'LEARNINGS_DIR', temp_learnings_dir):
            with patch.object(integration_module, 'INTELLIGENCE_DIR', temp_learnings_dir / "pr_intelligence"):
                integration = PRFailureLearningIntegration(verbose=False)
                assert integration is not None
    
    def test_get_agent_failures_by_specialization(self, integration_with_data):
        """Test getting failures by agent specialization"""
        failures = integration_with_data.get_agent_failures('engineer-master')
        assert len(failures) == 2  # Two failures with engineer-master specialization
    
    def test_get_agent_failures_empty(self, integration_with_data):
        """Test getting failures for agent with no failures"""
        failures = integration_with_data.get_agent_failures('nonexistent-agent')
        assert len(failures) == 0
    
    def test_generate_learning_context_basic(self, integration_with_data):
        """Test basic learning context generation"""
        context = integration_with_data.generate_learning_context('engineer-master')
        assert context.agent_id == 'engineer-master'
        assert context.past_failures_count == 2
        assert len(context.proactive_warnings) > 0
        assert len(context.recommended_approach) > 0
        assert len(context.success_patterns) > 0
    
    def test_generate_learning_context_with_issue_number(self, integration_with_data):
        """Test learning context with issue number"""
        context = integration_with_data.generate_learning_context(
            'engineer-master',
            issue_number=123
        )
        assert context.issue_number == 123
    
    def test_generate_learning_context_no_failures(self, integration_with_data):
        """Test context for agent with no failures"""
        context = integration_with_data.generate_learning_context('new-agent')
        assert context.past_failures_count == 0
        assert len(context.proactive_warnings) == 0
        # Should still have recommendations and patterns
        assert len(context.recommended_approach) > 0
        assert len(context.success_patterns) > 0


class TestProactiveWarnings:
    """Test proactive warning generation"""
    
    def test_warnings_for_review_rejections(self, integration_with_data):
        """Test warnings when agent has review rejections"""
        context = integration_with_data.generate_learning_context('support-master')
        # support-master has 1 review rejection
        assert any('review rejection' in w.lower() or 'rejection' in w.lower() 
                  for w in context.proactive_warnings)
    
    def test_warnings_for_test_failures(self, integration_with_data):
        """Test warnings when agent has test failures"""
        context = integration_with_data.generate_learning_context('engineer-master')
        # engineer-master has test failures
        assert any('test' in w.lower() for w in context.proactive_warnings)
    
    def test_warnings_for_merge_conflicts(self, integration_with_data):
        """Test warnings for merge conflicts"""
        context = integration_with_data.generate_learning_context('organize-guru')
        # organize-guru has merge conflict and large PR
        assert any('conflict' in w.lower() or 'large' in w.lower() 
                  for w in context.proactive_warnings)


class TestSuccessPatterns:
    """Test success pattern generation"""
    
    def test_success_patterns_from_data(self, integration_with_data):
        """Test that success patterns come from pattern data"""
        context = integration_with_data.generate_learning_context('test-agent')
        # Should include patterns from the sample data
        assert any('10 files' in p for p in context.success_patterns)
        assert any('test' in p.lower() for p in context.success_patterns)


class TestImprovementChecklist:
    """Test improvement checklist generation"""
    
    def test_generate_checklist_basic(self, integration_with_data):
        """Test basic checklist generation"""
        checklist = integration_with_data.generate_improvement_checklist('engineer-master')
        assert checklist.agent_id == 'engineer-master'
        assert len(checklist.checklist_items) > 0
        assert len(checklist.priority_focus) > 0
    
    def test_checklist_prioritizes_based_on_failures(self, integration_with_data):
        """Test that checklist prioritizes based on agent's failures"""
        checklist = integration_with_data.generate_improvement_checklist('engineer-master')
        
        # engineer-master has test and CI failures, so those should be high priority
        test_item = next(
            (item for item in checklist.checklist_items 
             if 'test' in item['text'].lower()),
            None
        )
        assert test_item is not None
        assert test_item['priority'] == 'high'
    
    def test_checklist_low_priority_for_no_history(self, integration_with_data):
        """Test that items are lower priority for agents with no issues"""
        checklist = integration_with_data.generate_improvement_checklist('new-agent')
        
        # Should still have items but with appropriate priorities
        assert len(checklist.checklist_items) > 0


class TestLearningTracker:
    """Test learning tracker functionality"""
    
    def test_track_pr_outcome_success(self, integration_with_data, temp_learnings_dir):
        """Test tracking a successful PR outcome"""
        with patch.object(integration_module, 'AGENT_LEARNING_TRACKER_FILE',
                         temp_learnings_dir / "pr_intelligence" / "agent_learning_tracker.json"):
            integration_with_data.track_pr_outcome(
                agent_id='test-agent',
                pr_number=200,
                success=True
            )
            
            stats = integration_with_data.get_agent_learning_stats('test-agent')
            assert stats['total_tracked'] >= 1
            assert stats['success_rate'] > 0
    
    def test_track_pr_outcome_failure(self, integration_with_data, temp_learnings_dir):
        """Test tracking a failed PR outcome"""
        with patch.object(integration_module, 'AGENT_LEARNING_TRACKER_FILE',
                         temp_learnings_dir / "pr_intelligence" / "agent_learning_tracker.json"):
            integration_with_data.track_pr_outcome(
                agent_id='test-agent',
                pr_number=201,
                success=False,
                failure_type='test_failure'
            )
            
            stats = integration_with_data.get_agent_learning_stats('test-agent')
            assert 'test_failure' in stats.get('failure_types', {})
    
    def test_get_stats_no_history(self, integration_with_data):
        """Test getting stats for agent with no history"""
        stats = integration_with_data.get_agent_learning_stats('nonexistent-agent')
        assert stats['total_tracked'] == 0
        assert stats['trajectory'] == 'unknown'


class TestImprovementTrajectory:
    """Test improvement trajectory calculation"""
    
    def test_trajectory_improving(self, integration_with_data, temp_learnings_dir):
        """Test detecting improving trajectory"""
        tracker_file = temp_learnings_dir / "pr_intelligence" / "agent_learning_tracker.json"
        
        # Create history with improving trend
        tracker_data = {
            'agents': {
                'improving-agent': {
                    'success_history': [False, False, False, True, True, True],
                    'first_tracked': datetime.now(timezone.utc).isoformat()
                }
            }
        }
        with open(tracker_file, 'w') as f:
            json.dump(tracker_data, f)
        
        with patch.object(integration_module, 'AGENT_LEARNING_TRACKER_FILE', tracker_file):
            integration_with_data.learning_tracker = tracker_data
            trajectory = integration_with_data._calculate_improvement_trajectory('improving-agent')
            assert trajectory == 'improving'
    
    def test_trajectory_declining(self, integration_with_data, temp_learnings_dir):
        """Test detecting declining trajectory"""
        tracker_file = temp_learnings_dir / "pr_intelligence" / "agent_learning_tracker.json"
        
        # Create history with declining trend
        tracker_data = {
            'agents': {
                'declining-agent': {
                    'success_history': [True, True, True, False, False, False],
                    'first_tracked': datetime.now(timezone.utc).isoformat()
                }
            }
        }
        with open(tracker_file, 'w') as f:
            json.dump(tracker_data, f)
        
        with patch.object(integration_module, 'AGENT_LEARNING_TRACKER_FILE', tracker_file):
            integration_with_data.learning_tracker = tracker_data
            trajectory = integration_with_data._calculate_improvement_trajectory('declining-agent')
            assert trajectory == 'declining'


class TestMarkdownOutput:
    """Test markdown output formatting"""
    
    def test_context_markdown_structure(self, integration_with_data):
        """Test that context markdown has proper structure"""
        context = integration_with_data.generate_learning_context('engineer-master')
        markdown = context.to_markdown()
        
        # Should have proper markdown headers
        assert '###' in markdown
        # Should have the agent name
        assert '@engineer-master' in markdown
        # Should have emoji indicators
        assert '⚠️' in markdown or '✅' in markdown or '🎯' in markdown
    
    def test_checklist_markdown_structure(self, integration_with_data):
        """Test that checklist markdown has proper structure"""
        checklist = integration_with_data.generate_improvement_checklist('engineer-master')
        markdown = checklist.to_markdown()
        
        # Should have header
        assert '##' in markdown
        # Should have checkbox format
        assert '- [ ]' in markdown
        # Should have priority indicators
        assert '🔴' in markdown or '🟡' in markdown or '🟢' in markdown


class TestEdgeCases:
    """Test edge cases and error handling"""
    
    def test_empty_failures_list(self, temp_learnings_dir):
        """Test with empty failures list"""
        failures_file = temp_learnings_dir / "pr_failures.json"
        with open(failures_file, 'w') as f:
            json.dump({'failures': [], 'last_updated': None}, f)
        
        with patch.object(integration_module, 'LEARNINGS_DIR', temp_learnings_dir):
            with patch.object(integration_module, 'PR_FAILURES_FILE', failures_file):
                with patch.object(integration_module, 'INTELLIGENCE_DIR', temp_learnings_dir / "pr_intelligence"):
                    integration = PRFailureLearningIntegration()
                    context = integration.generate_learning_context('any-agent')
                    assert context.past_failures_count == 0
    
    def test_missing_patterns_file(self, temp_learnings_dir):
        """Test with missing patterns file"""
        with patch.object(integration_module, 'LEARNINGS_DIR', temp_learnings_dir):
            with patch.object(integration_module, 'INTELLIGENCE_DIR', temp_learnings_dir / "pr_intelligence"):
                with patch.object(integration_module, 'PATTERNS_FILE', temp_learnings_dir / "nonexistent.json"):
                    integration = PRFailureLearningIntegration()
                    # Should still work with default patterns
                    context = integration.generate_learning_context('test-agent')
                    assert len(context.success_patterns) > 0
    
    def test_malformed_failure_data(self, temp_learnings_dir):
        """Test handling of malformed failure data"""
        failures_file = temp_learnings_dir / "pr_failures.json"
        with open(failures_file, 'w') as f:
            json.dump({'failures': [{'pr_number': 1}]}, f)  # Minimal data
        
        with patch.object(integration_module, 'LEARNINGS_DIR', temp_learnings_dir):
            with patch.object(integration_module, 'PR_FAILURES_FILE', failures_file):
                with patch.object(integration_module, 'INTELLIGENCE_DIR', temp_learnings_dir / "pr_intelligence"):
                    integration = PRFailureLearningIntegration()
                    # Should not crash
                    context = integration.generate_learning_context('any-agent')
                    assert context is not None


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
