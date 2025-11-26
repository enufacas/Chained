"""
Agent Executor implementation for Chained agents.

This module provides a base AgentExecutor that wraps Chained agents
for execution via the A2A protocol.
"""

import asyncio
from typing import Optional

from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.utils import new_agent_text_message

from .agent_card import parse_agent_definition


class ChainedAgentExecutor(AgentExecutor):
    """
    Agent Executor for Chained agents.
    
    This executor wraps a Chained agent and makes it available via A2A protocol.
    It handles task execution, cancellation, and event streaming.
    
    Example:
        >>> executor = ChainedAgentExecutor(agent_name="engineer-master")
        >>> # Use with A2A server
        >>> request_handler = DefaultRequestHandler(
        ...     agent_executor=executor,
        ...     task_store=InMemoryTaskStore(),
        ... )
    """
    
    def __init__(self, agent_name: str):
        """
        Initialize the executor.
        
        Args:
            agent_name: Name of the Chained agent to wrap
        """
        self.agent_name = agent_name
        self.metadata = parse_agent_definition(agent_name)
        self._running_tasks = {}
    
    async def execute(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ) -> None:
        """
        Execute the agent task.
        
        This method is called by the A2A server when a task is submitted.
        It processes the request and enqueues response events.
        
        Args:
            context: Request context containing the task details
            event_queue: Queue for sending response events
        """
        # Extract the message from context
        request = context.request
        params = request.params
        
        if not params or not hasattr(params, 'message'):
            await event_queue.enqueue_event(
                new_agent_text_message("Error: No message provided in request")
            )
            return
        
        message = params.message
        
        # Extract text from message parts
        user_input = self._extract_text_from_message(message)
        
        # Send initial acknowledgment
        await event_queue.enqueue_event(
            new_agent_text_message(f"Agent {self.agent_name} processing request...")
        )
        
        try:
            # Store task for cancellation support
            task_id = context.task_id if hasattr(context, 'task_id') else None
            current_task = asyncio.current_task()
            if task_id and current_task:
                self._running_tasks[task_id] = current_task
            
            # Simulate agent processing
            # TODO: This is a placeholder - integrate with actual Chained agent execution
            result = await self._process_agent_task(user_input, event_queue)
            
            # Send final result
            await event_queue.enqueue_event(
                new_agent_text_message(result)
            )
            
        except asyncio.CancelledError:
            await event_queue.enqueue_event(
                new_agent_text_message(f"Task cancelled for {self.agent_name}")
            )
            raise
        
        except Exception as e:
            await event_queue.enqueue_event(
                new_agent_text_message(f"Error in {self.agent_name}: {str(e)}")
            )
            raise
        
        finally:
            # Clean up task tracking
            if task_id and task_id in self._running_tasks:
                del self._running_tasks[task_id]
    
    async def cancel(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ) -> None:
        """
        Cancel a running task.
        
        Args:
            context: Request context
            event_queue: Event queue
        """
        task_id = context.task_id if hasattr(context, 'task_id') else None
        
        if task_id and task_id in self._running_tasks:
            task = self._running_tasks[task_id]
            task.cancel()
            await event_queue.enqueue_event(
                new_agent_text_message(f"Cancelling task {task_id}")
            )
        else:
            await event_queue.enqueue_event(
                new_agent_text_message("No active task to cancel")
            )
    
    def _extract_text_from_message(self, message) -> str:
        """
        Extract text content from A2A message.
        
        Args:
            message: A2A message object
            
        Returns:
            Extracted text content
        """
        if not hasattr(message, 'parts'):
            return str(message)
        
        text_parts = []
        for part in message.parts:
            if hasattr(part, 'kind') and part.kind == 'text':
                if hasattr(part, 'text'):
                    text_parts.append(part.text)
        
        return "\n".join(text_parts) if text_parts else ""
    
    async def _process_agent_task(
        self,
        user_input: str,
        event_queue: EventQueue,
    ) -> str:
        """
        Process the agent task.
        
        This is a placeholder implementation that will be replaced with
        actual agent execution logic.
        
        Args:
            user_input: User's input message
            event_queue: Queue for sending progress updates
            
        Returns:
            Agent's response
        """
        # Send progress update
        await event_queue.enqueue_event(
            new_agent_text_message(f"Analyzing request with {self.agent_name}...")
        )
        
        # Simulate processing time
        await asyncio.sleep(1)
        
        # Generate response based on agent specialization
        specialization = self.metadata.get("specialization", "general")
        description = self.metadata.get("description", "")
        
        response = (
            f"Response from {self.agent_name} ({specialization}):\n\n"
            f"I am specialized in: {description}\n\n"
            f"Your request: {user_input}\n\n"
            f"[TODO: Implement actual agent execution logic]\n\n"
            f"This is a placeholder response. The agent would normally:\n"
            f"1. Analyze the request based on my specialization\n"
            f"2. Execute the appropriate tools and workflows\n"
            f"3. Return the results\n\n"
            f"Future integration will connect to GitHub Copilot or other agent runtimes."
        )
        
        return response


# Future: Add specialized executors for different agent types
class GitHubCopilotExecutor(ChainedAgentExecutor):
    """
    Executor that integrates with GitHub Copilot for agent execution.
    
    This is a future enhancement that would:
    - Trigger GitHub Copilot coding agent via GitHub Actions
    - Stream results back via A2A protocol
    - Handle authentication and authorization
    """
    pass


class LocalToolExecutor(ChainedAgentExecutor):
    """
    Executor that runs agents using local tools (bash, Python, etc.).
    
    This is a future enhancement that would:
    - Execute tools directly in the container
    - Manage file I/O and state
    - Provide isolated execution environments
    """
    pass
