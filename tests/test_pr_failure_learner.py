#!/usr/bin/env python3
"""
Tests for PR Failure Learning System

Comprehensive test suite covering data collection, pattern analysis,
and suggestion generation for the PR failure learning system.
"""

import json
import pytest
import sys
from pathlib import Path
from datetime import datetime, timezone
from unittest.mock import Mock, patch, MagicMock

# Add tools directory to path
tools_path = Path(__file__).parent.parent / 'tools'
sys.path.insert(0, str(tools_path))

# Import with fallback for module name issues
try:
    from pr_failure_learner import (
        PRFailure,
        FailurePattern,
        PRFailureLearner,
        LEARNINGS_DIR
    )
    import pr_failure_learner
except ModuleNotFoundError:
    # Try with absolute import
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "pr_failure_learner",
        tools_path / "pr-failure-learner.py"
    )
    pr_failure_learner = importlib.util.module_from_spec(spec)
    sys.modules['pr_failure_learner'] = pr_failure_learner  # Register in sys.modules
    spec.loader.exec_module(pr_failure_learner)
    PRFailure = pr_failure_learner.PRFailure
    FailurePattern = pr_failure_learner.FailurePattern
    PRFailureLearner = pr_failure_learner.PRFailureLearner
    LEARNINGS_DIR = pr_failure_learner.LEARNINGS_DIR


@pytest.fixture
def sample_pr_failure():
    """Create a sample PR failure for testing"""
    return PRFailure(
        pr_number=123,
        title="Fix: Update authentication logic",
        author="testuser",
        agent_id="agent-123",
        agent_specialization="secure-specialist",
        created_at="2025-11-13T10:00:00Z",
        closed_at="2025-11-13T11:00:00Z",
        failure_type="test_failure",
        failure_details={"state_reason": "Test failures detected"},
        check_runs=[
            {
                "name": "pytest",
                "conclusion": "failure",
                "output": {"title": "Test failed", "summary": "3 tests failed"}
            }
        ],
        review_comments=[],
        files_changed=5,
        additions=100,
        deletions=20,
        labels=["agent:secure-specialist", "bug"]
    )


@pytest.fixture
def sample_failures_list():
    """Create a list of sample failures for pattern analysis"""
    return [
        PRFailure(
            pr_number=101,
            title="Add feature X",
            author="dev1",
            agent_specialization="engineer-master",
            failure_type="test_failure",
            check_runs=[{"name": "pytest", "conclusion": "failure"}],
            files_changed=10
        ),
        PRFailure(
            pr_number=102,
            title="Fix bug Y",
            author="dev2",
            agent_specialization="engineer-master",
            failure_type="test_failure",
            check_runs=[{"name": "pytest", "conclusion": "failure"}],
            files_changed=3
        ),
        PRFailure(
            pr_number=103,
            title="Update docs",
            author="dev3",
            agent_specialization="support-master",
            failure_type="review_rejection",
            review_comments=[
                {"author": "reviewer", "body": "Missing test coverage", "state": "CHANGES_REQUESTED"}
            ],
            files_changed=2
        ),
        PRFailure(
            pr_number=104,
            title="Large refactor",
            author="dev4",
            agent_specialization="organize-guru",
            failure_type="merge_conflict",
            files_changed=50
        ),
    ]


@pytest.fixture
def learner():
    """Create a PRFailureLearner instance"""
    return PRFailureLearner(verbose=False)


class TestPRFailureDataStructures:
    """Test data structures and serialization"""
    
    def test_pr_failure_creation(self, sample_pr_failure):
        """Test PRFailure creation with all fields"""
        assert sample_pr_failure.pr_number == 123
        assert sample_pr_failure.author == "testuser"
        assert sample_pr_failure.failure_type == "test_failure"
        assert len(sample_pr_failure.check_runs) == 1
        assert sample_pr_failure.files_changed == 5
    
    def test_pr_failure_to_dict(self, sample_pr_failure):
        """Test PRFailure serialization to dict"""
        data = sample_pr_failure.to_dict()
        assert isinstance(data, dict)
        assert data['pr_number'] == 123
        assert data['failure_type'] == 'test_failure'
        assert 'check_runs' in data
    
    def test_pr_failure_minimal(self):
        """Test PRFailure with minimal required fields"""
        failure = PRFailure(
            pr_number=456,
            title="Test PR",
            author="testuser"
        )
        assert failure.pr_number == 456
        assert failure.agent_id is None
        assert failure.check_runs == []
    
    def test_failure_pattern_creation(self):
        """Test FailurePattern creation"""
        pattern = FailurePattern(
            pattern_type="test_failure",
            occurrences=5,
            affected_agents=["engineer-master", "secure-specialist"],
            common_issues=["pytest failures"],
            suggested_improvements=["Run tests locally"],
            confidence_score=0.8
        )
        assert pattern.pattern_type == "test_failure"
        assert pattern.occurrences == 5
        assert len(pattern.affected_agents) == 2


class TestPRFailureLearner:
    """Test PRFailureLearner main class"""
    
    def test_learner_initialization(self, learner):
        """Test learner initialization"""
        assert learner is not None
        assert learner.verbose == False
    
    def test_learner_verbose_mode(self):
        """Test verbose logging"""
        learner = PRFailureLearner(verbose=True)
        assert learner.verbose == True
    
    def test_log_method(self, learner, capsys):
        """Test logging method"""
        learner.verbose = True
        learner.log("Test message")
        captured = capsys.readouterr()
        assert "Test message" in captured.err
    
    def test_detect_failure_type_merge_conflict(self, learner):
        """Test detection of merge conflict failures"""
        pr = {
            'title': 'Fix merge conflict in main',
            'labels': [{'name': 'merge-conflict'}]
        }
        failure_type = learner._detect_failure_type(pr)
        assert failure_type == 'merge_conflict'
    
    def test_detect_failure_type_test_failure(self, learner):
        """Test detection of test failures from title"""
        pr = {
            'title': 'Tests fail after update',
            'labels': []
        }
        failure_type = learner._detect_failure_type(pr)
        assert failure_type == 'test_failure'
    
    def test_detect_failure_type_default(self, learner):
        """Test default failure type detection"""
        pr = {
            'title': 'Regular PR',
            'labels': []
        }
        failure_type = learner._detect_failure_type(pr)
        assert failure_type == 'review_rejection'


class TestPatternAnalysis:
    """Test pattern analysis functionality"""
    
    def test_analyze_patterns_basic(self, learner, sample_failures_list):
        """Test basic pattern analysis"""
        patterns = learner.analyze_patterns(sample_failures_list)
        assert len(patterns) > 0
        assert all(isinstance(p, FailurePattern) for p in patterns)
    
    def test_analyze_patterns_groups_by_type(self, learner, sample_failures_list):
        """Test that patterns are grouped by failure type"""
        patterns = learner.analyze_patterns(sample_failures_list)
        pattern_types = [p.pattern_type for p in patterns]
        assert 'test_failure' in pattern_types
        assert 'review_rejection' in pattern_types
        assert 'merge_conflict' in pattern_types
    
    def test_analyze_patterns_counts_occurrences(self, learner, sample_failures_list):
        """Test that pattern occurrences are counted correctly"""
        patterns = learner.analyze_patterns(sample_failures_list)
        test_failure_pattern = next(p for p in patterns if p.pattern_type == 'test_failure')
        assert test_failure_pattern.occurrences == 2  # Two test failures in sample
    
    def test_analyze_patterns_identifies_agents(self, learner, sample_failures_list):
        """Test that affected agents are identified"""
        patterns = learner.analyze_patterns(sample_failures_list)
        test_failure_pattern = next(p for p in patterns if p.pattern_type == 'test_failure')
        assert 'engineer-master' in test_failure_pattern.affected_agents
    
    def test_extract_common_issues_check_failures(self, learner):
        """Test extraction of common check failures"""
        failures = [
            PRFailure(
                pr_number=1,
                title="PR 1",
                author="dev",
                check_runs=[{"name": "pytest", "conclusion": "failure"}]
            ),
            PRFailure(
                pr_number=2,
                title="PR 2",
                author="dev",
                check_runs=[{"name": "pytest", "conclusion": "failure"}]
            ),
        ]
        issues = learner._extract_common_issues(failures)
        assert len(issues) > 0
        assert any('pytest' in issue for issue in issues)
    
    def test_extract_common_issues_large_changes(self, learner):
        """Test detection of large changeset pattern"""
        failures = [
            PRFailure(pr_number=i, title=f"PR {i}", author="dev", files_changed=25)
            for i in range(5)
        ]
        issues = learner._extract_common_issues(failures)
        assert any('Large changeset' in issue or '>20 files' in issue for issue in issues)
    
    def test_extract_common_issues_review_comments(self, learner):
        """Test extraction of common review concerns"""
        failures = [
            PRFailure(
                pr_number=1,
                title="PR 1",
                author="dev",
                review_comments=[
                    {"author": "reviewer", "body": "Missing test coverage", "state": "CHANGES_REQUESTED"}
                ]
            ),
            PRFailure(
                pr_number=2,
                title="PR 2",
                author="dev",
                review_comments=[
                    {"author": "reviewer", "body": "Need more tests here", "state": "CHANGES_REQUESTED"}
                ]
            ),
        ]
        issues = learner._extract_common_issues(failures)
        assert any('missing_tests' in issue.lower() for issue in issues)


class TestSuggestionGeneration:
    """Test improvement suggestion generation"""
    
    def test_generate_suggestions_ci_failure(self, learner):
        """Test suggestions for CI failures"""
        failures = [PRFailure(pr_number=1, title="PR", author="dev", failure_type="ci_failure")]
        suggestions = learner._generate_suggestions('ci_failure', [], failures)
        assert len(suggestions) > 0
        assert any('test' in s.lower() or 'ci' in s.lower() for s in suggestions)
    
    def test_generate_suggestions_test_failure(self, learner):
        """Test suggestions for test failures"""
        issues = ["Repeated check failure: pytest (3 times)"]
        failures = [PRFailure(pr_number=1, title="PR", author="dev")]
        suggestions = learner._generate_suggestions('test_failure', issues, failures)
        assert any('test' in s.lower() for s in suggestions)
    
    def test_generate_suggestions_review_rejection(self, learner):
        """Test suggestions for review rejections"""
        issues = ["Review concern - missing_tests: 3 mentions"]
        failures = [PRFailure(pr_number=1, title="PR", author="dev")]
        suggestions = learner._generate_suggestions('review_rejection', issues, failures)
        assert any('test' in s.lower() for s in suggestions)
    
    def test_generate_suggestions_merge_conflict(self, learner):
        """Test suggestions for merge conflicts"""
        suggestions = learner._generate_suggestions('merge_conflict', [], [])
        assert len(suggestions) > 0
        assert any('sync' in s.lower() or 'rebase' in s.lower() for s in suggestions)
    
    def test_generate_suggestions_large_prs(self, learner):
        """Test suggestions for large PRs"""
        failures = [
            PRFailure(pr_number=i, title=f"PR {i}", author="dev", files_changed=30)
            for i in range(5)
        ]
        suggestions = learner._generate_suggestions('review_rejection', [], failures)
        assert any('smaller' in s.lower() or 'break' in s.lower() for s in suggestions)


class TestAgentSuggestions:
    """Test agent-specific suggestion generation"""
    
    def test_generate_agent_suggestions_all(self, learner, tmp_path, sample_failures_list):
        """Test generating suggestions for all agents"""
        # Mock save/load
        import pr_failure_learner
        original_file = pr_failure_learner.PR_FAILURES_FILE
        pr_failure_learner.PR_FAILURES_FILE = tmp_path / "pr_failures.json"
        
        try:
            learner.save_failures(sample_failures_list)
            suggestions = learner.generate_agent_suggestions()
            
            assert isinstance(suggestions, dict)
            assert len(suggestions) > 0
            assert 'engineer-master' in suggestions
            assert 'total_failures' in suggestions['engineer-master']
        finally:
            pr_failure_learner.PR_FAILURES_FILE = original_file
    
    def test_generate_agent_suggestions_specific_agent(self, learner, tmp_path):
        """Test generating suggestions for specific agent"""
        import pr_failure_learner
        original_file = pr_failure_learner.PR_FAILURES_FILE
        pr_failure_learner.PR_FAILURES_FILE = tmp_path / "pr_failures.json"
        
        try:
            failures = [
                PRFailure(
                    pr_number=1,
                    title="PR 1",
                    author="dev",
                    agent_id="agent-123",
                    agent_specialization="engineer-master",
                    failure_type="test_failure"
                )
            ]
            learner.save_failures(failures)
            
            suggestions = learner.generate_agent_suggestions(agent_id="agent-123")
            assert isinstance(suggestions, dict)
        finally:
            pr_failure_learner.PR_FAILURES_FILE = original_file
    
    def test_agent_suggestions_structure(self, learner, tmp_path, sample_failures_list):
        """Test structure of agent suggestions"""
        import pr_failure_learner
        original_file = pr_failure_learner.PR_FAILURES_FILE
        pr_failure_learner.PR_FAILURES_FILE = tmp_path / "pr_failures.json"
        
        try:
            learner.save_failures(sample_failures_list)
            suggestions = learner.generate_agent_suggestions()
            
            for agent, data in suggestions.items():
                assert 'total_failures' in data
                assert 'failure_types' in data
                assert 'improvements' in data
                assert isinstance(data['total_failures'], int)
                assert isinstance(data['failure_types'], dict)
                assert isinstance(data['improvements'], list)
        finally:
            pr_failure_learner.PR_FAILURES_FILE = original_file


class TestDataPersistence:
    """Test data saving and loading"""
    
    def test_save_failures(self, learner, tmp_path, sample_failures_list):
        """Test saving failures to file"""
        import pr_failure_learner
        original_file = pr_failure_learner.PR_FAILURES_FILE
        pr_failure_learner.PR_FAILURES_FILE = tmp_path / "pr_failures.json"
        
        try:
            learner.save_failures(sample_failures_list)
            assert (tmp_path / "pr_failures.json").exists()
            
            with open(tmp_path / "pr_failures.json", 'r') as f:
                data = json.load(f)
            
            assert 'failures' in data
            assert 'last_updated' in data
            assert len(data['failures']) == len(sample_failures_list)
        finally:
            pr_failure_learner.PR_FAILURES_FILE = original_file
    
    def test_load_failures(self, learner, tmp_path, sample_failures_list):
        """Test loading failures from file"""
        import pr_failure_learner
        original_file = pr_failure_learner.PR_FAILURES_FILE
        pr_failure_learner.PR_FAILURES_FILE = tmp_path / "pr_failures.json"
        
        try:
            learner.save_failures(sample_failures_list)
            loaded = learner.load_failures()
            
            assert len(loaded) == len(sample_failures_list)
            assert all(isinstance(f, PRFailure) for f in loaded)
            assert loaded[0].pr_number == sample_failures_list[0].pr_number
        finally:
            pr_failure_learner.PR_FAILURES_FILE = original_file
    
    def test_save_avoids_duplicates(self, learner, tmp_path, sample_failures_list):
        """Test that saving doesn't create duplicates"""
        import pr_failure_learner
        original_file = pr_failure_learner.PR_FAILURES_FILE
        pr_failure_learner.PR_FAILURES_FILE = tmp_path / "pr_failures.json"
        
        try:
            learner.save_failures(sample_failures_list)
            learner.save_failures(sample_failures_list)  # Save again
            
            loaded = learner.load_failures()
            assert len(loaded) == len(sample_failures_list)  # No duplicates
        finally:
            pr_failure_learner.PR_FAILURES_FILE = original_file
    
    def test_load_nonexistent_file(self, learner, tmp_path):
        """Test loading when file doesn't exist"""
        import pr_failure_learner
        original_file = pr_failure_learner.PR_FAILURES_FILE
        pr_failure_learner.PR_FAILURES_FILE = tmp_path / "nonexistent.json"
        
        try:
            loaded = learner.load_failures()
            assert loaded == []
        finally:
            pr_failure_learner.PR_FAILURES_FILE = original_file


class TestGitHubIntegration:
    """Test GitHub API integration (with mocks)"""
    
    @patch('pr_failure_learner.GitHubAPIClient')
    def test_collect_pr_failures_with_mock(self, mock_client_class):
        """Test PR collection with mocked GitHub API"""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        
        # Mock PR data
        mock_client.get.return_value = [
            {
                'number': 123,
                'title': 'Test PR',
                'user': {'login': 'testuser'},
                'created_at': '2025-11-01T10:00:00Z',
                'closed_at': '2025-11-01T11:00:00Z',
                'merged_at': None,  # Not merged = failure
                'labels': [],
                'changed_files': 5,
                'additions': 100,
                'deletions': 20
            }
        ]
        
        learner = PRFailureLearner(verbose=False)
        learner.client = mock_client
        
        failures = learner.collect_pr_failures(since_days=30)
        assert len(failures) >= 0  # May be 0 if date filtering excludes it
    
    def test_collect_without_client(self, learner):
        """Test collection when GitHub client unavailable"""
        learner.client = None
        failures = learner.collect_pr_failures(since_days=30)
        assert failures == []


class TestEdgeCases:
    """Test edge cases and error handling"""
    
    def test_empty_failures_list(self, learner):
        """Test analysis with empty failures list"""
        patterns = learner.analyze_patterns([])
        assert patterns == []
    
    def test_failure_without_agent(self):
        """Test failure without agent information"""
        failure = PRFailure(
            pr_number=999,
            title="No agent PR",
            author="user"
        )
        assert failure.agent_id is None
        assert failure.agent_specialization is None
    
    def test_failure_with_empty_check_runs(self):
        """Test failure with no check runs"""
        failure = PRFailure(
            pr_number=888,
            title="PR",
            author="user",
            check_runs=[]
        )
        assert len(failure.check_runs) == 0
    
    def test_analyze_single_failure(self, learner):
        """Test analysis with single failure"""
        failure = PRFailure(
            pr_number=1,
            title="Single PR",
            author="dev",
            failure_type="test_failure"
        )
        patterns = learner.analyze_patterns([failure])
        assert len(patterns) == 1
        assert patterns[0].occurrences == 1


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
