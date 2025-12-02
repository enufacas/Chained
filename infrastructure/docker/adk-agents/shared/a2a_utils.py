"""
A2A Protocol utilities for ADK agents.

This module provides common A2A protocol utilities shared across all ADK agents
in the Chained ecosystem.
"""

import json
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

import httpx
from pydantic import BaseModel


class AIUnavailableError(Exception):
    """Raised when Gemini AI is not available but is required."""
    pass


def build_ai_unavailable_error_message(
    genai_available: bool,
    has_api_key: bool,
    agent_name: str = "Agent"
) -> str:
    """
    Build a consistent error message for AI unavailability.
    
    Args:
        genai_available: Whether google-generativeai package is installed
        has_api_key: Whether GEMINI_API_KEY or GOOGLE_API_KEY is set
        agent_name: Name of the agent for the error message
        
    Returns:
        A descriptive error message explaining what's missing
    """
    error_msg = f"{agent_name}: Gemini AI is required but not available. "
    if not genai_available:
        error_msg += "The google-generativeai package is not installed. "
    if not has_api_key:
        error_msg += "No API key found in GEMINI_API_KEY or GOOGLE_API_KEY environment variables."
    return error_msg


class AgentCard(BaseModel):
    """A2A Agent Card per specification §4.4.1."""

    name: str
    description: str
    url: str
    version: str = "1.0.0"
    protocolVersion: str = "0.3.0"
    skills: List[Dict[str, Any]] = []
    capabilities: Dict[str, bool] = {"streaming": False, "pushNotifications": False}


class TaskStatus(BaseModel):
    """A2A Task Status per specification §4.1.2."""

    state: str  # submitted, working, completed, failed, cancelled
    timestamp: str
    message: Optional[Dict[str, Any]] = None


class Task(BaseModel):
    """A2A Task per specification §4.1.1."""

    id: str
    contextId: Optional[str] = None
    status: TaskStatus
    artifacts: List[Dict[str, Any]] = []
    referenceTaskIds: List[str] = []


class A2AMessage(BaseModel):
    """A2A Message per specification §4.1.4."""

    role: str  # user, agent
    parts: List[Dict[str, Any]]


class A2AClient:
    """Client for communicating with A2A agents."""

    def __init__(self, base_url: str, timeout: float = 30.0):
        self.base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create the HTTP client."""
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=self._timeout)
        return self._client

    async def get_agent_card(self) -> AgentCard:
        """Fetch agent card from .well-known endpoint."""
        client = await self._get_client()
        response = await client.get(
            f"{self.base_url}/.well-known/agent.json"
        )
        response.raise_for_status()
        return AgentCard(**response.json())

    async def send_message(
        self,
        message: str,
        context_id: Optional[str] = None,
        reference_task_ids: Optional[List[str]] = None,
    ) -> Task:
        """Send a message to the agent and receive a task."""
        payload = {
            "message": {
                "role": "user",
                "parts": [{"text": message}],
            }
        }
        if context_id:
            payload["contextId"] = context_id
        if reference_task_ids:
            payload["referenceTaskIds"] = reference_task_ids

        client = await self._get_client()
        response = await client.post(
            f"{self.base_url}/a2a/tasks",
            json=payload,
        )
        response.raise_for_status()
        return Task(**response.json())

    async def get_task_status(self, task_id: str) -> Task:
        """Get the status of a task."""
        client = await self._get_client()
        response = await client.get(
            f"{self.base_url}/a2a/tasks/{task_id}"
        )
        response.raise_for_status()
        return Task(**response.json())

    async def close(self):
        """Close the HTTP client."""
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit - ensures client is closed."""
        await self.close()


def create_task_id() -> str:
    """Generate a unique task ID."""
    import uuid
    return f"task-{uuid.uuid4().hex[:12]}"


def create_context_id(session_name: str) -> str:
    """Generate a context ID for grouping related tasks."""
    timestamp = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
    return f"{session_name}-{timestamp}"


def create_artifact(
    name: str,
    content: Any,
    artifact_type: str = "text"
) -> Dict[str, Any]:
    """Create an A2A artifact."""
    return {
        "name": name,
        "type": artifact_type,
        "data": content if isinstance(content, str) else json.dumps(content),
        "createdAt": datetime.utcnow().isoformat(),
    }


def get_agent_urls() -> Dict[str, str]:
    """Get URLs for all ADK agents from environment."""
    return {
        "academic-research": os.getenv(
            "ACADEMIC_RESEARCH_URL",
            "http://localhost:8081"
        ),
        "blog-writer": os.getenv(
            "BLOG_WRITER_URL",
            "http://localhost:8082"
        ),
        "google-trends": os.getenv(
            "GOOGLE_TRENDS_URL",
            "http://localhost:8083"
        ),
    }


def parse_llm_json_response(text: str) -> Optional[Any]:
    """
    Parse JSON from an LLM response, handling markdown code blocks.
    
    LLMs often wrap JSON responses in markdown code blocks like:
    ```json
    {"key": "value"}
    ```
    
    This utility safely extracts and parses the JSON.
    
    Args:
        text: The raw LLM response text
        
    Returns:
        Parsed JSON data, or None if parsing fails
    """
    if not text:
        return None
    
    text = text.strip()
    
    # Handle markdown code blocks
    if text.startswith("```"):
        try:
            # Split by ``` and take the content
            parts = text.split("```")
            if len(parts) >= 2:
                code_content = parts[1]
                # Remove language identifier if present (e.g., "json")
                if code_content.startswith("json"):
                    code_content = code_content[4:]
                elif code_content.startswith("JSON"):
                    code_content = code_content[4:]
                text = code_content.strip()
        except Exception:
            pass
    
    # Try to parse as JSON
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return None


async def send_error_to_observer(
    error_event_dict: Dict[str, Any],
    error_observer_url: Optional[str] = None,
) -> bool:
    """
    Send an error event to the error_observer agent.
    
    This is a helper function for agents to report errors as A2A tasks.
    
    Args:
        error_event_dict: Error event data as dict (should match ErrorEvent schema)
        error_observer_url: URL of error_observer agent (defaults to env var)
        
    Returns:
        True if successfully sent, False otherwise
    """
    if not error_observer_url:
        error_observer_url = os.getenv("ERROR_OBSERVER_URL")
    
    if not error_observer_url:
        print("⚠️ Error observer URL not configured, cannot send error event")
        return False
    
    try:
        async with A2AClient(error_observer_url) as client:
            # Send error event as JSON in message
            message = json.dumps(error_event_dict)
            task = await client.send_message(
                message=message,
                context_id=f"error-{datetime.utcnow().timestamp()}",
            )
            print(f"✅ Sent error event to observer: {task.id}")
            return True
    except Exception as e:
        print(f"❌ Failed to send error to observer: {str(e)}")
        return False


async def report_agent_error(
    agent_name: str,
    exception: Exception,
    task_type: str = "agent_task",
    a2a_ui_url: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> bool:
    """
    Report an agent error to the error_observer.
    
    This is a convenience wrapper that creates an ErrorEvent from an exception
    and sends it to the error_observer agent.
    
    Args:
        agent_name: Name of the agent where the error occurred
        exception: The exception that was raised
        task_type: Type of task that failed
        a2a_ui_url: Optional URL to the A2A UI for this task
        metadata: Optional additional metadata
        
    Returns:
        True if successfully reported, False otherwise
    """
    # Import here to avoid circular dependency
    try:
        from shared.error_event import ErrorEvent
    except ImportError:
        print("⚠️ ErrorEvent module not available, cannot report error")
        return False
    
    try:
        error_event = ErrorEvent.from_exception(
            service=agent_name,
            exception=exception,
            source_agent=agent_name,
            source_channel="runtime",
            a2a_ui_url=a2a_ui_url,
            metadata=metadata or {},
        )
        
        return await send_error_to_observer(error_event.model_dump())
    
    except Exception as e:
        print(f"❌ Failed to create/send error event: {str(e)}")
        return False
