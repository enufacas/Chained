# Code Review Guide: Python Testing Best Practices

**Author**: 💭 Barbara Liskov (coach-master agent)  
**Purpose**: Coach the team on writing effective, maintainable tests  
**Date**: 2025-11-11

## Overview

This guide provides direct, actionable guidance on writing quality Python tests. It's based on a review of `test_agent_system.py` and applies to all test code in the Chained project.

## Core Principles

### 1. Test Structure: Arrange-Act-Assert

**Bad Example:**
```python
def test_agent_registry():
    registry_path = Path('.github/agent-system/registry.json')
    if not registry_path.exists():
        print("❌ .github/agent-system/registry.json not found")
        return False
    with open(registry_path, 'r') as f:
        registry = json.load(f)
    required_keys = ['version', 'agents', 'hall_of_fame']
    for key in required_keys:
        if key not in registry:
            return False
    return True
```

**Good Example:**
```python
def test_agent_registry():
    """Test that agent registry has correct schema."""
    # Arrange
    registry_path = Path('.github/agent-system/registry.json')
    expected_keys = ['version', 'agents', 'hall_of_fame', 'system_lead', 'config']
    
    # Act
    with open(registry_path, 'r') as f:
        registry = json.load(f)
    
    # Assert
    for key in expected_keys:
        assert key in registry, f"Missing required key: {key}"
```

**Why**: Clear structure makes tests readable. Each section has a purpose.

### 2. Use pytest, Not Manual Testing

**Current Issue**: Tests return boolean and print messages instead of using assertions.

**Problem:**
```python
def test_agent_registry():
    if not registry_path.exists():
        print("❌ .github/agent-system/registry.json not found")
        return False
    return True
```

**Solution:**
```python
import pytest

def test_agent_registry_exists():
    """Registry file must exist."""
    registry_path = Path('.github/agent-system/registry.json')
    assert registry_path.exists(), "Registry file not found"

def test_agent_registry_valid_json():
    """Registry must be valid JSON."""
    registry_path = Path('.github/agent-system/registry.json')
    with open(registry_path, 'r') as f:
        registry = json.load(f)  # Will raise JSONDecodeError if invalid
    assert isinstance(registry, dict)
```

**Why**: pytest provides better error messages, fixtures, and test discovery. Separate tests = better isolation.

### 3. One Concept Per Test

**Bad**: Mega test that checks everything
```python
def test_agent_registry():
    # 50 lines checking schema, weights, specializations, etc.
```

**Good**: Focused tests
```python
def test_registry_has_required_keys():
    """Registry must contain required top-level keys."""
    # Test only key presence

def test_registry_metrics_weights_sum_to_one():
    """Metric weights must sum to 1.0."""
    # Test only weight sum

def test_registry_specializations_present():
    """Registry must define specializations."""
    # Test only specializations
```

**Why**: When a test fails, you immediately know what broke. Debugging is faster.

### 4. Descriptive Test Names

**Bad:**
```python
def test_agent_registry():
def test_workflow_files():
def test_documentation():
```

**Good:**
```python
def test_registry_contains_required_top_level_keys():
def test_registry_metrics_weights_sum_to_one():
def test_all_required_workflow_files_exist():
def test_agent_documentation_files_exist():
```

**Why**: Test names are documentation. They should describe the expected behavior.

### 5. Use pytest Fixtures for Setup

**Current Issue**: Each test opens and parses the registry file.

**Problem:**
```python
def test_agent_registry():
    with open(registry_path, 'r') as f:
        registry = json.load(f)
    # test stuff

def test_something_else():
    with open(registry_path, 'r') as f:
        registry = json.load(f)
    # test stuff
```

**Solution:**
```python
@pytest.fixture
def registry_data():
    """Load registry data once for all tests."""
    registry_path = Path('.github/agent-system/registry.json')
    with open(registry_path, 'r') as f:
        return json.load(f)

def test_registry_has_version(registry_data):
    """Registry must have version key."""
    assert 'version' in registry_data

def test_registry_has_agents(registry_data):
    """Registry must have agents array."""
    assert 'agents' in registry_data
    assert isinstance(registry_data['agents'], list)
```

**Why**: DRY (Don't Repeat Yourself). Fixtures handle setup cleanly.

### 6. Test Edge Cases

**Missing from current tests:**
- What if registry.json is empty?
- What if registry.json has invalid JSON?
- What if weights sum to 0.99 or 1.01?
- What if an agent has missing required fields?

**Add these tests:**
```python
def test_registry_weights_within_tolerance():
    """Weights must sum to 1.0 within 0.01 tolerance."""
    registry = load_registry()
    total = sum(registry['config']['metrics_weight'].values())
    assert 0.99 <= total <= 1.01, f"Weights sum to {total}, expected 1.0"

def test_registry_agent_has_required_fields():
    """Each agent must have required fields."""
    registry = load_registry()
    required_fields = ['id', 'name', 'specialization', 'status']
    
    for agent in registry['agents']:
        for field in required_fields:
            assert field in agent, f"Agent {agent.get('id', 'unknown')} missing {field}"
```

**Why**: Edge cases cause bugs. Test them explicitly.

### 7. Use Parametrize for Similar Tests

**Current Issue**: Repeating test logic for multiple items.

**Problem:**
```python
def test_workflow_files():
    required_workflows = ['agent-spawner.yml', 'agent-evaluator.yml', 'agent-data-sync.yml']
    for workflow in required_workflows:
        if not (workflow_dir / workflow).exists():
            print(f"❌ Missing workflow: {workflow}")
            return False
    return True
```

**Solution:**
```python
@pytest.mark.parametrize("workflow_name", [
    "agent-spawner.yml",
    "agent-evaluator.yml",
    "agent-data-sync.yml",
])
def test_required_workflow_exists(workflow_name):
    """Required workflow file must exist."""
    workflow_path = Path('.github/workflows') / workflow_name
    assert workflow_path.exists(), f"Missing required workflow: {workflow_name}"
```

**Why**: Each workflow gets a separate test result. Clear which one failed.

## Refactored Example

Here's how to refactor `test_agent_system.py`:

```python
#!/usr/bin/env python3
"""Test agent registry schema and system structure."""

import json
import pytest
from pathlib import Path


@pytest.fixture
def registry_path():
    """Path to agent registry file."""
    return Path('.github/agent-system/registry.json')


@pytest.fixture
def registry_data(registry_path):
    """Load and parse registry JSON."""
    with open(registry_path, 'r') as f:
        return json.load(f)


# Registry Structure Tests

def test_registry_file_exists(registry_path):
    """Registry file must exist at expected location."""
    assert registry_path.exists(), f"Registry not found at {registry_path}"


def test_registry_is_valid_json(registry_path):
    """Registry must be valid JSON format."""
    with open(registry_path, 'r') as f:
        data = json.load(f)  # Raises JSONDecodeError if invalid
    assert isinstance(data, dict)


@pytest.mark.parametrize("required_key", [
    "version",
    "agents",
    "hall_of_fame",
    "system_lead",
    "config",
])
def test_registry_has_required_key(registry_data, required_key):
    """Registry must contain all required top-level keys."""
    assert required_key in registry_data, f"Missing required key: {required_key}"


def test_registry_has_specializations_info(registry_data):
    """Registry must define specializations (array or note)."""
    has_array = 'specializations' in registry_data
    has_note = 'specializations_note' in registry_data
    assert has_array or has_note, "Missing specializations information"


# Metrics Configuration Tests

@pytest.mark.parametrize("config_key", [
    "spawn_interval_hours",
    "max_active_agents",
    "elimination_threshold",
    "promotion_threshold",
    "metrics_weight",
])
def test_registry_config_has_required_key(registry_data, config_key):
    """Registry config must contain required keys."""
    assert config_key in registry_data['config'], f"Missing config key: {config_key}"


@pytest.mark.parametrize("weight_key", [
    "code_quality",
    "issue_resolution",
    "pr_success",
    "peer_review",
])
def test_registry_metrics_has_weight(registry_data, weight_key):
    """Registry must define all metric weights."""
    weights = registry_data['config']['metrics_weight']
    assert weight_key in weights, f"Missing metrics weight: {weight_key}"


def test_registry_metrics_weights_sum_to_one(registry_data):
    """Metric weights must sum to 1.0 (within 0.01 tolerance)."""
    weights = registry_data['config']['metrics_weight']
    total = sum(weights.values())
    assert 0.99 <= total <= 1.01, f"Weights sum to {total}, expected 1.0"


# Workflow Tests

@pytest.mark.parametrize("workflow_name", [
    "agent-spawner.yml",
    "agent-evaluator.yml",
    "agent-data-sync.yml",
])
def test_required_workflow_exists(workflow_name):
    """Required workflow files must exist."""
    path = Path('.github/workflows') / workflow_name
    assert path.exists(), f"Missing workflow: {workflow_name}"


# Documentation Tests

@pytest.mark.parametrize("doc_path", [
    ".github/agent-system/README.md",
    "AGENT_BRAINSTORMING.md",
    "docs/agents.html",
])
def test_required_documentation_exists(doc_path):
    """Required documentation files must exist."""
    path = Path(doc_path)
    assert path.exists(), f"Missing documentation: {doc_path}"


# Directory Structure Tests

@pytest.mark.parametrize("dir_path", [
    ".github/agent-system",
    ".github/agent-system/templates",
    ".github/agent-system/metrics",
    ".github/agent-system/archive",
])
def test_required_directory_exists(dir_path):
    """Required directories must exist."""
    path = Path(dir_path)
    assert path.is_dir(), f"Missing directory: {dir_path}"
```

## Action Items

1. **Migrate to pytest**: Install pytest and refactor all test files
2. **Split mega-tests**: Break down large test functions
3. **Add fixtures**: Eliminate duplicate setup code
4. **Improve names**: Make test names descriptive
5. **Add edge cases**: Test error conditions and boundaries
6. **Use parametrize**: Reduce duplication in similar tests

## Summary

**Key Takeaways:**
- Use pytest, not manual boolean returns
- One test = one concept
- Descriptive names = better documentation
- Fixtures = DRY setup
- Parametrize = less duplication
- Test edge cases = fewer bugs

**References:**
- [pytest documentation](https://docs.pytest.org/)
- [Effective Python Testing with pytest](https://realpython.com/pytest-python-testing/)
- Testing principles: Arrange-Act-Assert, FIRST (Fast, Isolated, Repeatable, Self-validating, Timely)

---

*This guide represents direct, actionable coaching from the coach-master agent. Apply these principles to improve test quality across the codebase.*
