#!/bin/bash
# Demo script for Week 3 Phase A: UI Inference with Stack Context
# Tests ui_inference_activity integration in Temporal workflow

set -e

echo "🎨 Week 3 Phase A Demo: UI Inference with Stack Context"
echo "========================================================"
echo ""

# Check Temporal server
echo "📡 Checking Temporal server..."
if ! docker ps | grep -q temporal-server; then
    echo "❌ Temporal server not running. Start with: bash backend/scripts/setup_temporal.sh"
    exit 1
fi
echo "   ✅ Temporal server running"
echo ""

# Check if worker is running
echo "🔍 Checking Temporal worker..."
if [ -f backend/.worker.pid ]; then
    WORKER_PID=$(cat backend/.worker.pid)
    if ps -p $WORKER_PID > /dev/null 2>&1; then
        echo "   ✅ Worker running (PID: $WORKER_PID)"
    else
        echo "   ⚠️  Worker not running. Starting worker..."
        nohup python backend/workflows/build_project_workflow.py > backend/logs/temporal_worker.log 2>&1 &
        WORKER_PID=$!
        echo $WORKER_PID > backend/.worker.pid
        echo "   ✅ Worker started (PID: $WORKER_PID)"
        sleep 3
    fi
else
    echo "   ⚠️  Worker not running. Starting worker..."
    nohup python backend/workflows/build_project_workflow.py > backend/logs/temporal_worker.log 2>&1 &
    WORKER_PID=$!
    echo $WORKER_PID > backend/.worker.pid
    echo "   ✅ Worker started (PID: $WORKER_PID)"
    sleep 3
fi
echo ""

# Test scopes with different UI complexity
echo "🧪 Running UI Inference Tests (3 scopes)"
echo "========================================"
echo ""

# Test 1: Simple Dashboard (MERN stack)
echo "Test 1: Simple Dashboard App"
echo "----------------------------"
python3 -c "
import asyncio
from temporalio.client import Client

async def run():
    client = await Client.connect('localhost:7233')

    scope = 'Build a task management dashboard with Next.js, showing active tasks and stats'
    project_id = 'demo-ui-dashboard-001'

    print(f'📨 Scope: {scope}')
    print(f'🔑 Project ID: {project_id}')
    print('⏳ Running workflow...')
    print()

    result = await client.execute_workflow(
        'BuildProjectWorkflow',
        args=[scope, project_id],
        id=f'workflow-{project_id}',
        task_queue='grok-orc-queue'
    )

    print('✅ Workflow completed!')
    print()
    print('📊 Results:')
    print(f'   Stack: {result[\"plan\"][\"stack_backend\"]} + {result[\"plan\"][\"stack_frontend\"]}')
    stack_conf = result['plan']['stack_confidence']
    print(f'   Confidence: {stack_conf:.2f}', end='')
    if stack_conf < 0.7:
        print(' ⚠️  LOW CONFIDENCE - Stack may need manual review')
    else:
        print(' ✅')
    print()
    print('🎨 UI Inference Results:')
    ui = result['ui']
    print(f'   Components: {len(ui[\"components\"])} generated')
    for i, comp in enumerate(ui['components'][:5], 1):
        print(f'      {i}. {comp}')
    print(f'   Responsive: {ui[\"constraints\"].get(\"responsive\", False)}')
    print(f'   WCAG: {ui[\"constraints\"].get(\"wcag\", \"N/A\")}')
    print(f'   Needs Review: {ui[\"needs_review\"]}', end='')
    if ui['needs_review']:
        print(' ⚠️  UI generation had low confidence - manual review recommended')
    else:
        print(' ✅')
    print()

asyncio.run(run())
"
echo ""

# Test 2: E-commerce Site (T3 stack)
echo "Test 2: E-commerce Product Catalog"
echo "-----------------------------------"
python3 -c "
import asyncio
from temporalio.client import Client

async def run():
    client = await Client.connect('localhost:7233')

    scope = 'Build an e-commerce product catalog with TypeScript, tRPC, Prisma, and Tailwind'
    project_id = 'demo-ui-ecommerce-002'

    print(f'📨 Scope: {scope}')
    print(f'🔑 Project ID: {project_id}')
    print('⏳ Running workflow...')
    print()

    result = await client.execute_workflow(
        'BuildProjectWorkflow',
        args=[scope, project_id],
        id=f'workflow-{project_id}',
        task_queue='grok-orc-queue'
    )

    print('✅ Workflow completed!')
    print()
    print('📊 Results:')
    print(f'   Stack: {result[\"plan\"][\"stack_backend\"]} + {result[\"plan\"][\"stack_frontend\"]}')
    stack_conf = result['plan']['stack_confidence']
    print(f'   Confidence: {stack_conf:.2f}', end='')
    if stack_conf < 0.7:
        print(' ⚠️  LOW CONFIDENCE - Stack may need manual review')
    else:
        print(' ✅')
    print()
    print('🎨 UI Inference Results:')
    ui = result['ui']
    print(f'   Components: {len(ui[\"components\"])} generated')
    for i, comp in enumerate(ui['components'][:5], 1):
        print(f'      {i}. {comp}')
    print(f'   Hooks: {len(ui.get(\"hooks\", []))} API hooks')
    for i, hook in enumerate(ui.get('hooks', [])[:3], 1):
        print(f'      {i}. {hook}')
    print(f'   Needs Review: {ui[\"needs_review\"]}', end='')
    if ui['needs_review']:
        print(' ⚠️  UI generation had low confidence - manual review recommended')
    else:
        print(' ✅')
    print()

asyncio.run(run())
"
echo ""

# Test 3: Data Visualization App (FastAPI + React)
echo "Test 3: Data Analytics Dashboard"
echo "---------------------------------"
python3 -c "
import asyncio
from temporalio.client import Client

async def run():
    client = await Client.connect('localhost:7233')

    scope = 'Build a data analytics dashboard with Python FastAPI backend, React frontend, and PostgreSQL'
    project_id = 'demo-ui-analytics-003'

    print(f'📨 Scope: {scope}')
    print(f'🔑 Project ID: {project_id}')
    print('⏳ Running workflow...')
    print()

    result = await client.execute_workflow(
        'BuildProjectWorkflow',
        args=[scope, project_id],
        id=f'workflow-{project_id}',
        task_queue='grok-orc-queue'
    )

    print('✅ Workflow completed!')
    print()
    print('📊 Results:')
    print(f'   Stack: {result[\"plan\"][\"stack_backend\"]} + {result[\"plan\"][\"stack_frontend\"]}')
    stack_conf = result['plan']['stack_confidence']
    print(f'   Confidence: {stack_conf:.2f}', end='')
    if stack_conf < 0.7:
        print(' ⚠️  LOW CONFIDENCE - Stack may need manual review')
    else:
        print(' ✅')
    print()
    print('🎨 UI Inference Results:')
    ui = result['ui']
    print(f'   Components: {len(ui[\"components\"])} generated')
    for i, comp in enumerate(ui['components'][:7], 1):
        print(f'      {i}. {comp}')
    print(f'   Theme: {ui[\"constraints\"].get(\"theme\", \"N/A\")}')
    print(f'   Stack Hint: {ui.get(\"stack_hint\", {}).get(\"frontend\", \"N/A\")} (passed to Frontend Agent)')
    print(f'   Needs Review: {ui[\"needs_review\"]}', end='')
    if ui['needs_review']:
        print(' ⚠️  UI generation had low confidence - manual review recommended')
    else:
        print(' ✅')
    print()

asyncio.run(run())
"
echo ""

echo "🎉 UI Inference Demo Complete!"
echo ""
echo "📝 Summary:"
echo "   - All 3 workflows executed UI inference activity"
echo "   - Stack context passed to UI generation"
echo "   - Components generated with constraints and hooks"
echo "   - needs_review flag indicates low confidence cases"
echo ""
echo "🔍 View worker logs: tail -f backend/logs/temporal_worker.log"
echo "🌐 View Temporal UI: http://localhost:8233"
