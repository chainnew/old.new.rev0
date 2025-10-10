#!/bin/bash
# ========================================
# Start All Synergy Services
# ========================================
# Starts:
# - Orchestration Monitor (background)
# - Temporal Worker (background) - Phase 2B
# - Swarm API with OTel tracing (foreground)
#
# Run: bash backend/scripts/start_all_services.sh

set -e

# Get project root directory (2 levels up from this script)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
BACKEND_DIR="$PROJECT_ROOT/backend"

# Create necessary directories
mkdir -p "$BACKEND_DIR/logs"

echo "🚀 Starting All Synergy Services..."
echo "=========================================="
echo ""

# Check if already running
if lsof -i:8000 > /dev/null 2>&1; then
    echo "⚠️  Port 8000 already in use (swarm_api.py likely running)"
    echo "   Kill it with: pkill -f swarm_api.py"
    exit 1
fi

# Change to backend directory for Python imports
cd "$BACKEND_DIR"

# Start orchestration monitor in background
echo "📊 Starting Orchestration Monitor (background)..."
nohup python3 orchestration_monitor.py > logs/monitor.log 2>&1 &
MONITOR_PID=$!
echo $MONITOR_PID > .monitor.pid
echo "   PID: $MONITOR_PID (log: $BACKEND_DIR/logs/monitor.log)"
echo ""

# Start Temporal worker in background (Phase 2B)
echo "⚡ Starting Temporal Worker (background)..."
if docker ps | grep -q temporal-server; then
    nohup python3 workflows/build_project_workflow.py > logs/temporal_worker.log 2>&1 &
    WORKER_PID=$!
    echo $WORKER_PID > .worker.pid
    echo "   PID: $WORKER_PID (log: $BACKEND_DIR/logs/temporal_worker.log)"
    echo "   ✅ Temporal workflows enabled"
else
    echo "   ⚠️  Temporal server not running (workflows disabled)"
    echo "   To enable: bash backend/scripts/setup_temporal.sh"
fi
echo ""

# Give services time to start
sleep 2

# Start swarm API (foreground with OTel traces)
echo "🌐 Starting Swarm API with OpenTelemetry..."
echo "   API: http://localhost:8000"
echo "   Docs: http://localhost:8000/docs"
echo "   Press Ctrl+C to stop"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Trap to cleanup on exit
cleanup() {
    echo ''
    echo '🛑 Stopping services...'
    kill $MONITOR_PID 2>/dev/null
    if [ -f "$BACKEND_DIR/.worker.pid" ]; then
        kill $(cat "$BACKEND_DIR/.worker.pid") 2>/dev/null
        rm "$BACKEND_DIR/.worker.pid"
    fi
    rm "$BACKEND_DIR/.monitor.pid" 2>/dev/null
    echo '✅ All services stopped'
    exit
}
trap cleanup INT TERM

# Start API (foreground - you'll see OTel traces here)
python3 swarm_api.py
