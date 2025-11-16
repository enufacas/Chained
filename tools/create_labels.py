#!/usr/bin/env python3
"""
Bulk Label Creator for Chained Repository
Creates all standard system labels
"""

import subprocess
import sys
from typing import List, Tuple

# Label definitions: (name, color, description)
SYSTEM_LABELS: List[Tuple[str, str, str]] = [
    # System automation labels
    ("automated", "E99695", "Automated workflow action"),
    ("bot-created", "E99695", "Created by bot/automation"),
    ("copilot", "3B82F6", "Work assigned to GitHub Copilot"),
    
    # Learning system labels
    ("learning", "0E8A16", "Learning system activity"),
    ("learning-assignment", "0E8A16", "Agent learning task"),
    ("learning-source-tldr", "10B981", "From TLDR Tech newsletter"),
    ("learning-source-hn", "F59E0B", "From Hacker News"),
    ("learning-source-trending", "8B5CF6", "From GitHub Trending"),
    
    # Agent system labels
    ("agent-system", "1D76DB", "Agent system related"),
    ("agent-mission", "1D76DB", "Agent mission/task"),
    ("agent-spawner", "2563EB", "Agent creation/spawning"),
    ("performance-metrics", "6366F1", "Agent performance tracking"),
    ("investment-tracker", "8B5CF6", "Agent investment/expertise tracking"),
    ("collaboration", "EC4899", "Multi-agent collaboration"),
    
    # World model labels
    ("world-model", "5319E7", "World model updates"),
    ("world-state", "7C3AED", "World state changes"),
    ("knowledge-graph", "A855F7", "Knowledge graph updates"),
    ("navigation", "C084FC", "Agent navigation/movement"),
    
    # Infrastructure labels
    ("documentation", "0075CA", "Documentation updates"),
    ("testing", "FEF2C0", "Testing related"),
    ("ci-cd", "1F2937", "CI/CD workflows"),
    ("github-pages", "FB923C", "GitHub Pages site"),
    ("pages-health", "FB923C", "GitHub Pages health checks"),
    ("github-actions", "2088FF", "GitHub Actions workflows"),
    
    # Code quality and development labels
    ("code-quality", "D93F0B", "Code quality improvements"),
    ("bug", "D73A4A", "Bug or error fix"),
    ("security", "B60205", "Security related"),
    ("performance", "10B981", "Performance improvements"),
    ("workflow-optimization", "0E8A16", "Workflow optimization"),
    
    # Backlog and planning labels
    ("future-expansion", "FBCA04", "Backlog for future work"),
    ("enhancement", "A2EEEF", "Improvement suggestion"),
    ("idea", "D4C5F9", "New idea proposal"),
    
    # Status labels
    ("status:backlog", "EDEDED", "Not yet started"),
    ("status:ready", "0E8A16", "Ready to begin"),
    ("status:in-progress", "FBCA04", "Currently being worked on"),
    ("status:blocked", "D93F0B", "Waiting on dependencies"),
    ("status:review", "0075CA", "In code review"),
    ("status:testing", "FEF2C0", "Being tested"),
    ("status:done", "0E8A16", "Completed"),
    
    # Priority labels
    ("priority:critical", "B60205", "Urgent, blocks system"),
    ("priority:high", "D93F0B", "Important, should be done soon"),
    ("priority:medium", "FBCA04", "Normal priority"),
    ("priority:low", "0E8A16", "Nice to have"),
]

def create_label(name: str, color: str, description: str, force: bool = True) -> bool:
    """
    Create a single label using gh CLI
    
    Args:
        name: Label name
        color: Hex color code (without #)
        description: Label description
        force: Use --force to update existing labels
    
    Returns:
        True if successful, False otherwise
    """
    cmd = ['gh', 'label', 'create', name, '--description', description, '--color', color]
    
    if force:
        cmd.append('--force')
    
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True
    )
    
    # Success if returncode is 0 or if label already exists
    if result.returncode == 0:
        return True
    elif 'already exists' in result.stderr.lower():
        return True
    else:
        print(f"   Error: {result.stderr.strip()}", file=sys.stderr)
        return False

def create_agent_labels(agent_names: List[str]) -> int:
    """
    Create agent: namespaced labels for all agents
    
    Args:
        agent_names: List of agent names (without agent: prefix)
    
    Returns:
        Number of labels successfully created
    """
    success_count = 0
    
    print("\n🤖 Creating agent labels...")
    print("-" * 60)
    
    for agent in agent_names:
        label_name = f"agent:{agent}"
        description = f"Assigned to {agent} agent"
        
        if create_label(label_name, "1D76DB", description):
            print(f"✅ {label_name}")
            success_count += 1
        else:
            print(f"❌ {label_name}")
    
    return success_count

def create_category_labels(categories: List[str]) -> int:
    """
    Create category: namespaced labels
    
    Args:
        categories: List of category names
    
    Returns:
        Number of labels successfully created
    """
    success_count = 0
    
    print("\n📚 Creating category labels...")
    print("-" * 60)
    
    for category in categories:
        label_name = f"category:{category}"
        description = f"{category.replace('-', ' ').title()} category"
        
        if create_label(label_name, "D4C5F9", description):
            print(f"✅ {label_name}")
            success_count += 1
        else:
            print(f"❌ {label_name}")
    
    return success_count

def create_location_labels(locations: List[str]) -> int:
    """
    Create location: namespaced labels
    
    Args:
        locations: List of location names
    
    Returns:
        Number of labels successfully created
    """
    success_count = 0
    
    print("\n🌍 Creating location labels...")
    print("-" * 60)
    
    for location in locations:
        label_name = f"location:{location}"
        description = f"Ideas originating from {location.replace('-', ' ').title()}"
        
        if create_label(label_name, "FEF2C0", description):
            print(f"✅ {label_name}")
            success_count += 1
        else:
            print(f"❌ {label_name}")
    
    return success_count

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Create standard labels for Chained repository'
    )
    parser.add_argument(
        '--all',
        action='store_true',
        help='Create all standard labels'
    )
    parser.add_argument(
        '--system',
        action='store_true',
        help='Create system labels only'
    )
    parser.add_argument(
        '--agents',
        action='store_true',
        help='Create agent labels'
    )
    parser.add_argument(
        '--categories',
        action='store_true',
        help='Create category labels'
    )
    parser.add_argument(
        '--locations',
        action='store_true',
        help='Create location labels'
    )
    
    args = parser.parse_args()
    
    # If no specific flags, default to --all
    if not any([args.all, args.system, args.agents, args.categories, args.locations]):
        args.all = True
    
    print("🏷️  Chained Label Creator")
    print("=" * 60)
    
    total_success = 0
    total_attempted = 0
    
    # Create system labels
    if args.all or args.system:
        print("\n🏗️  Creating system labels...")
        print("-" * 60)
        
        for name, color, desc in SYSTEM_LABELS:
            total_attempted += 1
            if create_label(name, color, desc):
                print(f"✅ {name}")
                total_success += 1
            else:
                print(f"❌ {name}")
    
    # Create agent labels (from known agents)
    if args.all or args.agents:
        common_agents = [
            "accelerate-master", "accelerate-specialist",
            "assert-specialist", "assert-whiz", "validator-pro", "edge-cases-pro",
            "coach-master", "coach-wizard", "guide-wizard", "support-master",
            "create-guru", "create-champion", "infrastructure-specialist",
            "engineer-master", "engineer-wizard", "develop-specialist",
            "investigate-champion", "investigate-specialist",
            "secure-specialist", "secure-pro", "secure-ninja", "monitor-champion",
            "organize-guru", "organize-expert", "organize-specialist",
            "bridge-master", "integrate-specialist",
            "clarify-champion", "document-ninja", "communicator-maestro",
            "meta-coordinator", "align-wizard", "coordinate-wizard",
            "pioneer-pro", "pioneer-sage",
            "troubleshoot-expert",
        ]
        
        agent_count = create_agent_labels(common_agents)
        total_success += agent_count
        total_attempted += len(common_agents)
    
    # Create category labels
    if args.all or args.categories:
        common_categories = [
            "api-design", "backend", "frontend", "database",
            "security", "performance", "testing", "documentation",
            "devops", "ci-cd", "infrastructure", "machine-learning",
            "ai", "data-science", "mobile", "web", "cloud", "networking",
        ]
        
        category_count = create_category_labels(common_categories)
        total_success += category_count
        total_attempted += len(common_categories)
    
    # Create location labels
    if args.all or args.locations:
        common_locations = [
            "san-francisco", "seattle", "austin", "new-york", "boston",
            "london", "berlin", "paris", "amsterdam",
            "tokyo", "singapore", "bangalore", "beijing",
            "toronto", "sydney", "tel-aviv",
        ]
        
        location_count = create_location_labels(common_locations)
        total_success += location_count
        total_attempted += len(common_locations)
    
    # Summary
    print("\n" + "=" * 60)
    print(f"✅ Created/updated: {total_success}/{total_attempted} labels")
    
    if total_success == total_attempted:
        print("🎉 All labels created successfully!")
        sys.exit(0)
    else:
        failed = total_attempted - total_success
        print(f"⚠️  {failed} labels failed (see errors above)")
        sys.exit(1)

if __name__ == "__main__":
    main()
