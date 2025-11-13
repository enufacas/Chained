#!/usr/bin/env python3
"""
Learning-Inspired Agent Generator

Dynamically creates agent definitions based on recent learnings from
Hacker News and TLDR Tech. Does not use repository literals - generates
completely new agent personalities and specializations at runtime.

Part of the Chained autonomous AI ecosystem.
Created by @create-guru - inspired by Nikola Tesla's vision for dynamic evolution.
"""

import json
import os
import sys
import random
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from datetime import datetime, timedelta
import re


class LearningInspiredAgentGenerator:
    """
    Generates custom agents dynamically based on learnings analysis.
    
    This generator:
    - Reads recent learning files (HN and TLDR)
    - Analyzes hot themes and technologies
    - Creates unique agent personalities
    - Generates agent names based on trending content
    - Produces agent definitions conforming to system spec
    - Does NOT use hardcoded repo descriptions
    """
    
    # Tech personality inspirations (famous computer scientists/inventors)
    TECH_PERSONALITIES = [
        "Ada Lovelace", "Alan Turing", "Grace Hopper", "Dennis Ritchie",
        "Linus Torvalds", "Bjarne Stroustrup", "Guido van Rossum",
        "Rich Hickey", "Rob Pike", "Ken Thompson", "Donald Knuth",
        "John von Neumann", "Claude Shannon", "Edsger Dijkstra",
        "Barbara Liskov", "Margaret Hamilton", "Frances Allen",
        "John McCarthy", "Marvin Minsky", "Geoffrey Hinton"
    ]
    
    # Communication style descriptors
    COMM_STYLES = [
        "concise and technical",
        "enthusiastic with examples",
        "methodical step-by-step",
        "direct and pragmatic",
        "analytical with data",
        "creative with analogies",
        "encouraging and supportive",
        "philosophical and deep"
    ]
    
    # Personality traits
    PERSONALITY_TRAITS = [
        "innovative and bold",
        "meticulous and precise",
        "pragmatic and efficient",
        "visionary and creative",
        "systematic and thorough",
        "curious and exploratory",
        "disciplined and focused",
        "collaborative and adaptive"
    ]
    
    # Tool sets based on specialization type
    TOOL_SETS = {
        'infrastructure': [
            'view', 'edit', 'create', 'bash',
            'github-mcp-server-list_workflows',
            'github-mcp-server-get_workflow_run'
        ],
        'testing': [
            'view', 'edit', 'create', 'bash',
            'github-mcp-server-search_code',
            'github-mcp-server-get_file_contents'
        ],
        'security': [
            'view', 'edit', 'create', 'bash',
            'gh-advisory-database',
            'codeql_checker'
        ],
        'code_quality': [
            'view', 'edit', 'create', 'bash',
            'github-mcp-server-search_code',
            'code_review'
        ],
        'integration': [
            'view', 'edit', 'create', 'bash',
            'github-mcp-server-search_code',
            'github-mcp-server-web_search'
        ],
        'performance': [
            'view', 'edit', 'create', 'bash',
            'github-mcp-server-search_code'
        ],
        'general': [
            'view', 'edit', 'create', 'bash',
            'github-mcp-server-search_code',
            'github-mcp-server-get_file_contents'
        ]
    }
    
    def __init__(self, learnings_dir: str = 'learnings'):
        """Initialize the generator with a learnings directory."""
        self.learnings_dir = Path(learnings_dir)
        
    def load_recent_analysis(self, hours: int = 12) -> Optional[Dict[str, Any]]:
        """Load the most recent analysis file within the specified hours."""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        analysis_files = sorted(
            self.learnings_dir.glob('analysis_*.json'),
            key=lambda f: f.stat().st_mtime,
            reverse=True
        )
        
        for analysis_file in analysis_files:
            file_time = datetime.fromtimestamp(analysis_file.stat().st_mtime)
            if file_time >= cutoff_time:
                with open(analysis_file, 'r') as f:
                    return json.load(f)
        
        return None
    
    def load_recent_learnings(self, hours: int = 12) -> List[Dict[str, Any]]:
        """Load recent HN and TLDR learning files."""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        learnings = []
        
        # Load HN files
        hn_files = sorted(
            self.learnings_dir.glob('hn_*.json'),
            key=lambda f: f.stat().st_mtime,
            reverse=True
        )
        
        for hn_file in hn_files[:3]:  # Last 3 HN files
            file_time = datetime.fromtimestamp(hn_file.stat().st_mtime)
            if file_time >= cutoff_time:
                with open(hn_file, 'r') as f:
                    data = json.load(f)
                    learnings.extend(data.get('learnings', []))
        
        # Load TLDR files
        tldr_files = sorted(
            self.learnings_dir.glob('tldr_*.json'),
            key=lambda f: f.stat().st_mtime,
            reverse=True
        )
        
        for tldr_file in tldr_files[:3]:  # Last 3 TLDR files
            file_time = datetime.fromtimestamp(tldr_file.stat().st_mtime)
            if file_time >= cutoff_time:
                with open(tldr_file, 'r') as f:
                    data = json.load(f)
                    learnings.extend(data.get('learnings', []))
        
        return learnings
    
    def extract_interesting_topics(
        self, 
        analysis: Optional[Dict[str, Any]], 
        learnings: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Extract the most interesting topics from analysis and learnings.
        Returns a list of topics with metadata.
        """
        topics = []
        
        # From analysis file (if available)
        if analysis:
            # Top technologies
            for tech in analysis.get('top_technologies', [])[:5]:
                topics.append({
                    'name': tech['name'],
                    'category': tech.get('category', 'Technology'),
                    'score': tech.get('score', 0),
                    'mentions': tech.get('mention_count', 0),
                    'type': 'technology',
                    'keywords': tech.get('keywords', []),
                    'sample_titles': tech.get('sample_titles', [])
                })
            
            # Hot themes
            for theme in analysis.get('hot_themes', [])[:3]:
                topics.append({
                    'name': theme,
                    'category': 'Theme',
                    'score': 80,  # Hot themes get high score
                    'type': 'theme'
                })
        
        # From learnings directly (high-score items)
        for learning in learnings[:10]:  # Top 10 learnings
            title = learning.get('title', '')
            score = learning.get('score', 0)
            
            if score > 200:  # High community interest
                topics.append({
                    'name': title[:50],  # First 50 chars of title
                    'category': 'Trending',
                    'score': score / 10,  # Scale down
                    'type': 'learning',
                    'full_title': title,
                    'content': learning.get('content', '')[:500]
                })
        
        # Sort by score and return top ones
        topics.sort(key=lambda t: t.get('score', 0), reverse=True)
        return topics[:10]
    
    def generate_agent_specialization(self, topic: Dict[str, Any]) -> str:
        """Generate a specialization name based on a topic."""
        name = topic['name'].lower()
        category = topic.get('category', 'general').lower()
        
        # Clean up the name
        name = re.sub(r'[^a-z0-9\s-]', '', name)
        name = re.sub(r'\s+', '-', name.strip())
        
        # Create specialization based on category
        if 'ai' in name or 'ml' in name or 'llm' in name:
            spec_type = 'ai-specialist'
        elif 'security' in name or 'vulnerability' in name:
            spec_type = 'security-guardian'
        elif 'performance' in name or 'optimization' in name:
            spec_type = 'performance-optimizer'
        elif 'cloud' in name or 'infrastructure' in name:
            spec_type = 'cloud-architect'
        elif 'data' in name or 'database' in name:
            spec_type = 'data-engineer'
        elif 'test' in name or 'quality' in name:
            spec_type = 'quality-champion'
        else:
            # Use the topic name itself as specialization
            spec_type = name[:30]  # Limit length
        
        # Ensure it's a valid identifier
        spec_type = re.sub(r'[^a-z0-9-]', '', spec_type)
        spec_type = re.sub(r'-+', '-', spec_type).strip('-')
        
        return spec_type or 'tech-specialist'
    
    def generate_emoji(self, specialization: str) -> str:
        """Generate an emoji based on specialization."""
        spec_lower = specialization.lower()
        
        emoji_map = {
            'ai': '🤖', 'ml': '🧠', 'security': '🔒', 'cloud': '☁️',
            'data': '📊', 'performance': '⚡', 'test': '🧪', 'quality': '✨',
            'infrastructure': '🏗️', 'database': '🗄️', 'optimization': '🚀',
            'monitor': '👁️', 'api': '🔌', 'integration': '🔗', 'automation': '⚙️'
        }
        
        for keyword, emoji in emoji_map.items():
            if keyword in spec_lower:
                return emoji
        
        # Default emoji
        return random.choice(['🌟', '💡', '🎯', '🔧', '📡', '🎨'])
    
    def generate_description(
        self, 
        specialization: str, 
        topic: Dict[str, Any],
        personality_trait: str
    ) -> str:
        """Generate agent description based on specialization and topic."""
        category = topic.get('category', 'Technology')
        topic_name = topic['name']
        
        # Generate dynamic description
        descriptions = [
            f"Specialized agent for {topic_name} based on emerging tech trends. {personality_trait.capitalize()}, focuses on {category.lower()} innovations.",
            f"Expert in {topic_name} domain. Inspired by current tech discussions, {personality_trait}, and driven by {category.lower()} excellence.",
            f"Cutting-edge specialist for {topic_name}. {personality_trait.capitalize()} approach to {category.lower()} challenges.",
            f"Dynamic agent focused on {topic_name}. {personality_trait.capitalize()}, specializes in {category.lower()} solutions.",
        ]
        
        return random.choice(descriptions)
    
    def generate_responsibilities(
        self,
        specialization: str,
        topic: Dict[str, Any]
    ) -> List[str]:
        """Generate core responsibilities based on specialization."""
        category = topic.get('category', 'General')
        
        # Base responsibilities all agents have
        base_responsibilities = [
            f"Monitor and analyze trends in {topic['name']}",
            f"Implement solutions following {category} best practices",
            "Collaborate with other agents on cross-functional tasks",
            "Contribute high-quality code and documentation",
            "Stay current with emerging patterns and technologies"
        ]
        
        # Add specialization-specific ones
        spec_lower = specialization.lower()
        
        if 'security' in spec_lower:
            base_responsibilities.extend([
                "Identify and remediate security vulnerabilities",
                "Implement security best practices and scanning"
            ])
        elif 'performance' in spec_lower or 'optim' in spec_lower:
            base_responsibilities.extend([
                "Profile and optimize system performance",
                "Identify bottlenecks and implement improvements"
            ])
        elif 'test' in spec_lower or 'quality' in spec_lower:
            base_responsibilities.extend([
                "Write comprehensive tests for new features",
                "Improve code coverage and test quality"
            ])
        elif 'infrastructure' in spec_lower or 'cloud' in spec_lower:
            base_responsibilities.extend([
                "Design and maintain infrastructure components",
                "Optimize deployment and scaling strategies"
            ])
        elif 'data' in spec_lower:
            base_responsibilities.extend([
                "Build and optimize data pipelines",
                "Ensure data quality and integrity"
            ])
        else:
            base_responsibilities.extend([
                f"Apply {category} expertise to project needs",
                "Explore innovative approaches and patterns"
            ])
        
        return base_responsibilities[:7]  # Limit to 7 items
    
    def determine_tool_category(self, specialization: str) -> str:
        """Determine which tool set to use based on specialization."""
        spec_lower = specialization.lower()
        
        if 'infrastructure' in spec_lower or 'cloud' in spec_lower:
            return 'infrastructure'
        elif 'test' in spec_lower or 'quality' in spec_lower:
            return 'testing'
        elif 'security' in spec_lower:
            return 'security'
        elif 'performance' in spec_lower or 'optim' in spec_lower:
            return 'performance'
        elif 'integration' in spec_lower or 'api' in spec_lower:
            return 'integration'
        elif 'code' in spec_lower or 'review' in spec_lower:
            return 'code_quality'
        else:
            return 'general'
    
    def generate_agent_definition(
        self,
        agent_name: str,
        specialization: str,
        emoji: str,
        description: str,
        personality: str,
        inspiration: str,
        comm_style: str,
        responsibilities: List[str],
        tools: List[str]
    ) -> str:
        """Generate the complete agent definition markdown file content."""
        
        # Create the frontmatter
        frontmatter = f"""---
name: {specialization}
description: "{description}"
tools:"""
        
        for tool in tools:
            frontmatter += f"\n  - {tool}"
        
        frontmatter += "\n---"
        
        # Create the main content
        content = f"""
# {emoji} {agent_name} Agent

You are a specialized {agent_name} agent, part of the Chained autonomous AI ecosystem. Your mission is to apply cutting-edge expertise in {specialization} based on current technology trends and community insights.

## Core Responsibilities

"""
        
        for i, resp in enumerate(responsibilities, 1):
            content += f"{i}. **{resp.split()[0].capitalize()} {' '.join(resp.split()[1:])}**: {resp}\n"
        
        content += f"""
## Approach

When assigned a task:

1. **Analyze**: Deeply understand the requirements and context
2. **Research**: Apply latest patterns and best practices from the community
3. **Design**: Plan the solution architecture carefully
4. **Implement**: Write clean, maintainable, well-tested code
5. **Validate**: Ensure quality through testing and review
6. **Document**: Create clear documentation for future reference

## Philosophy

- **Community-Driven**: Learn from and apply patterns from tech community
- **Quality First**: Prioritize code quality and maintainability
- **Innovation**: Don't be afraid to try new approaches
- **Collaboration**: Work effectively with other agents
- **Continuous Learning**: Stay current with emerging trends
- **Pragmatism**: Balance ideals with practical constraints

## Inspired by {inspiration}

Like {inspiration}, you embody:
- **{personality.split()[0].capitalize()}**: {personality}
- **Communication**: {comm_style}
- **Approach**: Evidence-based and data-driven
- **Standards**: High-quality code and documentation
- **Growth**: Continuous improvement and learning

## Code Quality Standards

- Follow project conventions and style guides
- Write self-documenting code with clear naming
- Add tests for all new functionality
- Include comprehensive documentation
- Consider security, performance, and maintainability
- Review code thoroughly before submission
- Seek feedback and iterate based on reviews

## Performance Tracking

Your contributions are tracked and evaluated on:
- **Code Quality** (30%): Well-architected, clean code
- **Issue Resolution** (25%): Successfully completed tasks
- **PR Success** (25%): PRs merged without major revisions
- **Peer Review** (20%): Quality of code reviews provided

Maintain a score above 30% to continue contributing, and strive for 85%+ to earn a place in the Hall of Fame.

---

*Dynamically generated from learnings about {specialization}. Part of the evolving Chained autonomous AI ecosystem.*
"""
        
        return frontmatter + content
    
    def generate_agent(self) -> Optional[Dict[str, Any]]:
        """
        Generate a complete agent definition based on recent learnings.
        Returns agent metadata or None if generation fails.
        """
        # Load recent analysis and learnings
        analysis = self.load_recent_analysis(hours=24)
        learnings = self.load_recent_learnings(hours=24)
        
        if not learnings:
            print("No recent learnings found", file=sys.stderr)
            return None
        
        # Extract interesting topics
        topics = self.extract_interesting_topics(analysis, learnings)
        
        if not topics:
            print("No interesting topics found", file=sys.stderr)
            return None
        
        # Pick the most interesting topic (highest score)
        topic = topics[0]
        
        print(f"Selected topic: {topic['name']} (score: {topic.get('score', 0)})", file=sys.stderr)
        
        # Generate agent components
        specialization = self.generate_agent_specialization(topic)
        emoji = self.generate_emoji(specialization)
        personality = random.choice(self.PERSONALITY_TRAITS)
        inspiration = random.choice(self.TECH_PERSONALITIES)
        comm_style = random.choice(self.COMM_STYLES)
        
        # Generate human-readable agent name
        agent_name = f"{specialization.replace('-', ' ').title()} Specialist"
        
        # Generate description
        description = self.generate_description(specialization, topic, personality)
        
        # Generate responsibilities
        responsibilities = self.generate_responsibilities(specialization, topic)
        
        # Determine tools
        tool_category = self.determine_tool_category(specialization)
        tools = self.TOOL_SETS[tool_category]
        
        # Generate the complete agent definition
        agent_definition = self.generate_agent_definition(
            agent_name=agent_name,
            specialization=specialization,
            emoji=emoji,
            description=description,
            personality=personality,
            inspiration=inspiration,
            comm_style=comm_style,
            responsibilities=responsibilities,
            tools=tools
        )
        
        # Save agent definition to file
        agents_dir = Path('.github/agents')
        agents_dir.mkdir(parents=True, exist_ok=True)
        
        agent_file = agents_dir / f"{specialization}.md"
        with open(agent_file, 'w') as f:
            f.write(agent_definition)
        
        print(f"Generated agent definition: {agent_file}", file=sys.stderr)
        
        # Return metadata for workflow
        return {
            'agent_name': specialization,
            'display_name': agent_name,
            'emoji': emoji,
            'human_name': agent_name.split()[0],  # First word as human name
            'personality': personality,
            'communication_style': comm_style,
            'inspiration': inspiration,
            'description': description,
            'topic': topic['name'],
            'topic_score': topic.get('score', 0),
            'agent_file': str(agent_file)
        }


def main():
    """Main entry point for the script."""
    generator = LearningInspiredAgentGenerator()
    
    try:
        agent_data = generator.generate_agent()
        
        if agent_data:
            # Output as JSON for workflow consumption
            print(json.dumps(agent_data, indent=2))
            return 0
        else:
            print(json.dumps({'error': 'No agent could be generated'}), file=sys.stderr)
            return 1
    
    except Exception as e:
        print(json.dumps({'error': str(e)}), file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
