#!/bin/bash

echo "╔══════════════════════════════════════╗"
echo "║   🧪 HECTIC SWARM TEST SUITE 🧪      ║"
echo "╚══════════════════════════════════════╝"
echo ""

BACKEND_URL="${PYTHON_BACKEND_URL:-http://localhost:8000}"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test 1: Health Check
echo -e "${YELLOW}Test 1: Health Check${NC}"
response=$(curl -s "$BACKEND_URL/")
if echo "$response" | grep -q "HECTIC SWARM"; then
    echo -e "${GREEN}✅ Backend is running${NC}"
    echo "$response" | jq '.'
else
    echo -e "${RED}❌ Backend not responding${NC}"
    echo "Make sure backend is running: cd backend && ./start.sh"
    exit 1
fi

echo ""
echo "─────────────────────────────────────"
echo ""

# Test 2: Simple Code Migration
echo -e "${YELLOW}Test 2: Code Migration Request${NC}"
echo "Request: Port x86 traps to ARM"

curl -s -X POST "$BACKEND_URL/swarm/orchestrate" \
  -H "Content-Type: application/json" \
  -d '{
    "userMessage": "Port arch/x86/traps.c to ARM64 for Xen hypervisor",
    "conversationId": "test-'$(date +%s)'"
  }' | jq '{
    response: .response,
    task_count: (.tasks | length),
    stats: .swarm_stats,
    first_task: .tasks[0]
  }'

if [ $? -eq 0 ]; then
    echo -e "\n${GREEN}✅ Swarm orchestration successful${NC}"
else
    echo -e "\n${RED}❌ Swarm orchestration failed${NC}"
    exit 1
fi

echo ""
echo "─────────────────────────────────────"
echo ""

# Test 3: Single Agent Test
echo -e "${YELLOW}Test 3: Direct Code Agent Test${NC}"

curl -s -X POST "$BACKEND_URL/agent/code/execute" \
  -H "Content-Type: application/json" \
  -d '{
    "id": "direct-test-1",
    "conversation_id": "test-direct",
    "description": "Convert x86 cli/sti to ARM msr instructions",
    "code_snippet": "void disable_interrupts() { cli(); }"
  }' | jq '{
    status: .status,
    has_diff: (.output.diff != null),
    summary: .output.summary
  }'

if [ $? -eq 0 ]; then
    echo -e "\n${GREEN}✅ Direct agent test successful${NC}"
else
    echo -e "\n${RED}❌ Direct agent test failed${NC}"
fi

echo ""
echo "╔══════════════════════════════════════╗"
echo "║   🎉 ALL TESTS COMPLETE! 🎉          ║"
echo "╚══════════════════════════════════════╝"
echo ""
echo "Try it in your chat UI:"
echo '  Type: "Port x86 trap handling to ARM64"'
echo ""
