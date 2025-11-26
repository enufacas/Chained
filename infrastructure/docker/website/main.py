"""
Chained Website - Main Application
==================================
A FastAPI-based website that demonstrates agent-based concepts
and provides a dashboard for monitoring agent activity.
"""

import os
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# Initialize FastAPI app
app = FastAPI(
    title="Chained - Autonomous AI Ecosystem",
    description="Website and dashboard for the Chained autonomous AI system",
    version="1.0.0",
)

# Environment configuration
ENVIRONMENT = os.getenv("ENVIRONMENT", "dev")
AGENT_GATEWAY_URL = os.getenv("AGENT_GATEWAY_URL", "http://localhost:8081")

# Templates directory (create templates/ folder with your HTML files)
# templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def home():
    """
    Home page - Overview of the Chained system.
    """
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Chained - Autonomous AI Ecosystem</title>
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                max-width: 800px;
                margin: 50px auto;
                padding: 20px;
                background: #0d1117;
                color: #c9d1d9;
            }
            h1 { color: #58a6ff; }
            .status { 
                padding: 10px 20px;
                background: #238636;
                color: white;
                border-radius: 6px;
                display: inline-block;
            }
            .card {
                background: #161b22;
                border: 1px solid #30363d;
                border-radius: 6px;
                padding: 20px;
                margin: 20px 0;
            }
            a { color: #58a6ff; }
        </style>
    </head>
    <body>
        <h1>🔗 Chained</h1>
        <p class="status">✅ System Online</p>
        
        <div class="card">
            <h2>🤖 Autonomous AI Ecosystem</h2>
            <p>Chained is a fully autonomous software development ecosystem featuring:</p>
            <ul>
                <li>48+ specialized AI agents with unique personalities</li>
                <li>Autonomous closed-loop pipeline: learning → planning → building → reviewing</li>
                <li>External learning from TLDR, Hacker News, and GitHub Trending</li>
                <li>Self-documenting on GitHub Pages</li>
            </ul>
        </div>
        
        <div class="card">
            <h2>📊 Quick Links</h2>
            <ul>
                <li><a href="/health">Health Check</a></li>
                <li><a href="/api/agents">Active Agents</a></li>
                <li><a href="/api/tasks">Recent Tasks</a></li>
            </ul>
        </div>
        
        <div class="card">
            <h2>⚙️ Environment</h2>
            <p>Environment: <code>""" + ENVIRONMENT + """</code></p>
            <p>Agent Gateway: <code>""" + AGENT_GATEWAY_URL + """</code></p>
        </div>
    </body>
    </html>
    """


@app.get("/health")
async def health():
    """
    Health check endpoint for Cloud Run.
    """
    return {
        "status": "healthy",
        "service": "chained-website",
        "environment": ENVIRONMENT,
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.get("/api/agents")
async def list_agents():
    """
    List active agents (placeholder - integrate with Firestore).
    """
    # TODO: Integrate with Firestore to fetch real agent data
    return {
        "agents": [
            {"name": "investigator", "status": "active", "specialization": "analysis"},
            {"name": "engineer", "status": "active", "specialization": "implementation"},
            {"name": "reviewer", "status": "idle", "specialization": "code-review"},
        ],
        "total": 3,
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.get("/api/tasks")
async def list_tasks():
    """
    List recent tasks (placeholder - integrate with Firestore).
    """
    # TODO: Integrate with Firestore to fetch real task data
    return {
        "tasks": [
            {
                "id": "task-001",
                "type": "analyze",
                "status": "completed",
                "agent": "investigator",
            },
            {
                "id": "task-002",
                "type": "implement",
                "status": "in_progress",
                "agent": "engineer",
            },
        ],
        "total": 2,
        "timestamp": datetime.utcnow().isoformat(),
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
