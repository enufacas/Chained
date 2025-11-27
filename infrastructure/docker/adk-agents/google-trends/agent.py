"""
Google Trends Agent - ADK-based A2A Agent
==========================================

This agent analyzes Google Trends data to identify trending topics
that can enhance blog content with SEO insights.

Based on Google ADK patterns from:
- https://github.com/google/adk-samples
- https://google.github.io/adk-docs/

A2A Protocol Implementation:
- Exposes AgentCard at /.well-known/agent.json
- Handles SendMessage at POST /a2a/tasks
- Returns Tasks with trend analysis artifacts
"""

import json
import os
import random
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel

# =============================================================================
# Configuration
# =============================================================================

AGENT_NAME = "google-trends"
AGENT_DESCRIPTION = "Analyzes Google Trends data to identify trending topics for SEO"
AGENT_VERSION = "1.0.0"
PORT = int(os.getenv("PORT", "8083"))
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
# Simulated Trends Data
# =============================================================================

SIMULATED_TRENDS = {
    "artificial intelligence": {
        "interest_over_time": [
            {"date": "2024-01", "value": 75},
            {"date": "2024-02", "value": 82},
            {"date": "2024-03", "value": 88},
            {"date": "2024-04", "value": 91},
            {"date": "2024-05", "value": 95},
            {"date": "2024-06", "value": 100},
        ],
        "related_queries": [
            {"query": "ChatGPT", "value": 100},
            {"query": "Claude AI", "value": 75},
            {"query": "Gemini AI", "value": 68},
            {"query": "AI agents", "value": 55},
            {"query": "LLM reasoning", "value": 42},
        ],
        "regional_interest": [
            {"region": "United States", "value": 100},
            {"region": "United Kingdom", "value": 78},
            {"region": "India", "value": 65},
            {"region": "Germany", "value": 52},
            {"region": "Canada", "value": 48},
        ],
    },
    "cloud computing": {
        "interest_over_time": [
            {"date": "2024-01", "value": 65},
            {"date": "2024-02", "value": 68},
            {"date": "2024-03", "value": 70},
            {"date": "2024-04", "value": 72},
            {"date": "2024-05", "value": 74},
            {"date": "2024-06", "value": 76},
        ],
        "related_queries": [
            {"query": "AWS", "value": 100},
            {"query": "Google Cloud", "value": 65},
            {"query": "Azure", "value": 62},
            {"query": "serverless", "value": 45},
            {"query": "Kubernetes", "value": 40},
        ],
        "regional_interest": [
            {"region": "United States", "value": 100},
            {"region": "India", "value": 82},
            {"region": "United Kingdom", "value": 58},
            {"region": "Germany", "value": 55},
            {"region": "Singapore", "value": 52},
        ],
    },
    "cybersecurity": {
        "interest_over_time": [
            {"date": "2024-01", "value": 55},
            {"date": "2024-02", "value": 62},
            {"date": "2024-03", "value": 68},
            {"date": "2024-04", "value": 75},
            {"date": "2024-05", "value": 80},
            {"date": "2024-06", "value": 85},
        ],
        "related_queries": [
            {"query": "zero trust", "value": 100},
            {"query": "ransomware", "value": 78},
            {"query": "SIEM", "value": 55},
            {"query": "SOC", "value": 48},
            {"query": "threat detection", "value": 42},
        ],
        "regional_interest": [
            {"region": "United States", "value": 100},
            {"region": "Israel", "value": 85},
            {"region": "United Kingdom", "value": 72},
            {"region": "Germany", "value": 65},
            {"region": "Australia", "value": 58},
        ],
    },
    "devops": {
        "interest_over_time": [
            {"date": "2024-01", "value": 58},
            {"date": "2024-02", "value": 60},
            {"date": "2024-03", "value": 62},
            {"date": "2024-04", "value": 65},
            {"date": "2024-05", "value": 68},
            {"date": "2024-06", "value": 70},
        ],
        "related_queries": [
            {"query": "platform engineering", "value": 100},
            {"query": "GitOps", "value": 72},
            {"query": "CI/CD", "value": 68},
            {"query": "infrastructure as code", "value": 55},
            {"query": "terraform", "value": 48},
        ],
        "regional_interest": [
            {"region": "United States", "value": 100},
            {"region": "India", "value": 88},
            {"region": "Germany", "value": 65},
            {"region": "United Kingdom", "value": 62},
            {"region": "Netherlands", "value": 55},
        ],
    },
}


# =============================================================================
# Trends Analysis Logic
# =============================================================================


def generate_task_id() -> str:
    """Generate a unique task ID."""
    import uuid
    return f"task-{uuid.uuid4().hex[:12]}"


async def get_trends_for_topic(topic: str) -> Dict[str, Any]:
    """
    Get Google Trends data for a topic.

    In production, this would:
    1. Query the Google Trends API
    2. Use Gemini to analyze and interpret the data
    3. Generate SEO recommendations
    """
    topic_lower = topic.lower()

    # Find matching simulated data
    trends_data = None
    for key, data in SIMULATED_TRENDS.items():
        if key in topic_lower or topic_lower in key:
            trends_data = data
            break

    # If no match, generate random data
    if not trends_data:
        trends_data = {
            "interest_over_time": [
                {"date": f"2024-0{i}", "value": random.randint(40, 100)}
                for i in range(1, 7)
            ],
            "related_queries": [
                {"query": f"{topic} example {i}", "value": random.randint(20, 100)}
                for i in range(1, 6)
            ],
            "regional_interest": [
                {"region": region, "value": random.randint(30, 100)}
                for region in ["United States", "India", "United Kingdom", "Germany", "Canada"]
            ],
        }

    return {
        "topic": topic,
        **trends_data,
    }


async def analyze_trends(
    topics: List[str],
    timeframe: str = "past_12_months"
) -> Dict[str, Any]:
    """
    Analyze trends for multiple topics and generate insights.
    """
    topic_trends = []
    all_keywords = []

    for topic in topics:
        data = await get_trends_for_topic(topic)
        topic_trends.append(data)

        # Collect related keywords
        for query in data.get("related_queries", []):
            all_keywords.append({
                "keyword": query["query"],
                "score": query["value"],
                "source_topic": topic,
            })

    # Sort keywords by score
    all_keywords.sort(key=lambda x: x["score"], reverse=True)

    # Calculate trend scores
    trend_scores = []
    for trend in topic_trends:
        time_data = trend.get("interest_over_time", [])
        if len(time_data) >= 2:
            # Calculate growth rate
            first_value = time_data[0]["value"]
            last_value = time_data[-1]["value"]
            growth = ((last_value - first_value) / first_value * 100) if first_value > 0 else 0
            trend_scores.append({
                "topic": trend["topic"],
                "current_interest": last_value,
                "growth_rate": round(growth, 1),
                "trend_direction": "rising" if growth > 0 else "falling" if growth < 0 else "stable",
            })

    return {
        "topics_analyzed": len(topics),
        "topic_trends": topic_trends,
        "trend_scores": trend_scores,
        "trending_keywords": [k["keyword"] for k in all_keywords[:10]],
        "all_keywords": all_keywords[:20],
        "seo_recommendations": generate_seo_recommendations(trend_scores, all_keywords),
        "timeframe": timeframe,
        "analyzed_at": datetime.utcnow().isoformat(),
    }


def generate_seo_recommendations(
    trend_scores: List[Dict],
    keywords: List[Dict]
) -> List[Dict[str, Any]]:
    """Generate SEO recommendations based on trend analysis."""
    recommendations = []

    # Find rising topics
    rising_topics = [t for t in trend_scores if t.get("trend_direction") == "rising"]
    if rising_topics:
        top_rising = sorted(rising_topics, key=lambda x: x["growth_rate"], reverse=True)[0]
        recommendations.append({
            "type": "focus_topic",
            "priority": "high",
            "recommendation": f"Focus on {top_rising['topic']} - showing {top_rising['growth_rate']}% growth",
        })

    # Recommend top keywords
    top_keywords = [k["keyword"] for k in keywords[:5]]
    if top_keywords:
        recommendations.append({
            "type": "keywords",
            "priority": "high",
            "recommendation": f"Include these trending keywords: {', '.join(top_keywords)}",
        })

    # Timing recommendation
    recommendations.append({
        "type": "timing",
        "priority": "medium",
        "recommendation": "Publish content during weekday mornings for maximum engagement",
    })

    return recommendations


async def process_trends_request(message_text: str) -> Dict[str, Any]:
    """
    Process a trends analysis request.
    """
    # Extract topics from message
    topics = []

    # Look for common topic indicators
    for keyword in SIMULATED_TRENDS.keys():
        if keyword in message_text.lower():
            topics.append(keyword)

    # Default topics if none found
    if not topics:
        topics = ["artificial intelligence", "cloud computing"]

    # Analyze trends
    analysis = await analyze_trends(topics)

    return analysis


# =============================================================================
# FastAPI Application
# =============================================================================


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    print(f"📈 Google Trends Agent starting on port {PORT}")
    print(f"   AI Mode: {'Enabled' if USE_AI else 'Simulated'}")
    yield
    print("📈 Google Trends Agent shutting down")


app = FastAPI(
    title="Google Trends Agent",
    description="A2A-compatible agent for analyzing Google Trends data",
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
                id="analyze-trends",
                name="Analyze Trends",
                description="Analyze Google Trends data for topics",
                tags=["trends", "analysis", "SEO"],
            ),
            AgentSkill(
                id="get-keywords",
                name="Get Trending Keywords",
                description="Extract trending keywords for content optimization",
                tags=["keywords", "SEO", "content"],
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

    Analyzes trends and returns SEO insights for the Blog Writer Agent.
    """
    task_id = generate_task_id()

    try:
        # Extract message text
        message_text = " ".join(part.text for part in request.message.parts)

        # Process the trends request
        result = await process_trends_request(message_text)

        # Create artifacts
        artifacts = [
            Artifact(
                name="trends-analysis",
                type="application/json",
                data=json.dumps(result),
            ),
            Artifact(
                name="seo-recommendations",
                type="application/json",
                data=json.dumps(result["seo_recommendations"]),
            ),
            Artifact(
                name="trending-keywords",
                type="application/json",
                data=json.dumps(result["trending_keywords"]),
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
                        text=f"Analyzed {result['topics_analyzed']} topics. "
                             f"Top trending keywords: {', '.join(result['trending_keywords'][:3])}"
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
