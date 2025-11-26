"""
Chained Agent Gateway - Main Application
========================================
The agent gateway receives A2A tasks and dispatches them to agent workers
via Cloud Pub/Sub.
"""

import json
import os
import uuid
from datetime import datetime
from typing import Dict, List, Optional

from fastapi import FastAPI, HTTPException
from google.cloud import firestore, pubsub_v1
from pydantic import BaseModel

# =============================================================================
# Configuration
# =============================================================================

ENVIRONMENT = os.getenv("ENVIRONMENT", "dev")
PUBSUB_TOPIC = os.getenv("PUBSUB_TOPIC", "chained-agent-tasks")
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "")

# Initialize clients
publisher = None
db = None

# =============================================================================
# FastAPI Application
# =============================================================================

app = FastAPI(
    title="Chained Agent Gateway",
    description="A2A-compatible agent gateway for task dispatching",
    version="1.0.0",
)


# =============================================================================
# Models
# =============================================================================


class AgentTask(BaseModel):
    """A2A-compatible task model."""

    type: str
    input: Dict
    assigned_agent: Optional[str] = None
    required_skills: Optional[List[str]] = None
    priority: Optional[int] = 5
    metadata: Optional[Dict] = None


class TaskResponse(BaseModel):
    """Response after task submission."""

    task_id: str
    status: str
    assigned_agent: Optional[str] = None
    created_at: str


# =============================================================================
# Startup/Shutdown
# =============================================================================


@app.on_event("startup")
async def startup_event():
    """Initialize GCP clients on startup."""
    global publisher, db

    if PROJECT_ID:
        publisher = pubsub_v1.PublisherClient()
        db = firestore.Client()
        print(f"✅ Connected to GCP project: {PROJECT_ID}")
    else:
        print("⚠️ Running in local mode (no GCP project configured)")


# =============================================================================
# Endpoints
# =============================================================================


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "chained-agent-gateway",
        "environment": ENVIRONMENT,
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "service": "Chained Agent Gateway",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "submit_task": "POST /a2a/task",
            "get_task": "GET /a2a/task/{task_id}",
            "list_agents": "GET /agents",
        },
    }


@app.post("/a2a/task", response_model=TaskResponse)
async def submit_task(task: AgentTask):
    """
    Submit a task for agent processing (A2A-compatible endpoint).
    """
    task_id = f"task-{uuid.uuid4().hex[:12]}"
    created_at = datetime.utcnow().isoformat()

    # Match task to appropriate agent if not specified
    assigned_agent = task.assigned_agent or match_task_to_agent(task)

    # Prepare task data
    task_data = {
        "id": task_id,
        "type": task.type,
        "input": task.input,
        "assigned_agent": assigned_agent,
        "required_skills": task.required_skills or [],
        "priority": task.priority,
        "status": "submitted",
        "created_at": created_at,
        "metadata": task.metadata or {},
    }

    # Store task in Firestore
    if db:
        db.collection("tasks").document(task_id).set(task_data)

    # Publish to Pub/Sub for worker processing
    if publisher and PROJECT_ID:
        topic_path = publisher.topic_path(PROJECT_ID, PUBSUB_TOPIC)
        message = json.dumps(task_data).encode("utf-8")
        future = publisher.publish(topic_path, message)
        future.result()  # Wait for publish to complete
        print(f"📤 Published task {task_id} to {PUBSUB_TOPIC}")

    return TaskResponse(
        task_id=task_id,
        status="submitted",
        assigned_agent=assigned_agent,
        created_at=created_at,
    )


@app.get("/a2a/task/{task_id}")
async def get_task(task_id: str):
    """
    Get task status and details.
    """
    if not db:
        raise HTTPException(status_code=503, detail="Firestore not available")

    doc = db.collection("tasks").document(task_id).get()

    if not doc.exists:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

    return doc.to_dict()


@app.get("/agents")
async def list_agents():
    """
    List available agents and their capabilities.
    """
    # Agent registry - in production, this would come from Firestore
    agents = [
        {
            "name": "investigator",
            "skills": ["analysis", "research", "investigation"],
            "status": "active",
        },
        {
            "name": "engineer",
            "skills": ["implementation", "coding", "debugging"],
            "status": "active",
        },
        {
            "name": "reviewer",
            "skills": ["code-review", "quality", "feedback"],
            "status": "active",
        },
        {
            "name": "documenter",
            "skills": ["documentation", "writing", "explanation"],
            "status": "active",
        },
    ]

    return {
        "agents": agents,
        "total": len(agents),
        "timestamp": datetime.utcnow().isoformat(),
    }


# =============================================================================
# Helper Functions
# =============================================================================


def match_task_to_agent(task: AgentTask) -> str:
    """
    Match a task to the most appropriate agent based on task type and skills.
    """
    # Simple matching logic - in production, this would be more sophisticated
    task_type_mapping = {
        "analyze": "investigator",
        "research": "investigator",
        "investigate": "investigator",
        "implement": "engineer",
        "code": "engineer",
        "fix": "engineer",
        "review": "reviewer",
        "check": "reviewer",
        "document": "documenter",
        "explain": "documenter",
    }

    task_type = task.type.lower()
    for keyword, agent in task_type_mapping.items():
        if keyword in task_type:
            return agent

    # Default to investigator for unknown task types
    return "investigator"


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8080)
