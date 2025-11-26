"""
Utility functions for A2A integration.
"""

import hashlib
import os
from typing import Optional


def get_agent_port(agent_name: str, base_port: int = 9001) -> int:
    """
    Get the A2A server port for a given agent.
    
    Uses SHA256 for highly collision-resistant port assignment.
    
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
    
    # Use SHA256 for better distribution and collision resistance
    sha = hashlib.sha256(agent_name.encode('utf-8')).digest()
    # Use first 4 bytes as integer
    port_offset = int.from_bytes(sha[:4], 'big') % 50000
    # This gives us port range 9001-59000 with excellent distribution
    return base_port + port_offset


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
