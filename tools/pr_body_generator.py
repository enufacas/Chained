#!/usr/bin/env python3
"""
Pull Request Body Generator

Crafts elegant PR bodies for evaluation commits.
Every PR tells a story of change and evolution.
"""

import json
from pathlib import Path
from typing import Dict, List, Any


def generate_pr_body() -> str:
    """
    Generate a beautiful PR body from evaluation results.
    
    Returns formatted PR body string ready for GitHub.
    """
    # Load evaluation results
    results_path = Path('/tmp/evaluation_results.json')
    with open(results_path, 'r') as file:
        results = json.load(file)
    
    # Extract counts
    promoted = results.get('promoted', [])
    eliminated = results.get('eliminated', [])
    maintained = results.get('maintained', [])
    
    # Build PR body sections
    sections = [
        _create_header(),
        _create_summary(len(promoted), len(eliminated), len(maintained)),
        _create_promoted_section(promoted),
        _create_eliminated_section(eliminated),
        _create_changes_section(),
        _create_footer()
    ]
    
    return '\n\n'.join(filter(None, sections))


def _create_header() -> str:
    """Create PR header"""
    return """## 🏛️ Daily Agent Evaluation Results

The agent ecosystem has been evaluated based on performance metrics."""


def _create_summary(promoted: int, eliminated: int, maintained: int) -> str:
    """Create summary section"""
    return f"""### Summary

- 🏆 **Promoted to Hall of Fame**: {promoted} agents
- ❌ **Eliminated**: {eliminated} agents  
- ✅ **Maintained Active Status**: {maintained} agents"""


def _create_promoted_section(promoted: List[Dict[str, Any]]) -> str:
    """Create promoted agents section"""
    if not promoted:
        return ""
    
    lines = ["#### 🏆 Promoted to Hall of Fame", ""]
    
    for agent in promoted:
        name = agent['name']
        score = agent['score']
        lines.append(f"- **{name}** - Score: {score:.2%}")
    
    return '\n'.join(lines)


def _create_eliminated_section(eliminated: List[Dict[str, Any]]) -> str:
    """Create eliminated agents section"""
    if not eliminated:
        return ""
    
    lines = ["#### ❌ Eliminated", ""]
    
    for agent in eliminated:
        name = agent['name']
        score = agent['score']
        lines.append(f"- **{name}** - Score: {score:.2%} (below threshold)")
    
    return '\n'.join(lines)


def _create_changes_section() -> str:
    """Create changes section"""
    return """### Changes

- Updated agent registry
- Modified agent profiles  
- Archived eliminated agents
- Updated system lead if applicable"""


def _create_footer() -> str:
    """Create PR footer"""
    return "---\n*🤖 Automated agent evaluation system - Survival of the fittest in action!*"


if __name__ == '__main__':
    print(generate_pr_body())
