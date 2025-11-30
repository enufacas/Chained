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

**IMPORTANT**: This agent uses Gemini/Vertex AI for intelligent topic discovery.
All model interactions are logged and captured as artifacts for debugging.
"""

import json
import os
import random
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
from shared.a2a_utils import parse_llm_json_response

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

AGENT_NAME = "academic-research"
AGENT_DESCRIPTION = "Discovers and analyzes academic research topics using Vertex AI"
AGENT_VERSION = "1.2.0"  # Updated with AI-powered research
PORT = int(os.getenv("PORT", "8081"))
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
    print(f"✅ Gemini AI configured for research agent with key: {api_key[:8]}...")
else:
    print(f"⚠️ Research Agent: Gemini AI NOT configured - using simulated data")


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
    Discover research topics based on query using Gemini AI.

    When AI is enabled:
    1. Use Gemini to generate relevant research topics
    2. Get detailed analysis and key points
    3. Score topics for blog relevance
    
    Fallback: Use simulated data if AI is not available.
    """
    if USE_AI and genai:
        return await discover_topics_with_ai(query, max_topics)
    
    # Fallback to simulated data
    log_interaction("fallback_discovery", {
        "reason": "AI not available",
        "query": query
    })
    
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


async def discover_topics_with_ai(
    query: Optional[str] = None,
    max_topics: int = 3
) -> List[Dict[str, Any]]:
    """
    Use Gemini AI to discover and analyze research topics.
    """
    topic_query = query or "latest trends in technology and AI"
    
    prompt = f"""You are a research analyst specializing in technology trends.
Identify {max_topics} compelling research topics related to: "{topic_query}"

For each topic, provide:
1. A specific, focused title (not generic)
2. A brief abstract (2-3 sentences)
3. 4-5 relevant keywords
4. The domain/field it belongs to
5. A relevance score (0.0-1.0) for blog writing potential

Return the response as a JSON array with this exact structure:
[
  {{
    "title": "Specific Topic Title",
    "abstract": "Brief description of the topic and its significance.",
    "keywords": ["keyword1", "keyword2", "keyword3"],
    "domain": "Domain Name",
    "relevance_score": 0.95
  }}
]

Focus on:
- Current, trending topics (2024-2025)
- Topics with practical applications
- Areas with recent breakthroughs or developments
- Topics that would interest tech professionals

Return ONLY the JSON array, no other text."""

    # Log the LLM request
    log_interaction("llm_request", {
        "model": "gemini-1.5-flash",
        "purpose": "topic_discovery",
        "query": topic_query,
        "prompt_length": len(prompt),
        "prompt_preview": prompt[:400] + "..."
    })
    
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        start_time = datetime.utcnow()
        response = model.generate_content(
            prompt,
            generation_config=genai.GenerationConfig(
                temperature=0.7,
                max_output_tokens=2048,
            )
        )
        end_time = datetime.utcnow()
        duration_ms = (end_time - start_time).total_seconds() * 1000
        
        if response.text:
            # Log successful response
            log_interaction("llm_response", {
                "model": "gemini-1.5-flash",
                "status": "success",
                "response_length": len(response.text),
                "duration_ms": duration_ms,
                "response_preview": response.text[:500] + "..." if len(response.text) > 500 else response.text
            })
            
            # Parse the JSON response using shared utility
            topics = parse_llm_json_response(response.text)
            if topics:
                print(f"✅ Gemini discovered {len(topics)} research topics")
                return topics[:max_topics]
            else:
                log_interaction("parse_error", {
                    "error": "Failed to parse JSON",
                    "raw_response": response.text[:200]
                })
                # Fall back to simulated data
                return get_simulated_topics(query, max_topics)
        else:
            log_interaction("llm_response", {
                "model": "gemini-1.5-flash",
                "status": "empty_response",
                "duration_ms": duration_ms
            })
            return get_simulated_topics(query, max_topics)
            
    except Exception as e:
        log_interaction("llm_error", {
            "model": "gemini-1.5-flash",
            "error": str(e),
            "error_type": type(e).__name__
        })
        print(f"⚠️ Gemini topic discovery failed: {e}")
        return get_simulated_topics(query, max_topics)


def get_simulated_topics(query: Optional[str], max_topics: int) -> List[Dict[str, Any]]:
    """Return simulated topics as fallback."""
    all_topics = []
    for domain in RESEARCH_DOMAINS:
        for topic in domain["topics"]:
            all_topics.append({**topic, "domain": domain["domain"]})
    
    if query:
        query_lower = query.lower()
        filtered = [
            t for t in all_topics
            if query_lower in t["title"].lower()
            or query_lower in t["abstract"].lower()
        ]
        if filtered:
            all_topics = filtered
    
    all_topics.sort(key=lambda x: x["relevance_score"], reverse=True)
    return all_topics[:max_topics]


async def analyze_topic_for_blog(topic: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyze a research topic and generate blog writing suggestions using AI.

    Uses Gemini to:
    1. Summarize the research in accessible language
    2. Identify key insights for general audience
    3. Suggest blog angles and structure
    """
    if USE_AI and genai:
        return await analyze_topic_with_ai(topic)
    
    # Fallback to template-based analysis
    return {
        "topic": topic["title"],
        "domain": topic.get("domain", "Technology"),
        "blog_angle": f"How {topic['title']} is changing the industry",
        "key_points": [
            f"Introduction to {topic.get('keywords', ['the topic'])[0]}",
            "Current state of research",
            "Practical implications for practitioners",
            "Future directions and predictions",
        ],
        "target_audience": "Tech professionals and enthusiasts",
        "suggested_length": "1500-2000 words",
        "seo_keywords": topic.get("keywords", []),
    }


async def analyze_topic_with_ai(topic: Dict[str, Any]) -> Dict[str, Any]:
    """Use Gemini to analyze a topic for blog writing."""
    prompt = f"""Analyze this research topic for a tech blog post:

Topic: {topic.get('title', 'Unknown')}
Domain: {topic.get('domain', 'Technology')}
Abstract: {topic.get('abstract', 'No abstract available')}

Generate a comprehensive blog writing plan. Return as JSON:
{{
    "topic": "The exact topic title",
    "domain": "The field/domain",
    "blog_angle": "A unique, engaging angle for the blog post",
    "key_points": [
        "Specific point 1 to cover",
        "Specific point 2 to cover",
        "Specific point 3 to cover",
        "Specific point 4 to cover"
    ],
    "target_audience": "Who this is for",
    "suggested_length": "Word count recommendation",
    "seo_keywords": ["keyword1", "keyword2", "keyword3", "keyword4", "keyword5"]
}}

Make the blog_angle creative and specific, not generic.
Key points should be actionable and detailed.
Return ONLY the JSON, no other text."""

    log_interaction("llm_request", {
        "model": "gemini-1.5-flash",
        "purpose": "topic_analysis",
        "topic": topic.get("title"),
        "prompt_length": len(prompt)
    })
    
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        start_time = datetime.utcnow()
        response = model.generate_content(
            prompt,
            generation_config=genai.GenerationConfig(
                temperature=0.6,
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
                "response_preview": response.text[:300]
            })
            
            # Parse JSON using shared utility
            analysis = parse_llm_json_response(response.text)
            if analysis:
                return analysis
        
        # Fallback
        return {
            "topic": topic["title"],
            "domain": topic.get("domain", "Technology"),
            "blog_angle": f"How {topic['title']} is changing the industry",
            "key_points": topic.get("keywords", ["Overview"]),
            "target_audience": "Tech professionals",
            "suggested_length": "1500-2000 words",
            "seo_keywords": topic.get("keywords", []),
        }
        
    except Exception as e:
        log_interaction("llm_error", {
            "error": str(e),
            "topic": topic.get("title")
        })
        return {
            "topic": topic["title"],
            "domain": topic.get("domain", "Technology"),
            "blog_angle": f"Understanding {topic['title']}",
            "key_points": ["Overview", "Key concepts", "Applications", "Future outlook"],
            "target_audience": "Tech professionals",
            "suggested_length": "1500-2000 words",
            "seo_keywords": topic.get("keywords", []),
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

        # Process the research request
        result = await process_research_request(message_text)
        
        # Get model interactions
        model_interactions = get_interactions()

        # Create artifacts including model interactions
        artifacts = [
            Artifact(
                name="research-findings",
                type="application/json",
                data=json.dumps(result),
            ),
            Artifact(
                name="recommended-topic",
                type="application/json",
                data=json.dumps(result.get("recommended_topic", {})),
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
            "topics_found": result.get("topics_found", 0),
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
