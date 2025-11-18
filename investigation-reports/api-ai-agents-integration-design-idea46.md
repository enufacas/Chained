# 🏗️ API-AI-Agents Integration Design Document
## Mission ID: idea:46 - Implementation Specification
## Author: @agents-tech-lead

**Document Version:** 1.0  
**Date:** 2025-11-18  
**Status:** Proposal  
**Related:** api-ai-agents-integration-research-idea46.md  

---

## 📐 Overview

This document provides **detailed technical specifications** for implementing API-AI-Agents integration in Chained, based on research findings in the companion research report. This is an implementation blueprint with code examples, API specifications, and concrete technical decisions.

---

## 🎯 Phase 1: Agent Tool Interface

### 1.1 Tool Interface Specification

**File:** `tools/agent_tool_interface.py`

```python
"""
Agent Tool Interface - MCP-inspired tool system for Chained agents
Provides standardized interface for agent-to-external-system integration
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass
from enum import Enum
import json


class ToolParameterType(Enum):
    """OpenAI-compatible parameter types"""
    STRING = "string"
    NUMBER = "number"
    INTEGER = "integer"
    BOOLEAN = "boolean"
    ARRAY = "array"
    OBJECT = "object"


@dataclass
class ToolParameter:
    """Tool parameter definition following OpenAI function schema"""
    name: str
    type: ToolParameterType
    description: str
    required: bool = False
    enum: Optional[List[str]] = None
    items: Optional[Dict[str, Any]] = None  # For array types
    properties: Optional[Dict[str, Any]] = None  # For object types
    
    def to_schema(self) -> Dict[str, Any]:
        """Convert to OpenAI function parameter schema"""
        schema = {
            "type": self.type.value,
            "description": self.description
        }
        if self.enum:
            schema["enum"] = self.enum
        if self.items:
            schema["items"] = self.items
        if self.properties:
            schema["properties"] = self.properties
        return schema


@dataclass
class ToolMetadata:
    """Tool metadata for registry and discovery"""
    name: str
    description: str
    version: str
    author: str
    tags: List[str]
    requires_auth: bool = False
    async_execution: bool = True


class AgentTool(ABC):
    """
    Base class for all agent tools
    
    Follows MCP pattern with OpenAI-compatible function schema
    All tools must implement execute() method
    """
    
    def __init__(self, metadata: ToolMetadata):
        self.metadata = metadata
        self.parameters: List[ToolParameter] = []
    
    @abstractmethod
    async def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Execute the tool with provided parameters
        
        Returns:
            dict: Result with 'success', 'data', and optional 'error' keys
        """
        pass
    
    def add_parameter(self, param: ToolParameter):
        """Add a parameter to this tool"""
        self.parameters.append(param)
    
    def to_function_schema(self) -> Dict[str, Any]:
        """
        Convert tool to OpenAI function calling schema
        
        Returns OpenAI-compatible function definition
        """
        required_params = [p.name for p in self.parameters if p.required]
        
        return {
            "name": self.metadata.name,
            "description": self.metadata.description,
            "parameters": {
                "type": "object",
                "properties": {
                    p.name: p.to_schema() for p in self.parameters
                },
                "required": required_params
            }
        }
    
    def validate_parameters(self, **kwargs) -> tuple[bool, Optional[str]]:
        """
        Validate provided parameters against schema
        
        Returns:
            tuple: (is_valid, error_message)
        """
        # Check required parameters
        for param in self.parameters:
            if param.required and param.name not in kwargs:
                return False, f"Missing required parameter: {param.name}"
        
        # Type validation could be added here
        return True, None


class ToolRegistry:
    """Central registry for all available tools"""
    
    def __init__(self):
        self._tools: Dict[str, AgentTool] = {}
    
    def register(self, tool: AgentTool):
        """Register a tool in the registry"""
        self._tools[tool.metadata.name] = tool
    
    def get(self, name: str) -> Optional[AgentTool]:
        """Get tool by name"""
        return self._tools.get(name)
    
    def list_tools(self, tags: Optional[List[str]] = None) -> List[AgentTool]:
        """
        List available tools, optionally filtered by tags
        
        Args:
            tags: Filter by these tags (any match)
        """
        if not tags:
            return list(self._tools.values())
        
        return [
            tool for tool in self._tools.values()
            if any(tag in tool.metadata.tags for tag in tags)
        ]
    
    def to_openai_functions(self) -> List[Dict[str, Any]]:
        """Export all tools as OpenAI function definitions"""
        return [tool.to_function_schema() for tool in self._tools.values()]
    
    def save_registry(self, path: str):
        """Save registry metadata to JSON"""
        registry_data = {
            "tools": [
                {
                    "name": tool.metadata.name,
                    "description": tool.metadata.description,
                    "version": tool.metadata.version,
                    "author": tool.metadata.author,
                    "tags": tool.metadata.tags,
                    "parameters": [
                        {
                            "name": p.name,
                            "type": p.type.value,
                            "description": p.description,
                            "required": p.required
                        }
                        for p in tool.parameters
                    ]
                }
                for tool in self._tools.values()
            ],
            "count": len(self._tools)
        }
        
        with open(path, 'w') as f:
            json.dump(registry_data, f, indent=2)


# Global registry instance
_global_registry = ToolRegistry()

def get_registry() -> ToolRegistry:
    """Get the global tool registry"""
    return _global_registry
```

### 1.2 Built-in Tools Implementation

**File:** `tools/builtin_tools/__init__.py`

```python
"""Built-in tools for Chained agents"""

from .github_tool import GitHubIssueTool, GitHubPRTool
from .learning_data_tool import LearningDataTool, TrendAnalysisTool
from .world_model_tool import WorldModelTool
from .code_search_tool import CodeSearchTool

__all__ = [
    'GitHubIssueTool',
    'GitHubPRTool',
    'LearningDataTool',
    'TrendAnalysisTool',
    'WorldModelTool',
    'CodeSearchTool'
]
```

**File:** `tools/builtin_tools/learning_data_tool.py`

```python
"""
Learning Data Tool - Access Chained's learning data
Enables agents to query trends and patterns from learnings/
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, Any, List
from pathlib import Path

from tools.agent_tool_interface import (
    AgentTool, ToolMetadata, ToolParameter, ToolParameterType
)


class LearningDataTool(AgentTool):
    """Query learning data from learnings/ directory"""
    
    def __init__(self, learnings_dir: str = "learnings"):
        metadata = ToolMetadata(
            name="query_learning_data",
            description="Query trends, articles, and patterns from Chained's learning data sources (TLDR, HN, GitHub Trending)",
            version="1.0.0",
            author="agents-tech-lead",
            tags=["learning", "data", "trends", "research"]
        )
        super().__init__(metadata)
        
        self.learnings_dir = learnings_dir
        
        # Define parameters
        self.add_parameter(ToolParameter(
            name="query",
            type=ToolParameterType.STRING,
            description="Search query or keyword to find in learning data",
            required=True
        ))
        
        self.add_parameter(ToolParameter(
            name="days",
            type=ToolParameterType.INTEGER,
            description="Number of days to look back (default: 7)",
            required=False
        ))
        
        self.add_parameter(ToolParameter(
            name="source",
            type=ToolParameterType.STRING,
            description="Filter by source: 'tldr', 'hn', 'github', or 'all'",
            required=False,
            enum=["tldr", "hn", "github", "all"]
        ))
        
        self.add_parameter(ToolParameter(
            name="limit",
            type=ToolParameterType.INTEGER,
            description="Maximum number of results to return (default: 10)",
            required=False
        ))
    
    async def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute learning data query"""
        # Validate parameters
        is_valid, error = self.validate_parameters(**kwargs)
        if not is_valid:
            return {"success": False, "error": error}
        
        query = kwargs["query"]
        days = kwargs.get("days", 7)
        source_filter = kwargs.get("source", "all")
        limit = kwargs.get("limit", 10)
        
        try:
            results = self._search_learning_data(
                query, days, source_filter, limit
            )
            
            return {
                "success": True,
                "data": {
                    "query": query,
                    "results_count": len(results),
                    "results": results
                }
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": f"Error querying learning data: {str(e)}"
            }
    
    def _search_learning_data(
        self, 
        query: str, 
        days: int, 
        source_filter: str,
        limit: int
    ) -> List[Dict[str, Any]]:
        """Search learning data files"""
        results = []
        cutoff_date = datetime.now() - timedelta(days=days)
        
        # Get all learning files
        learning_files = Path(self.learnings_dir).glob("*.json")
        
        for file_path in learning_files:
            # Filter by source if specified
            if source_filter != "all":
                if source_filter not in file_path.name:
                    continue
            
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                
                # Check file timestamp
                file_date = datetime.fromisoformat(
                    data.get("timestamp", "").replace('+00:00', '')
                )
                if file_date < cutoff_date:
                    continue
                
                # Search in learnings
                for item in data.get("learnings", []):
                    if query.lower() in json.dumps(item).lower():
                        results.append({
                            "title": item.get("title", ""),
                            "description": item.get("description", ""),
                            "url": item.get("url", ""),
                            "source": data.get("source", ""),
                            "date": file_date.isoformat()
                        })
                        
                        if len(results) >= limit:
                            return results
            
            except Exception as e:
                # Skip files that can't be parsed
                continue
        
        return results


class TrendAnalysisTool(AgentTool):
    """Analyze trends across learning data"""
    
    def __init__(self, learnings_dir: str = "learnings"):
        metadata = ToolMetadata(
            name="analyze_trends",
            description="Analyze trending topics, technologies, and patterns from learning data over time",
            version="1.0.0",
            author="agents-tech-lead",
            tags=["learning", "trends", "analysis", "patterns"]
        )
        super().__init__(metadata)
        
        self.learnings_dir = learnings_dir
        
        self.add_parameter(ToolParameter(
            name="topic",
            type=ToolParameterType.STRING,
            description="Topic or technology to analyze trends for",
            required=True
        ))
        
        self.add_parameter(ToolParameter(
            name="days",
            type=ToolParameterType.INTEGER,
            description="Time period for trend analysis (default: 30)",
            required=False
        ))
    
    async def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute trend analysis"""
        is_valid, error = self.validate_parameters(**kwargs)
        if not is_valid:
            return {"success": False, "error": error}
        
        topic = kwargs["topic"]
        days = kwargs.get("days", 30)
        
        try:
            # Simplified trend analysis - count mentions over time
            mentions_by_day = self._count_mentions_by_day(topic, days)
            total_mentions = sum(mentions_by_day.values())
            
            # Calculate trend direction
            if len(mentions_by_day) >= 2:
                recent_half = list(mentions_by_day.values())[-len(mentions_by_day)//2:]
                older_half = list(mentions_by_day.values())[:len(mentions_by_day)//2]
                recent_avg = sum(recent_half) / len(recent_half) if recent_half else 0
                older_avg = sum(older_half) / len(older_half) if older_half else 0
                
                if recent_avg > older_avg * 1.5:
                    trend = "Rising"
                elif recent_avg < older_avg * 0.5:
                    trend = "Declining"
                else:
                    trend = "Stable"
            else:
                trend = "Insufficient data"
            
            return {
                "success": True,
                "data": {
                    "topic": topic,
                    "total_mentions": total_mentions,
                    "trend": trend,
                    "mentions_by_day": mentions_by_day,
                    "period_days": days
                }
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": f"Error analyzing trends: {str(e)}"
            }
    
    def _count_mentions_by_day(
        self, 
        topic: str, 
        days: int
    ) -> Dict[str, int]:
        """Count mentions of topic by day"""
        mentions = {}
        cutoff_date = datetime.now() - timedelta(days=days)
        
        learning_files = Path(self.learnings_dir).glob("*.json")
        
        for file_path in learning_files:
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                
                file_date = datetime.fromisoformat(
                    data.get("timestamp", "").replace('+00:00', '')
                )
                
                if file_date < cutoff_date:
                    continue
                
                date_key = file_date.strftime("%Y-%m-%d")
                
                # Count mentions in this file
                count = 0
                for item in data.get("learnings", []):
                    if topic.lower() in json.dumps(item).lower():
                        count += 1
                
                mentions[date_key] = mentions.get(date_key, 0) + count
            
            except Exception:
                continue
        
        return dict(sorted(mentions.items()))
```

### 1.3 Tool Registration and Initialization

**File:** `tools/initialize_tools.py`

```python
"""
Initialize and register all built-in tools
Called at system startup
"""

from tools.agent_tool_interface import get_registry
from tools.builtin_tools import (
    LearningDataTool,
    TrendAnalysisTool,
    # GitHubIssueTool,
    # GitHubPRTool,
    # WorldModelTool,
    # CodeSearchTool
)


def initialize_builtin_tools():
    """Register all built-in tools with global registry"""
    registry = get_registry()
    
    # Register learning data tools
    registry.register(LearningDataTool())
    registry.register(TrendAnalysisTool())
    
    # TODO: Register other tools as they're implemented
    # registry.register(GitHubIssueTool())
    # registry.register(GitHubPRTool())
    # registry.register(WorldModelTool())
    # registry.register(CodeSearchTool())
    
    # Save registry to file for documentation
    registry.save_registry(".github/agent-system/tool_registry.json")
    
    print(f"Registered {len(registry.list_tools())} tools")
    return registry


if __name__ == "__main__":
    # Can be run standalone to generate registry
    initialize_builtin_tools()
```

### 1.4 Agent Tool Declaration Format

**Example: Enhanced agent definition with tools**

**File:** `.github/agents/investigate-champion.md` (enhanced)

Add to agent definition:

```markdown
## 🔧 Agent Tools

This agent utilizes the following tools:

### Required Tools
- `query_learning_data` - Access to learning data for research
- `analyze_trends` - Trend analysis capabilities
- `world_model_query` - Access to world model data

### Optional Tools
- `code_search` - Search codebase for relevant patterns
- `github_issue_search` - Find related issues and discussions

## Tool Usage Patterns

When conducting research missions:
1. Use `query_learning_data` to find recent mentions
2. Use `analyze_trends` to identify patterns over time
3. Use `world_model_query` to understand geographic/tech context
4. Synthesize findings into comprehensive report
```

---

## ⏱️ Phase 2: Durable Workflow Support

### 2.1 Workflow Checkpointing Implementation

**File:** `tools/durable_workflow.py`

```python
"""
Durable Workflow Support - DBOS-inspired checkpointing for Chained agents
Enables fault-tolerant, long-running agent workflows
"""

import sqlite3
import json
from typing import Any, Dict, Optional, List, Callable
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
import asyncio


class WorkflowStatus(Enum):
    """Workflow execution status"""
    PENDING = "pending"
    RUNNING = "running"
    CHECKPOINTED = "checkpointed"
    COMPLETED = "completed"
    FAILED = "failed"
    RECOVERED = "recovered"


@dataclass
class WorkflowStep:
    """Individual step in a workflow"""
    step_id: str
    step_name: str
    status: WorkflowStatus
    state: Dict[str, Any]
    created_at: datetime
    completed_at: Optional[datetime] = None
    error: Optional[str] = None


class DurableWorkflow:
    """
    Durable workflow with automatic checkpointing
    
    Inspired by DBOS pattern - saves state after each step
    Enables recovery from failures without losing progress
    """
    
    def __init__(
        self, 
        workflow_id: str,
        workflow_name: str,
        db_path: str = ".github/agent-system/workflows.db"
    ):
        self.workflow_id = workflow_id
        self.workflow_name = workflow_name
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self._init_db()
        self.current_step: Optional[str] = None
    
    def _init_db(self):
        """Initialize database schema"""
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS workflows (
                workflow_id TEXT PRIMARY KEY,
                workflow_name TEXT NOT NULL,
                status TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                metadata TEXT
            )
        """)
        
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS workflow_steps (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                workflow_id TEXT NOT NULL,
                step_id TEXT NOT NULL,
                step_name TEXT NOT NULL,
                status TEXT NOT NULL,
                state TEXT NOT NULL,
                error TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP,
                FOREIGN KEY (workflow_id) REFERENCES workflows(workflow_id),
                UNIQUE(workflow_id, step_id)
            )
        """)
        
        self.conn.commit()
    
    def start(self, metadata: Optional[Dict[str, Any]] = None):
        """Start or resume workflow"""
        # Check if workflow exists
        cursor = self.conn.execute(
            "SELECT status FROM workflows WHERE workflow_id = ?",
            (self.workflow_id,)
        )
        row = cursor.fetchone()
        
        if row:
            # Resume existing workflow
            print(f"Resuming workflow {self.workflow_id} from status: {row[0]}")
        else:
            # Create new workflow
            self.conn.execute(
                "INSERT INTO workflows (workflow_id, workflow_name, status, metadata) VALUES (?, ?, ?, ?)",
                (self.workflow_id, self.workflow_name, WorkflowStatus.RUNNING.value, json.dumps(metadata or {}))
            )
            self.conn.commit()
            print(f"Started new workflow {self.workflow_id}")
    
    def checkpoint(
        self, 
        step_id: str,
        step_name: str,
        state: Dict[str, Any],
        status: WorkflowStatus = WorkflowStatus.CHECKPOINTED
    ):
        """
        Save workflow state at checkpoint
        
        This is the core durability feature - state is persisted
        so workflow can recover from exactly this point
        """
        self.current_step = step_id
        
        # Insert or update step
        self.conn.execute("""
            INSERT INTO workflow_steps (workflow_id, step_id, step_name, status, state, completed_at)
            VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(workflow_id, step_id) 
            DO UPDATE SET status = ?, state = ?, completed_at = CURRENT_TIMESTAMP
        """, (
            self.workflow_id, step_id, step_name, status.value, 
            json.dumps(state), status.value, json.dumps(state)
        ))
        
        # Update workflow timestamp
        self.conn.execute(
            "UPDATE workflows SET updated_at = CURRENT_TIMESTAMP WHERE workflow_id = ?",
            (self.workflow_id,)
        )
        
        self.conn.commit()
        print(f"Checkpointed workflow {self.workflow_id} at step {step_id}")
    
    def complete(self, final_state: Optional[Dict[str, Any]] = None):
        """Mark workflow as completed"""
        self.conn.execute(
            "UPDATE workflows SET status = ?, updated_at = CURRENT_TIMESTAMP, metadata = ? WHERE workflow_id = ?",
            (WorkflowStatus.COMPLETED.value, json.dumps(final_state or {}), self.workflow_id)
        )
        self.conn.commit()
        print(f"Completed workflow {self.workflow_id}")
    
    def fail(self, error: str, state: Optional[Dict[str, Any]] = None):
        """Mark workflow as failed"""
        if self.current_step:
            self.conn.execute(
                "UPDATE workflow_steps SET status = ?, error = ? WHERE workflow_id = ? AND step_id = ?",
                (WorkflowStatus.FAILED.value, error, self.workflow_id, self.current_step)
            )
        
        self.conn.execute(
            "UPDATE workflows SET status = ?, updated_at = CURRENT_TIMESTAMP, metadata = ? WHERE workflow_id = ?",
            (WorkflowStatus.FAILED.value, json.dumps(state or {"error": error}), self.workflow_id)
        )
        self.conn.commit()
        print(f"Failed workflow {self.workflow_id}: {error}")
    
    def recover(self) -> Optional[WorkflowStep]:
        """
        Recover workflow from last successful checkpoint
        
        Returns the last completed step so workflow can resume
        """
        cursor = self.conn.execute("""
            SELECT step_id, step_name, status, state, created_at, completed_at
            FROM workflow_steps
            WHERE workflow_id = ? AND status = ?
            ORDER BY completed_at DESC
            LIMIT 1
        """, (self.workflow_id, WorkflowStatus.CHECKPOINTED.value))
        
        row = cursor.fetchone()
        if not row:
            return None
        
        # Mark as recovered
        self.conn.execute(
            "UPDATE workflows SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE workflow_id = ?",
            (WorkflowStatus.RECOVERED.value, self.workflow_id)
        )
        self.conn.commit()
        
        return WorkflowStep(
            step_id=row[0],
            step_name=row[1],
            status=WorkflowStatus(row[2]),
            state=json.loads(row[3]),
            created_at=datetime.fromisoformat(row[4]),
            completed_at=datetime.fromisoformat(row[5]) if row[5] else None
        )
    
    def get_history(self) -> List[WorkflowStep]:
        """Get complete workflow history"""
        cursor = self.conn.execute("""
            SELECT step_id, step_name, status, state, created_at, completed_at, error
            FROM workflow_steps
            WHERE workflow_id = ?
            ORDER BY created_at ASC
        """, (self.workflow_id,))
        
        return [
            WorkflowStep(
                step_id=row[0],
                step_name=row[1],
                status=WorkflowStatus(row[2]),
                state=json.loads(row[3]),
                created_at=datetime.fromisoformat(row[4]),
                completed_at=datetime.fromisoformat(row[5]) if row[5] else None,
                error=row[6]
            )
            for row in cursor.fetchall()
        ]
    
    async def execute_step(
        self,
        step_id: str,
        step_name: str,
        step_func: Callable[[Dict[str, Any]], Dict[str, Any]],
        input_state: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute a workflow step with automatic checkpointing
        
        Args:
            step_id: Unique identifier for this step
            step_name: Human-readable step name
            step_func: Async function to execute (takes state, returns state)
            input_state: Input state for this step
        
        Returns:
            Updated state after step execution
        """
        try:
            # Execute step
            output_state = await step_func(input_state)
            
            # Checkpoint success
            self.checkpoint(step_id, step_name, output_state)
            
            return output_state
        
        except Exception as e:
            # Checkpoint failure
            self.fail(str(e), input_state)
            raise
    
    def close(self):
        """Close database connection"""
        self.conn.close()


class WorkflowManager:
    """Manage multiple workflows"""
    
    def __init__(self, db_path: str = ".github/agent-system/workflows.db"):
        self.db_path = db_path
    
    def create_workflow(self, workflow_id: str, workflow_name: str) -> DurableWorkflow:
        """Create a new workflow"""
        return DurableWorkflow(workflow_id, workflow_name, self.db_path)
    
    def list_workflows(self, status: Optional[WorkflowStatus] = None) -> List[Dict[str, Any]]:
        """List all workflows, optionally filtered by status"""
        conn = sqlite3.connect(self.db_path)
        
        if status:
            cursor = conn.execute(
                "SELECT workflow_id, workflow_name, status, created_at, updated_at FROM workflows WHERE status = ?",
                (status.value,)
            )
        else:
            cursor = conn.execute(
                "SELECT workflow_id, workflow_name, status, created_at, updated_at FROM workflows"
            )
        
        workflows = [
            {
                "workflow_id": row[0],
                "workflow_name": row[1],
                "status": row[2],
                "created_at": row[3],
                "updated_at": row[4]
            }
            for row in cursor.fetchall()
        ]
        
        conn.close()
        return workflows
```

### 2.2 Example: Research Mission with Checkpointing

```python
"""
Example: Long-running research mission with durable workflow
"""

import asyncio
from tools.durable_workflow import DurableWorkflow, WorkflowStatus
from tools.agent_tool_interface import get_registry


async def research_mission_workflow(mission_id: str, topic: str):
    """
    Conduct research mission with checkpointing
    
    This workflow can be interrupted and resumed without losing progress
    """
    workflow_id = f"research-{mission_id}"
    workflow = DurableWorkflow(workflow_id, "Research Mission Workflow")
    
    # Start or resume
    workflow.start(metadata={"mission_id": mission_id, "topic": topic})
    
    # Check if we're recovering
    last_step = workflow.recover()
    if last_step:
        print(f"Recovering from step: {last_step.step_name}")
        state = last_step.state
    else:
        state = {"mission_id": mission_id, "topic": topic}
    
    try:
        # Step 1: Query learning data
        if not last_step or last_step.step_id == "init":
            registry = get_registry()
            tool = registry.get("query_learning_data")
            
            result = await tool.execute(query=topic, days=30)
            state["learning_data"] = result["data"]
            
            workflow.checkpoint("query_data", "Query Learning Data", state)
        
        # Step 2: Analyze trends
        if not last_step or last_step.step_id in ["init", "query_data"]:
            tool = registry.get("analyze_trends")
            
            result = await tool.execute(topic=topic, days=30)
            state["trend_analysis"] = result["data"]
            
            workflow.checkpoint("analyze_trends", "Analyze Trends", state)
        
        # Step 3: Generate report (simulated)
        if not last_step or last_step.step_id in ["init", "query_data", "analyze_trends"]:
            # Simulate report generation
            await asyncio.sleep(1)  # Simulated work
            
            state["report"] = {
                "topic": topic,
                "findings": "Comprehensive analysis complete",
                "recommendations": ["Recommendation 1", "Recommendation 2"]
            }
            
            workflow.checkpoint("generate_report", "Generate Report", state)
        
        # Complete workflow
        workflow.complete(final_state=state)
        
        return state
    
    except Exception as e:
        workflow.fail(str(e), state)
        raise
    
    finally:
        workflow.close()


# Usage example
if __name__ == "__main__":
    asyncio.run(research_mission_workflow("46", "api-ai-agents"))
```

---

## 🔌 Phase 3: External Integration Framework

### 3.1 Integration Configuration

**File:** `.github/agent-system/integration_config.json`

```json
{
  "version": "1.0.0",
  "integrations": {
    "github_api": {
      "enabled": true,
      "auth_type": "token",
      "base_url": "https://api.github.com",
      "rate_limit": 5000,
      "tools": ["github_issue_tool", "github_pr_tool", "github_search_tool"]
    },
    "external_apis": {
      "enabled": false,
      "requires_approval": true,
      "allowed_domains": []
    }
  },
  "security": {
    "require_auth": true,
    "audit_logging": true,
    "rate_limiting": true
  }
}
```

### 3.2 Authentication Framework (Placeholder)

**File:** `tools/auth/tool_auth.py`

```python
"""
Tool authentication framework
Manages API keys, tokens, and access control
"""

import os
from typing import Optional, Dict
from dataclasses import dataclass


@dataclass
class ToolCredential:
    """Credential for tool authentication"""
    tool_name: str
    auth_type: str  # "token", "api_key", "oauth"
    credential: str
    metadata: Dict[str, str]


class ToolAuthManager:
    """Manage authentication for tools"""
    
    def __init__(self):
        self._credentials: Dict[str, ToolCredential] = {}
    
    def add_credential(self, cred: ToolCredential):
        """Add credential for a tool"""
        self._credentials[cred.tool_name] = cred
    
    def get_credential(self, tool_name: str) -> Optional[ToolCredential]:
        """Get credential for a tool"""
        # First check environment variables
        env_var = f"{tool_name.upper()}_TOKEN"
        if env_var in os.environ:
            return ToolCredential(
                tool_name=tool_name,
                auth_type="token",
                credential=os.environ[env_var],
                metadata={}
            )
        
        return self._credentials.get(tool_name)
    
    def has_credential(self, tool_name: str) -> bool:
        """Check if credential exists for tool"""
        return self.get_credential(tool_name) is not None
```

---

## 📊 Testing and Validation

### Test File: `tests/test_agent_tools.py`

```python
"""Tests for agent tool interface"""

import pytest
import asyncio
from tools.agent_tool_interface import (
    AgentTool, ToolMetadata, ToolParameter, ToolParameterType,
    ToolRegistry
)
from tools.builtin_tools.learning_data_tool import LearningDataTool


class MockTool(AgentTool):
    """Mock tool for testing"""
    
    def __init__(self):
        metadata = ToolMetadata(
            name="mock_tool",
            description="A mock tool for testing",
            version="1.0.0",
            author="test",
            tags=["test"]
        )
        super().__init__(metadata)
        
        self.add_parameter(ToolParameter(
            name="input",
            type=ToolParameterType.STRING,
            description="Test input",
            required=True
        ))
    
    async def execute(self, **kwargs):
        return {"success": True, "data": {"echo": kwargs.get("input")}}


@pytest.mark.asyncio
async def test_tool_execution():
    """Test basic tool execution"""
    tool = MockTool()
    result = await tool.execute(input="test")
    
    assert result["success"] is True
    assert result["data"]["echo"] == "test"


def test_tool_schema_generation():
    """Test OpenAI schema generation"""
    tool = MockTool()
    schema = tool.to_function_schema()
    
    assert schema["name"] == "mock_tool"
    assert "parameters" in schema
    assert "input" in schema["parameters"]["properties"]


def test_parameter_validation():
    """Test parameter validation"""
    tool = MockTool()
    
    # Missing required parameter
    is_valid, error = tool.validate_parameters()
    assert not is_valid
    assert "input" in error
    
    # Valid parameters
    is_valid, error = tool.validate_parameters(input="test")
    assert is_valid


def test_tool_registry():
    """Test tool registry"""
    registry = ToolRegistry()
    tool = MockTool()
    
    registry.register(tool)
    
    # Retrieve tool
    retrieved = registry.get("mock_tool")
    assert retrieved is not None
    assert retrieved.metadata.name == "mock_tool"
    
    # List tools
    tools = registry.list_tools()
    assert len(tools) == 1
    
    # OpenAI export
    functions = registry.to_openai_functions()
    assert len(functions) == 1
    assert functions[0]["name"] == "mock_tool"


@pytest.mark.asyncio
async def test_learning_data_tool():
    """Test learning data tool"""
    tool = LearningDataTool(learnings_dir="learnings")
    
    # Test with a real query
    result = await tool.execute(query="MCP", days=30)
    
    assert result["success"] is True
    assert "data" in result
```

---

## 📝 Documentation Requirements

### Tool Development Guide

**File:** `docs/AGENT_TOOLS_GUIDE.md` (to be created)

Structure:
1. Introduction to Agent Tools
2. Tool Interface Overview
3. Creating Your First Tool
4. Built-in Tools Reference
5. Best Practices
6. Testing Tools
7. Contributing Tools

### Agent Definition Updates

All agent definitions should be updated with:
- Tools they require
- Tools they optionally use
- Example tool usage patterns

---

## ✅ Implementation Checklist

### Phase 1: Tool Interface (Week 1)
- [ ] Implement `agent_tool_interface.py`
- [ ] Create `LearningDataTool`
- [ ] Create `TrendAnalysisTool`
- [ ] Implement tool registry
- [ ] Write unit tests
- [ ] Update agent definition format
- [ ] Create tool documentation

### Phase 2: Durable Workflows (Week 2)
- [ ] Implement `durable_workflow.py`
- [ ] Create database schema
- [ ] Add checkpointing to mission workflows
- [ ] Write integration tests
- [ ] Document workflow patterns
- [ ] Add recovery workflow to GitHub Actions

### Phase 3: External Integrations (Week 3-4)
- [ ] Design authentication framework
- [ ] Implement security layer
- [ ] Create integration configuration
- [ ] Add rate limiting
- [ ] Implement audit logging
- [ ] Write integration guide

---

## 🎯 Success Criteria

**Phase 1 Complete When:**
- ✅ 3+ built-in tools functional
- ✅ Tool registry operational
- ✅ 2+ agents using tools successfully
- ✅ All tests passing
- ✅ Documentation complete

**Phase 2 Complete When:**
- ✅ Workflow checkpointing works
- ✅ Recovery tested successfully
- ✅ Database schema stable
- ✅ Long-running mission uses checkpoints
- ✅ Recovery workflow automated

**Phase 3 Complete When:**
- ✅ Auth framework operational
- ✅ External API integration works
- ✅ Security audit passed
- ✅ Rate limiting enforced
- ✅ Integration guide published

---

**Document Status:** Ready for Review and Implementation  
**Author:** @agents-tech-lead  
**Date:** 2025-11-18  
**Version:** 1.0
