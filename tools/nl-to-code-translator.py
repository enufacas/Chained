#!/usr/bin/env python3
"""
Natural Language to Code Translator for Issues
Part of the Chained autonomous AI ecosystem

This tool analyzes issue descriptions written in natural language and generates
actionable code templates, implementation plans, and scaffolding.

Features:
- Intent classification (create, modify, analyze, test)
- Entity extraction (files, functions, classes, features)
- Code template generation
- Integration with repository patterns
- Validation against existing code style

Author: @investigate-champion
"""

import re
import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum


class CodeIntent(Enum):
    """Types of code intents that can be extracted from issues."""
    CREATE = "create"
    MODIFY = "modify"
    ANALYZE = "analyze"
    TEST = "test"
    DOCUMENT = "document"
    REFACTOR = "refactor"
    FIX = "fix"
    OPTIMIZE = "optimize"


@dataclass
class Entity:
    """Represents an entity extracted from natural language."""
    type: str  # file, function, class, feature, tool, workflow
    name: str
    context: str = ""
    confidence: float = 1.0


@dataclass
class TranslationResult:
    """Result of translating natural language to code."""
    intent: CodeIntent
    entities: List[Entity]
    code_template: str
    implementation_plan: List[str]
    file_suggestions: List[str]
    confidence: float
    metadata: Dict[str, Any]


class NLToCodeTranslator:
    """Translates natural language issue descriptions to code."""
    
    def __init__(self, repo_path: str = "."):
        self.repo_path = Path(repo_path)
        self._load_repository_patterns()
    
    def _load_repository_patterns(self):
        """Load patterns from repository structure."""
        self.patterns = {
            'tools': [],
            'workflows': [],
            'agents': [],
            'tests': []
        }
        
        # Scan tools directory
        tools_dir = self.repo_path / "tools"
        if tools_dir.exists():
            self.patterns['tools'] = [f.stem for f in tools_dir.glob("*.py")]
        
        # Scan workflows directory
        workflows_dir = self.repo_path / ".github" / "workflows"
        if workflows_dir.exists():
            self.patterns['workflows'] = [f.stem for f in workflows_dir.glob("*.yml")]
        
        # Scan agents directory
        agents_dir = self.repo_path / ".github" / "agents"
        if agents_dir.exists():
            self.patterns['agents'] = [f.stem for f in agents_dir.glob("*.md") if f.stem != "README"]
    
    def classify_intent(self, text: str) -> Tuple[CodeIntent, float]:
        """Classify the primary intent of the text.
        
        Args:
            text: Natural language description
            
        Returns:
            Tuple of (intent, confidence_score)
        """
        text_lower = text.lower()
        
        # Intent patterns with confidence weights
        intent_patterns = {
            CodeIntent.CREATE: [
                (r'\b(create|build|develop|implement|add|generate)\b', 1.0),
                (r'\bnew\b.*\b(tool|feature|function|class|workflow)\b', 0.9),
                (r'\bfrom scratch\b', 1.0)
            ],
            CodeIntent.MODIFY: [
                (r'\b(modify|change|update|edit|alter|enhance)\b', 1.0),
                (r'\b(extend|improve)\b', 0.8),
                (r'\bsupport\b', 0.7)
            ],
            CodeIntent.ANALYZE: [
                (r'\b(analyze|investigate|examine|explore|study)\b', 1.0),
                (r'\b(understand|review|assess)\b', 0.8),
                (r'\bcode patterns?\b', 0.9)
            ],
            CodeIntent.TEST: [
                (r'\b(test|validate|verify|testing)\b', 1.0),
                (r'\b(coverage|test case|unit test)\b', 0.9),
                (r'\bwrite.*tests?\b', 0.95)
            ],
            CodeIntent.DOCUMENT: [
                (r'\b(document|describe|explain|write docs?|documentation)\b', 1.0),
                (r'\breadme\b', 0.9),
                (r'\bapi\b.*\bdocument', 0.95)
            ],
            CodeIntent.REFACTOR: [
                (r'\b(refactor|reorganize|restructure|clean up)\b', 1.0),
                (r'\b(duplication|simplify)\b', 0.8)
            ],
            CodeIntent.FIX: [
                (r'\b(fix|repair|resolve|solve|debug)\b', 1.0),
                (r'\b(bug|issue|problem|error)\b', 0.8)
            ],
            CodeIntent.OPTIMIZE: [
                (r'\b(optimize|performance|faster|improve speed|speedup)\b', 1.0),
                (r'\b(efficiency|bottleneck|slow)\b', 0.8)
            ]
        }
        
        # Calculate scores for each intent
        scores = {}
        for intent, patterns in intent_patterns.items():
            score = 0.0
            matches = 0
            for pattern, weight in patterns:
                if re.search(pattern, text_lower):
                    score += weight
                    matches += 1
            if matches > 0:
                scores[intent] = score / len(patterns)  # Normalize
        
        if not scores:
            return CodeIntent.CREATE, 0.5  # Default with low confidence
        
        # Return intent with highest score
        best_intent = max(scores.items(), key=lambda x: x[1])
        return best_intent[0], min(best_intent[1], 1.0)
    
    def extract_entities(self, text: str) -> List[Entity]:
        """Extract entities (files, functions, classes, etc.) from text.
        
        Args:
            text: Natural language description
            
        Returns:
            List of extracted entities
        """
        entities = []
        
        # Extract file references
        file_patterns = [
            r'(?:file|script|module)?\s*[`"]([a-zA-Z0-9_\-/]+\.(?:py|yml|yaml|md|json|txt))[`"]',
            r'(?:in|for)\s+([a-zA-Z0-9_\-]+\.(?:py|yml|yaml|md))',
        ]
        for pattern in file_patterns:
            for match in re.finditer(pattern, text):
                entities.append(Entity(
                    type="file",
                    name=match.group(1),
                    context=match.group(0),
                    confidence=0.9
                ))
        
        # Extract function/method names
        function_patterns = [
            r'function\s+[`"]?([a-zA-Z_][a-zA-Z0-9_]*)[`"]?',
            r'method\s+[`"]?([a-zA-Z_][a-zA-Z0-9_]*)[`"]?',
            r'(?:call|calls|calling)\s+[`"]?([a-zA-Z_][a-zA-Z0-9_]*)\(\)',
        ]
        for pattern in function_patterns:
            for match in re.finditer(pattern, text):
                entities.append(Entity(
                    type="function",
                    name=match.group(1),
                    context=match.group(0),
                    confidence=0.8
                ))
        
        # Extract class names
        class_patterns = [
            r'class\s+[`"]?([A-Z][a-zA-Z0-9_]*)[`"]?',
            r'(?:create|implement)\s+(?:a|an)\s+([A-Z][a-zA-Z0-9_]*)\s+class',
        ]
        for pattern in class_patterns:
            for match in re.finditer(pattern, text):
                entities.append(Entity(
                    type="class",
                    name=match.group(1),
                    context=match.group(0),
                    confidence=0.85
                ))
        
        # Extract feature names
        feature_patterns = [
            r'(?:feature|capability|functionality)[:"]?\s+([a-zA-Z][a-zA-Z0-9\s\-]+)',
            r'(?:implement|create|build)\s+(?:a|an)?\s*([a-z][a-z0-9\s\-]{5,30})',
        ]
        for pattern in feature_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                feature_name = match.group(1).strip()
                if len(feature_name.split()) <= 6:  # Reasonable feature name length
                    entities.append(Entity(
                        type="feature",
                        name=feature_name,
                        context=match.group(0),
                        confidence=0.7
                    ))
        
        # Extract tool/workflow references
        for tool in self.patterns['tools']:
            if tool.lower() in text.lower():
                entities.append(Entity(
                    type="tool",
                    name=tool,
                    context="existing tool",
                    confidence=0.95
                ))
        
        for workflow in self.patterns['workflows']:
            if workflow.lower() in text.lower():
                entities.append(Entity(
                    type="workflow",
                    name=workflow,
                    context="existing workflow",
                    confidence=0.95
                ))
        
        # Deduplicate entities
        unique_entities = []
        seen = set()
        for entity in entities:
            key = (entity.type, entity.name.lower())
            if key not in seen:
                seen.add(key)
                unique_entities.append(entity)
        
        return unique_entities
    
    def generate_code_template(self, intent: CodeIntent, entities: List[Entity]) -> str:
        """Generate code template based on intent and entities.
        
        Args:
            intent: The classified intent
            entities: Extracted entities
            
        Returns:
            Code template as a string
        """
        templates = {
            CodeIntent.CREATE: self._template_create,
            CodeIntent.MODIFY: self._template_modify,
            CodeIntent.ANALYZE: self._template_analyze,
            CodeIntent.TEST: self._template_test,
            CodeIntent.DOCUMENT: self._template_document,
            CodeIntent.REFACTOR: self._template_refactor,
            CodeIntent.FIX: self._template_fix,
            CodeIntent.OPTIMIZE: self._template_optimize,
        }
        
        generator = templates.get(intent, self._template_create)
        return generator(entities)
    
    def _template_create(self, entities: List[Entity]) -> str:
        """Generate template for CREATE intent."""
        # Check if we're creating a tool, workflow, or class
        has_tool = any(e.type in ['tool', 'file'] and '.py' in e.name for e in entities)
        has_class = any(e.type == 'class' for e in entities)
        has_workflow = any(e.type in ['workflow', 'file'] and '.yml' in e.name for e in entities)
        
        if has_workflow:
            return self._template_workflow(entities)
        elif has_class:
            return self._template_class(entities)
        elif has_tool:
            return self._template_tool(entities)
        else:
            return self._template_generic_create(entities)
    
    def _template_tool(self, entities: List[Entity]) -> str:
        """Template for creating a Python tool."""
        class_entities = [e for e in entities if e.type == 'class']
        function_entities = [e for e in entities if e.type == 'function']
        
        class_name = class_entities[0].name if class_entities else "NewTool"
        
        template = f'''#!/usr/bin/env python3
"""
{class_name} - Auto-generated by NL-to-Code Translator
Part of the Chained autonomous AI ecosystem
"""

import sys
from pathlib import Path
from typing import List, Dict, Optional


class {class_name}:
    """Main class for {class_name} functionality."""
    
    def __init__(self):
        """Initialize the {class_name}."""
        pass
    
'''
        
        # Add methods for each function entity
        for func in function_entities:
            template += f'''    def {func.name}(self):
        """TODO: Implement {func.name}."""
        pass
    
'''
        
        template += '''

def main():
    """Main entry point."""
    tool = {class_name}()
    # TODO: Implement main logic
    pass


if __name__ == "__main__":
    main()
'''
        return template.replace('{class_name}', class_name)
    
    def _template_class(self, entities: List[Entity]) -> str:
        """Template for creating a class."""
        class_entity = next((e for e in entities if e.type == 'class'), None)
        class_name = class_entity.name if class_entity else "NewClass"
        
        return f'''class {class_name}:
    """TODO: Document {class_name} purpose."""
    
    def __init__(self):
        """Initialize {class_name}."""
        pass
    
    def process(self):
        """TODO: Implement main processing logic."""
        pass
'''
    
    def _template_workflow(self, entities: List[Entity]) -> str:
        """Template for creating a GitHub Actions workflow."""
        workflow_entity = next((e for e in entities if e.type in ['workflow', 'file']), None)
        name = workflow_entity.name if workflow_entity else "new-workflow"
        
        return f'''name: "{name.replace('-', ' ').title()}"

on:
  workflow_dispatch:
  schedule:
    - cron: '0 0 * * *'

permissions:
  contents: read
  issues: write

jobs:
  run:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
      
      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.x'
      
      - name: Run workflow logic
        run: |
          echo "TODO: Implement workflow logic"
'''
    
    def _template_generic_create(self, entities: List[Entity]) -> str:
        """Generic creation template."""
        return '''# TODO: Implement new functionality
# Based on extracted requirements:
''' + '\n'.join(f'# - {e.type}: {e.name}' for e in entities)
    
    def _template_modify(self, entities: List[Entity]) -> str:
        """Template for MODIFY intent."""
        files = [e for e in entities if e.type == 'file']
        if files:
            return f'''# Modification plan for {files[0].name}:
# 1. Load existing file
# 2. Identify modification points
# 3. Apply changes carefully
# 4. Validate changes
# 5. Test modifications
'''
        return "# TODO: Modify existing code\n# Target: " + ', '.join(e.name for e in entities)
    
    def _template_analyze(self, entities: List[Entity]) -> str:
        """Template for ANALYZE intent."""
        return f'''# Analysis Template
# Targets: {', '.join(e.name for e in entities) if entities else 'TBD'}
# 
# Analysis steps:
# 1. Collect relevant data/code
# 2. Identify patterns and metrics
# 3. Document findings
# 4. Provide recommendations
'''
    
    def _template_test(self, entities: List[Entity]) -> str:
        """Template for TEST intent."""
        target = entities[0].name if entities else "module"
        return f'''#!/usr/bin/env python3
"""Tests for {target}"""

import unittest
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


class Test{target.replace('-', '_').replace('.', '_').title()}(unittest.TestCase):
    """Test cases for {target}."""
    
    def setUp(self):
        """Set up test fixtures."""
        pass
    
    def test_basic_functionality(self):
        """Test basic functionality."""
        # TODO: Implement test
        pass
    
    def test_edge_cases(self):
        """Test edge cases."""
        # TODO: Implement test
        pass


if __name__ == '__main__':
    unittest.main()
'''
    
    def _template_document(self, entities: List[Entity]) -> str:
        """Template for DOCUMENT intent."""
        target = entities[0].name if entities else "Component"
        return f'''# {target} Documentation

## Overview

TODO: Provide overview of {target}

## Usage

TODO: Describe how to use {target}

## Examples

TODO: Provide examples

## API Reference

TODO: Document API if applicable
'''
    
    def _template_refactor(self, entities: List[Entity]) -> str:
        """Template for REFACTOR intent."""
        return f'''# Refactoring Plan
# Targets: {', '.join(e.name for e in entities) if entities else 'TBD'}
#
# Steps:
# 1. Identify code smells
# 2. Extract common patterns
# 3. Simplify complex logic
# 4. Remove duplication
# 5. Improve naming
# 6. Add tests if missing
# 7. Verify behavior unchanged
'''
    
    def _template_fix(self, entities: List[Entity]) -> str:
        """Template for FIX intent."""
        return f'''# Bug Fix Plan
# Affected: {', '.join(e.name for e in entities) if entities else 'TBD'}
#
# Steps:
# 1. Reproduce the issue
# 2. Identify root cause
# 3. Implement fix
# 4. Add regression test
# 5. Verify fix works
# 6. Check for similar issues
'''
    
    def _template_optimize(self, entities: List[Entity]) -> str:
        """Template for OPTIMIZE intent."""
        return f'''# Optimization Plan
# Targets: {', '.join(e.name for e in entities) if entities else 'TBD'}
#
# Steps:
# 1. Profile current performance
# 2. Identify bottlenecks
# 3. Apply optimizations:
#    - Algorithm improvements
#    - Caching strategies
#    - Resource reduction
# 4. Benchmark improvements
# 5. Validate correctness maintained
'''
    
    def generate_implementation_plan(self, intent: CodeIntent, entities: List[Entity]) -> List[str]:
        """Generate step-by-step implementation plan.
        
        Args:
            intent: The classified intent
            entities: Extracted entities
            
        Returns:
            List of implementation steps
        """
        plans = {
            CodeIntent.CREATE: [
                "Create new file(s) based on template",
                "Implement core functionality",
                "Add error handling",
                "Write tests",
                "Document the code",
                "Integrate with existing system"
            ],
            CodeIntent.MODIFY: [
                "Review existing code",
                "Identify modification points",
                "Make minimal changes",
                "Update tests",
                "Verify behavior"
            ],
            CodeIntent.ANALYZE: [
                "Collect relevant code/data",
                "Analyze patterns and metrics",
                "Document findings",
                "Provide recommendations"
            ],
            CodeIntent.TEST: [
                "Identify test cases",
                "Write unit tests",
                "Add integration tests",
                "Achieve target coverage",
                "Document test strategy"
            ],
            CodeIntent.DOCUMENT: [
                "Review code/feature",
                "Write clear documentation",
                "Add usage examples",
                "Update README if needed"
            ],
            CodeIntent.REFACTOR: [
                "Identify refactoring opportunities",
                "Plan minimal changes",
                "Refactor incrementally",
                "Verify tests pass",
                "Document improvements"
            ],
            CodeIntent.FIX: [
                "Reproduce the issue",
                "Identify root cause",
                "Implement minimal fix",
                "Add regression test",
                "Verify fix works"
            ],
            CodeIntent.OPTIMIZE: [
                "Profile current performance",
                "Identify bottlenecks",
                "Implement optimizations",
                "Benchmark improvements",
                "Validate correctness"
            ]
        }
        
        base_plan = plans.get(intent, plans[CodeIntent.CREATE])
        
        # Customize plan based on entities
        customized_plan = []
        for step in base_plan:
            if entities:
                entity_names = ', '.join(e.name for e in entities[:3])
                step = step.replace("file(s)", entity_names)
                step = step.replace("code", f"{entity_names}")
            customized_plan.append(step)
        
        return customized_plan
    
    def suggest_files(self, intent: CodeIntent, entities: List[Entity]) -> List[str]:
        """Suggest file paths based on intent and entities.
        
        Args:
            intent: The classified intent
            entities: Extracted entities
            
        Returns:
            List of suggested file paths
        """
        suggestions = []
        
        # Extract existing file references
        for entity in entities:
            if entity.type == 'file':
                suggestions.append(entity.name)
        
        # Suggest new files based on intent and features
        features = [e for e in entities if e.type == 'feature']
        classes = [e for e in entities if e.type == 'class']
        
        if intent == CodeIntent.CREATE:
            if classes:
                # Suggest tool file
                for cls in classes:
                    filename = cls.name.lower().replace('_', '-')
                    suggestions.append(f"tools/{filename}.py")
            elif features:
                # Suggest based on feature name
                for feature in features:
                    filename = feature.name.lower().replace(' ', '-')
                    suggestions.append(f"tools/{filename}.py")
        
        if intent == CodeIntent.TEST:
            # Suggest test file
            if entities:
                target = entities[0].name.replace('.py', '').replace('-', '_')
                suggestions.append(f"tests/test_{target}.py")
        
        if intent == CodeIntent.DOCUMENT:
            # Suggest documentation file
            if entities:
                target = entities[0].name.replace('.py', '').upper()
                suggestions.append(f"docs/{target}.md")
        
        return suggestions
    
    def translate(self, issue_text: str) -> TranslationResult:
        """Translate natural language issue to code.
        
        Args:
            issue_text: The issue description text
            
        Returns:
            TranslationResult with all extracted information
        """
        # Classify intent
        intent, intent_confidence = self.classify_intent(issue_text)
        
        # Extract entities
        entities = self.extract_entities(issue_text)
        
        # Generate code template
        code_template = self.generate_code_template(intent, entities)
        
        # Generate implementation plan
        implementation_plan = self.generate_implementation_plan(intent, entities)
        
        # Suggest files
        file_suggestions = self.suggest_files(intent, entities)
        
        # Calculate overall confidence
        entity_confidence = sum(e.confidence for e in entities) / max(len(entities), 1)
        overall_confidence = (intent_confidence + entity_confidence) / 2
        
        # Metadata
        metadata = {
            'entity_count': len(entities),
            'entity_types': list(set(e.type for e in entities)),
            'intent_name': intent.value
        }
        
        return TranslationResult(
            intent=intent,
            entities=entities,
            code_template=code_template,
            implementation_plan=implementation_plan,
            file_suggestions=file_suggestions,
            confidence=overall_confidence,
            metadata=metadata
        )


def main():
    """Main entry point for CLI usage."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Translate natural language issue descriptions to code"
    )
    parser.add_argument(
        'input',
        nargs='?',
        help='Issue text or path to file containing issue text'
    )
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output result as JSON'
    )
    parser.add_argument(
        '--template-only',
        action='store_true',
        help='Only output the code template'
    )
    
    args = parser.parse_args()
    
    # Get input text
    if args.input:
        if Path(args.input).exists():
            with open(args.input, 'r') as f:
                issue_text = f.read()
        else:
            issue_text = args.input
    else:
        # Read from stdin
        issue_text = sys.stdin.read()
    
    # Translate
    translator = NLToCodeTranslator()
    result = translator.translate(issue_text)
    
    # Output
    if args.template_only:
        print(result.code_template)
    elif args.json:
        output = {
            'intent': result.intent.value,
            'entities': [asdict(e) for e in result.entities],
            'code_template': result.code_template,
            'implementation_plan': result.implementation_plan,
            'file_suggestions': result.file_suggestions,
            'confidence': result.confidence,
            'metadata': result.metadata
        }
        print(json.dumps(output, indent=2))
    else:
        print(f"Intent: {result.intent.value} (confidence: {result.confidence:.2f})")
        print(f"\nEntities ({len(result.entities)}):")
        for entity in result.entities:
            print(f"  - {entity.type}: {entity.name} (confidence: {entity.confidence:.2f})")
        
        print(f"\nFile Suggestions:")
        for file in result.file_suggestions:
            print(f"  - {file}")
        
        print(f"\nImplementation Plan:")
        for i, step in enumerate(result.implementation_plan, 1):
            print(f"  {i}. {step}")
        
        print(f"\nCode Template:")
        print("-" * 60)
        print(result.code_template)
        print("-" * 60)


if __name__ == "__main__":
    main()
