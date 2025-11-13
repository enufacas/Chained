# Code Paradigm Translator

## Overview

The Code Paradigm Translator is a tool that automatically transforms code between different programming paradigms. This enhances the Chained autonomous system's ability to adapt and refactor code patterns dynamically.

## Supported Paradigms

The translator supports bidirectional transformations between:

- **Object-Oriented (OOP)** ↔ **Functional**
- **Imperative** ↔ **Declarative**
- **Procedural** ↔ **Object-Oriented**

## Features

### 1. Paradigm Translation

Transform code from one paradigm to another while preserving functionality:

```python
from paradigm_translator import ParadigmTranslator, Paradigm

translator = ParadigmTranslator()

# Translate imperative to declarative
code = """
doubled = []
for n in numbers:
    doubled.append(n * 2)
"""

result = translator.translate(code, Paradigm.IMPERATIVE, Paradigm.DECLARATIVE)
print(result.translated_code)
# Output: doubled = [n * 2 for n in numbers]
```

### 2. Paradigm Detection

Automatically detect the primary paradigm of existing code:

```python
code = """
class Calculator:
    def add(self, a, b):
        return a + b
"""

detected = translator.detect_paradigm(code)
print(detected)  # Output: Paradigm.OBJECT_ORIENTED
```

### 3. Detailed Transformation Tracking

Get insights into what transformations were applied:

```python
result = translator.translate(code, source, target)
print(f"Success: {result.success}")
print(f"Transformations: {result.transformations_applied}")
print(f"Warnings: {result.warnings}")
```

## Transformation Examples

### Imperative → Declarative

**Before (Imperative):**
```python
evens = []
for n in numbers:
    if n % 2 == 0:
        evens.append(n)
```

**After (Declarative):**
```python
evens = [n for n in numbers if n % 2 == 0]
```

### Declarative → Imperative

**Before (Declarative):**
```python
doubled = [n * 2 for n in numbers]
```

**After (Imperative):**
```python
doubled = []
for n in numbers:
    doubled.append(n * 2)
```

### OOP → Functional

**Before (OOP):**
```python
class Calculator:
    def multiply_by_two(self):
        result = []
        for num in self.numbers:
            result.append(num * 2)
        return result
```

**After (Functional):**
```python
class Calculator:
    def multiply_by_two(self):
        result = list(map(lambda num: num * 2, self.numbers))
        return result
```

### Functional → OOP

**Before (Functional):**
```python
def add(a, b):
    return a + b

def multiply(a, b):
    return a * b
```

**After (OOP):**
```python
class DataProcessor:
    def __init__(self, data):
        self.data = data

    def add(self, a, b):
        return a + b

    def multiply(self, a, b):
        return a * b
```

### Procedural → OOP

**Before (Procedural):**
```python
def process_data(data):
    return data * 2

def validate_data(data):
    return data > 0
```

**After (OOP):**
```python
class DataHandler:
    def __init__(self):
        pass

    def process_data(self, data):
        return data * 2

    def validate_data(self, data):
        return data > 0
```

### OOP → Procedural

**Before (OOP):**
```python
class DataHandler:
    def process(self, data):
        return data * 2
```

**After (Procedural):**
```python
def process(data):
    return data * 2
```

## API Reference

### ParadigmTranslator Class

#### Methods

##### `translate(code: str, source: Paradigm, target: Paradigm) -> TranslationResult`

Translate code from source paradigm to target paradigm.

**Parameters:**
- `code`: Source code to translate
- `source`: Source paradigm (Paradigm enum)
- `target`: Target paradigm (Paradigm enum)

**Returns:**
- `TranslationResult` object containing:
  - `source_paradigm`: Original paradigm
  - `target_paradigm`: Target paradigm
  - `original_code`: Input code
  - `translated_code`: Transformed code
  - `transformations_applied`: List of transformations
  - `success`: Boolean indicating success
  - `warnings`: List of warnings

##### `detect_paradigm(code: str) -> Optional[Paradigm]`

Detect the primary paradigm of the given code.

**Parameters:**
- `code`: Source code to analyze

**Returns:**
- `Paradigm` enum value or `None` if detection fails

### Paradigm Enum

Available paradigms:
- `Paradigm.OBJECT_ORIENTED`
- `Paradigm.FUNCTIONAL`
- `Paradigm.IMPERATIVE`
- `Paradigm.DECLARATIVE`
- `Paradigm.PROCEDURAL`

## Usage in Autonomous System

The paradigm translator enhances the Chained system's capabilities in several ways:

### 1. Code Modernization
Automatically transform legacy procedural code to modern OOP or functional styles.

### 2. Pattern Optimization
Convert imperative loops to declarative comprehensions for better readability and performance.

### 3. Learning from Patterns
Analyze which paradigms work best for specific problem types and automatically apply them.

### 4. Cross-Repository Learning
Translate patterns discovered in one codebase to be applicable in different paradigm contexts.

## Running the Tool

### Basic Usage
```bash
python3 tools/paradigm-translator.py
```

This runs the built-in examples demonstrating various transformations.

### Running Tests
```bash
python3 tools/test_paradigm_translator.py
```

This executes the comprehensive test suite with 17+ test cases.

### Integration in Workflows

Add to `.github/workflows/`:

```yaml
- name: Analyze Code Paradigms
  run: |
    python3 tools/paradigm-translator.py
```

## Limitations

### Current Limitations

1. **Complex Class Hierarchies**: Deep inheritance chains may not translate perfectly
2. **Context Preservation**: Some context-dependent code may require manual adjustment
3. **Side Effects**: Pure functional translations may not handle all side effects
4. **Language-Specific Features**: Currently focused on Python patterns

### Future Enhancements

- Support for more paradigms (reactive, logic programming)
- Multi-language support (JavaScript, Java, etc.)
- AI-driven optimization based on code metrics
- Integration with code quality analysis
- Automatic test generation for translated code

## Design Philosophy

Following Margaret Hamilton's principles:

- **Rigor**: Systematic transformation rules
- **Reliability**: Comprehensive testing
- **Innovation**: Novel pattern detection
- **Defensive Programming**: Error handling and validation
- **Clear Documentation**: Detailed examples and API docs

## Contributing

When adding new transformations:

1. Add transformation strategy method
2. Update `translation_strategies` mapping
3. Add comprehensive test cases
4. Document with examples
5. Consider edge cases and error conditions

## Testing

The test suite (`test_paradigm_translator.py`) includes:

- ✓ All paradigm pair transformations
- ✓ Paradigm detection for each type
- ✓ Error handling and edge cases
- ✓ Multiple transformation tracking
- ✓ Same paradigm handling
- ✓ Unsupported translation handling

Run tests: `python3 tools/test_paradigm_translator.py`

Expected output: `17 passed, 0 failed`

## Performance

- **Fast**: Regex-based transformations are efficient
- **Scalable**: Works with large codebases
- **Memory-Efficient**: Processes code in-memory
- **Non-Destructive**: Original code preserved in result

## Security Considerations

- No code execution during translation
- No external dependencies required
- Safe for untrusted code analysis
- All transformations are static analysis

## Related Tools

- `code-analyzer.py`: Analyzes code patterns and quality
- `code-smell-fixer.py`: Fixes code smells and anti-patterns
- `pattern-matcher.py`: Detects common patterns
- `readability-scorer.py`: Scores code readability

## License

Part of the Chained autonomous AI ecosystem. Open source and available for educational purposes.

---

*Built with rigor and innovation by the engineer-master agent, inspired by Margaret Hamilton's systematic approach to software engineering.*
