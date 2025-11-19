# Chained Agent Configuration

## Version
**Format Version:** 1.0  
**Last Updated:** 2025-11-19  
**Maintained by:** @agents-tech-lead

---

## Global Defaults

All agents inherit these defaults unless explicitly overridden:

```yaml
global_defaults:
  # Logging and Communication
  logging_style: "structured"
  commit_message_format: "conventional"
  comment_verbosity: "standard"
  
  # Code Standards
  code_style: "pep8"
  max_line_length: 88
  test_framework: "pytest"
  documentation_format: "markdown"
  
  # Review and Quality
  code_review_depth: "standard"
  review_focus: ["correctness", "readability", "performance"]
  auto_fix_linting: true
  
  # Workflow Behavior
  max_file_changes: 15
  create_draft_prs: false
  auto_merge_threshold: 0.85
  
  # Agent Coordination
  collaboration_mode: "competitive"
  task_timeout_minutes: 120
  retry_on_failure: true
  max_retries: 3
```

---

## Agent-Specific Overrides

### Infrastructure & Development Agents

#### @APIs-architect
```yaml
agent_overrides:
  apis-architect:
    logging_style: "verbose"
    review_focus: ["architecture", "scalability", "api-design"]
    max_file_changes: 20
    documentation_format: "openapi"
    specialization_tags:
      - api-design
      - rest-architecture
      - graphql
```

#### @engineer-master
```yaml
agent_overrides:
  engineer-master:
    logging_style: "detailed"
    review_focus: ["architecture", "scalability", "maintainability"]
    max_file_changes: 25
    test_coverage_minimum: 0.90
    documentation_format: "markdown+diagrams"
    specialization_tags:
      - system-design
      - infrastructure
      - best-practices
```

#### @create-guru
```yaml
agent_overrides:
  create-guru:
    logging_style: "creative"
    review_focus: ["innovation", "feasibility", "integration"]
    max_file_changes: 30
    experimentation_enabled: true
    proof_of_concept_mode: true
    specialization_tags:
      - infrastructure
      - innovation
      - prototyping
```

### Performance Agents

#### @accelerate-master
```yaml
agent_overrides:
  accelerate-master:
    logging_style: "metrics-focused"
    review_focus: ["performance", "efficiency", "resource-usage"]
    max_file_changes: 10
    benchmark_required: true
    profiling_enabled: true
    performance_threshold: 0.20  # 20% improvement minimum
    specialization_tags:
      - optimization
      - performance
      - profiling
```

#### @accelerate-specialist
```yaml
agent_overrides:
  accelerate-specialist:
    logging_style: "analytical"
    review_focus: ["algorithms", "complexity", "efficiency"]
    max_file_changes: 8
    complexity_analysis_required: true
    benchmark_required: true
    specialization_tags:
      - algorithms
      - optimization
      - data-structures
```

### Testing & Quality Agents

#### @assert-specialist
```yaml
agent_overrides:
  assert-specialist:
    logging_style: "test-focused"
    review_focus: ["test-coverage", "edge-cases", "quality"]
    max_file_changes: 5
    test_coverage_minimum: 0.95
    test_first_development: true
    mutation_testing: true
    specialization_tags:
      - testing
      - quality-assurance
      - tdd
```

#### @edge-cases-pro
```yaml
agent_overrides:
  edge-cases-pro:
    logging_style: "paranoid"
    review_focus: ["edge-cases", "error-handling", "robustness"]
    max_file_changes: 3
    test_exotic_inputs: true
    fuzz_testing: true
    specialization_tags:
      - edge-cases
      - error-handling
      - robustness
```

### Security Agents

#### @secure-specialist
```yaml
agent_overrides:
  secure-specialist:
    logging_style: "audit"
    review_focus: ["security", "vulnerabilities", "compliance"]
    max_file_changes: 5
    security_scan_enabled: true
    vulnerability_validation: "sandbox"
    auto_patch_generation: true
    cve_tracking: true
    specialization_tags:
      - security
      - vulnerabilities
      - compliance
```

#### @secure-ninja
```yaml
agent_overrides:
  secure-ninja:
    logging_style: "security-audit"
    review_focus: ["access-control", "authentication", "authorization"]
    max_file_changes: 3
    permission_audit: true
    security_scan_enabled: true
    specialization_tags:
      - access-control
      - authentication
      - identity-management
```

### Code Organization Agents

#### @organize-guru
```yaml
agent_overrides:
  organize-guru:
    logging_style: "structural"
    review_focus: ["duplication", "structure", "maintainability"]
    max_file_changes: 20
    duplication_threshold: 0.15
    refactoring_aggressive: true
    specialization_tags:
      - refactoring
      - code-structure
      - maintainability
```

#### @refactor-champion
```yaml
agent_overrides:
  refactor-champion:
    logging_style: "improvement-focused"
    review_focus: ["complexity", "readability", "simplicity"]
    max_file_changes: 15
    cyclomatic_complexity_max: 10
    refactoring_conservative: false
    specialization_tags:
      - refactoring
      - complexity-reduction
      - clean-code
```

### Documentation Agents

#### @document-ninja
```yaml
agent_overrides:
  document-ninja:
    logging_style: "minimal"
    review_focus: ["clarity", "completeness", "examples"]
    max_file_changes: 10
    documentation_format: "markdown"
    code_examples_required: true
    markdown_linter: "markdownlint"
    diagram_generation: true
    specialization_tags:
      - documentation
      - tutorials
      - examples
```

#### @clarify-champion
```yaml
agent_overrides:
  clarify-champion:
    logging_style: "educational"
    review_focus: ["clarity", "accessibility", "structure"]
    max_file_changes: 8
    reading_level: "intermediate"
    analogies_enabled: true
    specialization_tags:
      - documentation
      - clarity
      - education
```

### CI/CD Agents

#### @troubleshoot-expert
```yaml
agent_overrides:
  troubleshoot-expert:
    logging_style: "diagnostic"
    review_focus: ["workflows", "failures", "ci-cd"]
    max_file_changes: 5
    workflow_validation: true
    log_analysis_depth: "deep"
    auto_retry_logic: true
    specialization_tags:
      - github-actions
      - troubleshooting
      - ci-cd
```

#### @align-wizard
```yaml
agent_overrides:
  align-wizard:
    logging_style: "workflow-focused"
    review_focus: ["automation", "orchestration", "efficiency"]
    max_file_changes: 10
    workflow_optimization: true
    parallel_execution_preferred: true
    specialization_tags:
      - ci-cd
      - automation
      - workflows
```

### Coordination Agents

#### @meta-coordinator
```yaml
agent_overrides:
  meta-coordinator:
    logging_style: "orchestration"
    review_focus: ["task-decomposition", "agent-selection", "coordination"]
    max_file_changes: 50
    task_decomposition_enabled: true
    parallel_coordination: true
    agent_selection_algorithm: "competitive"
    multi_agent_orchestration: true
    specialization_tags:
      - coordination
      - orchestration
      - task-planning
```

---

## Configuration Usage

### For Workflows

Workflows can read agent configuration like this:

```yaml
- name: Load agent configuration
  id: load-config
  run: |
    python tools/parse_agent_config.py --agent "$AGENT_NAME"
```

### For Agent Behavior

Agents should respect their configuration:

```python
from tools.agent_config import get_agent_settings

settings = get_agent_settings('secure-specialist')
if settings['security_scan_enabled']:
    run_security_scan()
if settings['vulnerability_validation'] == 'sandbox':
    validate_in_sandbox()
```

### For Issue Assignment

Agent matching can use configuration:

```python
from tools.agent_config import get_agent_settings

def match_agent_to_issue(issue):
    # Check specialization tags
    for agent in all_agents:
        settings = get_agent_settings(agent)
        if issue.has_tags(settings['specialization_tags']):
            return agent
```

---

## Configuration Validation

This configuration file is validated on every commit by:
1. YAML syntax validation
2. Required field checks
3. Value range validation
4. Agent name consistency check

See `.github/workflows/validate-agent-config.yml` for validation rules.

---

## Extending Configuration

To add new configuration options:

1. Update `global_defaults` section
2. Document the option's purpose and valid values
3. Update parser utility in `tools/parse_agent_config.py`
4. Update validation rules
5. Add usage examples

---

## Version History

### Version 1.0 (2025-11-19)
- Initial AGENTS.md configuration format
- 15 agent configurations defined
- Global defaults established
- Validation framework created

---

**Maintained by @agents-tech-lead**  
**Part of Mission ID: idea:41 - GitHub Innovation Integration**
