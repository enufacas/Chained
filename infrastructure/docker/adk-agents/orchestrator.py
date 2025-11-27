"""
A2A Blog Pipeline Orchestrator
==============================

This orchestrator coordinates the A2A agents in a pipeline:
1. Academic Research Agent discovers topics
2. Google Trends Agent analyzes trends for SEO
3. Blog Writer Agent writes and publishes blog

The orchestrator uses the A2A protocol to communicate with agents.
"""

import asyncio
import json
import os
import sys
from datetime import datetime
from typing import Any, Dict, List, Optional

import httpx


# =============================================================================
# Configuration
# =============================================================================

AGENT_URLS = {
    "academic-research": os.getenv(
        "ACADEMIC_RESEARCH_URL",
        "http://localhost:8081"
    ),
    "blog-writer": os.getenv(
        "BLOG_WRITER_URL",
        "http://localhost:8082"
    ),
    "google-trends": os.getenv(
        "GOOGLE_TRENDS_URL",
        "http://localhost:8083"
    ),
}


# =============================================================================
# A2A Client
# =============================================================================


class A2AClient:
    """Client for A2A agent communication."""

    def __init__(self, base_url: str, timeout: float = 60.0):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    async def get_agent_card(self) -> Dict[str, Any]:
        """Fetch the agent's card."""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(
                f"{self.base_url}/.well-known/agent.json"
            )
            response.raise_for_status()
            return response.json()

    async def send_message(
        self,
        message: str,
        context_id: Optional[str] = None,
        reference_task_ids: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Send a message to the agent and get a task response."""
        payload = {
            "message": {
                "role": "user",
                "parts": [{"text": message}],
            }
        }
        if context_id:
            payload["contextId"] = context_id
        if reference_task_ids:
            payload["referenceTaskIds"] = reference_task_ids
        if metadata:
            payload["metadata"] = metadata

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/a2a/tasks",
                json=payload,
            )
            response.raise_for_status()
            return response.json()

    async def check_health(self) -> Dict[str, Any]:
        """Check agent health status."""
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{self.base_url}/health")
            response.raise_for_status()
            return response.json()


# =============================================================================
# Pipeline Orchestrator
# =============================================================================


class BlogPipelineOrchestrator:
    """Orchestrates the A2A blog writing pipeline."""

    def __init__(self):
        self.clients = {
            name: A2AClient(url)
            for name, url in AGENT_URLS.items()
        }
        self.context_id = f"blog-pipeline-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}"
        self.task_history: List[Dict[str, Any]] = []

    async def check_agents_health(self) -> Dict[str, bool]:
        """Check health of all agents."""
        health_status = {}
        for name, client in self.clients.items():
            try:
                await client.check_health()
                health_status[name] = True
                print(f"✅ {name}: healthy")
            except Exception as e:
                health_status[name] = False
                print(f"❌ {name}: unhealthy - {e}")
        return health_status

    async def discover_agent_cards(self) -> Dict[str, Dict[str, Any]]:
        """Discover all agent cards."""
        cards = {}
        for name, client in self.clients.items():
            try:
                card = await client.get_agent_card()
                cards[name] = card
                print(f"📋 {name}: {card.get('description', 'No description')}")
            except Exception as e:
                print(f"⚠️ Could not get card for {name}: {e}")
        return cards

    async def step_1_research(self, topic_query: Optional[str] = None) -> Dict[str, Any]:
        """Step 1: Discover research topics."""
        print("\n" + "=" * 60)
        print("STEP 1: Academic Research")
        print("=" * 60)

        message = topic_query or "Find trending research topics for a tech blog"

        try:
            result = await self.clients["academic-research"].send_message(
                message=message,
                context_id=self.context_id,
            )
            self.task_history.append(result)

            # Extract findings from artifacts
            findings = None
            for artifact in result.get("artifacts", []):
                if artifact.get("name") == "research-findings":
                    findings = json.loads(artifact.get("data", "{}"))
                    break

            print(f"📚 Found {findings.get('topics_found', 0) if findings else 0} research topics")
            if findings and findings.get("recommended_topic"):
                print(f"   Recommended: {findings['recommended_topic'].get('topic', 'N/A')}")

            return {
                "task": result,
                "findings": findings,
                "task_id": result.get("id"),
            }

        except Exception as e:
            print(f"❌ Research step failed: {e}")
            return {"error": str(e)}

    async def step_2_trends(
        self,
        research_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Step 2: Analyze Google Trends for SEO insights."""
        print("\n" + "=" * 60)
        print("STEP 2: Google Trends Analysis")
        print("=" * 60)

        # Extract topic from research
        topic = "artificial intelligence"  # Default
        if research_result.get("findings"):
            recommended = research_result["findings"].get("recommended_topic", {})
            topic = recommended.get("topic", topic)

        message = f"Analyze trends for: {topic}"
        reference_task_ids = [research_result.get("task_id")] if research_result.get("task_id") else []

        try:
            result = await self.clients["google-trends"].send_message(
                message=message,
                context_id=self.context_id,
                reference_task_ids=reference_task_ids,
            )
            self.task_history.append(result)

            # Extract trends from artifacts
            trends_data = None
            for artifact in result.get("artifacts", []):
                if artifact.get("name") == "trends-analysis":
                    trends_data = json.loads(artifact.get("data", "{}"))
                    break

            if trends_data:
                keywords = trends_data.get("trending_keywords", [])[:3]
                print(f"📈 Analyzed trends for {trends_data.get('topics_analyzed', 0)} topics")
                print(f"   Top keywords: {', '.join(keywords) if keywords else 'None'}")

            return {
                "task": result,
                "trends_data": trends_data,
                "task_id": result.get("id"),
            }

        except Exception as e:
            print(f"❌ Trends analysis failed: {e}")
            return {"error": str(e)}

    async def step_3_write_blog(
        self,
        research_result: Dict[str, Any],
        trends_result: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Step 3: Write and publish the blog post."""
        print("\n" + "=" * 60)
        print("STEP 3: Blog Writing & Publishing")
        print("=" * 60)

        # Prepare topic data
        topic_data = {}
        if research_result.get("findings"):
            topic_data = research_result["findings"].get("recommended_topic", {})

        trends_data = trends_result.get("trends_data")

        # Collect reference task IDs
        reference_task_ids = []
        if research_result.get("task_id"):
            reference_task_ids.append(research_result["task_id"])
        if trends_result.get("task_id"):
            reference_task_ids.append(trends_result["task_id"])

        topic = topic_data.get("topic", "Technology Trends")
        message = f"Write a blog post about: {topic}"

        try:
            result = await self.clients["blog-writer"].send_message(
                message=message,
                context_id=self.context_id,
                reference_task_ids=reference_task_ids,
                metadata={
                    "topic_data": topic_data,
                    "trends_data": trends_data,
                },
            )
            self.task_history.append(result)

            # Extract deployment info
            deployment_info = None
            blog_metadata = None
            for artifact in result.get("artifacts", []):
                if artifact.get("name") == "deployment-info":
                    deployment_info = json.loads(artifact.get("data", "{}"))
                elif artifact.get("name") == "blog-metadata":
                    blog_metadata = json.loads(artifact.get("data", "{}"))

            if deployment_info:
                print(f"📝 Blog post written and deployed!")
                print(f"   URL: {deployment_info.get('url', 'N/A')}")
                if blog_metadata:
                    print(f"   Words: {blog_metadata.get('word_count', 'N/A')}")
                    print(f"   Read time: {blog_metadata.get('read_time_minutes', 'N/A')} min")

            return {
                "task": result,
                "deployment_info": deployment_info,
                "blog_metadata": blog_metadata,
                "task_id": result.get("id"),
            }

        except Exception as e:
            print(f"❌ Blog writing failed: {e}")
            return {"error": str(e)}

    async def run_pipeline(
        self,
        topic_query: Optional[str] = None
    ) -> Dict[str, Any]:
        """Run the complete blog pipeline."""
        print("\n" + "=" * 60)
        print("A2A BLOG PIPELINE ORCHESTRATOR")
        print("=" * 60)
        print(f"Context ID: {self.context_id}")
        print(f"Started at: {datetime.utcnow().isoformat()}")

        # Check agent health
        print("\n🔍 Checking agent health...")
        health = await self.check_agents_health()
        if not all(health.values()):
            unhealthy = [k for k, v in health.items() if not v]
            return {
                "success": False,
                "error": f"Unhealthy agents: {unhealthy}",
            }

        # Discover agent cards
        print("\n📋 Discovering agent capabilities...")
        cards = await self.discover_agent_cards()

        # Step 1: Research
        research_result = await self.step_1_research(topic_query)
        if research_result.get("error"):
            return {
                "success": False,
                "error": research_result["error"],
                "step": "research",
            }

        # Step 2: Trends
        trends_result = await self.step_2_trends(research_result)
        if trends_result.get("error"):
            # Continue even if trends fail
            print("⚠️ Continuing without trends data")
            trends_result = {"trends_data": None}

        # Step 3: Write Blog
        blog_result = await self.step_3_write_blog(research_result, trends_result)
        if blog_result.get("error"):
            return {
                "success": False,
                "error": blog_result["error"],
                "step": "blog_writing",
            }

        # Summary
        print("\n" + "=" * 60)
        print("PIPELINE COMPLETE")
        print("=" * 60)
        print(f"✅ Context ID: {self.context_id}")
        print(f"✅ Tasks completed: {len(self.task_history)}")
        if blog_result.get("deployment_info"):
            print(f"✅ Blog URL: {blog_result['deployment_info'].get('url', 'N/A')}")

        return {
            "success": True,
            "context_id": self.context_id,
            "tasks_completed": len(self.task_history),
            "research": research_result,
            "trends": trends_result,
            "blog": blog_result,
            "completed_at": datetime.utcnow().isoformat(),
        }


# =============================================================================
# Main Entry Point
# =============================================================================


async def main():
    """Run the blog pipeline."""
    topic_query = None
    if len(sys.argv) > 1:
        topic_query = " ".join(sys.argv[1:])

    orchestrator = BlogPipelineOrchestrator()
    result = await orchestrator.run_pipeline(topic_query)

    # Write result to file for workflow consumption
    output_file = os.getenv("OUTPUT_FILE", "pipeline_result.json")
    with open(output_file, "w") as f:
        json.dump(result, f, indent=2)

    print(f"\n📄 Result written to: {output_file}")

    # Exit with appropriate code
    sys.exit(0 if result.get("success") else 1)


if __name__ == "__main__":
    asyncio.run(main())
