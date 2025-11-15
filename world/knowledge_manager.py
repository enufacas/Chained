#!/usr/bin/env python3
"""
Knowledge Manager
Manages ideas and their associated inspiration regions in the world knowledge base.
"""

import json
import os
from typing import Dict, List, Optional, Any

WORLD_DIR = os.path.dirname(os.path.abspath(__file__))
KNOWLEDGE_FILE = os.path.join(WORLD_DIR, "knowledge.json")


def load_knowledge() -> Dict[str, Any]:
    """Load the knowledge base from disk."""
    if not os.path.exists(KNOWLEDGE_FILE):
        return {"ideas": []}
    
    with open(KNOWLEDGE_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_knowledge(knowledge: Dict[str, Any]) -> None:
    """Save the knowledge base to disk."""
    with open(KNOWLEDGE_FILE, 'w', encoding='utf-8') as f:
        json.dump(knowledge, f, indent=2, ensure_ascii=False)


def add_idea(knowledge: Dict[str, Any], idea: Dict[str, Any]) -> str:
    """
    Add a new idea to the knowledge base.
    Returns the idea ID.
    """
    if 'ideas' not in knowledge:
        knowledge['ideas'] = []
    
    # Ensure idea has an ID
    if 'id' not in idea:
        idea_num = len(knowledge['ideas']) + 1
        idea['id'] = f"idea:{idea_num}"
    
    knowledge['ideas'].append(idea)
    return idea['id']


def get_idea_by_id(knowledge: Dict[str, Any], idea_id: str) -> Optional[Dict[str, Any]]:
    """Get an idea by ID."""
    for idea in knowledge.get('ideas', []):
        if idea.get('id') == idea_id:
            return idea
    return None


def get_all_ideas(knowledge: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Get all ideas."""
    return knowledge.get('ideas', [])


def get_ideas_for_region(knowledge: Dict[str, Any], region_id: str) -> List[Dict[str, Any]]:
    """Get all ideas that have the specified region in their inspiration_regions."""
    matching_ideas = []
    for idea in knowledge.get('ideas', []):
        for region in idea.get('inspiration_regions', []):
            if region.get('region_id') == region_id:
                matching_ideas.append(idea)
                break
    return matching_ideas


def count_ideas_per_region(knowledge: Dict[str, Any]) -> Dict[str, int]:
    """Count how many ideas are associated with each region."""
    region_counts = {}
    for idea in knowledge.get('ideas', []):
        for region in idea.get('inspiration_regions', []):
            region_id = region.get('region_id')
            if region_id:
                region_counts[region_id] = region_counts.get(region_id, 0) + 1
    return region_counts


def create_idea_from_article(
    title: str,
    summary: str,
    patterns: List[str],
    companies: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Create an idea object from article data.
    
    Args:
        title: Article title
        summary: Article summary (2-3 sentences)
        patterns: List of pattern tags
        companies: List of company dicts with name, hq_city, hq_country, lat, lng
    
    Returns:
        Complete idea object ready to be added to knowledge base
    """
    # Calculate inspiration regions from company HQs
    inspiration_regions = []
    region_weights = {}
    
    for company in companies:
        region_id = f"{company['hq_country']}:{company['hq_city']}"
        if region_id not in region_weights:
            region_weights[region_id] = {
                'region_id': region_id,
                'lat': company['lat'],
                'lng': company['lng'],
                'count': 0
            }
        region_weights[region_id]['count'] += 1
    
    # Normalize weights
    total = sum(r['count'] for r in region_weights.values())
    for region_id, region_data in region_weights.items():
        inspiration_regions.append({
            'region_id': region_id,
            'lat': region_data['lat'],
            'lng': region_data['lng'],
            'weight': region_data['count'] / total if total > 0 else 0
        })
    
    idea = {
        "title": title,
        "summary": summary,
        "patterns": patterns,
        "companies": companies,
        "inspiration_regions": inspiration_regions
    }
    
    return idea


def get_region_list_from_ideas(knowledge: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Extract a list of unique regions from all ideas.
    Returns list of region dicts with id, label, lat, lng, idea_count.
    """
    regions = {}
    idea_counts = count_ideas_per_region(knowledge)
    
    for idea in knowledge.get('ideas', []):
        for insp_region in idea.get('inspiration_regions', []):
            region_id = insp_region.get('region_id')
            if region_id and region_id not in regions:
                # Extract city name from region_id (Country:City)
                parts = region_id.split(':', 1)
                label = parts[1] if len(parts) > 1 else region_id
                
                regions[region_id] = {
                    'id': region_id,
                    'label': label,
                    'lat': insp_region.get('lat'),
                    'lng': insp_region.get('lng'),
                    'idea_count': idea_counts.get(region_id, 0)
                }
    
    return list(regions.values())


if __name__ == '__main__':
    # Test the module
    knowledge = load_knowledge()
    print("Current knowledge base:")
    print(f"  Total ideas: {len(knowledge.get('ideas', []))}")
    
    region_counts = count_ideas_per_region(knowledge)
    print(f"  Ideas per region: {region_counts}")
