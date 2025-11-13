#!/usr/bin/env python3
"""
Test script for TLDR RSS feeds
This script verifies that the TLDR RSS feeds are accessible and contain valid data.
"""

import requests
import json
from datetime import datetime, timezone
from xml.etree import ElementTree as ET

def test_tldr_rss_feeds():
    """Test TLDR RSS feed URLs"""
    
    print("=" * 70)
    print("TLDR RSS Feed Test")
    print("=" * 70)
    
    # RSS feed URLs (updated format)
    rss_urls = [
        'https://tldr.tech/api/rss/tech',
        'https://tldr.tech/api/rss/ai',
        'https://tldr.tech/api/rss/devops'
    ]
    
    learnings = []
    tech_trends = []
    
    for rss_url in rss_urls:
        try:
            print(f"\nTesting: {rss_url}")
            response = requests.get(rss_url, timeout=10)
            
            if response.status_code != 200:
                print(f"  ✗ HTTP {response.status_code}")
                continue
                
            print(f"  ✓ HTTP 200 OK")
            print(f"  Content-Type: {response.headers.get('content-type', 'unknown')}")
            print(f"  Size: {len(response.content)} bytes")
            
            # Parse RSS content
            try:
                root = ET.fromstring(response.content)
                items = root.findall('.//item')
                print(f"  ✓ Valid RSS/XML")
                print(f"  ✓ Found {len(items)} items")
                
                items_collected = 0
                for item in items[:5]:  # Top 5 items
                    title = item.find('title')
                    desc = item.find('description')
                    
                    if title is not None and title.text:
                        learnings.append({
                            'title': title.text,
                            'description': desc.text if desc is not None else '',
                            'source': 'TLDR'
                        })
                        items_collected += 1
                        
                        # Extract tech trends
                        title_lower = title.text.lower()
                        if any(word in title_lower for word in ['ai', 'ml', 'llm', 'gpt', 'copilot']):
                            tech_trends.append(f"AI/ML: {title.text}")
                        elif any(word in title_lower for word in ['github', 'git', 'devops', 'ci/cd']):
                            tech_trends.append(f"DevOps: {title.text}")
                        elif any(word in title_lower for word in ['python', 'javascript', 'rust', 'go']):
                            tech_trends.append(f"Programming: {title.text}")
                
                print(f"  ✓ Collected {items_collected} learnings")
                
                # Show sample
                if items and items_collected > 0:
                    first_title = items[0].find('title')
                    if first_title is not None:
                        print(f"  Sample: {first_title.text[:60]}...")
                
            except ET.ParseError as e:
                print(f"  ✗ XML Parse Error: {e}")
                
        except requests.Timeout:
            print(f"  ✗ Timeout after 10 seconds")
        except requests.ConnectionError as e:
            print(f"  ✗ Connection Error: {e}")
        except Exception as e:
            print(f"  ✗ Error: {e}")
    
    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Total learnings collected: {len(learnings)}")
    print(f"Total trends identified: {len(tech_trends)}")
    
    if learnings:
        print("\n✅ SUCCESS: RSS feeds are working correctly")
        print("\nSample Learnings:")
        for i, learning in enumerate(learnings[:5], 1):
            print(f"  {i}. {learning['title'][:70]}...")
        
        if tech_trends:
            print("\nSample Trends:")
            for i, trend in enumerate(tech_trends[:5], 1):
                print(f"  {i}. {trend[:70]}...")
        
        # Test saving to file
        now = datetime.now(timezone.utc)
        timestamp = now.strftime('%Y%m%d_%H%M%S')
        test_data = {
            'timestamp': now.isoformat(),
            'source': 'TLDR Tech',
            'learnings': learnings,
            'trends': tech_trends
        }
        
        print(f"\nTest data structure:")
        print(json.dumps(test_data, indent=2)[:500] + "...")
        
        return True
    else:
        print("\n❌ FAILURE: No learnings were collected")
        print("The RSS feeds may be inaccessible or have changed format again.")
        return False

if __name__ == "__main__":
    import sys
    success = test_tldr_rss_feeds()
    sys.exit(0 if success else 1)
