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

__version__ = "0.1.0"

from .agent_card import generate_agent_card, parse_agent_definition, generate_all_agent_cards
from .agent_executor import ChainedAgentExecutor
from .utils import get_agent_port, get_discovery_url

__all__ = [
    "generate_agent_card",
    "parse_agent_definition",
    "generate_all_agent_cards",
    "ChainedAgentExecutor",
    "get_agent_port",
    "get_discovery_url",
]
