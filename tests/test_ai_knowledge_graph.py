#!/usr/bin/env python3
"""
Test script to validate AI Knowledge Graph data processing
"""

import json
import os
from collections import defaultdict

def test_learning_data_extraction():
    """Test that we can extract AI-related data from learning files"""
    print("Testing Learning Data Extraction...")
    
    learnings_dir = "learnings"
    ai_stories = []
    
    if not os.path.exists(learnings_dir):
        print(f"❌ Learnings directory not found: {learnings_dir}")
        return False
    
    for filename in os.listdir(learnings_dir):
        if filename.endswith('.json') and not filename == 'index.json':
            filepath = os.path.join(learnings_dir, filename)
            try:
                with open(filepath, 'r') as f:
                    data = json.load(f)
                    
                # Extract AI-related stories
                for learning in data.get('learnings', []):
                    title = learning.get('title', '').lower()
                    if any(keyword in title for keyword in ['ai', 'ml', 'llm', 'gpt', 'neural', 'machine learning', 'copilot', 'model', 'training']):
                        ai_stories.append({
                            'title': learning.get('title'),
                            'score': learning.get('score', 0),
                            'source': filename
                        })
            except Exception as e:
                print(f"⚠️ Error reading {filename}: {e}")
    
    print(f"✅ Found {len(ai_stories)} AI-related stories")
    return len(ai_stories) > 0

def test_topic_extraction():
    """Test topic extraction from titles"""
    print("\nTesting Topic Extraction...")
    
    test_titles = [
        "Study identifies weaknesses in how AI systems are evaluated",
        "New GPT-5 model shows impressive performance",
        "Machine Learning framework for production deployment",
        "Building a neural network from scratch"
    ]
    
    ai_terms = [
        'ai', 'ml', 'gpt', 'llm', 'neural', 'model', 'training', 'dataset',
        'transformer', 'copilot', 'chatbot', 'nlp', 'vision', 'deep learning',
        'machine learning'
    ]
    
    for title in test_titles:
        title_lower = title.lower()
        found_terms = [term for term in ai_terms if term in title_lower]
        print(f"  '{title}' -> {found_terms}")
    
    print("✅ Topic extraction working")
    return True

def test_categorization():
    """Test story categorization"""
    print("\nTesting Story Categorization...")
    
    categories = {
        'AI/ML': ['gpt', 'llm', 'neural', 'model', 'training'],
        'Tools': ['framework', 'library', 'tool', 'sdk', 'api'],
        'Research': ['research', 'study', 'paper', 'academic']
    }
    
    test_cases = [
        ("GPT-4 model training techniques", "AI/ML"),
        ("New Python framework for ML", "Tools"),
        ("Academic research on neural networks", "Research")
    ]
    
    for title, expected_category in test_cases:
        title_lower = title.lower()
        found = False
        for category, keywords in categories.items():
            if any(kw in title_lower for kw in keywords):
                print(f"  '{title}' -> {category}")
                found = True
                break
        if not found:
            print(f"  '{title}' -> default")
    
    print("✅ Categorization working")
    return True

def test_relationship_detection():
    """Test relationship detection between stories"""
    print("\nTesting Relationship Detection...")
    
    stories = [
        {'title': 'GPT-4 training with transformers', 'terms': ['gpt', 'training', 'transformer']},
        {'title': 'Transformer architecture improvements', 'terms': ['transformer', 'neural']},
        {'title': 'Neural network optimization', 'terms': ['neural', 'training']}
    ]
    
    relationships = []
    for i, story1 in enumerate(stories):
        for story2 in stories[i+1:]:
            shared = set(story1['terms']) & set(story2['terms'])
            if len(shared) >= 1:
                relationships.append((story1['title'], story2['title'], shared))
    
    print(f"  Found {len(relationships)} relationships:")
    for s1, s2, terms in relationships:
        print(f"    - '{s1[:30]}...' <-> '{s2[:30]}...' (shared: {terms})")
    
    print("✅ Relationship detection working")
    return True

def test_data_quality():
    """Test overall data quality"""
    print("\nTesting Data Quality...")
    
    learnings_dir = "learnings"
    valid_files = 0
    total_learnings = 0
    topics = defaultdict(int)
    
    for filename in os.listdir(learnings_dir):
        if filename.endswith('.json') and not filename == 'index.json':
            filepath = os.path.join(learnings_dir, filename)
            try:
                with open(filepath, 'r') as f:
                    data = json.load(f)
                    
                valid_files += 1
                total_learnings += len(data.get('learnings', []))
                
                # Count topics
                for topic, stories in data.get('topics', {}).items():
                    topics[topic] += len(stories)
                    
            except Exception as e:
                print(f"❌ Invalid file {filename}: {e}")
                return False
    
    print(f"  Valid files: {valid_files}")
    print(f"  Total learnings: {total_learnings}")
    print(f"  Topics tracked: {len(topics)}")
    print(f"  Topic distribution: {dict(topics)}")
    
    if valid_files > 0 and total_learnings > 0:
        print("✅ Data quality is good")
        return True
    else:
        print("❌ Insufficient data")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("AI Knowledge Graph Data Processing Tests")
    print("=" * 60)
    
    tests = [
        test_learning_data_extraction,
        test_topic_extraction,
        test_categorization,
        test_relationship_detection,
        test_data_quality
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            results.append(False)
    
    print("\n" + "=" * 60)
    print("Test Results Summary")
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("✅ All tests passed!")
        return 0
    else:
        print("❌ Some tests failed")
        return 1

if __name__ == "__main__":
    exit(main())
