# AI-Native Control Plane — LangChain Tool Definitions

*This document is part of the AI-Native Control Plane specification defined in `.github/copilot/tasks/ai-native-control-plane.md`*

## Overview

This document defines the **10 core LangChain tools** that enable AI agents to operate cloud infrastructure autonomously. These tools provide deterministic, typed interfaces for all infrastructure operations, replacing manual Terraform and CI/CD workflows.

### Design Principles

All tools must adhere to:

1. **Deterministic Schemas**: Fixed input/output structures with strong typing
2. **Structured JSON I/O**: All data serialized as JSON for parsing and validation
3. **Safe Error Escalation**: Graceful failure handling with actionable error messages
4. **Comprehensive Logging**: OpenTelemetry traces, structured logs, correlation IDs
5. **Explicit Versioning**: Tool version compatibility and schema evolution

---

## Tool Architecture

### Common Patterns

All tools share these foundational elements:

```python
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
import hashlib
import json

class ToolInput(BaseModel):
    """Base schema for all tool inputs"""
    correlation_id: str = Field(..., description="Unique correlation ID for tracing")
    dry_run: bool = Field(default=False, description="Execute in validation-only mode")
    version: str = Field(default="1.0.0", description="Tool schema version")

class ToolOutput(BaseModel):
    """Base schema for all tool outputs"""
    success: bool = Field(..., description="Operation success status")
    correlation_id: str = Field(..., description="Matching correlation ID")
    operation_id: Optional[str] = Field(None, description="Logged operation ID in state-db")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    execution_time_ms: int = Field(..., description="Execution duration in milliseconds")
    result: Optional[Dict[str, Any]] = Field(None, description="Tool-specific result data")
    error: Optional[str] = Field(None, description="Error message if failed")
    warnings: List[str] = Field(default_factory=list, description="Non-fatal warnings")
```

### Deterministic ID Generation

All tools use SHA256-based IDs for reproducibility:

```python
def generate_deterministic_id(prefix: str, *components: str) -> str:
    """Generate deterministic SHA256 hash-based ID"""
    content = ":".join([prefix] + list(components))
    return f"{prefix}:{hashlib.sha256(content.encode()).hexdigest()[:16]}"

# Example usage:
app_id = generate_deterministic_id("app", "my-forum", "2025-01-01T00:00:00Z")
# Result: "app:a3f2d9e1b4c8f7a2"
```

### Error Classification

```python
class ErrorSeverity(str, Enum):
    WARNING = "warning"      # Non-blocking, operation continues
    RECOVERABLE = "recoverable"  # Retry may succeed
    FATAL = "fatal"          # Operation cannot proceed
    POLICY = "policy"        # Blocked by policy rules

class ToolError(BaseModel):
    severity: ErrorSeverity
    code: str  # e.g., "INVALID_SCHEMA", "GCP_QUOTA_EXCEEDED"
    message: str
    retry_after_seconds: Optional[int] = None
    remediation_hint: Optional[str] = None
```

---

## 1. create_app_spec

**Purpose**: Generate a validated application specification from natural language requirements.

### Input Schema

```python
class CreateAppSpecInput(ToolInput):
    user_request: str = Field(..., description="Natural language app description")
    app_type: str = Field(..., description="static|dynamic|event-driven|scheduled")
    constraints: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Resource constraints (memory, CPU, budget)"
    )
    existing_context: Optional[List[str]] = Field(
        default=None,
        description="Related app IDs or pattern IDs from memory"
    )
```

### Output Schema

```python
class AppSpec(BaseModel):
    app_id: str = Field(..., description="Deterministic app identifier")
    name: str = Field(..., description="Human-readable app name")
    type: str = Field(..., description="static|dynamic|event-driven|scheduled")
    description: str = Field(..., description="AI-generated app description")
    
    # Resource requirements
    resources: Dict[str, Any] = Field(..., description="Memory, CPU, storage specs")
    
    # Components
    components: List[Dict[str, Any]] = Field(
        ...,
        description="Frontend, backend, database, storage components"
    )
    
    # Dependencies
    dependencies: List[str] = Field(
        default_factory=list,
        description="Required libraries/frameworks"
    )
    
    # Deployment config
    deployment: Dict[str, Any] = Field(
        ...,
        description="Domain, scaling, network configuration"
    )
    
    # Validation
    validation_status: str = Field(..., description="passed|failed|needs_review")
    validation_errors: List[str] = Field(default_factory=list)
    
    # Metadata
    created_at: datetime
    plan_hash: str = Field(..., description="SHA256 hash of spec for versioning")

class CreateAppSpecOutput(ToolOutput):
    result: Optional[AppSpec] = None
```

### Error Codes

- `INVALID_APP_TYPE`: Unknown app type specified
- `CONSTRAINT_VIOLATION`: Request exceeds resource constraints
- `AMBIGUOUS_REQUEST`: Cannot determine intent unambiguously
- `MISSING_REQUIRED_FIELD`: Essential specification field missing

### Example Usage

```python
from langchain.tools import StructuredTool

create_app_spec_tool = StructuredTool.from_function(
    func=create_app_spec_handler,
    name="create_app_spec",
    description="Generate validated app specification from natural language",
    args_schema=CreateAppSpecInput,
    return_direct=False
)
```

---

## 2. build_static_app

**Purpose**: Generate complete static website code (HTML, CSS, JavaScript) from specification.

### Input Schema

```python
class BuildStaticAppInput(ToolInput):
    app_spec: AppSpec = Field(..., description="Validated app specification")
    template_id: Optional[str] = Field(
        default=None,
        description="Optional template pattern from vector memory"
    )
    style_preferences: Optional[Dict[str, str]] = Field(
        default=None,
        description="UI framework, color scheme, typography"
    )
```

### Output Schema

```python
class StaticAsset(BaseModel):
    path: str = Field(..., description="Relative file path (e.g., 'index.html')")
    content: str = Field(..., description="File content")
    content_type: str = Field(..., description="MIME type")
    size_bytes: int = Field(..., description="Content size")
    hash: str = Field(..., description="SHA256 content hash")

class BuildStaticAppOutput(ToolOutput):
    result: Optional[Dict[str, Any]] = Field(None)
    
    class Result(BaseModel):
        build_id: str = Field(..., description="Deterministic build identifier")
        assets: List[StaticAsset] = Field(..., description="Generated files")
        total_size_bytes: int
        preview_url: Optional[str] = None
        lighthouse_score: Optional[int] = Field(
            None,
            description="Estimated performance score (0-100)"
        )
```

### Error Codes

- `TEMPLATE_NOT_FOUND`: Specified template ID doesn't exist
- `BUILD_FAILED`: Code generation encountered errors
- `ASSET_TOO_LARGE`: Generated asset exceeds size limits
- `INVALID_CONTENT`: Generated content failed validation

---

## 3. build_dynamic_app

**Purpose**: Generate backend service code (API, database schema, business logic) from specification.

### Input Schema

```python
class BuildDynamicAppInput(ToolInput):
    app_spec: AppSpec = Field(..., description="Validated app specification")
    framework: str = Field(
        default="fastapi",
        description="Backend framework: fastapi|flask|express"
    )
    database_type: str = Field(
        default="postgresql",
        description="Database: postgresql|mongodb|firestore"
    )
    api_style: str = Field(
        default="rest",
        description="API style: rest|graphql|grpc"
    )
```

### Output Schema

```python
class DynamicServiceArtifact(BaseModel):
    type: str = Field(..., description="code|schema|config|dockerfile")
    path: str = Field(..., description="File path in service structure")
    content: str = Field(..., description="File content")
    language: Optional[str] = Field(None, description="Programming language")
    hash: str = Field(..., description="Content hash")

class BuildDynamicAppOutput(ToolOutput):
    result: Optional[Dict[str, Any]] = None
    
    class Result(BaseModel):
        build_id: str = Field(..., description="Deterministic build identifier")
        artifacts: List[DynamicServiceArtifact] = Field(
            ...,
            description="Generated service files"
        )
        
        # Service metadata
        service_name: str
        framework: str
        runtime: str = Field(..., description="python39|node18|go121")
        
        # Database
        database_schema: Optional[str] = Field(
            None,
            description="SQL/NoSQL schema definition"
        )
        
        # API
        api_spec: Optional[str] = Field(
            None,
            description="OpenAPI/GraphQL schema"
        )
        
        # Container
        dockerfile: str = Field(..., description="Generated Dockerfile")
        estimated_image_size_mb: int
        
        # Endpoints
        endpoints: List[Dict[str, str]] = Field(
            default_factory=list,
            description="API endpoint paths and methods"
        )
```

### Error Codes

- `UNSUPPORTED_FRAMEWORK`: Requested framework not available
- `SCHEMA_GENERATION_FAILED`: Database schema generation failed
- `CODE_GENERATION_FAILED`: Service code generation failed
- `DOCKERFILE_INVALID`: Generated Dockerfile failed validation

---

## 4. deploy_static_site

**Purpose**: Deploy static website to GCS bucket with CDN and custom domain.

### Input Schema

```python
class DeployStaticSiteInput(ToolInput):
    build_id: str = Field(..., description="Build identifier from build_static_app")
    app_id: str = Field(..., description="Application identifier")
    assets: List[StaticAsset] = Field(..., description="Files to deploy")
    
    # Deployment config
    bucket_name: Optional[str] = Field(
        None,
        description="GCS bucket name (auto-generated if not provided)"
    )
    custom_domain: Optional[str] = Field(
        None,
        description="Custom domain (e.g., 'my-app.example.com')"
    )
    enable_cdn: bool = Field(default=True, description="Enable Cloud CDN")
    enable_ssl: bool = Field(default=True, description="Enable HTTPS")
    
    # Caching
    cache_control: str = Field(
        default="public, max-age=3600",
        description="Cache-Control header value"
    )
```

### Output Schema

```python
class DeployStaticSiteOutput(ToolOutput):
    result: Optional[Dict[str, Any]] = None
    
    class Result(BaseModel):
        deployment_id: str = Field(..., description="Deployment identifier")
        app_id: str
        
        # URLs
        public_url: str = Field(..., description="Primary access URL")
        cdn_url: Optional[str] = Field(None, description="CDN endpoint")
        custom_domain_url: Optional[str] = None
        
        # Infrastructure
        bucket_name: str
        bucket_location: str = Field(..., description="GCS region")
        total_size_bytes: int
        
        # Status
        deployed_at: datetime
        deployment_status: str = Field(
            ...,
            description="success|partial|failed"
        )
        
        # Health
        health_check_url: str
        health_status: str = Field(..., description="healthy|unhealthy")
        
        # Costs
        estimated_monthly_cost_usd: float = Field(
            ...,
            description="Estimated monthly hosting cost"
        )
```

### Error Codes

- `BUCKET_CREATION_FAILED`: GCS bucket creation failed
- `UPLOAD_FAILED`: Asset upload failed
- `CDN_CONFIG_FAILED`: CDN configuration failed
- `DOMAIN_MAPPING_FAILED`: Custom domain mapping failed
- `SSL_CERT_FAILED`: SSL certificate provisioning failed

---

## 5. deploy_dynamic_service

**Purpose**: Deploy containerized backend service to Cloud Run with auto-scaling.

### Input Schema

```python
class DeployDynamicServiceInput(ToolInput):
    build_id: str = Field(..., description="Build identifier from build_dynamic_app")
    app_id: str = Field(..., description="Application identifier")
    artifacts: List[DynamicServiceArtifact] = Field(
        ...,
        description="Service code and configs"
    )
    
    # Compute configuration
    cpu: str = Field(default="1", description="CPU allocation (1, 2, 4)")
    memory: str = Field(default="512Mi", description="Memory allocation")
    max_instances: int = Field(default=10, description="Auto-scaling maximum")
    min_instances: int = Field(default=0, description="Min instances (0 = scale to zero)")
    
    # Network
    allow_public: bool = Field(
        default=True,
        description="Allow unauthenticated access"
    )
    custom_domain: Optional[str] = None
    
    # Environment
    env_vars: Dict[str, str] = Field(
        default_factory=dict,
        description="Environment variables"
    )
    secrets: List[str] = Field(
        default_factory=list,
        description="Secret Manager secret names"
    )
    
    # Database
    database_config: Optional[Dict[str, Any]] = Field(
        None,
        description="Cloud SQL or Firestore configuration"
    )
```

### Output Schema

```python
class DeployDynamicServiceOutput(ToolOutput):
    result: Optional[Dict[str, Any]] = None
    
    class Result(BaseModel):
        deployment_id: str
        app_id: str
        service_name: str
        
        # URLs
        service_url: str = Field(..., description="Cloud Run service URL")
        custom_domain_url: Optional[str] = None
        
        # Container
        image_uri: str = Field(..., description="Container Registry image")
        image_size_mb: int
        
        # Configuration
        region: str = Field(..., description="GCP region")
        cpu: str
        memory: str
        max_instances: int
        
        # Status
        deployed_at: datetime
        deployment_status: str = Field(
            ...,
            description="success|partial|failed"
        )
        
        # Health
        health_check_url: str
        health_status: str = Field(..., description="healthy|unhealthy")
        startup_time_ms: int = Field(
            ...,
            description="Cold start time"
        )
        
        # Database
        database_instance: Optional[str] = None
        database_connection_name: Optional[str] = None
        
        # Costs
        estimated_monthly_cost_usd: float
```

### Error Codes

- `IMAGE_BUILD_FAILED`: Container image build failed
- `IMAGE_PUSH_FAILED`: Image push to registry failed
- `SERVICE_DEPLOYMENT_FAILED`: Cloud Run deployment failed
- `DATABASE_PROVISION_FAILED`: Database provisioning failed
- `DOMAIN_MAPPING_FAILED`: Custom domain mapping failed
- `HEALTH_CHECK_FAILED`: Service failed health checks

---

## 6. update_app_state

**Purpose**: Update application record in state-db with deployment status and metadata.

### Input Schema

```python
class UpdateAppStateInput(ToolInput):
    app_id: str = Field(..., description="Application identifier")
    
    # State updates
    status: Optional[str] = Field(
        None,
        description="pending|building|deploying|active|failed|archived"
    )
    deployment_id: Optional[str] = None
    
    # URLs
    primary_url: Optional[str] = None
    cdn_url: Optional[str] = None
    
    # Infrastructure references
    infra_objects: Optional[List[Dict[str, Any]]] = Field(
        None,
        description="GCS buckets, Cloud Run services, databases"
    )
    
    # Metadata updates
    metadata: Optional[Dict[str, Any]] = Field(
        None,
        description="Additional app metadata"
    )
    
    # Costs
    estimated_monthly_cost_usd: Optional[float] = None
```

### Output Schema

```python
class UpdateAppStateOutput(ToolOutput):
    result: Optional[Dict[str, Any]] = None
    
    class Result(BaseModel):
        app_id: str
        updated_fields: List[str] = Field(
            ...,
            description="List of fields that were updated"
        )
        previous_status: Optional[str] = None
        new_status: str
        updated_at: datetime
        
        # Operation logging
        operation_id: str = Field(
            ...,
            description="Event log entry in operations table"
        )
```

### Error Codes

- `APP_NOT_FOUND`: Application ID doesn't exist
- `INVALID_STATUS_TRANSITION`: Status change violates state machine
- `DATABASE_WRITE_FAILED`: State-db update failed
- `CONFLICT`: Concurrent modification detected

---

## 7. fetch_memory_context

**Purpose**: Retrieve relevant patterns and historical context from vector-db for planning.

### Input Schema

```python
class FetchMemoryContextInput(ToolInput):
    query: str = Field(..., description="Semantic query for similar patterns")
    pattern_types: Optional[List[str]] = Field(
        default=None,
        description="Filter: template|style|intent|error_repair|system_upgrade|migration"
    )
    limit: int = Field(default=10, description="Maximum results to return")
    min_similarity: float = Field(
        default=0.7,
        description="Minimum cosine similarity (0.0-1.0)"
    )
    
    # Context filters
    app_type: Optional[str] = Field(
        None,
        description="Filter by app type if provided"
    )
    tags: Optional[List[str]] = Field(
        None,
        description="Filter by metadata tags"
    )
```

### Output Schema

```python
class MemoryPattern(BaseModel):
    pattern_id: str = Field(..., description="Unique pattern identifier")
    pattern_type: str
    
    # Content
    description: str = Field(..., description="Human-readable description")
    content: Dict[str, Any] = Field(
        ...,
        description="Pattern data (spec, code, config)"
    )
    
    # Similarity
    similarity_score: float = Field(
        ...,
        description="Cosine similarity to query (0.0-1.0)"
    )
    
    # Metadata
    created_at: datetime
    used_count: int = Field(..., description="Times this pattern was used")
    success_rate: float = Field(
        ...,
        description="Successful applications (0.0-1.0)"
    )
    tags: List[str]

class FetchMemoryContextOutput(ToolOutput):
    result: Optional[Dict[str, Any]] = None
    
    class Result(BaseModel):
        query: str
        patterns: List[MemoryPattern] = Field(
            ...,
            description="Matching patterns ordered by similarity"
        )
        total_found: int
        query_time_ms: int
        
        # Recommendations
        recommended_pattern_id: Optional[str] = Field(
            None,
            description="Best match based on success rate + similarity"
        )
```

### Error Codes

- `VECTOR_DB_UNAVAILABLE`: Vector database connection failed
- `QUERY_TIMEOUT`: Query exceeded time limit
- `INVALID_PATTERN_TYPE`: Unknown pattern type specified

---

## 8. write_memory_context

**Purpose**: Store successful operation patterns in vector-db for future reuse.

### Input Schema

```python
class WriteMemoryContextInput(ToolInput):
    pattern_type: str = Field(
        ...,
        description="template|style|intent|error_repair|system_upgrade|migration"
    )
    description: str = Field(..., description="Human-readable description")
    content: Dict[str, Any] = Field(
        ...,
        description="Pattern data to store"
    )
    
    # Classification
    tags: List[str] = Field(
        default_factory=list,
        description="Searchable metadata tags"
    )
    app_type: Optional[str] = None
    
    # Attribution
    source_operation_id: Optional[str] = Field(
        None,
        description="Link to operation event that created this pattern"
    )
    
    # Evaluation
    initial_success_indicator: bool = Field(
        default=True,
        description="Whether pattern worked on first use"
    )
```

### Output Schema

```python
class WriteMemoryContextOutput(ToolOutput):
    result: Optional[Dict[str, Any]] = None
    
    class Result(BaseModel):
        pattern_id: str = Field(..., description="Generated pattern identifier")
        embedding_id: str = Field(
            ...,
            description="Vector database embedding reference"
        )
        stored_at: datetime
        
        # Similar patterns (potential duplicates)
        similar_patterns: List[Dict[str, Any]] = Field(
            default_factory=list,
            description="Existing patterns with high similarity"
        )
```

### Error Codes

- `DUPLICATE_PATTERN`: Identical pattern already exists
- `EMBEDDING_GENERATION_FAILED`: Vector embedding creation failed
- `VECTOR_DB_WRITE_FAILED`: Storage to vector-db failed
- `INVALID_PATTERN_TYPE`: Unknown pattern type

---

## 9. propose_system_upgrade

**Purpose**: Generate self-improvement proposals for the control plane itself.

### Input Schema

```python
class ProposeSystemUpgradeInput(ToolInput):
    upgrade_category: str = Field(
        ...,
        description="planning|tools|validation|observability|cost_optimization"
    )
    motivation: str = Field(
        ...,
        description="Why this upgrade is needed"
    )
    proposed_changes: Dict[str, Any] = Field(
        ...,
        description="Detailed description of changes"
    )
    
    # Impact assessment
    estimated_improvement: Dict[str, float] = Field(
        ...,
        description="Metrics: speed, cost, reliability improvements"
    )
    breaking_changes: bool = Field(
        default=False,
        description="Whether upgrade breaks compatibility"
    )
    rollback_plan: str = Field(
        ...,
        description="How to revert if upgrade fails"
    )
```

### Output Schema

```python
class ProposeSystemUpgradeOutput(ToolOutput):
    result: Optional[Dict[str, Any]] = None
    
    class Result(BaseModel):
        proposal_id: str = Field(..., description="Unique proposal identifier")
        upgrade_category: str
        
        # Proposal details
        summary: str = Field(
            ...,
            description="AI-generated executive summary"
        )
        implementation_plan: List[str] = Field(
            ...,
            description="Step-by-step implementation"
        )
        
        # Risk assessment
        risk_level: str = Field(
            ...,
            description="low|medium|high"
        )
        risk_factors: List[str]
        mitigation_strategies: List[str]
        
        # Testing requirements
        test_plan: str
        validation_criteria: List[str]
        
        # Approval requirements
        requires_human_approval: bool
        estimated_implementation_time_hours: int
        
        # Storage
        stored_in_vector_db: bool = Field(
            ...,
            description="Whether proposal was stored for review"
        )
```

### Error Codes

- `INSUFFICIENT_MOTIVATION`: Proposal lacks clear justification
- `MISSING_ROLLBACK_PLAN`: No rollback strategy provided
- `RISK_TOO_HIGH`: Proposal rejected due to high risk
- `VALIDATION_FAILED`: Proposal failed consistency checks

---

## 10. evaluate_upgrade_proposal

**Purpose**: Analyze system upgrade proposal for safety, feasibility, and expected impact.

### Input Schema

```python
class EvaluateUpgradeProposalInput(ToolInput):
    proposal_id: str = Field(..., description="Proposal to evaluate")
    
    # Evaluation mode
    mode: str = Field(
        default="full",
        description="full|quick|safety_only"
    )
    
    # Context
    current_system_version: str = Field(
        ...,
        description="Current control plane version"
    )
    recent_operations: Optional[List[str]] = Field(
        None,
        description="Recent operation IDs for conflict analysis"
    )
```

### Output Schema

```python
class UpgradeEvaluation(BaseModel):
    # Safety analysis
    safety_score: float = Field(
        ...,
        description="Safety assessment (0.0-1.0, higher = safer)"
    )
    safety_concerns: List[str]
    
    # Feasibility
    feasibility_score: float = Field(
        ...,
        description="Implementation feasibility (0.0-1.0)"
    )
    implementation_blockers: List[str]
    
    # Impact
    expected_benefits: Dict[str, float] = Field(
        ...,
        description="Performance, cost, reliability improvements"
    )
    potential_downsides: List[str]
    
    # Dependencies
    prerequisite_upgrades: List[str] = Field(
        default_factory=list,
        description="Required prior upgrades"
    )
    affected_components: List[str]
    
    # Recommendation
    recommendation: str = Field(
        ...,
        description="approve|reject|needs_revision|needs_human_review"
    )
    reasoning: str = Field(
        ...,
        description="Detailed explanation of recommendation"
    )

class EvaluateUpgradeProposalOutput(ToolOutput):
    result: Optional[Dict[str, Any]] = None
    
    class Result(BaseModel):
        proposal_id: str
        evaluation: UpgradeEvaluation
        evaluated_at: datetime
        evaluator_version: str = Field(
            ...,
            description="Version of evaluation logic used"
        )
```

### Error Codes

- `PROPOSAL_NOT_FOUND`: Proposal ID doesn't exist
- `EVALUATION_TIMEOUT`: Analysis exceeded time limit
- `INSUFFICIENT_CONTEXT`: Cannot evaluate without more information
- `CONFLICTING_PROPOSALS`: Multiple proposals target same system

---

## Tool Integration with LangChain

### Example: Building an Agent with These Tools

```python
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

# Initialize LLM
llm = ChatOpenAI(model="gpt-4", temperature=0)

# Create tools list
tools = [
    create_app_spec_tool,
    build_static_app_tool,
    build_dynamic_app_tool,
    deploy_static_site_tool,
    deploy_dynamic_service_tool,
    update_app_state_tool,
    fetch_memory_context_tool,
    write_memory_context_tool,
    propose_system_upgrade_tool,
    evaluate_upgrade_proposal_tool,
]

# Define agent prompt
prompt = ChatPromptTemplate.from_messages([
    ("system", """You are an AI infrastructure operator. You can:
    - Create app specifications from natural language
    - Build and deploy static and dynamic applications
    - Manage state in the database
    - Learn from past operations via semantic memory
    - Propose and evaluate system improvements
    
    Always use fetch_memory_context to check for similar patterns before creating new specs.
    Always update_app_state after deployments.
    Always write_memory_context for successful operations.
    """),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}"),
])

# Create agent
agent = create_openai_tools_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

# Execute request
result = agent_executor.invoke({
    "input": "Create a blog platform with posts, comments, and tags. Deploy it."
})
```

---

## Error Handling Strategy

### Retry Logic

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=lambda ex: isinstance(ex, RecoverableError)
)
def execute_tool(tool_input: ToolInput) -> ToolOutput:
    """Execute tool with automatic retries on recoverable errors"""
    # Implementation
    pass
```

### Error Propagation

```python
class ToolException(Exception):
    """Base exception for tool errors"""
    def __init__(self, error: ToolError):
        self.error = error
        super().__init__(error.message)

class RecoverableError(ToolException):
    """Errors that may succeed on retry"""
    pass

class FatalError(ToolException):
    """Errors that cannot be recovered"""
    pass

class PolicyViolation(ToolException):
    """Errors due to policy constraints"""
    pass
```

---

## Logging and Observability

### OpenTelemetry Integration

```python
from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode

tracer = trace.get_tracer(__name__)

def execute_tool_with_tracing(
    tool_name: str,
    tool_input: ToolInput
) -> ToolOutput:
    """Execute tool with full OpenTelemetry tracing"""
    with tracer.start_as_current_span(
        f"tool.{tool_name}",
        attributes={
            "tool.name": tool_name,
            "tool.version": tool_input.version,
            "correlation_id": tool_input.correlation_id,
            "dry_run": tool_input.dry_run,
        }
    ) as span:
        try:
            output = execute_tool(tool_name, tool_input)
            
            span.set_attributes({
                "tool.success": output.success,
                "tool.execution_time_ms": output.execution_time_ms,
            })
            
            if output.success:
                span.set_status(Status(StatusCode.OK))
            else:
                span.set_status(
                    Status(StatusCode.ERROR, output.error or "Unknown error")
                )
            
            return output
            
        except Exception as e:
            span.set_status(Status(StatusCode.ERROR, str(e)))
            span.record_exception(e)
            raise
```

### Structured Logging

```python
import structlog

logger = structlog.get_logger()

def log_tool_execution(tool_name: str, tool_input: ToolInput, output: ToolOutput):
    """Log tool execution with structured data"""
    logger.info(
        "tool_executed",
        tool_name=tool_name,
        correlation_id=tool_input.correlation_id,
        success=output.success,
        execution_time_ms=output.execution_time_ms,
        operation_id=output.operation_id,
        dry_run=tool_input.dry_run,
        warnings=len(output.warnings),
        error=output.error if not output.success else None,
    )
```

---

## Tool Versioning

### Schema Evolution

Each tool maintains a version number that tracks schema changes:

```python
# Version 1.0.0 - Initial release
class CreateAppSpecInput_v1(ToolInput):
    version: str = Field(default="1.0.0")
    user_request: str
    app_type: str

# Version 1.1.0 - Add constraints field (backward compatible)
class CreateAppSpecInput_v1_1(ToolInput):
    version: str = Field(default="1.1.0")
    user_request: str
    app_type: str
    constraints: Optional[Dict[str, Any]] = None  # New, optional

# Version 2.0.0 - Breaking change (required field added)
class CreateAppSpecInput_v2(ToolInput):
    version: str = Field(default="2.0.0")
    user_request: str
    app_type: str
    constraints: Dict[str, Any]  # Now required (breaking)
```

### Compatibility Matrix

| Tool Version | Agent Version | Compatible |
|--------------|---------------|------------|
| 1.0.0        | 0.1.0         | ✅         |
| 1.1.0        | 0.1.0         | ✅ (backward compatible) |
| 2.0.0        | 0.1.0         | ❌ (breaking change) |
| 2.0.0        | 0.2.0         | ✅         |

---

## Testing Tools

### Unit Test Template

```python
import pytest
from unittest.mock import Mock, patch

def test_create_app_spec_success():
    """Test successful app spec creation"""
    # Arrange
    tool_input = CreateAppSpecInput(
        correlation_id="test-123",
        user_request="Create a blog platform",
        app_type="dynamic",
        dry_run=True
    )
    
    # Act
    output = create_app_spec_handler(tool_input)
    
    # Assert
    assert output.success is True
    assert output.correlation_id == "test-123"
    assert output.result is not None
    assert output.result.type == "dynamic"
    assert output.result.validation_status == "passed"
    assert output.execution_time_ms > 0

def test_create_app_spec_invalid_type():
    """Test error handling for invalid app type"""
    # Arrange
    tool_input = CreateAppSpecInput(
        correlation_id="test-456",
        user_request="Create something",
        app_type="invalid_type",
        dry_run=True
    )
    
    # Act
    output = create_app_spec_handler(tool_input)
    
    # Assert
    assert output.success is False
    assert "INVALID_APP_TYPE" in output.error
    assert output.result is None
```

---

## Performance Targets

| Tool | p50 Latency | p95 Latency | p99 Latency |
|------|-------------|-------------|-------------|
| create_app_spec | 1s | 3s | 5s |
| build_static_app | 5s | 15s | 30s |
| build_dynamic_app | 10s | 30s | 60s |
| deploy_static_site | 20s | 60s | 120s |
| deploy_dynamic_service | 60s | 180s | 300s |
| update_app_state | 100ms | 500ms | 1s |
| fetch_memory_context | 200ms | 1s | 2s |
| write_memory_context | 500ms | 2s | 5s |
| propose_system_upgrade | 5s | 15s | 30s |
| evaluate_upgrade_proposal | 3s | 10s | 20s |

---

## Security Considerations

### Input Validation

All tools must validate inputs before execution:

```python
def validate_tool_input(tool_input: ToolInput) -> List[str]:
    """Validate tool input and return list of errors"""
    errors = []
    
    # Check correlation ID format
    if not tool_input.correlation_id or len(tool_input.correlation_id) < 8:
        errors.append("Invalid correlation_id")
    
    # Check version format
    if not re.match(r'^\d+\.\d+\.\d+$', tool_input.version):
        errors.append("Invalid version format (expected semver)")
    
    return errors
```

### Authorization

Tools check permissions before executing operations:

```python
def check_authorization(
    operation: str,
    resource: str,
    actor_id: str
) -> bool:
    """Check if actor is authorized for operation on resource"""
    # Query policy engine
    # Return True if authorized, False otherwise
    pass
```

### Secrets Management

Never log or return secrets in tool outputs:

```python
REDACTED_KEYS = [
    "password", "secret", "token", "key", "credential",
    "api_key", "private_key", "access_token"
]

def redact_secrets(data: Dict[str, Any]) -> Dict[str, Any]:
    """Recursively redact secret values from data"""
    redacted = {}
    for key, value in data.items():
        if any(secret_key in key.lower() for secret_key in REDACTED_KEYS):
            redacted[key] = "***REDACTED***"
        elif isinstance(value, dict):
            redacted[key] = redact_secrets(value)
        else:
            redacted[key] = value
    return redacted
```

---

## Summary

These 10 LangChain tools provide a complete, production-ready interface for AI agents to autonomously operate cloud infrastructure:

1. ✅ **create_app_spec** — Parse natural language into validated specifications
2. ✅ **build_static_app** — Generate complete static websites
3. ✅ **build_dynamic_app** — Generate backend services with APIs and databases
4. ✅ **deploy_static_site** — Deploy to GCS with CDN and custom domains
5. ✅ **deploy_dynamic_service** — Deploy to Cloud Run with auto-scaling
6. ✅ **update_app_state** — Maintain ground truth in state-db
7. ✅ **fetch_memory_context** — Retrieve learned patterns from vector-db
8. ✅ **write_memory_context** — Store successful patterns for reuse
9. ✅ **propose_system_upgrade** — Generate self-improvement proposals
10. ✅ **evaluate_upgrade_proposal** — Assess upgrade safety and feasibility

All tools follow the design principles:
- ✅ Deterministic schemas with strong typing
- ✅ Structured JSON I/O for all operations
- ✅ Safe error escalation with retry logic
- ✅ Comprehensive OpenTelemetry logging
- ✅ Explicit semantic versioning

---

**Next Steps**: Continue to Step 6 — Agent Graph (LangGraph) to define how these tools are orchestrated by multiple specialized agents.

**Resume Command**:
> "Run Step 6 of the AI-Native Control Plane tasks."

---

*Last Updated: 2025-12-06*
