#!/bin/bash
# ========================================
# Stop All Synergy Services
# ========================================
# Stops:
# - Orchestration Monitor
# - Swarm API
#
# Run: bash backend/scripts/stop_all_services.sh

echo "🛑 Stopping All Synergy Services..."
echo "=========================================="
echo ""

# Stop monitor if PID file exists
if [ -f backend/.monitor.pid ]; then
    MONITOR_PID=$(cat backend/.monitor.pid)
    echo "📊 Stopping Orchestration Monitor (PID: $MONITOR_PID)..."
    kill $MONITOR_PID 2>/dev/null || echo "   (Already stopped)"
    rm backend/.monitor.pid
else
    echo "📊 Orchestration Monitor: No PID file found"
fi

# Stop swarm API
echo "🌐 Stopping Swarm API..."
pkill -f swarm_api.py 2>/dev/null && echo "   ✅ Stopped" || echo "   (Already stopped)"

# Cleanup any orphaned Python processes on port 8000
if lsof -ti:8000 > /dev/null 2>&1; then
    echo "🧹 Cleaning up port 8000..."
    lsof -ti:8000 | xargs kill -9 2>/dev/null
fi

echo ""
echo "✅ All services stopped"
