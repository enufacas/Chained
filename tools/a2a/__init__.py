"""
A2A (Agent-to-Agent) Protocol Integration for Chained

This package provides A2A protocol support for the Chained autonomous AI ecosystem,
enabling true multi-agent collaboration and communication.

Based on the official A2A specification: https://github.com/a2aproject/A2A
Following patterns from: https://github.com/a2aproject/a2a-samples

Key Components:
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

Usage:
    from tools.a2a import generate_agent_card, GeminiAgentExecutor
    
    # Generate agent card from Chained definition (§4.4.1)
    card = generate_agent_card("engineer-master")
    
    # Tier 1: Run agent as A2A server with Gemini backend
    from tools.a2a import create_gemini_agent_server
    server = create_gemini_agent_server("engineer-master", port=8080)
    
    # Tier 2: Cross-runner delegation (workflows)
    from tools.a2a import send_task_via_github, send_task_via_branch
    issue_num = await send_task_via_github(agent, msg, token, owner, repo)
    branch = await send_task_via_branch(agent, msg, token, owner, repo)
    
    # Tier 3: MCP-native (future, Copilot agents only)
    from tools.a2a import MCPTransport
    # See mcp_transport.py for design notes
"""

__version__ = "0.4.0"

from .agent_card import generate_agent_card, parse_agent_definition, generate_all_agent_cards
from .agent_executor import ChainedAgentExecutor
from .gemini_executor import GeminiAgent, GeminiAgentExecutor, create_gemini_agent_server
from .agent_server import create_agent_server, run_agent_server
from .client import ChainedA2AClient, discover_agents_by_skill, send_to_agent
from .discovery import get_discovery_service, DiscoveryService, AgentRegistry
from .github_transport import GitHubA2ATransport, send_task_via_github, wait_for_task_completion
from .github_branch_transport import GitHubBranchTransport, send_task_via_branch, wait_for_task_completion_branch
from .mcp_transport import MCPTransport, MCPTransportTask
from .utils import get_agent_port, get_discovery_url, check_port_available, get_available_port

__all__ = [
    # Agent cards (§4.4.1)
    "generate_agent_card",
    "parse_agent_definition",
    "generate_all_agent_cards",
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
