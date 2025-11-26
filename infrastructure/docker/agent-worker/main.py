"""
Chained Agent Worker - Main Application
=======================================
Agent workers process tasks from the Pub/Sub queue and store results
in Firestore.
"""

import base64
import json
import os
from datetime import datetime
from typing import Dict, Optional

from fastapi import FastAPI, HTTPException, Request
from google.cloud import firestore
from pydantic import BaseModel

# =============================================================================
# Configuration
# =============================================================================

ENVIRONMENT = os.getenv("ENVIRONMENT", "dev")
PUBSUB_SUBSCRIPTION = os.getenv("PUBSUB_SUBSCRIPTION", "chained-agent-tasks-sub")
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "")

# Initialize Firestore client
db = None

# =============================================================================
# FastAPI Application
# =============================================================================

app = FastAPI(
    title="Chained Agent Worker",
    description="Processes agent tasks from Pub/Sub queue",
    version="1.0.0",
)


# =============================================================================
# Models
# =============================================================================


class PubSubMessage(BaseModel):
    """Pub/Sub push message format."""

    message: Dict
    subscription: Optional[str] = None


class TaskResult(BaseModel):
    """Result of task processing."""

    task_id: str
    status: str
    result: Dict
    agent: str
    completed_at: str


# =============================================================================
# Startup/Shutdown
# =============================================================================


@app.on_event("startup")
async def startup_event():
    """Initialize GCP clients on startup."""
    global db

    if PROJECT_ID:
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
        "service": "chained-agent-worker",
        "environment": ENVIRONMENT,
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.get("/")
async def root():
    """Root endpoint with worker information."""
    return {
        "service": "Chained Agent Worker",
        "version": "1.0.0",
        "description": "Processes agent tasks from Pub/Sub queue",
        "endpoints": {
            "health": "/health",
            "process_task": "POST /process (Pub/Sub push)",
        },
    }


@app.post("/process")
async def process_task(request: Request):
    """
    Process a task from Pub/Sub push subscription.
    This endpoint receives Pub/Sub messages as HTTP POST requests.
    """
    try:
        body = await request.json()
        envelope = PubSubMessage(**body)

        # Decode the Pub/Sub message data
        message_data = envelope.message.get("data", "")
        if message_data:
            decoded = base64.b64decode(message_data).decode("utf-8")
            task = json.loads(decoded)
        else:
            raise HTTPException(status_code=400, detail="Empty message data")

        print(f"📥 Received task: {task.get('id', 'unknown')}")

        # Process the task
        result = await execute_task(task)

        # Update task status in Firestore
        if db and task.get("id"):
            db.collection("tasks").document(task["id"]).update(
                {
                    "status": "completed",
                    "result": result,
                    "completed_at": datetime.utcnow().isoformat(),
                }
            )

        print(f"✅ Completed task: {task.get('id', 'unknown')}")
        return {"status": "success", "task_id": task.get("id")}

    except Exception as e:
        print(f"❌ Error processing task: {e}")
        # Return 200 to acknowledge the message (avoid redelivery)
        # In production, you might want to handle retries differently
        return {"status": "error", "error": str(e)}


async def execute_task(task: Dict) -> Dict:
    """
    Execute the agent task based on task type.
    This is a placeholder - implement real agent logic here.
    """
    task_type = task.get("type", "unknown")
    task_input = task.get("input", {})
    assigned_agent = task.get("assigned_agent", "unknown")

    print(f"🤖 Agent '{assigned_agent}' executing task type: {task_type}")

    # Simulate different agent behaviors based on task type
    if task_type in ["analyze", "research", "investigate"]:
        result = await analyze_task(task_input)
    elif task_type in ["implement", "code", "fix"]:
        result = await implement_task(task_input)
    elif task_type in ["review", "check"]:
        result = await review_task(task_input)
    elif task_type in ["document", "explain"]:
        result = await document_task(task_input)
    else:
        result = {"message": f"Processed unknown task type: {task_type}"}

    return {
        "task_type": task_type,
        "agent": assigned_agent,
        "output": result,
        "processing_time_ms": 100,  # Placeholder
    }


# =============================================================================
# Agent Task Implementations (Placeholders)
# =============================================================================


async def analyze_task(input_data: Dict) -> Dict:
    """Investigator agent: Analyze and research."""
    topic = input_data.get("topic", "unknown topic")
    return {
        "analysis": f"Analyzed topic: {topic}",
        "findings": ["Finding 1", "Finding 2", "Finding 3"],
        "confidence": 0.85,
    }


async def implement_task(input_data: Dict) -> Dict:
    """Engineer agent: Implement solutions."""
    feature = input_data.get("feature", "unknown feature")
    return {
        "implementation": f"Implemented feature: {feature}",
        "files_changed": ["file1.py", "file2.py"],
        "tests_passed": True,
    }


async def review_task(input_data: Dict) -> Dict:
    """Reviewer agent: Review code or content."""
    target = input_data.get("target", "unknown target")
    return {
        "review": f"Reviewed: {target}",
        "score": 8.5,
        "suggestions": ["Suggestion 1", "Suggestion 2"],
    }


async def document_task(input_data: Dict) -> Dict:
    """Documenter agent: Create documentation."""
    subject = input_data.get("subject", "unknown subject")
    return {
        "documentation": f"Documented: {subject}",
        "sections": ["Overview", "Usage", "Examples"],
        "word_count": 500,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8080)
