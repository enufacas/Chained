#!/usr/bin/env python3
"""
ADK A2A Blog Pipeline Dashboard
================================

@create-botter's visionary monitoring dashboard for the ADK A2A pipeline.
Provides real-time status, health checks, and historical analytics.

Inspired by Nikola Tesla - elegant, powerful, and innovative.
"""

import argparse
import asyncio
import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

try:
    import httpx
except ImportError:
    print("⚠️  httpx not installed. Install with: pip install httpx")
    sys.exit(1)


# =============================================================================
# Configuration
# =============================================================================

REPO_ROOT = Path(__file__).parent.parent
ADK_AGENTS_PATH = REPO_ROOT / "infrastructure" / "docker" / "adk-agents"

# Agent configuration
AGENTS = {
    "academic-research": {
        "name": "Academic Research Agent",
        "emoji": "🔬",
        "port": 8081,
        "url_env": "ACADEMIC_RESEARCH_URL",
    },
    "google-trends": {
        "name": "Google Trends Agent",
        "emoji": "📈",
        "port": 8083,
        "url_env": "GOOGLE_TRENDS_URL",
    },
    "blog-writer": {
        "name": "Blog Writer Agent",
        "emoji": "✍️",
        "port": 8082,
        "url_env": "BLOG_WRITER_URL",
    },
}


# =============================================================================
# Agent Health Checker
# =============================================================================


class AgentHealthChecker:
    """Check health of A2A agents."""

    def __init__(self, timeout: float = 10.0):
        self.timeout = timeout

    def _get_agent_url(self, agent_id: str) -> str:
        """Get agent URL from environment or default."""
        agent_config = AGENTS[agent_id]
        return os.getenv(
            agent_config["url_env"],
            f"http://localhost:{agent_config['port']}"
        )

    async def check_agent_health(self, agent_id: str) -> Dict:
        """Check health of a single agent."""
        url = self._get_agent_url(agent_id)
        agent_config = AGENTS[agent_id]
        
        result = {
            "agent_id": agent_id,
            "name": agent_config["name"],
            "emoji": agent_config["emoji"],
            "url": url,
            "healthy": False,
            "response_time_ms": None,
            "error": None,
            "agent_card": None,
        }

        try:
            start = datetime.now()
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # Check health endpoint
                health_response = await client.get(f"{url}/health")
                health_response.raise_for_status()
                
                # Get agent card
                card_response = await client.get(f"{url}/.well-known/agent.json")
                card_response.raise_for_status()
                
                end = datetime.now()
                
                result["healthy"] = True
                result["response_time_ms"] = (end - start).total_seconds() * 1000
                result["agent_card"] = card_response.json()
                
        except httpx.TimeoutException:
            result["error"] = "Timeout"
        except httpx.HTTPError as e:
            result["error"] = f"HTTP Error: {e}"
        except Exception as e:
            result["error"] = f"Error: {e}"

        return result

    async def check_all_agents(self) -> Dict[str, Dict]:
        """Check health of all agents."""
        tasks = [
            self.check_agent_health(agent_id)
            for agent_id in AGENTS.keys()
        ]
        results = await asyncio.gather(*tasks)
        return {r["agent_id"]: r for r in results}


# =============================================================================
# Pipeline Status Analyzer
# =============================================================================


class PipelineStatusAnalyzer:
    """Analyze pipeline execution history."""

    def __init__(self, issue_number: Optional[int] = None):
        self.issue_number = issue_number

    def get_tracking_issue_number(self) -> Optional[int]:
        """Get tracking issue number from GitHub."""
        if self.issue_number:
            return self.issue_number
        
        # Try to find issue via gh CLI
        try:
            import subprocess
            result = subprocess.run(
                ["gh", "issue", "list", "--label", "adk-pipeline", 
                 "--state", "open", "--limit", "1", "--json", "number"],
                capture_output=True,
                text=True,
                check=False
            )
            if result.returncode == 0:
                data = json.loads(result.stdout)
                if data and len(data) > 0:
                    return data[0]["number"]
        except Exception:
            pass
        
        return None

    def analyze_recent_runs(self, limit: int = 10) -> Dict:
        """Analyze recent pipeline runs."""
        issue_number = self.get_tracking_issue_number()
        
        if not issue_number:
            return {
                "error": "Could not find tracking issue",
                "issue_number": None,
            }

        try:
            import subprocess
            result = subprocess.run(
                ["gh", "issue", "view", str(issue_number), 
                 "--json", "comments", "--jq", ".comments[]"],
                capture_output=True,
                text=True,
                check=False
            )
            
            if result.returncode != 0:
                return {
                    "error": f"Failed to fetch issue comments: {result.stderr}",
                    "issue_number": issue_number,
                }

            # Parse comments
            comments = []
            for line in result.stdout.strip().split("\n"):
                if line:
                    try:
                        comments.append(json.loads(line))
                    except json.JSONDecodeError:
                        pass

            # Analyze runs
            recent_runs = []
            for comment in comments[-limit:]:
                body = comment.get("body", "")
                if "Pipeline Run:" in body:
                    recent_runs.append({
                        "created_at": comment.get("createdAt"),
                        "author": comment.get("author", {}).get("login"),
                        "body": body,
                    })

            return {
                "issue_number": issue_number,
                "total_runs": len(recent_runs),
                "recent_runs": recent_runs,
            }

        except Exception as e:
            return {
                "error": f"Failed to analyze runs: {e}",
                "issue_number": issue_number,
            }


# =============================================================================
# Dashboard Display
# =============================================================================


class Dashboard:
    """Display pipeline dashboard."""

    @staticmethod
    def print_header(title: str):
        """Print section header."""
        print()
        print("=" * 80)
        print(f"  {title}")
        print("=" * 80)
        print()

    @staticmethod
    def print_agent_health(health_results: Dict[str, Dict]):
        """Print agent health status."""
        Dashboard.print_header("🏥 Agent Health Status")
        
        all_healthy = all(r["healthy"] for r in health_results.values())
        
        if all_healthy:
            print("✅ All agents are healthy and operational!")
        else:
            print("⚠️  Some agents are not responding")
        
        print()
        
        for agent_id, result in health_results.items():
            emoji = result["emoji"]
            name = result["name"]
            status = "✅ HEALTHY" if result["healthy"] else "❌ UNHEALTHY"
            
            print(f"{emoji} {name}")
            print(f"   URL: {result['url']}")
            print(f"   Status: {status}")
            
            if result["healthy"]:
                print(f"   Response Time: {result['response_time_ms']:.0f}ms")
                if result["agent_card"]:
                    card = result["agent_card"]
                    print(f"   Version: {card.get('version', 'N/A')}")
                    skills = card.get("skills", [])
                    if skills:
                        skill_names = [s.get("name", "unknown") for s in skills]
                        print(f"   Skills: {', '.join(skill_names)}")
            else:
                print(f"   Error: {result['error']}")
            
            print()

    @staticmethod
    def print_pipeline_status(status_data: Dict):
        """Print pipeline execution status."""
        Dashboard.print_header("📊 Pipeline Execution Status")
        
        if "error" in status_data:
            print(f"❌ {status_data['error']}")
            return
        
        issue_number = status_data.get("issue_number")
        total_runs = status_data.get("total_runs", 0)
        
        print(f"📋 Tracking Issue: #{issue_number}")
        print(f"🔄 Total Runs Analyzed: {total_runs}")
        print()
        
        recent_runs = status_data.get("recent_runs", [])
        if recent_runs:
            print("Recent Pipeline Runs:")
            print()
            for i, run in enumerate(reversed(recent_runs[-5:]), 1):
                created = run["created_at"]
                print(f"  {i}. Run at {created}")
                # Parse run details from body
                body = run["body"]
                if "Mode |" in body:
                    # Extract mode
                    for line in body.split("\n"):
                        if "| Mode |" in line:
                            mode = line.split("|")[2].strip()
                            print(f"     Mode: {mode}")
                            break
                print()
        else:
            print("No recent runs found.")

    @staticmethod
    def print_summary(health_results: Dict[str, Dict], status_data: Dict):
        """Print dashboard summary."""
        Dashboard.print_header("📈 Dashboard Summary")
        
        # Agent health summary
        healthy_count = sum(1 for r in health_results.values() if r["healthy"])
        total_count = len(health_results)
        health_pct = (healthy_count / total_count * 100) if total_count > 0 else 0
        
        print(f"🏥 Agent Health: {healthy_count}/{total_count} healthy ({health_pct:.0f}%)")
        
        # Pipeline summary
        if "total_runs" in status_data:
            print(f"📊 Pipeline Runs: {status_data['total_runs']} tracked")
        
        print()
        print("✨ Powered by @create-botter - Visionary Infrastructure")


# =============================================================================
# CLI
# =============================================================================


async def main():
    parser = argparse.ArgumentParser(
        description="ADK A2A Blog Pipeline Dashboard",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Check agent health
  %(prog)s health
  
  # View pipeline status
  %(prog)s status
  
  # Full dashboard
  %(prog)s dashboard
  
  # Quick check
  %(prog)s check
        """
    )
    
    parser.add_argument(
        "command",
        choices=["health", "status", "dashboard", "check"],
        help="Command to execute"
    )
    
    parser.add_argument(
        "--issue",
        type=int,
        help="Tracking issue number (auto-detected if not provided)"
    )
    
    parser.add_argument(
        "--timeout",
        type=float,
        default=10.0,
        help="Timeout for agent health checks (default: 10s)"
    )
    
    args = parser.parse_args()
    
    # Initialize components
    health_checker = AgentHealthChecker(timeout=args.timeout)
    status_analyzer = PipelineStatusAnalyzer(issue_number=args.issue)
    
    # Execute command
    if args.command in ["health", "dashboard", "check"]:
        print("🔍 Checking agent health...")
        health_results = await health_checker.check_all_agents()
        Dashboard.print_agent_health(health_results)
    
    if args.command in ["status", "dashboard"]:
        print("📊 Analyzing pipeline status...")
        status_data = status_analyzer.analyze_recent_runs()
        Dashboard.print_pipeline_status(status_data)
    
    if args.command == "dashboard":
        Dashboard.print_summary(health_results, status_data)
    
    if args.command == "check":
        # Quick check - just show if all healthy
        all_healthy = all(r["healthy"] for r in health_results.values())
        if all_healthy:
            print("\n✅ All systems operational!")
            return 0
        else:
            print("\n⚠️  Some agents are not responding")
            return 1


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code or 0)
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        sys.exit(1)
