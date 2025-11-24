#!/usr/bin/env python3
"""
Contextual Prompt Adapter

Adapts prompts based on agent specialization, issue context, and repository state.
Enhances base prompts with agent-specific guidance and contextual information.

Part of the self-improving prompt generator system.
Created by @create-guru - infrastructure creation inspired by Nikola Tesla.
"""

import json
import os
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class AgentProfile:
    """Agent specialization profile"""
    name: str
    specialization: str
    personality: str
    strengths: List[str]
    approach: str


class ContextualPromptAdapter:
    """
    Adapts prompts based on context to maximize effectiveness.
    
    Context factors:
    - Agent specialization and personality
    - Issue labels and keywords
    - Recent repository activity
    - Historical success patterns
    - Time of day / urgency
    """
    
    def __init__(self, agents_dir: str = ".github/agents"):
        """Initialize the adapter"""
        self.agents_dir = Path(agents_dir)
        self.agent_profiles = {}
        self._load_agent_profiles()
    
    def _load_agent_profiles(self):
        """Load agent profiles from agent definitions"""
        if not self.agents_dir.exists():
            return
        
        for agent_file in self.agents_dir.glob("*.md"):
            try:
                profile = self._parse_agent_file(agent_file)
                if profile:
                    self.agent_profiles[profile.name] = profile
            except Exception as e:
                print(f"Warning: Could not parse {agent_file}: {e}")
    
    def _parse_agent_file(self, agent_file: Path) -> Optional[AgentProfile]:
        """Parse agent markdown file to extract profile"""
        with open(agent_file, 'r') as f:
            content = f.read()
        
        # Extract frontmatter
        frontmatter_match = re.search(r'^---\n(.*?)\n---', content, re.DOTALL)
        if not frontmatter_match:
            return None
        
        frontmatter = frontmatter_match.group(1)
        
        # Parse key fields
        name_match = re.search(r'^name:\s*(.+)$', frontmatter, re.MULTILINE)
        desc_match = re.search(r'^description:\s*["\'](.+)["\']$', frontmatter, re.MULTILINE)
        
        if not name_match:
            return None
        
        name = name_match.group(1).strip()
        description = desc_match.group(1) if desc_match else ""
        
        # Extract specialization from description
        specialization = ""
        if "Specialized agent for" in description:
            specialization = description.split("Specialized agent for")[1].split(".")[0].strip()
        
        # Extract personality
        personality = ""
        if "Inspired by" in description:
            personality = description.split("Inspired by")[1].split("-")[0].strip().strip("'\"")
        
        # Extract approach/traits from description
        approach = ""
        if "-" in description:
            parts = description.split("-")
            if len(parts) > 1:
                approach = parts[-1].strip().rstrip(".")
        
        # Parse strengths from content
        strengths = []
        strengths_section = re.search(
            r'##\s+(?:Core Responsibilities|Responsibilities|Specializations)(.*?)(?=##|\Z)',
            content,
            re.DOTALL | re.IGNORECASE
        )
        if strengths_section:
            section_text = strengths_section.group(1)
            # Extract bullet points
            bullets = re.findall(r'[-*]\s*\*?\*?([^:\n]+)', section_text)
            strengths = [b.strip().strip('*').strip() for b in bullets if len(b.strip()) > 5][:5]
        
        return AgentProfile(
            name=name,
            specialization=specialization,
            personality=personality,
            strengths=strengths,
            approach=approach
        )
    
    def adapt_prompt_for_agent(
        self,
        base_prompt: str,
        agent_name: str,
        issue_context: Optional[Dict] = None
    ) -> str:
        """
        Adapt a prompt for a specific agent.
        
        Args:
            base_prompt: The base prompt template
            agent_name: The agent to adapt for
            issue_context: Optional issue context (labels, keywords, etc.)
            
        Returns:
            Enhanced prompt adapted for the agent
        """
        agent = self.agent_profiles.get(agent_name)
        if not agent:
            # Unknown agent, return base prompt
            return base_prompt
        
        # Build adaptation sections
        adaptations = []
        
        # Add personality-appropriate guidance
        personality_guidance = self._get_personality_guidance(agent)
        if personality_guidance:
            adaptations.append(personality_guidance)
        
        # Add specialization-specific tips
        specialization_tips = self._get_specialization_tips(agent, issue_context)
        if specialization_tips:
            adaptations.append(specialization_tips)
        
        # Add contextual warnings/notes
        contextual_notes = self._get_contextual_notes(agent, issue_context)
        if contextual_notes:
            adaptations.append(contextual_notes)
        
        # Combine adaptations with base prompt
        if adaptations:
            adaptation_section = "\n\n" + "\n\n".join(adaptations)
            adapted_prompt = base_prompt + adaptation_section
        else:
            adapted_prompt = base_prompt
        
        return adapted_prompt
    
    def _get_personality_guidance(self, agent: AgentProfile) -> str:
        """Generate personality-appropriate guidance"""
        if not agent.personality:
            return ""
        
        personality_lower = agent.personality.lower()
        
        # Map personalities to guidance styles
        guidance_map = {
            'nikola tesla': """**Visionary Approach (@{name}):**
As you embody Tesla's inventive spirit, approach this with:
- Bold, innovative solutions that look beyond the obvious
- Elegant architecture that balances power with simplicity
- Creative problem-solving that challenges conventional limits""",
            
            'grace hopper': """**Pragmatic Pioneer (@{name}):**
Channel Grace Hopper's practical innovation:
- Focus on solutions that work reliably in the real world
- Pioneer new approaches while maintaining accessibility
- Build tools that amplify human capability""",
            
            'margaret hamilton': """**Mission-Critical Rigor (@{name}):**
Apply Margaret Hamilton's systematic excellence:
- Rigorous verification at every step
- Defensive programming and error handling
- Documentation of all critical decisions""",
            
            'edsger dijkstra': """**Elegant Efficiency (@{name}):**
Follow Dijkstra's principles of algorithmic elegance:
- Seek the most efficient solution path
- Prove correctness through clear reasoning
- Value simplicity and mathematical beauty""",
            
            'rich hickey': """**Thoughtful Design (@{name}):**
Apply Rich Hickey's deliberate approach:
- Consider the problem deeply before coding
- Design for simplicity and composability
- Think about long-term implications""",
            
            'alan turing': """**Systematic Collaboration (@{name}):**
Embody Turing's methodical brilliance:
- Break complex problems into logical components
- Test hypotheses rigorously
- Coordinate multiple aspects harmoniously"""
        }
        
        for key, guidance in guidance_map.items():
            if key in personality_lower:
                return guidance.replace('{name}', agent.name)
        
        return ""
    
    def _get_specialization_tips(
        self,
        agent: AgentProfile,
        issue_context: Optional[Dict]
    ) -> str:
        """Generate specialization-specific tips"""
        if not agent.specialization:
            return ""
        
        spec_lower = agent.specialization.lower()
        tips = []
        
        # Infrastructure/Tools specialization
        if any(word in spec_lower for word in ['infrastructure', 'tools', 'building', 'creating']):
            tips.extend([
                "Consider scalability and future extensibility",
                "Design for reusability across the codebase",
                "Think about developer experience and usability"
            ])
        
        # Performance/Optimization specialization  
        if any(word in spec_lower for word in ['performance', 'optimization', 'efficiency', 'accelerat']):
            tips.extend([
                "Profile before optimizing to find real bottlenecks",
                "Measure the impact of each optimization",
                "Balance performance with code maintainability"
            ])
        
        # Testing/Quality specialization
        if any(word in spec_lower for word in ['test', 'quality', 'assert', 'validat']):
            tips.extend([
                "Cover edge cases and boundary conditions",
                "Write tests that document expected behavior",
                "Consider both positive and negative test cases"
            ])
        
        # Security specialization
        if any(word in spec_lower for word in ['security', 'guard', 'protect', 'secur']):
            tips.extend([
                "Assume all input is potentially malicious",
                "Follow principle of least privilege",
                "Document security assumptions explicitly"
            ])
        
        # Refactoring/Organization specialization
        if any(word in spec_lower for word in ['refactor', 'organiz', 'clean', 'restructur']):
            tips.extend([
                "Preserve existing behavior - tests must pass",
                "Make incremental, verifiable changes",
                "Improve readability without over-engineering"
            ])
        
        # Documentation specialization
        if any(word in spec_lower for word in ['document', 'clarify', 'teach', 'communicat']):
            tips.extend([
                "Use clear examples to illustrate concepts",
                "Structure content for easy scanning",
                "Keep audience needs central"
            ])
        
        # Code Review/Coaching specialization
        if any(word in spec_lower for word in ['review', 'coach', 'mentor', 'guide']):
            tips.extend([
                "Focus feedback on teaching, not just finding issues",
                "Explain the reasoning behind suggestions",
                "Acknowledge what's done well"
            ])
        
        # Investigation/Analysis specialization
        if any(word in spec_lower for word in ['investigat', 'analyz', 'examin', 'inspect']):
            tips.extend([
                "Gather comprehensive data before forming conclusions",
                "Look for patterns across multiple data points",
                "Document your investigative process"
            ])
        
        if not tips:
            return ""
        
        # Add context-based prioritization
        if issue_context:
            labels = issue_context.get('labels', [])
            if 'urgent' in labels or 'critical' in labels:
                tips.insert(0, "⚠️ URGENT: Prioritize speed while maintaining quality")
            if 'breaking' in labels:
                tips.insert(0, "⚠️ BREAKING: Extra caution - this affects existing functionality")
        
        tips_section = f"**Specialization Tips (@{agent.name} - {agent.specialization}):**\n"
        for tip in tips[:4]:  # Limit to top 4 tips
            tips_section += f"- {tip}\n"
        
        return tips_section.rstrip()
    
    def _get_contextual_notes(
        self,
        agent: AgentProfile,
        issue_context: Optional[Dict]
    ) -> str:
        """Generate contextual notes based on issue context"""
        if not issue_context:
            return ""
        
        notes = []
        
        labels = issue_context.get('labels', [])
        keywords = issue_context.get('keywords', [])
        
        # Complexity warnings
        if 'complex' in labels or any(k in keywords for k in ['architecture', 'refactor', 'redesign']):
            notes.append("⚠️ Complex issue: Break into smaller steps, document assumptions")
        
        # Dependency notes
        if 'dependencies' in labels or any(k in keywords for k in ['dependency', 'library', 'package']):
            notes.append("📦 Dependencies: Check for security vulnerabilities and license compatibility")
        
        # Performance notes
        if 'performance' in labels or any(k in keywords for k in ['slow', 'optimize', 'performance']):
            notes.append("⚡ Performance: Establish baseline metrics before and after changes")
        
        # Documentation notes
        if 'documentation' in labels:
            notes.append("📝 Documentation: Ensure examples are tested and work correctly")
        
        # Breaking change warnings
        if 'breaking' in labels or 'breaking change' in keywords:
            notes.append("⚠️ BREAKING: Document migration path and update changelog")
        
        # First-time contributor notes
        if 'good first issue' in labels:
            notes.append("👋 Good First Issue: Be extra clear and welcoming in communication")
        
        if not notes:
            return ""
        
        notes_section = "**Contextual Notes:**\n"
        for note in notes:
            notes_section += f"- {note}\n"
        
        return notes_section.rstrip()
    
    def enhance_prompt_with_context(
        self,
        base_prompt: str,
        agent_name: str,
        issue_title: str = "",
        issue_labels: List[str] = None,
        issue_body: str = ""
    ) -> str:
        """
        Enhance a prompt with full contextual adaptation.
        
        Args:
            base_prompt: The base prompt template
            agent_name: The agent to use
            issue_title: Issue title for keyword extraction
            issue_labels: Issue labels for context
            issue_body: Issue body for keyword extraction
            
        Returns:
            Fully contextualized prompt
        """
        # Extract keywords from title and body
        keywords = []
        text = (issue_title + " " + issue_body).lower()
        
        # Extract key technical terms
        tech_keywords = [
            'api', 'database', 'security', 'performance', 'test', 'bug',
            'feature', 'refactor', 'documentation', 'integration', 'deploy',
            'architecture', 'design', 'optimize', 'fix'
        ]
        keywords = [k for k in tech_keywords if k in text]
        
        # Build issue context
        issue_context = {
            'labels': issue_labels or [],
            'keywords': keywords
        }
        
        # Adapt prompt
        adapted_prompt = self.adapt_prompt_for_agent(
            base_prompt,
            agent_name,
            issue_context
        )
        
        return adapted_prompt


def main():
    """CLI interface for the contextual adapter"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Contextual prompt adapter - enhance prompts for specific agents"
    )
    parser.add_argument(
        "agent",
        help="Agent name (e.g., create-guru, engineer-master)"
    )
    parser.add_argument(
        "--prompt",
        required=True,
        help="Base prompt to adapt"
    )
    parser.add_argument(
        "--labels",
        help="Comma-separated issue labels"
    )
    parser.add_argument(
        "--title",
        default="",
        help="Issue title"
    )
    parser.add_argument(
        "--body",
        default="",
        help="Issue body"
    )
    
    args = parser.parse_args()
    
    adapter = ContextualPromptAdapter()
    
    labels = args.labels.split(',') if args.labels else []
    
    adapted_prompt = adapter.enhance_prompt_with_context(
        args.prompt,
        args.agent,
        args.title,
        labels,
        args.body
    )
    
    print("=" * 70)
    print(f"CONTEXTUALLY ADAPTED PROMPT FOR @{args.agent}")
    print("=" * 70)
    print()
    print(adapted_prompt)
    print()
    print("=" * 70)
    
    return 0


if __name__ == "__main__":
    exit(main())
