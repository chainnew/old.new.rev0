#!/bin/bash

# ============================================================================
# GROK-ORC SYNERGY - Master Launcher
# Supports both HECTIC SWARM (original) and Synergy Stack (production MVP)
# ============================================================================

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${CYAN}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

log_header() {
    echo -e "${PURPLE}$1${NC}"
}

# Print banner
clear
echo -e "${PURPLE}"
cat << "EOF"
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║   🚀  GROK-ORC SYNERGY - MASTER LAUNCHER  🚀              ║
║                                                           ║
║   Multi-Agent AI System with SLO-Enforced Quality Gates  ║
║   ───────────────────────────────────────────             ║
║   Mode 1: HECTIC SWARM (Original)                        ║
║   • Port 8001: MCP Server (Agent Tools)                   ║
║   • Port 8000: API Server (Orchestrator)                  ║
║   • Port 3000: Next.js App (UI)                           ║
║                                                           ║
║   Mode 2: Synergy Stack (Production MVP v1.0)            ║
║   • Port 7233: Temporal (Workflows)                       ║
║   • Port 9090: Prometheus (Metrics)                       ║
║   • Port 3000: Grafana (Dashboards)                       ║
║   • Port 8000: API + Orchestrator + Monitor               ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"
echo ""

# Project root directory
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$PROJECT_ROOT/backend"
LOG_DIR="$PROJECT_ROOT/logs"
BACKEND_LOG_DIR="$BACKEND_DIR/logs"

# Create logs directories
mkdir -p "$LOG_DIR"
mkdir -p "$BACKEND_LOG_DIR"

log_info "Project root: $PROJECT_ROOT"
echo ""

# ============================================================================
# Mode Selection
# ============================================================================
echo ""
log_header "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
log_header "SELECT STARTUP MODE"
log_header "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  1) HECTIC SWARM (Original) - Simple dev mode"
echo "     ├─ MCP Server + API + Next.js UI"
echo "     ├─ Quick start, no Docker required"
echo "     └─ Best for: Development & testing"
echo ""
echo "  2) Synergy Stack (MVP v1.0) - Full production stack"
echo "     ├─ Temporal + Grafana + Prometheus"
echo "     ├─ SLO enforcement + observability"
echo "     ├─ Requires Docker Desktop running"
echo "     └─ Best for: Production pilot & demos"
echo ""
echo "  3) Hybrid Mode - Both stacks (advanced)"
echo "     └─ Run everything simultaneously"
echo ""

read -p "Select mode (1/2/3) [default: 1]: " MODE_CHOICE
MODE_CHOICE=${MODE_CHOICE:-1}

echo ""

# ============================================================================
# Step 1: Environment Check
# ============================================================================
log_header "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
log_header "STEP 1: Environment Validation"
log_header "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check for .env files
if [ -f "$PROJECT_ROOT/.env.local" ]; then
    log_success "Found .env.local"
elif [ -f "$PROJECT_ROOT/.env" ]; then
    log_success "Found .env"
elif [ -f "$BACKEND_DIR/.env" ]; then
    log_success "Found backend/.env"
else
    log_error "No .env file found!"
    log_warning "Please create .env.local or backend/.env with your API keys:"
    echo ""
    echo "OPENROUTER_API_KEY=sk-or-v1-..."
    echo "DATABASE_URL=postgresql://user:pass@localhost/hive_mind"
    echo "MCP_API_KEY=your-mcp-secret"
    echo ""
    exit 1
fi

# Check for required commands
log_info "Checking required commands..."

# Check Python
if command -v python3 &> /dev/null; then
    log_success "Python: $(python3 --version)"
elif command -v python &> /dev/null; then
    log_success "Python: $(python --version)"
    alias python3=python
else
    log_error "Python not found! Please install Python 3.9+"
    exit 1
fi

# Check Node.js (only for mode 1 or 3)
if [ "$MODE_CHOICE" == "1" ] || [ "$MODE_CHOICE" == "3" ]; then
    if ! command -v node &> /dev/null; then
        log_error "Node.js not found! Please install Node.js 18+"
        exit 1
    fi
    log_success "Node.js: $(node --version)"

    if ! command -v npm &> /dev/null; then
        log_error "npm not found! Please install npm"
        exit 1
    fi
    log_success "npm: $(npm --version)"
fi

# Check Docker (only for mode 2 or 3)
if [ "$MODE_CHOICE" == "2" ] || [ "$MODE_CHOICE" == "3" ]; then
    if ! command -v docker &> /dev/null; then
        log_error "Docker not found! Please install Docker Desktop"
        log_info "Download from: https://www.docker.com/products/docker-desktop"
        exit 1
    fi

    # Check if Docker daemon is running
    if ! docker ps &> /dev/null; then
        log_error "Docker daemon is not running!"
        log_warning "Please start Docker Desktop and try again"
        log_info "After starting Docker Desktop, run this script again"
        exit 1
    fi

    log_success "Docker: $(docker --version)"
    log_success "Docker daemon is running"
fi

echo ""

# ============================================================================
# Step 2: Backend Setup (Python)
# ============================================================================
log_header "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
log_header "STEP 2: Backend Setup (Python)"
log_header "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

cd "$BACKEND_DIR"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    log_info "Creating Python virtual environment..."
    python3 -m venv venv
    log_success "Virtual environment created"
else
    log_success "Virtual environment exists"
fi

# Activate virtual environment
log_info "Activating virtual environment..."
source venv/bin/activate
log_success "Virtual environment activated"

# Install/update Python dependencies
log_info "Installing Python dependencies (this may take a moment)..."
pip install -r requirements.txt --quiet --upgrade
log_success "Python dependencies installed"

echo ""

# ============================================================================
# Step 3: Frontend Setup (Node.js) - Only for Mode 1 or 3
# ============================================================================
if [ "$MODE_CHOICE" == "1" ] || [ "$MODE_CHOICE" == "3" ]; then
    log_header "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    log_header "STEP 3: Frontend Setup (Node.js)"
    log_header "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""

    cd "$PROJECT_ROOT"

    if [ ! -d "node_modules" ]; then
        log_info "Installing Node.js dependencies..."
        npm install
        log_success "Node.js dependencies installed"
    else
        log_success "Node.js dependencies exist"
    fi

    echo ""
fi

# ============================================================================
# Step 4: Database Setup
# ============================================================================
log_header "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
log_header "STEP 4: Database Setup"
log_header "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Create backend/swarms directory for SQLite databases
mkdir -p "$BACKEND_DIR/swarms"
log_success "Swarms directory ready"

# Check if PostgreSQL is configured
if grep -q "DATABASE_URL" "$PROJECT_ROOT/.env.local" 2>/dev/null || \
   grep -q "DATABASE_URL" "$PROJECT_ROOT/.env" 2>/dev/null || \
   grep -q "DATABASE_URL" "$BACKEND_DIR/.env" 2>/dev/null; then
    log_success "PostgreSQL configured"

    # For mode 2/3, check if pgvector migration is needed
    if [ "$MODE_CHOICE" == "2" ] || [ "$MODE_CHOICE" == "3" ]; then
        log_info "Synergy Stack requires pgvector extension"
        log_warning "If you haven't run migrations, execute:"
        echo "  psql -d hive_mind -f backend/migrations/001_add_pgvector.sql"
    fi
else
    log_warning "PostgreSQL not configured - using SQLite fallback"
    log_info "For full Synergy Stack features, configure DATABASE_URL in .env"
fi

echo ""

# ============================================================================
# Step 5: Synergy Stack Setup (Mode 2 or 3)
# ============================================================================
if [ "$MODE_CHOICE" == "2" ] || [ "$MODE_CHOICE" == "3" ]; then
    log_header "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    log_header "STEP 5: Synergy Stack Setup (Temporal + Grafana)"
    log_header "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""

    # Setup Temporal
    log_info "Setting up Temporal server..."
    if docker ps | grep -q temporal-server; then
        log_success "Temporal server already running"
    else
        bash "$BACKEND_DIR/scripts/setup_temporal.sh" || {
            log_error "Temporal setup failed"
            log_warning "Continuing without Temporal (workflows disabled)"
        }
    fi

    # Setup Grafana (optional)
    read -p "Setup Grafana + Prometheus for observability? (y/N): " SETUP_GRAFANA
    if [ "$SETUP_GRAFANA" == "y" ] || [ "$SETUP_GRAFANA" == "Y" ]; then
        log_info "Setting up Grafana + Prometheus..."
        bash "$BACKEND_DIR/scripts/setup_grafana.sh" || {
            log_warning "Grafana setup failed - continuing without observability dashboards"
        }
    else
        log_info "Skipping Grafana setup (can run later with: bash backend/scripts/setup_grafana.sh)"
    fi

    echo ""
fi

# ============================================================================
# Step 6: Start Services
# ============================================================================
log_header "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
log_header "STEP 6: Starting Services"
log_header "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Function to kill processes on specific ports
kill_port() {
    local port=$1
    local pid=$(lsof -ti:$port 2>/dev/null)
    if [ ! -z "$pid" ]; then
        log_warning "Port $port is already in use (PID: $pid). Killing process..."
        kill -9 $pid 2>/dev/null || true
        sleep 1
    fi
}

# Mode-specific service startup
case $MODE_CHOICE in
    1)
        # HECTIC SWARM Mode
        log_info "Starting HECTIC SWARM services..."
        echo ""

        # Clean up ports
        kill_port 8001
        kill_port 8000
        kill_port 3000

        # Start MCP Server
        log_info "Starting MCP Server on port 8001..."
        cd "$BACKEND_DIR"
        source venv/bin/activate
        nohup python3 mcp_servers.py > "$LOG_DIR/mcp-server.log" 2>&1 &
        MCP_PID=$!
        echo $MCP_PID > "$LOG_DIR/mcp-server.pid"
        log_success "MCP Server started (PID: $MCP_PID)"

        sleep 2

        # Start API Server
        log_info "Starting API Server on port 8000..."
        nohup python3 main.py > "$LOG_DIR/api-server.log" 2>&1 &
        API_PID=$!
        echo $API_PID > "$LOG_DIR/api-server.pid"
        log_success "API Server started (PID: $API_PID)"

        sleep 2

        # Start Next.js
        log_info "Starting Next.js App on port 3000..."
        cd "$PROJECT_ROOT"
        nohup npm run dev > "$LOG_DIR/nextjs.log" 2>&1 &
        NEXT_PID=$!
        echo $NEXT_PID > "$LOG_DIR/nextjs.pid"
        log_success "Next.js App started (PID: $NEXT_PID)"
        ;;

    2)
        # Synergy Stack Mode
        log_info "Starting Synergy Stack services..."
        echo ""

        # Export Prometheus flag
        export PROMETHEUS_ENABLED=true

        # Start all synergy services
        bash "$BACKEND_DIR/scripts/start_all_services.sh"
        ;;

    3)
        # Hybrid Mode
        log_info "Starting HYBRID mode (all services)..."
        echo ""

        # Start HECTIC SWARM services
        kill_port 8001
        kill_port 8000
        kill_port 3000

        cd "$BACKEND_DIR"
        source venv/bin/activate

        nohup python3 mcp_servers.py > "$LOG_DIR/mcp-server.log" 2>&1 &
        MCP_PID=$!
        echo $MCP_PID > "$LOG_DIR/mcp-server.pid"
        log_success "MCP Server started (PID: $MCP_PID)"

        cd "$PROJECT_ROOT"
        nohup npm run dev > "$LOG_DIR/nextjs.log" 2>&1 &
        NEXT_PID=$!
        echo $NEXT_PID > "$LOG_DIR/nextjs.pid"
        log_success "Next.js App started (PID: $NEXT_PID)"

        # Start Synergy Stack
        export PROMETHEUS_ENABLED=true
        bash "$BACKEND_DIR/scripts/start_all_services.sh"
        ;;
esac

echo ""

# ============================================================================
# Step 7: Health Check & Summary
# ============================================================================
log_header "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
log_header "STEP 7: Health Check"
log_header "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

log_info "Waiting for services to be ready (10 seconds)..."
sleep 10

echo ""
log_header "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
log_header "🎉 SERVICES STARTED SUCCESSFULLY!"
log_header "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

case $MODE_CHOICE in
    1)
        log_success "HECTIC SWARM Mode Active"
        echo ""
        echo -e "  ${CYAN}🌐 Frontend (Next.js)${NC}"
        echo -e "     ${GREEN}http://localhost:3000${NC}"
        echo ""
        echo -e "  ${CYAN}🔧 MCP Server (Agent Tools)${NC}"
        echo -e "     ${GREEN}http://localhost:8001${NC}"
        echo ""
        echo -e "  ${CYAN}⚙️  API Server (Orchestrator)${NC}"
        echo -e "     ${GREEN}http://localhost:8000/docs${NC}"
        ;;

    2)
        log_success "Synergy Stack Mode Active (v1.0-mvp)"
        echo ""
        echo -e "  ${CYAN}🔄 Temporal (Workflows)${NC}"
        echo -e "     ${GREEN}http://localhost:8233${NC}"
        echo ""
        echo -e "  ${CYAN}📊 Prometheus (Metrics)${NC}"
        echo -e "     ${GREEN}http://localhost:9090${NC}"
        echo ""
        echo -e "  ${CYAN}📈 Grafana (Dashboards)${NC}"
        echo -e "     ${GREEN}http://localhost:3000${NC} (admin/admin)"
        echo ""
        echo -e "  ${CYAN}⚙️  API + Orchestrator + Monitor${NC}"
        echo -e "     ${GREEN}http://localhost:8000/docs${NC}"
        echo ""
        log_info "Run demo: bash backend/scripts/demo_slo_workflow.sh"
        ;;

    3)
        log_success "Hybrid Mode Active (All Services)"
        echo ""
        echo "  HECTIC SWARM:"
        echo -e "    ${GREEN}http://localhost:3000${NC} (Next.js)"
        echo -e "    ${GREEN}http://localhost:8001${NC} (MCP Server)"
        echo ""
        echo "  SYNERGY STACK:"
        echo -e "    ${GREEN}http://localhost:8233${NC} (Temporal)"
        echo -e "    ${GREEN}http://localhost:9090${NC} (Prometheus)"
        echo -e "    ${GREEN}http://localhost:8000${NC} (API + Orchestrator)"
        ;;
esac

echo ""
log_info "Logs directory: $LOG_DIR"
log_info "Backend logs: $BACKEND_LOG_DIR"
echo ""
log_warning "To stop all services, run: ./stop.sh"
echo ""
log_header "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Keep script running
log_info "Services are running. Press Ctrl+C to stop all services..."
echo ""

# Trap Ctrl+C
trap "echo ''; log_warning 'Stopping all services...'; ./stop.sh; exit 0" INT

# Wait indefinitely
while true; do
    sleep 1
done
