#!/usr/bin/env python3
"""
Example: Using Semantic Similarity Engine with Chained Workflows

Demonstrates how to integrate the semantic similarity engine into
the Chained autonomous agent system.

Created by @engineer-master
"""

import json
from pathlib import Path
from semantic_similarity_engine import SemanticSimilarityEngine, IssueRecord


def example_basic_usage():
    """Basic example of using the similarity engine."""
    print("=" * 80)
    print("Example 1: Basic Usage")
    print("=" * 80)
    print()
    
    # Initialize engine
    engine = SemanticSimilarityEngine()
    
    # Add a few historical issues
    issues = [
        IssueRecord(
            issue_number=101,
            title="API endpoint timeout",
            body="Users API timing out under load",
            labels=["bug", "api", "performance"],
            solution_summary="Added connection pooling and increased timeout",
            agent_assigned="accelerate-master",
            resolved_at="2024-01-01T00:00:00Z",
            pr_number=201
        ),
        IssueRecord(
            issue_number=102,
            title="Authentication bug in login",
            body="Login fails with invalid credentials",
            labels=["bug", "security"],
            solution_summary="Fixed JWT token validation",
            agent_assigned="secure-specialist",
            resolved_at="2024-01-02T00:00:00Z",
            pr_number=202
        ),
        IssueRecord(
            issue_number=103,
            title="Add tests for user endpoints",
            body="Need comprehensive API tests",
            labels=["testing", "api"],
            solution_summary="Added integration tests with 95% coverage",
            agent_assigned="assert-specialist",
            resolved_at="2024-01-03T00:00:00Z",
            pr_number=203
        )
    ]
    
    for issue in issues:
        engine.add_issue(issue)
    
    print(f"✅ Added {len(issues)} issues to history")
    print()
    
    # Search for similar issues
    print("Searching for: 'API timeout error'")
    print()
    
    matches = engine.find_similar_issues(
        title="API timeout error",
        body="Getting timeouts on API calls",
        top_k=3
    )
    
    if matches:
        print(f"Found {len(matches)} similar issue(s):")
        print()
        for i, match in enumerate(matches, 1):
            print(f"{i}. Issue #{match.issue_number}: {match.title}")
            print(f"   Similarity: {match.similarity_score:.1%}")
            print(f"   Agent: @{match.agent_assigned}")
            print(f"   Solution: {match.solution_summary}")
            print()
    
    print()


def example_agent_recommendation():
    """Example of using similarity for agent recommendation."""
    print("=" * 80)
    print("Example 2: Agent Recommendation Based on History")
    print("=" * 80)
    print()
    
    engine = SemanticSimilarityEngine()
    
    # Simulate having multiple issues resolved by different agents
    test_data = [
        ("API performance issues", "accelerate-master"),
        ("API rate limiting", "engineer-master"),
        ("API authentication", "secure-specialist"),
        ("API endpoint timeout", "accelerate-master"),
        ("API caching strategy", "accelerate-master"),
    ]
    
    for i, (title, agent) in enumerate(test_data, 200):
        engine.add_issue(IssueRecord(
            issue_number=i,
            title=title,
            body=f"Details about {title}",
            labels=["api"],
            solution_summary=f"Fixed by {agent}",
            agent_assigned=agent,
            resolved_at="2024-01-01T00:00:00Z"
        ))
    
    # New issue: Which agent should handle it?
    new_issue_title = "API slow response time"
    print(f"New issue: '{new_issue_title}'")
    print()
    
    matches = engine.find_similar_issues(new_issue_title, "", top_k=5)
    
    # Count agents who solved similar issues
    agent_scores = {}
    for match in matches:
        agent = match.agent_assigned
        score = match.similarity_score
        if agent:
            agent_scores[agent] = agent_scores.get(agent, 0) + score
    
    if agent_scores:
        print("Agent recommendations based on historical success:")
        print()
        sorted_agents = sorted(agent_scores.items(), key=lambda x: x[1], reverse=True)
        for agent, score in sorted_agents:
            count = sum(1 for m in matches if m.agent_assigned == agent)
            print(f"  @{agent}: {score:.2f} combined similarity ({count} similar issues)")
        
        print()
        print(f"✅ Recommended: @{sorted_agents[0][0]}")
    
    print()


def example_solution_templates():
    """Example of extracting solution templates from history."""
    print("=" * 80)
    print("Example 3: Learning Solution Patterns")
    print("=" * 80)
    print()
    
    engine = SemanticSimilarityEngine()
    
    # Add issues with detailed solutions
    solutions = [
        {
            "issue_number": 301,
            "title": "Database query performance",
            "solution": "Added indexes on frequently queried columns, implemented query caching, optimized JOIN operations"
        },
        {
            "issue_number": 302,
            "title": "Slow database queries",
            "solution": "Created composite indexes, added connection pooling, implemented read replicas"
        },
        {
            "issue_number": 303,
            "title": "Database timeout errors",
            "solution": "Optimized N+1 queries, added query timeout limits, implemented circuit breaker"
        }
    ]
    
    for sol in solutions:
        engine.add_issue(IssueRecord(
            issue_number=sol["issue_number"],
            title=sol["title"],
            body="",
            labels=["performance", "database"],
            solution_summary=sol["solution"],
            agent_assigned="accelerate-master",
            resolved_at="2024-01-01T00:00:00Z"
        ))
    
    # Find patterns in solutions
    new_issue = "Database performance problem"
    matches = engine.find_similar_issues(new_issue, "", top_k=3)
    
    print(f"New issue: '{new_issue}'")
    print()
    print("Historical solutions for similar issues:")
    print()
    
    for i, match in enumerate(matches, 1):
        print(f"{i}. From Issue #{match.issue_number} ({match.similarity_score:.1%} similar):")
        print(f"   {match.solution_summary}")
        print()
    
    # Extract common terms from solutions
    all_solution_terms = set()
    for match in matches:
        words = match.solution_summary.lower().split()
        all_solution_terms.update(words)
    
    # Common technical terms
    technical_terms = {
        'indexes', 'caching', 'pooling', 'optimization',
        'queries', 'replicas', 'timeout', 'circuit'
    }
    
    common = all_solution_terms & technical_terms
    if common:
        print(f"💡 Common solution approaches: {', '.join(sorted(common))}")
    
    print()


def example_workflow_integration():
    """Example of integrating with GitHub Actions workflow."""
    print("=" * 80)
    print("Example 4: Workflow Integration Pattern")
    print("=" * 80)
    print()
    
    print("In a GitHub Actions workflow, you would:")
    print()
    print("1. When a new issue is created:")
    print("   - Extract title and body")
    print("   - Search for similar historical issues")
    print("   - Comment with relevant context")
    print()
    print("2. When an issue is resolved:")
    print("   - Extract solution from PR")
    print("   - Add to similarity engine history")
    print("   - Update the knowledge base")
    print()
    print("3. For agent assignment:")
    print("   - Use similarity + keyword matching")
    print("   - Weight historical success heavily")
    print("   - Provide confidence scores")
    print()
    
    # Simulate workflow
    engine = SemanticSimilarityEngine()
    
    # Step 1: New issue arrives
    new_issue = {
        "number": 500,
        "title": "Security vulnerability in authentication",
        "body": "Found XSS vulnerability in login form"
    }
    
    print("Example workflow execution:")
    print()
    print(f"📥 New Issue #{new_issue['number']}: {new_issue['title']}")
    print()
    
    # Step 2: Search history
    matches = engine.find_similar_issues(
        new_issue['title'],
        new_issue['body'],
        top_k=3
    )
    
    if matches:
        print("📚 Found similar historical issues:")
        for match in matches[:2]:
            print(f"   - Issue #{match.issue_number}: {match.title}")
            print(f"     Resolved by: @{match.agent_assigned}")
    else:
        print("📚 No similar historical issues found (learning opportunity!)")
    
    print()
    print("🤖 Suggested agent: @secure-specialist")
    print("💬 Added comment to issue with historical context")
    print()


def main():
    """Run all examples."""
    print()
    print("🎓 Semantic Similarity Engine - Examples")
    print()
    
    examples = [
        example_basic_usage,
        example_agent_recommendation,
        example_solution_templates,
        example_workflow_integration
    ]
    
    for example_func in examples:
        try:
            example_func()
        except Exception as e:
            print(f"❌ Error in example: {e}")
            import traceback
            traceback.print_exc()
        
        print()
    
    print("=" * 80)
    print("✅ All examples completed!")
    print("=" * 80)


if __name__ == '__main__':
    main()
