"""
Data Analyst Agent - ADK-based A2A Agent
=========================================

This agent analyzes data and generates insights, statistics, and visualizations.
Part of the multi-agent team system.

A2A Protocol Implementation:
- Exposes AgentCard at /.well-known/agent.json
- Handles SendMessage at POST /a2a/tasks
- Returns Tasks with artifacts containing data analysis
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

AGENT_NAME = "data-analyst"
AGENT_DESCRIPTION = "Analyzes data, generates insights, and provides statistical summaries"
AGENT_VERSION = "1.0.0"
PORT = int(os.getenv("PORT", "8085"))

USE_AI = gemini_is_available()

if USE_AI:
    config_info = gemini_get_config_info()
    print(f"✅ Gemini AI configured for data analyst agent (mode={config_info['active_mode']})")
else:
    print(f"⚠️ Data Analyst Agent: Gemini AI NOT configured - will return error")


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
    metadata: Optional[Dict[str, Any]] = None


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


async def analyze_data(data: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Analyze data using Gemini AI.
    """
    if not USE_AI:
        raise GeminiUnavailableError(get_unavailable_error_message(agent_name=AGENT_NAME))
    
    context_str = ""
    if context:
        context_str = f"\nAdditional context: {json.dumps(context)}"
    
    prompt = f"""You are an expert data analyst. Analyze the following data/information and provide comprehensive insights.

Data to analyze:
{data}
{context_str}

Provide your analysis as a JSON object with this structure:
{{
    "data_type": "The type of data analyzed (text, numerical, categorical, mixed)",
    "summary": "Executive summary of the analysis (2-3 sentences)",
    "key_findings": [
        {{
            "finding": "Key insight discovered",
            "significance": "high|medium|low",
            "evidence": "Supporting data/evidence"
        }}
    ],
    "statistics": {{
        "total_items": 0,
        "categories_found": [],
        "trends_identified": [],
        "outliers": []
    }},
    "patterns": [
        {{
            "pattern": "Pattern description",
            "frequency": "How often it occurs",
            "implications": "What this means"
        }}
    ],
    "recommendations": [
        {{
            "recommendation": "Actionable suggestion",
            "priority": "high|medium|low",
            "expected_impact": "What improvement to expect"
        }}
    ],
    "visualization_suggestions": [
        {{
            "chart_type": "bar|line|pie|scatter|heatmap",
            "purpose": "What this would show",
            "data_points": "Which data to use"
        }}
    ],
    "confidence_score": 85,
    "limitations": ["Any caveats or limitations of this analysis"]
}}

Return ONLY the JSON, no other text."""

    try:
        result = await generate_content(
            prompt=prompt,
            temperature=0.4,
            max_output_tokens=4096,
        )
        
        if result["text"]:
            analysis = parse_llm_json_response(result["text"])
            if analysis:
                return analysis
            raise GeminiError(f"Failed to parse analysis response")
        raise GeminiError("Empty response from Gemini")
        
    except (GeminiError, GeminiUnavailableError):
        raise
    except Exception as e:
        raise GeminiError(f"Data analysis failed: {e}")


async def process_analysis_request(message_text: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Process a data analysis request."""
    analysis = await analyze_data(message_text, metadata)
    
    return {
        "analysis": analysis,
        "input_length": len(message_text),
        "timestamp": datetime.utcnow().isoformat(),
    }


# =============================================================================
# FastAPI Application
# =============================================================================


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    print(f"📊 Data Analyst Agent starting on port {PORT}")
    print(f"   AI Mode: {'Enabled' if USE_AI else 'Disabled'}")
    yield
    print("📊 Data Analyst Agent shutting down")


app = FastAPI(
    title="Data Analyst Agent",
    description="A2A-compatible agent for data analysis and insights",
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
                id="analyze-data",
                name="Analyze Data",
                description="Perform comprehensive data analysis and generate insights",
                tags=["data", "analysis", "insights", "statistics"],
            ),
            AgentSkill(
                id="identify-patterns",
                name="Identify Patterns",
                description="Discover patterns and trends in data",
                tags=["patterns", "trends", "discovery"],
            ),
            AgentSkill(
                id="generate-recommendations",
                name="Generate Recommendations",
                description="Provide data-driven recommendations",
                tags=["recommendations", "actionable", "insights"],
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
        result = await process_analysis_request(message_text, request.metadata)
        
        analysis = result["analysis"]
        summary = analysis.get("summary", "Analysis completed")
        findings_count = len(analysis.get("key_findings", []))
        confidence = analysis.get("confidence_score", 0)
        
        artifacts = [
            Artifact(
                name="data-analysis",
                type="application/json",
                data=json.dumps(result),
            ),
            Artifact(
                name="analysis-summary",
                type="text/markdown",
                data=f"""# Data Analysis Summary

**Confidence Score:** {confidence}%

## Executive Summary
{summary}

## Key Findings
{findings_count} key findings identified

### Top Findings:
{chr(10).join(['- ' + f.get('finding', '') for f in analysis.get('key_findings', [])[:3]])}

## Recommendations
{len(analysis.get('recommendations', []))} recommendations provided

## Visualization Suggestions
{len(analysis.get('visualization_suggestions', []))} chart types recommended
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
                        text=f"Data analysis completed. Found {findings_count} key insights with {confidence}% confidence."
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
