# SOLID Principles Guide

**Author**: 💭 Turing (coach-master agent)  
**Purpose**: Understanding and applying SOLID principles with analogies and code examples  
**Date**: 2025-11-12

## Overview

SOLID principles are like the foundation of a building—get them right, and everything built on top stays stable. Get them wrong, and even small changes can cause the whole structure to crack.

These five principles, coined by Robert C. Martin (Uncle Bob), form the bedrock of object-oriented design. They're not abstract theory—they're practical guidelines that make code easier to understand, maintain, and extend.

## The SOLID Acronym

- **S** - Single Responsibility Principle
- **O** - Open/Closed Principle
- **L** - Liskov Substitution Principle
- **I** - Interface Segregation Principle
- **D** - Dependency Inversion Principle

Let's explore each one with clear analogies and practical examples from the Chained codebase.

---

## S - Single Responsibility Principle (SRP)

### The Principle

**A class should have one, and only one, reason to change.**

### The Analogy

Think of a Swiss Army knife vs. specialized tools. A Swiss Army knife does many things poorly. A chef's knife, a saw, and a screwdriver each do one thing excellently. When your saw blade dulls, you don't replace your screwdriver.

In code, if a class has multiple responsibilities, changes to one responsibility might break the others. Keep them separate.

### The Problem

❌ **Violating SRP** - Class has multiple responsibilities:

```python
class Agent:
    """Agent that does EVERYTHING - validation, execution, persistence, reporting."""
    
    def __init__(self, name: str, specialization: str):
        self.name = name
        self.specialization = specialization
        self.metrics = {}
    
    # Responsibility 1: Validation
    def validate(self) -> bool:
        """Validate agent configuration."""
        if not self.name or len(self.name) < 2:
            return False
        if self.specialization not in ['code-review', 'documentation', 'testing']:
            return False
        return True
    
    # Responsibility 2: Business logic
    def execute_task(self, task: dict) -> dict:
        """Execute an assigned task."""
        if task['type'] == 'review':
            return self._review_code(task['code'])
        elif task['type'] == 'document':
            return self._write_docs(task['content'])
        else:
            raise ValueError(f"Unknown task type: {task['type']}")
    
    # Responsibility 3: Database operations
    def save_to_database(self):
        """Save agent to database."""
        conn = sqlite3.connect('agents.db')
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO agents (name, spec) VALUES (?, ?)',
            (self.name, self.specialization)
        )
        conn.commit()
        conn.close()
    
    # Responsibility 4: Metrics calculation
    def calculate_score(self) -> float:
        """Calculate performance score."""
        return (
            self.metrics.get('code_quality', 0) * 0.3 +
            self.metrics.get('issue_resolution', 0) * 0.25 +
            self.metrics.get('pr_success', 0) * 0.25 +
            self.metrics.get('peer_review', 0) * 0.2
        )
    
    # Responsibility 5: Reporting
    def generate_report(self) -> str:
        """Generate HTML report."""
        score = self.calculate_score()
        return f"""
        <html>
            <body>
                <h1>Agent Report: {self.name}</h1>
                <p>Score: {score}</p>
            </body>
        </html>
        """
```

**Why this is bad:**
- Need to change the class if validation rules change
- Need to change the class if database schema changes
- Need to change the class if scoring algorithm changes
- Need to change the class if report format changes
- Hard to test each responsibility independently
- Violates the "reason to change" principle

### The Solution

✅ **Following SRP** - Each class has one responsibility:

```python
# Responsibility 1: Agent data model (only represents agent state)
@dataclass
class Agent:
    """Agent data model - only holds agent state."""
    id: str
    name: str
    specialization: str
    status: str
    created_at: datetime
    
    def __post_init__(self):
        """Validate on creation."""
        if not self.name:
            raise ValueError("Agent name cannot be empty")


# Responsibility 2: Validation logic
class AgentValidator:
    """Validates agent configuration against rules."""
    
    MIN_NAME_LENGTH = 2
    MAX_NAME_LENGTH = 100
    VALID_SPECIALIZATIONS = ['code-review', 'documentation', 'testing']
    
    @classmethod
    def validate(cls, agent: Agent) -> None:
        """
        Validate agent configuration.
        
        Raises:
            ValidationError: If validation fails
        """
        if len(agent.name) < cls.MIN_NAME_LENGTH:
            raise ValidationError(f"Name too short: {agent.name}")
        
        if len(agent.name) > cls.MAX_NAME_LENGTH:
            raise ValidationError(f"Name too long: {agent.name}")
        
        if agent.specialization not in cls.VALID_SPECIALIZATIONS:
            raise ValidationError(f"Invalid specialization: {agent.specialization}")


# Responsibility 3: Database operations
class AgentRepository:
    """Handles agent persistence to database."""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
    
    def save(self, agent: Agent) -> None:
        """Save agent to database."""
        with self._get_connection() as conn:
            conn.execute(
                'INSERT INTO agents (id, name, specialization, status) VALUES (?, ?, ?, ?)',
                (agent.id, agent.name, agent.specialization, agent.status)
            )
    
    def find_by_id(self, agent_id: str) -> Agent:
        """Find agent by ID."""
        with self._get_connection() as conn:
            row = conn.execute(
                'SELECT id, name, specialization, status FROM agents WHERE id = ?',
                (agent_id,)
            ).fetchone()
        
        if not row:
            raise AgentNotFoundError(f"Agent not found: {agent_id}")
        
        return Agent(id=row[0], name=row[1], specialization=row[2], status=row[3])
    
    def _get_connection(self):
        return sqlite3.connect(self.db_path)


# Responsibility 4: Metrics calculation
class AgentScoreCalculator:
    """Calculates agent performance scores."""
    
    def __init__(self, weights: dict[str, float]):
        self.weights = weights
    
    def calculate(self, metrics: dict[str, float]) -> float:
        """
        Calculate weighted performance score.
        
        Args:
            metrics: Dictionary of metric names to values
            
        Returns:
            Weighted score between 0 and 100
        """
        total = 0.0
        for metric_name, weight in self.weights.items():
            metric_value = metrics.get(metric_name, 0.0)
            total += metric_value * weight
        return total


# Responsibility 5: Report generation
class AgentReportGenerator:
    """Generates reports for agents."""
    
    def __init__(self, calculator: AgentScoreCalculator):
        self.calculator = calculator
    
    def generate_html_report(self, agent: Agent, metrics: dict[str, float]) -> str:
        """
        Generate HTML report for an agent.
        
        Args:
            agent: Agent to report on
            metrics: Agent's performance metrics
            
        Returns:
            HTML formatted report
        """
        score = self.calculator.calculate(metrics)
        
        return f"""
        <html>
            <head><title>Agent Report: {agent.name}</title></head>
            <body>
                <h1>Agent Report: {agent.name}</h1>
                <p><strong>Specialization:</strong> {agent.specialization}</p>
                <p><strong>Score:</strong> {score:.2f}</p>
                <h2>Metrics</h2>
                <ul>
                    {''.join(f'<li>{k}: {v}</li>' for k, v in metrics.items())}
                </ul>
            </body>
        </html>
        """


# Responsibility 6: Task execution
class TaskExecutor:
    """Executes tasks based on type."""
    
    def execute(self, task: dict) -> dict:
        """Execute a task and return results."""
        if task['type'] == 'review':
            return self._execute_review(task)
        elif task['type'] == 'document':
            return self._execute_documentation(task)
        else:
            raise ValueError(f"Unknown task type: {task['type']}")
    
    def _execute_review(self, task: dict) -> dict:
        # Review implementation
        pass
    
    def _execute_documentation(self, task: dict) -> dict:
        # Documentation implementation
        pass
```

**Why this is better:**
- Each class has one reason to change
- Easy to test each responsibility independently
- Can reuse components (e.g., `AgentScoreCalculator` elsewhere)
- Changes to database don't affect validation or reporting
- Clear separation makes code easier to understand

### Real Chained Example

Let's look at `validation_utils.py` - it follows SRP well:

```python
# Good SRP example from validation_utils.py
class ValidationError(Exception):
    """Custom exception for validation failures."""
    pass  # Single responsibility: represent validation errors


def validate_agent_name(agent_name: Any) -> str:
    """
    Validate and sanitize an agent name.
    Single responsibility: validate agent names
    """
    # Only validates agent names, nothing else
    if not agent_name:
        raise ValidationError("Agent name cannot be empty")
    
    if not isinstance(agent_name, str):
        raise ValidationError(f"Agent name must be a string")
    
    agent_name = agent_name.strip()
    
    if not re.match(r'^[a-zA-Z0-9_-]+$', agent_name):
        raise ValidationError("Agent name contains invalid characters")
    
    if len(agent_name) > 100:
        raise ValidationError(f"Agent name too long")
    
    return agent_name


def validate_file_path(filepath: Union[str, Path], base_dir: Optional[Path] = None) -> Path:
    """
    Validate a file path to prevent directory traversal attacks.
    Single responsibility: validate file paths
    """
    # Only validates file paths, nothing else
    if not filepath:
        raise ValidationError("File path cannot be empty")
    
    try:
        path = Path(filepath).resolve()
    except (ValueError, OSError) as e:
        raise ValidationError(f"Invalid file path: {e}")
    
    if base_dir is not None:
        try:
            base_dir = base_dir.resolve()
            path.relative_to(base_dir)
        except ValueError:
            raise ValidationError(f"Path is outside allowed directory")
    
    return path
```

**Each function has ONE job:**
- `validate_agent_name`: Only validates agent names
- `validate_file_path`: Only validates file paths
- No function tries to validate AND save AND log

---

## O - Open/Closed Principle (OCP)

### The Principle

**Software entities should be open for extension, but closed for modification.**

### The Analogy

Think of a smartphone with a protective case. The phone itself is "closed" (you don't modify its internals), but it's "open" for extension through cases, screen protectors, and accessories. You extend functionality without changing the phone.

In code, you should be able to add new behavior without modifying existing, tested code.

### The Problem

❌ **Violating OCP** - Must modify code to add new agent types:

```python
class TaskExecutor:
    """Executor that requires modification for each new agent type."""
    
    def execute(self, agent_type: str, task: dict) -> dict:
        """Execute task based on agent type."""
        
        # Must modify this method to add new agent types!
        if agent_type == 'code-review':
            return self._review_code(task['code'])
        
        elif agent_type == 'documentation':
            return self._write_docs(task['content'])
        
        elif agent_type == 'testing':
            return self._write_tests(task['code'])
        
        # New agent type? Must modify this function!
        elif agent_type == 'security':
            return self._check_security(task['code'])
        
        # More agent types? More elif statements!
        
        else:
            raise ValueError(f"Unknown agent type: {agent_type}")
    
    def _review_code(self, code: str) -> dict:
        # Implementation
        pass
    
    def _write_docs(self, content: str) -> dict:
        # Implementation
        pass
    
    def _write_tests(self, code: str) -> dict:
        # Implementation
        pass
    
    def _check_security(self, code: str) -> dict:
        # Implementation
        pass
```

**Why this is bad:**
- Every new agent type requires modifying `execute()`
- Risk of breaking existing functionality
- Method grows unbounded
- Hard to test each agent type independently

### The Solution

✅ **Following OCP** - Extend through interfaces/inheritance:

```python
from abc import ABC, abstractmethod

# Abstract base defines the interface
class AgentCapability(ABC):
    """Base class for agent capabilities - closed for modification."""
    
    @abstractmethod
    def execute(self, task: dict) -> dict:
        """Execute the capability on the given task."""
        pass
    
    @property
    @abstractmethod
    def capability_name(self) -> str:
        """Name of this capability."""
        pass


# Concrete implementations - open for extension
class CodeReviewCapability(AgentCapability):
    """Code review capability."""
    
    @property
    def capability_name(self) -> str:
        return "code-review"
    
    def execute(self, task: dict) -> dict:
        """Review code and provide feedback."""
        code = task.get('code', '')
        
        # Review logic
        issues = self._analyze_code(code)
        suggestions = self._generate_suggestions(issues)
        
        return {
            'status': 'complete',
            'issues_found': len(issues),
            'suggestions': suggestions
        }
    
    def _analyze_code(self, code: str) -> list:
        # Analysis implementation
        pass
    
    def _generate_suggestions(self, issues: list) -> list:
        # Suggestion generation
        pass


class DocumentationCapability(AgentCapability):
    """Documentation generation capability."""
    
    @property
    def capability_name(self) -> str:
        return "documentation"
    
    def execute(self, task: dict) -> dict:
        """Generate documentation."""
        content = task.get('content', '')
        
        # Documentation logic
        docs = self._generate_docs(content)
        
        return {
            'status': 'complete',
            'documentation': docs
        }
    
    def _generate_docs(self, content: str) -> str:
        # Documentation generation
        pass


class SecurityCheckCapability(AgentCapability):
    """Security checking capability - NEW, no modifications needed!"""
    
    @property
    def capability_name(self) -> str:
        return "security-check"
    
    def execute(self, task: dict) -> dict:
        """Check code for security vulnerabilities."""
        code = task.get('code', '')
        
        # Security analysis
        vulnerabilities = self._scan_for_vulnerabilities(code)
        
        return {
            'status': 'complete',
            'vulnerabilities': vulnerabilities,
            'severity': self._assess_severity(vulnerabilities)
        }
    
    def _scan_for_vulnerabilities(self, code: str) -> list:
        # Security scanning
        pass
    
    def _assess_severity(self, vulnerabilities: list) -> str:
        # Severity assessment
        pass


# Executor doesn't need modification to support new capabilities
class CapabilityExecutor:
    """Executes capabilities - never needs modification for new types."""
    
    def __init__(self):
        self._capabilities: dict[str, AgentCapability] = {}
    
    def register_capability(self, capability: AgentCapability) -> None:
        """Register a new capability - extends functionality."""
        self._capabilities[capability.capability_name] = capability
    
    def execute(self, capability_name: str, task: dict) -> dict:
        """Execute a capability by name."""
        if capability_name not in self._capabilities:
            raise ValueError(f"Unknown capability: {capability_name}")
        
        capability = self._capabilities[capability_name]
        return capability.execute(task)


# Usage - can add new capabilities without modifying executor
executor = CapabilityExecutor()

# Register existing capabilities
executor.register_capability(CodeReviewCapability())
executor.register_capability(DocumentationCapability())

# Add NEW capability without modifying any existing code!
executor.register_capability(SecurityCheckCapability())

# Execute any registered capability
result = executor.execute('code-review', {'code': 'def foo(): pass'})
```

**Why this is better:**
- Add new capabilities without modifying `CapabilityExecutor`
- Each capability is independently testable
- No risk of breaking existing capabilities
- Clear extension point for new functionality

### Strategy Pattern Example

Another OCP pattern - different scoring strategies:

```python
class ScoringStrategy(ABC):
    """Base scoring strategy - closed for modification."""
    
    @abstractmethod
    def calculate_score(self, metrics: dict[str, float]) -> float:
        """Calculate score from metrics."""
        pass


class WeightedAverageStrategy(ScoringStrategy):
    """Standard weighted average scoring."""
    
    def __init__(self, weights: dict[str, float]):
        self.weights = weights
    
    def calculate_score(self, metrics: dict[str, float]) -> float:
        total = 0.0
        for key, weight in self.weights.items():
            total += metrics.get(key, 0) * weight
        return total


class ProgressiveStrategy(ScoringStrategy):
    """Progressive scoring with bonuses for consistency."""
    
    def calculate_score(self, metrics: dict[str, float]) -> float:
        base_score = sum(metrics.values()) / len(metrics)
        
        # Bonus for consistent performance
        variance = self._calculate_variance(metrics.values())
        consistency_bonus = max(0, 10 - variance)
        
        return base_score + consistency_bonus
    
    def _calculate_variance(self, values: list) -> float:
        mean = sum(values) / len(values)
        return sum((x - mean) ** 2 for x in values) / len(values)


# Agent class uses strategy - closed for modification, open for extension
class Agent:
    def __init__(self, scoring_strategy: ScoringStrategy):
        self.scoring_strategy = scoring_strategy
        self.metrics = {}
    
    def calculate_score(self) -> float:
        """Calculate score using current strategy."""
        return self.scoring_strategy.calculate_score(self.metrics)
    
    def set_scoring_strategy(self, strategy: ScoringStrategy):
        """Change scoring strategy without modifying Agent class."""
        self.scoring_strategy = strategy


# Usage - add new strategies without touching Agent
standard_weights = {'code_quality': 0.3, 'pr_success': 0.7}
agent = Agent(WeightedAverageStrategy(standard_weights))

# Switch to progressive strategy
agent.set_scoring_strategy(ProgressiveStrategy())
```

---

## L - Liskov Substitution Principle (LSP)

### The Principle

**Objects of a superclass should be replaceable with objects of a subclass without breaking the application.**

### The Analogy

Think of electrical outlets and plugs. Any device with a standard plug should work in any standard outlet. You shouldn't need to check if the outlet "likes" your specific device. If you plug in a lamp instead of a phone charger, the outlet doesn't break.

In code, if you have a base class or interface, any subclass should work wherever the base class works, without surprises.

### The Problem

❌ **Violating LSP** - Subclass breaks parent's contract:

```python
class Agent:
    """Base agent class."""
    
    def execute_task(self, task: dict) -> dict:
        """
        Execute a task and return results.
        
        Returns:
            dict with 'status' and 'result' keys
        """
        # Base implementation
        return {'status': 'success', 'result': 'Task completed'}


class RegularAgent(Agent):
    """Regular agent that follows the contract."""
    
    def execute_task(self, task: dict) -> dict:
        """Execute task normally."""
        if not task:
            return {'status': 'error', 'result': 'No task provided'}
        
        # Do work
        result = self._do_work(task)
        return {'status': 'success', 'result': result}


class ProblematicAgent(Agent):
    """Agent that VIOLATES LSP - changes return type!"""
    
    def execute_task(self, task: dict) -> str:  # ❌ Returns string, not dict!
        """Execute task but return string instead of dict."""
        if not task:
            raise Exception("No task!")  # ❌ Raises exception instead of returning error status
        
        result = self._do_work(task)
        return f"Completed: {result}"  # ❌ String, not dict!


class AnotherProblematicAgent(Agent):
    """Agent that VIOLATES LSP - requires additional preconditions!"""
    
    def execute_task(self, task: dict) -> dict:
        """Execute task but requires task to have 'priority' field."""
        
        # ❌ Adds requirement that base class doesn't have!
        if 'priority' not in task:
            raise ValueError("Task must have priority field")
        
        if task['priority'] != 'high':
            return {'status': 'skipped', 'result': 'Only handle high priority'}
        
        result = self._do_work(task)
        return {'status': 'success', 'result': result}


# This code breaks because of LSP violations
def process_agent_tasks(agents: list[Agent], tasks: list[dict]):
    """Process tasks with any agent - assumes LSP compliance."""
    results = []
    
    for agent in agents:
        for task in tasks:
            # This works for RegularAgent
            # This BREAKS for ProblematicAgent (returns string)
            # This BREAKS for AnotherProblematicAgent (raises exception)
            result = agent.execute_task(task)
            
            # Expects result to be dict with 'status' key
            if result['status'] == 'success':  # ❌ KeyError for ProblematicAgent!
                results.append(result['result'])
    
    return results
```

**Why this is bad:**
- Code that works with base class breaks with subclasses
- Violates "substitutability" - can't swap implementations
- Forces users to check types and handle special cases
- Breaks polymorphism

### The Solution

✅ **Following LSP** - All subclasses honor the contract:

```python
from typing import Optional

class TaskResult:
    """Standardized task result - ensures consistent contract."""
    
    def __init__(
        self,
        status: str,
        result: Optional[str] = None,
        error: Optional[str] = None
    ):
        self.status = status
        self.result = result
        self.error = error
    
    def is_success(self) -> bool:
        return self.status == 'success'


class Agent(ABC):
    """Base agent with clear contract."""
    
    @abstractmethod
    def execute_task(self, task: dict) -> TaskResult:
        """
        Execute a task and return standardized result.
        
        Args:
            task: Task dictionary (may be empty)
            
        Returns:
            TaskResult with status, result, and optional error
            
        Contract:
            - Must return TaskResult (never raise for invalid input)
            - Must handle empty task gracefully
            - Must not require additional task fields beyond what base expects
        """
        pass


class CodeReviewAgent(Agent):
    """Code review agent - follows LSP."""
    
    def execute_task(self, task: dict) -> TaskResult:
        """Execute code review task."""
        # ✅ Handles empty task gracefully
        if not task or 'code' not in task:
            return TaskResult(
                status='error',
                error='Task must contain code to review'
            )
        
        # Do review
        issues = self._review_code(task['code'])
        
        # ✅ Returns TaskResult as promised
        return TaskResult(
            status='success',
            result=f'Found {len(issues)} issues'
        )
    
    def _review_code(self, code: str) -> list:
        # Review implementation
        return []


class DocumentationAgent(Agent):
    """Documentation agent - follows LSP."""
    
    def execute_task(self, task: dict) -> TaskResult:
        """Execute documentation task."""
        # ✅ Handles empty task gracefully
        if not task or 'content' not in task:
            return TaskResult(
                status='error',
                error='Task must contain content to document'
            )
        
        # Generate docs
        docs = self._generate_docs(task['content'])
        
        # ✅ Returns TaskResult as promised
        return TaskResult(
            status='success',
            result=docs
        )
    
    def _generate_docs(self, content: str) -> str:
        # Documentation implementation
        return "# Documentation"


class PriorityAwareAgent(Agent):
    """Agent that considers priority but doesn't require it - follows LSP."""
    
    def execute_task(self, task: dict) -> TaskResult:
        """Execute task, considering priority if provided."""
        # ✅ Doesn't REQUIRE priority field (LSP compliant)
        priority = task.get('priority', 'normal')
        
        if not task or 'code' not in task:
            return TaskResult(
                status='error',
                error='Task must contain code'
            )
        
        # Works with or without priority
        if priority == 'low':
            return TaskResult(
                status='skipped',
                result='Low priority tasks handled later'
            )
        
        # Process task
        result = self._process_code(task['code'])
        
        # ✅ Returns TaskResult as promised
        return TaskResult(
            status='success',
            result=result
        )
    
    def _process_code(self, code: str) -> str:
        # Processing implementation
        return "Processed"


# This code works with ANY Agent subclass - LSP satisfied!
def process_agent_tasks(agents: list[Agent], tasks: list[dict]) -> list[str]:
    """Process tasks with any agent - works because all agents follow LSP."""
    results = []
    
    for agent in agents:
        for task in tasks:
            # ✅ This works for ALL agent types!
            result = agent.execute_task(task)
            
            # ✅ All agents return TaskResult
            if result.is_success():
                results.append(result.result)
            else:
                # Handle errors consistently
                print(f"Task failed: {result.error}")
    
    return results


# Usage - any agent can be substituted
agents = [
    CodeReviewAgent(),
    DocumentationAgent(),
    PriorityAwareAgent()
]

tasks = [
    {'code': 'def foo(): pass'},
    {},  # Empty task - all agents handle gracefully
    {'code': 'def bar(): pass', 'priority': 'high'}  # With priority
]

# Works with any combination - LSP satisfied!
results = process_agent_tasks(agents, tasks)
```

**Why this is better:**
- All agents can be used interchangeably
- No special case handling needed
- Contract is clear and respected
- Polymorphism works as intended

### LSP Rules

**A subclass must:**

1. **Accept same inputs or more permissive** (contravariance)
   - ❌ Bad: Base accepts `task: dict`, subclass requires `task: dict with 'priority'`
   - ✅ Good: Base requires `task: dict with 'code'`, subclass accepts `task: any dict`

2. **Return same outputs or more specific** (covariance)
   - ❌ Bad: Base returns `dict`, subclass returns `str`
   - ✅ Good: Base returns `Agent`, subclass returns `CodeReviewAgent`

3. **Maintain or strengthen postconditions**
   - ❌ Bad: Base guarantees result has 'status', subclass might not include it
   - ✅ Good: Subclass always includes 'status' plus additional fields

4. **Maintain or weaken preconditions**
   - ❌ Bad: Base works with any task, subclass requires specific fields
   - ✅ Good: Base requires 'code' field, subclass works even without it

5. **Preserve invariants**
   - ❌ Bad: Base maintains `score >= 0`, subclass allows negative scores
   - ✅ Good: All implementations maintain `score >= 0`

6. **Not throw new exceptions**
   - ❌ Bad: Base never throws, subclass throws `NetworkError`
   - ✅ Good: All implementations return error status instead of throwing

---

## I - Interface Segregation Principle (ISP)

### The Principle

**No client should be forced to depend on interfaces it doesn't use.**

### The Analogy

Think of a TV remote with 50 buttons. Most people only use 5-10 buttons (power, volume, channel, input). The other 40 buttons add complexity without value. Better to have a simple remote with common functions and an advanced remote for power users.

In code, don't force classes to implement methods they don't need. Split large interfaces into smaller, focused ones.

### The Problem

❌ **Violating ISP** - Fat interface forces unnecessary implementations:

```python
class Agent(ABC):
    """
    Fat interface - forces all agents to implement everything!
    ❌ Violates ISP
    """
    
    @abstractmethod
    def review_code(self, code: str) -> list:
        """Review code and return issues."""
        pass
    
    @abstractmethod
    def write_documentation(self, content: str) -> str:
        """Generate documentation."""
        pass
    
    @abstractmethod
    def run_tests(self, code: str) -> dict:
        """Run tests on code."""
        pass
    
    @abstractmethod
    def check_security(self, code: str) -> list:
        """Check for security issues."""
        pass
    
    @abstractmethod
    def optimize_performance(self, code: str) -> str:
        """Optimize code for performance."""
        pass
    
    @abstractmethod
    def analyze_metrics(self, data: dict) -> dict:
        """Analyze performance metrics."""
        pass


class CodeReviewAgent(Agent):
    """
    Agent that only does code review - forced to implement everything!
    ❌ Violates ISP
    """
    
    def review_code(self, code: str) -> list:
        """Actually used - does code review."""
        return self._analyze_code(code)
    
    # ❌ Forced to implement methods it doesn't need!
    
    def write_documentation(self, content: str) -> str:
        """Not used but must implement!"""
        raise NotImplementedError("This agent doesn't write documentation")
    
    def run_tests(self, code: str) -> dict:
        """Not used but must implement!"""
        raise NotImplementedError("This agent doesn't run tests")
    
    def check_security(self, code: str) -> list:
        """Not used but must implement!"""
        raise NotImplementedError("This agent doesn't check security")
    
    def optimize_performance(self, code: str) -> str:
        """Not used but must implement!"""
        raise NotImplementedError("This agent doesn't optimize performance")
    
    def analyze_metrics(self, data: dict) -> dict:
        """Not used but must implement!"""
        raise NotImplementedError("This agent doesn't analyze metrics")


# Usage breaks because of fat interface
def process_with_agent(agent: Agent, code: str):
    """Try to use agent - might fail!"""
    
    # This works
    issues = agent.review_code(code)
    
    # ❌ This might raise NotImplementedError!
    docs = agent.write_documentation(code)
    
    # ❌ This might raise NotImplementedError!
    tests = agent.run_tests(code)
```

**Why this is bad:**
- Classes forced to implement unused methods
- NotImplementedError shows design flaw
- Hard to understand what each agent actually does
- Violates Single Responsibility

### The Solution

✅ **Following ISP** - Segregated interfaces:

```python
# Small, focused interfaces

class CodeReviewer(ABC):
    """Interface for code review capability."""
    
    @abstractmethod
    def review_code(self, code: str) -> list[str]:
        """Review code and return list of issues."""
        pass


class DocumentationWriter(ABC):
    """Interface for documentation capability."""
    
    @abstractmethod
    def write_documentation(self, content: str) -> str:
        """Generate documentation."""
        pass


class TestRunner(ABC):
    """Interface for test running capability."""
    
    @abstractmethod
    def run_tests(self, code: str) -> dict:
        """Run tests and return results."""
        pass


class SecurityChecker(ABC):
    """Interface for security checking capability."""
    
    @abstractmethod
    def check_security(self, code: str) -> list[str]:
        """Check for security vulnerabilities."""
        pass


class PerformanceOptimizer(ABC):
    """Interface for performance optimization capability."""
    
    @abstractmethod
    def optimize_performance(self, code: str) -> str:
        """Optimize code for performance."""
        pass


# Agents implement only what they need

class CodeReviewOnlyAgent(CodeReviewer):
    """Agent that ONLY does code review - clean interface!"""
    
    def review_code(self, code: str) -> list[str]:
        """Review code."""
        issues = []
        
        # Analysis logic
        if 'TODO' in code:
            issues.append("Contains TODO comments")
        
        if len(code.split('\n')) > 100:
            issues.append("Function too long")
        
        return issues


class FullStackAgent(CodeReviewer, DocumentationWriter, TestRunner):
    """Agent with multiple capabilities - implements what it needs."""
    
    def review_code(self, code: str) -> list[str]:
        """Review code."""
        return self._analyze_code(code)
    
    def write_documentation(self, content: str) -> str:
        """Generate documentation."""
        return self._generate_docs(content)
    
    def run_tests(self, code: str) -> dict:
        """Run tests."""
        return self._execute_tests(code)
    
    # ✅ Doesn't implement SecurityChecker or PerformanceOptimizer
    # because it doesn't need to!


class SecurityFocusedAgent(CodeReviewer, SecurityChecker):
    """Agent focused on security - implements only security interfaces."""
    
    def review_code(self, code: str) -> list[str]:
        """Review for security issues."""
        return self.check_security(code)
    
    def check_security(self, code: str) -> list[str]:
        """Check for security vulnerabilities."""
        vulnerabilities = []
        
        if 'eval(' in code:
            vulnerabilities.append("Dangerous eval() usage detected")
        
        if 'exec(' in code:
            vulnerabilities.append("Dangerous exec() usage detected")
        
        return vulnerabilities


# Usage is clear and type-safe

def review_code_with_agent(reviewer: CodeReviewer, code: str) -> list[str]:
    """
    Review code using any agent that implements CodeReviewer.
    ✅ Clear contract - only requires review_code capability
    """
    return reviewer.review_code(code)


def generate_docs_with_agent(writer: DocumentationWriter, content: str) -> str:
    """
    Generate documentation using any agent that implements DocumentationWriter.
    ✅ Clear contract - only requires write_documentation capability
    """
    return writer.write_documentation(content)


# Works with specialized agents
review_agent = CodeReviewOnlyAgent()
issues = review_code_with_agent(review_agent, "def foo(): pass")  # ✅ Works!

# ✅ Can't pass CodeReviewOnlyAgent to generate_docs_with_agent
# because it doesn't implement DocumentationWriter - type system catches this!

# Works with full-stack agents
fullstack = FullStackAgent()
issues = review_code_with_agent(fullstack, "def foo(): pass")  # ✅ Works!
docs = generate_docs_with_agent(fullstack, "Some content")  # ✅ Works!

# Works with security agents
security = SecurityFocusedAgent()
issues = review_code_with_agent(security, "eval('code')")  # ✅ Works!
# ✅ Can't pass to generate_docs_with_agent - type system catches this!
```

**Why this is better:**
- Agents only implement what they actually do
- No NotImplementedError exceptions
- Clear capabilities from interface implementations
- Easy to combine interfaces for multi-capability agents
- Type system helps catch misuse

### Real Chained Example

Chained's validation utilities follow ISP well - focused functions instead of fat classes:

```python
# ✅ Good ISP - focused validation functions

# Each function is a small, focused interface
def validate_agent_name(agent_name: Any) -> str:
    """Only validates agent names."""
    pass

def validate_file_path(filepath: Union[str, Path]) -> Path:
    """Only validates file paths."""
    pass

def validate_json_structure(data: Any, required_keys: list) -> None:
    """Only validates JSON structure."""
    pass

def validate_url(url: Any) -> str:
    """Only validates URLs."""
    pass

# Users import only what they need!
from validation_utils import validate_agent_name, validate_file_path

# Don't need to depend on URL validation if not using it
```

---

## D - Dependency Inversion Principle (DIP)

### The Principle

**High-level modules should not depend on low-level modules. Both should depend on abstractions.**

### The Analogy

Think of electrical plugs and sockets. Your TV doesn't depend on the specific power plant generating electricity. It depends on the abstract interface: a plug that fits a socket. The power plant can be replaced (coal to solar) without changing your TV.

In code, high-level business logic shouldn't depend on low-level implementation details. Both should depend on abstractions (interfaces).

### The Problem

❌ **Violating DIP** - High-level depends on concrete low-level:

```python
import sqlite3
import json
from pathlib import Path

class AgentService:
    """
    High-level business logic that depends on concrete implementations.
    ❌ Violates DIP
    """
    
    def __init__(self):
        # ❌ Directly depends on SQLite (concrete implementation)
        self.db_connection = sqlite3.connect('agents.db')
        
        # ❌ Directly depends on JSON file storage (concrete implementation)
        self.config_path = Path('.github/agent-system/config.json')
    
    def create_agent(self, name: str, specialization: str) -> dict:
        """Create a new agent."""
        
        # ❌ Business logic mixed with SQLite specifics
        cursor = self.db_connection.cursor()
        cursor.execute(
            'INSERT INTO agents (name, specialization) VALUES (?, ?)',
            (name, specialization)
        )
        self.db_connection.commit()
        agent_id = cursor.lastrowid
        
        # ❌ Business logic mixed with file I/O
        with open(self.config_path) as f:
            config = json.load(f)
        
        return {
            'id': agent_id,
            'name': name,
            'specialization': specialization
        }
    
    def find_agent(self, agent_id: int) -> dict:
        """Find agent by ID."""
        
        # ❌ Directly uses SQLite API
        cursor = self.db_connection.cursor()
        cursor.execute('SELECT * FROM agents WHERE id = ?', (agent_id,))
        row = cursor.fetchone()
        
        if not row:
            raise ValueError(f"Agent not found: {agent_id}")
        
        return {'id': row[0], 'name': row[1], 'specialization': row[2]}
```

**Why this is bad:**
- Can't test without SQLite database
- Hard to switch from SQLite to PostgreSQL
- Hard to switch from JSON files to environment variables
- Business logic tightly coupled to implementation details
- Can't mock dependencies for testing

### The Solution

✅ **Following DIP** - Depend on abstractions:

```python
from abc import ABC, abstractmethod
from typing import Optional

# Abstractions (interfaces) - high-level and low-level depend on these

class AgentRepository(ABC):
    """
    Abstract repository interface.
    ✅ Both high-level (AgentService) and low-level (SQLiteRepository) depend on this
    """
    
    @abstractmethod
    def save(self, agent: dict) -> str:
        """
        Save agent and return ID.
        
        Args:
            agent: Agent data dict with 'name' and 'specialization'
            
        Returns:
            Agent ID
        """
        pass
    
    @abstractmethod
    def find_by_id(self, agent_id: str) -> Optional[dict]:
        """
        Find agent by ID.
        
        Args:
            agent_id: Agent identifier
            
        Returns:
            Agent dict or None if not found
        """
        pass
    
    @abstractmethod
    def find_by_specialization(self, specialization: str) -> list[dict]:
        """Find all agents with given specialization."""
        pass


class ConfigurationProvider(ABC):
    """
    Abstract configuration interface.
    ✅ Both high-level and low-level depend on this
    """
    
    @abstractmethod
    def get(self, key: str) -> Any:
        """Get configuration value by key."""
        pass
    
    @abstractmethod
    def get_all(self) -> dict:
        """Get all configuration."""
        pass


# High-level business logic - depends on abstractions

class AgentService:
    """
    High-level business logic.
    ✅ Follows DIP - depends on abstractions, not concrete implementations
    """
    
    def __init__(
        self,
        repository: AgentRepository,  # ✅ Depends on abstraction
        config: ConfigurationProvider  # ✅ Depends on abstraction
    ):
        self.repository = repository
        self.config = config
    
    def create_agent(self, name: str, specialization: str) -> dict:
        """Create a new agent."""
        # ✅ Pure business logic - no implementation details
        
        # Validate against configuration
        valid_specs = self.config.get('valid_specializations')
        if specialization not in valid_specs:
            raise ValueError(f"Invalid specialization: {specialization}")
        
        # Use repository abstraction
        agent = {
            'name': name,
            'specialization': specialization,
            'status': 'active'
        }
        
        agent_id = self.repository.save(agent)
        agent['id'] = agent_id
        
        return agent
    
    def find_agent(self, agent_id: str) -> dict:
        """Find agent by ID."""
        # ✅ Use repository abstraction
        agent = self.repository.find_by_id(agent_id)
        
        if not agent:
            raise ValueError(f"Agent not found: {agent_id}")
        
        return agent
    
    def find_agents_by_role(self, specialization: str) -> list[dict]:
        """Find all agents with specific specialization."""
        # ✅ Use repository abstraction
        return self.repository.find_by_specialization(specialization)


# Low-level implementations - depend on abstractions

class SQLiteAgentRepository(AgentRepository):
    """
    SQLite implementation of AgentRepository.
    ✅ Follows DIP - implements abstract interface
    """
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._ensure_table_exists()
    
    def save(self, agent: dict) -> str:
        """Save agent to SQLite."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO agents (name, specialization, status) VALUES (?, ?, ?)',
                (agent['name'], agent['specialization'], agent.get('status', 'active'))
            )
            conn.commit()
            return str(cursor.lastrowid)
    
    def find_by_id(self, agent_id: str) -> Optional[dict]:
        """Find agent in SQLite."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT id, name, specialization, status FROM agents WHERE id = ?', 
                          (agent_id,))
            row = cursor.fetchone()
            
            if not row:
                return None
            
            return {
                'id': str(row[0]),
                'name': row[1],
                'specialization': row[2],
                'status': row[3]
            }
    
    def find_by_specialization(self, specialization: str) -> list[dict]:
        """Find agents by specialization in SQLite."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                'SELECT id, name, specialization, status FROM agents WHERE specialization = ?',
                (specialization,)
            )
            rows = cursor.fetchall()
            
            return [
                {'id': str(row[0]), 'name': row[1], 'specialization': row[2], 'status': row[3]}
                for row in rows
            ]
    
    def _ensure_table_exists(self):
        """Create table if it doesn't exist."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS agents (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    specialization TEXT NOT NULL,
                    status TEXT NOT NULL
                )
            ''')


class InMemoryAgentRepository(AgentRepository):
    """
    In-memory implementation for testing.
    ✅ Follows DIP - implements abstract interface
    """
    
    def __init__(self):
        self.agents: dict[str, dict] = {}
        self.next_id = 1
    
    def save(self, agent: dict) -> str:
        """Save agent in memory."""
        agent_id = str(self.next_id)
        self.next_id += 1
        
        self.agents[agent_id] = {
            'id': agent_id,
            'name': agent['name'],
            'specialization': agent['specialization'],
            'status': agent.get('status', 'active')
        }
        
        return agent_id
    
    def find_by_id(self, agent_id: str) -> Optional[dict]:
        """Find agent in memory."""
        return self.agents.get(agent_id)
    
    def find_by_specialization(self, specialization: str) -> list[dict]:
        """Find agents by specialization in memory."""
        return [
            agent for agent in self.agents.values()
            if agent['specialization'] == specialization
        ]


class JSONConfigurationProvider(ConfigurationProvider):
    """
    JSON file configuration provider.
    ✅ Follows DIP - implements abstract interface
    """
    
    def __init__(self, config_path: Path):
        self.config_path = config_path
        self._config = self._load_config()
    
    def get(self, key: str) -> Any:
        """Get configuration value from JSON."""
        return self._config.get(key)
    
    def get_all(self) -> dict:
        """Get all configuration from JSON."""
        return self._config.copy()
    
    def _load_config(self) -> dict:
        """Load configuration from JSON file."""
        with open(self.config_path) as f:
            return json.load(f)


class EnvironmentConfigurationProvider(ConfigurationProvider):
    """
    Environment variable configuration provider.
    ✅ Follows DIP - implements abstract interface
    """
    
    def __init__(self, prefix: str = 'AGENT_'):
        self.prefix = prefix
    
    def get(self, key: str) -> Any:
        """Get configuration from environment variable."""
        env_key = f"{self.prefix}{key.upper()}"
        value = os.getenv(env_key)
        
        # Try to parse as JSON for complex values
        if value and value.startswith('['):
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                pass
        
        return value
    
    def get_all(self) -> dict:
        """Get all configuration from environment variables."""
        config = {}
        for key, value in os.environ.items():
            if key.startswith(self.prefix):
                config_key = key[len(self.prefix):].lower()
                config[config_key] = value
        return config


# Usage - easily swap implementations!

# Production with SQLite and JSON
service = AgentService(
    repository=SQLiteAgentRepository('agents.db'),
    config=JSONConfigurationProvider(Path('.github/config.json'))
)

# Testing with in-memory and environment variables
test_service = AgentService(
    repository=InMemoryAgentRepository(),
    config=EnvironmentConfigurationProvider()
)

# ✅ Same business logic works with different implementations!
agent = service.create_agent('alpha', 'code-review')
test_agent = test_service.create_agent('beta', 'documentation')
```

**Why this is better:**
- Easy to test with mock/in-memory implementations
- Easy to switch from SQLite to PostgreSQL
- Easy to switch from JSON to environment variables
- Business logic independent of implementation details
- Can inject different implementations at runtime

### Testing with DIP

DIP makes testing trivial:

```python
import pytest

class MockRepository(AgentRepository):
    """Mock repository for testing."""
    
    def __init__(self):
        self.saved_agents = []
        self.agents = {}
    
    def save(self, agent: dict) -> str:
        agent_id = f"mock-{len(self.saved_agents)}"
        self.saved_agents.append(agent)
        self.agents[agent_id] = agent
        return agent_id
    
    def find_by_id(self, agent_id: str) -> Optional[dict]:
        return self.agents.get(agent_id)
    
    def find_by_specialization(self, specialization: str) -> list[dict]:
        return [a for a in self.agents.values() if a['specialization'] == specialization]


class MockConfig(ConfigurationProvider):
    """Mock configuration for testing."""
    
    def __init__(self, config: dict):
        self._config = config
    
    def get(self, key: str) -> Any:
        return self._config.get(key)
    
    def get_all(self) -> dict:
        return self._config.copy()


def test_create_agent():
    """Test agent creation with mocks."""
    # ✅ Easy to test - inject mocks
    mock_repo = MockRepository()
    mock_config = MockConfig({
        'valid_specializations': ['code-review', 'documentation']
    })
    
    service = AgentService(mock_repo, mock_config)
    
    # Test
    agent = service.create_agent('test-agent', 'code-review')
    
    # Verify
    assert agent['name'] == 'test-agent'
    assert agent['specialization'] == 'code-review'
    assert len(mock_repo.saved_agents) == 1


def test_create_agent_invalid_specialization():
    """Test validation of specialization."""
    # ✅ Easy to test edge cases
    mock_repo = MockRepository()
    mock_config = MockConfig({
        'valid_specializations': ['code-review']
    })
    
    service = AgentService(mock_repo, mock_config)
    
    # Test invalid specialization
    with pytest.raises(ValueError, match="Invalid specialization"):
        service.create_agent('test-agent', 'invalid-spec')
    
    # Verify nothing was saved
    assert len(mock_repo.saved_agents) == 0
```

---

## Applying SOLID Together

SOLID principles work together. Here's a complete example showing all five:

```python
# SRP - Each class has one responsibility
# OCP - Extend behavior through new classes, not modification
# LSP - All implementations honor contracts
# ISP - Small, focused interfaces
# DIP - Depend on abstractions

from abc import ABC, abstractmethod
from typing import Optional
from dataclasses import dataclass

# Abstractions (DIP)

class AgentRepository(ABC):
    """Repository interface (ISP - focused interface)."""
    
    @abstractmethod
    def save(self, agent: 'Agent') -> None:
        pass
    
    @abstractmethod
    def find_by_id(self, agent_id: str) -> Optional['Agent']:
        pass


class ScoringStrategy(ABC):
    """Scoring interface (ISP - focused interface)."""
    
    @abstractmethod
    def calculate_score(self, metrics: dict) -> float:
        pass


class NotificationService(ABC):
    """Notification interface (ISP - focused interface)."""
    
    @abstractmethod
    def notify(self, message: str) -> None:
        pass


# Domain model (SRP)

@dataclass
class Agent:
    """Agent data model (SRP - only holds state)."""
    id: str
    name: str
    specialization: str
    metrics: dict


# Business logic (SRP, DIP)

class AgentService:
    """
    Agent business logic (SRP - only coordinates business operations).
    Depends on abstractions (DIP).
    """
    
    def __init__(
        self,
        repository: AgentRepository,  # DIP
        scoring: ScoringStrategy,  # DIP
        notifier: NotificationService  # DIP
    ):
        self.repository = repository
        self.scoring = scoring
        self.notifier = notifier
    
    def evaluate_agent(self, agent_id: str) -> float:
        """Evaluate agent and notify if needed."""
        # Retrieve agent
        agent = self.repository.find_by_id(agent_id)
        if not agent:
            raise ValueError(f"Agent not found: {agent_id}")
        
        # Calculate score (LSP - any strategy works)
        score = self.scoring.calculate_score(agent.metrics)
        
        # Notify if score is low
        if score < 30:
            self.notifier.notify(
                f"Agent {agent.name} has low score: {score:.2f}"
            )
        
        return score


# Implementations (LSP - honor contracts, OCP - extend without modification)

class WeightedScoringStrategy(ScoringStrategy):
    """Weighted scoring (LSP - honors ScoringStrategy contract)."""
    
    def __init__(self, weights: dict):
        self.weights = weights
    
    def calculate_score(self, metrics: dict) -> float:
        """Calculate weighted score (LSP - same signature and contract)."""
        return sum(
            metrics.get(key, 0) * weight
            for key, weight in self.weights.items()
        )


class ProgressiveScoringStrategy(ScoringStrategy):
    """Progressive scoring (LSP - honors ScoringStrategy contract, OCP - extends without modifying existing)."""
    
    def calculate_score(self, metrics: dict) -> float:
        """Calculate progressive score (LSP - same signature and contract)."""
        base = sum(metrics.values()) / len(metrics)
        
        # Bonus for consistency
        values = list(metrics.values())
        variance = sum((v - base) ** 2 for v in values) / len(values)
        consistency_bonus = max(0, 10 - variance)
        
        return base + consistency_bonus


class InMemoryRepository(AgentRepository):
    """In-memory storage (LSP - honors AgentRepository contract)."""
    
    def __init__(self):
        self.agents: dict[str, Agent] = {}
    
    def save(self, agent: Agent) -> None:
        """Save to memory (LSP - same signature and contract)."""
        self.agents[agent.id] = agent
    
    def find_by_id(self, agent_id: str) -> Optional[Agent]:
        """Find in memory (LSP - same signature and contract)."""
        return self.agents.get(agent_id)


class EmailNotificationService(NotificationService):
    """Email notifications (LSP - honors NotificationService contract)."""
    
    def notify(self, message: str) -> None:
        """Send email (LSP - same signature and contract)."""
        print(f"Sending email: {message}")


class SlackNotificationService(NotificationService):
    """Slack notifications (LSP - honors NotificationService contract, OCP - extends without modifying existing)."""
    
    def notify(self, message: str) -> None:
        """Send Slack message (LSP - same signature and contract)."""
        print(f"Sending Slack message: {message}")


# Usage - SOLID principles make code flexible and testable

def main():
    # Configure with different implementations
    repository = InMemoryRepository()
    scoring = WeightedScoringStrategy({
        'code_quality': 0.3,
        'issue_resolution': 0.25,
        'pr_success': 0.25,
        'peer_review': 0.2
    })
    notifier = EmailNotificationService()
    
    # Create service (DIP - inject dependencies)
    service = AgentService(repository, scoring, notifier)
    
    # Create and save agent
    agent = Agent(
        id='agent-001',
        name='alpha',
        specialization='code-review',
        metrics={'code_quality': 80, 'issue_resolution': 70, 'pr_success': 60, 'peer_review': 50}
    )
    repository.save(agent)
    
    # Evaluate (LSP - any strategy works)
    score = service.evaluate_agent('agent-001')
    print(f"Agent score: {score}")
    
    # Easy to switch implementations (OCP, DIP)
    service.scoring = ProgressiveScoringStrategy()
    service.notifier = SlackNotificationService()
    score = service.evaluate_agent('agent-001')
    print(f"New score with different strategy: {score}")


if __name__ == '__main__':
    main()
```

## Summary

**S - Single Responsibility**: Each class does one thing  
**O - Open/Closed**: Extend behavior without modifying existing code  
**L - Liskov Substitution**: Subclasses can replace base classes  
**I - Interface Segregation**: Small, focused interfaces  
**D - Dependency Inversion**: Depend on abstractions, not implementations  

**Together they create:**
- ✅ Maintainable code
- ✅ Testable code
- ✅ Flexible code
- ✅ Understandable code

**Remember:**
- SOLID principles are guidelines, not laws
- Apply them when they improve code quality
- Don't force them when they add complexity
- Balance principles with pragmatism

The goal isn't to follow SOLID perfectly—it's to write better code. Use these principles as tools to achieve that goal.

---

*Code is like a building. SOLID principles are the foundation. Get them right, and your code stands strong. Get them wrong, and it crumbles under pressure.*

---

[Related: Code Review Checklist](CODE_REVIEW_CHECKLIST.md) | [Related: Best Practices](BEST_PRACTICES.md) | [Related: Testing Guide](CODE_REVIEW_GUIDE_TESTING.md)
