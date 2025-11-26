#!/usr/bin/env python3
"""
Multi-Agent Collaboration Example using A2A Protocol
Phase 2B: Testing & Integration

This example demonstrates how multiple agents can collaborate on a complex task
using the A2A protocol within a single GitHub Actions runner (Tier 1).

Scenario: Design and implement a secure REST API
- engineer-master: Designs the API endpoints
- secure-specialist: Reviews security implications
- organize-guru: Structures the code layout
- Meta-coordinator: Orchestrates the collaboration
"""

import asyncio
import sys
from pathlib import Path
from typing import Dict, List

# Add tools to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.a2a import (
    get_discovery_service,
    ChainedA2AClient,
    generate_agent_card,
    get_agent_port
)


class MultiAgentOrchestrator:
    """Orchestrates multi-agent collaboration."""
    
    def __init__(self):
        self.discovery = None
        self.client = None
        self.results = {}
    
    async def setup(self):
        """Initialize discovery service and register agents."""
        print("🔧 Setting up multi-agent environment...\n")
        
        self.discovery = get_discovery_service()
        
        # Register agents
        agents = [
            "engineer-master",
            "secure-specialist", 
            "organize-guru"
        ]
        
        for agent_name in agents:
            card = generate_agent_card(agent_name)
            # Register in discovery using registry API
            port = get_agent_port(agent_name)
            skills = [s.id for s in card.skills] if card.skills else []
            self.discovery.registry.register_agent(agent_name, port, skills)
            print(f"✅ Registered: {agent_name} ({', '.join(s.name for s in card.skills)})")
        
        print()
    
    async def delegate_task(self, agent_name: str, task: str):
        """Delegate a task to an agent."""
        print(f"📤 Delegating to {agent_name}:")
        print(f"   Task: {task}\n")
        
        # In a real implementation with running servers:
        # async with ChainedA2AClient() as client:
        #     result = await client.send_message(agent_name, task)
        #     return result
        
        # For this example, simulate agent responses
        simulated_results = {
            "engineer-master": {
                "status": "completed",
                "deliverable": "API Design",
                "details": [
                    "GET /api/v1/users - List users",
                    "POST /api/v1/users - Create user",
                    "GET /api/v1/users/{id} - Get user",
                    "PUT /api/v1/users/{id} - Update user",
                    "DELETE /api/v1/users/{id} - Delete user"
                ]
            },
            "secure-specialist": {
                "status": "completed",
                "deliverable": "Security Review",
                "details": [
                    "Require JWT authentication on all endpoints",
                    "Implement rate limiting (100 req/min per user)",
                    "Validate input with JSON schema",
                    "Use HTTPS only",
                    "Implement CORS with whitelist"
                ]
            },
            "organize-guru": {
                "status": "completed",
                "deliverable": "Code Structure",
                "details": [
                    "src/api/routes/ - Route handlers",
                    "src/api/middleware/ - Authentication, logging",
                    "src/api/models/ - Data models",
                    "src/api/validators/ - Input validation",
                    "tests/api/ - API tests"
                ]
            }
        }
        
        result = simulated_results.get(agent_name, {})
        
        print(f"✅ {agent_name} completed: {result.get('deliverable', 'Task')}")
        for detail in result.get('details', []):
            print(f"   • {detail}")
        print()
        
        return result
    
    async def orchestrate(self):
        """Orchestrate multi-agent collaboration."""
        print("=" * 70)
        print("Multi-Agent Collaboration: Secure REST API Design")
        print("=" * 70)
        print()
        
        # Phase 1: API Design
        print("📋 Phase 1: API Design")
        print("-" * 70)
        result1 = await self.delegate_task(
            "engineer-master",
            "Design RESTful API endpoints for user management system"
        )
        self.results["api_design"] = result1
        
        # Phase 2: Security Review
        print("📋 Phase 2: Security Review")
        print("-" * 70)
        result2 = await self.delegate_task(
            "secure-specialist",
            f"Review security implications of API design: {result1.get('details', [])}"
        )
        self.results["security_review"] = result2
        
        # Phase 3: Code Organization
        print("📋 Phase 3: Code Organization")
        print("-" * 70)
        result3 = await self.delegate_task(
            "organize-guru",
            "Design directory structure and code organization for the API"
        )
        self.results["code_structure"] = result3
        
        return self.results
    
    def generate_summary(self):
        """Generate summary of collaboration."""
        print("=" * 70)
        print("🎯 Collaboration Summary")
        print("=" * 70)
        print()
        
        print("✅ Completed Tasks:")
        for phase, result in self.results.items():
            print(f"   • {phase.replace('_', ' ').title()}: {result.get('deliverable', 'Done')}")
        
        print()
        print("📊 Collaboration Metrics:")
        print(f"   • Agents involved: {len(self.results)}")
        print(f"   • Tasks completed: {len(self.results)}")
        print(f"   • Communication: Tier 1 (same-runner HTTP)")
        print(f"   • Total deliverables: {sum(len(r.get('details', [])) for r in self.results.values())}")
        
        print()
        print("🚀 Next Steps:")
        print("   1. Implement API endpoints based on design")
        print("   2. Apply security measures from review")
        print("   3. Follow code structure recommendations")
        print("   4. Write tests and documentation")
        print()


async def main():
    """Run multi-agent collaboration example."""
    orchestrator = MultiAgentOrchestrator()
    
    try:
        await orchestrator.setup()
        await orchestrator.orchestrate()
        orchestrator.generate_summary()
        
        print("=" * 70)
        print("✅ Multi-agent collaboration completed successfully!")
        print("=" * 70)
        print()
        print("💡 This example demonstrates:")
        print("   • Agent discovery and registration")
        print("   • Task delegation pattern")
        print("   • Sequential multi-agent workflow")
        print("   • Result aggregation")
        print()
        print("🔧 To run with actual agent servers:")
        print("   1. Start discovery service")
        print("   2. Start agent servers (uvicorn)")
        print("   3. Use ChainedA2AClient for real communication")
        print()
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
