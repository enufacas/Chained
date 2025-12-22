"""
GitHub Branch-based transport layer for A2A protocol.

Alternative to issue-based transport. Uses ephemeral git branches to communicate
between agents, avoiding issue tracker clutter.

Architecture:
- Create branch: a2a-tasks/{task-id}
- Write files: task.json, status.json, result.json
- Poll branch for completion
- Delete branch when done
"""

import json
import base64
import time
import asyncio
from typing import Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
from uuid import uuid4

import httpx


@dataclass
class BranchA2ATask:
    """Represents an A2A task tracked via git branch."""
    task_id: str
    branch_name: str
    agent_name: str
    message: Dict[str, Any]
    status: str  # "submitted", "working", "completed", "failed"
    created_at: str
    result: Optional[Dict[str, Any]] = None


class GitHubBranchTransport:
    """
    A2A transport layer using git branches.
    
    Benefits over issue-based:
    - No issue tracker clutter
    - Supports binary artifacts
    - Automatic cleanup (delete branch)
    - Git-native operations
    
    Trade-offs:
    - No built-in UI for tracking
    - Manual status management
    - Less discoverable
    """
    
    def __init__(
        self,
        github_token: str,
        repo_owner: str,
        repo_name: str,
        base_branch: str = "main",
    ):
        """
        Initialize GitHub branch transport.
        
        Args:
            github_token: GitHub token with repo access
            repo_owner: Repository owner
            repo_name: Repository name
            base_branch: Branch to base task branches on
        """
        self.github_token = github_token
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        self.base_branch = base_branch
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
    
    async def _get_base_sha(self) -> str:
        """Get SHA of base branch."""
        response = await self.client.get(
            f"{self.base_url}/git/refs/heads/{self.base_branch}"
        )
        response.raise_for_status()
        return response.json()["object"]["sha"]
    
    async def _create_branch(self, branch_name: str) -> None:
        """Create a new branch from base."""
        base_sha = await self._get_base_sha()
        
        response = await self.client.post(
            f"{self.base_url}/git/refs",
            json={
                "ref": f"refs/heads/{branch_name}",
                "sha": base_sha,
            }
        )
        response.raise_for_status()
    
    async def _write_file(
        self,
        branch_name: str,
        path: str,
        content: str,
        message: str,
    ) -> None:
        """Write a file to the branch."""
        # Check if file exists
        try:
            response = await self.client.get(
                f"{self.base_url}/contents/{path}",
                params={"ref": branch_name}
            )
            sha = response.json()["sha"]
        except Exception:
            sha = None
        
        # Write file
        encoded_content = base64.b64encode(content.encode()).decode()
        
        data = {
            "message": message,
            "content": encoded_content,
            "branch": branch_name,
        }
        
        if sha:
            data["sha"] = sha
        
        response = await self.client.put(
            f"{self.base_url}/contents/{path}",
            json=data
        )
        response.raise_for_status()
    
    async def _read_file(
        self,
        branch_name: str,
        path: str,
    ) -> Optional[str]:
        """Read a file from the branch."""
        try:
            response = await self.client.get(
                f"{self.base_url}/contents/{path}",
                params={"ref": branch_name}
            )
            response.raise_for_status()
            
            encoded = response.json()["content"]
            return base64.b64decode(encoded).decode()
        except Exception:
            return None
    
    async def _delete_branch(self, branch_name: str) -> None:
        """Delete the branch."""
        try:
            await self.client.delete(
                f"{self.base_url}/git/refs/heads/{branch_name}"
            )
        except Exception:
            pass  # Branch may not exist
    
    async def create_task(
        self,
        agent_name: str,
        message: Dict[str, Any],
        priority: str = "normal",
    ) -> BranchA2ATask:
        """
        Create a new A2A task via git branch.
        
        Args:
            agent_name: Target agent name
            message: A2A message payload
            priority: Task priority
            
        Returns:
            BranchA2ATask object
        """
        # Generate unique task ID
        task_id = uuid4().hex[:12]
        branch_name = f"a2a-tasks/{agent_name}/{task_id}"
        
        # Create branch
        await self._create_branch(branch_name)
        
        # Write task file
        task_data = {
            "task_id": task_id,
            "agent_name": agent_name,
            "message": message,
            "priority": priority,
            "created_at": datetime.utcnow().isoformat(),
        }
        
        await self._write_file(
            branch_name,
            f"{branch_name}/task.json",
            json.dumps(task_data, indent=2),
            f"Create A2A task for {agent_name}"
        )
        
        # Write status file
        status_data = {
            "status": "submitted",
            "updated_at": datetime.utcnow().isoformat(),
        }
        
        await self._write_file(
            branch_name,
            f"{branch_name}/status.json",
            json.dumps(status_data, indent=2),
            "Initialize task status"
        )
        
        # Trigger workflow (optional - can also poll branches)
        try:
            await self._trigger_agent_workflow(agent_name, branch_name)
        except Exception:
            pass  # Workflow trigger is optional
        
        return BranchA2ATask(
            task_id=task_id,
            branch_name=branch_name,
            agent_name=agent_name,
            message=message,
            status="submitted",
            created_at=datetime.utcnow().isoformat(),
        )
    
    async def _trigger_agent_workflow(
        self,
        agent_name: str,
        branch_name: str,
    ) -> None:
        """Trigger agent workflow via workflow_dispatch."""
        response = await self.client.post(
            f"{self.base_url}/actions/workflows/a2a-agent-worker.yml/dispatches",
            json={
                "ref": self.base_branch,
                "inputs": {
                    "agent_name": agent_name,
                    "branch_name": branch_name,
                }
            }
        )
        # Don't raise - workflow dispatch is optional
    
    async def get_task_status(self, branch_name: str) -> BranchA2ATask:
        """
        Get current status of a task.
        
        Args:
            branch_name: Branch name
            
        Returns:
            BranchA2ATask with current status
        """
        # Read task file
        task_content = await self._read_file(branch_name, f"{branch_name}/task.json")
        if not task_content:
            raise ValueError(f"Task not found: {branch_name}")
        
        task_data = json.loads(task_content)
        
        # Read status file
        status_content = await self._read_file(branch_name, f"{branch_name}/status.json")
        if status_content:
            status_data = json.loads(status_content)
            status = status_data.get("status", "unknown")
        else:
            status = "unknown"
        
        # Read result if completed
        result = None
        if status in ["completed", "failed"]:
            result_content = await self._read_file(branch_name, f"{branch_name}/result.json")
            if result_content:
                result = json.loads(result_content)
        
        return BranchA2ATask(
            task_id=task_data["task_id"],
            branch_name=branch_name,
            agent_name=task_data["agent_name"],
            message=task_data["message"],
            status=status,
            created_at=task_data["created_at"],
            result=result,
        )
    
    async def post_result(
        self,
        branch_name: str,
        result: Dict[str, Any],
        status: str = "completed",
    ) -> None:
        """
        Post task result to branch.
        
        Args:
            branch_name: Branch name
            result: A2A result payload
            status: Final status
        """
        # Write result file
        await self._write_file(
            branch_name,
            f"{branch_name}/result.json",
            json.dumps(result, indent=2),
            f"Post A2A result ({status})"
        )
        
        # Update status
        status_data = {
            "status": status,
            "updated_at": datetime.utcnow().isoformat(),
        }
        
        await self._write_file(
            branch_name,
            f"{branch_name}/status.json",
            json.dumps(status_data, indent=2),
            f"Update status to {status}"
        )
    
    async def poll_for_completion(
        self,
        branch_name: str,
        timeout: int = 3600,
        poll_interval: int = 5,
        auto_cleanup: bool = True,
    ) -> BranchA2ATask:
        """
        Poll branch until task completes or times out.
        
        Args:
            branch_name: Branch name to poll
            timeout: Maximum time to wait (seconds)
            poll_interval: Time between polls (seconds)
            auto_cleanup: Delete branch after completion
            
        Returns:
            Completed BranchA2ATask
            
        Raises:
            TimeoutError: If task doesn't complete in time
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            task = await self.get_task_status(branch_name)
            
            if task.status in ["completed", "failed"]:
                # Cleanup branch if requested
                if auto_cleanup:
                    await self._delete_branch(branch_name)
                
                return task
            
            await asyncio.sleep(poll_interval)
        
        raise TimeoutError(
            f"Task {branch_name} did not complete within {timeout} seconds"
        )
    
    async def list_pending_tasks(
        self,
        agent_name: Optional[str] = None,
    ) -> list:
        """
        List pending A2A tasks.
        
        Args:
            agent_name: Filter by agent (optional)
            
        Returns:
            List of branch names with pending tasks
        """
        # List branches with a2a-tasks prefix
        response = await self.client.get(
            f"{self.base_url}/git/refs/heads/a2a-tasks/"
        )
        
        if response.status_code != 200:
            return []
        
        branches = response.json()
        task_branches = []
        
        for branch_ref in branches:
            branch_name = branch_ref["ref"].replace("refs/heads/", "")
            
            # Filter by agent if specified
            if agent_name and f"a2a-tasks/{agent_name}/" not in branch_name:
                continue
            
            # Check if task is pending
            try:
                task = await self.get_task_status(branch_name)
                if task.status in ["submitted", "working"]:
                    task_branches.append(branch_name)
            except Exception:
                continue
        
        return task_branches


# Helper functions

async def send_task_via_branch(
    agent_name: str,
    message: Dict[str, Any],
    github_token: str,
    repo_owner: str,
    repo_name: str,
) -> str:
    """
    Send A2A task via git branch.
    
    Returns branch name (task ID)
    """
    transport = GitHubBranchTransport(github_token, repo_owner, repo_name)
    try:
        task = await transport.create_task(agent_name, message)
        return task.branch_name
    finally:
        await transport.close()


async def wait_for_task_completion_branch(
    branch_name: str,
    github_token: str,
    repo_owner: str,
    repo_name: str,
    timeout: int = 3600,
    auto_cleanup: bool = True,
) -> Dict[str, Any]:
    """
    Wait for task completion on branch and return result.
    
    Raises TimeoutError if task doesn't complete.
    """
    transport = GitHubBranchTransport(github_token, repo_owner, repo_name)
    try:
        task = await transport.poll_for_completion(
            branch_name, timeout, auto_cleanup=auto_cleanup
        )
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
            print("Usage: python -m tools.a2a.github_branch_transport <owner> <repo> <agent> <message>")
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
        
        print(f"Sending task to {agent} via git branch...")
        branch_name = await send_task_via_branch(agent, message, token, owner, repo)
        print(f"Created branch: {branch_name}")
        print(f"View at: https://github.com/{owner}/{repo}/tree/{branch_name}")
    
    asyncio.run(main())
