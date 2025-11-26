"""
A2A Agent Server wrapper for Chained agents.

This module provides a simple wrapper to run any Chained agent as an A2A-compliant
HTTP server using the A2A Python SDK.
"""

import uvicorn
from typing import Optional

from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCard

from .agent_card import generate_agent_card
from .agent_executor import ChainedAgentExecutor
from .utils import get_agent_port


def create_agent_server(
    agent_name: str,
    port: Optional[int] = None,
    host: str = "0.0.0.0",
) -> A2AStarletteApplication:
    """
    Create an A2A server for a Chained agent.
    
    Args:
        agent_name: Name of the Chained agent (e.g., "engineer-master")
        port: Port to run the server on (auto-assigned if None)
        host: Host to bind to (default: "0.0.0.0")
        
    Returns:
        A2AStarletteApplication ready to run
        
    Example:
        >>> server = create_agent_server("engineer-master")
        >>> # Server ready to run with uvicorn
    """
    # Get port
    if port is None:
        port = get_agent_port(agent_name)
    
    # Generate agent card
    agent_card = generate_agent_card(agent_name, port=port)
    
    # Create executor
    executor = ChainedAgentExecutor(agent_name=agent_name)
    
    # Create task store
    task_store = InMemoryTaskStore()
    
    # Create request handler
    request_handler = DefaultRequestHandler(
        agent_executor=executor,
        task_store=task_store,
    )
    
    # Create and return server
    server = A2AStarletteApplication(
        agent_card=agent_card,
        http_handler=request_handler,
    )
    
    return server


def run_agent_server(
    agent_name: str,
    port: Optional[int] = None,
    host: str = "0.0.0.0",
    log_level: str = "info",
) -> None:
    """
    Run an A2A server for a Chained agent.
    
    This is a convenience function that creates and runs the server.
    
    Args:
        agent_name: Name of the Chained agent
        port: Port to run on (auto-assigned if None)
        host: Host to bind to
        log_level: Uvicorn log level
        
    Example:
        >>> run_agent_server("engineer-master")
        # Server starts on auto-assigned port
    """
    if port is None:
        port = get_agent_port(agent_name)
    
    server = create_agent_server(agent_name, port, host)
    
    print(f"Starting A2A server for {agent_name} on {host}:{port}")
    print(f"Agent Card: http://{host}:{port}/.well-known/agent-card")
    
    uvicorn.run(server.build(), host=host, port=port, log_level=log_level)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python -m tools.a2a.agent_server <agent-name> [port]")
        sys.exit(1)
    
    agent_name = sys.argv[1]
    port = int(sys.argv[2]) if len(sys.argv) > 2 else None
    
    run_agent_server(agent_name, port)
