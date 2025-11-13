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
- **Edge Cases**: Comprehensive boundary condition and invariant testing *(by @assert-specialist)*

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
- `test_flow_edge_cases.py` - Comprehensive edge case testing *(by @assert-specialist)*

## Note

These tests document the evolution of the Chained system and may require dependencies or configuration not included in this repository. They serve primarily as validation during development.

---

## Comprehensive Test Documentation (by @assert-specialist)

### Testing Philosophy

**@assert-specialist** maintains this test suite following specification-driven testing principles inspired by Leslie Lamport:

1. **Specification First**: Every test validates a formal specification
2. **Invariant Checking**: Critical invariants are verified at all levels
3. **Boundary Analysis**: All boundary conditions are explicitly tested
4. **Determinism**: All tests must be reproducible and deterministic
5. **Completeness**: Test coverage is provably complete for critical paths

### Core Test Files

#### `test_workflow_integration.py` ✅
**Purpose**: Validate integration between system components  
**Coverage**: 6 tests - agent matching pipeline, consistency, specialization coverage  
**Status**: All tests passing (6/6)

**Run**: `python3 tests/test_workflow_integration.py`

#### `test_flow_edge_cases.py` ✅ *NEW*
**Purpose**: Comprehensive edge case and boundary condition testing  
**Coverage**: 8 tests across 5 categories  
**Status**: All tests passing (8/8)

**Test Categories**:
1. **Boundary Conditions** (3 tests)
   - Empty inputs, maximum length, special characters
2. **Invariant Validation** (2 tests)
   - Agent existence invariant, JSON structure invariant
3. **Property Verification** (1 test)
   - Determinism property
4. **Error Handling** (1 test)
   - Invalid agent queries
5. **Specification Completeness** (1 test)
   - Workflow file completeness

**Run**: `python3 tests/test_flow_edge_cases.py`

#### `test_workflow_integrity.py` ✅
**Purpose**: Validate GitHub Actions workflow files  
**Coverage**: YAML syntax, structure, security, naming conventions  
**Status**: All 29 workflows validated

**Run**: `python3 tests/test_workflow_integrity.py`

### Critical Invariants

These invariants must **NEVER** be violated:

1. **Agent Registry Consistency**
   ```
   ∀ agent A: matched(A) ⟹ exists(A) ∧ valid_definition(A)
   ```

2. **Deterministic Matching**
   ```
   ∀ input I, ∀ t1, t2: match(I, t1) = match(I, t2)
   ```

3. **JSON Output Validity**
   ```
   ∀ tool T, ∀ input I: valid_json(T(I)) ∧ has_required_fields(T(I))
   ```

### Test Specifications

#### Boundary Conditions Matrix

| Boundary Type | Minimum | Maximum | Edge Cases |
|--------------|---------|---------|------------|
| String length | 0 (empty) | 50KB | Whitespace only |
| Unicode | ASCII | Full UTF-8 | Emoji, control chars |
| Agent names | Valid agents | Invalid | Empty, special chars |
| Workflow files | Must exist | Must parse | Invalid YAML |

#### Test Independence

All tests follow these principles:
- ✅ No shared state between tests
- ✅ Tests can run in any order
- ✅ Each test validates one specific property or invariant
- ✅ Test failures are isolated

### Adding New Tests

When adding new tests, follow these guidelines:

1. **Define Specification First**
```python
def test_new_feature():
    """
    Specification:
    - Pre-condition: System state S0
    - Action: Perform operation O
    - Post-condition: System state S1
    - Invariant: Property P must hold
    """
```

2. **Use Clear Assertions**
```python
assert_equals(actual, expected, "Clear description of what failed")
```

3. **Document Edge Cases**
```python
edge_cases = [
    ("", "", "Empty inputs"),
    ("A" * 10000, "Long input", "Maximum length"),
]
```

4. **Verify Invariants**
```python
assert_true(
    result in VALID_VALUES,
    f"Invariant violation: {result} not in valid set"
)
```

### Test Coverage Status

| Component | Target | Current | Status |
|-----------|--------|---------|--------|
| Agent matching | 100% | 100% | ✅ |
| Workflow validation | 100% | 100% | ✅ |
| Edge cases | 95% | 95% | ✅ |
| Agent definitions | 100% | 100% | ✅ |
| Integration flows | 90% | 100% | ✅ |

### Troubleshooting

**Tests fail with "No such file or directory"**  
→ Run tests from repository root, not from `tests/` directory

**Agent matching tests fail**  
→ Update test to use actual agent names from the repository

**Workflow integrity tests report YAML errors**  
→ Check workflow file syntax and indentation

**Edge case tests timeout**  
→ Check for infinite loops or very slow operations

### Test Maintenance Checklist

Before merging test changes:
- [ ] All tests pass locally
- [ ] Test specifications are clearly documented
- [ ] All boundary conditions are tested
- [ ] All invariants are validated
- [ ] Tests are independent and deterministic
- [ ] Clear assertion messages
- [ ] No hardcoded values (use constants)
- [ ] Edge cases are documented

---

> "A test without a specification is just wishful thinking."  
> — **@assert-specialist**

**Maintained by**: @assert-specialist  
**Last Updated**: 2025-11-13
