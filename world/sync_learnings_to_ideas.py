#!/usr/bin/env python3
"""
Sync Learnings to World Ideas
Converts learning analysis into geographic ideas for the world model.
"""

import json
import os
import sys
from datetime import datetime, timezone
from typing import Dict, List, Any
from pathlib import Path

# Path constants
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
LEARNINGS_DIR = os.path.join(SCRIPT_DIR, '..', 'learnings')
KNOWLEDGE_PATH = os.path.join(SCRIPT_DIR, 'knowledge.json')
WORLD_STATE_PATH = os.path.join(SCRIPT_DIR, 'world_state.json')

# Technology to company/location mapping
TECH_COMPANY_MAP = {
    'ai': [
        {'name': 'OpenAI', 'city': 'San Francisco', 'country': 'US', 'lat': 37.7749, 'lng': -122.4194},
        {'name': 'DeepMind', 'city': 'London', 'country': 'GB', 'lat': 51.5074, 'lng': -0.1278},
        {'name': 'Anthropic', 'city': 'San Francisco', 'country': 'US', 'lat': 37.7749, 'lng': -122.4194}
    ],
    'cloud': [
        {'name': 'AWS', 'city': 'Seattle', 'country': 'US', 'lat': 47.6062, 'lng': -122.3321},
        {'name': 'Microsoft Azure', 'city': 'Redmond', 'country': 'US', 'lat': 47.674, 'lng': -122.1215},
        {'name': 'Google Cloud', 'city': 'San Francisco', 'country': 'US', 'lat': 37.7749, 'lng': -122.4194}
    ],
    'agents': [
        {'name': 'OpenAI', 'city': 'San Francisco', 'country': 'US', 'lat': 37.7749, 'lng': -122.4194},
        {'name': 'Microsoft', 'city': 'Redmond', 'country': 'US', 'lat': 47.674, 'lng': -122.1215}
    ],
    'security': [
        {'name': 'Cloudflare', 'city': 'San Francisco', 'country': 'US', 'lat': 37.7749, 'lng': -122.4194},
        {'name': 'CrowdStrike', 'city': 'Austin', 'country': 'US', 'lat': 30.2672, 'lng': -97.7431}
    ],
    'database': [
        {'name': 'MongoDB', 'city': 'New York', 'country': 'US', 'lat': 40.7128, 'lng': -74.006},
        {'name': 'Redis', 'city': 'San Francisco', 'country': 'US', 'lat': 37.7749, 'lng': -122.4194}
    ],
    'devops': [
        {'name': 'GitHub', 'city': 'San Francisco', 'country': 'US', 'lat': 37.7749, 'lng': -122.4194},
        {'name': 'GitLab', 'city': 'San Francisco', 'country': 'US', 'lat': 37.7749, 'lng': -122.4194}
    ]
}


def load_json_file(filepath: str) -> Dict[str, Any]:
    """Load a JSON file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_json_file(filepath: str, data: Dict[str, Any]) -> None:
    """Save data to a JSON file."""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def get_latest_analysis_file() -> str:
    """Get the most recent analysis file from learnings directory."""
    analysis_files = sorted(
        Path(LEARNINGS_DIR).glob('analysis_*.json'),
        key=lambda p: p.stat().st_mtime,
        reverse=True
    )
    
    if not analysis_files:
        raise FileNotFoundError("No analysis files found in learnings directory")
    
    return str(analysis_files[0])


def create_idea_from_technology(tech: Dict[str, Any], idea_id_base: int) -> Dict[str, Any]:
    """
    Create a world idea from a technology trend.
    
    Args:
        tech: Technology dict from analysis
        idea_id_base: Base number for idea ID
        
    Returns:
        Idea dict for knowledge base
    """
    tech_name = tech.get('name', 'unknown').lower()
    category = tech.get('category', 'General')
    mention_count = tech.get('mention_count', 0)
    sample_titles = tech.get('sample_titles', [])
    
    # Get companies associated with this tech
    companies = TECH_COMPANY_MAP.get(tech_name, [
        {'name': 'Tech Hub', 'city': 'San Francisco', 'country': 'US', 
         'lat': 37.7749, 'lng': -122.4194}
    ])
    
    # Create inspiration regions from companies
    inspiration_regions = []
    region_weights = {}
    
    for company in companies:
        region_id = f"{company['country']}:{company['city']}"
        if region_id not in region_weights:
            region_weights[region_id] = 0
        region_weights[region_id] += 1.0 / len(companies)
    
    for region_id, weight in region_weights.items():
        company = next(c for c in companies if f"{c['country']}:{c['city']}" == region_id)
        inspiration_regions.append({
            'region_id': region_id,
            'lat': company['lat'],
            'lng': company['lng'],
            'weight': round(weight, 2)
        })
    
    # Create idea
    idea = {
        'id': f"idea:{idea_id_base}",
        'title': f"{category}: {tech_name.title()} Innovation",
        'summary': f"Exploring {tech_name} trends with {mention_count} mentions. " + 
                   (sample_titles[0][:80] + '...' if sample_titles else 'Hot topic in tech.'),
        'patterns': [tech_name, category.lower()],
        'companies': companies,
        'inspiration_regions': inspiration_regions,
        'source': 'learning_analysis',
        'mention_count': mention_count,
        'created_at': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    }
    
    return idea


def update_world_state_regions(world_state: Dict[str, Any], ideas: List[Dict[str, Any]]) -> None:
    """Update region idea counts in world state."""
    region_idea_counts = {}
    
    # Count ideas per region
    for idea in ideas:
        for insp_region in idea.get('inspiration_regions', []):
            region_id = insp_region.get('region_id')
            if region_id:
                region_idea_counts[region_id] = region_idea_counts.get(region_id, 0) + 1
    
    # Update world state regions
    regions = world_state.get('regions', [])
    for region in regions:
        region_id = region.get('id')
        if region_id in region_idea_counts:
            region['idea_count'] = region_idea_counts[region_id]
    
    # Add new regions from ideas if needed
    existing_region_ids = {r.get('id') for r in regions}
    for idea in ideas:
        for insp_region in idea.get('inspiration_regions', []):
            region_id = insp_region.get('region_id')
            if region_id and region_id not in existing_region_ids:
                # Extract city and country from region_id (format: "US:San Francisco")
                parts = region_id.split(':', 1)
                if len(parts) == 2:
                    country, city = parts
                    new_region = {
                        'id': region_id,
                        'label': city,
                        'lat': insp_region.get('lat'),
                        'lng': insp_region.get('lng'),
                        'idea_count': region_idea_counts.get(region_id, 0)
                    }
                    regions.append(new_region)
                    existing_region_ids.add(region_id)
                    print(f"   ✓ Added new region: {city} ({region_id})")
    
    world_state['regions'] = regions


def sync_learnings_to_ideas(max_ideas: int = 10) -> Dict[str, Any]:
    """
    Main sync function: Load latest analysis, create ideas, update world.
    
    Args:
        max_ideas: Maximum number of ideas to create from top technologies
        
    Returns:
        Summary of sync operation
    """
    print("=" * 70)
    print("💡 Syncing Learning Analysis to World Ideas")
    print("=" * 70)
    
    # Load latest analysis
    print(f"\n📖 Loading latest learning analysis...")
    analysis_file = get_latest_analysis_file()
    print(f"   Using: {os.path.basename(analysis_file)}")
    analysis = load_json_file(analysis_file)
    
    # Extract top technologies
    top_technologies = analysis.get('top_technologies', [])[:max_ideas]
    print(f"   Found {len(top_technologies)} top technologies")
    
    # Load knowledge base
    print(f"\n📚 Loading knowledge base...")
    knowledge = load_json_file(KNOWLEDGE_PATH)
    existing_ideas = knowledge.get('ideas', [])
    print(f"   Current ideas: {len(existing_ideas)}")
    
    # Create new ideas from technologies
    print(f"\n💡 Creating ideas from technologies...")
    new_ideas = []
    idea_id_base = len(existing_ideas) + 1
    
    for i, tech in enumerate(top_technologies):
        idea = create_idea_from_technology(tech, idea_id_base + i)
        new_ideas.append(idea)
        print(f"   ✓ {idea['title']} (mentions: {tech.get('mention_count', 0)})")
    
    # Add new ideas to knowledge (replace old learning-based ideas)
    # Keep only non-learning ideas
    other_ideas = [idea for idea in existing_ideas if idea.get('source') != 'learning_analysis']
    all_ideas = other_ideas + new_ideas
    knowledge['ideas'] = all_ideas
    
    # Save knowledge base
    print(f"\n💾 Saving updated knowledge base...")
    save_json_file(KNOWLEDGE_PATH, knowledge)
    print(f"   ✓ Total ideas now: {len(all_ideas)}")
    
    # Load and update world state
    print(f"\n🌍 Updating world state regions...")
    world_state = load_json_file(WORLD_STATE_PATH)
    update_world_state_regions(world_state, all_ideas)
    
    # Update metrics
    world_state['metrics']['total_ideas'] = len(all_ideas)
    world_state['time'] = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    
    # Save world state
    save_json_file(WORLD_STATE_PATH, world_state)
    print(f"   ✓ Regions updated")
    
    summary = {
        'analysis_file': os.path.basename(analysis_file),
        'technologies_analyzed': len(top_technologies),
        'ideas_created': len(new_ideas),
        'total_ideas': len(all_ideas),
        'timestamp': world_state['time']
    }
    
    print("\n" + "=" * 70)
    print("✅ Sync Complete!")
    print("=" * 70)
    print(f"Technologies analyzed: {summary['technologies_analyzed']}")
    print(f"New ideas created: {summary['ideas_created']}")
    print(f"Total ideas in system: {summary['total_ideas']}")
    print(f"Timestamp: {summary['timestamp']}")
    print("=" * 70)
    
    return summary


def main():
    """Main entry point."""
    try:
        summary = sync_learnings_to_ideas(max_ideas=10)
        return 0
    except Exception as e:
        print(f"\n❌ Error during sync: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
