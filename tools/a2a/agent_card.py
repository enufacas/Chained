"""
Agent Card generation from Chained agent definitions.

This module converts Chained agent definitions (.github/agents/*.md)
into A2A Protocol Agent Cards.
"""

import os
import re
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Any

from a2a.types import (
    AgentCard,
    AgentCapabilities,
    AgentSkill,
)

from .utils import get_agent_base_url, get_agent_port


def parse_agent_definition(agent_name: str) -> Dict[str, Any]:
    """
    Parse a Chained agent definition file.
    
    Args:
        agent_name: Name of the agent (e.g., "engineer-master")
        
    Returns:
        Dict containing parsed agent metadata
        
    Raises:
        FileNotFoundError: If agent definition file doesn't exist
        ValueError: If agent definition is invalid
    """
    # Find agent definition file
    repo_root = Path(__file__).parent.parent.parent
    agent_file = repo_root / ".github" / "agents" / f"{agent_name}.md"
    
    if not agent_file.exists():
        raise FileNotFoundError(f"Agent definition not found: {agent_file}")
    
    # Read and parse the file
    content = agent_file.read_text(encoding="utf-8")
    
    # Extract YAML frontmatter
    frontmatter_match = re.match(r"^---\n(.*?)\n---\n(.*)$", content, re.DOTALL)
    if not frontmatter_match:
        raise ValueError(f"Invalid agent definition format: {agent_file}")
    
    frontmatter_text = frontmatter_match.group(1)
    markdown_content = frontmatter_match.group(2)
    
    # Parse YAML frontmatter
    try:
        metadata = yaml.safe_load(frontmatter_text)
    except yaml.YAMLError as e:
        raise ValueError(f"Invalid YAML in agent definition: {e}")
    
    # Extract additional info from markdown content
    metadata["markdown_content"] = markdown_content
    
    # Parse responsibilities if present
    responsibilities_match = re.search(
        r"## (?:Core )?Responsibilities\n\n(.*?)(?=\n##|\Z)",
        markdown_content,
        re.DOTALL
    )
    if responsibilities_match:
        resp_text = responsibilities_match.group(1)
        # Extract bullet points
        responsibilities = re.findall(r"[-*]\s+\*\*([^*]+)\*\*:?\s+([^\n]+)", resp_text)
        if not responsibilities:
            # Try simpler pattern
            responsibilities = re.findall(r"[-*]\s+([^\n]+)", resp_text)
            responsibilities = [(r.strip(), "") for r in responsibilities]
        metadata["responsibilities"] = responsibilities
    
    return metadata


def extract_skills_from_agent(metadata: Dict[str, Any]) -> List[AgentSkill]:
    """
    Extract A2A skills from agent metadata.
    
    Args:
        metadata: Parsed agent metadata
        
    Returns:
        List of AgentSkill objects
    """
    skills = []
    
    # Primary skill from specialization or description
    specialization = metadata.get("specialization", "")
    description = metadata.get("description", "")
    name = metadata.get("name", "")
    
    # Create primary skill
    skill_id = specialization.replace(" ", "_").replace("-", "_").lower() if specialization else name.replace("-", "_")
    skill_name = specialization.title() if specialization else name.replace("-", " ").title()
    
    primary_skill = AgentSkill(
        id=skill_id,
        name=skill_name,
        description=description,
        tags=[tag.strip() for tag in specialization.split(",") if tag.strip()] if specialization else [name],
        examples=_generate_examples_from_description(description),
    )
    skills.append(primary_skill)
    
    # Add skills from responsibilities if available
    responsibilities = metadata.get("responsibilities", [])
    for i, resp in enumerate(responsibilities[:3], start=2):  # Limit to top 3
        if isinstance(resp, tuple):
            resp_name, resp_desc = resp
        else:
            resp_name = str(resp)
            resp_desc = ""
        
        # Clean up the responsibility name
        resp_name = resp_name.strip().rstrip(":")
        
        if resp_name and len(resp_name) > 3:  # Skip very short names
            skill = AgentSkill(
                id=f"{skill_id}_{i}",
                name=resp_name,
                description=resp_desc if resp_desc else resp_name,
                tags=[skill_id, resp_name.lower().replace(" ", "_")],
                examples=[f"Help with {resp_name.lower()}"],
            )
            skills.append(skill)
    
    return skills


def _generate_examples_from_description(description: str) -> List[str]:
    """
    Generate example prompts from agent description.
    
    Args:
        description: Agent description
        
    Returns:
        List of example prompts
    """
    examples = []
    
    # Extract key verbs and nouns
    words = description.lower().split()
    
    # Common action verbs in agent descriptions
    action_verbs = [
        "implement", "design", "create", "build", "develop", "optimize",
        "refactor", "analyze", "review", "test", "debug", "fix", "secure"
    ]
    
    # Find actions in description
    actions = [word for word in words if word.rstrip("ing") in action_verbs]
    
    if actions:
        # Generate examples based on actions
        for action in actions[:2]:  # Top 2 actions
            examples.append(f"{action.title()} this component")
    else:
        # Fallback to generic examples
        examples.append(f"Help me with {description.lower()}")
    
    return examples if examples else ["Can you help with this task?"]


def generate_agent_card(
    agent_name: str,
    version: str = "1.0.0",
    port: Optional[int] = None,
) -> AgentCard:
    """
    Generate an A2A Agent Card from a Chained agent definition.
    
    Args:
        agent_name: Name of the agent (e.g., "engineer-master")
        version: Agent version (default: "1.0.0")
        port: Port number for the agent server (auto-assigned if None)
        
    Returns:
        AgentCard object ready for A2A protocol
        
    Example:
        >>> card = generate_agent_card("engineer-master")
        >>> print(card.name)
        engineer-master
        >>> print(card.skills[0].name)
        API Engineering
    """
    # Parse agent definition
    metadata = parse_agent_definition(agent_name)
    
    # Get port
    if port is None:
        port = get_agent_port(agent_name)
    
    # Get base URL
    base_url = get_agent_base_url()
    agent_url = f"{base_url}:{port}/"
    
    # Extract skills
    skills = extract_skills_from_agent(metadata)
    
    # Create capabilities
    capabilities = AgentCapabilities(
        streaming=True,  # Enable streaming for all agents
    )
    
    # Create and return agent card
    card = AgentCard(
        name=metadata.get("name", agent_name),
        description=metadata.get("description", ""),
        url=agent_url,
        version=version,
        default_input_modes=["text"],
        default_output_modes=["text", "artifact"],
        capabilities=capabilities,
        skills=skills,
        supports_authenticated_extended_card=False,  # Can be enhanced later
    )
    
    return card


def generate_all_agent_cards() -> Dict[str, AgentCard]:
    """
    Generate agent cards for all Chained agents.
    
    Returns:
        Dict mapping agent names to their AgentCards
    """
    cards = {}
    
    # Find all agent definition files
    repo_root = Path(__file__).parent.parent.parent
    agents_dir = repo_root / ".github" / "agents"
    
    for agent_file in agents_dir.glob("*.md"):
        agent_name = agent_file.stem
        
        # Skip non-agent files (README, etc.)
        if agent_name.upper() == agent_name or agent_name == "README":
            continue
        
        try:
            card = generate_agent_card(agent_name)
            cards[agent_name] = card
        except Exception as e:
            print(f"Warning: Failed to generate card for {agent_name}: {e}")
            continue
    
    return cards


if __name__ == "__main__":
    # Example usage
    import sys
    
    if len(sys.argv) > 1:
        agent_name = sys.argv[1]
        card = generate_agent_card(agent_name)
        print(card.model_dump_json(indent=2, exclude_none=True))
    else:
        print("Usage: python -m tools.a2a.agent_card <agent-name>")
        print("\nGenerating cards for all agents...")
        cards = generate_all_agent_cards()
        print(f"Generated {len(cards)} agent cards")
        for name, card in list(cards.items())[:3]:
            print(f"\n{name}:")
            print(f"  Skills: {len(card.skills)}")
            print(f"  URL: {card.url}")
