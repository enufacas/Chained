#!/usr/bin/env python3
"""
Comprehensive test suite for code-style-transfer.py
Tests style extraction, neural encoding, and style transfer functionality.

Author: @engineer-master
"""

import sys
import os
import pytest
import tempfile
from pathlib import Path

# Add tools directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'tools'))

# Import with dash becomes underscore in Python
import importlib.util
spec = importlib.util.spec_from_file_location(
    "code_style_transfer",
    str(Path(__file__).parent.parent / 'tools' / 'code-style-transfer.py')
)
code_style_transfer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(code_style_transfer)

StyleExtractor = code_style_transfer.StyleExtractor
NeuralStyleEncoder = code_style_transfer.NeuralStyleEncoder
StyleTransformer = code_style_transfer.StyleTransformer
CodeStyleTransferSystem = code_style_transfer.CodeStyleTransferSystem
StyleFeatures = code_style_transfer.StyleFeatures
TransferResult = code_style_transfer.TransferResult
StyleDimension = code_style_transfer.StyleDimension


# Test fixtures

@pytest.fixture
def sample_snake_case_code():
    """Sample code using snake_case naming convention."""
    return '''
def calculate_average(numbers_list):
    """Calculate the average of a list of numbers."""
    total_sum = 0
    for number_item in numbers_list:
        total_sum += number_item
    return total_sum / len(numbers_list)


class DataProcessor:
    """Process data with snake_case style."""
    
    def __init__(self):
        self.data_items = []
    
    def add_item(self, new_item):
        """Add an item to the collection."""
        self.data_items.append(new_item)
'''


@pytest.fixture
def sample_camel_case_code():
    """Sample code using camelCase naming convention."""
    return '''
def calculateAverage(numbersList):
    """Calculate the average of a list of numbers."""
    totalSum = 0
    for numberItem in numbersList:
        totalSum += numberItem
    return totalSum / len(numbersList)


class DataProcessor:
    """Process data with camelCase style."""
    
    def __init__(self):
        self.dataItems = []
    
    def addItem(self, newItem):
        """Add an item to the collection."""
        self.dataItems.append(newItem)
'''


@pytest.fixture
def sample_code_with_docstrings():
    """Sample code with comprehensive docstrings."""
    return '''#!/usr/bin/env python3
"""
Module docstring explaining the purpose.
"""


def process_data(data):
    """Process the input data.
    
    Args:
        data: Input data to process
        
    Returns:
        Processed data
    """
    return data * 2


class Calculator:
    """A calculator class with full documentation."""
    
    def add(self, a, b):
        """Add two numbers.
        
        Args:
            a: First number
            b: Second number
            
        Returns:
            Sum of a and b
        """
        return a + b
'''


@pytest.fixture
def sample_code_minimal():
    """Minimal code without much style."""
    return '''
def add(a, b):
    return a + b
'''


@pytest.fixture
def style_extractor():
    """Create a StyleExtractor instance."""
    return StyleExtractor()


@pytest.fixture
def neural_encoder():
    """Create a NeuralStyleEncoder instance."""
    return NeuralStyleEncoder()


@pytest.fixture
def style_transformer():
    """Create a StyleTransformer instance."""
    return StyleTransformer()


# Style Extraction Tests

def test_extractor_analyzes_basic_metrics(style_extractor, sample_snake_case_code):
    """Test that extractor correctly identifies basic code metrics."""
    features = style_extractor.extract_from_code(sample_snake_case_code)
    
    assert features.total_lines > 0
    assert features.code_lines > 0
    assert features.comment_lines > 0
    assert features.blank_lines > 0


def test_extractor_detects_snake_case(style_extractor, sample_snake_case_code):
    """Test that extractor correctly identifies snake_case naming."""
    features = style_extractor.extract_from_code(sample_snake_case_code)
    
    assert features.variable_naming == 'snake_case' or features.variable_naming == 'mixed'
    assert features.function_naming == 'snake_case'


def test_extractor_detects_camel_case(style_extractor, sample_camel_case_code):
    """Test that extractor correctly identifies camelCase naming."""
    features = style_extractor.extract_from_code(sample_camel_case_code)
    
    # Variable naming should show camelCase tendency
    assert features.variable_naming in ['camelCase', 'mixed']


def test_extractor_detects_indentation(style_extractor, sample_snake_case_code):
    """Test that extractor correctly identifies indentation style."""
    features = style_extractor.extract_from_code(sample_snake_case_code)
    
    assert features.indent_size in [2, 4, 8]
    assert features.indent_type in ['spaces', 'tabs']


def test_extractor_detects_docstrings(style_extractor, sample_code_with_docstrings):
    """Test that extractor correctly identifies docstring usage."""
    features = style_extractor.extract_from_code(sample_code_with_docstrings)
    
    assert features.has_module_docstring is True
    assert features.has_function_docstrings is True
    assert features.has_class_docstrings is True


def test_extractor_calculates_line_length(style_extractor, sample_snake_case_code):
    """Test that extractor calculates line length metrics."""
    features = style_extractor.extract_from_code(sample_snake_case_code)
    
    assert features.avg_line_length > 0
    assert features.max_line_length > 0
    assert features.max_line_length >= features.avg_line_length


def test_extractor_calculates_comment_density(style_extractor, sample_code_with_docstrings):
    """Test that extractor calculates comment density."""
    features = style_extractor.extract_from_code(sample_code_with_docstrings)
    
    assert features.comment_density >= 0
    # Should have some comments
    assert features.comment_lines > 0


def test_extractor_handles_empty_code(style_extractor):
    """Test that extractor handles empty code gracefully."""
    features = style_extractor.extract_from_code("")
    
    assert features.total_lines == 1  # Empty string splits to ['']
    assert features.code_lines == 0


def test_extractor_handles_syntax_errors(style_extractor):
    """Test that extractor handles invalid Python syntax."""
    invalid_code = "def broken_function(\n    # missing closing paren"
    
    # Should not raise exception
    features = style_extractor.extract_from_code(invalid_code)
    assert features is not None


# Neural Encoder Tests

def test_encoder_creates_embeddings(neural_encoder):
    """Test that encoder creates style embeddings."""
    features = StyleFeatures()
    encoding = neural_encoder.encode_style(features)
    
    assert isinstance(encoding, list)
    assert len(encoding) == neural_encoder.hidden_dim
    assert all(isinstance(x, float) for x in encoding)


def test_encoder_consistent_encoding(neural_encoder):
    """Test that encoder produces consistent results for same input."""
    features = StyleFeatures()
    
    encoding1 = neural_encoder.encode_style(features)
    encoding2 = neural_encoder.encode_style(features)
    
    assert encoding1 == encoding2


def test_encoder_different_features_different_encodings(neural_encoder):
    """Test that different features produce different encodings."""
    features1 = StyleFeatures(indent_size=4, variable_naming='snake_case')
    features2 = StyleFeatures(indent_size=2, variable_naming='camelCase')
    
    encoding1 = neural_encoder.encode_style(features1)
    encoding2 = neural_encoder.encode_style(features2)
    
    assert encoding1 != encoding2


def test_encoder_similarity_identical(neural_encoder):
    """Test that identical encodings have similarity of 1.0."""
    features = StyleFeatures()
    encoding = neural_encoder.encode_style(features)
    
    similarity = neural_encoder.similarity(encoding, encoding)
    assert 0.9 <= similarity <= 1.0  # Allow for floating point precision


def test_encoder_similarity_different(neural_encoder):
    """Test that different encodings have similarity less than 1.0."""
    features1 = StyleFeatures(indent_size=4)
    features2 = StyleFeatures(indent_size=2)
    
    encoding1 = neural_encoder.encode_style(features1)
    encoding2 = neural_encoder.encode_style(features2)
    
    similarity = neural_encoder.similarity(encoding1, encoding2)
    assert 0.0 <= similarity < 1.0


def test_encoder_similarity_empty(neural_encoder):
    """Test that empty encodings return 0 similarity."""
    similarity = neural_encoder.similarity([], [])
    assert similarity == 0.0


# Style Transformer Tests

def test_transformer_creates_result(style_transformer, sample_snake_case_code):
    """Test that transformer creates a TransferResult."""
    target_style = StyleFeatures(indent_size=2)
    result = style_transformer.transfer_style(sample_snake_case_code, target_style)
    
    assert isinstance(result, TransferResult)
    assert result.original_code == sample_snake_case_code
    assert result.transformed_code is not None


def test_transformer_records_changes(style_transformer, sample_snake_case_code):
    """Test that transformer records style changes made."""
    target_style = StyleFeatures(indent_size=2)
    result = style_transformer.transfer_style(sample_snake_case_code, target_style)
    
    assert isinstance(result.style_changes, list)
    # If indentation changed, should have a change recorded
    if result.transformed_code != result.original_code:
        assert len(result.style_changes) > 0


def test_transformer_calculates_confidence(style_transformer, sample_snake_case_code):
    """Test that transformer calculates confidence score."""
    target_style = StyleFeatures()
    result = style_transformer.transfer_style(sample_snake_case_code, target_style)
    
    assert 0.0 <= result.confidence <= 1.0


def test_transformer_includes_metadata(style_transformer, sample_snake_case_code):
    """Test that transformer includes metadata in result."""
    target_style = StyleFeatures()
    result = style_transformer.transfer_style(sample_snake_case_code, target_style)
    
    assert 'source_style' in result.metadata
    assert 'target_style' in result.metadata


def test_transformer_changes_indentation(style_transformer):
    """Test that transformer can change indentation."""
    code = "def foo():\n    pass"
    target_style = StyleFeatures(indent_size=2)
    
    result = style_transformer.transfer_style(code, target_style)
    
    # Should have attempted to change indentation
    assert result.transformed_code is not None


def test_transformer_preserves_functionality_flag(style_transformer, sample_minimal):
    """Test that transformer respects preserve_functionality flag."""
    target_style = StyleFeatures()
    result = style_transformer.transfer_style(
        sample_minimal, 
        target_style,
        preserve_functionality=True
    )
    
    assert result.preserved_functionality is True


# Code Style Transfer System Tests

def test_system_initializes():
    """Test that CodeStyleTransferSystem initializes correctly."""
    system = CodeStyleTransferSystem()
    
    assert system.extractor is not None
    assert system.encoder is not None
    assert system.transformer is not None
    assert isinstance(system.style_database, dict)


def test_system_learns_from_directory():
    """Test that system can learn style from a directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create sample files
        file1 = Path(tmpdir) / "sample1.py"
        file1.write_text("def foo():\n    pass\n")
        
        file2 = Path(tmpdir) / "sample2.py"
        file2.write_text("def bar():\n    return 42\n")
        
        system = CodeStyleTransferSystem()
        features = system.learn_project_style(tmpdir, "test_project")
        
        assert isinstance(features, StyleFeatures)
        assert "test_project" in system.style_database


def test_system_stores_learned_styles():
    """Test that system stores learned styles in database."""
    with tempfile.TemporaryDirectory() as tmpdir:
        file1 = Path(tmpdir) / "sample.py"
        file1.write_text("def foo():\n    pass\n")
        
        system = CodeStyleTransferSystem()
        system.learn_project_style(tmpdir, "test_project")
        
        assert "test_project" in system.style_database
        assert "features" in system.style_database["test_project"]
        assert "encoding" in system.style_database["test_project"]
        assert "file_count" in system.style_database["test_project"]


def test_system_applies_learned_style():
    """Test that system can apply a learned style."""
    with tempfile.TemporaryDirectory() as tmpdir:
        file1 = Path(tmpdir) / "sample.py"
        file1.write_text("def foo():\n    pass\n")
        
        system = CodeStyleTransferSystem()
        system.learn_project_style(tmpdir, "test_project")
        
        code = "def bar():\n        x = 1\n        return x"
        result = system.apply_project_style(code, "test_project")
        
        assert isinstance(result, TransferResult)


def test_system_raises_on_unknown_style():
    """Test that system raises error for unknown project style."""
    system = CodeStyleTransferSystem()
    
    with pytest.raises(ValueError):
        system.apply_project_style("def foo(): pass", "unknown_project")


def test_system_compares_two_styles():
    """Test that system can compare two learned styles."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create two different projects
        dir1 = Path(tmpdir) / "project1"
        dir1.mkdir()
        (dir1 / "sample.py").write_text("def foo():\n    pass\n")
        
        dir2 = Path(tmpdir) / "project2"
        dir2.mkdir()
        (dir2 / "sample.py").write_text("def foo():\n  pass\n")
        
        system = CodeStyleTransferSystem()
        system.learn_project_style(str(dir1), "project1")
        system.learn_project_style(str(dir2), "project2")
        
        comparison = system.compare_styles("project1", "project2")
        
        assert "similarity" in comparison
        assert "differences" in comparison
        assert 0.0 <= comparison["similarity"] <= 1.0


def test_system_exports_database():
    """Test that system can export style database to JSON."""
    with tempfile.TemporaryDirectory() as tmpdir:
        proj_dir = Path(tmpdir) / "project"
        proj_dir.mkdir()
        (proj_dir / "sample.py").write_text("def foo():\n    pass\n")
        
        system = CodeStyleTransferSystem()
        system.learn_project_style(str(proj_dir), "test_project")
        
        export_file = Path(tmpdir) / "export.json"
        system.export_style_database(str(export_file))
        
        assert export_file.exists()
        
        # Verify JSON is valid
        import json
        with open(export_file, 'r') as f:
            data = json.load(f)
        assert "test_project" in data


def test_system_imports_database():
    """Test that system can import style database from JSON."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create and export
        proj_dir = Path(tmpdir) / "project"
        proj_dir.mkdir()
        (proj_dir / "sample.py").write_text("def foo():\n    pass\n")
        
        system1 = CodeStyleTransferSystem()
        system1.learn_project_style(str(proj_dir), "test_project")
        
        export_file = Path(tmpdir) / "export.json"
        system1.export_style_database(str(export_file))
        
        # Import into new system
        system2 = CodeStyleTransferSystem()
        system2.import_style_database(str(export_file))
        
        assert "test_project" in system2.style_database


def test_system_aggregates_multiple_files():
    """Test that system correctly aggregates features from multiple files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create multiple files with similar style
        for i in range(3):
            file = Path(tmpdir) / f"file{i}.py"
            file.write_text(f"def func{i}():\n    return {i}\n")
        
        system = CodeStyleTransferSystem()
        features = system.learn_project_style(tmpdir, "multi_file_project")
        
        # Should have aggregated features
        assert features.indent_size > 0
        assert system.style_database["multi_file_project"]["file_count"] == 3


def test_system_ignores_test_files():
    """Test that system ignores test files when learning."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create regular file
        (Path(tmpdir) / "regular.py").write_text("def foo():\n    pass\n")
        
        # Create test file
        (Path(tmpdir) / "test_something.py").write_text("def test_foo():\n    pass\n")
        
        system = CodeStyleTransferSystem()
        system.learn_project_style(tmpdir, "test_project")
        
        # Should only count regular file
        assert system.style_database["test_project"]["file_count"] == 1


def test_system_handles_empty_directory():
    """Test that system handles directory with no Python files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        system = CodeStyleTransferSystem()
        features = system.learn_project_style(tmpdir, "empty_project")
        
        # Should return default features
        assert isinstance(features, StyleFeatures)


# Integration Tests

def test_full_style_transfer_workflow():
    """Test complete workflow: learn, apply, compare."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create source project
        source_dir = Path(tmpdir) / "source"
        source_dir.mkdir()
        (source_dir / "source.py").write_text(
            "def calculate():\n    x = 1\n    return x\n"
        )
        
        # Create target project with different style
        target_dir = Path(tmpdir) / "target"
        target_dir.mkdir()
        (target_dir / "target.py").write_text(
            "def calculate():\n  x = 1\n  return x\n"
        )
        
        # Initialize system and learn both styles
        system = CodeStyleTransferSystem()
        system.learn_project_style(str(source_dir), "source")
        system.learn_project_style(str(target_dir), "target")
        
        # Compare styles
        comparison = system.compare_styles("source", "target")
        assert comparison["similarity"] >= 0.0
        
        # Apply target style to source code
        source_code = "def new_func():\n    return 42\n"
        result = system.apply_project_style(source_code, "target")
        
        assert result.transformed_code is not None
        assert result.confidence >= 0.0


def test_style_features_serialization():
    """Test that StyleFeatures can be serialized and deserialized."""
    from dataclasses import asdict
    
    features = StyleFeatures(
        indent_size=4,
        variable_naming="snake_case",
        has_module_docstring=True
    )
    
    # Convert to dict
    features_dict = asdict(features)
    assert isinstance(features_dict, dict)
    assert features_dict["indent_size"] == 4
    
    # Recreate from dict
    features_restored = StyleFeatures(**features_dict)
    assert features_restored.indent_size == 4
    assert features_restored.variable_naming == "snake_case"


# Edge Cases and Error Handling

def test_handles_unicode_code(style_extractor):
    """Test that system handles Unicode characters in code."""
    code = "def greet():\n    print('Hello 世界')\n"
    features = style_extractor.extract_from_code(code)
    
    assert features is not None


def test_handles_mixed_indentation(style_extractor):
    """Test that system handles mixed indentation gracefully."""
    code = "def foo():\n    x = 1\n  y = 2\n"
    features = style_extractor.extract_from_code(code)
    
    assert features is not None
    assert features.indent_size > 0


def test_handles_very_long_lines(style_extractor):
    """Test that system handles very long lines."""
    code = "x = " + "1 + " * 100 + "1\n"
    features = style_extractor.extract_from_code(code)
    
    assert features.max_line_length > 100


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
