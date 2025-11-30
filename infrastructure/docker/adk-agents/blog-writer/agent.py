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

**IMPORTANT**: This agent uses Gemini/Vertex AI to generate REAL content.
All model interactions are logged and captured as artifacts for debugging.
"""

import json
import os
from datetime import datetime
from typing import Any, Dict, List, Optional
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel

# Try to import Gemini AI - may not be available in all environments
try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False
    genai = None

# =============================================================================
# Configuration
# =============================================================================

AGENT_NAME = "blog-writer"
AGENT_DESCRIPTION = "Writes engaging blog posts from research topics and trend data using Vertex AI"
AGENT_VERSION = "1.2.0"  # Updated version with model interaction logging
PORT = int(os.getenv("PORT", "8082"))
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
WEBSITE_DEPLOY_URL = os.getenv("WEBSITE_DEPLOY_URL", "")

# Use Gemini API if available and genai library is installed
USE_AI = GENAI_AVAILABLE and bool(GEMINI_API_KEY or GOOGLE_API_KEY)

# Request-scoped model interaction log using contextvars for thread safety
from contextvars import ContextVar
_model_interactions: ContextVar[List[Dict[str, Any]]] = ContextVar('model_interactions', default=[])

def log_interaction(interaction_type: str, data: Dict[str, Any]) -> None:
    """Log a model interaction for later retrieval (request-scoped)."""
    # Filter out sensitive data from logs
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
    # Log to stdout for Cloud Run (without full prompt content for security)
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
    print(f"✅ Gemini AI configured")
else:
    print(f"⚠️ Gemini AI NOT configured - USE_AI={USE_AI}, GENAI_AVAILABLE={GENAI_AVAILABLE}")
    if not GENAI_AVAILABLE:
        print("   google-generativeai package not installed")
    if not (GEMINI_API_KEY or GOOGLE_API_KEY):
        print("   No API key found in GEMINI_API_KEY or GOOGLE_API_KEY")


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

    This function:
    1. Uses Gemini to generate engaging content (when USE_AI=True)
    2. Incorporates trend data for SEO optimization
    3. Formats for the target blog platform
    4. Logs all model interactions for debugging
    
    Fallback: Template-based content if Gemini is unavailable.
    """
    topic = topic_data.get("topic", "Technology Trends")
    domain = topic_data.get("domain", "Technology")
    key_points = topic_data.get("key_points", [])
    seo_keywords = topic_data.get("seo_keywords", [])
    
    # Log the write request
    log_interaction("write_request", {
        "topic": topic,
        "domain": domain,
        "key_points_count": len(key_points),
        "seo_keywords": seo_keywords[:5],
        "ai_enabled": USE_AI and genai is not None
    })
    
    # Extract trend keywords if available
    trend_keywords = []
    recommended_focus = topic
    if trends_data:
        trend_keywords = trends_data.get("trending_keywords", [])
        recommended_focus = trends_data.get("recommended_focus", topic)

    # Generate blog title
    title = f"{topic}: A Deep Dive into Modern {domain}"
    slug = generate_blog_slug(title)
    
    # Use Gemini for content generation if available
    content_result = None
    if USE_AI and genai:
        content_result = await generate_content_with_gemini(
            topic=topic,
            domain=domain,
            key_points=key_points,
            seo_keywords=seo_keywords,
            trend_keywords=trend_keywords,
            recommended_focus=recommended_focus
        )
        full_content = content_result["content"]
        
        # Update title from generated content if it has a better one
        if full_content.startswith("# "):
            first_line = full_content.split("\n")[0]
            generated_title = first_line.replace("# ", "").strip()
            if generated_title:
                title = generated_title
                slug = generate_blog_slug(title)
    else:
        # Fallback to template-based content
        log_interaction("fallback_mode", {
            "reason": "Gemini AI not available",
            "use_ai": USE_AI,
            "genai_available": genai is not None
        })
        full_content = generate_template_content(
            topic=topic,
            domain=domain,
            key_points=key_points,
            trends_data=trends_data
        )
        content_result = None

    return {
        "title": title,
        "slug": slug,
        "full_content": full_content,
        "metadata": {
            "author": "Chained AI Blog Writer",
            "domain": domain,
            "seo_keywords": seo_keywords + trend_keywords[:5],
            "word_count": len(full_content.split()),
            "read_time_minutes": max(1, len(full_content.split()) // 200),
            "generated_at": datetime.utcnow().isoformat(),
            "ai_generated": content_result is not None,
        },
        "model_interactions": get_interactions() if content_result else [],
    }


async def generate_content_with_gemini(
    topic: str,
    domain: str,
    key_points: List[str],
    seo_keywords: List[str],
    trend_keywords: List[str],
    recommended_focus: str
) -> Dict[str, Any]:
    """
    Generate blog content using Gemini AI.
    
    This creates comprehensive, well-researched blog content that:
    - Is 1500-2500 words
    - Has proper structure with headers
    - Includes specific examples and data points
    - Is SEO-optimized with relevant keywords
    
    Returns a dict with:
    - content: The generated markdown content
    - model_interactions: List of all LLM calls made
    """
    # Build the comprehensive prompt
    key_points_str = "\n".join(f"- {p}" for p in key_points) if key_points else "- Overview\n- Key Concepts\n- Applications"
    seo_str = ", ".join(seo_keywords[:8]) if seo_keywords else topic
    trends_str = ", ".join(trend_keywords[:8]) if trend_keywords else ""
    
    prompt = f"""Write a comprehensive, engaging, and well-researched blog post about: "{topic}"

## Content Requirements

**Domain/Field:** {domain}
**Primary Focus:** {recommended_focus}

**Key Points to Cover:**
{key_points_str}

**Tone & Style:**
- Professional yet accessible - explain complex concepts clearly
- Use concrete examples and real-world applications
- Include specific data points, statistics, or facts where relevant
- Avoid generic filler content - every paragraph should add value
- Write in an engaging narrative style

**Structure (Target: 1500-2500 words):**

1. **Title** - Create an engaging, SEO-friendly title
2. **Introduction** (200-250 words)
   - Hook the reader with a surprising fact, question, or scenario
   - Clearly state what they'll learn
   - Why this topic matters right now

3. **Background & Context** (300-400 words)
   - Historical context or evolution of the topic
   - Key terminology explained
   - Current landscape overview

4. **Deep Dive: Core Concepts** (500-700 words)
   - 3-4 main concepts explained in detail
   - Use subheadings for each concept
   - Include specific examples for each

5. **Practical Applications** (300-400 words)
   - Real-world use cases
   - Industry examples
   - How readers can apply this knowledge

6. **Future Outlook** (200-300 words)
   - Where is this heading?
   - Expert predictions or emerging trends
   - What to watch for

7. **Conclusion** (150-200 words)
   - Key takeaways (3-5 bullet points)
   - Actionable next steps for readers

**SEO Optimization:**
- Primary keywords: {seo_str}
{f"- Trending keywords to include naturally: {trends_str}" if trends_str else ""}
- Use keywords in headings and throughout the content naturally

**Quality Requirements:**
- NO generic placeholder content like "This is a significant development"
- Include SPECIFIC examples, numbers, and data points
- Make claims concrete and supported
- Write engaging, non-robotic prose

Format the output as Markdown with proper headers (##, ###), bullet points, and formatting.
Start with `# [Your Title Here]` as the first line."""

    # Log the prompt being sent
    log_interaction("llm_request", {
        "model": "gemini-1.5-flash",
        "prompt_length": len(prompt),
        "prompt_preview": prompt[:500] + "..." if len(prompt) > 500 else prompt,
        "topic": topic,
        "generation_config": {
            "temperature": 0.7,
            "top_p": 0.9,
            "max_output_tokens": 4096
        }
    })

    try:
        # Use Gemini 1.5 Flash for fast, quality content
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        start_time = datetime.utcnow()
        response = model.generate_content(
            prompt,
            generation_config=genai.GenerationConfig(
                temperature=0.7,  # Creative but focused
                top_p=0.9,
                max_output_tokens=4096,  # Allow long content
            )
        )
        end_time = datetime.utcnow()
        duration_ms = (end_time - start_time).total_seconds() * 1000
        
        if response.text:
            word_count = len(response.text.split())
            print(f"✅ Gemini generated {word_count} words for: {topic} in {duration_ms:.0f}ms")
            
            # Log the successful response
            # Safely access finish_reason - check both candidates existence and length
            finish_reason = 'unknown'
            if response.candidates and len(response.candidates) > 0:
                finish_reason = getattr(response.candidates[0], 'finish_reason', 'unknown')
            
            log_interaction("llm_response", {
                "model": "gemini-1.5-flash",
                "status": "success",
                "word_count": word_count,
                "response_length": len(response.text),
                "response_preview": response.text[:500] + "..." if len(response.text) > 500 else response.text,
                "duration_ms": duration_ms,
                "finish_reason": finish_reason
            })
            
            return {
                "content": response.text,
                "word_count": word_count,
                "ai_generated": True
            }
        else:
            print(f"⚠️ Gemini returned empty response for: {topic}")
            log_interaction("llm_response", {
                "model": "gemini-1.5-flash",
                "status": "empty_response",
                "duration_ms": duration_ms
            })
            # Fall back to template
            fallback_content = generate_template_content(topic, domain, key_points, {"trending_keywords": trend_keywords})
            return {
                "content": fallback_content,
                "word_count": len(fallback_content.split()),
                "ai_generated": False,
                "fallback_reason": "empty_response"
            }
            
    except Exception as e:
        error_msg = str(e)
        print(f"⚠️ Gemini content generation failed: {error_msg}")
        
        # Log the error
        log_interaction("llm_error", {
            "model": "gemini-1.5-flash",
            "error": error_msg,
            "error_type": type(e).__name__
        })
        
        # Fall back to template content
        fallback_content = generate_template_content(topic, domain, key_points, {"trending_keywords": trend_keywords})
        return {
            "content": fallback_content,
            "word_count": len(fallback_content.split()),
            "ai_generated": False,
            "fallback_reason": f"error: {error_msg}"
        }


def generate_template_content(
    topic: str,
    domain: str,
    key_points: List[str],
    trends_data: Optional[Dict[str, Any]] = None
) -> str:
    """
    Generate template-based content when AI is not available.
    This is the fallback mode that produces shorter, template content.
    """
    title = f"{topic}: A Deep Dive into Modern {domain}"
    
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

    return full_content


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
    """Generate HTML for a blog post with proper XSS protection."""
    import html
    
    # HTML-escape user-controlled values to prevent XSS
    title_escaped = html.escape(title)
    domain_escaped = html.escape(str(metadata.get('domain', 'Technology')))
    read_time = int(metadata.get('read_time_minutes', 5))
    
    # Escape content for JavaScript template literal
    # This goes through marked.js which sanitizes HTML by default
    content_escaped = content.replace('\\', '\\\\').replace('`', '\\`').replace('${', '\\${')
    
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title_escaped} - Chained AI Blog</title>
    <meta name="description" content="{domain_escaped} insights from Chained AI">
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
            <h1>{title_escaped}</h1>
            <p class="meta">
                🤖 Generated by Chained AI · 
                📅 {datetime.utcnow().strftime("%B %d, %Y")} · 
                ⏱️ {read_time} min read
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
    
    All model interactions (LLM calls) are logged and returned as artifacts
    for debugging and transparency.
    """
    task_id = generate_task_id()
    
    # Clear previous interactions for this new request
    clear_interactions()
    
    # Log the incoming request
    log_interaction("task_start", {
        "task_id": task_id,
        "context_id": request.contextId,
        "message_length": sum(len(p.text) for p in request.message.parts),
        "has_metadata": request.metadata is not None,
        "reference_tasks": request.referenceTaskIds or []
    })

    try:
        # Extract message text
        message_text = " ".join(part.text for part in request.message.parts)

        # Process the write request
        result = await process_write_request(message_text, request.metadata)
        
        # Get all model interactions for this request
        model_interactions = get_interactions()

        # Create artifacts including model interactions
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
            # NEW: Include model interactions as an artifact for deep dive
            Artifact(
                name="model-interactions",
                type="application/json",
                data=json.dumps(model_interactions, default=str),
            ),
        ]
        
        # Log task completion
        log_interaction("task_complete", {
            "task_id": task_id,
            "word_count": result["blog_post"]["metadata"].get("word_count", 0),
            "ai_generated": result["blog_post"]["metadata"].get("ai_generated", False),
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
                        text=f"Blog post '{result['blog_post']['title']}' written and "
                             f"deployed to {result['deployment']['url']} "
                             f"({result['blog_post']['metadata'].get('word_count', 0)} words, "
                             f"AI: {result['blog_post']['metadata'].get('ai_generated', False)})"
                    )],
                ),
            ),
            artifacts=artifacts,
            referenceTaskIds=request.referenceTaskIds or [],
        )

    except Exception as e:
        # Log the error
        log_interaction("task_error", {
            "task_id": task_id,
            "error": str(e),
            "error_type": type(e).__name__
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
