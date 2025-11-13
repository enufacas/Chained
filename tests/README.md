# Test Suite

This directory contains test files for the Chained system.

## Test Files

The test suite includes tests for:

- **Agent System**: Agent matching, spawning, assignment, and lifecycle
- **AI Features**: Knowledge graph, creativity metrics, dynamic orchestration
- **GitHub Integration**: Issue format, workflow integration and integrity
- **Performance**: Optimization tests
- **Security**: Agent matching security
- **Validation**: Agent definition validation, custom agent conventions

## Running Tests

Tests can be run individually or as a suite. Note that many tests expect to be run from the repository root directory:

```bash
# From repository root
python3 tests/test_agent_matching.py

# Or run all tests that support pytest
python3 -m pytest tests/
```

Some tests interact with external tools in the `tools/` directory and expect to find them relative to the repository root.

## Test Organization

- `test_agent_*.py` - Agent system tests
- `test_workflow_*.py` - Workflow-related tests
- `test_github_*.py` - GitHub integration tests
- `test_*_security.py` - Security-focused tests

## Note

These tests document the evolution of the Chained system and may require dependencies or configuration not included in this repository. They serve primarily as validation during development.
