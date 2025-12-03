"""
Image Generator Agent - ADK-based A2A Agent
============================================

This agent generates visual content descriptions and diagram specifications.
Part of the multi-agent team system.

Note: This agent generates descriptions for images/diagrams that can be used
with image generation APIs or SVG generators. It doesn't directly generate
binary images but provides structured specifications.

A2A Protocol Implementation:
- Exposes AgentCard at /.well-known/agent.json
- Handles SendMessage at POST /a2a/tasks
- Returns Tasks with artifacts containing image specifications
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
from shared.a2a_utils import parse_llm_json_response, report_agent_error
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

AGENT_NAME = "image-generator"
AGENT_DESCRIPTION = "Generates visual content descriptions, diagrams, and image specifications"
AGENT_VERSION = "1.0.0"
PORT = int(os.getenv("PORT", "8086"))

USE_AI = gemini_is_available()

if USE_AI:
    config_info = gemini_get_config_info()
    print(f"✅ Gemini AI configured for image generator agent (mode={config_info['active_mode']})")
else:
    print(f"⚠️ Image Generator Agent: Gemini AI NOT configured - will return error")


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


async def generate_visual_spec(prompt: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Generate visual content specification using Gemini AI.
    """
    if not USE_AI:
        raise GeminiUnavailableError(get_unavailable_error_message(agent_name=AGENT_NAME))
    
    context_str = ""
    if context:
        context_str = f"\nAdditional context: {json.dumps(context)}"
    
    ai_prompt = f"""You are an expert visual designer and diagram creator. Create a detailed specification for visual content based on the following request.

Request: {prompt}
{context_str}

Provide your response as a JSON object with this structure:
{{
    "visual_type": "diagram|infographic|chart|illustration|flowchart|architecture",
    "title": "Title for the visual",
    "description": "Brief description of what the visual shows",
    "dimensions": {{
        "width": 800,
        "height": 600,
        "aspect_ratio": "4:3"
    }},
    "color_scheme": {{
        "primary": "#4A90D9",
        "secondary": "#2ECC71",
        "accent": "#E74C3C",
        "background": "#FFFFFF",
        "text": "#333333"
    }},
    "elements": [
        {{
            "type": "shape|text|icon|arrow|connector|image",
            "id": "element-1",
            "properties": {{
                "x": 100,
                "y": 100,
                "width": 200,
                "height": 100,
                "content": "Element content if text",
                "style": "Any specific styling"
            }},
            "connections": ["element-2"]
        }}
    ],
    "layout": {{
        "type": "hierarchical|radial|grid|freeform|flowchart",
        "direction": "top-down|left-right|radial",
        "spacing": 20,
        "alignment": "center"
    }},
    "svg_specification": "A complete SVG code that implements this visual",
    "mermaid_code": "If applicable, Mermaid.js code for the diagram",
    "alt_text": "Accessibility description of the visual",
    "usage_notes": "How and where to use this visual"
}}

For the svg_specification, provide a complete, valid SVG that can be rendered directly.
For diagrams, also provide mermaid_code if appropriate.

Return ONLY the JSON, no other text."""

    try:
        result = await generate_content(
            prompt=ai_prompt,
            temperature=0.7,
            max_output_tokens=8192,
        )
        
        if result["text"]:
            spec = parse_llm_json_response(result["text"])
            if spec:
                return spec
            raise GeminiError(f"Failed to parse visual specification")
        raise GeminiError("Empty response from Gemini")
        
    except (GeminiError, GeminiUnavailableError):
        raise
    except Exception as e:
        raise GeminiError(f"Visual generation failed: {e}")


async def process_image_request(message_text: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Process an image generation request."""
    spec = await generate_visual_spec(message_text, metadata)
    
    return {
        "specification": spec,
        "prompt": message_text,
        "timestamp": datetime.utcnow().isoformat(),
    }


# =============================================================================
# FastAPI Application
# =============================================================================


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    print(f"🎨 Image Generator Agent starting on port {PORT}")
    print(f"   AI Mode: {'Enabled' if USE_AI else 'Disabled'}")
    yield
    print("🎨 Image Generator Agent shutting down")


app = FastAPI(
    title="Image Generator Agent",
    description="A2A-compatible agent for generating visual content specifications",
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
                id="generate-diagram",
                name="Generate Diagram",
                description="Create flowcharts, architecture diagrams, and technical visuals",
                tags=["diagram", "flowchart", "architecture", "technical"],
            ),
            AgentSkill(
                id="create-infographic",
                name="Create Infographic",
                description="Design informative infographics and data visualizations",
                tags=["infographic", "data-viz", "visual"],
            ),
            AgentSkill(
                id="design-illustration",
                name="Design Illustration",
                description="Create illustrations and conceptual visuals",
                tags=["illustration", "concept", "design"],
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
        result = await process_image_request(message_text, request.metadata)
        
        spec = result["specification"]
        visual_type = spec.get("visual_type", "visual")
        title = spec.get("title", "Generated Visual")
        
        artifacts = [
            Artifact(
                name="visual-specification",
                type="application/json",
                data=json.dumps(result),
            ),
        ]
        
        # Add SVG if generated
        if spec.get("svg_specification"):
            artifacts.append(Artifact(
                name="generated-svg",
                type="image/svg+xml",
                data=spec["svg_specification"],
            ))
        
        # Add Mermaid code if generated
        if spec.get("mermaid_code"):
            artifacts.append(Artifact(
                name="mermaid-diagram",
                type="text/plain",
                data=spec["mermaid_code"],
            ))
        
        artifacts.append(Artifact(
            name="visual-summary",
            type="text/markdown",
            data=f"""# Visual Content Generated

**Type:** {visual_type}
**Title:** {title}

## Description
{spec.get('description', 'No description provided')}

## Layout
- Type: {spec.get('layout', {}).get('type', 'freeform')}
- Direction: {spec.get('layout', {}).get('direction', 'top-down')}

## Elements
{len(spec.get('elements', []))} elements created

## Accessibility
{spec.get('alt_text', 'No alt text provided')}

## Usage Notes
{spec.get('usage_notes', 'Use as needed')}
""",
        ))
        
        return Task(
            id=task_id,
            contextId=request.contextId,
            status=TaskStatus(
                state="completed",
                timestamp=datetime.utcnow().isoformat(),
                message=Message(
                    role="agent",
                    parts=[MessagePart(
                        text=f"Visual content generated: {title} ({visual_type}). {len(spec.get('elements', []))} elements created."
                    )],
                ),
            ),
            artifacts=artifacts,
            referenceTaskIds=request.referenceTaskIds or [],
        )
        
    except Exception as e:
        # Report error to error observer
        try:
            await report_agent_error(
                agent_name="image-generator",
                exception=e,
                task_type="agent_task",
            )
        except Exception:
            pass  # Don't block on error reporting failure
        
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
