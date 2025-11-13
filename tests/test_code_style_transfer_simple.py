#!/usr/bin/env python3
"""
Simple test runner for code-style-transfer.py
Tests basic functionality without pytest dependency.

Author: @engineer-master
"""

import sys
import os
import tempfile
from pathlib import Path

# Add tools directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'tools'))

# Import with dynamic loading
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


def test_style_extraction():
    """Test basic style extraction."""
    print("Testing style extraction...")
    
    code = '''
def calculate_sum(numbers):
    """Calculate sum of numbers."""
    total = 0
    for num in numbers:
        total += num
    return total
'''
    
    extractor = StyleExtractor()
    features = extractor.extract_from_code(code)
    
    assert features.code_lines > 0, "Should extract code lines"
    assert features.indent_size in [2, 4, 8], f"Indent size should be standard: {features.indent_size}"
    assert features.indent_type in ['spaces', 'tabs'], f"Indent type invalid: {features.indent_type}"
    
    print("  ✓ Style extraction works correctly")
    return True


def test_neural_encoding():
    """Test neural style encoding."""
    print("Testing neural encoding...")
    
    encoder = NeuralStyleEncoder()
    features = StyleFeatures(indent_size=4, variable_naming='snake_case')
    
    encoding = encoder.encode_style(features)
    
    assert isinstance(encoding, list), "Encoding should be a list"
    assert len(encoding) == encoder.hidden_dim, f"Encoding dimension mismatch: {len(encoding)}"
    assert all(isinstance(x, float) for x in encoding), "All encoding values should be floats"
    
    # Test consistency
    encoding2 = encoder.encode_style(features)
    assert encoding == encoding2, "Encoding should be consistent"
    
    # Test similarity
    similarity = encoder.similarity(encoding, encoding2)
    assert 0.9 <= similarity <= 1.0, f"Self-similarity should be ~1.0: {similarity}"
    
    print("  ✓ Neural encoding works correctly")
    return True


def test_style_transfer():
    """Test style transformation."""
    print("Testing style transfer...")
    
    source_code = "def foo():\n    pass\n"
    target_style = StyleFeatures(indent_size=2)
    
    transformer = StyleTransformer()
    result = transformer.transfer_style(source_code, target_style)
    
    assert result.original_code == source_code, "Original code should be preserved"
    assert result.transformed_code is not None, "Transformed code should exist"
    assert isinstance(result.style_changes, list), "Style changes should be a list"
    assert 0.0 <= result.confidence <= 1.0, f"Confidence out of range: {result.confidence}"
    
    print("  ✓ Style transfer works correctly")
    return True


def test_project_learning():
    """Test learning from project directory."""
    print("Testing project style learning...")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create sample project
        sample_file = Path(tmpdir) / "sample.py"
        sample_file.write_text("def calculate():\n    return 42\n")
        
        system = CodeStyleTransferSystem()
        features = system.learn_project_style(tmpdir, "test_project")
        
        assert isinstance(features, StyleFeatures), "Should return StyleFeatures"
        assert "test_project" in system.style_database, "Should store in database"
        assert system.style_database["test_project"]["file_count"] == 1, "Should count files"
        
        print("  ✓ Project learning works correctly")
        return True


def test_style_application():
    """Test applying learned style."""
    print("Testing style application...")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create and learn project style
        sample_file = Path(tmpdir) / "sample.py"
        sample_file.write_text("def calculate():\n    return 42\n")
        
        system = CodeStyleTransferSystem()
        system.learn_project_style(tmpdir, "test_project")
        
        # Apply style
        code = "def new_func():\n        return 1\n"
        result = system.apply_project_style(code, "test_project")
        
        assert result.transformed_code is not None, "Should produce transformed code"
        assert result.confidence >= 0.0, "Should have confidence score"
        
        print("  ✓ Style application works correctly")
        return True


def test_style_comparison():
    """Test comparing two styles."""
    print("Testing style comparison...")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create two projects
        dir1 = Path(tmpdir) / "proj1"
        dir1.mkdir()
        (dir1 / "file.py").write_text("def foo():\n    pass\n")
        
        dir2 = Path(tmpdir) / "proj2"
        dir2.mkdir()
        (dir2 / "file.py").write_text("def foo():\n  pass\n")
        
        system = CodeStyleTransferSystem()
        system.learn_project_style(str(dir1), "project1")
        system.learn_project_style(str(dir2), "project2")
        
        comparison = system.compare_styles("project1", "project2")
        
        assert "similarity" in comparison, "Should have similarity"
        assert "differences" in comparison, "Should have differences"
        assert 0.0 <= comparison["similarity"] <= 1.0, "Similarity in range"
        
        print("  ✓ Style comparison works correctly")
        return True


def test_database_export_import():
    """Test exporting and importing style database."""
    print("Testing database export/import...")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create project and learn
        proj_dir = Path(tmpdir) / "project"
        proj_dir.mkdir()
        (proj_dir / "file.py").write_text("def foo():\n    pass\n")
        
        system1 = CodeStyleTransferSystem()
        system1.learn_project_style(str(proj_dir), "test_project")
        
        # Export
        export_file = Path(tmpdir) / "export.json"
        system1.export_style_database(str(export_file))
        assert export_file.exists(), "Export file should exist"
        
        # Import
        system2 = CodeStyleTransferSystem()
        system2.import_style_database(str(export_file))
        assert "test_project" in system2.style_database, "Should import project"
        
        print("  ✓ Database export/import works correctly")
        return True


def test_edge_cases():
    """Test edge cases and error handling."""
    print("Testing edge cases...")
    
    extractor = StyleExtractor()
    
    # Empty code
    features = extractor.extract_from_code("")
    assert features is not None, "Should handle empty code"
    
    # Invalid syntax
    features = extractor.extract_from_code("def broken(")
    assert features is not None, "Should handle syntax errors"
    
    # Unicode
    features = extractor.extract_from_code("x = '你好'")
    assert features is not None, "Should handle Unicode"
    
    print("  ✓ Edge cases handled correctly")
    return True


def main():
    """Run all tests."""
    print("=" * 60)
    print("Code Style Transfer - Test Suite")
    print("=" * 60)
    print()
    
    tests = [
        test_style_extraction,
        test_neural_encoding,
        test_style_transfer,
        test_project_learning,
        test_style_application,
        test_style_comparison,
        test_database_export_import,
        test_edge_cases,
    ]
    
    passed = 0
    failed = 0
    
    for test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"  ✗ Test failed: {e}")
            failed += 1
        print()
    
    print("=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 60)
    
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
