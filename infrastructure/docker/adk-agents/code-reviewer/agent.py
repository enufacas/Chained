"""
Code Reviewer Agent - ADK-based A2A Agent
==========================================

This agent reviews code snippets and suggests improvements, best practices,
and potential issues. Part of the multi-agent team system.

A2A Protocol Implementation:
- Exposes AgentCard at /.well-known/agent.json
- Handles SendMessage at POST /a2a/tasks
- Returns Tasks with artifacts containing code review analysis
"""

import json
import os
import sys
from datetime import datetime
from typing import Any, Dict, List, Optional
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# Add shared utilities to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from shared.a2a_utils import parse_llm_json_response
from shared.gemini_client import (
    generate_content,
    is_available as gemini_is_available,
    get_mode as gemini_get_mode,
    get_unavailable_error_message,
    get_config_info as gemini_get_config_info,
    GeminiError,
    GeminiUnavailableError,
)

# =============================================================================
# Configuration
# =============================================================================

AGENT_NAME = "code-reviewer"
AGENT_DESCRIPTION = "Reviews code snippets, suggests improvements, and identifies best practices"
AGENT_VERSION = "1.0.0"
PORT = int(os.getenv("PORT", "8084"))

USE_AI = gemini_is_available()

if USE_AI:
    config_info = gemini_get_config_info()
    print(f"✅ Gemini AI configured for code reviewer agent (mode={config_info['active_mode']})")
else:
    print(f"⚠️ Code Reviewer Agent: Gemini AI NOT configured - will return error")


# =============================================================================
# Pydantic Models
# =============================================================================


class AgentSkill(BaseModel):
    """A2A Agent Skill per specification §4.4.5."""
    id: str
    name: str
    description: str
    tags: List[str] = []


class AgentCard(BaseModel):
    """A2A Agent Card per specification §4.4.1."""
    name: str
    description: str
    url: str
    version: str = "1.0.0"
    protocolVersion: str = "0.3.0"
    skills: List[AgentSkill] = []
    capabilities: Dict[str, bool] = {"streaming": False, "pushNotifications": False}


class MessagePart(BaseModel):
    """A2A Message Part (TextPart)."""
    text: str


class Message(BaseModel):
    """A2A Message per specification §4.1.4."""
    role: str
    parts: List[MessagePart]


class SendMessageRequest(BaseModel):
    """A2A SendMessage request per specification §3.1.1."""
    message: Message
    contextId: Optional[str] = None
    referenceTaskIds: Optional[List[str]] = None


class TaskStatus(BaseModel):
    """A2A Task Status per specification §4.1.2."""
    state: str
    timestamp: str
    message: Optional[Message] = None


class Artifact(BaseModel):
    """A2A Artifact per specification §4.1.9."""
    name: str
    type: str = "text"
    data: str


class Task(BaseModel):
    """A2A Task per specification §4.1.1."""
    id: str
    contextId: Optional[str] = None
    status: TaskStatus
    artifacts: List[Artifact] = []
    referenceTaskIds: List[str] = []


# =============================================================================
# Agent Logic
# =============================================================================


def generate_task_id() -> str:
    """Generate a unique task ID."""
    import uuid
    return f"task-{uuid.uuid4().hex[:12]}"


async def review_code(code: str, language: Optional[str] = None) -> Dict[str, Any]:
    """
    Review code using Gemini AI.
    """
    if not USE_AI:
        raise GeminiUnavailableError(get_unavailable_error_message(agent_name=AGENT_NAME))
    
    prompt = f"""You are an expert code reviewer. Analyze the following code and provide a comprehensive review.

Code to review:
```{language or ''}
{code}
```

Provide your review as a JSON object with this structure:
{{
    "language_detected": "The programming language",
    "overall_quality": "excellent|good|needs_improvement|poor",
    "score": 85,  // 0-100
    "summary": "Brief overall assessment",
    "issues": [
        {{
            "severity": "critical|warning|suggestion",
            "line": 1,
            "description": "Issue description",
            "suggestion": "How to fix it"
        }}
    ],
    "best_practices": [
        "What the code does well"
    ],
    "improvements": [
        {{
            "category": "performance|security|readability|maintainability",
            "description": "Improvement suggestion",
            "example": "Example of improved code if applicable"
        }}
    ],
    "security_concerns": [
        "Any security issues found"
    ],
    "refactored_code": "If significant improvements are possible, show refactored version"
}}

Return ONLY the JSON, no other text."""

    try:
        result = await generate_content(
            prompt=prompt,
            temperature=0.3,
            max_output_tokens=4096,
        )
        
        if result["text"]:
            review = parse_llm_json_response(result["text"])
            if review:
                return review
            raise GeminiError(f"Failed to parse review response")
        raise GeminiError("Empty response from Gemini")
        
    except (GeminiError, GeminiUnavailableError):
        raise
    except Exception as e:
        raise GeminiError(f"Code review failed: {e}")


async def process_review_request(message_text: str) -> Dict[str, Any]:
    """Process a code review request."""
    # Extract code from message
    code = message_text
    language = None
    
    # Try to extract code from markdown code blocks
    import re
    code_block = re.search(r'```(\w+)?\s*([\s\S]*?)```', message_text)
    if code_block:
        language = code_block.group(1)
        code = code_block.group(2).strip()
    
    review = await review_code(code, language)
    
    return {
        "review": review,
        "code_length": len(code),
        "language": language or review.get("language_detected", "unknown"),
        "timestamp": datetime.utcnow().isoformat(),
    }


# =============================================================================
# FastAPI Application
# =============================================================================


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    print(f"🔍 Code Reviewer Agent starting on port {PORT}")
    print(f"   AI Mode: {'Enabled' if USE_AI else 'Disabled'}")
    yield
    print("🔍 Code Reviewer Agent shutting down")


app = FastAPI(
    title="Code Reviewer Agent",
    description="A2A-compatible agent for code review and analysis",
    version=AGENT_VERSION,
    lifespan=lifespan,
)


@app.get("/.well-known/agent.json")
async def get_agent_card() -> AgentCard:
    """Return the A2A Agent Card per specification §4.4.1."""
    base_url = os.getenv("AGENT_URL", f"http://localhost:{PORT}")
    return AgentCard(
        name=AGENT_NAME,
        description=AGENT_DESCRIPTION,
        url=base_url,
        version=AGENT_VERSION,
        skills=[
            AgentSkill(
                id="review-code",
                name="Review Code",
                description="Analyze code for issues, best practices, and improvements",
                tags=["code", "review", "quality", "best-practices"],
            ),
            AgentSkill(
                id="suggest-improvements",
                name="Suggest Improvements",
                description="Provide refactoring suggestions and code improvements",
                tags=["refactoring", "optimization", "clean-code"],
            ),
            AgentSkill(
                id="security-check",
                name="Security Check",
                description="Identify potential security vulnerabilities in code",
                tags=["security", "vulnerabilities", "audit"],
            ),
        ],
        capabilities={"streaming": False, "pushNotifications": False},
    )


@app.post("/a2a/tasks")
async def send_message(request: SendMessageRequest) -> Task:
    """Handle A2A SendMessage operation per specification §3.1.1."""
    task_id = generate_task_id()
    
    try:
        message_text = " ".join(part.text for part in request.message.parts)
        result = await process_review_request(message_text)
        
        review = result["review"]
        summary = review.get("summary", "Code review completed")
        score = review.get("score", 0)
        quality = review.get("overall_quality", "unknown")
        
        artifacts = [
            Artifact(
                name="code-review",
                type="application/json",
                data=json.dumps(result),
            ),
            Artifact(
                name="review-summary",
                type="text/markdown",
                data=f"""# Code Review Summary

**Quality Score:** {score}/100 ({quality})

## Summary
{summary}

## Issues Found
{len(review.get('issues', []))} issues identified

## Best Practices
{len(review.get('best_practices', []))} best practices noted

## Improvement Suggestions
{len(review.get('improvements', []))} improvements suggested
""",
            ),
        ]
        
        return Task(
            id=task_id,
            contextId=request.contextId,
            status=TaskStatus(
                state="completed",
                timestamp=datetime.utcnow().isoformat(),
                message=Message(
                    role="agent",
                    parts=[MessagePart(
                        text=f"Code review completed. Quality: {quality} ({score}/100). {len(review.get('issues', []))} issues found."
                    )],
                ),
            ),
            artifacts=artifacts,
            referenceTaskIds=request.referenceTaskIds or [],
        )
        
    except Exception as e:
        return Task(
            id=task_id,
            contextId=request.contextId,
            status=TaskStatus(
                state="failed",
                timestamp=datetime.utcnow().isoformat(),
                message=Message(
                    role="agent",
                    parts=[MessagePart(text=f"Error: {str(e)}")],
                ),
            ),
            artifacts=[],
            referenceTaskIds=request.referenceTaskIds or [],
        )


@app.get("/a2a/tasks/{task_id}")
async def get_task(task_id: str) -> Task:
    """Get task status."""
    raise HTTPException(
        status_code=404,
        detail="Task not found (this agent uses synchronous processing)"
    )


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "agent": AGENT_NAME,
        "version": AGENT_VERSION,
        "ai_mode": "enabled" if USE_AI else "disabled",
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.get("/")
async def root():
    """Root endpoint with agent information."""
    return {
        "agent": AGENT_NAME,
        "description": AGENT_DESCRIPTION,
        "version": AGENT_VERSION,
        "a2a_protocol": "0.3.0",
        "endpoints": {
            "agent_card": "GET /.well-known/agent.json",
            "send_message": "POST /a2a/tasks",
            "health": "GET /health",
        },
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=PORT)
