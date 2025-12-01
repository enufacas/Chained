"""
Team Orchestrator - Turn-Based Multi-Agent Coordination
========================================================

This module provides turn-based orchestration for multi-agent teams.
It supports:

1. Configurable "recipes" - sequences of agents for tasks
2. Turn-based execution with context passing
3. Sequential and parallel agent execution modes
4. Progress tracking and artifact collection
5. Recipe management (create, save, load)
"""

import asyncio
import json
import os
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Callable
from dataclasses import dataclass, field, asdict
from enum import Enum

import httpx

# Import registry if available
try:
    from shared.agent_registry import get_registry, AgentRegistry, RegisteredAgent, AgentStatus
except ImportError:
    # Fallback for standalone usage
    AgentRegistry = None
    get_registry = lambda: None


class TurnStatus(str, Enum):
    """Status of a turn in the orchestration."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class ExecutionMode(str, Enum):
    """Execution mode for agent steps."""
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"


@dataclass
class RecipeStep:
    """A single step in an agent recipe."""
    agent_id: str
    instruction: str
    required: bool = True
    timeout_seconds: int = 120
    depends_on: List[str] = field(default_factory=list)  # List of step IDs
    execution_mode: ExecutionMode = ExecutionMode.SEQUENTIAL
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            **asdict(self),
            "execution_mode": self.execution_mode.value,
        }


@dataclass
class Recipe:
    """A recipe defining a sequence of agent steps."""
    id: str
    name: str
    description: str
    goal: str
    steps: List[RecipeStep] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    tags: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            **asdict(self),
            "steps": [s.to_dict() for s in self.steps],
        }


@dataclass
class TurnResult:
    """Result of a single turn/step execution."""
    step_index: int
    agent_id: str
    agent_name: str
    status: TurnStatus
    started_at: str
    completed_at: Optional[str] = None
    duration_ms: Optional[int] = None
    task_id: Optional[str] = None
    message: Optional[str] = None
    artifacts: List[Dict[str, Any]] = field(default_factory=list)
    error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            **asdict(self),
            "status": self.status.value,
        }


@dataclass
class TeamSession:
    """A team execution session."""
    id: str
    recipe_id: str
    recipe_name: str
    goal: str
    status: TurnStatus
    current_turn: int
    total_turns: int
    created_at: str
    updated_at: str
    context: Dict[str, Any] = field(default_factory=dict)
    turn_results: List[TurnResult] = field(default_factory=list)
    final_result: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            **asdict(self),
            "status": self.status.value,
            "turn_results": [t.to_dict() for t in self.turn_results],
        }


# =============================================================================
# Built-in Recipes
# =============================================================================

BUILTIN_RECIPES = {
    "blog-pipeline": Recipe(
        id="blog-pipeline",
        name="Blog Writing Pipeline",
        description="Research, analyze trends, and write a blog post",
        goal="Create a well-researched, SEO-optimized blog post",
        steps=[
            RecipeStep(
                agent_id="academic-research",
                instruction="Research the topic thoroughly and identify key concepts, trends, and insights.",
            ),
            RecipeStep(
                agent_id="google-trends",
                instruction="Analyze trending keywords and SEO opportunities based on the research.",
                depends_on=["academic-research"],
            ),
            RecipeStep(
                agent_id="blog-writer",
                instruction="Write a comprehensive blog post using the research and SEO insights.",
                depends_on=["academic-research", "google-trends"],
            ),
        ],
        tags=["content", "blog", "seo"],
    ),
    "technical-review": Recipe(
        id="technical-review",
        name="Technical Content Review",
        description="Research, write, and review technical content with code examples",
        goal="Create reviewed technical content with code samples",
        steps=[
            RecipeStep(
                agent_id="academic-research",
                instruction="Research the technical topic and gather key information.",
            ),
            RecipeStep(
                agent_id="data-analyst",
                instruction="Analyze the research data and identify key statistics and patterns.",
                depends_on=["academic-research"],
            ),
            RecipeStep(
                agent_id="blog-writer",
                instruction="Write technical content including code examples.",
                depends_on=["academic-research", "data-analyst"],
            ),
            RecipeStep(
                agent_id="code-reviewer",
                instruction="Review any code examples for best practices and correctness.",
                depends_on=["blog-writer"],
            ),
        ],
        tags=["technical", "code", "review"],
    ),
    "visual-content": Recipe(
        id="visual-content",
        name="Visual Content Creation",
        description="Research and create visual content with diagrams",
        goal="Create informative content with supporting visuals",
        steps=[
            RecipeStep(
                agent_id="academic-research",
                instruction="Research the topic and identify key concepts to visualize.",
            ),
            RecipeStep(
                agent_id="image-generator",
                instruction="Create diagrams and visual content based on the research.",
                depends_on=["academic-research"],
            ),
            RecipeStep(
                agent_id="blog-writer",
                instruction="Write content that incorporates and explains the visuals.",
                depends_on=["academic-research", "image-generator"],
            ),
        ],
        tags=["visual", "diagrams", "content"],
    ),
    "data-analysis": Recipe(
        id="data-analysis",
        name="Data Analysis Pipeline",
        description="Analyze data and create visualizations with insights",
        goal="Generate comprehensive data analysis with visual reports",
        steps=[
            RecipeStep(
                agent_id="data-analyst",
                instruction="Analyze the provided data and generate key insights.",
            ),
            RecipeStep(
                agent_id="image-generator",
                instruction="Create charts and visualizations based on the analysis.",
                depends_on=["data-analyst"],
            ),
            RecipeStep(
                agent_id="blog-writer",
                instruction="Write a report summarizing the analysis and visualizations.",
                depends_on=["data-analyst", "image-generator"],
            ),
        ],
        tags=["data", "analysis", "visualization"],
    ),
}


class TeamOrchestrator:
    """
    Turn-based multi-agent team orchestrator.
    
    Manages the execution of agent "recipes" - configured sequences
    of agent tasks that work together to accomplish a goal.
    """
    
    def __init__(self, timeout: float = 120.0):
        self._timeout = timeout
        self._client: Optional[httpx.AsyncClient] = None
        self._sessions: Dict[str, TeamSession] = {}
        self._recipes: Dict[str, Recipe] = dict(BUILTIN_RECIPES)
        self._registry: Optional[AgentRegistry] = None
        
        # Callbacks for progress updates
        self._on_turn_start: Optional[Callable] = None
        self._on_turn_complete: Optional[Callable] = None
        self._on_session_complete: Optional[Callable] = None
    
    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=self._timeout)
        return self._client
    
    async def close(self):
        """Close HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None
    
    def set_registry(self, registry: AgentRegistry):
        """Set the agent registry for discovery."""
        self._registry = registry
    
    # =========================================================================
    # Recipe Management
    # =========================================================================
    
    def get_recipe(self, recipe_id: str) -> Optional[Recipe]:
        """Get a recipe by ID."""
        return self._recipes.get(recipe_id)
    
    def get_all_recipes(self) -> List[Recipe]:
        """Get all available recipes."""
        return list(self._recipes.values())
    
    def add_recipe(self, recipe: Recipe):
        """Add or update a recipe."""
        self._recipes[recipe.id] = recipe
    
    def remove_recipe(self, recipe_id: str):
        """Remove a recipe."""
        if recipe_id in self._recipes and recipe_id not in BUILTIN_RECIPES:
            del self._recipes[recipe_id]
    
    def create_recipe(
        self,
        name: str,
        description: str,
        goal: str,
        steps: List[Dict[str, Any]],
        tags: Optional[List[str]] = None,
    ) -> Recipe:
        """Create a new recipe from configuration."""
        recipe_id = f"recipe-{uuid.uuid4().hex[:8]}"
        recipe = Recipe(
            id=recipe_id,
            name=name,
            description=description,
            goal=goal,
            steps=[
                RecipeStep(
                    agent_id=s["agent_id"],
                    instruction=s.get("instruction", ""),
                    required=s.get("required", True),
                    timeout_seconds=s.get("timeout_seconds", 120),
                    depends_on=s.get("depends_on", []),
                    execution_mode=ExecutionMode(s.get("execution_mode", "sequential")),
                )
                for s in steps
            ],
            tags=tags or [],
        )
        self._recipes[recipe_id] = recipe
        return recipe
    
    # =========================================================================
    # Session Management
    # =========================================================================
    
    def get_session(self, session_id: str) -> Optional[TeamSession]:
        """Get a session by ID."""
        return self._sessions.get(session_id)
    
    def get_all_sessions(self) -> List[TeamSession]:
        """Get all sessions."""
        return list(self._sessions.values())
    
    def get_active_sessions(self) -> List[TeamSession]:
        """Get all active (running) sessions."""
        return [
            s for s in self._sessions.values()
            if s.status in (TurnStatus.PENDING, TurnStatus.RUNNING)
        ]
    
    # =========================================================================
    # Execution
    # =========================================================================
    
    async def _call_agent(
        self,
        agent_url: str,
        message: str,
        context: Dict[str, Any],
        reference_task_ids: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Call an A2A agent."""
        client = await self._get_client()
        
        payload = {
            "message": {
                "role": "user",
                "parts": [{"text": message}],
            },
            "contextId": context.get("context_id", f"team-{uuid.uuid4().hex[:8]}"),
            "metadata": context,
        }
        
        if reference_task_ids:
            payload["referenceTaskIds"] = reference_task_ids
        
        response = await client.post(
            f"{agent_url}/a2a/tasks",
            json=payload,
        )
        response.raise_for_status()
        return response.json()
    
    def _get_agent_url(self, agent_id: str) -> Optional[str]:
        """Get agent URL from registry or environment."""
        # Try registry first
        if self._registry:
            agent = self._registry.get_agent(agent_id)
            if agent and agent.status == AgentStatus.AVAILABLE:
                return agent.url
        
        # Fall back to environment variables
        from shared.agent_registry import AgentRegistry
        url_env = AgentRegistry.DEFAULT_AGENTS.get(agent_id, {}).get("url_env")
        if url_env:
            return os.getenv(url_env)
        
        return None
    
    async def execute_turn(
        self,
        session: TeamSession,
        step: RecipeStep,
        step_index: int,
    ) -> TurnResult:
        """Execute a single turn in the session."""
        started_at = datetime.utcnow().isoformat()
        
        turn_result = TurnResult(
            step_index=step_index,
            agent_id=step.agent_id,
            agent_name=step.agent_id,
            status=TurnStatus.RUNNING,
            started_at=started_at,
        )
        
        # Notify turn start
        if self._on_turn_start:
            await self._on_turn_start(session, turn_result)
        
        agent_url = self._get_agent_url(step.agent_id)
        if not agent_url:
            turn_result.status = TurnStatus.FAILED
            turn_result.error = f"Agent {step.agent_id} not available"
            turn_result.completed_at = datetime.utcnow().isoformat()
            
            if not step.required:
                turn_result.status = TurnStatus.SKIPPED
            
            return turn_result
        
        try:
            # Build instruction with context
            full_instruction = f"""Goal: {session.goal}

{step.instruction}

Previous context and findings:
{json.dumps(session.context, indent=2)}"""
            
            # Get reference task IDs from dependencies
            reference_task_ids = []
            for dep in step.depends_on:
                for prev_result in session.turn_results:
                    if prev_result.agent_id == dep and prev_result.task_id:
                        reference_task_ids.append(prev_result.task_id)
            
            # Call the agent
            task = await self._call_agent(
                agent_url,
                full_instruction,
                session.context,
                reference_task_ids,
            )
            
            completed_at = datetime.utcnow()
            duration_ms = int(
                (completed_at - datetime.fromisoformat(started_at)).total_seconds() * 1000
            )
            
            turn_result.task_id = task.get("id")
            turn_result.status = TurnStatus.COMPLETED
            turn_result.completed_at = completed_at.isoformat()
            turn_result.duration_ms = duration_ms
            
            # Extract message
            if task.get("status", {}).get("message", {}).get("parts"):
                turn_result.message = task["status"]["message"]["parts"][0].get("text", "")
            
            # Extract artifacts and update context
            artifacts = task.get("artifacts", [])
            turn_result.artifacts = artifacts
            
            # Add artifacts to session context
            session.context[f"{step.agent_id}_artifacts"] = artifacts
            session.context[f"{step.agent_id}_task_id"] = task.get("id")
            
            # Parse JSON artifacts into context
            for artifact in artifacts:
                if artifact.get("type") == "application/json":
                    try:
                        data = json.loads(artifact.get("data", "{}"))
                        session.context[f"{step.agent_id}_{artifact.get('name', 'data')}"] = data
                    except json.JSONDecodeError:
                        pass
            
        except Exception as e:
            turn_result.status = TurnStatus.FAILED
            turn_result.error = str(e)
            turn_result.completed_at = datetime.utcnow().isoformat()
            
            if not step.required:
                turn_result.status = TurnStatus.SKIPPED
        
        # Notify turn complete
        if self._on_turn_complete:
            await self._on_turn_complete(session, turn_result)
        
        return turn_result
    
    async def execute_session(
        self,
        recipe_id: str,
        goal: str,
        initial_context: Optional[Dict[str, Any]] = None,
    ) -> TeamSession:
        """
        Execute a full team session using a recipe.
        
        Args:
            recipe_id: ID of the recipe to execute
            goal: The specific goal for this session
            initial_context: Optional initial context data
            
        Returns:
            TeamSession with results
        """
        recipe = self.get_recipe(recipe_id)
        if not recipe:
            raise ValueError(f"Recipe {recipe_id} not found")
        
        # Create session
        session_id = f"session-{uuid.uuid4().hex[:12]}"
        now = datetime.utcnow().isoformat()
        
        session = TeamSession(
            id=session_id,
            recipe_id=recipe_id,
            recipe_name=recipe.name,
            goal=goal,
            status=TurnStatus.PENDING,
            current_turn=0,
            total_turns=len(recipe.steps),
            created_at=now,
            updated_at=now,
            context=initial_context or {},
        )
        
        # Add goal to context
        session.context["goal"] = goal
        session.context["context_id"] = session_id
        
        self._sessions[session_id] = session
        
        # Execute turns
        session.status = TurnStatus.RUNNING
        
        for i, step in enumerate(recipe.steps):
            session.current_turn = i + 1
            session.updated_at = datetime.utcnow().isoformat()
            
            turn_result = await self.execute_turn(session, step, i)
            session.turn_results.append(turn_result)
            
            # Stop on required failure
            if turn_result.status == TurnStatus.FAILED and step.required:
                session.status = TurnStatus.FAILED
                break
        
        # Mark complete
        if session.status != TurnStatus.FAILED:
            session.status = TurnStatus.COMPLETED
        
        session.updated_at = datetime.utcnow().isoformat()
        
        # Build final result
        session.final_result = {
            "session_id": session_id,
            "recipe": recipe.name,
            "goal": goal,
            "status": session.status.value,
            "turns_completed": len([t for t in session.turn_results if t.status == TurnStatus.COMPLETED]),
            "turns_total": len(recipe.steps),
            "context": session.context,
        }
        
        # Notify session complete
        if self._on_session_complete:
            await self._on_session_complete(session)
        
        return session
    
    # =========================================================================
    # Callback Registration
    # =========================================================================
    
    def on_turn_start(self, callback: Callable):
        """Register callback for turn start events."""
        self._on_turn_start = callback
    
    def on_turn_complete(self, callback: Callable):
        """Register callback for turn complete events."""
        self._on_turn_complete = callback
    
    def on_session_complete(self, callback: Callable):
        """Register callback for session complete events."""
        self._on_session_complete = callback


# Global orchestrator instance
_orchestrator: Optional[TeamOrchestrator] = None


def get_orchestrator() -> TeamOrchestrator:
    """Get or create global team orchestrator."""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = TeamOrchestrator()
    return _orchestrator
