"""
GitHub Models A2A Agent Executor.

This module provides an A2A-compliant AgentExecutor that wraps the GitHub Models API
for executing agent tasks. This follows the official A2A samples pattern and provides
parity with the Gemini executor, enabling mixed-provider agent orchestration.

The GitHub Models API is accessed via:
  - Endpoint: https://models.github.ai/inference/chat/completions
  - Authentication: `Authorization: token YOUR_PAT` (NOT Bearer - Bearer returns 401)
  - Required Scope: Fine-grained PAT with `models:read` permission
  - Note: Official docs show Bearer but testing confirms only 'token' format works

Models available (tested within free tier):
  - meta/meta-llama-3.1-8b-instruct (default, works within budget)
  - mistral-ai/mistral-small-2503 (works within budget)
  - cohere/cohere-command-a (works within budget)
  - openai/gpt-4.1-nano (works within budget)
  - openai/gpt-4o-mini (may hit budget limits)

Tool Support:
  - Tools are defined in agent definitions (.github/agents/*.md)
  - GitHub Models API supports tool-calling via OpenAI-compatible format
  - Tools are executed locally and results returned to the model

Common Errors (from API responses):
  - {"code":"no_access","message":"No access to model: ..."} - PAT is missing `models:read` scope
  - {"message":"Unable to proceed with model usage. This account has reached its budget limit."} - Usage quota exceeded
  - 401 Unauthorized - Token invalid OR using Bearer instead of token format
"""

import asyncio
import json
import os
import subprocess
from typing import Any, Dict, List, Optional

import httpx

from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.utils import new_agent_text_message

from .agent_card import parse_agent_definition


# GitHub Models API endpoint
GITHUB_MODELS_ENDPOINT = "https://models.github.ai/inference/chat/completions"

# Default model - llama-3.1-8b-instruct works within free tier budget
# Other working models: mistral-ai/mistral-small-2503, cohere/cohere-command-a, openai/gpt-4.1-nano
# Note: openai/gpt-4o-mini may hit budget limits
DEFAULT_MODEL = "meta/meta-llama-3.1-8b-instruct"


# =============================================================================
# TOOL DEFINITIONS
# =============================================================================
# These tools map to the tools defined in agent definitions and provide
# actual functionality when called by the model.
# =============================================================================

AVAILABLE_TOOLS = {
    "get_file_contents": {
        "type": "function",
        "function": {
            "name": "get_file_contents",
            "description": "Read the contents of a file from the repository",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path to the file relative to repository root"
                    }
                },
                "required": ["path"]
            }
        }
    },
    "search_code": {
        "type": "function",
        "function": {
            "name": "search_code",
            "description": "Search for code patterns in the repository",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query (grep pattern)"
                    },
                    "file_pattern": {
                        "type": "string",
                        "description": "File pattern to search (e.g., '*.py', '*.yml')",
                        "default": "*"
                    }
                },
                "required": ["query"]
            }
        }
    },
    "list_directory": {
        "type": "function",
        "function": {
            "name": "list_directory",
            "description": "List files and directories in a path",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Directory path relative to repository root",
                        "default": "."
                    }
                },
                "required": []
            }
        }
    },
    "get_issue": {
        "type": "function",
        "function": {
            "name": "get_issue",
            "description": "Get details of a GitHub issue",
            "parameters": {
                "type": "object",
                "properties": {
                    "issue_number": {
                        "type": "integer",
                        "description": "Issue number"
                    }
                },
                "required": ["issue_number"]
            }
        }
    },
    "add_issue_comment": {
        "type": "function",
        "function": {
            "name": "add_issue_comment",
            "description": "Add a comment to a GitHub issue",
            "parameters": {
                "type": "object",
                "properties": {
                    "issue_number": {
                        "type": "integer",
                        "description": "Issue number"
                    },
                    "body": {
                        "type": "string",
                        "description": "Comment body (markdown supported)"
                    }
                },
                "required": ["issue_number", "body"]
            }
        }
    },
}

# Map agent tool names to our tool definitions
TOOL_NAME_MAPPING = {
    "view": "get_file_contents",
    "github-mcp-server-get_file_contents": "get_file_contents",
    "github-mcp-server-search_code": "search_code",
    "github-mcp-server-get_issue": "get_issue",
    "github-mcp-server-add_issue_comment": "add_issue_comment",
    "bash": "search_code",  # Limited bash via search
}


# Content truncation limits
MAX_FILE_CONTENT_SIZE = 10000
MAX_SEARCH_RESULT_SIZE = 5000


def sanitize_search_query(query: str) -> str:
    """
    Sanitize a search query to prevent command injection.
    
    Args:
        query: Raw search query
        
    Returns:
        Sanitized query safe for subprocess
    """
    # Remove shell metacharacters
    dangerous_chars = ['`', '$', '|', ';', '&', '>', '<', '\\', '\n', '\r']
    sanitized = query
    for char in dangerous_chars:
        sanitized = sanitized.replace(char, '')
    # Limit length
    return sanitized[:200]


def execute_tool(tool_name: str, arguments: Dict[str, Any]) -> str:
    """
    Execute a tool and return the result.
    
    Args:
        tool_name: Name of the tool to execute
        arguments: Tool arguments
        
    Returns:
        Tool execution result as string
    """
    try:
        if tool_name == "get_file_contents":
            path = arguments.get("path", "")
            # Basic path traversal protection
            if ".." in path or path.startswith("/"):
                return f"Error: Invalid path: {path}"
            if os.path.exists(path):
                with open(path, "r") as f:
                    content = f.read()
                # Limit content size for API
                if len(content) > MAX_FILE_CONTENT_SIZE:
                    content = content[:MAX_FILE_CONTENT_SIZE] + "\n... [truncated]"
                return content
            else:
                return f"Error: File not found: {path}"
                
        elif tool_name == "search_code":
            query = sanitize_search_query(arguments.get("query", ""))
            file_pattern = arguments.get("file_pattern", "*")
            # Sanitize file pattern too
            file_pattern = sanitize_search_query(file_pattern)
            if not query:
                return "Error: Empty search query"
            try:
                result = subprocess.run(
                    ["grep", "-r", "-n", "-l", "-F", query, "--include", file_pattern, "."],
                    capture_output=True, text=True, timeout=10
                )
                if result.stdout:
                    return f"Files matching '{query}':\n{result.stdout[:MAX_SEARCH_RESULT_SIZE]}"
                return f"No matches found for '{query}'"
            except subprocess.TimeoutExpired:
                return "Search timed out"
            except Exception as e:
                return f"Search error: {str(e)}"
                
        elif tool_name == "list_directory":
            path = arguments.get("path", ".")
            if os.path.isdir(path):
                entries = os.listdir(path)
                return "\n".join(sorted(entries)[:100])
            return f"Error: Directory not found: {path}"
            
        elif tool_name == "get_issue":
            issue_number = arguments.get("issue_number")
            try:
                result = subprocess.run(
                    ["gh", "issue", "view", str(issue_number), "--json", "title,body,state,labels"],
                    capture_output=True, text=True, timeout=30
                )
                if result.returncode == 0:
                    return result.stdout
                return f"Error getting issue: {result.stderr}"
            except Exception as e:
                return f"Error: {str(e)}"
                
        elif tool_name == "add_issue_comment":
            issue_number = arguments.get("issue_number")
            body = arguments.get("body", "")
            try:
                result = subprocess.run(
                    ["gh", "issue", "comment", str(issue_number), "--body", body],
                    capture_output=True, text=True, timeout=30
                )
                if result.returncode == 0:
                    return "Comment added successfully"
                return f"Error adding comment: {result.stderr}"
            except Exception as e:
                return f"Error: {str(e)}"
                
        else:
            return f"Unknown tool: {tool_name}"
            
    except Exception as e:
        return f"Tool execution error: {str(e)}"


def get_tools_for_agent(agent_name: str) -> List[Dict]:
    """
    Get tool definitions for an agent based on its definition.
    
    Args:
        agent_name: Name of the agent
        
    Returns:
        List of tool definitions in OpenAI format
    """
    metadata = parse_agent_definition(agent_name)
    agent_tools = metadata.get("tools", [])
    
    # Track added tool names to avoid duplicates
    added_tool_names = set()
    tools = []
    
    for tool in agent_tools:
        # Map agent tool name to our tool definition
        mapped_name = TOOL_NAME_MAPPING.get(tool, tool)
        if mapped_name in AVAILABLE_TOOLS and mapped_name not in added_tool_names:
            tools.append(AVAILABLE_TOOLS[mapped_name])
            added_tool_names.add(mapped_name)
    
    # Always include core tools (if not already added)
    for core_tool in ["get_file_contents", "list_directory", "get_issue"]:
        if core_tool not in added_tool_names:
            tools.append(AVAILABLE_TOOLS[core_tool])
            added_tool_names.add(core_tool)
    
    return tools


class GitHubModelsAgent:
    """
    GitHub Models AI Agent that executes tasks via GitHub Models API.

    This follows the same pattern as GeminiAgent, but uses GitHub's
    Models API for actual AI-powered responses.

    Authentication: Uses `Authorization: token` format (NOT Bearer - Bearer returns 401)
    Required: Fine-grained PAT with `models:read` scope.
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
            model: GitHub Models model to use (e.g., "openai/gpt-4.1")
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
        enable_tools: bool = True,
    ) -> str:
        """
        Invoke GitHub Models API to process the message with tool support.

        Args:
            message: User message to process
            context: Optional additional context
            system_prompt: Optional system prompt override
            enable_tools: Whether to enable tool calling (default: True)

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
You have access to tools to help you understand and analyze the codebase.
{f"Additional Context: {context}" if context else ""}"""

        # Build messages array
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": message},
        ]

        # Get tools for this agent
        tools = get_tools_for_agent(self.agent_name) if enable_tools else []

        # Execute via GitHub Models API with tool loop
        try:
            result = await self._call_github_models_api_with_tools(messages, tools)
            return result
        except Exception as e:
            return f"[{self.agent_name}] Error invoking GitHub Models API: {str(e)}"

    async def _call_github_models_api_with_tools(
        self, 
        messages: List[Dict], 
        tools: List[Dict],
        max_tool_rounds: int = 5
    ) -> str:
        """
        Call the GitHub Models API with tool support.
        
        Implements a tool-calling loop that:
        1. Sends request with tool definitions
        2. If model requests tool calls, executes them
        3. Returns tool results to model
        4. Repeats until model gives final response
        
        Args:
            messages: Conversation messages
            tools: Tool definitions in OpenAI format
            max_tool_rounds: Maximum tool-calling iterations
            
        Returns:
            Final model response
        """
        if not self.api_token:
            return (
                f"[{self.agent_name}] Error: No API token configured. "
                "Set COPILOT_PAT or GITHUB_TOKEN environment variable "
                "with a PAT that has `models:read` scope."
            )

        # Note: Despite official docs showing Bearer, testing confirms 'token' format works
        # Bearer returns 401 Unauthorized with fine-grained PATs
        headers = {
            "Authorization": f"token {self.api_token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "Content-Type": "application/json",
        }

        # Tool-calling loop
        for round_num in range(max_tool_rounds):
            payload = {
                "model": self.model,
                "messages": messages,
                "max_tokens": 4096,
            }
            
            # Add tools if available
            if tools:
                payload["tools"] = tools
                payload["tool_choice"] = "auto"

            async with httpx.AsyncClient(timeout=120.0) as client:
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
                    remaining = response.headers.get("X-Ratelimit-Remaining-Requests", "?")
                    limit = response.headers.get("X-Ratelimit-Limit-Requests", "?")
                    return (
                        f"[{self.agent_name}] Rate limited (429). "
                        f"Remaining: {remaining}/{limit} requests."
                    )

                response.raise_for_status()
                data = response.json()

                if "choices" not in data or len(data["choices"]) == 0:
                    return f"[{self.agent_name}] Unexpected response format: {data}"

                choice = data["choices"][0]
                message = choice.get("message", {})
                finish_reason = choice.get("finish_reason", "")

                # Check if model wants to call tools
                tool_calls = message.get("tool_calls", [])
                
                if tool_calls and finish_reason == "tool_calls":
                    # Add assistant message with tool calls to history
                    messages.append(message)
                    
                    # Execute each tool and add results
                    for tool_call in tool_calls:
                        tool_name = tool_call["function"]["name"]
                        try:
                            arguments = json.loads(tool_call["function"]["arguments"])
                        except json.JSONDecodeError:
                            arguments = {}
                        
                        # Execute the tool
                        tool_result = execute_tool(tool_name, arguments)
                        
                        # Add tool result to messages
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call["id"],
                            "name": tool_name,
                            "content": tool_result
                        })
                    
                    # Continue loop for next round
                    continue
                
                # No more tool calls, return final response
                content = message.get("content", "")
                if content:
                    return content
                
                return f"[{self.agent_name}] No content in response"

        return f"[{self.agent_name}] Max tool rounds ({max_tool_rounds}) exceeded"

    async def _call_github_models_api(self, messages: list) -> str:
        """
        Simple API call without tools (backward compatibility).

        Uses token authentication (NOT Bearer - Bearer returns 401).
        """
        return await self._call_github_models_api_with_tools(messages, tools=[])


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

    # Note: Despite official docs showing Bearer, testing confirms 'token' format works
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
        print("Models available (with tool-calling support):")
        print("  - openai/gpt-4o-mini (default, high volume, best accessibility)")
        print("  - openai/gpt-4o (multimodal, large context)")
        print("  - openai/gpt-4.1 (latest GPT-4, may require premium access)")
        print()
        print("Example:")
        print("  python -m tools.a2a.github_models_executor engineer-master 8080 openai/gpt-4o-mini")
