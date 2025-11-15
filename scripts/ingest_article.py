#!/usr/bin/env python3
"""
Article Ingestion Pipeline
Processes articles into ideas with inspiration regions for the world model.
"""

import sys
import os
import json
import argparse
from datetime import datetime
from typing import Dict, List, Any

# Add world directory to path
WORLD_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'world')
sys.path.insert(0, WORLD_DIR)

from world_state_manager import load_world_state, save_world_state, add_or_update_region, get_region_by_id
from knowledge_manager import load_knowledge, save_knowledge, add_idea, create_idea_from_article, get_region_list_from_ideas


# Sample company headquarters database (would be expanded or fetched from an API)
COMPANY_HQ_DATABASE = {
    "OpenAI": {"city": "San Francisco", "country": "US", "lat": 37.7749, "lng": -122.4194},
    "Google": {"city": "Mountain View", "country": "US", "lat": 37.3861, "lng": -122.0839},
    "Microsoft": {"city": "Redmond", "country": "US", "lat": 47.6740, "lng": -122.1215},
    "Amazon": {"city": "Seattle", "country": "US", "lat": 47.6062, "lng": -122.3321},
    "Meta": {"city": "Menlo Park", "country": "US", "lat": 37.4529, "lng": -122.1817},
    "Apple": {"city": "Cupertino", "country": "US", "lat": 37.3230, "lng": -122.0322},
    "TSMC": {"city": "Hsinchu", "country": "TW", "lat": 24.8138, "lng": 120.9675},
    "Samsung": {"city": "Seoul", "country": "KR", "lat": 37.5665, "lng": 126.9780},
    "Alibaba": {"city": "Hangzhou", "country": "CN", "lat": 30.2741, "lng": 120.1551},
    "Tencent": {"city": "Shenzhen", "country": "CN", "lat": 22.5431, "lng": 114.0579},
    "GitHub": {"city": "San Francisco", "country": "US", "lat": 37.7749, "lng": -122.4194},
    "Stripe": {"city": "San Francisco", "country": "US", "lat": 37.7749, "lng": -122.4194},
    "Netflix": {"city": "Los Gatos", "country": "US", "lat": 37.2358, "lng": -121.9623},
    "Spotify": {"city": "Stockholm", "country": "SE", "lat": 59.3293, "lng": 18.0686},
    "DeepMind": {"city": "London", "country": "GB", "lat": 51.5074, "lng": -0.1278},
}


def extract_companies_from_text(text: str) -> List[str]:
    """
    Extract company names from article text.
    This is a simple stub - would use NLP/LLM in production.
    """
    companies = []
    text_upper = text.upper()
    
    for company_name in COMPANY_HQ_DATABASE.keys():
        if company_name.upper() in text_upper:
            companies.append(company_name)
    
    return companies


def extract_patterns_from_text(text: str) -> List[str]:
    """
    Extract technical patterns from article text.
    This is a stub - would use NLP/LLM in production.
    """
    # Simple keyword-based pattern detection
    pattern_keywords = {
        'ci_automation': ['ci', 'continuous integration', 'pipeline'],
        'self_healing': ['self-healing', 'auto-fix', 'automated repair'],
        'ai_ml': ['ai', 'machine learning', 'neural network', 'llm'],
        'distributed_systems': ['distributed', 'microservices', 'kubernetes'],
        'security': ['security', 'encryption', 'authentication'],
        'performance': ['performance', 'optimization', 'scaling'],
        'testing': ['testing', 'test automation', 'qa'],
        'devops': ['devops', 'infrastructure', 'deployment'],
    }
    
    patterns = []
    text_lower = text.lower()
    
    for pattern, keywords in pattern_keywords.items():
        for keyword in keywords:
            if keyword in text_lower:
                patterns.append(pattern)
                break
    
    return patterns


def ingest_article(
    url: str = None,
    title: str = None,
    text: str = None,
    summary: str = None
) -> Dict[str, Any]:
    """
    Ingest an article and convert it to an idea.
    
    Args:
        url: Article URL (optional, for reference)
        title: Article title
        text: Article text content
        summary: Pre-written summary (if None, will be extracted from text)
    
    Returns:
        Dict with status and created idea
    """
    if not title or not text:
        return {"success": False, "error": "Title and text are required"}
    
    # Extract companies mentioned
    company_names = extract_companies_from_text(text)
    
    # Build company list with HQ information
    companies = []
    for company_name in company_names:
        hq = COMPANY_HQ_DATABASE.get(company_name)
        if hq:
            companies.append({
                "name": company_name,
                "hq_city": hq["city"],
                "hq_country": hq["country"],
                "lat": hq["lat"],
                "lng": hq["lng"]
            })
    
    # Extract patterns
    patterns = extract_patterns_from_text(text)
    
    # Create summary if not provided (simple stub)
    if not summary:
        sentences = text.split('.')[:3]  # First 3 sentences
        summary = '. '.join(sentences).strip() + '.'
    
    # Create idea object
    idea = create_idea_from_article(title, summary, patterns, companies)
    
    # Add URL if provided
    if url:
        idea['url'] = url
    
    # Load knowledge and add idea
    knowledge = load_knowledge()
    idea_id = add_idea(knowledge, idea)
    save_knowledge(knowledge)
    
    # Update world state with new regions
    world_state = load_world_state()
    
    # Add/update regions from idea
    for insp_region in idea.get('inspiration_regions', []):
        region_id = insp_region['region_id']
        existing_region = get_region_by_id(world_state, region_id)
        
        if not existing_region:
            # Create new region
            parts = region_id.split(':', 1)
            label = parts[1] if len(parts) > 1 else region_id
            
            add_or_update_region(world_state, {
                'id': region_id,
                'label': label,
                'lat': insp_region['lat'],
                'lng': insp_region['lng'],
                'idea_count': 1
            })
        else:
            # Update idea count
            existing_region['idea_count'] = existing_region.get('idea_count', 0) + 1
    
    # Update metrics
    world_state['metrics']['total_ideas'] = len(knowledge['ideas'])
    
    save_world_state(world_state)
    
    return {
        "success": True,
        "idea_id": idea_id,
        "regions_added": len(idea.get('inspiration_regions', [])),
        "companies_found": len(companies),
        "patterns_found": len(patterns)
    }


def main():
    parser = argparse.ArgumentParser(description='Ingest an article into the world model')
    parser.add_argument('--url', help='Article URL')
    parser.add_argument('--title', required=True, help='Article title')
    parser.add_argument('--text', required=True, help='Article text content')
    parser.add_argument('--summary', help='Article summary (optional)')
    
    args = parser.parse_args()
    
    result = ingest_article(
        url=args.url,
        title=args.title,
        text=args.text,
        summary=args.summary
    )
    
    if result['success']:
        print(f"✅ Article ingested successfully!")
        print(f"   Idea ID: {result['idea_id']}")
        print(f"   Companies: {result['companies_found']}")
        print(f"   Patterns: {result['patterns_found']}")
        print(f"   Regions: {result['regions_added']}")
    else:
        print(f"❌ Failed: {result.get('error')}")
        sys.exit(1)


if __name__ == '__main__':
    main()
