#!/usr/bin/env python3
"""
Test script to validate agent assignment diversity with penalty system.
Simulates the autonomous-pipeline mission matching logic.
"""

import json
import subprocess
import sys

# Mock world state with agents
mock_agents = [
    {"id": "cloud-architect", "label": "Cloud Expert", "specialization": "cloud-architect"},
    {"id": "assert-specialist", "label": "Tesla", "specialization": "assert-specialist"},
    {"id": "organize-guru", "label": "Robert Martin", "specialization": "organize-guru"},
    {"id": "coach-master", "label": "Turing", "specialization": "coach-master"},
    {"id": "secure-specialist", "label": "Schneier", "specialization": "secure-specialist"},
]

# Mock ideas with different patterns
mock_ideas = [
    {
        "id": "idea1",
        "title": "Cloud Security Best Practices",
        "summary": "Best practices for securing cloud infrastructure",
        "patterns": ["cloud", "security", "devops"]
    },
    {
        "id": "idea2",
        "title": "Testing Frameworks Comparison",
        "summary": "Comparison of different testing frameworks",
        "patterns": ["testing", "coverage", "api"]
    },
    {
        "id": "idea3",
        "title": "Code Review Best Practices",
        "summary": "Best practices for conducting code reviews",
        "patterns": ["review", "refactor", "clean"]
    },
    {
        "id": "idea4",
        "title": "Performance Optimization Techniques",
        "summary": "Techniques for optimizing application performance",
        "patterns": ["performance", "optimize"]
    },
    {
        "id": "idea5",
        "title": "Kubernetes Best Practices",
        "summary": "Best practices for Kubernetes deployment",
        "patterns": ["cloud", "kubernetes", "devops"]
    },
]

print("🧪 Testing Mission Matching with Diversity Penalty System")
print("=" * 60)
print()

# Track agent assignment counts (diversity penalty system)
agent_assignment_count = {}
diversity_weight = 0.7  # Same as agent_learning_matcher.py

missions = []

for idea in mock_ideas:
    idea_title = idea['title']
    idea_patterns = idea['patterns']
    
    match_text = f"{idea_title}. Patterns: {', '.join(idea_patterns)}"
    
    try:
        result = subprocess.run(
            ['python3', 'tools/match-issue-to-agent.py', match_text],
            capture_output=True,
            text=True,
            check=True
        )
        match_data = json.loads(result.stdout)
        all_scores = match_data.get('all_scores', {})
        
        # Apply diversity penalty (like autonomous-pipeline.yml now does)
        adjusted_scores = []
        for agent_spec, base_score in all_scores.items():
            assignment_count = agent_assignment_count.get(agent_spec, 0)
            penalty = assignment_count * diversity_weight
            adjusted_score = base_score * (1.0 - min(penalty, 0.9))
            adjusted_scores.append((agent_spec, adjusted_score, base_score))
        
        adjusted_scores.sort(key=lambda x: x[1], reverse=True)
        
        if adjusted_scores:
            matched_specialization = adjusted_scores[0][0]
            adjusted_score = adjusted_scores[0][1]
            base_score = adjusted_scores[0][2]
            
            agent_details = None
            for agent in mock_agents:
                if agent.get('specialization') == matched_specialization:
                    agent_details = agent
                    break
            
            if not agent_details:
                agent_details = {"id": matched_specialization, "label": matched_specialization, "specialization": matched_specialization}
            
            print(f"📋 {idea_title}")
            print(f"   Patterns: {', '.join(idea_patterns)}")
            
            # Show top 3 with penalty info
            print(f"\n   Top Candidates:")
            for i, (agent_spec, adj_score, orig_score) in enumerate(adjusted_scores[:3], 1):
                count = agent_assignment_count.get(agent_spec, 0)
                penalty_pct = min(count * diversity_weight * 100, 90)
                penalty_info = f" (penalty: -{penalty_pct:.0f}%)" if count > 0 else ""
                print(f"   {i}. @{agent_spec:25s} Base:{orig_score:.3f} → Adjusted:{adj_score:.3f}{penalty_info}")
            
            rank = agent_assignment_count.get(matched_specialization, 0) + 1
            rank_marker = f" (#{rank} assignment)" if rank > 1 else ""
            print(f"\n   ✅ Selected: @{matched_specialization}{rank_marker}\n")
            
            agent_assignment_count[matched_specialization] = agent_assignment_count.get(matched_specialization, 0) + 1
            
            missions.append({
                'idea': idea_title,
                'agent': matched_specialization,
                'base_score': base_score,
                'adjusted_score': adjusted_score,
                'assignment_rank': rank
            })
    
    except Exception as e:
        print(f"⚠️  Error: {e}")

print("=" * 60)
print("\n📊 Mission Summary:\n")

for mission in missions:
    rank_marker = f" (#{mission['assignment_rank']})" if mission['assignment_rank'] > 1 else ""
    print(f"   • {mission['idea']:45s} → @{mission['agent']}{rank_marker}")

print()
unique_agents = len(set(m['agent'] for m in missions))
total_missions = len(missions)
diversity_pct = (unique_agents / total_missions * 100) if total_missions > 0 else 0

print(f"   Diversity: {unique_agents}/{total_missions} unique agents ({diversity_pct:.0f}%)")

if diversity_pct >= 80:
    print(f"   ✅ PASS: Excellent diversity (≥80%)!")
    sys.exit(0)
elif diversity_pct >= 60:
    print(f"   ✅ PASS: Good diversity (≥60%)!")
    sys.exit(0)
else:
    print(f"   ❌ FAIL: Low diversity (<60%)")
    sys.exit(1)
