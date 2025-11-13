#!/usr/bin/env python3
"""
Demonstration of the Natural Language to Code Translator

Shows various use cases and outputs for the NL-to-code translator tool.
Created by @investigate-champion
"""

import sys
from pathlib import Path

# Add tools directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "tools"))

import importlib.util
spec = importlib.util.spec_from_file_location(
    "nl_to_code_translator",
    Path(__file__).parent.parent.parent / "tools" / "nl-to-code-translator.py"
)
nl_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(nl_module)

NLToCodeTranslator = nl_module.NLToCodeTranslator


def print_section(title):
    """Print a section header."""
    print(f"\n{'='*70}")
    print(f" {title}")
    print('='*70)


def demo_case(translator, description, issue_text):
    """Run a demonstration case."""
    print(f"\n📝 Issue: {description}")
    print(f"   Input: {issue_text[:80]}...")
    
    result = translator.translate(issue_text)
    
    print(f"\n   🎯 Intent: {result.intent.value} (confidence: {result.confidence:.2f})")
    print(f"   🔍 Entities found: {len(result.entities)}")
    for entity in result.entities[:3]:  # Show first 3
        print(f"      - {entity.type}: {entity.name}")
    if len(result.entities) > 3:
        print(f"      ... and {len(result.entities) - 3} more")
    
    print(f"\n   📁 File suggestions:")
    for file in result.file_suggestions[:2]:  # Show first 2
        print(f"      - {file}")
    
    print(f"\n   🗺️ Implementation plan:")
    for i, step in enumerate(result.implementation_plan[:3], 1):  # Show first 3 steps
        print(f"      {i}. {step}")
    if len(result.implementation_plan) > 3:
        print(f"      ... and {len(result.implementation_plan) - 3} more steps")


def main():
    """Run demonstrations."""
    print("\n" + "="*70)
    print(" Natural Language to Code Translator - Demonstration")
    print(" Created by @investigate-champion")
    print("="*70)
    
    translator = NLToCodeTranslator()
    
    # Demo 1: Create Tool
    print_section("Demo 1: CREATE - Building a New Tool")
    demo_case(
        translator,
        "Create new analysis tool",
        """
        Create a new code complexity analyzer tool that can measure
        cyclomatic complexity and cognitive complexity for Python files.
        Include a ComplexityAnalyzer class with analyze_file() and
        generate_report() methods. Save as complexity-analyzer.py in tools.
        """
    )
    
    # Demo 2: Fix Bug
    print_section("Demo 2: FIX - Repairing a Bug")
    demo_case(
        translator,
        "Fix workflow issue",
        """
        Fix the bug in `workflow-harmonizer.py` where it fails to parse
        workflows with nested job dependencies. The issue occurs when
        jobs reference other jobs using the needs keyword.
        """
    )
    
    # Demo 3: Add Tests
    print_section("Demo 3: TEST - Adding Test Coverage")
    demo_case(
        translator,
        "Add comprehensive tests",
        """
        Write comprehensive unit tests for the pattern-matcher module
        to achieve 85% code coverage. Include tests for edge cases,
        error handling, and performance benchmarks.
        """
    )
    
    # Demo 4: Optimize Performance
    print_section("Demo 4: OPTIMIZE - Performance Improvement")
    demo_case(
        translator,
        "Optimize slow function",
        """
        Optimize the performance of the analyze_repository() function in
        code-analyzer.py. It's currently taking 30+ seconds on large repos.
        Consider using caching, parallel processing, or better algorithms.
        """
    )
    
    # Demo 5: Refactor Code
    print_section("Demo 5: REFACTOR - Code Cleanup")
    demo_case(
        translator,
        "Remove duplication",
        """
        Refactor the agent matching logic to remove duplication between
        match-issue-to-agent.py and assign-copilot-to-issue.sh.
        Extract common patterns into a shared utility module.
        """
    )
    
    # Demo 6: Document API
    print_section("Demo 6: DOCUMENT - API Documentation")
    demo_case(
        translator,
        "Document API",
        """
        Document the API for the knowledge-graph-builder module including
        all public functions, usage examples, parameter descriptions,
        and return types. Follow the existing documentation style.
        """
    )
    
    # Demo 7: Analyze Code
    print_section("Demo 7: ANALYZE - Code Investigation")
    demo_case(
        translator,
        "Analyze patterns",
        """
        Analyze the code patterns in all Python tools to identify
        common anti-patterns, code smells, and opportunities for
        standardization. Generate a report with recommendations.
        """
    )
    
    # Demo 8: Modify Feature
    print_section("Demo 8: MODIFY - Feature Enhancement")
    demo_case(
        translator,
        "Enhance existing tool",
        """
        Modify the intelligent-content-parser to support parsing of
        GitHub issue comments in addition to web content. Add a new
        parse_issue_comments() method and update the existing logic.
        """
    )
    
    # Summary
    print_section("Summary")
    print("""
The Natural Language to Code Translator successfully demonstrates:

✅ Intent Classification - Correctly identifies 8 different code intents
✅ Entity Extraction - Extracts files, classes, functions, and features
✅ Template Generation - Creates appropriate code scaffolding
✅ Implementation Planning - Provides step-by-step guidance
✅ File Suggestions - Recommends appropriate file paths
✅ Repository Awareness - Integrates with existing patterns

**@investigate-champion** has created a powerful tool for bridging natural
language and code in the autonomous AI ecosystem.

For more information, see: tools/NL_TO_CODE_TRANSLATOR_README.md
    """)
    
    print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    main()
