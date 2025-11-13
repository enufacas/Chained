#!/usr/bin/env python3
"""
Tests for protected agent functionality.
Ensures that protected agents cannot be deleted or voted off.
"""

import json
import pytest
from pathlib import Path

# Paths
AGENTS_DIR = Path(".github/agents")
REGISTRY_FILE = Path(".github/agent-system/registry.json")


def test_registry_has_protected_specializations():
    """Test that the registry has a protected_specializations config."""
    with open(REGISTRY_FILE, 'r') as f:
        registry = json.load(f)
    
    assert 'config' in registry, "Registry must have a config section"
    assert 'protected_specializations' in registry['config'], \
        "Registry config must include protected_specializations"
    
    protected = registry['config']['protected_specializations']
    assert isinstance(protected, list), "protected_specializations must be a list"


def test_troubleshoot_expert_is_protected():
    """Test that troubleshoot-expert is in the protected list."""
    with open(REGISTRY_FILE, 'r') as f:
        registry = json.load(f)
    
    protected = registry['config']['protected_specializations']
    assert 'troubleshoot-expert' in protected, \
        "troubleshoot-expert must be in protected_specializations"


def test_troubleshoot_expert_agent_exists():
    """Test that the troubleshoot-expert agent definition file exists."""
    agent_file = AGENTS_DIR / "troubleshoot-expert.md"
    assert agent_file.exists(), \
        f"Protected agent definition must exist at {agent_file}"


def test_troubleshoot_expert_has_protected_marker():
    """Test that troubleshoot-expert agent file indicates protected status."""
    agent_file = AGENTS_DIR / "troubleshoot-expert.md"
    
    with open(agent_file, 'r') as f:
        content = f.read()
    
    # Check that the description mentions protected status
    assert 'protected' in content.lower() or 'cannot be deleted' in content.lower(), \
        "Agent definition should indicate protected status"
    
    # Check for the protected emoji or marker
    assert '🛡️' in content or 'Protected' in content, \
        "Agent should have protected marker (🛡️) in content"


def test_troubleshoot_expert_has_github_actions_tools():
    """Test that troubleshoot-expert has GitHub Actions-related tools."""
    agent_file = AGENTS_DIR / "troubleshoot-expert.md"
    
    with open(agent_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Parse YAML frontmatter
    assert content.startswith('---'), "Agent file must have YAML frontmatter"
    parts = content.split('---', 2)
    assert len(parts) >= 3, "Agent file must have complete YAML frontmatter"
    
    frontmatter = parts[1]
    
    # Check for workflow-related tools
    workflow_tools = [
        'list_workflows',
        'list_workflow_runs',
        'get_workflow_run',
        'list_workflow_jobs',
        'get_job_logs',
        'summarize_job_log_failures',
        'summarize_run_log_failures'
    ]
    
    found_tools = 0
    for tool in workflow_tools:
        if tool in frontmatter:
            found_tools += 1
    
    assert found_tools >= 5, \
        f"Protected agent should have at least 5 GitHub Actions tools, found {found_tools}"


def test_protected_agents_readme_documentation():
    """Test that protected agents are documented in the README."""
    agents_readme = AGENTS_DIR / "README.md"
    
    with open(agents_readme, 'r') as f:
        content = f.read()
    
    assert 'troubleshoot-expert' in content.lower(), \
        "troubleshoot-expert should be listed in agents README"
    
    assert 'protected' in content.lower(), \
        "README should mention protected status"


def test_agent_system_readme_documents_protected():
    """Test that the agent system README documents protected agents."""
    system_readme = Path(".github/agent-system/README.md")
    
    with open(system_readme, 'r') as f:
        content = f.read()
    
    assert 'protected' in content.lower(), \
        "Agent system README should document protected agents"
    
    assert 'cannot be deleted' in content.lower() or 'cannot be eliminated' in content.lower(), \
        "Agent system README should explain that protected agents cannot be deleted"


def test_evaluator_workflow_checks_protected_status():
    """Test that the evaluator workflow checks for protected agents."""
    evaluator_workflow = Path(".github/workflows/agent-evaluator.yml")
    
    with open(evaluator_workflow, 'r') as f:
        content = f.read()
    
    assert 'protected_specializations' in content, \
        "Evaluator workflow should check protected_specializations"
    
    assert 'is_protected' in content or 'protected' in content.lower(), \
        "Evaluator workflow should have logic for protected agents"


def test_protected_agent_cannot_be_eliminated_in_evaluator():
    """Test that the evaluator workflow skips elimination for protected agents."""
    evaluator_workflow = Path(".github/workflows/agent-evaluator.yml")
    
    with open(evaluator_workflow, 'r') as f:
        content = f.read()
    
    # Look for logic that skips protected agents
    assert 'continue' in content or 'skip' in content.lower(), \
        "Evaluator should skip or continue for protected agents"
    
    # Should not eliminate protected agents
    lines = content.split('\n')
    protected_check_found = False
    for i, line in enumerate(lines):
        if 'is_protected' in line or 'protected_specializations' in line:
            protected_check_found = True
            # Check nearby lines for skip/continue logic
            nearby = '\n'.join(lines[max(0, i-5):min(len(lines), i+10)])
            if 'continue' in nearby or 'skip' in nearby.lower():
                break
    
    assert protected_check_found, \
        "Evaluator workflow should check for protected status and skip elimination"


def test_all_protected_agents_exist():
    """Test that all agents listed as protected have definition files."""
    with open(REGISTRY_FILE, 'r') as f:
        registry = json.load(f)
    
    protected = registry['config']['protected_specializations']
    
    for specialization in protected:
        agent_file = AGENTS_DIR / f"{specialization}.md"
        assert agent_file.exists(), \
            f"Protected agent {specialization} must have definition file at {agent_file}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
