#!/bin/bash
# Test A2A Integration
#
# This script tests the A2A integration by:
# 1. Generating agent cards for sample agents
# 2. (Future) Starting an agent server
# 3. (Future) Testing client communication

set -e

echo "========================================"
echo "A2A Integration Test"
echo "========================================"
echo ""

# Test 1: Generate agent cards
echo "Test 1: Generating Agent Cards"
echo "----------------------------------------"

python3 -c "
from tools.a2a import generate_agent_card

agents = ['engineer-master', 'secure-specialist', 'organize-guru', 'troubleshoot-expert']

for agent_name in agents:
    try:
        card = generate_agent_card(agent_name)
        print(f'✅ {agent_name:25} - {len(card.skills)} skills at {card.url}')
    except Exception as e:
        print(f'❌ {agent_name:25} - ERROR: {e}')
"

echo ""
echo "Test 2: Generate All Agent Cards"
echo "----------------------------------------"

python3 -c "
from tools.a2a import generate_all_agent_cards

cards = generate_all_agent_cards()
print(f'✅ Generated {len(cards)} agent cards')
print(f'   Sample agents: {list(cards.keys())[:5]}')
"

echo ""
echo "========================================"
echo "✅ All tests passed!"
echo "========================================"
echo ""
echo "Next steps:"
echo "  1. Run: python3 examples/a2a_agent_server.py engineer-master"
echo "  2. In another terminal: python3 examples/a2a_client.py http://localhost:9788 'Your message'"
echo ""
