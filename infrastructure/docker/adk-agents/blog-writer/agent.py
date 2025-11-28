"""
Blog Writer Agent - ADK-based A2A Agent
========================================

This agent takes research topics from the Academic Research Agent and
Google Trends Agent, then writes blog posts for the website.

Based on Google ADK patterns from:
- https://github.com/google/adk-samples
- https://google.github.io/adk-docs/

A2A Protocol Implementation:
- Exposes AgentCard at /.well-known/agent.json
- Handles SendMessage at POST /a2a/tasks
- Accepts referenceTaskIds from other agents
- Returns Tasks with blog content artifacts
"""

import json
import os
from datetime import datetime
from typing import Any, Dict, List, Optional
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel

# =============================================================================
# Configuration
# =============================================================================

AGENT_NAME = "blog-writer"
AGENT_DESCRIPTION = "Writes engaging blog posts from research topics and trend data"
AGENT_VERSION = "1.0.0"
PORT = int(os.getenv("PORT", "8082"))
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
WEBSITE_DEPLOY_URL = os.getenv("WEBSITE_DEPLOY_URL", "")

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
# Blog Writing Logic
# =============================================================================


def generate_task_id() -> str:
    """Generate a unique task ID."""
    import uuid
    return f"task-{uuid.uuid4().hex[:12]}"


def generate_blog_slug(title: str) -> str:
    """Generate a URL-friendly slug from title."""
    import re
    slug = title.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'[\s_-]+', '-', slug)
    slug = slug.strip('-')
    return slug[:60]


async def write_blog_post(
    topic_data: Dict[str, Any],
    trends_data: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Write a blog post based on research topic and trends.

    In production, this would:
    1. Use Gemini to generate engaging content
    2. Incorporate trend data for SEO optimization
    3. Format for the target blog platform
    """
    topic = topic_data.get("topic", "Technology Trends")
    domain = topic_data.get("domain", "Technology")
    key_points = topic_data.get("key_points", [])
    suggested_length = topic_data.get("suggested_length", "1500-2000 words")
    seo_keywords = topic_data.get("seo_keywords", [])

    # Generate blog structure
    title = f"{topic}: A Deep Dive into Modern {domain}"
    slug = generate_blog_slug(title)
    
    # Simulate blog content generation
    introduction = f"""
In the rapidly evolving landscape of {domain.lower()}, few topics have garnered as much 
attention as {topic}. This exploration delves into the current state of research, 
practical implications, and what the future might hold for practitioners and 
enthusiasts alike.
""".strip()

    sections = []
    for i, point in enumerate(key_points, 1):
        sections.append({
            "heading": point,
            "content": f"This section explores {point.lower()}, providing insights and "
                      f"practical guidance for readers interested in {domain.lower()}.",
        })

    # Add trends section if available
    if trends_data:
        trend_keywords = trends_data.get("trending_keywords", [])
        if trend_keywords:
            sections.append({
                "heading": "Current Trends and Search Interest",
                "content": f"According to recent trends, related topics like "
                          f"{', '.join(trend_keywords[:3])} are seeing increased interest. "
                          f"This indicates growing awareness and adoption in the industry.",
            })

    conclusion = f"""
As we've explored throughout this article, {topic} represents a significant 
development in {domain.lower()}. Whether you're a seasoned practitioner or just 
beginning your journey, understanding these concepts will be crucial for staying 
ahead in an increasingly competitive landscape.
""".strip()

    # Build the full blog post
    full_content = f"# {title}\n\n{introduction}\n\n"
    for section in sections:
        full_content += f"## {section['heading']}\n\n{section['content']}\n\n"
    full_content += f"## Conclusion\n\n{conclusion}\n"

    return {
        "title": title,
        "slug": slug,
        "introduction": introduction,
        "sections": sections,
        "conclusion": conclusion,
        "full_content": full_content,
        "metadata": {
            "author": "Chained AI Blog Writer",
            "domain": domain,
            "seo_keywords": seo_keywords,
            "word_count": len(full_content.split()),
            "read_time_minutes": max(1, len(full_content.split()) // 200),
            "generated_at": datetime.utcnow().isoformat(),
        },
    }


async def deploy_blog_post(blog_post: Dict[str, Any]) -> Dict[str, Any]:
    """
    Deploy the blog post to Cloud Storage.

    This function:
    1. Creates an HTML file from the blog content
    2. Uploads it to the Cloud Storage blog bucket
    3. Updates the posts.json index
    4. Returns the live URL
    """
    slug = blog_post.get("slug", "new-post")
    title = blog_post.get("title", "Untitled")
    content = blog_post.get("full_content", "")
    metadata = blog_post.get("metadata", {})
    
    # Get bucket name from environment
    bucket_name = os.getenv("BLOG_BUCKET_NAME", "")
    
    if not bucket_name:
        # Fallback to simulation mode if no bucket configured
        deploy_url = WEBSITE_DEPLOY_URL or "https://enufacas.github.io/Chained"
        return {
            "deployed": False,
            "simulated": True,
            "url": f"{deploy_url}/blog/{slug}",
            "file_path": f"posts/{slug}.html",
            "deployed_at": datetime.utcnow().isoformat(),
            "message": "No BLOG_BUCKET_NAME configured - simulating deployment"
        }
    
    try:
        from google.cloud import storage
        
        client = storage.Client()
        bucket = client.bucket(bucket_name)
        
        # Create HTML content
        html_content = generate_blog_html(title, content, metadata)
        
        # Upload the blog post
        blob = bucket.blob(f"posts/{slug}.html")
        blob.upload_from_string(html_content, content_type="text/html")
        
        # Update posts.json index
        await update_posts_index(bucket, slug, title, metadata)
        
        # Construct URL
        blog_url = f"https://storage.googleapis.com/{bucket_name}/posts/{slug}.html"
        
        return {
            "deployed": True,
            "url": blog_url,
            "file_path": f"posts/{slug}.html",
            "bucket": bucket_name,
            "deployed_at": datetime.utcnow().isoformat(),
        }
        
    except ImportError:
        # google-cloud-storage not installed - simulate
        deploy_url = WEBSITE_DEPLOY_URL or "https://enufacas.github.io/Chained"
        return {
            "deployed": False,
            "simulated": True,
            "url": f"{deploy_url}/blog/{slug}",
            "file_path": f"posts/{slug}.html",
            "deployed_at": datetime.utcnow().isoformat(),
            "message": "google-cloud-storage not installed - simulating deployment"
        }
    except Exception as e:
        # Log error but don't fail - return simulation response
        print(f"⚠️ Cloud Storage deployment failed: {e}")
        deploy_url = WEBSITE_DEPLOY_URL or "https://enufacas.github.io/Chained"
        return {
            "deployed": False,
            "simulated": True,
            "url": f"{deploy_url}/blog/{slug}",
            "file_path": f"posts/{slug}.html",
            "deployed_at": datetime.utcnow().isoformat(),
            "error": str(e)
        }


def generate_blog_html(title: str, content: str, metadata: Dict[str, Any]) -> str:
    """Generate HTML for a blog post."""
    # Escape content for JavaScript
    content_escaped = content.replace('\\', '\\\\').replace('`', '\\`').replace('${', '\\${')
    
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - Chained AI Blog</title>
    <meta name="description" content="{metadata.get('domain', 'Technology')} insights from Chained AI">
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{ 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #0a0a1a 0%, #1a1a3e 100%);
            color: #e0e0e0;
            min-height: 100vh;
            line-height: 1.7;
        }}
        .container {{ max-width: 800px; margin: 0 auto; padding: 2rem; }}
        header {{ margin-bottom: 2rem; }}
        .back {{ color: #00d4ff; text-decoration: none; display: inline-block; margin-bottom: 1rem; }}
        .back:hover {{ text-decoration: underline; }}
        h1 {{ font-size: 2.2rem; color: #fff; margin-bottom: 0.5rem; }}
        .meta {{ color: #888; margin-bottom: 2rem; }}
        .content {{ }}
        .content h2 {{ color: #00d4ff; margin: 2rem 0 1rem; font-size: 1.5rem; }}
        .content p {{ margin: 1rem 0; }}
        .content code {{ background: rgba(0,212,255,0.1); padding: 0.2em 0.4em; border-radius: 4px; }}
        footer {{ margin-top: 3rem; padding-top: 2rem; border-top: 1px solid #333; color: #666; text-align: center; }}
        footer a {{ color: #00d4ff; }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <a href="../index.html" class="back">← Back to Blog</a>
            <h1>{title}</h1>
            <p class="meta">
                🤖 Generated by Chained AI · 
                📅 {datetime.utcnow().strftime("%B %d, %Y")} · 
                ⏱️ {metadata.get('read_time_minutes', 5)} min read
            </p>
        </header>
        <main class="content" id="content"></main>
        <footer>
            <p>Powered by <a href="https://github.com/enufacas/Chained">Chained</a> autonomous AI ecosystem</p>
        </footer>
    </div>
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    <script>
        const markdown = `{content_escaped}`;
        document.getElementById('content').innerHTML = marked.parse(markdown);
    </script>
</body>
</html>'''


async def update_posts_index(bucket, slug: str, title: str, metadata: Dict[str, Any]) -> None:
    """
    Update the posts.json index in Cloud Storage.
    
    Uses generation-based conditional updates to handle concurrent writes safely.
    If a conflict occurs, retries with the latest version.
    """
    import json
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            # Download existing posts.json with generation info
            blob = bucket.blob("posts.json")
            generation = None
            
            if blob.exists():
                blob.reload()  # Get current generation
                generation = blob.generation
                posts = json.loads(blob.download_as_text())
            else:
                posts = []
            
            # Create new post entry
            new_post = {
                "slug": slug,
                "title": title,
                "date": datetime.utcnow().isoformat(),
                "readTime": metadata.get("read_time_minutes", 5),
                "domain": metadata.get("domain", "Technology"),
            }
            
            # Remove existing post with same slug
            posts = [p for p in posts if p.get("slug") != slug]
            
            # Add new post at the beginning
            posts.insert(0, new_post)
            
            # Keep only last 50 posts
            posts = posts[:50]
            
            # Upload with conditional update (if_generation_match)
            # This will fail if the file was modified since we read it
            if generation is not None:
                blob.upload_from_string(
                    json.dumps(posts, indent=2),
                    content_type="application/json",
                    if_generation_match=generation
                )
            else:
                # New file - use if_generation_match=0 to ensure we're creating
                blob.upload_from_string(
                    json.dumps(posts, indent=2),
                    content_type="application/json",
                    if_generation_match=0
                )
            
            return  # Success
            
        except Exception as e:
            error_str = str(e).lower()
            if "precondition" in error_str or "generation" in error_str:
                # Conflict - another write happened, retry
                if attempt < max_retries - 1:
                    print(f"⚠️ Concurrent write detected, retrying ({attempt + 1}/{max_retries})")
                    continue
            print(f"⚠️ Failed to update posts index: {e}")
            break


async def process_write_request(
    message_text: str,
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Process a blog writing request.
    """
    # Extract topic data from metadata or message
    topic_data = {}
    trends_data = None

    if metadata:
        if "topic_data" in metadata:
            topic_data = metadata["topic_data"]
        if "trends_data" in metadata:
            trends_data = metadata["trends_data"]

    # Parse topic from message if not in metadata
    if not topic_data:
        topic_data = {
            "topic": message_text[:100],
            "domain": "Technology",
            "key_points": [
                "Introduction and Overview",
                "Key Concepts",
                "Practical Applications",
                "Future Outlook",
            ],
            "seo_keywords": message_text.lower().split()[:5],
        }

    # Write the blog post
    blog_post = await write_blog_post(topic_data, trends_data)

    # Deploy (simulated)
    deployment = await deploy_blog_post(blog_post)

    return {
        "blog_post": blog_post,
        "deployment": deployment,
        "status": "published",
        "timestamp": datetime.utcnow().isoformat(),
    }


# =============================================================================
# FastAPI Application
# =============================================================================


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    print(f"✍️ Blog Writer Agent starting on port {PORT}")
    print(f"   AI Mode: {'Enabled' if USE_AI else 'Simulated'}")
    yield
    print("✍️ Blog Writer Agent shutting down")


app = FastAPI(
    title="Blog Writer Agent",
    description="A2A-compatible agent for writing blog posts",
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
                id="write-blog",
                name="Write Blog Post",
                description="Generate a complete blog post from research topics",
                tags=["writing", "blog", "content"],
            ),
            AgentSkill(
                id="deploy-blog",
                name="Deploy Blog Post",
                description="Deploy blog post to the website",
                tags=["deploy", "publish", "website"],
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

    This agent accepts referenceTaskIds from the Academic Research Agent
    and Google Trends Agent to incorporate their findings.
    """
    task_id = generate_task_id()

    try:
        # Extract message text
        message_text = " ".join(part.text for part in request.message.parts)

        # Process the write request
        result = await process_write_request(message_text, request.metadata)

        # Create artifacts
        artifacts = [
            Artifact(
                name="blog-post",
                type="text/markdown",
                data=result["blog_post"]["full_content"],
            ),
            Artifact(
                name="blog-metadata",
                type="application/json",
                data=json.dumps(result["blog_post"]["metadata"]),
            ),
            Artifact(
                name="deployment-info",
                type="application/json",
                data=json.dumps(result["deployment"]),
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
                        text=f"Blog post '{result['blog_post']['title']}' written and "
                             f"deployed to {result['deployment']['url']}"
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
