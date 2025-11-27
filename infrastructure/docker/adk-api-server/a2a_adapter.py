"""
A2A Protocol Adapter - Bridges ADK API to A2A Protocol
======================================================

This module provides an adapter that translates ADK API calls
to A2A protocol calls for communication with deployed A2A agents.
"""

import json
import logging
import os
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, AsyncIterator

import httpx

# Configure logging
logger = logging.getLogger(__name__)


@dataclass
class AgentConfig:
    """Configuration for an A2A agent."""

    name: str
    url: str
    description: str = ""
    version: str = "1.0.0"
    skills: List[Dict[str, Any]] = field(default_factory=list)
    capabilities: Dict[str, bool] = field(default_factory=dict)


@dataclass
class A2AMessage:
    """A2A Protocol Message."""

    role: str
    parts: List[Dict[str, str]]

    def to_dict(self) -> Dict[str, Any]:
        return {"role": self.role, "parts": self.parts}


@dataclass
class A2ATask:
    """A2A Protocol Task."""

    id: str
    status: Dict[str, Any]
    artifacts: List[Dict[str, Any]] = field(default_factory=list)
    context_id: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "A2ATask":
        return cls(
            id=data.get("id", ""),
            status=data.get("status", {}),
            artifacts=data.get("artifacts", []),
            context_id=data.get("contextId"),
        )


class A2AAdapter:
    """Adapter for communicating with A2A protocol agents."""

    def __init__(self, timeout: float = 60.0):
        self.timeout = timeout
        self._agents: Dict[str, AgentConfig] = {}
        self._client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=self.timeout)
        return self._client

    async def close(self):
        """Close the HTTP client."""
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    def discover_agents_from_env(self) -> Dict[str, AgentConfig]:
        """Discover agents from environment variables.

        Environment variables format:
        - AGENT_<NAME>_URL=https://agent-url.run.app
        - AGENT_<NAME>_DESCRIPTION=Agent description

        Example:
        - AGENT_ACADEMIC_RESEARCH_URL=https://chained-academic-research-xxx.a.run.app
        """
        agents = {}

        # Look for AGENT_*_URL environment variables
        for key, value in os.environ.items():
            if key.startswith("AGENT_") and key.endswith("_URL"):
                # Extract agent name (e.g., AGENT_ACADEMIC_RESEARCH_URL -> academic-research)
                name_parts = key[6:-4].lower().split("_")  # Remove AGENT_ and _URL
                agent_name = "-".join(name_parts)

                # Get description if available
                desc_key = f"AGENT_{'_'.join(name_parts).upper()}_DESCRIPTION"
                description = os.getenv(desc_key, f"{agent_name} agent")

                agents[agent_name] = AgentConfig(
                    name=agent_name,
                    url=value,
                    description=description,
                )

        self._agents = agents
        return agents

    def add_agent(self, config: AgentConfig):
        """Add an agent configuration."""
        self._agents[config.name] = config

    def get_agent(self, name: str) -> Optional[AgentConfig]:
        """Get an agent by name."""
        return self._agents.get(name)

    def list_agents(self) -> List[AgentConfig]:
        """List all configured agents."""
        return list(self._agents.values())

    async def fetch_agent_card(self, agent_url: str) -> Optional[Dict[str, Any]]:
        """Fetch the A2A Agent Card from an agent.

        Args:
            agent_url: Base URL of the agent

        Returns:
            Agent Card dictionary or None if not available
        """
        try:
            client = await self._get_client()
            response = await client.get(f"{agent_url}/.well-known/agent.json")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.warning(f"Error fetching agent card from {agent_url}: {e}")
            return None

    async def refresh_agent_details(self, agent_name: str) -> Optional[AgentConfig]:
        """Refresh agent details by fetching the Agent Card.

        Args:
            agent_name: Name of the agent to refresh

        Returns:
            Updated AgentConfig or None if not found
        """
        agent = self._agents.get(agent_name)
        if agent is None:
            return None

        card = await self.fetch_agent_card(agent.url)
        if card:
            agent.description = card.get("description", agent.description)
            agent.version = card.get("version", agent.version)
            agent.skills = card.get("skills", [])
            agent.capabilities = card.get("capabilities", {})
            self._agents[agent_name] = agent

        return agent

    async def send_message(
        self,
        agent_name: str,
        message: str,
        context_id: Optional[str] = None,
        reference_task_ids: Optional[List[str]] = None,
    ) -> A2ATask:
        """Send a message to an A2A agent.

        Args:
            agent_name: Name of the agent
            message: Message text to send
            context_id: Optional context/session ID
            reference_task_ids: Optional list of reference task IDs

        Returns:
            A2ATask with the response

        Raises:
            ValueError: If agent not found
            httpx.HTTPError: If request fails
        """
        agent = self._agents.get(agent_name)
        if agent is None:
            raise ValueError(f"Agent not found: {agent_name}")

        # Build A2A SendMessage request
        request_data = {
            "message": {"role": "user", "parts": [{"text": message}]},
        }

        if context_id:
            request_data["contextId"] = context_id

        if reference_task_ids:
            request_data["referenceTaskIds"] = reference_task_ids

        # Send request to A2A endpoint
        client = await self._get_client()
        response = await client.post(
            f"{agent.url}/a2a/tasks",
            json=request_data,
            headers={"Content-Type": "application/json"},
        )
        response.raise_for_status()

        return A2ATask.from_dict(response.json())

    async def check_health(self, agent_name: str) -> Dict[str, Any]:
        """Check the health of an agent.

        Args:
            agent_name: Name of the agent

        Returns:
            Health status dictionary
        """
        agent = self._agents.get(agent_name)
        if agent is None:
            return {"status": "error", "message": f"Agent not found: {agent_name}"}

        try:
            client = await self._get_client()
            response = await client.get(f"{agent.url}/health")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def stream_message(
        self,
        agent_name: str,
        message: str,
        context_id: Optional[str] = None,
    ) -> AsyncIterator[Dict[str, Any]]:
        """Stream a message response from an A2A agent.

        Note: Most A2A agents don't support streaming, so this falls back
        to a single response wrapped in SSE format.

        Args:
            agent_name: Name of the agent
            message: Message text to send
            context_id: Optional context/session ID

        Yields:
            SSE-formatted events
        """
        # Check if agent supports streaming
        agent = self._agents.get(agent_name)
        if agent is None:
            yield {
                "event": "error",
                "data": json.dumps({"error": f"Agent not found: {agent_name}"}),
            }
            return

        # Most A2A agents don't support streaming, so simulate it
        supports_streaming = agent.capabilities.get("streaming", False)

        if not supports_streaming:
            # Fall back to synchronous request wrapped in SSE
            try:
                task = await self.send_message(
                    agent_name, message, context_id=context_id
                )

                # Emit start event
                yield {
                    "event": "start",
                    "data": json.dumps(
                        {"task_id": task.id, "context_id": task.context_id}
                    ),
                }

                # Emit message content
                status_message = task.status.get("message", {})
                if status_message:
                    parts = status_message.get("parts", [])
                    for part in parts:
                        if "text" in part:
                            yield {
                                "event": "message",
                                "data": json.dumps({"content": part["text"]}),
                            }

                # Emit artifacts
                for artifact in task.artifacts:
                    yield {"event": "artifact", "data": json.dumps(artifact)}

                # Emit completion
                yield {
                    "event": "done",
                    "data": json.dumps(
                        {
                            "task_id": task.id,
                            "status": task.status.get("state", "completed"),
                        }
                    ),
                }

            except Exception as e:
                yield {"event": "error", "data": json.dumps({"error": str(e)})}


def create_adapter() -> A2AAdapter:
    """Create and configure an A2A adapter from environment."""
    adapter = A2AAdapter()
    adapter.discover_agents_from_env()
    return adapter
