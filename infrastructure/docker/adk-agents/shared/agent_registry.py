"""
Agent Registry - Dynamic Agent Discovery and Management
========================================================

This module provides agent discovery, registration, and capability tracking
for the multi-agent team system. It supports:

1. Dynamic agent discovery from configured URLs
2. Agent card fetching per A2A spec §4.4.1
3. Agent capability and status tracking
4. Health monitoring for registered agents
"""

import asyncio
import json
import os
from datetime import datetime
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field, asdict
from enum import Enum

import httpx


class AgentStatus(str, Enum):
    """Agent availability status."""
    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"
    BUSY = "busy"
    UNKNOWN = "unknown"


@dataclass
class AgentSkill:
    """Agent skill definition."""
    id: str
    name: str
    description: str
    tags: List[str] = field(default_factory=list)


@dataclass
class RegisteredAgent:
    """Registered agent with capabilities and status."""
    id: str
    name: str
    display_name: str
    description: str
    url: str
    version: str = "1.0.0"
    protocol_version: str = "0.3.0"
    skills: List[AgentSkill] = field(default_factory=list)
    capabilities: Dict[str, bool] = field(default_factory=dict)
    status: AgentStatus = AgentStatus.UNKNOWN
    last_health_check: Optional[str] = None
    response_time_ms: Optional[int] = None
    icon: str = "🤖"
    category: str = "general"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            **asdict(self),
            "status": self.status.value,
            "skills": [asdict(s) for s in self.skills],
        }


class AgentRegistry:
    """
    Dynamic agent registry for multi-agent team system.
    
    Supports:
    - Registering agents from URLs
    - Fetching agent cards from /.well-known/agent.json
    - Health checking registered agents
    - Capability-based agent discovery
    """
    
    # Default agent configurations
    DEFAULT_AGENTS = {
        "academic-research": {
            "display_name": "Academic Research",
            "icon": "🔬",
            "category": "research",
            "url_env": "AGENT_ACADEMIC_RESEARCH_URL",
            "default_url": "http://localhost:8081",
        },
        "google-trends": {
            "display_name": "Google Trends",
            "icon": "📈",
            "category": "seo",
            "url_env": "AGENT_GOOGLE_TRENDS_URL",
            "default_url": "http://localhost:8083",
        },
        "blog-writer": {
            "display_name": "Blog Writer",
            "icon": "✍️",
            "category": "content",
            "url_env": "AGENT_BLOG_WRITER_URL",
            "default_url": "http://localhost:8082",
        },
        "code-reviewer": {
            "display_name": "Code Reviewer",
            "icon": "🔍",
            "category": "development",
            "url_env": "AGENT_CODE_REVIEWER_URL",
            "default_url": "http://localhost:8084",
        },
        "data-analyst": {
            "display_name": "Data Analyst",
            "icon": "📊",
            "category": "analytics",
            "url_env": "AGENT_DATA_ANALYST_URL",
            "default_url": "http://localhost:8085",
        },
        "image-generator": {
            "display_name": "Image Generator",
            "icon": "🎨",
            "category": "visual",
            "url_env": "AGENT_IMAGE_GENERATOR_URL",
            "default_url": "http://localhost:8086",
        },
    }
    
    def __init__(self, timeout: float = 10.0):
        self._agents: Dict[str, RegisteredAgent] = {}
        self._timeout = timeout
        self._client: Optional[httpx.AsyncClient] = None
        
    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=self._timeout)
        return self._client
    
    async def close(self):
        """Close HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None
    
    def _get_agent_url(self, agent_id: str) -> Optional[str]:
        """Get agent URL from environment or defaults."""
        if agent_id in self.DEFAULT_AGENTS:
            config = self.DEFAULT_AGENTS[agent_id]
            url = os.getenv(config["url_env"])
            if url:
                return url
            # Only use default in development
            if os.getenv("NODE_ENV") == "development":
                return config["default_url"]
        return None
    
    async def discover_agent(self, agent_id: str, url: Optional[str] = None) -> Optional[RegisteredAgent]:
        """
        Discover an agent by fetching its Agent Card.
        
        Args:
            agent_id: Agent identifier
            url: Optional URL override
            
        Returns:
            RegisteredAgent if successful, None otherwise
        """
        agent_url = url or self._get_agent_url(agent_id)
        if not agent_url:
            return None
        
        try:
            client = await self._get_client()
            start_time = datetime.utcnow()
            
            # Fetch agent card
            response = await client.get(f"{agent_url}/.well-known/agent.json")
            response.raise_for_status()
            
            end_time = datetime.utcnow()
            response_time = int((end_time - start_time).total_seconds() * 1000)
            
            card = response.json()
            
            # Get default config if available
            default_config = self.DEFAULT_AGENTS.get(agent_id, {})
            
            # Create registered agent
            agent = RegisteredAgent(
                id=agent_id,
                name=card.get("name", agent_id),
                display_name=default_config.get("display_name", card.get("name", agent_id)),
                description=card.get("description", ""),
                url=agent_url,
                version=card.get("version", "1.0.0"),
                protocol_version=card.get("protocolVersion", "0.3.0"),
                skills=[
                    AgentSkill(
                        id=s.get("id", ""),
                        name=s.get("name", ""),
                        description=s.get("description", ""),
                        tags=s.get("tags", []),
                    )
                    for s in card.get("skills", [])
                ],
                capabilities=card.get("capabilities", {}),
                status=AgentStatus.AVAILABLE,
                last_health_check=datetime.utcnow().isoformat(),
                response_time_ms=response_time,
                icon=default_config.get("icon", "🤖"),
                category=default_config.get("category", "general"),
            )
            
            self._agents[agent_id] = agent
            return agent
            
        except Exception as e:
            print(f"⚠️ Failed to discover agent {agent_id}: {e}")
            return None
    
    async def discover_all_agents(self) -> List[RegisteredAgent]:
        """Discover all configured agents."""
        tasks = [
            self.discover_agent(agent_id)
            for agent_id in self.DEFAULT_AGENTS.keys()
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return [r for r in results if isinstance(r, RegisteredAgent)]
    
    async def check_agent_health(self, agent_id: str) -> AgentStatus:
        """Check health of a registered agent."""
        agent = self._agents.get(agent_id)
        if not agent:
            return AgentStatus.UNKNOWN
        
        try:
            client = await self._get_client()
            start_time = datetime.utcnow()
            
            response = await client.get(f"{agent.url}/health")
            response.raise_for_status()
            
            end_time = datetime.utcnow()
            response_time = int((end_time - start_time).total_seconds() * 1000)
            
            agent.status = AgentStatus.AVAILABLE
            agent.last_health_check = datetime.utcnow().isoformat()
            agent.response_time_ms = response_time
            
            return AgentStatus.AVAILABLE
            
        except Exception:
            agent.status = AgentStatus.UNAVAILABLE
            agent.last_health_check = datetime.utcnow().isoformat()
            return AgentStatus.UNAVAILABLE
    
    async def check_all_health(self) -> Dict[str, AgentStatus]:
        """Check health of all registered agents."""
        results = {}
        for agent_id in self._agents:
            results[agent_id] = await self.check_agent_health(agent_id)
        return results
    
    def get_agent(self, agent_id: str) -> Optional[RegisteredAgent]:
        """Get a registered agent by ID."""
        return self._agents.get(agent_id)
    
    def get_all_agents(self) -> List[RegisteredAgent]:
        """Get all registered agents."""
        return list(self._agents.values())
    
    def get_available_agents(self) -> List[RegisteredAgent]:
        """Get all available agents."""
        return [a for a in self._agents.values() if a.status == AgentStatus.AVAILABLE]
    
    def get_agents_by_category(self, category: str) -> List[RegisteredAgent]:
        """Get agents by category."""
        return [a for a in self._agents.values() if a.category == category]
    
    def get_agents_by_skill(self, skill_tag: str) -> List[RegisteredAgent]:
        """Get agents that have a specific skill tag."""
        result = []
        for agent in self._agents.values():
            for skill in agent.skills:
                if skill_tag in skill.tags:
                    result.append(agent)
                    break
        return result
    
    def register_custom_agent(self, agent: RegisteredAgent):
        """Register a custom agent."""
        self._agents[agent.id] = agent
    
    def unregister_agent(self, agent_id: str):
        """Unregister an agent."""
        if agent_id in self._agents:
            del self._agents[agent_id]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert registry to dictionary."""
        return {
            "agents": {k: v.to_dict() for k, v in self._agents.items()},
            "available_count": len(self.get_available_agents()),
            "total_count": len(self._agents),
        }


# Global registry instance
_registry: Optional[AgentRegistry] = None


def get_registry() -> AgentRegistry:
    """Get or create global agent registry."""
    global _registry
    if _registry is None:
        _registry = AgentRegistry()
    return _registry


async def initialize_registry() -> AgentRegistry:
    """Initialize and discover all agents."""
    registry = get_registry()
    await registry.discover_all_agents()
    return registry
