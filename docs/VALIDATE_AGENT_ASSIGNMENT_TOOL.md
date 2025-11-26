# Agent Assignment Validation Tool

**Created by @create-guru** as part of the direct custom agent assignment test.

## Overview

This tool validates that custom agent assignments are properly configured in the Chained repository. It verifies:

- ✅ Agent definition files exist
- ✅ Agent metadata is properly formatted
- ✅ Agent tools are configured
- ✅ All agents can be listed and validated

## Usage

### Validate a Specific Agent

```bash
python3 tools/validate-agent-assignment.py validate <agent-name>
```

**Example:**
```bash
python3 tools/validate-agent-assignment.py validate create-guru
```

**Output:**
```
🔍 Validating agent assignment: @create-guru
======================================================================
✅ Agent definition exists: .github/agents/create-guru.md
✅ Agent info retrieved successfully
✅ Agent has tools configured
======================================================================
✅ Agent @create-guru is properly configured for assignment
```

### List All Available Agents

```bash
python3 tools/validate-agent-assignment.py list
```

**Output:**
```
📋 Available Agents:
======================================================================
  • @create-guru
  • @engineer-master
  • @secure-specialist
  ... (100+ agents)

Total: 103 agents
```

### Verbose Mode

Add `-v` or `--verbose` for detailed information:

```bash
python3 tools/validate-agent-assignment.py validate create-guru -v
```

## Testing

Run the test suite to verify the tool works correctly:

```bash
python3 tests/test_validate_agent_assignment.py
```

## Integration

This tool can be used in workflows to verify agent configurations:

```yaml
- name: Validate Agent Assignment
  run: |
    python3 tools/validate-agent-assignment.py validate ${{ env.AGENT_NAME }}
```

## Architecture

The tool follows **@create-guru**'s infrastructure design principles:

- **Modular**: Reusable `AgentAssignmentValidator` class
- **Tested**: Comprehensive test coverage
- **Documented**: Clear usage examples
- **Robust**: Error handling and validation

## Related Files

- **Tool**: `tools/validate-agent-assignment.py`
- **Tests**: `tests/test_validate_agent_assignment.py`
- **Agent Definitions**: `.github/agents/*.md`
- **Assignment Script**: `tools/assign-agent-directly.sh`

---

*Created with inventive flair by **@create-guru** 🏭 - Infrastructure creation inspired by Nikola Tesla*
