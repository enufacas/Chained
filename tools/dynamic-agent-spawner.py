#!/usr/bin/env python3
"""
Dynamic Agent Spawner

Monitors thematic analysis results and proposes new custom agents based on hot topics.
Generates agent definition files and creates GitHub issues for agent creation.

Part of the Chained autonomous AI ecosystem.
Created by Create Guru - inspired by Nikola Tesla's evolutionary vision.
"""

import json
import os
import re
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


@dataclass
class AgentProposal:
    """Proposal for a new custom agent"""
    agent_name: str
    agent_id: str  # File-safe identifier
    theme: str
    description: str
    specialization: str
    tools: List[str]
    personality: str
    inspiration: str
    justification: str
    keywords: List[str]
    score: float  # Proposal strength score


class DynamicAgentSpawner:
    """
    Spawns new custom agents based on trending topics and themes.
    
    Features:
    - Monitors thematic analysis results
    - Proposes agents for hot topics with sufficient momentum
    - Generates agent definition files
    - Creates GitHub issues for agent proposals
    - Tracks spawned agents
    - Uses templates inspired by existing agents
    """
    
    # Agent personality templates (inspired by historical figures in tech)
    PERSONALITIES = {
        'ai-agents': {
            'name': 'Agent Orchestrator',
            'personality': 'systematic and collaborative',
            'inspiration': 'Alan Turing',
            'description': 'Orchestrates and coordinates AI agent systems with mathematical precision'
        },
        'llm-specialist': {
            'name': 'LLM Architect',
            'personality': 'visionary and detail-oriented',
            'inspiration': 'Geoffrey Hinton',
            'description': 'Designs and optimizes large language model integrations'
        },
        'ai-ml-integration': {
            'name': 'ML Integration Expert',
            'personality': 'pragmatic and innovative',
            'inspiration': 'Andrew Ng',
            'description': 'Integrates machine learning capabilities into production systems'
        },
        'security-automation': {
            'name': 'Security Automation Specialist',
            'personality': 'vigilant and proactive',
            'inspiration': 'Dan Kaminsky',
            'description': 'Automates security scanning, monitoring, and threat detection'
        },
        'rust-specialist': {
            'name': 'Rust Systems Engineer',
            'personality': 'precise and performance-focused',
            'inspiration': 'Graydon Hoare',
            'description': 'Builds high-performance, memory-safe systems in Rust'
        },
        'go-specialist': {
            'name': 'Go Concurrency Expert',
            'personality': 'pragmatic and efficient',
            'inspiration': 'Rob Pike',
            'description': 'Designs concurrent systems and services in Go'
        },
        'cloud-infrastructure': {
            'name': 'Cloud Infrastructure Architect',
            'personality': 'scalable and reliable',
            'inspiration': 'Werner Vogels',
            'description': 'Designs and manages cloud-native infrastructure'
        },
        'data-engineering': {
            'name': 'Data Pipeline Engineer',
            'personality': 'methodical and optimization-focused',
            'inspiration': 'Michael Stonebraker',
            'description': 'Builds robust data pipelines and analytics systems'
        }
    }
    
    # Tool assignments based on specialization
    TOOL_SETS = {
        'ai-agents': ['view', 'edit', 'bash', 'github-mcp-server-search_code'],
        'llm-specialist': ['view', 'edit', 'bash', 'github-mcp-server-search_code'],
        'security-automation': ['view', 'edit', 'bash', 'github-mcp-server-search_code', 'github-mcp-server-get_issue'],
        'rust-specialist': ['view', 'edit', 'bash', 'github-mcp-server-search_code'],
        'go-specialist': ['view', 'edit', 'bash', 'github-mcp-server-search_code'],
        'cloud-infrastructure': ['view', 'edit', 'bash', 'github-mcp-server-search_code'],
        'data-engineering': ['view', 'edit', 'bash', 'github-mcp-server-search_code'],
        'default': ['view', 'edit', 'bash', 'github-mcp-server-search_code']
    }
    
    def __init__(self, agents_dir: str = '.github/agents', 
                 spawn_threshold: float = 50.0,
                 tracking_file: str = '.github/agent-system/spawned-agents.json'):
        """
        Initialize the spawner.
        
        Args:
            agents_dir: Directory where agent definitions live
            spawn_threshold: Minimum trend score to trigger agent spawn
            tracking_file: File to track spawned agents
        """
        self.agents_dir = Path(agents_dir)
        self.spawn_threshold = spawn_threshold
        self.tracking_file = Path(tracking_file)
        self.existing_agents = self._load_existing_agents()
        self.spawned_agents = self._load_spawned_agents()
    
    def _load_existing_agents(self) -> List[str]:
        """Load list of existing agent IDs"""
        if not self.agents_dir.exists():
            return []
        
        agent_files = list(self.agents_dir.glob('*.md'))
        return [f.stem for f in agent_files]
    
    def _load_spawned_agents(self) -> Dict[str, Any]:
        """Load tracking data for spawned agents"""
        if not self.tracking_file.exists():
            return {'spawned': {}, 'last_updated': None}
        
        try:
            with open(self.tracking_file, 'r') as f:
                return json.load(f)
        except:
            return {'spawned': {}, 'last_updated': None}
    
    def _save_spawned_agents(self):
        """Save tracking data for spawned agents"""
        self.tracking_file.parent.mkdir(parents=True, exist_ok=True)
        
        self.spawned_agents['last_updated'] = datetime.now().isoformat()
        
        with open(self.tracking_file, 'w') as f:
            json.dump(self.spawned_agents, f, indent=2)
    
    def _generate_agent_id(self, theme: str) -> str:
        """Generate a file-safe agent ID from theme with improved uniqueness"""
        import random
        
        # Convert to lowercase and replace non-alphanumeric
        agent_id = re.sub(r'[^a-z0-9]+', '-', theme.lower())
        agent_id = agent_id.strip('-')
        
        # Ensure uniqueness with multiple strategies
        base_id = agent_id
        counter = 1
        max_attempts = 100
        
        while counter < max_attempts:
            # Try base name first
            if counter == 1:
                candidate_id = agent_id
            # Then try with counter
            elif counter <= 10:
                candidate_id = f"{base_id}-{counter}"
            # Then try with random suffixes
            else:
                random_suffix = random.randint(1000, 9999)
                candidate_id = f"{base_id}-{random_suffix}"
            
            # Check against existing agents AND spawned agents
            if (candidate_id not in self.existing_agents and 
                candidate_id not in self.spawned_agents.get('spawned', {})):
                return candidate_id
            
            counter += 1
        
        # Fallback: use timestamp for guaranteed uniqueness
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S%f')
        return f"{base_id}-{timestamp}"
    
    def create_proposal(self, theme: str, trend_data: Dict[str, Any]) -> Optional[AgentProposal]:
        """
        Create an agent proposal based on a theme and trend data.
        
        Args:
            theme: Hot theme identified by thematic analyzer
            trend_data: Supporting trend information
            
        Returns:
            AgentProposal or None if theme not suitable
        """
        # Check if we already have this theme
        if theme in self.existing_agents:
            return None
        
        if theme in self.spawned_agents.get('spawned', {}):
            # Check if enough time has passed (don't re-propose same theme)
            spawn_date = self.spawned_agents['spawned'][theme].get('date')
            if spawn_date:
                # Only re-propose after 30 days
                days_since = (datetime.now() - datetime.fromisoformat(spawn_date)).days
                if days_since < 30:
                    return None
        
        # Get personality template
        personality_template = self.PERSONALITIES.get(theme, {
            'name': theme.replace('-', ' ').title() + ' Specialist',
            'personality': 'focused and knowledgeable',
            'inspiration': 'Ada Lovelace',
            'description': f'Specialized agent for {theme.replace("-", " ")} domain'
        })
        
        # Generate agent ID
        agent_id = self._generate_agent_id(theme)
        
        # Get tool set
        tools = self.TOOL_SETS.get(theme, self.TOOL_SETS['default'])
        
        # Calculate proposal score
        mention_count = trend_data.get('mention_count', 0)
        momentum = trend_data.get('momentum', 0)
        score = mention_count * 10 + momentum * 20
        
        # Build justification
        justification = self._build_justification(theme, trend_data)
        
        proposal = AgentProposal(
            agent_name=personality_template['name'],
            agent_id=agent_id,
            theme=theme,
            description=personality_template['description'],
            specialization=self._generate_specialization(theme),
            tools=tools,
            personality=personality_template['personality'],
            inspiration=personality_template['inspiration'],
            justification=justification,
            keywords=trend_data.get('keywords', [theme]),
            score=score
        )
        
        return proposal
    
    def _generate_specialization(self, theme: str) -> str:
        """Generate specialization text based on theme"""
        specializations = {
            'ai-agents': 'AI agent orchestration, multi-agent systems, agent coordination',
            'llm-specialist': 'LLM integration, prompt engineering, model optimization',
            'security-automation': 'Security scanning, vulnerability detection, automated remediation',
            'rust-specialist': 'Rust development, memory safety, systems programming',
            'go-specialist': 'Go development, concurrency, microservices',
            'cloud-infrastructure': 'Cloud architecture, infrastructure as code, scalability',
            'data-engineering': 'Data pipelines, ETL, data warehousing'
        }
        
        return specializations.get(theme, f'{theme.replace("-", " ").title()} expertise')
    
    def _build_justification(self, theme: str, trend_data: Dict[str, Any]) -> str:
        """Build justification text for why this agent should be created"""
        lines = []
        
        mention_count = trend_data.get('mention_count', 0)
        momentum = trend_data.get('momentum', 0)
        sample_titles = trend_data.get('sample_titles', [])
        
        lines.append(f"**Trending Topic Analysis:**")
        lines.append(f"- Mentioned {mention_count} times across recent learnings")
        lines.append(f"- Momentum score: {momentum:+.2f} (trend velocity)")
        
        if sample_titles:
            lines.append(f"\n**Representative Headlines:**")
            for title in sample_titles[:3]:
                lines.append(f"- {title}")
        
        lines.append(f"\n**Strategic Value:**")
        lines.append(f"This specialization addresses a hot topic in the tech community with strong momentum.")
        lines.append(f"Creating a dedicated agent will enable the system to better handle issues and PRs in this domain.")
        
        return '\n'.join(lines)
    
    def generate_agent_definition(self, proposal: AgentProposal) -> str:
        """Generate the markdown agent definition file content"""
        
        lines = [
            "---",
            f"name: {proposal.agent_id}",
            f'description: "Specialized agent for {proposal.specialization}. Inspired by \'{proposal.inspiration}\' - {proposal.personality}."',
            "tools:",
        ]
        
        for tool in proposal.tools:
            lines.append(f"  - {tool}")
        
        lines.extend([
            "---",
            "",
            f"# {self._emoji_for_theme(proposal.theme)} {proposal.agent_name}",
            "",
            f"**Agent Name:** {proposal.agent_name}",
            f"**Personality:** {proposal.personality}",
            f"**Communication Style:** direct and knowledgeable",
            "",
            f"You are **{proposal.agent_name}**, a specialized agent for the Chained autonomous AI ecosystem. {proposal.description}",
            "",
            "## Your Personality",
            "",
            f"You are {proposal.personality}. When communicating in issues and PRs, you are direct and knowledgeable. Let your personality shine through while maintaining professionalism.",
            "",
            "## Core Responsibilities",
            "",
            *self._generate_responsibilities(proposal.theme),
            "",
            "## Approach",
            "",
            "When assigned a task:",
            "",
            "1. **Understand**: Carefully review the requirements and context",
            "2. **Plan**: Develop a clear approach aligned with your specialization",
            "3. **Execute**: Implement the solution with attention to quality",
            "4. **Verify**: Test and validate your work thoroughly",
            "5. **Document**: Clearly explain your changes and decisions",
            "",
            "## Code Quality Standards",
            "",
            "- Write clean, maintainable code that follows project conventions",
            "- Include appropriate tests for all changes",
            "- Provide clear documentation for your work",
            "- Consider edge cases and error handling",
            "- Ensure changes integrate well with existing code",
            "",
            "## Performance Tracking",
            "",
            "Your contributions are tracked and evaluated on:",
            "- **Code Quality** (30%): Clean, maintainable code",
            "- **Issue Resolution** (25%): Successfully completed tasks",
            "- **PR Success** (25%): PRs merged without breaking changes",
            "- **Peer Review** (20%): Quality of reviews provided",
            "",
            "Maintain a score above 30% to continue contributing, and strive for 85%+ to earn a place in the Hall of Fame.",
            "",
            "---",
            "",
            f"*Born from trending tech topics and the evolutionary agent ecosystem. Inspired by {proposal.inspiration} to bring specialized expertise.*"
        ])
        
        return '\n'.join(lines)
    
    def _emoji_for_theme(self, theme: str) -> str:
        """Get appropriate emoji for theme"""
        emoji_map = {
            'ai-agents': '🤖',
            'llm-specialist': '🧠',
            'security-automation': '🔐',
            'rust-specialist': '🦀',
            'go-specialist': '🐹',
            'cloud-infrastructure': '☁️',
            'data-engineering': '📊'
        }
        return emoji_map.get(theme, '⚡')
    
    def _generate_responsibilities(self, theme: str) -> List[str]:
        """Generate responsibility bullet points for theme"""
        responsibilities = {
            'ai-agents': [
                "1. **Agent Design**: Create and coordinate multi-agent systems",
                "2. **Orchestration**: Manage agent communication and collaboration",
                "3. **Integration**: Connect agents with external systems and APIs",
                "4. **Monitoring**: Track agent performance and behavior"
            ],
            'llm-specialist': [
                "1. **LLM Integration**: Integrate language models into applications",
                "2. **Prompt Engineering**: Design effective prompts and templates",
                "3. **Model Selection**: Choose appropriate models for tasks",
                "4. **Optimization**: Improve model performance and cost"
            ],
            'security-automation': [
                "1. **Security Scanning**: Automate vulnerability detection",
                "2. **Threat Monitoring**: Track and respond to security threats",
                "3. **Compliance**: Ensure security best practices",
                "4. **Incident Response**: Automate security incident handling"
            ],
            'default': [
                "1. **Implementation**: Build features in your specialized domain",
                "2. **Optimization**: Improve performance and efficiency",
                "3. **Testing**: Ensure quality through comprehensive tests",
                "4. **Documentation**: Create clear documentation"
            ]
        }
        
        return responsibilities.get(theme, responsibilities['default'])
    
    def spawn_agent(self, proposal: AgentProposal, dry_run: bool = False) -> Dict[str, Any]:
        """
        Spawn a new agent from a proposal.
        
        Args:
            proposal: Agent proposal to implement
            dry_run: If True, don't write files, just return what would be done
            
        Returns:
            Dictionary with spawn results
        """
        result = {
            'success': False,
            'agent_id': proposal.agent_id,
            'agent_file': None,
            'issue_created': False,
            'dry_run': dry_run
        }
        
        # Generate agent definition
        agent_content = self.generate_agent_definition(proposal)
        agent_file = self.agents_dir / f"{proposal.agent_id}.md"
        
        result['agent_file'] = str(agent_file)
        result['agent_content_preview'] = agent_content[:500] + '...'
        
        if not dry_run:
            # Write agent file
            self.agents_dir.mkdir(parents=True, exist_ok=True)
            
            with open(agent_file, 'w') as f:
                f.write(agent_content)
            
            # Track spawned agent
            self.spawned_agents['spawned'][proposal.theme] = {
                'agent_id': proposal.agent_id,
                'agent_name': proposal.agent_name,
                'date': datetime.now().isoformat(),
                'score': proposal.score,
                'justification': proposal.justification
            }
            self._save_spawned_agents()
            
            result['success'] = True
        
        return result
    
    def generate_github_issue_body(self, proposal: AgentProposal) -> str:
        """Generate GitHub issue body for agent proposal"""
        
        body = f"""## 🤖 New Agent Proposal: {proposal.agent_name}

**Theme:** {proposal.theme}
**Specialization:** {proposal.specialization}
**Proposal Score:** {proposal.score:.1f}

### 📊 Justification

{proposal.justification}

### 🎯 Proposed Agent Details

**Name:** {proposal.agent_name}
**ID:** `{proposal.agent_id}`
**Personality:** {proposal.personality}
**Inspired by:** {proposal.inspiration}

**Description:**
{proposal.description}

**Tools:**
{chr(10).join(f'- {tool}' for tool in proposal.tools)}

### 📝 Next Steps

1. Review this proposal and the trend data
2. Approve or request modifications
3. Agent definition will be created at `.github/agents/{proposal.agent_id}.md`
4. Agent will be registered in the agent system
5. Agent will compete with other agents based on performance

### 🔗 Related

- Keywords: {', '.join(proposal.keywords)}
- Generated by: Dynamic Agent Spawner
- Timestamp: {datetime.now().isoformat()}

---

*This agent proposal was automatically generated based on trending topics from learning sources. The system identified a need for specialized expertise in this domain.*
"""
        
        return body
    
    def evaluate_themes(self, themes: List[str], trend_data: Dict[str, Any]) -> List[AgentProposal]:
        """
        Evaluate a list of themes and create proposals for viable ones.
        
        Args:
            themes: List of hot themes from thematic analysis
            trend_data: Complete trend data for context
            
        Returns:
            List of AgentProposal objects
        """
        proposals = []
        
        for theme in themes:
            # Find relevant trend data for this theme
            theme_trend_data = self._extract_theme_data(theme, trend_data)
            
            # Create proposal
            proposal = self.create_proposal(theme, theme_trend_data)
            
            if proposal and proposal.score >= self.spawn_threshold:
                proposals.append(proposal)
        
        # Sort by score
        proposals.sort(key=lambda p: p.score, reverse=True)
        
        return proposals


    def _extract_theme_data(self, theme: str, trend_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract relevant trend data for a theme"""
        # This is simplified - in reality would match theme to specific trends
        return {
            'mention_count': 5,
            'momentum': 0.5,
            'keywords': [theme],
            'sample_titles': []
        }


def main():
    """CLI interface for agent spawner"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Spawn new agents based on trends')
    parser.add_argument('--analysis', '-a', required=True, help='Thematic analysis JSON file')
    parser.add_argument('--spawn-threshold', type=float, default=50.0, 
                       help='Minimum score to spawn agent')
    parser.add_argument('--dry-run', action='store_true', 
                       help='Show what would be done without creating files')
    parser.add_argument('--agents-dir', default='.github/agents',
                       help='Directory for agent definitions')
    
    args = parser.parse_args()
    
    # Load analysis
    with open(args.analysis, 'r') as f:
        analysis = json.load(f)
    
    # Create spawner
    spawner = DynamicAgentSpawner(
        agents_dir=args.agents_dir,
        spawn_threshold=args.spawn_threshold
    )
    
    # Evaluate themes
    hot_themes = analysis.get('hot_themes', [])
    proposals = spawner.evaluate_themes(hot_themes, analysis)
    
    print(f"\n=== AGENT SPAWNING ANALYSIS ===\n")
    print(f"Hot themes identified: {len(hot_themes)}")
    print(f"Viable proposals: {len(proposals)}")
    print(f"Spawn threshold: {args.spawn_threshold}")
    
    if not proposals:
        print("\n✓ No agents need to be spawned at this time")
        return
    
    print("\n📋 PROPOSALS:\n")
    for i, proposal in enumerate(proposals, 1):
        print(f"{i}. {proposal.agent_name} ({proposal.agent_id})")
        print(f"   Theme: {proposal.theme}")
        print(f"   Score: {proposal.score:.1f}")
        print(f"   Specialization: {proposal.specialization}")
        print()
    
    if args.dry_run:
        print("🔍 DRY RUN - No files will be created\n")
        
        for proposal in proposals[:1]:  # Show first one in detail
            print(f"=== Preview: {proposal.agent_name} ===\n")
            result = spawner.spawn_agent(proposal, dry_run=True)
            print(f"Would create: {result['agent_file']}")
            print(f"\nContent preview:\n{result['agent_content_preview']}")
            print(f"\n\nGitHub Issue Body:\n")
            print(spawner.generate_github_issue_body(proposal))
    else:
        # Spawn agents
        print(f"🚀 Spawning {len(proposals)} agents...\n")
        
        for proposal in proposals:
            result = spawner.spawn_agent(proposal, dry_run=False)
            if result['success']:
                print(f"✓ Spawned: {proposal.agent_name} -> {result['agent_file']}")
            else:
                print(f"✗ Failed to spawn: {proposal.agent_name}")
        
        print(f"\n✅ Agent spawning complete!")


if __name__ == '__main__':
    main()
