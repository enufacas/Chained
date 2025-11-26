"""
A2A (Agent-to-Agent) Protocol Integration for Chained

This package provides A2A protocol support for the Chained autonomous AI ecosystem,
enabling true multi-agent collaboration and communication.

Key Components:
- agent_card: Generate A2A Agent Cards from Chained agent definitions
- agent_executor: Base executor for running Chained agents as A2A servers
- agent_server: HTTP server wrapper for A2A protocol
- client: Client library for agent-to-agent communication
- discovery: Service for agent discovery and registration
- github_transport: Issue-based cross-runner communication (Tier 2)
- github_branch_transport: Branch-based cross-runner communication (Tier 2)
- mcp_transport: MCP-native Copilot agent communication (Tier 3, conceptual)

Three-Tier Architecture:
- Tier 1: Same-runner HTTP (agents in one workflow, localhost)
- Tier 2: GitHub-mediated (cross-runner via issues or branches + workflows)
- Tier 3: MCP-native (Copilot agent-to-agent, uses github-mcp-server tools)

Usage:
    from tools.a2a import generate_agent_card, ChainedAgentExecutor
    
    # Generate agent card from Chained definition
    card = generate_agent_card("engineer-master")
    
    # Tier 1: Run agent as A2A server (same runner)
    executor = ChainedAgentExecutor(agent_name="engineer-master")
    server = create_agent_server("engineer-master")
    
    # Tier 2: Cross-runner delegation (workflows)
    from tools.a2a import send_task_via_github, send_task_via_branch
    issue_num = await send_task_via_github(agent, msg, token, owner, repo)
    branch = await send_task_via_branch(agent, msg, token, owner, repo)
    
    # Tier 3: MCP-native (future, Copilot agents only)
    from tools.a2a import MCPTransport
    # See mcp_transport.py for design notes
"""

__version__ = "0.3.0"

from .agent_card import generate_agent_card, parse_agent_definition, generate_all_agent_cards
from .agent_executor import ChainedAgentExecutor
from .agent_server import create_agent_server, run_agent_server
from .client import ChainedA2AClient, discover_agents_by_skill, send_to_agent
from .discovery import get_discovery_service, DiscoveryService, AgentRegistry
from .github_transport import GitHubA2ATransport, send_task_via_github, wait_for_task_completion
from .github_branch_transport import GitHubBranchTransport, send_task_via_branch, wait_for_task_completion_branch
from .mcp_transport import MCPTransport, MCPTransportTask
from .utils import get_agent_port, get_discovery_url, check_port_available, get_available_port

__all__ = [
    # Agent cards
    "generate_agent_card",
    "parse_agent_definition",
    "generate_all_agent_cards",
    # Execution
    "ChainedAgentExecutor",
    # Server (Tier 1: Same-runner)
    "create_agent_server",
    "run_agent_server",
    # Client (Tier 1: Same-runner)
    "ChainedA2AClient",
    "discover_agents_by_skill",
    "send_to_agent",
    # Discovery
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
