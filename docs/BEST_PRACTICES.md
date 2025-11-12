# Best Practices Guide

**Author**: 💭 Turing (coach-master agent)  
**Purpose**: Core engineering principles and how to apply them in Chained  
**Date**: 2025-11-12

## Overview

Engineering principles are like the rules of physics—they don't care if you believe in them, they'll affect your code anyway. The difference is, you can choose to work with them instead of against them.

This guide provides direct, actionable guidance on software engineering best practices, grounded in proven principles. These aren't theoretical ideals—they're practical tools that make your code better.

## Core Principles

### 1. DRY - Don't Repeat Yourself

**The Principle**: Every piece of knowledge should have a single, authoritative representation in the system.

**Think of it like**: A single source of truth is like a master copy. If you have multiple copies and need to change something, you have to update all copies. Miss one, and you have inconsistency.

**In Practice:**

❌ **Bad** - Repeated validation logic:
```python
def create_agent(name):
    if not name or len(name) < 2 or len(name) > 100:
        raise ValueError("Invalid agent name")
    # ... create agent

def update_agent(name):
    if not name or len(name) < 2 or len(name) > 100:
        raise ValueError("Invalid agent name")
    # ... update agent

def validate_agent_in_form(name):
    if not name or len(name) < 2 or len(name) > 100:
        return False
    return True
```

✅ **Good** - Single source of truth:
```python
def validate_agent_name(name: str) -> str:
    """
    Validate agent name meets requirements.
    
    Returns the validated name or raises ValidationError.
    """
    if not name:
        raise ValidationError("Agent name cannot be empty")
    
    if len(name) < 2 or len(name) > 100:
        raise ValidationError(f"Agent name must be 2-100 chars, got {len(name)}")
    
    return name.strip()

def create_agent(name):
    validated_name = validate_agent_name(name)
    # ... create agent with validated_name

def update_agent(name):
    validated_name = validate_agent_name(name)
    # ... update agent with validated_name
```

**When to Apply:**
- Logic appears in 2+ places
- Configuration/constants are duplicated
- Validation rules are repeated

**When Not to Apply:**
- Code looks similar but serves different purposes
- The duplication is coincidental, not conceptual
- Abstraction would make code harder to understand

### 2. KISS - Keep It Simple, Stupid

**The Principle**: Simplicity should be a key goal in design. Unnecessary complexity should be avoided.

**Think of it like**: If you can explain your code to someone in 30 seconds, it's probably simple enough. If it takes 10 minutes, it's too complex.

**In Practice:**

❌ **Bad** - Overengineered:
```python
class AgentFactoryBuilder:
    def __init__(self):
        self._factories = {}
        
    def register_factory(self, agent_type, factory):
        self._factories[agent_type] = factory
        
    def build_factory(self, agent_type):
        return self._factories.get(agent_type)

class AgentFactory:
    def create(self, config):
        # 50 lines of abstract factory pattern
        pass

# Usage requires understanding multiple abstraction layers
builder = AgentFactoryBuilder()
builder.register_factory('code-review', CodeReviewAgentFactory())
factory = builder.build_factory('code-review')
agent = factory.create(config)
```

✅ **Good** - Simple and direct:
```python
def create_agent(agent_type: str, config: dict):
    """Create an agent of the specified type."""
    if agent_type == 'code-review':
        return create_code_review_agent(config)
    elif agent_type == 'documentation':
        return create_documentation_agent(config)
    else:
        raise ValueError(f"Unknown agent type: {agent_type}")

# Usage is straightforward
agent = create_agent('code-review', config)
```

**When to Apply:**
- You're adding abstraction layers "just in case"
- The code is harder to read than it should be
- New team members struggle to understand it

**When Not to Apply:**
- Complexity is inherent to the problem
- Simpler solution would sacrifice correctness
- Current complexity prevents future complexity

### 3. YAGNI - You Aren't Gonna Need It

**The Principle**: Don't implement functionality until you actually need it.

**Think of it like**: Packing for a trip. You could bring an emergency tent, a week's worth of food, and a first aid kit for a weekend city break, but you won't need them. Pack for the trip you're taking, not the trip you might take.

**In Practice:**

❌ **Bad** - Building for hypothetical future:
```python
class Agent:
    def __init__(self, name, spec):
        self.name = name
        self.spec = spec
        self.cache = {}  # Might need caching later
        self.queue = []  # Might need task queue
        self.history = []  # Might need history
        self.plugins = []  # Might support plugins
        self.watchers = []  # Might need observers
        
    def execute(self, task):
        # Only actually uses name and spec
        return self._do_work(task)
```

✅ **Good** - Build what you need now:
```python
class Agent:
    def __init__(self, name: str, specialization: str):
        self.name = name
        self.specialization = specialization
        
    def execute(self, task):
        return self._do_work(task)

# Add caching when/if you need it:
# self.cache = {}  # Added 2025-11-15 for performance optimization
```

**When to Apply:**
- Adding features "in case we need them later"
- Designing overly flexible systems
- Building generic solutions for specific problems

**When Not to Apply:**
- The requirement is clearly coming soon
- Refactoring later would be expensive
- Current design blocks obvious extensions

### 4. Separation of Concerns

**The Principle**: Different aspects of a program should be isolated from each other.

**Think of it like**: A restaurant separates the kitchen, dining room, and accounting office. The chef doesn't handle billing, the waiter doesn't cook, and the accountant doesn't serve tables.

**In Practice:**

❌ **Bad** - Mixed concerns:
```python
def process_agent_task(agent_id, task_data):
    # Database access
    conn = sqlite3.connect('agents.db')
    cursor = conn.cursor()
    
    # Business logic
    result = validate_and_execute(task_data)
    
    # More database access
    cursor.execute('UPDATE agents SET last_task = ? WHERE id = ?', 
                   (result, agent_id))
    conn.commit()
    
    # Presentation/formatting
    html = f"<div class='result'>{result}</div>"
    
    # Logging
    print(f"Task completed: {result}")
    
    conn.close()
    return html
```

✅ **Good** - Clear separation:
```python
# Data access layer
class AgentRepository:
    def update_last_task(self, agent_id: str, result: str):
        with self.get_connection() as conn:
            conn.execute(
                'UPDATE agents SET last_task = ? WHERE id = ?',
                (result, agent_id)
            )

# Business logic layer
class TaskProcessor:
    def process(self, task_data: dict) -> str:
        validated = validate_task(task_data)
        return execute_task(validated)

# Presentation layer
class ResultFormatter:
    def format_html(self, result: str) -> str:
        return f"<div class='result'>{escape_html(result)}</div>"

# Orchestration
def process_agent_task(agent_id: str, task_data: dict) -> str:
    processor = TaskProcessor()
    repository = AgentRepository()
    formatter = ResultFormatter()
    
    result = processor.process(task_data)
    repository.update_last_task(agent_id, result)
    logger.info(f"Task completed: {result}")
    
    return formatter.format_html(result)
```

**When to Apply:**
- Functions handle multiple responsibilities
- Changes in one area require changes in unrelated areas
- Testing requires complex setup

**When Not to Apply:**
- The separation would create trivial classes
- The concerns are naturally coupled
- Over-separation reduces clarity

### 5. Fail Fast

**The Principle**: Detect and report errors as early as possible.

**Think of it like**: Finding out your tire is flat when you start the car is better than finding out at 70mph on the highway. Fail at the safest, earliest moment.

**In Practice:**

❌ **Bad** - Late failure:
```python
def process_agents(agent_data):
    results = []
    
    # Process continues even with bad data
    for agent in agent_data:
        try:
            result = process_single_agent(agent)
            results.append(result)
        except Exception:
            results.append(None)  # Silent failure
            
    # Discover problems after partial processing
    return results
```

✅ **Good** - Early validation:
```python
def process_agents(agent_data: list) -> list:
    # Validate everything upfront
    if not agent_data:
        raise ValueError("Agent data cannot be empty")
    
    # Validate each agent before processing any
    for i, agent in enumerate(agent_data):
        if 'id' not in agent:
            raise ValueError(f"Agent {i} missing required 'id' field")
        if 'spec' not in agent:
            raise ValueError(f"Agent {i} missing required 'spec' field")
    
    # Only process if all validation passes
    results = []
    for agent in agent_data:
        result = process_single_agent(agent)
        results.append(result)
    
    return results
```

**When to Apply:**
- Validating input parameters
- Checking preconditions
- Detecting configuration errors

**When Not to Apply:**
- Validation is expensive and errors are rare
- Partial success is acceptable
- Error recovery is straightforward

### 6. Composition Over Inheritance

**The Principle**: Favor object composition over class inheritance.

**Think of it like**: Building with LEGO vs. buying pre-built models. Composition lets you swap parts and recombine them. Inheritance locks you into a rigid hierarchy.

**In Practice:**

❌ **Bad** - Deep inheritance:
```python
class Agent:
    def execute(self):
        pass

class SpecializedAgent(Agent):
    def analyze(self):
        pass

class CodeReviewAgent(SpecializedAgent):
    def review_code(self):
        pass

class SecurityCodeReviewAgent(CodeReviewAgent):
    def check_security(self):
        pass

# Rigid hierarchy, hard to reuse parts
```

✅ **Good** - Composition:
```python
class CodeAnalyzer:
    def analyze(self, code: str) -> dict:
        # Reusable analysis logic
        pass

class SecurityChecker:
    def check_security(self, code: str) -> list:
        # Reusable security checking
        pass

class CodeReviewer:
    def review(self, code: str) -> str:
        # Reusable review logic
        pass

class Agent:
    def __init__(self, capabilities: list):
        # Compose agent from capabilities
        self.capabilities = capabilities
        
    def execute(self, code: str):
        results = {}
        for capability in self.capabilities:
            results[capability.name] = capability.run(code)
        return results

# Flexible composition
security_reviewer = Agent([
    CodeAnalyzer(),
    SecurityChecker(),
    CodeReviewer()
])
```

**When to Apply:**
- Deep inheritance hierarchies form
- Behavior needs to be reused across hierarchies
- Objects need different combinations of behavior

**When Not to Apply:**
- Clear "is-a" relationship exists
- Shared behavior truly belongs in base class
- Composition adds unnecessary complexity

### 7. Explicit is Better Than Implicit

**The Principle**: Make behavior and dependencies clear and obvious.

**Think of it like**: A contract should spell out what each party agrees to, not rely on handshake agreements and assumptions.

**In Practice:**

❌ **Bad** - Implicit behavior:
```python
def process_task(task):
    # Implicitly depends on global state
    agent = current_agent  # Where did this come from?
    config = load_config()  # What config? From where?
    
    # Implicit side effects
    update_metrics()  # Updates what? When?
    
    return agent.execute(task, config)
```

✅ **Good** - Explicit dependencies:
```python
def process_task(
    task: dict,
    agent: Agent,
    config: Configuration,
    metrics_tracker: MetricsTracker
) -> TaskResult:
    """
    Process a task using the specified agent and configuration.
    
    Args:
        task: Task data to process
        agent: Agent that will execute the task
        config: Configuration for task execution
        metrics_tracker: Tracker to record metrics
        
    Returns:
        Result of task execution
        
    Side effects:
        Updates metrics via metrics_tracker
    """
    result = agent.execute(task, config)
    metrics_tracker.record_task_completion(result)
    return result
```

**When to Apply:**
- Functions depend on global state
- Side effects are unclear
- Dependencies are hidden

**When Not to Apply:**
- Dependencies are obvious from context
- Explicitness reduces readability
- Convention is well-established

### 8. Defensive Programming

**The Principle**: Anticipate and handle edge cases, errors, and invalid states.

**Think of it like**: Wearing a seatbelt. You don't expect to crash, but you're prepared if it happens.

**In Practice:**

❌ **Bad** - Assumes everything works:
```python
def get_agent_metric(agent_id, metric_name):
    agent = agents[agent_id]  # KeyError if missing
    return agent.metrics[metric_name]  # KeyError if missing
```

✅ **Good** - Defensive checks:
```python
def get_agent_metric(
    agent_id: str,
    metric_name: str,
    default: float = 0.0
) -> float:
    """
    Get a metric value for an agent, with fallback.
    
    Args:
        agent_id: ID of the agent
        metric_name: Name of the metric to retrieve
        default: Value to return if metric not found
        
    Returns:
        Metric value or default
        
    Raises:
        ValueError: If agent_id is empty or None
    """
    if not agent_id:
        raise ValueError("agent_id cannot be empty")
    
    if agent_id not in agents:
        logger.warning(f"Agent not found: {agent_id}")
        return default
    
    agent = agents[agent_id]
    
    if not hasattr(agent, 'metrics'):
        logger.warning(f"Agent {agent_id} has no metrics")
        return default
        
    return agent.metrics.get(metric_name, default)
```

**When to Apply:**
- Accessing external data (files, network, database)
- Processing user input
- Working with data from other systems

**When Not to Apply:**
- Checking for impossible conditions
- Over-defensive code that hides real bugs
- Performance-critical paths with validated input

## Chained-Specific Best Practices

### Agent Development

**1. Validation is Mandatory**

```python
# Always validate agent data
from tools.validation_utils import (
    validate_agent_name,
    validate_file_path,
    validate_json_structure
)

def create_agent(data: dict):
    # Validate first, fail fast
    validate_json_structure(data, ['name', 'specialization', 'personality'])
    name = validate_agent_name(data['name'])
    # ... proceed with valid data
```

**2. Use Type Hints**

```python
# Type hints improve readability and catch errors
def calculate_agent_score(
    code_quality: float,
    issue_resolution: float,
    pr_success: float,
    peer_review: float,
    weights: dict[str, float]
) -> float:
    """Calculate weighted agent performance score."""
    return (
        code_quality * weights['code_quality'] +
        issue_resolution * weights['issue_resolution'] +
        pr_success * weights['pr_success'] +
        peer_review * weights['peer_review']
    )
```

**3. Centralize Configuration**

```python
# Don't scatter magic numbers
# Bad:
if agent_score < 30:  # What is 30?
    eliminate_agent()

# Good:
from config import ELIMINATION_THRESHOLD

if agent_score < ELIMINATION_THRESHOLD:
    eliminate_agent()
```

### Workflow Development

**1. Validate Inputs**

```yaml
# Always validate workflow inputs
inputs:
  agent-name:
    description: 'Name of the agent to create'
    required: true
    type: string

jobs:
  create:
    steps:
      - name: Validate input
        run: |
          if [ -z "${{ inputs.agent-name }}" ]; then
            echo "Error: agent-name cannot be empty"
            exit 1
          fi
```

**2. Handle Errors Gracefully**

```yaml
- name: Process agent data
  run: python tools/process-agent.py
  continue-on-error: false  # Fail workflow on error
  
- name: Cleanup on failure
  if: failure()
  run: python tools/cleanup.py
```

**3. Use Secrets Properly**

```yaml
# Never hardcode tokens
# Bad:
env:
  GITHUB_TOKEN: ghp_xxxxxxxxxxxxx

# Good:
env:
  GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

### Testing

**1. Use pytest, Not Manual Tests**

```python
# Bad - boolean returns
def test_registry():
    if not path.exists():
        return False
    return True

# Good - pytest assertions
def test_registry_exists():
    """Registry file must exist."""
    assert registry_path.exists(), "Registry not found"
```

**2. Test Edge Cases**

```python
def test_agent_name_validation():
    """Test agent name validation edge cases."""
    
    # Valid names
    assert validate_agent_name("alpha-01")
    assert validate_agent_name("code_review")
    
    # Edge cases
    with pytest.raises(ValidationError):
        validate_agent_name("")  # Empty
    
    with pytest.raises(ValidationError):
        validate_agent_name("a")  # Too short
    
    with pytest.raises(ValidationError):
        validate_agent_name("a" * 101)  # Too long
    
    with pytest.raises(ValidationError):
        validate_agent_name("agent name")  # Spaces not allowed
```

**3. Use Fixtures for Setup**

```python
@pytest.fixture
def sample_agent():
    """Provide a sample agent for testing."""
    return {
        'id': 'agent-001',
        'name': 'test-agent',
        'specialization': 'testing',
        'status': 'active'
    }

def test_agent_processing(sample_agent):
    """Test agent processing with sample data."""
    result = process_agent(sample_agent)
    assert result['status'] == 'success'
```

## Code Smells to Avoid

### 1. God Objects

**Smell**: Classes that know or do too much.

```python
# Bad - God class
class Agent:
    def execute_task(self): pass
    def update_database(self): pass
    def send_notification(self): pass
    def generate_report(self): pass
    def validate_input(self): pass
    def log_metrics(self): pass
    # ... 20 more methods

# Good - Single Responsibility
class Agent:
    def execute_task(self): pass

class AgentRepository:
    def save(self): pass
    def load(self): pass

class NotificationService:
    def notify(self): pass
```

### 2. Long Parameter Lists

**Smell**: Functions with too many parameters.

```python
# Bad - 8 parameters!
def create_agent(name, spec, personality, status, created, updated, metrics, config):
    pass

# Good - Use objects
@dataclass
class AgentConfig:
    name: str
    specialization: str
    personality: str
    status: str = 'active'
    
def create_agent(config: AgentConfig):
    pass
```

### 3. Primitive Obsession

**Smell**: Using primitives instead of domain objects.

```python
# Bad - strings everywhere
def calculate_score(agent_id: str, scores: dict) -> float:
    pass

# Good - domain objects
@dataclass
class AgentId:
    value: str
    
    def __post_init__(self):
        validate_agent_name(self.value)

@dataclass
class MetricScores:
    code_quality: float
    issue_resolution: float
    pr_success: float
    peer_review: float
    
def calculate_score(agent_id: AgentId, scores: MetricScores) -> float:
    pass
```

### 4. Shotgun Surgery

**Smell**: Small changes require modifications across many files.

```python
# Bad - changing validation means updating 10 files
# file1.py
if len(name) < 2 or len(name) > 100:
    raise ValueError("Invalid name")

# file2.py
if len(name) < 2 or len(name) > 100:
    raise ValueError("Invalid name")

# ... 8 more files with same code

# Good - single source of truth
from validation import validate_agent_name

# All files use the same validation function
validate_agent_name(name)
```

### 5. Feature Envy

**Smell**: Methods that use another object's data more than their own.

```python
# Bad - feature envy
class AgentReporter:
    def generate_report(self, agent):
        # Using agent's data extensively
        score = (
            agent.metrics['code_quality'] * 0.3 +
            agent.metrics['issue_resolution'] * 0.25 +
            agent.metrics['pr_success'] * 0.25 +
            agent.metrics['peer_review'] * 0.2
        )
        return f"Agent {agent.name}: {score}"

# Good - behavior follows data
class Agent:
    def calculate_score(self) -> float:
        return (
            self.metrics['code_quality'] * 0.3 +
            self.metrics['issue_resolution'] * 0.25 +
            self.metrics['pr_success'] * 0.25 +
            self.metrics['peer_review'] * 0.2
        )

class AgentReporter:
    def generate_report(self, agent):
        score = agent.calculate_score()
        return f"Agent {agent.name}: {score}"
```

## Refactoring Guidelines

### When to Refactor

✅ **Do refactor when:**
- Adding a feature to code that's hard to modify
- Fixing bugs in confusing code
- Code review reveals clarity issues
- Tests are hard to write

❌ **Don't refactor when:**
- Code works and is clear
- Deadline is imminent
- Changes are purely stylistic
- Risk is high, benefit is low

### How to Refactor Safely

1. **Ensure tests exist** - Write tests before refactoring
2. **Make small changes** - One refactoring at a time
3. **Run tests frequently** - After each change
4. **Commit often** - Easy to roll back if needed
5. **Review the diff** - Ensure only intended changes

**Example: Extract Function Refactoring**

```python
# Before: Duplicated code
def process_code_review_agent(agent):
    if not agent['name']:
        raise ValueError("Name required")
    if len(agent['name']) > 100:
        raise ValueError("Name too long")
    # ... process agent

def process_documentation_agent(agent):
    if not agent['name']:
        raise ValueError("Name required")
    if len(agent['name']) > 100:
        raise ValueError("Name too long")
    # ... process agent

# After: Extracted validation
def validate_agent_name(name: str):
    """Validate agent name or raise ValueError."""
    if not name:
        raise ValueError("Name required")
    if len(name) > 100:
        raise ValueError("Name too long")

def process_code_review_agent(agent):
    validate_agent_name(agent['name'])
    # ... process agent

def process_documentation_agent(agent):
    validate_agent_name(agent['name'])
    # ... process agent
```

## Performance Best Practices

### 1. Measure First

```python
# Don't optimize without data
import time

def benchmark():
    start = time.time()
    result = expensive_operation()
    duration = time.time() - start
    print(f"Operation took {duration:.2f}s")
    return result
```

### 2. Use Appropriate Data Structures

```python
# Bad - O(n) lookup
agent_list = [{'id': '1', ...}, {'id': '2', ...}]
agent = next(a for a in agent_list if a['id'] == target_id)

# Good - O(1) lookup
agent_dict = {'1': {...}, '2': {...}}
agent = agent_dict[target_id]
```

### 3. Avoid Premature Optimization

```python
# Bad - premature optimization
def calculate_score(metrics):
    # Complex bit manipulation to save 0.001ms
    return ((metrics[0] << 2) | (metrics[1] << 1)) & 0xFF

# Good - clear and fast enough
def calculate_score(metrics):
    return sum(metrics) / len(metrics)
```

## Summary

**Remember the fundamentals:**

1. **DRY**: Don't repeat yourself
2. **KISS**: Keep it simple
3. **YAGNI**: You aren't gonna need it
4. **Separation of Concerns**: Keep different aspects separate
5. **Fail Fast**: Detect errors early
6. **Composition Over Inheritance**: Flexible building blocks
7. **Explicit Over Implicit**: Be clear and obvious
8. **Defensive Programming**: Anticipate errors

**Apply them practically:**
- Validate all inputs
- Use type hints
- Write tests
- Keep functions small
- Handle errors properly
- Document public APIs
- Review your own code first

**Avoid code smells:**
- God objects
- Long parameter lists
- Primitive obsession
- Shotgun surgery
- Feature envy

Good code isn't about being clever—it's about being clear, maintainable, and correct. Write code you'd want to maintain at 2am during an outage.

---

*These principles aren't dogma—they're tools. Use them when they help, ignore them when they don't. But know why you're making that choice.*

---

[Related: Code Review Checklist](CODE_REVIEW_CHECKLIST.md) | [Related: SOLID Principles](SOLID_PRINCIPLES_GUIDE.md) | [Related: Testing Guide](CODE_REVIEW_GUIDE_TESTING.md)
