"""
A2A Discovery Service for agent registry and lookup.

This module provides a discovery service that maintains a registry of available
agents and their capabilities, enabling agents to discover each other.
"""

import asyncio
import json
import re
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set

import httpx
from a2a.types import AgentCard

from .agent_card import generate_agent_card, generate_all_agent_cards
from .utils import get_agent_base_url, get_agent_port


@dataclass
class AgentRegistration:
    """Registration information for an agent."""
    agent_name: str
    port: int
    url: str
    card_url: str
    status: str  # "active", "inactive", "unknown"
    last_health_check: Optional[str] = None
    skills: List[str] = None
    
    def to_dict(self):
        """Convert to dictionary."""
        return asdict(self)


class AgentRegistry:
    """
    Registry of A2A agents.
    
    Maintains a registry of available agents, their endpoints, and capabilities.
    Provides discovery and health checking functionality.
    """
    
    def __init__(self, registry_file: Optional[Path] = None):
        """
        Initialize the agent registry.
        
        Args:
            registry_file: Path to persist registry (optional)
        """
        self.agents: Dict[str, AgentRegistration] = {}
        self.registry_file = registry_file
        self._lock = asyncio.Lock()
        
        if registry_file and registry_file.exists():
            self.load()
    
    def register_agent(
        self,
        agent_name: str,
        port: Optional[int] = None,
        skills: Optional[List[str]] = None,
        status: str = "unknown",
    ) -> AgentRegistration:
        """
        Register an agent in the registry.
        
        Args:
            agent_name: Name of the agent
            port: Port the agent is running on (auto-assigned if None)
            skills: List of skill IDs the agent provides
            status: Initial status (default: "unknown", use "active" for testing)
            
        Returns:
            AgentRegistration object
        """
        if port is None:
            port = get_agent_port(agent_name)
        
        base_url = get_agent_base_url()
        url = f"{base_url}:{port}/"
        card_url = f"{url}.well-known/agent-card"
        
        registration = AgentRegistration(
            agent_name=agent_name,
            port=port,
            url=url,
            card_url=card_url,
            status=status,
            skills=skills or [],
        )
        
        self.agents[agent_name] = registration
        
        if self.registry_file:
            self.save()
        
        return registration
    
    def unregister_agent(self, agent_name: str) -> bool:
        """
        Unregister an agent.
        
        Args:
            agent_name: Name of the agent to unregister
            
        Returns:
            True if agent was unregistered, False if not found
        """
        if agent_name in self.agents:
            del self.agents[agent_name]
            if self.registry_file:
                self.save()
            return True
        return False
    
    def get_agent(self, agent_name: str) -> Optional[AgentRegistration]:
        """Get registration for a specific agent."""
        return self.agents.get(agent_name)
    
    def list_agents(
        self,
        status: Optional[str] = None,
        skill: Optional[str] = None,
    ) -> List[AgentRegistration]:
        """
        List registered agents.
        
        Args:
            status: Filter by status ("active", "inactive", "unknown")
            skill: Filter by skill ID (supports substring matching)
            
        Returns:
            List of agent registrations matching criteria
        """
        agents = list(self.agents.values())
        
        if status:
            agents = [a for a in agents if a.status == status]
        
        if skill:
            # Support substring matching for skills
            agents = [
                a for a in agents 
                if any(skill in s for s in (a.skills or []))
            ]
        
        return agents
    
    async def health_check_agent(self, agent_name: str) -> bool:
        """
        Perform health check on an agent.
        
        Args:
            agent_name: Name of the agent
            
        Returns:
            True if agent is healthy, False otherwise
        """
        agent = self.agents.get(agent_name)
        if not agent:
            return False
        
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{agent.url}health")
                is_healthy = response.status_code == 200
                
                async with self._lock:
                    agent.status = "active" if is_healthy else "inactive"
                    agent.last_health_check = datetime.utcnow().isoformat()
                    
                    if self.registry_file:
                        self.save()
                
                return is_healthy
        except Exception:
            async with self._lock:
                agent.status = "inactive"
                agent.last_health_check = datetime.utcnow().isoformat()
                
                if self.registry_file:
                    self.save()
            
            return False
    
    async def health_check_all(self) -> Dict[str, bool]:
        """
        Perform health check on all registered agents.
        
        Returns:
            Dict mapping agent names to health status
        """
        results = {}
        tasks = []
        
        for agent_name in self.agents.keys():
            tasks.append(self.health_check_agent(agent_name))
        
        if tasks:
            health_results = await asyncio.gather(*tasks, return_exceptions=True)
            for agent_name, is_healthy in zip(self.agents.keys(), health_results):
                results[agent_name] = is_healthy if isinstance(is_healthy, bool) else False
        
        return results
    
    def save(self) -> None:
        """Save registry to file."""
        if not self.registry_file:
            return
        
        data = {
            "agents": {
                name: reg.to_dict()
                for name, reg in self.agents.items()
            }
        }
        
        self.registry_file.parent.mkdir(parents=True, exist_ok=True)
        self.registry_file.write_text(json.dumps(data, indent=2))
    
    def load(self) -> None:
        """Load registry from file."""
        if not self.registry_file or not self.registry_file.exists():
            return
        
        data = json.loads(self.registry_file.read_text())
        
        self.agents = {}
        for name, reg_data in data.get("agents", {}).items():
            self.agents[name] = AgentRegistration(**reg_data)


class DiscoveryService:
    """
    A2A Discovery Service.
    
    Provides agent discovery, registration, and health monitoring.
    """
    
    def __init__(self, registry_file: Optional[Path] = None):
        """
        Initialize the discovery service.
        
        Args:
            registry_file: Path to persist registry
        """
        self.registry = AgentRegistry(registry_file)
        # Store full agent cards for later retrieval
        self._cards: Dict[str, AgentCard] = {}
    
    async def register_agent(self, card: AgentCard) -> AgentRegistration:
        """
        Register an agent from an AgentCard.
        
        Args:
            card: AgentCard to register
            
        Returns:
            AgentRegistration object
        """
        # Store the full card
        self._cards[card.name] = card
        
        # Extract port from URL
        port_match = re.search(r':(\d+)/', card.url)
        port = int(port_match.group(1)) if port_match else get_agent_port(card.name)
        
        # Extract skills from card
        skills = [skill.id for skill in card.skills] if card.skills else []
        
        # Register as active by default (tests/development mode)
        return self.registry.register_agent(card.name, port, skills, status="active")
    
    async def get_agent(self, agent_name: str) -> Optional[AgentCard]:
        """
        Get AgentCard for a specific agent.
        
        Args:
            agent_name: Name of the agent
            
        Returns:
            AgentCard if found, None otherwise
        """
        # Return stored card if available
        if agent_name in self._cards:
            return self._cards[agent_name]
        
        # Otherwise try to generate it
        try:
            card = generate_agent_card(agent_name)
            self._cards[agent_name] = card
            return card
        except Exception:
            return None
    
    async def auto_register_all_agents(self) -> int:
        """
        Auto-register all Chained agents.
        
        Returns:
            Number of agents registered
        """
        cards = generate_all_agent_cards()
        count = 0
        
        for agent_name, card in cards.items():
            # Store the card
            self._cards[agent_name] = card
            
            # Extract skills from card
            skills = [skill.id for skill in card.skills] if card.skills else []
            
            # Extract port from URL
            port = get_agent_port(agent_name)
            
            # Register as active
            self.registry.register_agent(agent_name, port, skills, status="active")
            count += 1
        
        return count
    
    async def discover_agents(
        self,
        skill: Optional[str] = None,
        active_only: bool = True,
    ) -> List[AgentRegistration]:
        """
        Discover agents by criteria.
        
        Args:
            skill: Filter by skill ID
            active_only: Only return active agents
            
        Returns:
            List of matching agent registrations
        """
        status = "active" if active_only else None
        return self.registry.list_agents(status=status, skill=skill)
    
    async def get_agent_card(self, agent_name: str) -> Optional[AgentCard]:
        """
        Fetch an agent's card from its endpoint.
        
        Args:
            agent_name: Name of the agent
            
        Returns:
            AgentCard if successful, None otherwise
        """
        agent = self.registry.get_agent(agent_name)
        if not agent:
            return None
        
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(agent.card_url)
                if response.status_code == 200:
                    return AgentCard(**response.json())
        except Exception:
            pass
        
        return None


# Singleton instance for convenience
_default_discovery_service: Optional[DiscoveryService] = None


def get_discovery_service(registry_file: Optional[Path] = None) -> DiscoveryService:
    """
    Get the default discovery service instance.
    
    Args:
        registry_file: Path to registry file (used only on first call)
        
    Returns:
        DiscoveryService instance
    """
    global _default_discovery_service
    
    if _default_discovery_service is None:
        if registry_file is None:
            # Default location
            registry_file = Path(__file__).parent.parent.parent / ".github" / "agent-system" / "a2a-registry.json"
        
        _default_discovery_service = DiscoveryService(registry_file)
    
    return _default_discovery_service


if __name__ == "__main__":
    import sys
    
    # Simple CLI for testing
    service = get_discovery_service()
    
    if len(sys.argv) > 1 and sys.argv[1] == "register-all":
        # Run async function
        count = asyncio.run(service.auto_register_all_agents())
        print(f"Registered {count} agents")
        print(f"Registry saved to: {service.registry.registry_file}")
    else:
        print("Usage: python -m tools.a2a.discovery register-all")
