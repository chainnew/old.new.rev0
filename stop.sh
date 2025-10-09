#!/bin/bash

# ============================================================================
# HECTIC SWARM - Stop Script
# Gracefully stops all services
# ============================================================================

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${CYAN}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

echo ""
echo -e "${RED}╔═══════════════════════════════════════╗${NC}"
echo -e "${RED}║  STOPPING HECTIC SWARM SERVICES...   ║${NC}"
echo -e "${RED}╚═══════════════════════════════════════╝${NC}"
echo ""

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="$PROJECT_ROOT/logs"

# Function to stop a service by PID file
stop_service() {
    local name=$1
    local pid_file=$2

    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        if ps -p $pid > /dev/null 2>&1; then
            log_info "Stopping $name (PID: $pid)..."
            kill $pid 2>/dev/null || true
            sleep 1

            # Force kill if still running
            if ps -p $pid > /dev/null 2>&1; then
                log_warning "Force killing $name..."
                kill -9 $pid 2>/dev/null || true
            fi

            log_success "$name stopped"
        else
            log_warning "$name was not running (PID: $pid)"
        fi
        rm -f "$pid_file"
    else
        log_warning "No PID file found for $name"
    fi
}

# Function to kill process by port
kill_port() {
    local port=$1
    local name=$2
    local pid=$(lsof -ti:$port 2>/dev/null)

    if [ ! -z "$pid" ]; then
        log_info "Stopping $name on port $port (PID: $pid)..."
        kill $pid 2>/dev/null || true
        sleep 1

        # Force kill if still running
        if ps -p $pid > /dev/null 2>&1; then
            kill -9 $pid 2>/dev/null || true
        fi

        log_success "$name stopped"
    else
        log_info "$name not running on port $port"
    fi
}

# Stop services by PID files first
if [ -d "$LOG_DIR" ]; then
    stop_service "Next.js App" "$LOG_DIR/nextjs.pid"
    stop_service "API Server" "$LOG_DIR/api-server.pid"
    stop_service "MCP Server" "$LOG_DIR/mcp-server.pid"
fi

# Fallback: kill by port
log_info "Checking ports..."
kill_port 3000 "Next.js App"
kill_port 8000 "API Server"
kill_port 8001 "MCP Server"

echo ""
log_success "All services stopped!"
echo ""
log_info "To restart, run: ./start.sh"
echo ""
