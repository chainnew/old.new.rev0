#!/bin/bash
# ========================================
# Temporal Server Setup Script
# ========================================
# Sets up Temporal with PostgreSQL backend
# for durable workflow orchestration
#
# Run: bash backend/scripts/setup_temporal.sh

set -e

echo "🚀 Setting up Temporal Server (Phase 2B)"
echo "=========================================="
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running"
    echo "   Please start Docker Desktop and try again"
    exit 1
fi

echo "✅ Docker is running"
echo ""

# Create network
echo "🌐 Creating Temporal network..."
docker network create temporal-net 2>/dev/null || echo "   (Network already exists)"
echo ""

# Check if PostgreSQL is already running
if docker ps | grep -q temporal-postgres; then
    echo "✅ PostgreSQL already running"
else
    echo "🐘 Starting PostgreSQL for Temporal..."
    docker run -d \
        --name temporal-postgres \
        --network temporal-net \
        -p 5432:5432 \
        -e POSTGRES_USER=postgres \
        -e POSTGRES_PASSWORD=postgres \
        -e POSTGRES_DB=temporal \
        postgres:13-alpine

    echo "   Waiting for PostgreSQL to be ready..."
    sleep 5

    # Wait for PostgreSQL to accept connections
    for i in {1..10}; do
        if docker exec temporal-postgres pg_isready -U postgres > /dev/null 2>&1; then
            echo "✅ PostgreSQL is ready"
            break
        fi
        if [ $i -eq 10 ]; then
            echo "❌ PostgreSQL failed to start"
            echo "   Check logs: docker logs temporal-postgres"
            exit 1
        fi
        echo "   Waiting... ($i/10)"
        sleep 2
    done
fi

echo ""

# Check if Temporal is already running
if docker ps | grep -q temporal-server; then
    echo "⚠️  Temporal server already running"
    echo "   Stop it with: docker stop temporal-server"
    echo "   Or remove it with: docker rm -f temporal-server"
    read -p "   Remove and recreate? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        docker rm -f temporal-server
    else
        echo "   Keeping existing server"
        exit 0
    fi
fi

# Start Temporal server
echo "🏗️  Starting Temporal server (this may take 30-60s)..."
docker run -d \
    --name temporal-server \
    --network temporal-net \
    -p 7233:7233 \
    -p 8233:8233 \
    -e DB=postgresql \
    -e DB_PORT=5432 \
    -e POSTGRES_USER=postgres \
    -e POSTGRES_PWD=postgres \
    -e POSTGRES_SEEDS=temporal-postgres \
    temporalio/auto-setup:1.20.0

echo "   Container started, waiting for initialization..."
sleep 15

# Check if server is up
echo "🔍 Checking Temporal server health..."
for i in {1..10}; do
    if docker logs temporal-server 2>&1 | grep -q "All services are started"; then
        echo "✅ Temporal server is healthy!"
        break
    fi
    if [ $i -eq 10 ]; then
        echo "❌ Temporal server failed to start"
        echo "   Check logs: docker logs temporal-server"
        exit 1
    fi
    echo "   Waiting... ($i/10)"
    sleep 3
done

echo ""

# Register namespace
echo "📋 Registering namespace 'grok-orc-ns'..."
docker run --network temporal-net --rm temporalio/admin-tools:1.20.0 \
    tctl --ns grok-orc-ns namespace register 2>/dev/null || \
    echo "   (Namespace already exists)"

echo ""
echo "=========================================="
echo "🎉 Temporal Setup Complete!"
echo "=========================================="
echo ""
echo "✅ Temporal server running:"
echo "   - gRPC: localhost:7233"
echo "   - UI: http://localhost:8233"
echo "   - Namespace: grok-orc-ns"
echo ""
echo "Next steps:"
echo "1. Start worker: python backend/workflows/build_project_workflow.py"
echo "2. Run demo: bash backend/scripts/demo_temporal_workflow.sh"
echo ""
echo "To stop: docker stop temporal-server temporal-postgres"
echo "To remove: docker rm -f temporal-server temporal-postgres"
echo "To remove network: docker network rm temporal-net"
echo ""
