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
- task_store: Task persistence and lifecycle management

Usage:
    from tools.a2a import generate_agent_card, ChainedAgentExecutor
    
    # Generate agent card from Chained definition
    card = generate_agent_card("engineer-master")
    
    # Run agent as A2A server
    executor = ChainedAgentExecutor(agent_name="engineer-master")
    server = create_a2a_server(executor, card, port=9001)
"""

__version__ = "0.2.1"

from .agent_card import generate_agent_card, parse_agent_definition, generate_all_agent_cards
from .agent_executor import ChainedAgentExecutor
from .agent_server import create_agent_server, run_agent_server
from .client import ChainedA2AClient, discover_agents_by_skill, send_to_agent
from .discovery import get_discovery_service, DiscoveryService, AgentRegistry
from .github_transport import GitHubA2ATransport, send_task_via_github, wait_for_task_completion
from .github_branch_transport import GitHubBranchTransport, send_task_via_branch, wait_for_task_completion_branch
from .utils import get_agent_port, get_discovery_url

__all__ = [
    # Agent cards
    "generate_agent_card",
    "parse_agent_definition",
    "generate_all_agent_cards",
    # Execution
    "ChainedAgentExecutor",
    # Server (Tier 1)
    "create_agent_server",
    "run_agent_server",
    # Client (Tier 1)
    "ChainedA2AClient",
    "discover_agents_by_skill",
    "send_to_agent",
    # Discovery
    "get_discovery_service",
    "DiscoveryService",
    "AgentRegistry",
    # GitHub transport (Tier 2) - Issue-based
    "GitHubA2ATransport",
    "send_task_via_github",
    "wait_for_task_completion",
    # GitHub transport (Tier 2) - Branch-based
    "GitHubBranchTransport",
    "send_task_via_branch",
    "wait_for_task_completion_branch",
    # Utils
    "get_agent_port",
    "get_discovery_url",
]
