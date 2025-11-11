#!/usr/bin/env python3
"""
Agent Definition Validator
A comprehensive validation tool for GitHub Copilot custom agent definitions.

This infrastructure tool ensures that all agent definitions in .github/agents/
follow the GitHub Copilot custom agents convention and maintain consistency.

Inspired by the create-guru agent's vision for robust infrastructure.
"""

import sys
import yaml
import argparse
from pathlib import Path
from typing import Dict, List, Tuple, Optional

# ANSI color codes for beautiful terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header(text: str) -> None:
    """Print a visually appealing header."""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{text}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.END}\n")

def print_success(text: str) -> None:
    """Print success message."""
    print(f"{Colors.GREEN}✅ {text}{Colors.END}")

def print_error(text: str) -> None:
    """Print error message."""
    print(f"{Colors.RED}❌ {text}{Colors.END}")

def print_warning(text: str) -> None:
    """Print warning message."""
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.END}")

def print_info(text: str) -> None:
    """Print info message."""
    print(f"{Colors.BLUE}ℹ️  {text}{Colors.END}")

def validate_yaml_frontmatter(content: str, filename: str) -> Tuple[bool, Optional[Dict], List[str]]:
    """
    Validate YAML frontmatter in agent definition.
    
    Returns:
        (is_valid, parsed_data, errors)
    """
    errors = []
    
    if not content.startswith('---'):
        errors.append(f"Missing YAML frontmatter opening '---'")
        return False, None, errors
    
    parts = content.split('---', 2)
    if len(parts) < 3:
        errors.append(f"Missing YAML frontmatter closing '---'")
        return False, None, errors
    
    frontmatter = parts[1].strip()
    
    try:
        data = yaml.safe_load(frontmatter)
        if not isinstance(data, dict):
            errors.append(f"YAML frontmatter is not a dictionary")
            return False, None, errors
        
        # Check required fields
        if 'name' not in data:
            errors.append("Missing required field: 'name'")
        elif not isinstance(data['name'], str) or not data['name']:
            errors.append("Field 'name' must be a non-empty string")
        elif data['name'] != Path(filename).stem:
            errors.append(f"Field 'name' ({data['name']}) must match filename stem ({Path(filename).stem})")
        
        if 'description' not in data:
            errors.append("Missing required field: 'description'")
        elif not isinstance(data['description'], str) or not data['description']:
            errors.append("Field 'description' must be a non-empty string")
        
        # Check optional but recommended fields
        if 'tools' in data:
            if not isinstance(data['tools'], list):
                errors.append("Field 'tools' must be a list")
            elif len(data['tools']) == 0:
                errors.append("Field 'tools' is empty - consider adding relevant tools")
        
        return len(errors) == 0, data, errors
        
    except yaml.YAMLError as e:
        errors.append(f"YAML parsing error: {e}")
        return False, None, errors

def validate_markdown_body(content: str) -> Tuple[bool, List[str]]:
    """
    Validate markdown body structure.
    
    Returns:
        (is_valid, warnings)
    """
    warnings = []
    
    parts = content.split('---', 2)
    if len(parts) < 3:
        return False, ["Missing markdown body"]
    
    body = parts[2].strip()
    
    if not body:
        warnings.append("Markdown body is empty")
        return False, warnings
    
    # Check for recommended sections
    recommended_sections = [
        'Core Responsibilities',
        'Approach',
        'Code Quality Standards',
        'Performance Tracking'
    ]
    
    for section in recommended_sections:
        if section.lower() not in body.lower():
            warnings.append(f"Consider adding section: '{section}'")
    
    # Check for agent header
    if not body.startswith('#'):
        warnings.append("Markdown body should start with a header (# Agent Name)")
    
    return True, warnings

def validate_naming_convention(filename: str) -> Tuple[bool, List[str]]:
    """
    Validate agent filename follows kebab-case convention.
    
    Returns:
        (is_valid, errors)
    """
    errors = []
    stem = Path(filename).stem
    
    # Check kebab-case
    if not all(c.islower() or c == '-' for c in stem):
        errors.append(f"Filename '{stem}' should be in kebab-case (lowercase with hyphens)")
    
    if stem.startswith('-') or stem.endswith('-'):
        errors.append(f"Filename '{stem}' should not start or end with hyphen")
    
    if '--' in stem:
        errors.append(f"Filename '{stem}' should not contain consecutive hyphens")
    
    return len(errors) == 0, errors

def validate_agent_file(filepath: Path) -> Tuple[bool, Dict]:
    """
    Validate a single agent definition file.
    
    Returns:
        (is_valid, results_dict)
    """
    results = {
        'filename': filepath.name,
        'path': str(filepath),
        'valid': True,
        'errors': [],
        'warnings': []
    }
    
    try:
        # Read file
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Validate naming convention
        naming_valid, naming_errors = validate_naming_convention(filepath.name)
        results['errors'].extend(naming_errors)
        
        # Validate YAML frontmatter
        yaml_valid, data, yaml_errors = validate_yaml_frontmatter(content, filepath.name)
        results['errors'].extend(yaml_errors)
        
        if data:
            results['name'] = data.get('name', 'N/A')
            results['description'] = data.get('description', 'N/A')
            results['tools_count'] = len(data.get('tools', []))
        
        # Validate markdown body
        body_valid, body_warnings = validate_markdown_body(content)
        results['warnings'].extend(body_warnings)
        
        # Overall validation status
        results['valid'] = naming_valid and yaml_valid and body_valid
        
    except FileNotFoundError:
        results['valid'] = False
        results['errors'].append(f"File not found: {filepath}")
    except Exception as e:
        results['valid'] = False
        results['errors'].append(f"Unexpected error: {e}")
    
    return results['valid'], results

def validate_agents_directory(agents_dir: Path) -> Tuple[int, int, List[Dict]]:
    """
    Validate all agent definitions in the directory.
    
    Returns:
        (total_agents, valid_agents, all_results)
    """
    if not agents_dir.exists():
        print_error(f"Agents directory not found: {agents_dir}")
        return 0, 0, []
    
    agent_files = sorted(agents_dir.glob('*.md'))
    # Exclude README.md
    agent_files = [f for f in agent_files if f.name != 'README.md']
    
    all_results = []
    valid_count = 0
    
    for agent_file in agent_files:
        is_valid, results = validate_agent_file(agent_file)
        all_results.append(results)
        if is_valid:
            valid_count += 1
    
    return len(all_results), valid_count, all_results

def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(
        description='Validate GitHub Copilot custom agent definitions',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        '-d', '--directory',
        type=str,
        default='.github/agents',
        help='Directory containing agent definitions (default: .github/agents)'
    )
    parser.add_argument(
        '-f', '--file',
        type=str,
        help='Validate a specific agent file'
    )
    parser.add_argument(
        '--strict',
        action='store_true',
        help='Treat warnings as errors'
    )
    parser.add_argument(
        '--quiet',
        action='store_true',
        help='Only show errors'
    )
    
    args = parser.parse_args()
    
    print_header("🏭 Agent Definition Validator")
    print_info("Validating GitHub Copilot custom agent definitions")
    print_info("Following convention: https://docs.github.com/en/copilot/reference/custom-agents-configuration\n")
    
    if args.file:
        # Validate single file
        filepath = Path(args.file)
        is_valid, results = validate_agent_file(filepath)
        
        print(f"\n{Colors.BOLD}Validating: {results['filename']}{Colors.END}")
        
        if results['errors']:
            print(f"\n{Colors.BOLD}Errors:{Colors.END}")
            for error in results['errors']:
                print_error(error)
        
        if results['warnings'] and not args.quiet:
            print(f"\n{Colors.BOLD}Warnings:{Colors.END}")
            for warning in results['warnings']:
                print_warning(warning)
        
        if is_valid and not (args.strict and results['warnings']):
            print_success(f"\n{results['filename']} is valid!")
            return 0
        else:
            print_error(f"\n{results['filename']} has validation issues!")
            return 1
    
    else:
        # Validate directory
        agents_dir = Path(args.directory)
        total, valid, all_results = validate_agents_directory(agents_dir)
        
        if total == 0:
            print_error("No agent definitions found!")
            return 1
        
        # Display results
        print(f"{Colors.BOLD}Found {total} agent definition(s){Colors.END}\n")
        
        for results in all_results:
            status = "✅" if results['valid'] else "❌"
            print(f"{status} {Colors.BOLD}{results['filename']}{Colors.END}")
            
            if results.get('name'):
                print(f"   Name: {results['name']}")
            if results.get('description'):
                desc = results['description'][:60] + '...' if len(results['description']) > 60 else results['description']
                print(f"   Description: {desc}")
            if results.get('tools_count') is not None:
                print(f"   Tools: {results['tools_count']}")
            
            if results['errors']:
                for error in results['errors']:
                    print(f"   {Colors.RED}• {error}{Colors.END}")
            
            if results['warnings'] and not args.quiet:
                for warning in results['warnings']:
                    print(f"   {Colors.YELLOW}• {warning}{Colors.END}")
            
            print()
        
        # Summary
        print_header("Summary")
        print(f"{Colors.BOLD}Total agents: {total}{Colors.END}")
        print(f"{Colors.GREEN}Valid: {valid}{Colors.END}")
        print(f"{Colors.RED}Invalid: {total - valid}{Colors.END}")
        
        if valid == total:
            print_success("\n🎉 All agent definitions are valid!")
            return 0
        else:
            print_error(f"\n⚠️  {total - valid} agent definition(s) need attention")
            return 1

if __name__ == '__main__':
    sys.exit(main())
