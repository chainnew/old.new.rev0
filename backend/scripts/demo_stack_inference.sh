#!/bin/bash
# ========================================
# Stack Inference Demo Script
# ========================================
# Demonstrates Phase 2A integration:
# - Stack inference running in orchestrator
# - OTel tracing with stack attributes
# - Confidence-based auto-fill
#
# Run: bash backend/scripts/demo_stack_inference.sh

echo "🎬 Stack Inference Demo: Phase 2A Integration"
echo "=========================================="
echo ""

# Demo scopes
echo "Testing 3 different project scopes..."
echo ""

# Test 1: Python backend
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📋 Test 1: Task management app with Python"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
curl -s -X POST http://localhost:8000/orchestrator/process \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Build a task management app like Trello with Python backend and modern UI",
    "user_id": "demo_user"
  }' | python -m json.tool
echo ""
echo "Expected: FastAPI + React (confidence >0.7)"
echo ""
sleep 2

# Test 2: E-commerce
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📋 Test 2: E-commerce with Next.js and Stripe"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
curl -s -X POST http://localhost:8000/orchestrator/process \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Create an e-commerce store with Next.js, Stripe integration, and product catalog",
    "user_id": "demo_user"
  }' | python -m json.tool
echo ""
echo "Expected: Next.js (T3 Stack or similar)"
echo ""
sleep 2

# Test 3: Serverless
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📋 Test 3: Real-time chat with authentication"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
curl -s -X POST http://localhost:8000/orchestrator/process \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Build a real-time chat application with user authentication and message history",
    "user_id": "demo_user"
  }' | python -m json.tool
echo ""
echo "Expected: Supabase or FastAPI (real-time stack)"
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎉 Demo complete!"
echo ""
echo "Check the swarm_api.py terminal for OTel traces showing:"
echo "- stack.confidence"
echo "- stack.backend"
echo "- stack.template"
echo ""
echo "To see more details, check:"
echo "- PostgreSQL: stack_templates table for matched templates"
echo "- Console: Stack inference logs with rationale"
echo "=========================================="
