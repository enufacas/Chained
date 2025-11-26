#!/usr/bin/env python3
"""
Example A2A Client

This example demonstrates how to communicate with an A2A agent server.
It shows how to:
1. Discover an agent's capabilities via its Agent Card
2. Send a message/task to the agent
3. Receive and display the response

Usage:
    # Start a server first:
    python3 examples/a2a_agent_server.py engineer-master
    
    # Then in another terminal:
    python3 examples/a2a_client.py http://localhost:9788 "Design a REST API for user authentication"

Arguments:
    agent_url: Full URL to the agent (e.g., http://localhost:9788)
    message: Message to send to the agent
"""

import sys
import asyncio
from uuid import uuid4
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import httpx
from a2a.client import A2ACardResolver, A2AClient
from a2a.types import MessageSendParams, SendMessageRequest


async def main():
    """Run the A2A client."""
    # Parse arguments
    if len(sys.argv) < 3:
        print(__doc__)
        print("\nExample:")
        print("  python3 examples/a2a_client.py http://localhost:9788 'Design a REST API'")
        sys.exit(1)
    
    agent_url = sys.argv[1].rstrip('/')
    user_message = sys.argv[2]
    
    print(f"\n{'='*70}")
    print(f"A2A Client - Connecting to Agent")
    print(f"{'='*70}\n")
    print(f"🌐 Agent URL: {agent_url}")
    print(f"💬 Message: {user_message}\n")
    
    async with httpx.AsyncClient(timeout=30.0) as httpx_client:
        # Step 1: Fetch Agent Card
        print(f"📋 Fetching Agent Card...")
        try:
            resolver = A2ACardResolver(
                httpx_client=httpx_client,
                base_url=agent_url,
            )
            agent_card = await resolver.get_agent_card()
            
            print(f"✅ Agent Card received")
            print(f"   Name: {agent_card.name}")
            print(f"   Description: {agent_card.description[:80]}...")
            print(f"   Skills: {len(agent_card.skills)}")
            for skill in agent_card.skills[:3]:  # Show first 3 skills
                print(f"     - {skill.name}")
            if len(agent_card.skills) > 3:
                print(f"     ... and {len(agent_card.skills) - 3} more")
            print()
        
        except Exception as e:
            print(f"❌ Failed to fetch agent card: {e}")
            print(f"   Make sure the agent server is running at {agent_url}")
            sys.exit(1)
        
        # Step 2: Create A2A Client
        print(f"🔧 Creating A2A Client...")
        client = A2AClient(
            httpx_client=httpx_client,
            agent_card=agent_card,
        )
        print(f"✅ Client created\n")
        
        # Step 3: Send Message
        print(f"📤 Sending message to agent...")
        print(f"{'─'*70}")
        
        send_message_payload = {
            'message': {
                'role': 'user',
                'parts': [
                    {'kind': 'text', 'text': user_message}
                ],
                'messageId': uuid4().hex,
            },
        }
        
        request = SendMessageRequest(
            id=str(uuid4()),
            params=MessageSendParams(**send_message_payload)
        )
        
        try:
            # Send non-streaming request
            print(f"⏳ Waiting for response...\n")
            response = await client.send_message(request)
            
            # Display response
            print(f"{'='*70}")
            print(f"📥 Response from {agent_card.name}")
            print(f"{'='*70}\n")
            
            # Extract and display messages
            if hasattr(response, 'result') and hasattr(response.result, 'message'):
                message = response.result.message
                if hasattr(message, 'parts'):
                    for part in message.parts:
                        if hasattr(part, 'text'):
                            print(part.text)
            else:
                print(response.model_dump(mode='json', exclude_none=True))
            
            print(f"\n{'='*70}")
            print(f"✅ Communication complete")
            print(f"{'='*70}\n")
        
        except Exception as e:
            print(f"\n❌ Error sending message: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
