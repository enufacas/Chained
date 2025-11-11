#!/usr/bin/env python3
"""
Test to verify that generate-new-agent.py outputs all required fields.
This test validates the fix for the null name agent issue.
"""

import json
import subprocess
import sys


def test_generate_new_agent_output():
    """Test that generate-new-agent.py outputs all required fields."""
    
    # Run the script
    result = subprocess.run(
        ['python3', 'tools/generate-new-agent.py'],
        capture_output=True,
        text=True,
        timeout=15
    )
    
    if result.returncode != 0:
        print(f"❌ Script failed with return code {result.returncode}")
        print(f"stderr: {result.stderr}")
        return False
    
    # Parse JSON output
    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError as e:
        print(f"❌ Failed to parse JSON output: {e}")
        print(f"stdout: {result.stdout}")
        return False
    
    # Required fields for the workflow
    required_fields = [
        'success',
        'agent_name',
        'emoji',
        'human_name',
        'personality',
        'communication_style',
        'description',
        'message'
    ]
    
    # Check all required fields exist
    missing_fields = []
    for field in required_fields:
        if field not in data:
            missing_fields.append(field)
        elif not data[field]:  # Check field is not empty/null
            print(f"⚠️  Field '{field}' is empty or null: {data[field]}")
            missing_fields.append(field)
    
    if missing_fields:
        print(f"❌ Missing or empty fields: {', '.join(missing_fields)}")
        print(f"Output: {json.dumps(data, indent=2)}")
        return False
    
    # Verify human_name is not "null" string
    if data['human_name'] == 'null':
        print(f"❌ human_name is the string 'null'")
        return False
    
    # Verify emoji is a non-empty string
    if not isinstance(data['emoji'], str) or len(data['emoji']) == 0:
        print(f"❌ emoji is not a valid non-empty string: {data['emoji']}")
        return False
    
    print(f"✅ All required fields present and valid")
    print(f"   agent_name: {data['agent_name']}")
    print(f"   emoji: {data['emoji']}")
    print(f"   human_name: {data['human_name']}")
    print(f"   personality: {data['personality']}")
    print(f"   communication_style: {data['communication_style']}")
    
    return True


def main():
    """Run the test."""
    print("Testing generate-new-agent.py output...")
    print("-" * 60)
    
    success = test_generate_new_agent_output()
    
    print("-" * 60)
    if success:
        print("✅ Test PASSED")
        sys.exit(0)
    else:
        print("❌ Test FAILED")
        sys.exit(1)


if __name__ == "__main__":
    main()
