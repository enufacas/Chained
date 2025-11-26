"""
GitHub-based transport layer for A2A protocol.

This module implements A2A communication using GitHub Issues and Comments
as a message bus, enabling cross-runner agent communication within the
constraints of GitHub Actions.
"""

import json
import time
import asyncio
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime

import httpx


@dataclass
class GitHubA2ATask:
    """Represents an A2A task tracked via GitHub issue."""
    issue_number: int
    agent_name: str
    message: Dict[str, Any]
    status: str  # "submitted", "working", "completed", "failed"
    created_at: str
    result: Optional[Dict[str, Any]] = None


class GitHubA2ATransport:
    """
    A2A transport layer using GitHub Issues as message bus.
    
    This enables cross-runner agent communication by using GitHub Issues
    for task delegation and Comments for responses.
    
    Architecture:
    - Task submission → Create GitHub Issue with A2A payload
    - Task execution → Workflow triggered by issue creation
    - Task completion → Comment with result + label update
    - Task monitoring → Poll issue labels and comments
    """
    
    def __init__(
        self,
        github_token: str,
        repo_owner: str,
        repo_name: str,
    ):
        """
        Initialize GitHub transport.
        
        Args:
            github_token: GitHub token with repo access
            repo_owner: Repository owner
            repo_name: Repository name
        """
        self.github_token = github_token
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        self.base_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}"
        
        self.client = httpx.AsyncClient(
            headers={
                "Authorization": f"token {github_token}",
                "Accept": "application/vnd.github.v3+json",
            },
            timeout=30.0,
        )
    
    async def close(self):
        """Close HTTP client."""
        await self.client.aclose()
    
    async def create_task(
        self,
        agent_name: str,
        message: Dict[str, Any],
        priority: str = "normal",
    ) -> GitHubA2ATask:
        """
        Create a new A2A task via GitHub issue.
        
        Args:
            agent_name: Target agent name
            message: A2A message payload (JSON-RPC format)
            priority: Task priority (normal, high, critical)
            
        Returns:
            GitHubA2ATask object
        """
        # Prepare issue payload
        issue_title = f"🤖 A2A Task for @{agent_name}"
        
        # Format issue body with A2A payload
        issue_body = f"""## A2A Protocol Task

**Target Agent:** `@{agent_name}`  
**Created:** {datetime.utcnow().isoformat()}Z  
**Priority:** {priority}

### Message Payload

```json
{json.dumps(message, indent=2)}
```

### Status

- [ ] Task submitted
- [ ] Agent acknowledged
- [ ] Task completed

---
*This issue was created by the A2A protocol transport layer*
"""
        
        # Determine labels
        labels = [
            "a2a-task",
            f"agent:{agent_name}",
            "status:submitted",
            f"priority:{priority}",
        ]
        
        # Create issue
        response = await self.client.post(
            f"{self.base_url}/issues",
            json={
                "title": issue_title,
                "body": issue_body,
                "labels": labels,
            }
        )
        response.raise_for_status()
        
        issue_data = response.json()
        issue_number = issue_data["number"]
        
        # Trigger workflow if possible (workflow_dispatch)
        # Note: This requires separate workflow setup
        try:
            await self._trigger_agent_workflow(agent_name, issue_number)
        except Exception:
            # Workflow trigger is optional - agent can also poll for issues
            pass
        
        return GitHubA2ATask(
            issue_number=issue_number,
            agent_name=agent_name,
            message=message,
            status="submitted",
            created_at=datetime.utcnow().isoformat(),
        )
    
    async def _trigger_agent_workflow(
        self,
        agent_name: str,
        issue_number: int,
    ) -> None:
        """
        Trigger agent workflow via workflow_dispatch.
        
        Args:
            agent_name: Agent to trigger
            issue_number: Issue number with task
        """
        # This assumes a workflow exists: .github/workflows/a2a-agent-worker.yml
        response = await self.client.post(
            f"{self.base_url}/actions/workflows/a2a-agent-worker.yml/dispatches",
            json={
                "ref": "main",  # or current branch
                "inputs": {
                    "agent_name": agent_name,
                    "issue_number": str(issue_number),
                }
            }
        )
        # Don't raise - workflow dispatch is optional
    
    async def get_task_status(self, issue_number: int) -> GitHubA2ATask:
        """
        Get current status of a task.
        
        Args:
            issue_number: Issue number
            
        Returns:
            GitHubA2ATask with current status
        """
        response = await self.client.get(f"{self.base_url}/issues/{issue_number}")
        response.raise_for_status()
        
        issue = response.json()
        
        # Extract status from labels
        labels = [label["name"] for label in issue["labels"]]
        status = "unknown"
        agent_name = "unknown"
        
        for label in labels:
            if label.startswith("status:"):
                status = label.split(":", 1)[1]
            elif label.startswith("agent:"):
                agent_name = label.split(":", 1)[1]
        
        # Extract result from comments if completed
        result = None
        if status in ["completed", "failed"]:
            result = await self._extract_result_from_comments(issue_number)
        
        # Extract original message from issue body
        message = self._extract_message_from_body(issue["body"])
        
        return GitHubA2ATask(
            issue_number=issue_number,
            agent_name=agent_name,
            message=message,
            status=status,
            created_at=issue["created_at"],
            result=result,
        )
    
    async def _extract_result_from_comments(
        self,
        issue_number: int,
    ) -> Optional[Dict[str, Any]]:
        """Extract A2A result from issue comments."""
        response = await self.client.get(
            f"{self.base_url}/issues/{issue_number}/comments"
        )
        response.raise_for_status()
        
        comments = response.json()
        
        # Look for last comment with A2A result marker
        for comment in reversed(comments):
            body = comment["body"]
            if "```json" in body and "A2A Result" in body:
                # Extract JSON from code block
                try:
                    start = body.find("```json") + 7
                    end = body.find("```", start)
                    json_str = body[start:end].strip()
                    return json.loads(json_str)
                except Exception:
                    continue
        
        return None
    
    def _extract_message_from_body(self, body: str) -> Dict[str, Any]:
        """Extract A2A message from issue body."""
        try:
            # Find JSON code block
            start = body.find("```json") + 7
            end = body.find("```", start)
            json_str = body[start:end].strip()
            return json.loads(json_str)
        except Exception:
            return {}
    
    async def post_result(
        self,
        issue_number: int,
        result: Dict[str, Any],
        status: str = "completed",
    ) -> None:
        """
        Post task result as issue comment.
        
        Args:
            issue_number: Issue number
            result: A2A result payload
            status: Final status (completed, failed)
        """
        # Post result comment
        comment_body = f"""## ✅ A2A Result

**Status:** {status}  
**Completed:** {datetime.utcnow().isoformat()}Z

### Result Payload

```json
{json.dumps(result, indent=2)}
```

---
*Posted by A2A protocol transport layer*
"""
        
        await self.client.post(
            f"{self.base_url}/issues/{issue_number}/comments",
            json={"body": comment_body}
        )
        
        # Update issue labels
        await self._update_status_label(issue_number, status)
        
        # Close issue if completed
        if status == "completed":
            await self.client.patch(
                f"{self.base_url}/issues/{issue_number}",
                json={"state": "closed"}
            )
    
    async def _update_status_label(
        self,
        issue_number: int,
        new_status: str,
    ) -> None:
        """Update status label on issue."""
        # Get current labels
        response = await self.client.get(f"{self.base_url}/issues/{issue_number}")
        issue = response.json()
        
        # Remove old status labels
        labels = [
            label["name"]
            for label in issue["labels"]
            if not label["name"].startswith("status:")
        ]
        
        # Add new status label
        labels.append(f"status:{new_status}")
        
        # Update issue
        await self.client.patch(
            f"{self.base_url}/issues/{issue_number}",
            json={"labels": labels}
        )
    
    async def poll_for_completion(
        self,
        issue_number: int,
        timeout: int = 3600,
        poll_interval: int = 5,
    ) -> GitHubA2ATask:
        """
        Poll issue until task completes or times out.
        
        Args:
            issue_number: Issue number to poll
            timeout: Maximum time to wait (seconds)
            poll_interval: Time between polls (seconds)
            
        Returns:
            Completed GitHubA2ATask
            
        Raises:
            TimeoutError: If task doesn't complete in time
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            task = await self.get_task_status(issue_number)
            
            if task.status in ["completed", "failed"]:
                return task
            
            await asyncio.sleep(poll_interval)
        
        raise TimeoutError(
            f"Task {issue_number} did not complete within {timeout} seconds"
        )
    
    async def list_pending_tasks(
        self,
        agent_name: Optional[str] = None,
    ) -> List[GitHubA2ATask]:
        """
        List pending A2A tasks.
        
        Args:
            agent_name: Filter by agent (optional)
            
        Returns:
            List of pending tasks
        """
        # Build labels filter
        labels = ["a2a-task", "status:submitted"]
        if agent_name:
            labels.append(f"agent:{agent_name}")
        
        response = await self.client.get(
            f"{self.base_url}/issues",
            params={
                "labels": ",".join(labels),
                "state": "open",
            }
        )
        response.raise_for_status()
        
        issues = response.json()
        
        tasks = []
        for issue in issues:
            # Parse task from issue
            task = GitHubA2ATask(
                issue_number=issue["number"],
                agent_name=agent_name or "unknown",
                message=self._extract_message_from_body(issue["body"]),
                status="submitted",
                created_at=issue["created_at"],
            )
            tasks.append(task)
        
        return tasks


# Helper functions for convenience

async def send_task_via_github(
    agent_name: str,
    message: Dict[str, Any],
    github_token: str,
    repo_owner: str,
    repo_name: str,
) -> int:
    """
    Send A2A task via GitHub Issues.
    
    Returns issue number (task ID)
    """
    transport = GitHubA2ATransport(github_token, repo_owner, repo_name)
    try:
        task = await transport.create_task(agent_name, message)
        return task.issue_number
    finally:
        await transport.close()


async def wait_for_task_completion(
    issue_number: int,
    github_token: str,
    repo_owner: str,
    repo_name: str,
    timeout: int = 3600,
) -> Dict[str, Any]:
    """
    Wait for task completion and return result.
    
    Raises TimeoutError if task doesn't complete.
    """
    transport = GitHubA2ATransport(github_token, repo_owner, repo_name)
    try:
        task = await transport.poll_for_completion(issue_number, timeout)
        return task.result or {}
    finally:
        await transport.close()


if __name__ == "__main__":
    import os
    import sys
    
    # Simple CLI for testing
    async def main():
        token = os.getenv("GITHUB_TOKEN")
        if not token:
            print("Error: GITHUB_TOKEN environment variable required")
            sys.exit(1)
        
        if len(sys.argv) < 4:
            print("Usage: python -m tools.a2a.github_transport <owner> <repo> <agent> <message>")
            sys.exit(1)
        
        owner = sys.argv[1]
        repo = sys.argv[2]
        agent = sys.argv[3]
        message_text = sys.argv[4]
        
        message = {
            "method": "task.execute",
            "params": {"text": message_text},
            "id": "test-task-1",
        }
        
        print(f"Sending task to {agent} via GitHub Issues...")
        issue_num = await send_task_via_github(agent, message, token, owner, repo)
        print(f"Created issue #{issue_num}")
        print(f"View at: https://github.com/{owner}/{repo}/issues/{issue_num}")
    
    asyncio.run(main())
