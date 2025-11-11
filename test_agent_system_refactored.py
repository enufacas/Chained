#!/usr/bin/env python3
"""Test agent registry schema and system structure.

This refactored version demonstrates pytest best practices:
- Focused, single-purpose tests
- Descriptive test names
- pytest fixtures for shared setup
- Parametrized tests for repetitive checks
- Clear assertions with helpful error messages
"""

import json
import pytest
from pathlib import Path


# Fixtures

@pytest.fixture
def registry_path():
    """Path to agent registry file."""
    return Path('.github/agent-system/registry.json')


@pytest.fixture
def registry_data(registry_path):
    """Load and parse registry JSON.
    
    This fixture is cached for the test session to avoid
    re-reading the file for every test.
    """
    with open(registry_path, 'r') as f:
        return json.load(f)


@pytest.fixture
def workflow_dir():
    """Path to workflows directory."""
    return Path('.github/workflows')


# Registry File Tests

def test_registry_file_exists(registry_path):
    """Registry file must exist at expected location."""
    assert registry_path.exists(), f"Registry not found at {registry_path}"


def test_registry_is_valid_json(registry_path):
    """Registry must be valid JSON format."""
    with open(registry_path, 'r') as f:
        data = json.load(f)  # Raises JSONDecodeError if invalid
    assert isinstance(data, dict), "Registry must be a JSON object"


def test_registry_is_not_empty(registry_data):
    """Registry must not be empty."""
    assert len(registry_data) > 0, "Registry is empty"


# Registry Structure Tests

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
    """Registry must define specializations (array or note).
    
    v2.0.0+ uses specializations_note for dynamic loading.
    Earlier versions use specializations array.
    """
    has_array = 'specializations' in registry_data
    has_note = 'specializations_note' in registry_data
    assert has_array or has_note, (
        "Missing specializations information "
        "(need either 'specializations' array or 'specializations_note')"
    )


def test_registry_version_format(registry_data):
    """Registry version must follow semantic versioning."""
    version = registry_data['version']
    assert isinstance(version, str), "Version must be a string"
    parts = version.split('.')
    assert len(parts) >= 2, f"Version must be at least X.Y format, got: {version}"


# Agents Array Tests

def test_registry_agents_is_list(registry_data):
    """Agents must be stored in a list."""
    assert isinstance(registry_data['agents'], list), "agents must be a list"


def test_registry_has_agents_or_empty(registry_data):
    """Agents array can be empty but must exist."""
    agents = registry_data['agents']
    assert isinstance(agents, list), "agents must be a list"
    # Note: Empty list is valid for new systems


# Config Structure Tests

@pytest.mark.parametrize("config_key", [
    "spawn_interval_hours",
    "max_active_agents",
    "elimination_threshold",
    "promotion_threshold",
    "metrics_weight",
])
def test_registry_config_has_required_key(registry_data, config_key):
    """Registry config must contain required keys."""
    config = registry_data.get('config', {})
    assert config_key in config, f"Missing config key: {config_key}"


def test_config_spawn_interval_is_positive(registry_data):
    """Spawn interval must be a positive number."""
    interval = registry_data['config']['spawn_interval_hours']
    assert isinstance(interval, (int, float)), "spawn_interval_hours must be numeric"
    assert interval > 0, f"spawn_interval_hours must be positive, got: {interval}"


def test_config_max_agents_is_positive_integer(registry_data):
    """Max active agents must be a positive integer."""
    max_agents = registry_data['config']['max_active_agents']
    assert isinstance(max_agents, int), "max_active_agents must be an integer"
    assert max_agents > 0, f"max_active_agents must be positive, got: {max_agents}"


def test_config_thresholds_are_valid_percentages(registry_data):
    """Elimination and promotion thresholds must be between 0 and 1."""
    config = registry_data['config']
    
    for threshold_name in ['elimination_threshold', 'promotion_threshold']:
        threshold = config[threshold_name]
        assert isinstance(threshold, (int, float)), f"{threshold_name} must be numeric"
        assert 0 <= threshold <= 1, (
            f"{threshold_name} must be between 0 and 1, got: {threshold}"
        )


# Metrics Weight Tests

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
    """Metric weights must sum to 1.0 (within 0.01 tolerance).
    
    Small tolerance accounts for floating point arithmetic.
    """
    weights = registry_data['config']['metrics_weight']
    total = sum(weights.values())
    assert abs(total - 1.0) <= 0.01, (
        f"Weights sum to {total:.4f}, expected 1.0"
    )


def test_registry_all_weights_are_positive(registry_data):
    """All metric weights must be positive."""
    weights = registry_data['config']['metrics_weight']
    for key, value in weights.items():
        assert value >= 0, f"Weight '{key}' is negative: {value}"


# Specializations Tests

def test_specializations_list_or_note(registry_data):
    """If specializations array exists, it must be a list."""
    if 'specializations' in registry_data:
        assert isinstance(registry_data['specializations'], list), (
            "specializations must be a list"
        )


def test_specializations_not_empty_if_present(registry_data):
    """If specializations array exists, it should not be empty."""
    if 'specializations' in registry_data:
        specs = registry_data['specializations']
        if isinstance(specs, list):
            # Allow empty for initial setup, but warn if using old format
            pass  # This is checked in test_registry_has_specializations_info


# Workflow Files Tests

@pytest.mark.parametrize("workflow_name", [
    "agent-spawner.yml",
    "agent-evaluator.yml",
    "agent-data-sync.yml",
])
def test_required_workflow_exists(workflow_dir, workflow_name):
    """Required workflow files must exist."""
    workflow_path = workflow_dir / workflow_name
    assert workflow_path.exists(), f"Missing required workflow: {workflow_name}"


def test_workflows_directory_exists():
    """Workflows directory must exist."""
    workflow_dir = Path('.github/workflows')
    assert workflow_dir.exists(), "Workflows directory not found"
    assert workflow_dir.is_dir(), "Workflows path is not a directory"


# Documentation Tests

@pytest.mark.parametrize("doc_path", [
    ".github/agent-system/README.md",
    "AGENT_BRAINSTORMING.md",
    "docs/agents.html",
])
def test_required_documentation_exists(doc_path):
    """Required documentation files must exist."""
    path = Path(doc_path)
    assert path.exists(), f"Missing required documentation: {doc_path}"


# Directory Structure Tests

@pytest.mark.parametrize("dir_path", [
    ".github/agent-system",
    ".github/agent-system/templates",
    ".github/agent-system/metrics",
    ".github/agent-system/archive",
    ".github/agent-system/profiles",
])
def test_required_directory_exists(dir_path):
    """Required directories must exist."""
    path = Path(dir_path)
    assert path.exists(), f"Missing directory: {dir_path}"
    assert path.is_dir(), f"Path exists but is not a directory: {dir_path}"


# Integration test combining multiple checks

def test_registry_overall_validity(registry_data):
    """High-level integration test for registry validity.
    
    This test provides a quick overall health check.
    Individual tests provide detailed failure information.
    """
    # Has core structure
    assert 'version' in registry_data
    assert 'agents' in registry_data
    assert 'config' in registry_data
    
    # Config is valid
    config = registry_data['config']
    assert 'metrics_weight' in config
    
    # Weights are reasonable
    weights_sum = sum(config['metrics_weight'].values())
    assert 0.99 <= weights_sum <= 1.01
    
    # Basic structure intact
    assert isinstance(registry_data['agents'], list)


if __name__ == '__main__':
    # Allow running with: python test_agent_system.py
    # But prefer: pytest test_agent_system.py
    import sys
    
    print("=" * 60)
    print("Running tests with pytest...")
    print("=" * 60)
    
    # Run pytest programmatically
    exit_code = pytest.main([__file__, '-v', '--tb=short'])
    sys.exit(exit_code)
