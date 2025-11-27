"""
ADK API Server - Main FastAPI Server
====================================

This server implements the ADK API interface expected by google/adk-web,
translating requests to A2A protocol calls for the deployed agents.

Endpoints implemented:
- GET /list-apps - List available agent applications
- POST /apps/{app_name}/users/{user_id}/sessions - Create session
- GET /apps/{app_name}/users/{user_id}/sessions - List sessions
- GET /apps/{app_name}/users/{user_id}/sessions/{session_id} - Get session
- DELETE /apps/{app_name}/users/{user_id}/sessions/{session_id} - Delete session
- POST /run - Run agent synchronously
- POST /run_sse - Run agent with Server-Sent Events streaming

Reference:
- google/adk-web: https://github.com/google/adk-web
- ADK API: https://google.github.io/adk-docs/
"""

import json
import logging
import os
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import uvicorn
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field

from session_store import (
    Message,
    Session,
    SessionStore,
    get_session_store,
)
from a2a_adapter import A2AAdapter, AgentConfig, create_adapter

# Configure logging
logger = logging.getLogger(__name__)

# =============================================================================
# Configuration
# =============================================================================

PORT = int(os.getenv("PORT", "8080"))
HOST = os.getenv("HOST", "0.0.0.0")
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

# CORS configuration
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")

# Template configuration
BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

# =============================================================================
# Pydantic Models
# =============================================================================


class AppInfo(BaseModel):
    """Information about an available application/agent."""

    name: str
    description: str = ""
    version: str = "1.0.0"
    skills: List[Dict[str, Any]] = []
    capabilities: Dict[str, bool] = {}


class SessionCreate(BaseModel):
    """Request to create a new session."""

    session_id: Optional[str] = Field(None, alias="sessionId")
    state: Optional[Dict[str, Any]] = None


class SessionResponse(BaseModel):
    """Response for session operations."""

    id: str
    user_id: str = Field(alias="userId")
    app_name: str = Field(alias="appName")
    messages: List[Dict[str, Any]] = []
    state: Dict[str, Any] = {}
    created_at: str = Field(alias="createdAt")
    updated_at: str = Field(alias="updatedAt")

    class Config:
        populate_by_name = True


class RunRequest(BaseModel):
    """Request to run an agent."""

    app_name: str = Field(alias="appName")
    user_id: str = Field(alias="userId")
    session_id: str = Field(alias="sessionId")
    new_message: str = Field(alias="newMessage")
    streaming: bool = False

    class Config:
        populate_by_name = True


class RunResponse(BaseModel):
    """Response from running an agent."""

    session_id: str = Field(alias="sessionId")
    task_id: str = Field(alias="taskId")
    status: str
    message: Optional[str] = None
    artifacts: List[Dict[str, Any]] = []
    timestamp: str

    class Config:
        populate_by_name = True


# =============================================================================
# Helper Functions
# =============================================================================


def serialize_message(message: Message) -> Dict[str, Any]:
    """Serialize a Message to a dictionary for API responses."""
    return {
        "role": message.role,
        "content": message.content,
        "timestamp": message.timestamp,
    }


# =============================================================================
# Application State
# =============================================================================


class AppState:
    """Application state container."""

    def __init__(self):
        self.session_store: Optional[SessionStore] = None
        self.a2a_adapter: Optional[A2AAdapter] = None


app_state = AppState()


# =============================================================================
# FastAPI Application
# =============================================================================


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    print(f"🚀 ADK API Server starting on {HOST}:{PORT}")
    print(f"   Environment: {ENVIRONMENT}")

    # Initialize session store
    app_state.session_store = get_session_store()
    print(f"   Session store: {type(app_state.session_store).__name__}")

    # Initialize A2A adapter and discover agents
    app_state.a2a_adapter = create_adapter()
    agents = app_state.a2a_adapter.list_agents()
    print(f"   Discovered {len(agents)} agents:")
    for agent in agents:
        print(f"     - {agent.name}: {agent.url}")

    yield

    # Cleanup
    if app_state.a2a_adapter:
        await app_state.a2a_adapter.close()
    print("🛑 ADK API Server shutting down")


app = FastAPI(
    title="ADK API Server",
    description="API server for google/adk-web, bridging to A2A protocol agents",
    version="1.0.0",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =============================================================================
# Health and Info Endpoints
# =============================================================================


@app.get("/health")
async def health():
    """Health check endpoint."""
    agents = app_state.a2a_adapter.list_agents() if app_state.a2a_adapter else []
    return {
        "status": "healthy",
        "service": "adk-api-server",
        "version": "1.0.0",
        "environment": ENVIRONMENT,
        "agents_configured": len(agents),
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Root endpoint - serves the Agent Console GUI."""
    agents = app_state.a2a_adapter.list_agents() if app_state.a2a_adapter else []
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "service_name": "ADK API Server",
            "version": "1.0.0",
            "environment": ENVIRONMENT,
            "agent_count": len(agents),
        }
    )


@app.get("/api")
async def api_info():
    """API information endpoint (JSON)."""
    return {
        "service": "ADK API Server",
        "description": "API server for google/adk-web, bridging to A2A protocol agents",
        "version": "1.0.0",
        "endpoints": {
            "list_apps": "GET /list-apps",
            "create_session": "POST /apps/{app_name}/users/{user_id}/sessions",
            "list_sessions": "GET /apps/{app_name}/users/{user_id}/sessions",
            "get_session": "GET /apps/{app_name}/users/{user_id}/sessions/{session_id}",
            "delete_session": "DELETE /apps/{app_name}/users/{user_id}/sessions/{session_id}",
            "run": "POST /run",
            "run_sse": "POST /run_sse",
            "health": "GET /health",
        },
        "gui": "GET /",
        "docs": {
            "ag_ui_protocol": "https://docs.ag-ui.com/",
            "copilotkit": "https://docs.copilotkit.ai/",
            "google_adk": "https://google.github.io/adk-docs/",
        },
    }


# =============================================================================
# App/Agent Management Endpoints
# =============================================================================


@app.get("/list-apps", response_model=List[AppInfo])
async def list_apps():
    """List all available agent applications.

    This endpoint returns the list of A2A agents configured for this server.
    """
    if not app_state.a2a_adapter:
        return []

    agents = app_state.a2a_adapter.list_agents()

    # Refresh agent details from their Agent Cards
    result = []
    for agent in agents:
        # Try to refresh from Agent Card
        refreshed = await app_state.a2a_adapter.refresh_agent_details(agent.name)
        if refreshed:
            result.append(
                AppInfo(
                    name=refreshed.name,
                    description=refreshed.description,
                    version=refreshed.version,
                    skills=refreshed.skills,
                    capabilities=refreshed.capabilities,
                )
            )
        else:
            result.append(
                AppInfo(
                    name=agent.name,
                    description=agent.description,
                    version=agent.version,
                )
            )

    return result


@app.get("/apps/{app_name}")
async def get_app(app_name: str):
    """Get details for a specific application/agent."""
    if not app_state.a2a_adapter:
        raise HTTPException(status_code=503, detail="Service not initialized")

    agent = app_state.a2a_adapter.get_agent(app_name)
    if not agent:
        raise HTTPException(status_code=404, detail=f"App not found: {app_name}")

    # Refresh agent details
    refreshed = await app_state.a2a_adapter.refresh_agent_details(app_name)
    if refreshed:
        agent = refreshed

    return AppInfo(
        name=agent.name,
        description=agent.description,
        version=agent.version,
        skills=agent.skills,
        capabilities=agent.capabilities,
    )


# =============================================================================
# Session Management Endpoints
# =============================================================================


@app.post(
    "/apps/{app_name}/users/{user_id}/sessions", response_model=SessionResponse
)
async def create_session(
    app_name: str,
    user_id: str,
    request: SessionCreate = None,
):
    """Create a new session for a user with an agent."""
    if not app_state.session_store:
        raise HTTPException(status_code=503, detail="Service not initialized")

    # Verify agent exists
    if app_state.a2a_adapter and not app_state.a2a_adapter.get_agent(app_name):
        raise HTTPException(status_code=404, detail=f"App not found: {app_name}")

    session_id = request.session_id if request else None
    session = await app_state.session_store.create_session(
        app_name, user_id, session_id
    )

    # Set initial state if provided
    if request and request.state:
        session.state = request.state
        session = await app_state.session_store.update_session(session)

    return SessionResponse(
        id=session.id,
        userId=session.user_id,
        appName=session.app_name,
        messages=[serialize_message(m) for m in session.messages],
        state=session.state,
        createdAt=session.created_at,
        updatedAt=session.updated_at,
    )


@app.get(
    "/apps/{app_name}/users/{user_id}/sessions", response_model=List[SessionResponse]
)
async def list_sessions(app_name: str, user_id: str):
    """List all sessions for a user with an agent."""
    if not app_state.session_store:
        raise HTTPException(status_code=503, detail="Service not initialized")

    sessions = await app_state.session_store.list_sessions(app_name, user_id)

    return [
        SessionResponse(
            id=s.id,
            userId=s.user_id,
            appName=s.app_name,
            messages=[serialize_message(m) for m in s.messages],
            state=s.state,
            createdAt=s.created_at,
            updatedAt=s.updated_at,
        )
        for s in sessions
    ]


@app.get(
    "/apps/{app_name}/users/{user_id}/sessions/{session_id}",
    response_model=SessionResponse,
)
async def get_session(app_name: str, user_id: str, session_id: str):
    """Get a specific session."""
    if not app_state.session_store:
        raise HTTPException(status_code=503, detail="Service not initialized")

    session = await app_state.session_store.get_session(app_name, user_id, session_id)
    if not session:
        raise HTTPException(status_code=404, detail=f"Session not found: {session_id}")

    return SessionResponse(
        id=session.id,
        userId=session.user_id,
        appName=session.app_name,
        messages=[serialize_message(m) for m in session.messages],
        state=session.state,
        createdAt=session.created_at,
        updatedAt=session.updated_at,
    )


@app.delete("/apps/{app_name}/users/{user_id}/sessions/{session_id}")
async def delete_session(app_name: str, user_id: str, session_id: str):
    """Delete a session."""
    if not app_state.session_store:
        raise HTTPException(status_code=503, detail="Service not initialized")

    deleted = await app_state.session_store.delete_session(
        app_name, user_id, session_id
    )
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Session not found: {session_id}")

    return {"status": "deleted", "session_id": session_id}


# =============================================================================
# Agent Execution Endpoints
# =============================================================================


@app.post("/run", response_model=RunResponse)
async def run_agent(request: RunRequest):
    """Run an agent synchronously.

    This sends a message to the A2A agent and waits for a response.
    """
    if not app_state.a2a_adapter or not app_state.session_store:
        raise HTTPException(status_code=503, detail="Service not initialized")

    # Verify agent exists
    agent = app_state.a2a_adapter.get_agent(request.app_name)
    if not agent:
        raise HTTPException(
            status_code=404, detail=f"App not found: {request.app_name}"
        )

    # Get or create session
    session = await app_state.session_store.get_session(
        request.app_name, request.user_id, request.session_id
    )
    if not session:
        session = await app_state.session_store.create_session(
            request.app_name, request.user_id, request.session_id
        )

    # Add user message to session
    user_message = Message(
        role="user",
        content=request.new_message,
    )
    session = await app_state.session_store.add_message(
        request.app_name, request.user_id, request.session_id, user_message
    )

    try:
        # Send message to A2A agent
        task = await app_state.a2a_adapter.send_message(
            request.app_name,
            request.new_message,
            context_id=request.session_id,
        )

        # Extract response message
        status_message = task.status.get("message", {})
        response_text = ""
        if status_message:
            parts = status_message.get("parts", [])
            response_text = " ".join(p.get("text", "") for p in parts)

        # Add agent response to session
        agent_message = Message(
            role="agent",
            content=response_text,
            metadata={
                "task_id": task.id,
                "artifacts": task.artifacts,
            },
        )
        await app_state.session_store.add_message(
            request.app_name, request.user_id, request.session_id, agent_message
        )

        return RunResponse(
            sessionId=request.session_id,
            taskId=task.id,
            status=task.status.get("state", "completed"),
            message=response_text,
            artifacts=task.artifacts,
            timestamp=datetime.utcnow().isoformat(),
        )

    except Exception as e:
        logger.error(f"Agent execution failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Agent execution failed. Please try again.")


@app.post("/run_sse")
async def run_agent_sse(request: RunRequest):
    """Run an agent with Server-Sent Events streaming.

    This provides real-time updates as the agent processes the request.
    """
    if not app_state.a2a_adapter or not app_state.session_store:
        raise HTTPException(status_code=503, detail="Service not initialized")

    # Verify agent exists
    agent = app_state.a2a_adapter.get_agent(request.app_name)
    if not agent:
        raise HTTPException(
            status_code=404, detail=f"App not found: {request.app_name}"
        )

    # Get or create session
    session = await app_state.session_store.get_session(
        request.app_name, request.user_id, request.session_id
    )
    if not session:
        session = await app_state.session_store.create_session(
            request.app_name, request.user_id, request.session_id
        )

    # Add user message to session
    user_message = Message(
        role="user",
        content=request.new_message,
    )
    await app_state.session_store.add_message(
        request.app_name, request.user_id, request.session_id, user_message
    )

    async def generate_sse():
        """Generate Server-Sent Events."""
        response_text = ""
        task_id = ""

        async for event in app_state.a2a_adapter.stream_message(
            request.app_name,
            request.new_message,
            context_id=request.session_id,
        ):
            event_type = event.get("event", "message")
            event_data = event.get("data", "{}")

            # Track response for session storage
            if event_type == "message":
                try:
                    data = json.loads(event_data)
                    response_text += data.get("content", "")
                except json.JSONDecodeError:
                    pass
            elif event_type == "start":
                try:
                    data = json.loads(event_data)
                    task_id = data.get("task_id", "")
                except json.JSONDecodeError:
                    pass

            # Format as SSE
            yield f"event: {event_type}\n"
            yield f"data: {event_data}\n\n"

        # Store agent response in session
        if response_text:
            agent_message = Message(
                role="agent",
                content=response_text,
                metadata={"task_id": task_id},
            )
            await app_state.session_store.add_message(
                request.app_name, request.user_id, request.session_id, agent_message
            )

    return StreamingResponse(
        generate_sse(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


# =============================================================================
# Agent Health Endpoints
# =============================================================================


@app.get("/apps/{app_name}/health")
async def check_agent_health(app_name: str):
    """Check the health of a specific agent."""
    if not app_state.a2a_adapter:
        raise HTTPException(status_code=503, detail="Service not initialized")

    health = await app_state.a2a_adapter.check_health(app_name)
    return health


# =============================================================================
# Main Entry Point
# =============================================================================

if __name__ == "__main__":
    uvicorn.run(app, host=HOST, port=PORT)
