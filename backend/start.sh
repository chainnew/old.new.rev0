#!/bin/bash

echo "╔═══════════════════════════════════╗"
echo "║   🚀 HECTIC SWARM LAUNCHER 🚀     ║"
echo "╚═══════════════════════════════════╝"
echo ""

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate venv
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Install/update dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt --quiet

# Check environment variables
if [ ! -f "../.env" ] && [ ! -f "../.env.local" ]; then
    echo "⚠️  No .env file found!"
    echo "💡 Copy .env.example to .env and add your API keys"
    exit 1
fi

echo "✅ Environment ready"
echo ""
echo "🌐 Starting FastAPI server..."
echo "📚 API docs will be at: http://localhost:8000/docs"
echo ""

# Start server
python main.py
