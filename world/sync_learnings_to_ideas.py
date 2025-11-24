#!/usr/bin/env python3
"""
Sync Learnings to World Ideas
Converts learning analysis into geographic ideas for the world model.

**@align-wizard** Enhancement: Preserves existing ideas and mission state
to prevent duplicate missions and ensure continuous learning progress.
"""

import json
import os
import sys
import hashlib
from datetime import datetime, timezone
from typing import Dict, List, Any
from pathlib import Path

# Path constants
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
LEARNINGS_DIR = os.path.join(SCRIPT_DIR, '..', 'learnings')
KNOWLEDGE_PATH = os.path.join(SCRIPT_DIR, 'knowledge.json')
WORLD_STATE_PATH = os.path.join(SCRIPT_DIR, 'world_state.json')

# Configuration constants
# How long to retain old learning ideas (in days) before archiving
IDEA_RETENTION_DAYS = 7

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


def create_combination_ideas(technologies: List[Dict[str, Any]], max_combinations: int = 3) -> List[Dict[str, Any]]:
    """
    **@construct-specialist** Enhancement: Create combination/integration ideas.
    
    These ideas explore synergies between different technologies.
    
    Args:
        technologies: List of technology trends
        max_combinations: Maximum number of combination ideas to create
        
    Returns:
        List of combination idea dicts
    """
    import random
    
    combination_ideas = []
    
    # Define interesting combination patterns
    ai_keywords = {'ai', 'ml', 'agents', 'llm', 'claude', 'gpt'}
    infra_keywords = {'cloud', 'devops', 'kubernetes', 'docker', 'infrastructure'}
    security_keywords = {'security', 'authentication', 'encryption', 'vulnerability'}
    web_keywords = {'web', 'api', 'frontend', 'backend', 'javascript'}
    
    # Find technologies in different categories
    ai_techs = [t for t in technologies if any(kw in t.get('keywords', []) for kw in ai_keywords)]
    infra_techs = [t for t in technologies if any(kw in t.get('keywords', []) for kw in infra_keywords)]
    security_techs = [t for t in technologies if any(kw in t.get('keywords', []) for kw in security_keywords)]
    web_techs = [t for t in technologies if any(kw in t.get('keywords', []) for kw in web_keywords)]
    
    # Create interesting combinations
    combinations = [
        ('AI + Infrastructure', ai_techs, infra_techs, 'Integrate AI capabilities with cloud infrastructure'),
        ('Security + AI', security_techs, ai_techs, 'Apply AI/ML to enhance security systems'),
        ('Web + AI', web_techs, ai_techs, 'Build AI-powered web applications'),
        ('Cloud + Security', infra_techs, security_techs, 'Secure cloud infrastructure and deployments'),
    ]
    
    for combo_title, list1, list2, combo_desc in combinations:
        if len(combination_ideas) >= max_combinations:
            break
            
        if list1 and list2:
            # Pick one from each list
            tech1 = random.choice(list1) if list1 else None
            tech2 = random.choice(list2) if list2 else None
            
            if tech1 and tech2:
                name1 = tech1.get('name', 'unknown').title()
                name2 = tech2.get('name', 'unknown').title()
                
                combination_ideas.append({
                    'name': f"{name1}-{name2}".lower(),
                    'category': 'Integration',
                    'mention_count': (tech1.get('mention_count', 0) + tech2.get('mention_count', 0)) // 2,
                    'score': 80.0,  # Good score for combinations
                    'sample_titles': [
                        f"{combo_title}: {combo_desc}",
                        f"Combining {name1} and {name2} for better solutions"
                    ],
                    'keywords': tech1.get('keywords', []) + tech2.get('keywords', []),
                    'is_combination': True,
                    'combined_from': [tech1.get('name'), tech2.get('name')]
                })
    
    return combination_ideas


def create_idea_from_technology(tech: Dict[str, Any], idea_id_base: int, is_deep_discovery: bool = False) -> Dict[str, Any]:
    """
    Create a world idea from a technology trend.
    
    Args:
        tech: Technology dict from analysis
        idea_id_base: Base number for idea ID
        is_deep_discovery: Whether this is from deep discovery mode (affects title format)
        
    Returns:
        Idea dict for knowledge base
    """
    tech_name = tech.get('name', 'unknown').lower()
    category = tech.get('category', 'General')
    mention_count = tech.get('mention_count', 0)
    sample_titles = tech.get('sample_titles', [])
    keywords = tech.get('keywords', [tech_name])
    
    # **@construct-specialist** Enhancement: Better pattern extraction
    # Extract more patterns from keywords and category
    patterns = list(set([tech_name] + keywords + [category.lower().replace(' ', '_')]))
    
    # **@troubleshoot-expert** Fix: Include sample title hash in patterns for uniqueness
    # Uses MD5 hash of first sample title to create stable, collision-resistant fingerprint
    # This is an additional uniqueness signal (date pattern is the primary one)
    if sample_titles:
        # Use hash of first sample title for stable fingerprint
        title_hash = hashlib.md5(sample_titles[0].encode()).hexdigest()[:8]
        patterns.append(f"topic:{title_hash}")
    
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
    
    # **@construct-specialist** Enhancement: More descriptive summaries with context
    summary_base = f"Exploring {tech_name} trends with {mention_count} mentions"
    if sample_titles:
        # Use first title for context
        summary_base += f". {sample_titles[0][:100]}"
        if len(sample_titles) > 1:
            summary_base += f" Also: {sample_titles[1][:80]}"
    else:
        summary_base += ". Hot topic in tech."
    
    # **@troubleshoot-expert** Fix: Include date in title for daily mission generation
    # This ensures each day's analysis creates new ideas that can spawn missions
    today_str = datetime.now(timezone.utc).strftime('%Y-%m-%d')
    
    # Create idea with enhanced title based on category - include date for uniqueness
    if category == 'Company Innovation':
        title = f"{tech_name.title()} Innovation ({today_str})"
    elif category == 'Emerging Theme':
        title = f"Emerging Theme: {tech_name.replace('-', ' ').title()} ({today_str})"
    else:
        title = f"{category}: {tech_name.title()} ({today_str})"
    
    # Add date pattern for hash uniqueness
    date_pattern = f"date:{today_str}"
    if date_pattern not in patterns:
        patterns.append(date_pattern)
    
    idea = {
        'id': f"idea:{idea_id_base}",
        'title': title,
        'summary': summary_base,
        'patterns': patterns,
        'companies': companies,
        'inspiration_regions': inspiration_regions,
        'source': 'learning_analysis',
        'mention_count': mention_count,
        'category': category,
        'analysis_date': today_str,  # Track which day's analysis created this idea
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


def generate_idea_content_hash(idea: Dict[str, Any]) -> str:
    """
    Generate a content hash for an idea based on its core attributes.
    
    This hash is used to detect when ideas are truly the same, even if
    they're regenerated from new learning analysis runs.
    
    Args:
        idea: Idea dict
        
    Returns:
        MD5 hash of idea content
    """
    # Use title and patterns to identify unique ideas
    # (Don't use mention_count or other volatile fields)
    title = idea.get('title', '')
    patterns = sorted(idea.get('patterns', []))
    category = idea.get('category', '')
    
    content = f"{title}:{category}:{':'.join(patterns)}"
    return hashlib.md5(content.encode()).hexdigest()


def sync_learnings_to_ideas(max_ideas: int = 10, enable_deep_discovery: bool = True) -> Dict[str, Any]:
    """
    Main sync function: Load latest analysis, create ideas, update world.
    
    **@align-wizard** Enhancement: Preserves existing ideas and their mission state.
    Only adds truly new ideas based on content hash deduplication.
    
    Args:
        max_ideas: Maximum number of ideas to create from top technologies
        enable_deep_discovery: Enable deeper topic exploration for more mission diversity
        
    Returns:
        Summary of sync operation
    """
    print("=" * 70)
    print("💡 Syncing Learning Analysis to World Ideas (@align-wizard)")
    print("=" * 70)
    
    # Load latest analysis
    print(f"\n📖 Loading latest learning analysis...")
    analysis_file = get_latest_analysis_file()
    print(f"   Using: {os.path.basename(analysis_file)}")
    analysis = load_json_file(analysis_file)
    
    # Extract top technologies
    top_technologies = analysis.get('top_technologies', [])[:max_ideas]
    print(f"   Found {len(top_technologies)} top technologies")
    
    # **@construct-specialist** Enhancement: Deep Discovery Mode
    if enable_deep_discovery:
        print(f"\n🔍 Deep Discovery Mode: Exploring additional topics...")
        
        # Also extract from companies, hot_themes, and create combination ideas
        top_companies = analysis.get('top_companies', [])[:5]
        hot_themes = analysis.get('hot_themes', [])
        
        print(f"   Companies: {len(top_companies)}")
        print(f"   Hot themes: {len(hot_themes)}")
        
        # Add companies as technology opportunities
        for company in top_companies:
            # Convert company to tech opportunity format
            tech_opportunity = {
                'name': company.get('name', 'unknown').lower(),
                'category': 'Company Innovation',
                'mention_count': company.get('mention_count', 0),
                'score': company.get('score', 0),
                'sample_titles': company.get('sample_titles', [])[:2],
                'keywords': company.get('keywords', [])
            }
            top_technologies.append(tech_opportunity)
        
        # Add hot themes as exploration areas
        for theme in hot_themes:
            # Create a theme-based technology entry
            theme_parts = theme.split('-')
            theme_tech = {
                'name': theme,
                'category': 'Emerging Theme',
                'mention_count': 10,  # Default for themes
                'score': 75.0,  # Good score for hot themes
                'sample_titles': [f"Explore {theme.replace('-', ' ').title()} innovations"],
                'keywords': theme_parts
            }
            top_technologies.append(theme_tech)
        
        print(f"   ✓ Expanded from {len(analysis.get('top_technologies', [])[:max_ideas])} to {len(top_technologies)} opportunities")
    
    # Load knowledge base
    print(f"\n📚 Loading knowledge base...")
    knowledge = load_json_file(KNOWLEDGE_PATH)
    existing_ideas = knowledge.get('ideas', [])
    print(f"   Current ideas: {len(existing_ideas)}")
    
    # **@align-wizard** Enhancement: Build hash map of existing learning ideas
    # This preserves mission state and prevents duplicate idea creation
    existing_learning_ideas = [idea for idea in existing_ideas if idea.get('source') == 'learning_analysis']
    existing_content_hashes = {}
    
    for idea in existing_learning_ideas:
        content_hash = generate_idea_content_hash(idea)
        existing_content_hashes[content_hash] = idea
    
    print(f"   Existing learning ideas: {len(existing_learning_ideas)}")
    print(f"   Content hashes: {len(existing_content_hashes)}")
    
    # Create new ideas from technologies
    print(f"\n💡 Processing technologies for ideas...")
    new_ideas = []
    updated_ideas = []
    skipped_duplicates = 0
    
    # **@APIs-architect** Fix: Use max ID instead of count to prevent duplicate IDs
    # Extract numeric IDs and find the maximum
    max_id = 0
    for idea in existing_ideas:
        idea_id = idea.get('id', 'idea:0')
        if idea_id.startswith('idea:'):
            try:
                num = int(idea_id.split(':')[1])
                max_id = max(max_id, num)
            except (ValueError, IndexError):
                pass
    
    idea_id_base = max_id + 1
    
    for i, tech in enumerate(top_technologies):
        # Create candidate idea
        candidate_idea = create_idea_from_technology(tech, idea_id_base + len(new_ideas))
        candidate_hash = generate_idea_content_hash(candidate_idea)
        
        # Check if this idea already exists
        if candidate_hash in existing_content_hashes:
            # Idea exists - preserve it with its mission state
            existing_idea = existing_content_hashes[candidate_hash]
            
            # Update mention count if it changed significantly
            old_mentions = existing_idea.get('mention_count', 0)
            new_mentions = tech.get('mention_count', 0)
            
            if abs(new_mentions - old_mentions) > 5:
                existing_idea['mention_count'] = new_mentions
                existing_idea['updated_at'] = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
                updated_ideas.append(existing_idea)
                print(f"   ↻ Updated: {existing_idea['title'][:50]} (mentions: {old_mentions} → {new_mentions})")
            else:
                print(f"   ✓ Kept: {existing_idea['title'][:50]} (unchanged)")
            
            skipped_duplicates += 1
        else:
            # Truly new idea
            new_ideas.append(candidate_idea)
            print(f"   + New: {candidate_idea['title']} (mentions: {tech.get('mention_count', 0)})")
    
    # **@construct-specialist** Enhancement: Add combination ideas for synergy
    if enable_deep_discovery and len(top_technologies) >= 2:
        print(f"\n🔗 Creating combination/integration ideas...")
        combination_ideas = create_combination_ideas(top_technologies, max_combinations=3)
        
        for combo_idea in combination_ideas:
            candidate_idea = create_idea_from_technology(combo_idea, idea_id_base + len(new_ideas), is_deep_discovery=True)
            candidate_hash = generate_idea_content_hash(candidate_idea)
            
            if candidate_hash not in existing_content_hashes:
                new_ideas.append(candidate_idea)
                print(f"   + New integration: {candidate_idea['title']}")
            else:
                skipped_duplicates += 1
                print(f"   ✓ Kept: {existing_content_hashes[candidate_hash]['title'][:50]} (combination exists)")
        
        print(f"   Created {len([i for i in new_ideas if i.get('is_combination')])} new combination ideas")
    
    # **@align-wizard** Enhancement: Merge ideas intelligently
    # Keep non-learning ideas + existing learning ideas + new learning ideas
    other_ideas = [idea for idea in existing_ideas if idea.get('source') != 'learning_analysis']
    
    # **@troubleshoot-expert** Fix: Cleanup old learning ideas to prevent unbounded growth
    # Keep ideas without missions (regardless of age) + recent ideas with missions
    # This prevents the knowledge base from growing indefinitely with daily ideas
    from datetime import timedelta
    cutoff_date = (datetime.now(timezone.utc) - timedelta(days=IDEA_RETENTION_DAYS)).strftime('%Y-%m-%d')
    
    retained_learning_ideas = []
    archived_count = 0
    for idea in list(existing_content_hashes.values()):
        # Keep ideas that:
        # 1. Don't have mission_created (still waiting for missions) - keep regardless of age
        # 2. Have mission_created AND analysis_date within retention period
        # 3. Have mission_created AND no analysis_date (old format) - archive these as they're legacy
        analysis_date = idea.get('analysis_date', '')
        has_mission = idea.get('mission_created', False)
        
        if not has_mission:
            # Always keep ideas without missions - they need missions!
            retained_learning_ideas.append(idea)
        elif analysis_date and analysis_date >= cutoff_date:
            # Recent ideas with missions - keep them for reference
            retained_learning_ideas.append(idea)
        else:
            # Old ideas with missions (with or without analysis_date) - archive them
            archived_count += 1
    
    if archived_count > 0:
        print(f"\n🗑️  Archived {archived_count} old learning ideas (older than {IDEA_RETENTION_DAYS} days with missions)")
    
    all_ideas = other_ideas + retained_learning_ideas + new_ideas
    
    print(f"\n📊 Sync Summary:")
    print(f"   Existing learning ideas preserved: {len(existing_content_hashes)}")
    print(f"   New ideas added: {len(new_ideas)}")
    print(f"   Ideas updated: {len(updated_ideas)}")
    print(f"   Duplicates skipped: {skipped_duplicates}")
    
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
        # **@construct-specialist** Enhancement: Enable deep discovery by default
        # **@APIs-architect** Enhancement: Increased from 10 to 20 for more mission diversity
        # This creates more diverse missions from learning topics
        summary = sync_learnings_to_ideas(max_ideas=20, enable_deep_discovery=True)
        return 0
    except Exception as e:
        print(f"\n❌ Error during sync: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
