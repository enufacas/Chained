# AI-Native Control Plane — Agent Graph (LangGraph)

*This document is part of the AI-Native Control Plane specification defined in `.github/copilot/tasks/ai-native-control-plane.md`*

## Overview

This document defines the **multi-agent orchestration system** powered by LangGraph that coordinates AI operations for autonomous infrastructure management. Seven specialized agents work together through a state machine to handle complex deployment workflows, self-improvement proposals, and failure recovery.

### Design Philosophy

The agent graph follows these principles:

1. **Specialized Agents**: Each agent has a focused responsibility and expertise
2. **Explicit State Management**: All state transitions are deterministic and auditable
3. **Observable Execution**: Every agent action generates structured logs and traces
4. **Graceful Degradation**: Agents can operate in degraded modes when services are unavailable
5. **Self-Awareness**: The system can reason about its own capabilities and limitations

---

## Architecture Overview

### Agent Graph Structure

```
┌─────────────────────────────────────────────────────────────────────┐
│                         User Request                                 │
│              "Create a blog platform and deploy it"                  │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │  PLANNER AGENT  │ ◄──────┐
                    │                 │        │
                    │ • Parse intent  │        │
                    │ • Fetch memory  │        │ Replan
                    │ • Score plans   │        │ on failure
                    │ • Select best   │        │
                    └────────┬────────┘        │
                             │                 │
                             ▼                 │
                    ┌─────────────────┐        │
                    │  POLICY AGENT   │        │
                    │                 │        │
                    │ • Check quotes  │        │
                    │ • Validate auth │        │
                    │ • Cost limits   │        │
                    │ • Security scan │        │
                    └────────┬────────┘        │
                             │                 │
                    ┌────────▼─────────┐       │
                    │  Approved?       │       │
                    └──┬────────────┬──┘       │
                 YES   │            │ NO       │
                       ▼            └──────────┘
              ┌─────────────────┐
              │  MEMORY AGENT   │
              │                 │
              │ • Fetch context │
              │ • Load patterns │
              │ • Check similar │
              └────────┬────────┘
                       │
                       ▼
              ┌─────────────────┐
              │ APP BUILDER     │
              │ AGENT           │
              │                 │
              │ • Generate code │
              │ • Build assets  │
              │ • Create config │
              └────────┬────────┘
                       │
                       ▼
              ┌─────────────────┐
              │ INFRA AGENT     │
              │                 │
              │ • Deploy bucket │
              │ • Deploy service│
              │ • Config domain │
              └────────┬────────┘
                       │
                       ▼
              ┌─────────────────┐
              │ STATE MANAGER   │
              │                 │
              │ • Update app DB │
              │ • Log operation │
              │ • Write memory  │
              └────────┬────────┘
                       │
                       ▼
              ┌─────────────────┐
              │ OUTPUT AGENT    │
              │                 │
              │ • Format result │
              │ • Generate reply│
              │ • Return to user│
              └─────────────────┘
```

---

## Agent Definitions

### 1. Planner Agent

**Responsibility**: Parse user intent, retrieve relevant patterns, generate and score execution plans.

#### Capabilities

- **Intent Classification**: Determine request type (create app, update, deploy, system upgrade)
- **Pattern Retrieval**: Query vector-db for similar successful operations
- **Plan Generation**: Create multiple candidate plans with different approaches
- **Plan Scoring**: Evaluate plans based on cost, complexity, reliability, and historical success
- **Plan Selection**: Choose optimal plan or request human clarification

#### Tools Used

- `fetch_memory_context` — Retrieve learned patterns
- `create_app_spec` — Generate initial specifications

#### State Inputs

```python
class PlannerInput(BaseModel):
    user_request: str
    correlation_id: str
    user_id: str
    mode: str = "normal"  # normal|repair|migration|self_upgrade
    error_context: Optional[Dict[str, Any]] = None  # For repair mode
```

#### State Outputs

```python
class PlannerOutput(BaseModel):
    intent: str  # create_app|update_app|deploy|delete|system_upgrade
    confidence: float  # 0.0-1.0
    
    # Generated plans
    candidate_plans: List[ExecutionPlan]
    selected_plan: ExecutionPlan
    selection_reasoning: str
    
    # Memory context
    similar_patterns: List[str]  # Pattern IDs
    pattern_match_quality: float
    
    # Metadata
    planning_time_ms: int
    plans_generated: int
    
class ExecutionPlan(BaseModel):
    plan_id: str  # Deterministic hash
    steps: List[Dict[str, Any]]
    estimated_duration_seconds: int
    estimated_cost_usd: float
    complexity_score: float  # 0.0-1.0
    reliability_score: float  # Based on similar past operations
```

#### Decision Logic

```python
def plan_and_select(input: PlannerInput) -> PlannerOutput:
    """Generate and select optimal execution plan"""
    
    # 1. Classify intent
    intent = classify_intent(input.user_request)
    
    # 2. Retrieve similar patterns
    memory_results = fetch_memory_context(
        query=input.user_request,
        pattern_types=["template", "intent"],
        limit=10
    )
    
    # 3. Generate candidate plans
    plans = []
    for pattern in memory_results.patterns[:3]:
        plan = generate_plan_from_pattern(
            user_request=input.user_request,
            pattern=pattern,
            mode=input.mode
        )
        plans.append(plan)
    
    # Also generate a fresh plan without pattern bias
    fresh_plan = generate_plan_from_scratch(input.user_request)
    plans.append(fresh_plan)
    
    # 4. Score plans
    scored_plans = []
    for plan in plans:
        score = calculate_plan_score(
            plan=plan,
            historical_success_rate=get_success_rate(plan.pattern_id),
            cost_weight=0.3,
            complexity_weight=0.2,
            reliability_weight=0.5
        )
        plan.score = score
        scored_plans.append(plan)
    
    # 5. Select best plan
    selected = max(scored_plans, key=lambda p: p.score)
    
    return PlannerOutput(
        intent=intent,
        confidence=calculate_intent_confidence(intent, input.user_request),
        candidate_plans=scored_plans,
        selected_plan=selected,
        selection_reasoning=explain_selection(selected, scored_plans)
    )
```

#### Failure Modes

- **Low Confidence**: Request human clarification if confidence < 0.6
- **No Patterns Found**: Generate fresh plan, mark as experimental
- **Conflicting Patterns**: Choose most recent successful pattern
- **Ambiguous Intent**: Ask clarifying questions

---

### 2. Policy Agent

**Responsibility**: Validate plans against organizational policies, quotas, budgets, and security rules.

#### Capabilities

- **Quota Validation**: Check GCP quotas (compute, storage, network)
- **Budget Enforcement**: Ensure costs stay within limits
- **Security Scanning**: Validate against security policies (public access, IAM, secrets)
- **Compliance Checking**: Verify regulatory requirements (data residency, encryption)
- **Authorization**: Confirm user has permissions for requested operations

#### Tools Used

- None (reads from policy-db and queries GCP APIs)

#### State Inputs

```python
class PolicyInput(BaseModel):
    execution_plan: ExecutionPlan
    user_id: str
    correlation_id: str
```

#### State Outputs

```python
class PolicyOutput(BaseModel):
    approved: bool
    policy_decision: str  # approved|rejected|needs_review
    
    # Validation results
    validations: List[PolicyValidation]
    blocking_violations: List[str]
    warnings: List[str]
    
    # Cost analysis
    estimated_monthly_cost: float
    cost_limit: float
    within_budget: bool
    
    # Quotas
    quota_checks: List[QuotaCheck]
    quota_violations: List[str]
    
    # Security
    security_score: float  # 0.0-1.0
    security_issues: List[str]
    
class PolicyValidation(BaseModel):
    check_name: str
    passed: bool
    severity: str  # critical|warning|info
    message: str
    remediation: Optional[str] = None
```

#### Validation Rules

```python
POLICY_RULES = {
    "max_monthly_cost": 1000.0,  # USD
    "max_cpu_per_service": 4,
    "max_memory_per_service": "8Gi",
    "max_instances": 100,
    "require_ssl": True,
    "allow_public_services": True,
    "require_cors": False,
    "max_storage_gb": 100,
    "allowed_regions": ["us-central1", "us-east1", "europe-west1"],
}

def validate_policy(plan: ExecutionPlan) -> PolicyOutput:
    """Validate execution plan against policies"""
    validations = []
    
    # Cost check
    if plan.estimated_cost_usd > POLICY_RULES["max_monthly_cost"]:
        validations.append(PolicyValidation(
            check_name="cost_limit",
            passed=False,
            severity="critical",
            message=f"Plan exceeds cost limit: ${plan.estimated_cost_usd} > ${POLICY_RULES['max_monthly_cost']}",
            remediation="Reduce resource allocation or request budget increase"
        ))
    
    # Security checks
    for step in plan.steps:
        if step["type"] == "deploy_dynamic_service":
            if step.get("allow_public") and not step.get("enable_ssl"):
                validations.append(PolicyValidation(
                    check_name="ssl_required",
                    passed=False,
                    severity="critical",
                    message="Public services must enable SSL",
                    remediation="Set enable_ssl=true in deployment config"
                ))
    
    # Determine approval
    blocking = [v for v in validations if not v.passed and v.severity == "critical"]
    approved = len(blocking) == 0
    
    return PolicyOutput(
        approved=approved,
        policy_decision="approved" if approved else "rejected",
        validations=validations,
        blocking_violations=[v.message for v in blocking]
    )
```

#### Decision Logic

The Policy Agent acts as a **gate** in the workflow:

- **Approved**: Plan proceeds to Memory Agent
- **Rejected**: Return to Planner Agent with violations for replanning
- **Needs Review**: Pause execution, notify human operator, wait for manual approval

---

### 3. Memory Agent

**Responsibility**: Retrieve relevant patterns, templates, and historical context to inform execution.

#### Capabilities

- **Pattern Retrieval**: Find similar successful operations
- **Template Loading**: Load code templates and configurations
- **Error History**: Retrieve past failures to avoid repeating mistakes
- **Success Metrics**: Fetch success rates for similar operations
- **Context Enrichment**: Add metadata and tags to improve pattern matching

#### Tools Used

- `fetch_memory_context` — Query vector-db

#### State Inputs

```python
class MemoryInput(BaseModel):
    execution_plan: ExecutionPlan
    app_spec: Optional[AppSpec] = None  # If already created
    correlation_id: str
```

#### State Outputs

```python
class MemoryOutput(BaseModel):
    # Retrieved patterns
    templates: List[MemoryPattern]
    styles: List[MemoryPattern]
    error_repairs: List[MemoryPattern]
    
    # Recommendations
    recommended_template_id: Optional[str]
    recommended_approach: str
    confidence: float
    
    # Historical data
    similar_operations_count: int
    avg_success_rate: float
    common_failure_modes: List[str]
    
    # Enrichment
    suggested_tags: List[str]
    related_apps: List[str]
```

#### Retrieval Strategy

```python
def fetch_and_enrich_context(input: MemoryInput) -> MemoryOutput:
    """Retrieve relevant patterns and enrich context"""
    
    # 1. Fetch templates for app type
    templates = fetch_memory_context(
        query=f"app_type:{input.app_spec.type}",
        pattern_types=["template"],
        limit=5,
        min_similarity=0.7
    )
    
    # 2. Fetch style patterns
    styles = fetch_memory_context(
        query=input.app_spec.description,
        pattern_types=["style"],
        limit=3,
        min_similarity=0.6
    )
    
    # 3. Fetch error repair patterns (defensive)
    error_repairs = fetch_memory_context(
        query=f"error_repair for {input.app_spec.type}",
        pattern_types=["error_repair"],
        limit=5,
        min_similarity=0.5
    )
    
    # 4. Calculate success metrics
    similar_ops = query_operation_history(
        app_type=input.app_spec.type,
        last_n_days=90
    )
    avg_success = calculate_success_rate(similar_ops)
    
    # 5. Recommend best template
    if templates.patterns:
        recommended = max(
            templates.patterns,
            key=lambda p: p.similarity_score * p.success_rate
        )
        recommended_id = recommended.pattern_id
    else:
        recommended_id = None
    
    return MemoryOutput(
        templates=templates.patterns,
        styles=styles.patterns,
        error_repairs=error_repairs.patterns,
        recommended_template_id=recommended_id,
        avg_success_rate=avg_success,
        similar_operations_count=len(similar_ops)
    )
```

---

### 4. App Builder Agent

**Responsibility**: Generate application code, configurations, and assets based on specifications and patterns.

#### Capabilities

- **Code Generation**: Generate frontend and backend code
- **Configuration Creation**: Create deployment configs, Dockerfiles, schemas
- **Asset Generation**: Create static files (HTML, CSS, JS)
- **Schema Design**: Generate database schemas
- **API Specification**: Create OpenAPI/GraphQL schemas

#### Tools Used

- `build_static_app` — Generate static website
- `build_dynamic_app` — Generate backend service

#### State Inputs

```python
class BuilderInput(BaseModel):
    app_spec: AppSpec
    memory_context: MemoryOutput  # Patterns to use
    correlation_id: str
```

#### State Outputs

```python
class BuilderOutput(BaseModel):
    build_id: str
    
    # Static builds
    static_assets: Optional[List[StaticAsset]] = None
    static_build_success: bool
    
    # Dynamic builds
    dynamic_artifacts: Optional[List[DynamicServiceArtifact]] = None
    dynamic_build_success: bool
    
    # Metadata
    build_time_ms: int
    total_files: int
    total_size_bytes: int
    
    # Quality
    code_quality_score: float  # Based on linting, complexity
    estimated_performance_score: int  # Lighthouse score for static
    
    # Errors
    build_errors: List[str]
    build_warnings: List[str]
```

#### Build Process

```python
def build_application(input: BuilderInput) -> BuilderOutput:
    """Build application artifacts based on spec and patterns"""
    
    build_id = generate_deterministic_id(
        "build",
        input.app_spec.app_id,
        datetime.utcnow().isoformat()
    )
    
    # Static build
    static_result = None
    if input.app_spec.type in ["static", "dynamic"]:
        template = get_template(input.memory_context.recommended_template_id)
        
        static_result = build_static_app(
            app_spec=input.app_spec,
            template_id=input.memory_context.recommended_template_id,
            style_preferences=extract_styles(input.memory_context.styles)
        )
    
    # Dynamic build
    dynamic_result = None
    if input.app_spec.type in ["dynamic", "event-driven", "scheduled"]:
        dynamic_result = build_dynamic_app(
            app_spec=input.app_spec,
            framework=input.app_spec.components[0].get("framework", "fastapi"),
            database_type=input.app_spec.components[0].get("database", "postgresql")
        )
    
    return BuilderOutput(
        build_id=build_id,
        static_assets=static_result.assets if static_result else None,
        static_build_success=static_result.success if static_result else False,
        dynamic_artifacts=dynamic_result.artifacts if dynamic_result else None,
        dynamic_build_success=dynamic_result.success if dynamic_result else False,
        total_files=count_files(static_result, dynamic_result)
    )
```

---

### 5. Infra Agent

**Responsibility**: Execute infrastructure operations on GCP (deploy, scale, configure).

#### Capabilities

- **Static Deployment**: Deploy to GCS buckets with CDN
- **Dynamic Deployment**: Deploy to Cloud Run with auto-scaling
- **Database Provisioning**: Create Cloud SQL instances
- **Domain Configuration**: Map custom domains
- **SSL Configuration**: Provision and configure certificates
- **Health Checking**: Verify deployment health

#### Tools Used

- `deploy_static_site` — Deploy static assets
- `deploy_dynamic_service` — Deploy containerized service

#### State Inputs

```python
class InfraInput(BaseModel):
    app_spec: AppSpec
    build_output: BuilderOutput
    correlation_id: str
```

#### State Outputs

```python
class InfraOutput(BaseModel):
    deployment_id: str
    
    # Static deployment
    static_deployment: Optional[Dict[str, Any]] = None
    static_url: Optional[str] = None
    
    # Dynamic deployment
    dynamic_deployment: Optional[Dict[str, Any]] = None
    service_url: Optional[str] = None
    
    # Infrastructure objects
    created_resources: List[Dict[str, Any]]  # GCS, Cloud Run, Cloud SQL
    
    # Status
    deployment_status: str  # success|partial|failed
    deployment_errors: List[str]
    
    # Health
    health_status: str  # healthy|degraded|unhealthy
    health_checks: List[Dict[str, Any]]
    
    # Costs
    estimated_monthly_cost_usd: float
    
    # Timing
    deployment_time_ms: int
```

#### Deployment Strategy

```python
def deploy_infrastructure(input: InfraInput) -> InfraOutput:
    """Deploy application infrastructure to GCP"""
    
    deployment_id = generate_deterministic_id(
        "deployment",
        input.app_spec.app_id,
        datetime.utcnow().isoformat()
    )
    
    resources_created = []
    
    # Deploy static site
    static_result = None
    if input.build_output.static_assets:
        static_result = deploy_static_site(
            build_id=input.build_output.build_id,
            app_id=input.app_spec.app_id,
            assets=input.build_output.static_assets,
            custom_domain=input.app_spec.deployment.get("domain"),
            enable_cdn=True
        )
        
        if static_result.success:
            resources_created.append({
                "type": "gcs_bucket",
                "name": static_result.result.bucket_name,
                "url": static_result.result.public_url
            })
    
    # Deploy dynamic service
    dynamic_result = None
    if input.build_output.dynamic_artifacts:
        dynamic_result = deploy_dynamic_service(
            build_id=input.build_output.build_id,
            app_id=input.app_spec.app_id,
            artifacts=input.build_output.dynamic_artifacts,
            cpu=input.app_spec.resources.get("cpu", "1"),
            memory=input.app_spec.resources.get("memory", "512Mi"),
            max_instances=input.app_spec.deployment.get("max_instances", 10)
        )
        
        if dynamic_result.success:
            resources_created.append({
                "type": "cloud_run_service",
                "name": dynamic_result.result.service_name,
                "url": dynamic_result.result.service_url
            })
    
    # Health checks
    health_checks = []
    for resource in resources_created:
        health = check_resource_health(resource)
        health_checks.append(health)
    
    overall_health = "healthy" if all(h["status"] == "healthy" for h in health_checks) else "degraded"
    
    return InfraOutput(
        deployment_id=deployment_id,
        static_deployment=static_result.result if static_result else None,
        dynamic_deployment=dynamic_result.result if dynamic_result else None,
        created_resources=resources_created,
        deployment_status="success",
        health_status=overall_health,
        health_checks=health_checks
    )
```

---

### 6. State Manager Agent

**Responsibility**: Maintain ground truth in state-db, log operations, and write successful patterns to vector-db.

#### Capabilities

- **State Updates**: Update app records in state-db
- **Operation Logging**: Record all infrastructure mutations
- **Pattern Storage**: Write successful operations to vector-db
- **Metadata Management**: Track deployment history, costs, health
- **Audit Trail**: Maintain complete operation history

#### Tools Used

- `update_app_state` — Update application record
- `write_memory_context` — Store successful patterns

#### State Inputs

```python
class StateManagerInput(BaseModel):
    app_spec: AppSpec
    execution_plan: ExecutionPlan
    builder_output: BuilderOutput
    infra_output: InfraOutput
    correlation_id: str
```

#### State Outputs

```python
class StateManagerOutput(BaseModel):
    # State updates
    app_state_updated: bool
    app_status: str  # pending|active|failed
    
    # Operation logging
    operation_id: str
    logged_at: datetime
    
    # Pattern storage
    pattern_stored: bool
    pattern_id: Optional[str] = None
    
    # Metadata
    update_time_ms: int
```

#### State Management Logic

```python
def manage_state(input: StateManagerInput) -> StateManagerOutput:
    """Update state and log operations"""
    
    # 1. Update app state in state-db
    app_update = update_app_state(
        app_id=input.app_spec.app_id,
        status="active" if input.infra_output.deployment_status == "success" else "failed",
        deployment_id=input.infra_output.deployment_id,
        primary_url=input.infra_output.static_url or input.infra_output.service_url,
        infra_objects=input.infra_output.created_resources,
        estimated_monthly_cost_usd=input.infra_output.estimated_monthly_cost_usd
    )
    
    # 2. Log operation in operations table
    operation_id = log_operation(
        operation_type="app_deployment",
        actor="ai-control-plane",
        plan_hash=input.execution_plan.plan_id,
        before_snapshot=None,
        after_snapshot={
            "app_id": input.app_spec.app_id,
            "status": app_update.result.new_status,
            "resources": input.infra_output.created_resources
        },
        correlation_id=input.correlation_id
    )
    
    # 3. Store successful pattern in vector-db (if deployment succeeded)
    pattern_id = None
    if input.infra_output.deployment_status == "success":
        pattern_result = write_memory_context(
            pattern_type="template",
            description=f"Successful {input.app_spec.type} app deployment",
            content={
                "app_spec": input.app_spec.dict(),
                "build_config": {
                    "framework": input.builder_output.dynamic_artifacts[0].language if input.builder_output.dynamic_artifacts else None
                },
                "deployment_config": input.app_spec.deployment
            },
            tags=[input.app_spec.type, "successful_deployment"],
            app_type=input.app_spec.type,
            source_operation_id=operation_id,
            initial_success_indicator=True
        )
        
        if pattern_result.success:
            pattern_id = pattern_result.result.pattern_id
    
    return StateManagerOutput(
        app_state_updated=app_update.success,
        app_status=app_update.result.new_status,
        operation_id=operation_id,
        logged_at=datetime.utcnow(),
        pattern_stored=pattern_id is not None,
        pattern_id=pattern_id
    )
```

---

### 7. Output Agent

**Responsibility**: Format results for end users, generate human-readable responses, provide next steps.

#### Capabilities

- **Response Formatting**: Convert technical results to natural language
- **URL Generation**: Provide clickable links to deployed resources
- **Summary Generation**: Create concise summaries of operations
- **Next Steps**: Suggest follow-up actions
- **Cost Reporting**: Present cost estimates clearly
- **Error Explanation**: Translate technical errors to user-friendly messages

#### Tools Used

- None (pure formatting logic)

#### State Inputs

```python
class OutputInput(BaseModel):
    user_request: str
    execution_plan: ExecutionPlan
    infra_output: InfraOutput
    state_manager_output: StateManagerOutput
    correlation_id: str
```

#### State Outputs

```python
class OutputOutput(BaseModel):
    # User-facing message
    message: str  # Natural language response
    
    # URLs
    urls: List[Dict[str, str]]  # [{"label": "Website", "url": "https://..."}]
    
    # Summary
    summary: Dict[str, Any]
    
    # Next steps
    next_steps: List[str]
    
    # Metadata
    execution_time_seconds: int
    total_cost_usd: float
    
    # References
    correlation_id: str
    operation_id: str
    app_id: str
```

#### Output Formatting

```python
def format_output(input: OutputInput) -> OutputOutput:
    """Generate user-friendly response"""
    
    if input.infra_output.deployment_status == "success":
        message = generate_success_message(input)
    else:
        message = generate_failure_message(input)
    
    # Extract URLs
    urls = []
    if input.infra_output.static_url:
        urls.append({"label": "Website", "url": input.infra_output.static_url})
    if input.infra_output.service_url:
        urls.append({"label": "API", "url": input.infra_output.service_url})
    
    # Generate summary
    summary = {
        "request": input.user_request,
        "status": input.infra_output.deployment_status,
        "resources_created": len(input.infra_output.created_resources),
        "health": input.infra_output.health_status
    }
    
    # Suggest next steps
    next_steps = generate_next_steps(input)
    
    return OutputOutput(
        message=message,
        urls=urls,
        summary=summary,
        next_steps=next_steps,
        total_cost_usd=input.infra_output.estimated_monthly_cost_usd,
        correlation_id=input.correlation_id,
        operation_id=input.state_manager_output.operation_id,
        app_id=input.infra_output.static_deployment.get("app_id") if input.infra_output.static_deployment else "unknown"
    )

def generate_success_message(input: OutputInput) -> str:
    """Generate success message for user"""
    return f"""✅ Successfully deployed your {input.execution_plan.selected_plan.app_type} application!

🌐 Your site is live at: {input.infra_output.static_url or input.infra_output.service_url}

📊 Deployment Summary:
- Resources created: {len(input.infra_output.created_resources)}
- Health status: {input.infra_output.health_status}
- Estimated monthly cost: ${input.infra_output.estimated_monthly_cost_usd:.2f}

🔗 Operation ID: {input.state_manager_output.operation_id}

Your application is now running and ready to use!
"""
```

---

## State Modes

The agent graph operates in four distinct modes that change behavior and routing:

### 1. Normal Mode

**Purpose**: Standard operation for new application deployments.

**Flow**:
```
Planner → Policy → Memory → Builder → Infra → State Manager → Output
```

**Characteristics**:
- Full planning and pattern retrieval
- All policy checks enabled
- Complete state logging
- Pattern storage for successful operations

---

### 2. Repair Mode

**Purpose**: Fix failed deployments or resolve errors.

**Triggers**:
- Deployment health check failures
- User reports of broken functionality
- Automated monitoring alerts

**Flow**:
```
Planner (with error context) → Memory (error_repair patterns) → Builder → Infra → State Manager → Output
        ↑                                                                         │
        └─────────────────────── Retry loop (max 3 attempts) ───────────────────┘
```

**Special Behaviors**:
- Planner receives error embeddings and failure logs
- Memory Agent prioritizes `error_repair` patterns
- Policy Agent relaxes some constraints (e.g., allows higher costs for fixes)
- Automatic retries with exponential backoff
- If all retries fail, escalate to human operator

**Example**:
```python
class RepairModeInput(PlannerInput):
    mode: str = "repair"
    error_context: Dict[str, Any] = {
        "failure_type": "health_check_failed",
        "error_message": "Service returns 502 Bad Gateway",
        "failed_at": "2025-01-15T10:30:00Z",
        "previous_deployment_id": "deployment:abc123",
        "attempted_fixes": []  # List of previously attempted repairs
    }
```

---

### 3. Migration Mode

**Purpose**: Move existing applications to new infrastructure or upgrade versions.

**Triggers**:
- User requests infrastructure upgrade
- Platform version upgrades
- Cost optimization requests
- Region migrations

**Flow**:
```
Planner (migration strategy) → Policy → Memory (migration patterns) → 
Blue-Green Deployment → Gradual Traffic Shift → State Manager → Output
```

**Special Behaviors**:
- Creates new version alongside old version (blue-green)
- Gradually shifts traffic from old to new
- Maintains rollback capability
- Monitors error rates during migration
- Auto-rollback if error rate exceeds threshold

**Traffic Shift Strategy**:
```python
migration_strategy = {
    "type": "gradual",
    "stages": [
        {"new_traffic_percent": 10, "duration_minutes": 5},
        {"new_traffic_percent": 25, "duration_minutes": 10},
        {"new_traffic_percent": 50, "duration_minutes": 15},
        {"new_traffic_percent": 100, "duration_minutes": 0}
    ],
    "success_criteria": {
        "max_error_rate": 0.05,  # 5%
        "min_success_rate": 0.95  # 95%
    },
    "rollback_on_failure": True
}
```

---

### 4. Self-Upgrade Proposal Mode

**Purpose**: System generates and evaluates proposals to improve itself.

**Triggers**:
- Periodic self-assessment (weekly)
- Performance degradation detected
- User feedback about system limitations
- New capabilities identified in patterns

**Flow**:
```
Planner (identify improvement) → propose_system_upgrade → 
evaluate_upgrade_proposal → Policy (safety check) → 
[Human Approval Required] → Execute Upgrade → State Manager → Output
```

**Special Behaviors**:
- System analyzes its own performance metrics
- Generates concrete improvement proposals
- Evaluates proposals for safety and feasibility
- ALWAYS requires human approval before execution
- Implements with rollback capability
- Monitors post-upgrade metrics

**Example Proposal**:
```python
upgrade_proposal = {
    "proposal_id": "upgrade:better-plan-scoring",
    "category": "planning",
    "motivation": "Current plan scoring doesn't account for historical latency. Adding latency weight could improve user experience.",
    "proposed_changes": {
        "file": "agents/planner.py",
        "function": "calculate_plan_score",
        "change": "Add latency_weight=0.2 to scoring formula"
    },
    "estimated_improvement": {
        "avg_response_time_reduction_percent": 15,
        "cost_reduction_percent": 0,
        "reliability_improvement_percent": 5
    },
    "risk_level": "low",
    "requires_human_approval": True
}
```

---

## Planning Mechanics

### Vector Retrieval Strategy

The Planner Agent uses sophisticated vector retrieval to find relevant patterns:

```python
def retrieve_patterns_for_planning(
    user_request: str,
    app_type: Optional[str] = None,
    mode: str = "normal"
) -> List[MemoryPattern]:
    """Multi-stage pattern retrieval"""
    
    # Stage 1: Exact intent match
    exact_matches = fetch_memory_context(
        query=user_request,
        pattern_types=["intent"],
        limit=5,
        min_similarity=0.85  # High threshold
    )
    
    # Stage 2: Template match (if app type known)
    templates = []
    if app_type:
        templates = fetch_memory_context(
            query=f"app_type:{app_type}",
            pattern_types=["template"],
            limit=10,
            min_similarity=0.70
        )
    
    # Stage 3: Style match (broader)
    styles = fetch_memory_context(
        query=user_request,
        pattern_types=["style"],
        limit=5,
        min_similarity=0.60
    )
    
    # Stage 4: Error repair (defensive, if in repair mode)
    error_repairs = []
    if mode == "repair":
        error_repairs = fetch_memory_context(
            query=f"error_repair {app_type or ''}",
            pattern_types=["error_repair"],
            limit=10,
            min_similarity=0.50  # Lower threshold, cast wider net
        )
    
    # Combine and deduplicate
    all_patterns = (
        exact_matches.patterns +
        templates.patterns +
        styles.patterns +
        error_repairs.patterns
    )
    
    # Remove duplicates by pattern_id
    unique_patterns = {p.pattern_id: p for p in all_patterns}.values()
    
    return list(unique_patterns)
```

### Plan Scoring Formula

Plans are scored based on multiple weighted factors:

```python
def calculate_plan_score(
    plan: ExecutionPlan,
    historical_success_rate: float,
    cost_weight: float = 0.3,
    complexity_weight: float = 0.2,
    reliability_weight: float = 0.5
) -> float:
    """Calculate weighted plan score (0.0-1.0)"""
    
    # Cost score (lower cost = higher score)
    max_acceptable_cost = 1000.0  # USD
    cost_score = 1.0 - min(plan.estimated_cost_usd / max_acceptable_cost, 1.0)
    
    # Complexity score (lower complexity = higher score)
    complexity_score = 1.0 - plan.complexity_score
    
    # Reliability score (based on historical success of similar plans)
    reliability_score = historical_success_rate
    
    # Weighted combination
    total_score = (
        cost_weight * cost_score +
        complexity_weight * complexity_score +
        reliability_weight * reliability_score
    )
    
    return total_score
```

### Deterministic Hashing

All plans are hashed deterministically for versioning and comparison:

```python
def hash_execution_plan(plan: ExecutionPlan) -> str:
    """Generate deterministic SHA256 hash of plan"""
    
    # Normalize plan to canonical form
    canonical = {
        "steps": sorted([
            {k: v for k, v in step.items() if k != "metadata"}
            for step in plan.steps
        ], key=lambda s: s.get("order", 0)),
        "app_type": plan.app_type,
        "target_config": plan.target_config
    }
    
    # Serialize to JSON (sorted keys for consistency)
    plan_json = json.dumps(canonical, sort_keys=True)
    
    # Hash
    plan_hash = hashlib.sha256(plan_json.encode()).hexdigest()
    
    return f"plan:{plan_hash[:16]}"
```

### Fallback Strategies

When pattern retrieval fails or returns low-quality results:

```python
FALLBACK_STRATEGIES = {
    "no_patterns_found": {
        "action": "generate_from_scratch",
        "use_default_template": True,
        "mark_as_experimental": True,
        "increase_logging": True
    },
    "low_confidence_patterns": {
        "action": "request_clarification",
        "clarifying_questions": [
            "What framework do you prefer?",
            "Do you need a database?",
            "Should this be publicly accessible?"
        ]
    },
    "conflicting_patterns": {
        "action": "choose_most_recent_successful",
        "tiebreaker": "highest_success_rate"
    },
    "pattern_retrieval_timeout": {
        "action": "use_cached_patterns",
        "cache_ttl_minutes": 60
    }
}
```

---

## Failure Handling

### Exponential Backoff

All agent operations implement exponential backoff for transient failures:

```python
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=2, min=1, max=10),
    retry=retry_if_exception_type(TransientError)
)
def execute_agent_step(agent: Agent, input: AgentInput) -> AgentOutput:
    """Execute agent step with automatic retry"""
    try:
        return agent.execute(input)
    except Exception as e:
        # Log failure
        logger.error(
            "agent_step_failed",
            agent=agent.name,
            attempt=execute_agent_step.retry.statistics["attempt_number"],
            error=str(e)
        )
        
        # Classify error
        if is_transient(e):
            raise TransientError(e) from e
        else:
            raise FatalError(e) from e
```

### Replan with Error Embeddings

When operations fail, the system replans using error context:

```python
def replan_after_failure(
    original_plan: ExecutionPlan,
    failure_context: Dict[str, Any]
) -> ExecutionPlan:
    """Generate new plan incorporating failure information"""
    
    # 1. Create error embedding
    error_embedding = create_error_embedding(
        error_type=failure_context["error_type"],
        error_message=failure_context["error_message"],
        failed_step=failure_context["failed_step"],
        context=failure_context.get("additional_context", {})
    )
    
    # 2. Search for similar error repairs
    repairs = fetch_memory_context(
        query=error_embedding,
        pattern_types=["error_repair"],
        limit=5,
        min_similarity=0.6
    )
    
    # 3. Generate alternative plan
    if repairs.patterns:
        # Use successful repair pattern
        best_repair = max(repairs.patterns, key=lambda p: p.success_rate)
        new_plan = apply_repair_pattern(original_plan, best_repair)
    else:
        # Generate fresh plan with error context
        new_plan = generate_alternative_plan(
            original_plan=original_plan,
            avoid_steps=[failure_context["failed_step"]],
            error_context=failure_context
        )
    
    # 4. Mark as repair attempt
    new_plan.metadata["repair_attempt"] = True
    new_plan.metadata["original_plan_id"] = original_plan.plan_id
    new_plan.metadata["failure_context"] = failure_context
    
    return new_plan
```

### Operation Rollback

For certain operations, the system can rollback changes:

```python
def rollback_operation(operation_id: str) -> RollbackResult:
    """Attempt to rollback a failed operation"""
    
    # 1. Retrieve operation from log
    operation = get_operation(operation_id)
    
    if not operation:
        return RollbackResult(success=False, error="Operation not found")
    
    # 2. Check if rollback is feasible
    if not is_rollbackable(operation):
        return RollbackResult(
            success=False,
            error="Operation cannot be rolled back (stateless deployment)"
        )
    
    # 3. Execute rollback steps
    rollback_steps = []
    
    for resource in reversed(operation.created_resources):
        if resource["type"] == "gcs_bucket":
            # Delete bucket
            delete_bucket(resource["name"])
            rollback_steps.append({"deleted": "bucket", "name": resource["name"]})
            
        elif resource["type"] == "cloud_run_service":
            # Delete service
            delete_cloud_run_service(resource["name"])
            rollback_steps.append({"deleted": "service", "name": resource["name"]})
            
        elif resource["type"] == "cloud_sql_instance":
            # Don't automatically delete databases (too destructive)
            # Instead, mark for manual cleanup
            rollback_steps.append({"marked_for_cleanup": "database", "name": resource["name"]})
    
    # 4. Update operation log
    update_operation(operation_id, {
        "rolled_back": True,
        "rollback_steps": rollback_steps,
        "rolled_back_at": datetime.utcnow()
    })
    
    return RollbackResult(
        success=True,
        steps_executed=len(rollback_steps),
        manual_cleanup_required=any(s.get("marked_for_cleanup") for s in rollback_steps)
    )
```

### Circuit Breaker Pattern

To prevent cascading failures, agents implement circuit breakers:

```python
class CircuitBreaker:
    """Circuit breaker for agent operations"""
    
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout_seconds: int = 60
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout_seconds
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "closed"  # closed|open|half_open
    
    def call(self, func, *args, **kwargs):
        """Execute function with circuit breaker protection"""
        
        # Check circuit state
        if self.state == "open":
            # Check if recovery timeout has passed
            if datetime.utcnow() - self.last_failure_time > timedelta(seconds=self.recovery_timeout):
                self.state = "half_open"
                logger.info("circuit_breaker_half_open", func=func.__name__)
            else:
                raise CircuitBreakerOpenError("Circuit breaker is open")
        
        try:
            result = func(*args, **kwargs)
            
            # Success - reset failure count
            if self.state == "half_open":
                self.state = "closed"
                logger.info("circuit_breaker_closed", func=func.__name__)
            self.failure_count = 0
            
            return result
            
        except Exception as e:
            # Failure - increment count
            self.failure_count += 1
            self.last_failure_time = datetime.utcnow()
            
            if self.failure_count >= self.failure_threshold:
                self.state = "open"
                logger.error(
                    "circuit_breaker_opened",
                    func=func.__name__,
                    failure_count=self.failure_count
                )
            
            raise
```

---

## LangGraph Implementation

### State Schema

```python
from typing import TypedDict, List, Optional, Annotated
from langgraph.graph import StateGraph, END
import operator

class AgentGraphState(TypedDict):
    """Shared state across all agents"""
    
    # Request
    user_request: str
    correlation_id: str
    user_id: str
    mode: str  # normal|repair|migration|self_upgrade
    
    # Planner outputs
    intent: Optional[str]
    execution_plan: Optional[ExecutionPlan]
    
    # Policy outputs
    policy_approved: bool
    policy_violations: List[str]
    
    # Memory outputs
    memory_context: Optional[MemoryOutput]
    
    # Builder outputs
    builder_output: Optional[BuilderOutput]
    
    # Infra outputs
    infra_output: Optional[InfraOutput]
    
    # State Manager outputs
    state_manager_output: Optional[StateManagerOutput]
    
    # Output
    final_output: Optional[OutputOutput]
    
    # Error handling
    errors: Annotated[List[str], operator.add]  # Accumulate errors
    retry_count: int
```

### Graph Definition

```python
from langgraph.graph import StateGraph

def create_agent_graph() -> StateGraph:
    """Create LangGraph workflow for agent orchestration"""
    
    # Initialize graph
    graph = StateGraph(AgentGraphState)
    
    # Add agents as nodes
    graph.add_node("planner", planner_agent)
    graph.add_node("policy", policy_agent)
    graph.add_node("memory", memory_agent)
    graph.add_node("builder", app_builder_agent)
    graph.add_node("infra", infra_agent)
    graph.add_node("state_manager", state_manager_agent)
    graph.add_node("output", output_agent)
    
    # Define edges (workflow)
    graph.set_entry_point("planner")
    
    # Normal flow
    graph.add_edge("planner", "policy")
    
    # Policy decision routing
    graph.add_conditional_edges(
        "policy",
        route_after_policy,
        {
            "approved": "memory",
            "rejected": "planner",  # Replan
            "needs_review": END  # Human approval required
        }
    )
    
    graph.add_edge("memory", "builder")
    graph.add_edge("builder", "infra")
    
    # Infra decision routing (for retry logic)
    graph.add_conditional_edges(
        "infra",
        route_after_infra,
        {
            "success": "state_manager",
            "retry": "planner",  # Replan with error context
            "fatal": "output"  # Report failure
        }
    )
    
    graph.add_edge("state_manager", "output")
    graph.add_edge("output", END)
    
    return graph.compile()

def route_after_policy(state: AgentGraphState) -> str:
    """Route based on policy decision"""
    if state["policy_approved"]:
        return "approved"
    elif state["retry_count"] < 3:
        return "rejected"  # Try replanning
    else:
        return "needs_review"  # Exhausted retries

def route_after_infra(state: AgentGraphState) -> str:
    """Route based on infrastructure deployment result"""
    if state["infra_output"].deployment_status == "success":
        return "success"
    elif state["retry_count"] < 3:
        return "retry"  # Replan with error context
    else:
        return "fatal"  # Give up, report failure
```

### Execution

```python
# Create graph
agent_graph = create_agent_graph()

# Execute request
initial_state = {
    "user_request": "Create a blog platform with authentication",
    "correlation_id": "corr-123",
    "user_id": "user-456",
    "mode": "normal",
    "policy_approved": False,
    "errors": [],
    "retry_count": 0
}

# Run graph
result = agent_graph.invoke(initial_state)

# Extract final output
final_output = result["final_output"]
print(final_output.message)
print(f"URLs: {final_output.urls}")
```

---

## Observability and Monitoring

### Metrics

Key metrics tracked for each agent:

```python
AGENT_METRICS = {
    "execution_count": "Counter",
    "execution_duration_ms": "Histogram",
    "success_rate": "Gauge",
    "error_rate": "Gauge",
    "retry_count": "Counter",
    "circuit_breaker_trips": "Counter"
}
```

### Tracing

All agent executions are traced with OpenTelemetry:

```python
def trace_agent_execution(agent_name: str):
    """Decorator for tracing agent execution"""
    def decorator(func):
        @wraps(func)
        def wrapper(state: AgentGraphState) -> AgentGraphState:
            with tracer.start_as_current_span(
                f"agent.{agent_name}",
                attributes={
                    "agent.name": agent_name,
                    "correlation_id": state["correlation_id"],
                    "mode": state["mode"],
                    "retry_count": state["retry_count"]
                }
            ) as span:
                try:
                    result = func(state)
                    span.set_status(Status(StatusCode.OK))
                    return result
                except Exception as e:
                    span.set_status(Status(StatusCode.ERROR, str(e)))
                    span.record_exception(e)
                    raise
        return wrapper
    return decorator
```

---

## Summary

The agent graph provides a **robust, observable, and self-improving system** for autonomous infrastructure operations:

### Key Features

✅ **7 Specialized Agents** working in concert
- Planner, Policy, Memory, Builder, Infra, State Manager, Output

✅ **4 Operation Modes** for different scenarios
- Normal, Repair, Migration, Self-Upgrade Proposal

✅ **Sophisticated Planning** with vector retrieval and scoring
- Pattern matching, cost optimization, reliability scoring

✅ **Comprehensive Failure Handling**
- Exponential backoff, error embeddings, replanning, rollback

✅ **Complete Observability**
- OpenTelemetry traces, structured logs, metrics, circuit breakers

✅ **Self-Improvement Capability**
- System can propose and evaluate its own upgrades

---

**Next Steps**: Continue to Phase 4 — Execution Layer to implement skeleton services.

**Resume Command**:
> "Run Step 7 of the AI-Native Control Plane tasks."

---

*Last Updated: 2025-12-06*
