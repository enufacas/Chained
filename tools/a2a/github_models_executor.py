"""
GitHub Models A2A Agent Executor.

This module provides an A2A-compliant AgentExecutor that wraps the GitHub Models API
for executing agent tasks. This follows the official A2A samples pattern and provides
parity with the Gemini executor, enabling mixed-provider agent orchestration.

The GitHub Models API is accessed via:
  - Endpoint: https://models.github.ai/inference/chat/completions
  - Authentication: `Authorization: token YOUR_PAT` (NOT Bearer!)
  - Required Scope: Fine-grained PAT with `models:read` permission

Based on investigation findings from:
docs/a2a/A2A_COPILOT_CLI_INVESTIGATION.md

Models available:
  - openai/gpt-4o-mini (high volume, cost-effective)
  - openai/gpt-4o (higher token capacity)
  - openai/gpt-4.1 (latest, more restricted)
"""

import asyncio
import os
from typing import Optional

import httpx

from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.utils import new_agent_text_message

from .agent_card import parse_agent_definition


# GitHub Models API endpoint
GITHUB_MODELS_ENDPOINT = "https://models.github.ai/inference/chat/completions"

# Default model - gpt-4o-mini has best rate limits (20,000 req, 2M tokens)
DEFAULT_MODEL = "openai/gpt-4o-mini"


class GitHubModelsAgent:
    """
    GitHub Models AI Agent that executes tasks via GitHub Models API.

    This follows the same pattern as GeminiAgent, but uses GitHub's
    Models API for actual AI-powered responses.

    CRITICAL: Uses `Authorization: token` format, NOT Bearer!
    """

    def __init__(
        self,
        agent_name: str,
        model: str = DEFAULT_MODEL,
        api_token: Optional[str] = None,
    ):
        """
        Initialize the GitHub Models agent.

        Args:
            agent_name: Name of the Chained agent (for persona/context)
            model: GitHub Models model to use (e.g., "openai/gpt-4o-mini")
            api_token: GitHub PAT with models:read scope
                       (defaults to COPILOT_PAT or GITHUB_TOKEN env var)
        """
        self.agent_name = agent_name
        self.model = model
        self.api_token = (
            api_token
            or os.environ.get("COPILOT_PAT")
            or os.environ.get("GITHUB_TOKEN")
        )
        self.metadata = parse_agent_definition(agent_name)

    async def invoke(
        self,
        message: str,
        context: Optional[str] = None,
        system_prompt: Optional[str] = None,
    ) -> str:
        """
        Invoke GitHub Models API to process the message.

        Args:
            message: User message to process
            context: Optional additional context
            system_prompt: Optional system prompt override

        Returns:
            Model's response as a string
        """
        # Build the system prompt with agent persona
        specialization = self.metadata.get("specialization", "general")
        description = self.metadata.get("description", "")

        if system_prompt is None:
            system_prompt = f"""You are {self.agent_name}, a specialized AI agent.

Specialization: {specialization}
Description: {description}

You provide helpful, detailed responses from your specialized perspective.
{f"Additional Context: {context}" if context else ""}"""

        # Build messages array
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": message},
        ]

        # Execute via GitHub Models API
        try:
            result = await self._call_github_models_api(messages)
            return result
        except Exception as e:
            return f"[{self.agent_name}] Error invoking GitHub Models API: {str(e)}"

    async def _call_github_models_api(self, messages: list) -> str:
        """
        Call the GitHub Models API with the given messages.

        CRITICAL: Uses `Authorization: token` format, NOT Bearer!
        This was discovered through testing (see A2A_COPILOT_CLI_INVESTIGATION.md).
        """
        if not self.api_token:
            return (
                f"[{self.agent_name}] Error: No API token configured. "
                "Set COPILOT_PAT or GITHUB_TOKEN environment variable "
                "with a PAT that has `models:read` scope."
            )

        headers = {
            "Authorization": f"token {self.api_token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "Content-Type": "application/json",
        }

        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": 4096,
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                GITHUB_MODELS_ENDPOINT,
                headers=headers,
                json=payload,
            )

            if response.status_code == 401:
                return (
                    f"[{self.agent_name}] Authentication failed (401). "
                    "Ensure your PAT has `models:read` scope and is valid."
                )

            if response.status_code == 403:
                return (
                    f"[{self.agent_name}] Access forbidden (403). "
                    "Check if your account has access to GitHub Models."
                )

            if response.status_code == 429:
                # Extract rate limit info from headers
                remaining = response.headers.get("X-Ratelimit-Remaining-Requests", "?")
                limit = response.headers.get("X-Ratelimit-Limit-Requests", "?")
                return (
                    f"[{self.agent_name}] Rate limited (429). "
                    f"Remaining: {remaining}/{limit} requests."
                )

            response.raise_for_status()
            data = response.json()

            # Extract the assistant message
            if "choices" in data and len(data["choices"]) > 0:
                return data["choices"][0]["message"]["content"]

            return f"[{self.agent_name}] Unexpected response format: {data}"


class GitHubModelsAgentExecutor(AgentExecutor):
    """
    A2A Agent Executor that uses GitHub Models API for task execution.

    This follows the official A2A samples pattern:
    - Implements AgentExecutor interface
    - Uses execute() for task processing
    - Uses cancel() for task cancellation
    - Streams events via EventQueue

    Example:
        >>> executor = GitHubModelsAgentExecutor(agent_name="engineer-master")
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
        api_token: Optional[str] = None,
    ):
        """
        Initialize the GitHub Models executor.

        Args:
            agent_name: Name of the Chained agent
            model: GitHub Models model to use
            api_token: Optional API token (PAT with models:read scope)
        """
        self.agent_name = agent_name
        self.agent = GitHubModelsAgent(
            agent_name=agent_name,
            model=model,
            api_token=api_token,
        )
        self._running_tasks = {}

    async def execute(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ) -> None:
        """
        Execute the agent task using GitHub Models API.

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
        await event_queue.enqueue_event(
            new_agent_text_message(
                f"[{self.agent_name}] Processing with GitHub Models ({self.agent.model})..."
            )
        )

        try:
            # Track task for cancellation support
            task_id = getattr(context, "task_id", None)
            current_task = asyncio.current_task()
            if task_id and current_task:
                self._running_tasks[task_id] = current_task

            # Invoke GitHub Models agent
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


def create_github_models_agent_server(
    agent_name: str,
    port: int = 9999,
    model: str = DEFAULT_MODEL,
):
    """
    Create an A2A server for a GitHub Models-powered agent.

    This follows the official A2A samples pattern.

    Args:
        agent_name: Name of the Chained agent
        port: Port to run on
        model: GitHub Models model to use

    Returns:
        A2AStarletteApplication ready to run

    Example:
        >>> server = create_github_models_agent_server("engineer-master", port=8080)
        >>> import uvicorn
        >>> uvicorn.run(server.build(), host="0.0.0.0", port=8080)
    """
    from a2a.server.apps import A2AStarletteApplication
    from a2a.server.request_handlers import DefaultRequestHandler
    from a2a.server.tasks import InMemoryTaskStore

    from .agent_card import generate_agent_card

    # Generate AgentCard (A2A §4.4.1)
    agent_card = generate_agent_card(agent_name, port=port)

    # Create executor with GitHub Models backend
    executor = GitHubModelsAgentExecutor(
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


async def test_github_models_api(
    model: str = DEFAULT_MODEL,
    api_token: Optional[str] = None,
) -> dict:
    """
    Test the GitHub Models API connection.

    Args:
        model: Model to test with
        api_token: Optional PAT (uses env vars if not provided)

    Returns:
        Dict with test results
    """
    token = (
        api_token
        or os.environ.get("COPILOT_PAT")
        or os.environ.get("GITHUB_TOKEN")
    )

    if not token:
        return {
            "success": False,
            "error": "No API token. Set COPILOT_PAT or GITHUB_TOKEN.",
        }

    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "Content-Type": "application/json",
    }

    payload = {
        "model": model,
        "messages": [{"role": "user", "content": "Say 'Hello A2A!' in exactly 3 words."}],
        "max_tokens": 20,
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                GITHUB_MODELS_ENDPOINT,
                headers=headers,
                json=payload,
            )

            if response.status_code != 200:
                return {
                    "success": False,
                    "status_code": response.status_code,
                    "error": response.text,
                }

            data = response.json()
            return {
                "success": True,
                "model": data.get("model"),
                "response": data["choices"][0]["message"]["content"],
                "usage": data.get("usage", {}),
                "rate_limit_remaining": response.headers.get(
                    "X-Ratelimit-Remaining-Requests"
                ),
            }
    except Exception as e:
        return {"success": False, "error": str(e)}


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "test":
        # Test mode: verify API connectivity
        import asyncio

        print("Testing GitHub Models API...")
        result = asyncio.run(test_github_models_api())
        if result["success"]:
            print(f"✅ Success!")
            print(f"   Model: {result.get('model')}")
            print(f"   Response: {result.get('response')}")
            print(f"   Rate limit remaining: {result.get('rate_limit_remaining')}")
        else:
            print(f"❌ Failed: {result.get('error')}")
            sys.exit(1)

    elif len(sys.argv) > 1 and sys.argv[1] != "test":
        # Server mode
        import uvicorn

        agent_name = sys.argv[1]
        port = int(sys.argv[2]) if len(sys.argv) > 2 else 9999
        model = sys.argv[3] if len(sys.argv) > 3 else DEFAULT_MODEL

        print(f"Starting A2A GitHub Models Agent Server")
        print(f"  Agent: {agent_name}")
        print(f"  Port: {port}")
        print(f"  Model: {model}")
        print(f"  Agent Card: http://localhost:{port}/.well-known/agent-card")
        print()

        server = create_github_models_agent_server(agent_name, port, model)
        uvicorn.run(server.build(), host="0.0.0.0", port=port)

    else:
        print("Usage:")
        print("  Test API: python -m tools.a2a.github_models_executor test")
        print("  Run server: python -m tools.a2a.github_models_executor <agent-name> [port] [model]")
        print()
        print("Models available:")
        print("  - openai/gpt-4o-mini (default, high volume)")
        print("  - openai/gpt-4o (higher token capacity)")
        print("  - openai/gpt-4.1 (latest, more restricted)")
        print()
        print("Example:")
        print("  python -m tools.a2a.github_models_executor engineer-master 8080 openai/gpt-4o-mini")
