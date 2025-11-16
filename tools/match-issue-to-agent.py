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
import random
from pathlib import Path
from functools import lru_cache

# Agent utilities (inline for self-contained script)
AGENTS_DIR = Path(".github/agents")
REGISTRY_PATH = Path(".github/agent-system/registry.json")

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

@lru_cache(maxsize=1)
def load_registry():
    """Load the agent registry to get human names for agents.
    
    Uses LRU cache since registry doesn't change during execution.
    """
    try:
        if not REGISTRY_PATH.exists():
            return None
        
        with open(REGISTRY_PATH, 'r', encoding='utf-8') as f:
            registry = json.load(f)
        
        return registry
    except (IOError, OSError, json.JSONDecodeError) as e:
        return None

def get_human_name_for_specialization(specialization):
    """Get a human-readable name for a specialization from the registry.
    
    Returns the human_name of an active agent with the given specialization.
    If multiple agents have the same specialization, returns one randomly
    to encourage variety.
    """
    registry = load_registry()
    if not registry or 'agents' not in registry:
        return None
    
    # Find all active agents with this specialization
    matching_agents = [
        agent for agent in registry['agents']
        if agent.get('specialization') == specialization and agent.get('status') == 'active'
    ]
    
    if not matching_agents:
        return None
    
    # Randomly select one to encourage variety
    selected_agent = random.choice(matching_agents)
    return selected_agent.get('human_name')

# Define keyword patterns for each agent specialization
# All agents are inspired by legendary computer scientists and engineers
# COMPREHENSIVE PATTERNS - Covers all 43+ agent specializations
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
    'accelerate-specialist': {
        'keywords': [
            'performance', 'optimize', 'efficiency', 'resource usage',
            'speed up', 'faster', 'accelerate', 'throughput', 'scalability'
        ],
        'patterns': [
            r'\bperformance\b', r'\boptimi', r'\befficiency\b', r'\bresource\b',
            r'\bspeed\b', r'\baccelerat', r'\bthroughput\b'
        ]
    },
    'align-wizard': {
        'keywords': [
            'ci/cd', 'pipeline', 'workflow', 'automation', 'choreograph',
            'coordination', 'align', 'synchronize', 'orchestrate'
        ],
        'patterns': [
            r'\bci\b', r'\bcd\b', r'\bpipeline\b', r'\bworkflow\b',
            r'\bautomation\b', r'\borchestrat', r'\balign'
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
    'assert-whiz': {
        'keywords': [
            'test', 'testing', 'coverage', 'proof', 'verification',
            'edge cases', 'quality', 'qa', 'assert', 'spec'
        ],
        'patterns': [
            r'\btest', r'\bcoverage\b', r'\bproof\b', r'\bverif',
            r'\bedge case', r'\bqa\b', r'\bassert'
        ]
    },
    'bridge-master': {
        'keywords': [
            'integration', 'api', 'service', 'communication', 'bridge',
            'connect', 'interoperability', 'interface', 'collaborate'
        ],
        'patterns': [
            r'\bintegrat', r'\bapi\b', r'\bservice\b', r'\bbridge\b',
            r'\bconnect', r'\binterface\b', r'\bcollab'
        ]
    },
    'clarify-champion': {
        'keywords': [
            'documentation', 'tutorial', 'clarify', 'explain', 'guide',
            'comments', 'readme', 'docs', 'examples', 'teaching'
        ],
        'patterns': [
            r'\bdocument', r'\btutorial\b', r'\bclarif', r'\bexplain\b',
            r'\bguide\b', r'\bcomment', r'\breadme\b', r'\bdocs\b'
        ]
    },
    'cloud-architect': {
        'keywords': [
            'cloud', 'aws', 'azure', 'gcp', 'devops', 'kubernetes',
            'docker', 'container', 'infrastructure', 'deployment'
        ],
        'patterns': [
            r'\bcloud\b', r'\baws\b', r'\bazure\b', r'\bgcp\b',
            r'\bdevops\b', r'\bkubernetes\b', r'\bdocker\b', r'\bcontainer\b'
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
    'coach-wizard': {
        'keywords': [
            'coaching', 'skill building', 'mentor', 'guide', 'teach',
            'review', 'feedback', 'best practices', 'knowledge'
        ],
        'patterns': [
            r'\bcoach', r'\bskill\b', r'\bmentor', r'\bguide\b',
            r'\bteach', r'\breview\b', r'\bfeedback\b'
        ]
    },
    'communicator-maestro': {
        'keywords': [
            'documentation', 'examples', 'teaching', 'explain', 'communicate',
            'tutorial', 'guide', 'clarify', 'illustrate'
        ],
        'patterns': [
            r'\bdocument', r'\bexample', r'\bteach', r'\bexplain\b',
            r'\bcommunicat', r'\btutorial\b', r'\bguide\b'
        ]
    },
    'construct-specialist': {
        'keywords': [
            'construct', 'build', 'create', 'system', 'feature',
            'infrastructure', 'tools', 'framework', 'architecture'
        ],
        'patterns': [
            r'\bconstruct', r'\bbuild\b', r'\bcreate\b', r'\bsystem\b',
            r'\bfeature\b', r'\binfrastructure\b', r'\btools\b'
        ]
    },
    'coordinate-wizard': {
        'keywords': [
            'coordination', 'workflow', 'ci/cd', 'automation', 'orchestrate',
            'pipeline', 'integrate', 'synchronize', 'organize'
        ],
        'patterns': [
            r'\bcoordinat', r'\bworkflow\b', r'\bci\b', r'\bcd\b',
            r'\bautomation\b', r'\borchestrat', r'\bpipeline\b'
        ]
    },
    'create-champion': {
        'keywords': [
            'create', 'build', 'tools', 'feature', 'implement',
            'construct', 'develop', 'infrastructure', 'system'
        ],
        'patterns': [
            r'\bcreate\b', r'\bbuild\b', r'\btools\b', r'\bfeature\b',
            r'\bimplement', r'\bconstruct', r'\bdevelop'
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
    'develop-specialist': {
        'keywords': [
            'develop', 'api', 'implement', 'feature', 'service',
            'endpoint', 'backend', 'frontend', 'application'
        ],
        'patterns': [
            r'\bdevelop', r'\bapi\b', r'\bimplement', r'\bfeature\b',
            r'\bservice\b', r'\bendpoint\b', r'\bbackend\b'
        ]
    },
    'document-ninja': {
        'keywords': [
            'documentation', 'docs', 'tutorial', 'guide', 'readme',
            'comments', 'explain', 'clarify', 'examples', 'help'
        ],
        'patterns': [
            r'\bdocument', r'\bdocs\b', r'\btutorial\b', r'\bguide\b',
            r'\breadme\b', r'\bcomment', r'\bexplain\b'
        ]
    },
    'edge-cases-pro': {
        'keywords': [
            'edge cases', 'corner cases', 'boundary', 'test', 'validate',
            'safety', 'error handling', 'exception', 'defensive'
        ],
        'patterns': [
            r'\bedge\s*case', r'\bcorner\s*case', r'\bboundary\b',
            r'\btest', r'\bvalidat', r'\bsafety\b', r'\berror\s*handl'
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
    'guide-wizard': {
        'keywords': [
            'guide', 'mentor', 'skill building', 'teach', 'review',
            'best practices', 'knowledge', 'coaching', 'training'
        ],
        'patterns': [
            r'\bguide\b', r'\bmentor', r'\bskill\b', r'\bteach',
            r'\breview\b', r'\bbest practice', r'\bknowledge\b'
        ]
    },
    'infrastructure-specialist': {
        'keywords': [
            'infrastructure', 'deployment', 'devops', 'ci/cd', 'pipeline',
            'server', 'hosting', 'cloud', 'provision', 'configure'
        ],
        'patterns': [
            r'\binfrastructure\b', r'\bdeployment\b', r'\bdevops\b',
            r'\bci\b', r'\bcd\b', r'\bpipeline\b', r'\bserver\b'
        ]
    },
    'integrate-specialist': {
        'keywords': [
            'integration', 'integrate', 'data flow', 'api', 'service',
            'connect', 'bridge', 'interoperability', 'sync'
        ],
        'patterns': [
            r'\bintegrat', r'\bdata\s*flow', r'\bapi\b', r'\bservice\b',
            r'\bconnect', r'\bbridge\b', r'\bsync\b'
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
    'investigate-specialist': {
        'keywords': [
            'investigate', 'analyze', 'code patterns', 'data flow',
            'dependency', 'trace', 'research', 'diagnostic', 'explore'
        ],
        'patterns': [
            r'\binvestigat', r'\banalyz', r'\bpattern', r'\bdata\s*flow',
            r'\bdependenc', r'\btrace\b', r'\bresearch\b'
        ]
    },
    'meta-coordinator': {
        'keywords': [
            'coordination', 'orchestration', 'multi-agent', 'collaboration',
            'task decomposition', 'agent', 'delegate', 'organize'
        ],
        'patterns': [
            r'\bcoordinat', r'\borchestrat', r'\bmulti-agent\b',
            r'\bcollab', r'\bdecomposit', r'\bagent', r'\bdelegate\b'
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
    'organize-expert': {
        'keywords': [
            'organize', 'maintainability', 'structure', 'clean code',
            'refactor', 'complexity', 'simplify', 'readable'
        ],
        'patterns': [
            r'\borganiz', r'\bmaintain', r'\bstructure\b', r'\bclean\b',
            r'\brefactor', r'\bcomplex', r'\bsimplif'
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
    'organize-specialist': {
        'keywords': [
            'organize', 'code structure', 'refactor', 'clean', 'clarity',
            'maintainable', 'simplify', 'consolidate', 'architecture'
        ],
        'patterns': [
            r'\borganiz', r'\bstructure\b', r'\brefactor', r'\bclean\b',
            r'\bclarity\b', r'\bmaintain', r'\bsimplif'
        ]
    },
    'pioneer-pro': {
        'keywords': [
            'pioneer', 'new technology', 'cutting-edge', 'experimental',
            'innovative', 'modern', 'latest', 'emerging', 'breakthrough'
        ],
        'patterns': [
            r'\bpioneer', r'\bnew\s*technolog', r'\bcutting-edge\b',
            r'\bexperimental\b', r'\binnovative\b', r'\bemerging\b'
        ]
    },
    'pioneer-sage': {
        'keywords': [
            'pioneer', 'visionary', 'future', 'new technology', 'innovative',
            'cutting-edge', 'experimental', 'breakthrough', 'revolutionary'
        ],
        'patterns': [
            r'\bpioneer', r'\bvisionary\b', r'\bfuture\b', r'\bnew\s*tech',
            r'\binnovative\b', r'\bcutting-edge\b', r'\bbreakthrough\b'
        ]
    },
    'refactor-champion': {
        'keywords': [
            'refactor', 'complexity', 'clean code', 'simplify', 'improve',
            'restructure', 'optimize', 'maintainability', 'readable'
        ],
        'patterns': [
            r'\brefactor', r'\bcomplex', r'\bclean\b', r'\bsimplif',
            r'\bimprove\b', r'\brestructure\b', r'\bmaintain'
        ]
    },
    'restructure-master': {
        'keywords': [
            'restructure', 'refactor', 'complexity', 'architecture',
            'reorganize', 'clarity', 'simplify', 'improve', 'design'
        ],
        'patterns': [
            r'\brestructure\b', r'\brefactor', r'\bcomplex',
            r'\barchitecture\b', r'\breorganiz', r'\bclarity\b'
        ]
    },
    'secure-ninja': {
        'keywords': [
            'security', 'access control', 'authentication', 'authorization',
            'privacy', 'encrypt', 'secure', 'protection', 'confidential'
        ],
        'patterns': [
            r'\bsecur', r'\baccess\s*control\b', r'\bauth', r'\bprivacy\b',
            r'\bencrypt', r'\bprotect', r'\bconfidential\b'
        ]
    },
    'secure-pro': {
        'keywords': [
            'security', 'vulnerability', 'threat', 'risk', 'secure',
            'protect', 'defense', 'attack', 'exploit', 'patch'
        ],
        'patterns': [
            r'\bsecur', r'\bvulner', r'\bthreat\b', r'\brisk\b',
            r'\bprotect', r'\bdefense\b', r'\battack\b', r'\bexploit\b'
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
    'simplify-pro': {
        'keywords': [
            'simplify', 'code structure', 'clean', 'legacy', 'refactor',
            'complexity', 'maintainable', 'readable', 'clarity'
        ],
        'patterns': [
            r'\bsimplif', r'\bcode\s*structure\b', r'\bclean\b',
            r'\blegacy\b', r'\brefactor', r'\bcomplex', r'\bmaintain'
        ]
    },
    'steam-machine': {
        'keywords': [
            'steam machine', 'trending', 'modern', 'systematic', 'thorough',
            'comprehensive', 'solution', 'innovative'
        ],
        'patterns': [
            r'\bsteam\s*machine\b', r'\btrending\b', r'\bmodern\b',
            r'\bsystematic\b', r'\bthorough\b', r'\bcomprehensive\b'
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
    },
    'tools-analyst': {
        'keywords': [
            'tools', 'construct', 'build', 'utility', 'script',
            'automation', 'helper', 'command', 'cli', 'framework'
        ],
        'patterns': [
            r'\btools\b', r'\bconstruct', r'\bbuild\b', r'\butility\b',
            r'\bscript\b', r'\bautomation\b', r'\bhelper\b', r'\bcli\b'
        ]
    },
    'troubleshoot-expert': {
        'keywords': [
            'troubleshoot', 'debug', 'fix', 'error', 'failure', 'issue',
            'problem', 'workflow', 'ci/cd', 'github actions', 'broken'
        ],
        'patterns': [
            r'\btroubleshoot', r'\bdebug', r'\bfix\b', r'\berror\b',
            r'\bfailure\b', r'\bproblem\b', r'\bworkflow\b', r'\bbroken\b'
        ]
    },
    'validator-pro': {
        'keywords': [
            'validate', 'verification', 'test', 'coverage', 'proof',
            'quality', 'check', 'assert', 'confirm', 'ensure'
        ],
        'patterns': [
            r'\bvalidat', r'\bverif', r'\btest', r'\bcoverage\b',
            r'\bproof\b', r'\bquality\b', r'\bcheck\b', r'\bassert'
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
        # No clear match - use fallback strategy with variety
        # Instead of always using create-guru, rotate through capable general agents
        fallback_agents = [
            'create-guru',        # Infrastructure & feature creation
            'investigate-champion',  # General investigation
            'meta-coordinator',   # Multi-task coordination
            'engineer-master',    # Systematic engineering
            'organize-guru',      # General organization
        ]
        # Filter to available agents
        available_fallback = [a for a in fallback_agents if a in available_agents]
        if not available_fallback:
            available_fallback = list(available_agents)[:5]  # Use first 5 as fallback
        
        # Randomly select from fallback options for variety
        default_agent = random.choice(available_fallback)
        human_name = get_human_name_for_specialization(default_agent)
        agent_info = get_agent_info(default_agent)
        return {
            'agent': default_agent,
            'human_name': human_name,
            'score': 0,
            'confidence': 'low',
            'emoji': agent_info['emoji'] if agent_info else '',
            'description': agent_info['description'] if agent_info else '',
            'reason': f'No specific keywords matched, selected @{default_agent} from general agents pool'
        }
    
    # Find all agents with the maximum score (to handle ties)
    max_score = max(scores.values())
    
    # Be more liberal - consider agents within 80% of the max score as viable
    # This increases variety by not always picking the absolute highest scorer
    liberal_threshold = max_score * 0.8
    top_agents = [agent for agent, score in scores.items() if score >= liberal_threshold]
    
    # If too many agents match, narrow it down to top 5 to maintain quality
    if len(top_agents) > 5:
        # Sort by score and take top 5
        sorted_agents = sorted(top_agents, key=lambda a: scores[a], reverse=True)
        top_agents = sorted_agents[:5]
    
    # Randomly select from the top agents to promote variety
    # This prevents always selecting the same agent for similar issues
    best_agent = random.choice(top_agents)
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
    human_name = get_human_name_for_specialization(best_agent)
    
    return {
        'agent': best_agent,
        'human_name': human_name,
        'score': best_score,
        'confidence': confidence,
        'emoji': agent_info['emoji'] if agent_info else '',
        'description': agent_info['description'] if agent_info else '',
        'all_scores': scores,
        'top_agents': top_agents if len(top_agents) > 1 else None,  # Show ties
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
