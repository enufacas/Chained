#!/usr/bin/env python3
"""
Generate a visual diagram showing the sources of Copilot instructions.

This tool creates a table and ASCII diagram showing:
- Repository-level instructions
- Path-based instructions that apply to specific files
- Agent instructions (if an agent is assigned)
- The original issue/prompt

Usage:
    python3 tools/generate-instruction-diagram.py [--files FILE1 FILE2 ...] [--agent AGENT_NAME] [--issue ISSUE_NUMBER]
"""

import os
import sys
import argparse
import re
from pathlib import Path
from typing import List, Dict, Set
import fnmatch


def parse_instruction_file(filepath: str) -> Dict:
    """Parse an instruction file and extract its frontmatter metadata."""
    result = {
        'path': filepath,
        'apply_to': [],
        'title': '',
        'has_frontmatter': False
    }
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for YAML frontmatter
        if content.startswith('---\n'):
            parts = content.split('---\n', 2)
            if len(parts) >= 3:
                frontmatter = parts[1]
                body = parts[2]
                result['has_frontmatter'] = True
                
                # Parse applyTo patterns
                in_apply_to = False
                for line in frontmatter.split('\n'):
                    if line.strip().startswith('applyTo:'):
                        in_apply_to = True
                    elif in_apply_to:
                        if line.startswith('  - '):
                            pattern = line.strip()[2:].strip('"\'')
                            result['apply_to'].append(pattern)
                        elif not line.startswith(' '):
                            in_apply_to = False
                
                # Extract title from first heading
                for line in body.split('\n'):
                    if line.startswith('# '):
                        result['title'] = line[2:].strip()
                        break
    except Exception as e:
        print(f"Warning: Could not parse {filepath}: {e}", file=sys.stderr)
    
    return result


def file_matches_pattern(filepath: str, pattern: str) -> bool:
    """Check if a file path matches a glob pattern."""
    # Normalize paths
    filepath = filepath.replace('\\', '/')
    pattern = pattern.replace('\\', '/')
    
    # Handle absolute vs relative paths
    if filepath.startswith('./'):
        filepath = filepath[2:]
    if pattern.startswith('./'):
        pattern = pattern[2:]
    
    return fnmatch.fnmatch(filepath, pattern)


def find_applicable_instructions(files: List[str], repo_root: str) -> List[Dict]:
    """Find all path-based instructions that apply to the given files."""
    instructions_dir = os.path.join(repo_root, '.github', 'instructions')
    applicable = []
    
    if not os.path.isdir(instructions_dir):
        return applicable
    
    # Find all .instructions.md files
    instruction_files = []
    for root, dirs, filenames in os.walk(instructions_dir):
        # Skip archive directory
        if 'archive' in root:
            continue
        for filename in filenames:
            if filename.endswith('.instructions.md'):
                instruction_files.append(os.path.join(root, filename))
    
    # Check each instruction file
    for inst_file in instruction_files:
        inst_data = parse_instruction_file(inst_file)
        if not inst_data['apply_to']:
            continue
        
        # Check if any file matches any pattern
        matches = False
        for filepath in files:
            # Make path relative to repo root
            if filepath.startswith(repo_root):
                rel_path = os.path.relpath(filepath, repo_root)
            else:
                rel_path = filepath
            
            for pattern in inst_data['apply_to']:
                if file_matches_pattern(rel_path, pattern):
                    matches = True
                    break
            if matches:
                break
        
        if matches:
            # Make path relative for display
            display_path = os.path.relpath(inst_file, repo_root)
            inst_data['display_path'] = display_path
            applicable.append(inst_data)
    
    return applicable


def get_agent_info(agent_name: str, repo_root: str) -> Dict:
    """Get information about an agent."""
    if not agent_name:
        return None
    
    # Remove @ prefix if present
    agent_name = agent_name.lstrip('@')
    
    agent_file = os.path.join(repo_root, '.github', 'agents', f'{agent_name}.md')
    if not os.path.isfile(agent_file):
        return None
    
    result = {
        'name': agent_name,
        'path': f'.github/agents/{agent_name}.md',
        'description': '',
        'specialization': ''
    }
    
    try:
        with open(agent_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Try to extract from frontmatter first
        if content.startswith('---\n'):
            parts = content.split('---\n', 2)
            if len(parts) >= 3:
                frontmatter = parts[1]
                for line in frontmatter.split('\n'):
                    if line.startswith('description:'):
                        result['description'] = line.split(':', 1)[1].strip().strip('"\'')
                    elif line.startswith('specialization:'):
                        result['specialization'] = line.split(':', 1)[1].strip().strip('"\'')
    except Exception as e:
        print(f"Warning: Could not parse agent file {agent_file}: {e}", file=sys.stderr)
    
    return result


def generate_ascii_diagram(sources: Dict) -> str:
    """Generate an ASCII art diagram showing instruction sources."""
    lines = []
    
    lines.append("```")
    lines.append("                    ╔══════════════════════════════════╗")
    lines.append("                    ║   GitHub Copilot Instructions   ║")
    lines.append("                    ╚══════════════════════════════════╝")
    lines.append("                                  │")
    lines.append("                                  │")
    lines.append("        ┌─────────────────────────┼─────────────────────────┐")
    lines.append("        │                         │                         │")
    lines.append("        ▼                         ▼                         ▼")
    
    # First row: Repository, Prompt, Agent
    left = "┌─────────────────┐"
    center = "┌─────────────────┐"
    right = "┌─────────────────┐" if sources.get('agent') else "                   "
    lines.append(f"  {left}       {center}       {right}")
    
    left = "│   Repository    │"
    center = "│  Issue/Prompt   │"
    right = "│  Agent Profile  │" if sources.get('agent') else "                   "
    lines.append(f"  {left}       {center}       {right}")
    
    left = "│  Instructions   │"
    center = f"│    #{sources.get('issue', 'N/A'):>5}        │"
    right = f"│  @{sources.get('agent', {}).get('name', 'none'):<13}│" if sources.get('agent') else "                   "
    lines.append(f"  {left}       {center}       {right}")
    
    left = "└─────────────────┘"
    center = "└─────────────────┘"
    right = "└─────────────────┘" if sources.get('agent') else "                   "
    lines.append(f"  {left}       {center}       {right}")
    
    # Second row: Path-based instructions
    if sources.get('path_instructions'):
        lines.append("        │")
        lines.append("        ▼")
        lines.append("  ┌─────────────────────────────────────────────┐")
        lines.append("  │       Path-Specific Instructions           │")
        count = len(sources['path_instructions'])
        lines.append(f"  │           ({count} file{'s' if count != 1 else ''} apply)               │")
        lines.append("  └─────────────────────────────────────────────┘")
    
    lines.append("```")
    return '\n'.join(lines)


def generate_instruction_table(sources: Dict, repo_url: str = None) -> str:
    """Generate a markdown table listing all instruction sources."""
    lines = []
    
    lines.append("| Source Type | Location | Description |")
    lines.append("|-------------|----------|-------------|")
    
    # Repository instructions
    repo_instructions = []
    if sources.get('repo_root_instructions'):
        repo_instructions.append('.copilot-instructions.md')
    if sources.get('github_copilot_instructions'):
        repo_instructions.append('.github/copilot-instructions.md')
    
    for inst in repo_instructions:
        if repo_url:
            link = f"[{inst}]({repo_url}/blob/main/{inst})"
        else:
            link = f"`{inst}`"
        lines.append(f"| 📚 Repository | {link} | Base repository instructions |")
    
    # Issue/Prompt
    if sources.get('issue'):
        issue_num = sources['issue']
        if repo_url:
            link = f"[Issue #{issue_num}]({repo_url}/issues/{issue_num})"
        else:
            link = f"Issue #{issue_num}"
        lines.append(f"| 🎯 Prompt | {link} | Original issue description |")
    
    # Agent
    if sources.get('agent'):
        agent = sources['agent']
        agent_name = agent['name']
        agent_path = agent['path']
        if repo_url:
            link = f"[@{agent_name}]({repo_url}/blob/main/{agent_path})"
        else:
            link = f"`@{agent_name}`"
        desc = agent.get('description', 'Agent profile and specialization')
        lines.append(f"| 🤖 Agent | {link} | {desc[:50]}... |")
    
    # Path-based instructions
    if sources.get('path_instructions'):
        for inst in sources['path_instructions']:
            path = inst['display_path']
            title = inst.get('title', 'Path-specific rules')
            if repo_url:
                link = f"[{path}]({repo_url}/blob/main/{path})"
            else:
                link = f"`{path}`"
            # Truncate title if too long
            if len(title) > 60:
                title = title[:57] + '...'
            lines.append(f"| 📍 Path Rules | {link} | {title} |")
    
    return '\n'.join(lines)


def generate_diagram(files: List[str] = None, agent: str = None, issue: int = None, repo_root: str = None) -> str:
    """Generate the complete instruction source diagram."""
    if repo_root is None:
        repo_root = os.getcwd()
    
    # Normalize file paths
    if files:
        files = [os.path.abspath(f) if not f.startswith('/') else f for f in files]
    else:
        files = []
    
    # Collect sources
    sources = {
        'issue': issue,
        'files': files
    }
    
    # Check for repository-level instructions
    root_copilot = os.path.join(repo_root, '.copilot-instructions.md')
    github_copilot = os.path.join(repo_root, '.github', 'copilot-instructions.md')
    
    sources['repo_root_instructions'] = os.path.isfile(root_copilot)
    sources['github_copilot_instructions'] = os.path.isfile(github_copilot)
    
    # Find applicable path-based instructions
    if files:
        sources['path_instructions'] = find_applicable_instructions(files, repo_root)
    else:
        sources['path_instructions'] = []
    
    # Get agent info
    if agent:
        sources['agent'] = get_agent_info(agent, repo_root)
    
    # Detect repo URL for links
    repo_url = None
    try:
        import subprocess
        result = subprocess.run(
            ['git', 'config', '--get', 'remote.origin.url'],
            cwd=repo_root,
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            url = result.stdout.strip()
            # Convert git URL to https URL
            if url.startswith('git@github.com:'):
                url = url.replace('git@github.com:', 'https://github.com/')
            if url.endswith('.git'):
                url = url[:-4]
            repo_url = url
    except Exception:
        pass
    
    # Generate output
    output = []
    output.append("## 📋 Copilot Instruction Sources")
    output.append("")
    output.append("This PR was generated using instructions from the following sources:")
    output.append("")
    
    # Add ASCII diagram
    output.append(generate_ascii_diagram(sources))
    output.append("")
    
    # Add table
    output.append("### Instruction Source Details")
    output.append("")
    output.append(generate_instruction_table(sources, repo_url))
    output.append("")
    
    # Add file list if provided
    if files:
        output.append("### Modified Files Context")
        output.append("")
        output.append("The following files were modified, which triggered specific path-based instructions:")
        output.append("")
        for f in files:
            rel_path = os.path.relpath(f, repo_root) if f.startswith(repo_root) else f
            output.append(f"- `{rel_path}`")
        output.append("")
    
    return '\n'.join(output)


def main():
    parser = argparse.ArgumentParser(
        description='Generate instruction source diagram for Copilot PRs'
    )
    parser.add_argument(
        '--files',
        nargs='+',
        help='Files that were modified (to detect applicable path instructions)'
    )
    parser.add_argument(
        '--agent',
        help='Name of the assigned agent (e.g., engineer-master)'
    )
    parser.add_argument(
        '--issue',
        type=int,
        help='Issue number that triggered this work'
    )
    parser.add_argument(
        '--repo-root',
        default=None,
        help='Repository root directory (default: current directory)'
    )
    
    args = parser.parse_args()
    
    diagram = generate_diagram(
        files=args.files,
        agent=args.agent,
        issue=args.issue,
        repo_root=args.repo_root
    )
    
    print(diagram)


if __name__ == '__main__':
    main()
