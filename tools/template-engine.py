#!/usr/bin/env python3
"""
Template Engine - Automatically Generate Boilerplate from Examples

A performance-optimized template engine that learns from example code to generate
boilerplate automatically. Focuses on speed, efficiency, and pattern recognition.

Created by @accelerate-specialist - Elegant and efficient approach inspired by Edsger Dijkstra.
Part of the Chained autonomous AI ecosystem.
"""

import os
import re
import json
import hashlib
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass, asdict, field
from datetime import datetime, timezone
from collections import defaultdict, Counter


@dataclass
class Template:
    """Represents a code template extracted from examples"""
    template_id: str
    name: str
    category: str  # e.g., "function", "class", "workflow", "test"
    language: str  # e.g., "python", "javascript", "yaml"
    pattern: str  # The actual template with placeholders
    variables: List[str]  # List of variable names to be filled
    metadata: Dict[str, Any] = field(default_factory=dict)
    usage_count: int = 0
    success_rate: float = 1.0
    avg_generation_time_ms: float = 0.0
    source_file: str = ""
    extracted_at: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert template to dictionary"""
        return asdict(self)


@dataclass
class GeneratedCode:
    """Represents generated code from a template"""
    template_id: str
    code: str
    variables_used: Dict[str, str]
    generation_time_ms: float
    timestamp: str


class TemplateEngine:
    """
    High-performance template engine for automatic boilerplate generation.
    
    Features:
    - Fast pattern extraction from examples
    - Intelligent placeholder detection
    - Efficient template matching and generation
    - Performance tracking and optimization
    - Multi-language support
    """
    
    def __init__(self, 
                 examples_dir: str = "tools/examples",
                 cache_dir: str = "tools/data/templates",
                 enable_cache: bool = True):
        """
        Initialize the template engine.
        
        Args:
            examples_dir: Directory containing example code files
            cache_dir: Directory for template cache
            enable_cache: Whether to use caching for performance
        """
        self.examples_dir = Path(examples_dir)
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.enable_cache = enable_cache
        
        # Cache files
        self.templates_cache = self.cache_dir / "templates_cache.json"
        self.metrics_file = self.cache_dir / "generation_metrics.json"
        
        # In-memory storage
        self.templates: Dict[str, Template] = {}
        self.metrics: Dict[str, Any] = {
            'total_generations': 0,
            'avg_generation_time_ms': 0.0,
            'template_usage': defaultdict(int),
            'extraction_stats': {}
        }
        
        # Pattern detection rules
        self.pattern_rules = self._initialize_pattern_rules()
        
        # Load cached data
        if self.enable_cache:
            self._load_cache()
    
    def _initialize_pattern_rules(self) -> Dict[str, Dict[str, Any]]:
        """Initialize pattern detection rules for different code structures"""
        return {
            'python': {
                'function': r'def\s+(\w+)\s*\([^)]*\):\s*(?:"""[^"]*""")?\s*(.+?)(?=\ndef|\nclass|\Z)',
                'class': r'class\s+(\w+)(?:\([^)]*\))?:\s*(?:"""[^"]*""")?\s*(.+?)(?=\nclass|\Z)',
                'docstring': r'"""([^"]*)"""',
                'import': r'(?:from\s+[\w.]+\s+)?import\s+[\w.,\s]+',
            },
            'javascript': {
                'function': r'function\s+(\w+)\s*\([^)]*\)\s*\{([^}]+)\}',
                'arrow_function': r'const\s+(\w+)\s*=\s*\([^)]*\)\s*=>\s*\{([^}]+)\}',
                'class': r'class\s+(\w+)(?:\s+extends\s+\w+)?\s*\{([^}]+)\}',
            },
            'yaml': {
                'workflow': r'(name:\s*.+\non:\s*.+)',
                'job': r'(jobs:\s*\n(?:\s+\w+:\s*\n(?:\s+.+\n)+)+)',
            }
        }
    
    def extract_templates(self, force_refresh: bool = False) -> int:
        """
        Extract templates from example files.
        
        Args:
            force_refresh: Force re-extraction even if cached
            
        Returns:
            Number of templates extracted
        """
        if not force_refresh and self.enable_cache and self.templates:
            print(f"⚡ Using cached templates: {len(self.templates)} templates")
            return len(self.templates)
        
        print(f"🔍 Extracting templates from {self.examples_dir}...")
        start_time = datetime.now(timezone.utc)
        
        extracted_count = 0
        
        # Scan example files
        for file_path in self.examples_dir.rglob("*"):
            if file_path.is_file() and not file_path.name.startswith('.'):
                templates = self._extract_from_file(file_path)
                extracted_count += len(templates)
                
                for template in templates:
                    self.templates[template.template_id] = template
        
        extraction_time = (datetime.now(timezone.utc) - start_time).total_seconds()
        
        self.metrics['extraction_stats'] = {
            'last_extraction': datetime.now(timezone.utc).isoformat(),
            'extraction_time_seconds': extraction_time,
            'templates_extracted': extracted_count,
            'files_scanned': len(list(self.examples_dir.rglob("*")))
        }
        
        print(f"✅ Extracted {extracted_count} templates in {extraction_time:.2f}s")
        
        if self.enable_cache:
            self._save_cache()
        
        return extracted_count
    
    def _extract_from_file(self, file_path: Path) -> List[Template]:
        """Extract templates from a single file"""
        templates = []
        
        # Determine language
        language = self._detect_language(file_path)
        if not language:
            return templates
        
        try:
            content = file_path.read_text(encoding='utf-8')
        except Exception as e:
            print(f"⚠️  Failed to read {file_path}: {e}")
            return templates
        
        # Extract patterns based on language
        if language == 'python':
            templates.extend(self._extract_python_templates(content, file_path))
        elif language == 'javascript':
            templates.extend(self._extract_javascript_templates(content, file_path))
        elif language == 'yaml':
            templates.extend(self._extract_yaml_templates(content, file_path))
        
        return templates
    
    def _detect_language(self, file_path: Path) -> Optional[str]:
        """Detect programming language from file extension"""
        ext = file_path.suffix.lower()
        language_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.yaml': 'yaml',
            '.yml': 'yaml',
            '.sh': 'bash',
            '.md': 'markdown'
        }
        return language_map.get(ext)
    
    def _extract_python_templates(self, content: str, file_path: Path) -> List[Template]:
        """Extract Python-specific templates"""
        templates = []
        
        # Extract functions
        function_pattern = self.pattern_rules['python']['function']
        for match in re.finditer(function_pattern, content, re.DOTALL | re.MULTILINE):
            func_name = match.group(1)
            func_body = match.group(2)
            
            # Create template with placeholders
            template_pattern = self._create_template_pattern(func_name, func_body)
            variables = self._extract_variables(func_body)
            
            template = Template(
                template_id=self._generate_id(f"python_function_{func_name}"),
                name=func_name,
                category="function",
                language="python",
                pattern=template_pattern,
                variables=variables,
                source_file=str(file_path),
                extracted_at=datetime.now(timezone.utc).isoformat()
            )
            templates.append(template)
        
        # Extract classes
        class_pattern = self.pattern_rules['python']['class']
        for match in re.finditer(class_pattern, content, re.DOTALL | re.MULTILINE):
            class_name = match.group(1)
            class_body = match.group(2)
            
            template_pattern = self._create_template_pattern(class_name, class_body)
            variables = self._extract_variables(class_body)
            
            template = Template(
                template_id=self._generate_id(f"python_class_{class_name}"),
                name=class_name,
                category="class",
                language="python",
                pattern=template_pattern,
                variables=variables,
                source_file=str(file_path),
                extracted_at=datetime.now(timezone.utc).isoformat()
            )
            templates.append(template)
        
        return templates
    
    def _extract_javascript_templates(self, content: str, file_path: Path) -> List[Template]:
        """Extract JavaScript-specific templates"""
        templates = []
        
        # Extract functions
        function_pattern = self.pattern_rules['javascript']['function']
        for match in re.finditer(function_pattern, content):
            func_name = match.group(1)
            func_body = match.group(2)
            
            template_pattern = self._create_template_pattern(func_name, func_body)
            variables = self._extract_variables(func_body)
            
            template = Template(
                template_id=self._generate_id(f"js_function_{func_name}"),
                name=func_name,
                category="function",
                language="javascript",
                pattern=template_pattern,
                variables=variables,
                source_file=str(file_path),
                extracted_at=datetime.now(timezone.utc).isoformat()
            )
            templates.append(template)
        
        return templates
    
    def _extract_yaml_templates(self, content: str, file_path: Path) -> List[Template]:
        """Extract YAML-specific templates (e.g., GitHub Actions)"""
        templates = []
        
        # Extract workflow patterns
        if 'workflow' in str(file_path).lower() or 'action' in content.lower():
            # Simple YAML template for now
            template = Template(
                template_id=self._generate_id(f"yaml_workflow_{file_path.stem}"),
                name=file_path.stem,
                category="workflow",
                language="yaml",
                pattern=content,
                variables=self._extract_yaml_variables(content),
                source_file=str(file_path),
                extracted_at=datetime.now(timezone.utc).isoformat()
            )
            templates.append(template)
        
        return templates
    
    def _create_template_pattern(self, name: str, body: str) -> str:
        """Create a template pattern with placeholders"""
        # Replace specific values with placeholders
        pattern = body
        
        # Replace string literals with placeholders
        pattern = re.sub(r'"[^"]*"', '{{STRING}}', pattern)
        pattern = re.sub(r"'[^']*'", '{{STRING}}', pattern)
        
        # Replace numbers with placeholders
        pattern = re.sub(r'\b\d+\b', '{{NUMBER}}', pattern)
        
        # Keep variable names as-is for now
        return pattern
    
    def _extract_variables(self, code: str) -> List[str]:
        """Extract variable names from code"""
        variables = set()
        
        # Extract Python variable assignments
        var_pattern = r'\b([a-z_][a-z0-9_]*)\s*='
        variables.update(re.findall(var_pattern, code, re.IGNORECASE))
        
        return sorted(list(variables))
    
    def _extract_yaml_variables(self, content: str) -> List[str]:
        """Extract variables from YAML content"""
        # Find ${{ }} placeholders
        variables = re.findall(r'\$\{\{\s*([^}]+)\s*\}\}', content)
        return sorted(list(set(variables)))
    
    def _generate_id(self, seed: str) -> str:
        """Generate a unique template ID"""
        return hashlib.md5(seed.encode()).hexdigest()[:16]
    
    def generate_code(self, 
                     template_id: str, 
                     variables: Dict[str, str],
                     context: Optional[Dict[str, Any]] = None) -> Optional[GeneratedCode]:
        """
        Generate code from a template.
        
        Args:
            template_id: ID of the template to use
            variables: Dictionary of variable values
            context: Additional context for generation
            
        Returns:
            GeneratedCode object or None if template not found
        """
        start_time = datetime.now(timezone.utc)
        
        template = self.templates.get(template_id)
        if not template:
            print(f"⚠️  Template {template_id} not found")
            return None
        
        # Generate code by filling in placeholders
        code = template.pattern
        
        # Replace placeholders with values
        for var_name, var_value in variables.items():
            code = code.replace(f"{{{{{var_name}}}}}", var_value)
        
        generation_time = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
        
        # Update metrics
        self.metrics['total_generations'] += 1
        if template_id not in self.metrics['template_usage']:
            self.metrics['template_usage'][template_id] = 0
        self.metrics['template_usage'][template_id] += 1
        
        # Update template stats
        template.usage_count += 1
        
        # Update average generation time (running average)
        if template.avg_generation_time_ms == 0:
            template.avg_generation_time_ms = generation_time
        else:
            template.avg_generation_time_ms = (
                template.avg_generation_time_ms * 0.7 + generation_time * 0.3
            )
        
        generated = GeneratedCode(
            template_id=template_id,
            code=code,
            variables_used=variables,
            generation_time_ms=generation_time,
            timestamp=datetime.now(timezone.utc).isoformat()
        )
        
        print(f"⚡ Generated code in {generation_time:.2f}ms using template '{template.name}'")
        
        if self.enable_cache:
            self._save_metrics()
        
        return generated
    
    def find_templates(self, 
                      category: Optional[str] = None,
                      language: Optional[str] = None,
                      name_pattern: Optional[str] = None) -> List[Template]:
        """
        Find templates matching criteria.
        
        Args:
            category: Filter by category (e.g., 'function', 'class')
            language: Filter by language (e.g., 'python', 'javascript')
            name_pattern: Regex pattern to match template name
            
        Returns:
            List of matching templates
        """
        results = []
        
        for template in self.templates.values():
            # Apply filters
            if category and template.category != category:
                continue
            if language and template.language != language:
                continue
            if name_pattern and not re.search(name_pattern, template.name, re.IGNORECASE):
                continue
            
            results.append(template)
        
        # Sort by usage count (most used first)
        results.sort(key=lambda t: t.usage_count, reverse=True)
        
        return results
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get template engine statistics"""
        total_templates = len(self.templates)
        
        # Category breakdown
        categories = defaultdict(int)
        languages = defaultdict(int)
        
        for template in self.templates.values():
            categories[template.category] += 1
            languages[template.language] += 1
        
        # Most used templates
        most_used = sorted(
            self.templates.values(),
            key=lambda t: t.usage_count,
            reverse=True
        )[:5]
        
        stats = {
            'total_templates': total_templates,
            'total_generations': self.metrics['total_generations'],
            'categories': dict(categories),
            'languages': dict(languages),
            'most_used_templates': [
                {
                    'name': t.name,
                    'category': t.category,
                    'usage_count': t.usage_count,
                    'avg_generation_time_ms': t.avg_generation_time_ms
                }
                for t in most_used
            ],
            'extraction_stats': self.metrics.get('extraction_stats', {})
        }
        
        return stats
    
    def _load_cache(self):
        """Load templates from cache"""
        if not self.templates_cache.exists():
            return
        
        try:
            with open(self.templates_cache, 'r') as f:
                data = json.load(f)
            
            for template_data in data.get('templates', []):
                template = Template(**template_data)
                self.templates[template.template_id] = template
            
            self.metrics = data.get('metrics', self.metrics)
            
            print(f"📦 Loaded {len(self.templates)} templates from cache")
        except Exception as e:
            print(f"⚠️  Failed to load cache: {e}")
    
    def _save_cache(self):
        """Save templates to cache"""
        try:
            data = {
                'templates': [t.to_dict() for t in self.templates.values()],
                'metrics': self.metrics,
                'last_updated': datetime.now(timezone.utc).isoformat()
            }
            
            with open(self.templates_cache, 'w') as f:
                json.dump(data, f, indent=2)
            
            print(f"💾 Saved {len(self.templates)} templates to cache")
        except Exception as e:
            print(f"⚠️  Failed to save cache: {e}")
    
    def _save_metrics(self):
        """Save generation metrics"""
        try:
            with open(self.metrics_file, 'w') as f:
                json.dump(self.metrics, f, indent=2)
        except Exception as e:
            print(f"⚠️  Failed to save metrics: {e}")


def main():
    """Demo of template engine capabilities"""
    print("🚀 Template Engine - Boilerplate Generation from Examples")
    print("=" * 60)
    
    # Initialize engine
    engine = TemplateEngine()
    
    # Extract templates
    count = engine.extract_templates()
    print(f"\n📊 Extracted {count} templates")
    
    # Show statistics
    stats = engine.get_statistics()
    print(f"\n📈 Statistics:")
    print(f"  Total templates: {stats['total_templates']}")
    print(f"  Categories: {', '.join(stats['categories'].keys())}")
    print(f"  Languages: {', '.join(stats['languages'].keys())}")
    
    # Find Python function templates
    print(f"\n🔍 Finding Python function templates...")
    templates = engine.find_templates(category="function", language="python")
    print(f"  Found {len(templates)} templates")
    
    if templates:
        print(f"\n📝 Sample templates:")
        for i, template in enumerate(templates[:3], 1):
            print(f"  {i}. {template.name} (from {Path(template.source_file).name})")
    
    print(f"\n✅ Template engine ready for use!")


if __name__ == "__main__":
    main()
