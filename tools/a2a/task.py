"""
A2A Task and Artifact Management.

This module provides proper A2A protocol Task and Artifact handling following
the official specification from https://github.com/a2aproject/A2A

Based on the "Life of a Task" documentation:
https://a2a-protocol.org/latest/topics/life-of-a-task/

Key Concepts:
- Task: A stateful unit of work with lifecycle (submitted → working → completed)
- Artifact: Output produced by agents for tasks (versioned, multi-modal)
- contextId: Groups related Tasks together for continuity
- taskId: Unique identifier for each Task
- referenceTaskIds: Links follow-up tasks to previous tasks
"""

import base64
import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional


class TaskState(str, Enum):
    """
    A2A Task lifecycle states (Spec §4.1.3).
    
    Per the spec, tasks progress through these states:
    - submitted: Task created and submitted to agent
    - working: Agent is actively processing
    - input-required: Paused, waiting for more information
    - auth-required: Paused, waiting for authentication
    - completed: Successfully finished
    - canceled: Terminated by client
    - rejected: Agent declined the task
    - failed: Task encountered an error
    - unknown: State cannot be determined (extension for error handling)
    """
    SUBMITTED = "submitted"
    WORKING = "working"
    INPUT_REQUIRED = "input-required"
    AUTH_REQUIRED = "auth-required"
    COMPLETED = "completed"
    CANCELED = "canceled"
    REJECTED = "rejected"
    FAILED = "failed"
    UNKNOWN = "unknown"  # Extension for error handling
    
    def is_terminal(self) -> bool:
        """Check if this is a terminal state (task cannot restart)."""
        return self in {
            TaskState.COMPLETED,
            TaskState.CANCELED,
            TaskState.REJECTED,
            TaskState.FAILED,
        }
    
    def is_interrupted(self) -> bool:
        """Check if task is interrupted (waiting for input)."""
        return self in {
            TaskState.INPUT_REQUIRED,
            TaskState.AUTH_REQUIRED,
        }


@dataclass
class Part:
    """
    A2A Part - individual content unit (Spec §4.1.4).
    
    Parts can be:
    - TextPart: Text content with role (user/agent)
    - FilePart: Binary file content
    - DataPart: Structured data (JSON)
    """
    kind: str  # "text", "file", "data"
    text: Optional[str] = None
    file: Optional[Dict[str, Any]] = None
    data: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None
    
    @classmethod
    def text_part(cls, text: str, role: str = "agent") -> "Part":
        """Create a TextPart."""
        return cls(kind="text", text=text, metadata={"role": role})
    
    @classmethod
    def data_part(cls, data: Dict[str, Any]) -> "Part":
        """Create a DataPart."""
        return cls(kind="data", data=data)
    
    @classmethod
    def file_part(cls, name: str, mime_type: str, content: bytes) -> "Part":
        """Create a FilePart."""
        return cls(
            kind="file",
            file={
                "name": name,
                "mimeType": mime_type,
                "bytes": base64.b64encode(content).decode(),
            }
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        result = {"kind": self.kind}
        if self.text is not None:
            result["text"] = self.text
        if self.file is not None:
            result["file"] = self.file
        if self.data is not None:
            result["data"] = self.data
        if self.metadata is not None:
            result["metadata"] = self.metadata
        return result


@dataclass
class Artifact:
    """
    A2A Artifact - output produced by agents (Spec §4.1.9).
    
    Artifacts are the outputs of Tasks. They are versioned (via artifactId)
    and can contain multiple Parts for multi-modal content.
    
    Per the spec:
    - Use consistent artifact-name when generating refined versions
    - New versions get new artifactId but same name
    - Client tracks artifact mutations/versions
    """
    artifact_id: str
    name: str
    description: Optional[str] = None
    parts: List[Part] = field(default_factory=list)
    metadata: Optional[Dict[str, Any]] = None
    
    @classmethod
    def create(
        cls,
        name: str,
        description: Optional[str] = None,
        parts: Optional[List[Part]] = None,
    ) -> "Artifact":
        """Create a new Artifact with auto-generated ID."""
        return cls(
            artifact_id=f"artifact-{uuid.uuid4().hex[:12]}",
            name=name,
            description=description,
            parts=parts or [],
        )
    
    @classmethod
    def from_text(cls, name: str, text: str, description: Optional[str] = None) -> "Artifact":
        """Create an Artifact from text content."""
        return cls.create(
            name=name,
            description=description,
            parts=[Part.text_part(text)],
        )
    
    @classmethod
    def from_json(cls, name: str, data: Dict[str, Any], description: Optional[str] = None) -> "Artifact":
        """Create an Artifact from JSON data."""
        return cls.create(
            name=name,
            description=description,
            parts=[Part.data_part(data)],
        )
    
    def get_text_content(self) -> Optional[str]:
        """Extract text content from all TextParts."""
        texts = []
        for part in self.parts:
            if part.kind == "text" and part.text:
                texts.append(part.text)
        return "\n".join(texts) if texts else None
    
    def get_data_content(self) -> Optional[Dict[str, Any]]:
        """Extract data content from first DataPart."""
        for part in self.parts:
            if part.kind == "data" and part.data:
                return part.data
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        result = {
            "artifactId": self.artifact_id,
            "name": self.name,
            "parts": [p.to_dict() for p in self.parts],
        }
        if self.description:
            result["description"] = self.description
        if self.metadata:
            result["metadata"] = self.metadata
        return result


@dataclass
class TaskStatus:
    """
    A2A TaskStatus - current status of a Task (Spec §4.1.2).
    
    Contains the state, optional message, and timestamp.
    """
    state: TaskState
    message: Optional[Part] = None
    timestamp: Optional[str] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now(timezone.utc).isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        result = {
            "state": self.state.value,
            "timestamp": self.timestamp,
        }
        if self.message:
            result["message"] = {
                "role": "agent",
                "parts": [self.message.to_dict()],
            }
        return result


@dataclass
class Task:
    """
    A2A Task - stateful unit of work (Spec §4.1.1).
    
    This is the core object for tracking work in A2A. Key fields:
    - id: Unique taskId
    - contextId: Groups related tasks together
    - status: Current TaskStatus with state and message
    - artifacts: Output artifacts produced
    
    Per "Life of a Task":
    - Tasks are immutable once they reach terminal state
    - Follow-ups create new Tasks within same contextId
    - Use referenceTaskIds to link to previous tasks
    """
    id: str
    context_id: str
    status: TaskStatus
    artifacts: List[Artifact] = field(default_factory=list)
    reference_task_ids: List[str] = field(default_factory=list)
    agent_name: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    
    @classmethod
    def create(
        cls,
        context_id: Optional[str] = None,
        agent_name: Optional[str] = None,
        reference_task_ids: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> "Task":
        """
        Create a new Task in 'submitted' state.
        
        Args:
            context_id: Optional contextId (auto-generated if None)
            agent_name: Agent handling this task
            reference_task_ids: Previous tasks this references
            metadata: Optional metadata for the task
            
        Returns:
            New Task in submitted state
        """
        return cls(
            id=f"task-{uuid.uuid4().hex[:12]}",
            context_id=context_id or f"ctx-{uuid.uuid4().hex[:8]}",
            status=TaskStatus(state=TaskState.SUBMITTED),
            agent_name=agent_name,
            reference_task_ids=reference_task_ids or [],
            metadata=metadata,
        )
    
    def transition_to(self, state: TaskState, message: Optional[str] = None) -> None:
        """
        Transition the task to a new state.
        
        Args:
            state: New TaskState
            message: Optional status message
        """
        if self.status.state.is_terminal():
            raise ValueError(
                f"Cannot transition from terminal state {self.status.state.value}"
            )
        
        self.status = TaskStatus(
            state=state,
            message=Part.text_part(message) if message else None,
        )
    
    def set_working(self, message: Optional[str] = None) -> None:
        """Set task to working state."""
        self.transition_to(TaskState.WORKING, message)
    
    def complete(self, message: Optional[str] = None) -> None:
        """Set task to completed state."""
        self.transition_to(TaskState.COMPLETED, message)
    
    def fail(self, error: str) -> None:
        """Set task to failed state."""
        self.transition_to(TaskState.FAILED, error)
    
    def add_artifact(self, artifact: Artifact) -> None:
        """Add an artifact to the task."""
        self.artifacts.append(artifact)
    
    def add_text_artifact(
        self,
        name: str,
        text: str,
        description: Optional[str] = None,
    ) -> Artifact:
        """Add a text artifact to the task."""
        artifact = Artifact.from_text(name, text, description)
        self.add_artifact(artifact)
        return artifact
    
    def add_json_artifact(
        self,
        name: str,
        data: Dict[str, Any],
        description: Optional[str] = None,
    ) -> Artifact:
        """Add a JSON data artifact to the task."""
        artifact = Artifact.from_json(name, data, description)
        self.add_artifact(artifact)
        return artifact
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to A2A Task JSON format."""
        result = {
            "kind": "task",
            "id": self.id,
            "contextId": self.context_id,
            "status": self.status.to_dict(),
        }
        if self.artifacts:
            result["artifacts"] = [a.to_dict() for a in self.artifacts]
        if self.reference_task_ids:
            result["referenceTaskIds"] = self.reference_task_ids
        if self.agent_name:
            result["agentName"] = self.agent_name
        if self.metadata:
            result["metadata"] = self.metadata
        return result
    
    def to_json(self, indent: int = 2) -> str:
        """Serialize to JSON string."""
        return json.dumps(self.to_dict(), indent=indent)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Task":
        """Deserialize from dictionary."""
        # Reconstruct TaskStatus with message if present
        status_data = data["status"]
        message = None
        if "message" in status_data and status_data["message"]:
            msg_data = status_data["message"]
            if "parts" in msg_data and msg_data["parts"]:
                # Take the first text part as the message
                for part_data in msg_data["parts"]:
                    if part_data.get("kind") == "text":
                        message = Part(
                            kind=part_data["kind"],
                            text=part_data.get("text"),
                            metadata=part_data.get("metadata"),
                        )
                        break
        
        status = TaskStatus(
            state=TaskState(status_data["state"]),
            message=message,
            timestamp=status_data.get("timestamp"),
        )
        
        artifacts = []
        for a_data in data.get("artifacts", []):
            parts = []
            for p_data in a_data.get("parts", []):
                parts.append(Part(
                    kind=p_data["kind"],
                    text=p_data.get("text"),
                    file=p_data.get("file"),
                    data=p_data.get("data"),
                    metadata=p_data.get("metadata"),
                ))
            artifacts.append(Artifact(
                artifact_id=a_data["artifactId"],
                name=a_data["name"],
                description=a_data.get("description"),
                parts=parts,
                metadata=a_data.get("metadata"),
            ))
        
        return cls(
            id=data["id"],
            context_id=data["contextId"],
            status=status,
            artifacts=artifacts,
            reference_task_ids=data.get("referenceTaskIds", []),
            agent_name=data.get("agentName"),
            metadata=data.get("metadata"),
        )


class TaskStore:
    """
    Storage for A2A Tasks.
    
    This provides persistent storage for tasks and their artifacts,
    enabling task lookup by ID, contextId, or agent.
    """
    
    def __init__(self, storage_path: Optional[Path] = None):
        """
        Initialize the task store.
        
        Args:
            storage_path: Optional path for persistent storage
        """
        self.storage_path = storage_path
        self._tasks: Dict[str, Task] = {}
        self._contexts: Dict[str, List[str]] = {}  # contextId -> [taskIds]
        
        if storage_path and storage_path.exists():
            self.load()
    
    def store(self, task: Task) -> None:
        """Store a task."""
        self._tasks[task.id] = task
        
        # Index by contextId
        if task.context_id not in self._contexts:
            self._contexts[task.context_id] = []
        if task.id not in self._contexts[task.context_id]:
            self._contexts[task.context_id].append(task.id)
        
        self._persist()
    
    def get(self, task_id: str) -> Optional[Task]:
        """Get a task by ID."""
        return self._tasks.get(task_id)
    
    def get_by_context(self, context_id: str) -> List[Task]:
        """Get all tasks for a contextId."""
        task_ids = self._contexts.get(context_id, [])
        return [self._tasks[tid] for tid in task_ids if tid in self._tasks]
    
    def get_latest_artifacts(self, context_id: str) -> List[Artifact]:
        """Get the latest artifacts from the context (most recent task)."""
        tasks = self.get_by_context(context_id)
        if not tasks:
            return []
        
        # Get artifacts from the most recent completed task
        completed_tasks = [t for t in tasks if t.status.state == TaskState.COMPLETED]
        if not completed_tasks:
            return []
        
        # Sort by timestamp to get the truly most recent task
        # Tasks with no timestamp are considered oldest
        def get_timestamp(task):
            ts = task.status.timestamp
            if ts is None:
                return ""
            return ts
        
        completed_tasks.sort(key=get_timestamp)
        
        # Return artifacts from the most recent completed task
        return completed_tasks[-1].artifacts
    
    def _persist(self) -> None:
        """Persist tasks to storage."""
        if not self.storage_path:
            return
        
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        
        data = {
            "tasks": {tid: t.to_dict() for tid, t in self._tasks.items()},
            "contexts": self._contexts,
        }
        
        with open(self.storage_path, "w") as f:
            json.dump(data, f, indent=2)
    
    def load(self) -> None:
        """Load tasks from storage."""
        if not self.storage_path or not self.storage_path.exists():
            return
        
        with open(self.storage_path) as f:
            data = json.load(f)
        
        self._tasks = {
            tid: Task.from_dict(t_data)
            for tid, t_data in data.get("tasks", {}).items()
        }
        self._contexts = data.get("contexts", {})


def create_analysis_task(
    issue_number: int,
    agent_name: str,
    run_id: str,
    context_id: Optional[str] = None,
) -> Task:
    """
    Create an analysis task for an agent.
    
    This creates a properly structured A2A Task for agent analysis,
    following the protocol spec.
    
    Args:
        issue_number: GitHub issue number
        agent_name: Name of the agent handling analysis
        run_id: Workflow run ID
        context_id: Optional shared context ID
        
    Returns:
        New Task in submitted state
    """
    return Task.create(
        context_id=context_id or f"issue-{issue_number}",
        agent_name=agent_name,
        metadata={
            "issueNumber": issue_number,
            "runId": run_id,
            "taskType": "analysis",
        },
    )


def create_implementation_task(
    issue_number: int,
    run_id: str,
    reference_task_ids: List[str],
    context_id: str,
) -> Task:
    """
    Create an implementation task that references analysis tasks.
    
    This creates a follow-up task that references previous analysis tasks,
    following the A2A "Life of a Task" pattern for task refinements.
    
    Args:
        issue_number: GitHub issue number
        run_id: Workflow run ID
        reference_task_ids: IDs of analysis tasks to reference
        context_id: Shared context ID from analysis phase
        
    Returns:
        New Task linking to analysis tasks
    """
    return Task.create(
        context_id=context_id,
        agent_name="implementation-executor",
        reference_task_ids=reference_task_ids,
        metadata={
            "issueNumber": issue_number,
            "runId": run_id,
            "taskType": "implementation",
        },
    )


def aggregate_artifacts(tasks: List[Task]) -> Dict[str, Any]:
    """
    Aggregate artifacts from multiple completed tasks.
    
    This creates a consolidated view of all artifacts from analysis tasks,
    suitable for passing to an implementation task.
    
    Args:
        tasks: List of completed analysis tasks
        
    Returns:
        Aggregated artifact data
    """
    if not tasks:
        return {
            "contextId": None,
            "taskIds": [],
            "agents": {},
            "combinedAnalysis": [],
        }
    
    result = {
        "contextId": tasks[0].context_id,
        "taskIds": [t.id for t in tasks],
        "agents": {},
        "combinedAnalysis": [],
    }
    
    for task in tasks:
        if task.status.state != TaskState.COMPLETED:
            continue
        
        agent_data = {
            "taskId": task.id,
            "artifacts": [],
        }
        
        for artifact in task.artifacts:
            artifact_data = {
                "artifactId": artifact.artifact_id,
                "name": artifact.name,
                "description": artifact.description,
            }
            
            # Extract text content
            text_content = artifact.get_text_content()
            if text_content:
                artifact_data["textContent"] = text_content
                result["combinedAnalysis"].append({
                    "agent": task.agent_name,
                    "content": text_content,
                })
            
            # Extract data content
            data_content = artifact.get_data_content()
            if data_content:
                artifact_data["dataContent"] = data_content
            
            agent_data["artifacts"].append(artifact_data)
        
        if task.agent_name:
            result["agents"][task.agent_name] = agent_data
    
    return result
