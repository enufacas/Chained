#!/usr/bin/env python3
"""
Example: Agent Collaboration Manager Integration

This example demonstrates integrating the collaboration manager with
the investment tracker and learning matcher systems.

Created by: @coordinate-wizard
Date: 2025-11-15
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from agent_collaboration_manager import (
    AgentCollaborationManager,
    CollaborationType,
    CollaborationOutcome
)
from agent_investment_tracker import AgentInvestmentTracker
from agent_learning_matcher import AgentLearningMatcher


def main():
    """Demonstrate collaboration manager integration."""
    print("=" * 70)
    print("Agent Collaboration Manager Integration Example")
    print("=" * 70)
    print()
    
    # Initialize systems
    print("📦 Initializing systems...")
    tracker = AgentInvestmentTracker()
    matcher = AgentLearningMatcher()
    manager = AgentCollaborationManager()
    
    # Integrate systems
    manager.integrate_investment_tracker(tracker)
    manager.integrate_learning_matcher(matcher)
    
    print("✅ Systems initialized and integrated")
    print()
    
    # Scenario 1: Agent learning DevOps needs help
    print("=" * 70)
    print("Scenario 1: Agent Requests Help with Learning")
    print("=" * 70)
    print()
    
    requester = "engineer-master"
    topic = "CI/CD pipeline implementation"
    category = "DevOps"
    
    print(f"🤔 {requester} is working on: {topic}")
    print(f"   Learning category: {category}")
    print()
    
    # Create collaboration request
    request = manager.create_request(
        requester=requester,
        collaboration_type=CollaborationType.PAIR_PROGRAMMING,
        topic=topic,
        description="Implementing GitHub Actions workflow for automated testing. Need hands-on help with workflow syntax and best practices.",
        learning_category=category,
        priority=0.8,
        estimated_duration=4.0,
        tags=["github-actions", "testing", "automation"]
    )
    
    print(f"📝 Created collaboration request: {request.request_id}")
    print()
    
    # Find suitable helpers
    print("🔍 Finding suitable helpers...")
    helpers = manager.find_helpers(
        topic=topic,
        learning_category=category,
        exclude_agents=[requester],
        max_results=3
    )
    
    if helpers:
        print(f"   Found {len(helpers)} potential helpers:")
        for helper, score in helpers:
            print(f"   - {helper} (match score: {score:.2f})")
        
        # Best helper accepts
        best_helper = helpers[0][0]
        print()
        print(f"✅ {best_helper} accepts the collaboration request")
        
        manager.accept_request(request.request_id, best_helper)
        manager.start_collaboration(request.request_id)
        
        print(f"🤝 Collaboration started between {requester} and {best_helper}")
    else:
        print("   ⚠️  No helpers found (this is expected in test environment)")
    
    print()
    
    # Scenario 2: Complete collaboration and record outcome
    print("=" * 70)
    print("Scenario 2: Complete Collaboration and Record Outcome")
    print("=" * 70)
    print()
    
    print("⏰ Collaboration in progress...")
    print("   (Agents are working together on CI/CD implementation)")
    print()
    
    # Simulate successful collaboration
    outcome = CollaborationOutcome(
        request_id=request.request_id,
        success=True,
        duration_hours=5.5,
        outcome_description="Successfully implemented complete CI/CD pipeline with automated testing, linting, and deployment stages. Pipeline runs on push to main and pull requests.",
        learning_gained="GitHub Actions workflow syntax, matrix builds, secrets management, deployment strategies, action caching",
        knowledge_shared="Best practices for CI/CD pipelines, test automation patterns, workflow optimization techniques",
        value_rating=0.92,
        would_collaborate_again=True,
        artifacts=[
            ".github/workflows/ci.yml",
            "docs/ci-cd-setup.md"
        ],
        feedback_requester="Excellent collaboration! Learned so much about GitHub Actions. The hands-on approach was perfect.",
        feedback_helper="Great learning mindset. Asked good questions and quickly grasped the concepts. Would definitely work together again."
    )
    
    print("✅ Collaboration completed successfully!")
    print(f"   Duration: {outcome.duration_hours} hours")
    print(f"   Value rating: {outcome.value_rating:.2f}/1.0")
    print(f"   Would collaborate again: {outcome.would_collaborate_again}")
    print()
    
    if helpers:
        manager.complete_collaboration(request.request_id, outcome)
        
        # Record cultivation event in investment tracker
        tracker.record_cultivation(
            agent_name=requester,
            category=category,
            learning_id=request.request_id,
            impact=outcome.value_rating,  # Use value rating as impact
            context=f"Collaboration with {best_helper}"
        )
        
        print(f"📊 Updated {requester}'s investment in {category}")
        summary = tracker.get_investment_summary(requester)
        if category in summary.get('categories', []):
            print(f"   Total investments: {summary['total_investments']}")
            print(f"   Categories: {', '.join(summary['categories'])}")
    
    print()
    
    # Scenario 3: Get collaboration statistics
    print("=" * 70)
    print("Scenario 3: View Collaboration Statistics")
    print("=" * 70)
    print()
    
    stats = manager.get_statistics()
    
    print("📊 System-wide collaboration statistics:")
    print(f"   Total requests: {stats['total_requests']}")
    print(f"   Total completed: {stats['total_completed']}")
    print(f"   Success rate: {stats.get('success_rate', 0):.1%}")
    print(f"   Average duration: {stats['average_duration']:.1f} hours")
    print(f"   Average value rating: {stats['average_value_rating']:.2f}/1.0")
    print(f"   Active requests: {stats['active_requests']}")
    print()
    
    # Scenario 4: Suggest collaboration opportunities
    print("=" * 70)
    print("Scenario 4: Discover Collaboration Opportunities")
    print("=" * 70)
    print()
    
    # Check active requests
    active_requests = manager.get_active_requests()
    print(f"📋 Currently {len(active_requests)} active collaboration requests")
    print()
    
    if active_requests:
        for req in active_requests[:3]:  # Show first 3
            print(f"   Request: {req.topic}")
            print(f"   Requester: {req.requester}")
            print(f"   Type: {req.collaboration_type.value}")
            print(f"   Category: {req.learning_category or 'N/A'}")
            print(f"   Priority: {req.priority:.2f}")
            print()
    
    # Scenario 5: View collaboration history
    if helpers:
        print("=" * 70)
        print("Scenario 5: View Collaboration History")
        print("=" * 70)
        print()
        
        history = manager.get_collaboration_history(requester, limit=5)
        
        print(f"📜 Recent collaborations for {requester}:")
        print()
        
        for collab_request, collab_outcome in history:
            print(f"   Topic: {collab_request.topic}")
            print(f"   Partner: {collab_request.helper or 'N/A'}")
            print(f"   Status: {collab_request.status.value}")
            
            if collab_outcome:
                print(f"   Success: {'✅' if collab_outcome.success else '❌'}")
                print(f"   Value: {collab_outcome.value_rating:.2f}/1.0")
            
            print()
        
        # Show collaboration partners
        partners = manager.get_collaboration_partners(requester)
        if partners:
            print(f"🤝 {requester} has collaborated with:")
            for partner in partners:
                print(f"   - {partner}")
    
    print()
    print("=" * 70)
    print("Example Complete!")
    print("=" * 70)
    print()
    print("🎭 The collaboration system enables agents to:")
    print("   ✓ Request help from specialists")
    print("   ✓ Share knowledge across the ecosystem")
    print("   ✓ Build expertise through collaboration")
    print("   ✓ Form effective partnerships")
    print("   ✓ Track and improve collaboration quality")
    print()
    print("🎼 Like a great orchestra, agents harmonize their expertise!")
    print()


if __name__ == '__main__':
    main()
