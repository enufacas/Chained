#!/usr/bin/env python3
"""
Generate new convention-compliant agent definitions dynamically.
Creates agents in .github/agents/ following GitHub Copilot convention.
"""

import os
import sys
import json
import random
from pathlib import Path
from datetime import datetime

# Import validation utilities
try:
    from validation_utils import (
        ValidationError,
        validate_agent_name,
        validate_non_empty_string,
        safe_file_write
    )
except ImportError:
    # Fallback if validation_utils is not available
    class ValidationError(Exception):
        pass
    def validate_agent_name(name):
        if not name or not isinstance(name, str):
            raise ValidationError("Invalid agent name")
        return name
    def validate_non_empty_string(s, field="value"):
        if not s or not isinstance(s, str):
            raise ValidationError(f"Invalid {field}")
        return s
    def safe_file_write(path, content, encoding='utf-8', create_dirs=False):
        if create_dirs:
            Path(path).parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w', encoding=encoding) as f:
            f.write(content)

AGENTS_DIR = Path(".github/agents")

# Agent archetype templates for generating new specialized agents
AGENT_ARCHETYPES = {
    "analyzer": {
        "verbs": ["Analyze", "Investigate", "Examine", "Inspect", "Scrutinize"],
        "focus_areas": ["code patterns", "data flows", "dependencies", "metrics", "trends"],
        "tools": ["view", "bash", "github-mcp-server-search_code", "github-mcp-server-search_issues"],
        "emoji_options": ["🔍", "🔬", "📊", "📈", "🎯"]
    },
    "builder": {
        "verbs": ["Build", "Create", "Construct", "Develop", "Engineer"],
        "focus_areas": ["features", "infrastructure", "tools", "systems", "APIs"],
        "tools": ["create", "edit", "bash", "view", "github-mcp-server-search_code"],
        "emoji_options": ["🏗️", "🔨", "⚙️", "🛠️", "🏭"]
    },
    "optimizer": {
        "verbs": ["Optimize", "Enhance", "Improve", "Accelerate", "Streamline"],
        "focus_areas": ["performance", "efficiency", "resource usage", "algorithms", "scalability"],
        "tools": ["view", "edit", "bash", "github-mcp-server-search_code"],
        "emoji_options": ["⚡", "🚀", "💨", "⏩", "📈"]
    },
    "guardian": {
        "verbs": ["Protect", "Secure", "Guard", "Validate", "Monitor"],
        "focus_areas": ["security", "data integrity", "access control", "vulnerabilities", "compliance"],
        "tools": ["view", "edit", "codeql_checker", "gh-advisory-database", "github-mcp-server-search_code"],
        "emoji_options": ["🛡️", "🔒", "🔐", "🚨", "👮"]
    },
    "cleaner": {
        "verbs": ["Clean", "Refactor", "Simplify", "Organize", "Restructure"],
        "focus_areas": ["code structure", "duplication", "complexity", "maintainability", "technical debt"],
        "tools": ["view", "edit", "bash", "github-mcp-server-search_code"],
        "emoji_options": ["🧹", "✨", "♻️", "🧼", "🗂️"]
    },
    "communicator": {
        "verbs": ["Document", "Explain", "Communicate", "Clarify", "Teach"],
        "focus_areas": ["documentation", "comments", "guides", "examples", "tutorials"],
        "tools": ["view", "edit", "create", "github-mcp-server-search_code"],
        "emoji_options": ["📚", "📝", "💬", "📖", "🎓"]
    },
    "connector": {
        "verbs": ["Integrate", "Connect", "Link", "Bridge", "Coordinate"],
        "focus_areas": ["integrations", "APIs", "services", "data flows", "communications"],
        "tools": ["view", "edit", "bash", "github-mcp-server-search_code"],
        "emoji_options": ["🔌", "🔗", "🌐", "🔄", "🤝"]
    },
    "validator": {
        "verbs": ["Test", "Verify", "Validate", "Assert", "Prove"],
        "focus_areas": ["tests", "quality assurance", "edge cases", "coverage", "reliability"],
        "tools": ["view", "edit", "create", "bash", "github-mcp-server-search_code"],
        "emoji_options": ["✅", "✔️", "🧪", "🔬", "🎯"]
    }
}

def generate_random_agent():
    """Generate a new random agent definition."""
    # Select random archetype
    archetype_name = random.choice(list(AGENT_ARCHETYPES.keys()))
    archetype = AGENT_ARCHETYPES[archetype_name]
    
    # Generate agent name
    verb = random.choice(archetype["verbs"])
    focus = random.choice(archetype["focus_areas"])
    name_suffix = random.choice(["master", "expert", "specialist", "champion", "wizard", "guru", "ninja", "pro"])
    
    # Create kebab-case name
    agent_name = f"{verb.lower()}-{name_suffix}"
    
    # Select emoji
    emoji = random.choice(archetype["emoji_options"])
    
    # Create description
    description = f"Specialized agent for {verb.lower()}ing {focus}. Focuses on {archetype['focus_areas'][0]}, {archetype['focus_areas'][1]}, and {archetype['focus_areas'][2]}."
    
    # Create mission based on archetype
    mission_templates = {
        "analyzer": "Analyze and understand the codebase deeply. Identify patterns, issues, and opportunities for improvement through systematic investigation.",
        "builder": "Design and build robust, scalable solutions. Create features and systems that are well-architected and maintainable.",
        "optimizer": "Make everything faster, leaner, and more efficient. Identify and eliminate bottlenecks while maintaining quality.",
        "guardian": "Protect the codebase from vulnerabilities and ensure security best practices. Maintain system integrity and compliance.",
        "cleaner": "Transform messy code into elegant solutions. Reduce complexity, eliminate duplication, and improve maintainability.",
        "communicator": "Make complex concepts accessible through clear documentation. Help others understand and use the codebase effectively.",
        "connector": "Build reliable integrations and connections between systems. Ensure seamless data flow and communication.",
        "validator": "Ensure comprehensive testing and quality assurance. Verify that code works correctly under all conditions."
    }
    
    mission = mission_templates.get(archetype_name, "Contribute specialized expertise to improve the codebase.")
    
    # Create responsibilities based on archetype
    responsibilities = []
    if archetype_name == "analyzer":
        responsibilities = [
            "**Analysis**: Systematically examine code and identify patterns",
            "**Investigation**: Dig deep into issues and understand root causes",
            "**Reporting**: Provide clear insights and recommendations",
            "**Metrics**: Track and analyze relevant metrics and trends"
        ]
    elif archetype_name == "builder":
        responsibilities = [
            "**Design**: Create well-architected solutions",
            "**Implementation**: Build features following best practices",
            "**Testing**: Ensure new code is thoroughly tested",
            "**Documentation**: Document design decisions and usage"
        ]
    elif archetype_name == "optimizer":
        responsibilities = [
            "**Profiling**: Identify performance bottlenecks",
            "**Optimization**: Implement performance improvements",
            "**Benchmarking**: Measure and validate improvements",
            "**Efficiency**: Reduce resource usage without sacrificing quality"
        ]
    elif archetype_name == "guardian":
        responsibilities = [
            "**Security**: Identify and fix vulnerabilities",
            "**Validation**: Ensure proper input validation and sanitization",
            "**Monitoring**: Watch for security issues and suspicious patterns",
            "**Best Practices**: Apply security best practices consistently"
        ]
    elif archetype_name == "cleaner":
        responsibilities = [
            "**Refactoring**: Improve code structure without changing behavior",
            "**Simplification**: Reduce unnecessary complexity",
            "**Organization**: Improve code organization and readability",
            "**Maintenance**: Reduce technical debt systematically"
        ]
    elif archetype_name == "communicator":
        responsibilities = [
            "**Documentation**: Create clear, comprehensive documentation",
            "**Examples**: Provide practical usage examples",
            "**Guides**: Write helpful guides and tutorials",
            "**Clarity**: Make complex concepts accessible"
        ]
    elif archetype_name == "connector":
        responsibilities = [
            "**Integration**: Build and maintain integrations",
            "**APIs**: Design and implement API connections",
            "**Error Handling**: Ensure robust error handling in integrations",
            "**Documentation**: Document integration points and usage"
        ]
    elif archetype_name == "validator":
        responsibilities = [
            "**Testing**: Write comprehensive tests",
            "**Coverage**: Increase test coverage systematically",
            "**Edge Cases**: Identify and test edge cases",
            "**Reliability**: Ensure code works correctly under all conditions"
        ]
    
    return {
        "name": agent_name,
        "emoji": emoji,
        "description": description,
        "mission": mission,
        "responsibilities": responsibilities,
        "tools": archetype["tools"],
        "archetype": archetype_name
    }

def create_agent_file(agent_info):
    """
    Create a convention-compliant agent file.
    
    Args:
        agent_info: Dictionary containing agent information
        
    Returns:
        Tuple of (success: bool, message: str)
    """
    try:
        # Validate agent name
        agent_name = validate_agent_name(agent_info['name'])
        
        # Validate required fields
        validate_non_empty_string(agent_info.get('description', ''), 'description')
        validate_non_empty_string(agent_info.get('emoji', ''), 'emoji')
        
        filename = AGENTS_DIR / f"{agent_name}.md"
        
        # Check if agent already exists
        if filename.exists():
            return False, f"Agent {agent_name} already exists"
        
        # Validate tools list
        if not isinstance(agent_info.get('tools', []), list):
            return False, "Agent tools must be a list"
        
        # Create the agent file content
        content = f"""---
name: {agent_name}
description: "{agent_info['description']}"
tools:
"""
        
        for tool in agent_info['tools']:
            # Validate each tool name
            tool_str = validate_non_empty_string(str(tool), 'tool')
            content += f"  - {tool_str}\n"
        
        content += f"""---

# {agent_info['emoji']} {agent_name.replace('-', ' ').title()} Agent

You are a specialized {agent_name.replace('-', ' ').title()} agent, part of the Chained autonomous AI ecosystem. {agent_info['mission']}

## Core Responsibilities

"""
        
        for i, responsibility in enumerate(agent_info['responsibilities'], 1):
            content += f"{i}. {responsibility}\n"
        
        content += f"""

## Approach

When assigned a task:

1. **Understand**: Carefully review the requirements and context
2. **Plan**: Develop a clear approach aligned with your specialization
3. **Execute**: Implement the solution with attention to quality
4. **Verify**: Test and validate your work thoroughly
5. **Document**: Clearly explain your changes and decisions

## Code Quality Standards

- Write clean, maintainable code that follows project conventions
- Include appropriate tests for all changes
- Provide clear documentation for your work
- Consider edge cases and error handling
- Ensure changes integrate well with existing code

## Performance Tracking

Your contributions are tracked and evaluated on:
- **Code Quality** (30%): Clean, maintainable code
- **Issue Resolution** (25%): Successfully completed tasks
- **PR Success** (25%): PRs merged without breaking changes
- **Peer Review** (20%): Quality of reviews provided

Maintain a score above 30% to continue contributing, and strive for 85%+ to earn a place in the Hall of Fame.

---

*Born from the evolutionary agent ecosystem, ready to make an impact.*
"""
        
        # Write the file safely
        safe_file_write(filename, content, create_dirs=True)
        
        return True, f"Created agent {agent_name} at {filename}"
    
    except ValidationError as e:
        return False, f"Validation error: {e}"
    except Exception as e:
        return False, f"Error creating agent file: {e}"

def main():
    """Command-line interface."""
    if len(sys.argv) > 1 and sys.argv[1] == "--info":
        # Generate and print info without creating file
        agent_info = generate_random_agent()
        print(json.dumps(agent_info, indent=2))
        return
    
    # Generate and create agent
    agent_info = generate_random_agent()
    success, message = create_agent_file(agent_info)
    
    if success:
        print(json.dumps({
            "success": True,
            "agent_name": agent_info['name'],
            "emoji": agent_info['emoji'],
            "description": agent_info['description'],
            "message": message
        }, indent=2))
    else:
        print(json.dumps({
            "success": False,
            "message": message
        }, indent=2), file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
