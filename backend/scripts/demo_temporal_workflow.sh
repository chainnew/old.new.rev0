#!/bin/bash
# ========================================
# Temporal Workflow Demo Script
# ========================================
# Demonstrates Phase 2B:
# - Stack inference in workflows
# - Parallel task execution
# - Automatic retries
# - OTel tracing
#
# Prerequisites:
# 1. Temporal server running (setup_temporal.sh)
# 2. Worker running (start_all_services.sh or manual)
#
# Run: bash backend/scripts/demo_temporal_workflow.sh

echo "🎬 Temporal Workflow Demo: Phase 2B Integration"
echo "=========================================="
echo ""

# Check if Temporal server is running
if ! docker ps | grep -q temporal-server; then
    echo "❌ Temporal server not running"
    echo "   Start it with: bash backend/scripts/setup_temporal.sh"
    exit 1
fi

echo "✅ Temporal server is running"
echo ""

# Check if worker is running (optional - will warn)
if ! pgrep -f "build_project_workflow.py" > /dev/null; then
    echo "⚠️  Worker might not be running"
    echo "   Start it with: python backend/workflows/build_project_workflow.py &"
    echo "   Or use: bash backend/scripts/start_all_services.sh"
    echo ""
    read -p "   Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Test cases
echo "Running 3 test workflows..."
echo ""

# Test 1: Python backend
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📋 Test 1: Task management app with Python"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
python backend/scripts/demo_temporal.py \
    "Build a task management app like Trello with Python backend and modern UI" \
    "test-python-app"
echo ""
sleep 2

# Test 2: E-commerce
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📋 Test 2: E-commerce with Next.js"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
python backend/scripts/demo_temporal.py \
    "Create an e-commerce store with Next.js, Stripe, and product catalog" \
    "test-ecommerce"
echo ""
sleep 2

# Test 3: Real-time
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📋 Test 3: Real-time chat application"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
python backend/scripts/demo_temporal.py \
    "Build a real-time chat app with authentication and message history" \
    "test-chat-app"
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎉 Demo Complete!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "What to check:"
echo "1. Temporal UI: http://localhost:8233"
echo "   - View workflow execution history"
echo "   - See parallel task execution"
echo "   - Check retry attempts"
echo ""
echo "2. Worker logs (if running via start_all_services.sh):"
echo "   - OTel traces for activities"
echo "   - Stack inference results"
echo "   - Task completion status"
echo ""
echo "3. PostgreSQL:"
echo "   psql -d hive_mind -c \"SELECT * FROM stack_templates;\""
echo "   - Verify templates used"
echo ""
echo "=========================================="
