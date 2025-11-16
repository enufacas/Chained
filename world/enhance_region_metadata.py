#!/usr/bin/env python3
"""
Enhance Region Metadata
Adds timezone, region type, tech ecosystem, and other metadata to regions.
"""

import json
import os
from typing import Dict, Any

WORLD_DIR = os.path.dirname(os.path.abspath(__file__))
WORLD_STATE_FILE = os.path.join(WORLD_DIR, "world_state.json")

# Region metadata database
REGION_METADATA = {
    "US:Charlotte": {
        "timezone": "America/New_York",
        "utc_offset": -5,
        "region_type": "home_base",
        "tech_ecosystem": {
            "company_count": 50,
            "startup_count": 200,
            "specializations": ["fintech", "cloud", "data"]
        },
        "cost_multiplier": 1.0,
        "agent_capacity": 100,
        "description": "Home base for all Chained autonomous agents"
    },
    "US:San Francisco": {
        "timezone": "America/Los_Angeles",
        "utc_offset": -8,
        "region_type": "innovation_hub",
        "tech_ecosystem": {
            "company_count": 400,
            "startup_count": 2000,
            "specializations": ["ai_ml", "web3", "saas", "fintech"]
        },
        "cost_multiplier": 2.0,
        "agent_capacity": 20,
        "specialization_bonuses": {
            "create-guru": 1.5,
            "pioneer-pro": 1.4,
            "engineer-master": 1.3
        }
    },
    "US:Seattle": {
        "timezone": "America/Los_Angeles",
        "utc_offset": -8,
        "region_type": "tech_hub",
        "tech_ecosystem": {
            "company_count": 300,
            "startup_count": 800,
            "specializations": ["cloud", "ai_ml", "gaming", "e-commerce"]
        },
        "cost_multiplier": 1.8,
        "agent_capacity": 18,
        "specialization_bonuses": {
            "cloud-architect": 1.5,
            "engineer-master": 1.3,
            "create-guru": 1.2
        }
    },
    "US:New York": {
        "timezone": "America/New_York",
        "utc_offset": -5,
        "region_type": "financial_hub",
        "tech_ecosystem": {
            "company_count": 350,
            "startup_count": 1000,
            "specializations": ["fintech", "adtech", "security", "data"]
        },
        "cost_multiplier": 1.9,
        "agent_capacity": 15,
        "specialization_bonuses": {
            "secure-specialist": 1.4,
            "organize-guru": 1.3
        }
    },
    "US:Redmond": {
        "timezone": "America/Los_Angeles",
        "utc_offset": -8,
        "region_type": "corporate_hub",
        "tech_ecosystem": {
            "company_count": 50,
            "startup_count": 100,
            "specializations": ["cloud", "productivity", "gaming", "ai_ml"]
        },
        "cost_multiplier": 1.6,
        "agent_capacity": 12,
        "specialization_bonuses": {
            "cloud-architect": 1.5,
            "engineer-master": 1.3
        }
    },
    "TW:Hsinchu": {
        "timezone": "Asia/Taipei",
        "utc_offset": 8,
        "region_type": "manufacturing_hub",
        "tech_ecosystem": {
            "company_count": 200,
            "startup_count": 300,
            "specializations": ["hardware", "semiconductors", "manufacturing"]
        },
        "cost_multiplier": 1.3,
        "agent_capacity": 10,
        "specialization_bonuses": {
            "accelerate-master": 1.4,
            "investigate-champion": 1.2
        }
    },
    "KR:Seoul": {
        "timezone": "Asia/Seoul",
        "utc_offset": 9,
        "region_type": "tech_hub",
        "tech_ecosystem": {
            "company_count": 250,
            "startup_count": 600,
            "specializations": ["mobile", "gaming", "ai_ml", "hardware"]
        },
        "cost_multiplier": 1.4,
        "agent_capacity": 12,
        "specialization_bonuses": {
            "accelerate-master": 1.3,
            "engineer-wizard": 1.2
        }
    },
    "CN:Hangzhou": {
        "timezone": "Asia/Shanghai",
        "utc_offset": 8,
        "region_type": "innovation_hub",
        "tech_ecosystem": {
            "company_count": 300,
            "startup_count": 800,
            "specializations": ["e-commerce", "fintech", "ai_ml", "cloud"]
        },
        "cost_multiplier": 1.2,
        "agent_capacity": 15,
        "specialization_bonuses": {
            "organize-guru": 1.4,
            "create-guru": 1.2
        }
    },
    "CN:Shenzhen": {
        "timezone": "Asia/Shanghai",
        "utc_offset": 8,
        "region_type": "hardware_hub",
        "tech_ecosystem": {
            "company_count": 400,
            "startup_count": 1200,
            "specializations": ["hardware", "iot", "ai_ml", "manufacturing"]
        },
        "cost_multiplier": 1.1,
        "agent_capacity": 18,
        "specialization_bonuses": {
            "accelerate-master": 1.5,
            "investigate-champion": 1.3
        }
    },
    "SE:Stockholm": {
        "timezone": "Europe/Stockholm",
        "utc_offset": 1,
        "region_type": "startup_hub",
        "tech_ecosystem": {
            "company_count": 150,
            "startup_count": 500,
            "specializations": ["saas", "gaming", "fintech", "greentech"]
        },
        "cost_multiplier": 1.5,
        "agent_capacity": 10,
        "specialization_bonuses": {
            "coach-master": 1.4,
            "organize-guru": 1.2
        }
    }
}


def enhance_regions(world_state: Dict[str, Any]) -> int:
    """
    Enhance regions with additional metadata.
    
    Returns:
        Number of regions enhanced
    """
    regions = world_state.get('regions', [])
    enhanced_count = 0
    
    for region in regions:
        region_id = region.get('id')
        if region_id in REGION_METADATA:
            metadata = REGION_METADATA[region_id]
            
            # Merge metadata into region
            region.update(metadata)
            enhanced_count += 1
            print(f"  ✅ Enhanced {region_id} - Type: {metadata['region_type']}, Timezone: {metadata['timezone']}")
        else:
            # Add basic metadata for unknown regions
            if 'timezone' not in region:
                region['timezone'] = 'UTC'
                region['utc_offset'] = 0
                region['region_type'] = 'general'
                region['cost_multiplier'] = 1.0
                region['agent_capacity'] = 10
                print(f"  ⚠️ Added basic metadata to {region_id}")
                enhanced_count += 1
    
    return enhanced_count


def main():
    """Main function to enhance region metadata."""
    print("=" * 70)
    print("🌍 Enhancing Region Metadata")
    print("=" * 70)
    
    # Load world state
    print(f"\n📖 Loading world state from: {WORLD_STATE_FILE}")
    with open(WORLD_STATE_FILE, 'r', encoding='utf-8') as f:
        world_state = json.load(f)
    
    total_regions = len(world_state.get('regions', []))
    print(f"   Found {total_regions} regions")
    
    # Enhance regions
    print(f"\n🔧 Enhancing region metadata...")
    enhanced_count = enhance_regions(world_state)
    
    # Save world state
    print(f"\n💾 Saving enhanced world state...")
    with open(WORLD_STATE_FILE, 'w', encoding='utf-8') as f:
        json.dump(world_state, f, indent=2, ensure_ascii=False)
    
    print(f"\n" + "=" * 70)
    print(f"✅ SUCCESS: Enhanced {enhanced_count}/{total_regions} regions")
    print("=" * 70)
    
    return enhanced_count


if __name__ == '__main__':
    main()
