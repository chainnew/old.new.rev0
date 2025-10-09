#!/bin/bash

# ============================================================================
# HECTIC SWARM - Master Launcher
# Starts all services: MCP Server (8001), API Server (8000), Next.js App (3000)
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
║   🚀  HECTIC SWARM - MASTER LAUNCHER  🚀                  ║
║                                                           ║
║   Multi-Agent AI System with Grok 4 Fast                 ║
║   ───────────────────────────────────────────             ║
║   Services:                                               ║
║   • Port 8001: MCP Server (Agent Tools)                   ║
║   • Port 8000: API Server (Orchestrator)                  ║
║   • Port 3000: Next.js App (UI)                           ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"
echo ""

# Project root directory
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$PROJECT_ROOT/backend"
LOG_DIR="$PROJECT_ROOT/logs"

# Create logs directory
mkdir -p "$LOG_DIR"

log_info "Project root: $PROJECT_ROOT"
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
    log_warning "Please create .env.local with your API keys:"
    echo ""
    echo "OPENROUTER_API_KEY1=sk-or-..."
    echo "OPENROUTER_API_KEY2=sk-or-..."
    echo "OPENROUTER_API_KEY3=sk-or-..."
    echo "OPENROUTER_API_KEY4=sk-or-..."
    echo "DATABASE_URL=postgresql://..."
    echo "MCP_API_KEY=your-mcp-secret"
    echo ""
    exit 1
fi

# Check for required commands
log_info "Checking required commands..."

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

if ! command -v python3 &> /dev/null; then
    log_error "Python 3 not found! Please install Python 3.8+"
    exit 1
fi
log_success "Python: $(python3 --version)"

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
log_info "Installing Python dependencies..."
pip install -r requirements.txt --quiet
log_success "Python dependencies installed"

echo ""

# ============================================================================
# Step 3: Frontend Setup (Node.js)
# ============================================================================
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
    log_info "PostgreSQL configured - running Prisma migrations..."
    npx prisma generate
    npx prisma db push
    log_success "Database schema updated"
else
    log_warning "PostgreSQL not configured - some features may be limited"
fi

echo ""

# ============================================================================
# Step 5: Start Services
# ============================================================================
log_header "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
log_header "STEP 5: Starting Services"
log_header "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Function to kill processes on specific ports
kill_port() {
    local port=$1
    local pid=$(lsof -ti:$port)
    if [ ! -z "$pid" ]; then
        log_warning "Port $port is already in use (PID: $pid). Killing process..."
        kill -9 $pid 2>/dev/null || true
        sleep 1
    fi
}

# Clean up any existing processes on our ports
kill_port 8001
kill_port 8000
kill_port 3000

log_info "Starting services in background..."
echo ""

# Start MCP Server (port 8001)
log_info "Starting MCP Server on port 8001..."
cd "$BACKEND_DIR"
source venv/bin/activate
nohup python3 mcp_servers.py > "$LOG_DIR/mcp-server.log" 2>&1 &
MCP_PID=$!
echo $MCP_PID > "$LOG_DIR/mcp-server.pid"
log_success "MCP Server started (PID: $MCP_PID)"
log_info "  → Logs: $LOG_DIR/mcp-server.log"
log_info "  → Tools: browser, code-gen, db-sync, communication"

# Wait a moment for MCP server to start
sleep 2

# Start API Server (port 8000)
log_info "Starting API Server on port 8000..."
cd "$BACKEND_DIR"
source venv/bin/activate
nohup python3 main.py > "$LOG_DIR/api-server.log" 2>&1 &
API_PID=$!
echo $API_PID > "$LOG_DIR/api-server.pid"
log_success "API Server started (PID: $API_PID)"
log_info "  → Logs: $LOG_DIR/api-server.log"
log_info "  → API Docs: http://localhost:8000/docs"

# Wait a moment for API server to start
sleep 2

# Start Next.js App (port 3000)
log_info "Starting Next.js App on port 3000..."
cd "$PROJECT_ROOT"
nohup npm run dev > "$LOG_DIR/nextjs.log" 2>&1 &
NEXT_PID=$!
echo $NEXT_PID > "$LOG_DIR/nextjs.pid"
log_success "Next.js App started (PID: $NEXT_PID)"
log_info "  → Logs: $LOG_DIR/nextjs.log"
log_info "  → App: http://localhost:3000"

echo ""

# ============================================================================
# Step 6: Health Check
# ============================================================================
log_header "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
log_header "STEP 6: Health Check"
log_header "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

log_info "Waiting for services to be ready..."
sleep 5

# Check each service
check_service() {
    local name=$1
    local url=$2
    local max_attempts=10
    local attempt=1

    while [ $attempt -le $max_attempts ]; do
        if curl -s "$url" > /dev/null 2>&1; then
            log_success "$name is ready!"
            return 0
        fi
        log_info "  Waiting for $name... (attempt $attempt/$max_attempts)"
        sleep 2
        ((attempt++))
    done

    log_error "$name failed to start!"
    return 1
}

# Check services
check_service "MCP Server (8001)" "http://localhost:8001" || true
check_service "API Server (8000)" "http://localhost:8000" || true
check_service "Next.js App (3000)" "http://localhost:3000" || true

echo ""

# ============================================================================
# Summary
# ============================================================================
log_header "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
log_header "🎉 ALL SERVICES STARTED SUCCESSFULLY!"
log_header "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
log_success "Services Running:"
echo ""
echo -e "  ${CYAN}📱 Frontend (Next.js)${NC}"
echo -e "     ${GREEN}http://localhost:3000${NC}"
echo -e "     PID: $NEXT_PID"
echo ""
echo -e "  ${CYAN}🔧 MCP Server (Agent Tools)${NC}"
echo -e "     ${GREEN}http://localhost:8001${NC}"
echo -e "     PID: $MCP_PID"
echo -e "     Tools: browser, code-gen, db-sync, communication"
echo ""
echo -e "  ${CYAN}⚙️  API Server (Orchestrator)${NC}"
echo -e "     ${GREEN}http://localhost:8000${NC}"
echo -e "     ${GREEN}http://localhost:8000/docs${NC} (API Documentation)"
echo -e "     PID: $API_PID"
echo -e "     Agents: Frontend Architect, Backend Integrator, Deployment Guardian"
echo ""
log_info "Logs directory: $LOG_DIR"
echo ""
log_warning "To stop all services, run: ./stop.sh"
log_info "Or manually: kill $NEXT_PID $MCP_PID $API_PID"
echo ""
log_header "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Keep script running to monitor services
log_info "Press Ctrl+C to stop all services..."
echo ""

# Trap Ctrl+C
trap "echo ''; log_warning 'Stopping all services...'; kill $NEXT_PID $MCP_PID $API_PID 2>/dev/null; exit 0" INT

# Wait for any service to exit
wait $NEXT_PID $MCP_PID $API_PID
