"""
Utility functions for A2A integration.
"""

import os
from typing import Optional


def get_agent_port(agent_name: str, base_port: int = 9001) -> int:
    """
    Get the A2A server port for a given agent.
    
    Args:
        agent_name: Name of the agent
        base_port: Base port number (default: 9001)
        
    Returns:
        Port number for the agent
    """
    # Use environment variable if set
    env_var = f"A2A_{agent_name.upper().replace('-', '_')}_PORT"
    if env_var in os.environ:
        return int(os.environ[env_var])
    
    # Simple hash-based port assignment
    # This ensures consistent port assignment across runs
    hash_value = abs(hash(agent_name)) % 1000
    return base_port + hash_value


def get_discovery_url() -> str:
    """
    Get the A2A discovery service URL.
    
    Returns:
        Discovery service URL
    """
    return os.getenv("A2A_DISCOVERY_SERVICE_URL", "http://localhost:9000")


def get_agent_base_url() -> str:
    """
    Get the base URL for agent servers.
    
    Returns:
        Base URL (e.g., http://localhost)
    """
    return os.getenv("A2A_AGENT_BASE_URL", "http://localhost")


def is_a2a_enabled() -> bool:
    """
    Check if A2A protocol is enabled.
    
    Returns:
        True if A2A is enabled
    """
    return os.getenv("A2A_ENABLED", "true").lower() in ("true", "1", "yes")


def get_task_timeout() -> int:
    """
    Get the task timeout in seconds.
    
    Returns:
        Timeout in seconds
    """
    return int(os.getenv("A2A_TASK_TIMEOUT", "3600"))
