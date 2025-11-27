"""
Academic Research Agent - ADK-based A2A Agent
==============================================

This agent discovers and analyzes academic research topics, then passes
insights to other agents in the blog writing pipeline.

Based on Google ADK patterns from:
- https://github.com/google/adk-samples
- https://google.github.io/adk-docs/

A2A Protocol Implementation:
- Exposes AgentCard at /.well-known/agent.json
- Handles SendMessage at POST /a2a/tasks
- Returns Tasks with artifacts containing research findings
"""

import json
import os
import random
from datetime import datetime
from typing import Any, Dict, List, Optional
from contextlib import asynccontextmanager

import httpx
import uvicorn
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel

# =============================================================================
# Configuration
# =============================================================================

AGENT_NAME = "academic-research"
AGENT_DESCRIPTION = "Discovers and analyzes academic research topics for blog content"
AGENT_VERSION = "1.0.0"
PORT = int(os.getenv("PORT", "8081"))
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")

# Use Gemini API if available
USE_AI = bool(GEMINI_API_KEY or GOOGLE_API_KEY)


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
# Research Topics Database (Simulated)
# =============================================================================

RESEARCH_DOMAINS = [
    {
        "domain": "Artificial Intelligence",
        "topics": [
            {
                "title": "Large Language Model Reasoning Capabilities",
                "abstract": "Recent advances in chain-of-thought prompting and reasoning in LLMs.",
                "keywords": ["LLM", "reasoning", "AI", "chain-of-thought"],
                "relevance_score": 0.95,
            },
            {
                "title": "Multimodal Foundation Models",
                "abstract": "Integration of vision, language, and audio in unified AI models.",
                "keywords": ["multimodal", "vision", "foundation models"],
                "relevance_score": 0.92,
            },
            {
                "title": "AI Safety and Alignment",
                "abstract": "Ensuring AI systems remain beneficial and aligned with human values.",
                "keywords": ["AI safety", "alignment", "ethics"],
                "relevance_score": 0.90,
            },
        ],
    },
    {
        "domain": "Cloud Computing",
        "topics": [
            {
                "title": "Serverless Computing Patterns",
                "abstract": "Best practices for building scalable serverless applications.",
                "keywords": ["serverless", "cloud", "scalability"],
                "relevance_score": 0.88,
            },
            {
                "title": "Edge Computing and 5G",
                "abstract": "Low-latency computing at the network edge.",
                "keywords": ["edge", "5G", "latency"],
                "relevance_score": 0.85,
            },
        ],
    },
    {
        "domain": "Software Engineering",
        "topics": [
            {
                "title": "AI-Assisted Code Generation",
                "abstract": "Using AI tools to augment software development workflows.",
                "keywords": ["AI coding", "Copilot", "automation"],
                "relevance_score": 0.93,
            },
            {
                "title": "DevOps and Platform Engineering",
                "abstract": "Evolution of developer experience and internal platforms.",
                "keywords": ["DevOps", "platform", "developer experience"],
                "relevance_score": 0.87,
            },
        ],
    },
    {
        "domain": "Cybersecurity",
        "topics": [
            {
                "title": "Zero Trust Architecture",
                "abstract": "Implementing zero trust security in modern enterprises.",
                "keywords": ["zero trust", "security", "authentication"],
                "relevance_score": 0.89,
            },
            {
                "title": "AI-Powered Threat Detection",
                "abstract": "Using machine learning for security threat identification.",
                "keywords": ["AI security", "threat detection", "ML"],
                "relevance_score": 0.86,
            },
        ],
    },
]


# =============================================================================
# Agent Logic
# =============================================================================


def generate_task_id() -> str:
    """Generate a unique task ID."""
    import uuid
    return f"task-{uuid.uuid4().hex[:12]}"


async def discover_research_topics(
    query: Optional[str] = None,
    max_topics: int = 3
) -> List[Dict[str, Any]]:
    """
    Discover research topics based on query or randomly.

    In production, this would:
    1. Query academic APIs (arXiv, Google Scholar, Semantic Scholar)
    2. Use Gemini to analyze and summarize papers
    3. Score topics for blog relevance
    """
    all_topics = []
    for domain in RESEARCH_DOMAINS:
        for topic in domain["topics"]:
            all_topics.append({
                **topic,
                "domain": domain["domain"],
            })

    # Filter by query if provided
    if query:
        query_lower = query.lower()
        filtered = [
            t for t in all_topics
            if query_lower in t["title"].lower()
            or query_lower in t["abstract"].lower()
            or any(query_lower in k.lower() for k in t["keywords"])
        ]
        if filtered:
            all_topics = filtered

    # Sort by relevance and return top N
    all_topics.sort(key=lambda x: x["relevance_score"], reverse=True)
    return all_topics[:max_topics]


async def analyze_topic_for_blog(topic: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyze a research topic and generate blog writing suggestions.

    In production, this would use Gemini to:
    1. Summarize the research in accessible language
    2. Identify key insights for general audience
    3. Suggest blog angles and structure
    """
    return {
        "topic": topic["title"],
        "domain": topic["domain"],
        "blog_angle": f"How {topic['title']} is changing the industry",
        "key_points": [
            f"Introduction to {topic['keywords'][0] if topic['keywords'] else 'the topic'}",
            "Current state of research",
            "Practical implications for practitioners",
            "Future directions and predictions",
        ],
        "target_audience": "Tech professionals and enthusiasts",
        "suggested_length": "1500-2000 words",
        "seo_keywords": topic["keywords"],
    }


async def process_research_request(message_text: str) -> Dict[str, Any]:
    """
    Process a research request and return findings.
    """
    # Extract query from message (simple parsing)
    query = None
    if "about" in message_text.lower():
        query = message_text.lower().split("about")[-1].strip()
    elif "on" in message_text.lower():
        query = message_text.lower().split("on")[-1].strip()

    # Discover topics
    topics = await discover_research_topics(query=query, max_topics=3)

    # Analyze each topic for blog potential
    analyses = []
    for topic in topics:
        analysis = await analyze_topic_for_blog(topic)
        analyses.append(analysis)

    return {
        "query": query,
        "topics_found": len(topics),
        "topics": topics,
        "blog_analyses": analyses,
        "recommended_topic": analyses[0] if analyses else None,
        "timestamp": datetime.utcnow().isoformat(),
    }


# =============================================================================
# FastAPI Application
# =============================================================================


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    print(f"🔬 Academic Research Agent starting on port {PORT}")
    print(f"   AI Mode: {'Enabled' if USE_AI else 'Simulated'}")
    yield
    print("🔬 Academic Research Agent shutting down")


app = FastAPI(
    title="Academic Research Agent",
    description="A2A-compatible agent for discovering research topics",
    version=AGENT_VERSION,
    lifespan=lifespan,
)


# =============================================================================
# A2A Protocol Endpoints
# =============================================================================


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
                id="discover-topics",
                name="Discover Research Topics",
                description="Find trending academic research topics for blog content",
                tags=["research", "discovery", "topics"],
            ),
            AgentSkill(
                id="analyze-topic",
                name="Analyze Topic for Blog",
                description="Analyze a research topic and suggest blog angles",
                tags=["analysis", "blog", "content"],
            ),
        ],
        capabilities={
            "streaming": False,
            "pushNotifications": False,
        },
    )


@app.post("/a2a/tasks")
async def send_message(request: SendMessageRequest) -> Task:
    """
    Handle A2A SendMessage operation per specification §3.1.1.

    This is the main entry point for agent communication.
    """
    task_id = generate_task_id()

    try:
        # Extract message text
        message_text = " ".join(part.text for part in request.message.parts)

        # Process the research request
        result = await process_research_request(message_text)

        # Create artifacts
        artifacts = [
            Artifact(
                name="research-findings",
                type="application/json",
                data=json.dumps(result),
            ),
            Artifact(
                name="recommended-topic",
                type="text/plain",
                data=json.dumps(result.get("recommended_topic", {})),
            ),
        ]

        # Return completed task
        return Task(
            id=task_id,
            contextId=request.contextId,
            status=TaskStatus(
                state="completed",
                timestamp=datetime.utcnow().isoformat(),
                message=Message(
                    role="agent",
                    parts=[MessagePart(
                        text=f"Found {result['topics_found']} research topics. "
                             f"Recommended: {result['recommended_topic']['topic'] if result.get('recommended_topic') else 'None'}"
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
    """Get task status (for async operations)."""
    # In a production system, tasks would be stored in a database
    raise HTTPException(
        status_code=404,
        detail="Task not found (this agent uses synchronous processing)"
    )


# =============================================================================
# Health and Info Endpoints
# =============================================================================


@app.get("/health")
async def health():
    """Health check endpoint for Cloud Run."""
    return {
        "status": "healthy",
        "agent": AGENT_NAME,
        "version": AGENT_VERSION,
        "ai_mode": "enabled" if USE_AI else "simulated",
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


# =============================================================================
# Main Entry Point
# =============================================================================


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=PORT)
