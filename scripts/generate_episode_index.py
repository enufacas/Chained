#!/usr/bin/env python3
"""
Generate an index of all Chained TV episodes organized by date.
"""

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from collections import defaultdict


def generate_episode_index():
    """Generate an index of all episodes organized by date"""
    
    episodes_dir = Path('docs/episodes')
    
    if not episodes_dir.exists():
        print("❌ Episodes directory not found")
        return
    
    # Find all episode JSON files (exclude latest.json, demo, and README)
    episode_files = [
        f for f in episodes_dir.glob('episode-*.json')
        if f.is_file()
    ]
    
    print(f"📊 Found {len(episode_files)} episode files")
    
    # Group episodes by date
    episodes_by_date = defaultdict(list)
    
    for episode_file in sorted(episode_files, reverse=True):
        try:
            with open(episode_file, 'r') as f:
                episode_data = json.load(f)
            
            # Extract date from the episode
            episode_date_str = episode_data.get('date', '')
            if episode_date_str:
                episode_dt = datetime.fromisoformat(episode_date_str.replace('Z', '+00:00'))
                date_key = episode_dt.strftime('%Y-%m-%d')
            else:
                # Fall back to filename parsing
                # Format: episode-YYYYMMDD-HHMM.json
                filename = episode_file.stem
                parts = filename.split('-')
                if len(parts) >= 2:
                    date_str = parts[1]  # YYYYMMDD
                    date_key = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"
                else:
                    date_key = "unknown"
            
            episodes_by_date[date_key].append({
                'filename': episode_file.name,
                'title': episode_data.get('title', 'Untitled'),
                'date': episode_data.get('date', ''),
                'scene_count': len(episode_data.get('scenes', []))
            })
            
        except Exception as e:
            print(f"⚠️ Error processing {episode_file.name}: {e}")
            continue
    
    # Create index structure
    index = {
        'generated_at': datetime.now(timezone.utc).isoformat(),
        'total_episodes': sum(len(eps) for eps in episodes_by_date.values()),
        'dates': []
    }
    
    # Sort dates in descending order (newest first)
    for date_key in sorted(episodes_by_date.keys(), reverse=True):
        episodes = episodes_by_date[date_key]
        
        # Sort episodes within the same date by time (newest first)
        episodes.sort(key=lambda x: x['date'], reverse=True)
        
        index['dates'].append({
            'date': date_key,
            'episode_count': len(episodes),
            'episodes': episodes
        })
    
    # Save index
    index_path = episodes_dir / 'index.json'
    with open(index_path, 'w') as f:
        json.dump(index, f, indent=2)
    
    print(f"✅ Generated episode index: {index_path}")
    print(f"   Total episodes: {index['total_episodes']}")
    print(f"   Date groups: {len(index['dates'])}")
    
    return index


def main():
    """Main entry point"""
    print("=" * 70)
    print("Chained TV Episode Index Generator")
    print("=" * 70)
    print()
    
    index = generate_episode_index()
    
    print()
    print("=" * 70)
    print("Index generation complete!")
    print("=" * 70)


if __name__ == '__main__':
    main()
