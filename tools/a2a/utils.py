"""
Utility functions for A2A integration.
"""

import hashlib
import os
import socket
from typing import Optional, Set


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


def check_port_available(port: int, host: str = 'localhost') -> bool:
    """
    Check if a port is available for binding.
    
    Args:
        port: Port number to check
        host: Host to check (default: localhost)
        
    Returns:
        True if port is available, False otherwise
    """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind((host, port))
            return True
    except OSError:
        return False


def get_available_port(agent_name: str, base_port: int = 9001, max_attempts: int = 100) -> int:
    """
    Get an available port for an agent, handling collisions.
    
    This is a more robust version of get_agent_port() that checks
    if the port is actually available and tries alternatives if not.
    
    Args:
        agent_name: Name of the agent
        base_port: Base port number (default: 9001)
        max_attempts: Maximum number of ports to try
        
    Returns:
        Available port number for the agent
        
    Raises:
        RuntimeError: If no available port found after max_attempts
    """
    # Start with the deterministic port
    port = get_agent_port(agent_name, base_port)
    
    for attempt in range(max_attempts):
        if check_port_available(port):
            return port
        # Try next port
        port += 1
        if port > base_port + 50000:
            port = base_port
    
    raise RuntimeError(f"Could not find available port for {agent_name} after {max_attempts} attempts")


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
