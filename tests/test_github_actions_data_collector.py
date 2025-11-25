#!/usr/bin/env python3
"""
Tests for GitHub Actions Data Collector
Created by @create-guru

Comprehensive test suite for the GitHub Actions workflow data collector.
"""

import sys
import os
import json
import tempfile
import shutil
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add tools directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'tools'))

from github_actions_data_collector import (
    GitHubActionsDataCollector,
    WorkflowRunData
)


class TestGitHubActionsDataCollector:
    """Test suite for GitHub Actions Data Collector."""
    
    def __init__(self):
        self.temp_dir = None
        self.test_results = []
    
    def setup(self):
        """Setup test environment."""
        self.temp_dir = tempfile.mkdtemp()
        # Create .git directory to simulate repo
        git_dir = Path(self.temp_dir) / '.git'
        git_dir.mkdir(parents=True)
        print(f"✓ Test environment created at {self.temp_dir}")
    
    def teardown(self):
        """Cleanup test environment."""
        if self.temp_dir and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
            print(f"✓ Test environment cleaned up")
    
    def test_initialization(self):
        """Test collector initialization."""
        print("\n🧪 Testing collector initialization...")
        
        collector = GitHubActionsDataCollector(
            repo_root=self.temp_dir,
            owner='test-owner',
            repo='test-repo'
        )
        
        assert collector.repo_root == Path(self.temp_dir)
        assert collector.owner == 'test-owner'
        assert collector.repo == 'test-repo'
        
        print("  ✓ Collector initialized successfully")
        self.test_results.append(("initialization", True))
    
    def test_workflow_run_data_creation(self):
        """Test WorkflowRunData dataclass."""
        print("\n🧪 Testing WorkflowRunData creation...")
        
        now = datetime.now(timezone.utc)
        
        run_data = WorkflowRunData(
            workflow_name="test-workflow",
            workflow_id=123,
            run_id=456,
            run_number=1,
            status="completed",
            conclusion="success",
            start_time=now - timedelta(minutes=5),
            end_time=now,
            duration_seconds=300,
            event="push",
            branch="main",
            actor="test-user"
        )
        
        assert run_data.workflow_name == "test-workflow"
        assert run_data.workflow_id == 123
        assert run_data.run_id == 456
        assert run_data.duration_seconds == 300
        assert run_data.conclusion == "success"
        
        print("  ✓ WorkflowRunData created successfully")
        self.test_results.append(("workflow_run_data", True))
    
    def test_collection_log_save_and_load(self):
        """Test saving and loading collection log."""
        print("\n🧪 Testing collection log persistence...")
        
        collector = GitHubActionsDataCollector(
            repo_root=self.temp_dir,
            owner='test-owner',
            repo='test-repo'
        )
        
        # Save a collection log entry
        collector._save_collection_log(50, 45)
        
        # Verify file was created
        assert collector.collection_history_file.exists()
        
        # Load and verify contents
        with open(collector.collection_history_file, 'r') as f:
            data = json.load(f)
        
        assert 'collections' in data
        assert len(data['collections']) == 1
        assert data['collections'][0]['runs_fetched'] == 50
        assert data['collections'][0]['runs_recorded'] == 45
        
        # Save another entry
        collector._save_collection_log(30, 28)
        
        with open(collector.collection_history_file, 'r') as f:
            data = json.load(f)
        
        assert len(data['collections']) == 2
        
        print("  ✓ Collection log saved and loaded successfully")
        self.test_results.append(("collection_log", True))
    
    def test_record_to_predictor(self):
        """Test recording runs to the AI predictor."""
        print("\n🧪 Testing recording to AI predictor...")
        
        collector = GitHubActionsDataCollector(
            repo_root=self.temp_dir,
            owner='test-owner',
            repo='test-repo'
        )
        
        # Create test runs
        now = datetime.now(timezone.utc)
        runs = [
            WorkflowRunData(
                workflow_name=f"workflow-{i}",
                workflow_id=100 + i,
                run_id=200 + i,
                run_number=i,
                status="completed",
                conclusion="success",
                start_time=now - timedelta(minutes=10*i + 10),
                end_time=now - timedelta(minutes=10*i),
                duration_seconds=600,
                event="push",
                branch="main",
                actor="test-user"
            )
            for i in range(5)
        ]
        
        # Add a non-completed run that should be skipped
        runs.append(WorkflowRunData(
            workflow_name="incomplete-workflow",
            workflow_id=999,
            run_id=999,
            run_number=999,
            status="in_progress",
            conclusion="unknown",
            start_time=now,
            end_time=None,
            duration_seconds=0,
            event="push",
            branch="main",
            actor="test-user"
        ))
        
        recorded = collector.record_to_predictor(runs)
        
        # Only completed runs should be recorded
        assert recorded == 5
        
        # Verify data in predictor
        if collector.predictor:
            assert len(collector.predictor.execution_history) >= 5
        
        print(f"  ✓ Recorded {recorded} runs to predictor")
        self.test_results.append(("record_to_predictor", True))
    
    @patch('subprocess.run')
    def test_fetch_workflow_runs_mock(self, mock_run):
        """Test fetching workflow runs with mocked gh CLI."""
        print("\n🧪 Testing fetch with mocked gh CLI...")
        
        # Mock gh CLI response
        now = datetime.now(timezone.utc)
        mock_response = json.dumps([
            {
                'workflowName': 'Test Workflow',
                'workflowDatabaseId': 123,
                'databaseId': 456,
                'number': 1,
                'status': 'completed',
                'conclusion': 'success',
                'createdAt': (now - timedelta(minutes=5)).isoformat(),
                'updatedAt': now.isoformat(),
                'event': 'push',
                'headBranch': 'main',
                'actor': {'login': 'test-user'}
            },
            {
                'workflowName': 'Another Workflow',
                'workflowDatabaseId': 124,
                'databaseId': 457,
                'number': 2,
                'status': 'completed',
                'conclusion': 'failure',
                'createdAt': (now - timedelta(minutes=10)).isoformat(),
                'updatedAt': (now - timedelta(minutes=5)).isoformat(),
                'event': 'pull_request',
                'headBranch': 'feature',
                'actor': {'login': 'another-user'}
            }
        ])
        
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout=mock_response
        )
        
        collector = GitHubActionsDataCollector(
            repo_root=self.temp_dir,
            owner='test-owner',
            repo='test-repo'
        )
        
        runs = collector.fetch_workflow_runs(limit=10)
        
        assert len(runs) == 2
        assert runs[0].workflow_name == 'Test Workflow'
        assert runs[0].conclusion == 'success'
        assert runs[1].workflow_name == 'Another Workflow'
        assert runs[1].conclusion == 'failure'
        
        print(f"  ✓ Fetched {len(runs)} workflow runs from mocked API")
        self.test_results.append(("fetch_workflow_runs", True))
    
    def test_get_workflow_stats_empty(self):
        """Test getting stats when no data exists."""
        print("\n🧪 Testing stats with no data...")
        
        # Use a fresh temp directory to ensure no data exists
        import tempfile
        fresh_temp_dir = tempfile.mkdtemp()
        fresh_git_dir = Path(fresh_temp_dir) / '.git'
        fresh_git_dir.mkdir(parents=True)
        
        try:
            collector = GitHubActionsDataCollector(
                repo_root=fresh_temp_dir,
                owner='test-owner',
                repo='test-repo'
            )
            
            stats = collector.get_workflow_stats()
            
            assert 'status' in stats
            assert stats['status'] == 'no_data'
            
            print("  ✓ Empty stats handled correctly")
            self.test_results.append(("empty_stats", True))
        finally:
            shutil.rmtree(fresh_temp_dir)
    
    def test_get_workflow_stats_with_data(self):
        """Test getting stats after recording data."""
        print("\n🧪 Testing stats with recorded data...")
        
        collector = GitHubActionsDataCollector(
            repo_root=self.temp_dir,
            owner='test-owner',
            repo='test-repo'
        )
        
        # Record some test data
        now = datetime.now(timezone.utc)
        runs = [
            WorkflowRunData(
                workflow_name="test-workflow-1",
                workflow_id=100,
                run_id=200 + i,
                run_number=i,
                status="completed",
                conclusion="success" if i % 2 == 0 else "failure",
                start_time=now - timedelta(minutes=i*5 + 5),
                end_time=now - timedelta(minutes=i*5),
                duration_seconds=300,
                event="push",
                branch="main",
                actor="test-user"
            )
            for i in range(10)
        ]
        
        collector.record_to_predictor(runs)
        
        stats = collector.get_workflow_stats()
        
        assert 'total_executions' in stats
        assert stats['total_executions'] >= 10
        assert 'unique_workflows' in stats
        
        print(f"  ✓ Stats generated: {stats['total_executions']} executions")
        self.test_results.append(("stats_with_data", True))
    
    @patch('subprocess.run')
    def test_collect_and_record(self, mock_run):
        """Test the complete collect and record flow."""
        print("\n🧪 Testing complete collection flow...")
        
        now = datetime.now(timezone.utc)
        mock_response = json.dumps([
            {
                'workflowName': 'CI Pipeline',
                'workflowDatabaseId': 123,
                'databaseId': 456,
                'number': 100,
                'status': 'completed',
                'conclusion': 'success',
                'createdAt': (now - timedelta(minutes=15)).isoformat(),
                'updatedAt': now.isoformat(),
                'event': 'push',
                'headBranch': 'main',
                'actor': {'login': 'developer'}
            }
        ])
        
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout=mock_response
        )
        
        collector = GitHubActionsDataCollector(
            repo_root=self.temp_dir,
            owner='test-owner',
            repo='test-repo'
        )
        
        result = collector.collect_and_record(limit=10)
        
        assert result['status'] == 'success'
        assert result['runs_fetched'] == 1
        assert result['runs_recorded'] == 1
        assert 'CI Pipeline' in result['workflows']
        
        print(f"  ✓ Collected and recorded: {result['runs_recorded']} runs")
        self.test_results.append(("collect_and_record", True))
    
    @patch('subprocess.run')
    def test_no_runs_available(self, mock_run):
        """Test handling when no workflow runs are available."""
        print("\n🧪 Testing empty API response...")
        
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout='[]'
        )
        
        collector = GitHubActionsDataCollector(
            repo_root=self.temp_dir,
            owner='test-owner',
            repo='test-repo'
        )
        
        result = collector.collect_and_record(limit=10)
        
        assert result['status'] == 'no_data'
        assert result['runs_fetched'] == 0
        
        print("  ✓ Empty response handled correctly")
        self.test_results.append(("no_runs", True))
    
    @patch('subprocess.run')
    def test_gh_cli_failure(self, mock_run):
        """Test handling when gh CLI fails."""
        print("\n🧪 Testing gh CLI failure handling...")
        
        mock_run.return_value = MagicMock(
            returncode=1,
            stdout='',
            stderr='gh: not logged in'
        )
        
        collector = GitHubActionsDataCollector(
            repo_root=self.temp_dir,
            owner='test-owner',
            repo='test-repo'
        )
        
        runs = collector.fetch_workflow_runs(limit=10)
        
        assert len(runs) == 0
        
        print("  ✓ CLI failure handled gracefully")
        self.test_results.append(("cli_failure", True))
    
    def test_generate_collection_report(self):
        """Test report generation."""
        print("\n🧪 Testing report generation...")
        
        collector = GitHubActionsDataCollector(
            repo_root=self.temp_dir,
            owner='test-owner',
            repo='test-repo'
        )
        
        # Record some data first
        now = datetime.now(timezone.utc)
        runs = [
            WorkflowRunData(
                workflow_name="report-test",
                workflow_id=100,
                run_id=200 + i,
                run_number=i,
                status="completed",
                conclusion="success",
                start_time=now - timedelta(minutes=i*5 + 5),
                end_time=now - timedelta(minutes=i*5),
                duration_seconds=180,
                event="push",
                branch="main",
                actor="test-user"
            )
            for i in range(3)
        ]
        collector.record_to_predictor(runs)
        
        report = collector.generate_collection_report()
        
        assert 'timestamp' in report
        assert 'repository' in report
        assert report['repository'] == 'test-owner/test-repo'
        
        print("  ✓ Report generated successfully")
        self.test_results.append(("report_generation", True))
    
    def run_all_tests(self):
        """Run all tests."""
        print("="*70)
        print("🧪 Running GitHub Actions Data Collector Test Suite")
        print("   @create-guru")
        print("="*70)
        
        try:
            self.setup()
            
            # Run all tests
            self.test_initialization()
            self.test_workflow_run_data_creation()
            self.test_collection_log_save_and_load()
            self.test_record_to_predictor()
            self.test_fetch_workflow_runs_mock()
            self.test_get_workflow_stats_empty()
            self.test_get_workflow_stats_with_data()
            self.test_collect_and_record()
            self.test_no_runs_available()
            self.test_gh_cli_failure()
            self.test_generate_collection_report()
            
            # Summary
            print("\n" + "="*70)
            print("📊 Test Results Summary")
            print("="*70)
            
            passed = sum(1 for _, result in self.test_results if result)
            total = len(self.test_results)
            
            for test_name, result in self.test_results:
                status = "✓ PASS" if result else "✗ FAIL"
                print(f"{status}: {test_name}")
            
            print("\n" + "="*70)
            print(f"Total: {passed}/{total} tests passed ({passed/total*100:.0f}%)")
            print("="*70 + "\n")
            
            return passed == total
            
        except Exception as e:
            print(f"\n❌ Test suite failed with error: {e}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            self.teardown()


def main():
    """Main entry point."""
    tester = TestGitHubActionsDataCollector()
    success = tester.run_all_tests()
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
