"""
Gemini A2A Agent Executor.

This module provides an A2A-compliant AgentExecutor that wraps Gemini CLI
for executing agent tasks. This follows the official A2A samples pattern from:
https://github.com/a2aproject/a2a-samples

Based on the helloworld sample structure:
- Agent class handles the actual AI invocation (GeminiAgent)
- AgentExecutor wraps it for A2A protocol compliance (GeminiAgentExecutor)
"""

import asyncio
import os
from typing import Optional

from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.utils import new_agent_text_message

from .agent_card import parse_agent_definition


class GeminiAgent:
    """
    Gemini AI Agent that executes tasks via Gemini CLI.
    
    This follows the same pattern as HelloWorldAgent in the A2A samples,
    but uses Gemini CLI for actual AI-powered responses.
    """
    
    def __init__(
        self,
        agent_name: str,
        model: str = "gemini-2.5-flash",
        api_key: Optional[str] = None,
    ):
        """
        Initialize the Gemini agent.
        
        Args:
            agent_name: Name of the Chained agent (for persona/context)
            model: Gemini model to use
            api_key: Gemini API key (defaults to GEMINI_API_KEY env var)
        """
        self.agent_name = agent_name
        self.model = model
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
        self.metadata = parse_agent_definition(agent_name)
    
    async def invoke(self, message: str, context: Optional[str] = None) -> str:
        """
        Invoke Gemini to process the message.
        
        Args:
            message: User message to process
            context: Optional additional context
            
        Returns:
            Gemini's response as a string
        """
        # Build the prompt with agent persona
        specialization = self.metadata.get("specialization", "general")
        description = self.metadata.get("description", "")
        
        prompt = f"""You are {self.agent_name}, a specialized AI agent.

Specialization: {specialization}
Description: {description}

{f"Additional Context: {context}" if context else ""}

User Request:
{message}

Provide a helpful, detailed response from your specialized perspective.
"""
        
        # Execute via Gemini CLI
        try:
            result = await self._run_gemini_cli(prompt)
            return result
        except Exception as e:
            return f"Error invoking Gemini: {str(e)}"
    
    async def _run_gemini_cli(self, prompt: str) -> str:
        """
        Run Gemini CLI with the given prompt.
        
        This uses the gemini CLI tool which is the official way to
        interact with Gemini in GitHub Actions workflows.
        """
        # Build the gemini command
        cmd = [
            "gemini",
            "--model", self.model,
        ]
        
        if self.api_key:
            env = os.environ.copy()
            env["GEMINI_API_KEY"] = self.api_key
        else:
            env = os.environ.copy()
        
        try:
            # Run gemini with the prompt from stdin
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=env,
            )
            
            stdout, stderr = await process.communicate(input=prompt.encode())
            
            if process.returncode != 0:
                # If CLI fails, try using the Python API directly
                return await self._run_gemini_python(prompt)
            
            return stdout.decode().strip()
            
        except FileNotFoundError:
            # gemini CLI not installed, fall back to Python API
            return await self._run_gemini_python(prompt)
    
    async def _run_gemini_python(self, prompt: str) -> str:
        """
        Fallback: Run Gemini using the Python API directly.
        
        This is used when the CLI is not available.
        """
        try:
            import google.generativeai as genai
            
            if self.api_key:
                genai.configure(api_key=self.api_key)
            
            model = genai.GenerativeModel(self.model)
            response = await asyncio.to_thread(
                model.generate_content, prompt
            )
            
            return response.text
            
        except ImportError:
            return (
                f"[{self.agent_name}] Gemini API not available. "
                "Install google-generativeai: pip install google-generativeai"
            )
        except Exception as e:
            return f"[{self.agent_name}] Error: {str(e)}"


class GeminiAgentExecutor(AgentExecutor):
    """
    A2A Agent Executor that uses Gemini for task execution.
    
    This follows the official A2A samples pattern:
    - Implements AgentExecutor interface
    - Uses execute() for task processing
    - Uses cancel() for task cancellation
    - Streams events via EventQueue
    
    Example:
        >>> executor = GeminiAgentExecutor(agent_name="engineer-master")
        >>> # Use with A2A server
        >>> from a2a.server.request_handlers import DefaultRequestHandler
        >>> from a2a.server.tasks import InMemoryTaskStore
        >>> handler = DefaultRequestHandler(
        ...     agent_executor=executor,
        ...     task_store=InMemoryTaskStore(),
        ... )
    """
    
    def __init__(
        self,
        agent_name: str,
        model: str = "gemini-2.5-flash",
        api_key: Optional[str] = None,
    ):
        """
        Initialize the Gemini executor.
        
        Args:
            agent_name: Name of the Chained agent
            model: Gemini model to use
            api_key: Optional API key
        """
        self.agent_name = agent_name
        self.agent = GeminiAgent(
            agent_name=agent_name,
            model=model,
            api_key=api_key,
        )
        self._running_tasks = {}
    
    async def execute(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ) -> None:
        """
        Execute the agent task using Gemini.
        
        This method is called by the A2A server when a task is submitted.
        It follows the A2A protocol for event streaming.
        
        Args:
            context: Request context containing task details
            event_queue: Queue for sending response events (A2A §4.1.9 Artifact)
        """
        # Extract message from context (A2A §4.1.4 Message)
        request = context.request
        params = request.params
        
        if not params or not hasattr(params, 'message'):
            await event_queue.enqueue_event(
                new_agent_text_message("Error: No message provided in request")
            )
            return
        
        message = params.message
        user_input = self._extract_text_from_message(message)
        
        # Send working status (A2A §4.1.3 TaskState: working)
        await event_queue.enqueue_event(
            new_agent_text_message(f"[{self.agent_name}] Processing request...")
        )
        
        try:
            # Track task for cancellation support
            task_id = getattr(context, 'task_id', None)
            current_task = asyncio.current_task()
            if task_id and current_task:
                self._running_tasks[task_id] = current_task
            
            # Invoke Gemini agent
            result = await self.agent.invoke(user_input)
            
            # Send result as Artifact (A2A §4.1.9)
            await event_queue.enqueue_event(
                new_agent_text_message(result)
            )
            
        except asyncio.CancelledError:
            await event_queue.enqueue_event(
                new_agent_text_message(f"[{self.agent_name}] Task cancelled")
            )
            raise
        
        except Exception as e:
            await event_queue.enqueue_event(
                new_agent_text_message(f"[{self.agent_name}] Error: {str(e)}")
            )
            raise
        
        finally:
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
        task_id = getattr(context, 'task_id', None)
        
        if task_id and task_id in self._running_tasks:
            task = self._running_tasks[task_id]
            task.cancel()
            await event_queue.enqueue_event(
                new_agent_text_message(f"[{self.agent_name}] Cancelling task {task_id}")
            )
        else:
            await event_queue.enqueue_event(
                new_agent_text_message(f"[{self.agent_name}] No active task to cancel")
            )
    
    def _extract_text_from_message(self, message) -> str:
        """Extract text content from A2A message (§4.1.4 Message)."""
        if not hasattr(message, 'parts'):
            return str(message)
        
        text_parts = []
        for part in message.parts:
            if hasattr(part, 'kind') and part.kind == 'text':
                if hasattr(part, 'text'):
                    text_parts.append(part.text)
        
        return "\n".join(text_parts) if text_parts else ""


def create_gemini_agent_server(
    agent_name: str,
    port: int = 9999,
    model: str = "gemini-2.5-flash",
):
    """
    Create an A2A server for a Gemini-powered agent.
    
    This follows the official A2A samples pattern from:
    https://github.com/a2aproject/a2a-samples/blob/main/samples/python/agents/helloworld/__main__.py
    
    Args:
        agent_name: Name of the Chained agent
        port: Port to run on
        model: Gemini model to use
        
    Returns:
        A2AStarletteApplication ready to run
        
    Example:
        >>> server = create_gemini_agent_server("engineer-master", port=8080)
        >>> import uvicorn
        >>> uvicorn.run(server.build(), host="0.0.0.0", port=8080)
    """
    from a2a.server.apps import A2AStarletteApplication
    from a2a.server.request_handlers import DefaultRequestHandler
    from a2a.server.tasks import InMemoryTaskStore
    
    from .agent_card import generate_agent_card
    
    # Generate AgentCard (A2A §4.4.1)
    agent_card = generate_agent_card(agent_name, port=port)
    
    # Create executor with Gemini backend
    executor = GeminiAgentExecutor(
        agent_name=agent_name,
        model=model,
    )
    
    # Create request handler (A2A §3.1.1 SendMessage)
    request_handler = DefaultRequestHandler(
        agent_executor=executor,
        task_store=InMemoryTaskStore(),
    )
    
    # Create A2A server application
    server = A2AStarletteApplication(
        agent_card=agent_card,
        http_handler=request_handler,
    )
    
    return server


if __name__ == "__main__":
    import sys
    import uvicorn
    
    if len(sys.argv) < 2:
        print("Usage: python -m tools.a2a.gemini_executor <agent-name> [port] [model]")
        print("\nExample:")
        print("  python -m tools.a2a.gemini_executor engineer-master 8080 gemini-2.5-flash")
        sys.exit(1)
    
    agent_name = sys.argv[1]
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 9999
    model = sys.argv[3] if len(sys.argv) > 3 else "gemini-2.5-flash"
    
    print(f"Starting A2A Gemini Agent Server")
    print(f"  Agent: {agent_name}")
    print(f"  Port: {port}")
    print(f"  Model: {model}")
    print(f"  Agent Card: http://localhost:{port}/.well-known/agent-card")
    print()
    
    server = create_gemini_agent_server(agent_name, port, model)
    uvicorn.run(server.build(), host="0.0.0.0", port=port)
