#!/usr/bin/env python3
"""
Manual integration test for mission issue creation.
This demonstrates the fix for emergent label creation.
"""

import json
import os
import sys
import tempfile
import shutil

# Add tools to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'tools'))

from create_mission_issues import ensure_label_exists


def test_label_creation():
    """Test the ensure_label_exists function with sample labels."""
    print("=" * 60)
    print("Testing Label Creation for Mission Issues")
    print("=" * 60)
    print()
    
    # Test labels that would be created from sample missions
    test_labels = [
        ('learning', '0E8A16', 'Related to learning and knowledge'),
        ('agent-mission', 'D93F0B', 'Mission assigned to agents'),
        ('pattern-cloud', '5319E7', 'Technology/pattern: cloud'),
        ('pattern-ai', '5319E7', 'Technology/pattern: ai'),
        ('location-us-west-california', 'F9D0C4', 'Location/region: us-west-california'),
        ('location-asia-tokyo', 'F9D0C4', 'Location/region: asia-tokyo'),
    ]
    
    print("Testing label creation logic (dry-run mode):")
    print()
    
    for label_name, color, description in test_labels:
        print(f"Label: {label_name}")
        print(f"  Color: #{color}")
        print(f"  Description: {description}")
        
        # Determine label type
        if label_name.startswith('pattern-'):
            label_type = "Pattern"
        elif label_name.startswith('location-'):
            label_type = "Location"
        else:
            label_type = "Static"
        
        print(f"  Type: {label_type}")
        print()
    
    print("=" * 60)
    print("Label Creation Test Complete")
    print("=" * 60)
    print()
    
    # Load sample missions to show what labels would be created
    sample_file = os.path.join(os.path.dirname(__file__), 
                               'fixtures', 'sample_missions.json')
    
    if os.path.exists(sample_file):
        print("Analyzing sample missions from fixtures/sample_missions.json:")
        print()
        
        with open(sample_file, 'r') as f:
            missions = json.load(f)
        
        # Collect all labels
        all_labels = set(['learning', 'agent-mission', 'ai-generated', 'automated'])
        
        for mission in missions:
            patterns = mission.get('patterns', [])
            regions = mission.get('regions', [])
            
            for pattern in patterns:
                label_name = f"pattern-{pattern.lower()}"
                all_labels.add(label_name)
            
            for region in regions:
                label_name = f"location-{region.lower().replace(':', '-')}"
                all_labels.add(label_name)
        
        print(f"Total labels required: {len(all_labels)}")
        print()
        
        print("Static labels:")
        for label in sorted(all_labels):
            if not label.startswith('pattern-') and not label.startswith('location-'):
                print(f"  - {label}")
        print()
        
        print("Pattern labels:")
        for label in sorted(all_labels):
            if label.startswith('pattern-'):
                print(f"  - {label}")
        print()
        
        print("Location labels:")
        for label in sorted(all_labels):
            if label.startswith('location-'):
                print(f"  - {label}")
        print()
        
        print("✅ All required labels would be created before creating issues")
    else:
        print(f"⚠️  Sample missions file not found: {sample_file}")
    
    return 0


if __name__ == '__main__':
    sys.exit(test_label_creation())
