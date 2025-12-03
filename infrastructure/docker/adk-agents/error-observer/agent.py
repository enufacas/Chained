"""
Error Observer Agent - A2A System Agent
========================================

This agent is a system-level observer that receives error_event tasks/messages
from A2A agents, the UI, and log-consumer agents, and forwards selected events
to GitHub via repository_dispatch for Copilot-driven triage.

Role:
- Subscribes to error_event task type
- Enriches and validates error events
- Forwards errors to GitHub for automated triage
- Tracks state for UI visualization (idle, ingesting, dispatching, success, failure)

Based on A2A protocol patterns from the Chained ecosystem.
"""

import json
import os
import sys
from datetime import datetime
from typing import Any, Dict, List, Optional
from contextlib import asynccontextmanager

import httpx
import uvicorn
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel

# Add shared utilities to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from shared.a2a_utils import AgentCard, Task, TaskStatus, A2AMessage
from shared.error_event import ErrorEvent

# =============================================================================
# Configuration
# =============================================================================

AGENT_NAME = "error-observer"
AGENT_DESCRIPTION = "System-level observer that receives error events and forwards to GitHub for triage"
AGENT_VERSION = "1.0.0"
PORT = int(os.getenv("PORT", "8090"))

# GitHub configuration
GITHUB_TOKEN = os.getenv("GITHUB_PAT") or os.getenv("GITHUB_TOKEN")
GITHUB_REPO = os.getenv("GITHUB_REPO", "enufacas/Chained")
GITHUB_API_URL = "https://api.github.com"

# Agent state tracking
class AgentState:
    def __init__(self):
        self.status = "idle"  # idle, ingesting, dispatching, success, failure
        self.last_error: Optional[ErrorEvent] = None
        self.last_dispatch_time: Optional[str] = None
        self.last_dispatch_status: Optional[str] = None
        self.errors_handled_24h = 0
        self.recent_errors: List[Dict[str, Any]] = []
        self.status_message = "Waiting for errors"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status,
            "status_message": self.status_message,
            "last_error": self.last_error.model_dump() if self.last_error else None,
            "last_dispatch_time": self.last_dispatch_time,
            "last_dispatch_status": self.last_dispatch_status,
            "errors_handled_24h": self.errors_handled_24h,
            "recent_errors": self.recent_errors[-10:],  # Last 10 errors
        }

agent_state = AgentState()

# =============================================================================
# GitHub Repository Dispatch Tool
# =============================================================================

async def dispatch_to_github(error_event: ErrorEvent) -> Dict[str, Any]:
    """
    Forward an error event to GitHub via repository_dispatch.
    
    Args:
        error_event: The error event to dispatch
        
    Returns:
        Dict with success status and message
        
    Raises:
        HTTPException: If GitHub API call fails
    """
    if not GITHUB_TOKEN:
        raise HTTPException(
            status_code=500,
            detail="GitHub token not configured (GITHUB_PAT or GITHUB_TOKEN required)"
        )
    
    url = f"{GITHUB_API_URL}/repos/{GITHUB_REPO}/dispatches"
    
    payload = {
        "event_type": "cloudrun-error",
        "client_payload": error_event.to_github_payload(),
    }
    
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "User-Agent": f"error-observer-agent/{AGENT_VERSION}",
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, json=payload, headers=headers)
            
            if response.status_code == 204:
                # Success - GitHub returns 204 No Content
                print(f"✅ Successfully dispatched error to GitHub: {error_event.error_hash}")
                return {
                    "success": True,
                    "message": "Error event dispatched to GitHub",
                    "error_hash": error_event.error_hash,
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                }
            else:
                error_msg = f"GitHub API returned {response.status_code}: {response.text}"
                print(f"❌ Failed to dispatch to GitHub: {error_msg}")
                return {
                    "success": False,
                    "message": error_msg,
                    "error_hash": error_event.error_hash,
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                }
    
    except httpx.TimeoutException:
        error_msg = "GitHub API request timed out"
        print(f"❌ {error_msg}")
        return {
            "success": False,
            "message": error_msg,
            "error_hash": error_event.error_hash,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }
    
    except Exception as e:
        error_msg = f"GitHub dispatch error: {str(e)}"
        print(f"❌ {error_msg}")
        return {
            "success": False,
            "message": error_msg,
            "error_hash": error_event.error_hash,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }

# =============================================================================
# Error Event Processing
# =============================================================================

async def process_error_event(error_event: ErrorEvent) -> Dict[str, Any]:
    """
    Process an incoming error event.
    
    1. Update agent state to 'ingesting'
    2. Validate and enrich the error event
    3. Update agent state to 'dispatching'
    4. Call GitHub dispatch tool
    5. Update agent state to 'success' or 'failure'
    
    Args:
        error_event: The error event to process
        
    Returns:
        Processing result
    """
    print(f"🔍 Processing error event: {error_event.error_hash} from {error_event.service}")
    
    # State: ingesting
    agent_state.status = "ingesting"
    agent_state.last_error = error_event
    agent_state.status_message = f"Processing error from {error_event.service}"
    
    # Enrich error event (add any additional context)
    # For now, just validate it's complete
    if not error_event.service or not error_event.error_message:
        agent_state.status = "failure"
        agent_state.status_message = "Invalid error event (missing required fields)"
        return {
            "success": False,
            "message": "Invalid error event",
        }
    
    # State: dispatching
    agent_state.status = "dispatching"
    agent_state.status_message = f"Dispatching to GitHub: {error_event.error_hash}"
    
    # Call GitHub dispatch tool
    dispatch_result = await dispatch_to_github(error_event)
    
    # Update state based on result
    if dispatch_result["success"]:
        agent_state.status = "success"
        agent_state.status_message = "Successfully dispatched to GitHub"
        agent_state.last_dispatch_status = "success"
    else:
        agent_state.status = "failure"
        agent_state.status_message = f"Dispatch failed: {dispatch_result['message']}"
        agent_state.last_dispatch_status = "failure"
    
    agent_state.last_dispatch_time = dispatch_result["timestamp"]
    agent_state.errors_handled_24h += 1
    
    # Track recent error
    agent_state.recent_errors.append({
        "error_hash": error_event.error_hash,
        "service": error_event.service,
        "message": error_event.error_message[:100],
        "timestamp": error_event.last_seen,
        "dispatch_status": agent_state.last_dispatch_status,
    })
    
    return dispatch_result

# =============================================================================
# FastAPI Application
# =============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    print(f"🚀 Error Observer Agent starting on port {PORT}")
    print(f"   GitHub integration: {'✅ Configured' if GITHUB_TOKEN else '❌ Not configured'}")
    yield
    print("🛑 Error Observer Agent shutting down")

app = FastAPI(title="Error Observer Agent", version=AGENT_VERSION, lifespan=lifespan)

# =============================================================================
# A2A Protocol Endpoints
# =============================================================================

@app.get("/.well-known/agent.json")
async def get_agent_card():
    """Return A2A Agent Card."""
    card = AgentCard(
        name=AGENT_NAME,
        description=AGENT_DESCRIPTION,
        url=os.getenv("SERVICE_URL", f"http://localhost:{PORT}"),
        version=AGENT_VERSION,
        protocolVersion="0.3.0",
        skills=[
            {
                "name": "error_observation",
                "description": "Receive and process error events from A2A agents",
                "input": {"type": "error_event"},
                "output": {"type": "dispatch_result"},
            }
        ],
        capabilities={
            "streaming": False,
            "pushNotifications": False,
        },
    )
    return card.model_dump()

@app.post("/a2a/tasks")
async def handle_task(request: Request):
    """
    Handle A2A task requests (SendMessage).
    
    This endpoint processes error_event tasks and forwards them to GitHub.
    """
    try:
        body = await request.json()
        message = body.get("message", {})
        context_id = body.get("contextId")
        
        # Extract message text
        parts = message.get("parts", [])
        message_text = parts[0].get("text", "") if parts else ""
        
        print(f"📨 Received A2A task (contextId: {context_id})")
        print(f"   Message: {message_text[:200]}")
        
        # Parse error event from message
        # The message could contain JSON or we look for error_event in metadata
        metadata = body.get("metadata", {})
        error_event_data = metadata.get("error_event")
        
        if error_event_data:
            # Error event in metadata
            error_event = ErrorEvent(**error_event_data)
        elif message_text.startswith("{"):
            # Try to parse as JSON
            try:
                error_event_data = json.loads(message_text)
                error_event = ErrorEvent(**error_event_data)
            except (json.JSONDecodeError, ValueError) as e:
                raise HTTPException(status_code=400, detail=f"Invalid error event JSON: {str(e)}")
        else:
            # Create error event from plain message
            error_event = ErrorEvent(
                service="unknown",
                error_message=message_text,
                error_hash=ErrorEvent.compute_error_hash("unknown", message_text, "generic"),
                first_seen=datetime.utcnow().isoformat() + "Z",
                last_seen=datetime.utcnow().isoformat() + "Z",
            )
        
        # Process the error event
        result = await process_error_event(error_event)
        
        # Build A2A response task
        task_id = f"task-{datetime.utcnow().timestamp()}"
        
        response_message = (
            f"Processed error event from {error_event.service}\n"
            f"Error hash: {error_event.error_hash}\n"
            f"Dispatch result: {result['message']}"
        )
        
        task = Task(
            id=task_id,
            contextId=context_id,
            status=TaskStatus(
                state="completed" if result["success"] else "failed",
                timestamp=datetime.utcnow().isoformat() + "Z",
                message=A2AMessage(
                    role="agent",
                    parts=[{"text": response_message}],
                ).model_dump(),
            ),
            artifacts=[
                error_event.to_a2a_artifact(),
                {
                    "name": "dispatch_result",
                    "type": "dispatch_result",
                    "data": json.dumps(result, indent=2),
                },
            ],
        )
        
        return task.model_dump()
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error handling task: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "agent": AGENT_NAME,
        "version": AGENT_VERSION,
        "github_configured": bool(GITHUB_TOKEN),
    }

@app.get("/status")
async def get_status():
    """
    Get current agent status for UI visualization.
    
    Returns detailed status including:
    - Current state (idle, ingesting, dispatching, success, failure)
    - Last error processed
    - Recent error history
    - Dispatch statistics
    """
    return agent_state.to_dict()

# =============================================================================
# Main
# =============================================================================

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=PORT)
