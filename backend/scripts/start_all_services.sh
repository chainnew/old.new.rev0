#!/bin/bash
# ========================================
# Start All Synergy Services
# ========================================
# Starts:
# - Orchestration Monitor (background)
# - Swarm API with OTel tracing (foreground)
#
# Run: bash backend/scripts/start_all_services.sh

set -e

echo "🚀 Starting All Synergy Services..."
echo "=========================================="
echo ""

# Check if already running
if lsof -i:8000 > /dev/null 2>&1; then
    echo "⚠️  Port 8000 already in use (swarm_api.py likely running)"
    echo "   Kill it with: pkill -f swarm_api.py"
    exit 1
fi

# Start orchestration monitor in background
echo "📊 Starting Orchestration Monitor (background)..."
nohup python backend/orchestration_monitor.py > backend/logs/monitor.log 2>&1 &
MONITOR_PID=$!
echo $MONITOR_PID > backend/.monitor.pid
echo "   PID: $MONITOR_PID (log: backend/logs/monitor.log)"
echo ""

# Give monitor time to start
sleep 2

# Start swarm API (foreground with OTel traces)
echo "🌐 Starting Swarm API with OpenTelemetry..."
echo "   API: http://localhost:8000"
echo "   Docs: http://localhost:8000/docs"
echo "   Press Ctrl+C to stop"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Create logs directory
mkdir -p backend/logs

# Trap to cleanup on exit
trap "echo ''; echo '🛑 Stopping services...'; kill $MONITOR_PID 2>/dev/null; rm backend/.monitor.pid; echo '✅ All services stopped'; exit" INT TERM

# Start API (foreground - you'll see OTel traces here)
python backend/swarm_api.py
