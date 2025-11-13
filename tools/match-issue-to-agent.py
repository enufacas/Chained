#!/usr/bin/env python3
"""
Intelligent agent matching system for Chained.
Analyzes issue content and matches it to the most appropriate specialized agent.

Performance optimizations:
- Pre-compiled regex patterns for faster matching
- LRU cache for agent info to reduce file I/O
- Memoization for text normalization
"""

import sys
import json
import re
import os
import yaml
from pathlib import Path
from functools import lru_cache

# Agent utilities (inline for self-contained script)
AGENTS_DIR = Path(".github/agents")

# Pre-compiled regex patterns for performance
_FRONTMATTER_PATTERN = re.compile(r'^---\n(.*?)\n---\n(.*)$', re.DOTALL)
_EMOJI_PATTERN = re.compile(r'^#\s*([^\s]+)\s+')

@lru_cache(maxsize=32)
def parse_agent_file(filepath):
    """Parse an agent markdown file and extract frontmatter and content.
    
    Uses LRU cache to avoid repeated file reads for the same agent.
    """
    try:
        # Validate filepath to prevent path traversal
        filepath = Path(filepath).resolve()
        agents_dir = AGENTS_DIR.resolve()
        
        # Ensure the file is within the agents directory
        if not str(filepath).startswith(str(agents_dir)):
            return None
        
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        frontmatter_match = _FRONTMATTER_PATTERN.match(content)
        if not frontmatter_match:
            return None
        
        frontmatter_str = frontmatter_match.group(1)
        body = frontmatter_match.group(2).strip()
        
        try:
            frontmatter = yaml.safe_load(frontmatter_str)
        except yaml.YAMLError:
            return None
        
        # Validate that frontmatter is a dict
        if not isinstance(frontmatter, dict):
            return None
        
        emoji_match = _EMOJI_PATTERN.search(body)
        emoji = emoji_match.group(1) if emoji_match else ""
        
        return {
            'name': frontmatter.get('name', ''),
            'description': frontmatter.get('description', ''),
            'emoji': emoji
        }
    except (IOError, OSError, UnicodeDecodeError) as e:
        # Handle file reading errors gracefully
        return None
    except Exception as e:
        # Catch any other unexpected errors
        return None

@lru_cache(maxsize=128)
def list_agents():
    """List all agent names from .github/agents/.
    
    Uses LRU cache to avoid repeated directory scans.
    """
    agents = []
    if not AGENTS_DIR.exists():
        return tuple(agents)  # Return tuple for hashability
    
    for filepath in AGENTS_DIR.glob("*.md"):
        if filepath.name == "README.md":
            continue
        # Convert path to string for caching compatibility
        agent_info = parse_agent_file(str(filepath))
        if agent_info and agent_info['name']:
            agents.append(agent_info['name'])
    
    return tuple(sorted(agents))  # Return tuple for hashability

@lru_cache(maxsize=32)
def get_agent_info(agent_name):
    """Get full information about a specific agent.
    
    Uses LRU cache to avoid repeated file reads.
    """
    # Validate agent_name to prevent path traversal
    if not agent_name or not isinstance(agent_name, str):
        return None
    
    # Only allow alphanumeric, hyphens, and underscores in agent names
    if not re.match(r'^[a-zA-Z0-9_-]+$', agent_name):
        return None
    
    filepath = AGENTS_DIR / f"{agent_name}.md"
    if not filepath.exists():
        return None
    
    return parse_agent_file(str(filepath))

# Define keyword patterns for each agent specialization
# All agents are inspired by legendary computer scientists and engineers
AGENT_PATTERNS = {
    'accelerate-master': {
        'keywords': [
            'performance', 'slow', 'optimize', 'speed', 'latency',
            'throughput', 'efficiency', 'memory', 'cpu', 'bottleneck',
            'scalability', 'fast', 'faster', 'algorithm', 'accelerate'
        ],
        'patterns': [
            r'\bperformance\b', r'\bslow\b', r'\boptimi', r'\bspeed\b',
            r'\blatency\b', r'\bmemory\b', r'\bbottleneck\b', r'\balgorithm\b'
        ]
    },
    'assert-specialist': {
        'keywords': [
            'test', 'testing', 'coverage', 'unit test', 'integration test',
            'e2e', 'spec', 'assertion', 'mock', 'validate', 'verification',
            'quality assurance', 'qa', 'assert', 'specification'
        ],
        'patterns': [
            r'\btest', r'\bcoverage\b', r'\bunit\b', r'\bintegration\b',
            r'\bvalidat', r'\bverif', r'\bqa\b', r'\bassert'
        ]
    },
    'coach-master': {
        'keywords': [
            'review', 'code review', 'best practices', 'mentor', 'guide',
            'coaching', 'teaching', 'feedback', 'standards', 'conventions',
            'principles', 'patterns', 'learning', 'knowledge sharing'
        ],
        'patterns': [
            r'\breview\b', r'\bmentor', r'\bguide\b', r'\bcoach',
            r'\bbest practice', r'\bfeedback\b', r'\bstandard', r'\bpattern'
        ]
    },
    'create-guru': {
        'keywords': [
            'feature', 'new', 'create', 'build', 'implement', 'infrastructure',
            'system', 'innovative', 'groundbreaking', 'visionary', 'invention',
            'capability', 'functionality', 'creative'
        ],
        'patterns': [
            r'\bfeature\b', r'\bnew\b', r'\bcreate\b', r'\bbuild\b',
            r'\binfrastructure\b', r'\binnovative\b', r'\bvision'
        ]
    },
    'engineer-master': {
        'keywords': [
            'api', 'endpoint', 'service', 'engineering', 'systematic',
            'rigorous', 'architecture', 'design', 'implementation',
            'rest', 'graphql', 'http', 'backend'
        ],
        'patterns': [
            r'\bapi\b', r'\bendpoint\b', r'\bservice\b', r'\bengine',
            r'\barchitecture\b', r'\bdesign\b', r'\brest\b', r'\bhttp\b'
        ]
    },
    'engineer-wizard': {
        'keywords': [
            'api', 'service', 'engineering', 'innovative', 'creative',
            'bold', 'visionary', 'endpoint', 'integration', 'system',
            'inventive', 'groundbreaking'
        ],
        'patterns': [
            r'\bapi\b', r'\bservice\b', r'\bengine', r'\binnovative\b',
            r'\bintegrat', r'\binventive\b', r'\bbold\b'
        ]
    },
    'investigate-champion': {
        'keywords': [
            'investigate', 'analyze', 'metrics', 'data', 'pattern',
            'flow', 'dependency', 'trace', 'research', 'explore',
            'diagnostic', 'analysis', 'insight', 'understanding'
        ],
        'patterns': [
            r'\binvestigat', r'\banalyz', r'\bmetric', r'\bdata\b',
            r'\bpattern', r'\bflow\b', r'\bdependenc', r'\btrace\b'
        ]
    },
    'monitor-champion': {
        'keywords': [
            'security', 'monitor', 'surveillance', 'access control',
            'authentication', 'authorization', 'audit', 'compliance',
            'data integrity', 'privacy', 'protection', 'watch'
        ],
        'patterns': [
            r'\bsecur', r'\bmonitor', r'\baccess\b', r'\bauth',
            r'\baudit\b', r'\bintegrity\b', r'\bprotect', r'\bwatch\b'
        ]
    },
    'organize-guru': {
        'keywords': [
            'refactor', 'clean', 'organize', 'structure', 'duplicate',
            'complexity', 'simplify', 'solid', 'principles', 'discipline',
            'maintainable', 'reorganize', 'consolidate'
        ],
        'patterns': [
            r'\brefactor', r'\bclean\b', r'\borganiz', r'\bstructure\b',
            r'\bduplicate', r'\bcomplex', r'\bsimplif', r'\bsolid\b'
        ]
    },
    'secure-specialist': {
        'keywords': [
            'security', 'vulnerability', 'exploit', 'attack', 'xss',
            'sql injection', 'csrf', 'encryption', 'secure', 'sanitize',
            'threat', 'risk', 'defense', 'protection', 'safety'
        ],
        'patterns': [
            r'\bsecur', r'\bvulner', r'\bexploit\b', r'\battack\b',
            r'\bxss\b', r'\binjection\b', r'\bencrypt', r'\bthreat\b'
        ]
    },
    'support-master': {
        'keywords': [
            'support', 'help', 'guide', 'mentor', 'review', 'feedback',
            'learning', 'skill', 'knowledge', 'best practices', 'coaching',
            'principles', 'standards', 'teaching'
        ],
        'patterns': [
            r'\bsupport\b', r'\bhelp\b', r'\bguide\b', r'\bmentor',
            r'\breview\b', r'\bfeedback\b', r'\blearn', r'\bskill\b'
        ]
    }
}

# Pre-compile all regex patterns for performance
# This is done once at module load time, avoiding recompilation on every match
_COMPILED_PATTERNS = {}
for agent_name, patterns_dict in AGENT_PATTERNS.items():
    _COMPILED_PATTERNS[agent_name] = [
        re.compile(pattern, re.IGNORECASE) 
        for pattern in patterns_dict['patterns']
    ]

# Pre-compile whitespace normalization pattern
_WHITESPACE_PATTERN = re.compile(r'\s+')

@lru_cache(maxsize=256)
def sanitize_input(text):
    """Sanitize input text to prevent issues with special characters.
    
    Uses LRU cache to avoid re-sanitizing the same text.
    """
    if not text:
        return ""
    # Remove null bytes and other control characters (except common whitespace)
    # This prevents potential security issues and processing errors
    text = text.replace('\x00', '')  # Remove null bytes
    text = ''.join(char for char in text if ord(char) >= 32 or char in '\t\n\r')
    return text

@lru_cache(maxsize=256)
def normalize_text(text):
    """Normalize text for matching (lowercase, remove extra whitespace).
    
    Uses LRU cache to avoid re-normalizing the same text.
    Uses pre-compiled pattern for whitespace normalization.
    """
    if not text:
        return ""
    # First sanitize the input
    text = sanitize_input(text)
    # Then normalize whitespace and convert to lowercase
    return _WHITESPACE_PATTERN.sub(' ', text.lower().strip())

def calculate_match_score(text, agent_name):
    """Calculate how well the text matches an agent's specialization.
    
    Uses pre-compiled regex patterns for optimal performance.
    """
    if agent_name not in AGENT_PATTERNS:
        return 0
    
    patterns = AGENT_PATTERNS[agent_name]
    normalized_text = normalize_text(text)
    
    score = 0
    
    # Check keyword matches (1 point each)
    for keyword in patterns['keywords']:
        if keyword in normalized_text:
            score += 1
    
    # Check pattern matches (2 points each, as they're more precise)
    # Use pre-compiled patterns from _COMPILED_PATTERNS
    for compiled_pattern in _COMPILED_PATTERNS[agent_name]:
        if compiled_pattern.search(normalized_text):
            score += 2
    
    return score

def match_issue_to_agent(title, body=""):
    """
    Match an issue to the most appropriate agent based on content.
    
    Args:
        title: Issue title
        body: Issue body/description
        
    Returns:
        Dictionary with matched agent info and confidence score
    """
    # Combine title and body, with title weighted more heavily
    combined_text = f"{title} {title} {body}"  # Title appears twice for emphasis
    
    # Get all available agents
    available_agents = list_agents()
    
    # Calculate scores for each agent
    scores = {}
    for agent_name in available_agents:
        score = calculate_match_score(combined_text, agent_name)
        scores[agent_name] = score
    
    # Find the best match
    if not scores or max(scores.values()) == 0:
        # No clear match, default to create-guru for general issues
        return {
            'agent': 'create-guru',
            'score': 0,
            'confidence': 'low',
            'reason': 'No specific keywords matched, using default agent'
        }
    
    best_agent = max(scores, key=scores.get)
    best_score = scores[best_agent]
    
    # Determine confidence level
    if best_score >= 5:
        confidence = 'high'
    elif best_score >= 3:
        confidence = 'medium'
    else:
        confidence = 'low'
    
    # Get agent info
    agent_info = get_agent_info(best_agent)
    
    return {
        'agent': best_agent,
        'score': best_score,
        'confidence': confidence,
        'emoji': agent_info['emoji'] if agent_info else '',
        'description': agent_info['description'] if agent_info else '',
        'all_scores': scores,
        'reason': f'Matched based on issue content analysis'
    }

def main():
    """Command-line interface."""
    if len(sys.argv) < 2:
        print("Usage: match-issue-to-agent.py <title> [body]", file=sys.stderr)
        print("", file=sys.stderr)
        print("Analyzes issue content and suggests the best agent specialization.", file=sys.stderr)
        sys.exit(1)
    
    try:
        title = sys.argv[1]
        body = sys.argv[2] if len(sys.argv) > 2 else ""
        
        # Sanitize inputs to prevent issues with special characters
        title = sanitize_input(title)
        body = sanitize_input(body)
        
        result = match_issue_to_agent(title, body)
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(json.dumps({
            'error': str(e),
            'agent': 'create-guru',
            'score': 0,
            'confidence': 'low',
            'reason': 'Error processing input, using default agent'
        }, indent=2), file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
