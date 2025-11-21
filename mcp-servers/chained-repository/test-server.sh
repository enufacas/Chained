#!/bin/bash

# Test script for Chained Repository MCP Server
# Created by @investigate-champion

echo "🧪 Testing Chained Repository MCP Server"
echo "=========================================="
echo ""

# Test 1: List Tools
echo "📋 Test 1: List Tools"
echo '{"jsonrpc": "2.0", "id": 1, "method": "tools/list"}' | node dist/server.js 2>/dev/null | jq -r '.result.tools[] | "  - \(.name): \(.description)"'
echo ""

# Test 2: Get Agent Registry
echo "🤖 Test 2: Get Agent Registry"
echo '{"jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {"name": "get_agent_registry", "arguments": {}}}' | node dist/server.js 2>/dev/null | jq -r '.result.content[0].text' | jq -r '.agents | length as $count | "  Total agents: \($count)"'
echo ""

# Test 3: List Specializations
echo "🎯 Test 3: List Specializations"
echo '{"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "list_specializations", "arguments": {}}}' | node dist/server.js 2>/dev/null | jq -r '.result.content[0].text' | jq -r '.[] | "  - \(.)"' | head -10
echo ""

# Test 4: Get Hall of Fame
echo "🏆 Test 4: Get Hall of Fame"
echo '{"jsonrpc": "2.0", "id": 4, "method": "tools/call", "params": {"name": "get_hall_of_fame", "arguments": {}}}' | node dist/server.js 2>/dev/null | jq -r '.result.content[0].text' | jq -r 'length as $count | "  Hall of Fame members: \($count)"'
echo ""

# Test 5: Search Agent Patterns
echo "🔍 Test 5: Search Agent Patterns (api, testing)"
echo '{"jsonrpc": "2.0", "id": 5, "method": "tools/call", "params": {"name": "search_agent_patterns", "arguments": {"keywords": ["api", "testing"]}}}' | node dist/server.js 2>/dev/null | jq -r '.result.content[0].text' | jq -r 'keys[] | "  - \(.)"' | head -5
echo ""

# Test 6: List Available Tools
echo "🛠️  Test 6: List Available Tools"
echo '{"jsonrpc": "2.0", "id": 6, "method": "tools/call", "params": {"name": "list_available_tools", "arguments": {}}}' | node dist/server.js 2>/dev/null | jq -r '.result.content[0].text' | jq -r '.[] | "  - \(.)"' | head -10
echo ""

echo "✅ All tests completed!"
echo ""
echo "To use this MCP server with Claude Desktop:"
echo "1. Build: npm run build"
echo "2. Configure Claude Desktop with the path to dist/server.js"
echo "3. Restart Claude Desktop"
echo ""
