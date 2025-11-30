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

**IMPORTANT**: This agent uses Gemini/Vertex AI for intelligent trend analysis.
All model interactions are logged and captured as artifacts for debugging.
"""

import json
import os
import random
import sys
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel

# Add shared utilities to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from shared.a2a_utils import parse_llm_json_response, AIUnavailableError, build_ai_unavailable_error_message

# Try to import Gemini AI
try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False
    genai = None

# =============================================================================
# Configuration
# =============================================================================

AGENT_NAME = "google-trends"
AGENT_DESCRIPTION = "Analyzes trends and generates SEO insights using Vertex AI"
AGENT_VERSION = "1.3.0"  # Updated: No fallback - requires Gemini AI
PORT = int(os.getenv("PORT", "8083"))
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")

# Use Gemini API if available
USE_AI = GENAI_AVAILABLE and bool(GEMINI_API_KEY or GOOGLE_API_KEY)

# Request-scoped model interaction log using contextvars for thread safety
from contextvars import ContextVar
_model_interactions: ContextVar[List[Dict[str, Any]]] = ContextVar('model_interactions', default=[])

def log_interaction(interaction_type: str, data: Dict[str, Any]) -> None:
    """Log a model interaction for later retrieval (request-scoped)."""
    safe_data = {k: v for k, v in data.items() if k not in ("api_key", "api_key_prefix")}
    interaction = {
        "type": interaction_type,
        "timestamp": datetime.utcnow().isoformat(),
        "agent": AGENT_NAME,
        **safe_data
    }
    interactions = _model_interactions.get()
    interactions.append(interaction)
    _model_interactions.set(interactions)
    log_preview = {k: (v[:100] + "..." if isinstance(v, str) and len(v) > 100 else v) 
                   for k, v in safe_data.items() if k not in ("prompt_preview", "response_preview")}
    print(f"🤖 [MODEL] {interaction_type}: {json.dumps(log_preview, default=str)[:300]}")

def clear_interactions() -> None:
    """Clear the model interactions log for a new request."""
    _model_interactions.set([])

def get_interactions() -> List[Dict[str, Any]]:
    """Get all model interactions for this request."""
    return _model_interactions.get().copy()

# Configure Gemini if available
if USE_AI and genai:
    api_key = GEMINI_API_KEY or GOOGLE_API_KEY
    genai.configure(api_key=api_key)
    print(f"✅ Gemini AI configured for trends agent with key: {api_key[:8]}...")
else:
    print(f"⚠️ Trends Agent: Gemini AI NOT configured - using simulated data")


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
    Get trends data for a topic using AI analysis.

    REQUIRED: Gemini AI must be configured for this agent to function.
    
    When AI is enabled, uses Gemini to:
    1. Analyze the topic's potential trending keywords
    2. Generate realistic trend data and insights
    3. Provide SEO recommendations
    
    NO FALLBACK: If AI is not available, raises an error.
    """
    if not USE_AI or genai is None:
        error_msg = build_ai_unavailable_error_message(
            genai_available=GENAI_AVAILABLE,
            has_api_key=bool(GEMINI_API_KEY or GOOGLE_API_KEY),
            agent_name=AGENT_NAME
        )
        
        log_interaction("ai_unavailable_error", {
            "error": error_msg,
            "genai_available": GENAI_AVAILABLE,
            "has_api_key": bool(GEMINI_API_KEY or GOOGLE_API_KEY)
        })
        raise AIUnavailableError(error_msg)
    
    return await get_trends_with_ai(topic)


async def get_trends_with_ai(topic: str) -> Dict[str, Any]:
    """
    Use Gemini AI to generate trend analysis for a topic.
    NO FALLBACK: Raises error if AI call fails.
    """
    prompt = f"""Analyze the search trend potential for the topic: "{topic}"

Generate realistic trend data and SEO insights. Return as JSON:
{{
    "topic": "{topic}",
    "interest_over_time": [
        {{"date": "2024-01", "value": 65}},
        {{"date": "2024-02", "value": 70}},
        {{"date": "2024-03", "value": 75}},
        {{"date": "2024-04", "value": 80}},
        {{"date": "2024-05", "value": 85}},
        {{"date": "2024-06", "value": 90}}
    ],
    "related_queries": [
        {{"query": "specific related query 1", "value": 100}},
        {{"query": "specific related query 2", "value": 85}},
        {{"query": "specific related query 3", "value": 70}},
        {{"query": "specific related query 4", "value": 55}},
        {{"query": "specific related query 5", "value": 40}}
    ],
    "regional_interest": [
        {{"region": "United States", "value": 100}},
        {{"region": "United Kingdom", "value": 75}},
        {{"region": "India", "value": 70}},
        {{"region": "Germany", "value": 60}},
        {{"region": "Canada", "value": 55}}
    ]
}}

Make the data realistic based on current 2024-2025 trends.
- Interest values should show a believable trend (rising, falling, or stable)
- Related queries should be REAL, specific search terms people use
- Regional interest should reflect realistic geographic patterns

Return ONLY the JSON, no other text."""

    log_interaction("llm_request", {
        "model": "gemini-1.5-flash",
        "purpose": "trend_analysis",
        "topic": topic,
        "prompt_length": len(prompt)
    })
    
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        start_time = datetime.utcnow()
        response = model.generate_content(
            prompt,
            generation_config=genai.GenerationConfig(
                temperature=0.7,
                max_output_tokens=1024,
            )
        )
        end_time = datetime.utcnow()
        duration_ms = (end_time - start_time).total_seconds() * 1000
        
        if response.text:
            log_interaction("llm_response", {
                "model": "gemini-1.5-flash",
                "status": "success",
                "duration_ms": duration_ms,
                "response_preview": response.text[:400]
            })
            
            # Parse JSON using shared utility
            trends = parse_llm_json_response(response.text)
            if trends:
                print(f"✅ Gemini generated trend data for: {topic}")
                return trends
            else:
                error_msg = f"Failed to parse JSON response from Gemini: {response.text[:200]}"
                log_interaction("parse_error", {
                    "error": "Failed to parse JSON",
                    "topic": topic
                })
                # NO FALLBACK - raise error
                raise AIUnavailableError(error_msg)
        
        # NO FALLBACK - raise error on empty response
        raise AIUnavailableError("Gemini returned empty response for trend analysis")
        
    except AIUnavailableError:
        raise  # Re-raise our custom errors
    except Exception as e:
        log_interaction("llm_error", {
            "error": str(e),
            "topic": topic
        })
        # NO FALLBACK - raise error
        raise AIUnavailableError(f"Gemini API error during trend analysis: {e}")


def get_simulated_trend(topic: str) -> Dict[str, Any]:
    """Return simulated trend data as fallback."""
    topic_lower = topic.lower()
    for key, data in SIMULATED_TRENDS.items():
        if key in topic_lower or topic_lower in key:
            return {"topic": topic, **data}
    
    return {
        "topic": topic,
        "interest_over_time": [
            {"date": f"2024-0{i}", "value": random.randint(50, 90)}
            for i in range(1, 7)
        ],
        "related_queries": [
            {"query": f"{topic} guide", "value": 80},
            {"query": f"{topic} tutorial", "value": 65},
            {"query": f"best {topic}", "value": 55},
        ],
        "regional_interest": [
            {"region": "United States", "value": 100},
            {"region": "India", "value": 75},
        ],
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
    All model interactions are logged and returned as artifacts.
    """
    task_id = generate_task_id()
    
    # Clear previous interactions
    clear_interactions()
    
    # Log task start
    log_interaction("task_start", {
        "task_id": task_id,
        "context_id": request.contextId,
        "message_preview": " ".join(p.text for p in request.message.parts)[:100]
    })

    try:
        # Extract message text
        message_text = " ".join(part.text for part in request.message.parts)

        # Process the trends request
        result = await process_trends_request(message_text)
        
        # Get model interactions
        model_interactions = get_interactions()

        # Create artifacts including model interactions
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
            # NEW: Include model interactions
            Artifact(
                name="model-interactions",
                type="application/json",
                data=json.dumps(model_interactions, default=str),
            ),
        ]
        
        # Log task completion
        log_interaction("task_complete", {
            "task_id": task_id,
            "topics_analyzed": result.get("topics_analyzed", 0),
            "keywords_found": len(result.get("trending_keywords", [])),
            "interactions_count": len(model_interactions)
        })

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
                             f"Top trending keywords: {', '.join(result['trending_keywords'][:3])} "
                             f"(AI: {USE_AI})"
                    )],
                ),
            ),
            artifacts=artifacts,
            referenceTaskIds=request.referenceTaskIds or [],
        )

    except Exception as e:
        # Log error
        log_interaction("task_error", {
            "task_id": task_id,
            "error": str(e)
        })
        
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
