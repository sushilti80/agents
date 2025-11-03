#!/bin/bash
# Quick start script for Daedalus Agent in Pantheon

echo "🏛️ Pantheon - Starting Daedalus Agent..."

# Get script directory and navigate to project root
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"
cd "$PROJECT_ROOT"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  No .env file found!"
    echo "Please create .env from .env.example and configure your credentials."
    exit 1
fi

# Start Chainlit with Daedalus
echo "Starting Daedalus on http://localhost:8000"
chainlit run agents/daedalus/main.py -w
