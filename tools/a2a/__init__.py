"""
A2A (Agent-to-Agent) Protocol Integration for Chained

This package provides A2A protocol support for the Chained autonomous AI ecosystem,
enabling true multi-agent collaboration and communication.

Based on the official A2A specification: https://github.com/a2aproject/A2A
Following patterns from: https://github.com/a2aproject/a2a-samples
See also: https://a2a-protocol.org/latest/topics/life-of-a-task/

Key Components:
- task: Task and Artifact management per "Life of a Task" (§4.1.1-4.1.9)
- agent_card: Generate A2A Agent Cards from Chained agent definitions (§4.4.1)
- agent_executor: Base executor for running Chained agents as A2A servers
- gemini_executor: Gemini-powered A2A executor (production implementation)
- agent_server: HTTP server wrapper for A2A protocol (§3)
- client: Client library for agent-to-agent communication (§3.1.1)
- discovery: Service for agent discovery and registration (§8)
- github_transport: Issue-based cross-runner communication (Tier 2)
- github_branch_transport: Branch-based cross-runner communication (Tier 2)
- mcp_transport: MCP-native Copilot agent communication (Tier 3, conceptual)

Three-Tier Architecture:
- Tier 1: Same-runner HTTP (agents in one workflow, localhost)
- Tier 2: GitHub-mediated (cross-runner via issues or branches + workflows)
- Tier 3: MCP-native (Copilot agent-to-agent, uses github-mcp-server tools)

Task Lifecycle (per A2A spec "Life of a Task"):
- contextId: Groups related Tasks together for continuity
- taskId: Unique identifier for each Task
- TaskState: submitted → working → completed/failed/canceled
- Artifact: Versioned output with Parts (TextPart, FilePart, DataPart)
- referenceTaskIds: Links follow-up tasks to previous tasks

Usage:
    from tools.a2a import (
        # Task management (§4.1.1-4.1.9)
        Task, TaskState, TaskStatus, Artifact, Part, TaskStore,
        create_analysis_task, create_implementation_task, aggregate_artifacts,
        # Agent discovery (§4.4.1, §8)
        generate_agent_card, DiscoveryService, AgentRegistry,
        # Execution
        GeminiAgentExecutor, ChainedAgentExecutor,
    )
    
    # Create an analysis task (§4.1.1)
    task = create_analysis_task(issue_number=123, agent_name="engineer-master", run_id="abc")
    task.set_working("Analyzing issue...")
    
    # Add artifact when analysis completes (§4.1.9)
    task.add_text_artifact("analysis", "Findings from engineer-master...")
    task.complete("Analysis complete")
    
    # Create follow-up implementation task with referenceTaskIds
    impl_task = create_implementation_task(
        issue_number=123,
        run_id="abc",
        reference_task_ids=[task.id],  # Links to analysis task
        context_id=task.context_id,     # Same context
    )
    
    # Aggregate artifacts from all analysis tasks for implementation
    aggregated = aggregate_artifacts([task])
"""

__version__ = "0.5.0"

from .agent_card import generate_agent_card, parse_agent_definition, generate_all_agent_cards
from .agent_executor import ChainedAgentExecutor
from .gemini_executor import GeminiAgent, GeminiAgentExecutor, create_gemini_agent_server
from .agent_server import create_agent_server, run_agent_server
from .client import ChainedA2AClient, discover_agents_by_skill, send_to_agent
from .discovery import get_discovery_service, DiscoveryService, AgentRegistry
from .github_transport import GitHubA2ATransport, send_task_via_github, wait_for_task_completion
from .github_branch_transport import GitHubBranchTransport, send_task_via_branch, wait_for_task_completion_branch
from .mcp_transport import MCPTransport, MCPTransportTask
from .task import (
    Task,
    TaskState,
    TaskStatus,
    Artifact,
    Part,
    TaskStore,
    create_analysis_task,
    create_implementation_task,
    aggregate_artifacts,
)
from .utils import get_agent_port, get_discovery_url, check_port_available, get_available_port

__all__ = [
    # Agent cards (§4.4.1)
    "generate_agent_card",
    "parse_agent_definition",
    "generate_all_agent_cards",
    # Task and Artifact management (§4.1.1-4.1.9, Life of a Task)
    "Task",
    "TaskState",
    "TaskStatus",
    "Artifact",
    "Part",
    "TaskStore",
    "create_analysis_task",
    "create_implementation_task",
    "aggregate_artifacts",
    # Execution - Base
    "ChainedAgentExecutor",
    # Execution - Gemini (production)
    "GeminiAgent",
    "GeminiAgentExecutor",
    "create_gemini_agent_server",
    # Server (Tier 1: Same-runner) (§3)
    "create_agent_server",
    "run_agent_server",
    # Client (Tier 1: Same-runner) (§3.1.1)
    "ChainedA2AClient",
    "discover_agents_by_skill",
    "send_to_agent",
    # Discovery (§8)
    "get_discovery_service",
    "DiscoveryService",
    "AgentRegistry",
    # GitHub transport (Tier 2: Cross-runner workflows) - Issue-based
    "GitHubA2ATransport",
    "send_task_via_github",
    "wait_for_task_completion",
    # GitHub transport (Tier 2: Cross-runner workflows) - Branch-based
    "GitHubBranchTransport",
    "send_task_via_branch",
    "wait_for_task_completion_branch",
    # MCP transport (Tier 3: Copilot agent-to-agent) - Conceptual
    "MCPTransport",
    "MCPTransportTask",
    # Utils
    "get_agent_port",
    "get_discovery_url",
    "check_port_available",
    "get_available_port",
]
