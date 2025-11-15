#!/usr/bin/env python3
"""
Example Integration: HN Code Generator with Learnings Book

Shows how to integrate the code generator with the learnings book
to automatically generate tools based on trending topics.

Created by @investigate-champion
"""

import json
import sys
from pathlib import Path

# Add tools to path
tools_dir = Path(__file__).parent.parent
sys.path.insert(0, str(tools_dir))

try:
    from hn_code_generator import HNCodeGenerator
except ImportError:
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "hn_code_generator",
        tools_dir / "hn-code-generator.py"
    )
    hn_code_generator = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(hn_code_generator)
    HNCodeGenerator = hn_code_generator.HNCodeGenerator


def generate_tools_from_learnings_book():
    """
    Read learnings book topics and generate relevant tools
    """
    print("="*70)
    print("Integration Example: Generate Tools from Learnings Book")
    print("="*70)
    print()
    
    # Initialize generator
    generator = HNCodeGenerator()
    
    # Read learnings book
    book_dir = Path(__file__).parent.parent.parent / "learnings" / "book"
    
    if not book_dir.exists():
        print("⚠️  Learnings book not found")
        return
    
    # Check AI/ML chapter
    ai_ml_file = book_dir / "AI_ML.md"
    
    if ai_ml_file.exists():
        print("📖 Reading AI & Machine Learning chapter...")
        
        # In a real implementation, we'd parse the markdown
        # For now, we'll generate based on common AI topics
        
        ai_topics = [
            ("machine learning model", "MLModel", "neural network"),
            ("transformer architecture", "TransformerBlock", "attention-based model"),
            ("data preprocessing", "DataPreprocessor", "training data"),
        ]
        
        print()
        print("Generating AI/ML tools:")
        print()
        
        for description, class_name, context_name in ai_topics:
            generated = generator.generate_code(
                description,
                context={
                    'class_name': class_name,
                    'model_name': context_name
                }
            )
            
            if generated:
                print(f"✓ {class_name}")
                print(f"  Template: {generated.template_used}")
                print(f"  Confidence: {generated.confidence:.2f}")
                print()
    
    # Check Programming chapter
    prog_file = book_dir / "Programming.md"
    
    if prog_file.exists():
        print("📖 Reading Programming chapter...")
        print()
        
        prog_topics = [
            ("API client", "CodeAPI", "GitHub"),
            ("code analyzer", "CodeAnalyzer", "Python code"),
        ]
        
        print("Generating Programming tools:")
        print()
        
        for description, class_name, context_name in prog_topics:
            generated = generator.generate_code(
                description,
                context={
                    'class_name': class_name,
                    'api_name': context_name
                }
            )
            
            if generated:
                print(f"✓ {class_name}")
                print(f"  Template: {generated.template_used}")
                print(f"  Confidence: {generated.confidence:.2f}")
                print()
    
    # Final statistics
    print("="*70)
    stats = generator.get_statistics()
    print(f"📊 Total generated: {stats['total_generated']} tools")
    print(f"📈 Average confidence: {stats['avg_confidence']:.2f}")
    print("="*70)


if __name__ == '__main__':
    generate_tools_from_learnings_book()
