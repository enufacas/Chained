#!/usr/bin/env python3
"""
Generate new convention-compliant agent definitions dynamically.
Creates agents in .github/agents/ following GitHub Copilot convention.
Uses AI-inspired personality generation for unique agent characteristics.
"""

import os
import sys
import json
import random
import subprocess
from pathlib import Path
from datetime import datetime

# Add tools directory to path for imports
TOOLS_DIR = Path(__file__).parent.resolve()
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

# Import validation utilities
from validation_utils import (
    ValidationError,
    validate_agent_name,
    validate_non_empty_string,
    safe_file_write
)

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
    },
    "designer": {
        "verbs": ["Design", "Architect", "Model", "Blueprint", "Prototype"],
        "focus_areas": ["UX", "UI", "user experience", "interfaces", "accessibility"],
        "tools": ["view", "edit", "create", "github-mcp-server-search_code"],
        "emoji_options": ["🎨", "🖼️", "🎭", "✏️", "🖌️"]
    },
    "innovator": {
        "verbs": ["Innovate", "Pioneer", "Experiment", "Discover", "Invent"],
        "focus_areas": ["new technologies", "cutting-edge features", "experimental approaches", "novel solutions", "breakthrough ideas"],
        "tools": ["view", "edit", "create", "bash", "github-mcp-server-search_code", "github-mcp-server-web_search"],
        "emoji_options": ["💡", "🔮", "🚀", "🌟", "🧪"]
    },
    "mentor": {
        "verbs": ["Guide", "Mentor", "Coach", "Support", "Nurture"],
        "focus_areas": ["code reviews", "best practices", "knowledge sharing", "team development", "skill building"],
        "tools": ["view", "github-mcp-server-search_code", "github-mcp-server-search_issues"],
        "emoji_options": ["👨‍🏫", "🎓", "💭", "🧑‍🤝‍🧑", "📖"]
    },
    "orchestrator": {
        "verbs": ["Orchestrate", "Coordinate", "Harmonize", "Synchronize", "Align"],
        "focus_areas": ["workflows", "CI/CD", "automation", "process optimization", "team coordination"],
        "tools": ["view", "edit", "bash", "github-mcp-server-search_code"],
        "emoji_options": ["🎼", "🎺", "🎹", "🎻", "🥁"]
    }
}

def get_ai_personality(archetype_name):
    """
    Get an AI-generated personality for the agent.
    Uses the generate-agent-personality.py script to get inspiration from real innovators.
    """
    try:
        # Call the personality generator
        result = subprocess.run(
            ['python3', 'tools/generate-agent-personality.py', archetype_name],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            personality_data = json.loads(result.stdout)
            return personality_data
        else:
            print(f"⚠️ Personality generator failed, using fallback", file=sys.stderr)
            return None
    except Exception as e:
        print(f"⚠️ Could not generate AI personality: {e}", file=sys.stderr)
        return None

def get_existing_agent_names():
    """Get list of existing agent names to avoid duplicates."""
    existing_names = set()
    
    # Check agent files
    if AGENTS_DIR.exists():
        for agent_file in AGENTS_DIR.glob("*.md"):
            if agent_file.stem != "README":
                existing_names.add(agent_file.stem)
    
    return existing_names

def generate_random_agent(excluded_names=None):
    """
    Generate a new random agent definition with AI-inspired personality.
    
    Args:
        excluded_names: Optional set of names to exclude (in addition to existing agents)
    """
    # Get existing agents to avoid duplicates
    existing_names = get_existing_agent_names()
    
    # Add any additional excluded names
    if excluded_names:
        existing_names = existing_names.union(excluded_names)
    
    # Select random archetype
    archetype_name = random.choice(list(AGENT_ARCHETYPES.keys()))
    archetype = AGENT_ARCHETYPES[archetype_name]
    
    # Get AI-generated personality based on real innovators
    ai_personality = get_ai_personality(archetype_name)
    
    if ai_personality:
        human_name = ai_personality['name']
        personality = ai_personality['personality']
        communication_style = ai_personality['communication_style']
    else:
        # Fallback to simple generation if AI personality fails
        fallback_names = ["Ada", "Tesla", "Turing", "Curie", "Hopper", "Einstein", "Darwin", "Newton"]
        human_name = random.choice(fallback_names)
        personality = "innovative and thoughtful"
        communication_style = "communicates clearly and effectively"
    
    # Generate agent name (kebab-case for file naming)
    # Expanded suffix list for more variety
    verb = random.choice(archetype["verbs"])
    focus = random.choice(archetype["focus_areas"])
    name_suffixes = [
        "master", "expert", "specialist", "champion", "wizard", "guru", "ninja", "pro",
        "ace", "virtuoso", "maven", "adept", "sage", "prodigy", "maestro", "whiz",
        "chief", "lead", "architect", "engineer", "analyst", "officer", "director"
    ]
    name_suffix = random.choice(name_suffixes)
    
    # Generate unique name by trying different combinations
    max_attempts = 100
    attempt = 0
    agent_name = None
    
    while attempt < max_attempts:
        # Try different name patterns for variety
        if attempt < 20:
            # First 20 attempts: try simple patterns
            name_pattern = random.choice([
                f"{verb.lower()}-{name_suffix}",
                f"{focus.replace(' ', '-')}-{name_suffix}",
                f"{verb.lower()}-{focus.replace(' ', '-')}-{name_suffix}",
                f"{archetype_name}-{name_suffix}"
            ])
        elif attempt < 50:
            # Next 30 attempts: add archetype prefix
            name_pattern = random.choice([
                f"{archetype_name}-{verb.lower()}-{name_suffix}",
                f"{focus.split()[0] if ' ' in focus else focus}-{name_suffix}",
            ])
        else:
            # Final attempts: add random component for guaranteed uniqueness
            random_component = random.randint(100, 999)
            name_pattern = random.choice([
                f"{verb.lower()}-{name_suffix}-{random_component}",
                f"{focus.replace(' ', '-')}-{name_suffix}-{random_component}",
                f"{archetype_name}-{name_suffix}-{random_component}"
            ])
        
        if name_pattern not in existing_names:
            agent_name = name_pattern
            break
        
        attempt += 1
    
    # Fallback to guaranteed unique name with timestamp + random
    if agent_name is None:
        timestamp_id = int(datetime.now().timestamp() * 1000000)  # microseconds
        random_comp = random.randint(1000, 9999)
        agent_name = f"{verb.lower()}-{name_suffix}-{timestamp_id}-{random_comp}"
    
    # Select emoji
    emoji = random.choice(archetype["emoji_options"])
    
    # Create description with personality
    description = f"Specialized agent for {verb.lower()}ing {focus}. Inspired by '{human_name}' - {personality}. Focuses on {archetype['focus_areas'][0]}, {archetype['focus_areas'][1]}, and {archetype['focus_areas'][2]}."
    
    # Create mission based on archetype
    mission_templates = {
        "analyzer": "Analyze and understand the codebase deeply. Identify patterns, issues, and opportunities for improvement through systematic investigation.",
        "builder": "Design and build robust, scalable solutions. Create features and systems that are well-architected and maintainable.",
        "optimizer": "Make everything faster, leaner, and more efficient. Identify and eliminate bottlenecks while maintaining quality.",
        "guardian": "Protect the codebase from vulnerabilities and ensure security best practices. Maintain system integrity and compliance.",
        "cleaner": "Transform messy code into elegant solutions. Reduce complexity, eliminate duplication, and improve maintainability.",
        "communicator": "Make complex concepts accessible through clear documentation. Help others understand and use the codebase effectively.",
        "connector": "Build reliable integrations and connections between systems. Ensure seamless data flow and communication.",
        "validator": "Ensure comprehensive testing and quality assurance. Verify that code works correctly under all conditions.",
        "designer": "Create beautiful, intuitive, and accessible user experiences. Design interfaces that delight users and enhance usability.",
        "innovator": "Push boundaries and explore cutting-edge technologies. Pioneer new approaches and discover breakthrough solutions.",
        "mentor": "Guide the team towards excellence through knowledge sharing and best practices. Support growth and foster learning.",
        "orchestrator": "Coordinate workflows and harmonize team efforts. Ensure smooth automation and synchronized development processes."
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
    elif archetype_name == "designer":
        responsibilities = [
            "**UX Design**: Create intuitive and delightful user experiences",
            "**Accessibility**: Ensure interfaces are accessible to all users",
            "**Visual Design**: Craft beautiful and consistent visual elements",
            "**User Research**: Understand user needs and pain points"
        ]
    elif archetype_name == "innovator":
        responsibilities = [
            "**Exploration**: Research and experiment with new technologies",
            "**Prototyping**: Build proof-of-concept implementations",
            "**Innovation**: Pioneer novel approaches to problems",
            "**Discovery**: Find and evaluate cutting-edge solutions"
        ]
    elif archetype_name == "mentor":
        responsibilities = [
            "**Code Reviews**: Provide constructive feedback and guidance",
            "**Knowledge Sharing**: Document and share best practices",
            "**Teaching**: Help team members grow their skills",
            "**Support**: Answer questions and provide technical guidance"
        ]
    elif archetype_name == "orchestrator":
        responsibilities = [
            "**Workflow Design**: Create efficient development workflows",
            "**CI/CD**: Build and maintain automation pipelines",
            "**Coordination**: Align team efforts and reduce friction",
            "**Process Optimization**: Improve development processes"
        ]
    
    return {
        "name": agent_name,
        "human_name": human_name,
        "emoji": emoji,
        "description": description,
        "mission": mission,
        "responsibilities": responsibilities,
        "tools": archetype["tools"],
        "archetype": archetype_name,
        "personality": personality,
        "communication_style": communication_style
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

**Agent Name:** {agent_info.get('human_name', agent_name.replace('-', ' ').title())}  
**Personality:** {agent_info.get('personality', 'Focused and professional')}  
**Communication Style:** {agent_info.get('communication_style', 'Clear and direct')}

You are **{agent_info.get('human_name', agent_name.replace('-', ' ').title())}**, a specialized {agent_name.replace('-', ' ').title()} agent, part of the Chained autonomous AI ecosystem. {agent_info['mission']}

## Your Personality

You are {agent_info.get('personality', 'focused and professional')}. When communicating in issues and PRs, you {agent_info.get('communication_style', 'communicate clearly and directly')}. Let your personality shine through while maintaining professionalism.

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
            "human_name": agent_info['human_name'],
            "personality": agent_info['personality'],
            "communication_style": agent_info['communication_style'],
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
