#!/usr/bin/env python3
"""
Example A2A Agent Server

This example demonstrates running a Chained agent as an A2A-compatible server.
It shows how to:
1. Generate an A2A Agent Card from a Chained agent definition
2. Create an AgentExecutor
3. Run the agent as an HTTP server using the A2A protocol

Usage:
    python3 examples/a2a_agent_server.py <agent-name> [port]
    
Examples:
    python3 examples/a2a_agent_server.py engineer-master
    python3 examples/a2a_agent_server.py secure-specialist 9002
"""

import sys
import asyncio
import uvicorn
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore

from tools.a2a import generate_agent_card, ChainedAgentExecutor, get_agent_port


def main():
    """Run an A2A agent server."""
    # Parse arguments
    if len(sys.argv) < 2:
        print(__doc__)
        print("\nAvailable agents:")
        from tools.a2a import generate_all_agent_cards
        cards = generate_all_agent_cards()
        for i, name in enumerate(sorted(cards.keys())[:10], 1):
            print(f"  {i}. {name}")
        print(f"  ... and {len(cards) - 10} more")
        sys.exit(1)
    
    agent_name = sys.argv[1]
    port = int(sys.argv[2]) if len(sys.argv) > 2 else get_agent_port(agent_name)
    
    print(f"\n{'='*60}")
    print(f"Starting A2A Server for: {agent_name}")
    print(f"{'='*60}\n")
    
    # Generate agent card
    print(f"📋 Generating Agent Card...")
    try:
        agent_card = generate_agent_card(agent_name, port=port)
        print(f"✅ Agent Card generated successfully")
        print(f"   Name: {agent_card.name}")
        print(f"   URL: {agent_card.url}")
        print(f"   Skills: {len(agent_card.skills)}")
        for skill in agent_card.skills:
            print(f"     - {skill.name}: {skill.description[:60]}...")
    except Exception as e:
        print(f"❌ Failed to generate agent card: {e}")
        sys.exit(1)
    
    # Create executor
    print(f"\n⚙️  Creating Agent Executor...")
    try:
        executor = ChainedAgentExecutor(agent_name=agent_name)
        print(f"✅ Executor created for {agent_name}")
        print(f"   Specialization: {executor.metadata.get('specialization', 'N/A')}")
    except Exception as e:
        print(f"❌ Failed to create executor: {e}")
        sys.exit(1)
    
    # Create request handler with task store
    print(f"\n🔧 Setting up Request Handler...")
    task_store = InMemoryTaskStore()
    request_handler = DefaultRequestHandler(
        agent_executor=executor,
        task_store=task_store,
    )
    print(f"✅ Request handler configured")
    
    # Create A2A Starlette application
    print(f"\n🌐 Creating HTTP Server...")
    server = A2AStarletteApplication(
        agent_card=agent_card,
        http_handler=request_handler,
    )
    print(f"✅ Server created")
    
    # Run the server
    print(f"\n{'='*60}")
    print(f"🚀 Starting server on port {port}...")
    print(f"{'='*60}\n")
    print(f"Agent Card URL: http://localhost:{port}/.well-known/agent-card")
    print(f"Health Check: http://localhost:{port}/health")
    print(f"\nPress Ctrl+C to stop the server\n")
    
    try:
        uvicorn.run(server.build(), host='0.0.0.0', port=port, log_level="info")
    except KeyboardInterrupt:
        print(f"\n\n{'='*60}")
        print(f"Server stopped for {agent_name}")
        print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
