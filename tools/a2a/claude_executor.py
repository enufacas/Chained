"""
Claude A2A Agent Executor.

This module provides an A2A-compliant AgentExecutor that wraps Claude (Anthropic)
for executing agent tasks. It supports both direct Anthropic API and Google Vertex AI
(via OIDC authentication).

Authentication Options:
1. Direct Anthropic API: Set ANTHROPIC_API_KEY environment variable
2. Google Vertex AI: Set CLAUDE_CODE_USE_VERTEX=1 and configure GCP credentials

For Vertex AI setup, see: docs/VERTEX_AI_CLAUDE_SETUP.md

Based on the official A2A samples pattern from:
https://github.com/a2aproject/a2a-samples
"""

import asyncio
import os
from typing import Any, Dict, List, Optional

from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.utils import new_agent_text_message

from .agent_card import parse_agent_definition


# Default model for Claude
DEFAULT_MODEL = "claude-sonnet-4-20250514"

# Vertex AI model name format (different from direct API)
VERTEX_MODEL_FORMAT = "claude-sonnet-4@20250514"


class ClaudeAgent:
    """
    Claude AI Agent that executes tasks via Anthropic API or Vertex AI.
    
    This follows the same pattern as GeminiAgent and GitHubModelsAgent,
    but uses Claude for AI-powered responses.
    
    Authentication:
    - Direct API: ANTHROPIC_API_KEY environment variable
    - Vertex AI: ANTHROPIC_VERTEX_PROJECT_ID, CLOUD_ML_REGION, and GCP credentials
    """
    
    def __init__(
        self,
        agent_name: str,
        model: str = DEFAULT_MODEL,
        api_key: Optional[str] = None,
        use_vertex: bool = False,
        vertex_project_id: Optional[str] = None,
        vertex_region: Optional[str] = None,
    ):
        """
        Initialize the Claude agent.
        
        Args:
            agent_name: Name of the Chained agent (for persona/context)
            model: Claude model to use (e.g., "claude-sonnet-4-20250514")
            api_key: Anthropic API key (for direct API, not Vertex AI)
            use_vertex: Use Google Vertex AI instead of direct Anthropic API
            vertex_project_id: GCP project ID for Vertex AI
            vertex_region: GCP region for Vertex AI (e.g., "us-east5")
        """
        self.agent_name = agent_name
        self.model = model
        self.use_vertex = use_vertex or os.environ.get("CLAUDE_CODE_USE_VERTEX", "").lower() in ("1", "true")
        
        # Direct API configuration
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        
        # Vertex AI configuration
        self.vertex_project_id = vertex_project_id or os.environ.get("ANTHROPIC_VERTEX_PROJECT_ID")
        self.vertex_region = vertex_region or os.environ.get("CLOUD_ML_REGION", "us-east5")
        
        # Parse agent metadata
        self.metadata = parse_agent_definition(agent_name)
        
        # Initialize client lazily
        self._client = None
    
    def _get_client(self):
        """Get or create the Anthropic client."""
        if self._client is not None:
            return self._client
        
        try:
            if self.use_vertex:
                # Use Vertex AI via AnthropicVertex client
                from anthropic import AnthropicVertex
                
                if not self.vertex_project_id:
                    raise ValueError(
                        "Vertex AI requires ANTHROPIC_VERTEX_PROJECT_ID environment variable"
                    )
                
                self._client = AnthropicVertex(
                    project_id=self.vertex_project_id,
                    region=self.vertex_region,
                )
                print(f"✓ Claude agent initialized with Vertex AI (region: {self.vertex_region})")
            else:
                # Use direct Anthropic API
                from anthropic import Anthropic
                
                if not self.api_key:
                    raise ValueError(
                        "Direct API requires ANTHROPIC_API_KEY environment variable. "
                        "Alternatively, set CLAUDE_CODE_USE_VERTEX=1 for Vertex AI."
                    )
                
                self._client = Anthropic(api_key=self.api_key)
                print("✓ Claude agent initialized with direct Anthropic API")
            
            return self._client
            
        except ImportError as e:
            raise ImportError(
                "Anthropic SDK not installed. Install with: pip install anthropic"
            ) from e
    
    def _get_model_name(self) -> str:
        """Get the appropriate model name based on provider."""
        if self.use_vertex:
            # Vertex AI uses different model naming convention
            # e.g., "claude-sonnet-4@20250514" instead of "claude-sonnet-4-20250514"
            if "@" not in self.model:
                # Convert standard model name to Vertex format
                parts = self.model.rsplit("-", 1)
                if len(parts) == 2 and parts[1].isdigit():
                    return f"{parts[0]}@{parts[1]}"
            return self.model
        return self.model
    
    async def invoke(
        self,
        message: str,
        context: Optional[str] = None,
        system_prompt: Optional[str] = None,
        max_tokens: int = 4096,
        temperature: float = 0.7,
    ) -> str:
        """
        Invoke Claude to process the message.
        
        Args:
            message: User message to process
            context: Optional additional context
            system_prompt: Optional system prompt override
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature (0.0-1.0)
            
        Returns:
            Claude's response as a string
        """
        # Build the system prompt with agent persona
        specialization = self.metadata.get("specialization", "general")
        description = self.metadata.get("description", "")
        
        if system_prompt is None:
            system_prompt = f"""You are {self.agent_name}, a specialized AI agent.

Specialization: {specialization}
Description: {description}

{f"Additional Context: {context}" if context else ""}

Provide a helpful, detailed response from your specialized perspective."""
        
        # Execute via Claude API
        try:
            result = await self._call_claude_api(
                message=message,
                system_prompt=system_prompt,
                max_tokens=max_tokens,
                temperature=temperature,
            )
            return result
        except Exception as e:
            return f"[{self.agent_name}] Error invoking Claude: {str(e)}"
    
    async def _call_claude_api(
        self,
        message: str,
        system_prompt: str,
        max_tokens: int,
        temperature: float,
    ) -> str:
        """
        Call the Claude API (direct or via Vertex AI).
        
        Uses synchronous API wrapped in asyncio.to_thread for non-blocking operation.
        """
        client = self._get_client()
        model_name = self._get_model_name()
        
        def sync_call():
            response = client.messages.create(
                model=model_name,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system_prompt,
                messages=[{"role": "user", "content": message}],
            )
            return response.content[0].text
        
        # Run synchronous API call in thread pool
        result = await asyncio.to_thread(sync_call)
        return result


class ClaudeAgentExecutor(AgentExecutor):
    """
    A2A Agent Executor that uses Claude (Anthropic) for task execution.
    
    This follows the official A2A samples pattern:
    - Implements AgentExecutor interface
    - Uses execute() for task processing
    - Uses cancel() for task cancellation
    - Streams events via EventQueue
    
    Example:
        >>> executor = ClaudeAgentExecutor(agent_name="engineer-master")
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
        model: str = DEFAULT_MODEL,
        api_key: Optional[str] = None,
        use_vertex: bool = False,
        vertex_project_id: Optional[str] = None,
        vertex_region: Optional[str] = None,
    ):
        """
        Initialize the Claude executor.
        
        Args:
            agent_name: Name of the Chained agent
            model: Claude model to use
            api_key: Optional API key (for direct API)
            use_vertex: Use Vertex AI instead of direct API
            vertex_project_id: GCP project ID for Vertex AI
            vertex_region: GCP region for Vertex AI
        """
        self.agent_name = agent_name
        self.agent = ClaudeAgent(
            agent_name=agent_name,
            model=model,
            api_key=api_key,
            use_vertex=use_vertex,
            vertex_project_id=vertex_project_id,
            vertex_region=vertex_region,
        )
        self._running_tasks: Dict[str, asyncio.Task] = {}
    
    async def execute(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ) -> None:
        """
        Execute the agent task using Claude.
        
        This method is called by the A2A server when a task is submitted.
        It follows the A2A protocol for event streaming.
        
        Args:
            context: Request context containing task details
            event_queue: Queue for sending response events (A2A §4.1.9 Artifact)
        """
        # Extract message from context (A2A §4.1.4 Message)
        request = context.request
        params = request.params
        
        if not params or not hasattr(params, "message"):
            await event_queue.enqueue_event(
                new_agent_text_message("Error: No message provided in request")
            )
            return
        
        message = params.message
        user_input = self._extract_text_from_message(message)
        
        # Send working status (A2A §4.1.3 TaskState: working)
        provider_info = "Vertex AI" if self.agent.use_vertex else "Direct API"
        await event_queue.enqueue_event(
            new_agent_text_message(
                f"[{self.agent_name}] Processing with Claude ({provider_info})..."
            )
        )
        
        try:
            # Track task for cancellation support
            task_id = getattr(context, "task_id", None)
            current_task = asyncio.current_task()
            if task_id and current_task:
                self._running_tasks[task_id] = current_task
            
            # Invoke Claude agent
            result = await self.agent.invoke(user_input)
            
            # Send result as Artifact (A2A §4.1.9)
            await event_queue.enqueue_event(new_agent_text_message(result))
            
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
        task_id = getattr(context, "task_id", None)
        
        if task_id and task_id in self._running_tasks:
            task = self._running_tasks[task_id]
            task.cancel()
            await event_queue.enqueue_event(
                new_agent_text_message(
                    f"[{self.agent_name}] Cancelling task {task_id}"
                )
            )
        else:
            await event_queue.enqueue_event(
                new_agent_text_message(
                    f"[{self.agent_name}] No active task to cancel"
                )
            )
    
    def _extract_text_from_message(self, message) -> str:
        """Extract text content from A2A message (§4.1.4 Message)."""
        if not hasattr(message, "parts"):
            return str(message)
        
        text_parts = []
        for part in message.parts:
            if hasattr(part, "kind") and part.kind == "text":
                if hasattr(part, "text"):
                    text_parts.append(part.text)
        
        return "\n".join(text_parts) if text_parts else ""


def create_claude_agent_server(
    agent_name: str,
    port: int = 9999,
    model: str = DEFAULT_MODEL,
    use_vertex: bool = False,
):
    """
    Create an A2A server for a Claude-powered agent.
    
    This follows the official A2A samples pattern.
    
    Args:
        agent_name: Name of the Chained agent
        port: Port to run on
        model: Claude model to use
        use_vertex: Use Vertex AI instead of direct API
        
    Returns:
        A2AStarletteApplication ready to run
        
    Example:
        >>> server = create_claude_agent_server("engineer-master", port=8080)
        >>> import uvicorn
        >>> uvicorn.run(server.build(), host="0.0.0.0", port=8080)
    """
    from a2a.server.apps import A2AStarletteApplication
    from a2a.server.request_handlers import DefaultRequestHandler
    from a2a.server.tasks import InMemoryTaskStore
    
    from .agent_card import generate_agent_card
    
    # Generate AgentCard (A2A §4.4.1)
    agent_card = generate_agent_card(agent_name, port=port)
    
    # Create executor with Claude backend
    executor = ClaudeAgentExecutor(
        agent_name=agent_name,
        model=model,
        use_vertex=use_vertex,
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


async def test_claude_api(
    model: str = DEFAULT_MODEL,
    use_vertex: bool = False,
) -> Dict[str, Any]:
    """
    Test the Claude API connection.
    
    Args:
        model: Model to test with
        use_vertex: Use Vertex AI instead of direct API
        
    Returns:
        Dict with test results
    """
    agent = ClaudeAgent(
        agent_name="test-agent",
        model=model,
        use_vertex=use_vertex,
    )
    
    try:
        result = await agent.invoke(
            message="Say 'Hello A2A!' in exactly 3 words.",
            max_tokens=20,
        )
        
        return {
            "success": True,
            "model": model,
            "provider": "Vertex AI" if use_vertex else "Direct API",
            "response": result,
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "provider": "Vertex AI" if use_vertex else "Direct API",
        }


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        # Test mode: verify API connectivity
        print("Testing Claude API...")
        
        # Check for Vertex AI
        use_vertex = os.environ.get("CLAUDE_CODE_USE_VERTEX", "").lower() in ("1", "true")
        
        result = asyncio.run(test_claude_api(use_vertex=use_vertex))
        
        if result["success"]:
            print(f"✅ Success!")
            print(f"   Provider: {result['provider']}")
            print(f"   Model: {result['model']}")
            print(f"   Response: {result['response']}")
        else:
            print(f"❌ Failed: {result.get('error')}")
            print(f"\nSetup Instructions:")
            print("=" * 50)
            print("\nOption 1: Direct Anthropic API")
            print("  export ANTHROPIC_API_KEY='your-api-key'")
            print("\nOption 2: Google Vertex AI (OIDC)")
            print("  export CLAUDE_CODE_USE_VERTEX=1")
            print("  export ANTHROPIC_VERTEX_PROJECT_ID='your-gcp-project'")
            print("  export CLOUD_ML_REGION='us-east5'")
            print("  # Configure GCP credentials via gcloud or workload identity")
            print("\nSee docs/VERTEX_AI_CLAUDE_SETUP.md for detailed setup guide.")
            sys.exit(1)
    
    elif len(sys.argv) > 1 and sys.argv[1] != "test":
        # Server mode
        import uvicorn
        
        agent_name = sys.argv[1]
        port = int(sys.argv[2]) if len(sys.argv) > 2 else 9999
        model = sys.argv[3] if len(sys.argv) > 3 else DEFAULT_MODEL
        
        # Check for Vertex AI
        use_vertex = os.environ.get("CLAUDE_CODE_USE_VERTEX", "").lower() in ("1", "true")
        
        print(f"Starting A2A Claude Agent Server")
        print(f"  Agent: {agent_name}")
        print(f"  Port: {port}")
        print(f"  Model: {model}")
        print(f"  Provider: {'Vertex AI' if use_vertex else 'Direct API'}")
        print(f"  Agent Card: http://localhost:{port}/.well-known/agent-card")
        print()
        
        server = create_claude_agent_server(agent_name, port, model, use_vertex)
        uvicorn.run(server.build(), host="0.0.0.0", port=port)
    
    else:
        print("Claude A2A Agent Executor")
        print("=" * 50)
        print("\nUsage:")
        print("  Test API: python -m tools.a2a.claude_executor test")
        print("  Run server: python -m tools.a2a.claude_executor <agent-name> [port] [model]")
        print()
        print("Models available:")
        print("  - claude-sonnet-4-20250514 (default, balanced)")
        print("  - claude-3-5-sonnet-20241022 (previous generation)")
        print("  - claude-3-5-haiku-20241022 (faster, cheaper)")
        print()
        print("Authentication:")
        print("  Option 1 - Direct Anthropic API:")
        print("    export ANTHROPIC_API_KEY='your-api-key'")
        print()
        print("  Option 2 - Google Vertex AI (OIDC):")
        print("    export CLAUDE_CODE_USE_VERTEX=1")
        print("    export ANTHROPIC_VERTEX_PROJECT_ID='your-gcp-project'")
        print("    export CLOUD_ML_REGION='us-east5'")
        print()
        print("Example:")
        print("  python -m tools.a2a.claude_executor engineer-master 8080")
