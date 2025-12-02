"""
Error Event Models for A2A Error Observer System
================================================

This module defines the canonical error_event task/message type used across
the A2A network for error reporting and observation.

All agents, UI backends, and log consumers can emit error_event tasks to the
error_observer agent for centralized error handling and GitHub dispatch.
"""

import hashlib
import json
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ErrorEvent(BaseModel):
    """
    Canonical error event structure for A2A error reporting.
    
    This model represents an error that occurred in the A2A system and should
    be forwarded to the error_observer agent for processing.
    
    All timestamps should be in RFC3339 format (ISO 8601).
    """
    
    service: str = Field(
        ...,
        description="Service name where the error occurred (e.g., 'academic-research', 'a2a-ui')"
    )
    
    region: str = Field(
        default="us-central1",
        description="GCP region where the service is deployed"
    )
    
    environment: str = Field(
        default="production",
        description="Environment where the error occurred (e.g., 'production', 'staging', 'development')"
    )
    
    error_message: str = Field(
        ...,
        description="The error message or description"
    )
    
    stack_trace: Optional[str] = Field(
        default=None,
        description="Stack trace if available"
    )
    
    logs: List[str] = Field(
        default_factory=list,
        description="Additional log entries related to this error"
    )
    
    run_console_url: Optional[str] = Field(
        default=None,
        description="URL to GCP Cloud Run console for this service"
    )
    
    a2a_ui_url: Optional[str] = Field(
        default=None,
        description="URL to A2A UI view for the relevant mission/task"
    )
    
    error_hash: str = Field(
        ...,
        description="Stable hash for deduplication (computed from service + error_message + task_type)"
    )
    
    first_seen: str = Field(
        ...,
        description="RFC3339 timestamp when this error was first observed"
    )
    
    last_seen: str = Field(
        ...,
        description="RFC3339 timestamp when this error was last observed"
    )
    
    occurrences: int = Field(
        default=1,
        description="Number of times this error has occurred"
    )
    
    source_agent: Optional[str] = Field(
        default=None,
        description="Name of the agent where the error originated"
    )
    
    source_channel: str = Field(
        default="runtime",
        description="Channel where the error originated (e.g., 'runtime', 'ui', 'cloudrun')"
    )
    
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata about the error context"
    )
    
    @staticmethod
    def compute_error_hash(service: str, error_message: str, task_type: str = "error") -> str:
        """
        Compute a stable hash for error deduplication.
        
        Args:
            service: Service name
            error_message: Error message
            task_type: Type of task (default: "error")
            
        Returns:
            Hex digest of the hash
        """
        hash_input = f"{service}|{error_message}|{task_type}"
        return hashlib.sha256(hash_input.encode()).hexdigest()[:16]
    
    @classmethod
    def from_exception(
        cls,
        service: str,
        exception: Exception,
        source_agent: Optional[str] = None,
        source_channel: str = "runtime",
        region: str = "us-central1",
        environment: str = "production",
        a2a_ui_url: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> "ErrorEvent":
        """
        Create an ErrorEvent from a Python exception.
        
        Args:
            service: Service name where the exception occurred
            exception: The exception object
            source_agent: Optional agent name
            source_channel: Channel where error originated
            region: GCP region
            environment: Environment name
            a2a_ui_url: Optional UI URL
            metadata: Optional additional metadata
            
        Returns:
            ErrorEvent instance
        """
        import traceback
        
        error_message = str(exception)
        stack_trace = "".join(traceback.format_exception(type(exception), exception, exception.__traceback__))
        
        now = datetime.utcnow().isoformat() + "Z"
        error_hash = cls.compute_error_hash(service, error_message, "exception")
        
        return cls(
            service=service,
            region=region,
            environment=environment,
            error_message=error_message,
            stack_trace=stack_trace,
            error_hash=error_hash,
            first_seen=now,
            last_seen=now,
            source_agent=source_agent,
            source_channel=source_channel,
            a2a_ui_url=a2a_ui_url,
            metadata=metadata or {},
        )
    
    @classmethod
    def from_ui_error(
        cls,
        message: str,
        stack: Optional[str] = None,
        url: Optional[str] = None,
        user_agent: Optional[str] = None,
        extra: Optional[Dict[str, Any]] = None,
    ) -> "ErrorEvent":
        """
        Create an ErrorEvent from a UI error report.
        
        Args:
            message: Error message
            stack: Stack trace
            url: URL where error occurred
            user_agent: Browser user agent
            extra: Additional context
            
        Returns:
            ErrorEvent instance
        """
        now = datetime.utcnow().isoformat() + "Z"
        error_hash = cls.compute_error_hash("a2a-ui", message, "ui-error")
        
        logs = []
        if user_agent:
            logs.append(f"User-Agent: {user_agent}")
        if extra:
            logs.append(f"Extra: {json.dumps(extra)}")
        
        return cls(
            service="a2a-ui",
            region="us-central1",
            environment="production",
            error_message=message,
            stack_trace=stack,
            error_hash=error_hash,
            first_seen=now,
            last_seen=now,
            source_agent="a2a-ui-backend",
            source_channel="ui",
            a2a_ui_url=url,
            logs=logs,
            metadata=extra or {},
        )
    
    @classmethod
    def from_cloudrun_log(
        cls,
        service_name: str,
        log_entry: Dict[str, Any],
        region: str = "us-central1",
        environment: str = "production",
    ) -> "ErrorEvent":
        """
        Create an ErrorEvent from a Cloud Run log entry.
        
        Args:
            service_name: Name of the Cloud Run service
            log_entry: Cloud Logging entry as dict
            region: GCP region
            environment: Environment name
            
        Returns:
            ErrorEvent instance
        """
        # Extract fields from structured log entry
        text_payload = log_entry.get("textPayload", "")
        json_payload = log_entry.get("jsonPayload", {})
        timestamp = log_entry.get("timestamp", datetime.utcnow().isoformat() + "Z")
        
        # Try to extract error message
        error_message = text_payload or json_payload.get("message", "Unknown error")
        
        # Extract stack trace if present
        stack_trace = json_payload.get("stack_trace") or json_payload.get("stack")
        
        # Compute hash
        error_hash = cls.compute_error_hash(service_name, error_message, "cloudrun-log")
        
        # Build logs array
        logs = [text_payload] if text_payload else []
        if json_payload:
            logs.append(f"JSON: {json.dumps(json_payload)}")
        
        return cls(
            service=service_name,
            region=region,
            environment=environment,
            error_message=error_message,
            stack_trace=stack_trace,
            error_hash=error_hash,
            first_seen=timestamp,
            last_seen=timestamp,
            source_channel="cloudrun",
            logs=logs,
            metadata={"log_entry": log_entry},
        )
    
    def to_a2a_artifact(self) -> Dict[str, Any]:
        """
        Convert this error event to an A2A artifact.
        
        Returns:
            A2A artifact dict with error event data
        """
        return {
            "name": "error_event",
            "type": "error_event",
            "data": self.model_dump_json(indent=2),
        }
    
    def to_github_payload(self) -> Dict[str, Any]:
        """
        Convert this error event to a GitHub repository_dispatch payload.
        
        Returns:
            Dict suitable for GitHub repository_dispatch client_payload
        """
        return self.model_dump()
