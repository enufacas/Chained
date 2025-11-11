#!/usr/bin/env python3
"""
Intelligent agent matching system for Chained.
Analyzes issue content and matches it to the most appropriate specialized agent.
"""

import sys
import json
import re
import os
import yaml
from pathlib import Path

# Agent utilities (inline for self-contained script)
AGENTS_DIR = Path(".github/agents")

def parse_agent_file(filepath):
    """Parse an agent markdown file and extract frontmatter and content."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    frontmatter_match = re.match(r'^---\n(.*?)\n---\n(.*)$', content, re.DOTALL)
    if not frontmatter_match:
        return None
    
    frontmatter_str = frontmatter_match.group(1)
    body = frontmatter_match.group(2).strip()
    
    try:
        frontmatter = yaml.safe_load(frontmatter_str)
    except yaml.YAMLError:
        return None
    
    emoji_match = re.search(r'^#\s*([^\s]+)\s+', body)
    emoji = emoji_match.group(1) if emoji_match else ""
    
    return {
        'name': frontmatter.get('name', ''),
        'description': frontmatter.get('description', ''),
        'emoji': emoji
    }

def list_agents():
    """List all agent names from .github/agents/."""
    agents = []
    if not AGENTS_DIR.exists():
        return agents
    
    for filepath in AGENTS_DIR.glob("*.md"):
        if filepath.name == "README.md":
            continue
        agent_info = parse_agent_file(filepath)
        if agent_info and agent_info['name']:
            agents.append(agent_info['name'])
    
    return sorted(agents)

def get_agent_info(agent_name):
    """Get full information about a specific agent."""
    filepath = AGENTS_DIR / f"{agent_name}.md"
    if not filepath.exists():
        return None
    
    return parse_agent_file(filepath)

# Define keyword patterns for each agent specialization
AGENT_PATTERNS = {
    'bug-hunter': {
        'keywords': [
            'bug', 'error', 'crash', 'fail', 'broken', 'issue', 'problem',
            'not working', 'exception', 'stacktrace', 'debug', 'fix',
            'regression', 'edge case', 'null pointer', 'undefined'
        ],
        'patterns': [
            r'\berror\b', r'\bcrash', r'\bfail', r'\bbug\b', r'\bbroken\b',
            r'\bnot work', r'\bexception\b', r'\bstack\s*trace\b'
        ]
    },
    'feature-architect': {
        'keywords': [
            'feature', 'new', 'add', 'implement', 'create', 'build',
            'enhancement', 'improve', 'design', 'architecture', 'system',
            'integration', 'capability', 'functionality'
        ],
        'patterns': [
            r'\bfeature\b', r'\bnew\b', r'\badd\b', r'\bimplement',
            r'\bcreate\b', r'\bbuild\b', r'\benhance', r'\bdesign\b'
        ]
    },
    'doc-master': {
        'keywords': [
            'documentation', 'docs', 'readme', 'comment', 'explain',
            'clarify', 'guide', 'tutorial', 'example', 'docstring',
            'api doc', 'manual', 'help', 'instructions'
        ],
        'patterns': [
            r'\bdoc', r'\breadme\b', r'\bguide\b', r'\btutorial\b',
            r'\bexample', r'\bcomment', r'\bexplain\b'
        ]
    },
    'test-champion': {
        'keywords': [
            'test', 'testing', 'coverage', 'unit test', 'integration test',
            'e2e', 'spec', 'assertion', 'mock', 'validate', 'verification',
            'quality assurance', 'qa'
        ],
        'patterns': [
            r'\btest', r'\bcoverage\b', r'\bunit\b', r'\bintegration\b',
            r'\bvalidat', r'\bverif', r'\bqa\b'
        ]
    },
    'performance-optimizer': {
        'keywords': [
            'performance', 'slow', 'optimize', 'speed', 'latency',
            'throughput', 'efficiency', 'memory', 'cpu', 'bottleneck',
            'scalability', 'fast', 'faster'
        ],
        'patterns': [
            r'\bperformance\b', r'\bslow\b', r'\boptimi', r'\bspeed\b',
            r'\blatency\b', r'\bmemory\b', r'\bbottleneck\b'
        ]
    },
    'security-guardian': {
        'keywords': [
            'security', 'vulnerability', 'exploit', 'attack', 'xss',
            'sql injection', 'csrf', 'authentication', 'authorization',
            'encryption', 'secure', 'sanitize', 'validate input'
        ],
        'patterns': [
            r'\bsecur', r'\bvulner', r'\bexploit\b', r'\battack\b',
            r'\bxss\b', r'\binjection\b', r'\bauth', r'\bencrypt'
        ]
    },
    'code-poet': {
        'keywords': [
            'refactor', 'clean', 'readable', 'maintainable', 'code quality',
            'style', 'formatting', 'conventions', 'best practices',
            'elegant', 'simplify', 'clarity'
        ],
        'patterns': [
            r'\brefactor\b', r'\bclean\b', r'\breadable\b', r'\bmaintain',
            r'\bcode quality\b', r'\bstyle\b', r'\bformat', r'\belegant\b'
        ]
    },
    'refactor-wizard': {
        'keywords': [
            'refactor', 'restructure', 'reorganize', 'duplicate',
            'technical debt', 'complexity', 'simplify', 'decompose',
            'extract', 'consolidate', 'improve structure'
        ],
        'patterns': [
            r'\brefactor', r'\brestructur', r'\breorganiz', r'\bduplicate',
            r'\btechnical debt\b', r'\bcomplex', r'\bsimplif', r'\bextract\b'
        ]
    },
    'integration-specialist': {
        'keywords': [
            'integration', 'api', 'webhook', 'external', 'third-party',
            'service', 'endpoint', 'http', 'rest', 'graphql', 'connect',
            'interface', 'plugin', 'stripe', 'paypal', 'payment', 'oauth'
        ],
        'patterns': [
            r'\bintegrat', r'\bapi\b', r'\bwebhook\b', r'\bexternal\b',
            r'\bthird.?party\b', r'\bservice\b', r'\bendpoint\b', r'\bhttp\b',
            r'\bstripe\b', r'\bpaypal\b', r'\bpayment\b', r'\boauth\b'
        ]
    },
    'ux-enhancer': {
        'keywords': [
            'ui', 'ux', 'user interface', 'user experience', 'design',
            'usability', 'accessibility', 'a11y', 'responsive', 'layout',
            'css', 'styling', 'visual', 'polish', 'colors', 'theme'
        ],
        'patterns': [
            r'\bui\b', r'\bux\b', r'\buser interface\b', r'\buser experience\b',
            r'\busabilit', r'\baccessibilit', r'\ba11y\b', r'\bresponsive\b',
            r'\bdesign\b', r'\bcolors?\b', r'\btheme\b', r'\blayout\b'
        ]
    }
}

def normalize_text(text):
    """Normalize text for matching (lowercase, remove extra whitespace)."""
    if not text:
        return ""
    return re.sub(r'\s+', ' ', text.lower().strip())

def calculate_match_score(text, agent_name):
    """Calculate how well the text matches an agent's specialization."""
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
    for pattern in patterns['patterns']:
        if re.search(pattern, normalized_text, re.IGNORECASE):
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
        # No clear match, default to feature-architect for general issues
        return {
            'agent': 'feature-architect',
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
    
    title = sys.argv[1]
    body = sys.argv[2] if len(sys.argv) > 2 else ""
    
    result = match_issue_to_agent(title, body)
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
