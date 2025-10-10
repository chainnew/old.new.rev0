#!/bin/bash
# ========================================
# Phase 1 + 2A Setup Script
# ========================================
# Sets up:
# - Phase 1: OTel + Monitor + Stack Inference
# - Phase 2A: Stack Integration
#
# Run: bash backend/scripts/setup_phase1_and_2a.sh

set -e  # Exit on error

echo "🚀 Setting up Phase 1 + 2A: Synergy Systems"
echo "=========================================="
echo ""

# Step 1: Install dependencies
echo "📦 Step 1: Installing Python dependencies..."
cd backend
pip install -r requirements.txt
cd ..
echo "✅ Dependencies installed"
echo ""

# Step 2: Check PostgreSQL connection
echo "🔍 Step 2: Checking PostgreSQL connection..."
if psql -d hive_mind -U postgres -c "SELECT version();" > /dev/null 2>&1; then
    echo "✅ PostgreSQL connection OK"
else
    echo "❌ PostgreSQL connection failed"
    echo "   Please ensure PostgreSQL 16 is running:"
    echo "   brew services start postgresql@16"
    exit 1
fi
echo ""

# Step 3: Run pgvector migration
echo "🗄️  Step 3: Setting up pgvector extension..."
if psql -d hive_mind -U postgres -f backend/migrations/001_add_pgvector.sql > /dev/null 2>&1; then
    echo "✅ pgvector migration complete"
else
    echo "❌ pgvector migration failed"
    echo "   You may need to install pgvector:"
    echo "   brew install pgvector"
    echo "   brew services restart postgresql@16"
    exit 1
fi
echo ""

# Step 4: Seed embeddings
echo "🌱 Step 4: Seeding stack template embeddings..."
python backend/analyzers/stack_inferencer.py --seed-embeddings
echo ""

# Step 5: Test stack inference
echo "🧪 Step 5: Testing stack inference..."
python backend/analyzers/stack_inferencer.py --test
echo ""

# Step 6: Test integration
echo "🔗 Step 6: Testing orchestrator integration..."
python backend/test_stack_integration.py
echo ""

# Success
echo "=========================================="
echo "🎉 Phase 1 + 2A Setup Complete!"
echo "=========================================="
echo ""
echo "✅ All systems operational:"
echo "   - OpenTelemetry tracing"
echo "   - Orchestration monitor"
echo "   - Stack inference engine"
echo "   - Orchestrator integration"
echo ""
echo "Next steps:"
echo "1. Run backend/scripts/demo_stack_inference.sh to see it in action"
echo "2. Start swarm API: python backend/swarm_api.py"
echo "3. Create a swarm and watch stack auto-fill!"
echo ""
