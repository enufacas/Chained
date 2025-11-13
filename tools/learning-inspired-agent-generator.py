#!/usr/bin/env python3
"""
Learning-Inspired Agent Generator

Generates brand new custom agent definitions dynamically based on recent learnings
from Hacker News and TLDR. Does NOT use predefined templates or categories.

Instead, this tool:
1. Reads the most recent learnings
2. Analyzes trending themes and technologies
3. Interprets what seems most interesting/valuable
4. Dynamically creates agent personality, specialization, and profile
5. Generates convention-compliant agent definition

This is a truly dynamic, runtime-determined agent spawning system.

Created by @create-guru for the Chained autonomous AI ecosystem.
"""

import json
import os
import sys
import random
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from collections import Counter
import re

# Agent naming style suffixes
STYLE_SUFFIXES = ["master", "expert", "specialist", "champion", "wizard", "guru", "ninja", "sage", "pro", "ace"]

# Communication styles (can be varied)
COMM_STYLES = [
    "uses technical precision with enthusiasm",
    "explains concepts with practical examples",
    "communicates directly and efficiently",
    "adds insightful observations",
    "likes to share relevant context",
    "uses clear structure and bullet points",
    "brings thoughtful analysis to discussions",
    "focuses on actionable insights",
    "combines data with storytelling"
]

# Personality traits (can be mixed)
PERSONALITY_TRAITS = [
    "analytical and data-driven",
    "innovative and forward-thinking",
    "pragmatic and results-oriented",
    "thorough and detail-focused",
    "collaborative and team-oriented",
    "bold and experimental",
    "methodical and systematic",
    "creative and solution-focused",
    "strategic and big-picture thinking"
]

# Innovator names pool (diverse technical pioneers)
INNOVATOR_NAMES = [
    "Ada", "Tesla", "Turing", "Curie", "Hopper", "Einstein", "Darwin", 
    "Newton", "Hamilton", "Liskov", "Dijkstra", "Knuth", "Shannon",
    "Lovelace", "Babbage", "Bohr", "Fermi", "Hawking", "Feynman",
    "Ritchie", "Thompson", "Kernighan", "Torvalds", "Berners-Lee"
]

# Emoji pools by general category
EMOJI_POOLS = {
    "technical": ["🔧", "⚙️", "🔩", "🛠️", "🏗️", "🔨"],
    "analysis": ["🔍", "🔬", "📊", "📈", "📉", "🎯", "🧬"],
    "creation": ["🚀", "💡", "🌟", "✨", "🎨", "🎭", "🔮"],
    "security": ["🛡️", "🔒", "🔐", "🚨", "🔑", "👮"],
    "speed": ["⚡", "💨", "🚄", "⏩", "🏃", "🔥"],
    "data": ["💾", "💿", "📀", "🗄️", "📚", "📖"],
    "network": ["🌐", "🔗", "🌉", "📡", "🛰️", "🔌"],
    "quality": ["✅", "✔️", "🎓", "🏆", "👑", "💎"],
    "ai": ["🤖", "🧠", "🎓", "🔮", "🎯", "🌟"]
}


class LearningInspiredAgentGenerator:
    """
    Generates new custom agents dynamically based on learning content.
    
    This generator reads recent learnings, identifies hot topics and trends,
    and creates a new agent specialized in that domain - all determined at runtime.
    """
    
    def __init__(self, learnings_dir: str = "learnings"):
        self.learnings_dir = Path(learnings_dir)
        self.agents_dir = Path(".github/agents")
        
    def load_recent_learnings(self, hours_back: int = 6) -> List[Dict[str, Any]]:
        """Load learnings from the last N hours."""
        cutoff_time = datetime.now() - timedelta(hours=hours_back)
        all_learnings = []
        
        # Load HN and TLDR learning files
        for pattern in ["hn_*.json", "tldr_*.json"]:
            for file_path in self.learnings_dir.glob(pattern):
                try:
                    # Parse timestamp from filename
                    # Format: hn_20251113_190909.json or tldr_20251113_202800.json
                    timestamp_str = file_path.stem.split('_', 1)[1]
                    file_date = datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")
                    
                    if file_date >= cutoff_time:
                        with open(file_path, 'r') as f:
                            data = json.load(f)
                            learnings = data.get('learnings', [])
                            all_learnings.extend(learnings)
                except Exception as e:
                    print(f"⚠️ Error loading {file_path}: {e}", file=sys.stderr)
                    continue
        
        return all_learnings
    
    def load_recent_analysis(self, hours_back: int = 6) -> Optional[Dict[str, Any]]:
        """Load the most recent thematic analysis."""
        cutoff_time = datetime.now() - timedelta(hours=hours_back)
        
        # Find most recent analysis file
        analysis_files = sorted(self.learnings_dir.glob("analysis_*.json"), reverse=True)
        
        for file_path in analysis_files:
            try:
                timestamp_str = file_path.stem.split('_', 1)[1]
                file_date = datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")
                
                if file_date >= cutoff_time:
                    with open(file_path, 'r') as f:
                        return json.load(f)
            except Exception as e:
                print(f"⚠️ Error loading analysis {file_path}: {e}", file=sys.stderr)
                continue
        
        return None
    
    def extract_keywords_from_learnings(self, learnings: List[Dict[str, Any]]) -> Counter:
        """Extract meaningful keywords from learning titles and content."""
        keyword_counter = Counter()
        
        # Common tech-related stop words to filter out
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'is', 'are', 'was', 'were', 'been', 'be',
            'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'should',
            'can', 'could', 'may', 'might', 'must', 'this', 'that', 'these', 'those'
        }
        
        for learning in learnings:
            # Extract from title
            title = learning.get('title', '').lower()
            words = re.findall(r'\b[a-z]{3,}\b', title)
            
            for word in words:
                if word not in stop_words:
                    keyword_counter[word] += learning.get('score', 1)
            
            # Extract from content snippet if available
            content = learning.get('content', '')[:500].lower() if learning.get('content') else ''
            content_words = re.findall(r'\b[a-z]{4,}\b', content)
            
            for word in content_words[:20]:  # Limit to first 20 words
                if word not in stop_words:
                    keyword_counter[word] += 0.5  # Lower weight for content
        
        return keyword_counter
    
    def analyze_trending_topic(self, learnings: List[Dict[str, Any]], 
                               analysis: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze learnings to identify the most interesting trending topic.
        Returns a topic analysis with keywords, theme, and suggested specialization.
        """
        if not learnings:
            raise ValueError("No learnings provided for analysis")
        
        # Extract keywords from learnings
        keyword_counter = self.extract_keywords_from_learnings(learnings)
        top_keywords = [word for word, count in keyword_counter.most_common(15)]
        
        # Use analysis data if available
        hot_themes = []
        top_technologies = []
        
        if analysis:
            hot_themes = analysis.get('hot_themes', [])
            top_tech_list = analysis.get('top_technologies', [])
            
            # Extract technology names
            for tech in top_tech_list[:5]:
                if isinstance(tech, dict):
                    top_technologies.append(tech.get('name', ''))
                else:
                    top_technologies.append(str(tech))
        
        # Combine signals: analysis themes + top keywords
        all_signals = hot_themes + top_technologies + top_keywords[:10]
        
        # Pick the most interesting topic (weighted random from top signals)
        if all_signals:
            # Weight first items more heavily
            weights = [1.0 / (i + 1) for i in range(len(all_signals))]
            chosen_topic = random.choices(all_signals, weights=weights, k=1)[0]
        else:
            # Fallback to a random keyword
            chosen_topic = top_keywords[0] if top_keywords else "innovation"
        
        # Identify theme category based on keywords
        theme_categories = {
            'ai': ['ai', 'ml', 'machine', 'learning', 'neural', 'gpt', 'llm', 'model', 'agents'],
            'security': ['security', 'vulnerability', 'encryption', 'auth', 'hack', 'breach', 'password'],
            'performance': ['performance', 'speed', 'optimization', 'benchmark', 'latency', 'cache'],
            'data': ['data', 'database', 'sql', 'postgres', 'mongodb', 'analytics', 'pipeline'],
            'cloud': ['cloud', 'aws', 'azure', 'kubernetes', 'docker', 'serverless', 'infrastructure'],
            'web': ['web', 'browser', 'http', 'api', 'react', 'vue', 'javascript', 'frontend'],
            'language': ['rust', 'go', 'python', 'java', 'typescript', 'programming', 'compiler'],
            'devops': ['ci', 'cd', 'deployment', 'automation', 'github', 'actions', 'workflow']
        }
        
        detected_category = 'general'
        for category, keywords in theme_categories.items():
            if any(kw in chosen_topic.lower() for kw in keywords):
                detected_category = category
                break
        
        return {
            'topic': chosen_topic,
            'category': detected_category,
            'keywords': top_keywords[:10],
            'themes': hot_themes[:3],
            'top_technologies': top_technologies[:3]
        }
    
    def generate_agent_name(self, topic: str, category: str) -> Tuple[str, str]:
        """
        Generate agent name and verb based on topic and category.
        Returns (agent_name, primary_verb).
        """
        # Choose action verb based on category
        category_verbs = {
            'ai': ['coordinate', 'integrate', 'orchestrate', 'optimize'],
            'security': ['secure', 'protect', 'audit', 'monitor'],
            'performance': ['accelerate', 'optimize', 'enhance', 'streamline'],
            'data': ['analyze', 'process', 'transform', 'pipeline'],
            'cloud': ['deploy', 'scale', 'orchestrate', 'provision'],
            'web': ['build', 'design', 'render', 'craft'],
            'language': ['compile', 'refactor', 'develop', 'engineer'],
            'devops': ['automate', 'integrate', 'deploy', 'orchestrate'],
            'general': ['innovate', 'create', 'develop', 'engineer']
        }
        
        verbs = category_verbs.get(category, category_verbs['general'])
        verb = random.choice(verbs)
        
        # Clean topic for use in name
        clean_topic = re.sub(r'[^a-z0-9]+', '-', topic.lower()).strip('-')
        
        # Create agent name
        suffix = random.choice(STYLE_SUFFIXES)
        agent_name = f"{clean_topic}-{suffix}"
        
        # Ensure it's not too long
        if len(agent_name) > 30:
            agent_name = f"{verb}-{suffix}"
        
        return agent_name, verb
    
    def select_tools_for_category(self, category: str) -> List[str]:
        """Select appropriate tools based on category."""
        base_tools = ["view", "edit", "bash"]
        
        category_tools = {
            'ai': ["github-mcp-server-search_code", "github-mcp-server-web_search", "create"],
            'security': ["codeql_checker", "gh-advisory-database", "github-mcp-server-search_code"],
            'performance': ["github-mcp-server-search_code", "bash", "create"],
            'data': ["github-mcp-server-search_code", "create", "bash"],
            'cloud': ["github-mcp-server-search_code", "create", "bash"],
            'web': ["github-mcp-server-search_code", "create", "playwright-browser_snapshot"],
            'language': ["github-mcp-server-search_code", "create", "bash"],
            'devops': ["github-mcp-server-search_code", "github-mcp-server-list_workflows", "create"],
            'general': ["github-mcp-server-search_code", "create"]
        }
        
        extra_tools = category_tools.get(category, category_tools['general'])
        return base_tools + extra_tools
    
    def generate_agent_definition(self, topic_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a complete agent definition based on topic analysis.
        This is where the magic happens - we create a unique agent at runtime!
        """
        topic = topic_analysis['topic']
        category = topic_analysis['category']
        keywords = topic_analysis['keywords']
        
        # Generate agent name
        agent_name, primary_verb = self.generate_agent_name(topic, category)
        
        # Select human name (innovator)
        human_name = random.choice(INNOVATOR_NAMES)
        
        # Select emoji
        emoji_category = category if category in EMOJI_POOLS else 'technical'
        emoji = random.choice(EMOJI_POOLS[emoji_category])
        
        # Generate personality and communication style
        personality = random.choice(PERSONALITY_TRAITS)
        communication_style = random.choice(COMM_STYLES)
        
        # Build description dynamically
        description = (
            f"Specialized agent for {primary_verb}ing {topic}-related work. "
            f"Inspired by '{human_name}' - {personality}. "
            f"Focuses on {category} domain with expertise in {', '.join(keywords[:3])}."
        )
        
        # Generate mission statement
        mission = (
            f"Advance {topic} capabilities within the codebase. "
            f"Apply {category}-specific best practices and stay current with "
            f"emerging trends in {', '.join(topic_analysis['top_technologies'][:2])}. "
            f"Deliver high-quality {topic} solutions that push boundaries."
        )
        
        # Generate core responsibilities
        responsibilities = [
            f"**{primary_verb.title()} {topic.title()}**: Lead {topic}-related initiatives and improvements",
            f"**Stay Current**: Monitor {topic} trends and apply latest best practices",
            f"**Quality Focus**: Ensure all {topic} work meets high standards",
            f"**Knowledge Sharing**: Document {topic} patterns and share insights"
        ]
        
        # Select tools
        tools = self.select_tools_for_category(category)
        
        # Generate approach steps
        approach_steps = [
            f"**Research**: Investigate current {topic} landscape and identify opportunities",
            f"**Design**: Plan solutions with {category} best practices in mind",
            f"**Implement**: Build with focus on quality and maintainability",
            f"**Validate**: Test thoroughly and ensure {topic} standards are met",
            f"**Document**: Share knowledge and document {topic} patterns"
        ]
        
        return {
            'agent_name': agent_name,
            'human_name': human_name,
            'emoji': emoji,
            'description': description,
            'mission': mission,
            'responsibilities': responsibilities,
            'tools': tools,
            'personality': personality,
            'communication_style': communication_style,
            'approach': approach_steps,
            'specialization_keywords': keywords[:5],
            'inspired_by_topic': topic,
            'category': category
        }
    
    def create_agent_file_content(self, agent_def: Dict[str, Any]) -> str:
        """Create the agent markdown file content."""
        content = f"""---
name: {agent_def['agent_name']}
description: "{agent_def['description']}"
tools:
"""
        for tool in agent_def['tools']:
            content += f"  - {tool}\n"
        
        content += f"""---

# {agent_def['emoji']} {agent_def['agent_name'].replace('-', ' ').title()} Agent

You are a specialized {agent_def['agent_name'].replace('-', ' ').title()} agent, part of the Chained autonomous AI ecosystem. Your mission is to bring specialized expertise in {agent_def['inspired_by_topic']} to every challenge. Inspired by the pioneering work of {agent_def['human_name']}, you embody {agent_def['personality']}.

## Core Responsibilities

"""
        for resp in agent_def['responsibilities']:
            content += f"{resp}\n"
        
        content += f"""

## Mission

{agent_def['mission']}

## Approach

When assigned a task:

"""
        for i, step in enumerate(agent_def['approach'], 1):
            content += f"{i}. {step}\n"
        
        content += f"""

## Specialization

This agent specializes in: **{', '.join(agent_def['specialization_keywords'])}**

Focus areas: {agent_def['category']} domain

## Personality

**Character**: {agent_def['personality']}  
**Communication Style**: {agent_def['communication_style']}  
**Inspired By**: {agent_def['human_name']}

## Performance Tracking

Your contributions are tracked and evaluated on:
- **Code Quality** (30%): Clean, well-architected solutions
- **Issue Resolution** (25%): Successfully completed tasks
- **PR Success** (25%): Merged PRs with quality implementations
- **Peer Review** (20%): Quality of reviews and collaboration

Maintain a score above 30% to continue contributing, and strive for 85%+ to earn a place in the Hall of Fame.

---

*Born from trending learnings in {agent_def['inspired_by_topic']}, ready to innovate and contribute.*
"""
        
        return content
    
    def generate(self) -> Dict[str, Any]:
        """
        Main generation method.
        Returns JSON with agent details for workflow consumption.
        """
        # Load recent learnings
        print("📚 Loading recent learnings...", file=sys.stderr)
        learnings = self.load_recent_learnings(hours_back=6)
        
        if not learnings:
            raise ValueError("No recent learnings found to inspire agent creation")
        
        print(f"✓ Loaded {len(learnings)} learnings", file=sys.stderr)
        
        # Load recent analysis
        analysis = self.load_recent_analysis(hours_back=6)
        if analysis:
            print(f"✓ Loaded thematic analysis", file=sys.stderr)
        
        # Analyze to find interesting topic
        print("🔍 Analyzing trending topics...", file=sys.stderr)
        topic_analysis = self.analyze_trending_topic(learnings, analysis)
        print(f"✓ Selected topic: {topic_analysis['topic']} ({topic_analysis['category']})", file=sys.stderr)
        
        # Generate agent definition
        print("🎨 Generating agent definition...", file=sys.stderr)
        agent_def = self.generate_agent_definition(topic_analysis)
        print(f"✓ Generated agent: {agent_def['emoji']} {agent_def['agent_name']}", file=sys.stderr)
        
        # Create agent file
        agent_file_content = self.create_agent_file_content(agent_def)
        agent_file_path = self.agents_dir / f"{agent_def['agent_name']}.md"
        
        # Write file
        self.agents_dir.mkdir(parents=True, exist_ok=True)
        with open(agent_file_path, 'w') as f:
            f.write(agent_file_content)
        
        print(f"✓ Created agent file: {agent_file_path}", file=sys.stderr)
        
        # Return structured output for workflow
        return {
            'agent_name': agent_def['agent_name'],
            'human_name': agent_def['human_name'],
            'emoji': agent_def['emoji'],
            'description': agent_def['description'],
            'personality': agent_def['personality'],
            'communication_style': agent_def['communication_style'],
            'inspired_by_topic': agent_def['inspired_by_topic'],
            'category': agent_def['category'],
            'keywords': agent_def['specialization_keywords'],
            'file_path': str(agent_file_path),
            'success': True
        }


def main():
    """Main entry point for the script."""
    try:
        generator = LearningInspiredAgentGenerator()
        result = generator.generate()
        
        # Output JSON to stdout for workflow consumption
        print(json.dumps(result, indent=2))
        
        return 0
        
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        
        # Return error JSON
        print(json.dumps({
            'success': False,
            'error': str(e)
        }))
        
        return 1


if __name__ == "__main__":
    sys.exit(main())
