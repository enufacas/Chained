"""
Test suite for ADK A2A Blog Pipeline components.

This test validates that the pipeline infrastructure is properly configured
and the orchestrator can interact with the agents.

Related Files:
- .github/workflows/adk-a2a-blog-pipeline.yml
- infrastructure/docker/adk-agents/orchestrator.py
- infrastructure/docker/adk-agents/*/agent.py
"""

import json
import os
import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


# Add infrastructure path to sys.path
REPO_ROOT = Path(__file__).parent.parent
ADK_AGENTS_PATH = REPO_ROOT / "infrastructure" / "docker" / "adk-agents"
sys.path.insert(0, str(ADK_AGENTS_PATH))


# =============================================================================
# Test Configuration
# =============================================================================


@pytest.fixture
def mock_agent_urls():
    """Mock agent URLs for testing."""
    return {
        "academic-research": "http://localhost:8081",
        "blog-writer": "http://localhost:8082",
        "google-trends": "http://localhost:8083",
    }


@pytest.fixture
def mock_agent_card():
    """Mock agent card response."""
    return {
        "name": "Test Agent",
        "version": "1.0.0",
        "description": "Test agent for pipeline",
        "skills": [
            {
                "name": "test-skill",
                "description": "Test skill",
            }
        ],
    }


@pytest.fixture
def mock_task_response():
    """Mock A2A task response."""
    return {
        "id": "task-123",
        "status": "completed",
        "artifacts": [
            {
                "name": "test-artifact",
                "type": "application/json",
                "data": json.dumps({"result": "success"}),
            }
        ],
    }


# =============================================================================
# Orchestrator Module Tests
# =============================================================================


class TestOrchestratorModule:
    """Test the orchestrator module can be imported and instantiated."""

    def test_import_orchestrator(self):
        """Test that orchestrator module can be imported."""
        try:
            from orchestrator import BlogPipelineOrchestrator
            assert BlogPipelineOrchestrator is not None
        except ImportError as e:
            pytest.fail(f"Failed to import orchestrator: {e}")

    def test_import_a2a_client(self):
        """Test that A2AClient can be imported."""
        try:
            from orchestrator import A2AClient
            assert A2AClient is not None
        except ImportError as e:
            pytest.fail(f"Failed to import A2AClient: {e}")

    def test_orchestrator_instantiation(self):
        """Test that BlogPipelineOrchestrator can be instantiated."""
        from orchestrator import BlogPipelineOrchestrator

        orchestrator = BlogPipelineOrchestrator()
        assert orchestrator is not None
        assert hasattr(orchestrator, "context_id")
        assert hasattr(orchestrator, "clients")
        assert hasattr(orchestrator, "task_history")


# =============================================================================
# A2A Client Tests
# =============================================================================


class TestA2AClient:
    """Test the A2A client functionality."""

    def test_client_initialization(self):
        """Test A2A client can be initialized."""
        from orchestrator import A2AClient

        client = A2AClient("http://localhost:8081")
        assert client.base_url == "http://localhost:8081"
        assert client.timeout == 60.0

    def test_client_strips_trailing_slash(self):
        """Test that trailing slash is removed from base URL."""
        from orchestrator import A2AClient

        client = A2AClient("http://localhost:8081/")
        assert client.base_url == "http://localhost:8081"

    @pytest.mark.asyncio
    async def test_send_message_payload_structure(self, mock_task_response):
        """Test that send_message creates correct payload structure."""
        from orchestrator import A2AClient

        client = A2AClient("http://localhost:8081")

        with patch("httpx.AsyncClient") as mock_client:
            mock_response = MagicMock()
            mock_response.json.return_value = mock_task_response
            mock_response.raise_for_status = MagicMock()
            
            mock_post = AsyncMock(return_value=mock_response)
            mock_client.return_value.__aenter__.return_value.post = mock_post

            result = await client.send_message(
                message="Test message",
                context_id="ctx-123",
                reference_task_ids=["task-1", "task-2"],
                metadata={"key": "value"},
            )

            # Verify call was made
            assert mock_post.called
            call_args = mock_post.call_args

            # Verify URL
            assert call_args[0][0] == "http://localhost:8081/a2a/tasks"

            # Verify payload structure
            payload = call_args[1]["json"]
            assert "message" in payload
            assert payload["message"]["role"] == "user"
            assert len(payload["message"]["parts"]) == 1
            assert payload["message"]["parts"][0]["text"] == "Test message"
            assert payload["contextId"] == "ctx-123"
            assert payload["referenceTaskIds"] == ["task-1", "task-2"]
            assert payload["metadata"] == {"key": "value"}


# =============================================================================
# Workflow Integration Tests
# =============================================================================


class TestWorkflowIntegration:
    """Test workflow integration points."""

    def test_workflow_file_exists(self):
        """Test that the ADK pipeline workflow file exists."""
        workflow_path = REPO_ROOT / ".github" / "workflows" / "adk-a2a-blog-pipeline.yml"
        assert workflow_path.exists(), "Workflow file should exist"

    def test_workflow_has_tracking_issue_logic(self):
        """Test that workflow contains tracking issue creation logic."""
        workflow_path = REPO_ROOT / ".github" / "workflows" / "adk-a2a-blog-pipeline.yml"
        content = workflow_path.read_text()

        # Check for key elements
        assert "adk-pipeline" in content, "Should have adk-pipeline label"
        assert "ADK A2A Blog Pipeline Status" in content, "Should have status title"
        assert "gh issue create" in content, "Should create issue"
        assert "gh issue comment" in content, "Should comment on issue"

    def test_orchestrator_file_exists(self):
        """Test that orchestrator.py exists."""
        orchestrator_path = ADK_AGENTS_PATH / "orchestrator.py"
        assert orchestrator_path.exists(), "Orchestrator file should exist"

    def test_orchestrator_has_main_entry_point(self):
        """Test that orchestrator has main entry point."""
        orchestrator_path = ADK_AGENTS_PATH / "orchestrator.py"
        content = orchestrator_path.read_text()

        assert "async def main()" in content, "Should have main function"
        assert 'if __name__ == "__main__"' in content, "Should have main guard"
        assert "asyncio.run(main())" in content, "Should run async main"

    def test_orchestrator_writes_output_file(self):
        """Test that orchestrator writes pipeline_result.json."""
        orchestrator_path = ADK_AGENTS_PATH / "orchestrator.py"
        content = orchestrator_path.read_text()

        assert "OUTPUT_FILE" in content, "Should reference OUTPUT_FILE"
        assert "pipeline_result.json" in content, "Should have default output file"
        assert "json.dump" in content, "Should write JSON output"


# =============================================================================
# Pipeline Configuration Tests
# =============================================================================


class TestPipelineConfiguration:
    """Test pipeline configuration and environment."""

    def test_agent_urls_configuration(self):
        """Test that agent URLs can be configured from environment."""
        from orchestrator import get_agent_urls

        # Test with default values
        urls = get_agent_urls()
        assert "academic-research" in urls
        assert "blog-writer" in urls
        assert "google-trends" in urls

    def test_orchestrator_uses_agent_urls(self):
        """Test that orchestrator uses configured agent URLs."""
        from orchestrator import BlogPipelineOrchestrator

        orchestrator = BlogPipelineOrchestrator()
        assert "academic-research" in orchestrator.clients
        assert "blog-writer" in orchestrator.clients
        assert "google-trends" in orchestrator.clients


# =============================================================================
# Documentation Tests
# =============================================================================


class TestDocumentation:
    """Test that documentation is in place."""

    def test_readme_exists(self):
        """Test that ADK agents README exists."""
        readme_path = ADK_AGENTS_PATH / "README.md"
        assert readme_path.exists(), "README should exist"

    def test_readme_has_pipeline_description(self):
        """Test that README describes the pipeline."""
        readme_path = ADK_AGENTS_PATH / "README.md"
        content = readme_path.read_text()

        assert "A2A" in content, "Should mention A2A protocol"
        assert "blog" in content.lower(), "Should mention blog pipeline"
        assert "orchestrator" in content.lower(), "Should mention orchestrator"

    def test_implementation_doc_exists(self):
        """Test that implementation documentation exists."""
        doc_path = REPO_ROOT / "docs" / "ADK_A2A_PIPELINE_IMPLEMENTATION.md"
        assert doc_path.exists(), "Implementation doc should exist"

    def test_implementation_doc_has_tracking_issue_info(self):
        """Test that implementation doc describes tracking issue."""
        doc_path = REPO_ROOT / "docs" / "ADK_A2A_PIPELINE_IMPLEMENTATION.md"
        content = doc_path.read_text()

        assert "tracking issue" in content.lower(), "Should mention tracking issue"
        assert "adk-pipeline" in content, "Should mention adk-pipeline label"


# =============================================================================
# Health Check Tests
# =============================================================================


class TestHealthChecks:
    """Test health check functionality."""

    @pytest.mark.asyncio
    async def test_orchestrator_has_health_check(self):
        """Test that orchestrator has health check method."""
        from orchestrator import BlogPipelineOrchestrator

        orchestrator = BlogPipelineOrchestrator()
        assert hasattr(orchestrator, "check_agents_health")

    @pytest.mark.asyncio
    async def test_health_check_calls_agents(self):
        """Test that health check calls all agents."""
        from orchestrator import BlogPipelineOrchestrator

        orchestrator = BlogPipelineOrchestrator()

        # Mock the client health checks
        with patch.object(orchestrator.clients["academic-research"], "check_health") as mock1, \
             patch.object(orchestrator.clients["blog-writer"], "check_health") as mock2, \
             patch.object(orchestrator.clients["google-trends"], "check_health") as mock3:
            
            mock1.return_value = True
            mock2.return_value = True
            mock3.return_value = True

            health = await orchestrator.check_agents_health()

            assert "academic-research" in health
            assert "blog-writer" in health
            assert "google-trends" in health
