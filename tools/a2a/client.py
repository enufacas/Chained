"""
A2A Client Library for agent-to-agent communication.

This module provides helper functions for Chained agents to communicate
with each other using the A2A protocol.
"""

from typing import Optional, Dict, Any, List
from uuid import uuid4

import httpx
from a2a.client import A2ACardResolver, A2AClient
from a2a.types import (
    AgentCard,
    MessageSendParams,
    SendMessageRequest,
    SendStreamingMessageRequest,
)

from .discovery import get_discovery_service, AgentRegistration


class ChainedA2AClient:
    """
    Client for Chained agents to communicate via A2A protocol.
    
    This client simplifies agent-to-agent communication by handling:
    - Agent discovery
    - Card fetching
    - Message creation
    - Task delegation
    """
    
    def __init__(self, httpx_client: Optional[httpx.AsyncClient] = None):
        """
        Initialize the A2A client.
        
        Args:
            httpx_client: Optional httpx client (created if None)
        """
        self._httpx_client = httpx_client
        self._own_httpx_client = httpx_client is None
        self.discovery = get_discovery_service()
    
    async def __aenter__(self):
        """Async context manager entry."""
        if self._own_httpx_client:
            self._httpx_client = httpx.AsyncClient(timeout=30.0)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self._own_httpx_client and self._httpx_client:
            await self._httpx_client.aclose()
    
    async def discover_agent(
        self,
        agent_name: Optional[str] = None,
        skill: Optional[str] = None,
    ) -> Optional[AgentRegistration]:
        """
        Discover an agent by name or skill.
        
        Args:
            agent_name: Specific agent name to find
            skill: Skill ID to search for
            
        Returns:
            AgentRegistration if found, None otherwise
        """
        if agent_name:
            return self.discovery.registry.get_agent(agent_name)
        
        if skill:
            agents = await self.discovery.discover_agents(skill=skill, active_only=True)
            return agents[0] if agents else None
        
        return None
    
    async def get_agent_card(self, agent_name: str) -> Optional[AgentCard]:
        """
        Fetch an agent's card.
        
        Args:
            agent_name: Name of the agent
            
        Returns:
            AgentCard if successful
        """
        agent = await self.discover_agent(agent_name=agent_name)
        if not agent:
            return None
        
        try:
            resolver = A2ACardResolver(
                httpx_client=self._httpx_client,
                base_url=agent.url.rstrip('/'),
            )
            return await resolver.get_agent_card()
        except Exception:
            return None
    
    async def send_message(
        self,
        agent_name: str,
        message: str,
        **kwargs: Any,
    ) -> Optional[Dict[str, Any]]:
        """
        Send a message to an agent.
        
        Args:
            agent_name: Target agent name
            message: Message text to send
            **kwargs: Additional parameters
            
        Returns:
            Response dict if successful, None otherwise
        """
        # Get agent card
        card = await self.get_agent_card(agent_name)
        if not card:
            return None
        
        # Create A2A client
        client = A2AClient(
            httpx_client=self._httpx_client,
            agent_card=card,
        )
        
        # Create message request
        send_message_payload = {
            'message': {
                'role': 'user',
                'parts': [
                    {'kind': 'text', 'text': message}
                ],
                'messageId': uuid4().hex,
            },
        }
        
        request = SendMessageRequest(
            id=str(uuid4()),
            params=MessageSendParams(**send_message_payload)
        )
        
        try:
            response = await client.send_message(request)
            return response.model_dump(mode='json', exclude_none=True)
        except Exception:
            return None
    
    async def send_message_streaming(
        self,
        agent_name: str,
        message: str,
        **kwargs: Any,
    ):
        """
        Send a message to an agent with streaming response.
        
        Args:
            agent_name: Target agent name
            message: Message text to send
            **kwargs: Additional parameters
            
        Yields:
            Response chunks as they arrive
        """
        # Get agent card
        card = await self.get_agent_card(agent_name)
        if not card:
            return
        
        # Create A2A client
        client = A2AClient(
            httpx_client=self._httpx_client,
            agent_card=card,
        )
        
        # Create streaming message request
        send_message_payload = {
            'message': {
                'role': 'user',
                'parts': [
                    {'kind': 'text', 'text': message}
                ],
                'messageId': uuid4().hex,
            },
        }
        
        request = SendStreamingMessageRequest(
            id=str(uuid4()),
            params=MessageSendParams(**send_message_payload)
        )
        
        try:
            stream = client.send_message_streaming(request)
            async for chunk in stream:
                yield chunk
        except Exception:
            return
    
    async def delegate_task(
        self,
        agent_name: str,
        task_description: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> Optional[str]:
        """
        Delegate a task to another agent.
        
        Args:
            agent_name: Target agent name
            task_description: Description of the task to delegate
            context: Optional context information
            
        Returns:
            Task ID if successful, None otherwise
        """
        # For now, this is the same as send_message
        # In future, we can add task tracking and lifecycle management
        response = await self.send_message(agent_name, task_description)
        
        if response:
            # Extract task/message ID from response
            # This is simplified - actual implementation would track task IDs
            return response.get('id', str(uuid4()))
        
        return None


async def discover_agents_by_skill(skill: str) -> List[str]:
    """
    Discover agents that provide a specific skill.
    
    Args:
        skill: Skill ID to search for
        
    Returns:
        List of agent names that provide the skill
    """
    discovery = get_discovery_service()
    agents = await discovery.discover_agents(skill=skill, active_only=True)
    return [agent.agent_name for agent in agents]


async def send_to_agent(
    agent_name: str,
    message: str,
) -> Optional[Dict[str, Any]]:
    """
    Simple helper to send a message to an agent.
    
    Args:
        agent_name: Target agent name
        message: Message to send
        
    Returns:
        Response dict if successful
    """
    async with ChainedA2AClient() as client:
        return await client.send_message(agent_name, message)


if __name__ == "__main__":
    import asyncio
    import sys
    
    async def main():
        """Simple CLI test."""
        if len(sys.argv) < 3:
            print("Usage: python -m tools.a2a.client <agent-name> <message>")
            sys.exit(1)
        
        agent_name = sys.argv[1]
        message = sys.argv[2]
        
        print(f"Sending to {agent_name}: {message}")
        
        response = await send_to_agent(agent_name, message)
        
        if response:
            print("\nResponse:")
            import json
            print(json.dumps(response, indent=2))
        else:
            print(f"\nFailed to communicate with {agent_name}")
    
    asyncio.run(main())
