#!/usr/bin/env python3
"""
Tests for Template Engine

Comprehensive test suite for the template engine that generates boilerplate from examples.

Created by @accelerate-specialist - Testing with efficiency and elegance.
"""

import unittest
import tempfile
import shutil
import json
from pathlib import Path
import sys

# Add tools directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'tools'))

# Import using exec to handle hyphenated names
import importlib.util

def load_module(file_path, module_name):
    """Load a Python module from a file path"""
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

tools_dir = Path(__file__).parent.parent / 'tools'
template_module = load_module(tools_dir / 'template-engine.py', 'template_engine')

Template = template_module.Template
TemplateEngine = template_module.TemplateEngine
GeneratedCode = template_module.GeneratedCode


class TestTemplate(unittest.TestCase):
    """Test suite for Template dataclass"""
    
    def test_template_creation(self):
        """Test that templates can be created"""
        template = Template(
            template_id="test123",
            name="test_function",
            category="function",
            language="python",
            pattern="def {{NAME}}():\n    pass",
            variables=["NAME"],
            source_file="test.py"
        )
        
        self.assertEqual(template.template_id, "test123")
        self.assertEqual(template.name, "test_function")
        self.assertEqual(template.category, "function")
        self.assertEqual(template.language, "python")
        self.assertIn("NAME", template.variables)
    
    def test_template_to_dict(self):
        """Test template conversion to dictionary"""
        template = Template(
            template_id="test123",
            name="test_function",
            category="function",
            language="python",
            pattern="def test():\n    pass",
            variables=[],
            source_file="test.py"
        )
        
        template_dict = template.to_dict()
        self.assertIsInstance(template_dict, dict)
        self.assertEqual(template_dict['template_id'], "test123")
        self.assertEqual(template_dict['name'], "test_function")


class TestTemplateEngine(unittest.TestCase):
    """Test suite for TemplateEngine"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_dir = tempfile.mkdtemp()
        self.examples_dir = Path(self.test_dir) / 'examples'
        self.cache_dir = Path(self.test_dir) / 'cache'
        
        self.examples_dir.mkdir(parents=True)
        self.cache_dir.mkdir(parents=True)
        
        # Create sample example files
        self._create_sample_examples()
        
        # Initialize engine with test directories
        self.engine = TemplateEngine(
            examples_dir=str(self.examples_dir),
            cache_dir=str(self.cache_dir),
            enable_cache=False  # Disable cache for tests
        )
    
    def tearDown(self):
        """Clean up test fixtures"""
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def _create_sample_examples(self):
        """Create sample example files for testing"""
        # Python example with functions
        python_code = '''
def hello_world(name):
    """Say hello to someone"""
    print(f"Hello, {name}!")
    return True

def calculate_sum(a, b):
    """Calculate sum of two numbers"""
    result = a + b
    return result

class Calculator:
    """Simple calculator class"""
    def __init__(self):
        self.value = 0
    
    def add(self, x):
        self.value += x
        return self.value
'''
        (self.examples_dir / 'sample.py').write_text(python_code)
        
        # JavaScript example
        js_code = '''
function greet(name) {
    console.log("Hello, " + name);
    return true;
}

const multiply = (a, b) => {
    return a * b;
}

class Counter {
    constructor() {
        this.count = 0;
    }
}
'''
        (self.examples_dir / 'sample.js').write_text(js_code)
    
    def test_engine_initialization(self):
        """Test that engine initializes correctly"""
        self.assertIsInstance(self.engine, TemplateEngine)
        self.assertEqual(self.engine.examples_dir, self.examples_dir)
        self.assertEqual(self.engine.cache_dir, self.cache_dir)
        self.assertIsInstance(self.engine.templates, dict)
    
    def test_template_extraction(self):
        """Test template extraction from examples"""
        count = self.engine.extract_templates()
        
        self.assertGreater(count, 0, "Should extract at least one template")
        self.assertGreater(len(self.engine.templates), 0, "Templates dict should not be empty")
    
    def test_python_template_extraction(self):
        """Test extraction of Python templates"""
        self.engine.extract_templates()
        
        # Find Python function templates
        python_templates = [
            t for t in self.engine.templates.values()
            if t.language == 'python' and t.category == 'function'
        ]
        
        self.assertGreater(len(python_templates), 0, "Should find Python function templates")
        
        # Check that template has expected attributes
        template = python_templates[0]
        self.assertIsNotNone(template.pattern)
        self.assertIsNotNone(template.name)
    
    def test_javascript_template_extraction(self):
        """Test extraction of JavaScript templates"""
        self.engine.extract_templates()
        
        # Find JavaScript templates
        js_templates = [
            t for t in self.engine.templates.values()
            if t.language == 'javascript'
        ]
        
        self.assertGreater(len(js_templates), 0, "Should find JavaScript templates")
    
    def test_class_template_extraction(self):
        """Test extraction of class templates"""
        self.engine.extract_templates()
        
        # Find class templates
        class_templates = [
            t for t in self.engine.templates.values()
            if t.category == 'class'
        ]
        
        self.assertGreater(len(class_templates), 0, "Should find class templates")
    
    def test_find_templates_by_category(self):
        """Test finding templates by category"""
        self.engine.extract_templates()
        
        function_templates = self.engine.find_templates(category='function')
        self.assertIsInstance(function_templates, list)
        
        # All results should be functions
        for template in function_templates:
            self.assertEqual(template.category, 'function')
    
    def test_find_templates_by_language(self):
        """Test finding templates by language"""
        self.engine.extract_templates()
        
        python_templates = self.engine.find_templates(language='python')
        self.assertIsInstance(python_templates, list)
        
        # All results should be Python
        for template in python_templates:
            self.assertEqual(template.language, 'python')
    
    def test_find_templates_by_name_pattern(self):
        """Test finding templates by name pattern"""
        self.engine.extract_templates()
        
        # Find templates with 'hello' or 'greet' in name
        templates = self.engine.find_templates(name_pattern='hello|greet')
        self.assertIsInstance(templates, list)
        
        # Check that results match pattern
        for template in templates:
            self.assertTrue(
                'hello' in template.name.lower() or 'greet' in template.name.lower(),
                f"Template name '{template.name}' should match pattern"
            )
    
    def test_find_templates_multiple_filters(self):
        """Test finding templates with multiple filters"""
        self.engine.extract_templates()
        
        # Find Python functions
        templates = self.engine.find_templates(
            category='function',
            language='python'
        )
        
        self.assertIsInstance(templates, list)
        for template in templates:
            self.assertEqual(template.category, 'function')
            self.assertEqual(template.language, 'python')
    
    def test_code_generation(self):
        """Test code generation from template"""
        self.engine.extract_templates()
        
        # Get a template
        templates = list(self.engine.templates.values())
        if not templates:
            self.skipTest("No templates available")
        
        template = templates[0]
        
        # Generate code with dummy variables
        variables = {var: f"test_{var}" for var in template.variables}
        generated = self.engine.generate_code(template.template_id, variables)
        
        self.assertIsNotNone(generated)
        self.assertIsInstance(generated, GeneratedCode)
        self.assertIsNotNone(generated.code)
        self.assertGreater(generated.generation_time_ms, 0)
    
    def test_generation_metrics_update(self):
        """Test that generation updates metrics"""
        self.engine.extract_templates()
        
        templates = list(self.engine.templates.values())
        if not templates:
            self.skipTest("No templates available")
        
        template = templates[0]
        initial_usage = template.usage_count
        initial_total = self.engine.metrics['total_generations']
        
        # Generate code
        variables = {var: f"test_{var}" for var in template.variables}
        self.engine.generate_code(template.template_id, variables)
        
        # Check metrics updated
        self.assertEqual(template.usage_count, initial_usage + 1)
        self.assertEqual(
            self.engine.metrics['total_generations'],
            initial_total + 1
        )
    
    def test_statistics(self):
        """Test statistics generation"""
        self.engine.extract_templates()
        
        stats = self.engine.get_statistics()
        
        self.assertIsInstance(stats, dict)
        self.assertIn('total_templates', stats)
        self.assertIn('categories', stats)
        self.assertIn('languages', stats)
        self.assertIn('most_used_templates', stats)
        
        self.assertEqual(stats['total_templates'], len(self.engine.templates))
    
    def test_cache_save_and_load(self):
        """Test cache saving and loading"""
        # Create engine with cache enabled
        engine_with_cache = TemplateEngine(
            examples_dir=str(self.examples_dir),
            cache_dir=str(self.cache_dir),
            enable_cache=True
        )
        
        # Extract templates
        engine_with_cache.extract_templates()
        original_count = len(engine_with_cache.templates)
        
        # Save cache
        engine_with_cache._save_cache()
        
        # Create new engine and load cache
        engine2 = TemplateEngine(
            examples_dir=str(self.examples_dir),
            cache_dir=str(self.cache_dir),
            enable_cache=True
        )
        
        # Should load from cache
        self.assertEqual(len(engine2.templates), original_count)
    
    def test_template_id_generation(self):
        """Test template ID generation is consistent"""
        id1 = self.engine._generate_id("test_seed")
        id2 = self.engine._generate_id("test_seed")
        
        self.assertEqual(id1, id2, "Same seed should produce same ID")
        
        id3 = self.engine._generate_id("different_seed")
        self.assertNotEqual(id1, id3, "Different seeds should produce different IDs")
    
    def test_variable_extraction(self):
        """Test variable extraction from code"""
        code = """
        x = 10
        result = calculate(x)
        final_value = result + 5
        """
        
        variables = self.engine._extract_variables(code)
        
        self.assertIsInstance(variables, list)
        self.assertIn('x', variables)
        self.assertIn('result', variables)
        self.assertIn('final_value', variables)
    
    def test_language_detection(self):
        """Test language detection from file path"""
        test_cases = [
            (Path('test.py'), 'python'),
            (Path('test.js'), 'javascript'),
            (Path('test.yaml'), 'yaml'),
            (Path('test.yml'), 'yaml'),
            (Path('test.sh'), 'bash'),
            (Path('test.txt'), None),
        ]
        
        for file_path, expected_lang in test_cases:
            detected = self.engine._detect_language(file_path)
            self.assertEqual(
                detected, expected_lang,
                f"File {file_path} should be detected as {expected_lang}"
            )
    
    def test_force_refresh_extraction(self):
        """Test force refresh of template extraction"""
        # Extract once
        count1 = self.engine.extract_templates()
        
        # Extract again without force (should use cache)
        count2 = self.engine.extract_templates(force_refresh=False)
        
        # Extract with force refresh
        count3 = self.engine.extract_templates(force_refresh=True)
        
        self.assertEqual(count1, count3)
    
    def test_invalid_template_generation(self):
        """Test generation with invalid template ID"""
        result = self.engine.generate_code('invalid_id', {})
        
        self.assertIsNone(result, "Should return None for invalid template ID")
    
    def test_pattern_rules_initialization(self):
        """Test pattern rules are properly initialized"""
        rules = self.engine.pattern_rules
        
        self.assertIn('python', rules)
        self.assertIn('javascript', rules)
        self.assertIn('yaml', rules)
        
        self.assertIn('function', rules['python'])
        self.assertIn('class', rules['python'])


class TestTemplateEnginePerformance(unittest.TestCase):
    """Performance tests for template engine"""
    
    def setUp(self):
        """Set up performance test fixtures"""
        self.test_dir = tempfile.mkdtemp()
        self.examples_dir = Path(self.test_dir) / 'examples'
        self.cache_dir = Path(self.test_dir) / 'cache'
        
        self.examples_dir.mkdir(parents=True)
        
        # Create multiple example files
        for i in range(10):
            code = f'''
def function_{i}(x):
    """Function {i}"""
    return x * {i}

class Class{i}:
    """Class {i}"""
    def __init__(self):
        self.value = {i}
'''
            (self.examples_dir / f'example_{i}.py').write_text(code)
        
        self.engine = TemplateEngine(
            examples_dir=str(self.examples_dir),
            cache_dir=str(self.cache_dir),
            enable_cache=True
        )
    
    def tearDown(self):
        """Clean up test fixtures"""
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_extraction_performance(self):
        """Test that extraction is reasonably fast"""
        import time
        
        start = time.time()
        self.engine.extract_templates()
        elapsed = time.time() - start
        
        # Should complete in less than 1 second for 10 files
        self.assertLess(elapsed, 1.0, "Extraction should be fast")
    
    def test_generation_performance(self):
        """Test that code generation is fast"""
        import time
        
        self.engine.extract_templates()
        templates = list(self.engine.templates.values())
        
        if not templates:
            self.skipTest("No templates available")
        
        template = templates[0]
        variables = {var: f"test_{var}" for var in template.variables}
        
        # Generate code 10 times
        times = []
        for _ in range(10):
            start = time.time()
            self.engine.generate_code(template.template_id, variables)
            elapsed = time.time() - start
            times.append(elapsed)
        
        avg_time = sum(times) / len(times)
        
        # Should average less than 10ms per generation
        self.assertLess(avg_time, 0.01, "Generation should be very fast")
    
    def test_cache_performance(self):
        """Test that caching improves performance"""
        import time
        
        # First extraction (no cache)
        start = time.time()
        count1 = self.engine.extract_templates(force_refresh=True)
        time_no_cache = time.time() - start
        template_count = len(self.engine.templates)
        
        # Second extraction (with cache)
        start = time.time()
        count2 = self.engine.extract_templates(force_refresh=False)
        time_with_cache = time.time() - start
        
        # Cached version should have same number of unique templates
        self.assertEqual(len(self.engine.templates), template_count)


def run_tests():
    """Run all tests"""
    unittest.main(argv=[''], verbosity=2, exit=False)


if __name__ == '__main__':
    run_tests()
